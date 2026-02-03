"""Personas API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import uuid

from ...db.database import get_db
from ...models import Persona
from ...services.persona.generator import PersonaGenerator

router = APIRouter()
persona_gen = PersonaGenerator()


class PersonaCreate(BaseModel):
    """Persona creation schema."""
    name: str
    age: int
    occupation: str
    location: str
    traits: dict
    communication_style: str
    backstory: dict


class PersonaResponse(BaseModel):
    """Persona response schema."""
    id: str
    name: str
    age: int
    occupation: str
    location: str
    is_active: bool


@router.get("/")
async def list_personas(db: Session = Depends(get_db)):
    """List all personas."""
    personas = db.query(Persona).filter(Persona.is_active == True).all()
    
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "age": p.age,
            "occupation": p.occupation,
            "location": p.location,
            "traits": p.traits,
            "communication_style": p.communication_style,
            "backstory": p.backstory,
            "is_active": p.is_active
        }
        for p in personas
    ]


@router.get("/templates")
async def get_templates():
    """Get predefined persona templates."""
    return persona_gen.templates


@router.post("/")
async def create_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new persona."""
    new_persona = Persona(
        name=persona.name,
        age=persona.age,
        occupation=persona.occupation,
        location=persona.location,
        traits=persona.traits,
        communication_style=persona.communication_style,
        backstory=persona.backstory,
        is_active=True
    )
    
    db.add(new_persona)
    db.commit()
    db.refresh(new_persona)
    
    return {
        "id": str(new_persona.id),
        "name": new_persona.name,
        "message": "Persona created successfully"
    }


@router.get("/{persona_id}")
async def get_persona(persona_id: str, db: Session = Depends(get_db)):
    """Get persona details."""
    try:
        p_uuid = uuid.UUID(persona_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid persona ID")
    
    persona = db.query(Persona).filter(Persona.id == p_uuid).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    return {
        "id": str(persona.id),
        "name": persona.name,
        "age": persona.age,
        "occupation": persona.occupation,
        "location": persona.location,
        "traits": persona.traits,
        "communication_style": persona.communication_style,
        "backstory": persona.backstory,
        "is_active": persona.is_active
    }
