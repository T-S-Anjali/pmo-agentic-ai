"""
Charter Workflow Nodes — Foundation Task 2.
Implements the 21-node execution path for Project Intake → Charter Generation.
"""
from __future__ import annotations

from typing import Any
import structlog
from langchain_core.messages import AIMessage

from graph_runtime.state import CharterWorkflowState
from agents.charter_draft_agent import CharterDraftAgent
from agents.data_completeness_agent import DataCompletenessAgent
from agents.governance_validation_agent import GovernanceValidationAgent
from agents.artifact_critique_agent import ArtifactCritiqueAgent

logger = structlog.get_logger(__name__)


def classify_intake(state: CharterWorkflowState) -> dict[str, Any]:
    """Classify request type and determine template path."""
    # Placeholder for LLM classification logic
    classification = "standard_project"
    return {
        "extensions": {
            **state.get("extensions", {}),
            "intake": {"classification": classification}
        },
        "current_node": "classify_intake"
    }


def retrieve_charter_template(state: CharterWorkflowState) -> dict[str, Any]:
    """Fetch the applicable charter template."""
    return {
        "retrieved_context": state.get("retrieved_context", []) + [{"type": "template", "id": "tmpl_standard"}],
        "current_node": "retrieve_charter_template"
    }


def retrieve_governance_rules(state: CharterWorkflowState) -> dict[str, Any]:
    """Fetch PMO governance and mandatory checks."""
    return {
        "retrieved_context": state.get("retrieved_context", []) + [{"type": "rules", "id": "gov_v1"}],
        "current_node": "retrieve_governance_rules"
    }


def draft_charter(state: CharterWorkflowState) -> dict[str, Any]:
    """Generate initial charter draft."""
    agent = CharterDraftAgent()
    draft = agent.generate(
        input_payload=state.get("normalized_input", {}),
        template_context="Standard Charter Template Content...",
    )
    return {
        "generated_artifacts": state.get("generated_artifacts", []) + [draft],
        "current_node": "draft_charter"
    }


def validate_required_fields(state: CharterWorkflowState) -> dict[str, Any]:
    """Ensure mandatory charter sections are present."""
    agent = DataCompletenessAgent()
    check = agent.check(
        input_data=state.get("generated_artifacts", [])[-1].get("content", {}),
        required_fields=["title", "sponsor", "business_purpose"]
    )
    return {
        "validation_findings": state.get("validation_findings", []) + [{"rule_id": "REQ-1", "message": f"Completeness: {check['status']}"}],
        "current_node": "validate_required_fields"
    }


def validate_policy_compliance(state: CharterWorkflowState) -> dict[str, Any]:
    """Check governance and template compliance."""
    agent = GovernanceValidationAgent()
    result = agent.validate(
        artifact_type="project_charter_draft",
        artifact_content=state.get("generated_artifacts", [])[-1]
    )
    return {
        "validation_findings": state.get("validation_findings", []) + result.get("findings", []),
        "validation_summary": result.get("summary"),
        "current_node": "validate_policy_compliance"
    }


def route_after_validation(state: CharterWorkflowState) -> str:
    """Determine next path based on validation results."""
    summary = state.get("validation_summary", {})
    if summary.get("blocking_count", 0) > 0:
        return "rework_needed"
    return "pm_review"


def critique_charter_artifact(state: CharterWorkflowState) -> dict[str, Any]:
    """Quality review for the project charter."""
    last_artifact = state.get("generated_artifacts", [])[-1]
    agent = ArtifactCritiqueAgent()
    result = agent.critique(
        artifact_type="project_charter_draft",
        content=last_artifact
    )
    return {
        "validation_findings": state.get("validation_findings", []) + result.get("findings", []),
        "validation_summary": {
            "blocking_count": 1 if result.get("readiness") == "revise" else 0,
            "warning_count": 0
        },
        "current_node": "critique_charter_artifact"
    }


def create_pm_review_task(state: CharterWorkflowState) -> dict[str, Any]:
    """Create human review task for PM."""
    task = {
        "task_id": "task_pm_review_1",
        "task_type": "pm_review",
        "status": "open"
    }
    return {
        "human_tasks": state.get("human_tasks", []) + [task],
        "current_node": "create_pm_review_task"
    }
