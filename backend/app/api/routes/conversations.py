"""Conversations API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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


@router.get("", response_model=List[ConversationListItem])
async def list_conversations(
    status: Optional[str] = None,
    scam_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List all conversations with optional filtering.
    
    Query parameters:
    - status: Filter by conversation status
    - scam_type: Filter by scam type
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    # Import here to avoid circular dependency
    from app.api.routes.messages import active_conversations
    
    conversations = []
    for conv_id, conv_data in active_conversations.items():
        state = conv_data["state"]
        
        # Apply filters
        if status and state.status.value != status:
            continue
        if scam_type and state.scam_type != scam_type:
            continue
        
        conversations.append(ConversationListItem(
            id=str(state.conversation_id),
            scammer_identifier=state.scammer_identifier,
            status=state.status.value,
            scam_type=state.scam_type,
            detection_confidence=state.detection_confidence,
            started_at=state.started_at,
            message_count=state.message_count,
            duration_seconds=state.get_duration()
        ))
    
    # Sort by most recent first
    conversations.sort(key=lambda x: x.started_at, reverse=True)
    
    return conversations[offset:offset + limit]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """Get detailed information about a specific conversation."""
    from app.api.routes.messages import active_conversations
    
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv_data = active_conversations[conversation_id]
    state = conv_data["state"]
    memory = conv_data["memory"]
    
    # Build message list
    messages = []
    for idx, msg in enumerate(memory.get_full_history()):
        messages.append(Message(
            id=f"{conversation_id}-{idx}",
            sender_type=msg["sender_type"],
            content=msg["content"],
            timestamp=datetime.utcnow()  # Would use actual timestamps in production
        ))
    
    return ConversationDetail(
        id=str(state.conversation_id),
        scammer_identifier=state.scammer_identifier,
        status=state.status.value,
        scam_type=state.scam_type,
        detection_confidence=state.detection_confidence,
        started_at=state.started_at,
        last_activity=state.last_activity,
        message_count=state.message_count,
        duration_seconds=state.get_duration(),
        persona=state.persona,
        messages=messages,
        intelligence_extracted=state.intelligence_extracted,
        manipulation_tactics=state.manipulation_tactics
    )
