"""
Pydantic schemas for workflow request/response contracts.
"""
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Request Schemas ───────────────────────────────────────────────────

class UserContext(BaseModel):
    user_id: str
    role: str


class ClientContext(BaseModel):
    channel: str = "web"
    request_id: str | None = None


class WorkflowStartRequest(BaseModel):
    workflow_type: str
    project_id: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    user_context: UserContext
    client_context: ClientContext | None = None
    correlation_id: str | None = None


class WorkflowResumeRequest(BaseModel):
    resume_reason: str = "human_decision_applied"
    source_task_id: str | None = None
    actor: UserContext
    correlation_id: str | None = None
    # For backwards compatibility with internal logic
    comments: str | None = None
    corrections: dict[str, Any] | None = None


# ── Response Schemas ──────────────────────────────────────────────────

class WorkflowStartResponse(BaseModel):
    workflow_id: str
    thread_id: str
    workflow_type: str
    status: str
    current_step: str | None = None
    created_at: str | None = None


class WorkflowStatusResponse(BaseModel):
    model_config = {"from_attributes": True}

    workflow_id: str = Field(alias="id")
    workflow_type: str
    status: str
    approval_status: str | None = None
    current_step: str | None = None
    pending_task_id: str | None = None
    updated_at: Any
