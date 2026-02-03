"""Main agent loop for honeypot operation."""
from typing import Optional, Dict, Any
from app.core.agent.state import ConversationState
from app.core.agent.memory import AgentMemory
from app.core.security import SafetyGuardrails
from app.services.detection.detector import ScamDetector
from app.services.persona.generator import PersonaGenerator
from app.services.extraction.extractor import IntelligenceExtractor
from app.services.response.generator import ResponseGenerator
from app.services.response.strategies import ResponseStrategy


class HoneypotAgent:
    """
    Main honeypot agent implementing the Perceive → Think → Decide → Act → Learn loop.
    """
    
    def __init__(self):
        """Initialize honeypot agent."""
        self.detector = ScamDetector()
        self.persona_generator = PersonaGenerator()
        self.extractor = IntelligenceExtractor()
        self.response_generator = ResponseGenerator()
        self.safety = SafetyGuardrails()
    
    async def process_incoming_message(
        self,
        message: str,
        state: ConversationState,
        memory: AgentMemory
    ) -> Dict[str, Any]:
        """
        Process an incoming message through the agent loop.
        
        Args:
            message: Incoming scammer message
            state: Current conversation state
            memory: Agent memory
            
        Returns:
            Dictionary with response and updated state
        """
        # PERCEIVE: Analyze the incoming message
        perception = await self._perceive(message, memory)
        
        # THINK: Analyze the situation and update beliefs
        thinking = self._think(perception, state, memory)
        
        # DECIDE: Determine action strategy
        decision = self._decide(thinking, state, memory)
        
        # ACT: Generate and validate response
        action = await self._act(decision, message, state, memory)
        
        # LEARN: Update state and memory
        self._learn(perception, thinking, decision, action, state, memory)
        
        return {
            "response": action.get("response"),
            "state": state.to_dict(),
            "perception": perception,
            "decision": decision
        }
    
    async def _perceive(self, message: str, memory: AgentMemory) -> Dict[str, Any]:
        """
        PERCEIVE: Analyze incoming message.
        
        Returns:
            Perception results including scam detection and intelligence extraction
        """
        # Detect if message is a scam
        detection_result = await self.detector.detect(
            message,
            memory.get_recent_messages()
        )
        
        # Extract intelligence from message
        extraction_result = self.extractor.extract_from_message(message)
        
        return {
            "detection": detection_result,
            "extraction": extraction_result
        }
    
    def _think(
        self,
        perception: Dict[str, Any],
        state: ConversationState,
        memory: AgentMemory
    ) -> Dict[str, Any]:
        """
        THINK: Analyze situation and update beliefs.
        
        Returns:
            Thinking results with updated beliefs and context
        """
        detection = perception["detection"]
        
        # Update state based on detection
        if detection["confidence"] > state.detection_confidence:
            state.detection_confidence = detection["confidence"]
            state.scam_type = detection["scam_type"]
        
        # Update manipulation tactics
        for tactic in detection.get("manipulation_tactics", []):
            if tactic not in state.manipulation_tactics:
                state.manipulation_tactics.append(tactic)
        
        # Check conversation safety
        is_safe, safety_warning = self.safety.check_conversation_safety(
            state.message_count,
            state.get_duration(),
            state.detection_confidence
        )
        
        return {
            "is_safe": is_safe,
            "safety_warning": safety_warning,
            "scam_confirmed": detection["is_scam"],
            "scam_type": detection["scam_type"],
            "confidence": detection["confidence"]
        }
    
    def _decide(
        self,
        thinking: Dict[str, Any],
        state: ConversationState,
        memory: AgentMemory
    ) -> Dict[str, Any]:
        """
        DECIDE: Determine action strategy.
        
        Returns:
            Decision with strategy and actions to take
        """
        # If not safe to continue, decide to exit
        if not thinking["is_safe"]:
            return {
                "strategy": "exit",
                "phase": "completed",
                "reason": thinking.get("safety_warning", "Safety limit reached")
            }
        
        # Determine response strategy
        strategy, phase = ResponseStrategy.determine_strategy(
            thinking["confidence"],
            state.message_count,
            state.intelligence_extracted,
            thinking["scam_type"]
        )
        
        # Determine if we should ask extraction questions
        extraction_question = None
        if strategy == "extract":
            extraction_question = self.extractor.get_next_extraction_question({})
        
        return {
            "strategy": strategy,
            "phase": phase.value,
            "extraction_question": extraction_question,
            "continue_conversation": ResponseStrategy.should_continue_conversation(
                state.message_count,
                state.get_duration(),
                state.intelligence_extracted
            )
        }
    
    async def _act(
        self,
        decision: Dict[str, Any],
        incoming_message: str,
        state: ConversationState,
        memory: AgentMemory
    ) -> Dict[str, Any]:
        """
        ACT: Generate response based on decision.
        
        Returns:
            Action results with generated response
        """
        # If not continuing, return empty response
        if not decision.get("continue_conversation", True):
            return {"response": "", "should_respond": False}
        
        # Generate response using persona and strategy
        if not state.persona:
            # Select persona if not already set
            persona_template = self.persona_generator.select_persona(state.scam_type)
            state.persona = self.persona_generator.create_persona_context(persona_template)
        
        response = await self.response_generator.generate_response(
            incoming_message,
            state.persona,
            memory.get_recent_messages(),
            decision["strategy"],
            decision.get("extraction_question")
        )
        
        # Validate response against safety guardrails
        is_valid, violation = self.safety.validate_response(response)
        
        if not is_valid:
            # Use fallback safe response
            response = "I see. Let me think about this."
            memory.update_context("safety_violation", violation)
        
        return {
            "response": response,
            "should_respond": True,
            "validated": is_valid
        }
    
    def _learn(
        self,
        perception: Dict[str, Any],
        thinking: Dict[str, Any],
        decision: Dict[str, Any],
        action: Dict[str, Any],
        state: ConversationState,
        memory: AgentMemory
    ):
        """
        LEARN: Update state and memory based on the interaction.
        """
        # Add extracted intelligence to state
        for artifact in perception["extraction"].get("artifacts", []):
            state.add_intelligence(artifact["type"], artifact["value"])
        
        # Update conversation status based on phase
        if decision["phase"] == "completed":
            from app.models.conversation import ConversationStatus
            state.status = ConversationStatus.COMPLETED
        elif decision["phase"] == "stalling":
            from app.models.conversation import ConversationStatus
            state.status = ConversationStatus.STALLING
        
        # Update activity
        state.update_activity()
