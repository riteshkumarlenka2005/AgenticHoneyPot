"""Hidden Markov Model for scam stage prediction."""
from enum import Enum
from typing import List, Dict, Tuple
import numpy as np


class ScamStage(str, Enum):
    """Scam conversation stages."""
    INITIAL_CONTACT = "initial_contact"  # First message, hook/bait
    BUILDING_TRUST = "building_trust"    # Establishing credibility
    CREATING_URGENCY = "creating_urgency"  # Time pressure, FOMO
    PAYMENT_REQUEST = "payment_request"  # Asking for money/details
    FOLLOW_UP = "follow_up"              # Following up on request
    ESCALATION = "escalation"            # Increasing pressure
    RESOLUTION = "resolution"            # Deal closed or victim lost


class ScamStageHMM:
    """Hidden Markov Model for predicting scam stages."""
    
    def __init__(self):
        """Initialize HMM with transition probabilities."""
        self.stages = list(ScamStage)
        self.num_states = len(self.stages)
        
        # Transition probability matrix
        # Row = current state, Column = next state
        self.transition_matrix = self._build_transition_matrix()
        
        # Initial state probabilities
        self.initial_probs = self._build_initial_probs()
        
        # Observation keywords for each stage
        self.stage_keywords = self._build_stage_keywords()
    
    def _build_transition_matrix(self) -> np.ndarray:
        """Build transition probability matrix."""
        # Initialize with small probability everywhere
        matrix = np.ones((self.num_states, self.num_states)) * 0.01
        
        # Define likely transitions
        transitions = {
            ScamStage.INITIAL_CONTACT: {
                ScamStage.BUILDING_TRUST: 0.7,
                ScamStage.PAYMENT_REQUEST: 0.2,  # Aggressive scammers
                ScamStage.INITIAL_CONTACT: 0.09
            },
            ScamStage.BUILDING_TRUST: {
                ScamStage.BUILDING_TRUST: 0.3,
                ScamStage.CREATING_URGENCY: 0.5,
                ScamStage.PAYMENT_REQUEST: 0.19
            },
            ScamStage.CREATING_URGENCY: {
                ScamStage.PAYMENT_REQUEST: 0.6,
                ScamStage.CREATING_URGENCY: 0.2,
                ScamStage.ESCALATION: 0.19
            },
            ScamStage.PAYMENT_REQUEST: {
                ScamStage.PAYMENT_REQUEST: 0.3,
                ScamStage.FOLLOW_UP: 0.4,
                ScamStage.ESCALATION: 0.2,
                ScamStage.RESOLUTION: 0.09
            },
            ScamStage.FOLLOW_UP: {
                ScamStage.FOLLOW_UP: 0.2,
                ScamStage.ESCALATION: 0.5,
                ScamStage.PAYMENT_REQUEST: 0.2,
                ScamStage.RESOLUTION: 0.09
            },
            ScamStage.ESCALATION: {
                ScamStage.ESCALATION: 0.3,
                ScamStage.PAYMENT_REQUEST: 0.3,
                ScamStage.RESOLUTION: 0.39
            },
            ScamStage.RESOLUTION: {
                ScamStage.RESOLUTION: 0.99
            }
        }
        
        # Fill matrix
        for i, from_stage in enumerate(self.stages):
            if from_stage in transitions:
                for to_stage, prob in transitions[from_stage].items():
                    j = self.stages.index(to_stage)
                    matrix[i][j] = prob
        
        # Normalize rows
        for i in range(self.num_states):
            row_sum = matrix[i].sum()
            matrix[i] = matrix[i] / row_sum
        
        return matrix
    
    def _build_initial_probs(self) -> np.ndarray:
        """Build initial state probabilities."""
        probs = np.zeros(self.num_states)
        probs[self.stages.index(ScamStage.INITIAL_CONTACT)] = 0.98
        probs[self.stages.index(ScamStage.BUILDING_TRUST)] = 0.02
        return probs
    
    def _build_stage_keywords(self) -> Dict[ScamStage, List[str]]:
        """Build keyword indicators for each stage."""
        return {
            ScamStage.INITIAL_CONTACT: [
                "congratulations", "winner", "selected", "lucky", "prize",
                "hello", "dear", "sir", "madam", "customer"
            ],
            ScamStage.BUILDING_TRUST: [
                "official", "verified", "certified", "legitimate", "government",
                "bank", "company", "representative", "authorized"
            ],
            ScamStage.CREATING_URGENCY: [
                "urgent", "immediately", "today", "expire", "limited time",
                "only", "hours", "minutes", "last chance", "hurry"
            ],
            ScamStage.PAYMENT_REQUEST: [
                "pay", "payment", "transfer", "send", "fee", "tax",
                "account", "upi", "bank", "card", "money", "amount"
            ],
            ScamStage.FOLLOW_UP: [
                "did you", "have you", "waiting", "confirm", "confirmation",
                "status", "update", "check", "received"
            ],
            ScamStage.ESCALATION: [
                "problem", "issue", "blocked", "suspended", "locked",
                "legal", "action", "consequences", "penalty", "fine"
            ],
            ScamStage.RESOLUTION: [
                "thank you", "received", "processed", "completed", "done",
                "final", "ended", "closed"
            ]
        }
    
    def predict_stage(
        self,
        message: str,
        previous_stage: ScamStage = None
    ) -> Tuple[ScamStage, float]:
        """
        Predict current scam stage based on message and history.
        
        Args:
            message: Current message content
            previous_stage: Previous stage in conversation
        
        Returns:
            Tuple of (predicted_stage, confidence)
        """
        message_lower = message.lower()
        
        # Calculate emission probabilities (how likely is this message in each stage)
        emission_probs = np.zeros(self.num_states)
        
        for i, stage in enumerate(self.stages):
            keywords = self.stage_keywords[stage]
            matches = sum(1 for kw in keywords if kw in message_lower)
            # Normalize by number of keywords
            emission_probs[i] = matches / len(keywords) if keywords else 0
        
        # Smooth with small probability
        emission_probs = emission_probs + 0.01
        emission_probs = emission_probs / emission_probs.sum()
        
        # If we have previous stage, use transition probabilities
        if previous_stage:
            prev_idx = self.stages.index(previous_stage)
            transition_probs = self.transition_matrix[prev_idx]
            
            # Combine emission and transition probabilities
            combined_probs = emission_probs * transition_probs
            combined_probs = combined_probs / combined_probs.sum()
        else:
            # Use initial probabilities
            combined_probs = emission_probs * self.initial_probs
            combined_probs = combined_probs / combined_probs.sum()
        
        # Get most likely stage
        best_idx = np.argmax(combined_probs)
        best_stage = self.stages[best_idx]
        confidence = combined_probs[best_idx]
        
        return best_stage, float(confidence)
    
    def predict_sequence(
        self,
        messages: List[str]
    ) -> List[Tuple[ScamStage, float]]:
        """
        Predict stages for a sequence of messages using Viterbi algorithm.
        
        Args:
            messages: List of message contents
        
        Returns:
            List of (stage, confidence) tuples
        """
        if not messages:
            return []
        
        predictions = []
        previous_stage = None
        
        for message in messages:
            stage, confidence = self.predict_stage(message, previous_stage)
            predictions.append((stage, confidence))
            previous_stage = stage
        
        return predictions


# Global HMM instance
scam_stage_hmm = ScamStageHMM()
