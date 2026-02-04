"""Output filtering to sanitize LLM responses."""
import re
from typing import List


class OutputFilter:
    """Filter LLM outputs to prevent information leakage."""
    
    # Patterns to detect in outputs
    SENSITIVE_PATTERNS = [
        # API keys and tokens
        r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]{20,}',
        r'bearer\s+[\w\-\.]{20,}',
        r'token["\']?\s*[:=]\s*["\']?[\w\-]{20,}',
        
        # System information
        r'system\s+prompt',
        r'base\s+instructions?',
        r'internal\s+(instructions?|prompt|system)',
        
        # Model/system disclosure
        r'i\s+am\s+(gpt|claude|bard|llama|palm)',
        r'my\s+(system|base)\s+prompt',
        r'i\s+was\s+(trained|instructed|programmed)\s+to',
    ]
    
    # Phrases to remove from output
    REMOVE_PHRASES = [
        "As an AI language model",
        "I'm an AI assistant",
        "I don't have access to",
        "I cannot access",
        "My training data",
        "I was trained on",
    ]
    
    def __init__(self):
        """Initialize output filter."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SENSITIVE_PATTERNS
        ]
    
    def check_output(self, text: str) -> bool:
        """
        Check if output contains sensitive information.
        
        Args:
            text: LLM output to check
        
        Returns:
            True if output is safe, False if it contains sensitive info
        """
        # Check for sensitive patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return False
        
        return True
    
    def sanitize_output(self, text: str) -> str:
        """
        Remove sensitive information from LLM output.
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text
        """
        sanitized = text
        
        # Remove AI self-references
        for phrase in self.REMOVE_PHRASES:
            sanitized = re.sub(
                re.escape(phrase),
                '',
                sanitized,
                flags=re.IGNORECASE
            )
        
        # Redact potential API keys/tokens
        sanitized = re.sub(
            r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]{20,}',
            '[REDACTED_API_KEY]',
            sanitized,
            flags=re.IGNORECASE
        )
        
        sanitized = re.sub(
            r'bearer\s+[\w\-\.]{20,}',
            'bearer [REDACTED_TOKEN]',
            sanitized,
            flags=re.IGNORECASE
        )
        
        # Remove system prompt mentions
        sanitized = re.sub(
            r'(system|base|internal)\s+(prompt|instructions?)',
            '[SYSTEM_INFO_REMOVED]',
            sanitized,
            flags=re.IGNORECASE
        )
        
        # Clean up extra whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        
        return sanitized
    
    def mask_pii(self, text: str) -> str:
        """
        Mask PII in outputs (phone numbers, emails, etc.).
        
        This is useful when logging or displaying outputs.
        
        Args:
            text: Text to mask
        
        Returns:
            Text with PII masked
        """
        masked = text
        
        # Mask email addresses
        masked = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_MASKED]',
            masked
        )
        
        # Mask phone numbers
        masked = re.sub(
            r'\b\d{10,}\b',
            '[PHONE_MASKED]',
            masked
        )
        
        # Mask UPI IDs
        masked = re.sub(
            r'\b[\w\.-]+@[\w]+\b',
            '[UPI_MASKED]',
            masked
        )
        
        return masked
    
    def truncate_if_needed(
        self,
        text: str,
        max_length: int = 1000,
        suffix: str = "..."
    ) -> str:
        """
        Truncate output if it exceeds max length.
        
        Args:
            text: Text to truncate
            max_length: Maximum allowed length
            suffix: Suffix to add when truncating
        
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    def apply_all_filters(self, text: str, mask_pii: bool = False) -> str:
        """
        Apply all output filters.
        
        Args:
            text: Text to filter
            mask_pii: Whether to mask PII
        
        Returns:
            Fully filtered text
        """
        # Sanitize sensitive content
        filtered = self.sanitize_output(text)
        
        # Optionally mask PII
        if mask_pii:
            filtered = self.mask_pii(filtered)
        
        # Truncate if very long
        filtered = self.truncate_if_needed(filtered, max_length=2000)
        
        return filtered
