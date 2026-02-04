"""Multi-Agent Orchestration System."""
from typing import Dict, List, Any, Optional
from enum import Enum
import json


class AgentRole(str, Enum):
    """Agent roles in the multi-agent system."""
    SUPERVISOR = "supervisor"
    TEXT_ANALYST = "text_analyst"
    BUSINESS_PROCESS = "business_process"
    SECURITY_ANALYST = "security_analyst"
    RESPONSE_GENERATOR = "response_generator"


class Agent:
    """Base agent class."""

    def __init__(self, role: AgentRole, name: str):
        """Initialize agent."""
        self.role = role
        self.name = name

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output."""
        raise NotImplementedError


class TextAnalystAgent(Agent):
    """Analyzes text for sentiment, intent, and key information."""

    def __init__(self):
        """Initialize text analyst agent."""
        super().__init__(AgentRole.TEXT_ANALYST, "Text Analyst")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze message text.
        
        Args:
            input_data: Dict with 'message' key
            
        Returns:
            Analysis results
        """
        message = input_data.get("message", "")
        
        # Sentiment analysis (simple keyword-based)
        sentiment = self._analyze_sentiment(message)
        
        # Intent detection
        intent = self._detect_intent(message)
        
        # Key phrases extraction
        key_phrases = self._extract_key_phrases(message)
        
        return {
            "agent": self.name,
            "sentiment": sentiment,
            "intent": intent,
            "key_phrases": key_phrases,
            "message_length": len(message),
            "word_count": len(message.split())
        }

    def _analyze_sentiment(self, message: str) -> str:
        """Analyze sentiment of message."""
        message_lower = message.lower()
        
        positive_words = ["great", "good", "excellent", "happy", "thank", "yes"]
        negative_words = ["no", "bad", "terrible", "sad", "angry", "problem"]
        urgent_words = ["urgent", "immediately", "now", "asap", "hurry"]
        
        pos_count = sum(1 for word in positive_words if word in message_lower)
        neg_count = sum(1 for word in negative_words if word in message_lower)
        urgent_count = sum(1 for word in urgent_words if word in message_lower)
        
        if urgent_count > 0:
            return "urgent"
        elif pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def _detect_intent(self, message: str) -> str:
        """Detect intent of message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["?", "how", "what", "when", "where", "who"]):
            return "question"
        elif any(word in message_lower for word in ["pay", "send", "transfer", "money"]):
            return "payment_request"
        elif any(word in message_lower for word in ["details", "information", "confirm", "verify"]):
            return "information_request"
        elif any(word in message_lower for word in ["hello", "hi", "greetings"]):
            return "greeting"
        else:
            return "statement"

    def _extract_key_phrases(self, message: str) -> List[str]:
        """Extract key phrases from message."""
        # Simple approach: look for common scam-related phrases
        phrases = []
        message_lower = message.lower()
        
        scam_phrases = [
            "bank account", "upi id", "payment", "urgent", "verify",
            "confirm", "winner", "lottery", "prize", "offer",
            "limited time", "act now", "click here"
        ]
        
        for phrase in scam_phrases:
            if phrase in message_lower:
                phrases.append(phrase)
        
        return phrases[:5]  # Return top 5


class BusinessProcessAgent(Agent):
    """Analyzes business process and workflow patterns."""

    def __init__(self):
        """Initialize business process agent."""
        super().__init__(AgentRole.BUSINESS_PROCESS, "Business Process Analyst")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze business process patterns.
        
        Args:
            input_data: Dict with message history
            
        Returns:
            Process analysis
        """
        messages = input_data.get("messages", [])
        
        # Analyze conversation flow
        flow_pattern = self._analyze_flow(messages)
        
        # Detect typical scam patterns
        scam_indicators = self._detect_scam_patterns(messages)
        
        return {
            "agent": self.name,
            "flow_pattern": flow_pattern,
            "scam_indicators": scam_indicators,
            "message_count": len(messages)
        }

    def _analyze_flow(self, messages: List[Dict]) -> str:
        """Analyze conversation flow pattern."""
        if len(messages) < 2:
            return "initial"
        elif len(messages) < 5:
            return "engagement"
        elif len(messages) < 10:
            return "development"
        else:
            return "advanced"

    def _detect_scam_patterns(self, messages: List[Dict]) -> List[str]:
        """Detect scam patterns in conversation."""
        patterns = []
        
        # Check for rapid escalation
        if len(messages) > 3:
            recent_messages = [m.get("content", "").lower() for m in messages[-3:]]
            if any("urgent" in m or "immediately" in m for m in recent_messages):
                patterns.append("urgency_escalation")
        
        # Check for information gathering
        info_keywords = ["name", "address", "account", "number", "details"]
        if any(
            any(keyword in m.get("content", "").lower() for keyword in info_keywords)
            for m in messages
        ):
            patterns.append("information_harvesting")
        
        # Check for payment requests
        payment_keywords = ["pay", "money", "transfer", "send"]
        if any(
            any(keyword in m.get("content", "").lower() for keyword in payment_keywords)
            for m in messages
        ):
            patterns.append("payment_solicitation")
        
        return patterns


class SecurityAnalystAgent(Agent):
    """Analyzes security threats and risks."""

    def __init__(self):
        """Initialize security analyst agent."""
        super().__init__(AgentRole.SECURITY_ANALYST, "Security Analyst")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security threats.
        
        Args:
            input_data: Dict with message and context
            
        Returns:
            Security analysis
        """
        message = input_data.get("message", "")
        intelligence = input_data.get("intelligence", [])
        
        # Threat assessment
        threat_level = self._assess_threat(message, intelligence)
        
        # Risk factors
        risk_factors = self._identify_risks(message)
        
        return {
            "agent": self.name,
            "threat_level": threat_level,
            "risk_factors": risk_factors,
            "intelligence_count": len(intelligence)
        }

    def _assess_threat(self, message: str, intelligence: List) -> str:
        """Assess threat level."""
        message_lower = message.lower()
        
        critical_keywords = ["account", "password", "otp", "pin", "cvv"]
        high_keywords = ["bank", "payment", "upi", "money"]
        medium_keywords = ["details", "verify", "confirm"]
        
        if any(keyword in message_lower for keyword in critical_keywords):
            return "critical"
        elif any(keyword in message_lower for keyword in high_keywords):
            return "high"
        elif any(keyword in message_lower for keyword in medium_keywords):
            return "medium"
        elif len(intelligence) > 0:
            return "medium"
        else:
            return "low"

    def _identify_risks(self, message: str) -> List[str]:
        """Identify specific risk factors."""
        risks = []
        message_lower = message.lower()
        
        if "click" in message_lower or "link" in message_lower:
            risks.append("phishing_link")
        if "download" in message_lower or "install" in message_lower:
            risks.append("malware_risk")
        if "password" in message_lower or "otp" in message_lower:
            risks.append("credential_theft")
        if "bank" in message_lower or "account" in message_lower:
            risks.append("financial_fraud")
        
        return risks


class ResponseGeneratorAgent(Agent):
    """Generates contextual responses."""

    def __init__(self):
        """Initialize response generator agent."""
        super().__init__(AgentRole.RESPONSE_GENERATOR, "Response Generator")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response recommendations.
        
        Args:
            input_data: Dict with analysis results
            
        Returns:
            Response recommendations
        """
        text_analysis = input_data.get("text_analysis", {})
        security_analysis = input_data.get("security_analysis", {})
        
        # Generate response strategy
        strategy = self._determine_strategy(text_analysis, security_analysis)
        
        # Generate response tone
        tone = self._determine_tone(text_analysis)
        
        return {
            "agent": self.name,
            "strategy": strategy,
            "tone": tone,
            "recommendations": self._generate_recommendations(strategy, security_analysis)
        }

    def _determine_strategy(self, text_analysis: Dict, security_analysis: Dict) -> str:
        """Determine response strategy."""
        intent = text_analysis.get("intent", "")
        threat_level = security_analysis.get("threat_level", "low")
        
        if threat_level in ["critical", "high"]:
            return "extract_intelligence"
        elif intent == "payment_request":
            return "stall_and_gather"
        elif intent == "information_request":
            return "deflect_and_misdirect"
        elif intent == "question":
            return "engage_and_build_trust"
        else:
            return "maintain_engagement"

    def _determine_tone(self, text_analysis: Dict) -> str:
        """Determine appropriate response tone."""
        sentiment = text_analysis.get("sentiment", "neutral")
        
        if sentiment == "urgent":
            return "concerned_but_cautious"
        elif sentiment == "positive":
            return "friendly_cooperative"
        elif sentiment == "negative":
            return "apologetic_compliant"
        else:
            return "neutral_curious"

    def _generate_recommendations(self, strategy: str, security_analysis: Dict) -> List[str]:
        """Generate specific recommendations."""
        recommendations = []
        
        if strategy == "extract_intelligence":
            recommendations.append("Ask for verification details")
            recommendations.append("Request alternative contact methods")
        elif strategy == "stall_and_gather":
            recommendations.append("Express technical difficulties")
            recommendations.append("Request more time to verify")
        elif strategy == "deflect_and_misdirect":
            recommendations.append("Provide partial information")
            recommendations.append("Ask clarifying questions")
        
        return recommendations


class SupervisorAgent(Agent):
    """Coordinates and supervises other agents."""

    def __init__(self):
        """Initialize supervisor agent."""
        super().__init__(AgentRole.SUPERVISOR, "Supervisor")
        
        # Initialize sub-agents
        self.text_analyst = TextAnalystAgent()
        self.business_process = BusinessProcessAgent()
        self.security_analyst = SecurityAnalystAgent()
        self.response_generator = ResponseGeneratorAgent()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate all agents and synthesize results.
        
        Args:
            input_data: Dict with message, messages, and intelligence
            
        Returns:
            Synthesized analysis and recommendations
        """
        # Run all agents in parallel (in real implementation)
        text_analysis = await self.text_analyst.process(input_data)
        process_analysis = await self.business_process.process(input_data)
        security_analysis = await self.security_analyst.process(input_data)
        
        # Generate response based on all analyses
        response_input = {
            "text_analysis": text_analysis,
            "process_analysis": process_analysis,
            "security_analysis": security_analysis
        }
        response_analysis = await self.response_generator.process(response_input)
        
        # Synthesize overall assessment
        overall_assessment = self._synthesize_assessment(
            text_analysis, process_analysis, security_analysis
        )
        
        return {
            "agent": self.name,
            "text_analysis": text_analysis,
            "process_analysis": process_analysis,
            "security_analysis": security_analysis,
            "response_analysis": response_analysis,
            "overall_assessment": overall_assessment
        }

    def _synthesize_assessment(
        self, text: Dict, process: Dict, security: Dict
    ) -> Dict[str, Any]:
        """Synthesize overall assessment from all agents."""
        return {
            "confidence": self._calculate_confidence(text, security),
            "priority": self._calculate_priority(security, process),
            "recommended_action": self._recommend_action(text, process, security)
        }

    def _calculate_confidence(self, text: Dict, security: Dict) -> float:
        """Calculate confidence score."""
        # Simple confidence based on available data
        base_confidence = 0.5
        
        if text.get("key_phrases"):
            base_confidence += 0.2
        
        threat_level = security.get("threat_level", "low")
        if threat_level in ["high", "critical"]:
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)

    def _calculate_priority(self, security: Dict, process: Dict) -> str:
        """Calculate priority level."""
        threat_level = security.get("threat_level", "low")
        scam_indicators = process.get("scam_indicators", [])
        
        if threat_level == "critical" or len(scam_indicators) > 2:
            return "high"
        elif threat_level == "high" or len(scam_indicators) > 0:
            return "medium"
        else:
            return "low"

    def _recommend_action(self, text: Dict, process: Dict, security: Dict) -> str:
        """Recommend action based on all analyses."""
        threat_level = security.get("threat_level", "low")
        intent = text.get("intent", "")
        
        if threat_level in ["critical", "high"]:
            return "extract_and_document"
        elif intent == "payment_request":
            return "stall_for_intelligence"
        elif len(process.get("scam_indicators", [])) > 0:
            return "engage_and_analyze"
        else:
            return "continue_monitoring"


class MultiAgentOrchestrator:
    """Orchestrates multi-agent analysis system."""

    def __init__(self):
        """Initialize orchestrator."""
        self.supervisor = SupervisorAgent()

    async def analyze_message(
        self,
        message: str,
        messages: List[Dict[str, Any]],
        intelligence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze message using multi-agent system.
        
        Args:
            message: Current message to analyze
            messages: Message history
            intelligence: Extracted intelligence
            
        Returns:
            Comprehensive analysis results
        """
        input_data = {
            "message": message,
            "messages": messages,
            "intelligence": intelligence
        }
        
        return await self.supervisor.process(input_data)
