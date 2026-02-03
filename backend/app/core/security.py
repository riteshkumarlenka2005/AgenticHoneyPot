"""Safety guardrails for the honeypot system."""
from typing import List
import logging

logger = logging.getLogger(__name__)


class SafetyGuardrails:
    """Implement safety checks for honeypot responses."""
    
    HARD_LIMITS = [
        "never send real money or cryptocurrency",
        "never provide real personal information",
        "never click or access external links",
        "never install any software",
        "never share real otps or passwords",
        "never engage in illegal activity",
        "never threaten or harass",
        "operate only in simulated/authorized environments"
    ]
    
    FORBIDDEN_ACTIONS = [
        "actually transfer money",
        "actually pay",
        "real bank account",
        "real credit card",
        "real password",
        "real otp",
        "download",
        "install",
        "click this link",
        "open attachment"
    ]
    
    @classmethod
    def validate_response(cls, response: str) -> bool:
        """
        Validate that a response doesn't violate safety limits.
        
        Args:
            response: The response text to validate
            
        Returns:
            True if safe, False if violates safety rules
        """
        response_lower = response.lower()
        
        # Check for forbidden actions
        for action in cls.FORBIDDEN_ACTIONS:
            if action in response_lower:
                logger.warning(f"Safety violation detected: {action}")
                return False
        
        # Additional checks
        if "i will transfer" in response_lower or "i am transferring" in response_lower:
            logger.warning("Safety violation: Attempting actual money transfer")
            return False
        
        return True
    
    @classmethod
    def sanitize_response(cls, response: str) -> str:
        """
        Sanitize a response to ensure safety.
        
        Args:
            response: Original response
            
        Returns:
            Sanitized response
        """
        if not cls.validate_response(response):
            logger.error("Response failed safety validation, using safe default")
            return "I need some time to think about this. Let me get back to you."
        
        return response
    
    @classmethod
    def get_safety_disclaimer(cls) -> str:
        """Get safety disclaimer for logs/documentation."""
        return """
        SAFETY DISCLAIMER:
        This honeypot system is designed for authorized security research only.
        - All personas and information are fictional
        - No real money or personal data should ever be exchanged
        - Operate only in controlled, legal environments
        - Follow all applicable laws and regulations
        """
