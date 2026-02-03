"""Intelligence model."""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..db.database import Base


class ArtifactType(str, enum.Enum):
    """Artifact type enum."""
    UPI_ID = "upi_id"
    BANK_ACCOUNT = "bank_account"
    IFSC_CODE = "ifsc_code"
    PHONE = "phone"
    URL = "url"
    EMAIL = "email"


class Intelligence(Base):
    """Intelligence model."""
    
    __tablename__ = "intelligence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    artifact_type = Column(SQLEnum(ArtifactType), nullable=False)
    value = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    validated = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="intelligence")
