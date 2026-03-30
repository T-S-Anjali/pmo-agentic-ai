"""
Workflow router — start, status, resume, cancel.
"""
import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.workflow import (
    WorkflowResumeRequest,
    WorkflowStartRequest,
    WorkflowStartResponse,
    WorkflowStatusResponse,
)
from app.services.workflow_service import WorkflowService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/start", response_model=WorkflowStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_workflow(
    body: WorkflowStartRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Start a new workflow (Section 7.2)."""
    thread_id = str(uuid.uuid4())
    svc = WorkflowService(db)
    
    # Use correlation_id if provided, else generate
    correlation_id = body.correlation_id or f"corr_{uuid.uuid4()}"
    
    workflow_id = await svc.create_workflow_instance(body, thread_id)
    
    from app.db.session import AsyncSessionLocal
    async def run_in_background():
        async with AsyncSessionLocal() as fresh_db:
            new_svc = WorkflowService(fresh_db)
            await new_svc.run_workflow(workflow_id, thread_id, body)

    background_tasks.add_task(run_in_background)
    
    return WorkflowStartResponse(
        workflow_id=workflow_id,
        thread_id=thread_id,
        workflow_type=body.workflow_type,
        status="running",
        current_step="normalize_input"
    )


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get summarized status (Section 7.2)."""
    svc = WorkflowService(db)
    record = await svc.get_workflow(workflow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowStatusResponse.model_validate(record)


@router.get("/{workflow_id}/state")
async def get_workflow_state(
    workflow_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get internal state snapshot (Section 7.2)."""
    svc = WorkflowService(db)
    state = await svc.get_workflow_state(workflow_id)
    return state


@router.post("/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    body: WorkflowResumeRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resume workflow from interrupt (Section 7.2)."""
    svc = WorkflowService(db)
    background_tasks.add_task(svc.resume_workflow, workflow_id, body)
    return {
        "workflow_id": workflow_id,
        "status": "resuming",
        "correlation_id": body.correlation_id
    }
