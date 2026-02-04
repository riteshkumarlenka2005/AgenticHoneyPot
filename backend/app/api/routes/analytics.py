"""Analytics API routes."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.database_service import DatabaseService

router = APIRouter()


class OverviewStats(BaseModel):
    """Overview statistics model."""
    active_conversations: int
    total_conversations: int
    intelligence_extracted: int
    time_wasted_seconds: int


class ScamTypeDistribution(BaseModel):
    """Scam type distribution model."""
    scam_type: str
    count: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    """Time series data point."""
    date: str
    count: int


@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(session: AsyncSession = Depends(get_db)):
    """
    Get dashboard overview statistics.
    
    Returns:
    - active_conversations: Number of active conversations
    - total_conversations: Total conversations
    - intelligence_extracted: Total intelligence artifacts extracted
    - time_wasted_seconds: Total time wasted by scammers
    """
    db = DatabaseService(session)
    
    overview = await db.get_analytics_overview()
    
    return OverviewStats(
        active_conversations=overview["active_conversations"],
        total_conversations=overview["total_conversations"],
        intelligence_extracted=overview["total_intelligence"],
        time_wasted_seconds=overview["total_time_wasted_seconds"]
    )


@router.get("/scam-types", response_model=List[ScamTypeDistribution])
async def get_scam_type_distribution(session: AsyncSession = Depends(get_db)):
    """
    Get distribution of scam types.
    
    Returns a list of scam types with their counts and percentages.
    """
    db = DatabaseService(session)
    
    distribution_data = await db.get_scam_type_distribution()
    
    # Calculate total for percentages
    total_scams = sum(item["count"] for item in distribution_data)
    
    # Build response with percentages
    distribution = []
    for item in distribution_data:
        percentage = (item["count"] / total_scams * 100) if total_scams > 0 else 0
        distribution.append(ScamTypeDistribution(
            scam_type=item["scam_type"] or "unknown",
            count=item["count"],
            percentage=round(percentage, 2)
        ))
    
    return distribution


@router.get("/timeline", response_model=List[TimeSeriesPoint])
async def get_timeline_data(
    days: int = 30,
    session: AsyncSession = Depends(get_db)
):
    """
    Get time series data for the last N days.
    
    Query parameters:
    - days: Number of days to look back (default: 30)
    
    Returns daily data points with conversation counts.
    """
    db = DatabaseService(session)
    
    timeline_data = await db.get_timeline_data(days=days)
    
    return [
        TimeSeriesPoint(
            date=item["date"],
            count=item["count"]
        )
        for item in timeline_data
    ]
