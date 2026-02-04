"""Hidden Markov Model for scam stage detection."""
from enum import Enum
from typing import Dict, List, Tuple, Optional
import random


class ScamStage(str, Enum):
    """Stages of a scam attempt."""
    INITIAL_CONTACT = "initial_contact"
    BUILDING_TRUST = "building_trust"
    CREATING_URGENCY = "creating_urgency"
    PAYMENT_REQUEST = "payment_request"
    PRESSURE_TACTICS = "pressure_tactics"
    FINAL_PUSH = "final_push"
    COMPLETED = "completed"


class ScamHMM:
    """
    Hidden Markov Model for predicting scam progression stages.
    
    This model helps predict which stage of a scam the conversation is in,
    allowing the honeypot to adapt its responses accordingly.
    """
    
    def __init__(self):
        """Initialize HMM with transition probabilities."""
        # Transition probabilities: P(next_stage | current_stage)
        self.transitions = {
            ScamStage.INITIAL_CONTACT: {
                ScamStage.INITIAL_CONTACT: 0.3,
                ScamStage.BUILDING_TRUST: 0.6,
                ScamStage.CREATING_URGENCY: 0.1,
            },
            ScamStage.BUILDING_TRUST: {
                ScamStage.BUILDING_TRUST: 0.4,
                ScamStage.CREATING_URGENCY: 0.4,
                ScamStage.PAYMENT_REQUEST: 0.2,
            },
            ScamStage.CREATING_URGENCY: {
                ScamStage.CREATING_URGENCY: 0.2,
                ScamStage.PAYMENT_REQUEST: 0.6,
                ScamStage.PRESSURE_TACTICS: 0.2,
            },
            ScamStage.PAYMENT_REQUEST: {
                ScamStage.PAYMENT_REQUEST: 0.3,
                ScamStage.PRESSURE_TACTICS: 0.5,
                ScamStage.FINAL_PUSH: 0.2,
            },
            ScamStage.PRESSURE_TACTICS: {
                ScamStage.PRESSURE_TACTICS: 0.3,
                ScamStage.FINAL_PUSH: 0.5,
                ScamStage.PAYMENT_REQUEST: 0.2,  # May back off and try again
            },
            ScamStage.FINAL_PUSH: {
                ScamStage.FINAL_PUSH: 0.4,
                ScamStage.COMPLETED: 0.4,
                ScamStage.PRESSURE_TACTICS: 0.2,  # Last ditch effort
            },
            ScamStage.COMPLETED: {
                ScamStage.COMPLETED: 1.0,
            }
        }
        
        # Emission probabilities: P(observation | stage)
        # Observations are message features
        self.emissions = {
            ScamStage.INITIAL_CONTACT: {
                "greeting": 0.7,
                "introduction": 0.8,
                "trust_building": 0.3,
                "urgency": 0.1,
                "payment": 0.05,
            },
            ScamStage.BUILDING_TRUST: {
                "greeting": 0.2,
                "introduction": 0.3,
                "trust_building": 0.8,
                "urgency": 0.2,
                "payment": 0.1,
            },
            ScamStage.CREATING_URGENCY: {
                "greeting": 0.05,
                "introduction": 0.1,
                "trust_building": 0.3,
                "urgency": 0.9,
                "payment": 0.4,
            },
            ScamStage.PAYMENT_REQUEST: {
                "greeting": 0.05,
                "introduction": 0.05,
                "trust_building": 0.2,
                "urgency": 0.6,
                "payment": 0.9,
            },
            ScamStage.PRESSURE_TACTICS: {
                "greeting": 0.0,
                "introduction": 0.0,
                "trust_building": 0.1,
                "urgency": 0.95,
                "payment": 0.85,
            },
            ScamStage.FINAL_PUSH: {
                "greeting": 0.0,
                "introduction": 0.0,
                "trust_building": 0.05,
                "urgency": 0.98,
                "payment": 0.95,
            },
            ScamStage.COMPLETED: {
                "greeting": 0.1,
                "introduction": 0.0,
                "trust_building": 0.0,
                "urgency": 0.2,
                "payment": 0.3,
            }
        }
    
    def extract_features(self, message: str) -> Dict[str, float]:
        """
        Extract features from a message for HMM observation.
        
        Args:
            message: The message to analyze
        
        Returns:
            Dictionary of feature scores (0-1)
        """
        message_lower = message.lower()
        
        features = {}
        
        # Greeting detection
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good evening"]
        features["greeting"] = 1.0 if any(g in message_lower for g in greetings) else 0.0
        
        # Introduction detection
        intro_phrases = ["my name is", "i am", "i'm", "this is", "calling from"]
        features["introduction"] = 1.0 if any(p in message_lower for p in intro_phrases) else 0.0
        
        # Trust-building detection
        trust_words = ["trust", "believe", "honest", "genuine", "legitimate", "official"]
        features["trust_building"] = min(
            sum(1 for w in trust_words if w in message_lower) / 3, 1.0
        )
        
        # Urgency detection
        urgency_words = ["urgent", "immediately", "now", "quick", "hurry", "fast", "deadline"]
        features["urgency"] = min(
            sum(1 for w in urgency_words if w in message_lower) / 2, 1.0
        )
        
        # Payment detection
        payment_words = ["money", "payment", "pay", "transfer", "send", "amount", "rupees", "dollars"]
        features["payment"] = min(
            sum(1 for w in payment_words if w in message_lower) / 2, 1.0
        )
        
        return features
    
    def predict_stage(
        self,
        current_stage: ScamStage,
        message: str,
        message_history: Optional[List[str]] = None
    ) -> Tuple[ScamStage, float]:
        """
        Predict the next scam stage based on current stage and observations.
        
        Args:
            current_stage: Current stage of the scam
            message: Latest message from scammer
            message_history: Optional conversation history
        
        Returns:
            Tuple of (predicted_stage, confidence)
        """
        # Extract features from current message
        features = self.extract_features(message)
        
        # Calculate probabilities for each possible next stage
        stage_probabilities = {}
        
        for next_stage, transition_prob in self.transitions[current_stage].items():
            # Calculate emission probability
            emission_prob = 1.0
            for feature, value in features.items():
                if feature in self.emissions[next_stage]:
                    # P(observation | stage)
                    emission_prob *= (
                        self.emissions[next_stage][feature] * value +
                        (1 - self.emissions[next_stage][feature]) * (1 - value)
                    )
            
            # Combined probability: P(next_stage | current) * P(observation | next_stage)
            stage_probabilities[next_stage] = transition_prob * emission_prob
        
        # Normalize probabilities
        total_prob = sum(stage_probabilities.values())
        if total_prob > 0:
            stage_probabilities = {
                stage: prob / total_prob
                for stage, prob in stage_probabilities.items()
            }
        
        # Get most likely stage
        if stage_probabilities:
            predicted_stage = max(stage_probabilities, key=stage_probabilities.get)
            confidence = stage_probabilities[predicted_stage]
        else:
            predicted_stage = current_stage
            confidence = 0.5
        
        return predicted_stage, confidence
    
    def get_stage_description(self, stage: ScamStage) -> str:
        """Get human-readable description of a scam stage."""
        descriptions = {
            ScamStage.INITIAL_CONTACT: "Scammer is making initial contact and gauging target",
            ScamStage.BUILDING_TRUST: "Scammer is building trust and rapport",
            ScamStage.CREATING_URGENCY: "Scammer is creating a sense of urgency",
            ScamStage.PAYMENT_REQUEST: "Scammer is requesting payment or financial information",
            ScamStage.PRESSURE_TACTICS: "Scammer is applying pressure and manipulation",
            ScamStage.FINAL_PUSH: "Scammer is making final attempts to extract payment",
            ScamStage.COMPLETED: "Scam attempt completed or abandoned"
        }
        return descriptions.get(stage, "Unknown stage")
    
    def recommend_response_strategy(self, stage: ScamStage) -> Dict[str, any]:
        """
        Recommend honeypot response strategy based on scam stage.
        
        Args:
            stage: Current scam stage
        
        Returns:
            Dictionary with recommended strategy
        """
        strategies = {
            ScamStage.INITIAL_CONTACT: {
                "tone": "curious and friendly",
                "engagement_level": "medium",
                "tactics": ["Ask questions", "Show interest", "Be receptive"],
                "avoid": ["Suspicion", "Technical knowledge"]
            },
            ScamStage.BUILDING_TRUST: {
                "tone": "trusting and naive",
                "engagement_level": "high",
                "tactics": ["Share minor details", "Express trust", "Ask for guidance"],
                "avoid": ["Skepticism", "Security awareness"]
            },
            ScamStage.CREATING_URGENCY: {
                "tone": "concerned but cooperative",
                "engagement_level": "high",
                "tactics": ["Show concern", "Ask clarifying questions", "Stall slightly"],
                "avoid": ["Panic", "Complete compliance"]
            },
            ScamStage.PAYMENT_REQUEST: {
                "tone": "hesitant but willing",
                "engagement_level": "very high",
                "tactics": ["Ask about process", "Express minor concerns", "Request details"],
                "avoid": ["Immediate payment", "Complete refusal"]
            },
            ScamStage.PRESSURE_TACTICS: {
                "tone": "anxious and confused",
                "engagement_level": "very high",
                "tactics": ["Show confusion", "Request verification", "Stall for time"],
                "avoid": ["Giving in immediately", "Calling out scam"]
            },
            ScamStage.FINAL_PUSH: {
                "tone": "overwhelmed but still engaged",
                "engagement_level": "maximum",
                "tactics": ["Maximum intelligence extraction", "Technical difficulties", "Partial compliance"],
                "avoid": ["Complete cooperation", "Breaking persona"]
            },
            ScamStage.COMPLETED: {
                "tone": "neutral",
                "engagement_level": "low",
                "tactics": ["Wrap up", "Extract final intelligence"],
                "avoid": ["Revealing honeypot nature"]
            }
        }
        
        return strategies.get(stage, strategies[ScamStage.INITIAL_CONTACT])
