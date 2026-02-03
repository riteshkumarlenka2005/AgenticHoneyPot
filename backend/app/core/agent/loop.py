"""Agent orchestration and main loop."""
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentState:
    """Manage agent conversation state."""
    
    def __init__(self, conversation_id: str):
        """Initialize agent state."""
        self.conversation_id = conversation_id
        self.phase = "detecting"
        self.persona = None
        self.scam_detected = False
        self.scam_type = None
        self.confidence = 0.0
        self.extraction_targets = []
        self.extracted_artifacts = {}
        self.message_count = 0
        self.started_at = datetime.utcnow()
    
    def update_phase(self, new_phase: str):
        """Update conversation phase."""
        self.phase = new_phase
        logger.info(f"Phase updated to: {new_phase}")
    
    def add_extracted_artifact(self, artifact_type: str, value: str):
        """Add extracted artifact."""
        if artifact_type not in self.extracted_artifacts:
            self.extracted_artifacts[artifact_type] = []
        if value not in self.extracted_artifacts[artifact_type]:
            self.extracted_artifacts[artifact_type].append(value)
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "phase": self.phase,
            "persona": self.persona,
            "scam_detected": self.scam_detected,
            "scam_type": self.scam_type,
            "confidence": self.confidence,
            "extracted_artifacts": self.extracted_artifacts,
            "message_count": self.message_count,
        }


class HoneypotAgent:
    """Main honeypot agent orchestrator."""
    
    def __init__(self, detector, persona_gen, extractor, response_gen):
        """
        Initialize the agent.
        
        Args:
            detector: ScamDetector instance
            persona_gen: PersonaGenerator instance
            extractor: IntelligenceExtractor instance
            response_gen: ResponseGenerator instance
        """
        self.detector = detector
        self.persona_gen = persona_gen
        self.extractor = extractor
        self.response_gen = response_gen
        self.states = {}
    
    def get_or_create_state(self, conversation_id: str) -> AgentState:
        """Get or create agent state for conversation."""
        if conversation_id not in self.states:
            self.states[conversation_id] = AgentState(conversation_id)
        return self.states[conversation_id]
    
    async def process_message(
        self,
        conversation_id: str,
        message: str,
        conversation_history: Optional[list] = None
    ) -> Dict:
        """
        Main agent loop: Perceive -> Think -> Decide -> Act.
        
        Args:
            conversation_id: Unique conversation identifier
            message: Incoming scammer message
            conversation_history: Previous messages
            
        Returns:
            Agent response with metadata
        """
        state = self.get_or_create_state(conversation_id)
        state.message_count += 1
        
        if conversation_history is None:
            conversation_history = []
        
        # PERCEIVE: Detect scam
        detection_result = await self.detector.detect_scam(message, conversation_history)
        
        # THINK: Update state based on detection
        if detection_result["is_scam"] and not state.scam_detected:
            state.scam_detected = True
            state.scam_type = detection_result["scam_type"]
            state.confidence = detection_result["confidence"]
            state.update_phase("engaging")
            
            # Select appropriate persona
            state.persona = self.persona_gen.get_persona_by_type(state.scam_type)
            logger.info(f"Scam detected! Type: {state.scam_type}, Using persona: {state.persona['name']}")
        
        # Extract intelligence from scammer message
        extracted = self.extractor.extract_from_message(message)
        for artifact_type, values in extracted.items():
            for value in values:
                state.add_extracted_artifact(artifact_type, value)
        
        # DECIDE: Determine response strategy
        if not state.scam_detected:
            # Not a scam, minimal engagement
            response_text = "Sorry, I'm not interested."
            strategy = "disengage"
        else:
            # Update phase based on message count and extraction
            if state.message_count >= 3 and not extracted:
                state.update_phase("extracting")
            elif state.message_count >= 6:
                state.update_phase("stalling")
            
            # ACT: Generate response
            response_data = await self.response_gen.generate_response(
                persona=state.persona,
                scammer_message=message,
                conversation_history=conversation_history,
                extraction_targets=["upi_id", "bank_account", "phone"]
            )
            response_text = response_data["message"]
            strategy = response_data["strategy"]
        
        # Prepare agent output
        result = {
            "response": response_text,
            "state": state.to_dict(),
            "detection": detection_result,
            "extracted": extracted,
            "strategy": strategy,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return result
