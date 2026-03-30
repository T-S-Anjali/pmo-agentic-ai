# Contributing Guide

## Branching Strategy
We use a trunk-based development model with short-lived feature branches.
- `feature/<name>` for new features.
- `fix/<name>` for bug fixes.
- `chore/<name>` for maintenance tasks.

## Pull Requests
Before submitting a PR:
1. **Lint & Format**: Run `scripts/lint.sh`.
2. **Test**: Run `scripts/test.sh`. Ensure unit tests pass.
3. **Docs**: Update `/docs` if contracts or designs changed.
4. **Schemas**: Update `/schemas` if API or output models changed.

## Coding Standards
### General
- Typed contracts required for all inter-service communication.
- No hardcoded secrets; use `.env`.
- Prompts must be stored in `/prompts`, not hardcoded in logic.
- All business-facing outputs must follow the defined JSON schemas in `/schemas`.

### Python
- Type hints are mandatory.
- Use Pydantic for data models and contract validation.
- Format code using Black and lint with Ruff.

### Frontend
- TypeScript is required.
- Keep components presentational; the backend owns workflow state transitions.

## Review Checklist
- [ ] Code builds and runs locally.
- [ ] Unit tests added for new logic.
- [ ] Integration checks for workflow transitions pass.
- [ ] No secrets committed.
- [ ] Documentation updated (README, architecture, etc.).
