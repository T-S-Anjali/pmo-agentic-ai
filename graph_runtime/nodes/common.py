"""
Common (Shared) Workflow Nodes — Foundation Task 2 & 3.
"""
from __future__ import annotations

from typing import Any
import structlog
from datetime import datetime
from langchain_core.messages import AIMessage

from graph_runtime.state import PMOGraphState

logger = structlog.get_logger(__name__)


def ingest_request(state: PMOGraphState) -> dict[str, Any]:
    """Accept initial API/UI payload and initialize runtime state."""
    logger.info("Ingesting request", workflow_type=state.get("workflow_type"))
    return {
        "workflow_status": "running",
        "approval_status": "pending",
        "current_node": "ingest_request",
        "timestamps": {
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_checkpoint_at": datetime.utcnow().isoformat()
        }
    }


def normalize_input(state: PMOGraphState) -> dict[str, Any]:
    """Map input fields into normalized internal format."""
    payload = state.get("input_payload", {})
    # Simple normalization for MVP
    normalized = {k.lower(): v for k, v in payload.items()}
    return {
        "normalized_input": normalized,
        "current_node": "normalize_input"
    }


def initialize_workflow_metadata(state: PMOGraphState) -> dict[str, Any]:
    """Set correlation IDs and other metadata."""
    return {
        "correlation_id": state.get("correlation_id") or f"corr_{datetime.utcnow().timestamp()}",
        "current_node": "initialize_workflow_metadata"
    }


def write_audit_record(state: PMOGraphState) -> dict[str, Any]:
    """Write approval, version, and trace events."""
    event = {
        "event_type": "node_completed",
        "node": state.get("current_node"),
        "timestamp": datetime.utcnow().isoformat(),
        "actor": "system"
    }
    return {
        "event_log": state.get("event_log", []) + [event],
        "current_node": "write_audit_record"
    }


def complete_workflow(state: PMOGraphState) -> dict[str, Any]:
    """Mark workflow terminal."""
    logger.info("Workflow completed", workflow_id=state.get("workflow_id"))
    return {
        "workflow_status": "completed",
        "approval_status": "approved",
        "current_node": "complete_workflow"
    }


def capture_error(state: PMOGraphState) -> dict[str, Any]:
    """Capture error state for recovery or failure."""
    return {
        "workflow_status": "failed",
        "current_node": "capture_error"
    }
