# Contributing

## Development Flow
1. Fork or clone the repository.
2. Create a topic-focused branch.
3. Install backend and frontend dependencies.
4. Run `python scripts/seed_demo.py`.
5. Verify backend tests and frontend build before opening a PR.

## Local Checks
- Backend tests: `python -m pytest -q backend/tests`
- Frontend build: `cd frontend && npm run build`
- Demo data: `python scripts/seed_demo.py`

## Project Conventions
- Keep backend logic inside `backend/app` by responsibility: `agents`, `services`, `repositories`, `api`.
- Keep frontend views inside `frontend/src/pages` and shared UI in `frontend/src/components`.
- Generated artifacts should stay under `backend/generated`.
- Sample inputs should stay under `samples/`.
- Do not hardcode secrets; use `.env`.

## Pull Requests
- Keep PRs scoped to one change area.
- Update `README.md` and `docs/runbook.md` when behavior or commands change.
- Include test/build evidence in the PR description.
- If you add a new agent behavior, document the responsibility split in `docs/openclaw_integration.md`.

