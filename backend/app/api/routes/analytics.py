"""Analytics API routes."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.conversation import Conversation, ConversationStatus
from app.models.intelligence import Intelligence

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
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """
    Get dashboard overview statistics.
    
    Returns:
    - active_conversations: Number of active conversations
    - scams_detected: Total scams detected
    - intelligence_extracted: Total intelligence artifacts extracted
    - time_wasted_seconds: Total time wasted by scammers
    """
    # Count active conversations
    active_result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.status == ConversationStatus.ACTIVE)
    )
    active_count = active_result.scalar() or 0
    
    # Count scams detected (confidence >= 0.5)
    scams_result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.detection_confidence >= 0.5)
    )
    scams_detected = scams_result.scalar() or 0
    
    # Count intelligence extracted
    intel_result = await db.execute(
        select(func.count(Intelligence.id))
    )
    intelligence_count = intel_result.scalar() or 0
    
    # Sum time wasted
    time_result = await db.execute(
        select(func.sum(Conversation.total_duration_seconds))
    )
    total_time_wasted = time_result.scalar() or 0
    
    return OverviewStats(
        active_conversations=active_count,
        scams_detected=scams_detected,
        intelligence_extracted=intelligence_count,
        time_wasted_seconds=total_time_wasted
    )


@router.get("/scam-types", response_model=List[ScamTypeDistribution])
async def get_scam_type_distribution(db: AsyncSession = Depends(get_db)):
    """
    Get distribution of scam types.
    
    Returns a list of scam types with their counts and percentages.
    """
    # Get scam type counts
    result = await db.execute(
        select(
            Conversation.scam_type,
            func.count(Conversation.id).label('count')
        )
        .where(Conversation.detection_confidence >= 0.5)
        .where(Conversation.scam_type.isnot(None))
        .group_by(Conversation.scam_type)
    )
    
    scam_type_counts = result.all()
    total_scams = sum(count for _, count in scam_type_counts)
    
    # Calculate percentages
    distribution = []
    for scam_type, count in scam_type_counts:
        percentage = (count / total_scams * 100) if total_scams > 0 else 0
        distribution.append(ScamTypeDistribution(
            scam_type=scam_type or "unknown",
            count=count,
            percentage=round(percentage, 2)
        ))
    
    # Sort by count descending
    distribution.sort(key=lambda x: x.count, reverse=True)
    
    return distribution


@router.get("/timeline", response_model=List[TimeSeriesPoint])
async def get_timeline_data(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Get time series data for the last N hours.
    
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    
    Returns hourly data points with scam detections and intelligence extracted.
    """
    # Generate hourly buckets
    now = datetime.utcnow()
    timeline = []
    
    for i in range(hours):
        hour_start = now - timedelta(hours=hours - i)
        hour_end = hour_start + timedelta(hours=1)
        
        # Count scams in this hour
        scams_result = await db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.started_at >= hour_start)
            .where(Conversation.started_at < hour_end)
            .where(Conversation.detection_confidence >= 0.5)
        )
        scams_in_hour = scams_result.scalar() or 0
        
        # Count intelligence in this hour
        intel_result = await db.execute(
            select(func.count(Intelligence.id))
            .where(Intelligence.extracted_at >= hour_start)
            .where(Intelligence.extracted_at < hour_end)
        )
        intelligence_in_hour = intel_result.scalar() or 0
        
        timeline.append(TimeSeriesPoint(
            timestamp=hour_start,
            scams_detected=scams_in_hour,
            intelligence_extracted=intelligence_in_hour
        ))
    
    return timeline
