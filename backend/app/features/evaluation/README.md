# evaluation

Stockfish evaluation backend feature.

## Scope

Owns the durable evaluation queue and its independently versioned SQLite schema over the shared analysis
pipeline, including the legacy-database schema initialization and migration helpers that the retained
`analysis/` feature still imports.

## Layers

| File pattern | Role |
|-------------|------|
| `service.py` | Business logic — queues jobs, calls engine, returns results |
| `queue.py` | Durable job queue for concurrent evaluation requests |
| `schema.py` (singular) | SQLite DDL initialization for evaluation tables |
| `models.py` | Value objects for queue items and service results |
| `errors.py` | Typed errors for schema, validation, queue, and lock failures |
| `__init__.py` | Package exports for the retained engine |

The legacy HTTP adapter (`router.py`, `api_schemas.py`) and its `/api/evaluation` routes were retired; no
HTTP surface remains in this package.

## Relationship to analysis

`analysis/` runs bulk, long-running Stockfish analysis across the corpus. `evaluation/` owns the durable
queue/schema the analysis engine and its legacy-schema migration rely on.
