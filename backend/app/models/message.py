"""Message model."""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..db.database import Base


class SenderType(str, enum.Enum):
    """Sender type enum."""
    SCAMMER = "scammer"
    HONEYPOT = "honeypot"


class Message(Base):
    """Message model."""
    
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(SQLEnum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    analysis = Column(JSON, default=dict)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
