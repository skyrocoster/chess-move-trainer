# backend

FastAPI application serving the Chess Move Trainer API.

## Entry point

`app/main.py` — creates the FastAPI app, attaches CORS middleware, and mounts feature routers.

## Convention

Each feature lives in `app/features/<name>/` and typically contains:

- `router.py` — FastAPI router with route handlers
- `schemas.py` — Pydantic request/response models

Some features add a `schema.py` (singular) for SQLite DDL initialization.

## Features

| Directory | Purpose |
|-----------|---------|
| `app/features/health/` | `GET /api/health` endpoint |
| `app/features/positions/` | FEN position CRUD |
| `app/features/evaluation/` | Stockfish evaluation job queue and results |
| `app/features/analysis/` | Stockfish analysis pipeline, benchmarking, and persistence |
| `app/features/preferred_move/` | Fixed-owner preferred-move API (`GET`/`PUT`/`DELETE /api/preferred-move`) |
| `app/features/position_context/` | Neutral recurrence context for a position (`GET /api/position-context`) |
| `app/features/openings/` | Read-only opening Line Library API (`GET /api/openings/line-library`) |

## Running

```bash
scripts/dev.py backend          # starts on port 5666
# or directly:
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host localhost --port 5666
```

## Tests

Tests mirror the feature structure under `tests/features/`. Run with:

```bash
.venv\Scripts\python.exe -m pytest backend/
```

## Ports

- Backend API: **5666**
- Frontend dev server: **8444** (configured in CORS `allow_origins`)
