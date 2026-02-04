"""Information Disclosure Rate (IDR) metric calculation."""
from typing import List, Dict, Any
from datetime import datetime, timedelta


class InformationDisclosureRate:
    """
    Calculate Information Disclosure Rate (IDR).
    
    IDR = (Number of Intelligence Artifacts Extracted) / (Total Conversations)
    
    This metric measures how effective the honeypot is at extracting
    intelligence from scam attempts.
    """
    
    def __init__(self):
        """Initialize IDR calculator."""
        self.conversation_data: List[Dict[str, Any]] = []
    
    def record_conversation(
        self,
        conversation_id: str,
        intelligence_count: int,
        duration_seconds: int,
        scam_type: str
    ):
        """
        Record a conversation for IDR calculation.
        
        Args:
            conversation_id: Unique conversation identifier
            intelligence_count: Number of intelligence artifacts extracted
            duration_seconds: Duration of conversation
            scam_type: Type of scam detected
        """
        self.conversation_data.append({
            "id": conversation_id,
            "intelligence_count": intelligence_count,
            "duration": duration_seconds,
            "scam_type": scam_type,
            "timestamp": datetime.utcnow()
        })
    
    def calculate_idr(
        self,
        time_period_hours: int = None,
        scam_type_filter: str = None
    ) -> Dict[str, float]:
        """
        Calculate Information Disclosure Rate.
        
        Args:
            time_period_hours: Optional time window to consider
            scam_type_filter: Optional filter for specific scam type
        
        Returns:
            Dictionary with IDR metrics
        """
        # Filter data
        filtered_data = self._filter_data(time_period_hours, scam_type_filter)
        
        if not filtered_data:
            return {
                "idr": 0.0,
                "total_conversations": 0,
                "total_intelligence": 0,
                "average_per_conversation": 0.0
            }
        
        total_conversations = len(filtered_data)
        total_intelligence = sum(c["intelligence_count"] for c in filtered_data)
        
        # Calculate IDR
        idr = total_intelligence / total_conversations if total_conversations > 0 else 0.0
        
        # Calculate additional metrics
        successful_extractions = len([c for c in filtered_data if c["intelligence_count"] > 0])
        success_rate = successful_extractions / total_conversations if total_conversations > 0 else 0.0
        
        return {
            "idr": idr,
            "total_conversations": total_conversations,
            "total_intelligence": total_intelligence,
            "average_per_conversation": idr,
            "successful_extraction_rate": success_rate,
            "conversations_with_intelligence": successful_extractions
        }
    
    def calculate_idr_by_scam_type(self) -> Dict[str, Dict[str, float]]:
        """Calculate IDR broken down by scam type."""
        scam_types = set(c["scam_type"] for c in self.conversation_data if c["scam_type"])
        
        results = {}
        for scam_type in scam_types:
            results[scam_type] = self.calculate_idr(scam_type_filter=scam_type)
        
        return results
    
    def get_top_performing_types(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top N scam types by IDR."""
        by_type = self.calculate_idr_by_scam_type()
        
        sorted_types = sorted(
            by_type.items(),
            key=lambda x: x[1]["idr"],
            reverse=True
        )
        
        return [
            {
                "scam_type": scam_type,
                "idr": metrics["idr"],
                "conversations": metrics["total_conversations"],
                "intelligence": metrics["total_intelligence"]
            }
            for scam_type, metrics in sorted_types[:top_n]
        ]
    
    def calculate_trend(self, window_days: int = 7) -> List[Dict[str, Any]]:
        """
        Calculate IDR trend over time.
        
        Args:
            window_days: Number of days to include in trend
        
        Returns:
            List of daily IDR values
        """
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        recent_data = [c for c in self.conversation_data if c["timestamp"] >= cutoff]
        
        # Group by day
        daily_data = {}
        for conv in recent_data:
            date_key = conv["timestamp"].date()
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(conv)
        
        # Calculate daily IDR
        trend = []
        for date in sorted(daily_data.keys()):
            day_convs = daily_data[date]
            total_intel = sum(c["intelligence_count"] for c in day_convs)
            count = len(day_convs)
            
            trend.append({
                "date": str(date),
                "idr": total_intel / count if count > 0 else 0.0,
                "conversations": count,
                "intelligence": total_intel
            })
        
        return trend
    
    def _filter_data(
        self,
        time_period_hours: int = None,
        scam_type_filter: str = None
    ) -> List[Dict[str, Any]]:
        """Filter conversation data based on criteria."""
        filtered = self.conversation_data
        
        if time_period_hours:
            cutoff = datetime.utcnow() - timedelta(hours=time_period_hours)
            filtered = [c for c in filtered if c["timestamp"] >= cutoff]
        
        if scam_type_filter:
            filtered = [c for c in filtered if c["scam_type"] == scam_type_filter]
        
        return filtered
