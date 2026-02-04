"""Information Disclosure Rate (IDR) metrics calculation."""
from typing import List, Dict
from datetime import datetime, timedelta


class IDRMetrics:
    """Calculate Information Disclosure Rate metrics."""
    
    @staticmethod
    def calculate_idr(
        intelligence_count: int,
        message_count: int
    ) -> float:
        """
        Calculate Information Disclosure Rate.
        
        IDR = (Intelligence Artifacts Extracted) / (Total Messages)
        
        Args:
            intelligence_count: Number of intelligence artifacts extracted
            message_count: Total number of messages in conversation
        
        Returns:
            IDR value (0.0 to 1.0)
        """
        if message_count == 0:
            return 0.0
        
        return intelligence_count / message_count
    
    @staticmethod
    def calculate_ids(
        intelligence_count: int,
        duration_seconds: int
    ) -> float:
        """
        Calculate Information Disclosure Speed.
        
        IDS = (Intelligence Artifacts) / (Time in minutes)
        
        Args:
            intelligence_count: Number of intelligence artifacts
            duration_seconds: Conversation duration in seconds
        
        Returns:
            IDS value (artifacts per minute)
        """
        if duration_seconds == 0:
            return 0.0
        
        duration_minutes = duration_seconds / 60
        return intelligence_count / duration_minutes
    
    @staticmethod
    def calculate_weighted_idr(
        artifacts_by_type: Dict[str, int],
        message_count: int,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate weighted IDR based on artifact importance.
        
        Args:
            artifacts_by_type: Dictionary of artifact type to count
            message_count: Total message count
            weights: Optional weights for each artifact type
        
        Returns:
            Weighted IDR value
        """
        if weights is None:
            # Default weights (higher value = more important)
            weights = {
                "upi_id": 1.5,
                "bank_account": 1.5,
                "ifsc_code": 1.2,
                "phone": 1.0,
                "email": 0.8,
                "url": 0.7
            }
        
        weighted_sum = 0.0
        for artifact_type, count in artifacts_by_type.items():
            weight = weights.get(artifact_type, 1.0)
            weighted_sum += count * weight
        
        if message_count == 0:
            return 0.0
        
        return weighted_sum / message_count
    
    @staticmethod
    def calculate_efficiency_score(
        idr: float,
        ids: float,
        time_wasted_seconds: int
    ) -> float:
        """
        Calculate overall honeypot efficiency score.
        
        Combines IDR, IDS, and time wasted to give overall score.
        
        Args:
            idr: Information Disclosure Rate
            ids: Information Disclosure Speed
            time_wasted_seconds: Time wasted by scammer
        
        Returns:
            Efficiency score (0-100)
        """
        # Normalize time wasted (max 1 hour = score of 1)
        time_score = min(time_wasted_seconds / 3600, 1.0)
        
        # Normalize IDS (assume max 2 artifacts per minute)
        ids_score = min(ids / 2.0, 1.0)
        
        # Combine scores (weighted average)
        efficiency = (idr * 0.4 + ids_score * 0.3 + time_score * 0.3) * 100
        
        return min(efficiency, 100.0)
    
    @staticmethod
    def get_metrics_for_conversation(
        conversation_data: Dict
    ) -> Dict:
        """
        Calculate all metrics for a conversation.
        
        Args:
            conversation_data: Dictionary with conversation details
        
        Returns:
            Dictionary with all calculated metrics
        """
        message_count = conversation_data.get("message_count", 0)
        duration_seconds = conversation_data.get("duration_seconds", 0)
        
        # Count intelligence by type
        intelligence_extracted = conversation_data.get("intelligence_extracted", {})
        total_intelligence = sum(intelligence_extracted.values())
        
        # Calculate metrics
        idr = IDRMetrics.calculate_idr(total_intelligence, message_count)
        ids = IDRMetrics.calculate_ids(total_intelligence, duration_seconds)
        weighted_idr = IDRMetrics.calculate_weighted_idr(
            intelligence_extracted,
            message_count
        )
        efficiency = IDRMetrics.calculate_efficiency_score(
            idr, ids, duration_seconds
        )
        
        return {
            "idr": round(idr, 3),
            "ids": round(ids, 3),
            "weighted_idr": round(weighted_idr, 3),
            "efficiency_score": round(efficiency, 2),
            "total_intelligence": total_intelligence,
            "time_wasted_minutes": round(duration_seconds / 60, 2)
        }


# Global metrics instance
idr_metrics = IDRMetrics()
