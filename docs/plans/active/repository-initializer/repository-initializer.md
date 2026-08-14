# Repository Initializer — Convert a copied scaffold in place

> **Status:** Approved; one ordered stage is ready for bounded order compilation.

- **Read trigger:** Open this Plan before implementing the Windows initializer or changing the
  scaffold's project identity, branding, copy cleanup, or repository setup guidance.

## What we're building & why

Add a root `initialize.ps1` that turns either a GitHub template copy or a raw filesystem copy of this
Windows scaffold into a new project in the current directory. It will collect or accept project identity
and branding, clean known generated state already present in a raw copy, preserve Git history by default,
and leave `setup.ps1` plus pinned lockfiles as the dependency recreation contract.

The initializer is deliberately bounded: it does not select technologies or features, create a sibling
directory, synchronize an upstream repository, mutate Git remotes, or perform implicit destructive Git
operations. The existing scaffold workflow and historical records remain authoritative for their own
purposes.

## Stages

1. **ORDERED** — Implement and verify the in-place initializer, identity and branding replacement,
   explicit cleanup and Git safeguards, optional upstream guidance, retention/removal behavior, and
   disposable-copy proof. Partial delivery is not an independently acceptable reusable-template flow.

## Shipped

| Stage | What shipped (≤2 sentences) |
|-------|------------------------------|

## Touches

- `*.ps1`
- `package.json`
- `package-lock.json`
- `pyproject.toml`
- `frontend/**`
- `backend/app/main.py`
- `tests/**`
- `README.md`
- `AGENTS.md`
- `docs/**`

## Compiler handoff

### Stage 1

- **Verified edit sites:** `initialize.ps1` is a new root file and must operate only on the current
  repository. It must validate the root and required scaffold files before mutation, gather a validated
  machine slug, display title, description, documentation brand, optional upstream URL, cleanup choice,
  history choice, and initializer-retention choice, then perform the bounded flow described below.
  `package.json:name` is currently `windows-fastapi-vite-scaffold-tools`; `package-lock.json:name` and
  `packages[""].name` have the same value. `pyproject.toml:[project].name` is currently
  `windows-fastapi-vite-scaffold`. `frontend/package.json:name` and both corresponding frontend lockfile
  root names are currently `windows-fastapi-vite-scaffold`. The approved default is to replace all four
  machine package/project names with one normalized project slug.
- **Verified branding sites:** `backend/app/main.py:create_app` uses
  `FastAPI(title="Python React Scaffold")`; `frontend/index.html` line 6 uses `<title>Service Status</title>`;
  `frontend/src/features/status/StatusPage.tsx` line 36 renders `<h1 id="page-title">Service status</h1>`;
  `README.md` lines 1 and 3 contain the scaffold title and description; `AGENTS.md` lines 1 and 3–5
  contain the project heading and application description; and `docs/README.md` lines 13–16 contain the
  adopting-project guidance. Display title and documentation brand replacements must keep these surfaces
  coherent. `docs/grilling-docs/python-react-scaffold-decisions.md` and the existing scaffold Plan/order
  are historical/workflow records and must not be rewritten as derived-project branding.
- **Verified tests and consumers:** `frontend/src/features/status/StatusPage.test.tsx` checks the status
  heading/state flow, and `tests/e2e/status.spec.ts` checks the live heading `Service status` and
  accessible success/error states. If the initializer customizes the heading, these template assertions
  must remain coherent. Existing test layers are pytest, Vitest/React Testing Library, and Playwright;
  there is no PowerShell/Pester harness.
- **Settled flow and cleanup contract:** Before editing, the initializer validates that it is at the
  scaffold root and that required files exist. It displays an explicit allowlist of generated state
  already present and, interactively, asks for cleanup with a yes default. Noninteractive execution must
  explicitly request cleanup or fail before mutation. Cleanup removes only known application artifacts:
  `.venv`, root `node_modules`, `frontend/node_modules`, `dist`, `build`, `frontend/dist`,
  `frontend/build`, project `__pycache__` directories, `.pytest_cache`, `test-results`,
  `.playwright-mcp`, `.coverage`, generated logs, and PID files. It must not delete unknown ignored files
  or workflow-tooling state. This cleanup handles artifacts that a raw filesystem copy already brought
  over; it does not claim to prevent the copy operation from copying them. After initialization,
  `setup.ps1` separately recreates the Python and npm dependencies from the pinned requirements and
  lockfiles.
- **Settled safety and lifecycle contracts:** Cancellation at input or cleanup confirmation makes no
  content, dependency, or Git-history change. Invalid or incomplete parameters fail nonzero with usage
  text before mutation. Git history is preserved by default; history replacement requires a dedicated
  opt-in and confirmation, and the initializer never commits, pushes, adds/removes remotes, fetches, or
  merges. An optional upstream URL may be omitted in both modes; when supplied it is documented only as
  a manual future merge source and is not configured automatically. On success the initializer asks
  whether to retain itself, defaulting to removal. Errors retain the initializer and do not perform
  success-only removal or history replacement. A retained initializer may be run again without
  duplicating upstream guidance or silently resetting history.
- **Verified setup and proof commands:** `setup.ps1` lines 13–23 creates `.venv`, installs
  `requirements.txt`, runs root and frontend `npm install`, and installs Playwright. The existing full
  gate is `powershell -ExecutionPolicy Bypass -File .\check.ps1`; documentation proof is
  `.venv\Scripts\python.exe scripts/check_docs.py --check`; the focused initializer suite will use
  `.venv\Scripts\python.exe -m pytest`. Disposable-copy live proof is a Windows PowerShell scenario
  that copies to a temporary directory, seeds known generated paths, invokes the initializer with
  explicit parameters, verifies cleanup/branding/history/retention, runs `setup.ps1`, and removes the
  temporary directory; it is proof, not product behavior.
- **Constraints:** Keep `setup.ps1` and both pinned lockfiles present and authoritative. Do not modify
  existing workflow-script behavior. Do not read or modify `scratch/**`. Do not add feature selection,
  technology selection, synchronization, application CI, Docker, persistence, auth, CRUD, commits, or
  pushes. Use only the listed cleanup paths and preserve unrelated worktree changes.
- **Open questions:** Resolve exact parameter names and Windows Git-history replacement mechanics; decide
  whether focused pytest subprocesses require `powershell.exe` or may accept an available `pwsh`; and
  settle temporary-copy quoting. These are bounded implementation lookups and must not widen the scope.

## Observable acceptance

- From a GitHub template copy or raw filesystem copy, interactive initialization runs in place and
  produces the selected identity and branding without creating a sibling directory.
- A raw copy containing the listed `.venv`, `node_modules`, cache, log, or build state shows those paths,
  removes only the approved paths after the default confirmation, and leaves unknown ignored files alone;
  `setup.ps1` then recreates dependencies separately.
- Parameterized initialization is noninteractive when all required values and explicit cleanup/history/
  retention choices are provided. An omitted upstream URL never blocks either mode.
- Cancel, invalid input, missing required parameters, and failed initialization stop safely; rerunning a
  retained initializer does not duplicate guidance, mutate remotes, or reset history.
- Default initialization preserves Git history and removes `initialize.ps1` only after all success
  conditions. Explicit history replacement remains opt-in and confirmed.
- The exact package/project identity, FastAPI title, frontend title/heading, README, AGENTS, and adopting
  documentation surfaces contain the selected values, while historical/workflow records remain intact.
- `setup.ps1` and pinned lockfiles remain available, and the initialized result contains no dependency,
  cache, build, log, or runtime artifact created by the initializer.

## Exclusions

- Feature or technology selection.
- Automatic upstream synchronization, merge, fetch, or remote mutation.
- Implicit Git reset, reinitialization, commit, push, or history replacement.
- Deletion of unknown ignored files or arbitrary user files.
- Preventing artifacts already copied by a raw filesystem copy; only the explicit initializer cleanup
  allowlist is in scope.
- Carrying installed dependencies, caches, build output, logs, or local runtime state into the initialized
  result.
- Rewriting `docs/grilling-docs/**` or the existing scaffold Plan/order as derived-project branding.
- Changes to existing workflow-script behavior, product features, deployment, CI, persistence,
  authentication, authorization, and CRUD.
