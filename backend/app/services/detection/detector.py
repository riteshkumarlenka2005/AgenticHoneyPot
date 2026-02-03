"""Main scam detection service."""
from typing import Optional
from app.services.detection.rules import detect_scam_type, detect_manipulation_tactics, calculate_scam_score
from app.services.detection.llm_analyzer import LLMAnalyzer


class ScamDetector:
    """Multi-layer scam detection service."""
    
    def __init__(self):
        """Initialize scam detector."""
        self.llm_analyzer = LLMAnalyzer()
    
    async def detect(self, message: str, conversation_history: Optional[list[dict]] = None) -> dict:
        """
        Detect if a message is a scam using multiple detection methods.
        
        Args:
            message: The message to analyze
            conversation_history: Previous messages in the conversation
            
        Returns:
            Detection results with confidence score and scam type
        """
        # Rule-based detection
        scam_type, type_confidence = detect_scam_type(message)
        manipulation_tactics = detect_manipulation_tactics(message)
        rule_score = calculate_scam_score(message)
        
        # LLM-based detection
        llm_analysis = await self.llm_analyzer.analyze_message(message, conversation_history)
        
        # Combine results (weighted average)
        final_confidence = (rule_score * 0.4) + (llm_analysis["confidence"] * 0.6)
        
        # Determine if it's a scam (threshold: 0.5)
        is_scam = final_confidence >= 0.5
        
        # Use LLM scam type if more confident, otherwise use rule-based
        if llm_analysis["confidence"] > type_confidence:
            final_scam_type = llm_analysis["scam_type"]
        else:
            final_scam_type = scam_type.value
        
        # Merge manipulation tactics
        all_tactics = list(set(manipulation_tactics + llm_analysis.get("manipulation_tactics", [])))
        
        return {
            "is_scam": is_scam,
            "confidence": final_confidence,
            "scam_type": final_scam_type,
            "manipulation_tactics": all_tactics,
            "rule_based": {
                "scam_type": scam_type.value,
                "confidence": type_confidence,
                "score": rule_score,
                "tactics": manipulation_tactics
            },
            "llm_based": llm_analysis,
            "recommended_strategy": llm_analysis.get("recommended_response_strategy", "engage")
        }
