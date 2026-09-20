# Chess Move Trainer

Chess Move Trainer is a Windows-focused web application for practising and reviewing chess moves.
It has a Python API, a React browser interface, and automated tests for both.

## Main tools

- **Backend:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, and python-chess
- **Frontend:** TypeScript, React, Vite, and React Chessboard
- **Testing:** pytest, Vitest, React Testing Library, and Playwright
- **UI development:** Storybook
- **Code quality:** Ruff, ESLint, and Prettier

## Repository map

- `backend/` — FastAPI application and backend tests
- `frontend/` — React application, styles, component tests, and Storybook
- `src/` — shared Python package and database code
- `tests/` — integration, database, engine, and end-to-end tests
- `data/` — local chess, database, and Stockfish data
- `docs/` — plans, examples, diagrams, and project notes
- `experiments/` — isolated prototypes and design experiments

Dependency versions are pinned in `requirements.txt`, `pyproject.toml`, and the root `package-lock.json`.

## Dependency policy

Python runtime versions are locked in `uv.lock` with a hashed `requirements.txt` export; npm
workspaces resolve from the root `package-lock.json`; Docker bases are digest-pinned. Re-check
them monthly with finite local commands (no application CI, no update bot):

- `npx -y npm@12.0.2 audit --json` from the root and from `.opencode/`
- `.venv/Scripts/python.exe -m pip_audit -r requirements.txt`
- Trivy `aquasec/trivy:0.74.0` scans of the final backend and frontend images

The full audit, scan results, and accepted-risk records live in
`docs/grilling-docs/dependency-and-library-audit-2026-09-19.md` (next review due 2026-10-19).
Apply upgrades manually in small groups using that document's verification runbook.

## Code-review inventory

An implementation-focused review, including prioritized improvement candidates
and suggested local tools, is in [docs/code-review/](docs/code-review/README.md).
It excludes `experiments/` and does not cover visual design.
