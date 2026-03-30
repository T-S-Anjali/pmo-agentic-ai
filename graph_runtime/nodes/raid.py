"""
RAID workflow nodes.
"""
import structlog
from langchain_core.messages import AIMessage

from graph_runtime.state import RAIDWorkflowState

logger = structlog.get_logger(__name__)


from agents.raid_extraction_agent import RAIDExtractionAgent
from agents.raid_classification_merge_agent import RAIDClassificationAndMergeAgent
from agents.governance_validation_agent import GovernanceValidationAgent

logger = structlog.get_logger(__name__)


def extract_raid_items(state: RAIDWorkflowState) -> dict:
    """Extract RAID items from raw meeting notes text."""
    agent = RAIDExtractionAgent()
    result = agent.extract(state["input_payload"].get("meeting_notes_text", ""))
    return {
        "extensions": {
            **state.get("extensions", {}),
            "raid": {"extracted_items": result.get("items", [])}
        },
        "current_node": "extract_raid_items",
        "messages": [AIMessage(content=f"Extracted {len(result.get('items', []))} RAID candidates.")],
    }


def classify_and_merge_raid(state: RAIDWorkflowState) -> dict:
    """Classify and deduplicate items against the existing log."""
    agent = RAIDClassificationAndMergeAgent()
    raid_ext = state.get("extensions", {}).get("raid", {})
    candidates = raid_ext.get("extracted_items", [])
    
    # Placeholder for retrieving existing log
    existing_log = [] 
    
    result = agent.merge(candidates, existing_log)
    return {
        "extensions": {
            **state.get("extensions", {}),
            "raid": {
                **raid_ext,
                "merged_items": result.get("new_items", []) + result.get("updated_items", [])
            }
        },
        "current_node": "classify_and_merge_raid"
    }


def validate_raid_log(state: RAIDWorkflowState) -> dict:
    """Validate the merged RAID log against governance rules."""
    agent = GovernanceValidationAgent()
    raid_ext = state.get("extensions", {}).get("raid", {})
    result = agent.validate("raid_log", {"items": raid_ext.get("merged_items", [])})
    return {
        "validation_findings": state.get("validation_findings", []) + result.get("findings", []),
        "validation_summary": result.get("summary"),
        "current_node": "validate_raid_log"
    }


def publish_raid_log(state: RAIDWorkflowState) -> dict:
    """Publish the approved RAID log."""
    return {
        "workflow_status": "completed",
        "approval_status": "approved",
        "messages": [AIMessage(content="RAID log updated and published.")],
    }
