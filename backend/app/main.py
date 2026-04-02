"""
PMO Agentic AI — FastAPI Application Entry Point
"""
import sys
from pathlib import Path

# Add the project root to sys.path so sibling modules (e.g. graph_runtime, agents) are discoverable
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import ssl
import httpx
import warnings

# Disable strict SSL verification for corporate network interceptors
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Monkeypatch HTTPX (used by LangChain/Google SDKs) to ignore SSL verification
_original_sync_init = httpx.Client.__init__
_original_async_init = httpx.AsyncClient.__init__

def _patched_sync_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_sync_init(self, *args, **kwargs)

def _patched_async_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _original_async_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_sync_init
httpx.AsyncClient.__init__ = _patched_async_init

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import configure_logging
from backend.app.db.session import init_db
from backend.app.routers import (
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
# â”€â”€ Routers (Foundation Task 4 aligned) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])

# ── Internal Service Proxies ─────────────────────────────────────────
app.include_router(orchestrator.router, prefix="/api/agent-runs", tags=["Orchestrator"])
app.include_router(llm_gateway.router, prefix="/api/llm", tags=["LLM Gateway"])
app.include_router(retrieval.router, prefix="/api/retrieval", tags=["Retrieval"])
app.include_router(validation.router, prefix="/api/validation", tags=["Validation"])
