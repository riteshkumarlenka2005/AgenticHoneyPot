"""Messages API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agent.loop import HoneypotAgent
from app.core.agent.state import ConversationState
from app.core.agent.memory import AgentMemory
from app.db.database import get_db
from app.services.database_service import ConversationService, MessageService, IntelligenceService
from app.models.message import SenderType
from app.models.intelligence import ArtifactType

router = APIRouter()

# In-memory storage for active agent states (agent state is still in-memory for now)
# TODO: Move agent state to Redis cache
active_agent_states = {}


class IncomingMessage(BaseModel):
    """Incoming message model."""
    message: str
    scammer_identifier: str
    conversation_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response model."""
    conversation_id: str
    honeypot_response: str
    scam_detected: bool
    confidence: float
    scam_type: str
    engagement_phase: str


@router.post("/incoming", response_model=MessageResponse)
async def receive_incoming_message(
    msg: IncomingMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive and process an incoming scam message.
    
    This endpoint:
    1. Detects if the message is a scam
    2. Generates an appropriate honeypot response
    3. Extracts intelligence if present
    4. Updates conversation state
    """
    # Get or create conversation in database
    conversation_id = msg.conversation_id
    conversation = None
    
    if conversation_id:
        try:
            conversation = await ConversationService.get_by_id(db, UUID(conversation_id))
        except (ValueError, AttributeError):
            pass
    
    # Get or create agent state (still in-memory)
    if conversation and str(conversation.id) in active_agent_states:
        state = active_agent_states[str(conversation.id)]["state"]
        memory = active_agent_states[str(conversation.id)]["memory"]
    else:
        # Create new conversation in database
        if not conversation:
            conversation = await ConversationService.create(
                db,
                scammer_identifier=msg.scammer_identifier
            )
            await db.commit()
        
        # Create new agent state
        state = ConversationState(
            scammer_identifier=msg.scammer_identifier,
            conversation_id=conversation.id
        )
        memory = AgentMemory()
        active_agent_states[str(conversation.id)] = {
            "state": state,
            "memory": memory
        }
    
    conversation_id = str(conversation.id)
    
    # Store scammer message in database
    await MessageService.create(
        db,
        conversation_id=conversation.id,
        sender_type=SenderType.SCAMMER,
        content=msg.message
    )
    
    # Add scammer message to memory
    memory.add_message("scammer", msg.message)
    state.add_message()
    
    # Process through agent
    agent = HoneypotAgent()
    result = await agent.process_incoming_message(msg.message, state, memory)
    
    # Store honeypot response in database
    if result.get("response"):
        await MessageService.create(
            db,
            conversation_id=conversation.id,
            sender_type=SenderType.HONEYPOT,
            content=result["response"],
            analysis=result.get("perception", {})
        )
        memory.add_message("honeypot", result["response"])
        state.add_message()
    
    # Store extracted intelligence
    if "extraction" in result and "artifacts" in result["extraction"]:
        for artifact in result["extraction"]["artifacts"]:
            try:
                artifact_type = ArtifactType(artifact["type"])
                await IntelligenceService.create(
                    db,
                    conversation_id=conversation.id,
                    artifact_type=artifact_type,
                    value=artifact["value"],
                    confidence=artifact.get("confidence", 0.0)
                )
            except (ValueError, KeyError):
                continue
    
    # Update conversation metadata
    await ConversationService.update_status(
        db,
        conversation_id=conversation.id,
        status=state.status
    )
    await ConversationService.update_duration(
        db,
        conversation_id=conversation.id,
        duration_seconds=state.get_duration()
    )
    
    await db.commit()
    
    # Return response
    return MessageResponse(
        conversation_id=conversation_id,
        honeypot_response=result.get("response", ""),
        scam_detected=result["perception"]["detection"]["is_scam"],
        confidence=result["perception"]["detection"]["confidence"],
        scam_type=result["perception"]["detection"]["scam_type"],
        engagement_phase=result["decision"]["phase"]
    )
