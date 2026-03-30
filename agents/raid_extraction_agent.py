"""
RAID Extraction Agent — extracts and classifies RAID items from meeting notes.
"""
from __future__ import annotations

import json
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt

from app.schemas.agents import RAIDCandidates

logger = structlog.get_logger(__name__)


class RAIDExtractionAgent:
    """
    Specialist agent: extracts RAID candidates (Section 8.5).
    """

    ALLOWED_TOOLS = ["llm"]
    CAN_DELEGATE_TO = ["raid_classification_merge_agent", "governance_validation_agent"]
    REQUIRES_HITL_BEFORE_PUBLISH = True

    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        self.system_prompt = load_prompt("raid_extraction_system")

    def extract(self, meeting_notes: str, project_context: str = "", existing_raid: str = "") -> dict[str, Any]:
        """
        Extract items. Returns RAIDCandidates schema.
        """
        user_prompt = f"Identify candidate RAID items from the meeting content.\n[INPUT]\nproject_context: {project_context}\nmeeting_notes: {meeting_notes}\nexisting_raid_summary: {existing_raid}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        
        try:
            # Validate with Pydantic
            candidates = RAIDCandidates.model_validate_json(response.content)
            result = candidates.model_dump()
        except Exception as exc:
            logger.error("RAID extraction failed validation", error=str(exc))
            result = {
                "artifact_type": "raid_candidates",
                "items": [],
                "unresolved_items": [f"Validation Error: {str(exc)}", response.content[:500]],
                "assumptions": ["Automatic extraction failed, manual review required"],
                "confidence": "low",
                "requires_human_confirmation": True
            }
            
        logger.info("RAID extraction complete", count=len(result.get("items", [])))
        return result
            
        logger.info("RAID extraction complete", count=len(result.get("items", [])))
        return result
