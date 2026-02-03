"""Message model."""
from datetime import datetime
from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.conversation import GUID


class SenderType(str, PyEnum):
    """Message sender type enumeration."""
    SCAMMER = "scammer"
    HONEYPOT = "honeypot"


class Message(Base):
    """Message model."""
    __tablename__ = "messages"
    
    id = Column(GUID(), primary_key=True, default=uuid4)
    conversation_id = Column(GUID(), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    analysis = Column(JSON, default=dict)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
