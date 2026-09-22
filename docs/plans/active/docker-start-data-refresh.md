# Docker start data refresh - `dev.ps1` fetches the latest games against the live volume database

> **Status:** pending — written 2026-09-22 from the approved direction record; coordinator-reviewed
> and corrected the same day (Stage 3 proof validity for the hardwired opt-in suites; Stage 4
> accelerated partial-stack restore excludes the normal `worker` from `up`). Execution is
> explicitly deferred until the user says go.

- **Read trigger:** Read before implementing or reviewing any change to `dev.ps1`, the lifecycle CLI
  (`setup` / `update games` / `update openings`), the preferred-move guesser deletion, the real-data
  test retirement, or the matching docs.
- **Upstream:** [Docker start data refresh direction record](../../grilling-docs/docker-start-data-refresh-2026-09-22.md)
  — the authoritative direction. All ten decisions there are settled; this Plan only pins the
  implementation edges. The coordinator additionally resolved five sub-decisions recorded below.

## Outcome

Starting the stack the normal way keeps the user's data current: `dev.ps1 start` on a cold stack
fetches the latest games from chess.com and republishes openings **against the live database the
services actually use** (the `chess.db` inside the `chess-database` volume) before the services
start. An already-healthy stack is left entirely alone. A first run with no database refuses and
points to a new one-time `dev.ps1 setup`. A new `dev.ps1 update` refreshes data on a live stack by
pausing the workers, running the same updates, and restoring the workers in the mode that was
active. The once-only preferred-move guesser, whose job is done, is deleted — while the
preferred-move schedule, API, repertoire-builder UI, and trainer flow that depend on its data stay
untouched. Host real-data tests no longer fail when no exported database file exists; they skip.

## Coordinator sub-decisions (binding)

1. **Already-healthy stack = full no-op.** `dev.ps1 start` on an already-healthy stack performs NO
   data update AND no worker-mode normalization (today's `start all` stops a running `worker-six`
   and starts one normal worker at `dev.ps1:141` — that switch is suppressed). Worker-mode control
   stays explicit via `dev.ps1 start worker` / `start worker-six`. When the stack is only partially
   up (not healthy), the update path applies: running workers are stopped first (never write while
   workers run), the update runs, and the workers are restored per the active mode before/with the
   remaining services (see the wiring note in Stage 4 so the Compose `up` does not create a mixed
   worker state).
2. **Wall-clock budgets (named, tunable):** update one-shot run **900,000 ms (15 min)**; setup
   one-shot run **3,600,000 ms (60 min)**; missing-database probe **60,000 ms**. Each is a script
   variable overridable by an environment variable (for example
   `CHESS_START_UPDATE_BUDGET_MS` / `CHESS_DEV_SETUP_BUDGET_MS` / `CHESS_DEV_PROBE_BUDGET_MS`) so
   the timeout behavior is provable without editing the script. On timeout the one-shot container
   is killed by fixed name (`docker compose run --name <fixed>` + `docker rm -f`) so no orphan
   updater can hold the SQLite lock; a killed `setup` additionally removes its own partial database
   from the volume (safe: `setup` refused to start when any database existed, so any file found
   after a killed setup was created by that attempt).
3. **CLI unlock mechanism:** explicit optional `--database` flag on `setup`, `update games`, and
   `update openings`, defaulting to `HOST_SEED_DATABASE_PATH`, mirroring the `schema` commands;
   forwarded through the existing private seams. Rewrite the pinned assertions in
   `tests/database/test_lifecycle_cli.py` rather than deleting the file.
4. **Proof scope for `setup`:** the refusal path is proven for real against the existing volume
   database. The full-creation success path is NOT proven by a live full-history fetch — it stays
   covered by the existing pytest coverage of the `_setup_database` seam plus a bounded wiring check
   of the composed container command. Never delete or recreate the `chess-database` volume for proof.
5. **Real update run:** one real cold-start update against the live volume (incremental fetch,
   normally one month) is the acceptance scenario — it is exactly what the feature does.
   Warn-and-continue is proven by forcing a timeout (tiny budget override) and observing the warning
   plus services still starting.

## Known facts execution must preserve

| Fact | Evidence |
|---|---|
| Live `chess.db` in the `chess-database` volume is the source of truth; host `chess-seed.db` is export storage only and nothing automatic produces or refreshes it. | `data/README.md:5-15`; `DEVELOPMENT_SERVICES.md:162-164` |
| The worker is the only database writer during normal operation; the backend reads. No database writes while workers run. | `DEVELOPMENT_SERVICES.md:161`; record fact 9 |
| `setup` refusal-if-exists and partial-file self-cleanup already exist — no lifecycle code needed for those decisions. | `lifecycle.py:90-94`, `lifecycle.py:141-152` |
| `update games` needs the saved month ledger; it refetches the newest saved month plus later ones with politeness sleeps. The ledger (`data/chess-com/raw/games/…`) is git-tracked and update runs modify it — **proof must never commit those changes**. | `acquisition.py:208-277`; `git ls-files data/chess-com/raw` |
| pytest is NOT in the runtime image (`--no-dev` requirements); the one-shot container needs no dev deps. | `backend/Dockerfile:27-28` |
| Backend/worker/Datasette topology, ports (5666/8444/6006/8666), health feature, and preferred-move API/UI/trainer behavior are unchanged. | record exclusions |
| `docker compose run --rm --no-deps worker …` needs **no compose.yaml change**: `worker` (via `x-worker-common`) has the venv image, `PYTHONPATH=/workspace:/workspace/src`, bind `.` → `/workspace`, the volume mounted over `/workspace/data/database`, no ports, no `depends_on`, no image ENTRYPOINT. It runs as the `app` user, same as workers, so sidecar ownership stays consistent. | `compose.yaml:3-17,173-186`; `backend/Dockerfile:22-38` |
| `HOST_SEED_DATABASE_PATH` and its boundary pins stay (the documented manual `docker cp` export still lands at `data/database/chess-seed.db`; the backend default at `backend/app/dependencies.py:25` is untouched). | `test_source_boundary.py:102/:106`; `test_package_boundary.py:23/:122` |

## Scope

- **Included:** `dev.ps1` start/update/setup behavior and safety wiring; lifecycle CLI unlock
  (`src/chess_move_trainer/database/cli_lifecycle.py`, `lifecycle.py` seams, `cli_helpers.py` target
  handling, `cli.py` re-exports); deletion of the preferred-move guesser
  (`preferred_moves/setup.py`, `inference.py`, CLI `setup` command, its render helper, and their
  tests); skip-when-missing retirement of the five host real-data suites; docs
  (`DEVELOPMENT_SERVICES.md`, `data/README.md`, `AGENTS.md`) and CLI help text.
- **Expected areas:** `dev.ps1`, `compose.yaml` (no change expected), `src/chess_move_trainer/database/cli_lifecycle.py`,
  `src/chess_move_trainer/database/lifecycle.py`, `src/chess_move_trainer/database/cli_helpers.py`,
  `src/chess_move_trainer/database/cli_preferred.py`, `src/chess_move_trainer/database/cli.py`,
  `src/chess_move_trainer/database/preferred_moves/`, `tests/database/**` (the suites named below),
  `backend/tests/**` (the suites named below), `docs/DEVELOPMENT_SERVICES.md`, `data/README.md`, `AGENTS.md`.
- **Excluded:** preferred-move refresh/rebuild capability; preferred-move API, UI, trainer, and
  `datasource_preferred_move_period` data; worker/analysis behavior; service topology and ports;
  any export action or export production (the manual `docker cp` procedure stays documented);
  application CI; Git operations (never commit — including refreshed raw-month ledger files).

## Stages

1. **pending** — **CLI unlock.** Add the explicit optional `--database` flag (default
   `HOST_SEED_DATABASE_PATH`) to `setup`, `update games`, and `update openings` in
   `cli_lifecycle.py`, forwarding the path through the existing private seams
   (`_setup_database/_update_games/_update_openings`, `lifecycle.py:76-78/:166-168/:256-258`);
   make `_run_lifecycle` (`cli_helpers.py:68-94`) target-aware so the seed-path guard (:78-84) and
   the `Target:` line (:89-90) use the requested destination and still reject a mismatched result;
   update the three command help strings and keep the container-path sentences; update the pinned
   assertions in `tests/database/test_lifecycle_cli.py` (help pins :18-31, fixed-path mocks :51-72,
   destination-override pin :94-108) to the new contract. No default-path behavior change for
   host users.
   - **Proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_lifecycle_cli.py tests/database/test_schema_cli.py tests/database/test_setup.py tests/database/test_update_games.py tests/database/test_update_openings.py -q` (tool timeout 150000 ms).
   - **Escalation:** if the target-aware guard cannot preserve the mismatch rejection cleanly.

2. **pending** — **Guesser deletion.** Delete `preferred_moves/setup.py` and
   `preferred_moves/inference.py`; delete the `setup` command in `cli_preferred.py:66-81` with its
   imports (`:20-22`, `:32-37`) and the `_render_preferred_setup` helper (`cli_helpers.py:24-26`,
   `:192-205`); delete `tests/database/preferred_moves/test_setup.py`, `test_inference.py`, and
   `test_cli.py` (all of it covers only the setup command). Keep `ranges.py`, `timeline.py`,
   `repository.py`, `mutations.py`, and `__init__.py` unchanged — they serve the load-bearing
   list/resolve/set/unset paths, `insight_helpers.py:17`, and `statistical_analysis/readers.py:9`.
   The boundary tests (`test_package_boundary.py:146-170`, `test_source_boundary.py:218-293`) need
   no edits.
   - **Proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` (tool timeout 150000 ms).
   - **Escalation:** any discovery that a kept path (timeline/ranges/repository) secretly depended
     on the deleted modules.

3. **pending** — **Test retirement.** In the five suites — `tests/database/proof/test_proof.py`
   (only the two real-DB tests at :44/:75), `tests/database/proof/test_measurements.py`,
   `backend/tests/benchmarks/test_api_benchmark_real.py` (replace the hard
   `assert database.exists()` at :70-73 with a skip), `backend/tests/features/position_training_requirements/test_real_database.py`,
   and the real-DB smoke in `backend/tests/features/games/test_api.py:358-372` — skip when the
   resolved database file is absent. Keep the existing `DIRECT_DATABASE` and
   `CHESS_REBUILT_DATABASE_PATH` overrides and the existing opt-in gates; follow the repo's skip
   idiom (`pytestmark = pytest.mark.skipif(...)` / `pytest.skip`). `HOST_SEED_DATABASE_PATH`
   imports and boundary pins stay.
    - **Proof (missing file):** the opt-in gates are set (`CHESS_RUN_API_BENCHMARK_REAL=1`,
      `CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE=1`) so a skip can only come from the missing
      file, never from the gate. `DIRECT_DATABASE` / `CHESS_REBUILT_DATABASE_PATH` pointed at a
      nonexistent path → the overridable suites skip for the missing-file reason:
      `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/proof/test_proof.py tests/database/proof/test_measurements.py backend/tests/benchmarks/test_api_benchmark_real.py -q` (tool timeout 150000 ms). The training-requirements smoke resolves its seed path CWD-relatively with no
      chdir, so it is proven from the pre-approved temp dir with its gate set:
      `timeout 120s .venv/Scripts/python.exe -m pytest G:/ChessMoveTrainer/backend/tests/features/position_training_requirements/test_real_database.py -q` (tool timeout 150000 ms; if imports fail from a foreign CWD, this scenario rests on code review). The games real-DB smoke **cannot** be proven this way: it `chdir(ROOT)`s itself
      (`test_api.py:364-366`), so the repo-root seed file is always present to it — its
      skip-when-missing branch rests on code review (same category as the missing-volume refusal).
      Then one run from the repo root confirming nothing over-skips today (`tests/database/proof` subset).
   - **Escalation:** none expected.

4. **pending** — **dev.ps1 wiring.** Add `setup` and `update` to the `$Action` ValidateSet
   (dev.ps1:4). Add a healthy-stack check (`docker compose ps` State/Health over backend, frontend,
   datasette, worker) and the missing-database probe —
   `docker compose run --rm --no-deps --name <fixed-probe-name> worker python -c "…exit 0 if the database file exists else 1…"` —
   so the host never needs a new image and stopped containers do not interfere.
   Wire the `start all` branch: healthy → exit as a full no-op (no update, no mode switch);
   not healthy and database missing → refuse with a pointer to `dev.ps1 setup`; not healthy and
   database present → stop any running workers, run `update games` then `update openings` as two
   sequential one-shot runs (`docker compose run --rm --no-deps --name chess-move-trainer-db-update worker python -m chess_move_trainer.database update games --database data/database/chess.db`, then the openings twin) under `UpdateBudgetMs`, on failure/timeout warn and continue into today's `docker compose up` (when the stack was partially up, restore the active worker mode first — and in accelerated mode bring up the non-worker services explicitly, `up --detach --wait backend frontend storybook datasette`, so the normal `worker` is never started alongside `worker-six`; no mixed worker state). `start worker`, `start worker-six`, `restart`, `rebuild`, per-service starts, `stop`, `logs`, `status` never run data updates.
   New `update` action: probe first (missing database → error pointing to `dev.ps1 setup`, non-zero,
   no pause); read `Get-WorkerMode`, refuse on invalid/mixed; pause the active mode, run both
   one-shot updates under the budget, restore workers in the active mode (`Start-NormalWorker` /
   `Start-AcceleratedWorkers`, dev.ps1:103-123); failure path restores workers first, then reports
   the error and exits non-zero. New `setup` action: probe first (database exists → refuse with
   message, non-zero, untouched); otherwise run one `setup --database data/database/chess.db`
   one-shot run under `SetupBudgetMs`; on timeout kill by fixed name, then run a one-shot cleanup
   command that deletes `chess.db` and its `-journal/-wal/-shm` sidecars from the volume (safe per
   sub-decision 2). Enforce every budget with a finite PowerShell process wait; never leave an
   orphan container named `chess-move-trainer-db-*`.
   - **Proof scenarios (each begins with `dev.ps1 status`; never `docker compose down`; volume
     never deleted; stack left healthy):**
     - Healthy no-op: with the stack healthy, `dev.ps1 start` → no updater container appears, worker mode unchanged.
     - Cold start with database (acceptance run): `dev.ps1 stop all`, then `dev.ps1 start` → both updates run before `docker compose up`, services end healthy; Datasette reflects refreshed data.
     - `dev.ps1 update` in normal mode: workers paused, updates run, normal worker restored, backend/frontend/datasette stay up; then once in accelerated mode (`start worker-six`, `update`, worker-six×6 restored).
     - `dev.ps1 setup` against the existing database → refusal message, non-zero exit, database bytes unchanged (`docker exec chess-move-trainer-backend-1 sha256sum /workspace/data/database/chess.db` before/after).
     - Forced timeout: tiny budget override on a stopped stack → warning printed, services start anyway on existing data, updater container killed by name and removed.
     - Probe mechanics: probe with the real path → exit 0; with an absent probe path → exit 1 (the full missing-volume refusal cannot be exercised without deleting the volume, which is forbidden; its wiring rests on this probe proof plus code review).
   - **Escalation:** budget values prove unusable; a scenario would need a destructive action
     (volume deletion, `down -v`, force-replacing the live database); the full no-op decision breaks
     an existing documented behavior.

5. **pending** — **Docs.** `DEVELOPMENT_SERVICES.md`: commands block (:13-33) gains `update`/`setup`
   and the one-shot container note; day-to-day (:148-174) keeps the export/stale-check prose as
   manual-procedure documentation but states that nothing automatic produces an export, that the
   proof/benchmark/smoke suites skip when no export exists, that cold `start` updates the live
   database in a one-shot container, and that `restart`/`rebuild`/per-service starts never do;
   agent rules (:192-208) gain the data-update safety lines. `data/README.md`: role table row
   (:34) and stale section (:41-55) adjusted to the same statements. `AGENTS.md`: `dev.ps1` action
   list gains `update` and `setup` with a one-line cold-start note. CLI help text was rewritten in
   Stage 1.
   - **Proof:** `timeout 30s grep -rn "chess-seed" docs/DEVELOPMENT_SERVICES.md data/README.md AGENTS.md` plus review that no doc still claims the host CLI is the only update path or that a workflow produces an export (tool timeout 60000 ms).
   - **Escalation:** none expected.

## Progress and decisions

- **Stage 1:** pending — proof: lifecycle/schema/update pytest subset; breakpoint: none.
- **Stage 2:** pending — proof: preferred-moves + boundary pytest subset; breakpoint: none.
- **Stage 3:** pending — proof: skip-when-missing runs (override, temp-CWD, and code-review variants per the stage proof); breakpoint: none.
- **Stage 4:** pending — proof: six dev.ps1/docker scenarios with finite budgets; breakpoint: budget tuning only.
- **Stage 5:** pending — proof: bounded grep + review; breakpoint: none.

## Proof

Passing behavioral proof is retained until a later change affects its command, inputs, exercised
behavior, configuration, dependencies, or environment; later stages run only missing or invalidated
proof. The full acceptance set:

- Cold `dev.ps1 start` with the database present → `update games` + `update openings` run in the
  one-shot container against `data/database/chess.db` in the `chess-database` volume before
  `docker compose up`; services end healthy.
- Healthy-stack `dev.ps1 start` → complete no-op: no update, no worker-mode switch.
- `dev.ps1 update` → workers paused, both updates run, workers restored in the active mode
  (proven in normal and accelerated-six modes); backend/frontend/Datasette never go down.
- `dev.ps1 setup` against an existing database → refusal, non-zero exit, database bytes unchanged.
- Forced timeout (tiny budget override) → clear warning, services start anyway on existing data;
  the killed container is removed by name. `dev.ps1 update` failure → workers restored first, then
  error, non-zero exit.
- Missing-database probe: exit 0 present / exit 1 absent (full refusal exercised in code review
  only — volume deletion is forbidden).
- The five retired suites skip when their database file is absent and run normally when present;
  env overrides kept.
- `preferred_moves/setup.py` / `inference.py` and the guesser tests are gone while
  `preferred_moves` public API, list/resolve/set/unset CLI, insight helpers, statistics readers,
  timeline, and all surviving preferred-move tests pass.

## Escalation boundaries

- The healthy-stack full-no-op decision breaks an existing documented behavior.
- A budget value (900,000 / 3,600,000 / 60,000 ms) proves unusable in practice.
- Any proof scenario would require a destructive action: deleting the `chess-database` volume,
  `docker compose down` / `down -v`, or force-replacing the live database.
- Anything that would change preferred-move API/UI/trainer behavior, worker/analysis behavior,
  service topology, ports, or the health feature.
- Any new product, data, dependency, ownership, or acceptance decision not settled by the direction
  record or the coordinator sub-decisions above.

## Visible result

> From a stopped stack, `dev.ps1 start` now refreshes the user's chess.com games and openings in
> the live database before the services come up — and running it again while everything is healthy
> does nothing at all.
