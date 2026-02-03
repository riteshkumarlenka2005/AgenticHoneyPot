"""Intelligence API routes."""
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
import json
import io
import csv

router = APIRouter()


class IntelligenceArtifact(BaseModel):
    """Intelligence artifact model."""
    id: str
    conversation_id: str
    artifact_type: str
    value: str
    confidence: float
    extracted_at: datetime


@router.get("", response_model=List[IntelligenceArtifact])
async def get_intelligence(
    artifact_type: str = None,
    min_confidence: float = 0.0
):
    """
    Get all extracted intelligence artifacts.
    
    Query parameters:
    - artifact_type: Filter by type (upi_id, bank_account, phone, url, email)
    - min_confidence: Minimum confidence score
    """
    from app.api.routes.messages import active_conversations
    
    artifacts = []
    artifact_id = 0
    
    for conv_id, conv_data in active_conversations.items():
        state = conv_data["state"]
        
        # Extract all intelligence types
        for intel_type, values in state.intelligence_extracted.items():
            for value in values:
                # Apply filters
                if artifact_type and intel_type != artifact_type:
                    continue
                
                # Confidence score (simplified)
                confidence = 0.8
                
                if confidence >= min_confidence:
                    artifacts.append(IntelligenceArtifact(
                        id=f"intel-{artifact_id}",
                        conversation_id=conv_id,
                        artifact_type=intel_type,
                        value=value,
                        confidence=confidence,
                        extracted_at=state.last_activity
                    ))
                    artifact_id += 1
    
    return artifacts


@router.get("/export")
async def export_intelligence(format: str = "json"):
    """
    Export intelligence data in various formats.
    
    Query parameters:
    - format: Export format (json or csv)
    """
    from app.api.routes.messages import active_conversations
    
    # Collect all intelligence
    intelligence_data = []
    
    for conv_id, conv_data in active_conversations.items():
        state = conv_data["state"]
        
        for intel_type, values in state.intelligence_extracted.items():
            for value in values:
                intelligence_data.append({
                    "conversation_id": conv_id,
                    "scammer_identifier": state.scammer_identifier,
                    "scam_type": state.scam_type,
                    "artifact_type": intel_type,
                    "value": value,
                    "extracted_at": state.last_activity.isoformat()
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
