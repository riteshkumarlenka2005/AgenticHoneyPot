"""Base LLM provider interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
        
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    async def generate_structured_output(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output matching a JSON schema.
        
        Args:
            messages: List of message dicts
            schema: JSON schema for the output
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters
        
        Returns:
            Structured data matching the schema
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model being used."""
        pass
