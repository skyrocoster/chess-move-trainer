# Dependency and library audit — 2026-09-19

## Executive summary

This audit covers the repository's committed Python and npm manifests, both npm lockfiles present in the working copy, Docker base images, Stockfish, the generated Graphify HTML dependency, and the unpinned Playwright MCP command.

The most important findings are:

1. **The root npm lock has active critical vulnerabilities.** `npm audit` reports 14 affected package entries: 3 critical, 7 high, 2 moderate, and 2 low. The urgent fixes are Vitest `4.1.11`, Vite `6.4.3`, aligned Playwright `1.63.0`, and ESLint `9.39.5`. `@hey-api/openapi-ts@0.99.0` is the awkward exception: it is the latest release but is vulnerable through its YAML parser, while npm's safe recommendation is the older `0.97.0`.
2. **The Python graph has eight unique known advisories.** One affects `pytest`; seven affect Starlette `0.41.3`, which is forced by FastAPI `0.115.6`. Moving to FastAPI `0.141.1` resolves to Starlette `1.6.0`, beyond every listed fixed version. Pytest should move to `9.1.1`.
3. **The current Docker tags are mutable and their operating-system layers have findings.** Trivy found 44 high package/CVE rows in the current `python:3.12-slim` tag and 56 rows (52 high, 4 critical) in `node:24-bookworm-slim`. Moving Node 24 from Bookworm to Trixie reduced the latter to 43 high and zero critical in a comparison scan, but neither Trixie image was clean.
4. **Stockfish 18 is out of date.** Stockfish 19 was released on 2026-09-05. It is intended as a drop-in UCI replacement, but it has stricter position validation and will change analysis results. The repository already stores engine version and checksum and requeues stale analysis, which gives it a good migration path.
5. **Several declarations can be removed or consolidated.** `temporal-polyfill` is unused; the root Mermaid CLI is unused; the frontend copy of `@axe-core/playwright` is unused; and the explicit `@typescript-eslint/parser` and `@typescript-eslint/eslint-plugin` declarations duplicate dependencies of the only package actually imported, `typescript-eslint`.
6. **Python transitive versions are not locked.** Direct pins do not make Docker builds reproducible because dependencies such as Starlette are resolved at install time. A Python lock with hashes is the largest dependency-management improvement available.

No product source or dependency version was changed during this audit.

## Implementation progress

Implementation started on 2026-09-19. This section is updated as each group is completed and proved.

- **Completed 2026-09-19:** Python locking/runtime separation, container hardening, Stockfish 19, declaration cleanup, the audited security refreshes, the Phase 4 major migrations (TypeScript 6, ESLint 10 with the preserved pre-v7 hooks contract, Vite 8, jsdom 30/jest-dom 7), and the complete verification runbook below. Deferred latest majors remain Vitest 5 (blocked by Storybook peer support) and TypeScript 7 (blocked by `typescript-eslint`).
- **Completed:** the npm security/current-line refresh and declaration cleanup are installed in the root lock. Vitest/Playwright/Vite/ESLint are on the audited safe lines; React, Storybook, TanStack Query, and the listed same-major packages are refreshed; Mermaid CLI, the direct Temporal declaration, the duplicate frontend Axe declaration, and direct TypeScript-ESLint internals are removed. Node's floor is `24.15`, npm is declared as `12.0.2`, Playwright MCP is lock-backed, and `npm audit --json` now reports **zero vulnerabilities**.
- **Hey API decision:** the `0.97.0` trial was rejected after regeneration exposed a newer direct advisory and incompatible generated-client types. The repository remains on `0.99.0` with `js-yaml@4.3.2` forced at the lock root. Regeneration succeeds and npm audit is clean; generated/API tests are being repaired against the current backend contract before this mitigation is called proved.
- **Python lock/security completed:** runtime requirements now live in `pyproject.toml`; pytest, Ruff, Graphify, and the newly pinned `pip-audit` are in the development group. `uv.lock` locks the root and experiments projects, and `requirements.txt` is now a generated, hashed runtime-only export. FastAPI `0.141.1`, Starlette `1.6.0`, Pydantic `2.13.5`, Uvicorn `0.53.0`, pytest `9.1.1`, and the audited patch/current lines are installed. `pip-audit` reports **no known vulnerabilities** in the runtime export. A focused 124-test Python run passed 120 tests; one FastAPI route-introspection assertion has been adapted to the new lazy-router API, one Windows abandoned-mutex check is being rerun as a suspected timing flake, and the two real-engine tests were waiting for provisioning.
- **Stockfish checkpoint:** source constants, identity validation, CLI help, fixtures, and both platform assets now target Stockfish 19 without changing `CONFIGURATION_VERSION`. The Windows universal archive was downloaded, matched SHA-256 `3c8bf1f9...30b48a7`, reported `Stockfish 19`, and replaced the local Stockfish 18 runtime (the old generated runtime was retained under the approved temporary directory). The Linux Docker stage now verifies SHA-256 `9defc0d4...e03611f` before copying only the engine into the final image.
- **Container/reproducibility checkpoint:** Python and Node base tags are digest-pinned, Node moved to Trixie, npm `12.0.2` is installed explicitly, build-only Stockfish download tools no longer enter the backend final image, hashed runtime requirements are enforced, and both images now declare non-root users. The OpenCode plugin manifest/lock are intentionally tracked and refreshed to `1.18.31`.
- **Verification (final, 2026-09-19):** frontend unit 597/597, Storybook browser project 235/235, `tsc -b && vite build` green, ESLint 0 errors (5 pre-existing warnings), Prettier clean, `npm audit` zero vulnerabilities (root and `.opencode/`), `pip-audit` clean on the runtime export, Python `backend/tests tests` 952 passed / 9 skipped plus Graphify catalogue 17/17, rebuilt-service smoke (`/api/health` ok, frontend/Storybook 200), app Playwright specs 10/10 (status, shell routing, trainer practice incl. live Caro-Kann retrieval), backend runs as `app` with Linux Stockfish 19 (`id name Stockfish 19`) and the worker polls quietly as `app`, frontend runs as `node`.
- **Storybook upgrade maintenance (same date):** the Playwright 1.63/Chromium 153 + axe-core 4.13 stack required four test-only adjustments, no product changes: exact 88px choice-box heights became `>= 88` minimums, the save/remove request-log assertions now allow duplicate refreshing GETs (invalidation plus refresh-key refetch no longer dedupe to one), the Storybook canvas wrapper paints the dark application background (opaque `100vh` so axe measures real contrast), and the responsive-stage lane fixtures gained a representative button so the independently scrolling wide-mode lanes contain keyboard-focusable content. The React Hooks plugin moved 5 -> 7 with only `rules-of-hooks` + `exhaustive-deps` enabled to preserve the pre-v7 lint contract; the new compiler ruleset needs a separate refactor.
- **Pre-existing breakage found, not caused by this audit:** the 13 `repertoire-builder-storybook-behaviors` E2E specs address story IDs under `application-repertoire-builder-workspace--*`, but the catalogue holds 235 stories and none use that prefix (current IDs start `production-application-...`). `tests/e2e/` is otherwise unmodified. Remapping those stale IDs is separate test maintenance.
- **Preserved unrelated work:** the pre-existing edit to `.opencode/agents/jesus.md` has not been changed.

## Scope and interpretation

### Sources inspected

- `requirements.txt`
- `pyproject.toml`
- `experiments/pyproject.toml`
- `package.json` and the authoritative root `package-lock.json`
- `frontend/package.json`
- `experiments/package.json`
- local, ignored `.opencode/package.json` and `.opencode/package-lock.json`
- `opencode.jsonc`
- `backend/Dockerfile`, `frontend/Dockerfile`, and `compose.yaml`
- direct imports and configuration under `backend/`, `frontend/`, `src/`, `tests/`, and `.opencode/`
- the generated `docs/graphify/*/graph.html` scripts

Generated dependency directories (`node_modules`, `.venv`), user-owned `scratch/`, and unrelated artifacts were not treated as declarations. Transitive packages were covered by the lockfile/resolver vulnerability scans rather than listed one by one.

### Audit tools and date sensitivity

- `npm audit --json` and `npm outdated ... --json`
- `pip-audit` against `requirements.txt`
- PyPI and npm registry metadata for latest stable versions
- OSV queries for `vis-network` and `@playwright/mcp`
- Trivy `0.74.0` against the public image tags as they resolved on 2026-09-19
- GitHub release metadata for Stockfish 19

Registry versions, advisories, and floating container tags can change after this date. Re-run the commands in the final section immediately before implementing an upgrade.

## Vulnerability findings

### npm application/workspace lock

`npm audit` scanned 783 production, development, optional, and peer dependency entries and reported 14 affected package entries. The count is by affected package in the dependency chain, not by unique advisory.

| Affected chain | Highest severity | Advisory IDs | Safe route |
|---|---:|---|---|
| `vitest`, `@vitest/browser-playwright`, `@vitest/browser`, `@vitest/mocker` | Critical | `GHSA-2h32-95rg-cppp`, `GHSA-p63j-vcc4-9vmv`, `GHSA-g8mr-85jm-7xhm`, `GHSA-82fw-gwwq-j7x9` | Upgrade `vitest` and `@vitest/browser-playwright` together from `4.1.5` to `4.1.11`. Keep them on exactly the same version. |
| `@playwright/test` -> `playwright` | High | `GHSA-7mvr-c777-76hp` | Upgrade root `@playwright/test` and frontend `playwright` together to `1.63.0`, then reinstall the matching browser binary. |
| `vite` -> old `esbuild` | High | `GHSA-67mh-4wv8-2f99`, `GHSA-x574-m823-4x7w`, `GHSA-356w-63v5-8wf4`, `GHSA-859w-5945-r5v3`, `GHSA-xcj6-pq6g-qj4x`, `GHSA-g4jq-h2w9-997c`, `GHSA-jqfw-vq24-v9c3`, `GHSA-93m4-6634-74q7`, `GHSA-4r4m-qw57-chr8`, `GHSA-4w7w-66w2-5vf9`, `GHSA-p9ff-h696-f583`, `GHSA-v6wh-96g9-6wx3`, `GHSA-fx2h-pf6j-xcff` | First move `6.0.11` to patched Vite `6.4.3`. A later Vite 8 migration is separate. |
| `@hey-api/openapi-ts` -> `@hey-api/json-schema-ref-parser` -> `js-yaml` | High | `GHSA-52cp-r559-cp3m`, `GHSA-5p4m-2wfm-xmqj`, `GHSA-2883-xcg3-v3hh` | No patched latest generator exists. See the special handling below. |
| `eslint` -> `@eslint/plugin-kit` | Low | `GHSA-xffm-g5w8-qvg7` | Upgrade ESLint and `@eslint/js` within major 9 to `9.39.5`. |

#### `@hey-api/openapi-ts` needs special handling

The repository is already on latest `@hey-api/openapi-ts@0.99.0`, but that release pins vulnerable `@hey-api/json-schema-ref-parser@1.4.4`. `npm audit` recommends `@hey-api/openapi-ts@0.97.0`; that release uses parser `1.4.1`, which is outside the affected parser ranges.

Recommended order:

1. Treat this as an upstream-blocked security update rather than pretending latest is safe.
2. Trial `@hey-api/openapi-ts@0.97.0` in a focused change.
3. Update the version-specific comment in `frontend/openapi-ts.config.ts`.
4. Regenerate `frontend/src/api/generated/` from the same checked-in OpenAPI document and inspect the full generated diff.
5. Run the API adapter and generated-client tests. Accept the downgrade only if the generated contract and runtime behavior remain correct.
6. Track upstream and return to a patched release newer than `0.99.0` when one exists.

An npm `overrides` entry that forces a different parser or `js-yaml` can make the audit quieter, but it bypasses the generator author's exact dependency pins. Use that only after proving code generation is byte-for-byte or behaviorally equivalent; the complete-generator downgrade is the safer first trial.

The generator reads the repository's own checked-in schema, so hostile YAML/JSON input is not a normal production path. That lowers immediate exploitability but does not make the dependency chain acceptable indefinitely.

### Python dependencies

`pip-audit -r requirements.txt` reported 16 raw records in two packages. Duplicate source records reduce this to **eight unique advisories**:

| Package resolved from the current requirements | Advisory | Practical exposure here | Fix |
|---|---|---|---|
| `pytest@8.3.4` | `PYSEC-2026-1845` / `CVE-2025-71176` / `GHSA-6w46-j5rx-g56g` | The flaw concerns predictable `/tmp/pytest-of-{user}` directories on Unix. The Windows host is unaffected, but pytest is unnecessarily installed in the Linux backend/worker image. | Upgrade to `pytest@9.1.1` (fixed from `9.0.3`), and remove test tooling from runtime images. |
| `starlette@0.41.3` | `PYSEC-2026-1941` / `CVE-2025-54121` / `GHSA-2c2j-9gv5-cj73` | Multipart rollover can block the event loop. No form or upload endpoint was found, so current direct exposure is low. | Upgrade through FastAPI. |
| `starlette@0.41.3` | `PYSEC-2026-1942` / `CVE-2025-62727` / `GHSA-7f5h-v6xp-fcq8` | Range parsing denial of service in `FileResponse`/`StaticFiles`. Neither is used by this backend. | Upgrade through FastAPI. |
| `starlette@0.41.3` | `PYSEC-2026-161` / `CVE-2026-48710` / `GHSA-86qp-5c8j-p5mr` | Malformed Host values can make `request.url` disagree with routing. No security decision based on `request.url` was found. | Upgrade through FastAPI. |
| `starlette@0.41.3` | `PYSEC-2026-2281` / `CVE-2026-48818` / `GHSA-wqp7-x3pw-xc5r` | Windows `StaticFiles` UNC-path credential leak. The app is Windows-focused, but it does not mount `StaticFiles`. | Upgrade through FastAPI. |
| `starlette@0.41.3` | `PYSEC-2026-2280` / `CVE-2026-48817` / `GHSA-x746-7m8f-x49c` | `HTTPEndpoint` method dispatch. The app uses FastAPI function routers, not `HTTPEndpoint`. | Upgrade through FastAPI. |
| `starlette@0.41.3` | `PYSEC-2026-249` / `CVE-2026-54283` / `GHSA-82w8-qh3p-5jfq` | URL-encoded form limits are not enforced. No form parsing was found. | Upgrade through FastAPI. |
| `starlette@0.41.3` | `PYSEC-2026-248` / `CVE-2026-54282` / `GHSA-jp82-jpqv-5vv3` | A malformed non-slash path can poison reconstructed URL fields. No pre-routing URL authorization was found. | Upgrade through FastAPI. |

FastAPI `0.115.6` requires Starlette `<0.42`, so Starlette cannot be fixed safely in isolation. A resolver dry run with the proposed direct versions completed without conflicts and selected FastAPI `0.141.1` with Starlette `1.6.0`, which is beyond all listed fixed versions.

### Container images

These are scans of the public base tags, not of a freshly rebuilt final application image. The final image combines these findings with the Python/npm findings above and, in the backend, the apt-installed download tools.

| Image tag as resolved on 2026-09-19 | Result | Unique CVEs represented | Recommendation |
|---|---:|---|---|
| `python:3.12-slim` (Debian 13.7) | 44 high package/CVE rows, 0 critical | `CVE-2026-76642`, `CVE-2026-78408`, `CVE-2026-78409`, `CVE-2026-78410`, `CVE-2026-54369`, `CVE-2025-69720`, `CVE-2026-16742`, `CVE-2026-9538` | No fixed Debian package version was shown. Keep Python 3.12, pin a reviewed image digest, rescan periodically, and rebuild when Debian publishes fixes. |
| `node:24-bookworm-slim` (Debian 12.15) | 52 high + 4 critical OS rows | The eight CVEs above plus `CVE-2026-53613`, `CVE-2026-41992`, `CVE-2026-13221`, `CVE-2026-42496`, `CVE-2026-8376`, `CVE-2026-42497`, `CVE-2026-48962`, `CVE-2026-57432`, `CVE-2026-57433`, and `CVE-2023-45853` | Move to `node:24-trixie-slim`, rebuild, and pin its digest. |
| `node:24-trixie-slim` comparison | 43 high, 0 critical OS rows | Same eight-CVE family as the Python Trixie base, with one fewer duplicate package row | Better than Bookworm today, but not clean. Accept only with a dated risk record and rescan schedule. |

The Node image also contains four high findings in its globally bundled npm packages:

- `brace-expansion@5.0.7`: `CVE-2026-14257` and `CVE-2026-69152`; fixed in `5.0.9` on that line.
- `ip-address@10.2.0`: `CVE-2026-69192`; fixed in `10.3.1`.
- `tar@7.5.19`: `CVE-2026-73566`; fixed in `7.5.21`.

Use an updated official Node image when it carries a fixed npm, or explicitly install a reviewed npm release in the image. Current npm is `12.0.2` and requires Node `24.15+`; if it is adopted, raise the repository engine floor from `>=24` to `>=24.15` and pin the npm version in root `package.json` with `packageManager`.

The present tags are floating. On the audit date, the multi-platform tag digests were:

- `python:3.12-slim@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9`
- `node:24-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6`

Do not blindly adopt those exact digests: the Node digest is the image recommended for replacement, and both must be rescanned when implementation starts.

### Other versioned inputs

| Input | Current | Finding |
|---|---|---|
| Stockfish | 18 / `sf_18` | Latest is Stockfish 19. No vulnerability database result was available; this is an outdated native runtime and supply-chain issue rather than a reported CVE. The Linux Docker download has no checksum verification. |
| Graphify HTML `vis-network` | CDN `9.1.6` | npm latest is `10.1.2`. OSV returned no known vulnerability for `9.1.6`. The generated pages depend on unpkg at view time and have no Subresource Integrity value. |
| Playwright MCP | `npx -y @playwright/mcp@latest` | Resolves dynamically; latest was `0.0.82` and itself depends on Playwright `1.64.0-alpha-...`. OSV returned no advisory for `0.0.82`, but every launch can change the code being executed. |
| `.opencode` plugin | local `1.18.18` | Latest is `1.18.31`; its 32-package lock audited clean. The manifest and lock are ignored by Git even though `.opencode/README.md` says they manage tool dependencies. |
| apt packages | unpinned `curl`, `ca-certificates`, `tar` | Installed during backend build from a mutable Debian repository. They remain in the final image even though they are needed only to fetch/extract Stockfish. |

## Direct dependency inventory and update status

### Python

| Declaration | Current | Latest | Used by | Migration assessment |
|---|---:|---:|---|---|
| `fastapi` | 0.115.6 | 0.141.1 | `backend/app/main.py` and feature routers | **Urgent framework update** because it frees the Starlette security fix. Run all API tests and inspect generated OpenAPI. |
| `httpx` | 0.28.1 | 0.28.1 | Chess.com and opening acquisition | Current; no action. |
| `PyYAML` | 6.0.2 | 6.0.3 | database configuration loaders | Safe patch candidate. |
| `pydantic` | 2.10.5 | 2.13.5 | backend API schemas | Upgrade with FastAPI; inspect strict validation and OpenAPI diffs. |
| `pytest` | 8.3.4 | 9.1.1 | all Python tests | Security fix crosses a major. No third-party pytest plugin is declared, so risk is moderate and concentrated in test behavior. |
| `chess` | 1.11.2 | 1.11.2 | chess/FEN/PGN domain operations | Current; no runtime replacement is needed. |
| `ruff` | 0.9.4 | 0.16.8 | local maintenance | Tool-only update. Expect lint/format output changes; update separately from product dependencies. |
| `uvicorn[standard]` | 0.34.0 | 0.53.0 | backend server and reload/watchfiles | Upgrade with FastAPI. Verify reload polling in Docker and health checks. |
| `SQLAlchemy` | 2.0.52 | 2.0.54 | SQLite repositories | Safe patch candidate; run database tests. |
| `typer` | 0.27.2 | 0.27.2 | database and Stockfish CLIs | Current. |
| `cachetools` | 5.5.2 | 7.2.0 | `TTLCache` in `backend/app/caching.py` | Major jump, but the repository uses a small stable API. Prove with cache mechanics and API-cache tests. |
| `graphifyy[sql,svg]` | 0.9.61 | 0.9.64 | `src/tools/graphify_catalogue.py` | Patch candidate. Regenerate all six catalogue bundles and inspect generated output. Distribution remains `graphifyy`; module remains `graphify`. |
| `setuptools` build floor | `>=75.0` | 84.0.0 | PEP 517 build isolation | Not actually pinned. Include it in the Python lock or intentionally raise the floor after an editable-install check. |
| experiments `python-chess` | `>=1.11,<2` | 1.999 metapackage | experiment-only chess code | Normalize to the same `chess==1.11.2` distribution as the application. The two names refer to the same implementation through a metapackage and currently create needless ambiguity. |

Python `3.12` is still supported and need not be changed for these upgrades. A Python 3.13/3.14 move should be a separate compatibility project because Graphify pulls many compiled tree-sitter and scientific wheels, and `pyproject.toml`, Ruff's target, the Docker base, and local environments must move together.

### Frontend runtime npm packages

| Package | Current | Latest | Assessment |
|---|---:|---:|---|
| `@base-ui/react` | 1.7.0 | 1.8.0 | Same-major update. Exercise buttons, toolbar, drawer, popover, select, radio, and checkbox components. |
| `@fullcalendar/react` | 7.1.0 | 7.1.0 | Current. Subpath plugin/theme imports in `PreferredMoveSchedulePrototype.tsx` make a future major migration sensitive. |
| `@headless-tree/core`, `@headless-tree/react` | 1.7.0 | 1.7.0 | Current. Keep both aligned. |
| `@tanstack/react-query` | 5.102.8 | 5.103.1 | Safe patch/minor candidate; run status, trainer-practice, and generated query-option tests. |
| `chess.js` | 1.4.0 | 1.4.0 | Current. |
| `lucide-react` | 1.31.0 | 1.47.0 | Same major. Visually check named icons used by AppShell, board controls, tabs, and repertoire actions. |
| `react`, `react-dom` | 19.0.0 | 19.3.0 | Upgrade together with matching type packages. Run all component and Storybook tests. |
| `react-chessboard` | 5.12.0 | 5.12.1 | Safe patch candidate; run board adapter and promotion tests. |
| `react-day-picker` | 10.0.1 | 10.0.1 | Current. |
| `react-error-boundary` | 6.1.3 | 6.1.5 | Safe patch candidate. |
| `react-resizable-panels` | 4.12.3 | 4.12.4 | Safe patch candidate; check wide/narrow repertoire layouts. |
| `react-router-dom` | 7.18.2 | 7.18.4 | Safe patch candidate; check navigation and direct route loads. |
| `recharts` | 3.10.1 | 3.10.1 | Current. |
| `temporal-polyfill` | 1.0.5 | 1.0.5 | Current but unused. Remove it rather than adding code solely to justify it. |

### npm development and workflow packages

#### Safe/current-major targets

| Package group | Current | Recommended current-line target | Notes |
|---|---:|---:|---|
| root `@playwright/test`; frontend `playwright` | 1.50.1 / 1.62.1 | both 1.63.0 | Security fix and version consolidation. Different driver versions in one lock are avoidable. |
| `vitest`, `@vitest/browser-playwright` | 4.1.5 | both 4.1.11 | Urgent security patch. Do not jump to Vitest 5 yet. |
| `vite` | 6.0.11 | 6.4.3 | Urgent security update while retaining major 6. |
| `eslint`, `@eslint/js` | 9.19.0 | both 9.39.5 | Security fix before considering ESLint 10. |
| `storybook`, `@storybook/react-vite`, `@storybook/addon-a11y`, `@storybook/addon-vitest` | 10.5.8 | 10.6.0 | Upgrade the complete Storybook set together. |
| `typescript-eslint`, `@typescript-eslint/eslint-plugin`, `@typescript-eslint/parser` | 8.22.0 | 8.70.0 | Latest line supports ESLint 10 but only TypeScript `<6.1`. Remove redundant direct parser/plugin declarations if the aggregate package remains the sole import. |
| `@chialab/vitest-axe` | 0.19.1 | 0.19.2 | Patch. Preserve matcher side-effect/type imports. |
| `@testing-library/react`, `@testing-library/user-event` | 16.1.0 / 14.6.1 | 16.3.3 / 14.6.7 | Same-major test updates. |
| `@types/node` | 24.13.3 | 24.13.6 | Stay on the Node 24 type line; do not adopt latest-major 26 while runtime is pinned to 24. |
| `@types/react`, `@types/react-dom` | 19.0.8 / 19.0.3 | both 19.3.0 | Align with React 19.3. |
| `eslint-plugin-react-refresh` | 0.4.18 | 0.5.7 | Pre-1.0 minor: treat as potentially breaking and run lint/build. |
| `prettier` | 3.5.3 | 3.9.8 | Same-major tool update; expect formatting diffs. |
| `@opencode-ai/plugin` | 1.18.18 | 1.18.31 | Local workflow patch; smoke-test `.opencode/tools/glob.ts` and `.opencode/plugin/context-budget.js`. |

Already at npm latest on the audit date: `@axe-core/playwright@4.13.0`, `@mermaid-js/mermaid-cli@11.17.0`, `@hey-api/openapi-ts@0.99.0` (vulnerable despite being latest), `@fullcalendar/react@7.1.0`, both Headless Tree packages, `chess.js@1.4.0`, `react-day-picker@10.0.1`, `recharts@3.10.1`, and `temporal-polyfill@1.0.5`.

#### Major-version work that should not be mixed with security patches

| Package/group | Latest | What is required |
|---|---:|---|
| TypeScript | 7.0.2 | **Blocked today:** `typescript-eslint@8.70.0` accepts TypeScript `<6.1`. Move first from 5.7.3 to supported TypeScript `6.0.3`, repair compiler errors, and wait for linter support before TypeScript 7. |
| ESLint / `@eslint/js` | 10.11.0 / 10.0.1 | Latest `typescript-eslint` supports ESLint 10 and Node 24 satisfies the engine. Upgrade the whole lint stack after the 9.39.5 security patch, then review flat-config behavior and new default rules. |
| Vite / React plugin | 8.3.0 / 6.1.1 | Upgrade together. The repository's Vite config is simple, and Storybook 10.6 accepts Vite 8, but Vite 8's build engine is a material change. Prove dev server, build, Vitest, and Storybook separately. |
| Vitest / browser provider | 5.0.1 | **Blocked by Storybook 10.6:** `@storybook/addon-vitest@10.6.0` peers only with Vitest 3 or 4 and `@vitest/browser-playwright` 4. Remain on secure 4.1.11 until Storybook supports 5. |
| `jsdom` | 30.1.0 | Requires Node `22.22.2`, `24.15`, or 26+. Raise the Node 24 engine floor and verify DOM-sensitive tests before upgrading from 26.0.0. |
| `@testing-library/jest-dom` | 7.0.1 | Requires Node 22+ and `@testing-library/dom` 10. Update with the testing stack and check the Vitest setup import. |
| `eslint-plugin-react-hooks` | 7.1.1 | Review newly recommended rules and React compiler-related behavior; do not accept rule changes silently. |
| `@types/node` | 26.6.2 | Defer until the runtime moves to Node 26. Node 24 remains the correct supported line now. |
| `@vitejs/plugin-react` | 6.1.1 | Requires Vite 8, so it is part of the Vite 8 migration, not an independent bump. |

`@storybook/addon-vitest` is the concrete reason not to run a blanket “upgrade everything to latest” command. It would install a test stack that violates declared peer support.

## Recommended migration sequence

### Phase 1 — remove known application/tool vulnerabilities

1. Upgrade Vitest and its browser provider to `4.1.11` together.
2. Upgrade Vite to `6.4.3`.
3. Upgrade ESLint and `@eslint/js` to `9.39.5`.
4. Align root `@playwright/test` and frontend `playwright` on `1.63.0`; reinstall Chromium and run both E2E and Storybook browser tests.
5. Trial the safe `@hey-api/openapi-ts@0.97.0` downgrade, regenerate the client, and retain it only if the generated/API tests pass.
6. Upgrade FastAPI to `0.141.1`, Pydantic to `2.13.5`, Uvicorn to `0.53.0`, and pytest to `9.1.1`. Let the resolver select Starlette `1.6.0`, then lock that complete graph.
7. Re-run `npm audit` and `pip-audit`. Do not claim completion while the Hey API issue remains unresolved or explicitly time-boxed.

### Phase 2 — make builds reproducible and reduce attack surface

1. Split Python runtime dependencies from test/tool dependencies. The backend/worker image should not contain pytest, Ruff, Graphify, matplotlib, NumPy, or dozens of tree-sitter grammars.
2. Add a checked-in Python lock with hashes. The recommended route is `uv`; the lower-change alternative is `pip-tools` with `requirements.in` plus generated, hashed requirements files.
3. Pin the selected Python and Node image digests. Retain readable tags before `@sha256:` so humans can see the intended runtime line.
4. Move the Node image from Bookworm to Trixie and update npm to a reviewed fixed release if the official image still contains the four bundled npm findings.
5. Download Stockfish in a build stage, verify the release SHA-256 before extraction, and copy only the executable into the final image. Do not leave curl and tar solely for a build-time download.
6. Add root `packageManager: "npm@12.0.2"` only after raising the Node floor to `>=24.15 <25` and confirming every developer/container uses that line.
7. Make `.opencode/package.json` and its lock intentionally tracked, or remove the misleading claim that they are repository-managed. An ignored lock is not reproducibility.

### Phase 3 — low-risk refreshes

Apply Python patch/current-minor updates and the frontend same-major targets in small groups. Keep these groups separate so failures have an obvious cause:

- React, React DOM, and React type packages.
- Storybook's four packages.
- TanStack Query and generated query tests.
- UI primitives (`@base-ui/react`, resizable panels, router, error boundary, chessboard, Lucide).
- Python database/runtime patches (PyYAML and SQLAlchemy).
- Cachetools 7 with cache-focused tests.
- Graphify patch with a full deterministic catalogue regeneration review.
- Ruff and Prettier as maintenance-only formatting/lint changes.

### Phase 4 — deliberate major migrations

1. TypeScript `5.7.3` -> `6.0.3` with `typescript-eslint@8.70.0`.
2. ESLint 9 -> 10 and React Hooks plugin 5 -> 7.
3. Vite 6 -> 8 and React plugin 4 -> 6.
4. jsdom 26 -> 30 and jest-dom 6 -> 7 after enforcing Node 24.15+.
5. Vitest 4 -> 5 only after the installed Storybook addon advertises support.
6. TypeScript 7 only after `typescript-eslint` supports it.

### Phase 5 — Stockfish 19

Stockfish 19 is newer, stronger, and uses universal binaries. Its release notes also describe stricter FEN/UCI validation that terminates the engine on invalid input.

Required repository work:

1. Change the Windows provisioner from `sf_18` / `stockfish-windows-x86-64-avx2.zip` to `sf_19` / `stockfish-windows-x86-64-universal.zip` and update `STOCKFISH_ARCHIVE_SHA256` to the release value `3c8bf1f9ea66a09350a40df4f632288285ac206d99f33ab5842c408fc30b48a7`.
2. Change the Linux asset to `stockfish-linux-x86-64-universal.tar.gz` and verify release SHA-256 `9defc0d4e55d49c65a6d042f3e571a39fcea499ade6dbe741b53b8c65e03611f` before extraction.
3. Update `STOCKFISH_VERSION`, identity parsing, exact error/help text, Docker build assertion, fixtures, and tests that intentionally name Stockfish 18.
4. Run invalid/canonical FEN tests because Stockfish 19 is stricter.
5. Keep the current nodes/threads/hash/MultiPV profile initially. Engine version is already stored separately and `targets.py` treats a mismatched version as stale, so old results will be requeued without a schema change. Do not bump `CONFIGURATION_VERSION` unless those result-affecting profile values also change.
6. Run the focused engine, queue, target-selection, analysis persistence, position-insight, and benchmark tests. Then perform one bounded real-engine analysis in both Windows provisioning and the Linux worker image.
7. Expect evaluation changes. Do not compare new Stockfish 19 results to Stockfish 18 golden values as if they must be identical.

## Removals, replacements, and useful additions

### Remove or consolidate now

| Change | Why | How to bring it in safely |
|---|---|---|
| Remove `temporal-polyfill` | No import or `Temporal` use exists. | Delete the declaration, refresh the root lock, run frontend tests/build. If date-only logic later needs Temporal, adopt it deliberately through one shared date module. |
| Remove root Mermaid CLI | No `mmdc` command, Mermaid source file, or rendered flowchart was found. It brings a Puppeteer install script and a large transitive graph. | Remove it from root dev dependencies and refresh the lock. If an out-of-repo workflow needs it, document and pin that workflow instead. |
| Remove frontend `@axe-core/playwright` | All AxeBuilder imports are in root `tests/e2e`; the root declaration is sufficient. | Remove only the frontend duplicate and run accessibility E2E tests. |
| Remove direct `@typescript-eslint/parser` and `@typescript-eslint/eslint-plugin` | `frontend/eslint.config.js` imports only `typescript-eslint`, which already depends on both at the same version. | Keep `typescript-eslint`, regenerate the lock, and run ESLint once as the proof. |
| Normalize `python-chess` naming | The experiment metapackage and application `chess` package describe the same implementation differently. | Use `chess==1.11.2` in both places or source both from the new Python lock. |
| Align Playwright declarations | Root E2E and frontend browser tests currently use different driver versions. | Pin root test runner and frontend Playwright to one release; keep both declarations because Vitest's provider has a direct Playwright peer. |

### Recommended new tooling

These are development/supply-chain tools, not new product runtime libraries.

#### 1. `uv` for a complete Python lock (recommended)

Bring it in as follows:

1. Move runtime dependencies into `[project.dependencies]` and create a development dependency group for pytest, Ruff, Graphify, and `pip-audit`.
2. Generate and commit `uv.lock` on Python 3.12.
3. Either install from `uv.lock` directly in Docker with a pinned uv image/binary, or export a hashed runtime requirements file for pip.
4. Keep Graphify out of the backend runtime group.
5. Update `AGENTS.md`, `README.md`, and Docker rebuild instructions together; the current statement that direct pins are authoritative would no longer be complete.

The lower-change alternative is `pip-tools`: maintain `requirements.in` and `requirements-dev.in`, generate fully pinned hashed output, and leave the Docker pip command mostly unchanged.

#### 2. `pip-audit` as a pinned development tool

Add it to the development group rather than the runtime image. Provide one finite local command that audits the lock/export. `uvx pip-audit` was useful for this one-off audit, but an unpinned transient tool is not a durable policy.

#### 3. Trivy for local image and filesystem scanning

Use a pinned scanner image such as `aquasec/trivy:0.74.0`, scan the rebuilt final backend and frontend images, and record accepted unfixed Debian findings with a review date. This remains a local command; no application CI is required.

#### 4. Optional Dependabot or Renovate update proposals

If automated pull requests are wanted, configure npm, pip/uv, Docker, and the local `.opencode` lock separately, group tightly coupled packages (React, Storybook, Vitest, Playwright), and never auto-merge. Repository policy still requires local tests and does not add application CI. A simpler alternative is a documented monthly local audit without a bot.

### Supply-chain improvements without adding a library

1. Replace `@playwright/mcp@latest` with a root locked dev dependency and run `npx --no-install playwright-mcp`, or at minimum pin an exact MCP version. The lockfile route is preferred because the current MCP release uses an alpha Playwright internally.
2. Do not hand-edit generated Graphify HTML. Upgrade Graphify first; if it still emits `vis-network@9.1.6`, request/configure self-contained output or a local pinned asset with integrity rather than relying on unpkg at page-open time.
3. Pin Stockfish release archives by SHA-256 on both Windows and Linux. The Windows path already does this; the Linux Docker build does not.
4. Review npm install scripts. The audit dry run identified scripts for esbuild and Puppeteer; removing unused Mermaid CLI should remove Puppeteer from the root graph.
5. Add a short dependency policy: review cadence, severity response times, how temporary accepted findings are recorded, and who updates floating external assets.

### Libraries not recommended

No new product runtime library is needed. The frontend already has overlapping but purposeful primitives for forms, trees, calendars, charts, chess, routing, queries, and error boundaries. Adding another UI kit, date library, state manager, HTTP client, or chess library would increase migration and bundle cost without solving a demonstrated gap.

## Verification runbook for implementation

Run upgrades in the phases above, refreshing locks only from the repository root.

### After npm security/current-major updates

1. `npm audit --json`
2. Frontend unit/component tests.
3. Storybook Vitest project.
4. Frontend TypeScript/Vite build.
5. Before browser/E2E work, use `dev.ps1 status` and reuse healthy shared services as required by `docs/DEVELOPMENT_SERVICES.md`.
6. Focused Playwright E2E and accessibility scenarios, including browser reinstallation for the new Playwright version.

### After Python framework/security updates

1. `pip-audit` against the new lock/export.
2. `.venv/Scripts/python.exe -m pytest backend/tests tests` with explicit command and tool timeouts.
3. Regenerate/compare OpenAPI and the Hey API client if the framework output changes.
4. Rebuild backend and worker images through `dev.ps1`, then verify health and worker startup.

### After container changes

1. Resolve and record exact base image digests.
2. Rebuild with no stale base image.
3. Scan the final images, not only their bases, with Trivy.
4. Verify each final image runs as the intended non-root user; the current Dockerfiles do not create one, so this is an additional hardening candidate.
5. Verify backend, frontend, Storybook, and worker through the shared service lifecycle.

### Audit commands used

All commands were run with finite command-level and tool-level timeouts. Core commands were:

```text
timeout 180s npm audit --json
timeout 180s npm outdated --workspaces --include-workspace-root --json
timeout 120s npm audit --json                         # from .opencode
timeout 120s npm outdated --json                      # from .opencode
timeout 300s uvx --from pip-audit pip-audit -r requirements.txt --format=json
timeout 600s docker run --rm aquasec/trivy:0.74.0 image --scanners vuln --severity HIGH,CRITICAL --format table python:3.12-slim
timeout 600s docker run --rm aquasec/trivy:0.74.0 image --scanners vuln --severity HIGH,CRITICAL --format table node:24-bookworm-slim
timeout 600s docker run --rm aquasec/trivy:0.74.0 image --scanners vuln --severity HIGH,CRITICAL --format table node:24-trixie-slim
```

Docker Scout was also attempted with `timeout 120s docker scout cves --only-severity critical,high --format sarif <image>` for both base tags. It stopped with `Log in with your Docker ID or email address to use docker scout.` Trivy was used as the unauthenticated fallback.

## Proposed acceptance criteria

The repository can reasonably call dependencies “up to date” when:

- npm audit has no unaccepted finding; the Hey API exception is either fixed upstream or documented with version, exposure, mitigation, owner, and expiry.
- pip-audit has no finding in the locked runtime or development graphs.
- the final Docker images, not just base tags, have no fixable critical/high finding; unfixed Debian findings have a dated acceptance record.
- all direct packages are latest within their intentionally supported runtime/peer line.
- deferred latest majors have a concrete blocker recorded (currently Vitest 5 and TypeScript 7), not merely “too risky.”
- Stockfish, MCP, image digests, npm, and Graphify's browser asset are exact and reviewable rather than floating.
- unused and duplicate declarations are removed.
- the full Python transitive graph and all npm workspaces are reproducible from committed locks.

## Final image scan and accepted-risk record — 2026-09-19

Scanned with `docker run --rm -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.74.0 image
--scanners vuln --severity HIGH,CRITICAL --format json <image>` (the socket mount is required to
reach local images; without it Trivy reports the image cannot be found).

- **Backend image** (`chess-move-trainer-backend:latest`): 44 HIGH, 0 CRITICAL, 0 with a fixed
  version available. All 44 are Debian Trixie OS packages (util-linux family, ncurses, perl-base,
  libacl1, libsystemd0/libudev1) with no upstream fix; zero Python package findings.
- **Frontend image** (`chess-move-trainer-frontend:latest`): 47 HIGH, 0 CRITICAL. 43 are the same
  unfixed Debian OS packages. The remaining 4 sit in the "Node.js" target, i.e. the bundled
  `node_modules` of the pinned global `npm@12.0.2` toolchain, not the audited lock tree
  (`npm audit` is clean and the workspace's own brace-expansion copies are unflagged):
  brace-expansion 5.0.7 (CVE-2026-14257, CVE-2026-69152), ip-address 10.2.0 (CVE-2026-69192),
  tar 7.5.19 (CVE-2026-73566). `npm view npm versions` confirms 12.0.2 is the newest 12.x, so no
  toolchain patch exists.
- **Accepted with review date 2026-10-19 (owner: repository maintainers):** all 44 + 43 unfixed
  Debian findings and the 4 npm-toolchain findings. Exposure is limited: the Debian packages are
  base-layer utilities with no fix published, and the npm bundle is exercised only at image build
  time and by the `npm run` dev-server launcher on localhost-only ports, never by served traffic.
  Re-scan monthly; upgrade the npm pin when a fixed 12.x ships and re-run this section's command.
