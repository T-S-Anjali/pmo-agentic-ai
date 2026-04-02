"""
Testing Workflow Nodes — Functional Test Generation via DeepAgents.

Nodes wire the build_testing_agent() into the LangGraph execution path.
"""
from __future__ import annotations

from typing import Any
import structlog
from datetime import datetime

from graph_runtime.state import PMOGraphState

logger = structlog.get_logger(__name__)


def ingest_testing_request(state: PMOGraphState) -> dict[str, Any]:
    """
    Read feature/API description from input_payload and store in extensions.
    Expected input_payload keys:
        - feature_description (str): What to generate tests for
        - filename (str, optional): Desired output filename
    """
    payload = state.get("input_payload", {})
    feature_description = payload.get("feature_description", "")
    filename = payload.get("filename", "test_generated.py")

    if not feature_description:
        logger.warning("No feature_description provided in input_payload")

    logger.info(
        "Ingesting testing request",
        filename=filename,
        description_length=len(feature_description),
    )

    return {
        "extensions": {
            **state.get("extensions", {}),
            "testing": {
                "feature_description": feature_description,
                "filename": filename,
                "agent_output": None,
                "saved_path": None,
                "run_result": None,
            },
        },
        "current_node": "ingest_testing_request",
    }


def run_testing_agent(state: PMOGraphState) -> dict[str, Any]:
    """
    Invoke the DeepAgents-powered testing agent with the feature description.
    The agent reasons, generates pytest code, saves it, and (optionally) runs it.
    """
    testing_ext = state.get("extensions", {}).get("testing", {})
    feature_description = testing_ext.get("feature_description", "")
    filename = testing_ext.get("filename", "test_generated.py")

    if not feature_description:
        logger.error("Cannot run testing agent — no feature_description in state")
        return {
            "error_state": {
                "node": "run_testing_agent",
                "message": "Missing feature_description in input_payload",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "current_node": "run_testing_agent",
        }

    try:
        from agents.testing_agent import build_testing_agent

        agent = build_testing_agent()

        prompt = (
            f"Generate a complete functional test suite for the following feature.\n\n"
            f"Feature Description:\n{feature_description}\n\n"
            f"Save the test script as: {filename}\n"
            f"After saving, run the tests using run_pytest and report results."
        )

        logger.info("Invoking testing agent", filename=filename)
        result = agent.invoke({"messages": [("human", prompt)]})

        # Extract the last AI message content as the agent output
        messages = result.get("messages", [])
        agent_output = ""
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content:
                agent_output = msg.content
                break

        logger.info("Testing agent completed", output_length=len(agent_output))

        return {
            "extensions": {
                **state.get("extensions", {}),
                "testing": {
                    **testing_ext,
                    "agent_output": agent_output,
                },
            },
            "current_node": "run_testing_agent",
        }

    except Exception as exc:
        logger.exception("Testing agent failed", error=str(exc))
        return {
            "error_state": {
                "node": "run_testing_agent",
                "message": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            },
            "current_node": "run_testing_agent",
        }


def save_test_results(state: PMOGraphState) -> dict[str, Any]:
    """
    Package the agent output into generated_artifacts and set validation summary.
    """
    testing_ext = state.get("extensions", {}).get("testing", {})
    agent_output = testing_ext.get("agent_output", "")
    filename = testing_ext.get("filename", "test_generated.py")

    error_state = state.get("error_state")
    if error_state:
        # Propagate error path
        return {
            "validation_summary": {
                "status": "fail",
                "blocking_count": 1,
                "warning_count": 0,
            },
            "current_node": "save_test_results",
        }

    artifact = {
        "type": "functional_test_script",
        "filename": filename,
        "content": agent_output,
        "generated_at": datetime.utcnow().isoformat(),
    }

    logger.info("Saving test results artifact", filename=filename)

    return {
        "generated_artifacts": state.get("generated_artifacts", []) + [artifact],
        "validation_summary": {
            "status": "pass",
            "blocking_count": 0,
            "warning_count": 0,
        },
        "current_node": "save_test_results",
    }
