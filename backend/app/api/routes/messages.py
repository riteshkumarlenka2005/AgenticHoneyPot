"""Messages API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.core.agent.loop import HoneypotAgent
from app.core.agent.state import ConversationState
from app.core.agent.memory import AgentMemory
from app.db.database import get_db
from app.services.database_service import DatabaseService
from app.models.message import SenderType
from app.models.conversation import ConversationStatus
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


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
    session: AsyncSession = Depends(get_db)
):
    """
    Receive and process an incoming scam message.
    
    This endpoint:
    1. Detects if the message is a scam
    2. Generates an appropriate honeypot response
    3. Extracts intelligence if present
    4. Updates conversation state
    """
    db = DatabaseService(session)
    
    # Get or create conversation
    conversation_id = msg.conversation_id
    conversation = None
    
    if conversation_id:
        # Try to get existing conversation
        try:
            conversation = await db.get_conversation(UUID(conversation_id))
        except (ValueError, AttributeError):
            conversation = None
    
    if not conversation:
        # Check if there's an active conversation for this scammer
        conversation = await db.get_conversation_by_scammer(
            msg.scammer_identifier,
            status=ConversationStatus.ACTIVE
        )
    
    if not conversation:
        # Create new conversation
        persona = await db.get_random_active_persona()
        conversation = await db.create_conversation(
            scammer_identifier=msg.scammer_identifier,
            persona_id=persona.id if persona else None
        )
        
        # Create or update scammer profile
        await db.create_or_update_scammer_profile(msg.scammer_identifier)
    
    # Create state and memory from conversation
    state = ConversationState(
        conversation_id=conversation.id,
        scammer_identifier=msg.scammer_identifier
    )
    
    # Load conversation history into memory
    memory = AgentMemory()
    messages = await db.get_messages(conversation.id)
    for db_msg in messages:
        role = "scammer" if db_msg.sender_type == SenderType.SCAMMER else "honeypot"
        memory.add_message(role, db_msg.content)
    
    # Add scammer message to database and memory
    await db.create_message(
        conversation_id=conversation.id,
        sender_type=SenderType.SCAMMER,
        content=msg.message
    )
    memory.add_message("scammer", msg.message)
    state.add_message()
    
    # Process through agent
    agent = HoneypotAgent()
    result = await agent.process_incoming_message(msg.message, state, memory)
    
    # Save honeypot response to database
    honeypot_response = result.get("response", "")
    if honeypot_response:
        await db.create_message(
            conversation_id=conversation.id,
            sender_type=SenderType.HONEYPOT,
            content=honeypot_response,
            analysis=result.get("perception")
        )
        memory.add_message("honeypot", honeypot_response)
        state.add_message()
    
    # Update conversation with detection results
    if result["perception"]["detection"]["is_scam"]:
        conversation.scam_type = result["perception"]["detection"]["scam_type"]
        conversation.detection_confidence = result["perception"]["detection"]["confidence"]
    
    # Extract and save intelligence
    extraction_results = result["perception"].get("extraction", {})
    if extraction_results.get("artifacts"):
        from app.models.intelligence import ArtifactType
        
        for artifact in extraction_results["artifacts"]:
            artifact_type_str = artifact.get("type", "").upper()
            try:
                artifact_type = ArtifactType[artifact_type_str]
                await db.create_intelligence(
                    conversation_id=conversation.id,
                    artifact_type=artifact_type,
                    value=artifact.get("value", ""),
                    confidence=artifact.get("confidence", 0.0)
                )
            except (KeyError, ValueError):
                # Skip invalid artifact types
                pass
    
    # Commit all changes
    await session.commit()
    
    # Return response
    return MessageResponse(
        conversation_id=str(conversation.id),
        honeypot_response=honeypot_response,
        scam_detected=result["perception"]["detection"]["is_scam"],
        confidence=result["perception"]["detection"]["confidence"],
        scam_type=result["perception"]["detection"]["scam_type"],
        engagement_phase=result["decision"]["phase"]
    )
