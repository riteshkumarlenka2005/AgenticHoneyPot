"""Human-in-the-loop approval queue for sensitive responses."""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4


class ApprovalStatus(str, Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Represents a response awaiting human approval."""
    id: str = field(default_factory=lambda: str(uuid4()))
    conversation_id: str = ""
    response_text: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"  # low, medium, high, critical
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    modified_response: Optional[str] = None


class ApprovalQueue:
    """
    Manages human-in-the-loop approval for honeypot responses.
    
    Responses that require approval:
    - High-risk responses (potential PII leakage)
    - Responses in critical scam stages
    - Responses with low confidence scores
    - Randomly sampled responses for quality control
    """
    
    def __init__(
        self,
        approval_threshold: float = 0.7,
        sample_rate: float = 0.1
    ):
        """
        Initialize approval queue.
        
        Args:
            approval_threshold: Confidence below which approval is required
            sample_rate: Random sampling rate for quality control (0-1)
        """
        self.approval_threshold = approval_threshold
        self.sample_rate = sample_rate
        self.queue: Dict[str, ApprovalRequest] = {}
        self.history: List[ApprovalRequest] = []
    
    def submit_for_approval(
        self,
        conversation_id: str,
        response_text: str,
        context: Dict[str, Any],
        risk_level: str = "low"
    ) -> ApprovalRequest:
        """
        Submit a response for human approval.
        
        Args:
            conversation_id: ID of the conversation
            response_text: The response text to approve
            context: Additional context (confidence, stage, etc.)
            risk_level: Risk level of the response
        
        Returns:
            ApprovalRequest object
        """
        request = ApprovalRequest(
            conversation_id=conversation_id,
            response_text=response_text,
            context=context,
            risk_level=risk_level
        )
        
        self.queue[request.id] = request
        return request
    
    def requires_approval(
        self,
        confidence: float,
        risk_score: float,
        stage: str
    ) -> bool:
        """
        Determine if a response requires human approval.
        
        Args:
            confidence: Confidence score (0-1)
            risk_score: Risk score (0-1)
            stage: Conversation stage
        
        Returns:
            True if approval required
        """
        # Always require approval for high-risk responses
        if risk_score > 0.7:
            return True
        
        # Require approval for low-confidence responses
        if confidence < self.approval_threshold:
            return True
        
        # Require approval for critical stages
        critical_stages = ["payment_request", "final_push"]
        if stage in critical_stages:
            return True
        
        # Random sampling for quality control
        import random
        if random.random() < self.sample_rate:
            return True
        
        return False
    
    def get_pending_requests(
        self,
        priority_filter: Optional[str] = None
    ) -> List[ApprovalRequest]:
        """
        Get pending approval requests.
        
        Args:
            priority_filter: Filter by risk level
        
        Returns:
            List of pending requests
        """
        pending = [
            req for req in self.queue.values()
            if req.status == ApprovalStatus.PENDING
        ]
        
        if priority_filter:
            pending = [req for req in pending if req.risk_level == priority_filter]
        
        # Sort by risk level and age
        risk_priority = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        pending.sort(
            key=lambda x: (risk_priority.get(x.risk_level, 0), x.created_at),
            reverse=True
        )
        
        return pending
    
    def approve_request(
        self,
        request_id: str,
        reviewer_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Approve a request.
        
        Args:
            request_id: ID of the request
            reviewer_id: ID of the reviewer
            notes: Optional notes
        
        Returns:
            True if successful
        """
        request = self.queue.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        request.status = ApprovalStatus.APPROVED
        request.reviewer_id = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes
        
        # Move to history
        self.history.append(request)
        del self.queue[request_id]
        
        return True
    
    def reject_request(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str
    ) -> bool:
        """
        Reject a request.
        
        Args:
            request_id: ID of the request
            reviewer_id: ID of the reviewer
            notes: Rejection reason
        
        Returns:
            True if successful
        """
        request = self.queue.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        request.status = ApprovalStatus.REJECTED
        request.reviewer_id = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes
        
        # Move to history
        self.history.append(request)
        del self.queue[request_id]
        
        return True
    
    def modify_and_approve(
        self,
        request_id: str,
        reviewer_id: str,
        modified_response: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Modify and approve a request.
        
        Args:
            request_id: ID of the request
            reviewer_id: ID of the reviewer
            modified_response: Modified response text
            notes: Optional notes
        
        Returns:
            True if successful
        """
        request = self.queue.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        request.status = ApprovalStatus.MODIFIED
        request.reviewer_id = reviewer_id
        request.reviewed_at = datetime.utcnow()
        request.modified_response = modified_response
        request.reviewer_notes = notes
        
        # Move to history
        self.history.append(request)
        del self.queue[request_id]
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get approval queue statistics."""
        total_pending = len(self.queue)
        total_reviewed = len(self.history)
        
        if total_reviewed > 0:
            approved = len([r for r in self.history if r.status == ApprovalStatus.APPROVED])
            rejected = len([r for r in self.history if r.status == ApprovalStatus.REJECTED])
            modified = len([r for r in self.history if r.status == ApprovalStatus.MODIFIED])
            
            approval_rate = approved / total_reviewed
            modification_rate = modified / total_reviewed
        else:
            approved = rejected = modified = 0
            approval_rate = modification_rate = 0.0
        
        return {
            "pending": total_pending,
            "total_reviewed": total_reviewed,
            "approved": approved,
            "rejected": rejected,
            "modified": modified,
            "approval_rate": approval_rate,
            "modification_rate": modification_rate
        }
