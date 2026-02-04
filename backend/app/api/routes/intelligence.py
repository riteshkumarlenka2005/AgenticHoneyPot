"""Intelligence API routes."""
from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
import io
import csv

from app.db.database import get_db
from app.services.database_service import IntelligenceService, ConversationService
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
    
    class Config:
        from_attributes = True


class ValidateRequest(BaseModel):
    """Request to validate intelligence."""
    validated: bool


@router.get("", response_model=List[IntelligenceArtifact])
async def get_intelligence(
    artifact_type: Optional[str] = None,
    min_confidence: float = 0.0,
    validated: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all extracted intelligence artifacts.
    
    Query parameters:
    - artifact_type: Filter by type (upi_id, bank_account, phone, url, email)
    - min_confidence: Minimum confidence score
    - validated: Filter by validation status
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    # Convert artifact_type string to enum if provided
    artifact_type_enum = None
    if artifact_type:
        try:
            artifact_type_enum = ArtifactType(artifact_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid artifact type: {artifact_type}")
    
    intelligence = await IntelligenceService.list_intelligence(
        db,
        artifact_type=artifact_type_enum,
        validated=validated,
        limit=limit,
        offset=offset
    )
    
    # Filter by min_confidence
    artifacts = [
        IntelligenceArtifact(
            id=str(intel.id),
            conversation_id=str(intel.conversation_id),
            artifact_type=intel.artifact_type.value,
            value=intel.value,
            confidence=intel.confidence,
            extracted_at=intel.extracted_at,
            validated=intel.validated
        )
        for intel in intelligence
        if intel.confidence >= min_confidence
    ]
    
    return artifacts


@router.patch("/{intelligence_id}/validate")
async def validate_intelligence(
    intelligence_id: str,
    request: ValidateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Mark an intelligence artifact as validated or not."""
    try:
        intel_uuid = UUID(intelligence_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid intelligence ID format")
    
    await IntelligenceService.validate_intelligence(
        db,
        intelligence_id=intel_uuid,
        validated=request.validated
    )
    await db.commit()
    
    return {"status": "success", "validated": request.validated}


@router.get("/export")
async def export_intelligence(
    format: str = "json",
    db: AsyncSession = Depends(get_db)
):
    """
    Export intelligence data in various formats.
    
    Query parameters:
    - format: Export format (json, csv, or stix)
    """
    # Get all intelligence
    intelligence = await IntelligenceService.list_intelligence(db, limit=10000)
    
    # Collect all intelligence data
    intelligence_data = []
    
    for intel in intelligence:
        # Get conversation details
        conversation = await ConversationService.get_by_id(db, intel.conversation_id)
        
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
    elif format == "stix":
        # TODO: Implement STIX 2.1 format export
        raise HTTPException(status_code=501, detail="STIX format not yet implemented")
    else:
        # Return JSON
        return intelligence_data
