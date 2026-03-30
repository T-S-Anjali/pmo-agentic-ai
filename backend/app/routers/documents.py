"""Documents router — upload project and governance documents."""
from fastapi import APIRouter, File, UploadFile

router = APIRouter()


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
