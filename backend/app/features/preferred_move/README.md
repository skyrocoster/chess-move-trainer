# preferred_move

Fixed-owner preferred-move API backend feature.

## Scope

Serves a small HTTP lifecycle for the fixed owner's one preferred move per existing game-derived position:
retrieve the current or historical move, set/replace it, or remove it. Requests never create or migrate
database schema.

## API

- `GET /api/preferred-move?fen=<full FEN>&as_of=<optional UTC timestamp>` — returns `{fen, state, move}`,
  where `state` is `assigned` or `unassigned` and `move` is `{uci, san}` or `null`
- `PUT /api/preferred-move` — body `{fen, move_uci, effective_at?}`, returns `{fen, changed, effective_at}`
- `DELETE /api/preferred-move?fen=<full FEN>&effective_at=<optional timestamp>` — same mutation shape

## Layers

| File pattern | Role |
|-------------|------|
| `router.py` | FastAPI route handlers for `/api/preferred-move` |
| `api_schemas.py` | Strict Pydantic request/response/error models |
| `service.py` | Validation and orchestration (canonical FEN/UCI, UTC timestamps) |
| `repository.py` | Read/write SQLite adapter over existing append-only event storage |
| `errors.py` | Typed domain errors mapped to safe HTTP status codes |

## Relationship to storage

Event semantics delegate to the `scripts/opening_catalog/preferred_move*` primitives; ownership is the fixed
Skyrocoster subject UUID from `features/positions`. The completed implementation Plan is
`docs/plans/done/preferred-move-api/preferred-move-api.md`.