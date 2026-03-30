"""
Conditional edge routing functions shared across all PMO graphs.
"""
from typing import Literal

from graph_runtime.state import PMOGraphState


def route_after_validation(
    state: PMOGraphState,
) -> Literal["pass", "fail", "error"]:
    """
    Section 15.1 transition logic.
    """
    summary = state.get("validation_summary", {})
    blocking = summary.get("blocking_count", 0)
    
    if blocking > 0:
        retry = state.get("retry_count", 0)
        if retry >= 3:
            return "error"
        return "fail"
    return "pass"


def route_after_pm_review(
    state: PMOGraphState,
) -> Literal["approved", "rejected", "needs_changes"]:
    """Section 15.2 transition logic."""
    status = state.get("approval_status", "pending")
    if status == "approved":
        return "approved"
    if status == "rejected":
        return "rejected"
    if status == "needs_changes":
        return "needs_changes"
    return "approved" # Default to approved for MVP if not specified? 
