"""Scammer profile model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..db.database import Base


class ScammerProfile(Base):
    """Scammer profile model."""
    
    __tablename__ = "scammer_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String, unique=True, nullable=False)
    known_aliases = Column(JSON, default=list)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_conversations = Column(Integer, default=0)
    linked_intelligence = Column(JSON, default=list)
    threat_score = Column(Float, default=0.0)
