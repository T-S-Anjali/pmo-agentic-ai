"""
Pydantic schemas for Orchestrator, LLM, Retrieval, and Validation (Task 4 Contracts).
"""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

# ── Deep-Agent Orchestrator (Section 8.3) ──────────────────────────────
class AgentRunRequest(BaseModel):
    workflow_id: str
    thread_id: str
    agent_name: str
    task_type: str
    input_context: dict[str, Any]
    expected_output_schema: str | None = None
    correlation_id: str | None = None

class AgentRunResponse(BaseModel):
    run_id: str
    status: str
    agent_name: str
    output_schema: str | None = None
    output: dict[str, Any]

# ── LLM Gateway (Section 7.4) ──────────────────────────────────────────
class LLMGenerateRequest(BaseModel):
    prompt: str
    system_message: str | None = None
    schema_name: str | None = None
    correlation_id: str | None = None

class LLMGenerateResponse(BaseModel):
    content: str
    parsed_output: dict[str, Any] | None = None

# ── Retrieval Service (Section 8.4) ────────────────────────────────────
class RetrievalSearchRequest(BaseModel):
    workflow_type: str
    query_type: str = "reference_context"
    query_text: str
    project_id: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None

class RetrievalResult(BaseModel):
    ref_id: str
    type: str
    title: str
    summary: str | None = None
    content_fragment: str | None = None
    score: float = 0.0

class RetrievalSearchResponse(BaseModel):
    results: list[RetrievalResult]
    result_count: int

# ── Rules and Validation (Section 8.5) ─────────────────────────────────
class ValidationEvaluateRequest(BaseModel):
    workflow_type: str
    artifact_type: str
    artifact: dict[str, Any]
    ruleset_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None

class ValidationFinding(BaseModel):
    rule_id: str
    severity: Literal["low", "medium", "high", "critical"]
    blocking: bool
    type: str
    message: str
    recommended_action: str | None = None

class ValidationSummary(BaseModel):
    blocking_count: int = 0
    warning_count: int = 0

class ValidationEvaluateResponse(BaseModel):
    validation_status: str
    findings: list[ValidationFinding]
    summary: ValidationSummary
