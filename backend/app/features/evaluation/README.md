# evaluation

Stockfish evaluation backend feature.

## Scope

Handles browser-initiated evaluation requests: submit a FEN, get engine evaluation back.

## Layers

| File pattern | Role |
|-------------|------|
| `router.py` | FastAPI route handlers (`/api/evaluation/...`) |
| `schemas.py` | Pydantic request/response models |
| `service.py` | Business logic — queues jobs, calls engine, returns results |
| `queue.py` | Async job queue for concurrent evaluation requests |
| `schema.py` (singular) | SQLite DDL initialization for evaluation tables |

## Relationship to analysis

`analysis/` runs bulk, long-running Stockfish analysis across the corpus. `evaluation/` serves ad-hoc, single-position evaluations requested from the UI.
