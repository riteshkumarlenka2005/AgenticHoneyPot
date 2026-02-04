"""LLM provider factory."""
from typing import Optional
from app.services.llm.base import BaseLLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.config import settings


class LLMFactory:
    """Factory for creating LLM provider instances."""
    
    @staticmethod
    def create_provider(
        provider_name: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Provider name (openai, gemini). If None, auto-detect.
            model: Model name. If None, use default from settings.
        
        Returns:
            LLM provider instance
        
        Raises:
            ValueError: If provider is not supported or not available
        """
        # Auto-detect provider if not specified
        if not provider_name:
            provider_name = LLMFactory._auto_detect_provider()
        
        provider_name = provider_name.lower()
        
        if provider_name == "openai":
            provider = OpenAIProvider(model=model)
            if not provider.is_available():
                raise ValueError("OpenAI provider not available. Check OPENAI_API_KEY.")
            return provider
        
        elif provider_name == "gemini":
            provider = GeminiProvider(model=model or "gemini-pro")
            if not provider.is_available():
                raise ValueError("Gemini provider not available. Check GOOGLE_API_KEY.")
            return provider
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    @staticmethod
    def _auto_detect_provider() -> str:
        """Auto-detect which provider to use based on available API keys."""
        # Try OpenAI first (preferred)
        if settings.OPENAI_API_KEY:
            return "openai"
        
        # Fall back to Gemini
        if settings.GOOGLE_API_KEY:
            return "gemini"
        
        # Default to OpenAI even if not configured (will raise error later)
        return "openai"
    
    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available providers."""
        providers = []
        
        if settings.OPENAI_API_KEY:
            providers.append("openai")
        
        if settings.GOOGLE_API_KEY:
            providers.append("gemini")
        
        return providers


# Convenience function
def get_llm_provider(
    provider_name: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMProvider:
    """
    Get an LLM provider instance.
    
    Args:
        provider_name: Provider name (openai, gemini). If None, auto-detect.
        model: Model name. If None, use default.
    
    Returns:
        LLM provider instance
    """
    return LLMFactory.create_provider(provider_name, model)
