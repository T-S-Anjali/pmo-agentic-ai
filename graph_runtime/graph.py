"""
LangGraph graph builder for all PMO workflows.

Each workflow is assembled from shared nodes + workflow-specific nodes.
Human-in-the-loop checkpoints are implemented via interrupt_before on
the review nodes so LangGraph pauses execution and waits for resume.
"""
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from graph_runtime.state import (
    CharterWorkflowState,
    PMOGraphState,
    RAIDWorkflowState,
    StatusReportWorkflowState,
)
from graph_runtime.nodes import (
    charter as charter_nodes,
    common as common_nodes,
    raid as raid_nodes,
    status_report as status_nodes,
)
from graph_runtime.edges import route_after_validation, route_after_pm_review


# ── Shared checkpointer (swap with PostgresSaver in production) ───────
checkpointer = MemorySaver()


# ─────────────────────────────────────────────────────────────────────
# Workflow 1 — Project Intake to Charter
# ─────────────────────────────────────────────────────────────────────
def build_charter_graph():
    g = StateGraph(CharterWorkflowState)

    # Nodes
    g.add_node("ingest_request",              common_nodes.ingest_request)
    g.add_node("normalize_input",             common_nodes.normalize_input)
    g.add_node("classify_intake",             charter_nodes.classify_intake)
    g.add_node("retrieve_charter_template",   charter_nodes.retrieve_charter_template)
    g.add_node("retrieve_governance_rules",   charter_nodes.retrieve_governance_rules)
    g.add_node("draft_charter",               charter_nodes.draft_charter)
    g.add_node("critique_charter",            charter_nodes.critique_charter_artifact)
    g.add_node("validate_required_fields",    charter_nodes.validate_required_fields)
    g.add_node("validate_policy_compliance",   charter_nodes.validate_policy_compliance)
    g.add_node("create_pm_review_task",       charter_nodes.create_pm_review_task)
    g.add_node("complete_workflow",           common_nodes.complete_workflow)
    g.add_node("capture_error",               common_nodes.capture_error)

    # Edges
    g.add_edge(START, "ingest_request")
    g.add_edge("ingest_request", "normalize_input")
    g.add_edge("normalize_input", "classify_intake")
    g.add_edge("classify_intake", "retrieve_charter_template")
    g.add_edge("retrieve_charter_template", "retrieve_governance_rules")
    g.add_edge("retrieve_governance_rules", "draft_charter")
    g.add_edge("draft_charter", "critique_charter")
    
    g.add_conditional_edges("critique_charter", route_after_validation, {
        "pass": "validate_required_fields",
        "fail": "draft_charter",
        "error": "capture_error",
    })

    g.add_edge("validate_required_fields", "validate_policy_compliance")

    g.add_conditional_edges("validate_policy_compliance", route_after_validation, {
        "pass": "create_pm_review_task",
        "fail": "draft_charter",
        "error": "capture_error",
    })

    g.add_edge("create_pm_review_task", "complete_workflow")
    g.add_edge("complete_workflow", END)
    g.add_edge("capture_error", END)

    return g.compile(
        checkpointer=checkpointer,
        interrupt_before=["create_pm_review_task"],
    )


def build_status_report_graph():
    g = StateGraph(StatusReportWorkflowState)

    g.add_node("ingest_request",              common_nodes.ingest_request)
    g.add_node("generate_narrative",          status_nodes.generate_status_narrative)
    g.add_node("critique_status",             status_nodes.critique_status_artifact)
    g.add_node("generate_executive_summary",  status_nodes.generate_executive_summary)
    g.add_node("complete_workflow",           common_nodes.complete_workflow)
    g.add_node("capture_error",               common_nodes.capture_error)

    g.add_edge(START, "ingest_request")
    g.add_edge("ingest_request", "generate_narrative")
    g.add_edge("generate_narrative", "critique_status")

    g.add_conditional_edges("critique_status", route_after_validation, {
        "pass": "generate_executive_summary",
        "fail": "generate_narrative",
        "error": "capture_error",
    })

    g.add_edge("generate_executive_summary", "complete_workflow")
    g.add_edge("complete_workflow", END)
    g.add_edge("capture_error", END)

    return g.compile(
        checkpointer=checkpointer,
        interrupt_before=["complete_workflow"],
    )


# ── Workflow 3 — RAID Update from Meeting Notes
# ─────────────────────────────────────────────────────────────────────
def build_raid_graph():
    g = StateGraph(RAIDWorkflowState)

    g.add_node("ingest_request",      common_nodes.ingest_request)
    g.add_node("extract_raid_items",   raid_nodes.extract_raid_items)
    g.add_node("classify_and_merge",   raid_nodes.classify_and_merge_raid)
    g.add_node("validate_raid_log",    raid_nodes.validate_raid_log)
    g.add_node("complete_workflow",    common_nodes.complete_workflow)
    g.add_node("capture_error",        common_nodes.capture_error)

    g.add_edge(START, "ingest_request")
    g.add_edge("ingest_request", "extract_raid_items")
    g.add_edge("extract_raid_items", "classify_and_merge")
    g.add_edge("classify_and_merge", "validate_raid_log")

    g.add_conditional_edges("validate_raid_log", route_after_validation, {
        "pass": "complete_workflow",
        "fail": "extract_raid_items",
        "error": "capture_error",
    })

    g.add_edge("complete_workflow", END)
    g.add_edge("capture_error", END)

    return g.compile(
        checkpointer=checkpointer,
        interrupt_before=["complete_workflow"],
    )


# ── Graph Registry ────────────────────────────────────────────────────
GRAPH_REGISTRY = {
    "project_intake_to_charter": build_charter_graph,
    "weekly_status_report":      build_status_report_graph,
    "raid_update":               build_raid_graph,
}


def get_graph(workflow_type: str):
    builder = GRAPH_REGISTRY.get(workflow_type)
    if not builder:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    return builder()
