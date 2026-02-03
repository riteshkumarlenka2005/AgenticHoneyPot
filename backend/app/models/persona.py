"""Persona model."""
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class Persona(Base):
    """Persona model."""
    __tablename__ = "personas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String, nullable=False)
    location = Column(String, nullable=False)
    traits = Column(JSON, default=dict)
    communication_style = Column(Text, nullable=False)
    backstory = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
