# Frontend server-state caching - repeat frontend reads reuse recent in-memory results without changing the UI

> **Status:** done - all five stages accepted and archived on 2026-09-14.

- **Read trigger:** Read before changing frontend GET ownership, TanStack Query keys or defaults, frontend polling, mutation invalidation, or the test/Storybook QueryClient harness for the listed features.
- **Upstream:** `docs/grilling-docs/frontend-server-state-caching-direction.md` — governing approved direction for memory-only frontend caching, candidate reads, invalidation, polling, and exclusions. `docs/plans/active/api-latency-games-query-and-cache/` is a concurrently executing backend Plan and is read-only coordination evidence; its frontend exclusion and checked-in endpoint contract are the only relevant boundaries here.

## Outcome

The running React application reuses recent successful results for valuable GET state through the existing TanStack Query v5 QueryClient. Repeated or concurrent opening-catalogue, complete-filter training, game-detail, preferred-move, shared position-insight, and analysis-observation reads avoid duplicate work while remaining memory-only. Successful preferred-move and analysis mutations invalidate affected reads, analysis polling remains active and bounded, and existing loading, empty, error, retry, cancellation, and retained-result behavior remains visible to the user.

## Scope

- **Included:** Incremental query ownership for the six approved GET groups; canonical query keys; feature-specific freshness and garbage-collection policies; typed query-error adaptation; cancellation through TanStack `AbortSignal`; invalidation after successful preferred-move changes and analysis requests; matching position-insight invalidation after analysis state/result transitions; a reusable training-requirements invalidation seam for a future frontend training-answer owner; and focused Vitest/RTL plus one bounded browser proof.
- **Expected areas:**
  - `frontend/src/api/queryKeys.ts` (new) and `frontend/src/api/queryInvalidation.ts` (new)
  - `frontend/src/features/chess/chessPrimitives.ts`, `frontend/src/features/analysis/analysisApi.ts`
  - `frontend/src/features/trainer-practice/trainerPracticeApi.ts`, `frontend/src/features/trainer-practice/TrainerPracticePage.tsx`, and the existing Trainer Practice tests
  - `frontend/src/features/repertoire-builder/gameDetailQuery.ts` (new), `RepertoireBuilderWorkspace.tsx`, `preferredMoveState.ts`, `preferredMoveWorkflowState.ts`, and their focused tests/helpers
  - `frontend/src/features/position-insight/positionInsightQuery.ts` (new), `positionContextApi.ts`, `positionContextState.ts`, `moveResponseDistributionApi.ts`, `moveResponseDistributionState.ts`, and their focused tests
  - `frontend/src/features/analysis/analysisQuery.ts` (new), `analysisState.ts`, and its focused tests
  - `frontend/src/test-utils/QueryClientTestProvider.tsx`, `frontend/.storybook/preview.tsx`, `frontend/src/api/noAdoption.test.ts`
  - `tests/e2e/trainer-practice.spec.ts` for one repeat-read scenario only
- **Excluded:** `GET /api/games` or any games-list UI without a current frontend caller; opening-detail caching without a caller; health caching; persistent API storage in `localStorage`, `sessionStorage`, IndexedDB, or another browser store; service workers; HTTP caching headers or `Cache-Control`; backend source, schema, index, migration, or endpoint changes; generated OpenAPI contract regeneration; new libraries, cache services, or custom general-purpose caches; caching errors as successful data; caching POST/PUT/DELETE responses; unrelated UI or state rewrites; lint, formatting, type/build, source-size, aggregate, or independent backend validation; Git operations.

## Implementation-critical evidence

- `frontend/src/main.tsx:3-23,25-33` already provides one application QueryClient with `retry: false`, `refetchOnWindowFocus: false`, and `refetchOnReconnect: false`. Keep those conservative defaults and add no persistence plugin.
- `frontend/src/api/generated/@tanstack/react-query.gen.ts:86-307` generates GET options and keys for every operation, but those keys retain raw options. Use handwritten feature keys for canonical first-four-FEN identity and complete normalized filters; do not import the generated directory from features.
- `frontend/openapi-ts.config.ts:15-20,32-37` confirms the generated plugin emits query helpers only and disables mutation/infinite-query machinery. Existing handwritten feature clients remain the transport and validation seams.
- `frontend/src/api/noAdoption.test.ts:11-24,54-79` requires runtime API imports through `frontend/src/api/client.ts`. New production modules must follow that rule; update only the allowlist for any new central-client consumer.
- `frontend/src/features/trainer-practice/trainerPracticeApi.ts:83-172` preserves blank-search all-page catalogue retrieval with concurrency four and the current nonblank-search first-page behavior. `:190-260` assembles complete training results through sequential pages, deduplicating items.
- `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx:196-242` owns explicit game-UUID submission, aborts, reset, response mapping, and exact loader failures. `preferredMoveState.ts:29-89` and `preferredMoveWorkflowState.ts:271-343` own preferred reads, mutation guards, mutation aborts, and post-write confirmation.
- `frontend/src/features/position-context/positionContextApi.ts:109-128` and `frontend/src/features/move-response-distribution/moveResponseDistributionApi.ts:189-223` independently request the same position-insight endpoint. A shared raw query owner is required to deduplicate them without colliding different selected-data shapes.
- `frontend/src/features/analysis/analysisApi.ts:86-92` defines the existing canonical position identity by the first four FEN fields. `analysisState.ts:82-182,184-228` defines automatic observation, queued/running polling, the 60-attempt limit, deliberate requests, and retained results.
- `frontend/src/api/generatedSurface.test.ts:45-86` shows the checked-in frontend contract has no training-answer mutation and no current frontend games-list caller. Do not invent either owner.

## Query-key and policy contract

All query functions use `retry: false`, pass TanStack's signal to the existing handwritten client, rethrow aborts for cancellation, and throw a typed internal query error for non-success results. A failed result is never returned as successful query data. Existing feature readers may retain their public result unions for adapter and transport tests.

- **Opening catalogue:** `queryKeys.openingsCatalogue({ search, pageSize: 100, sort: "name_asc" })`; normalize `search.trim()` to either the trimmed value or `null`. Cache the final `fetchOpeningChoices` result, preserving all-page blank-search retrieval and first-page nonblank-search retrieval. `staleTime: 15 minutes`; `gcTime: 30 minutes`.
- **Complete training requirements:** `queryKeys.trainingRequirements({ asOf, trainerColor, openingKey, openingMatch, trainingRequirementLt: 0, pageSize: 100 })`; normalize empty opening and colour selections to `null`, retain `openingMatch: "reached"` only with an opening, and omit internal page numbers because the cached value is the complete assembled result. `staleTime: 60 seconds`; `gcTime: 10 minutes`.
- **Game detail:** `queryKeys.gameDetail({ gameUuid })`; use the trimmed UUID only after the existing explicit Game Loader submission. `staleTime: 5 minutes`; `gcTime: 30 minutes`.
- **Preferred move:** `queryKeys.preferredMove({ positionKey, today, tomorrow })`; use the canonical first-four-FEN position plus the current UTC one-day window so a midnight rollover cannot reuse yesterday's read. Continue sending the full FEN to the existing API client. `staleTime: 30 seconds`; `gcTime: 10 minutes`.
- **Shared position insight:** `queryKeys.positionInsight({ positionKey, trainerColor, asOf })`; use the canonical first-four-FEN position, selected trainer colour, and current UTC `as_of`. A single raw response query supplies selectors for both context and move-response distribution. `staleTime: 5 seconds`; `gcTime: 10 minutes`.
- **Analysis observation:** `queryKeys.analysisObservation({ positionKey })`; use `staleTime: 0` and `gcTime: 5 minutes`. Refetch only while the observation is `queued` or `running`, using the existing configurable interval (one second by default) and maximum of 60 poll attempts. Do not use a long freshness window to simulate polling.

The default application and test QueryClients remain memory-only. Leave focus and reconnect refetch disabled. Leave normal stale-query mount behavior enabled so fresh cached navigation is immediate while stale data can refresh. Query keys must be structural and independent of query-string ordering.

## Invalidation contract

- A successful preferred-move PUT or DELETE invalidates the exact preferred-move position/window key, all training-requirement keys, and all position-insight keys for the canonical position. Active affected queries may refetch; the preferred workflow must retain its existing pending-refresh confirmation before clearing staged state.
- A successful deliberate analysis request invalidates the canonical analysis-observation key and matching position-insight keys, then lets the existing queued/running polling coordinator observe the new state.
- When analysis observation receives a changed `state` or changed `result` for the canonical position, invalidate matching position-insight keys once for that transition. Do not invalidate insight on identical queued/running polls, or polling will create an avoidable feedback loop.
- Expose `invalidateTrainingRequirements(queryClient)` for a future frontend training-answer mutation. No current frontend operation or owner exists, so this Plan must not add one. The future owner must call the helper only after a successful answer mutation.

## Stages

1. **complete - Established canonical keys, invalidation seams, and isolated QueryClient harnesses.**
   - **Ordered actions:**
     1. Add the shared first-four-FEN identity to `frontend/src/features/chess/chessPrimitives.ts` and preserve the existing `positionKeyFromFen` export/test contract from `analysisApi.ts`.
     2. Add `frontend/src/api/queryKeys.ts` with the six key families and the exact normalization/policy inputs above. Include fixed response-affecting catalogue/training parameters and the preferred UTC date window.
     3. Add `frontend/src/api/queryInvalidation.ts` with exact-key/prefix helpers for preferred moves, training requirements, position insight, and analysis observation. Keep invalidation separate from transport and do not build a second cache.
     4. Reuse `QueryClientTestProvider` with fresh clients for component tests and add a fresh memory-only QueryClient decorator in `frontend/.storybook/preview.tsx`. Keep the production provider defaults in `main.tsx` unchanged.
     5. Update only `frontend/src/api/noAdoption.test.ts` for any new approved central API consumer; do not add direct generated-directory imports.
   - **Focused proof:**
     ```text
     timeout 60s npm --prefix frontend run test -- --run src/api/queryKeys.test.ts src/api/noAdoption.test.ts
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `120000` ms.
   - **Escalation boundary:** Stop before changing generated files, adding a dependency, changing global retry/focus/reconnect behavior, or introducing persistence or a general custom cache.
   - **Breakpoint:** None expected.

2. **complete - Migrated Trainer Practice catalogue and complete-filter results.**
   - **Ordered actions:**
     1. Keep `fetchOpeningChoices` and `fetchTrainingRequirements` as the behavior-preserving transport/assembly functions, and add query adapters that turn only unsuccessful unions into typed query errors.
     2. Replace the page's catalogue effect/retry counter with an enabled catalogue query keyed by normalized submitted search. Search input must remain local and must not request until the existing Search button is submitted; the existing catalogue loading/error/retry copy stays unchanged.
     3. Replace explicit training retrieval effects with an enabled query only after a valid form submission. Keep invalid-date short-circuiting, complete sequential retrieval, stale-date mapping, empty metadata, and existing request cancellation semantics.
     4. Add shared-client tests proving concurrent/repeated successful reads call the underlying loader once within freshness, reordered/normalized filters share a key, changed complete filters remain distinct, failed reads are retried rather than treated as cached success, and existing states remain exact.
   - **Focused proof:**
     ```text
     timeout 90s npm --prefix frontend run test -- --run src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/TrainerPracticePanel.test.tsx
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `150000` ms.
   - **Escalation boundary:** Stop before changing page-size/sort, search pagination semantics, training filter semantics, response mapping, or adding a training-answer operation.
   - **Breakpoint:** None expected.

3. **complete - Migrated Repertoire game detail and preferred-move reads while preserving mutations.**
   - **Ordered actions:**
     1. Add `gameDetailQuery.ts` around the existing injected `GameDetailClient`, keyed only by the trimmed submitted UUID. Preserve explicit submit/reset, abort-on-reset/new-submit, `mapGameDetailResponse`, and all `GameLoader` failure copy.
     2. Convert `usePreferredMoveState` to a canonical position/date-window query while retaining its public state shape, same-position retained data during refresh, typed failures, and abort behavior.
     3. Keep PUT/DELETE transport validation and the existing workflow guards. On successful mutation, use the invalidation helper and preserve the existing pending-refresh confirmation before announcing “Preferred move saved.” or “Preferred move removed.”
     4. Preserve injected test/Storybook clients through the existing props and wrap direct hook/workspace tests in fresh QueryClients; do not weaken the `api/client` import guard.
     5. Add cache, canonical counter-field, mutation-invalidation, reset, stale-response, and exact UI-state regression coverage.
   - **Focused proof:**
     ```text
     timeout 120s npm --prefix frontend run test -- --run src/features/repertoire-builder/preferredMoveState.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.
   - **Escalation boundary:** Stop before changing UUID validation, imported-game mapping, preferred mutation bodies/statuses, staged-move ownership, or invalidating unrelated query families.
   - **Breakpoint:** None expected.

4. **complete - Gave position context and move responses one shared position-insight query.**
   - **Ordered actions:**
     1. Add `frontend/src/features/position-insight/positionInsightQuery.ts` as the sole raw `getPositionInsight` query owner for the default clients, keyed by canonical position, trainer colour, and UTC `as_of`.
     2. Keep position-context and move-response-specific narrowing, validation, safe error mapping, no-games classification, retry, and selected-data shapes in their existing feature boundaries. Select from the shared raw result rather than caching two incompatible transformed shapes under one key.
     3. Preserve custom clients as test/Storybook seams without allowing their transformed results to collide with the shared raw production key. Ensure fresh Storybook/test clients do not leak across stories or tests.
     4. Hide retained data while context/distribution refresh is loading as the current hooks do; cached fresh data may render immediately on a revisit. Abort replaced requests and ignore late results.
     5. Prove two consumers of the same canonical position/colour/date make one underlying GET, counter-only variants share identity, distinct colour/date/position inputs remain distinct, malformed/error responses remain safe, and existing available/no-games/unavailable/retry UI remains unchanged.
   - **Focused proof:**
     ```text
      timeout 120s npm --prefix frontend run test -- --run src/features/position-insight/positionInsightQuery.test.tsx src/features/position-context/positionContextApi.test.ts src/features/position-context/positionContextState.test.ts src/features/move-response-distribution/moveResponseDistributionApi.test.ts src/features/move-response-distribution/moveResponseDistributionState.test.tsx src/features/move-response-distribution/MoveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.
   - **Escalation boundary:** Stop before caching a different position endpoint, changing insight response validation, changing `as_of` meaning, or creating separate caches for the two consumers.
   - **Breakpoint:** None expected.

5. **complete - Migrated analysis observation and completed frontend proof.**
   - **Ordered actions:**
     1. Add `frontend/src/features/analysis/analysisQuery.ts` as the query-owned adapter without changing the existing `AnalysisClient` transport contract. Use canonical position keys while passing the full current FEN to the GET operation.
     2. Replace the handwritten observation timer with one query polling coordinator: no polling for `not_requested`/`ready`, interval polling only for `queued`/`running`, exact 60-attempt limit, cancellation on position change/unmount, and existing retained-result merge when active responses omit a result.
     3. Keep the deliberate POST request separate from cached GET data. After success, invalidate analysis and matching position insight; after each actual analysis state/result transition, invalidate matching insight once. Preserve separate request errors and the deliberate Analyze action.
     4. Add focused tests for one shared observation request, queued/running polling, transition-triggered insight invalidation, result retention, request invalidation, no error-as-data caching, retry, position replacement, and the existing exact panel states.
     5. Extend `tests/e2e/trainer-practice.spec.ts` only with a repeated identical retrieval assertion proving the fresh complete-filter result makes no additional matching GET. Before the browser scenario, run `dev.ps1 status` and reuse healthy shared services as-is.
   - **Focused proof:**
     ```text
     timeout 120s npm --prefix frontend run test -- --run src/features/analysis/analysisApi.test.ts src/features/analysis/analysisQuery.test.ts src/features/analysis/analysisState.test.ts src/features/position-insight/positionInsightQuery.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.

     ```text
     timeout 30s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `60000` ms. Reuse healthy services; do not restart them for this proof.

     ```text
     timeout 90s npx playwright test tests/e2e/trainer-practice.spec.ts --config tests/e2e/playwright.config.ts
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `120000` ms.
   - **Acceptance within this stage:** The focused analysis tests pass with five-second insight freshness and ten-minute insight retention; the bounded browser scenario proves the visible Trainer Practice flow and fresh repeat-read deduplication. No broad or hygiene suite is required.
   - **Escalation boundary:** Stop before using a long analysis freshness window, caching POST results, polling outside queued/running states, widening invalidation to unrelated features, or changing the analysis response contract.
   - **Breakpoint:** None expected.

Stages are sequential; no parallel stages. A passing proof item remains valid until a later stage changes its command, inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only affected proof. Passing behavioral proof is retained until an affecting change; independent validation and complete test/fix runs are separate workflows when requested.

## Progress and decisions

- **Stage 1:** complete - six canonical key families, bounded invalidation helpers, shared first-four-FEN identity, and isolated Storybook/test QueryClients accepted. Proof: 3 files and 9 tests passed across the two focused commands below; breakpoint: none.
- **Stage 2:** complete - catalogue and complete training reads now use normalized TanStack Query keys, configured in-memory freshness/retention, cancellation, typed errors, and preserved UI states. Proof: 2 files and 31 tests passed; breakpoint: none.
- **Stage 3:** complete - game-detail and preferred-move reads now use bounded canonical queries; successful preferred mutations invalidate the approved preferred, training, and matching insight families while existing cancellation, staged-state, confirmation, and UI behavior remains covered. Proof: 4 files and 30 tests passed; prior Stage 1–2 proof remains valid; breakpoint: none.
- **Stage 4:** complete - position context and move-response distribution now share one canonical raw insight query with five-second freshness and feature-specific validation/selectors; custom-client, cancellation, loading, empty, error, and retry behavior remains covered. Proof: 7 files and 70 tests passed, including the invalidated Stage 3 integration test; prior Stage 1 proof remains valid; breakpoint: none.
- **Stage 5:** complete - analysis observation now uses canonical, bounded queued/running query polling with cancellation, retained results, transition-only insight invalidation, deliberate-request invalidation, and retry behavior. Focused proof passed 5 files and 41 tests; shared services were healthy; the one Trainer Practice E2E scenario passed and observed no additional matching GET on a fresh repeat. Stage 4 source paths were unchanged and its directly affected tests passed again; breakpoint: none.
- **Unresolved material decisions:** none. There is no current frontend training-answer operation or owner; the Plan records a reusable invalidation seam and explicitly defers that future integration rather than guessing an endpoint or UI. The backend Plan's Stage 3 measurement/escalation does not affect this frontend scope because games-list caching and backend implementation are excluded.

## Proof

- Stage 1 key and import-boundary proof: `timeout 60s npm --prefix frontend run test -- --run src/api/queryKeys.test.ts src/api/noAdoption.test.ts` from `G:\ChessMoveTrainer`; Bash tool timeout `120000` ms — passed, 2 files and 7 tests.
- Stage 1 invalidation-helper proof: `timeout 60s npm --prefix frontend run test -- --run src/api/queryInvalidation.test.ts` from `G:\ChessMoveTrainer`; Bash tool timeout `120000` ms — passed, 1 file and 2 tests; no edits followed, so the earlier Stage 1 proof remains valid.
- Stage 2 Trainer Practice proof: `timeout 90s npm --prefix frontend run test -- --run src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/TrainerPracticePanel.test.tsx` from `G:\ChessMoveTrainer`; Bash tool timeout `150000` ms — passed, 2 files and 31 tests.
- Stage 3 Repertoire proof: `timeout 120s npm --prefix frontend run test -- --run src/features/repertoire-builder/preferredMoveState.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx` from `G:\ChessMoveTrainer`; Bash tool timeout `180000` ms — passed, 4 files and 30 tests; no shared Stage 1 files changed, so prior proof remains valid.
- Stage 4 shared-insight proof: `timeout 120s npm --prefix frontend run test -- --run src/features/position-insight/positionInsightQuery.test.tsx src/features/position-context/positionContextApi.test.ts src/features/position-context/positionContextState.test.ts src/features/move-response-distribution/moveResponseDistributionApi.test.ts src/features/move-response-distribution/moveResponseDistributionState.test.tsx src/features/move-response-distribution/MoveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx` from `G:\ChessMoveTrainer`; Bash tool timeout `180000` ms — passed, 7 files and 70 tests; no Stage 1 files changed.
- Stage 5 analysis proof: `timeout 120s npm --prefix frontend run test -- --run src/features/analysis/analysisApi.test.ts src/features/analysis/analysisQuery.test.ts src/features/analysis/analysisState.test.ts src/features/position-insight/positionInsightQuery.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx` from `G:\ChessMoveTrainer`; Bash tool timeout `180000` ms — passed, 5 files and 41 tests.
- Before the one browser scenario: `timeout 30s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status` from `G:\ChessMoveTrainer`; Bash tool timeout `60000` ms — backend, frontend, and Storybook healthy; reused without lifecycle changes.
- One bounded browser scenario: `timeout 90s npx playwright test tests/e2e/trainer-practice.spec.ts --config tests/e2e/playwright.config.ts` from `G:\ChessMoveTrainer`; Bash tool timeout `120000` ms — passed, 1 test; repeated identical retrieval made no additional matching GET.
- No lint, formatting, type/build, source-size, aggregate, or independent backend validation is part of this Plan.

## Escalation boundaries

- Any change to the checked-in frontend API response, query parameters, status/error codes, or generated OpenAPI surface; stop and obtain a new decision rather than regenerating or guessing.
- Any direct edit to `docs/plans/active/api-latency-games-query-and-cache/` or its backend implementation areas; that Plan remains read-only and concurrently owned.
- Any need for a frontend training-answer endpoint, mutation owner, or answer UI; stop at the deferred invalidation seam and obtain the actual owner/contract.
- Any games-list caller, opening-detail caller, persistent storage, service worker, HTTP-cache header, new dependency/service, custom general cache, backend/schema/index/migration change, or cache of error/write responses.
- Any request to change the five-second position-insight freshness, ten-minute insight retention, canonical identity, exact invalidation fan-out, 60-attempt analysis limit, or current loading/error/empty/retry/cancellation semantics.
- Any directly conflicting concurrent edit in the expected frontend paths; preserve unrelated changes and re-assess the affected stage.

## Visible result

> Returning to the same trainer filters, game, or chess position during one browser session reuses recent successful work without persistent storage, while preferred-move updates and analysis progress make the next related read fresh and the existing screens keep their current feedback.

## Archive

- Accepted and moved from `docs/plans/active/frontend-server-state-caching/` to `docs/plans/done/frontend-server-state-caching/` on 2026-09-14.
- No transient `handoff.md` existed.
- Passing behavioral proof remains valid until a later change affects the covered paths, configuration, dependencies, or shared service environment. Complete test/fix work remains a separate workflow.
