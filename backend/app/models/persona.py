"""Persona model."""
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Text, JSON, Boolean
from app.db.database import Base
from app.models.conversation import GUID


class Persona(Base):
    """Persona model."""
    __tablename__ = "personas"
    
    id = Column(GUID(), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String, nullable=False)
    location = Column(String, nullable=False)
    traits = Column(JSON, default=dict)
    communication_style = Column(Text, nullable=False)
    backstory = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
