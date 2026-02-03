"""Intelligence model."""
from datetime import datetime
from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base


class ArtifactType(str, PyEnum):
    """Intelligence artifact type enumeration."""
    UPI_ID = "upi_id"
    BANK_ACCOUNT = "bank_account"
    IFSC_CODE = "ifsc_code"
    PHONE = "phone"
    URL = "url"
    EMAIL = "email"


class Intelligence(Base):
    """Intelligence model for extracted artifacts."""
    __tablename__ = "intelligence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    artifact_type = Column(Enum(ArtifactType), nullable=False)
    value = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    validated = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="intelligence")
