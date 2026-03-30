"""
Status Report Workflow Nodes — Foundation Task 2.
Implements the 5-step path for Weekly Status Reporting.
"""
from __future__ import annotations

from typing import Any
import structlog

from graph_runtime.state import StatusReportWorkflowState
from agents.status_summary_agent import StatusSummaryAgent
from agents.executive_summary_agent import ExecutiveSummaryAgent
from agents.artifact_critique_agent import ArtifactCritiqueAgent

logger = structlog.get_logger(__name__)


def generate_status_narrative(state: StatusReportWorkflowState) -> dict[str, Any]:
    """Generate detailed status report content."""
    agent = StatusSummaryAgent()
    result = agent.generate(
        project_data=state.get("normalized_input", {}),
        reporting_period=state.get("extensions", {}).get("status_report", {}).get("period", "Current Week")
    )
    return {
        "generated_artifacts": state.get("generated_artifacts", []) + [result],
        "current_node": "generate_status_narrative"
    }


def generate_executive_summary(state: StatusReportWorkflowState) -> dict[str, Any]:
    """Generate leadership summary from narrative."""
    last_artifact = state.get("generated_artifacts", [])[-1]
    agent = ExecutiveSummaryAgent()
    result = agent.generate(
        status_narrative=last_artifact.get("summary", ""),
        health_indicators={"rag": last_artifact.get("overall_rag")},
        escalations=last_artifact.get("issues", [])
    )
    return {
        "generated_artifacts": state.get("generated_artifacts", []) + [result],
        "current_node": "generate_executive_summary"
    }


def critique_status_artifact(state: StatusReportWorkflowState) -> dict[str, Any]:
    """Quality review for the status report."""
    last_artifact = state.get("generated_artifacts", [])[-1]
    agent = ArtifactCritiqueAgent()
    result = agent.critique(
        artifact_type=last_artifact.get("artifact_type", "status_report"),
        content=last_artifact
    )
    return {
        "validation_findings": state.get("validation_findings", []) + result.get("findings", []),
        "validation_summary": {
            "blocking_count": 1 if result.get("readiness") == "revise" else 0,
            "warning_count": 0
        },
        "current_node": "critique_status_artifact"
    }
