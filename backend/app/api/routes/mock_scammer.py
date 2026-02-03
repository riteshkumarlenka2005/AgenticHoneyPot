"""Mock scammer API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ...services.mock_scammer.simulator import MockScammer, ScamScenario

router = APIRouter()

# Store active mock scammer sessions
mock_sessions = {}


class StartSessionRequest(BaseModel):
    """Start session request schema."""
    scenario: ScamScenario
    session_id: Optional[str] = None


class MockMessageRequest(BaseModel):
    """Mock message request schema."""
    session_id: str
    message: str


@router.post("/start")
async def start_mock_session(request: StartSessionRequest):
    """Start a mock scammer session."""
    import uuid
    
    session_id = request.session_id or str(uuid.uuid4())
    
    # Create mock scammer
    scammer = MockScammer(request.scenario)
    mock_sessions[session_id] = scammer
    
    # Get opening message
    opening_message = scammer.get_opening_message()
    
    return {
        "session_id": session_id,
        "scenario": request.scenario.value,
        "opening_message": opening_message
    }


@router.post("/respond")
async def get_mock_response(request: MockMessageRequest):
    """Get mock scammer response to victim message."""
    scammer = mock_sessions.get(request.session_id)
    
    if not scammer:
        return {
            "error": "Session not found",
            "session_id": request.session_id
        }
    
    response = scammer.respond(request.message)
    
    return {
        "session_id": request.session_id,
        "scammer_response": response,
        "message_count": scammer.message_count,
        "details_provided": scammer.provided_details
    }


@router.get("/scenarios")
async def list_scenarios():
    """List available scam scenarios."""
    return {
        "scenarios": [scenario.value for scenario in ScamScenario]
    }


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End a mock scammer session."""
    if session_id in mock_sessions:
        del mock_sessions[session_id]
        return {"message": "Session ended", "session_id": session_id}
    
    return {"error": "Session not found", "session_id": session_id}
