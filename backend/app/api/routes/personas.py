"""Personas API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services.persona.templates import PERSONA_TEMPLATES

router = APIRouter()


class PersonaResponse(BaseModel):
    """Persona response model."""
    id: Optional[str] = None
    name: str
    age: int
    occupation: str
    location: str
    traits: dict
    communication_style: str
    backstory: dict
    is_active: bool = True


@router.get("", response_model=List[PersonaResponse])
async def list_personas():
    """
    Get all available personas.
    
    Returns a list of persona templates that can be used by the honeypot.
    """
    personas = []
    for idx, template in enumerate(PERSONA_TEMPLATES):
        personas.append(PersonaResponse(
            id=f"persona-{idx}",
            name=template["name"],
            age=template["age"],
            occupation=template["occupation"],
            location=template["location"],
            traits=template["traits"],
            communication_style=template["communication_style"],
            backstory=template["backstory"],
            is_active=True
        ))
    
    return personas


@router.post("", response_model=PersonaResponse)
async def create_persona(persona: PersonaResponse):
    """
    Create a new custom persona.
    
    This endpoint allows creating custom personas beyond the default templates.
    In production, this would save to database.
    """
    # In production, save to database
    # For now, just return the persona
    return persona
