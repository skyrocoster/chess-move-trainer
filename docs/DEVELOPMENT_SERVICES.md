# Persistent development services

The backend, frontend, Storybook, and analysis workers run as detached Docker Compose services. They keep
running after the PowerShell window closes, and ordinary source changes reload automatically without
restarting containers. The normal worker sleeps quietly and only starts the Stockfish engine while queued
analysis work exists. An optional profiled service can run exactly six parallel workers for background quick
coverage.

## Commands

Run commands from the repository root:

```powershell
# Start all services in the background and wait until they are healthy.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 start

# Check whether the services are running and healthy.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 status

# Read the latest 100 log lines without opening a permanent log window.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 logs

# Stop or explicitly restart all services.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 stop
powershell -ExecutionPolicy Bypass -File ./dev.ps1 restart
```

Add `backend`, `frontend`, `storybook`, `worker`, or `worker-six` after the action to affect only one service:

```powershell
powershell -ExecutionPolicy Bypass -File ./dev.ps1 restart backend
powershell -ExecutionPolicy Bypass -File ./dev.ps1 logs worker
```

### Optional six-worker mode

Normal mode is the default. To temporarily replace it with exactly six parallel analysis workers:

```powershell
# Accelerated mode on. This stops the normal worker first.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 start worker-six

# Report normal, accelerated-six, stopped, or invalid/partial/mixed worker state.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 status

# Accelerated mode off. This leaves all analysis workers stopped.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 stop worker-six

# Restore the normal one-worker mode.
powershell -ExecutionPolicy Bypass -File ./dev.ps1 start worker
```

The `worker-six` Compose service is hidden behind the `worker-six` profile and is scaled to six containers by
`dev.ps1`. The script stops the opposite mode before starting either mode. It reports a partial or mixed state
instead of treating it as healthy. Do not start worker containers with raw Docker commands.

Use `rebuild` instead of `restart` after changing a Dockerfile, Compose configuration, `requirements.txt`, or
the npm package manifests and lockfile. Target `backend` for Python dependencies, then `worker` separately
(the worker shares the backend image); rebuild all services after npm
dependency changes because the frontend and Storybook share them. Storybook is the exception to manual rebuilds:
it has `pull_policy: build`, so an ordinary `start` already rebuilds its image (fast from Docker layer cache when
dependencies are unchanged).

```powershell
powershell -ExecutionPolicy Bypass -File ./dev.ps1 rebuild backend
powershell -ExecutionPolicy Bypass -File ./dev.ps1 rebuild worker
powershell -ExecutionPolicy Bypass -File ./dev.ps1 rebuild worker-six
powershell -ExecutionPolicy Bypass -File ./dev.ps1 rebuild
```

Docker Desktop must be running. The script reports a clear error instead of opening another terminal when it is
not available.

## Addresses and ports

| Service | Address |
| --- | --- |
| Backend | <http://localhost:5666> |
| Frontend | <http://localhost:8444> |
| Storybook | <http://localhost:6006> |
| Worker | No port; normal mode drains the queue every 5 seconds |
| Six workers | No port; accelerated mode runs exactly six queue workers |

All three ports are published only on the local machine. Startup fails rather than selecting a different port when
one is already occupied. The containers have no automatic restart policy: `restart` remains an explicit command.

## Day-to-day behavior

- Python changes under `backend/` or `src/` reload the backend.
- Frontend source changes use Vite hot module replacement.
- Story and component changes use Storybook hot module replacement.
- `stop` preserves the containers so a later `start` is quick.
- `start` always rebuilds the Storybook image; backend, frontend, and worker reuse their existing images
  unless you run `rebuild`.
- Normal workers keep the database mutex and admit one background target at a time. Six-mode workers opt into
  capacity six and share the same active database mount; queue claims and claim tokens prevent duplicate work.
- A frontend request queued while six quick searches are active blocks further background admission. When a
  worker becomes available, requested work is claimed before another background target.
- Stopping a worker releases an in-process claim when possible. A forced stop leaves a running row reclaimable at
  the existing two-minute stale boundary; no database replacement should occur while either worker mode runs.
- The live database lives in the `chess-database` Docker volume, mounted at `/workspace/data/database` in the
  backend, worker, and worker-six containers. The host file `data/database/chess.db` is seed, backup, and export
  storage only: containers cannot see host-side edits, and host tools cannot see live results. To inspect or back
  up the live database, stop the workers first, then copy out of a container (for example
  `docker cp chess-move-trainer-worker-six-1:/workspace/data/database/chess.db data/database/chess.db`)
  and restart afterward. Host test suites that read `./data/database/chess.db` must run against such an export.
- Each Stockfish process retains six engine threads and 1024 MiB of hash. Six workers can therefore use about
  36 engine threads and 6 GiB of hash, plus container and operating-system overhead.
- Avoid `docker compose down`; it removes the persistent containers and is unnecessary for normal development.

## Container users and caches

The backend and worker images run as the non-root `app` user and the
frontend/Storybook images run as `node`. Two leftovers from the older
root-based images can break a first start after that hardening:

- The `frontend-node-modules` and `storybook-node-modules` volumes may still
  hold root-owned files, which makes the entrypoint's lockfile refresh fail
  with `Permission denied`. Reset only those two regenerable caches with
  `docker volume rm chess-move-trainer_frontend-node-modules chess-move-trainer_storybook-node-modules`
  and then `dev.ps1 start`; no user data is stored in them. Never run a bare
  `docker compose down -v`: it would also delete the `chess-database` volume holding the live database.
- The Stockfish lock sidecar (`chess.db.stockfish.lock`) lives beside the live database inside the
  `chess-database` volume owned by the `app` user. A stale root-owned copy can only come from a root-run
  helper container; deleting that file lets the worker recreate it on its next poll.

## AI agent behavior

The stack is shared development infrastructure, not temporary setup for each task. Repository agents manage these
services only through `dev.ps1` and follow these rules:

- Before any lifecycle action or browser/E2E check, run `dev.ps1 status` and reuse healthy services as they are;
  Playwright is configured to reuse them.
- Never launch Uvicorn, Vite, or Storybook directly on the host, and never start competing processes on the fixed
  ports `5666`, `8444`, or `6006`.
- Do not start, stop, or restart services before or after a task for ordinary source edits; hot reload applies
  them. If an approved check genuinely requires a stopped service, start only that service and leave the stack
  running afterward.
- Do not stop services as task cleanup, and never run `docker compose down` unless the user explicitly requests it.
- If a service is unhealthy, inspect its `dev.ps1 logs <service>` output before acting; restart only that service
  when a restart is actually needed, and leave the stack running afterward.
- Ordinary Python, TypeScript, CSS, and Storybook source edits never need a rebuild; only dependency, Dockerfile,
  or Compose changes might (see `rebuild` above).
