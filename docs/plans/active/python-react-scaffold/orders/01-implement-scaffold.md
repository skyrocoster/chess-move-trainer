# WORK ORDER 01 — Implement complete Windows FastAPI and Vite scaffold

- **OUTPUT:** `docs/plans/active/python-react-scaffold/orders/01-implement-scaffold.md`
- **GOAL:** Deliver the approved Python/React/TypeScript scaffold and all local proof.
- **REQUIRED STRENGTH:** Standard — Cross-stack scaffold with settled contracts and multiple local proof layers.
- **DEPENDS ON:** none

## Authorization

### Creates
- `backend/__init__.py`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/features/__init__.py`
- `backend/app/features/health/__init__.py`
- `backend/app/features/health/router.py`
- `backend/app/features/health/schemas.py`
- `backend/tests/__init__.py`
- `backend/tests/features/__init__.py`
- `backend/tests/features/health/test_health.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/index.html`
- `frontend/tsconfig.json`
- `frontend/tsconfig.app.json`
- `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`
- `frontend/vitest.config.ts`
- `frontend/eslint.config.js`
- `frontend/.prettierrc.json`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/app.css`
- `frontend/src/features/status/statusApi.ts`
- `frontend/src/features/status/StatusPage.tsx`
- `frontend/src/features/status/StatusPage.test.tsx`
- `frontend/src/test-setup.ts`
- `tests/e2e/status.spec.ts`
- `tests/e2e/playwright.config.ts`
- `scripts/dev.py`
- `scripts/check_size.py`
- `setup.ps1`
- `dev.ps1`
- `check.ps1`
- `pyproject.toml`
- `requirements.txt`
- `docs/grilling-docs/python-react-scaffold-decisions.md`

### Edits
- `AGENTS.md`
- `README.md`
- `.gitignore`

### Removes
- none

## Context inputs
1. `AGENTS.md` — whole file
   - Purpose: Preserve and extend repository operating instructions.
2. `docs/README.md` — whole file
   - Purpose: Respect the documentation router and canonical references.
3. `.github/workflows/docs-contract.yml` — whole file
   - Purpose: Preserve the existing docs-only workflow without adding application CI.

## Known facts
- Windows-only support; Python 3.12 and Node 22 LTS are the supported declarations.
- FastAPI serves GET /api/health on port 5666 and returns typed JSON exactly {status: ok}.
- CORS allows only http://localhost:8444; frontend runs on port 8444.
- scripts/dev.py supports backend, frontend, and all and destructively terminates listeners on exact required ports before starting.
- Handwritten Python/TS/TSX is limited to 300 lines and handwritten tests to 500; generated manifests/lockfiles and narrow configuration files are excluded.
- Preserve existing workflow scripts, the docs-only GitHub workflow, and all exclusions in the Plan.
- The historical record must reproduce the supplied original request, Q1-Q21 choices and rationales, confirmed decisions, repository evidence, exclusions, and completion rationale, and is historical evidence only.

## Ordered actions
1. **file** (`backend/__init__.py`, `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/features/__init__.py`, `backend/app/features/health/__init__.py`, `backend/app/features/health/router.py`, `backend/app/features/health/schemas.py`, `backend/tests/__init__.py`, `backend/tests/features/__init__.py`, `backend/tests/features/health/test_health.py`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/index.html`, `frontend/tsconfig.json`, `frontend/tsconfig.app.json`, `frontend/tsconfig.node.json`, `frontend/vite.config.ts`, `frontend/vitest.config.ts`, `frontend/eslint.config.js`, `frontend/.prettierrc.json`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/app.css`, `frontend/src/features/status/statusApi.ts`, `frontend/src/features/status/StatusPage.tsx`, `frontend/src/features/status/StatusPage.test.tsx`, `frontend/src/test-setup.ts`, `tests/e2e/status.spec.ts`, `tests/e2e/playwright.config.ts`, `scripts/dev.py`, `scripts/check_size.py`, `setup.ps1`, `dev.ps1`, `check.ps1`, `pyproject.toml`, `requirements.txt`, `docs/grilling-docs/python-react-scaffold-decisions.md`) — Create the feature-first application scaffold, Windows entry points, manifests, size checker, and tests.
2. **file** (`AGENTS.md`, `README.md`, `.gitignore`) — Document architecture, commands, ports, testing layers, limits, destructive behavior, and required ignores.

## Exact proof commands

### Proof 1 — Check the documentation contract.
Working directory: `.`

```text
.venv/Scripts/python.exe scripts/check_docs.py --check
```

### Proof 2 — Run backend tests.
Working directory: `.`

```text
.venv/Scripts/python.exe -m pytest
```

### Proof 3 — Run frontend Vitest and RTL tests.
Working directory: `.`

```text
npm run test --prefix frontend -- --run
```

### Proof 4 — Run ESLint.
Working directory: `.`

```text
npm run lint --prefix frontend
```

### Proof 5 — Run Prettier verification.
Working directory: `.`

```text
npm run format:check --prefix frontend
```

### Proof 6 — Run frontend type/build verification.
Working directory: `.`

```text
npm run build --prefix frontend
```

### Proof 7 — Run live Playwright success and unavailable-backend scenarios.
Working directory: `.`

```text
frontend/node_modules/.bin/playwright.cmd test tests/e2e
```

### Proof 8 — Enforce handwritten source and test line limits.
Working directory: `.`

```text
.venv/Scripts/python.exe scripts/check_size.py --source-max 300 --test-max 500
```

## Acceptance handoff

### Coordinator
- Confirm exact ports, health response, CORS allow-list, launcher modes, destructive termination, and no application CI.
- Confirm setup, unit/component, build, size, documentation, and Playwright proof results.
- Confirm only approved paths changed and historical record preserves all supplied Q1-Q21 material.

### Validator
- Independently exercise the live accessible status success and backend-unavailable states.
- Independently confirm exact port behavior and absence of application GitHub Actions.

## Exclusions
- Do not modify existing workflow-script behavior.
- Do not add Docker, database/persistence, authentication, authorization, CRUD, deployment, or application CI.
- Do not access scratch or commit, push, dispatch, validate, or reconcile.

## Escalate if
- A required dependency peer conflict would change a selected major version or tooling.
- The supplied Q1-Q21 ledger cannot be reproduced losslessly; never invent missing historical content.
- A requested implementation requires an unapproved path, contract, platform, or adjacent feature.
- A destructive port operation cannot be limited to ports 5666 and 8444.

## Canonical compile packet

```json
{
  "identity": {
    "number": "01",
    "slug": "implement-scaffold",
    "title": "Implement complete Windows FastAPI and Vite scaffold",
    "goal": "Deliver the approved Python/React/TypeScript scaffold and all local proof."
  },
  "depends_on": [],
  "required_strength": {
    "level": "Standard",
    "reason": "Cross-stack scaffold with settled contracts and multiple local proof layers."
  },
  "authorization": {
    "creates": [
      "backend/__init__.py",
      "backend/app/__init__.py",
      "backend/app/main.py",
      "backend/app/features/__init__.py",
      "backend/app/features/health/__init__.py",
      "backend/app/features/health/router.py",
      "backend/app/features/health/schemas.py",
      "backend/tests/__init__.py",
      "backend/tests/features/__init__.py",
      "backend/tests/features/health/test_health.py",
      "frontend/package.json",
      "frontend/package-lock.json",
      "frontend/index.html",
      "frontend/tsconfig.json",
      "frontend/tsconfig.app.json",
      "frontend/tsconfig.node.json",
      "frontend/vite.config.ts",
      "frontend/vitest.config.ts",
      "frontend/eslint.config.js",
      "frontend/.prettierrc.json",
      "frontend/src/main.tsx",
      "frontend/src/App.tsx",
      "frontend/src/app.css",
      "frontend/src/features/status/statusApi.ts",
      "frontend/src/features/status/StatusPage.tsx",
      "frontend/src/features/status/StatusPage.test.tsx",
      "frontend/src/test-setup.ts",
      "tests/e2e/status.spec.ts",
      "tests/e2e/playwright.config.ts",
      "scripts/dev.py",
      "scripts/check_size.py",
      "setup.ps1",
      "dev.ps1",
      "check.ps1",
      "pyproject.toml",
      "requirements.txt",
      "docs/grilling-docs/python-react-scaffold-decisions.md"
    ],
    "edits": [
      "AGENTS.md",
      "README.md",
      ".gitignore"
    ],
    "removes": []
  },
  "context": [
    {
      "path": "AGENTS.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Preserve and extend repository operating instructions."
    },
    {
      "path": "docs/README.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Respect the documentation router and canonical references."
    },
    {
      "path": ".github/workflows/docs-contract.yml",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Preserve the existing docs-only workflow without adding application CI."
    }
  ],
  "known_facts": [
    "Windows-only support; Python 3.12 and Node 22 LTS are the supported declarations.",
    "FastAPI serves GET /api/health on port 5666 and returns typed JSON exactly {status: ok}.",
    "CORS allows only http://localhost:8444; frontend runs on port 8444.",
    "scripts/dev.py supports backend, frontend, and all and destructively terminates listeners on exact required ports before starting.",
    "Handwritten Python/TS/TSX is limited to 300 lines and handwritten tests to 500; generated manifests/lockfiles and narrow configuration files are excluded.",
    "Preserve existing workflow scripts, the docs-only GitHub workflow, and all exclusions in the Plan.",
    "The historical record must reproduce the supplied original request, Q1-Q21 choices and rationales, confirmed decisions, repository evidence, exclusions, and completion rationale, and is historical evidence only."
  ],
  "actions": [
    {
      "kind": "file",
      "paths": [
        "backend/__init__.py",
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/features/__init__.py",
        "backend/app/features/health/__init__.py",
        "backend/app/features/health/router.py",
        "backend/app/features/health/schemas.py",
        "backend/tests/__init__.py",
        "backend/tests/features/__init__.py",
        "backend/tests/features/health/test_health.py",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/index.html",
        "frontend/tsconfig.json",
        "frontend/tsconfig.app.json",
        "frontend/tsconfig.node.json",
        "frontend/vite.config.ts",
        "frontend/vitest.config.ts",
        "frontend/eslint.config.js",
        "frontend/.prettierrc.json",
        "frontend/src/main.tsx",
        "frontend/src/App.tsx",
        "frontend/src/app.css",
        "frontend/src/features/status/statusApi.ts",
        "frontend/src/features/status/StatusPage.tsx",
        "frontend/src/features/status/StatusPage.test.tsx",
        "frontend/src/test-setup.ts",
        "tests/e2e/status.spec.ts",
        "tests/e2e/playwright.config.ts",
        "scripts/dev.py",
        "scripts/check_size.py",
        "setup.ps1",
        "dev.ps1",
        "check.ps1",
        "pyproject.toml",
        "requirements.txt",
        "docs/grilling-docs/python-react-scaffold-decisions.md"
      ],
      "instruction": "Create the feature-first application scaffold, Windows entry points, manifests, size checker, and tests."
    },
    {
      "kind": "file",
      "paths": [
        "AGENTS.md",
        "README.md",
        ".gitignore"
      ],
      "instruction": "Document architecture, commands, ports, testing layers, limits, destructive behavior, and required ignores."
    }
  ],
  "proof": [
    {
      "cwd": ".",
      "command": ".venv/Scripts/python.exe scripts/check_docs.py --check",
      "purpose": "Check the documentation contract."
    },
    {
      "cwd": ".",
      "command": ".venv/Scripts/python.exe -m pytest",
      "purpose": "Run backend tests."
    },
    {
      "cwd": ".",
      "command": "npm run test --prefix frontend -- --run",
      "purpose": "Run frontend Vitest and RTL tests."
    },
    {
      "cwd": ".",
      "command": "npm run lint --prefix frontend",
      "purpose": "Run ESLint."
    },
    {
      "cwd": ".",
      "command": "npm run format:check --prefix frontend",
      "purpose": "Run Prettier verification."
    },
    {
      "cwd": ".",
      "command": "npm run build --prefix frontend",
      "purpose": "Run frontend type/build verification."
    },
    {
      "cwd": ".",
      "command": "frontend/node_modules/.bin/playwright.cmd test tests/e2e",
      "purpose": "Run live Playwright success and unavailable-backend scenarios."
    },
    {
      "cwd": ".",
      "command": ".venv/Scripts/python.exe scripts/check_size.py --source-max 300 --test-max 500",
      "purpose": "Enforce handwritten source and test line limits."
    }
  ],
  "acceptance_handoff": {
    "coordinator": {
      "requirements": [
        "Confirm exact ports, health response, CORS allow-list, launcher modes, destructive termination, and no application CI.",
        "Confirm setup, unit/component, build, size, documentation, and Playwright proof results.",
        "Confirm only approved paths changed and historical record preserves all supplied Q1-Q21 material."
      ]
    },
    "validator": {
      "requirements": [
        "Independently exercise the live accessible status success and backend-unavailable states.",
        "Independently confirm exact port behavior and absence of application GitHub Actions."
      ]
    }
  },
  "exclusions": [
    "Do not modify existing workflow-script behavior.",
    "Do not add Docker, database/persistence, authentication, authorization, CRUD, deployment, or application CI.",
    "Do not access scratch or commit, push, dispatch, validate, or reconcile."
  ],
  "escalate_if": [
    "A required dependency peer conflict would change a selected major version or tooling.",
    "The supplied Q1-Q21 ledger cannot be reproduced losslessly; never invent missing historical content.",
    "A requested implementation requires an unapproved path, contract, platform, or adjacent feature.",
    "A destructive port operation cannot be limited to ports 5666 and 8444."
  ],
  "output_path": "docs/plans/active/python-react-scaffold/orders/01-implement-scaffold.md"
}
```
STATUS: PENDING

EXECUTOR RESULT:
- DEVIATIONS: none
- PROOF RESULTS: pending
- DIRTY PATHS: pending
- AUTHORIZATION AUDIT: pending
- ATTEMPTS: 0
- ESCALATION: none
