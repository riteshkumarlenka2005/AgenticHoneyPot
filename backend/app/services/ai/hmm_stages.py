"""Hidden Markov Model for Scam Stage Prediction."""
from typing import Dict, List, Tuple
from enum import Enum
import numpy as np
from datetime import datetime


class ScamStage(str, Enum):
    """Scam conversation stages."""
    INITIAL_CONTACT = "initial_contact"
    TRUST_BUILDING = "trust_building"
    INFORMATION_GATHERING = "information_gathering"
    URGENCY_CREATION = "urgency_creation"
    PAYMENT_REQUEST = "payment_request"
    ESCALATION = "escalation"
    EXIT = "exit"


class HMMStagePredictor:
    """
    Hidden Markov Model for predicting scam conversation stages.
    
    Uses a 7-stage model with transition probabilities to identify
    where in the scam process the conversation currently is.
    """

    def __init__(self):
        """Initialize HMM with transition probabilities."""
        self.stages = list(ScamStage)
        self.num_states = len(self.stages)
        
        # Transition matrix: P(next_state | current_state)
        # Higher values on diagonal + next stage indicate typical progression
        self.transition_matrix = np.array([
            # From:    IC    TB    IG    UC    PR    ES    EX
            [0.30, 0.50, 0.10, 0.05, 0.03, 0.01, 0.01],  # Initial Contact
            [0.05, 0.35, 0.45, 0.10, 0.03, 0.01, 0.01],  # Trust Building
            [0.02, 0.10, 0.40, 0.35, 0.10, 0.02, 0.01],  # Information Gathering
            [0.01, 0.05, 0.10, 0.35, 0.40, 0.08, 0.01],  # Urgency Creation
            [0.01, 0.02, 0.05, 0.15, 0.40, 0.30, 0.07],  # Payment Request
            [0.01, 0.01, 0.03, 0.10, 0.30, 0.40, 0.15],  # Escalation
            [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00],  # Exit (absorbing)
        ])
        
        # Initial state probabilities
        self.initial_probs = np.array([0.70, 0.20, 0.05, 0.03, 0.01, 0.01, 0.00])
        
        # Keywords/patterns for each stage (for emission probabilities)
        self.stage_indicators = {
            ScamStage.INITIAL_CONTACT: [
                "hello", "hi", "greetings", "dear", "sir", "madam",
                "need help", "opportunity", "winner", "selected"
            ],
            ScamStage.TRUST_BUILDING: [
                "trust", "legitimate", "verified", "official", "registered",
                "government", "company", "organization", "certificate"
            ],
            ScamStage.INFORMATION_GATHERING: [
                "name", "address", "details", "information", "confirm",
                "verify", "account", "number", "email", "phone"
            ],
            ScamStage.URGENCY_CREATION: [
                "urgent", "immediately", "now", "today", "hurry", "limited time",
                "expire", "deadline", "quick", "fast", "asap"
            ],
            ScamStage.PAYMENT_REQUEST: [
                "pay", "payment", "money", "transfer", "send", "amount",
                "fee", "charge", "cost", "price", "rupees", "upi", "bank"
            ],
            ScamStage.ESCALATION: [
                "final", "last chance", "warning", "consequences", "legal",
                "police", "arrest", "penalty", "fine", "action"
            ],
            ScamStage.EXIT: [
                "thank you", "goodbye", "completed", "done", "received",
                "confirmed", "bye", "take care"
            ]
        }

    def calculate_emission_probability(
        self, message: str, stage: ScamStage
    ) -> float:
        """
        Calculate probability of observing this message given the stage.
        
        Args:
            message: The message content
            stage: The scam stage
            
        Returns:
            Probability score (0-1)
        """
        message_lower = message.lower()
        indicators = self.stage_indicators[stage]
        
        # Count matching keywords
        matches = sum(1 for keyword in indicators if keyword in message_lower)
        
        # Normalize by number of indicators
        if len(indicators) > 0:
            score = matches / len(indicators)
        else:
            score = 0.0
            
        # Ensure minimum probability
        return max(score, 0.01)

    def predict_stage(
        self,
        messages: List[Dict],
        current_stage: ScamStage = ScamStage.INITIAL_CONTACT
    ) -> Tuple[ScamStage, float, Dict[ScamStage, float]]:
        """
        Predict the current scam stage based on message history.
        
        Args:
            messages: List of message dicts with 'content' and 'sender_type'
            current_stage: Previous known stage
            
        Returns:
            Tuple of (predicted_stage, confidence, stage_probabilities)
        """
        if not messages:
            return ScamStage.INITIAL_CONTACT, 1.0, {ScamStage.INITIAL_CONTACT: 1.0}
        
        # Get current state index
        current_idx = self.stages.index(current_stage)
        
        # Start with current state distribution
        state_probs = np.zeros(self.num_states)
        state_probs[current_idx] = 1.0
        
        # Process recent messages (last 5 for efficiency)
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        
        for msg in recent_messages:
            # Skip honeypot messages, only analyze scammer messages
            if msg.get("sender_type") == "honeypot":
                continue
                
            content = msg.get("content", "")
            
            # Calculate emission probabilities for this message
            emissions = np.array([
                self.calculate_emission_probability(content, stage)
                for stage in self.stages
            ])
            
            # Forward step: predict next state
            state_probs = state_probs @ self.transition_matrix
            
            # Update with observation
            state_probs = state_probs * emissions
            
            # Normalize
            total = state_probs.sum()
            if total > 0:
                state_probs = state_probs / total
        
        # Get most likely stage
        predicted_idx = np.argmax(state_probs)
        predicted_stage = self.stages[predicted_idx]
        confidence = float(state_probs[predicted_idx])
        
        # Convert to dict
        stage_probabilities = {
            stage: float(state_probs[i])
            for i, stage in enumerate(self.stages)
        }
        
        return predicted_stage, confidence, stage_probabilities

    def get_transition_probability(
        self, from_stage: ScamStage, to_stage: ScamStage
    ) -> float:
        """Get transition probability between two stages."""
        from_idx = self.stages.index(from_stage)
        to_idx = self.stages.index(to_stage)
        return float(self.transition_matrix[from_idx, to_idx])

    def get_stage_info(self, stage: ScamStage) -> Dict:
        """Get detailed information about a scam stage."""
        stage_descriptions = {
            ScamStage.INITIAL_CONTACT: {
                "description": "Scammer makes first contact, presents bait or opportunity",
                "risk_level": "low",
                "typical_duration": "1-3 messages"
            },
            ScamStage.TRUST_BUILDING: {
                "description": "Scammer establishes credibility and legitimacy",
                "risk_level": "medium",
                "typical_duration": "3-7 messages"
            },
            ScamStage.INFORMATION_GATHERING: {
                "description": "Scammer requests personal or financial information",
                "risk_level": "medium-high",
                "typical_duration": "2-5 messages"
            },
            ScamStage.URGENCY_CREATION: {
                "description": "Scammer creates time pressure to force quick decisions",
                "risk_level": "high",
                "typical_duration": "2-4 messages"
            },
            ScamStage.PAYMENT_REQUEST: {
                "description": "Scammer requests money or financial transaction",
                "risk_level": "critical",
                "typical_duration": "1-3 messages"
            },
            ScamStage.ESCALATION: {
                "description": "Scammer increases pressure with threats or warnings",
                "risk_level": "critical",
                "typical_duration": "1-3 messages"
            },
            ScamStage.EXIT: {
                "description": "Scammer completes interaction or abandons attempt",
                "risk_level": "low",
                "typical_duration": "1-2 messages"
            }
        }
        return stage_descriptions.get(stage, {})
