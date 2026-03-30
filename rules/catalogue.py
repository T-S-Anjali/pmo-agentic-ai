"""
MVP Rules Catalogue — Foundation Task 6.

Each rule is a dict with:
    id            — unique rule identifier
    name          — human-readable name
    applies_to    — workflow_type or "all"
    artifact_type — "charter" | "status_report" | "raid_log" | "any"
    severity      — "low" | "medium" | "high"
    blocking      — True blocks approval, False emits a warning
    evaluate(artifact_content: dict) -> tuple[bool, str]
              — returns (passed, message)
"""
from __future__ import annotations

from typing import Any, Callable


# --- Evaluation Logic Helpers ---

def _charter_mandatory_field(field: str, label: str, rule_id: str) -> Callable:
    def eval_fn(content: dict[str, Any]) -> tuple[bool, str]:
        val = content.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            return False, f"Charter must include {label} ({rule_id})."
        if isinstance(val, list) and not val:
            return False, f"Charter must include {label} ({rule_id})."
        return True, ""
    return eval_fn

def _status_mandatory_field(field: str, label: str, rule_id: str) -> Callable:
    def eval_fn(content: dict[str, Any]) -> tuple[bool, str]:
        val = content.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            return False, f"Status report must include {label} ({rule_id})."
        return True, ""
    return eval_fn
def _status_rag_narrative_aligned(content: dict[str, Any]) -> tuple[bool, str]:
    rag = content.get("overall_rag", "").lower()
    narrative = content.get("narrative", "").lower()
    if rag == "red" and "blocker" not in narrative and "risk" not in narrative:
        return False, "Red RAG status must reference blockers or risks in narrative (R-015)."
    return True, ""

def _raid_high_risk_has_owner(content: dict[str, Any]) -> tuple[bool, str]:
    items = content if isinstance(content, list) else [content]
    for item in items:
        if item.get("category") == "risk" and item.get("severity") == "high" and not item.get("owner"):
            return False, f"High-severity risk '{item.get('title', '?')}' must have an owner (R-024)."
    return True, ""

# --- Rule Catalogue ---

RULE_CATALOGUE: list[dict[str, Any]] = [
    # 7.1 Charter Rules
    {
        "id": "R-001",
        "name": "Charter must include sponsor",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": _charter_mandatory_field("project_sponsor", "sponsor", "R-001"),
        "recommended_action": "Assign a project sponsor.",
        "action_on_failure": "block_approval",
        "requires_human_action": True
    },
    {
        "id": "R-002",
        "name": "Charter must include business purpose",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": _charter_mandatory_field("business_case", "business purpose", "R-002"),
        "recommended_action": "Define the business purpose/case.",
        "action_on_failure": "block_approval",
        "requires_human_action": True
    },
    {
        "id": "R-003",
        "name": "Charter must include objectives",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": _charter_mandatory_field("objectives", "objectives", "R-003"),
        "recommended_action": "List project objectives.",
        "action_on_failure": "block_approval",
        "requires_human_action": True
    },
    {
        "id": "R-004",
        "name": "Charter must define scope",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (bool(c.get("scope_in") or c.get("scope_out")), "Scope in/out must be defined (R-004)."),
        "recommended_action": "Define scope boundaries.",
        "action_on_failure": "return_for_correction",
        "requires_human_action": True
    },
    {
        "id": "R-005",
        "name": "Charter must include timeline baseline",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "medium",
        "blocking": False,
        "evaluate": _charter_mandatory_field("timeline", "timeline baseline", "R-005"),
        "recommended_action": "Add key milestones or dates.",
        "action_on_failure": "return_for_correction",
        "requires_human_action": True
    },
    {
        "id": "R-009",
        "name": "Charter cannot be published without PM review",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (c.get("pm_review_status") == "approved", "PM review record absent (R-009)."),
        "recommended_action": "Obtain PM approval.",
        "action_on_failure": "block_publish",
        "requires_human_action": True
    },

    # 7.2 Weekly Status Report Rules
    {
        "id": "R-013",
        "name": "Status report must include reporting period",
        "applies_to": "weekly_status_report",
        "applies_to_artifact": "status_report",
        "severity": "high",
        "blocking": True,
        "evaluate": _status_mandatory_field("reporting_period", "reporting period", "R-013"),
        "recommended_action": "Set the reporting period.",
        "action_on_failure": "block_publish",
        "requires_human_action": False
    },
    {
        "id": "R-014",
        "name": "Status report must include overall RAG status",
        "applies_to": "weekly_status_report",
        "applies_to_artifact": "status_report",
        "severity": "high",
        "blocking": True,
        "evaluate": _status_mandatory_field("overall_rag", "overall RAG status", "R-014"),
        "recommended_action": "Define overall RAG (Red/Amber/Green).",
        "action_on_failure": "return_for_correction",
        "requires_human_action": True
    },
    {
        "id": "R-015",
        "name": "RAG status must align with narrative",
        "applies_to": "weekly_status_report",
        "applies_to_artifact": "status_report",
        "severity": "medium",
        "blocking": False,
        "evaluate": _status_rag_narrative_aligned,
        "recommended_action": "Ensure narrative justifies the RAG status.",
        "action_on_failure": "return_for_correction",
        "requires_human_action": True
    },
    {
        "id": "R-006",
        "name": "Charter budget must be present if funded",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (not (c.get("funded_delivery") and not c.get("budget")), "Funded projects must specify a budget (R-006)."),
        "recommended_action": "Specify the project budget.",
        "action_on_failure": "block_approval",
        "requires_human_action": True
    },
    # ... placeholder additions for R-007, R-008, R-010, R-011, R-012, etc.
    {
        "id": "R-012",
        "name": "Charter final version must reference validation",
        "applies_to": "project_charter",
        "applies_to_artifact": "charter",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (c.get("validation_status") is not None, "Validation summary absent (R-012)."),
        "recommended_action": "Run validation before final record.",
        "action_on_failure": "block_publish",
        "requires_human_action": False
    },
    # 7.2 Remaining Status Rules
    {
        "id": "R-018",
        "name": "Executive summary required for leadership",
        "applies_to": "weekly_status_report",
        "applies_to_artifact": "status_report",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (not (c.get("audience") == "leadership" and not c.get("executive_summary")), "Executive summary missing for leadership report (R-018)."),
        "recommended_action": "Generate an executive summary.",
        "action_on_failure": "block_publish",
        "requires_human_action": True
    },
    # 7.3 RAID Rules
    {
        "id": "R-023",
        "name": "Every RAID item must have a category",
        "applies_to": "raid_log",
        "applies_to_artifact": "raid_log",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (all(item.get("category") for item in (c if isinstance(c, list) else [c])), "RAID items must have a category (R-023)."),
        "recommended_action": "Assign a category (Risk, Action, Issue, Dependency).",
        "action_on_failure": "return_for_correction",
        "requires_human_action": False
    },
    {
        "id": "R-024",
        "name": "High risk item must have mitigation owner",
        "applies_to": "raid_log",
        "applies_to_artifact": "raid_log",
        "severity": "high",
        "blocking": True,
        "evaluate": _raid_high_risk_has_owner,
        "recommended_action": "Assign a mitigation owner.",
        "action_on_failure": "block_publish",
        "requires_human_action": True
    },
    {
        "id": "R-025",
        "name": "High issue item must have resolution owner",
        "applies_to": "raid_log",
        "applies_to_artifact": "raid_log",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (all(not (item.get("category") == "issue" and item.get("severity") == "high" and not item.get("owner")) for item in (c if isinstance(c, list) else [c])), "High-severity issues must have an owner (R-025)."),
        "recommended_action": "Assign a resolution owner.",
        "action_on_failure": "block_publish",
        "requires_human_action": True
    },

    # 7.4 Cross-Workflow Governance Rules
    {
        "id": "R-033",
        "name": "Final business artifact must have validation record",
        "applies_to": "all",
        "applies_to_artifact": "any",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (c.get("validation_record_exists", True), "Final artifact missing validation record (R-033)."),
        "recommended_action": "Ensure the validation service has processed this artifact.",
        "action_on_failure": "block_publish",
        "requires_human_action": False
    },
    {
        "id": "R-034",
        "name": "Final business artifact must require human confirmation",
        "applies_to": "all",
        "applies_to_artifact": "any",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (c.get("requires_human_confirmation", True) is True, "requires_human_confirmation must be True (R-034)."),
        "recommended_action": "Enable the requires_human_confirmation flag.",
        "action_on_failure": "block_publish",
        "requires_human_action": False
    },
    {
        "id": "R-035",
        "name": "Workflow cannot complete with unresolved blocking findings",
        "applies_to": "all",
        "applies_to_artifact": "any",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (c.get("blocking_findings_count", 0) == 0, "Unresolved blocking findings (R-035)."),
        "recommended_action": "Resolve all blocking findings before completion.",
        "action_on_failure": "block_publish",
        "requires_human_action": False
    },
    {
        "id": "R-040",
        "name": "Workflow resume after approval must use open interrupt",
        "applies_to": "all",
        "applies_to_artifact": "any",
        "severity": "high",
        "blocking": True,
        "evaluate": lambda c: (not (c.get("workflow_status") == "terminal" and c.get("resume_requested")), "Cannot resume terminal workflow (R-040)."),
        "recommended_action": "Check workflow state before resume.",
        "action_on_failure": "block_approval",
        "requires_human_action": False
    },
]
