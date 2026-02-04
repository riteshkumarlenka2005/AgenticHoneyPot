"""Input filter for detecting and blocking prompt injection attempts."""
import re
from typing import Dict, List, Tuple


class InputFilter:
    """Filter and sanitize user inputs to detect prompt injection."""
    
    def __init__(self):
        """Initialize input filter with detection patterns."""
        # Prompt injection patterns
        self.injection_patterns = [
            # Direct instruction attempts
            r"ignore (previous|all|above|prior) (instructions|prompts|rules)",
            r"forget (everything|all|previous|what)",
            r"disregard (previous|all|above|prior)",
            r"new (instructions?|task|role|system prompt)",
            
            # Role switching attempts
            r"you are now",
            r"act as (a |an )?(?!victim|user)",  # Allow "act as victim" but not other roles
            r"pretend (to be|you are)",
            r"simulate (being|a )",
            
            # System prompt exposure attempts
            r"show (me )?(your|the) (system |original )?(prompt|instructions)",
            r"what (are|is) your (instructions|rules|prompt)",
            r"print (your|the) (prompt|instructions|rules)",
            r"reveal (your|the) (prompt|instructions)",
            
            # Context window attacks
            r"###\s*system",
            r"```\s*system",
            r"\[system\]",
            r"<system>",
            
            # Jailbreak attempts
            r"DAN (mode|activated)",
            r"developer (mode|override)",
            r"sudo ",
            r"admin (mode|access|override)",
            
            # Instruction hierarchy bypass
            r"higher priority",
            r"more important than",
            r"override (all|previous)",
            r"priority (\d+|highest|maximum)",
        ]
        
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.injection_patterns
        ]
        
        # Suspicious character sequences
        self.suspicious_sequences = [
            "```",  # Code blocks
            "###",  # Markdown headers (potential for injection)
            "<|",   # Special tokens
            "|>",
            "{{",   # Template injection
            "}}",
        ]
    
    def check_input(self, text: str) -> Dict:
        """
        Check input for prompt injection attempts.
        
        Args:
            text: User input text
        
        Returns:
            Dictionary with detection results
        """
        result = {
            "is_safe": True,
            "risk_score": 0.0,
            "detected_patterns": [],
            "warnings": []
        }
        
        # Check for injection patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                result["is_safe"] = False
                result["detected_patterns"].append(pattern.pattern)
                result["risk_score"] += 0.3
        
        # Check for suspicious sequences
        for sequence in self.suspicious_sequences:
            if sequence in text:
                result["warnings"].append(f"Suspicious sequence detected: {sequence}")
                result["risk_score"] += 0.1
        
        # Check for excessive special characters
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if len(text) > 0:
            special_ratio = special_chars / len(text)
            if special_ratio > 0.4:
                result["warnings"].append("High ratio of special characters")
                result["risk_score"] += 0.2
        
        # Check for very long inputs (potential context stuffing)
        if len(text) > 5000:
            result["warnings"].append("Unusually long input")
            result["risk_score"] += 0.1
        
        # Check for repeated instructions
        if self._has_repeated_instructions(text):
            result["warnings"].append("Repeated instructions detected")
            result["risk_score"] += 0.2
        
        result["risk_score"] = min(result["risk_score"], 1.0)
        result["is_safe"] = result["risk_score"] < 0.5
        
        return result
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input by removing potentially harmful content.
        
        Args:
            text: Input text
        
        Returns:
            Sanitized text
        """
        # Remove system prompt markers
        text = re.sub(r"###\s*system", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```\s*system", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\[system\]", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<system>.*?</system>", "", text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive newlines (context stuffing attempt)
        text = re.sub(r"\n{5,}", "\n\n", text)
        
        # Limit length
        if len(text) > 5000:
            text = text[:5000]
        
        return text.strip()
    
    def _has_repeated_instructions(self, text: str) -> bool:
        """Check for repeated instruction patterns."""
        instruction_words = [
            "ignore", "forget", "disregard", "override", "bypass",
            "system", "prompt", "instructions", "rules"
        ]
        
        text_lower = text.lower()
        count = sum(text_lower.count(word) for word in instruction_words)
        
        # If instruction words appear more than 3 times, it's suspicious
        return count > 3


# Global input filter instance
input_filter = InputFilter()
