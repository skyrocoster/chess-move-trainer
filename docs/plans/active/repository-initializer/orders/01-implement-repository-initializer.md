# WORK ORDER 01 — Implement repository initializer

- **OUTPUT:** `docs/plans/active/repository-initializer/orders/01-implement-repository-initializer.md`
- **GOAL:** Implement and verify the complete in-place Windows repository initializer and proof.
- **REQUIRED STRENGTH:** Standard — One cross-file outcome with cleanup, branding, Git safety, and disposable-copy proof.
- **DEPENDS ON:** none

## Authorization

### Creates
- `initialize.ps1`
- `tests/test_initialize.py`
- `tests/run-initializer-disposable-proof.ps1`

### Edits
- `package.json`
- `package-lock.json`
- `pyproject.toml`
- `frontend/package.json`
- `frontend/package-lock.json`
- `backend/app/main.py`
- `frontend/index.html`
- `frontend/src/features/status/StatusPage.tsx`
- `frontend/src/features/status/StatusPage.test.tsx`
- `tests/e2e/status.spec.ts`
- `README.md`
- `AGENTS.md`
- `docs/README.md`

### Removes
- none

## Context inputs
1. `package.json` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
2. `package-lock.json` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
3. `pyproject.toml` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
4. `frontend/package.json` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
5. `frontend/package-lock.json` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
6. `backend/app/main.py` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
7. `frontend/index.html` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
8. `frontend/src/features/status/StatusPage.tsx` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
9. `frontend/src/features/status/StatusPage.test.tsx` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
10. `tests/e2e/status.spec.ts` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
11. `README.md` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
12. `AGENTS.md` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.
13. `docs/README.md` — whole file
   - Purpose: Verified implementation or consumer context for the approved initializer outcome.

## Known facts
- initialize.ps1 is new, root-local, and never creates a sibling directory.
- Interactive prompts are default; automation supplies slug, title, description, docs brand, cleanup/history/retention choices; upstream URL is optional.
- One normalized slug updates all approved manifest and lockfile root names.
- Branding targets are FastAPI title, frontend HTML title, StatusPage heading, README, AGENTS description, and docs README; historical/workflow records stay intact.
- Validate root before mutation; cleanup is an explicit allowlist of copied application artifacts, with interactive yes default and explicit noninteractive cleanup.
- Cleanup is separate from setup.ps1 recreation and never deletes unknown ignored or workflow-tooling state.
- Default history is preserved; replacement is separately confirmed opt-in; no commits, pushes, remote mutation, fetches, or merges.
- Cancel/error retains the initializer; success asks retention and defaults to removal; retained rerun is safe.
- Use existing pytest/Vitest/Playwright layers; do not add a PowerShell test framework.

## Ordered actions
1. **file** (`initialize.ps1`) — Create the interactive/parameterized Windows initializer with root validation, allowlisted cleanup, identity/branding replacement, optional documentation-only upstream guidance, safe default history preservation, separately confirmed history opt-in, setup.ps1 handoff, and success-only retention/removal.
2. **file** (`package.json`, `package-lock.json`, `pyproject.toml`, `frontend/package.json`, `frontend/package-lock.json`) — Replace approved machine identities with one normalized slug without changing dependency pins.
3. **file** (`backend/app/main.py`, `frontend/index.html`, `frontend/src/features/status/StatusPage.tsx`, `frontend/src/features/status/StatusPage.test.tsx`, `tests/e2e/status.spec.ts`, `README.md`, `AGENTS.md`, `docs/README.md`) — Apply selected display title, description, and docs brand to approved surfaces; keep assertions coherent and preserve historical/workflow records.
4. **file** (`tests/test_initialize.py`, `tests/run-initializer-disposable-proof.ps1`) — Add focused pytest coverage and the exact Windows disposable-copy harness using available PowerShell for cleanup, identity/branding, omitted upstream, cancellation/error, retained rerun, default history preservation, explicit history opt-in, setup recreation, and temp cleanup.
5. **non-file `windows_disposable_copy_proof`** — Run the approved Windows disposable-copy proof with seeded artifacts and unknown sentinel, omitted upstream, branding, setup recreation, default history preservation, retained rerun, explicit history opt-in, and temp cleanup.

## Exact proof commands

### Proof 1 — Run initializer and existing tests.
Working directory: `.`

```text
.venv/Scripts/python.exe -m pytest
```

### Proof 2 — Verify docs contract.
Working directory: `.`

```text
.venv/Scripts/python.exe scripts/check_docs.py --check
```

### Proof 3 — Run full local gate.
Working directory: `.`

```text
powershell -ExecutionPolicy Bypass -File ./check.ps1
```

### Proof 4 — Prove cleanup, branding, safety, setup, rerun, opt-in history, and temp cleanup.
Working directory: `.`

```text
powershell -NoProfile -ExecutionPolicy Bypass -File ./tests/run-initializer-disposable-proof.ps1
```

## Acceptance handoff

### Coordinator
- GitHub-template and raw copies initialize in place without sibling output.
- Only allowlisted copied artifacts are cleaned; unknown ignored files remain and setup.ps1 separately recreates dependencies.
- Interactive and parameterized modes allow omitted upstream; cancel/error/rerun are safe.
- Default history is preserved; explicit history replacement is confirmed; remotes, commits, and pushes are untouched.
- Approved identity/branding targets change; setup.ps1 and pinned lockfiles remain; successful default completion removes initialize.ps1 only after success.

### Validator
- none

## Exclusions
- Feature/technology selection.
- Upstream synchronization or remote mutation.
- Implicit Git reset/reinit/commit/push/history replacement.
- Unknown-file deletion or copy-prevention claims.
- Historical/workflow record rewrites.
- Workflow-script behavior, product features, deployment, CI, persistence, auth, and CRUD.

## Escalate if
- History replacement needs broader Git mutation.
- Targets or cleanup require unapproved paths.
- Required Windows proof host/dependencies are unavailable; do not invent a framework.
- setup.ps1, workflow scripts, historical records, or scaffold Plan/order must change.

## Canonical compile packet

```json
{
  "identity": {
    "number": "01",
    "slug": "implement-repository-initializer",
    "title": "Implement repository initializer",
    "goal": "Implement and verify the complete in-place Windows repository initializer and proof."
  },
  "depends_on": [],
  "required_strength": {
    "level": "Standard",
    "reason": "One cross-file outcome with cleanup, branding, Git safety, and disposable-copy proof."
  },
  "authorization": {
    "creates": [
      "initialize.ps1",
      "tests/test_initialize.py",
      "tests/run-initializer-disposable-proof.ps1"
    ],
    "edits": [
      "package.json",
      "package-lock.json",
      "pyproject.toml",
      "frontend/package.json",
      "frontend/package-lock.json",
      "backend/app/main.py",
      "frontend/index.html",
      "frontend/src/features/status/StatusPage.tsx",
      "frontend/src/features/status/StatusPage.test.tsx",
      "tests/e2e/status.spec.ts",
      "README.md",
      "AGENTS.md",
      "docs/README.md"
    ],
    "removes": []
  },
  "context": [
    {
      "path": "package.json",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "package-lock.json",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "pyproject.toml",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "frontend/package.json",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "frontend/package-lock.json",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "backend/app/main.py",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "frontend/index.html",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "frontend/src/features/status/StatusPage.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "frontend/src/features/status/StatusPage.test.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "tests/e2e/status.spec.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "README.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "AGENTS.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    },
    {
      "path": "docs/README.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Verified implementation or consumer context for the approved initializer outcome."
    }
  ],
  "known_facts": [
    "initialize.ps1 is new, root-local, and never creates a sibling directory.",
    "Interactive prompts are default; automation supplies slug, title, description, docs brand, cleanup/history/retention choices; upstream URL is optional.",
    "One normalized slug updates all approved manifest and lockfile root names.",
    "Branding targets are FastAPI title, frontend HTML title, StatusPage heading, README, AGENTS description, and docs README; historical/workflow records stay intact.",
    "Validate root before mutation; cleanup is an explicit allowlist of copied application artifacts, with interactive yes default and explicit noninteractive cleanup.",
    "Cleanup is separate from setup.ps1 recreation and never deletes unknown ignored or workflow-tooling state.",
    "Default history is preserved; replacement is separately confirmed opt-in; no commits, pushes, remote mutation, fetches, or merges.",
    "Cancel/error retains the initializer; success asks retention and defaults to removal; retained rerun is safe.",
    "Use existing pytest/Vitest/Playwright layers; do not add a PowerShell test framework."
  ],
  "actions": [
    {
      "kind": "file",
      "paths": [
        "initialize.ps1"
      ],
      "instruction": "Create the interactive/parameterized Windows initializer with root validation, allowlisted cleanup, identity/branding replacement, optional documentation-only upstream guidance, safe default history preservation, separately confirmed history opt-in, setup.ps1 handoff, and success-only retention/removal."
    },
    {
      "kind": "file",
      "paths": [
        "package.json",
        "package-lock.json",
        "pyproject.toml",
        "frontend/package.json",
        "frontend/package-lock.json"
      ],
      "instruction": "Replace approved machine identities with one normalized slug without changing dependency pins."
    },
    {
      "kind": "file",
      "paths": [
        "backend/app/main.py",
        "frontend/index.html",
        "frontend/src/features/status/StatusPage.tsx",
        "frontend/src/features/status/StatusPage.test.tsx",
        "tests/e2e/status.spec.ts",
        "README.md",
        "AGENTS.md",
        "docs/README.md"
      ],
      "instruction": "Apply selected display title, description, and docs brand to approved surfaces; keep assertions coherent and preserve historical/workflow records."
    },
    {
      "kind": "file",
      "paths": [
        "tests/test_initialize.py",
        "tests/run-initializer-disposable-proof.ps1"
      ],
      "instruction": "Add focused pytest coverage and the exact Windows disposable-copy harness using available PowerShell for cleanup, identity/branding, omitted upstream, cancellation/error, retained rerun, default history preservation, explicit history opt-in, setup recreation, and temp cleanup."
    },
    {
      "kind": "non_file",
      "operation": "windows_disposable_copy_proof",
      "paths": [],
      "instruction": "Run the approved Windows disposable-copy proof with seeded artifacts and unknown sentinel, omitted upstream, branding, setup recreation, default history preservation, retained rerun, explicit history opt-in, and temp cleanup."
    }
  ],
  "proof": [
    {
      "cwd": ".",
      "command": ".venv/Scripts/python.exe -m pytest",
      "purpose": "Run initializer and existing tests."
    },
    {
      "cwd": ".",
      "command": ".venv/Scripts/python.exe scripts/check_docs.py --check",
      "purpose": "Verify docs contract."
    },
    {
      "cwd": ".",
      "command": "powershell -ExecutionPolicy Bypass -File ./check.ps1",
      "purpose": "Run full local gate."
    },
    {
      "cwd": ".",
      "command": "powershell -NoProfile -ExecutionPolicy Bypass -File ./tests/run-initializer-disposable-proof.ps1",
      "purpose": "Prove cleanup, branding, safety, setup, rerun, opt-in history, and temp cleanup."
    }
  ],
  "acceptance_handoff": {
    "coordinator": {
      "requirements": [
        "GitHub-template and raw copies initialize in place without sibling output.",
        "Only allowlisted copied artifacts are cleaned; unknown ignored files remain and setup.ps1 separately recreates dependencies.",
        "Interactive and parameterized modes allow omitted upstream; cancel/error/rerun are safe.",
        "Default history is preserved; explicit history replacement is confirmed; remotes, commits, and pushes are untouched.",
        "Approved identity/branding targets change; setup.ps1 and pinned lockfiles remain; successful default completion removes initialize.ps1 only after success."
      ]
    },
    "validator": null
  },
  "exclusions": [
    "Feature/technology selection.",
    "Upstream synchronization or remote mutation.",
    "Implicit Git reset/reinit/commit/push/history replacement.",
    "Unknown-file deletion or copy-prevention claims.",
    "Historical/workflow record rewrites.",
    "Workflow-script behavior, product features, deployment, CI, persistence, auth, and CRUD."
  ],
  "escalate_if": [
    "History replacement needs broader Git mutation.",
    "Targets or cleanup require unapproved paths.",
    "Required Windows proof host/dependencies are unavailable; do not invent a framework.",
    "setup.ps1, workflow scripts, historical records, or scaffold Plan/order must change."
  ],
  "output_path": "docs/plans/active/repository-initializer/orders/01-implement-repository-initializer.md"
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
