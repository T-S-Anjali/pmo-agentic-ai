"""
RAID Classification and Merge Agent — Foundation Task 3.
Classifies and merges extracted RAID items into the log.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt
from app.schemas.agents import RAIDMergeRecommendation

logger = structlog.get_logger(__name__)


class RAIDClassificationAndMergeAgent:
    """
    Specialist agent: classifies items and deduplicates against existing log (Section 8.6).
    """

    ALLOWED_TOOLS = ["existing_raid_log", "rules", "llm"]
    CAN_DELEGATE_TO = ["governance_validation_agent"]
    REQUIRES_HITL_BEFORE_PUBLISH = True

    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.system_prompt = load_prompt("raid_merge_system")

    def merge(
        self,
        candidates: list[dict[str, Any]],
        existing_log: list[dict[str, Any]],
        classification_guidance: str = "",
    ) -> dict[str, Any]:
        """
        Merge items. Returns RAIDMergeRecommendation schema.
        """
        user_prompt = f"Produce a merge recommendation for extracted RAID items.\n[INPUT]\ncandidate_items: {json.dumps(candidates)}\nexisting_raid_log: {json.dumps(existing_log)}\nclassification_guidance: {classification_guidance}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            recommendation = RAIDMergeRecommendation.model_validate_json(response.content)
            result = recommendation.model_dump()
        except Exception as exc:
            logger.error("RAID merge failed validation", error=str(exc))
            result = {
                "artifact_type": "raid_merge_recommendation",
                "new_items": candidates,
                "updated_items": [],
                "duplicate_matches": [],
                "assumptions": [f"Validation failed: {str(exc)}"],
                "confidence": "low",
                "requires_human_confirmation": True
            }
            
        logger.info("RAID merge recommendation generated")
        return result
