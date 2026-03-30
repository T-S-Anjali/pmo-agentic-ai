import sys
import os
# Ensure backend is in the path
sys.path.append(os.path.abspath("backend"))

try:
    from app.schemas.agents import ProjectCharterDraft, SupervisorDecision
    print("Agent schemas imported successfully!")
    from agents.charter_draft_agent import CharterDraftAgent
    print("CharterDraftAgent initialized successfully!")
    from agents.supervisor import SupervisorAgent
    print("SupervisorAgent initialized successfully!")
    print("ALL Foundation Task 5 imports passed.")
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
