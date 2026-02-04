"""Intelligence API routes."""
from fastapi import APIRouter, Response, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import json
import io
import csv

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.database_service import DatabaseService
from app.models.intelligence import ArtifactType

router = APIRouter()


class IntelligenceArtifact(BaseModel):
    """Intelligence artifact model."""
    id: str
    conversation_id: str
    artifact_type: str
    value: str
    confidence: float
    extracted_at: datetime
    validated: bool


@router.get("", response_model=List[IntelligenceArtifact])
async def get_intelligence(
    artifact_type: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db)
):
    """
    Get all extracted intelligence artifacts.
    
    Query parameters:
    - artifact_type: Filter by type (UPI_ID, BANK_ACCOUNT, PHONE, URL, EMAIL, IFSC_CODE)
    - min_confidence: Minimum confidence score
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    db = DatabaseService(session)
    
    # Parse artifact_type filter
    artifact_filter = None
    if artifact_type:
        try:
            artifact_filter = ArtifactType[artifact_type.upper()]
        except KeyError:
            pass  # Skip invalid types
    
    # Get intelligence from database
    intelligence = await db.get_intelligence(
        artifact_type=artifact_filter,
        limit=limit,
        offset=offset
    )
    
    # Filter by confidence and build response
    result = []
    for intel in intelligence:
        if intel.confidence >= min_confidence:
            result.append(IntelligenceArtifact(
                id=str(intel.id),
                conversation_id=str(intel.conversation_id),
                artifact_type=intel.artifact_type.value,
                value=intel.value,
                confidence=intel.confidence,
                extracted_at=intel.extracted_at,
                validated=intel.validated
            ))
    
    return result


@router.get("/export")
async def export_intelligence(
    format: str = "json",
    session: AsyncSession = Depends(get_db)
):
    """
    Export intelligence data in various formats.
    
    Query parameters:
    - format: Export format (json or csv)
    """
    db = DatabaseService(session)
    
    # Get all intelligence with conversation info
    intelligence = await db.get_intelligence(limit=10000)
    
    # Collect all intelligence data
    intelligence_data = []
    
    for intel in intelligence:
        # Get conversation details
        conversation = await db.get_conversation(intel.conversation_id)
        
        intelligence_data.append({
            "id": str(intel.id),
            "conversation_id": str(intel.conversation_id),
            "scammer_identifier": conversation.scammer_identifier if conversation else "unknown",
            "scam_type": conversation.scam_type if conversation else "unknown",
            "artifact_type": intel.artifact_type.value,
            "value": intel.value,
            "confidence": intel.confidence,
            "validated": intel.validated,
            "extracted_at": intel.extracted_at.isoformat()
        })
    
    if format == "csv":
        # Generate CSV
        output = io.StringIO()
        if intelligence_data:
            writer = csv.DictWriter(output, fieldnames=intelligence_data[0].keys())
            writer.writeheader()
            writer.writerows(intelligence_data)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=intelligence.csv"}
        )
    else:
        # Return JSON
        return intelligence_data
