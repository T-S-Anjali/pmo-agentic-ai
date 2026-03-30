"""
Rules Engine — Foundation Task 6.

Evaluates MVP PMO rules against generated artifacts.
"""
from __future__ import annotations

from typing import Any

import structlog

from rules.catalogue import RULE_CATALOGUE

logger = structlog.get_logger(__name__)


def evaluate_rules(
    artifact_type: str,
    artifacts: list[dict[str, Any]],
    workflow_type: str = "all",
) -> list[dict[str, Any]]:
    """
    Run all applicable rules for the given artifact and workflow type.
    Returns a list of results following the Section 9 output contract.
    """
    findings: list[dict[str, Any]] = []
    applicable_rules = [
        r for r in RULE_CATALOGUE
        if r["applies_to"] in (artifact_type, workflow_type, "all")
    ]
    
    for rule in applicable_rules:
        for artifact in artifacts:
            # Match artifact type or 'any'
            if rule.get("applies_to_artifact") not in (artifact.get("type"), "any"):
                continue
                
            try:
                passed, message = rule["evaluate"](artifact.get("content", {}))
            except Exception as exc:
                logger.exception("Rule evaluation error", rule_id=rule["id"], exc=str(exc))
                passed, message = False, f"Rule evaluation error: {exc}"

            if not passed:
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "applies_to": rule["applies_to_artifact"],
                    "result": "fail",
                    "severity": rule["severity"],
                    "blocking": rule["blocking"],
                    "message": message,
                    "recommended_action": rule.get("recommended_action", "Check PMO guidelines."),
                    "action_on_failure": rule.get("action_on_failure", "return_for_correction"),
                    "requires_human_action": rule.get("requires_human_action", True)
                })

    return findings
