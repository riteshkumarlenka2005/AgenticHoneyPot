"""Intelligence extraction service."""
from typing import Optional
from app.services.extraction.patterns import (
    extract_all_intelligence,
    EXTRACTION_QUESTIONS
)
import random


class IntelligenceExtractor:
    """Service for extracting intelligence from scammer messages."""
    
    def __init__(self):
        """Initialize intelligence extractor."""
        self.extracted_types = set()
    
    def extract_from_message(self, message: str) -> dict:
        """
        Extract intelligence from a scammer message.
        
        Args:
            message: The scammer's message
            
        Returns:
            Dictionary of extracted intelligence with confidence scores
        """
        raw_extraction = extract_all_intelligence(message)
        
        # Build results with confidence scores
        results = {
            "artifacts": [],
            "summary": {}
        }
        
        # Process each type
        for artifact_type, values in raw_extraction.items():
            if values:
                results["summary"][artifact_type] = len(values)
                for value in values:
                    confidence = self._calculate_confidence(artifact_type, value)
                    results["artifacts"].append({
                        "type": artifact_type.rstrip('s'),  # Singular form
                        "value": value,
                        "confidence": confidence
                    })
                    self.extracted_types.add(artifact_type)
        
        return results
    
    def _calculate_confidence(self, artifact_type: str, value: str) -> float:
        """Calculate confidence score for extracted artifact."""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on type and value characteristics
        if artifact_type == "ifsc_codes":
            # IFSC codes have a strict format, so high confidence
            confidence = 0.95
        elif artifact_type == "upi_ids":
            # UPI IDs are fairly reliable
            confidence = 0.85
        elif artifact_type == "phone_numbers":
            # Phone numbers are reliable if formatted correctly
            confidence = 0.85
        elif artifact_type == "bank_accounts":
            # Account numbers can have false positives
            confidence = 0.75
        elif artifact_type == "urls":
            # URLs are usually reliable
            confidence = 0.80
        elif artifact_type == "emails":
            confidence = 0.80
        
        return confidence
    
    def get_next_extraction_question(self, conversation_context: dict) -> Optional[str]:
        """
        Get the next question to ask to extract specific intelligence.
        
        Args:
            conversation_context: Current conversation context
            
        Returns:
            Question string or None if no more questions needed
        """
        # Determine what we haven't extracted yet
        needed_types = []
        
        if "upi_ids" not in self.extracted_types:
            needed_types.append("upi_id")
        if "bank_accounts" not in self.extracted_types:
            needed_types.append("bank_account")
        if "phone_numbers" not in self.extracted_types:
            needed_types.append("phone")
        if "urls" not in self.extracted_types:
            needed_types.append("link")
        
        if not needed_types:
            return None
        
        # Prioritize: bank_account > upi_id > phone > link
        priority = ["bank_account", "upi_id", "phone", "link"]
        for ptype in priority:
            if ptype in needed_types:
                questions = EXTRACTION_QUESTIONS.get(ptype, [])
                return random.choice(questions) if questions else None
        
        return None
    
    def should_continue_extraction(self) -> bool:
        """Determine if we should continue trying to extract intelligence."""
        # Continue if we haven't extracted at least 2 critical pieces
        critical_extracted = sum(1 for t in ["upi_ids", "bank_accounts"] if t in self.extracted_types)
        return critical_extracted < 2
