"""Response generation service."""
from typing import Optional
import json
from openai import AsyncOpenAI
from app.config import settings
from app.services.persona.generator import PersonaGenerator


class ResponseGenerator:
    """Service for generating honeypot responses."""
    
    def __init__(self):
        """Initialize response generator."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.persona_generator = PersonaGenerator()
    
    async def generate_response(
        self,
        scammer_message: str,
        persona_context: dict,
        conversation_history: list[dict],
        strategy: str = "engage",
        extraction_hint: Optional[str] = None
    ) -> str:
        """
        Generate a honeypot response to a scammer message.
        
        Args:
            scammer_message: The latest message from the scammer
            persona_context: The persona being used
            conversation_history: Previous messages
            strategy: Response strategy (engage, extract, stall, exit)
            extraction_hint: Specific thing to try to extract
            
        Returns:
            Generated response text
        """
        if not self.client:
            return self._fallback_response(scammer_message, strategy)
        
        try:
            # Build conversation context
            messages = self._build_conversation_context(
                scammer_message,
                persona_context,
                conversation_history,
                strategy,
                extraction_hint
            )
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.8,  # Higher temperature for more natural variation
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Response generation error: {e}")
            return self._fallback_response(scammer_message, strategy)
    
    def _build_conversation_context(
        self,
        scammer_message: str,
        persona_context: dict,
        conversation_history: list[dict],
        strategy: str,
        extraction_hint: Optional[str]
    ) -> list[dict]:
        """Build conversation context for LLM."""
        # System prompt with persona and strategy
        system_prompt = persona_context.get("response_style_instructions", "")
        
        # Add strategy-specific instructions
        if strategy == "engage":
            system_prompt += "\n\nCurrent strategy: Show interest and ask clarifying questions. Be believable and cautious."
        elif strategy == "extract":
            system_prompt += "\n\nCurrent strategy: You're convinced and ready to proceed. Ask for specific details needed to complete the action."
            if extraction_hint:
                system_prompt += f"\n\nSpecifically try to get: {extraction_hint}"
        elif strategy == "stall":
            system_prompt += "\n\nCurrent strategy: You're interested but have concerns or difficulties. Ask questions, express confusion, or mention obstacles."
        elif strategy == "exit":
            system_prompt += "\n\nCurrent strategy: Politely disengage or stop responding."
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = "assistant" if msg.get("sender_type") == "honeypot" else "user"
            messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # Add current scammer message
        messages.append({
            "role": "user",
            "content": scammer_message
        })
        
        return messages
    
    def _fallback_response(self, scammer_message: str, strategy: str) -> str:
        """Generate fallback response when LLM is not available."""
        fallback_responses = {
            "engage": "I'm interested. Can you tell me more about this?",
            "extract": "Okay, I'm ready. What information do you need from me?",
            "stall": "I'm not sure I understand. Can you explain again?",
            "exit": "Thank you, I'll think about it."
        }
        return fallback_responses.get(strategy, "I see. Please continue.")
