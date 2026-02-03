"""Intelligence extraction service."""
from typing import Dict, List
import logging
from ..detection.rules import extract_patterns

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """Extract intelligence from scammer messages."""
    
    def __init__(self):
        """Initialize intelligence extractor."""
        pass
    
    def extract_from_message(self, message: str) -> Dict[str, List[str]]:
        """
        Extract intelligence artifacts from a message.
        
        Args:
            message: The message to extract from
            
        Returns:
            Dictionary of extracted artifacts by type
        """
        extracted = extract_patterns(message)
        
        logger.info(f"Extracted {sum(len(v) for v in extracted.values())} artifacts")
        return extracted
    
    def extract_from_conversation(self, messages: list) -> Dict:
        """
        Extract all intelligence from a conversation.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Aggregated intelligence from all messages
        """
        all_artifacts = {
            "upi_ids": [],
            "phone_numbers": [],
            "ifsc_codes": [],
            "bank_accounts": [],
            "urls": [],
            "emails": []
        }
        
        for msg in messages:
            if msg.get("sender_type") == "scammer":
                content = msg.get("content", "")
                extracted = self.extract_from_message(content)
                
                # Map pattern types to output format
                mapping = {
                    "upi_id": "upi_ids",
                    "phone": "phone_numbers",
                    "ifsc_code": "ifsc_codes",
                    "bank_account": "bank_accounts",
                    "url": "urls",
                    "email": "emails"
                }
                
                for pattern_type, artifacts in extracted.items():
                    output_key = mapping.get(pattern_type)
                    if output_key:
                        all_artifacts[output_key].extend(artifacts)
        
        # Remove duplicates
        for key in all_artifacts:
            all_artifacts[key] = list(set(all_artifacts[key]))
        
        return all_artifacts
    
    def get_extraction_prompts(self, conversation_phase: str) -> List[str]:
        """
        Get prompts to steer conversation towards intelligence extraction.
        
        Args:
            conversation_phase: Current phase of conversation
            
        Returns:
            List of potential prompts/questions
        """
        prompts = {
            "initial": [
                "Yes, I'm interested! How do I proceed?",
                "This sounds great! What do I need to do?",
                "I want to claim this. What are the next steps?"
            ],
            "trust_building": [
                "I trust you. Please guide me.",
                "You seem genuine. I'll follow your instructions.",
                "Okay, I'm ready to proceed as you say."
            ],
            "extraction": [
                "Where should I send the money?",
                "What's your account number?",
                "Can you share your UPI ID?",
                "Which bank should I transfer to?",
                "What's the payment link?"
            ],
            "stalling": [
                "I'm trying to arrange the money...",
                "My bank is having issues, give me a moment...",
                "Can you send the details again? I didn't save them.",
                "Let me just confirm with my son first..."
            ]
        }
        
        return prompts.get(conversation_phase, prompts["initial"])
