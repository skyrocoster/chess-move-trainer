# Database rebuild SETUP-02 API tooling - One command turns the real health route into a checked-in, typed TypeScript client

> **Status:** done - Stages 1 and 2 accepted on 2026-09-08

- **Read trigger:** whenever SETUP-02 implementation, validation, or repair is approved
- **Upstream:** [database-rebuild-setup-02.md](../../../grilling-docs/database-rebuild-setup-02.md) (binding
  directional evidence, approved 2026-09-08, including the user-approved removal of the redundant
  `@hey-api/client-fetch` dependency);
  [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md)
  SETUP-02/current-boundary sections (dependency ordering and continuing exclusions only)

## Outcome

One explicit repository command, run from the repository root without a running backend, exports a
checked-in OpenAPI contract containing only the current `GET /api/health` operation with explicit
`operation_id="getHealth"`, then regenerates a checked-in, self-contained TypeScript client with
`@hey-api/openapi-ts@0.99.0`. The generated surface exposes the typed health response and a plain
asynchronous `getHealth()` request function. One central handwritten module supplies the existing API
base URL convention. A real generated-client call against a bounded local uvicorn returns
`{"status":"ok"}`. FastAPI's served `/openapi.json` remains full and available with every current
route and `/docs` remains available; the only served change is the approved health operation's
`operationId` metadata becoming `getHealth`, with no other served schema or route change. Every other
current endpoint and every existing frontend API module stay unchanged; the production frontend does
not adopt the generated client.

## Scope

- **Included:** explicit `operation_id="getHealth"` on the existing health route only; a fail-closed
  allow-list export step deriving the contract from the real FastAPI app; a deterministic one-command
  export+generate orchestrator; `@hey-api/openapi-ts` generator configuration; the checked-in contract
  and generated client in a dedicated generated directory; one handwritten central client
  configuration module; removal of the redundant `@hey-api/client-fetch@0.13.1` dependency from
  `frontend/package.json` and `package-lock.json` via the smallest npm workspace uninstall action
  (user-approved; no replacement dependency; the user-installed `@hey-api/openapi-ts` entries and all
  unrelated lock content are preserved); focused
  finite proof for export, regeneration, generated surface, real call, and no production adoption.
- **Expected areas:** `backend/app/features/health/router.py`;
  `backend/tests/features/health/` (new focused export test); `scripts/api/` (new, contained:
  contract exporter, one-command orchestrator, small finite command wrapper);
  `frontend/openapi-ts.config.ts` (new); `frontend/src/api/generated/` (new: checked-in contract +
  generated output only); `frontend/src/api/client.ts` (new, handwritten central configuration, never
  overwritten by generation); one new focused frontend API test config plus tests outside the
  generated directory (proposed `frontend/vitest.api.config.ts`, tests under `frontend/src/api/`);
  `frontend/package.json` and root `package-lock.json` (dependency removal only, preserving the
  user-installed `@hey-api/openapi-ts` entries).
- **Excluded:** all other current endpoints in the exported or generated contract; any change to other
  routers, services, repositories, or backend behavior; any served OpenAPI/docs change beyond the
  approved health `operationId` metadata; any production frontend adoption or edit of existing modules
  such as `frontend/src/features/status/statusApi.ts`; Zod or other runtime validation; React Query or
  other request frameworks; API-01 through API-04 contracts, routes, errors, or DB access; chess.db
  activation; `setup.ps1` use or modification; lint, formatting, broad type/build, source-size,
  aggregate, or CI checks; commits, pushes, branches, worktrees, stashes.

### Baseline preservation

The worktree contains unrelated user deletions and edits (including docs/ and experiments/ deletions)
plus the authoritative `@hey-api/openapi-ts` manifest/lock additions and the grilling handoff
document. Implementation preserves all of these exactly: it removes only the approved
`@hey-api/client-fetch` entries, never restores, rewrites, stages, or absorbs unrelated work, and the
final scope audit reviews only SETUP-02 paths.

## Stages

1. **completed** - Health-only contract export foundation, dependency correction, and backend proof.
   Ordered actions:
   a. Add `operation_id="getHealth"` to the existing health route decorator in
      `backend/app/features/health/router.py`; change nothing else on the route or app.
   b. Create `scripts/api/export_contract.py`: builds `backend.app.main.create_app()`, calls
      `app.openapi()`, and writes a deterministic, formatted JSON contract containing exactly the
      approved allow-list entries (`/api/health` GET plus the `HealthResponse` schema it references).
      It fails closed if the filtered result would contain any other path, operation, or schema, and
      accepts an output path argument so tests can write to a temp directory. It never mutates the
      live app's route table; FastAPI keeps serving its full OpenAPI with every current route, only
      the health operation's `operationId` metadata changed as approved.
   c. Create `scripts/api/finite.py`: a small finite command wrapper that runs one child command with
      an explicit seconds argument, kills it on expiry, and returns the child's status. All Plan proof
      commands invoke it so every command has a finite command-level timeout.
   d. Remove the redundant dependency with the smallest actual npm workspace action, executed through
      the finite wrapper created in (c):
      `.venv/Scripts/python.exe scripts/api/finite.py 300 npm.cmd uninstall @hey-api/client-fetch
      --workspace frontend` (command-level timeout 300 s; future bash tool timeout 360000 ms), run
      from the repository root. This one action removes the package from `frontend/package.json` and
      updates `package-lock.json`. Preserve the user-installed `@hey-api/openapi-ts` entries and all
      unrelated lock content; the lock diff must remove only the client-fetch subtree.
   e. Add a focused backend test (proposed
      `backend/tests/features/health/test_contract_export.py`) that, via `scripts/api/finite.py` or an
      in-test finite subprocess timeout: exports to a temp path and asserts the contract contains only
      `/api/health` GET with `operationId` `getHealth` and exactly the `HealthResponse` schema; runs
      the export twice and asserts byte-identical output; and asserts the live `app.openapi()` remains
      full with every current route listed, `/docs` staying available, and that the only served
      difference is the health operation's `operationId` becoming `getHealth`.
   Proof (each with an explicit finite command-level timeout and the stated finite bash tool timeout):
   - `.venv/Scripts/python.exe scripts/api/finite.py 300 npm.cmd uninstall @hey-api/client-fetch
     --workspace frontend` (bash tool timeout 360000 ms) - dependency removal;
   - `.venv/Scripts/python.exe scripts/api/finite.py 300 .venv/Scripts/python.exe -m pytest
     backend/tests/features/health -q` (bash tool timeout 360000 ms).
   Escalation boundary: any non-health endpoint entering the contract, any other route edit, or any
   dependency change beyond the approved client-fetch removal. Breakpoint: none.
2. **completed** - Generator configuration, generated client, central configuration, one-command
   workflow, generated-client proof, and closeout.
   Ordered actions:
   a. Create `frontend/openapi-ts.config.ts` for `@hey-api/openapi-ts@0.99.0` using the
      `@hey-api/client-fetch` plugin in its default bundled (self-contained) mode, output directory
      `src/api/generated/`.
   b. Create `scripts/api/generate_client.py`, the one explicit repository command
      (`.venv/Scripts/python.exe scripts/api/generate_client.py`, from repository root, no backend
      needed): exports the contract to a temporary file, runs the generator with a finite child-process
      timeout, republishes the contract as `frontend/src/api/generated/openapi.json`, and reports a
      concise result. Output cleaning is confined to `frontend/src/api/generated/` so the handwritten
      central module at `frontend/src/api/client.ts` can never be overwritten.
   c. Run the command once to check in the generated client and contract.
   d. Create the handwritten `frontend/src/api/client.ts`: it imports the generated client singleton,
      applies the central base URL using the existing convention
      `import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666"` in one place, and re-exports the
      approved generated entrypoint (`getHealth`) and its health response types as the single import
      surface. The real-call proof imports `getHealth` through this central module. It remains unused
      by production application modules.
   e. Create the focused frontend API test config and tests (outside the generated directory): a
      surface test asserting the generated SDK module exports exactly one operation request function,
      `getHealth`, with the typed health success data and no other SDK operation (the vendored
      `client/` and `core/` helper modules may also be generated and are not SDK operations); a
      real-call test that starts a bounded local uvicorn on an ephemeral port (free-port probe, bounded
      startup wait, guaranteed teardown), calls the real generated `getHealth()` imported through the
      central module with that base URL, and asserts the typed result data equals `{"status":"ok"}`;
      and a narrow static adoption test asserting no file under `frontend/src` outside
      `frontend/src/api/` imports the generated directory or the central module.
   f. Determinism mode: extend `scripts/api/generate_client.py` with a `--check` mode that snapshots
      hashes of everything under `frontend/src/api/generated/`, regenerates, and fails on any byte
      change (hash comparison, not a git diff), confirming byte-identical regeneration.
   Proof (all run from the repository root; each with an explicit finite command-level timeout and the
   stated finite bash tool timeout):
   - `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py`
     (bash tool timeout 240000 ms) - first generation;
    - `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config
     frontend/vitest.api.config.ts --testTimeout 15000` (bash tool timeout 300000 ms) - surface, real
     call, and adoption tests; the focused API vitest config anchors its root to the `frontend/`
     directory so this repository-root invocation is valid;
   - `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
     (bash tool timeout 240000 ms) - byte-identical regeneration.
   Escalation boundary: any additional operation in the generated surface, any generated file written
   outside `frontend/src/api/generated/`, any production module importing the generated directory, or
   any new dependency. Breakpoint: none.

## Progress and decisions
- **Stage 1:** completed and accepted 2026-09-08 - the finite-wrapped workspace uninstall exited 0
  and removed the redundant `@hey-api/client-fetch` while retaining `@hey-api/openapi-ts@0.99.0`;
  the finite-wrapped focused backend command passed 8 tests in 6.02 seconds, proving existing health
  behavior, the health-only byte-deterministic export, stable `getHealth`, and the full served
  OpenAPI/docs boundary. Breakpoint: none.
- **Stage 2:** completed and accepted 2026-09-08 - the finite-wrapped one-command generation exited
  0 without a running backend and wrote the health-only contract plus 17 self-contained generated
  files; the focused frontend API run passed 4 tests across 3 files in 2.57 seconds, proving the
  single `getHealth` SDK operation, the typed real call returning `{"status":"ok"}`, and no
  production adoption; the finite-wrapped `generate_client.py --check` exited 0 and proved
  byte-identical regeneration of all 17 files. On Windows the planned `npx` invocation used
  `npx.cmd`, matching the repository's command-shim convention without changing behavior.
- **Closeout:** accepted and moved to `docs/plans/done/database-rebuild-setup-02/` on 2026-09-08;
  Stage 1 proof remained valid and was not rerun. No breakpoint or escalation boundary was reached.

## Proof

Finite behavioral proof only, each with an explicit finite command-level timeout (via
`scripts/api/finite.py` or an in-test bounded subprocess) and an explicit finite bash tool timeout:

- Existing health behavior regression: `backend/tests/features/health/test_health.py` keeps passing
  (included in the Stage 1 pytest command).
- Health-only deterministic export with `getHealth` operation ID, and the served OpenAPI boundary
  (full OpenAPI with every current route, `/docs` available, only the health `operationId` metadata
  changed): the new focused backend export test.
- One-command deterministic regeneration with the exact installed `@hey-api/openapi-ts@0.99.0`:
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
  (command-level timeout 180 s; bash tool timeout 240000 ms).
- Generated surface contains exactly one SDK operation, `getHealth`, with the typed health response:
  the frontend surface test against the checked-in generated module and contract (vendored `client/`
  and `core/` helpers are not SDK operations).
- Real generated-client call: bounded local uvicorn on an ephemeral port, real `getHealth()` imported
  through the central module returns `{"status":"ok"}`; uvicorn startup, execution, and teardown are
  all bounded.
- No production frontend adoption: the narrow static adoption test.

Accepted Stage 2 proof, all run from the repository root on 2026-09-08:

- `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py`
  exited 0 and generated the health-only contract and 17 self-contained client files without a
  running backend (command timeout 180 s; bash tool timeout 240000 ms).
- `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000`
  exited 0 with 4 tests across 3 files passing in 2.57 seconds (command timeout 240 s; test timeout
  15000 ms; bash tool timeout 300000 ms).
- `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
  exited 0 and reported byte-identical regeneration of 17 files (command timeout 180 s; bash tool
  timeout 240000 ms).

Retained passing proof stays valid until a later change affects its command, inputs, exercised
behavior, configuration, dependencies, or environment; later stages run only missing or invalidated
proof.

## Escalation boundaries

- Adding or changing any dependency beyond the user-approved removal of `@hey-api/client-fetch`.
- Including any current endpoint other than `GET /api/health` in the exported or generated contract.
- Modifying another API, route behavior, any served OpenAPI/docs content beyond the approved health
  `operationId` metadata, or any production frontend consumer or existing API module.
- Using or modifying `setup.ps1`; settling any future API-01..04 contract; integrating `chess.db`;
  expanding to maintenance, lint, or CI scope; any commit, push, branch, worktree, or stash.
- Restoring, rewriting, staging, or absorbing unrelated baseline worktree changes.

## Visible result

> One repository command regenerates a checked-in, health-only TypeScript API client exposing
> `getHealth()`, proven by a real call that returns `{"status":"ok"}`, while every other endpoint, the
> full served OpenAPI and available docs (with only the approved health `operationId` metadata
> change), and all existing frontend code remain untouched.
