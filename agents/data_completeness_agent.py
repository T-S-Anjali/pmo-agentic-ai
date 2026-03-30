"""
Data Completeness Agent — Foundation Task 3.
Identifies missing mandatory inputs or ambiguous fields.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt
from app.schemas.agents import DataCompletenessResult

logger = structlog.get_logger(__name__)


class DataCompletenessAgent:
    """
    Specialist agent: checks if input data is sufficient for generation (Section 8.9).
    """

    ALLOWED_TOOLS = ["normalized_input", "rules"]
    CAN_DELEGATE_TO = []
    REQUIRES_HITL_BEFORE_PUBLISH = False

    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        self.system_prompt = load_prompt("data_completeness_system")

    def check(
        self,
        workflow_type: str,
        input_data: dict[str, Any],
        required_fields: list[str],
    ) -> dict[str, Any]:
        """
        Returns DataCompletenessResult schema.
        """
        user_prompt = f"Evaluate whether the workflow input is sufficient, insufficient, or ambiguous.\n[INPUT]\nworkflow_type: {workflow_type}\nnormalized_input: {json.dumps(input_data)}\nrequired_input_fields: {json.dumps(required_fields)}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            completeness = DataCompletenessResult.model_validate_json(response.content)
            result = completeness.model_dump()
        except Exception as exc:
            logger.error("Data completeness check failed validation", error=str(exc))
            missing = [f for f in required_fields if f not in input_data]
            result = {
                "status": "sufficient" if not missing else "insufficient",
                "missing_fields": missing,
                "ambiguous_fields": [f"Validation Error: {str(exc)}"],
                "recommended_next_action": "continue" if not missing else "request_input"
            }
            
        logger.info("Data completeness check complete", status=result.get("status"))
        return result
