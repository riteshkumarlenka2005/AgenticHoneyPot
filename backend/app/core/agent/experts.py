"""Multi-role expert prompting (MRML Strategy) for enhanced scam analysis."""
from typing import Dict, List, Any
from abc import ABC, abstractmethod


class ExpertAgent(ABC):
    """Base class for expert agents in the MRML system."""
    
    @abstractmethod
    def get_role_description(self) -> str:
        """Get description of this expert's role."""
        pass
    
    @abstractmethod
    def analyze(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a message from this expert's perspective.
        
        Args:
            message: The message to analyze
            context: Additional context (conversation history, etc.)
        
        Returns:
            Analysis results from this expert's viewpoint
        """
        pass


class TextAnalystExpert(ExpertAgent):
    """Expert in linguistic analysis and communication patterns."""
    
    def get_role_description(self) -> str:
        return (
            "You are a forensic linguist and text analyst. "
            "You analyze communication patterns, detect deception, "
            "identify manipulation tactics, and assess linguistic markers "
            "that indicate scam attempts."
        )
    
    def analyze(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text patterns, tone, and linguistic markers."""
        analysis = {
            "expert": "text_analyst",
            "confidence": 0.0,
            "findings": []
        }
        
        # Analyze urgency markers
        urgency_words = ["urgent", "immediately", "now", "quick", "hurry", "fast"]
        urgency_count = sum(1 for word in urgency_words if word in message.lower())
        
        if urgency_count > 0:
            analysis["findings"].append({
                "type": "urgency_pressure",
                "severity": min(urgency_count / 3, 1.0),
                "description": f"Message contains {urgency_count} urgency markers"
            })
        
        # Analyze trust-building language
        trust_words = ["trust me", "believe me", "honestly", "i promise", "guarantee"]
        trust_building = any(phrase in message.lower() for phrase in trust_words)
        
        if trust_building:
            analysis["findings"].append({
                "type": "trust_manipulation",
                "severity": 0.6,
                "description": "Excessive trust-building language detected"
            })
        
        # Analyze emotional manipulation
        emotion_words = ["sad", "help", "desperate", "emergency", "crisis", "suffering"]
        emotion_count = sum(1 for word in emotion_words if word in message.lower())
        
        if emotion_count > 1:
            analysis["findings"].append({
                "type": "emotional_manipulation",
                "severity": min(emotion_count / 4, 1.0),
                "description": "High emotional pressure detected"
            })
        
        # Calculate confidence
        if analysis["findings"]:
            analysis["confidence"] = sum(f["severity"] for f in analysis["findings"]) / len(analysis["findings"])
        
        return analysis


class BusinessProcessExpert(ExpertAgent):
    """Expert in financial processes and legitimate business operations."""
    
    def get_role_description(self) -> str:
        return (
            "You are a business process and financial operations expert. "
            "You understand legitimate banking procedures, payment processes, "
            "and identify deviations from standard business practices."
        )
    
    def analyze(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for business process violations."""
        analysis = {
            "expert": "business_process",
            "confidence": 0.0,
            "findings": []
        }
        
        message_lower = message.lower()
        
        # Check for unusual payment requests
        if any(word in message_lower for word in ["send money", "transfer", "payment", "pay"]):
            if any(word in message_lower for word in ["urgent", "immediately", "now"]):
                analysis["findings"].append({
                    "type": "irregular_payment_request",
                    "severity": 0.8,
                    "description": "Urgent payment request outside normal business process"
                })
        
        # Check for verification bypasses
        bypass_phrases = [
            "don't need", "skip", "bypass", "ignore",
            "no need for", "without verification"
        ]
        if any(phrase in message_lower for phrase in bypass_phrases):
            analysis["findings"].append({
                "type": "process_bypass_attempt",
                "severity": 0.7,
                "description": "Attempt to bypass standard verification procedures"
            })
        
        # Check for unconventional payment methods
        unconventional = ["gift card", "bitcoin", "cryptocurrency", "western union", "moneygram"]
        if any(method in message_lower for method in unconventional):
            analysis["findings"].append({
                "type": "unconventional_payment",
                "severity": 0.9,
                "description": "Request for non-standard payment method"
            })
        
        # Calculate confidence
        if analysis["findings"]:
            analysis["confidence"] = sum(f["severity"] for f in analysis["findings"]) / len(analysis["findings"])
        
        return analysis


class SecurityAnalystExpert(ExpertAgent):
    """Expert in security threats and social engineering tactics."""
    
    def get_role_description(self) -> str:
        return (
            "You are a cybersecurity and social engineering expert. "
            "You identify phishing attempts, credential harvesting, "
            "and various social engineering tactics used by attackers."
        )
    
    def analyze(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for security threats and social engineering."""
        analysis = {
            "expert": "security_analyst",
            "confidence": 0.0,
            "findings": []
        }
        
        message_lower = message.lower()
        
        # Check for credential requests
        cred_requests = [
            "password", "pin", "otp", "cvv", "security code",
            "account number", "card number", "expiry"
        ]
        if any(req in message_lower for req in cred_requests):
            analysis["findings"].append({
                "type": "credential_harvesting",
                "severity": 1.0,
                "description": "Direct request for sensitive credentials"
            })
        
        # Check for authority impersonation
        authority = ["bank", "police", "government", "tax", "irs", "officer"]
        if any(auth in message_lower for auth in authority):
            analysis["findings"].append({
                "type": "authority_impersonation",
                "severity": 0.8,
                "description": "Claims to represent authority figure or organization"
            })
        
        # Check for phishing indicators
        phishing_indicators = [
            "verify your account", "confirm your identity",
            "update your information", "suspicious activity",
            "account will be closed", "limited time"
        ]
        if any(indicator in message_lower for indicator in phishing_indicators):
            analysis["findings"].append({
                "type": "phishing_attempt",
                "severity": 0.9,
                "description": "Classic phishing language detected"
            })
        
        # Calculate confidence
        if analysis["findings"]:
            analysis["confidence"] = min(sum(f["severity"] for f in analysis["findings"]) / len(analysis["findings"]) * 1.2, 1.0)
        
        return analysis


class ExpertPanel:
    """Orchestrates multiple expert agents for comprehensive analysis."""
    
    def __init__(self):
        """Initialize expert panel with all experts."""
        self.experts = [
            TextAnalystExpert(),
            BusinessProcessExpert(),
            SecurityAnalystExpert()
        ]
    
    def consult_all_experts(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Consult all experts and aggregate their findings.
        
        Args:
            message: Message to analyze
            context: Additional context
        
        Returns:
            Aggregated analysis from all experts
        """
        context = context or {}
        expert_analyses = []
        
        # Get analysis from each expert
        for expert in self.experts:
            analysis = expert.analyze(message, context)
            expert_analyses.append(analysis)
        
        # Aggregate results
        all_findings = []
        total_confidence = 0.0
        
        for analysis in expert_analyses:
            all_findings.extend(analysis["findings"])
            total_confidence += analysis["confidence"]
        
        # Calculate weighted consensus
        consensus_confidence = total_confidence / len(self.experts) if self.experts else 0.0
        
        # Determine overall risk level
        if consensus_confidence >= 0.8:
            risk_level = "critical"
        elif consensus_confidence >= 0.6:
            risk_level = "high"
        elif consensus_confidence >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "expert_analyses": expert_analyses,
            "all_findings": all_findings,
            "consensus_confidence": consensus_confidence,
            "risk_level": risk_level,
            "is_likely_scam": consensus_confidence >= 0.5,
            "recommendation": self._generate_recommendation(risk_level, all_findings)
        }
    
    def _generate_recommendation(
        self,
        risk_level: str,
        findings: List[Dict]
    ) -> str:
        """Generate action recommendation based on analysis."""
        if risk_level == "critical":
            return (
                "High confidence scam detected. Engage with maximum caution. "
                "Focus on intelligence extraction while maintaining persona."
            )
        elif risk_level == "high":
            return (
                "Likely scam attempt. Continue engagement to extract intelligence. "
                "Be prepared for escalation tactics."
            )
        elif risk_level == "medium":
            return (
                "Possible scam indicators present. Monitor conversation closely. "
                "Gather more information before classification."
            )
        else:
            return (
                "Low risk detected. May be legitimate contact or early-stage scam. "
                "Continue standard engagement protocols."
            )
