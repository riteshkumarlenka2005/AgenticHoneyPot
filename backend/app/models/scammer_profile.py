"""Scammer profile model."""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from app.db.database import Base
from app.models.conversation import GUID


class ScammerProfile(Base):
    """Scammer profile model."""
    __tablename__ = "scammer_profiles"
    
    id = Column(GUID(), primary_key=True, default=uuid4)
    identifier = Column(String, unique=True, nullable=False, index=True)
    known_aliases = Column(JSON, default=list)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_conversations = Column(Integer, default=0)
    linked_intelligence = Column(JSON, default=list)
    threat_score = Column(Float, default=0.0)
