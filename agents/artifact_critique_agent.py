"""
Artifact Critique Agent — Foundation Task 3.
Review generated output for clarity, completeness, and consistency.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt

from app.schemas.agents import ArtifactCritiqueResult

logger = structlog.get_logger(__name__)


class ArtifactCritiqueAgent:
    """
    Specialist agent: critiques artifacts for quality and readiness (Section 8.8).
    """

    ALLOWED_TOOLS = ["rubric", "llm"]
    CAN_DELEGATE_TO = []
    REQUIRES_HITL_BEFORE_PUBLISH = False

    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.system_prompt = load_prompt("artifact_critique_system")

    def critique(
        self,
        artifact_type: str,
        content: dict[str, Any],
        rubric: str | None = None,
    ) -> dict[str, Any]:
        """
        Critique the generated artifact. Returns ArtifactCritiqueResult schema.
        """
        user_prompt = f"Critique the provided artifact and indicate whether revision is recommended.\n[INPUT]\nartifact_type: {artifact_type}\nartifact: {json.dumps(content)}\nquality_rubric: {rubric or 'Standard PMO quality standards'}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            critique = ArtifactCritiqueResult.model_validate_json(response.content)
            result = critique.model_dump()
        except Exception as exc:
            logger.error("Artifact critique failed validation", error=str(exc))
            result = {
                "artifact_type": "critique_result",
                "readiness": "ready",
                "quality_score": 0.5,
                "findings": [{"dimension": "structure", "message": f"Validation Error: {str(exc)}", "recommended_revision": ""}]
            }
            
        logger.info("Artifact critique complete", readiness=result.get("readiness"))
        return result
