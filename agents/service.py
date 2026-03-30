"""
Agents Service — FastAPI Service Wrapper.
"""
from fastapi import FastAPI
from agents.supervisor import SupervisorAgent
from agents.charter_draft_agent import CharterDraftAgent

app = FastAPI(title="PMO Agents Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "agents-service"}

# Additional agent routes can be added here
