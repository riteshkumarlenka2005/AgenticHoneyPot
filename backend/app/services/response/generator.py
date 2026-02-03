"""Response generation service."""
from typing import Dict, Optional
import random
import logging

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generate honeypot responses."""
    
    def __init__(self):
        """Initialize response generator."""
        self.conversation_phases = [
            "initial_engagement",
            "trust_building",
            "information_extraction",
            "stalling",
            "final_extraction"
        ]
    
    async def generate_response(
        self,
        persona: Dict,
        scammer_message: str,
        conversation_history: list,
        extraction_targets: Optional[list] = None
    ) -> Dict:
        """
        Generate a honeypot response.
        
        Args:
            persona: The persona to use
            scammer_message: The scammer's message
            conversation_history: Previous messages
            extraction_targets: What to try to extract
            
        Returns:
            Response dictionary with message and metadata
        """
        # Determine conversation phase
        message_count = len(conversation_history)
        
        if message_count < 2:
            phase = "initial_engagement"
        elif message_count < 4:
            phase = "trust_building"
        elif message_count < 8:
            phase = "information_extraction"
        else:
            phase = "stalling"
        
        # Generate response based on phase
        response_text = self._generate_for_phase(
            phase, persona, scammer_message, extraction_targets
        )
        
        return {
            "message": response_text,
            "phase": phase,
            "persona": persona["name"],
            "strategy": self._get_strategy_for_phase(phase)
        }
    
    def _generate_for_phase(
        self,
        phase: str,
        persona: Dict,
        scammer_message: str,
        extraction_targets: Optional[list]
    ) -> str:
        """Generate response for specific phase."""
        name = persona["name"]
        
        responses = {
            "initial_engagement": [
                f"Hello! This is {name}. I received your message. Can you tell me more?",
                f"Hi, I'm {name}. This sounds interesting! Please explain further.",
                f"Dear Sir/Madam, I am {name}. I would like to know more about this opportunity."
            ],
            "trust_building": [
                "Thank you for explaining. I trust you will help me with this.",
                "You seem very professional. I appreciate your help!",
                "I am grateful for this opportunity. Please guide me step by step."
            ],
            "information_extraction": [
                "I'm ready to proceed! Where should I send the payment?",
                "What is your account number? I want to transfer now.",
                "Please share your UPI ID so I can make the payment immediately.",
                "Can you send me the payment link? I'm eager to complete this.",
                "What bank details do you need from me? And what are yours?"
            ],
            "stalling": [
                "I'm arranging the money... my bank app is slow today.",
                "Just a moment, I need to ask my son about the internet banking.",
                "Sorry for delay, the ATM was crowded. Can you resend the details?",
                "My phone battery died. What was your account number again?"
            ]
        }
        
        phase_responses = responses.get(phase, responses["initial_engagement"])
        return random.choice(phase_responses)
    
    def _get_strategy_for_phase(self, phase: str) -> str:
        """Get strategy description for phase."""
        strategies = {
            "initial_engagement": "Show interest and curiosity",
            "trust_building": "Express trust and willingness to comply",
            "information_extraction": "Directly ask for payment details",
            "stalling": "Delay while maintaining engagement",
            "final_extraction": "Make final attempts to get all details"
        }
        return strategies.get(phase, "Engage naturally")
