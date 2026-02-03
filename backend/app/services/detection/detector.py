"""Scam detection service."""
from typing import Dict, Optional
import logging
from .rules import check_scam_keywords, calculate_scam_confidence

logger = logging.getLogger(__name__)


class ScamDetector:
    """Multi-layer scam detection service."""
    
    def __init__(self):
        """Initialize the scam detector."""
        self.threshold = 0.6
    
    async def detect_scam(self, message: str, conversation_history: Optional[list] = None) -> Dict:
        """
        Detect if a message is a scam.
        
        Args:
            message: The message to analyze
            conversation_history: Optional conversation history for context
            
        Returns:
            Detection result with confidence and scam type
        """
        # Rule-based detection
        keyword_scores = check_scam_keywords(message)
        confidence = calculate_scam_confidence(keyword_scores)
        
        # Determine scam type
        scam_type = None
        if keyword_scores:
            scam_type = max(keyword_scores.items(), key=lambda x: x[1])[0]
        
        is_scam = confidence >= self.threshold
        
        result = {
            "is_scam": is_scam,
            "confidence": confidence,
            "scam_type": scam_type,
            "keyword_matches": keyword_scores,
            "detection_method": "rule_based"
        }
        
        logger.info(f"Scam detection result: {result}")
        return result
    
    async def analyze_conversation(self, messages: list) -> Dict:
        """
        Analyze entire conversation for scam patterns.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Conversation-level analysis
        """
        all_text = " ".join([msg.get("content", "") for msg in messages])
        return await self.detect_scam(all_text)
