# Database rebuild CONSUMER-01 - Status reaches the backend through the generated HeyAPI health query; checking/healthy behavior preserved and every failure displays exactly `Backend unavailable.`

> **Status:** done - accepted on 2026-09-09 after Stages 1-4 and all focused proof passed. This file was reconstructed on 2026-09-09 after a power outage zero-filled the original record; recovery used the durable upstream records, `docs/PLAN_TEMPLATE.md`, the current Stage 1 checkout, and the coordinator-approved contract. The recovery added no product or architecture decision.

- **Read trigger:** When executing, validating, or reviewing the `CONSUMER-01` Status migration, or when any later consumer slice needs the established TanStack foundation precedent.
- **Upstream:** `docs/master-plans/database-rebuild/database-rebuild.md` (`CONSUMER-01`: Status uses generated `getHealth()`; no other frontend adoption in this slice) and `docs/grilling-docs/database-rebuild-frontend-api-state-direction.md` (confirmed incremental TanStack/HeyAPI architecture and the stable friendly error decision). No design evidence.

## Outcome

The Status page stops calling the backend through the handwritten `statusApi.ts` fetch path and instead runs the generated HeyAPI `getHealth` query through a minimal TanStack Query foundation. The visible checking and healthy behavior is preserved. Every failure path - network failure, non-2xx response, non-`Error` throw, or a malformed HTTP 200 - shows exactly the stable friendly message `Backend unavailable.` instead of technical detail. This is the smallest vertical proof of the generated-client consumer pattern; later consumer slices build on the foundation it establishes without expanding it.

## Scope

- **Included:**
  - HeyAPI generated transport and contracts; TanStack Query introduced incrementally as the normal React server-state manager.
  - Narrow bundled `@tanstack/react-query` generation: query keys/options enabled; `mutationOptions`, `infiniteQueryKeys`, `infiniteQueryOptions` false; generated hooks and get/set-query-data helpers remain disabled. Helpers are mechanically generated for all GET operations, but only Status may consume them.
  - `frontend/src/api/client.ts` remains the configured handwritten boundary: it explicitly imports `getHealthOptions` from `./generated/@tanstack/react-query.gen` and exports it standalone; `getHealthOptions` is never exported through the generated index.
  - One application `QueryClientProvider` in `frontend/src/main.tsx` with `retry: false`, `refetchOnWindowFocus: false`, `refetchOnReconnect: false`; no `staleTime`, no persistence.
  - Direct Status consumption via `useQuery({ ...getHealthOptions(), gcTime: 0 })` (subject only to the exact generated shape already confirmed); no pass-through hook or service layer.
  - `gcTime: 0` is Status-local mount-fresh/cache-removal behavior. The generated `queryFn` separately consumes/forwards `signal` and uses `throwOnError: true`.
  - Status accepts only `data.status === "ok"` as healthy; all network, non-2xx, non-`Error`, and malformed-200 outcomes display the exact stable message `Backend unavailable.` in a message-less error view state.
  - Delete `statusApi.ts` only after a bounded unused proof.
  - `frontend/src/test-utils/QueryClientTestProvider.tsx` is the only new helper: fresh `QueryClient` per test/render, used only by StatusPage/App tests. The StatusPage story gets a narrow provider decorator.
  - Update the affected StatusPage/StatusView production code, unit tests, and stories.
- **Expected areas:** `frontend/openapi-ts.config.ts`; generated output under `frontend/src/api/generated/`; `frontend/src/api/client.ts`; `frontend/src/main.tsx`; StatusPage/StatusView production, tests, and stories plus deletion of `statusApi`; `frontend/src/test-utils/QueryClientTestProvider.tsx`; this Plan.
- **Excluded:** Any other consumer, dependency, tool, backend change, design work, or compatibility layer. No Repertoire/Viewer migration. No Zod/Valibot or general runtime-validation layer, no error hierarchy, no MSW, no React Query Devtools, no persistence, no polling, no prefetching. No lint/format/type/build/source-size/aggregate/hygiene proof.

## Stages

1. **done** - Generator configuration and narrow TanStack artifact: configure the bundled `@tanstack/react-query` plugin (query keys/options only; mutation and infinite machinery disabled), generate, and make `frontend/src/api/client.ts` the explicit configured export boundary for `getHealthOptions`, separate from the generated index.
2. **done** - TanStack foundation: add the one application `QueryClientProvider` (retry false, refetchOnWindowFocus false, refetchOnReconnect false, no staleTime/persistence) in `frontend/src/main.tsx`; add `frontend/src/test-utils/QueryClientTestProvider.tsx` (fresh QueryClient per test/render); wrap App/StatusPage tests with it; add the narrow StatusPage story provider decorator. Focused proof: App.test only.
3. **done** - Status migration: migrate StatusPage to direct `useQuery({ ...getHealthOptions(), gcTime: 0 })` consumption; make StatusView's error state message-less with the exact stable `Backend unavailable.` text; update affected unit tests and stories; prove `statusApi` unused, then delete it. Unit proof includes StatusPage.test, StatusView.test, and App.test; scenarios: loading/healthy, network failure, non-2xx, non-`Error`, malformed 200, remount-freshness checks again, and unmount abort.
4. **done** - Focused proof and audit: run the two focused Storybook stories and the focused live status E2E; run the no-other-consumer and legacy-absence audits; return to coordinator acceptance. Do not mark the Plan done or move it until coordinator acceptance.

Stages are sequential; no parallel stages. A passing proof item remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment; later stages run only missing or invalidated proof.

## Progress and decisions

- **Stage 1:** done - proof: generation and determinism checks passed (see receipt); breakpoint: none.
- **Stage 1 retained receipt:**
  - `frontend/openapi-ts.config.ts` configured as approved: bundled `@tanstack/react-query` plugin with `mutationOptions: false`, `infiniteQueryKeys: false`, `infiniteQueryOptions: false`; no per-operation filtering.
  - `frontend/src/api/generated/@tanstack/react-query.gen.ts` generated query keys/options for eight GET operations, no hook/mutation/infinite symbols. `getHealthOptions` at lines 101-112 returns `queryOptions`, forwards `signal`, `throwOnError: true`.
  - `frontend/src/api/client.ts` repaired and verified after a mid-stage interruption: explicit TanStack import on line 2, standalone `export { getHealthOptions };`, no `getHealthOptions` in the export-from-generated-index declaration; base URL configuration and all other generated operation/type exports intact; module comment identifies the future Status boundary.
  - Generation passed (5 generated this run / 18 checked in); deterministic `--check` passed byte-identical on 18 files; inverted symbol inspection exited 0 (no `useQuery`/`Mutation`/`Infinite` symbols in the generated TanStack artifact).
  - User-installed `@tanstack/react-query@5.102.8` dependency manifests and the grilling record preserved. Stage 1 changed only the generator configuration, generated TanStack artifact, `client.ts`, and this Plan.
- **Recovery decision:** The original Plan file was destroyed (all NUL bytes) by the power outage between Stage 1 completion and Stage 2 start. This reconstruction restores the approved semantics, stages, proof, and the Stage 1 receipt verbatim from the coordinator-approved recovery contract; it adds no new decisions and authorizes no Stage 2 work by itself.
- **Stage 2:** done - proof: focused unit run passed (see receipt); breakpoint: none.
- **Stage 2 receipt:**
  - `frontend/src/main.tsx`: one stable module-level `QueryClient` with exactly the approved defaults (`retry: false`, `refetchOnWindowFocus: false`, `refetchOnReconnect: false`; no `staleTime`, `gcTime`, persistence, or mutation configuration). App is wrapped with `QueryClientProvider` inside the existing `StrictMode`/`BrowserRouter` composition.
  - `frontend/src/test-utils/QueryClientTestProvider.tsx` (new, the only new helper): exports `createTestQueryClient()` with the same conservative defaults, and `QueryClientTestProvider`, which lazily creates a fresh client per mounted instance (fresh per `render()`/test, no cache leakage) and accepts an optional `client` prop reserved for Stage 3's one deliberate shared-client remount test. No broader test framework.
  - `frontend/src/App.test.tsx` and `frontend/src/features/status/StatusPage.test.tsx`: render paths wrapped through the helper; assertions and Status behavior unchanged.
  - `frontend/src/features/status/StatusPage.stories.tsx`: narrow meta-level decorator supplying one stable story QueryClient with the same conservative defaults; story rendering otherwise unchanged; no other stories altered; no API mocking or new dependency.
  - Proof passed: workdir `frontend`, `timeout 90s npx vitest run --project=unit src/App.test.tsx src/features/status/StatusPage.test.tsx` (bash tool 120000 ms): 2 files, 7 tests passed. First execution failed transiently: viewer/repertoire lazy routes exceeded their wait timeouts during cold vitest environment warm-up (environment phase 25.9s cold vs 1.0s warm); an isolation run of the HEAD-version App test passed, and the identical command passed on rerun with unchanged Stage 2 code. Recorded as a cold-start timing risk, not a Stage 2 defect; no test assertions or timeouts were changed.
- **Stage 3:** done - proof: focused unit command passed (see receipt); breakpoint: none.
- **Stage 3 receipt:**
  - `frontend/src/features/status/StatusPage.tsx`: rewritten from the `useState`/`useEffect`/`fetchHealth` path to a single direct `useQuery({ ...getHealthOptions(), gcTime: 0 })` importing `getHealthOptions` through the configured `frontend/src/api/client.ts`. No hook, service, or wrapper. Mapping: pending → checking; `data.status === "ok"` → healthy; every query error and every other resolved payload (including malformed 200) → error. No technical detail exposed.
  - `frontend/src/features/status/StatusView.tsx`: error state is message-less (`{ kind: "error" }`) and renders exactly `Backend unavailable.` with `alert` semantics; checking/healthy copy and roles preserved.
  - `frontend/src/features/status/StatusView.test.tsx` and `StatusView.stories.tsx`: updated to the message-less error contract, plus an explicit no-technical-detail assertion; Unavailable story simplified. StatusPage story needed no Stage 3 change.
  - `frontend/src/features/status/StatusPage.test.tsx`: seven scenarios - checking→healthy; network rejection, non-2xx, non-`Error` rejection, and malformed 200 each render exactly `Backend unavailable.` with no technical detail (malformed 200 asserted never healthy); remount on one deliberately shared test client waits for `gcTime: 0` cache removal then asserts checking is visible again and a second request occurs; unmount while pending captures the generated client's `Request` signal and asserts it becomes aborted (query-core confirmed: last-observer removal cancels the retryer, which aborts the forwarded signal; the vendored fetch client builds `new Request(url, init)` so the test captures `request.signal`).
  - Test-mock repair (only failure in this stage, fixed in approved test path): the first proof run failed because the mocked `Response` carried no `Content-Type` header; the generated client then parses the 200 body as a stream, so StatusPage correctly showed the error. Mocks now send `Content-Type: application/json` like the real backend, and the healthy mock returns a fresh `Response` per call so the shared-client remount exercises a clean second parse. Production code unchanged by this repair.
  - `frontend/src/features/status/statusApi.ts` deleted after bounded inspection: repo-wide `rg "statusApi|fetchHealth" frontend` matched only the definition itself.
  - Proof passed: workdir `frontend`, `timeout 90s npx vitest run --project=unit src/features/status/StatusPage.test.tsx src/features/status/StatusView.test.tsx src/App.test.tsx` (bash tool 120000 ms): 3 files, 16 tests passed (7 StatusPage, 5 StatusView incl. axe, 4 App).
- **Stage 4:** done and accepted - proof: focused Storybook, live E2E, and audits passed (see receipt); coordinator acceptance passed on 2026-09-09.
- **Stage 4 receipt:**
  - Storybook proof passed: workdir `frontend`, `timeout 240s npx vitest run --project=storybook src/features/status/StatusPage.stories.tsx src/features/status/StatusView.stories.tsx` (bash tool 300000 ms): 2 files, 4 tests passed (StatusPage Default with provider decorator; StatusView Loading/Healthy/Unavailable message-less).
  - Live E2E proof passed: workdir repo root, `timeout 120s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/status.spec.ts` (bash tool 180000 ms): 2 passed (12.8s) - live healthy status and accessible unavailable state; the Playwright config self-started and tore down the backend on port 5666.
  - Adoption audit passed: `timeout 20s rg -n "getHealthOptions" frontend/src` (bash tool 60000 ms) matched only the generated definition (`react-query.gen.ts:101`), the `client.ts` boundary (import line 2, comment lines 14-15, export line 22), and StatusPage use (lines 3, 7). No other production feature match.
  - Legacy absence passed: `timeout 20s bash -c '! rg -q "statusApi|fetchHealth" frontend/src'` (bash tool 60000 ms) exited 0.
  - Exclusion inspection (bounded content checks): no hook/mutation/infinite/mutationOptions symbols in the generated TanStack artifact (retained Stage 1 artifact proof still valid; generation not rerun); no MSW, persistence, devtools, polling, prefetch, or staleTime in Status production, provider, helper, client boundary, or generator config; the only dependency change remains the approved user-installed `@tanstack/react-query@^5.102.8`.

## Acceptance

- **Accepted on 2026-09-09:** Status now uses generated `getHealthOptions()` under the minimum TanStack Query foundation; the handwritten `statusApi.ts` transport is gone.
- Focused unit proof passed 16/16 tests, the two affected Storybook files passed 4/4 tests, and focused live E2E passed both healthy and unavailable scenarios.
- Deterministic generation, cancellation, mount-fresh checking, malformed-response rejection, stable friendly error copy, no-other-consumer adoption, and legacy-transport absence are all established by the retained receipts above.
- No independent Quality run was requested; no broad maintenance run is part of this acceptance.

## Proof

All commands use finite command-level and tool-level timeouts. No lint/format/type/build/size/aggregate/hygiene proof. Passing proof is retained until an affecting change.

- Generation (Stage 1, retained pass), repo root: `timeout 90s .venv/Scripts/python.exe scripts/api/generate_client.py`; bash tool 120000 ms.
- Determinism (Stage 1, retained pass), repo root: `timeout 90s .venv/Scripts/python.exe scripts/api/generate_client.py --check`; bash tool 120000 ms.
- Generated absence (Stage 1, retained pass), repo root: `timeout 20s bash -c '! rg -q "useQuery|Mutation|Infinite" frontend/src/api/generated/@tanstack/react-query.gen.ts'`; bash tool 60000 ms.
- Units (Stage 3), frontend: `timeout 90s npx vitest run --project=unit src/features/status/StatusPage.test.tsx src/features/status/StatusView.test.tsx src/App.test.tsx`; tool 120000 ms.
- Stories (Stage 4), frontend: `timeout 240s npx vitest run --project=storybook src/features/status/StatusPage.stories.tsx src/features/status/StatusView.stories.tsx`; tool 300000 ms.
- E2E (Stage 4), repo root: `timeout 120s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/status.spec.ts`; tool 180000 ms; the config self-starts and tears down backend/Vite from the repo-root cwd.
- Adoption audit (Stage 4), repo root: `timeout 20s rg -n "getHealthOptions" frontend/src`; tool 60000 ms; expected hits: only the generated definition, the `client.ts` export, and StatusPage use.
- Legacy absence (Stage 4), repo root: `timeout 20s bash -c '! rg -q "statusApi|fetchHealth" frontend/src'`; tool 60000 ms.

## Escalation boundaries

- Any change to the generated plugin flags, generated output shape, provider placement or defaults, the `Backend unavailable.` message text or error-view behavior, the `gcTime: 0` rule, the `data.status === "ok"` acceptance rule, or the client export boundary.
- Any second consumer, new dependency or repin, new helper beyond `QueryClientTestProvider.tsx`, pass-through hook/service, backend or contract change, or design change.
- Any destructive action, commit, or push; any edit outside the expected areas; returning to the coordinator whenever Stage 4 audit or acceptance finds drift.

## Visible result

> The Status page checks backend health through the generated HeyAPI query with unchanged checking/healthy behavior, and every failure shows exactly `Backend unavailable.` with no technical detail.
