"""HITL (Human-in-the-Loop) API routes."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from app.services.hitl.approval_queue import approval_queue, ApprovalStatus


router = APIRouter()


class ApprovalDecision(BaseModel):
    """Approval decision model."""
    reviewer: str
    notes: Optional[str] = None


class CreateApprovalRequest(BaseModel):
    """Create approval request model."""
    request_type: str
    data: dict
    priority: str = "medium"
    expires_in_seconds: int = 3600
    metadata: Optional[dict] = None
    auto_approve_confidence: Optional[float] = None


@router.get("/requests")
async def get_pending_requests(
    request_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get pending approval requests.
    
    Args:
        request_type: Filter by type (response, action, intelligence)
        priority: Filter by priority (low, medium, high, critical)
        limit: Maximum number of requests
        
    Returns:
        List of pending requests
    """
    requests = approval_queue.get_pending_requests(
        request_type=request_type,
        priority=priority,
        limit=limit
    )
    
    return {
        "count": len(requests),
        "requests": [req.to_dict() for req in requests]
    }


@router.get("/requests/{request_id}")
async def get_request(request_id: UUID):
    """
    Get specific approval request.
    
    Args:
        request_id: Request UUID
        
    Returns:
        Request details
    """
    request = approval_queue.get_request(request_id)
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return request.to_dict()


@router.post("/requests")
async def create_request(request_data: CreateApprovalRequest):
    """
    Create new approval request.
    
    Args:
        request_data: Request data
        
    Returns:
        Created request
    """
    request = approval_queue.create_request(
        request_type=request_data.request_type,
        data=request_data.data,
        priority=request_data.priority,
        expires_in_seconds=request_data.expires_in_seconds,
        metadata=request_data.metadata,
        auto_approve_confidence=request_data.auto_approve_confidence
    )
    
    return request.to_dict()


@router.post("/requests/{request_id}/approve")
async def approve_request(request_id: UUID, decision: ApprovalDecision):
    """
    Approve a request.
    
    Args:
        request_id: Request UUID
        decision: Approval decision with reviewer and notes
        
    Returns:
        Updated request
    """
    success = approval_queue.approve_request(
        request_id=request_id,
        reviewer=decision.reviewer,
        notes=decision.notes
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Could not approve request (may be expired or already reviewed)"
        )
    
    request = approval_queue.get_request(request_id)
    return request.to_dict()


@router.post("/requests/{request_id}/reject")
async def reject_request(request_id: UUID, decision: ApprovalDecision):
    """
    Reject a request.
    
    Args:
        request_id: Request UUID
        decision: Rejection decision with reviewer and notes
        
    Returns:
        Updated request
    """
    success = approval_queue.reject_request(
        request_id=request_id,
        reviewer=decision.reviewer,
        notes=decision.notes
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Could not reject request (may be expired or already reviewed)"
        )
    
    request = approval_queue.get_request(request_id)
    return request.to_dict()


@router.get("/statistics")
async def get_statistics():
    """
    Get approval queue statistics.
    
    Returns:
        Queue statistics
    """
    stats = approval_queue.get_statistics()
    return stats


@router.delete("/cleanup")
async def cleanup_old_requests(days: int = Query(7, ge=1, le=30)):
    """
    Cleanup old completed requests.
    
    Args:
        days: Number of days to keep
        
    Returns:
        Number of requests removed
    """
    removed = approval_queue.cleanup_old_requests(days=days)
    return {
        "removed_count": removed,
        "message": f"Removed {removed} old requests"
    }
