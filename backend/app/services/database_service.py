"""Database CRUD service layer."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, SenderType
from app.models.intelligence import Intelligence, ArtifactType
from app.models.persona import Persona
from app.models.scammer_profile import ScammerProfile


class DatabaseService:
    """CRUD service for database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    # Conversation operations
    async def create_conversation(
        self,
        scammer_identifier: str,
        persona_id: Optional[UUID] = None,
        scam_type: Optional[str] = None,
        detection_confidence: float = 0.0,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            scammer_identifier=scammer_identifier,
            persona_id=persona_id,
            scam_type=scam_type,
            detection_confidence=detection_confidence,
            status=ConversationStatus.ACTIVE,
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_conversation(
        self, conversation_id: UUID, include_messages: bool = False
    ) -> Optional[Conversation]:
        """Get a conversation by ID."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_conversations(
        self,
        status: Optional[ConversationStatus] = None,
        scam_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Conversation]:
        """Get list of conversations with filters."""
        query = select(Conversation)
        if status:
            query = query.where(Conversation.status == status)
        if scam_type:
            query = query.where(Conversation.scam_type == scam_type)
        query = query.order_by(Conversation.started_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_conversation(
        self, conversation_id: UUID, **kwargs: Any
    ) -> Optional[Conversation]:
        """Update a conversation."""
        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        return await self.get_conversation(conversation_id)

    # Message operations
    async def create_message(
        self,
        conversation_id: UUID,
        sender_type: SenderType,
        content: str,
        analysis: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            content=content,
            analysis=analysis or {},
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        """Get messages for a conversation."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # Intelligence operations
    async def create_intelligence(
        self,
        conversation_id: UUID,
        artifact_type: ArtifactType,
        value: str,
        confidence: float = 0.0,
        validated: bool = False,
    ) -> Intelligence:
        """Create a new intelligence artifact."""
        intelligence = Intelligence(
            conversation_id=conversation_id,
            artifact_type=artifact_type,
            value=value,
            confidence=confidence,
            validated=validated,
        )
        self.session.add(intelligence)
        await self.session.flush()
        return intelligence

    async def get_intelligence(
        self,
        conversation_id: Optional[UUID] = None,
        artifact_type: Optional[ArtifactType] = None,
        validated: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Intelligence]:
        """Get intelligence artifacts with filters."""
        query = select(Intelligence)
        if conversation_id:
            query = query.where(Intelligence.conversation_id == conversation_id)
        if artifact_type:
            query = query.where(Intelligence.artifact_type == artifact_type)
        if validated is not None:
            query = query.where(Intelligence.validated == validated)
        query = query.order_by(Intelligence.extracted_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # Persona operations
    async def create_persona(
        self,
        name: str,
        age: int,
        occupation: str,
        location: str,
        communication_style: str,
        traits: Optional[Dict[str, Any]] = None,
        backstory: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
    ) -> Persona:
        """Create a new persona."""
        persona = Persona(
            name=name,
            age=age,
            occupation=occupation,
            location=location,
            communication_style=communication_style,
            traits=traits or {},
            backstory=backstory or {},
            is_active=is_active,
        )
        self.session.add(persona)
        await self.session.flush()
        return persona

    async def get_persona(self, persona_id: UUID) -> Optional[Persona]:
        """Get a persona by ID."""
        result = await self.session.execute(select(Persona).where(Persona.id == persona_id))
        return result.scalar_one_or_none()

    async def get_personas(
        self, is_active: Optional[bool] = None, limit: int = 50, offset: int = 0
    ) -> List[Persona]:
        """Get list of personas."""
        query = select(Persona)
        if is_active is not None:
            query = query.where(Persona.is_active == is_active)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_persona(self, persona_id: UUID, **kwargs: Any) -> Optional[Persona]:
        """Update a persona."""
        stmt = (
            update(Persona)
            .where(Persona.id == persona_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        return await self.get_persona(persona_id)

    async def delete_persona(self, persona_id: UUID) -> bool:
        """Delete a persona."""
        stmt = delete(Persona).where(Persona.id == persona_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # Scammer profile operations
    async def create_scammer_profile(
        self,
        identifier: str,
        known_aliases: Optional[List[str]] = None,
        linked_intelligence: Optional[List[str]] = None,
        threat_score: float = 0.0,
    ) -> ScammerProfile:
        """Create a new scammer profile."""
        profile = ScammerProfile(
            identifier=identifier,
            known_aliases=known_aliases or [],
            linked_intelligence=linked_intelligence or [],
            threat_score=threat_score,
        )
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_scammer_profile(
        self, identifier: str
    ) -> Optional[ScammerProfile]:
        """Get a scammer profile by identifier."""
        result = await self.session.execute(
            select(ScammerProfile).where(ScammerProfile.identifier == identifier)
        )
        return result.scalar_one_or_none()

    async def update_scammer_profile(
        self, identifier: str, **kwargs: Any
    ) -> Optional[ScammerProfile]:
        """Update a scammer profile."""
        stmt = (
            update(ScammerProfile)
            .where(ScammerProfile.identifier == identifier)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        return await self.get_scammer_profile(identifier)

    # Analytics operations
    async def get_scam_type_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of scam types."""
        query = (
            select(
                Conversation.scam_type,
                func.count(Conversation.id).label("count"),
            )
            .where(Conversation.scam_type.isnot(None))
            .group_by(Conversation.scam_type)
        )
        result = await self.session.execute(query)
        rows = result.all()
        total = sum(row.count for row in rows)
        return [
            {
                "scam_type": row.scam_type,
                "count": row.count,
                "percentage": (row.count / total * 100) if total > 0 else 0,
            }
            for row in rows
        ]

    async def get_total_conversations(self) -> int:
        """Get total number of conversations."""
        result = await self.session.execute(select(func.count(Conversation.id)))
        return result.scalar() or 0

    async def get_total_intelligence(self) -> int:
        """Get total number of intelligence artifacts."""
        result = await self.session.execute(select(func.count(Intelligence.id)))
        return result.scalar() or 0
