"""Documents router — upload project and governance documents."""
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/download/{doc_type}/{filename}")
async def download_document(doc_type: str, filename: str):
    """Download a document (e.g., charter, governance, etc.) by type and filename."""
    # Define base directory for documents (customize as needed)
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "documents", doc_type)
    file_path = os.path.abspath(os.path.join(base_dir, filename))
    if not os.path.isfile(file_path):
        return {"error": "File not found."}
    return FileResponse(file_path, filename=filename, media_type="application/octet-stream")


@router.post("/upload/project")
async def upload_project_docs(files: list[UploadFile] = File(...)):
    """Upload project detail documents (SOW, brief, etc.)."""
    names = [f.filename for f in files]
    return {"uploaded": names, "category": "project"}


@router.post("/upload/governance")
async def upload_governance_docs(files: list[UploadFile] = File(...)):
    """Upload governance documents (templates, policies, etc.)."""
    names = [f.filename for f in files]
    return {"uploaded": names, "category": "governance"}
