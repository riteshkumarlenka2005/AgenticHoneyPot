"""Database service for CRUD operations."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, SenderType
from app.models.intelligence import Intelligence, ArtifactType
from app.models.persona import Persona
from app.models.scammer_profile import ScammerProfile


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize database service with session."""
        self.session = session
    
    # Conversation operations
    async def create_conversation(
        self,
        scammer_identifier: str,
        persona_id: Optional[UUID] = None,
        scam_type: Optional[str] = None,
        detection_confidence: Optional[float] = None
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            scammer_identifier=scammer_identifier,
            persona_id=persona_id,
            status=ConversationStatus.ACTIVE,
            scam_type=scam_type,
            detection_confidence=detection_confidence,
            started_at=datetime.utcnow()
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation
    
    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID."""
        result = await self.session.execute(
            select(Conversation)
            .options(
                selectinload(Conversation.messages),
                selectinload(Conversation.intelligence)
            )
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_conversation_by_scammer(
        self,
        scammer_identifier: str,
        status: Optional[ConversationStatus] = None
    ) -> Optional[Conversation]:
        """Get active conversation for a scammer."""
        query = select(Conversation).where(
            Conversation.scammer_identifier == scammer_identifier
        )
        if status:
            query = query.where(Conversation.status == status)
        query = query.order_by(desc(Conversation.last_activity))
        
        result = await self.session.execute(query)
        return result.scalar_first()
    
    async def list_conversations(
        self,
        status: Optional[ConversationStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Conversation]:
        """List conversations with optional filtering."""
        query = select(Conversation).order_by(desc(Conversation.started_at))
        
        if status:
            query = query.where(Conversation.status == status)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_conversation_status(
        self,
        conversation_id: UUID,
        status: ConversationStatus
    ) -> Optional[Conversation]:
        """Update conversation status."""
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.status = status
            conversation.last_activity = datetime.utcnow()
            await self.session.flush()
        return conversation
    
    # Message operations
    async def create_message(
        self,
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
            timestamp=datetime.utcnow(),
            analysis=analysis
        )
        self.session.add(message)
        
        # Update conversation last activity
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.last_activity = datetime.utcnow()
        
        await self.session.flush()
        return message
    
    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 100
    ) -> List[Message]:
        """Get messages for a conversation."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    # Intelligence operations
    async def create_intelligence(
        self,
        conversation_id: UUID,
        artifact_type: ArtifactType,
        value: str,
        confidence: float = 0.0,
        validated: bool = False
    ) -> Intelligence:
        """Create a new intelligence artifact."""
        intelligence = Intelligence(
            conversation_id=conversation_id,
            artifact_type=artifact_type,
            value=value,
            confidence=confidence,
            extracted_at=datetime.utcnow(),
            validated=validated
        )
        self.session.add(intelligence)
        await self.session.flush()
        return intelligence
    
    async def get_intelligence(
        self,
        conversation_id: Optional[UUID] = None,
        artifact_type: Optional[ArtifactType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Intelligence]:
        """Get intelligence artifacts with optional filtering."""
        query = select(Intelligence).order_by(desc(Intelligence.extracted_at))
        
        if conversation_id:
            query = query.where(Intelligence.conversation_id == conversation_id)
        
        if artifact_type:
            query = query.where(Intelligence.artifact_type == artifact_type)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def mark_intelligence_validated(
        self,
        intelligence_id: UUID,
        validated: bool = True
    ) -> Optional[Intelligence]:
        """Mark intelligence as validated."""
        result = await self.session.execute(
            select(Intelligence).where(Intelligence.id == intelligence_id)
        )
        intelligence = result.scalar_one_or_none()
        if intelligence:
            intelligence.validated = validated
            await self.session.flush()
        return intelligence
    
    # Persona operations
    async def create_persona(
        self,
        name: str,
        age: int,
        occupation: str,
        location: str,
        communication_style: str,
        traits: Optional[dict] = None,
        backstory: Optional[dict] = None,
        is_active: bool = True
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
            is_active=is_active
        )
        self.session.add(persona)
        await self.session.flush()
        return persona
    
    async def get_persona(self, persona_id: UUID) -> Optional[Persona]:
        """Get persona by ID."""
        result = await self.session.execute(
            select(Persona).where(Persona.id == persona_id)
        )
        return result.scalar_one_or_none()
    
    async def list_personas(
        self,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> List[Persona]:
        """List personas."""
        query = select(Persona)
        
        if is_active is not None:
            query = query.where(Persona.is_active == is_active)
        
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_random_active_persona(self) -> Optional[Persona]:
        """Get a random active persona."""
        result = await self.session.execute(
            select(Persona)
            .where(Persona.is_active == True)
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_first()
    
    # Scammer Profile operations
    async def create_or_update_scammer_profile(
        self,
        identifier: str,
        threat_score: Optional[float] = None
    ) -> ScammerProfile:
        """Create or update scammer profile."""
        result = await self.session.execute(
            select(ScammerProfile).where(ScammerProfile.identifier == identifier)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            # Update existing
            profile.last_seen = datetime.utcnow()
            profile.total_conversations = (profile.total_conversations or 0) + 1
            if threat_score is not None:
                profile.threat_score = threat_score
        else:
            # Create new
            profile = ScammerProfile(
                identifier=identifier,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                total_conversations=1,
                threat_score=threat_score
            )
            self.session.add(profile)
        
        await self.session.flush()
        return profile
    
    async def get_scammer_profile(self, identifier: str) -> Optional[ScammerProfile]:
        """Get scammer profile by identifier."""
        result = await self.session.execute(
            select(ScammerProfile).where(ScammerProfile.identifier == identifier)
        )
        return result.scalar_one_or_none()
    
    # Analytics operations
    async def get_analytics_overview(self) -> dict:
        """Get analytics overview."""
        # Total conversations
        total_conv = await self.session.execute(select(func.count(Conversation.id)))
        total_conversations = total_conv.scalar_one()
        
        # Active conversations
        active_conv = await self.session.execute(
            select(func.count(Conversation.id))
            .where(Conversation.status == ConversationStatus.ACTIVE)
        )
        active_conversations = active_conv.scalar_one()
        
        # Total intelligence
        total_intel = await self.session.execute(select(func.count(Intelligence.id)))
        total_intelligence = total_intel.scalar_one()
        
        # Total time wasted (sum of durations)
        time_wasted = await self.session.execute(
            select(func.coalesce(func.sum(Conversation.total_duration_seconds), 0))
        )
        total_time_wasted = time_wasted.scalar_one()
        
        return {
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "total_intelligence": total_intelligence,
            "total_time_wasted_seconds": total_time_wasted
        }
    
    async def get_scam_type_distribution(self) -> List[dict]:
        """Get distribution of scam types."""
        result = await self.session.execute(
            select(
                Conversation.scam_type,
                func.count(Conversation.id).label('count')
            )
            .where(Conversation.scam_type.isnot(None))
            .group_by(Conversation.scam_type)
        )
        
        return [
            {"scam_type": row[0], "count": row[1]}
            for row in result.all()
        ]
    
    async def get_timeline_data(self, days: int = 30) -> List[dict]:
        """Get timeline data for the last N days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(
                func.date(Conversation.started_at).label('date'),
                func.count(Conversation.id).label('count')
            )
            .where(Conversation.started_at >= cutoff_date)
            .group_by(func.date(Conversation.started_at))
            .order_by(func.date(Conversation.started_at))
        )
        
        return [
            {"date": str(row[0]), "count": row[1]}
            for row in result.all()
        ]
