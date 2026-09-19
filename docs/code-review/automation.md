# Automation, tests, and operations review

Scope: `dev.ps1`, Compose/Docker files, package/test configuration, and local
quality tooling. No CI is proposed; `AGENTS.md` requires local checks only.

## P0 — Playwright can start services that repository rules forbid starting directly

`docs/DEVELOPMENT_SERVICES.md` and `AGENTS.md` require agents to manage shared
services only through `dev.ps1` and to reuse healthy services. In contrast,
`tests/e2e/playwright.config.ts` lines 40–62 gives Playwright commands that
start Uvicorn, Vite, and Storybook directly on ports 5666, 8444, and 6006.
`reuseExistingServer` reduces the chance of a collision but does not remove it;
a test run with a stopped shared stack violates the documented lifecycle and can
leave competing processes behind.

**Change candidate:** remove `webServer` process startup from Playwright and
make the test preflight check `dev.ps1 status`, failing with the documented
start command when the selected service is unavailable. If direct local startup
must remain for a developer-only mode, give it different ports and an explicit
opt-in that agents do not use.

**Tools:** Playwright global setup/preflight, PowerShell Pester tests for
`dev.ps1`, and `docker compose ps` parsing tested against real command output.

## P1 — E2E server selection and timeouts are brittle

`serverProfile()` infers selected spec files from `process.argv`. Different
Playwright invocation styles, globs, projects, retries, or future sharding can
fall back to “all” and start unnecessary services. Only Storybook receives a
`webServer` timeout; the direct backend/frontend definitions rely on defaults.

**Change candidate:** after removing direct launch, select required services by
an explicit environment value or separate Playwright projects. Give every
external command an explicit finite timeout and report the exact missing service
and address.

**Tools:** focused Playwright config tests, `tsx`/Node unit tests for profile
selection, and a short timeout smoke scenario in a disposable environment.

## P1 — Docker image inputs are not fully reproducible or verified

`backend/Dockerfile` and `frontend/Dockerfile` use floating image tags rather
than digests. The backend downloads Stockfish without a checksum (detailed in
[core-data.md](core-data.md)). The frontend image copies
`experiments/package.json` solely because the root npm workspace includes it;
this couples normal frontend image construction to a workspace the review must
not touch. A change in that manifest or the root lockfile can invalidate a
frontend build unexpectedly.

**Change candidate:** decide whether experiments is intentionally a production
workspace dependency. If not, isolate its package manager metadata from the
frontend build. Pin base images and third-party binaries by digest/hash, then
document a deliberate update procedure.

**Tools:** Docker Scout/Trivy, Syft SBOM output, `hadolint`, and reproducible
build comparison using a clean Docker cache.

## P1 — Dependency review is missing from the documented developer loop

`requirements.txt` and both npm manifests pin many packages, but the root
README only states that versions are pinned. Pinning alone does not identify
known vulnerabilities, abandoned packages, license changes, or a compromised
transitive release. The Python Graphify dependency is named `graphifyy` while
the runner invokes `python -m graphify`; that relationship should be verified
and documented so a package rename cannot break the catalogue unexpectedly.

**Change candidate:** document a periodic local dependency review command and
its triage policy. Record intentional accepted findings with version, impact,
and expiry rather than silently ignoring them. Confirm the Graphify distribution
to module mapping in a clean environment.

**Tools:** `pip-audit`, `npm audit`, `osv-scanner`, Dependabot/Renovate only if
repository policy later permits automated update proposals, and `pip inspect`.

## P2 — The repository lacks one authoritative developer command index

The root `README.md` gives a broad map but no setup, local test, API generation,
schema inspection, Graphify refresh, vulnerability review, or recovery command.
`DEVELOPMENT_SERVICES.md` is good for Docker lifecycle but does not link the
test configurations that currently bypass it. The generated schema file names a
CLI command but does not explain when it should be regenerated or reviewed.

**Change candidate:** expand the root README with a concise command index that
links to the service document and code-review inventory. Include command purpose,
prerequisites, expected output, finite timeout guidance, and whether it changes
tracked files. Keep generated-reference instructions next to their sources.

**Tools:** `just` or `mise` only if the team wants a cross-shell task runner;
otherwise retain the existing PowerShell script and npm/Python commands to avoid
another abstraction.

## P2 — Size checks exist, but their output needs a remediation queue

`tests/cleanliness/check_file_lengths.py` enforces 500 lines for production and
700 for tests, excluding generated code, data, `.opencode`, scratch, and
experiments. It correctly identifies a pressure point but reports only the
current overage. Several modules are already structurally dense even below the
limit, notably frontend analysis state and Graphify orchestration.

**Change candidate:** keep the simple limit, but write a short remediation queue
for recurring large modules and require a named owner/reason for any exception.
Do not split generated files merely to satisfy the counter.

**Tools:** the existing `check_file_lengths.py --inventory`, Radon/Lizard for
complexity trends, and Semgrep rules for duplicated exception/route patterns.
