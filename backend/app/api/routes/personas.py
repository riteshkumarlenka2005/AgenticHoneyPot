"""Personas API routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.database_service import DatabaseService
from app.services.persona.templates import PERSONA_TEMPLATES

router = APIRouter()


class PersonaCreate(BaseModel):
    """Persona creation model."""
    name: str
    age: int
    occupation: str
    location: str
    traits: dict
    communication_style: str
    backstory: dict
    is_active: bool = True


class PersonaResponse(BaseModel):
    """Persona response model."""
    id: str
    name: str
    age: int
    occupation: str
    location: str
    traits: dict
    communication_style: str
    backstory: dict
    is_active: bool = True


@router.get("", response_model=List[PersonaResponse])
async def list_personas(
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_db)
):
    """
    Get all available personas.
    
    Returns a list of personas from the database.
    """
    db = DatabaseService(session)
    
    personas = await db.list_personas(is_active=is_active)
    
    return [
        PersonaResponse(
            id=str(persona.id),
            name=persona.name,
            age=persona.age,
            occupation=persona.occupation,
            location=persona.location,
            traits=persona.traits,
            communication_style=persona.communication_style,
            backstory=persona.backstory,
            is_active=persona.is_active
        )
        for persona in personas
    ]


@router.post("", response_model=PersonaResponse)
async def create_persona(
    persona: PersonaCreate,
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new custom persona.
    
    This endpoint allows creating custom personas beyond the default templates.
    """
    db = DatabaseService(session)
    
    new_persona = await db.create_persona(
        name=persona.name,
        age=persona.age,
        occupation=persona.occupation,
        location=persona.location,
        communication_style=persona.communication_style,
        traits=persona.traits,
        backstory=persona.backstory,
        is_active=persona.is_active
    )
    
    await session.commit()
    
    return PersonaResponse(
        id=str(new_persona.id),
        name=new_persona.name,
        age=new_persona.age,
        occupation=new_persona.occupation,
        location=new_persona.location,
        traits=new_persona.traits,
        communication_style=new_persona.communication_style,
        backstory=new_persona.backstory,
        is_active=new_persona.is_active
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific persona by ID."""
    db = DatabaseService(session)
    
    try:
        persona_uuid = UUID(persona_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid persona ID format")
    
    persona = await db.get_persona(persona_uuid)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    return PersonaResponse(
        id=str(persona.id),
        name=persona.name,
        age=persona.age,
        occupation=persona.occupation,
        location=persona.location,
        traits=persona.traits,
        communication_style=persona.communication_style,
        backstory=persona.backstory,
        is_active=persona.is_active
    )


@router.post("/seed")
async def seed_personas(session: AsyncSession = Depends(get_db)):
    """
    Seed the database with default persona templates.
    
    This endpoint creates personas from the PERSONA_TEMPLATES.
    """
    db = DatabaseService(session)
    
    created_count = 0
    for template in PERSONA_TEMPLATES:
        await db.create_persona(
            name=template["name"],
            age=template["age"],
            occupation=template["occupation"],
            location=template["location"],
            communication_style=template["communication_style"],
            traits=template["traits"],
            backstory=template["backstory"],
            is_active=True
        )
        created_count += 1
    
    await session.commit()
    
    return {"message": f"Seeded {created_count} personas successfully"}
