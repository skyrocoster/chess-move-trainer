# Python/React Scaffold — Windows-only local application foundation

> **Status:** Approved; one ordered stage is ready for bounded order compilation.

- **Read trigger:** Open this Plan before implementing the initial FastAPI/Vite scaffold, its local
  entry points, tests, or architecture documentation.

## What we're building & why

Create a small, feature-first Windows application scaffold that is easy for humans and AI agents to
navigate. It will provide a typed FastAPI health contract, a Vite React status page consuming that
contract, deterministic local startup and checks, layered tests, pinned dependencies, and explicit
module-size limits.

The scaffold deliberately stops before product CRUD, persistence, authentication, or deployment. The
historical grilling record is evidence of the decisions that led here; it is not implementation
authority.

## Stages

1. **ORDERED** — Build and verify the complete backend/frontend scaffold, Windows scripts, toolchain,
   tests, size checks, architecture documentation, and historical grilling record. Partial delivery is
   not an independently acceptable shipment.

## Shipped

| Stage | What shipped (≤2 sentences) |
|-------|------------------------------|

## Touches

- `AGENTS.md`
- `README.md`
- `docs/**`
- `scripts/**`
- `*`

## Compiler handoff

### Stage 1

- **Verified edit sites:** The repository currently has no application implementation or application
  manifests. Existing contracts are `AGENTS.md`, `docs/README.md`, `docs/PLAN_TEMPLATE.md`, and the
  docs-only `.github/workflows/docs-contract.yml`; existing `scripts/*.py` are workflow tooling and
  must remain invoke-only. New owning symbols/paths are:
  - `backend/app/main.py` — FastAPI application and CORS registration.
  - `backend/app/features/health/schemas.py` — typed `HealthResponse`.
  - `backend/app/features/health/router.py` — `GET /api/health`.
  - `frontend/src/features/status/statusApi.ts` — fetch and response validation.
  - `frontend/src/features/status/StatusPage.tsx` — loading, success, and failure state flow.
  - `scripts/dev.py` — `backend`, `frontend`, and `all` dispatch, exact-port discovery/termination,
    and subprocess startup.
  - `scripts/check_size.py` — handwritten source/test line-limit enforcement.
- **Verified tests:** No application tests currently exist. Create
  `backend/tests/features/health/test_health.py`,
  `frontend/src/features/status/StatusPage.test.tsx`, and `tests/e2e/status.spec.ts`.
- **Settled contracts:** Python 3.12 and Node 22 LTS; backend `http://localhost:5666`; frontend
  `http://localhost:8444`; `GET /api/health` returns typed JSON exactly `{"status":"ok"}`;
  CORS allows only `http://localhost:8444`; `scripts/dev.py` accepts exactly `backend`, `frontend`,
  and `all`; startup forcibly terminates listeners on required ports; `setup.ps1` installs Playwright
  Chromium; accessible frontend heading and status/error region are required.
- **Dependency/tool pins:** Start with Python pins `fastapi==0.115.6`, `pydantic==2.10.5`,
  `uvicorn[standard]==0.34.0`, `pytest==8.3.4`, `httpx==0.28.1`, and `ruff==0.9.4`.
  Start with React `19.0.0`, React DOM `19.0.0`, Vite `6.0.11`, TypeScript `5.7.3`,
  `@vitejs/plugin-react` `4.3.4`, Vitest `3.0.5`, jsdom `26.0.0`,
  `@testing-library/react` `16.1.0`, `@testing-library/jest-dom` `6.6.3`,
  `@testing-library/user-event` `14.6.1`, Playwright `1.50.1`, ESLint `9.19.0`, and
  Prettier `3.5.3`, plus compatible pinned ESLint React/TypeScript plugins. Peer compatibility may
  adjust patch pins only; it must not change selected major versions or tooling.
- **Commands:**
  - `powershell -ExecutionPolicy Bypass -File .\setup.ps1`
  - `powershell -ExecutionPolicy Bypass -File .\dev.ps1 backend`
  - `powershell -ExecutionPolicy Bypass -File .\dev.ps1 frontend`
  - `powershell -ExecutionPolicy Bypass -File .\dev.ps1 all`
  - `powershell -ExecutionPolicy Bypass -File .\check.ps1`
  - `.venv\Scripts\python.exe scripts/check_docs.py --check`
  - `.venv\Scripts\python.exe -m pytest`
  - `npm run test --prefix frontend -- --run`
  - `npm run lint --prefix frontend`
  - `npm run format:check --prefix frontend`
  - `npm run build --prefix frontend`
  - `frontend\node_modules\.bin\playwright.cmd test tests/e2e`
  - `.venv\Scripts\python.exe scripts/check_size.py --source-max 300 --test-max 500`
- **Acceptance:** `setup.ps1` creates `.venv`, installs pinned pip/npm dependencies, installs Chromium,
  and gives actionable prerequisite errors. The health route returns 200 and the exact body; unknown
  routes return FastAPI 404; unrelated CORS origins are rejected. The status page has accessible
  heading/status semantics and covers loading, healthy, network-failure, non-OK, malformed-response,
  and backend-unavailable states without uncaught UI errors. Playwright proves live success and
  backend-unavailable behavior. Unsupported launcher modes fail nonzero with usage text, and process
  termination failures are surfaced. Checks cover pytest, Vitest/RTL, Playwright, Ruff, ESLint,
  Prettier, frontend build/type checks, documentation, and exact source-size limits.
- **Historical record:** Create `docs/grilling-docs/` documentation preserving the original request,
  every Q1–Q21 choice and its stated recommendation rationale, all confirmed decisions, repository
  evidence, exclusions, and completion rationale. It must be labeled historical evidence only and
  explicitly grant no implementation authority. The approved grilling transcript/ledger is not
  present in the repository; order compilation must use the coordinator-supplied Q1–Q21 material and
  must escalate rather than invent any missing choice or rationale.
- **Constraints:** Preserve the docs-only GitHub workflow. Do not modify existing workflow-script
  behavior. Do not read or modify `scratch/**`. Do not add Docker, persistence, auth, CRUD, or
  application CI. Generated manifests/lockfiles and narrowly enumerated configuration files are
  excluded from size checks. The five pre-existing invoke-only workflow scripts
  (`scripts/check_docs.py`, `scripts/check_orders.py`, `scripts/new_order.py`, `scripts/order_check.py`,
  and `scripts/stage_check.py`) are an explicit legacy-tooling exclusion; new `scripts/dev.py` and
  `scripts/check_size.py` plus handwritten Python/TS/TSX and tests remain checked.
- **Open questions:** None affecting the approved outcome. The order compiler may resolve exact
  configuration filenames, Windows process APIs, and compatible patch releases within the selected
  dependency majors. It must resolve the missing Q1–Q21 historical ledger from the approved handoff;
  absence of that material is an escalation boundary, not permission to reconstruct it.

## Observable acceptance

- On a clean Windows setup, `setup.ps1` completes and `check.ps1` runs the complete local gate set.
- `dev.ps1 all` leaves the backend on port 5666 and frontend on port 8444, after terminating prior
  listeners on those ports only.
- A browser sees an accessible status page that reaches the typed health endpoint and visibly handles
  both healthy and unavailable-backend states.
- The exact commands above pass, including the documentation checker, size checker, unit/component
  suites, build, and Playwright scenario.

## Exclusions

- Docker, containers, deployment, and cloud services.
- Database, persistence, migrations, and product data models.
- Authentication and authorization.
- Product CRUD or domain features.
- Application GitHub Actions or CI changes.
- Unrelated cleanup, commits, pushes, and any `scratch/**` access.
