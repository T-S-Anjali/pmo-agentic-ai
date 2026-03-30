"""
Approvals router — list pending approvals, submit decision.
"""
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.approval import ApprovalDecisionRequest, ApprovalListResponse, ApprovalItemResponse
from app.services.approval_service import ApprovalService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/tasks", response_model=ApprovalListResponse)
async def list_approval_tasks(
    assigned_role: str | None = None,
    assigned_user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List approval tasks (Section 7.7)."""
    svc = ApprovalService(db)
    # Search logic should handle role/user filtering
    items = await svc.list_pending(assigned_user_id or assigned_role)
    return ApprovalListResponse(items=items)


@router.get("/tasks/{task_id}", response_model=ApprovalItemResponse)
async def get_approval_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get task detail (Section 7.7)."""
    svc = ApprovalService(db)
    item = await svc.get_task(task_id)
    return item


@router.post("/tasks/{task_id}/decision")
async def submit_approval_decision(
    task_id: str,
    body: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit approval decision (Section 7.7)."""
    svc = ApprovalService(db)
    await svc.submit_decision(task_id, body)
    return {
        "task_id": task_id,
        "status": "completed",
        "decision": body.decision,
        "resume_required": True
    }
