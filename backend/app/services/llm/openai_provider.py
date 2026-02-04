"""OpenAI LLM provider implementation."""
from typing import List, Dict, Optional
from app.services.llm.base import BaseLLMProvider
from app.config import settings


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider for LLM operations."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name (default from settings)
        """
        self.model = model or settings.OPENAI_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                pass
    
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using OpenAI completion API."""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_with_messages(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
    
    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using OpenAI chat completion API."""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return f"openai:{self.model}"
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None and self.api_key is not None
