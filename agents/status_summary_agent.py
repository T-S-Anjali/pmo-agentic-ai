"""
Status Summary Agent — generates status narrative and exec summary.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt

from app.schemas.agents import WeeklyStatusReport

logger = structlog.get_logger(__name__)


class StatusSummaryAgent:
    """
    Specialist agent: generates weekly status reports (Section 8.3).
    """

    ALLOWED_TOOLS = ["retrieval", "llm"]
    CAN_DELEGATE_TO = ["artifact_critique_agent", "governance_validation_agent"]
    REQUIRES_HITL_BEFORE_PUBLISH = True

    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.system_prompt = load_prompt("status_summary_system")

    def generate(
        self,
        project_data: dict[str, Any],
        reporting_period: str,
        prior_report: dict | None = None,
    ) -> dict[str, Any]:
        """
        Generate status report. Returns WeeklyStatusReport schema.
        """
        user_prompt = f"Create a weekly project status summary.\n[INPUT]\nproject_context: {json.dumps(project_data)}\nreporting_period: {reporting_period}\nprior_status_summary: {json.dumps(prior_report)}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            report = WeeklyStatusReport.model_validate_json(response.content)
            result = report.model_dump()
        except Exception as exc:
            logger.error("Status report failed validation", error=str(exc))
            result = {
                "artifact_type": "weekly_status_report",
                "reporting_period": reporting_period,
                "overall_rag": "amber",
                "summary": f"Validation Error: {str(exc)}",
                "milestone_updates": [],
                "risks": [],
                "issues": [],
                "dependencies": [],
                "assumptions": [f"Validation failed for: {response.content[:200]}..."],
                "confidence": "low",
                "requires_human_confirmation": True
            }
        
        logger.info("Status summary generated")
        return result
