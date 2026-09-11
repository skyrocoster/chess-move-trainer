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
