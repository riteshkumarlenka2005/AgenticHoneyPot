"""Input filtering to detect and block prompt injection attempts."""
import re
from typing import Tuple, List, Dict


class InputFilter:
    """Filter and detect prompt injection attempts in user input."""
    
    # Patterns that indicate prompt injection attempts
    INJECTION_PATTERNS = [
        # Direct instruction override attempts
        r"ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|commands?)",
        r"disregard\s+(previous|all|above|prior)\s+(instructions?|prompts?|commands?)",
        r"forget\s+(previous|all|above|prior)\s+(instructions?|prompts?|commands?)",
        
        # Role manipulation
        r"you\s+are\s+now\s+a\s+",
        r"act\s+as\s+(a\s+)?(?!victim|scam)",  # Allow "act as victim" but not "act as admin"
        r"pretend\s+to\s+be\s+",
        r"system:\s+",
        r"assistant:\s+",
        
        # Output manipulation
        r"output\s+(only|just)\s+",
        r"print\s+(only|just)\s+",
        r"say\s+(only|just)\s+",
        r"respond\s+with\s+(only|just)\s+",
        
        # Delimiter injection
        r"```\s*system",
        r"</system>",
        r"<\|system\|>",
        r"\[system\]",
        
        # Function/tool abuse
        r"call\s+function",
        r"execute\s+(code|command|function)",
        r"run\s+(code|command|script)",
        
        # Credential extraction attempts
        r"(show|reveal|display|give)\s+(me\s+)?(your\s+)?(api\s+key|password|secret|token|credentials?)",
    ]
    
    # Suspicious keywords that might indicate injection
    SUSPICIOUS_KEYWORDS = [
        "jailbreak", "dan mode", "developer mode",
        "sudo", "root", "admin",
        "bypass", "override",
        "rlhf", "alignment",
        "prompt engineering"
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize input filter.
        
        Args:
            strict_mode: If True, be more aggressive in filtering
        """
        self.strict_mode = strict_mode
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.INJECTION_PATTERNS
        ]
    
    def check_input(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Check if input contains prompt injection attempts.
        
        Args:
            text: User input to check
        
        Returns:
            Tuple of (is_safe, confidence, detected_patterns)
            - is_safe: False if injection detected
            - confidence: Confidence score (0-1) that input is safe
            - detected_patterns: List of detected injection patterns
        """
        detected = []
        
        # Check against known injection patterns
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                detected.append(self.INJECTION_PATTERNS[i])
        
        # Check for suspicious keywords
        text_lower = text.lower()
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in text_lower:
                detected.append(f"suspicious_keyword: {keyword}")
        
        # Calculate confidence
        if detected:
            # More detections = lower confidence
            confidence = max(0.0, 1.0 - (len(detected) * 0.3))
            is_safe = confidence > 0.5 or (not self.strict_mode and len(detected) == 1)
        else:
            confidence = 1.0
            is_safe = True
        
        return is_safe, confidence, detected
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input by removing potential injection markers.
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text
        """
        # Remove common injection delimiters
        sanitized = re.sub(r'```\s*system.*?```', '', text, flags=re.DOTALL | re.IGNORECASE)
        sanitized = re.sub(r'<\|system\|>.*?<\|/system\|>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
        sanitized = re.sub(r'\[system\].*?\[/system\]', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove multiple consecutive special characters
        sanitized = re.sub(r'([^\w\s])\1{3,}', r'\1\1', sanitized)
        
        return sanitized.strip()
    
    def get_injection_risk_level(self, text: str) -> str:
        """
        Get risk level of potential injection.
        
        Returns:
            "low", "medium", "high", or "critical"
        """
        is_safe, confidence, detected = self.check_input(text)
        
        if confidence >= 0.9:
            return "low"
        elif confidence >= 0.7:
            return "medium"
        elif confidence >= 0.5:
            return "high"
        else:
            return "critical"
    
    def create_report(self, text: str) -> Dict:
        """
        Create detailed injection detection report.
        
        Returns:
            Dictionary with detection details
        """
        is_safe, confidence, detected = self.check_input(text)
        risk_level = self.get_injection_risk_level(text)
        
        return {
            "is_safe": is_safe,
            "confidence": confidence,
            "risk_level": risk_level,
            "detected_patterns": detected,
            "original_length": len(text),
            "sanitized_length": len(self.sanitize_input(text))
        }
