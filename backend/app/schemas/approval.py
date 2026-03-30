"""
Pydantic schemas for the approvals API.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecisionRequest(BaseModel):
    decision: Literal["approve", "reject", "request_changes", "edit_and_approve"]
    comments: str | None = None
    artifact_edits: dict | None = None
    actor: dict[str, str]  # user_id, role
    correlation_id: str | None = None


class ApprovalTaskCreateRequest(BaseModel):
    workflow_id: str
    thread_id: str
    task_type: str
    assigned_role: str
    assigned_user_id: str | None = None
    artifact_ref: dict[str, Any]
    allowed_actions: list[str] = ["approve", "reject", "request_changes"]
    due_at: datetime | None = None
    correlation_id: str | None = None


class ApprovalItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str = Field(alias="id")
    status: str
    workflow_id: str
    assigned_role: str | None = None
    allowed_actions: list[str] = []
    created_at: datetime
    resolved_at: datetime | None = None


class ApprovalListResponse(BaseModel):
    items: list[ApprovalItemResponse]
