# Architecture Overview — PMO Persona Agentic AI

## High-Level Architecture

```
[React Frontend]
      |
      | REST / HTTP (JSON)
      v
[FastAPI Backend]
  ├── /workflows   — start, status, resume, cancel
  ├── /approvals   — list pending, submit decision
  ├── /documents   — upload project + governance docs
  └── /audit       — audit trail queries
      |
      v
[LangGraph Runtime]
  ├── graph.py         — 3 compiled workflow graphs
  ├── state.py         — PMOGraphState TypedDict
  ├── nodes/           — graph node implementations
  └── edges.py         — conditional routing functions
      |
      ├────────────────────────────────────────────────
      |                |                |             |
[Agents]        [Retrieval]      [Rules Engine]  [LLM Gateway]
  ├── supervisor     ChromaDB         catalogue.py  Azure OpenAI
  ├── charter_draft  Vector Store     engine.py
  ├── status_summary
  ├── raid_extraction
  └── governance_validation
```

## Data Flow — Project Intake to Charter

```
1. POST /workflows/start (workflow_type: project_intake_to_charter)
2. WorkflowService creates WorkflowInstance record + threads to background
3. LangGraph graph starts → classify_project → retrieve_template → draft_charter
4. validate_charter → rules engine evaluates R-001, R-002
5. If blocking findings → retry (draft_charter) max 3 times
6. interrupt_before=pm_review_checkpoint → workflow pauses, status=awaiting_review
7. PM reviews in UI → POST /workflows/{id}/resume (approved|rejected)
8. If approved → interrupt_before=pmo_approval_checkpoint → pause again
9. PMO approves → publish_charter → workflow_status=completed
```

## Human-in-the-Loop Design

- LangGraph `interrupt_before` pauses the graph at `pm_review_checkpoint` and `pmo_approval_checkpoint`
- Backend stores `workflow_status=awaiting_review` in DB
- Frontend polls `/workflows/{id}` and surfaces review UI
- `POST /workflows/{id}/resume` with `approval_status` resumes the graph
- LangGraph PostgresSaver checkpoint persists state between pause and resume

## State Persistence

- `MemorySaver` in development
- `PostgresSaver` (LangGraph) in production — uses `CHECKPOINT_DB_URL`
- Each workflow run has a unique `thread_id` for checkpoint isolation

## Security

- Azure AD OIDC tokens passed in Authorization header
- User identity and role propagated through `user_context` in graph state
- Role-based access: PM can review, PMO can approve, Exec is read-only
