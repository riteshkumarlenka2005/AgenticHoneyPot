"""Database service for CRUD operations."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, SenderType
from app.models.intelligence import Intelligence, ArtifactType
from app.models.persona import Persona
from app.models.scammer_profile import ScammerProfile


class ConversationService:
    """Service for conversation operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        scammer_identifier: str,
        persona_id: Optional[UUID] = None,
        scam_type: Optional[str] = None,
        detection_confidence: float = 0.0
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            scammer_identifier=scammer_identifier,
            persona_id=persona_id,
            scam_type=scam_type,
            detection_confidence=detection_confidence,
            status=ConversationStatus.ACTIVE
        )
        session.add(conversation)
        await session.flush()
        return conversation
    
    @staticmethod
    async def get_by_id(session: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
        """Get a conversation by ID."""
        result = await session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages), selectinload(Conversation.intelligence))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_conversations(
        session: AsyncSession,
        status: Optional[ConversationStatus] = None,
        scam_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """List conversations with optional filtering."""
        query = select(Conversation)
        
        if status:
            query = query.where(Conversation.status == status)
        if scam_type:
            query = query.where(Conversation.scam_type == scam_type)
        
        query = query.order_by(Conversation.started_at.desc()).limit(limit).offset(offset)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_status(
        session: AsyncSession,
        conversation_id: UUID,
        status: ConversationStatus
    ) -> None:
        """Update conversation status."""
        await session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(status=status, last_activity=datetime.utcnow())
        )
    
    @staticmethod
    async def update_duration(
        session: AsyncSession,
        conversation_id: UUID,
        duration_seconds: int
    ) -> None:
        """Update conversation duration."""
        await session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(total_duration_seconds=duration_seconds, last_activity=datetime.utcnow())
        )


class MessageService:
    """Service for message operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        conversation_id: UUID,
        sender_type: SenderType,
        content: str,
        analysis: Optional[dict] = None
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            analysis=analysis or {}
        )
        session.add(message)
        await session.flush()
        return message
    
    @staticmethod
    async def get_by_conversation(
        session: AsyncSession,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get messages for a conversation."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
        )
        
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        return list(result.scalars().all())


class IntelligenceService:
    """Service for intelligence operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        conversation_id: UUID,
        artifact_type: ArtifactType,
        value: str,
        confidence: float = 0.0
    ) -> Intelligence:
        """Create a new intelligence artifact."""
        intelligence = Intelligence(
            conversation_id=conversation_id,
            artifact_type=artifact_type,
            value=value,
            confidence=confidence
        )
        session.add(intelligence)
        await session.flush()
        return intelligence
    
    @staticmethod
    async def list_intelligence(
        session: AsyncSession,
        artifact_type: Optional[ArtifactType] = None,
        validated: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Intelligence]:
        """List intelligence artifacts with filtering."""
        query = select(Intelligence)
        
        if artifact_type:
            query = query.where(Intelligence.artifact_type == artifact_type)
        if validated is not None:
            query = query.where(Intelligence.validated == validated)
        
        query = query.order_by(Intelligence.extracted_at.desc()).limit(limit).offset(offset)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def validate_intelligence(
        session: AsyncSession,
        intelligence_id: UUID,
        validated: bool
    ) -> None:
        """Mark intelligence as validated or not."""
        await session.execute(
            update(Intelligence)
            .where(Intelligence.id == intelligence_id)
            .values(validated=validated)
        )


class PersonaService:
    """Service for persona operations."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        name: str,
        age: int,
        occupation: str,
        location: str,
        communication_style: str,
        traits: Optional[dict] = None,
        backstory: Optional[dict] = None
    ) -> Persona:
        """Create a new persona."""
        persona = Persona(
            name=name,
            age=age,
            occupation=occupation,
            location=location,
            communication_style=communication_style,
            traits=traits or {},
            backstory=backstory or {}
        )
        session.add(persona)
        await session.flush()
        return persona
    
    @staticmethod
    async def get_by_id(session: AsyncSession, persona_id: UUID) -> Optional[Persona]:
        """Get a persona by ID."""
        result = await session.execute(
            select(Persona).where(Persona.id == persona_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_active(session: AsyncSession) -> List[Persona]:
        """List all active personas."""
        result = await session.execute(
            select(Persona).where(Persona.is_active == True)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def list_all(session: AsyncSession) -> List[Persona]:
        """List all personas."""
        result = await session.execute(select(Persona))
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        session: AsyncSession,
        persona_id: UUID,
        **kwargs
    ) -> None:
        """Update a persona."""
        await session.execute(
            update(Persona)
            .where(Persona.id == persona_id)
            .values(**kwargs)
        )
    
    @staticmethod
    async def delete(session: AsyncSession, persona_id: UUID) -> None:
        """Delete a persona."""
        await session.execute(
            delete(Persona).where(Persona.id == persona_id)
        )


class ScammerProfileService:
    """Service for scammer profile operations."""
    
    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        identifier: str
    ) -> ScammerProfile:
        """Get or create a scammer profile."""
        result = await session.execute(
            select(ScammerProfile).where(ScammerProfile.identifier == identifier)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = ScammerProfile(identifier=identifier)
            session.add(profile)
            await session.flush()
        
        return profile
    
    @staticmethod
    async def update_activity(
        session: AsyncSession,
        identifier: str
    ) -> None:
        """Update scammer's last seen timestamp."""
        await session.execute(
            update(ScammerProfile)
            .where(ScammerProfile.identifier == identifier)
            .values(
                last_seen=datetime.utcnow(),
                total_conversations=ScammerProfile.total_conversations + 1
            )
        )
    
    @staticmethod
    async def get_stats(session: AsyncSession) -> dict:
        """Get statistics about scammer profiles."""
        result = await session.execute(
            select(
                func.count(ScammerProfile.id),
                func.sum(ScammerProfile.total_conversations),
                func.avg(ScammerProfile.threat_score)
            )
        )
        count, total_convs, avg_threat = result.one()
        
        return {
            "total_profiles": count or 0,
            "total_conversations": total_convs or 0,
            "average_threat_score": float(avg_threat) if avg_threat else 0.0
        }
