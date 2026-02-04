"""Dialogue State Tracking (DST) for conversation management."""
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ExtractionGoal(str, Enum):
    """Goals for intelligence extraction."""
    UPI_ID = "upi_id"
    BANK_ACCOUNT = "bank_account"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    URL = "url"
    IFSC_CODE = "ifsc_code"
    SCAMMER_NAME = "scammer_name"
    ORGANIZATION = "organization"


@dataclass
class DialogueSlot:
    """Represents a slot in the dialogue state."""
    name: str
    value: Optional[Any] = None
    confidence: float = 0.0
    source_turn: int = 0
    confirmed: bool = False
    
    def update(self, value: Any, confidence: float, turn: int):
        """Update slot with new value."""
        self.value = value
        self.confidence = confidence
        self.source_turn = turn


@dataclass
class DialogueState:
    """
    Tracks the state of the dialogue for effective conversation management.
    
    This includes:
    - Extracted information (slots)
    - Goals (what we're trying to extract)
    - Context (conversation history summary)
    - Confidence scores
    """
    
    # Conversation metadata
    conversation_id: str
    turn_number: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    # Slots for extracted information
    slots: Dict[str, DialogueSlot] = field(default_factory=dict)
    
    # Goals we're trying to achieve
    active_goals: Set[ExtractionGoal] = field(default_factory=set)
    completed_goals: Set[ExtractionGoal] = field(default_factory=set)
    
    # Conversation context
    scam_type: Optional[str] = None
    scam_confidence: float = 0.0
    current_stage: str = "initial_contact"
    
    # Behavioral tracking
    scammer_traits: List[str] = field(default_factory=list)
    manipulation_tactics: List[str] = field(default_factory=list)
    
    def add_slot(self, name: str, value: Any, confidence: float = 1.0):
        """Add or update a slot."""
        if name not in self.slots:
            self.slots[name] = DialogueSlot(
                name=name,
                value=value,
                confidence=confidence,
                source_turn=self.turn_number
            )
        else:
            self.slots[name].update(value, confidence, self.turn_number)
    
    def get_slot(self, name: str) -> Optional[DialogueSlot]:
        """Get a slot by name."""
        return self.slots.get(name)
    
    def has_slot(self, name: str) -> bool:
        """Check if slot exists and has value."""
        slot = self.slots.get(name)
        return slot is not None and slot.value is not None
    
    def add_goal(self, goal: ExtractionGoal):
        """Add an extraction goal."""
        self.active_goals.add(goal)
    
    def complete_goal(self, goal: ExtractionGoal):
        """Mark a goal as completed."""
        if goal in self.active_goals:
            self.active_goals.remove(goal)
        self.completed_goals.add(goal)
    
    def get_completion_rate(self) -> float:
        """Get the goal completion rate."""
        total_goals = len(self.active_goals) + len(self.completed_goals)
        if total_goals == 0:
            return 0.0
        return len(self.completed_goals) / total_goals
    
    def increment_turn(self):
        """Increment turn number."""
        self.turn_number += 1
    
    def update_context(
        self,
        scam_type: Optional[str] = None,
        scam_confidence: Optional[float] = None,
        stage: Optional[str] = None
    ):
        """Update conversation context."""
        if scam_type:
            self.scam_type = scam_type
        if scam_confidence is not None:
            self.scam_confidence = scam_confidence
        if stage:
            self.current_stage = stage
    
    def add_manipulation_tactic(self, tactic: str):
        """Record a manipulation tactic used by scammer."""
        if tactic not in self.manipulation_tactics:
            self.manipulation_tactics.append(tactic)
    
    def add_scammer_trait(self, trait: str):
        """Record a trait observed in the scammer."""
        if trait not in self.scammer_traits:
            self.scammer_traits.append(trait)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the dialogue state."""
        return {
            "conversation_id": self.conversation_id,
            "turn_number": self.turn_number,
            "scam_type": self.scam_type,
            "scam_confidence": self.scam_confidence,
            "current_stage": self.current_stage,
            "active_goals": [goal.value for goal in self.active_goals],
            "completed_goals": [goal.value for goal in self.completed_goals],
            "completion_rate": self.get_completion_rate(),
            "slots_filled": len([s for s in self.slots.values() if s.value is not None]),
            "total_slots": len(self.slots),
            "manipulation_tactics": self.manipulation_tactics,
            "scammer_traits": self.scammer_traits
        }
    
    def should_continue_engagement(self) -> bool:
        """Determine if we should continue engaging with scammer."""
        # Continue if we haven't completed all goals
        if self.active_goals:
            return True
        
        # Continue if scam confidence is high but we haven't extracted much
        if self.scam_confidence > 0.7 and len(self.slots) < 5:
            return True
        
        # Stop if we've been going for too long without progress
        if self.turn_number > 50 and self.get_completion_rate() < 0.3:
            return False
        
        return True
    
    def get_next_question_topic(self) -> Optional[str]:
        """Suggest next topic to ask about based on active goals."""
        # Prioritize goals by importance
        goal_priority = [
            ExtractionGoal.BANK_ACCOUNT,
            ExtractionGoal.UPI_ID,
            ExtractionGoal.PHONE_NUMBER,
            ExtractionGoal.EMAIL,
            ExtractionGoal.URL,
            ExtractionGoal.IFSC_CODE,
            ExtractionGoal.SCAMMER_NAME,
            ExtractionGoal.ORGANIZATION
        ]
        
        for goal in goal_priority:
            if goal in self.active_goals:
                return goal.value
        
        return None


class DialogueStateTracker:
    """Manages dialogue state updates and queries."""
    
    def __init__(self):
        """Initialize dialogue state tracker."""
        self.states: Dict[str, DialogueState] = {}
    
    def create_state(self, conversation_id: str) -> DialogueState:
        """Create a new dialogue state for a conversation."""
        state = DialogueState(conversation_id=conversation_id)
        
        # Initialize with default extraction goals
        state.add_goal(ExtractionGoal.UPI_ID)
        state.add_goal(ExtractionGoal.BANK_ACCOUNT)
        state.add_goal(ExtractionGoal.PHONE_NUMBER)
        
        self.states[conversation_id] = state
        return state
    
    def get_state(self, conversation_id: str) -> Optional[DialogueState]:
        """Get dialogue state for a conversation."""
        return self.states.get(conversation_id)
    
    def update_from_message(
        self,
        conversation_id: str,
        message: str,
        extracted_info: Dict[str, Any]
    ):
        """
        Update dialogue state based on a new message.
        
        Args:
            conversation_id: ID of the conversation
            message: The message content
            extracted_info: Information extracted from the message
        """
        state = self.get_state(conversation_id)
        if not state:
            state = self.create_state(conversation_id)
        
        state.increment_turn()
        
        # Update slots with extracted information
        for key, value in extracted_info.items():
            if value:
                state.add_slot(key, value, confidence=0.8)
                
                # Check if this completes a goal
                try:
                    goal = ExtractionGoal(key)
                    if goal in state.active_goals:
                        state.complete_goal(goal)
                except ValueError:
                    pass
    
    def get_engagement_strategy(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get recommended engagement strategy based on dialogue state.
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            Dictionary with engagement recommendations
        """
        state = self.get_state(conversation_id)
        if not state:
            return {"continue": True, "focus": "general", "tone": "neutral"}
        
        return {
            "continue": state.should_continue_engagement(),
            "focus": state.get_next_question_topic(),
            "tone": self._recommend_tone(state),
            "completion_rate": state.get_completion_rate(),
            "priority_goals": list(state.active_goals)[:3]  # Top 3
        }
    
    def _recommend_tone(self, state: DialogueState) -> str:
        """Recommend conversation tone based on state."""
        if state.current_stage == "initial_contact":
            return "curious"
        elif state.current_stage in ["building_trust", "creating_urgency"]:
            return "trusting"
        elif state.current_stage in ["payment_request", "pressure_tactics"]:
            return "hesitant"
        else:
            return "neutral"
