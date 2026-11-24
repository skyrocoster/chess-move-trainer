# AI Instructions: Chess Move Trainer
Windows-only FastAPI + Vite React TypeScript application for training chess moves. Use plain English and do not
assume the user is an expert. You will sometimes drift into overly technical language or skip real-world
examples — when you notice this, stop and rewrite with plain wording and concrete examples. Ground explanations
in this repository's actual files, commands, and behavior; do not use metaphors or invented analogies to explain
things that can be shown directly.

## Application architecture

- `backend/` contains the FastAPI/Pydantic service. The health feature owns `GET /api/health`, which
  returns `{"status":"ok"}` on HTTP port `5666`.
- `frontend/` contains the Vite React TypeScript client. The status page calls the backend health endpoint
  and runs on HTTP port `8444`.
- Datasette is a managed dev service for browsing the live SQLite database in the `chess-database`
  Docker volume. It runs on HTTP port `8666` (see `docs/DEVELOPMENT_SERVICES.md`).
- `tests/e2e/` contains Playwright browser tests. Backend tests live under `backend/tests/`; component
  tests live beside frontend features.
- Do not use ports 5666, 8444, and 8666 for unrelated services.

## Shell

Use Git Bash only. Use forward slashes in paths (for example `.venv/Scripts/python.exe`), not backslashes. Every
command has an explicit finite timeout. If a command fails, report the exact command and failure.

## Application commands

All commands run from the repository root as `uv run --no-sync sg ...` (the `sg` developer CLI).

- Services (start, stop, status, logs, data refresh, first-time setup): see
  [`docs/DEVELOPMENT_SERVICES.md`](docs/DEVELOPMENT_SERVICES.md).
- Tests, the full check, and screenshots: see [`docs/TESTING.md`](docs/TESTING.md).
- Python dependencies are pinned in `requirements.txt` and `uv.lock` and configured in `pyproject.toml`. The
  repository-root `package-lock.json` is authoritative for the npm workspaces.

Local Node may fall outside the `>=24 <25` engines pin. Ignore that warning.

All checks are local; do not add application CI.

## Persistent development services

The backend, frontend, worker, and Datasette run as shared, long-lived Docker Compose services. Manage them only
through `uv run --no-sync sg dev`: before any lifecycle action or browser/E2E check, run
`uv run --no-sync sg dev status` and reuse healthy services as-is. Commands, ports, day-to-day behavior, and the
full agent rules are in `docs/DEVELOPMENT_SERVICES.md`.

## Testing and module-size rules

The behavioral testing layers are pytest/API tests, Vitest plus React Testing Library component tests, and
Playwright end-to-end tests. Maintenance requires Ruff, ESLint, Prettier, and source-size limits, but Plan
implementation does not check or enforce them. A Plan may temporarily leave a source file above 500 lines or a
test above 700 lines; the separate complete check (`sg check`, see `docs/TESTING.md`) detects and repairs those
issues later.

**Mandatory safety:** every shell invocation must set an explicit finite timeout in milliseconds, and every test
must have explicit finite command-level and tool-level timeouts. Missing, zero, or non-finite timeouts are
forbidden because commands can hang. Never run an unbounded process.

## Start here

1. Read the relevant active Plan under `docs/plans/active/` when work is Plan-backed; completed Plans are
   archived under `docs/plans/done/`.
2. Before exploring source, read only the files named by the approved work or Plan stage.
3. Run only finite tests or browser scenarios that directly prove the approved behavior. Do not run lint,
   formatting, broad type/build, source-size, aggregate, or other repository-hygiene checks during Plan
   implementation unless the Plan's outcome specifically changes that tool or constraint. Complete check runs
   are separate maintenance work.

## Workspaces

`scratch/` is a user-owned temporary workspace. Preserve unrelated content and do not read or alter unrelated
paths.

Use the user-level `grilling` skill when the user requests an interview or when material decisions must be
settled before work continues.

## Safety

- Preserve unrelated worktree changes, completed historical Plans, grilling records, and master-plan records.
- Do not commit, push, or use destructive Git operations unless explicitly requested.
- Keep credentials, databases, logs, PID files, dependency directories, and generated build output out of commits.

## Development rules
- Prefer modifying, reusing, and composing existing frontend components over replacing them or creating new implementations.
- When similar UI already exists, adapt or extract the existing implementation into a reusable component instead of rebuilding the same UI from scratch.
- Preserve existing component APIs, behavior, styling, and structure unless the requested change requires altering them.
- Create a new component from scratch only when no existing component can reasonably be reused, composed, adapted, or extracted.
- Do not rewrite an existing component merely to make it cleaner, more idiomatic, or more consistent unless that refactor is part of the requested work.
