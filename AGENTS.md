# AI Instructions: Chess Move Trainer
Windows-only FastAPI + Vite React TypeScript application for training chess moves. The repository also
contains a small, role-based coordinator workflow. Use plain English and do not assume the user is an
expert. You will sometimes drift into overly technical language or skip real-world examples — when you
notice this, stop and rewrite with plain wording and concrete examples. Ground explanations in this
repository's actual files, commands, and behavior; do not use metaphors or invented analogies to explain
things that can be shown directly.

## Application architecture

- `backend/` contains the FastAPI/Pydantic service. The health feature owns `GET /api/health`, which
  returns `{"status":"ok"}` on HTTP port `5666`.
- `frontend/` contains the Vite React TypeScript client. The status page calls the backend health endpoint
  and runs on HTTP port `8444`.
- `tests/e2e/` contains Playwright browser tests. Backend tests live under `backend/tests/`; component
  tests live beside frontend features.
- Do not use ports 5666 and 8444 for unrelated services.

## Graphify catalogue

For orientation, dependency tracing, ownership discovery, or work across repository boundaries, consult
`docs/graphify/README.md`. A small edit in a known file does not require opening Graphify. The catalogue is
advisory only: source code, this `AGENTS.md`, and active Plans remain authoritative. Graphify uses local,
deterministic code-only AST extraction without an API or LLM; Markdown and YAML are not graph inputs. The
core-data layer covers the complete `src/` core/worker package and its schema source, never live database
records or other runtime data.

## Windows shell

The agent's preferred shell is Git Bash. Use PowerShell for commands documented for Windows users.
Both shells use forward slashes (e.g. `.venv/Scripts/python.exe`), not backslashes. PowerShell commands
must use `$(...)` for subexpressions, ASCII punctuation, and no `&&` or `||` operators. If a shell
command fails, report the exact command and failure.

## Application commands

- `powershell -ExecutionPolicy Bypass -File ./dev.ps1 start` starts the backend, frontend, worker, and Storybook in
  detached Docker containers. Replace `start` with `stop`, `restart`, `rebuild`, `status`, or `logs`; append one
  of `backend`, `frontend`, `worker`, or `storybook` to target a single service.
- `.venv/Scripts/python.exe -m pytest backend/tests tests` runs the Python suites.
- Python dependencies are pinned in `requirements.txt` and configured in `pyproject.toml`. The repository-root
  `package-lock.json` is authoritative for the npm workspaces.

Local Node may fall outside the `>=24 <25` engines pin. Ignore that warning and the non-fatal Storybook
`build-storybook` teardown libuv assertion.

All checks are local; do not add application CI.

## Persistent development services

The backend, frontend, worker, and Storybook run as shared, long-lived Docker Compose services. Manage them only through
`dev.ps1`: before any lifecycle action or browser/E2E check, run `dev.ps1 status` and reuse healthy services
as-is. Commands, ports, day-to-day behavior, and the full agent rules are in `docs/DEVELOPMENT_SERVICES.md`.

## Testing and module-size rules

The behavioral testing layers are pytest/API tests, Vitest plus React Testing Library component tests, and
Playwright end-to-end tests. Maintenance requires Ruff, ESLint, Prettier, and source-size limits, but Plan
implementation does not check or enforce them. A Plan may temporarily leave a source file above 500 lines or a
test above 700 lines; the separate complete test/fix maintenance run detects and repairs those issues later.

**Mandatory safety:** every `bash` invocation must set an explicit finite timeout in milliseconds, and every test
must have explicit finite command-level and tool-level timeouts. Missing, zero, or non-finite timeouts are
forbidden because commands can hang. Never run an unbounded process.

## Start here

1. Read the relevant active Plan under `docs/plans/active/` when work is Plan-backed; completed Plans are
   archived under `docs/plans/done/`.
2. Before exploring source, read only the files named by the approved work or Plan stage.
3. Run only finite tests or browser scenarios that directly prove the approved behavior. Do not run lint,
   formatting, broad type/build, source-size, aggregate, or other repository-hygiene checks during Plan
   implementation unless the Plan's outcome specifically changes that tool or constraint. Complete test/fix runs
   are separate maintenance work outside the implementation workflow.

## Workspaces

`scratch/` is a user-owned temporary workspace. Preserve unrelated content and do not read or alter unrelated
paths. Early HTML mock-ups, catalogues, optional design notes, and prototypes belong under `experiments/`, which
has its own manifests and ignored environments and artifacts. The design loop that turns an `experiments/`
mock-up into an approved Storybook candidate is defined in the Coordinator workflow skills.

## Working modes

This repository has two working modes: **God** and **Coordinator**.

- **God (default):** every session where the coordinator agent was not invoked. Work directly on the request
  using the application, command, and safety rules above. When a request is substantial enough that the
  role-based workflow would help, suggest moving it to the coordinator; do not assume that role yourself.
- **Coordinator:** runs only when the user explicitly invokes the coordinator agent, or when a coordinator
  session dispatches one of its subagents. Its routing, scope, Plan, direct, and design-exploration behavior
  lives in `.opencode/agents/coordinator.md` and its skills, and does not apply to God sessions.

Both modes use the `grilling` skill (`.opencode/skills/grilling/SKILL.md`): use it when the
user requests an interview or when material decisions must be settled before work continues.

## Safety

- Preserve unrelated worktree changes, completed historical Plans, grilling records, and master-plan records.
- Do not commit, push, or use destructive Git operations unless explicitly requested.
- Do not edit product source for workflow cleanup.
- Keep credentials, databases, logs, PID files, dependency directories, and generated build output out of commits.

## Workflow assets

`.opencode/` contains the Coordinator agent and its subagents and skills. Those assets belong to the
Coordinator workflow; God sessions use them only where `.opencode/agents/god.md` names them directly.

## Development rules
- Prefer modifying, reusing, and composing existing frontend components over replacing them or creating new implementations.
- When similar UI already exists, adapt or extract the existing implementation into a reusable component instead of rebuilding the same UI from scratch.
- Preserve existing component APIs, behavior, styling, and structure unless the requested change requires altering them.
- Create a new component from scratch only when no existing component can reasonably be reused, composed, adapted, or extracted.
- Do not rewrite an existing component merely to make it cleaner, more idiomatic, or more consistent unless that refactor is part of the requested work.
