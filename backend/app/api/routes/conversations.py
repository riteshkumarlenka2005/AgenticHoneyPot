"""Conversations API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import uuid

from ...db.database import get_db
from ...models import Conversation, Message
from ...models.conversation import ConversationStatus
from ...models.message import SenderType
from ...services.detection.detector import ScamDetector
from ...services.persona.generator import PersonaGenerator
from ...services.extraction.extractor import IntelligenceExtractor
from ...services.response.generator import ResponseGenerator
from ...core.agent.loop import HoneypotAgent
from ...core.security import SafetyGuardrails

router = APIRouter()

# Initialize services
detector = ScamDetector()
persona_gen = PersonaGenerator()
extractor = IntelligenceExtractor()
response_gen = ResponseGenerator()
agent = HoneypotAgent(detector, persona_gen, extractor, response_gen)


class IncomingMessage(BaseModel):
    """Incoming message schema."""
    scammer_identifier: str
    content: str


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    id: str
    scammer_identifier: str
    status: str
    scam_type: str | None
    detection_confidence: float | None
    started_at: datetime
    message_count: int


@router.post("/incoming")
async def receive_message(
    message: IncomingMessage,
    db: Session = Depends(get_db)
):
    """
    Receive an incoming scam message and generate honeypot response.
    """
    try:
        # Find or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.scammer_identifier == message.scammer_identifier,
            Conversation.status.in_([ConversationStatus.ACTIVE, ConversationStatus.STALLING])
        ).first()
        
        if not conversation:
            conversation = Conversation(
                scammer_identifier=message.scammer_identifier,
                status=ConversationStatus.ACTIVE
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save scammer message
        scammer_msg = Message(
            conversation_id=conversation.id,
            sender_type=SenderType.SCAMMER,
            content=message.content
        )
        db.add(scammer_msg)
        
        # Get conversation history
        history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp).all()
        
        history_list = [
            {
                "sender_type": msg.sender_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in history
        ]
        
        # Process with agent
        agent_result = await agent.process_message(
            conversation_id=str(conversation.id),
            message=message.content,
            conversation_history=history_list
        )
        
        # Update conversation with detection results
        if agent_result["detection"]["is_scam"]:
            conversation.scam_type = agent_result["detection"]["scam_type"]
            conversation.detection_confidence = agent_result["detection"]["confidence"]
        
        conversation.last_activity = datetime.utcnow()
        
        # Validate response with safety guardrails
        response_text = SafetyGuardrails.sanitize_response(agent_result["response"])
        
        # Save honeypot response
        honeypot_msg = Message(
            conversation_id=conversation.id,
            sender_type=SenderType.HONEYPOT,
            content=response_text,
            analysis=agent_result["state"]
        )
        db.add(honeypot_msg)
        
        db.commit()
        
        return {
            "conversation_id": str(conversation.id),
            "honeypot_response": response_text,
            "detection": agent_result["detection"],
            "state": agent_result["state"]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(db: Session = Depends(get_db)):
    """List all conversations."""
    conversations = db.query(Conversation).order_by(
        Conversation.started_at.desc()
    ).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        result.append({
            "id": str(conv.id),
            "scammer_identifier": conv.scammer_identifier,
            "status": conv.status.value,
            "scam_type": conv.scam_type,
            "detection_confidence": conv.detection_confidence,
            "started_at": conv.started_at,
            "message_count": message_count
        })
    
    return result


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation details with messages."""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conv_uuid
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conv_uuid
    ).order_by(Message.timestamp).all()
    
    return {
        "id": str(conversation.id),
        "scammer_identifier": conversation.scammer_identifier,
        "status": conversation.status.value,
        "scam_type": conversation.scam_type,
        "detection_confidence": conversation.detection_confidence,
        "started_at": conversation.started_at,
        "last_activity": conversation.last_activity,
        "messages": [
            {
                "id": str(msg.id),
                "sender_type": msg.sender_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "analysis": msg.analysis
            }
            for msg in messages
        ]
    }
