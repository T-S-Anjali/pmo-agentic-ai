"""
PMO Shared Graph State — Foundation Task 2.

This TypedDict is the single source of truth for all state flowing
through LangGraph nodes. Per-workflow extensions should subclass or
extend via Annotated fields.
"""
from __future__ import annotations

from typing import Annotated, Any, Literal
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# ── User Context ──────────────────────────────────────────────────────
class UserContext(TypedDict):
    user_id: str
    role: str  # pm | pmo | exec | auditor
    display_name: str | None


# ── Validation Finding ────────────────────────────────────────────────
class ValidationFinding(TypedDict):
    rule_id: str
    rule_name: str
    severity: Literal["low", "medium", "high"]
    type: str  # missing_field | policy_violation | format_issue | consistency_issue
    blocking: bool
    message: str
    recommended_action: str | None


class ValidationSummary(TypedDict):
    status: Literal["pending", "pass", "warning", "fail"]
    blocking_count: int
    warning_count: int


# ── Timestamps ────────────────────────────────────────────────────────
class Timestamps(TypedDict):
    created_at: str  # ISO string
    updated_at: str
    last_checkpoint_at: str | None


# ── Shared Base State ─────────────────────────────────────────────────
class PMOGraphState(TypedDict):
    # Identity
    workflow_id: str
    thread_id: str
    workflow_type: str
    workflow_version: str
    graph_version: str
    project_id: str | None
    tenant_id: str | None
    correlation_id: str | None

    # User
    user_context: UserContext

    # Payload
    input_payload: dict[str, Any]
    normalized_input: dict[str, Any]

    # Context retrieved from vector store / source systems
    retrieved_context: list[dict[str, Any]]
    retrieval_refs: list[str]

    # Artifacts produced by generation nodes
    generated_artifacts: list[dict[str, Any]]
    artifact_refs: list[str]

    # Findings from the rules/validation engine
    validation_findings: list[ValidationFinding]
    validation_summary: ValidationSummary

    # Human-in-the-loop
    approval_status: Literal["pending", "under_review", "approved", "rejected", "needs_changes"]
    approval_history: list[dict[str, Any]]
    human_tasks: list[dict[str, Any]]
    interrupt_reason: str | None
    interrupt_context: dict[str, Any] | None

    # Routing
    current_node: str
    next_node_hint: str | None
    retry_count: int
    error_state: dict[str, Any] | None

    # Audit & Lifecycle
    audit_refs: list[str]
    event_log: list[dict[str, Any]]
    workflow_status: Literal[
        "initiated", "running", "waiting_for_human", "completed", "failed", "cancelled", "rejected"
    ]
    timestamps: Timestamps

    # LangGraph messages bus (append-only via add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Workflow-specific extensions
    extensions: dict[str, Any]


# ── Per-Workflow State Extensions (Legacy subclasses if needed for typing) ───

class CharterWorkflowState(PMOGraphState):
    """Extended state for project-intake-to-charter."""
    # Data now primarily lives in state['extensions']['charter']
    pass


class StatusReportWorkflowState(PMOGraphState):
    """Extended state for weekly status report workflow."""
    # Data now primarily lives in state['extensions']['status_report']
    pass


class RAIDWorkflowState(PMOGraphState):
    """Extended state for RAID update workflow."""
    # Data now primarily lives in state['extensions']['raid']
    pass


class TestingWorkflowState(PMOGraphState):
    """Extended state for functional test generation workflow (DeepAgents)."""
    # Data lives in state['extensions']['testing']:
    #   feature_description: str  — what to generate tests for
    #   filename: str             — desired pytest output filename
    #   agent_output: str | None  — full agent response
    #   saved_path: str | None    — path to saved .py file
    #   run_result: str | None    — pytest execution output
    pass
