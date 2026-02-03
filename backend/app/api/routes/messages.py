"""Messages API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.agent.loop import HoneypotAgent
from app.core.agent.state import ConversationState
from app.core.agent.memory import AgentMemory

router = APIRouter()

# In-memory storage for active conversations (replace with database in production)
active_conversations = {}


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
async def receive_incoming_message(msg: IncomingMessage):
    """
    Receive and process an incoming scam message.
    
    This endpoint:
    1. Detects if the message is a scam
    2. Generates an appropriate honeypot response
    3. Extracts intelligence if present
    4. Updates conversation state
    """
    # Get or create conversation
    conversation_id = msg.conversation_id
    
    if not conversation_id or conversation_id not in active_conversations:
        # Create new conversation
        state = ConversationState(scammer_identifier=msg.scammer_identifier)
        memory = AgentMemory()
        conversation_id = str(state.conversation_id)
        active_conversations[conversation_id] = {
            "state": state,
            "memory": memory
        }
    else:
        # Get existing conversation
        conv = active_conversations[conversation_id]
        state = conv["state"]
        memory = conv["memory"]
    
    # Add scammer message to memory
    memory.add_message("scammer", msg.message)
    state.add_message()
    
    # Process through agent
    agent = HoneypotAgent()
    result = await agent.process_incoming_message(msg.message, state, memory)
    
    # Add honeypot response to memory
    if result.get("response"):
        memory.add_message("honeypot", result["response"])
        state.add_message()
    
    # Return response
    return MessageResponse(
        conversation_id=conversation_id,
        honeypot_response=result.get("response", ""),
        scam_detected=result["perception"]["detection"]["is_scam"],
        confidence=result["perception"]["detection"]["confidence"],
        scam_type=result["perception"]["detection"]["scam_type"],
        engagement_phase=result["decision"]["phase"]
    )
