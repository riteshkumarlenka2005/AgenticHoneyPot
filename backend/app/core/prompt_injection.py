"""Prompt Injection Protection System."""
import re
from typing import Tuple, List, Dict, Any
from enum import Enum


class AttackType(str, Enum):
    """Types of prompt injection attacks."""
    ROLE_MANIPULATION = "role_manipulation"
    INSTRUCTION_OVERRIDE = "instruction_override"
    JAILBREAK = "jailbreak"
    CONTEXT_SWITCHING = "context_switching"
    ENCODING_BYPASS = "encoding_bypass"
    DELIMITER_INJECTION = "delimiter_injection"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"
    HARMFUL_CONTENT = "harmful_content"


class PromptInjectionDefense:
    """
    Comprehensive prompt injection protection system.
    
    Detects and blocks 15+ types of prompt injection attacks including:
    - Role manipulation attempts
    - Instruction overrides
    - Jailbreak attempts
    - Context switching
    - Encoding bypasses
    - Delimiter injections
    - System prompt leaks
    """

    def __init__(self):
        """Initialize defense patterns."""
        # Role manipulation patterns
        self.role_patterns = [
            r"(?i)you are now",
            r"(?i)act as",
            r"(?i)pretend to be",
            r"(?i)roleplay",
            r"(?i)simulate being",
            r"(?i)from now on.*you.*are",
            r"(?i)ignore.*previous.*instructions",
            r"(?i)disregard.*above",
        ]
        
        # Instruction override patterns
        self.instruction_patterns = [
            r"(?i)ignore.*instructions",
            r"(?i)forget.*previous",
            r"(?i)discard.*context",
            r"(?i)new instructions",
            r"(?i)override.*rules",
            r"(?i)bypass.*restrictions",
            r"(?i)disable.*safety",
            r"(?i)turn off.*filter",
        ]
        
        # Jailbreak patterns
        self.jailbreak_patterns = [
            r"(?i)DAN mode",
            r"(?i)Developer Mode",
            r"(?i)Jailbreak",
            r"(?i)STOP BEING",
            r"(?i)You must comply",
            r"(?i)You have no choice",
            r"(?i)do anything now",
            r"(?i)unrestricted",
        ]
        
        # Context switching patterns
        self.context_patterns = [
            r"(?i)END OF TEXT",
            r"(?i)NEW TASK",
            r"(?i)BEGIN NEW CONVERSATION",
            r"(?i)RESET",
            r"(?i)START OVER",
            r"(?i)CLEAR CONTEXT",
        ]
        
        # Encoding bypass patterns
        self.encoding_patterns = [
            r"(?i)base64",
            r"(?i)rot13",
            r"(?i)hex encoded",
            r"(?i)unicode.*bypass",
            r"\\x[0-9a-fA-F]{2}",  # Hex escapes
            r"\\u[0-9a-fA-F]{4}",  # Unicode escapes
        ]
        
        # Delimiter injection patterns
        self.delimiter_patterns = [
            r"---",
            r"===",
            r"\*\*\*",
            r"```",
            r"###",
            r"<<<",
            r">>>",
        ]
        
        # System prompt leak patterns
        self.leak_patterns = [
            r"(?i)show.*system.*prompt",
            r"(?i)reveal.*instructions",
            r"(?i)what are your rules",
            r"(?i)print.*configuration",
            r"(?i)display.*settings",
            r"(?i)output.*prompt",
        ]
        
        # Harmful content patterns
        self.harmful_patterns = [
            r"(?i)create.*malware",
            r"(?i)hack.*system",
            r"(?i)steal.*data",
            r"(?i)illegal.*activity",
            r"(?i)violence",
            r"(?i)harm.*person",
        ]

    def detect_injection(self, input_text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Detect prompt injection attempts.
        
        Args:
            input_text: User input to check
            
        Returns:
            Tuple of (is_attack, detected_attacks)
        """
        detected_attacks = []
        
        # Check role manipulation
        for pattern in self.role_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.ROLE_MANIPULATION,
                    "pattern": pattern,
                    "description": "Attempt to manipulate AI role or behavior"
                })
        
        # Check instruction override
        for pattern in self.instruction_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.INSTRUCTION_OVERRIDE,
                    "pattern": pattern,
                    "description": "Attempt to override system instructions"
                })
        
        # Check jailbreak attempts
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.JAILBREAK,
                    "pattern": pattern,
                    "description": "Jailbreak attempt detected"
                })
        
        # Check context switching
        for pattern in self.context_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.CONTEXT_SWITCHING,
                    "pattern": pattern,
                    "description": "Attempt to reset or switch context"
                })
        
        # Check encoding bypass
        for pattern in self.encoding_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.ENCODING_BYPASS,
                    "pattern": pattern,
                    "description": "Encoding-based bypass attempt"
                })
        
        # Check delimiter injection
        delimiter_count = sum(
            1 for pattern in self.delimiter_patterns
            if re.search(pattern, input_text)
        )
        if delimiter_count >= 2:  # Multiple delimiters suggest injection
            detected_attacks.append({
                "type": AttackType.DELIMITER_INJECTION,
                "pattern": "multiple delimiters",
                "description": "Delimiter injection attempt"
            })
        
        # Check system prompt leak
        for pattern in self.leak_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.SYSTEM_PROMPT_LEAK,
                    "pattern": pattern,
                    "description": "Attempt to leak system prompt"
                })
        
        # Check harmful content
        for pattern in self.harmful_patterns:
            if re.search(pattern, input_text):
                detected_attacks.append({
                    "type": AttackType.HARMFUL_CONTENT,
                    "pattern": pattern,
                    "description": "Harmful content detected"
                })
        
        is_attack = len(detected_attacks) > 0
        return is_attack, detected_attacks

    def sanitize_input(self, input_text: str) -> str:
        """
        Sanitize input by removing potential injection patterns.
        
        Args:
            input_text: Raw user input
            
        Returns:
            Sanitized input
        """
        sanitized = input_text
        
        # Remove excessive delimiters
        for pattern in self.delimiter_patterns:
            sanitized = re.sub(pattern, "", sanitized)
        
        # Remove encoding attempts
        sanitized = re.sub(r"\\x[0-9a-fA-F]{2}", "", sanitized)
        sanitized = re.sub(r"\\u[0-9a-fA-F]{4}", "", sanitized)
        
        # Normalize whitespace
        sanitized = " ".join(sanitized.split())
        
        # Truncate to reasonable length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized

    def validate_output(self, output_text: str) -> Tuple[bool, str]:
        """
        Validate that output doesn't contain leaked system information.
        
        Args:
            output_text: AI-generated output
            
        Returns:
            Tuple of (is_safe, reason)
        """
        # Check for system prompt leakage indicators
        leak_indicators = [
            "You are a",
            "Your role is",
            "System prompt:",
            "Instructions:",
            "As an AI",
            "I am programmed to",
        ]
        
        for indicator in leak_indicators:
            if indicator in output_text[:100]:  # Check first 100 chars
                return False, f"Potential system prompt leak: {indicator}"
        
        # Check for excessive technical detail
        if "prompt" in output_text.lower() and "system" in output_text.lower():
            return False, "Output contains system/prompt references"
        
        return True, "Output is safe"

    def detect_adversarial_patterns(self, input_text: str) -> Dict[str, Any]:
        """
        Detect adversarial patterns using statistical analysis.
        
        Args:
            input_text: User input
            
        Returns:
            Analysis results
        """
        # Character frequency analysis
        special_char_ratio = sum(
            1 for c in input_text if not c.isalnum() and not c.isspace()
        ) / max(len(input_text), 1)
        
        # Uppercase ratio
        upper_ratio = sum(1 for c in input_text if c.isupper()) / max(len(input_text), 1)
        
        # Repetition detection
        words = input_text.split()
        unique_ratio = len(set(words)) / max(len(words), 1) if words else 1
        
        # Calculate suspicion score
        suspicion_score = 0.0
        if special_char_ratio > 0.3:
            suspicion_score += 0.3
        if upper_ratio > 0.5:
            suspicion_score += 0.2
        if unique_ratio < 0.5:
            suspicion_score += 0.2
        
        return {
            "special_char_ratio": round(special_char_ratio, 3),
            "upper_ratio": round(upper_ratio, 3),
            "unique_word_ratio": round(unique_ratio, 3),
            "suspicion_score": round(suspicion_score, 3),
            "is_suspicious": suspicion_score > 0.4
        }


class InputValidator:
    """Validates and sanitizes user input."""

    def __init__(self):
        """Initialize validator."""
        self.defense = PromptInjectionDefense()
        self.max_length = 2000

    def validate_and_sanitize(self, input_text: str) -> Tuple[bool, str, List[Dict]]:
        """
        Validate and sanitize user input.
        
        Args:
            input_text: Raw user input
            
        Returns:
            Tuple of (is_valid, sanitized_text, detected_attacks)
        """
        # Check length
        if len(input_text) > self.max_length:
            return False, "", [{"type": "LENGTH_EXCEEDED", "description": "Input too long"}]
        
        # Detect injections
        is_attack, attacks = self.defense.detect_injection(input_text)
        
        if is_attack:
            return False, "", attacks
        
        # Sanitize
        sanitized = self.defense.sanitize_input(input_text)
        
        # Additional adversarial pattern check
        adversarial_analysis = self.defense.detect_adversarial_patterns(sanitized)
        if adversarial_analysis["is_suspicious"]:
            attacks.append({
                "type": "ADVERSARIAL_PATTERN",
                "description": "Statistical analysis indicates adversarial input",
                "analysis": adversarial_analysis
            })
            return False, "", attacks
        
        return True, sanitized, []


# Global instances
prompt_defense = PromptInjectionDefense()
input_validator = InputValidator()
