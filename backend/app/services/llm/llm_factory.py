"""LLM Factory for provider switching."""
from typing import Dict, Any, List, Optional
from enum import Enum
import openai
from app.config import settings
from .gemini_client import GeminiClient, get_gemini_client


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"


class LLMClient:
    """Abstract LLM client interface."""

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate completion."""
        raise NotImplementedError


class OpenAIClient(LLMClient):
    """OpenAI LLM client wrapper."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        openai.api_key = self.api_key

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}",
                "content": None
            }


class LLMFactory:
    """
    Factory for creating and managing LLM clients.
    
    Supports switching between OpenAI and Google Gemini
    based on configuration or runtime selection.
    """

    def __init__(self, default_provider: Optional[LLMProvider] = None):
        """
        Initialize LLM factory.
        
        Args:
            default_provider: Default provider to use
        """
        self.default_provider = default_provider or LLMProvider.OPENAI
        self._clients: Dict[LLMProvider, LLMClient] = {}

    def get_client(self, provider: Optional[LLMProvider] = None) -> LLMClient:
        """
        Get LLM client for specified provider.
        
        Args:
            provider: Provider to use (uses default if not specified)
            
        Returns:
            LLM client instance
        """
        provider = provider or self.default_provider
        
        # Check cache
        if provider in self._clients:
            return self._clients[provider]
        
        # Create client
        if provider == LLMProvider.OPENAI:
            client = OpenAIClient()
        elif provider == LLMProvider.GEMINI:
            client = get_gemini_client()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Cache client
        self._clients[provider] = client
        
        return client

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        provider: Optional[LLMProvider] = None,
    ) -> Dict[str, Any]:
        """
        Generate completion using specified or default provider.
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            provider: LLM provider to use
            
        Returns:
            Completion response
        """
        client = self.get_client(provider)
        return await client.generate_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def generate_with_fallback(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        primary_provider: Optional[LLMProvider] = None,
        fallback_provider: Optional[LLMProvider] = None,
    ) -> Dict[str, Any]:
        """
        Generate completion with automatic fallback.
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            primary_provider: Primary provider to try
            fallback_provider: Fallback provider if primary fails
            
        Returns:
            Completion response
        """
        # Determine providers
        primary = primary_provider or self.default_provider
        fallback = fallback_provider or (
            LLMProvider.GEMINI if primary == LLMProvider.OPENAI
            else LLMProvider.OPENAI
        )
        
        # Try primary
        result = await self.generate_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=primary
        )
        
        # If primary fails, try fallback
        if not result.get("success"):
            result = await self.generate_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                provider=fallback
            )
            result["used_fallback"] = True
        else:
            result["used_fallback"] = False
        
        return result

    def set_default_provider(self, provider: LLMProvider) -> None:
        """
        Set default LLM provider.
        
        Args:
            provider: Provider to set as default
        """
        self.default_provider = provider

    def get_available_providers(self) -> List[LLMProvider]:
        """
        Get list of available providers based on configuration.
        
        Returns:
            List of available providers
        """
        available = []
        
        if settings.OPENAI_API_KEY:
            available.append(LLMProvider.OPENAI)
        
        if settings.GOOGLE_API_KEY:
            available.append(LLMProvider.GEMINI)
        
        return available

    async def analyze_with_best_provider(
        self,
        text: str,
        task: str = "analyze"
    ) -> Dict[str, Any]:
        """
        Analyze text using the best available provider.
        
        Args:
            text: Text to analyze
            task: Analysis task
            
        Returns:
            Analysis results
        """
        # Build prompt
        prompts = {
            "analyze": f"Analyze the following message for scam indicators:\n\n{text}",
            "extract": f"Extract key information (phone numbers, UPI IDs, URLs, etc.) from:\n\n{text}",
            "classify": f"Classify the scam type of the following message:\n\n{text}",
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing potential scam messages."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Use fallback mechanism
        return await self.generate_with_fallback(
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )


# Global LLM factory instance
llm_factory = LLMFactory()


# Convenience function
async def generate_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    provider: Optional[LLMProvider] = None,
) -> Dict[str, Any]:
    """
    Convenience function for generating completions.
    
    Args:
        messages: Conversation messages
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        provider: LLM provider
        
    Returns:
        Completion response
    """
    return await llm_factory.generate_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        provider=provider
    )
