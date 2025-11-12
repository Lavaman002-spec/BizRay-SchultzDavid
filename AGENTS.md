# Repository Guidelines

Concise guidance for contributing to BizRay. Keep changes focused, consistent with the current structure, and easy to verify locally.

## Project Structure & Module Organization
- Backend (Python/FastAPI): `backend/`
  - API: `backend/services/api/` (routers in `routers/`, app in `main.py`)
  - Data: `backend/database/` (client, queries, migrations)
  - Shared: `backend/shared/` (models, config, utils)
  - Tests: `backend/tests/`
- Frontend (Next.js/TypeScript): `frontend/`
  - App Router: `frontend/src/app/`
  - Components: `frontend/src/components/`
  - Public assets: `frontend/public/`

## Build, Test, and Development Commands
- Run both apps (creates venv, installs): `make dev`
- Backend only: `make backend` or `uvicorn backend/services/api/main:app --reload --port 8000`
- Backend tests: `cd backend && pytest`
- Frontend dev: `cd frontend && npm run dev`
- Frontend build/start: `cd frontend && npm run build && npm start`

## Coding Style & Naming Conventions
- Python: 4‑space indent; modules and functions snake_case; classes PascalCase. Format with Black and lint with Flake8. Prefer type hints and small, focused modules (e.g., `services/ingest/api_client.py`).
- TypeScript/React: Follow ESLint Next presets (`frontend/eslint.config.mjs`). Components PascalCase in `src/components`, hooks start with `use` in `src/lib/hooks`. Keep files cohesive and colocate UI with app routes where practical.

## Testing Guidelines
- Framework: pytest (see `backend/pytest.ini`). Tests live under `backend/tests`, named `test_*.py`. Use fixtures in `backend/tests/conftest.py` and assert API contracts for new/changed routes.
- Frontend: no tests yet; if adding, prefer Jest/RTL for units and Playwright for E2E.

## Commit & Pull Request Guidelines
- History shows mixed styles (e.g., ticket prefixes like `BZR-41 ...` and Conventional Commits like `chore:`). Use Conventional Commits with optional ticket prefix: `BZR-123 feat(api): add search endpoint`.
- PRs: include a concise description, linked issue, test plan, and screenshots/GIFs for UI changes. Ensure `pytest` passes and `npm run lint && npm run build` are clean.

## Security & Configuration
- Do not commit secrets. Backend env from `backend/.env.example` → `backend/.env`. Frontend local env in `frontend/.env.local`. Keep keys in your local env or a secret manager.

## Agent‑Specific Tips
- Prefer `make dev` for local runs. Use `rg` to explore code. Keep diffs surgical (avoid renames unless necessary). Update docs and examples when changing routes or data models.

