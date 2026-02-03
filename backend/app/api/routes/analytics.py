"""Analytics API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ...db.database import get_db
from ...models import Conversation, Message, Intelligence
from ...models.conversation import ConversationStatus

router = APIRouter()


@router.get("/overview")
async def get_overview(db: Session = Depends(get_db)):
    """Get dashboard overview statistics."""
    # Active conversations
    active_count = db.query(Conversation).filter(
        Conversation.status.in_([ConversationStatus.ACTIVE, ConversationStatus.STALLING])
    ).count()
    
    # Scams detected
    scams_detected = db.query(Conversation).filter(
        Conversation.scam_type.isnot(None)
    ).count()
    
    # Intelligence extracted
    intelligence_count = db.query(Intelligence).count()
    
    # Time wasted (approximate)
    total_messages = db.query(Message).filter(
        Message.sender_type == "scammer"
    ).count()
    time_wasted_seconds = total_messages * 120  # Assume 2 min per message
    
    return {
        "active_conversations": active_count,
        "scams_detected": scams_detected,
        "intelligence_extracted": intelligence_count,
        "time_wasted_seconds": time_wasted_seconds,
        "time_wasted_hours": round(time_wasted_seconds / 3600, 1)
    }


@router.get("/scam-types")
async def get_scam_types(db: Session = Depends(get_db)):
    """Get scam type distribution."""
    results = db.query(
        Conversation.scam_type,
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.scam_type.isnot(None)
    ).group_by(Conversation.scam_type).all()
    
    return [
        {"type": scam_type or "unknown", "count": count}
        for scam_type, count in results
    ]


@router.get("/timeline")
async def get_timeline(days: int = 7, db: Session = Depends(get_db)):
    """Get time series data for conversations."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get conversations per day
    results = db.query(
        func.date(Conversation.started_at).label('date'),
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.started_at >= start_date
    ).group_by(func.date(Conversation.started_at)).all()
    
    return [
        {"date": str(date), "count": count}
        for date, count in results
    ]


@router.get("/extraction-rate")
async def get_extraction_rate(db: Session = Depends(get_db)):
    """Get intelligence extraction success rate."""
    total_conversations = db.query(Conversation).filter(
        Conversation.scam_type.isnot(None)
    ).count()
    
    conversations_with_intel = db.query(
        func.distinct(Intelligence.conversation_id)
    ).count()
    
    if total_conversations == 0:
        success_rate = 0.0
    else:
        success_rate = (conversations_with_intel / total_conversations) * 100
    
    return {
        "total_scam_conversations": total_conversations,
        "conversations_with_intelligence": conversations_with_intel,
        "success_rate": round(success_rate, 1)
    }


@router.get("/recent-activity")
async def get_recent_activity(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent conversation activity."""
    messages = db.query(Message).order_by(
        Message.timestamp.desc()
    ).limit(limit).all()
    
    activities = []
    for msg in messages:
        conversation = db.query(Conversation).filter(
            Conversation.id == msg.conversation_id
        ).first()
        
        if conversation:
            activities.append({
                "timestamp": msg.timestamp,
                "conversation_id": str(conversation.id),
                "scammer_identifier": conversation.scammer_identifier,
                "sender_type": msg.sender_type.value,
                "preview": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                "scam_type": conversation.scam_type
            })
    
    return activities
