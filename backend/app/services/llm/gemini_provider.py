"""Google Gemini LLM provider implementation."""
from typing import List, Dict, Optional
from app.services.llm.base import BaseLLMProvider
from app.config import settings


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider for LLM operations."""
    
    def __init__(self, model: str = "gemini-pro"):
        """
        Initialize Gemini provider.
        
        Args:
            model: Model name (default: gemini-pro)
        """
        self.model = model
        self.api_key = settings.GOOGLE_API_KEY
        self.client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
            except ImportError:
                pass
    
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Gemini API."""
        if not self.client:
            raise RuntimeError("Gemini client not initialized. Check API key and installation.")
        
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = await self.client.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text from conversation messages using Gemini."""
        if not self.client:
            raise RuntimeError("Gemini client not initialized. Check API key and installation.")
        
        # Convert messages to Gemini format
        # Gemini uses a simpler format - combine into a single prompt
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n\n".join(prompt_parts)
        
        return await self.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return f"gemini:{self.model}"
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self.client is not None and self.api_key is not None
