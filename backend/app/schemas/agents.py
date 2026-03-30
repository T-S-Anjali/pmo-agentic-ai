from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

# ── Base Agent Output ──────────────────────────────────────────────────
class BaseAgentOutput(BaseModel):
    artifact_type: str
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"
    requires_human_confirmation: bool = True

# ── Supervisor Decision ────────────────────────────────────────────────
class SupervisorDecision(BaseModel):
    selected_action: Literal["delegate", "validate", "revise", "interrupt", "complete", "fallback"]
    selected_agent: str | None = None
    reason: str
    inputs_required: list[str] = Field(default_factory=list)
    expected_output_schema: str | None = None
    next_step_hint: str | None = None

# ── Project Charter Draft ──────────────────────────────────────────────
class CharterTimeline(BaseModel):
    start: str
    end: str

class CharterBudget(BaseModel):
    amount: float
    currency: str

class CharterContent(BaseModel):
    title: str
    sponsor: str
    business_purpose: str
    objectives: list[str]
    scope_in: list[str]
    scope_out: list[str]
    timeline: CharterTimeline
    budget: CharterBudget
    stakeholders: list[str]

class ProjectCharterDraft(BaseAgentOutput):
    artifact_type: Literal["project_charter_draft"] = "project_charter_draft"
    draft_version: int = 1
    content: CharterContent

# ── Weekly Status Report ───────────────────────────────────────────────
class StatusRisk(BaseModel):
    title: str
    severity: Literal["low", "medium", "high"]
    owner: str

class StatusIssue(BaseModel):
    title: str
    severity: Literal["low", "medium", "high"]
    owner: str

class WeeklyStatusReport(BaseAgentOutput):
    artifact_type: Literal["weekly_status_report"] = "weekly_status_report"
    reporting_period: str
    overall_rag: Literal["green", "amber", "red"]
    summary: str
    milestone_updates: list[str] = Field(default_factory=list)
    risks: list[StatusRisk] = Field(default_factory=list)
    issues: list[StatusIssue] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

# ── Executive Summary ─────────────────────────────────────────────────
class ExecutiveSummary(BaseAgentOutput):
    artifact_type: Literal["executive_summary"] = "executive_summary"
    reporting_period: str
    summary: str
    top_concerns: list[str] = Field(default_factory=list)
    decisions_required: list[str] = Field(default_factory=list)

# ── RAID Candidates ───────────────────────────────────────────────────
class RAIDCandidateItem(BaseModel):
    category: Literal["risk", "assumption", "issue", "dependency", "unknown"]
    title: str
    description: str
    evidence: str
    owner: str | None = None
    severity: Literal["low", "medium", "high", "unknown"]

class RAIDCandidates(BaseAgentOutput):
    artifact_type: Literal["raid_candidates"] = "raid_candidates"
    items: list[RAIDCandidateItem]
    unresolved_items: list[str] = Field(default_factory=list)

# ── RAID Merge Recommendation ──────────────────────────────────────────
class RAIDUpdateItem(BaseModel):
    existing_item_id: str
    recommended_changes: dict[str, Any]
    reason: str

class RAIDDuplicateMatch(BaseModel):
    candidate_title: str
    existing_item_id: str
    reason: str

class RAIDMergeRecommendation(BaseAgentOutput):
    artifact_type: Literal["raid_merge_recommendation"] = "raid_merge_recommendation"
    new_items: list[dict[str, Any]]
    updated_items: list[RAIDUpdateItem]
    duplicate_matches: list[RAIDDuplicateMatch]

# ── Governance Validation Result ───────────────────────────────────────
class ValidationFinding(BaseModel):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    type: Literal["missing_field", "policy_violation", "format_issue", "consistency_issue"]
    message: str
    recommended_action: str
    blocking: bool

class ValidationSummary(BaseModel):
    blocking_count: int
    warning_count: int

class GovernanceValidationResult(BaseModel):
    artifact_type: str
    validation_status: Literal["pass", "warning", "fail"]
    findings: list[ValidationFinding]
    summary: ValidationSummary

# ── Artifact Critique Result ──────────────────────────────────────────
class CritiqueFinding(BaseModel):
    dimension: Literal["clarity", "completeness", "consistency", "tone", "structure"]
    message: str
    recommended_revision: str

class ArtifactCritiqueResult(BaseModel):
    artifact_type: Literal["critique_result"] = "critique_result"
    readiness: Literal["ready", "revise"]
    quality_score: float
    findings: list[CritiqueFinding]

# ── Data Completeness Result ───────────────────────────────────────────
class DataCompletenessResult(BaseModel):
    status: Literal["sufficient", "insufficient", "ambiguous"]
    missing_fields: list[str] = Field(default_factory=list)
    ambiguous_fields: list[str] = Field(default_factory=list)
    recommended_next_action: Literal["continue", "request_input", "manual_review"]
