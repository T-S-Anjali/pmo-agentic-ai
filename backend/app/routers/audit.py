"""
Audit router — retrieve audit trail for a workflow.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/workflows/{workflow_id}")
async def get_audit_trail(
    workflow_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get audit trail for workflow (Section 7.8)."""
    svc = AuditService(db)
    events = await svc.get_events(workflow_id)
    return {"workflow_id": workflow_id, "events": events}


@router.get("/correlation/{correlation_id}")
async def get_correlation_trace(
    correlation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get cross-service trace view (Section 7.8)."""
    svc = AuditService(db)
    # Placeholder for correlation search logic
    return {"correlation_id": correlation_id, "events": []}
