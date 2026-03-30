"""
PMO Agentic AI — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.routers import (
    approvals,
    audit,
    auth,
    documents,
    health,
    workflows,
    orchestrator,
    llm_gateway,
    retrieval,
    validation,
)

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PMO Agentic AI backend", env=settings.APP_ENV)
    await init_db()
    yield
    logger.info("Shutting down PMO Agentic AI backend")


app = FastAPI(
    title="PMO Persona Agentic AI",
    description="Multi-agent PMO automation powered by LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────
# ── Routers (Foundation Task 4 aligned) ──────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(approvals.router, prefix="/api/tasks", tags=["Approvals"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])

# ── Internal Service Proxies ─────────────────────────────────────────
app.include_router(orchestrator.router, prefix="/agent-runs", tags=["Orchestrator"])
app.include_router(llm_gateway.router, prefix="/llm", tags=["LLM Gateway"])
app.include_router(retrieval.router, prefix="/retrieval", tags=["Retrieval"])
app.include_router(validation.router, prefix="/validation", tags=["Validation"])
