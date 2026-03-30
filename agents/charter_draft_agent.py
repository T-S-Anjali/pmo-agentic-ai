"""
Charter Draft Agent — generates project charter from template + inputs.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt

from app.schemas.agents import ProjectCharterDraft

logger = structlog.get_logger(__name__)


class CharterDraftAgent:
    """
    Specialist agent: generates a structured project charter (Section 8.2).
    """

    ALLOWED_TOOLS = ["retrieval", "llm"]
    CAN_DELEGATE_TO = ["artifact_critique_agent", "governance_validation_agent"]
    REQUIRES_HITL_BEFORE_PUBLISH = True

    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.system_prompt = load_prompt("charter_draft_system")

    def generate(
        self,
        input_payload: dict[str, Any],
        template_context: str | dict | None = None,
        revision_instructions: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate charter draft. Returns ProjectCharterDraft schema.
        """
        user_prompt = f"Create a project charter draft.\n[INPUT]\nnormalized_input: {json.dumps(input_payload)}\ntemplate_context: {json.dumps(template_context)}\nrevisions: {revision_instructions}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            charter = ProjectCharterDraft.model_validate_json(response.content)
            result = charter.model_dump()
        except Exception as exc:
            logger.error("Charter generation failed validation", error=str(exc))
            # Basic fallback for demo/stability
            result = {
                "artifact_type": "project_charter_draft",
                "draft_version": 1,
                "content": {
                    "title": "Draft Charter (Validation Failed)",
                    "sponsor": "Unknown",
                    "business_purpose": "Validation Error during generation",
                    "objectives": [],
                    "scope_in": [],
                    "scope_out": [],
                    "timeline": {"start": "TBD", "end": "TBD"},
                    "budget": {"amount": 0.0, "currency": "USD"},
                    "stakeholders": []
                },
                "assumptions": [f"Validation error: {str(exc)}"],
                "missing_information": [],
                "confidence": "low",
                "requires_human_confirmation": True
            }
        
        logger.info("Charter draft generated")
        return result
