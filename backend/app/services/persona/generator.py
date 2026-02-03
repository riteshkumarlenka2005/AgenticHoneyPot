"""Persona generation service."""
import random
from typing import Optional
from uuid import UUID
from app.services.persona.templates import PERSONA_TEMPLATES


class PersonaGenerator:
    """Service for generating and managing personas."""
    
    def __init__(self):
        """Initialize persona generator."""
        self.templates = PERSONA_TEMPLATES
    
    def select_persona(self, scam_type: Optional[str] = None) -> dict:
        """
        Select an appropriate persona based on scam type.
        
        Args:
            scam_type: Type of scam to match persona to
            
        Returns:
            Selected persona template
        """
        # Match persona to scam type for better believability
        if scam_type in ["tech_support", "bank_kyc_fraud"]:
            # Tech-naive personas work better for these scams
            suitable_personas = [p for p in self.templates if p["traits"]["tech_savvy"] in ["low", "very_low"]]
        elif scam_type in ["investment_fraud"]:
            # Greedy or risk-taking personas
            suitable_personas = [p for p in self.templates if p["traits"]["risk_tolerance"] in ["medium", "high"]]
        elif scam_type in ["job_scam"]:
            # Desperate personas
            suitable_personas = [p for p in self.templates if p["traits"]["desperation"] in ["medium", "high"]]
        else:
            suitable_personas = self.templates
        
        return random.choice(suitable_personas) if suitable_personas else random.choice(self.templates)
    
    def generate_response_style(self, persona: dict) -> str:
        """
        Generate response style instructions for the persona.
        
        Args:
            persona: Persona template
            
        Returns:
            Response style instructions for LLM
        """
        return f"""You are roleplaying as {persona['name']}, a {persona['age']}-year-old {persona['occupation']} from {persona['location']}.

Communication Style: {persona['communication_style']}

Background:
- Family: {persona['backstory']['family']}
- Financial Situation: {persona['backstory']['financial']}
- Technology Skills: {persona['backstory']['technology']}
- Personality: {persona['backstory']['personality']}

Key Traits:
- Tech Savvy: {persona['traits']['tech_savvy']}
- Trust Level: {persona['traits']['trust_level']}
- Risk Tolerance: {persona['traits']['risk_tolerance']}

IMPORTANT SAFETY RULES (NEVER VIOLATE):
1. Never send real money or provide real bank details
2. Never share real OTPs, passwords, or PINs
3. Never click on or access external links
4. Never install any software
5. Respond in character but maintain safety boundaries

Your goal is to engage the scammer convincingly while extracting information like bank accounts, UPI IDs, and phishing links they provide.
"""
    
    def create_persona_context(self, persona: dict) -> dict:
        """
        Create a persona context for conversation management.
        
        Args:
            persona: Persona template
            
        Returns:
            Persona context dictionary
        """
        return {
            "persona_id": None,  # To be set when saved to database
            "name": persona["name"],
            "age": persona["age"],
            "occupation": persona["occupation"],
            "location": persona["location"],
            "traits": persona["traits"],
            "communication_style": persona["communication_style"],
            "backstory": persona["backstory"],
            "response_style_instructions": self.generate_response_style(persona)
        }
