"""Conversations API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.database_service import ConversationService, MessageService
from app.models.conversation import ConversationStatus

router = APIRouter()


class ConversationListItem(BaseModel):
    """Conversation list item model."""
    id: str
    scammer_identifier: str
    status: str
    scam_type: str
    detection_confidence: float
    started_at: datetime
    message_count: int
    duration_seconds: int
    
    class Config:
        from_attributes = True


class Message(BaseModel):
    """Message model."""
    id: str
    sender_type: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Detailed conversation model."""
    id: str
    scammer_identifier: str
    status: str
    scam_type: str
    detection_confidence: float
    started_at: datetime
    last_activity: datetime
    message_count: int
    duration_seconds: int
    persona: Optional[dict] = None
    messages: List[Message] = []
    intelligence_extracted: dict = {}
    manipulation_tactics: List[str] = []
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    status: Optional[str] = None,
    scam_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all conversations with optional filtering.
    
    Query parameters:
    - status: Filter by conversation status
    - scam_type: Filter by scam type
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    # Convert status string to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = ConversationStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    conversations = await ConversationService.list_conversations(
        db,
        status=status_enum,
        scam_type=scam_type,
        limit=limit,
        offset=offset
    )
    
    result = []
    for conv in conversations:
        # Count messages
        messages = await MessageService.get_by_conversation(db, conv.id)
        
        result.append(ConversationListItem(
            id=str(conv.id),
            scammer_identifier=conv.scammer_identifier,
            status=conv.status.value,
            scam_type=conv.scam_type or "unknown",
            detection_confidence=conv.detection_confidence or 0.0,
            started_at=conv.started_at,
            message_count=len(messages),
            duration_seconds=conv.total_duration_seconds or 0
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a specific conversation."""
    try:
        conversation = await ConversationService.get_by_id(db, UUID(conversation_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages = await MessageService.get_by_conversation(db, conversation.id)
    
    # Build message list
    message_list = [
        Message(
            id=str(msg.id),
            sender_type=msg.sender_type.value,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]
    
    # Count intelligence extracted
    intelligence_count = {
        "upi_id": len([i for i in conversation.intelligence if i.artifact_type.value == "upi_id"]),
        "bank_account": len([i for i in conversation.intelligence if i.artifact_type.value == "bank_account"]),
        "phone": len([i for i in conversation.intelligence if i.artifact_type.value == "phone"]),
        "url": len([i for i in conversation.intelligence if i.artifact_type.value == "url"]),
        "email": len([i for i in conversation.intelligence if i.artifact_type.value == "email"]),
    }
    
    return ConversationDetail(
        id=str(conversation.id),
        scammer_identifier=conversation.scammer_identifier,
        status=conversation.status.value,
        scam_type=conversation.scam_type or "unknown",
        detection_confidence=conversation.detection_confidence or 0.0,
        started_at=conversation.started_at,
        last_activity=conversation.last_activity or conversation.started_at,
        message_count=len(messages),
        duration_seconds=conversation.total_duration_seconds or 0,
        persona=conversation.extra_data.get("persona") if conversation.extra_data else None,
        messages=message_list,
        intelligence_extracted=intelligence_count,
        manipulation_tactics=conversation.extra_data.get("manipulation_tactics", []) if conversation.extra_data else []
    )
