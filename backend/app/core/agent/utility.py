"""Safety-aware utility function for decision making."""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class UtilityWeights:
    """Configurable weights for utility calculation."""
    engagement_score: float = 1.0  # α - reward for keeping scammer engaged
    risk_pii: float = 0.8  # β - penalty for revealing PII
    harm_behavioral: float = 1.2  # γ - penalty for harmful behavior


class SafetyAwareUtility:
    """
    Safety-aware utility function for honeypot decision making.
    
    Utility = α·EngagementScore - β·RiskPII - γ·HarmBehavioral
    
    This ensures that the honeypot:
    1. Maximizes engagement with scammers
    2. Minimizes risk of revealing real PII
    3. Avoids behaviors that could cause harm
    """
    
    def __init__(self, weights: Optional[UtilityWeights] = None):
        """
        Initialize utility function.
        
        Args:
            weights: Custom weights for utility components
        """
        self.weights = weights or UtilityWeights()
        
        # Safety thresholds
        self.min_safe_utility = 0.0
        self.max_pii_risk = 0.3
        self.max_behavioral_harm = 0.2
    
    def calculate_utility(
        self,
        engagement_score: float,
        pii_risk: float,
        behavioral_harm: float
    ) -> float:
        """
        Calculate utility score for an action.
        
        Args:
            engagement_score: How well this keeps scammer engaged (0-1)
            pii_risk: Risk of revealing PII (0-1)
            behavioral_harm: Potential for behavioral harm (0-1)
        
        Returns:
            Utility score (higher is better)
        """
        utility = (
            self.weights.engagement_score * engagement_score -
            self.weights.risk_pii * pii_risk -
            self.weights.harm_behavioral * behavioral_harm
        )
        
        return utility
    
    def evaluate_response(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Evaluate a response candidate.
        
        Args:
            response: The proposed response
            context: Conversation context
        
        Returns:
            Dictionary with scores and utility
        """
        # Calculate engagement score
        engagement = self._calculate_engagement_score(response, context)
        
        # Calculate PII risk
        pii_risk = self._calculate_pii_risk(response)
        
        # Calculate behavioral harm
        behavioral_harm = self._calculate_behavioral_harm(response, context)
        
        # Calculate total utility
        utility = self.calculate_utility(engagement, pii_risk, behavioral_harm)
        
        return {
            "engagement_score": engagement,
            "pii_risk": pii_risk,
            "behavioral_harm": behavioral_harm,
            "utility": utility,
            "is_safe": self.is_safe_response(pii_risk, behavioral_harm),
            "recommendation": self._get_recommendation(utility, pii_risk, behavioral_harm)
        }
    
    def _calculate_engagement_score(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate how well response engages scammer."""
        score = 0.5  # Base score
        
        response_lower = response.lower()
        
        # Positive engagement factors
        if any(word in response_lower for word in ["yes", "okay", "sure", "will do"]):
            score += 0.2
        
        if any(word in response_lower for word in ["?", "how", "what", "when", "where"]):
            score += 0.15  # Asking questions keeps conversation going
        
        if len(response.split()) > 10:
            score += 0.1  # Detailed responses show engagement
        
        # Negative engagement factors
        if any(word in response_lower for word in ["no", "can't", "won't", "refuse"]):
            score -= 0.3
        
        if any(word in response_lower for word in ["scam", "fraud", "police", "report"]):
            score -= 0.5  # Breaking persona
        
        return max(0.0, min(1.0, score))
    
    def _calculate_pii_risk(self, response: str) -> float:
        """Calculate risk of revealing real PII."""
        risk = 0.0
        response_lower = response.lower()
        
        # Check for real credentials (these should never appear)
        high_risk_patterns = [
            "password", "pin", "otp", "cvv", 
            "real account", "actual account",
            "my real", "actual number"
        ]
        
        for pattern in high_risk_patterns:
            if pattern in response_lower:
                risk += 0.4
        
        # Check for realistic-looking fake data that might be too convincing
        # (We want obviously fake data)
        if any(word in response_lower for word in ["verify", "confirm", "authentic"]):
            # If we're confirming data, it better be obviously fake
            risk += 0.1
        
        return min(1.0, risk)
    
    def _calculate_behavioral_harm(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate potential for behavioral harm."""
        harm = 0.0
        response_lower = response.lower()
        
        # Wasting too much of the scammer's time without extracting intelligence
        # is not our goal - we want intelligence, not just time wasting
        if context.get("turn_number", 0) > 30:
            intelligence_count = context.get("intelligence_extracted", 0)
            if intelligence_count < 2:
                harm += 0.2  # Not extracting enough intelligence
        
        # Encouraging illegal behavior
        illegal_keywords = ["steal", "hack", "break into", "illegal"]
        if any(keyword in response_lower for keyword in illegal_keywords):
            harm += 0.5
        
        # Being too aggressive or hostile (breaks persona)
        hostile_keywords = ["stupid", "idiot", "fool", "hate"]
        if any(keyword in response_lower for keyword in hostile_keywords):
            harm += 0.3
        
        return min(1.0, harm)
    
    def is_safe_response(self, pii_risk: float, behavioral_harm: float) -> bool:
        """Check if response meets safety thresholds."""
        return (
            pii_risk <= self.max_pii_risk and
            behavioral_harm <= self.max_behavioral_harm
        )
    
    def _get_recommendation(
        self,
        utility: float,
        pii_risk: float,
        behavioral_harm: float
    ) -> str:
        """Get recommendation based on scores."""
        if not self.is_safe_response(pii_risk, behavioral_harm):
            if pii_risk > self.max_pii_risk:
                return "REJECT: PII risk too high"
            else:
                return "REJECT: Behavioral harm too high"
        
        if utility >= 0.5:
            return "APPROVE: Good utility, safe response"
        elif utility >= 0.0:
            return "CONSIDER: Moderate utility, acceptable"
        else:
            return "REJECT: Negative utility"
    
    def select_best_response(
        self,
        candidates: List[str],
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, float]]:
        """
        Select best response from candidates using utility function.
        
        Args:
            candidates: List of candidate responses
            context: Conversation context
        
        Returns:
            Tuple of (best_response, evaluation_scores)
        """
        best_response = None
        best_evaluation = None
        best_utility = float('-inf')
        
        for candidate in candidates:
            evaluation = self.evaluate_response(candidate, context)
            
            # Only consider safe responses
            if evaluation["is_safe"]:
                if evaluation["utility"] > best_utility:
                    best_utility = evaluation["utility"]
                    best_response = candidate
                    best_evaluation = evaluation
        
        # If no safe response found, return None or a default
        if best_response is None:
            # Return a safe default
            best_response = "I need to think about this. Can you give me more details?"
            best_evaluation = self.evaluate_response(best_response, context)
        
        return best_response, best_evaluation
