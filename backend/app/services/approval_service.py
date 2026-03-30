"""
Approval service — list pending and submit decisions.
"""
from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApprovalRecord, ApprovalStatus, WorkflowInstance, WorkflowStatus
from app.schemas.approval import ApprovalDecisionRequest

logger = structlog.get_logger(__name__)


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_pending(self, reviewer_id: str) -> list[ApprovalRecord]:
        result = await self.db.execute(
            select(ApprovalRecord).where(
                ApprovalRecord.reviewer_id == reviewer_id,
                ApprovalRecord.status == ApprovalStatus.PENDING,
            )
        )
        return list(result.scalars().all())

    async def get_task(self, task_id: str) -> ApprovalRecord:
        result = await self.db.execute(
            select(ApprovalRecord).where(ApprovalRecord.id == task_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError(f"Task {task_id} not found")
        return record

    async def submit_decision(self, task_id: str, request: ApprovalDecisionRequest) -> None:
        record = await self.get_task(task_id)

        # Map new decision types to DB status
        if request.decision in ["approve", "edit_and_approve"]:
            record.status = ApprovalStatus.APPROVED
        elif request.decision == "reject":
            record.status = ApprovalStatus.REJECTED
        elif request.decision == "request_changes":
             record.status = ApprovalStatus.PENDING # Or a new 'rework' status if modeled

        record.reviewer_id = request.actor.get("user_id")
        record.comments = request.comments
        record.resolved_at = datetime.utcnow()
        record.correlation_id = request.correlation_id

        # Update workflow instance status if strictly rejected
        if request.decision == "reject":
            wf_result = await self.db.execute(
                select(WorkflowInstance).where(WorkflowInstance.id == record.workflow_id)
            )
            wf = wf_result.scalar_one_or_none()
            if wf:
                wf.status = WorkflowStatus.REJECTED

        await self.db.commit()
        logger.info("Approval decision recorded", task_id=task_id, decision=request.decision, correlation_id=request.correlation_id)
