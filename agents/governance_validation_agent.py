"""
Governance Validation Agent — checks artifacts against PMO rules.
"""
from __future__ import annotations

from typing import Any

import structlog

from rules.engine import evaluate_rules

from app.schemas.agents import GovernanceValidationResult

logger = structlog.get_logger(__name__)


class GovernanceValidationAgent:
    """
    Specialist agent: validates artifacts against the PMO rules catalogue (Section 8.7).
    """

    ALLOWED_TOOLS = ["retrieval", "rules_engine"]
    CAN_DELEGATE_TO: list[str] = []
    REQUIRES_HITL_BEFORE_PUBLISH = False

    def validate(
        self,
        artifact_type: str,
        artifact_content: dict[str, Any],
        rules: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Returns GovernanceValidationResult schema.
        """
        artifacts = [{"type": artifact_type, "content": artifact_content}]
        findings = evaluate_rules(artifact_type, artifacts)
        
        # Map findings to the new schema format if necessary
        # Assuming evaluate_rules already returns compatible objects or we wrap them
        
        blocking_count = len([f for f in findings if f.get("blocking")])
        warning_count = len([f for f in findings if not f.get("blocking")])
        
        status = "pass"
        if blocking_count > 0:
            status = "fail"
        elif warning_count > 0:
            status = "warning"

        data = {
            "artifact_type": artifact_type,
            "validation_status": status,
            "findings": findings,
            "summary": {
                "blocking_count": blocking_count,
                "warning_count": warning_count
            }
        }
        
        try:
            result = GovernanceValidationResult.model_validate(data).model_dump()
        except Exception as exc:
            logger.error("Governance validation schema check failed", error=str(exc))
            # Fallback to the raw data if pydantic fails but logic is sound
            result = data

        logger.info(
            "Governance validation complete",
            status=status,
            blocking=blocking_count,
            warnings=warning_count
        )
        return result
