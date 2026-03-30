"""
Executive Summary Agent — Foundation Task 3.
Generates concise leadership-oriented messaging from project status items.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from prompts.loader import load_prompt
from app.schemas.agents import ExecutiveSummary

logger = structlog.get_logger(__name__)


class ExecutiveSummaryAgent:
    """
    Specialist agent: generates leadership executive summaries (Section 8.4).
    """

    ALLOWED_TOOLS = ["llm"]
    CAN_DELEGATE_TO = ["governance_validation_agent"]
    REQUIRES_HITL_BEFORE_PUBLISH = True

    def __init__(self):
        self.llm = get_llm(temperature=0.3)
        self.system_prompt = load_prompt("executive_summary_system")

    def generate(
        self,
        reporting_period: str,
        detailed_status: str,
        overall_rag: str,
        top_risks: list[str],
        top_issues: list[str],
        decisions_pending: list[str],
    ) -> dict[str, Any]:
        """
        Generate executive summary. Returns ExecutiveSummary schema.
        """
        user_prompt = f"Generate an executive summary for leadership review.\n[INPUT]\nreporting_period: {reporting_period}\ndetailed_status_summary: {detailed_status}\noverall_rag: {overall_rag}\ntop_risks: {json.dumps(top_risks)}\ntop_issues: {json.dumps(top_issues)}\ndecisions_pending: {json.dumps(decisions_pending)}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            summary = ExecutiveSummary.model_validate_json(response.content)
            result = summary.model_dump()
        except Exception as exc:
            logger.error("Executive summary failed validation", error=str(exc))
            result = {
                "artifact_type": "executive_summary",
                "reporting_period": reporting_period,
                "summary": f"Validation Error: {str(exc)}",
                "top_concerns": top_issues + top_risks,
                "decisions_required": decisions_pending,
                "assumptions": [f"Validation failed for: {response.content[:200]}..."],
                "confidence": "low",
                "requires_human_confirmation": True
            }
            
        logger.info("Executive summary generated")
        return result
