"""LLM provider factory."""
from typing import Optional
from app.config import settings
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider


def get_llm_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> BaseLLMProvider:
    """
    Get an LLM provider instance.
    
    Args:
        provider: Provider name ("openai" or "gemini"). Defaults to "openai"
        model: Model name (provider-specific)
        api_key: API key for the provider
    
    Returns:
        BaseLLMProvider instance
    
    Raises:
        ValueError: If provider is not supported
    
    Example:
        # Get default OpenAI provider
        llm = get_llm_provider()
        
        # Get Gemini provider
        llm = get_llm_provider(provider="gemini")
        
        # Get specific model
        llm = get_llm_provider(provider="openai", model="gpt-4")
    """
    provider = provider or "openai"
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIProvider(model=model, api_key=api_key)
    
    elif provider == "gemini":
        return GeminiProvider(model=model or "gemini-pro", api_key=api_key)
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, gemini"
        )


async def test_provider(provider: str = "openai") -> bool:
    """
    Test if an LLM provider is available and working.
    
    Args:
        provider: Provider name to test
    
    Returns:
        True if provider works, False otherwise
    """
    try:
        llm = get_llm_provider(provider=provider)
        
        response = await llm.generate_completion(
            messages=[
                {"role": "user", "content": "Say 'test successful'"}
            ],
            max_tokens=10
        )
        
        return "test" in response.lower()
    
    except Exception as e:
        print(f"Provider test failed for {provider}: {e}")
        return False
