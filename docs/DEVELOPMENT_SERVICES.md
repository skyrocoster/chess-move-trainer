# Persistent development services

The backend, frontend, Datasette, and analysis workers run as detached Docker Compose services. They keep
running after the terminal closes, and ordinary source changes reload automatically without restarting
containers. The normal worker sleeps quietly and only starts the Stockfish engine while queued analysis work
exists. An optional profiled service can run exactly six parallel workers for background quick coverage.

All service commands go through the `sg` developer CLI, which wraps Docker Compose. Run them from the
repository root in Git Bash. Each command below is written in full so it can be copied as-is.

## First-time setup

Run these once on a new machine, from the repository root:

```bash
uv sync --frozen                    # Python environment from uv.lock
npm ci                              # JavaScript dependencies for the npm workspaces
npx playwright install chromium     # Browser used by the end-to-end tests
uv run --no-sync sg setup           # Checks the prerequisites; installs nothing
```

`sg setup` reports what is missing (uv, the `.venv` Python 3.12, node, npm, Docker, the `sg` script,
`node_modules`, Playwright Chromium). Docker Desktop must be running before any service command. The full
`sg` command list is in [`src/tools/dev/README.md`](../src/tools/dev/README.md); `uv run --no-sync sg --help`
prints it.

If the live database does not exist yet, create it once with `uv run --no-sync sg dev setup-db` (see
[Commands](#commands)).

## Commands

```bash
# Start all services in the background and wait until they are healthy.
uv run --no-sync sg dev start

# Check whether the services are running and healthy (also shows the worker mode).
uv run --no-sync sg dev status

# Read the latest 100 log lines without opening a permanent log window.
uv run --no-sync sg dev logs

# Stop or explicitly restart all services.
uv run --no-sync sg dev stop
uv run --no-sync sg dev restart

# Refresh games and openings in the live database (pauses workers, restores them after).
uv run --no-sync sg dev update

# One-time creation of the live database (refuses when one already exists).
uv run --no-sync sg dev setup-db
```

`setup-db` refuses to run when the live database already exists. Otherwise it runs the setup in a one-shot
worker container within the setup budget. If that budget runs out, it deletes the partial `chess.db` and its
`-journal`, `-wal` and `-shm` files. It does not pause or restore workers; only `update` and a cold `start` do.

A cold `start` (stopped stack, live database present) first runs `update games` then `update openings` in a
short-lived one-shot container (`chess-move-trainer-db-update`, same worker image, no extra Compose service)
against the live database in the `chess-database` volume, then starts the services. A healthy stack is left
alone: `start` performs no update and no worker-mode change. A failed update only warns and the services still
start on the existing data. `restart`, `rebuild`, and per-service starts never run data updates.

Add `backend`, `frontend`, `datasette`, `worker`, or `worker-six` after the action to affect only one service.
The default is `all`:

```bash
uv run --no-sync sg dev restart backend
uv run --no-sync sg dev logs worker --tail 200
```

Every `sg dev` command accepts `--dry-run`, which prints the Docker commands without running them. `status`
also accepts `--json`, and `logs` accepts `--tail N` (default 100). `update` and `setup-db` take no service.

The time limits for the data refresh, live-database setup, and health probes are in milliseconds and can be
overridden with environment variables. The defaults are:

| Variable | Default | Used by |
| --- | --- | --- |
| `CHESS_START_UPDATE_BUDGET_MS` | 900000 | The data refresh in a cold `start` and in `update` |
| `CHESS_DEV_SETUP_BUDGET_MS` | 3600000 | `setup-db` |
| `CHESS_DEV_PROBE_BUDGET_MS` | 60000 | Health probes |

Example: `CHESS_START_UPDATE_BUDGET_MS=1800000 uv run --no-sync sg dev update`.

### Optional six-worker mode

Normal mode is the default. To temporarily replace it with exactly six parallel analysis workers:

```bash
# Accelerated mode on. This stops the normal worker first.
uv run --no-sync sg dev start worker-six

# Report normal, accelerated-six, stopped, or invalid/partial/mixed worker state.
uv run --no-sync sg dev status

# Accelerated mode off. This leaves all analysis workers stopped.
uv run --no-sync sg dev stop worker-six

# Restore the normal one-worker mode.
uv run --no-sync sg dev start worker
```

The `worker-six` Compose service is hidden behind the `worker-six` profile and is scaled to six containers by
`sg`. `sg` stops the opposite mode before starting either mode. It reports a partial or mixed state instead of
treating it as healthy. Do not start worker containers with raw Docker commands.

Use `rebuild` instead of `restart` after changing a Dockerfile, Compose configuration, `requirements.txt`, or
the npm package manifests and lockfile. Target `backend` for Python dependencies, then `worker` separately (the
worker shares the backend image); rebuild all services after npm dependency changes.

The backend Compose service explicitly provides the existing `CHESS_REBUILT_DATABASE_PATH=data/database/chess.db`
setting for the live container database. When that Compose environment changes, use the targeted
`rebuild backend` command; a plain `restart backend` does not recreate the container with the changed
environment.

```bash
uv run --no-sync sg dev rebuild backend
uv run --no-sync sg dev rebuild worker
uv run --no-sync sg dev rebuild worker-six
uv run --no-sync sg dev rebuild
```

Docker Desktop must be running. `sg` reports a clear error instead of opening another terminal when it is not
available.

## Addresses and ports

| Service | Address |
| --- | --- |
| Backend | <http://localhost:5666> |
| Frontend | <http://localhost:8444> |
| Datasette | <http://localhost:8666> |
| Worker | No port; normal mode drains the queue every 5 seconds |
| Six workers | No port; accelerated mode runs exactly six queue workers |

All three ports are published only on the local machine. Startup fails rather than selecting a different port
when one is already occupied. The containers have no automatic restart policy: `restart` remains an explicit
command.

## Explore the live database with Datasette

Datasette is an off-the-shelf web UI for SQLite, managed as a `datasette` service in `compose.yaml` and
started by `sg dev` like everything else. Use it to browse tables and run `SELECT` queries against the live
database without changing application code.

Why this setup fits here:

- The database is SQLite with 11 tables (see `src/chess_move_trainer/database/schema_v2.sql`).
- The Datasette container mounts the same `chess-database` Docker volume as the backend and workers (at `/data`
  inside its container), so it always shows live data. The host file `data/database/chess-seed.db` is seed and
  export storage only; the separate `chess.db.backup.pre-wal` file remains a manual backup snapshot (see the
  volume note under Day-to-day behavior).
- Datasette only issues `SELECT` statements while serving, so the normal worker or six accelerated workers can
  keep running while you browse.
- It uses port `8666`, so it does not clash with the backend (`5666`) or frontend (`8444`).

Manage it from the repository root like any other service (Docker Desktop must be running):

```bash
# Start it (a plain `start` brings it up together with everything else).
uv run --no-sync sg dev start datasette

# Check it and read its logs.
uv run --no-sync sg dev status datasette
uv run --no-sync sg dev logs datasette
```

Then open <http://localhost:8666>, select the `chess` database, and open a table. Use the built-in SQL page for
read-only queries, and add `.json` to a table or query URL when you need machine-readable output.

The service definition intentionally mounts the volume without `:ro` and omits Datasette's `--immutable` flag:
SQLite needs the `-wal`/`-shm` sidecars for locking, and the workers write while you browse. Immutable mode
skips locking, which produces bogus `database disk image is malformed` errors on a live database (see
`compose.yaml`).

Safety notes:

- Do not add `--immutable` while workers run; it causes false `database disk image is malformed` errors. The
  database itself is fine in that case. Verify with a read-only check inside the backend container, which reads
  the same `chess-database` volume at `/workspace/data/database/chess.db`:
  `docker exec chess-move-trainer-backend-1 python -c "import sqlite3; c = sqlite3.connect('file:/workspace/data/database/chess.db?mode=ro', uri=True, timeout=30); print(c.execute('PRAGMA quick_check').fetchall())"`
  (expect `[('ok',)]`).
- To look at the host seed file instead of live data, copy the live database out first (see the `docker cp`
  example below) and inspect the copy with a host-side SQLite tool; the managed Datasette always shows the live
  volume.

## Day-to-day behavior

- Python changes under `backend/` or `src/` reload the backend.
- Frontend source changes use Vite hot module replacement.
- `stop` preserves the containers so a later `start` is quick.
- Backend, frontend, and worker reuse their existing images unless you run `rebuild`.
- Normal workers keep the database mutex and admit one background target at a time. Six-mode workers opt into
  capacity six and share the same active database mount; queue claims and claim tokens prevent duplicate work.
- A frontend request queued while six quick searches are active blocks further background admission. When a
  worker becomes available, requested work is claimed before another background target.
- Stopping a worker releases an in-process claim when possible. A forced stop leaves a running row reclaimable
  at the existing two-minute stale boundary; no database replacement should occur while either worker mode runs.
- The live database lives in the `chess-database` Docker volume, mounted at `/workspace/data/database` in the
  backend, worker, and worker-six containers and at `/data` in the datasette container. The host file
  `data/database/chess-seed.db` is a different, diverged file: seed and export storage only. Nothing automatic
  produces or refreshes that export. The separate `chess.db.backup.pre-wal` file remains a manual backup; if a
  file is not in the volume, it is not live. The per-file manifest, the stale-check (`sha256sum` on the host
  seed copy versus `docker exec chess-move-trainer-backend-1 sha256sum /workspace/data/database/chess.db`), and
  the manual export procedure live in [`data/README.md`](../data/README.md). Containers cannot see host-side
  edits, and host tools cannot see live results. To inspect or back up the live database, stop the workers
  first, then copy out of a container (for example
  `docker cp chess-move-trainer-worker-six-1:/workspace/data/database/chess.db data/database/chess-seed.db`)
  and restart afterward. Host proof, benchmark, and smoke suites that read `./data/database/chess-seed.db`
  skip when no export exists; run them against such a manual export.
- A cold `sg dev start` refreshes games and openings in the live database inside a one-shot container before
  the services start (see Commands above). `sg dev update` does the same on a live stack with workers paused.
  `restart`, `rebuild`, and per-service starts never update data.
- Each Stockfish process retains six engine threads and 1024 MiB of hash. Six workers can therefore use about
  36 engine threads and 6 GiB of hash, plus container and operating-system overhead.
- Avoid `docker compose down`; it removes the persistent containers and is unnecessary for normal development.

## Container users and caches

The backend and worker images run as the non-root `app` user and the frontend image runs as `node`. A leftover
from the older root-based images can break a first start after that hardening:

- The `frontend-node-modules` volume may still hold root-owned files, which makes the entrypoint's lockfile
  refresh fail with `Permission denied`. Reset only that regenerable cache with
  `docker volume rm chess-move-trainer_frontend-node-modules` and then `uv run --no-sync sg dev start`; no user
  data is stored in it. Never run a bare `docker compose down -v`: it would also delete the `chess-database`
  volume holding the live database.
- The Stockfish lock sidecar (`chess.db.stockfish.lock`) lives beside the live database inside the
  `chess-database` volume owned by the `app` user. A stale root-owned copy can only come from a root-run helper
  container; deleting that file lets the worker recreate it on its next poll.

## AI agent behavior

The stack is shared development infrastructure, not temporary setup for each task. Repository agents manage
these services only through `uv run --no-sync sg dev` and follow these rules:

- Before any lifecycle action or browser/E2E check, run `uv run --no-sync sg dev status` and reuse healthy
  services as they are; Playwright is configured to reuse them.
- A read-only packet (mapping, lookup, review) never starts, stops, restarts, or rebuilds services.
- Never launch Uvicorn or Vite directly on the host, and never start competing processes on the fixed ports
  `5666`, `8444`, or `8666`.
- Do not start, stop, or restart services before or after a task for ordinary source edits; hot reload applies
  them. If an approved check genuinely requires a stopped service, start only that service and leave the stack
  running afterward.
- Do not stop services as task cleanup, and never run `docker compose down` unless the user explicitly requests
  it.
- If a service is unhealthy, inspect `uv run --no-sync sg dev logs <service>` before acting; restart only that
  service when a restart is actually needed, and leave the stack running afterward.
- Never touch the live `chess-database` volume directly, and never write to the live database while workers
  run. Data updates happen only on a cold `sg dev start` (nothing running yet) or via `sg dev update`, which
  pauses the workers first and restores them afterward. `sg dev setup-db` only creates a database that does not
  exist yet. Never copy a host database file
  into the volume.
- Ordinary Python, TypeScript, and CSS source edits never need a rebuild; only dependency, Dockerfile, or
  Compose changes might (see `rebuild` above).
