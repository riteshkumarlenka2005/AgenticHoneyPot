"""Conversation model."""
from datetime import datetime
from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class ConversationStatus(str, PyEnum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    STALLING = "stalling"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Conversation(Base):
    """Conversation model."""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    scammer_identifier = Column(String, nullable=False, index=True)
    persona_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    scam_type = Column(String, nullable=True)
    detection_confidence = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_duration_seconds = Column(Integer, default=0)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    intelligence = relationship("Intelligence", back_populates="conversation", cascade="all, delete-orphan")
