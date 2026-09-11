# Repertoire clean analysis lifecycle - deliberate Tool requests follow the selected position

> **Status:** done - accepted 2026-09-10

- **Read trigger:** Before implementing, validating, repairing, accepting, or closing `CONSUMER-05`.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) governs
  sequence, ownership, clean analysis semantics, and retirement boundaries; [CONSUMER-05 direction](../../../grilling-docs/database-rebuild-consumer-05.md)
  governs the settled user-visible lifecycle and exclusions; accepted [CONSUMER-04 Plan](../../done/database-rebuild-consumer-04/database-rebuild-consumer-04.md)
  governs the immediate frontend baseline; accepted [CLEAN-06](../../done/database-rebuild-clean-06/database-rebuild-clean-06.md)
  and [CLEAN-07](../../done/database-rebuild-clean-07/database-rebuild-clean-07.md) govern the generated observation and
  desired-result request contracts.

## Outcome

Repertoire observes analysis for the selected/current position through generated `getAnalysis()`. Selecting or navigating
never starts engine work. The user deliberately chooses **Analyze position**, which sends a generated
`requestAnalysis()` request with explicit `quality: "tool"`. Queued and running observations are polled and shown;
an accompanying current result remains visible until the ready result replaces it. Ready results have no Update or
Retry-analysis action. Retry observation remains available for load/transport failure, while candidate-line activation
and selected-position navigation remain unchanged.

## Scope

- **Included:** The existing injected Repertoire analysis-client seam; clean generated GET/POST transport; clean
  lifecycle and current-result mapping; bounded observation polling; deliberate Tool requests; request/observation
  loading and error handling; removal of stale, eligibility, failed, Update, and Retry-analysis concepts; preserved
  candidate-line interaction, selected-FEN behavior, navigation, cancellation, and stale-response protection; directly
  affected analysis/Repertoire tests, fixtures, stories, adoption guard, and focused Storybook browser proof.
- **Expected areas:** `frontend/src/features/analysis/analysisApi.ts`, `analysisState.ts`, `analysisFormatting.ts`,
  `evalBarDisplay.ts`, `AnalysisPanel.tsx`, `AnalysisPanel.module.css`, their focused tests and stories;
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`, `RepertoireAnalysisTabs.tsx`,
  `repertoireBuilderTestHelpers.tsx`, analysis-related workspace stories and fixtures, and directly affected workspace
  tests; `frontend/src/api/noAdoption.test.ts`; `tests/e2e/analysis-panel-storybook.spec.ts`; and
  `tests/e2e/repertoire-builder-storybook.spec.ts`.
- **Excluded:** `frontend/src/api/client.ts` changes; all generated files and regeneration; backend, database, schema,
  OpenAPI, or dependency changes; Preferred Move, position-context, move-response, or any other consumer migration;
  legacy evaluation route retirement; compatibility, fallback, dual-read, cache, or second data owner; browser-quality
  controls; arbitrary engine settings; action/history/failure/queue-internal concepts; visual redesign; broad
  maintenance or Quality validation; completed-record or grilling-record edits; unrelated worktree changes; and any
  commit, push, branch, worktree, or stash operation.

## Implementation-critical facts

- The central API module already exports generated `getAnalysis`, `requestAnalysis`, and their types. The generated
  surface is accepted and remains unchanged.
- `getAnalysis` and `requestAnalysis` both return the clean `{ fen, state, result }` representation. `state` is only
  `not_requested`, `queued`, `running`, or `ready`; `result` is nullable and is the one current complete result.
- The request body is `{ fen, quality: "tool" }`; no quality selector or arbitrary settings belong in Repertoire.
- Clean result lines provide `rank`, `score_kind`, `score_value`, WDL values, `pv_uci`, and `depth`. Legacy
  `profile_id`, timestamps, `seldepth`, nodes, engine timing, requested quality, attempts, and failure/history data do
  not map into the frontend view model. PV formatting uses the observation FEN because the clean result has no FEN field.
- Automatic observation follows `session.currentPosition.fen`. Polling repeats the clean observation operation rather
  than calling a separate status endpoint. Existing result data must survive an active queued/running state and an
  observation transport error.
- The injected `analysisClient` remains the test and Storybook seam. Other injected workflow clients and all selected
  position/candidate navigation behavior remain independent.
- Any clean HTTP error mapping must use the generated response status and typed code; aborted requests remain aborted.

## Stages

1. **pending - Replace analysis transport, state, and clean display derivation.** Ordered actions:
   1. Replace the legacy types and handwritten `/api/evaluation` requests in `analysisApi.ts` with clean lifecycle,
      current-result, line, request, and failure types. Use the central generated operations directly, validate the
      requested FEN and response identity, tolerate additive response fields, and map only the accepted clean fields.
      The default client must call `getAnalysis({ query: { fen }, signal })` and
      `requestAnalysis({ body: { fen, quality: "tool" }, signal })`; it must not expose a separate status method.
   2. Update `useAnalysisState` to observe automatically for every selected FEN, request only from the deliberate
      Analyze intent, poll with clean observation while queued/running, retain a result during active work, and keep
      bounded polling, cancellation, counter-insensitive identity, and stale-response protection. A request failure
      must not invent a clean failed state or Retry-analysis action.
   3. Update `analysisPanelDisplay` and `evaluationDisplay` to derive from clean `state` and `result`; preserve line,
      WDL, SAN, score, terminal-empty, and retained-candidate presentation while removing eligibility, stale, failed,
      and Update/Retry-analysis derivation. Refresh the focused API, state, formatting, and evaluation-bar tests.
   - **Focused proof:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **180 seconds** and recommended
     coordinator Bash tool timeout **210000 ms**:
     `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/analysis/analysisApi.test.ts src/features/analysis/analysisState.test.ts src/features/analysis/analysisFormatting.test.ts src/features/analysis/evalBarDisplay.test.ts`
   - **Breakpoint:** none. Escalate if clean fields cannot support the accepted display, active-result retention needs
     a contract change, polling cannot use clean observation, or clean error/abort behavior cannot remain within the
     existing seam.

2. **pending - Rebuild the panel contract and Repertoire integration.** Ordered actions:
   1. Remove `stale`, `onUpdate`, `onRetry`, update help, and Retry-analysis rendering from `AnalysisPanel`. Keep only
      deliberate Analyze, observation Retry, request-pending, and request-error behavior. Ready and active-with-result
      states must render the current candidate result without an update/retry control. Remove obsolete CSS states while
      preserving the accepted panel composition, accessibility, responsive, reduced-motion, and forced-colors behavior.
   2. Wire `RepertoireBuilderWorkspace` to the new analysis request intent and clean display contract. Continue passing
      `currentPosition.fen` to analysis, retain the candidate callback path, and leave position-context,
      move-response, Preferred Move, game loading, and navigation wiring unchanged. Update `RepertoireAnalysisTabs`
      only as required by the controlled panel type.
   3. Update the analysis panel tests, Repertoire workspace test helpers and focused workspace tests. Extend only the
      adoption allowlist needed for the neutral analysis API module; prohibit direct generated-directory imports and
      preserve the other consumer clients.
   - **Focused proof:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds** and recommended
     coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/analysis/AnalysisPanel.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx src/api/noAdoption.test.ts`
   - **Breakpoint:** none. Escalate if preserving candidate activation, selected-position identity, existing result
     visibility, accessibility behavior, or another injected workflow requires a product, visual, API, or ownership
     decision.

3. **pending - Refresh stories and prove the visible clean lifecycle.** Ordered actions:
   1. Replace old analysis story/test fixtures with clean `not_requested`, `queued`, `running`, `ready`, active-with-
      result, observation-error, request-pending, request-error, and terminal-empty cases. Ensure scripted clients
      prove observation does not request work and that deliberate requests use the clean request seam.
   2. Refresh `AnalysisPanel` and directly affected Repertoire workspace/preferred-workflow stories without changing
      the existing composition or visual direction. Add one bounded workspace journey named for the selected-position
      analysis lifecycle that proves automatic observation, deliberate request, polling, retained result, and candidate
      navigation.
   3. Update the existing focused browser assertions in the analysis-panel and Repertoire Storybook specs. Run only the
      focused Storybook and browser commands below; do not add a route, server, dependency, or live backend workflow.
   - **Focused Storybook proof:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds** and
     recommended coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/analysis/AnalysisPanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`
   - **Focused browser proof - Analysis Panel:** From `G:\ChessMoveTrainer`, command-level timeout **240 seconds** and
     recommended coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/analysis-panel-storybook.spec.ts --grep "controlled state|actions deliberate" --timeout=30000`
   - **Focused browser proof - Repertoire:** From `G:\ChessMoveTrainer`, command-level timeout **240 seconds** and
     recommended coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "selected-position analysis lifecycle" --timeout=30000`
   - **Breakpoint:** none. Escalate if the existing Storybook composition or bounded browser setup needs a new route,
     server, dependency, visual direction, or out-of-scope file, or if the browser proof cannot show the settled
     active-result and candidate-navigation behavior.

Stages are sequential; no parallel stages. A passing proof remains valid until a later stage changes its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only proof they invalidate.
The coordinator may split an oversized stage without changing the outcome or requiring a new decision.

## Progress and decisions

- **Assessment:** complete - the approved route, clean-to-view-model mapping, current seams, focused proof, and
  exclusions were assessed without edits.
- **Plan setup:** complete - this Plan records the approved three-stage implementation boundary.
- **Stage 1:** complete - proof: clean generated transport, state, polling, result retention, and display derivation;
  focused proof passed with 4 test files and 30 tests; breakpoint: none.
- **Stage 2:** complete - proof: panel contract, Repertoire wiring, candidate/navigation preservation, and consumer
  isolation; focused proof passed with 6 test files and 46 tests; breakpoint: none.
- **Stage 3:** complete - proof: refreshed Storybook fixtures and two focused browser journeys; breakpoint: none.
- **Acceptance/closeout:** complete - coordinator accepted all retained focused proof, confirmed the production analysis
  source no longer requests `/api/evaluation`, advanced the master plan to `CONSUMER-06`, and moved this Plan to done.
- **Closeout decision:** accept `CONSUMER-05` because all five finite proof groups passed, the settled deliberate Tool
  lifecycle and selected-position behavior are directly covered, other consumer seams and legacy routes remain intact,
  and the documentation-only closeout invalidated no source proof.

## Proof

1. **Clean transport/state/display derivation:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **180s**,
   Bash tool timeout **210000 ms**:
   `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/analysis/analysisApi.test.ts src/features/analysis/analysisState.test.ts src/features/analysis/analysisFormatting.test.ts src/features/analysis/evalBarDisplay.test.ts`
   **Result:** passed - 4 test files and 30 tests.
2. **Panel, Repertoire integration, and adoption/isolation:** From `G:\ChessMoveTrainer\frontend`, command-level timeout
   **240s**, Bash tool timeout **270000 ms**:
   `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/analysis/AnalysisPanel.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx src/api/noAdoption.test.ts`
   **Result:** passed - 6 test files and 46 tests.
3. **Storybook behavior:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **240s**, Bash tool timeout
    **270000 ms**:
    `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/analysis/AnalysisPanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`
    **Result:** passed - 4 test files and 52 tests.
4. **Analysis Panel browser journey:** From `G:\ChessMoveTrainer`, command-level timeout **240s**, Bash tool timeout
    **270000 ms**:
    `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/analysis-panel-storybook.spec.ts --grep "controlled state|actions deliberate" --timeout=30000`
    **Result:** passed - 2 tests.
5. **Repertoire selected-position analysis browser journey:** From `G:\ChessMoveTrainer`, command-level timeout **240s**,
    Bash tool timeout **270000 ms**:
    `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "selected-position analysis lifecycle" --timeout=30000`
    **Result:** passed - 1 test.

These are the complete implementation proof groups for this Plan. No lint, formatting, broad type/build, source-size,
aggregate, repository-hygiene, Quality, backend, generation, or route-retirement proof is included. Passing behavioral
proof is retained until a later affecting change invalidates it.

## Acceptance

- Selecting or navigating a Repertoire position performs clean observation only and never automatically submits engine
  work.
- **Analyze position** is the sole analysis request control and its generated POST always sends `quality: "tool"`.
- Queued/running clean observations are displayed and polled through generated GET observation; polling is bounded and
  abort/stale-response safe.
- A current complete result remains visible while queued/running work is active and is replaced by the ready result.
- Ready results expose no Update or Retry-analysis action; no stale, failed, history, attempt, or queue-internal state is
  presented.
- Retry observation remains available for observation load/transport failure, and request failure does not invent a
  failed lifecycle or Retry-analysis control.
- Candidate lines remain native activation controls, playing a candidate continues to the resulting selected position,
  and existing history/navigation behavior remains intact.
- No production frontend analysis request uses `/api/evaluation`; legacy evaluation routes remain served and untouched.
- Preferred Move, position-context, move-response, game loading, generated output, `frontend/src/api/client.ts`, and
  all unrelated worktree material remain unchanged.
- All five focused finite proof commands pass.

## Escalation boundaries

- Any change to the settled trigger, selected-position meaning, requested Tool quality, lifecycle/result visibility,
  candidate interaction, navigation, error meaning, or acceptance criteria.
- Any backend, database, schema, OpenAPI, generated-client, dependency, route-retirement, worker/engine, cache,
  compatibility, fallback, dual-read, or second-owner change.
- Any need to retain action-shaped Update/Retry semantics, expose queue internals/history/failure state, add browser
  quality or arbitrary settings, or introduce a new analysis data model.
- Any silent migration of Preferred Move, position context, move response, game loading, or another consumer.
- Any missing generated operation/type, nondeterministic generated output, direct generated-directory import, new route,
  server, visual direction, or out-of-scope path.
- Any conflicting unrelated worktree edit, completed-record/grilling-record edit, destructive action, Quality phase,
  broad maintenance run, commit, push, branch, worktree, or stash request.

## Visible result

> In Repertoire, the selected position shows its clean analysis state, deliberately requests Tool analysis only when the
> user clicks Analyze position, and keeps any current result visible while new work runs.
