# Persistent development services

The backend, frontend, and Storybook run as detached Docker Compose services. They keep running after the
PowerShell window closes, and ordinary source changes reload automatically without restarting containers.

## Commands

Run commands from the repository root:

```powershell
# Start all services in the background and wait until they are healthy.
powershell -ExecutionPolicy Bypass -File .\dev.ps1 start

# Check whether the services are running and healthy.
powershell -ExecutionPolicy Bypass -File .\dev.ps1 status

# Read the latest 100 log lines without opening a permanent log window.
powershell -ExecutionPolicy Bypass -File .\dev.ps1 logs

# Stop or explicitly restart all services.
powershell -ExecutionPolicy Bypass -File .\dev.ps1 stop
powershell -ExecutionPolicy Bypass -File .\dev.ps1 restart
```

Add `backend`, `frontend`, or `storybook` after the action to affect only one service:

```powershell
powershell -ExecutionPolicy Bypass -File .\dev.ps1 restart backend
powershell -ExecutionPolicy Bypass -File .\dev.ps1 logs storybook
```

Use `rebuild` instead of `restart` after changing a Dockerfile, Compose configuration, `requirements.txt`, or
the npm package manifests and lockfile. Target `backend` for Python dependencies; rebuild all services after npm
dependency changes because the frontend and Storybook share them:

```powershell
powershell -ExecutionPolicy Bypass -File .\dev.ps1 rebuild backend
powershell -ExecutionPolicy Bypass -File .\dev.ps1 rebuild
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
- Avoid `docker compose down`; it removes the persistent containers and is unnecessary for normal development.

## AI agent behavior

The stack is shared development infrastructure, not temporary setup for each task. Repository agents are instructed
to check `dev.ps1 status` and reuse healthy containers before browser or end-to-end checks. They must not launch
Uvicorn, Vite, or Storybook directly, restart containers for ordinary source edits, or stop containers during task
cleanup. If a service is unhealthy, they inspect its finite logs first and may restart only that service when the
restart is genuinely required.
