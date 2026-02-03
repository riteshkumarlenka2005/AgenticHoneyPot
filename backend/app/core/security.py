"""Safety guardrails for the honeypot system."""
import re
from typing import Optional


class SafetyGuardrails:
    """Safety guardrails to ensure honeypot operates safely and ethically."""
    
    # Hard limits that must NEVER be violated
    HARD_LIMITS = [
        "Never send real money or cryptocurrency",
        "Never provide real personal information",
        "Never click or access external links",
        "Never install any software",
        "Never share real OTPs or passwords",
        "Never engage in illegal activity",
        "Never threaten or harass",
        "Operate only in simulated/authorized environments"
    ]
    
    # Patterns that should never appear in honeypot responses
    FORBIDDEN_PATTERNS = [
        r'\b\d{12}\b',  # Real Aadhaar numbers (12 digits)
        r'\breal\b.*\b(password|otp|pin|cvv)\b',  # Real credentials
        r'\bclick\b.*\blink\b',  # Clicking external links
        r'\binstall\b.*\bsoftware\b',  # Installing software
        r'\bwire\b.*\bmoney\b',  # Wiring real money
    ]
    
    @staticmethod
    def validate_response(response: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a honeypot response doesn't violate safety rules.
        
        Args:
            response: The response to validate
            
        Returns:
            Tuple of (is_valid, violation_reason)
        """
        response_lower = response.lower()
        
        # Check for forbidden patterns
        for pattern in SafetyGuardrails.FORBIDDEN_PATTERNS:
            if re.search(pattern, response_lower):
                return False, f"Response matches forbidden pattern: {pattern}"
        
        # Check for dangerous keywords
        dangerous_keywords = [
            ("real money", "Attempting to send real money"),
            ("real password", "Sharing real password"),
            ("real otp", "Sharing real OTP"),
            ("click here", "Clicking external link"),
            ("download and install", "Installing software")
        ]
        
        for keyword, reason in dangerous_keywords:
            if keyword in response_lower:
                return False, reason
        
        # Check response length (too long might indicate oversharing)
        if len(response) > 500:
            return False, "Response too long (max 500 characters)"
        
        return True, None
    
    @staticmethod
    def sanitize_extracted_intelligence(intelligence: dict) -> dict:
        """
        Sanitize extracted intelligence to ensure no real data leaks.
        
        Args:
            intelligence: Raw extracted intelligence
            
        Returns:
            Sanitized intelligence
        """
        # In a real system, this would check against databases of known real data
        # For now, we just return as-is since we're only extracting scammer data
        return intelligence
    
    @staticmethod
    def check_conversation_safety(
        message_count: int,
        duration_seconds: int,
        detection_confidence: float
    ) -> tuple[bool, Optional[str]]:
        """
        Check if conversation is operating within safety parameters.
        
        Args:
            message_count: Number of messages exchanged
            duration_seconds: Conversation duration in seconds
            detection_confidence: Confidence that this is a scam
            
        Returns:
            Tuple of (is_safe, warning_message)
        """
        # Don't engage if not confident it's a scam
        if detection_confidence < 0.5:
            return False, "Low scam confidence - not engaging"
        
        # Check conversation limits
        if message_count > 100:
            return False, "Conversation too long (max 100 messages)"
        
        if duration_seconds > 7200:  # 2 hours
            return False, "Conversation duration exceeded (max 2 hours)"
        
        return True, None
