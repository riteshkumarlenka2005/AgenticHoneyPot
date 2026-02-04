"""Human review interface for HITL system."""
from typing import Dict, List, Optional, Any
from datetime import datetime


class ReviewInterface:
    """
    Interface for human reviewers to interact with the HITL system.
    
    Provides methods for:
    - Viewing pending reviews
    - Approving/rejecting responses
    - Providing feedback
    - Tracking review performance
    """
    
    def __init__(self, approval_queue):
        """
        Initialize review interface.
        
        Args:
            approval_queue: ApprovalQueue instance
        """
        self.queue = approval_queue
        self.reviewer_stats: Dict[str, Dict[str, Any]] = {}
    
    def get_next_review(
        self,
        reviewer_id: str,
        priority: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get next item for review.
        
        Args:
            reviewer_id: ID of the reviewer
            priority: Optional priority filter
        
        Returns:
            Review item dict or None
        """
        pending = self.queue.get_pending_requests(priority_filter=priority)
        
        if not pending:
            return None
        
        # Get the highest priority item
        request = pending[0]
        
        return {
            "id": request.id,
            "conversation_id": request.conversation_id,
            "response_text": request.response_text,
            "risk_level": request.risk_level,
            "context": request.context,
            "created_at": request.created_at.isoformat()
        }
    
    def submit_review(
        self,
        request_id: str,
        reviewer_id: str,
        decision: str,
        modified_text: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit a review decision.
        
        Args:
            request_id: ID of the request
            reviewer_id: ID of the reviewer
            decision: "approve", "reject", or "modify"
            modified_text: Modified response if decision is "modify"
            notes: Reviewer notes
        
        Returns:
            Result dict
        """
        success = False
        
        if decision == "approve":
            success = self.queue.approve_request(request_id, reviewer_id, notes)
        elif decision == "reject":
            success = self.queue.reject_request(request_id, reviewer_id, notes or "Rejected")
        elif decision == "modify" and modified_text:
            success = self.queue.modify_and_approve(
                request_id,
                reviewer_id,
                modified_text,
                notes
            )
        
        if success:
            self._update_reviewer_stats(reviewer_id, decision)
        
        return {
            "success": success,
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_review_queue_summary(self) -> Dict[str, Any]:
        """Get summary of review queue."""
        pending = self.queue.get_pending_requests()
        
        by_risk = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for request in pending:
            by_risk[request.risk_level] += 1
        
        return {
            "total_pending": len(pending),
            "by_risk_level": by_risk,
            "oldest_pending": min(
                (r.created_at for r in pending),
                default=None
            )
        }
    
    def get_reviewer_performance(
        self,
        reviewer_id: str
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a reviewer.
        
        Args:
            reviewer_id: ID of the reviewer
        
        Returns:
            Performance metrics
        """
        if reviewer_id not in self.reviewer_stats:
            return {
                "total_reviews": 0,
                "approved": 0,
                "rejected": 0,
                "modified": 0
            }
        
        return self.reviewer_stats[reviewer_id].copy()
    
    def _update_reviewer_stats(self, reviewer_id: str, decision: str):
        """Update statistics for a reviewer."""
        if reviewer_id not in self.reviewer_stats:
            self.reviewer_stats[reviewer_id] = {
                "total_reviews": 0,
                "approved": 0,
                "rejected": 0,
                "modified": 0
            }
        
        stats = self.reviewer_stats[reviewer_id]
        stats["total_reviews"] += 1
        
        if decision == "approve":
            stats["approved"] += 1
        elif decision == "reject":
            stats["rejected"] += 1
        elif decision == "modify":
            stats["modified"] += 1
    
    def provide_feedback(
        self,
        reviewer_id: str,
        feedback_text: str,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Allow reviewers to provide general feedback.
        
        Args:
            reviewer_id: ID of the reviewer
            feedback_text: Feedback text
            category: Feedback category
        
        Returns:
            Confirmation dict
        """
        # In production, this would save to database
        return {
            "success": True,
            "reviewer_id": reviewer_id,
            "category": category,
            "timestamp": datetime.utcnow().isoformat()
        }
