"""Conversation model."""
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..db.database import Base


class ConversationStatus(str, enum.Enum):
    """Conversation status enum."""
    ACTIVE = "active"
    STALLING = "stalling"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Conversation(Base):
    """Conversation model."""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scammer_identifier = Column(String, nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"))
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    scam_type = Column(String)
    detection_confidence = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    total_duration_seconds = Column(Integer, default=0)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    intelligence = relationship("Intelligence", back_populates="conversation", cascade="all, delete-orphan")
    persona = relationship("Persona", back_populates="conversations")
