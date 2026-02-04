"""OpenAI LLM provider implementation."""
import json
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI
from app.config import settings
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name (default from settings)
            api_key: API key (default from settings)
        """
        self.model = model or settings.OPENAI_MODEL
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    async def generate_structured_output(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output using OpenAI."""
        try:
            # Add schema instruction to system message
            schema_instruction = f"\n\nYou must respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
            
            # Modify last user message or add system message
            enhanced_messages = messages.copy()
            if enhanced_messages and enhanced_messages[-1]["role"] == "user":
                enhanced_messages[-1]["content"] += schema_instruction
            else:
                enhanced_messages.append({
                    "role": "system",
                    "content": schema_instruction
                })
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=enhanced_messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                **kwargs
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        
        except Exception as e:
            print(f"OpenAI structured output error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openai"
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.model
