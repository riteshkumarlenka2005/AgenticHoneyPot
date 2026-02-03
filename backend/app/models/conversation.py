"""Conversation model."""
from datetime import datetime
from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, JSON, TypeDecorator
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class ConversationStatus(str, PyEnum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    STALLING = "stalling"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Conversation(Base):
    """Conversation model."""
    __tablename__ = "conversations"
    
    id = Column(GUID(), primary_key=True, default=uuid4)
    scammer_identifier = Column(String, nullable=False, index=True)
    persona_id = Column(GUID(), nullable=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    scam_type = Column(String, nullable=True)
    detection_confidence = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_duration_seconds = Column(Integer, default=0)
    extra_data = Column(JSON, default=dict)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    intelligence = relationship("Intelligence", back_populates="conversation", cascade="all, delete-orphan")
