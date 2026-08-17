# AI Instructions - Chess Move Trainer

Windows-only FastAPI + Vite React TypeScript application for training chess moves.
coordinator workflow tooling. The application remains domain-neutral: it has no database, persistence,
authentication, authorization, or product CRUD.

## Application architecture

- `backend/` contains the FastAPI/Pydantic service. Modules are feature-first; the health feature owns
  `GET /api/health`, which returns `{"status":"ok"}` on HTTP port `5666`.
- `frontend/` contains the Vite React TypeScript client. Features own their API and UI behavior; the
  status page calls the backend health endpoint and runs on HTTP port `8444`.
- `tests/e2e/` contains Playwright browser tests. Backend tests live under `backend/tests/`; component
  tests live beside frontend features.
- `scripts/dev.py` is the Windows launcher and supports `backend`, `frontend`, and `all`.

The launcher intentionally kills **any process occupying ports 5666 and 8444** before starting the
requested service. This is destructive local development behavior: do not use these ports for unrelated
services while using the launcher.

## Windows shell

The agent's preferred, unrestricted shell is **Bash (Git Bash)**; use PowerShell only for commands that genuinely need it (the `.ps1` launchers a user runs natively). If any shell command fails, report the failure and the exact command for review instead of silently working around it.

For Windows/PowerShell-targeted commands (documented run commands, `.ps1` scripts, anything a user runs natively):
- Use backslash path separators for Windows paths (`.\setup.ps1`, `.venv\Scripts\python.exe`); don't normalize them to forward slashes.
- Don't use backticks for command substitution — in PowerShell the backtick is the escape/line-continuation character. Use `$(...)` only as a PowerShell subexpression, or call the supplied `.ps1`/`.py` launchers.
- Keep command text ASCII; smart quotes, emoji, and accented letters can be mangled by Windows console encoding.
- Avoid `&&`/`||` chain operators (Windows PowerShell 5.1 doesn't support them); use `;` or separate statements, or call the supplied launchers. Unix utilities (`grep`, `sed`, `awk`, `ls`, `rg`) come from Git Bash and are unaffected — only the PowerShell syntax above is restricted.

For Bash/Git Bash (the agent's own tooling and ad-hoc steps): unrestricted. Project commands should still target PowerShell so a Windows user can run them unchanged, but the agent's own execution is free to use bash.

Non-standard Git Bash commands installed via `winget` on the Windows PATH: `jq` (JSON), `yq` (YAML), `fd` (find), `bat` (cat), `fzf` (fuzzy), `tree` (tree). If one is missing, report it for review before assuming it's unavailable.

## Application commands

- `powershell -ExecutionPolicy Bypass -File .\setup.ps1` creates `.venv`, installs pinned Python/npm
  dependencies, and installs Playwright Chromium.
- `powershell -ExecutionPolicy Bypass -File .\dev.ps1 backend|frontend|all` starts services.
- `.venv\Scripts\python.exe scripts\check.py` (or `.venv/bin/python scripts/check.py` on POSIX) runs all
  local checks.
- Python dependencies are pinned in `requirements.txt` and configured in `pyproject.toml`; npm uses
  `frontend\package-lock.json`.

Local Node may exceed the `>=22 <23` engines pin (both `package.json` files); this is an accepted mismatch. Ignore engines warnings and the non-fatal Storybook `build-storybook` teardown libuv assertion.

All checks are local. The existing GitHub workflow is documentation-only; do not add application CI.

## Testing and module-size rules

The testing layers are pytest/API tests, Vitest + React Testing Library component tests, and Playwright
end-to-end tests. Ruff, ESLint, and Prettier are required quality checks. Handwritten Python, TypeScript,
and TSX source is limited to 500 lines per file; handwritten tests are limited to 700 lines. Generated
manifests/lockfiles and narrowly enumerated configuration files are excluded from the size check only.
The five pre-existing invoke-only workflow scripts (`scripts/check_docs.py`, `scripts/check_orders.py`,
`scripts/new_order.py`, `scripts/order_check.py`, and `scripts/stage_check.py`) are an explicit legacy
tooling exclusion; new `scripts/dev.py` and `scripts/check_size.py` remain subject to the source limit.

## Start Here

1. Open the [documentation router](docs/README.md).
2. Read the relevant active Plan under `docs/plans/active/` when work is Plan-backed.
3. Read only the Plan stage's **Read first** files before exploring source.
4. Run the documentation checker after documentation-impacting work:
   `.venv\Scripts\python.exe scripts\check_docs.py --check` on Windows, or
   `.venv/bin/python scripts/check_docs.py --check` on POSIX.

`scratch/` is user-owned temporary workspace. Do not explore, index, read, or update it unless the
user explicitly names a path there.

## Working Modes

- **Coordinator workflow:** repository-dependent work enters through
  `.opencode/agents/coordinator.md` and invokes `coordinator-workflow`. It owns assessment,
  route review, focused Plan and master-plan writing, bounded order authoring, and approved execution. The lifecycle
  format is defined by [docs/PLAN_TEMPLATE.md](docs/PLAN_TEMPLATE.md).
- **Planned quick stage:** a fully settled atomic Plan stage may use `implement-quick` without a
  work order when the exact edit, authorized paths, known facts, and focused proof are known. The Plan
  remains the durable record. Escalated work is compiled as an order; never widen the quick brief.
- **Bounded direct mode:** when a user requests direct implementation, proceed without a Plan or work
  order. Keep the change local, preserve unrelated worktree changes, run the applicable focused checks
  plus the documentation checker, and report changed files, checks, and residual risk.

## Documentation Contract

- Canonical project references, if an adopting repository creates them, own current contracts. Plans
  record intended changes and must not replace those references.
- Active Plans live under `docs/plans/active/<feature>/<feature>.md`; completed Plans move to
  `docs/plans/done/<feature>/`. Dependencies are declared in a Plan's `## Touches` section.
- Work orders are rendered by `scripts/new_order.py`, checked by `scripts/check_orders.py`, and may
  use `scripts/order_check.py` for explicitly supplied proof commands. `scripts/stage_check.py` runs
  documentation validation plus explicitly supplied project checks.
- The checker validates local documentation links, active-Plan metadata and touch globs, and canonical
  work-order structure. Add project-specific generators, inventories, API checks, and test contracts
  only when the adopting project has documented their owning source contract.
- The named workflow scripts are invoke-only unless you are deliberately changing that script's
  behavior. Use `--help` to learn their arguments.
- Regenerate or update only project documentation artifacts that the adopting repository actually
  defines. Do not carry forward assumptions from this skeleton.

## Project Integration

- Define application architecture, source roots, data ownership, design systems, test commands, CI
  requirements, and browser startup in the adopting repository's own documentation and configuration.
- Use browser automation only when an acceptance brief requires live UI evidence. The brief supplies
  the startup command, target URL, cleanup command, and exact scenario.
- Do not commit credentials, local databases, logs, PID files, dependency directories, or build output.

## Safety

- Preserve unrelated worktree changes.
- Do not commit, push, or use destructive Git operations unless the user explicitly requests it.
- Prefer the smallest correct change and existing local patterns.

## Available Workflow Assets

The `.opencode/` directory contains the `coordinator` agent, bounded case-worker and
validator agents, master-plan and work-order tooling, browser-validation guidance, and optional planning/UX/table-test
skills. Adopt or remove these assets deliberately; none declares an application-specific contract.
