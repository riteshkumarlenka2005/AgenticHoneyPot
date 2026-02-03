"""Mock scammer API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services.mock_scammer.simulator import MockScammerSimulator
from app.services.mock_scammer.scenarios import ScamScenario

router = APIRouter()

# Store active mock scammer sessions
mock_sessions = {}


class StartScamRequest(BaseModel):
    """Start scam session request."""
    scenario: ScamScenario
    session_id: Optional[str] = None


class StartScamResponse(BaseModel):
    """Start scam session response."""
    session_id: str
    initial_message: str
    scenario: str


class ScammerRespondRequest(BaseModel):
    """Scammer respond request."""
    session_id: str
    victim_message: str


class ScammerRespondResponse(BaseModel):
    """Scammer respond response."""
    session_id: str
    scammer_response: str


@router.post("/start", response_model=StartScamResponse)
async def start_mock_scam(request: StartScamRequest):
    """
    Start a mock scam session.
    
    This initializes a scammer simulator with a specific scenario.
    Use this to test the honeypot with realistic scammer behavior.
    """
    import uuid
    
    session_id = request.session_id or str(uuid.uuid4())
    
    # Create mock scammer
    simulator = MockScammerSimulator()
    initial_message = simulator.start_scam(request.scenario)
    
    # Store session
    mock_sessions[session_id] = {
        "simulator": simulator,
        "scenario": request.scenario,
        "conversation_history": [
            {"sender_type": "scammer", "content": initial_message}
        ]
    }
    
    return StartScamResponse(
        session_id=session_id,
        initial_message=initial_message,
        scenario=request.scenario.value
    )


@router.post("/respond", response_model=ScammerRespondResponse)
async def get_mock_scammer_response(request: ScammerRespondRequest):
    """
    Get a response from the mock scammer.
    
    Send the honeypot's message and get back the scammer's response.
    This simulates a realistic scammer conversation.
    """
    from fastapi import HTTPException
    
    if request.session_id not in mock_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = mock_sessions[request.session_id]
    simulator = session["simulator"]
    conversation_history = session["conversation_history"]
    
    # Add victim message to history
    conversation_history.append({
        "sender_type": "honeypot",
        "content": request.victim_message
    })
    
    # Generate scammer response
    scammer_response = await simulator.respond(
        request.victim_message,
        conversation_history
    )
    
    # Add scammer response to history
    conversation_history.append({
        "sender_type": "scammer",
        "content": scammer_response
    })
    
    return ScammerRespondResponse(
        session_id=request.session_id,
        scammer_response=scammer_response
    )


@router.get("/scenarios")
async def list_scenarios():
    """
    List all available mock scam scenarios.
    
    Returns the different types of scams that can be simulated.
    """
    return {
        "scenarios": [
            {
                "id": scenario.value,
                "name": scenario.value.replace("_", " ").title(),
                "description": f"Simulates a {scenario.value.replace('_', ' ')} scam"
            }
            for scenario in ScamScenario
        ]
    }
