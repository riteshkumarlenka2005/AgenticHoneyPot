"""Intelligence API routes."""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from datetime import datetime
import csv
import io
import json

from ...db.database import get_db
from ...models import Intelligence, Conversation, Message
from ...models.intelligence import ArtifactType
from ...services.extraction.extractor import IntelligenceExtractor

router = APIRouter()
extractor = IntelligenceExtractor()


class IntelligenceItem(BaseModel):
    """Intelligence item schema."""
    id: str
    conversation_id: str
    artifact_type: str
    value: str
    confidence: float
    extracted_at: datetime
    validated: bool


@router.get("/")
async def get_intelligence(db: Session = Depends(get_db)):
    """Get all extracted intelligence."""
    items = db.query(Intelligence).order_by(
        Intelligence.extracted_at.desc()
    ).all()
    
    result = []
    for item in items:
        result.append({
            "id": str(item.id),
            "conversation_id": str(item.conversation_id),
            "artifact_type": item.artifact_type.value,
            "value": item.value,
            "confidence": item.confidence,
            "extracted_at": item.extracted_at,
            "validated": item.validated
        })
    
    return result


@router.get("/summary")
async def get_intelligence_summary(db: Session = Depends(get_db)):
    """Get intelligence summary grouped by type."""
    summary = {}
    
    for artifact_type in ArtifactType:
        count = db.query(Intelligence).filter(
            Intelligence.artifact_type == artifact_type
        ).count()
        
        items = db.query(Intelligence).filter(
            Intelligence.artifact_type == artifact_type
        ).limit(10).all()
        
        summary[artifact_type.value] = {
            "count": count,
            "recent_items": [
                {
                    "value": item.value,
                    "confidence": item.confidence,
                    "extracted_at": item.extracted_at.isoformat()
                }
                for item in items
            ]
        }
    
    return summary


@router.get("/export")
async def export_intelligence(format: str = "json", db: Session = Depends(get_db)):
    """Export intelligence data in JSON or CSV format."""
    items = db.query(Intelligence).all()
    
    data = [
        {
            "id": str(item.id),
            "conversation_id": str(item.conversation_id),
            "artifact_type": item.artifact_type.value,
            "value": item.value,
            "confidence": item.confidence,
            "extracted_at": item.extracted_at.isoformat(),
            "validated": item.validated
        }
        for item in items
    ]
    
    if format.lower() == "csv":
        # Generate CSV
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=intelligence.csv"}
        )
    else:
        # Return JSON
        return data


@router.post("/extract/{conversation_id}")
async def extract_intelligence(conversation_id: str, db: Session = Depends(get_db)):
    """Extract intelligence from a specific conversation."""
    try:
        import uuid
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    # Get all scammer messages
    messages = db.query(Message).filter(
        Message.conversation_id == conv_uuid,
        Message.sender_type == "scammer"
    ).all()
    
    message_list = [{"content": msg.content} for msg in messages]
    extracted = extractor.extract_from_conversation(message_list)
    
    # Save extracted intelligence
    saved_items = []
    for artifact_type, values in extracted.items():
        # Map to enum
        type_mapping = {
            "upi_ids": ArtifactType.UPI_ID,
            "phone_numbers": ArtifactType.PHONE,
            "ifsc_codes": ArtifactType.IFSC_CODE,
            "bank_accounts": ArtifactType.BANK_ACCOUNT,
            "urls": ArtifactType.URL,
            "emails": ArtifactType.EMAIL
        }
        
        enum_type = type_mapping.get(artifact_type)
        if not enum_type:
            continue
        
        for value in values:
            # Check if already exists
            existing = db.query(Intelligence).filter(
                Intelligence.conversation_id == conv_uuid,
                Intelligence.artifact_type == enum_type,
                Intelligence.value == value
            ).first()
            
            if not existing:
                intel = Intelligence(
                    conversation_id=conv_uuid,
                    artifact_type=enum_type,
                    value=value,
                    confidence=0.8
                )
                db.add(intel)
                saved_items.append(value)
    
    db.commit()
    
    return {
        "conversation_id": conversation_id,
        "extracted": extracted,
        "saved_count": len(saved_items)
    }
