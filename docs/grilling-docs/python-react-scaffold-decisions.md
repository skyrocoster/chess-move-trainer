# Historical grilling record: Python/React scaffold

> **Status:** Historical evidence only. This record grants no implementation authority.

## Original request

“Scaffold this repo for python/react/typescript. Proper testing folders, ready made folder structure
that is easy for an AI to understand/discourage writing massive files. Relevant virtual environment.
Set up a back-end/front-end script that kills the previous versions; do it at ports 5666 and 8444 and
ensure that is marked in agents.md”.

## Q1–Q21 choices and recommendation rationales

| Question | Choice | Stated recommendation rationale |
|---|---|---|
| Q1 | A — FastAPI | Typed, clean React pairing. |
| Q2 | A — Vite + React + TypeScript | Lightweight separated responsibilities. |
| Q3 | A — npm | Portable and avoids an extra manager. |
| Q4 | B — pytest + Vitest/RTL + Playwright | Covers unit, component, and integration layers. |
| Q5 | A — backend 5666/frontend 8444 | Preserves the request order and gives the browser-facing service the higher port. |
| Q6 | A — cross-platform-style Python launcher with backend/frontend/all commands | One process-control implementation; subsequently constrained to Windows-only support. |
| Q7 | A — enforced line limits | Active deterrence against massive files. |
| Q8 | A — 300 source/500 tests | Focused modules with test headroom. |
| Q9 | A — pyproject + pip + pinned requirements | Fewest prerequisites and `.venv` compatibility. |
| Q10 | A — health endpoint + connected status page | Domain-neutral vertical proof. |
| Q11 | C — local checks only/GitHub record keeping | No application CI. |
| Q12 | A — Ruff + ESLint + Prettier | Fast conventional quality. |
| Q13 | A — kill any process on ports | Reliable restarts; explicitly destructive. |
| Q14 | B — Windows only | Matches the confirmed platform scope. |
| Q15 | A — PowerShell bootstrap | One-command repeatable setup. |
| Q16 | A — HTTP | Avoids local certificate complexity. |
| Q17 | A — backend/, frontend/, tests/e2e/ | Obvious ownership. |
| Q18 | A — feature-first | Co-located behavior avoids central massive files. |
| Q19 | A — root setup.ps1/dev.ps1/check.ps1 | Discoverable Windows entry points. |
| Q20 | A — no Docker/database | Domain-neutral minimal scaffold. |
| Q21 | A — confirmed complete specification | Exactly the summarized specification. |

## Confirmed decisions and repository evidence

The scaffold uses FastAPI/Pydantic on HTTP port 5666 and Vite React TypeScript on HTTP port 8444.
`GET /api/health` returns typed `{"status":"ok"}` and the frontend status page consumes it. CORS is
limited to `http://localhost:8444`. Root PowerShell entry points create the Python environment, start
services, run local checks, and the Python launcher destructively clears only ports 5666 and 8444.

At decision time the repository had no application architecture, manifests, or startup scripts. Its
coordinator workflow scripts and documentation checker are preserved, the existing GitHub workflow is
docs-only, and `scratch/` is prohibited. The completion rationale was that architecture, safety,
tooling, testing, infrastructure, platform, command, and exclusion branches were settled.

## Exclusions and completion rationale

Docker, persistence/database, authentication, authorization, product CRUD, deployment, and application
GitHub Actions are excluded. This record documents why the bounded scaffold was selected; it is not a
source of implementation permission, and later implementation must follow the approved canonical order.
