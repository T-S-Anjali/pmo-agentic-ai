# PMO Agentic AI — Local Startup Script (Section 8.3/11)
# Use this to start services in separate terminals.

# --- 1. SET ENVIRONMENT ---
$env:PYTHONPATH = "backend;.;"
$env:OLLAMA_BASE_URL = "http://localhost:11434" # If using local Ollama

# --- 2. START BACKEND API (Port 8000) ---
# cd backend
# .\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# --- 3. START GRAPH RUNTIME (Port 8001) ---
# .\backend\.venv\Scripts\python.exe -m uvicorn graph_runtime.runtime:app --reload --port 8001

# --- 4. START AGENTS SERVICE (Port 8002) ---
# .\backend\.venv\Scripts\python.exe -m uvicorn agents.service:app --reload --port 8002

# --- 5. START FRONTEND (Port 3000) ---
# cd frontend
# npm run dev
