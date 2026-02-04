"""Human Acceptance Rate (HAR) metric tracking."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class ReviewDecision(str, Enum):
    """Human review decisions."""
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    PENDING = "pending"


class HumanAcceptanceRate:
    """
    Track Human Acceptance Rate (HAR).
    
    HAR = (Approved Responses) / (Total Reviewed Responses)
    
    This metric measures how often human reviewers accept the honeypot's
    responses without modification.
    """
    
    def __init__(self):
        """Initialize HAR tracker."""
        self.reviews: List[Dict[str, Any]] = []
    
    def record_review(
        self,
        response_id: str,
        decision: ReviewDecision,
        response_text: str,
        modified_text: str = None,
        reviewer_notes: str = None,
        conversation_stage: str = None
    ):
        """
        Record a human review of a response.
        
        Args:
            response_id: Unique identifier for the response
            decision: Review decision
            response_text: Original response text
            modified_text: Modified text if decision was MODIFIED
            reviewer_notes: Optional notes from reviewer
            conversation_stage: Stage of conversation
        """
        self.reviews.append({
            "response_id": response_id,
            "decision": decision,
            "response_text": response_text,
            "modified_text": modified_text,
            "reviewer_notes": reviewer_notes,
            "conversation_stage": conversation_stage,
            "timestamp": datetime.utcnow()
        })
    
    def calculate_har(
        self,
        time_period_hours: int = None,
        stage_filter: str = None
    ) -> Dict[str, float]:
        """
        Calculate Human Acceptance Rate.
        
        Args:
            time_period_hours: Optional time window to consider
            stage_filter: Optional filter for conversation stage
        
        Returns:
            Dictionary with HAR metrics
        """
        # Filter data
        filtered_reviews = self._filter_data(time_period_hours, stage_filter)
        
        # Exclude pending reviews
        completed_reviews = [
            r for r in filtered_reviews
            if r["decision"] != ReviewDecision.PENDING
        ]
        
        if not completed_reviews:
            return {
                "har": 0.0,
                "total_reviews": 0,
                "approved": 0,
                "rejected": 0,
                "modified": 0,
                "approval_rate": 0.0,
                "modification_rate": 0.0
            }
        
        total = len(completed_reviews)
        approved = len([r for r in completed_reviews if r["decision"] == ReviewDecision.APPROVED])
        rejected = len([r for r in completed_reviews if r["decision"] == ReviewDecision.REJECTED])
        modified = len([r for r in completed_reviews if r["decision"] == ReviewDecision.MODIFIED])
        
        # HAR considers both approved and modified as acceptable
        acceptable = approved + modified
        har = acceptable / total if total > 0 else 0.0
        
        return {
            "har": har,
            "total_reviews": total,
            "approved": approved,
            "rejected": rejected,
            "modified": modified,
            "approval_rate": approved / total if total > 0 else 0.0,
            "modification_rate": modified / total if total > 0 else 0.0,
            "rejection_rate": rejected / total if total > 0 else 0.0
        }
    
    def calculate_har_by_stage(self) -> Dict[str, Dict[str, float]]:
        """Calculate HAR broken down by conversation stage."""
        stages = set(r["conversation_stage"] for r in self.reviews if r["conversation_stage"])
        
        results = {}
        for stage in stages:
            results[stage] = self.calculate_har(stage_filter=stage)
        
        return results
    
    def get_common_rejection_reasons(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get most common rejection/modification reasons.
        
        Args:
            top_n: Number of top reasons to return
        
        Returns:
            List of common reasons with counts
        """
        rejected_or_modified = [
            r for r in self.reviews
            if r["decision"] in [ReviewDecision.REJECTED, ReviewDecision.MODIFIED]
            and r["reviewer_notes"]
        ]
        
        # Count reasons (simple keyword extraction)
        reason_counts = {}
        for review in rejected_or_modified:
            notes = review["reviewer_notes"].lower()
            
            # Extract keywords
            keywords = [
                "persona", "pii", "safety", "coherence", "engagement",
                "intelligence", "tone", "length", "grammar", "context"
            ]
            
            for keyword in keywords:
                if keyword in notes:
                    reason_counts[keyword] = reason_counts.get(keyword, 0) + 1
        
        sorted_reasons = sorted(
            reason_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"reason": reason, "count": count}
            for reason, count in sorted_reasons[:top_n]
        ]
    
    def calculate_trend(self, window_days: int = 7) -> List[Dict[str, Any]]:
        """
        Calculate HAR trend over time.
        
        Args:
            window_days: Number of days to include in trend
        
        Returns:
            List of daily HAR values
        """
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        recent_data = [r for r in self.reviews if r["timestamp"] >= cutoff]
        
        # Group by day
        daily_data = {}
        for review in recent_data:
            date_key = review["timestamp"].date()
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(review)
        
        # Calculate daily HAR
        trend = []
        for date in sorted(daily_data.keys()):
            day_reviews = [r for r in daily_data[date] if r["decision"] != ReviewDecision.PENDING]
            
            if day_reviews:
                approved = len([r for r in day_reviews if r["decision"] == ReviewDecision.APPROVED])
                modified = len([r for r in day_reviews if r["decision"] == ReviewDecision.MODIFIED])
                total = len(day_reviews)
                har = (approved + modified) / total if total > 0 else 0.0
                
                trend.append({
                    "date": str(date),
                    "har": har,
                    "total_reviews": total,
                    "approved": approved,
                    "modified": modified
                })
        
        return trend
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall HAR performance summary."""
        overall_har = self.calculate_har()
        by_stage = self.calculate_har_by_stage()
        common_reasons = self.get_common_rejection_reasons(top_n=5)
        
        return {
            "overall": overall_har,
            "by_stage": by_stage,
            "common_rejection_reasons": common_reasons,
            "total_reviews": len(self.reviews),
            "pending_reviews": len([r for r in self.reviews if r["decision"] == ReviewDecision.PENDING])
        }
    
    def _filter_data(
        self,
        time_period_hours: int = None,
        stage_filter: str = None
    ) -> List[Dict[str, Any]]:
        """Filter review data based on criteria."""
        filtered = self.reviews
        
        if time_period_hours:
            cutoff = datetime.utcnow() - timedelta(hours=time_period_hours)
            filtered = [r for r in filtered if r["timestamp"] >= cutoff]
        
        if stage_filter:
            filtered = [r for r in filtered if r["conversation_stage"] == stage_filter]
        
        return filtered
