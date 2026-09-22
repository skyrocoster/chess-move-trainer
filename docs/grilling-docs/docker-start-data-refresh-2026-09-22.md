# Docker start data refresh

Date: 2026-09-22

## Goal

Round out the Docker starting workflow so that starting the stack via `dev.ps1` fetches the user's latest games from chess.com and updates the downstream data that depends on them, against the live database the services actually use — plus the explicit actions and safety rules around that.

## Repository facts found before the decisions

1. `dev.ps1 start` runs only `docker compose up --detach --wait --wait-timeout 180` (dev.ps1:133-149). No data step exists anywhere in the startup path; dev.ps1 and compose.yaml contain no `chess-seed` references.
2. Two databases exist. The live `chess.db` inside the `chess-database` Docker volume is used by backend, worker, and Datasette (compose.yaml:44-48, :15, :146/:157). The host file `data/database/chess-seed.db` is an export copy that goes stale the moment any worker writes (data/README.md:5-15, :32-34; DEVELOPMENT_SERVICES.md:162-164). The live file is the source of truth; the seed is export storage only.
3. Games updates are a manual host CLI locked to the seed path. `update games`, `update openings`, and `setup` accept no `--database` option (cli_lifecycle.py:25-71); the underlying functions have private `_database_path` seams (lifecycle.py:76-78, :166-168); the `schema create/upgrade/inspect` commands do take `--database` (cli_lifecycle.py:76, :102, :130). `setup` refuses to overwrite an existing file (lifecycle.py:90-94).
4. Acquisition fetches month archives from api.chess.com with politeness delays; incremental mode refetches only the newest saved month and later months (acquisition.py:208-213, :246, :252-253). Full setup downloads the entire game history (lifecycle `_setup_database`).
5. Downstream map. Derived game/position rows are computed during import (games/persistence_repository.py:362). Openings are NOT derived from games: `update openings` republishes the catalogue from the `data/chess-com/openings` source files (lifecycle.py:256-294). Stockfish analysis of new positions is picked up automatically by the worker's background selector (stockfish/targets.py:415-442 selects positions with no queue row; stockfish/worker.py:121-122, :313-327). Training aggregates update per API call.
6. Preferred moves are load-bearing end-to-end. Training-requirements discovery selects positions from `datasource_preferred_move_period` and scores answers against the active preferred move (positions/training_requirements_loaders.py:74-77, :138-160; positions/training_answers.py:218-256; training_requirements_repository.py:128-132). Statistics adherence (reporting/scope_readers.py:284, :307), games coverage (games/search_repository.py:316-334), the `/api/preferred-moves` router (backend/app/features/preferred_moves/router.py), and the repertoire-builder UI all read it.
7. The preferred-move guesser (deriving preferred moves from played games) is once-only: it refuses to run when a schedule already exists (preferred_moves/setup.py:142-147) and is hardcoded to the seed (cli_preferred.py:66-71). Once populated, manual curation (set/unset CLI, PUT/DELETE API, repertoire-builder UI) is the only path.
8. Host real-data tests. `tests/database/proof/test_proof.py` and `test_measurements.py` open the seed unconditionally, fail hard when it is missing, and accept a `DIRECT_DATABASE` env override (test_proof.py:19-24; test_measurements.py:14-19); they are strictly read-only (connection.py:121-124, `mode=ro`). Opt-in suites: the API benchmark accepts `CHESS_REBUILT_DATABASE_PATH` (test_api_benchmark_real.py:71); the training-requirements smoke and games smoke are hardwired to the seed. pytest is not in the backend image (requirements.txt is exported `--no-dev`; backend/Dockerfile:27-28). Boundary tests pin the `HOST_SEED_DATABASE_PATH` constant (test_source_boundary.py:102; test_package_boundary.py:23).
9. DEVELOPMENT_SERVICES.md:161: "no database replacement should occur while either worker mode runs." During normal operation the worker is the only writer to the live database; the backend only reads.

## Decisions

1. **Update the live database directly, from a short-lived container.** Rejected: updating the seed and copying it into the volume — that would destroy live-only state (Stockfish analysis results, training answer history). Rejected: auto-refreshing the seed export at start — it drags the export procedure into every start. The host seed copy is dumped from the workflow: nothing creates or refreshes it.
2. **Pipeline = `update games` + `update openings`.** Both target the live database. Stockfish analysis of new games stays automatic via the worker's background selection. Preferred moves are excluded from the pipeline.
3. **Update runs before services start; an already-healthy stack is left alone.** The cold-start window is the only case where nothing else holds the database. `restart`, `rebuild`, and per-service starts never trigger data updates.
4. **New `dev.ps1 update` action: pause workers → run both updates → restart workers in the mode that was active** (normal or the 6x `worker-six` profile). Backend, frontend, and Datasette stay up. Chosen over running the updater against a live stack, which would put two writers in contention for SQLite's single-writer lock.
5. **Warn and continue on update failure.** A failed or timed-out update never blocks the start; the update step always has a finite wall-clock budget. `dev.ps1 update` restores the workers first, then reports the error and exits non-zero.
6. **First run: refuse.** `dev.ps1 start` with no database in the volume stops and points to a new one-time `dev.ps1 setup` action. Reason: the user is concerned an automatic full setup could overwrite; play it safe. `setup` refuses to touch an existing database (inherited from lifecycle.py:90-94) and deletes its own partial file if it dies partway, so a retry starts clean — the incremental updater would not backfill gaps in a half-built database.
7. **Delete only the preferred-move guessing code** (`preferred_moves/setup.py`, `inference.py`, the `setup` CLI command, and their tests). The schedule table and its data, the `/api/preferred-moves` endpoints, the repertoire-builder UI, and the trainer flow stay untouched; the schedule changes only by manual curation. Rejected: deleting the whole feature — it is load-bearing for the trainer. The user got what they needed from the guesser and it does not work well.
8. **Retire host real-data tests.** The proof/benchmark/smoke suites skip when no database file is present (env overrides kept); nothing produces an export; the manual `docker cp` procedure stays documented in data/README.md. Rejected: running them in Docker against the live database — it requires dev dependencies in the runtime image and new test surface. Rejected: folding an export into `dev.ps1 update` — machinery in service of a file the user chose to dump.

## Resulting behavior (approved shape)

- `dev.ps1 start`, stack healthy → reuse as-is; no update, no churn.
- `dev.ps1 start`, stack stopped, database exists → one-shot container runs `update games` then `update openings` against `data/database/chess.db`, then services start. Failure or timeout → warning, start anyway on existing data.
- `dev.ps1 start`, no database → refuse; tell the user to run `dev.ps1 setup`.
- `dev.ps1 update` (new) → pause worker(s) → run both updates → restart worker(s) in the active mode. Failure → workers restored, error reported, non-zero exit.
- `dev.ps1 setup` (new, one-time) → create the database in a container (schema, full history from chess.com, openings); refuses if a database exists; cleans up its own partial file on failure.

## Constraints and exclusions

- Nothing automatic ever creates or replaces the database. The database is never written while workers run (cold start: nothing is running; `update`: workers are paused).
- No preferred-move refresh or rebuild capability is built; no changes to preferred-move API, UI, or trainer behavior.
- No export action; the seed file is not maintained by any workflow step.
- Worker/analysis behavior, service topology, ports, and the health feature are unchanged.
- Every command and test run uses explicit finite timeouts (repo mandatory rule).
- Plan proof is finite behavioral tests or browser scenarios only; no lint, formatting, type/build, source-size, or aggregate hygiene checks during implementation.
- This record settles direction only. It is not an implementation Plan or authorization to edit product code.

## Remaining assessment questions

- Exact deletion boundary of the guesser: what imports `setup`/`inference`; whether `timeline.py`/`ranges.py` serve non-guesser paths (list/resolve/set/unset, insight_helpers); which tests and boundary assertions must change.
- CLI unlock mechanism: explicit `--database` like the schema commands versus a default retarget, and how the one-shot container invokes it.
- dev.ps1 wiring: new actions in the ValidateSet, worker-mode detection and restore, healthy-stack detection, and missing-database detection from the host.
- Skip-when-missing changes for the proof and opt-in real-DB suites; the fate of the `HOST_SEED_DATABASE_PATH` constant and its boundary tests (the documented manual export path still lands there).
- Docs inventory: DEVELOPMENT_SERVICES.md (lifecycle and agent-rules sections), data/README.md, the AGENTS.md commands list, and CLI help text.

## Routing

The user chose Flash as the case-worker. Agreed route: assessment → Plan → coordinator review of the Plan → stop. Execution is explicitly deferred until the user says go.
