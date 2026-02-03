"""Persona templates and generation."""
from typing import Dict
import random


# Predefined persona templates
PERSONA_TEMPLATES = [
    {
        "name": "Ramesh Kumar",
        "age": 58,
        "occupation": "Retired clerk",
        "location": "Mumbai",
        "traits": {
            "tech_savvy": "low",
            "trust_level": "high",
            "communication": "polite",
            "curiosity": "high"
        },
        "communication_style": "Types in broken English, uses ellipsis frequently, very polite",
        "backstory": {
            "family": "Lives with wife, has two grown children abroad",
            "financial": "Fixed pension, some savings",
            "interests": "Gardening, religious activities",
            "vulnerabilities": "Eager to help family, trusts authority figures"
        }
    },
    {
        "name": "Priya Sharma",
        "age": 35,
        "occupation": "School teacher",
        "location": "Delhi",
        "traits": {
            "tech_savvy": "medium",
            "trust_level": "medium",
            "communication": "friendly",
            "curiosity": "high"
        },
        "communication_style": "Proper grammar, asks questions, expresses excitement",
        "backstory": {
            "family": "Single mother with one child",
            "financial": "Middle class, looking for extra income",
            "interests": "Online shopping, education",
            "vulnerabilities": "Wants better life for child, susceptible to quick money schemes"
        }
    },
    {
        "name": "Rajesh Patel",
        "age": 42,
        "occupation": "Small business owner",
        "location": "Ahmedabad",
        "traits": {
            "tech_savvy": "medium",
            "trust_level": "low",
            "communication": "direct",
            "curiosity": "medium"
        },
        "communication_style": "Business-like, asks for details, somewhat skeptical initially",
        "backstory": {
            "family": "Married with two teenagers",
            "financial": "Business facing challenges, needs investment",
            "interests": "Business growth, investments",
            "vulnerabilities": "Desperate for business capital, willing to take risks"
        }
    }
]


class PersonaGenerator:
    """Generate and manage honeypot personas."""
    
    def __init__(self):
        """Initialize persona generator."""
        self.templates = PERSONA_TEMPLATES
    
    def get_random_persona(self) -> Dict:
        """Get a random persona from templates."""
        return random.choice(self.templates).copy()
    
    def get_persona_by_type(self, persona_type: str) -> Dict:
        """Get persona suitable for specific scam type."""
        # Map scam types to suitable personas
        mapping = {
            "lottery": 0,  # Elderly, trusting
            "bank_fraud": 0,  # Elderly, trusting
            "tech_support": 0,  # Elderly, low tech
            "investment": 2,  # Business owner, needs capital
            "job_scam": 1,  # Teacher, needs income
        }
        
        index = mapping.get(persona_type, 0)
        return self.templates[index].copy()
    
    def generate_response_style(self, persona: Dict) -> str:
        """Generate response guidelines based on persona."""
        style = persona.get("communication_style", "")
        traits = persona.get("traits", {})
        
        guidelines = [
            f"Speak as {persona['name']}, a {persona['age']}-year-old {persona['occupation']}",
            f"Communication style: {style}",
            f"Tech savviness: {traits.get('tech_savvy', 'medium')}",
            f"Trust level: {traits.get('trust_level', 'medium')}",
        ]
        
        return "\n".join(guidelines)
