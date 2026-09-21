# Blunder training backend

**Started:** 2026-09-21  
**Status:** Implemented and locally verified.  
**Authority:** The user requested direct backend-only implementation without a question round. This running record captures repository facts, implementation decisions, uncertainties, and verification as work proceeds; it is not a separate Plan.

## Goal

Find blunders from games played within a requested timeframe and expose them through the backend so the existing `/trainer` experience can use them.

## User constraints

- Backend only. A separate agent owns frontend work, so frontend files must not be read or changed for this implementation.
- Do not ask follow-up questions; resolve non-blocking details from repository conventions and production-safe defaults.
- If new persistence is needed, use a reviewable JSON representation rather than creating a database table.
- Treat validation, deterministic behavior, error handling, tests, and API contracts as production work.

## Decision log

- Preserve the existing trainer and analysis contracts unless the requested capability requires an additive backend change.
- Prefer deriving blunders from authoritative game and engine-analysis data already in the repository rather than inventing a second chess-evaluation source.
- Keep any new persisted schema human-readable and explicitly versioned in JSON so it can be reviewed before a future database migration.
- No new persistence is required for the first production path. Blunders can be derived read-only from consecutive game positions and their existing analysis results, so no table or JSON data store will be introduced.
- A blunder is a move by the trainer that loses at least `0.20` expected game points according to Stockfish's normalized win/draw/loss values. Expected score is `win + 0.5 * draw`, viewed from the trainer's colour. This works consistently for centipawn and mate evaluations and avoids inventing a centipawn value for mate.
- The default threshold will be an application policy setting rather than a client-controlled label. It will be returned in the API response and can be changed through environment configuration without changing stored data.
- Discovery requires an explicit inclusive RFC3339 game-start range. Results are occurrence-based, retain game and ply provenance, and are ordered deterministically by largest expected-score loss first.
- Each result will provide the position before the mistake, the move played, and the first move from the pre-move principal variation as `preferred_move_uci`. Those fields let trainer clients present the existing board exercise without exposing SQLite identifiers.
- Moves lacking comparable completed analysis are not guessed. The response will report coverage counts so an empty result can be distinguished from incomplete analysis.

## Repository facts and verification log

- Games already store an RFC3339 start time, trainer colour, ordered position occurrences, and the outgoing UCI move in `datasource_game` and `derived_game_position`.
- Each analyzed canonical position stores a rank-one line with White-perspective WDL values. The Stockfish pipeline normalizes both score and WDL to White's perspective before persistence.
- Consecutive occurrences in one game describe the position before and after an outgoing move, so discovery can compare those two existing evaluations without writing data.
- Existing `/api/positions/training-requirements` items use `fen`, `trainer_color`, and `preferred_move_uci`; the blunder response will deliberately use the same three trainer-facing field names.
- There is no existing blunder threshold or persisted blunder entity. The implementation therefore needs an additive domain reader and HTTP endpoint, but no schema migration.
- `chess_move_trainer.database.blunders` now owns strict query and policy validation, read-only discovery, trainer-perspective WDL scoring, terminal-position scoring, deterministic sorting and pagination, and schema/storage error boundaries.
- `GET /api/trainer/blunders` requires inclusive `started_at_from` and `started_at_to` RFC3339 timestamps. It also accepts optional `trainer_color`, `page`, and `page_size` filters.
- The response includes the normalized timeframe, the active threshold and scoring basis, coverage counts, stable game/ply provenance, trainer-ready `fen` and `preferred_move_uci` fields, played move, expected scores, and analysis quality.
- Coverage is explicit: every in-scope trainer move is either comparable or counted in `skipped_missing_analysis_count`. Games with missing or malformed timestamps are counted separately and excluded rather than misclassified.
- The default threshold is `0.20` expected game points. `CHESS_BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS` can override it; invalid configuration makes only this capability return a controlled `503` response.
- The endpoint uses the existing bounded read cache. Its key includes the database path, normalized timeframe, colour, pagination, and policy threshold; database file changes still invalidate the payload through the shared signature mechanism.
- No database table, migration, or JSON persistence file was needed. Discovery reads existing normalized game and analysis records without mutating the database, so there is no provisional storage schema to review.
- Focused verification passed: **54 tests passed** across `tests/database/blunders` and `backend/tests/features/trainer_blunders`.
- The tests cover White and Black score perspective, exact-threshold inclusion, RFC3339 normalization and inclusive bounds, trainer-turn filtering, later-ply FEN counters, legal preferred-PV moves, missing-analysis coverage, terminal scoring, deterministic ordering and pagination, bounded large-ID reads, read-only behavior, missing/incompatible storage, strict API output, policy configuration, caching, controlled errors, and OpenAPI registration.
- Frontend source was not changed by this backend implementation. Existing unrelated frontend work in the shared worktree was left untouched.
