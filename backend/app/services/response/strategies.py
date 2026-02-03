"""Response strategies for different engagement phases."""
from enum import Enum


class EngagementPhase(str, Enum):
    """Engagement phase enumeration."""
    DETECTING = "detecting"
    ENGAGING = "engaging"
    EXTRACTING = "extracting_info"
    STALLING = "stalling"
    COMPLETED = "completed"


class ResponseStrategy:
    """Determine response strategy based on conversation state."""
    
    @staticmethod
    def determine_strategy(
        detection_confidence: float,
        message_count: int,
        intelligence_extracted: dict,
        scam_type: str
    ) -> tuple[str, EngagementPhase]:
        """
        Determine response strategy based on conversation state.
        
        Args:
            detection_confidence: Confidence that this is a scam (0-1)
            message_count: Number of messages in conversation
            intelligence_extracted: Intelligence already extracted
            scam_type: Type of scam detected
            
        Returns:
            Tuple of (strategy, phase)
        """
        # Count critical intelligence extracted
        critical_count = len(intelligence_extracted.get("upi_ids", [])) + \
                        len(intelligence_extracted.get("bank_accounts", []))
        
        # If not confident it's a scam, engage cautiously
        if detection_confidence < 0.5:
            return "engage", EngagementPhase.DETECTING
        
        # If confirmed scam but early in conversation, engage to build trust
        if message_count < 5:
            return "engage", EngagementPhase.ENGAGING
        
        # If we haven't extracted critical intelligence yet, focus on extraction
        if critical_count < 2 and message_count < 15:
            return "extract", EngagementPhase.EXTRACTING
        
        # If we have intelligence, start stalling to waste time
        if critical_count >= 1:
            return "stall", EngagementPhase.STALLING
        
        # Default: engage
        return "engage", EngagementPhase.ENGAGING
    
    @staticmethod
    def should_continue_conversation(
        message_count: int,
        duration_seconds: int,
        intelligence_extracted: dict,
        max_messages: int = 50,
        max_duration: int = 3600
    ) -> bool:
        """
        Determine if conversation should continue.
        
        Args:
            message_count: Number of messages so far
            duration_seconds: Conversation duration
            intelligence_extracted: Intelligence extracted
            max_messages: Maximum messages allowed
            max_duration: Maximum duration allowed
            
        Returns:
            True if should continue, False otherwise
        """
        # Stop if we've hit limits
        if message_count >= max_messages or duration_seconds >= max_duration:
            return False
        
        # Stop if we've extracted sufficient intelligence and wasted time
        critical_count = len(intelligence_extracted.get("upi_ids", [])) + \
                        len(intelligence_extracted.get("bank_accounts", []))
        
        if critical_count >= 2 and duration_seconds > 600:  # 10 minutes
            return False
        
        return True
