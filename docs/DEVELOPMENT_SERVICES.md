# Persistent development services

The backend, frontend, and Storybook run as detached Docker Compose services. They keep running after the
PowerShell window closes, and ordinary source changes reload automatically without restarting containers.

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

Add `backend`, `frontend`, or `storybook` after the action to affect only one service:

```powershell
powershell -ExecutionPolicy Bypass -File ./dev.ps1 restart backend
powershell -ExecutionPolicy Bypass -File ./dev.ps1 logs storybook
```

Use `rebuild` instead of `restart` after changing a Dockerfile, Compose configuration, `requirements.txt`, or
the npm package manifests and lockfile. Target `backend` for Python dependencies; rebuild all services after npm
dependency changes because the frontend and Storybook share them. Storybook is the exception to manual rebuilds:
it has `pull_policy: build`, so an ordinary `start` already rebuilds its image (fast from Docker layer cache when
dependencies are unchanged).

```powershell
powershell -ExecutionPolicy Bypass -File ./dev.ps1 rebuild backend
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

All three ports are published only on the local machine. Startup fails rather than selecting a different port when
one is already occupied. The containers have no automatic restart policy: `restart` remains an explicit command.

## Day-to-day behavior

- Python changes under `backend/` or `src/` reload the backend.
- Frontend source changes use Vite hot module replacement.
- Story and component changes use Storybook hot module replacement.
- `stop` preserves the containers so a later `start` is quick.
- `start` always rebuilds the Storybook image; backend and frontend reuse their existing images unless you run `rebuild`.
- Avoid `docker compose down`; it removes the persistent containers and is unnecessary for normal development.

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
