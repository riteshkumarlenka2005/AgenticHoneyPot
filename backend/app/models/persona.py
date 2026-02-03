"""Persona model."""
from sqlalchemy import Column, String, Integer, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..db.database import Base


class Persona(Base):
    """Persona model."""
    
    __tablename__ = "personas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    age = Column(Integer)
    occupation = Column(String)
    location = Column(String)
    traits = Column(JSON, default=dict)
    communication_style = Column(Text)
    backstory = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="persona")
