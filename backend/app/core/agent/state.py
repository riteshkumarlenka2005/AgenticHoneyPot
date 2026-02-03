"""Conversation state management."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from app.models.conversation import ConversationStatus


class ConversationState:
    """Manages state for a single conversation."""
    
    def __init__(
        self,
        conversation_id: Optional[UUID] = None,
        scammer_identifier: str = "",
        persona: Optional[dict] = None
    ):
        """Initialize conversation state."""
        self.conversation_id = conversation_id or uuid4()
        self.scammer_identifier = scammer_identifier
        self.persona = persona or {}
        self.status = ConversationStatus.ACTIVE
        self.scam_type = "unknown"
        self.detection_confidence = 0.0
        self.started_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.message_count = 0
        self.intelligence_extracted = {
            "upi_ids": [],
            "bank_accounts": [],
            "ifsc_codes": [],
            "phone_numbers": [],
            "urls": [],
            "emails": []
        }
        self.manipulation_tactics = []
        self.metadata: Dict[str, Any] = {}
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def add_message(self):
        """Increment message count and update activity."""
        self.message_count += 1
        self.update_activity()
    
    def add_intelligence(self, artifact_type: str, value: str):
        """Add extracted intelligence."""
        if artifact_type in self.intelligence_extracted:
            if value not in self.intelligence_extracted[artifact_type]:
                self.intelligence_extracted[artifact_type].append(value)
    
    def get_duration(self) -> int:
        """Get conversation duration in seconds."""
        return int((self.last_activity - self.started_at).total_seconds())
    
    def to_dict(self) -> dict:
        """Convert state to dictionary."""
        return {
            "conversation_id": str(self.conversation_id),
            "scammer_identifier": self.scammer_identifier,
            "persona": self.persona,
            "status": self.status.value,
            "scam_type": self.scam_type,
            "detection_confidence": self.detection_confidence,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "message_count": self.message_count,
            "duration_seconds": self.get_duration(),
            "intelligence_extracted": self.intelligence_extracted,
            "manipulation_tactics": self.manipulation_tactics,
            "metadata": self.metadata
        }
