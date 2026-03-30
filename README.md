# PMO Persona Agentic AI

## Overview
This repository contains the MVP implementation for the PMO Persona Agentic AI application.

## Main Components
- **frontend**: React/Next.js UI for intake, review, and approval.
- **backend**: FastAPI gateway for auth, workflow control, and artifact management.
- **graph-runtime**: LangGraph execution layer for multi-agent workflows.
- **agents**: Specialist agents (Charter, RAID, Status, etc.) and Supervisor logic.
- **prompts**: Centralized and versioned prompt templates.
- **retrieval**: Retrieval-Augmented Generation (RAG) logic and adapters.
- **rules**: PMO guardrails and validation engine.
- **integrations**: Adapters for LLMs, storage, and external services.

## MVP Workflows
- **Project Intake -> Charter Generation**: 21-node path from raw input to approved charter.
- **Weekly Status Report**: Automated narrative and executive summary generation.
- **RAID Update**: Extraction and merge of Risks, Actions, Issues, and Dependencies from meeting notes.

## Quick Start
1. Clone the repo.
2. Copy `.env.example` to `.env`.
3. Install dependencies per service (see `docs/runbook-local-dev.md`).
4. Start local services.
5. Open the frontend locally at `http://localhost:3000`.

## Repository Structure
See `/docs/architecture.md` and `/docs/runbook-local-dev.md` for detailed layout information.

## Development
- Use feature branches (`feature/<name>`).
- Submit Pull Requests to `main`.
- Ensure all CI checks pass.

## Testing
Run lint, unit tests, and integration tests before opening a PR.
```bash
# Example
pytest backend/tests
pytest graph-runtime/tests
```
