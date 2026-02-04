"""Conversations API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.database_service import DatabaseService
from app.models.conversation import ConversationStatus

router = APIRouter()


class ConversationListItem(BaseModel):
    """Conversation list item model."""
    id: str
    scammer_identifier: str
    status: str
    scam_type: Optional[str] = None
    detection_confidence: Optional[float] = None
    started_at: datetime
    message_count: int
    duration_seconds: Optional[int] = None


class Message(BaseModel):
    """Message model."""
    id: str
    sender_type: str
    content: str
    timestamp: datetime


class ConversationDetail(BaseModel):
    """Detailed conversation model."""
    id: str
    scammer_identifier: str
    status: str
    scam_type: Optional[str] = None
    detection_confidence: Optional[float] = None
    started_at: datetime
    last_activity: Optional[datetime] = None
    message_count: int
    duration_seconds: Optional[int] = None
    persona: Optional[dict] = None
    messages: List[Message] = []
    intelligence_count: int = 0


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    status: Optional[str] = None,
    scam_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db)
):
    """
    List all conversations with optional filtering.
    
    Query parameters:
    - status: Filter by conversation status
    - scam_type: Filter by scam type
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    db = DatabaseService(session)
    
    # Parse status filter
    status_filter = None
    if status:
        try:
            status_filter = ConversationStatus[status.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    # Get conversations from database
    conversations = await db.list_conversations(
        status=status_filter,
        limit=limit,
        offset=offset
    )
    
    # Build response
    result = []
    for conv in conversations:
        # Apply scam_type filter if provided
        if scam_type and conv.scam_type != scam_type:
            continue
        
        # Count messages
        messages = await db.get_messages(conv.id)
        
        result.append(ConversationListItem(
            id=str(conv.id),
            scammer_identifier=conv.scammer_identifier,
            status=conv.status.value,
            scam_type=conv.scam_type,
            detection_confidence=conv.detection_confidence,
            started_at=conv.started_at,
            message_count=len(messages),
            duration_seconds=conv.total_duration_seconds
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific conversation."""
    db = DatabaseService(session)
    
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    # Get conversation
    conversation = await db.get_conversation(conv_uuid)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    db_messages = await db.get_messages(conv_uuid)
    messages = [
        Message(
            id=str(msg.id),
            sender_type=msg.sender_type.value,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in db_messages
    ]
    
    # Get persona if exists
    persona_data = None
    if conversation.persona_id:
        persona = await db.get_persona(conversation.persona_id)
        if persona:
            persona_data = {
                "id": str(persona.id),
                "name": persona.name,
                "age": persona.age,
                "occupation": persona.occupation,
                "location": persona.location,
                "communication_style": persona.communication_style
            }
    
    # Count intelligence
    intelligence = await db.get_intelligence(conversation_id=conv_uuid)
    
    return ConversationDetail(
        id=str(conversation.id),
        scammer_identifier=conversation.scammer_identifier,
        status=conversation.status.value,
        scam_type=conversation.scam_type,
        detection_confidence=conversation.detection_confidence,
        started_at=conversation.started_at,
        last_activity=conversation.last_activity,
        message_count=len(messages),
        duration_seconds=conversation.total_duration_seconds,
        persona=persona_data,
        messages=messages,
        intelligence_count=len(intelligence)
    )
