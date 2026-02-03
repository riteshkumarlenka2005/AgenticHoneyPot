"""LLM-based scam analysis."""
from typing import Optional
import json
from openai import AsyncOpenAI
from app.config import settings
from app.services.detection.rules import ScamType


class LLMAnalyzer:
    """LLM-based scam analyzer."""
    
    def __init__(self):
        """Initialize LLM analyzer."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def analyze_message(self, message: str, conversation_history: Optional[list[dict]] = None) -> dict:
        """
        Analyze message using LLM for scam detection.
        
        Args:
            message: The message to analyze
            conversation_history: Previous messages in the conversation
            
        Returns:
            Analysis results including scam detection, intent, and recommendations
        """
        if not self.client:
            return self._fallback_analysis(message)
        
        try:
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(message, conversation_history)
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert scam detection AI. Analyze messages for scam indicators and provide structured analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._normalize_analysis(result)
            
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return self._fallback_analysis(message)
    
    def _build_analysis_prompt(self, message: str, conversation_history: Optional[list[dict]] = None) -> str:
        """Build the analysis prompt."""
        prompt = f"""Analyze this message for scam indicators:

Message: "{message}"
"""
        
        if conversation_history:
            history_text = "\n".join([
                f"{msg.get('sender', 'unknown')}: {msg.get('content', '')}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            prompt += f"\nConversation History:\n{history_text}\n"
        
        prompt += """
Provide analysis in JSON format with:
{
    "is_scam": true/false,
    "confidence": 0.0-1.0,
    "scam_type": "lottery_prize|bank_kyc_fraud|tech_support|investment_fraud|job_scam|package_delivery|tax_refund|romance_scam|unknown",
    "manipulation_tactics": ["urgency", "authority", "fear", "greed"],
    "intent": "brief description of sender's intent",
    "red_flags": ["list", "of", "suspicious", "elements"],
    "recommended_response_strategy": "how the honeypot should respond"
}
"""
        return prompt
    
    def _normalize_analysis(self, result: dict) -> dict:
        """Normalize LLM analysis result."""
        return {
            "is_scam": result.get("is_scam", False),
            "confidence": min(max(result.get("confidence", 0.0), 0.0), 1.0),
            "scam_type": result.get("scam_type", "unknown"),
            "manipulation_tactics": result.get("manipulation_tactics", []),
            "intent": result.get("intent", ""),
            "red_flags": result.get("red_flags", []),
            "recommended_response_strategy": result.get("recommended_response_strategy", "engage")
        }
    
    def _fallback_analysis(self, message: str) -> dict:
        """Fallback analysis when LLM is not available."""
        return {
            "is_scam": False,
            "confidence": 0.0,
            "scam_type": "unknown",
            "manipulation_tactics": [],
            "intent": "Unable to analyze - LLM not configured",
            "red_flags": [],
            "recommended_response_strategy": "engage"
        }
