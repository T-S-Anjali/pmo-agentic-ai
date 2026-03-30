"""
Supervisor Agent — Foundation Task 3.

The supervisor is responsible for planning, routing, and combining
outputs from specialist subagents. It decides which specialist to
invoke and aggregates results before returning to the graph.
"""
import json
from typing import Any

import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.llm_factory import get_llm
from prompts.loader import load_prompt
from app.schemas.agents import SupervisorDecision

logger = structlog.get_logger(__name__)


class SupervisorAgent:
    """
    PMO Workflow Supervisor Agent (Section 8.1).
    Decides the next action based on workflow state.
    """

    def __init__(self):
        self.llm = get_llm(temperature=0.0)
        self.system_prompt = load_prompt("supervisor_system")

    def plan(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Decision-making node to choose the next specialist or action.
        Returns SupervisorDecision schema.
        """
        input_summary = {
            "workflow_type": state.get("workflow_type"),
            "current_step": state.get("current_node"),
            "workflow_status": state.get("workflow_status"),
            "validation_summary": state.get("validation_summary"),
            "available_artifacts": [a.get("type") for a in state.get("generated_artifacts", [])],
            "pending_human_tasks": state.get("human_tasks"),
            "latest_findings": state.get("validation_findings")[-1:] if state.get("validation_findings") else []
        }

        user_prompt = f"Given the workflow context, select the next action.\n[INPUT]\n{json.dumps(input_summary, indent=2)}"

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        try:
            response = self.llm.invoke(messages)
            # Validate with Pydantic
            decision = SupervisorDecision.model_validate_json(response.content)
            result = decision.model_dump()
        except Exception as exc:
            logger.error("Supervisor decision failed validation", error=str(exc))
            # Fallback to interrupt if unsure
            result = {
                "selected_action": "interrupt",
                "selected_agent": None,
                "reason": f"Validation failure: {str(exc)}",
                "inputs_required": [],
                "expected_output_schema": None,
                "next_step_hint": "human_intervention_required"
            }
        
        logger.info("Supervisor decision made", action=result["selected_action"], agent=result["selected_agent"])
        return result


# Singleton
supervisor_agent = SupervisorAgent()
