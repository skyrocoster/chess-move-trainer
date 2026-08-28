# AI Instructions - Chess Move Trainer

Windows-only FastAPI + Vite React TypeScript application for training chess moves. The repository also
contains a small, role-based coordinator workflow. Use plain English and do not assume the user is an
expert.

## Application architecture

- `backend/` contains the FastAPI/Pydantic service. The health feature owns `GET /api/health`, which
  returns `{"status":"ok"}` on HTTP port `5666`.
- `frontend/` contains the Vite React TypeScript client. The status page calls the backend health endpoint
  and runs on HTTP port `8444`.
- `tests/e2e/` contains Playwright browser tests. Backend tests live under `backend/tests/`; component
  tests live beside frontend features.
- `scripts/dev.py` is the Windows launcher and supports `backend`, `frontend`, and `all`.

The launcher intentionally kills any process occupying ports 5666 and 8444 before starting the requested
service. Do not use these ports for unrelated services while using the launcher.

## Windows shell

The agent's preferred shell is Git Bash. Use PowerShell for commands documented for Windows users.
Git Bash commands must use forward slashes (e.g. `.venv/Scripts/python.exe`), not backslashes.
PowerShell commands must use backslash paths, `$(...)` for subexpressions, ASCII punctuation, and no
`&&` or `||` operators. If a shell command fails, report the exact command and failure.

## Application commands

- `powershell -ExecutionPolicy Bypass -File .\setup.ps1` installs pinned Python, npm, and Playwright dependencies.
- `powershell -ExecutionPolicy Bypass -File .\dev.ps1 backend|frontend|all` starts services.
- `.venv/Scripts/python.exe scripts/check.py` runs the fast fail-first local suite: roughly two minutes,
  stopping at the first failure with a short excerpt and a native rerun command.
- `.venv/Scripts/python.exe scripts/check.py --full` runs the complete local closeout suite (builds,
  Storybook, and E2E).
- `.venv/Scripts/python.exe scripts/check.py --fix` runs deterministic formatters, then the same checks;
  `--fix` stays explicit and deterministic.
- An AI may invoke `scripts/check.py --fix` without asking again only after a read-only check identifies
  deterministic formatting or lint issues; it must inspect the resulting diff and must not use `--fix` for
  semantic repair.
- Python dependencies are pinned in `requirements.txt` and configured in `pyproject.toml`; npm uses
  `frontend\package-lock.json`.

Local Node may exceed the `>=24 <25` engines pin. Ignore that warning and the non-fatal Storybook
`build-storybook` teardown libuv assertion.

All checks are local. The existing GitHub workflow is documentation-only; do not add application CI.

## Testing and module-size rules

The testing layers are pytest/API tests, Vitest plus React Testing Library component tests, and Playwright
end-to-end tests. Ruff, ESLint, and Prettier are required. Handwritten Python, TypeScript, and TSX source
is limited to 500 lines per file; handwritten tests are limited to 700 lines. Generated manifests,
lockfiles, and narrowly enumerated configuration files are excluded by `scripts/check_size.py`.

MANDATORY SAFETY: every test must have an explicit finite command-level timeout and finite tool-level timeout. Never run unbounded processes. 

## Start here

1. Open the [documentation router](docs/README.md).
2. Read the relevant active Plan under `docs/plans/active/` when work is Plan-backed.
3. Read only the files named by the approved case or Plan stage before exploring source.
4. Use `scripts/check.py` for closeout. It is read-only unless `--fix` is explicit.

`Scratch/` is user-owned temporary workspace. Preserve unrelated Scratch content. New mock-ups and
prototypes belong under `experiments/`, which has its own manifests and ignored environments/artifacts.
Do not read or alter unrelated Scratch paths.

## Working modes

These modes are when you are working as the coordinator or the coordinators subagents. If you in a regular build mode, you do not need to follow this workflow.

- **Coordinator workflow:** repository-dependent work enters through `.opencode/agents/coordinator.md`.
  The coordinator owns routing, scope, workflow records, acceptance, and repair-loop interruption. If you are not set to this agent, do not assume the role.
- **Grilling:** substantial research or decisions may produce one freely structured synthesis under
  `docs/grilling-docs/`; there is no mandatory grilling or document chain.
- **Plan:** nontrivial implementation uses one focused Plan as an implementation instrument. It records
  semantic scope, expected areas and exclusions, sequential AI-focused stages, ordered actions, focused
  proof, escalation boundaries, progress, breakpoint decisions, and one visible-result line. No stages run
  in parallel. Oversized stages may be split without human approval when the outcome is unchanged.
- **Direct:** small, settled changes can execute without a Plan. The approved case-worker performs the
  change and proof; Quality independently validates when selected.
- **Quality:** validation is read-only. A coordinator-authorized repair uses the Quality fix route, followed
  by fresh-session final validation. After one failed repair, return to the coordinator. Unrelated failures
  are reported, not absorbed.
- **Exploration:** mock-ups and prototypes are noncanonical until explicitly adopted.

The coordinator may approve scope expansion needed for the settled outcome unless behavior, direction,
contracts, destructive effects, or dependencies change. Human pauses are reserved for genuine product or
visual decisions. User edits during a visual breakpoint are authoritative and must be bounded, incorporated,
validated, and continued.

## Documentation contract

- Current Plans live under `docs/plans/active/<feature>/<feature>.md`; completed Plans move to
  `docs/plans/done/<feature>/`.
- `docs/PLAN_TEMPLATE.md` and `docs/MASTER_PLAN_TEMPLATE.md` are compact output schemas. Detailed guidance
  belongs in the planning skills.
- Active Plans may contain one transient `handoff.md` during context rollover. It is coordinator-reviewed,
  overwritten on rollover, and deleted at closeout.
- Completed historical Plans, grilling records, and the existing master-plan records are preserved unchanged.

## Safety

- Preserve unrelated worktree changes.
- Do not commit, push, or use destructive Git operations unless explicitly requested.
- Do not edit product source for workflow cleanup.
- Keep credentials, databases, logs, PID files, dependency directories, and generated build output out of commits.

## Workflow assets

`.opencode/` contains the coordinator, cheap Scout, selectable Flash/Luna case-workers, one Quality Agent,
one Exploration Agent, browser-proof guidance, and planning skills.
