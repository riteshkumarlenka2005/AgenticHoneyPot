"""Human-in-the-Loop Approval Queue."""
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from collections import deque


class ApprovalStatus(str, Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRequest:
    """Approval request for human review."""

    def __init__(
        self,
        request_type: str,
        data: Dict[str, Any],
        priority: str = "medium",
        expires_in_seconds: int = 3600,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize approval request.
        
        Args:
            request_type: Type of approval (response, action, intelligence)
            data: Data requiring approval
            priority: Priority level (low, medium, high, critical)
            expires_in_seconds: Time until request expires
            metadata: Optional metadata
        """
        self.id = uuid4()
        self.request_type = request_type
        self.data = data
        self.priority = priority
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=expires_in_seconds)
        self.reviewed_at: Optional[datetime] = None
        self.reviewer: Optional[str] = None
        self.decision_notes: Optional[str] = None
        self.metadata = metadata or {}

    def is_expired(self) -> bool:
        """Check if request has expired."""
        return datetime.utcnow() > self.expires_at and self.status == ApprovalStatus.PENDING

    def approve(self, reviewer: str, notes: Optional[str] = None) -> None:
        """
        Approve the request.
        
        Args:
            reviewer: Identifier of reviewer
            notes: Optional approval notes
        """
        self.status = ApprovalStatus.APPROVED
        self.reviewed_at = datetime.utcnow()
        self.reviewer = reviewer
        self.decision_notes = notes

    def reject(self, reviewer: str, notes: Optional[str] = None) -> None:
        """
        Reject the request.
        
        Args:
            reviewer: Identifier of reviewer
            notes: Optional rejection notes
        """
        self.status = ApprovalStatus.REJECTED
        self.reviewed_at = datetime.utcnow()
        self.reviewer = reviewer
        self.decision_notes = notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "request_type": self.request_type,
            "data": self.data,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewer": self.reviewer,
            "decision_notes": self.decision_notes,
            "metadata": self.metadata,
            "is_expired": self.is_expired()
        }


class ApprovalQueue:
    """
    Human-in-the-Loop approval queue and review interface.
    
    Manages approval requests for sensitive actions that require
    human oversight before execution.
    """

    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize approval queue.
        
        Args:
            max_queue_size: Maximum number of requests to keep
        """
        self.max_queue_size = max_queue_size
        self.requests: Dict[UUID, ApprovalRequest] = {}
        self.pending_queue: deque = deque(maxlen=max_queue_size)
        
        # Approval thresholds
        self.auto_approve_thresholds = {
            "response": 0.9,  # High confidence responses
            "intelligence": 0.8,  # High confidence intelligence
            "action": None,  # Never auto-approve actions
        }

    def create_request(
        self,
        request_type: str,
        data: Dict[str, Any],
        priority: str = "medium",
        expires_in_seconds: int = 3600,
        metadata: Optional[Dict[str, Any]] = None,
        auto_approve_confidence: Optional[float] = None
    ) -> ApprovalRequest:
        """
        Create new approval request.
        
        Args:
            request_type: Type of approval needed
            data: Data requiring approval
            priority: Priority level
            expires_in_seconds: Expiration time
            metadata: Optional metadata
            auto_approve_confidence: Confidence for auto-approval
            
        Returns:
            Created approval request
        """
        request = ApprovalRequest(
            request_type=request_type,
            data=data,
            priority=priority,
            expires_in_seconds=expires_in_seconds,
            metadata=metadata
        )
        
        # Check for auto-approval
        if auto_approve_confidence is not None:
            threshold = self.auto_approve_thresholds.get(request_type)
            if threshold and auto_approve_confidence >= threshold:
                request.approve("system-auto", "Auto-approved based on confidence threshold")
        
        # Add to queue if still pending
        if request.status == ApprovalStatus.PENDING:
            self.pending_queue.append(request.id)
        
        self.requests[request.id] = request
        return request

    def get_request(self, request_id: UUID) -> Optional[ApprovalRequest]:
        """Get approval request by ID."""
        return self.requests.get(request_id)

    def get_pending_requests(
        self,
        request_type: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50
    ) -> List[ApprovalRequest]:
        """
        Get pending approval requests.
        
        Args:
            request_type: Filter by request type
            priority: Filter by priority
            limit: Maximum number of requests
            
        Returns:
            List of pending requests
        """
        # Mark expired requests
        self._mark_expired()
        
        requests = []
        for request_id in self.pending_queue:
            request = self.requests.get(request_id)
            if not request or request.status != ApprovalStatus.PENDING:
                continue
            
            # Apply filters
            if request_type and request.request_type != request_type:
                continue
            if priority and request.priority != priority:
                continue
            
            requests.append(request)
            
            if len(requests) >= limit:
                break
        
        # Sort by priority and creation time
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        requests.sort(key=lambda r: (priority_order.get(r.priority, 99), r.created_at))
        
        return requests

    def approve_request(
        self,
        request_id: UUID,
        reviewer: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Approve a request.
        
        Args:
            request_id: Request ID
            reviewer: Reviewer identifier
            notes: Optional notes
            
        Returns:
            True if approved successfully
        """
        request = self.get_request(request_id)
        if not request:
            return False
        
        if request.status != ApprovalStatus.PENDING:
            return False
        
        if request.is_expired():
            request.status = ApprovalStatus.EXPIRED
            return False
        
        request.approve(reviewer, notes)
        return True

    def reject_request(
        self,
        request_id: UUID,
        reviewer: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Reject a request.
        
        Args:
            request_id: Request ID
            reviewer: Reviewer identifier
            notes: Optional notes
            
        Returns:
            True if rejected successfully
        """
        request = self.get_request(request_id)
        if not request:
            return False
        
        if request.status != ApprovalStatus.PENDING:
            return False
        
        request.reject(reviewer, notes)
        return True

    def _mark_expired(self) -> None:
        """Mark expired pending requests."""
        for request in self.requests.values():
            if request.is_expired():
                request.status = ApprovalStatus.EXPIRED

    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        self._mark_expired()
        
        total = len(self.requests)
        pending = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.PENDING)
        approved = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.REJECTED)
        expired = sum(1 for r in self.requests.values() if r.status == ApprovalStatus.EXPIRED)
        
        # Average review time for completed requests
        review_times = [
            (r.reviewed_at - r.created_at).total_seconds()
            for r in self.requests.values()
            if r.reviewed_at
        ]
        avg_review_time = sum(review_times) / len(review_times) if review_times else 0
        
        # By type
        by_type: Dict[str, int] = {}
        for request in self.requests.values():
            by_type[request.request_type] = by_type.get(request.request_type, 0) + 1
        
        return {
            "total_requests": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "expired": expired,
            "approval_rate": (approved / (approved + rejected)) if (approved + rejected) > 0 else 0,
            "average_review_time_seconds": round(avg_review_time, 2),
            "by_type": by_type,
            "queue_size": len(self.pending_queue)
        }

    def cleanup_old_requests(self, days: int = 7) -> int:
        """
        Remove old completed/expired requests.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of requests removed
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        to_remove = []
        
        for request_id, request in self.requests.items():
            if request.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED]:
                if request.created_at < cutoff:
                    to_remove.append(request_id)
        
        for request_id in to_remove:
            del self.requests[request_id]
        
        return len(to_remove)


# Global approval queue instance
approval_queue = ApprovalQueue()
