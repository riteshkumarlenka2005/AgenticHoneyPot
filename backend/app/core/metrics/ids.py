"""Information Disclosure Speed (IDS) metric calculation."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import statistics


class InformationDisclosureSpeed:
    """
    Calculate Information Disclosure Speed (IDS).
    
    IDS = Time to First Intelligence Extraction
    
    This metric measures how quickly the honeypot can extract the first
    piece of intelligence from a scammer.
    """
    
    def __init__(self):
        """Initialize IDS calculator."""
        self.extraction_times: List[Dict[str, Any]] = []
    
    def record_extraction(
        self,
        conversation_id: str,
        conversation_start: datetime,
        first_extraction_time: datetime,
        scam_type: str
    ):
        """
        Record an intelligence extraction for IDS calculation.
        
        Args:
            conversation_id: Unique conversation identifier
            conversation_start: When conversation started
            first_extraction_time: When first intelligence was extracted
            scam_type: Type of scam
        """
        time_to_first = (first_extraction_time - conversation_start).total_seconds()
        
        self.extraction_times.append({
            "id": conversation_id,
            "time_to_first_seconds": time_to_first,
            "scam_type": scam_type,
            "timestamp": first_extraction_time
        })
    
    def calculate_ids(
        self,
        time_period_hours: int = None,
        scam_type_filter: str = None
    ) -> Dict[str, float]:
        """
        Calculate Information Disclosure Speed metrics.
        
        Args:
            time_period_hours: Optional time window to consider
            scam_type_filter: Optional filter for specific scam type
        
        Returns:
            Dictionary with IDS metrics
        """
        # Filter data
        filtered_data = self._filter_data(time_period_hours, scam_type_filter)
        
        if not filtered_data:
            return {
                "average_ids_seconds": 0.0,
                "median_ids_seconds": 0.0,
                "min_ids_seconds": 0.0,
                "max_ids_seconds": 0.0,
                "sample_size": 0
            }
        
        times = [e["time_to_first_seconds"] for e in filtered_data]
        
        return {
            "average_ids_seconds": statistics.mean(times),
            "median_ids_seconds": statistics.median(times),
            "min_ids_seconds": min(times),
            "max_ids_seconds": max(times),
            "sample_size": len(times),
            "average_ids_minutes": statistics.mean(times) / 60,
            "median_ids_minutes": statistics.median(times) / 60
        }
    
    def calculate_ids_by_scam_type(self) -> Dict[str, Dict[str, float]]:
        """Calculate IDS broken down by scam type."""
        scam_types = set(e["scam_type"] for e in self.extraction_times if e["scam_type"])
        
        results = {}
        for scam_type in scam_types:
            results[scam_type] = self.calculate_ids(scam_type_filter=scam_type)
        
        return results
    
    def get_fastest_extraction_types(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get scam types with fastest intelligence extraction."""
        by_type = self.calculate_ids_by_scam_type()
        
        sorted_types = sorted(
            by_type.items(),
            key=lambda x: x[1]["average_ids_seconds"]
        )
        
        return [
            {
                "scam_type": scam_type,
                "average_seconds": metrics["average_ids_seconds"],
                "average_minutes": metrics["average_ids_minutes"],
                "median_seconds": metrics["median_ids_seconds"],
                "sample_size": metrics["sample_size"]
            }
            for scam_type, metrics in sorted_types[:top_n]
        ]
    
    def calculate_trend(self, window_days: int = 7) -> List[Dict[str, Any]]:
        """
        Calculate IDS trend over time.
        
        Args:
            window_days: Number of days to include in trend
        
        Returns:
            List of daily IDS values
        """
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        recent_data = [e for e in self.extraction_times if e["timestamp"] >= cutoff]
        
        # Group by day
        daily_data = {}
        for extraction in recent_data:
            date_key = extraction["timestamp"].date()
            if date_key not in daily_data:
                daily_data[date_key] = []
            daily_data[date_key].append(extraction)
        
        # Calculate daily IDS
        trend = []
        for date in sorted(daily_data.keys()):
            day_extractions = daily_data[date]
            times = [e["time_to_first_seconds"] for e in day_extractions]
            
            trend.append({
                "date": str(date),
                "average_ids_seconds": statistics.mean(times),
                "median_ids_seconds": statistics.median(times),
                "count": len(times)
            })
        
        return trend
    
    def get_performance_distribution(self) -> Dict[str, int]:
        """
        Get distribution of extraction speeds.
        
        Returns:
            Dictionary with counts in different time buckets
        """
        if not self.extraction_times:
            return {}
        
        times = [e["time_to_first_seconds"] for e in self.extraction_times]
        
        buckets = {
            "under_1_min": 0,
            "1_to_5_min": 0,
            "5_to_15_min": 0,
            "15_to_30_min": 0,
            "over_30_min": 0
        }
        
        for time_sec in times:
            time_min = time_sec / 60
            
            if time_min < 1:
                buckets["under_1_min"] += 1
            elif time_min < 5:
                buckets["1_to_5_min"] += 1
            elif time_min < 15:
                buckets["5_to_15_min"] += 1
            elif time_min < 30:
                buckets["15_to_30_min"] += 1
            else:
                buckets["over_30_min"] += 1
        
        return buckets
    
    def _filter_data(
        self,
        time_period_hours: int = None,
        scam_type_filter: str = None
    ) -> List[Dict[str, Any]]:
        """Filter extraction data based on criteria."""
        filtered = self.extraction_times
        
        if time_period_hours:
            cutoff = datetime.utcnow() - timedelta(hours=time_period_hours)
            filtered = [e for e in filtered if e["timestamp"] >= cutoff]
        
        if scam_type_filter:
            filtered = [e for e in filtered if e["scam_type"] == scam_type_filter]
        
        return filtered
