"""
Workflow service — orchestrates DB operations and graph execution.
"""
from __future__ import annotations

from typing import Any

import uuid
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import WorkflowInstance, WorkflowStatus
from app.schemas.workflow import WorkflowResumeRequest, WorkflowStartRequest

logger = structlog.get_logger(__name__)


class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow_instance(
        self, request: WorkflowStartRequest, thread_id: str
    ) -> str:
        instance = WorkflowInstance(
            thread_id=thread_id,
            workflow_type=request.workflow_type,
            project_id=request.project_id,
            input_payload=request.input_payload,
            user_id=request.user_context.user_id,
            user_role=request.user_context.role,
            status=WorkflowStatus.RUNNING,
            correlation_id=request.correlation_id or f"corr_{uuid.uuid4()}",
        )
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance.id

    async def get_workflow(self, workflow_id: str) -> WorkflowInstance | None:
        result = await self.db.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def get_workflow_state(self, workflow_id: str) -> dict[str, Any]:
        """Get internal state snapshot from checkpointer (Section 7.2)."""
        instance = await self.get_workflow(workflow_id)
        if not instance:
             return {}
        from graph_runtime.graph import get_graph
        graph = get_graph(instance.workflow_type)
        config = {"configurable": {"thread_id": instance.thread_id}}
        state = await graph.aget_state(config)
        return state.values

    async def run_workflow(
        self,
        workflow_id: str,
        thread_id: str,
        request: WorkflowStartRequest,
    ) -> None:
        """Execute the LangGraph workflow asynchronously."""
        from graph_runtime.graph import get_graph
        graph = get_graph(request.workflow_type)
        from datetime import datetime
        
        correlation_id = request.correlation_id or f"corr_{uuid.uuid4()}"
        
        initial_state: dict[str, Any] = {
            "workflow_id": workflow_id,
            "thread_id": thread_id,
            "workflow_type": request.workflow_type,
            "workflow_version": "1.0.0",
            "graph_version": "1.0.0",
            "project_id": request.project_id,
            "tenant_id": None,
            "correlation_id": correlation_id,
            "user_context": {
                "user_id": request.user_context.user_id,
                "role": request.user_context.role,
                "display_name": None
            },
            "input_payload": request.input_payload,
            "normalized_input": {},
            "retrieved_context": [],
            "retrieval_refs": [],
            "generated_artifacts": [],
            "artifact_refs": [],
            "validation_findings": [],
            "validation_summary": {
                "status": "pending",
                "blocking_count": 0,
                "warning_count": 0
            },
            "approval_status": "pending",
            "approval_history": [],
            "human_tasks": [],
            "interrupt_reason": None,
            "interrupt_context": None,
            "current_node": "start",
            "next_node_hint": None,
            "retry_count": 0,
            "error_state": None,
            "audit_refs": [],
            "event_log": [],
            "workflow_status": "initiated",
            "timestamps": {
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_checkpoint_at": None
            },
            "messages": [],
            "extensions": {},
        }
        config = {"configurable": {"thread_id": thread_id}}
        try:
            async for _ in graph.astream(initial_state, config):
                pass
            await self._update_status(workflow_id, WorkflowStatus.COMPLETED)
        except Exception as exc:
            logger.exception("Workflow execution failed", workflow_id=workflow_id, correlation_id=correlation_id, exc=str(exc))
            await self._update_status(workflow_id, WorkflowStatus.FAILED)

    async def resume_workflow(
        self,
        workflow_id: str,
        request: WorkflowResumeRequest,
    ) -> None:
        """Resume a paused workflow after human review (Section 8.8)."""
        from graph_runtime.graph import get_graph
        instance = await self.get_workflow(workflow_id)
        if not instance:
            raise ValueError(f"Workflow {workflow_id} not found")
        graph = get_graph(instance.workflow_type)
        
        # Backward compatibility with old corrections/comments if strictly needed
        corrections = request.corrections or {}
        
        resume_state = {
            "approval_status": "approved", # Default if resumed? Usually depends on task decision
            "approval_history": [{"decision": request.resume_reason, "actor": request.actor.user_id}],
            "interrupt_context": {"corrections": corrections, "reason": request.resume_reason},
            "correlation_id": request.correlation_id,
        }
        config = {"configurable": {"thread_id": instance.thread_id}}
        try:
            async for _ in graph.astream(resume_state, config):
                pass
        except Exception as exc:
            logger.exception("Workflow resume failed", workflow_id=workflow_id, correlation_id=request.correlation_id, exc=str(exc))

    async def cancel_workflow(self, workflow_id: str) -> None:
        await self._update_status(workflow_id, WorkflowStatus.FAILED)

    async def _update_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        instance = await self.get_workflow(workflow_id)
        if instance:
            instance.status = status
            await self.db.commit()
