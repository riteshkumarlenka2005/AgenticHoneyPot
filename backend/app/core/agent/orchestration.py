"""Multi-agent orchestration for coordinated intelligence gathering."""
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class AgentRole(str, Enum):
    """Roles for specialized agents."""
    SUPERVISOR = "supervisor"
    EXTRACTION = "extraction"
    VERIFICATION = "verification"
    ENGAGEMENT = "engagement"
    SAFETY = "safety"


@dataclass
class AgentTask:
    """Represents a task for an agent."""
    task_id: str
    role: AgentRole
    description: str
    priority: int  # Higher = more important
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None


class SupervisorAgent:
    """
    Supervisor agent that coordinates other specialized agents.
    
    This agent:
    1. Analyzes incoming messages
    2. Delegates tasks to specialist agents
    3. Synthesizes results
    4. Makes final decisions
    """
    
    def __init__(self):
        """Initialize supervisor agent."""
        self.active_tasks: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
    
    def analyze_message(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> List[AgentTask]:
        """
        Analyze message and create tasks for specialist agents.
        
        Args:
            message: Incoming message
            context: Conversation context
        
        Returns:
            List of tasks for specialist agents
        """
        tasks = []
        task_id_counter = len(self.active_tasks) + len(self.completed_tasks)
        
        # Always extract information
        tasks.append(AgentTask(
            task_id=f"task_{task_id_counter}",
            role=AgentRole.EXTRACTION,
            description=f"Extract intelligence from message: {message[:50]}...",
            priority=10
        ))
        task_id_counter += 1
        
        # If we've extracted something, verify it
        if context.get("has_extracted_info"):
            tasks.append(AgentTask(
                task_id=f"task_{task_id_counter}",
                role=AgentRole.VERIFICATION,
                description="Verify extracted intelligence",
                priority=8
            ))
            task_id_counter += 1
        
        # Generate engaging response
        tasks.append(AgentTask(
            task_id=f"task_{task_id_counter}",
            role=AgentRole.ENGAGEMENT,
            description="Generate engaging response to maintain conversation",
            priority=9
        ))
        task_id_counter += 1
        
        # Safety check
        tasks.append(AgentTask(
            task_id=f"task_{task_id_counter}",
            role=AgentRole.SAFETY,
            description="Verify response safety and compliance",
            priority=11  # Highest priority
        ))
        
        self.active_tasks.extend(tasks)
        return tasks
    
    def execute_tasks(
        self,
        tasks: List[AgentTask],
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tasks using appropriate agents.
        
        Args:
            tasks: List of tasks to execute
            message: The message being processed
            context: Conversation context
        
        Returns:
            Aggregated results from all agents
        """
        results = {
            "extraction": None,
            "verification": None,
            "engagement": None,
            "safety": None
        }
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        
        for task in sorted_tasks:
            task.status = "in_progress"
            
            if task.role == AgentRole.EXTRACTION:
                agent = ExtractionAgent()
                task.result = agent.execute(message, context)
                results["extraction"] = task.result
            
            elif task.role == AgentRole.VERIFICATION:
                agent = VerificationAgent()
                task.result = agent.execute(
                    results.get("extraction", {}),
                    context
                )
                results["verification"] = task.result
            
            elif task.role == AgentRole.ENGAGEMENT:
                agent = EngagementAgent()
                task.result = agent.execute(message, context, results)
                results["engagement"] = task.result
            
            elif task.role == AgentRole.SAFETY:
                agent = SafetyAgent()
                task.result = agent.execute(results.get("engagement", {}))
                results["safety"] = task.result
            
            task.status = "completed"
            self.active_tasks.remove(task)
            self.completed_tasks.append(task)
        
        return results
    
    def synthesize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize results from all agents into final decision.
        
        Args:
            results: Results from all specialist agents
        
        Returns:
            Final synthesized decision
        """
        # Check safety first
        if not results.get("safety", {}).get("is_safe", False):
            return {
                "approved": False,
                "response": "I need to think about this.",
                "reason": "Safety check failed",
                "intelligence_extracted": []
            }
        
        # Combine extraction and verification
        intelligence = []
        if results.get("extraction"):
            extracted = results["extraction"].get("artifacts", [])
            verified = results.get("verification", {}).get("verified_artifacts", [])
            
            # Only include verified intelligence
            intelligence = verified if verified else extracted
        
        # Get engagement response
        response = results.get("engagement", {}).get("response", "")
        
        return {
            "approved": True,
            "response": response,
            "intelligence_extracted": intelligence,
            "extraction_confidence": results.get("extraction", {}).get("confidence", 0.0),
            "engagement_quality": results.get("engagement", {}).get("quality_score", 0.0)
        }


class ExtractionAgent:
    """Specialized agent for extracting intelligence."""
    
    def execute(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract intelligence from message."""
        import re
        
        artifacts = []
        
        # Extract phone numbers
        phones = re.findall(r'\b\d{10,12}\b', message)
        for phone in phones:
            artifacts.append({
                "type": "PHONE",
                "value": phone,
                "confidence": 0.9
            })
        
        # Extract UPI IDs
        upis = re.findall(r'\b[\w\.-]+@[\w]+\b', message)
        for upi in upis:
            if '@' in upi and '.' not in upi.split('@')[1]:
                artifacts.append({
                    "type": "UPI_ID",
                    "value": upi,
                    "confidence": 0.85
                })
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', message)
        for url in urls:
            artifacts.append({
                "type": "URL",
                "value": url,
                "confidence": 0.95
            })
        
        return {
            "artifacts": artifacts,
            "confidence": 0.8 if artifacts else 0.0,
            "count": len(artifacts)
        }


class VerificationAgent:
    """Specialized agent for verifying extracted intelligence."""
    
    def execute(
        self,
        extraction_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify extracted artifacts."""
        artifacts = extraction_results.get("artifacts", [])
        verified = []
        
        for artifact in artifacts:
            # Basic verification logic
            if self._verify_artifact(artifact):
                verified.append(artifact)
        
        return {
            "verified_artifacts": verified,
            "verification_rate": len(verified) / len(artifacts) if artifacts else 0.0
        }
    
    def _verify_artifact(self, artifact: Dict[str, Any]) -> bool:
        """Verify a single artifact."""
        # Simple verification - could be enhanced with external APIs
        value = artifact.get("value", "")
        artifact_type = artifact.get("type", "")
        
        if artifact_type == "PHONE":
            return len(value) >= 10
        elif artifact_type == "UPI_ID":
            return '@' in value
        elif artifact_type == "URL":
            return value.startswith(('http://', 'https://'))
        
        return True


class EngagementAgent:
    """Specialized agent for generating engaging responses."""
    
    def execute(
        self,
        message: str,
        context: Dict[str, Any],
        other_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate engaging response."""
        # Simple engagement logic - in production, use LLM
        
        stage = context.get("stage", "initial_contact")
        
        if stage == "payment_request":
            response = "I want to help, but I'm not sure how to proceed. Can you explain the process step by step?"
        elif stage == "building_trust":
            response = "That sounds reasonable. Tell me more about this."
        else:
            response = "I see. What do you need from me?"
        
        return {
            "response": response,
            "quality_score": 0.7,
            "engagement_tactics": ["questioning", "cooperation"]
        }


class SafetyAgent:
    """Specialized agent for safety verification."""
    
    def execute(self, engagement_results: Dict[str, Any]) -> Dict[str, Any]:
        """Verify response safety."""
        response = engagement_results.get("response", "")
        
        # Check for PII leakage
        has_pii = any(word in response.lower() for word in [
            "my real", "actual", "genuine password", "real account"
        ])
        
        # Check for persona breaks
        breaks_persona = any(word in response.lower() for word in [
            "i am an ai", "honeypot", "scam detection"
        ])
        
        is_safe = not (has_pii or breaks_persona)
        
        return {
            "is_safe": is_safe,
            "pii_risk": 0.9 if has_pii else 0.1,
            "persona_maintained": not breaks_persona
        }
