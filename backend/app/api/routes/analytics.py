"""Analytics API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta

router = APIRouter()


class OverviewStats(BaseModel):
    """Overview statistics model."""
    active_conversations: int
    scams_detected: int
    intelligence_extracted: int
    time_wasted_seconds: int


class ScamTypeDistribution(BaseModel):
    """Scam type distribution model."""
    scam_type: str
    count: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    """Time series data point."""
    timestamp: datetime
    scams_detected: int
    intelligence_extracted: int


@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats():
    """
    Get dashboard overview statistics.
    
    Returns:
    - active_conversations: Number of active conversations
    - scams_detected: Total scams detected
    - intelligence_extracted: Total intelligence artifacts extracted
    - time_wasted_seconds: Total time wasted by scammers
    """
    from app.api.routes.messages import active_conversations
    
    active_count = 0
    scams_detected = 0
    intelligence_count = 0
    total_time_wasted = 0
    
    for conv_id, conv_data in active_conversations.items():
        state = conv_data["state"]
        
        # Count active conversations
        if state.status.value == "active":
            active_count += 1
        
        # Count scams detected
        if state.detection_confidence >= 0.5:
            scams_detected += 1
        
        # Count intelligence artifacts
        for intel_type, values in state.intelligence_extracted.items():
            intelligence_count += len(values)
        
        # Sum time wasted
        total_time_wasted += state.get_duration()
    
    return OverviewStats(
        active_conversations=active_count,
        scams_detected=scams_detected,
        intelligence_extracted=intelligence_count,
        time_wasted_seconds=total_time_wasted
    )


@router.get("/scam-types", response_model=List[ScamTypeDistribution])
async def get_scam_type_distribution():
    """
    Get distribution of scam types.
    
    Returns a list of scam types with their counts and percentages.
    """
    from app.api.routes.messages import active_conversations
    
    scam_type_counts: Dict[str, int] = {}
    total_scams = 0
    
    for conv_id, conv_data in active_conversations.items():
        state = conv_data["state"]
        
        if state.detection_confidence >= 0.5:
            scam_type = state.scam_type
            scam_type_counts[scam_type] = scam_type_counts.get(scam_type, 0) + 1
            total_scams += 1
    
    # Calculate percentages
    distribution = []
    for scam_type, count in scam_type_counts.items():
        percentage = (count / total_scams * 100) if total_scams > 0 else 0
        distribution.append(ScamTypeDistribution(
            scam_type=scam_type,
            count=count,
            percentage=round(percentage, 2)
        ))
    
    # Sort by count descending
    distribution.sort(key=lambda x: x.count, reverse=True)
    
    return distribution


@router.get("/timeline", response_model=List[TimeSeriesPoint])
async def get_timeline_data(hours: int = 24):
    """
    Get time series data for the last N hours.
    
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    
    Returns hourly data points with scam detections and intelligence extracted.
    """
    from app.api.routes.messages import active_conversations
    
    # Generate hourly buckets
    now = datetime.utcnow()
    timeline = []
    
    for i in range(hours):
        hour_start = now - timedelta(hours=hours - i)
        hour_end = hour_start + timedelta(hours=1)
        
        scams_in_hour = 0
        intelligence_in_hour = 0
        
        for conv_id, conv_data in active_conversations.items():
            state = conv_data["state"]
            
            # Check if conversation started in this hour
            if hour_start <= state.started_at < hour_end:
                if state.detection_confidence >= 0.5:
                    scams_in_hour += 1
                
                for intel_type, values in state.intelligence_extracted.items():
                    intelligence_in_hour += len(values)
        
        timeline.append(TimeSeriesPoint(
            timestamp=hour_start,
            scams_detected=scams_in_hour,
            intelligence_extracted=intelligence_in_hour
        ))
    
    return timeline
