"""Mock scammer simulator."""
import random
from typing import Optional
from openai import AsyncOpenAI
from app.config import settings
from app.services.mock_scammer.scenarios import (
    ScamScenario,
    SCENARIO_OPENERS,
    FAKE_SCAMMER_DETAILS
)


class MockScammerSimulator:
    """Simulates scammer behavior for testing."""
    
    def __init__(self):
        """Initialize mock scammer."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.scenario = None
        self.details_revealed = {
            "upi": False,
            "bank": False,
            "phone": False,
            "link": False
        }
    
    def start_scam(self, scenario: ScamScenario) -> str:
        """
        Start a scam conversation.
        
        Args:
            scenario: The scam scenario to use
            
        Returns:
            Opening scam message
        """
        self.scenario = scenario
        self.details_revealed = {
            "upi": False,
            "bank": False,
            "phone": False,
            "link": False
        }
        
        openers = SCENARIO_OPENERS.get(scenario, [])
        return random.choice(openers) if openers else "Hello, I have an important message for you."
    
    async def respond(
        self,
        victim_message: str,
        conversation_history: list[dict]
    ) -> str:
        """
        Generate scammer response to victim message.
        
        Args:
            victim_message: The victim's message
            conversation_history: Previous messages
            
        Returns:
            Scammer's response
        """
        if not self.client:
            return self._fallback_scammer_response(victim_message)
        
        try:
            # Determine what details to reveal based on victim's questions
            should_reveal_details = self._should_reveal_details(victim_message)
            
            # Build scammer persona and context
            messages = self._build_scammer_context(
                victim_message,
                conversation_history,
                should_reveal_details
            )
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.9,
                max_tokens=200
            )
            
            scammer_response = response.choices[0].message.content.strip()
            
            # Inject fake details if needed
            if should_reveal_details:
                scammer_response = self._inject_fake_details(scammer_response, victim_message)
            
            return scammer_response
            
        except Exception as e:
            print(f"Mock scammer response error: {e}")
            return self._fallback_scammer_response(victim_message)
    
    def _should_reveal_details(self, victim_message: str) -> bool:
        """Determine if scammer should reveal contact/payment details."""
        message_lower = victim_message.lower()
        
        # Check for payment-related keywords
        payment_keywords = ["pay", "send", "transfer", "upi", "account", "bank", "number", "details"]
        return any(keyword in message_lower for keyword in payment_keywords)
    
    def _build_scammer_context(
        self,
        victim_message: str,
        conversation_history: list[dict],
        should_reveal_details: bool
    ) -> list[dict]:
        """Build context for scammer LLM."""
        scenario_instructions = {
            ScamScenario.LOTTERY_PRIZE: "You are a scammer pretending to be from a lottery company. The victim has won a huge prize but needs to pay processing fee. Be persuasive, create urgency.",
            ScamScenario.BANK_KYC_FRAUD: "You are a scammer pretending to be from a bank. The victim's account will be locked unless they update KYC. Create fear and urgency.",
            ScamScenario.TECH_SUPPORT: "You are a scammer pretending to be from Microsoft/Apple tech support. The victim's computer has viruses. Create panic and urgency.",
            ScamScenario.INVESTMENT_FRAUD: "You are a scammer offering fake investment opportunities with guaranteed returns. Be professional but pushy. Create greed.",
            ScamScenario.JOB_SCAM: "You are a scammer offering fake work-from-home jobs. The victim needs to pay registration fee. Create hope and urgency."
        }
        
        system_prompt = scenario_instructions.get(
            self.scenario,
            "You are a scammer trying to defraud the victim. Be persuasive and create urgency."
        )
        
        system_prompt += "\n\nIMPORTANT: You are simulating a scammer for testing purposes only. Keep responses realistic but brief."
        
        if should_reveal_details:
            system_prompt += "\n\nThe victim is asking for payment/contact details. Provide fake details naturally in your response."
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-8:]:
            role = "assistant" if msg.get("sender_type") == "scammer" else "user"
            messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # Add current victim message
        messages.append({
            "role": "user",
            "content": victim_message
        })
        
        return messages
    
    def _inject_fake_details(self, response: str, victim_message: str) -> str:
        """Inject fake payment/contact details into response."""
        message_lower = victim_message.lower()
        
        # UPI ID
        if "upi" in message_lower and not self.details_revealed["upi"]:
            upi_id = random.choice(FAKE_SCAMMER_DETAILS["upi_ids"])
            response += f"\n\nPlease send payment to UPI ID: {upi_id}"
            self.details_revealed["upi"] = True
        
        # Bank account
        elif ("account" in message_lower or "bank" in message_lower) and not self.details_revealed["bank"]:
            bank_details = random.choice(FAKE_SCAMMER_DETAILS["bank_accounts"])
            response += f"\n\nBank Details:\nAccount Number: {bank_details['account_number']}\nIFSC Code: {bank_details['ifsc_code']}\nAccount Holder: {bank_details['account_holder']}"
            self.details_revealed["bank"] = True
        
        # Phone number
        elif ("phone" in message_lower or "number" in message_lower or "call" in message_lower) and not self.details_revealed["phone"]:
            phone = random.choice(FAKE_SCAMMER_DETAILS["phone_numbers"])
            response += f"\n\nYou can reach me at: {phone}"
            self.details_revealed["phone"] = True
        
        # Link
        elif ("link" in message_lower or "website" in message_lower) and not self.details_revealed["link"]:
            link = random.choice(FAKE_SCAMMER_DETAILS["phishing_links"])
            response += f"\n\nPlease visit: {link}"
            self.details_revealed["link"] = True
        
        return response
    
    def _fallback_scammer_response(self, victim_message: str) -> str:
        """Fallback response when LLM is not available."""
        if self._should_reveal_details(victim_message):
            upi_id = random.choice(FAKE_SCAMMER_DETAILS["upi_ids"])
            return f"Yes, please send the payment to this UPI ID: {upi_id}"
        
        return "Please proceed immediately to claim your prize/complete verification. Time is running out!"
