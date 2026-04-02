"""
start_backend.py — Run this from the project root.
Usage: py start_backend.py
"""
import sys, os

# Ensure project root is in path so 'backend.*' imports work
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")

for p in [ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.chdir(ROOT)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
