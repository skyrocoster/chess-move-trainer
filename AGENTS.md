# AI Instructions: Chess Move Trainer

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
  stopping at the first failure with a short excerpt and a native rerun command. It is a maintenance command, not
  Plan implementation proof.
- `.venv/Scripts/python.exe scripts/check.py --full` runs the complete local maintenance suite (builds,
  Storybook, and E2E).
- `.venv/Scripts/python.exe scripts/check.py --fix` runs deterministic formatters, then the same checks;
  `--fix` stays explicit and deterministic.
- An AI may invoke `scripts/check.py --fix` without asking again only after a read-only check identifies
  deterministic formatting or lint issues; it must inspect the resulting diff and must not use `--fix` for
  semantic repair.
- Python dependencies are pinned in `requirements.txt` and configured in `pyproject.toml`. The repository-root
  `package-lock.json` is authoritative for the npm workspaces.

Local Node may exceed the `>=24 <25` engines pin. Ignore that warning and the non-fatal Storybook
`build-storybook` teardown libuv assertion.

All checks are local. The existing GitHub workflow is documentation-only; do not add application CI.

## Testing and module-size rules

The behavioral testing layers are pytest/API tests, Vitest plus React Testing Library component tests, and
Playwright end-to-end tests. Maintenance requires Ruff, ESLint, Prettier, and source-size limits, but Plan
implementation does not check or enforce them. A Plan may temporarily leave a source file above 500 lines or a
test above 700 lines; the separate complete test/fix maintenance run detects and repairs those issues later.

**Mandatory safety:** every test must have an explicit finite command-level timeout and finite tool-level timeout.
Never run an unbounded process.

## Start here

1. Open the [documentation router](docs/README.md).
2. Read the relevant active Plan under `docs/plans/active/` when work is Plan-backed.
3. Read only the files named by the approved case or Plan stage before exploring source.
4. Run only finite tests or browser scenarios that directly prove the approved behavior. Do not run lint,
   formatting, broad type/build, source-size, aggregate, or other repository-hygiene checks during Plan
   implementation unless the Plan's outcome specifically changes that tool or constraint. Complete test/fix runs
   are separate maintenance work outside the implementation workflow.

`Scratch/` is a user-owned temporary workspace. Preserve unrelated content and do not read or alter unrelated
paths. Early HTML mock-ups, catalogues, optional design notes, and prototypes belong under `experiments/`, which
has its own manifests and ignored environments and artifacts. Once an HTML direction is selected, rebuild it in
the existing production Storybook with real components, tokens, styles, and accessibility behavior. Keep that
candidate isolated from application routes, state, data, and APIs until the user explicitly approves integration.

## Working modes

These modes apply when working as the coordinator or one of its subagents. Regular build mode does not use this
role-based workflow.

- **Coordinator workflow:** repository-dependent work enters through `.opencode/agents/coordinator.md`.
  The coordinator owns routing, scope, workflow records, design-exploration decisions and sign-off, acceptance,
  and repair-loop interruption. If you are not set to this agent, do not assume the role.
- **Grilling:** substantial research or decisions may produce one freely structured synthesis under
  `docs/grilling-docs/`; there is no mandatory grilling or document chain.
- **Plan:** nontrivial implementation uses one focused Plan as an implementation instrument. It records
  semantic scope, expected areas and exclusions, sequential AI-focused stages, ordered actions, focused
  proof, escalation boundaries, progress, breakpoint decisions, and one visible-result line. No stages run
  in parallel. Oversized stages may be split without human approval when the outcome is unchanged.
- **Direct:** small, settled changes can execute without a Plan. The approved case-worker performs the
  change and focused proof.
- **Quality:** optional validation requested separately from implementation is read-only. It independently audits
  retained proof and runs only missing or invalidated checks. A coordinator-authorized repair uses the Quality fix
  route, followed by fresh-session final validation of evidence invalidated by the repair. After one failed repair,
  return to the coordinator. Unrelated failures are reported, not absorbed.
- **Design exploration:** start with a basic self-contained HTML mock-up under `experiments/`, then, after the user
  selects a direction, rebuild and iterate on it in the existing production Storybook. Storybook candidates use real
  frontend tools but remain design work until the user approves integration. Do not require a Plan or `DESIGN.md`
  for this design loop. After approval, assess and Plan only the remaining application integration when its size
  warrants a Plan. The Exploration Agent owns disposable artifacts under `experiments/`; an approved case-worker
  owns production-backed Storybook changes.

  This workflow uses the repository's current checkout in place. Do not create or switch Git branches, worktrees,
  stashes, or commits as design-workflow steps unless the user explicitly asks for that Git operation.

The coordinator may approve scope expansion needed for the settled outcome unless behavior, direction, contracts,
destructive effects, or dependencies change. Human pauses are reserved for genuine product or visual decisions.
User edits during exploration or a visual breakpoint are authoritative and must be bounded, incorporated,
validated when applicable, and carried forward.

## Documentation contract

- Current Plans live under `docs/plans/active/<feature>/<feature>.md`; completed Plans move to
  `docs/plans/done/<feature>/`.
- `docs/PLAN_TEMPLATE.md` and `docs/MASTER_PLAN_TEMPLATE.md` are compact output schemas. Detailed guidance
  belongs in the planning skills.
- Active Plans may contain one transient `handoff.md` during context rollover. It is coordinator-reviewed,
  overwritten on rollover, and deleted at closeout.
- A selected HTML mock-up, an approved Storybook candidate, and optional design notes may provide upstream planning
  evidence. A `DESIGN.md` is never mandatory when the executable Storybook design expresses the needed decisions.
  Design approval authorizes assessment of integration, not silent application integration.
- Completed historical Plans, grilling records, and the existing master-plan records are preserved unchanged.

## Safety

- Preserve unrelated worktree changes.
- Do not commit, push, or use destructive Git operations unless explicitly requested.
- Do not edit product source for workflow cleanup.
- Keep credentials, databases, logs, PID files, dependency directories, and generated build output out of commits.

## Workflow assets

`.opencode/` contains the coordinator, cheap Scout, selectable Flash/Luna case-workers, one Quality Agent, one
Exploration Agent, browser-proof guidance, and planning skills. Design exploration is coordinator-owned through
`design-exploration`: the Exploration Agent produces disposable HTML evidence, and a case-worker uses
`frontend-component-iteration` for the production-backed Storybook design loop before integration.
