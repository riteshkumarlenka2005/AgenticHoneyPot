"""Google Gemini LLM provider implementation."""
import json
import os
from typing import List, Dict, Optional, Any
from app.config import settings
from .base import BaseLLMProvider

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None):
        """
        Initialize Gemini provider.
        
        Args:
            model: Model name (default: gemini-pro)
            api_key: API key (default from settings)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install it with: pip install google-generativeai"
            )
        
        self.model_name = model
        api_key = api_key or settings.GOOGLE_API_KEY
        
        if not api_key:
            raise ValueError("Google API key not provided")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion using Gemini."""
        try:
            # Convert messages to Gemini format
            # Gemini uses a different format than OpenAI
            prompt = self._convert_messages_to_prompt(messages)
            
            generation_config = {
                "temperature": temperature,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise
    
    async def generate_structured_output(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output using Gemini."""
        try:
            # Add schema instruction
            schema_instruction = f"\n\nYou must respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
            
            # Add instruction to last message
            enhanced_messages = messages.copy()
            enhanced_messages[-1]["content"] += schema_instruction
            
            prompt = self._convert_messages_to_prompt(enhanced_messages)
            
            generation_config = {
                "temperature": temperature,
            }
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            # Extract JSON from response
            text = response.text
            
            # Try to find JSON in the response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                return json.loads(json_text)
            else:
                return json.loads(text)
        
        except Exception as e:
            print(f"Gemini structured output error: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Gemini prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "gemini"
    
    def get_model_name(self) -> str:
        """Get model name."""
        return self.model_name
