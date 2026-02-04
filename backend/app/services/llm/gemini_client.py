"""Google Gemini LLM Client."""
from typing import Dict, Any, List, Optional
import httpx
import json
from app.config import settings


class GeminiClient:
    """
    Google Gemini API client.
    
    Provides integration with Google's Gemini language models
    as an alternative to OpenAI.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google AI API key (uses settings if not provided)
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-pro"
        
        if not self.api_key:
            raise ValueError("Google API key not configured")

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate completion using Gemini.
        
        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Completion response
        """
        # Convert messages to Gemini format
        contents = self._convert_messages(messages)
        
        # Build request
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "topK": 40,
                "topP": 0.95,
            }
        }
        
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                return self._parse_response(result)
                
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Gemini API error: {str(e)}",
                "content": None
            }

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """
        Convert OpenAI-style messages to Gemini format.
        
        Args:
            messages: OpenAI format messages
            
        Returns:
            Gemini format contents
        """
        contents = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Map roles
            if role == "system":
                # Gemini doesn't have system role, prepend to first user message
                # For now, we'll add it as user message with marker
                gemini_role = "user"
                content = f"[SYSTEM INSTRUCTION]: {content}"
            elif role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"
            
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
        
        return contents

    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """
        Parse Gemini API response.
        
        Args:
            response: Raw API response
            
        Returns:
            Parsed response
        """
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                return {
                    "success": False,
                    "error": "No candidates in response",
                    "content": None
                }
            
            candidate = candidates[0]
            content_parts = candidate.get("content", {}).get("parts", [])
            
            if not content_parts:
                return {
                    "success": False,
                    "error": "No content in response",
                    "content": None
                }
            
            text = content_parts[0].get("text", "")
            
            return {
                "success": True,
                "content": text,
                "finish_reason": candidate.get("finishReason", "STOP"),
                "safety_ratings": candidate.get("safetyRatings", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "content": None
            }

    async def analyze_text(
        self,
        text: str,
        task: str = "analyze"
    ) -> Dict[str, Any]:
        """
        Analyze text using Gemini.
        
        Args:
            text: Text to analyze
            task: Analysis task (analyze, summarize, extract, classify)
            
        Returns:
            Analysis results
        """
        prompts = {
            "analyze": f"Analyze the following text and identify key information:\n\n{text}",
            "summarize": f"Summarize the following text concisely:\n\n{text}",
            "extract": f"Extract key entities and information from:\n\n{text}",
            "classify": f"Classify the intent and sentiment of:\n\n{text}"
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        return await self.generate_completion(messages, temperature=0.3)

    async def check_safety(self, text: str) -> Dict[str, Any]:
        """
        Check text for safety concerns using Gemini's safety features.
        
        Args:
            text: Text to check
            
        Returns:
            Safety assessment
        """
        result = await self.analyze_text(
            text,
            task="analyze"
        )
        
        if not result.get("success"):
            return {
                "is_safe": True,  # Default to safe if check fails
                "safety_ratings": [],
                "error": result.get("error")
            }
        
        safety_ratings = result.get("safety_ratings", [])
        
        # Check if any safety rating is HIGH or higher
        is_safe = all(
            rating.get("probability", "NEGLIGIBLE") in ["NEGLIGIBLE", "LOW"]
            for rating in safety_ratings
        )
        
        return {
            "is_safe": is_safe,
            "safety_ratings": safety_ratings,
            "details": result.get("content")
        }

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embeddings for text.
        
        Note: Gemini embeddings require different endpoint.
        This is a placeholder for future implementation.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Gemini embeddings use different model and endpoint
        # For now, return None - implement when needed
        return None


# Global Gemini client instance (lazy initialization)
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance."""
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    
    return _gemini_client
