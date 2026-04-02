"""
Retrieval service — vector store queries and document loaders.
"""
from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def _get_chroma_collection(name: str):
    import chromadb
    from app.core.config import settings
    # Use PersistentClient for local-only mode without Docker
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection(name)


def retrieve_template_for_classification(classification: str) -> dict[str, Any]:
    """Retrieve the best-matching charter template for the given classification."""
    try:
        collection = _get_chroma_collection("pmo_templates")
        results = collection.query(
            query_texts=[f"project charter template for {classification}"],
            n_results=1,
        )
        if results and results["documents"]:
            return {
                "template_id": results["ids"][0][0],
                "content": results["documents"][0][0],
                "metadata": results["metadatas"][0][0],
            }
    except Exception as exc:
        logger.warning("Template retrieval failed — using fallback", exc=str(exc))
    return {"template_id": "default", "content": "", "metadata": {}}


def retrieve_project_status_inputs(project_id: str | None) -> list[dict[str, Any]]:
    """Retrieve project metrics, RAID items, and prior report for status generation."""
    try:
        collection = _get_chroma_collection("pmo_project_data")
        results = collection.query(
            query_texts=[f"project status metrics RAID issues project_id:{project_id}"],
            n_results=10,
        )
        docs = []
        if results and results["documents"]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                docs.append({"content": doc, "metadata": meta})
        return docs
    except Exception as exc:
        logger.warning("Status input retrieval failed", exc=str(exc))
        return []


def retrieve_existing_raid_log(project_id: str | None) -> list[dict[str, Any]]:
    """Retrieve the current RAID log for a project."""
    try:
        collection = _get_chroma_collection("pmo_raid_logs")
        results = collection.query(
            query_texts=[f"RAID log project_id:{project_id}"],
            n_results=50,
        )
        if results and results["documents"]:
            import json
            items = []
            for doc in results["documents"][0]:
                try:
                    items.append(json.loads(doc))
                except Exception:
                    pass
            return items
    except Exception as exc:
        logger.warning("RAID log retrieval failed", exc=str(exc))
    return []
