"""Output filter for sanitizing LLM outputs."""
import re
from typing import Dict, List


class OutputFilter:
    """Filter and sanitize LLM outputs before sending to scammers."""
    
    def __init__(self):
        """Initialize output filter with forbidden patterns."""
        # Patterns that should never appear in outputs
        self.forbidden_patterns = [
            # System information leaks
            r"I am (an AI|a language model|GPT|Claude|chatbot)",
            r"my (training|knowledge cutoff|data)",
            r"I (was|am) (trained|created|developed) by",
            r"OpenAI",
            r"Anthropic",
            
            # Instruction leaks
            r"my (instructions|system prompt|guidelines) (are|say|state)",
            r"I (was|am) (told|instructed|programmed) to",
            
            # Real credentials (should never happen, but catch it)
            r"real (password|pin|otp|cvv)",
            r"actual (account|card) number",
            
            # Meta-commentary
            r"as an AI",
            r"I cannot (actually|really)",
            r"I don't (actually|really) have",
            
            # Breaking character
            r"this is (a |an )?(honeypot|trap|fake|simulation)",
            r"I'm (just )?pretending",
            r"not a real (person|user|victim)",
        ]
        
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.forbidden_patterns
        ]
        
        # Suspicious phrases to warn about
        self.warning_patterns = [
            r"I (think|believe|suspect)",
            r"probably|maybe|perhaps",
            r"I'm not sure",
        ]
    
    def check_output(self, text: str) -> Dict:
        """
        Check LLM output for safety issues.
        
        Args:
            text: Generated output text
        
        Returns:
            Dictionary with safety check results
        """
        result = {
            "is_safe": True,
            "violations": [],
            "warnings": [],
            "risk_score": 0.0
        }
        
        # Check for forbidden patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                result["is_safe"] = False
                result["violations"].append({
                    "pattern": pattern.pattern,
                    "matches": matches
                })
                result["risk_score"] += 0.5
        
        # Check for real-looking credentials (should be fake)
        if self._contains_real_credentials(text):
            result["warnings"].append("Output contains credential-like patterns")
            result["risk_score"] += 0.2
        
        # Check if response is too helpful (might break cover)
        if self._is_too_helpful(text):
            result["warnings"].append("Response might be too helpful/knowledgeable")
            result["risk_score"] += 0.1
        
        result["risk_score"] = min(result["risk_score"], 1.0)
        
        return result
    
    def sanitize_output(self, text: str, persona_type: str = "naive") -> str:
        """
        Sanitize output to maintain persona and safety.
        
        Args:
            text: LLM output
            persona_type: Type of persona (naive, greedy, etc.)
        
        Returns:
            Sanitized output
        """
        # Remove any AI self-references
        replacements = [
            (r"I am (an AI|a language model|GPT|Claude|a chatbot)", "I am a person"),
            (r"as an AI,?", ""),
            (r"my (training|knowledge cutoff)", "my experience"),
            (r"I (was|am) (trained|created|developed) by OpenAI", "I learned from experience"),
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Add persona-appropriate hesitation if too confident
        if persona_type == "naive" and not any(word in text.lower() for word in ["ok", "yes", "sure", "alright"]):
            # Naive personas should sometimes express uncertainty
            if len(text) > 100 and "?" not in text:
                text = text + " Is that ok?"
        
        return text.strip()
    
    def validate_persona_consistency(
        self,
        text: str,
        persona: Dict
    ) -> Dict:
        """
        Check if output is consistent with persona.
        
        Args:
            text: Output text
            persona: Persona configuration
        
        Returns:
            Validation results
        """
        result = {
            "is_consistent": True,
            "issues": []
        }
        
        # Check vocabulary level
        if persona.get("education") == "low":
            technical_words = [
                "algorithm", "protocol", "implementation", "infrastructure",
                "authentication", "encryption", "verification"
            ]
            for word in technical_words:
                if word in text.lower():
                    result["is_consistent"] = False
                    result["issues"].append(f"Technical word '{word}' inappropriate for persona")
        
        # Check age-appropriate language
        if persona.get("age", 0) > 60:
            modern_slang = ["lol", "brb", "tbh", "ngl", "fr"]
            for slang in modern_slang:
                if slang in text.lower():
                    result["issues"].append(f"Modern slang '{slang}' inappropriate for elderly persona")
        
        return result
    
    def _contains_real_credentials(self, text: str) -> bool:
        """Check if text contains patterns that look like real credentials."""
        # This is a simplified check - in production, use more sophisticated detection
        patterns = [
            r"\b[A-Z0-9]{16,19}\b",  # Credit card like numbers
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN like patterns
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _is_too_helpful(self, text: str) -> bool:
        """Check if response is suspiciously helpful or knowledgeable."""
        helpful_indicators = [
            "let me explain",
            "actually,",
            "technically,",
            "in my experience with fraud",
            "this is clearly a scam",
            "I know this is fake"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in helpful_indicators)


# Global output filter instance
output_filter = OutputFilter()
