# Repertoire clean preferred timeline workflow - Current selected transitions use clean preferred operations

> **Status:** done - accepted 2026-09-11

- **Read trigger:** Before assessing, implementing, validating, repairing, accepting, or closing CONSUMER-06.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) governs the
  consumer sequence, clean preferred semantics, isolation, and RETIRE-05 timing; [CONSUMER-06 direction](../../../grilling-docs/database-rebuild-consumer-06.md)
  governs the confirmed current-day window and open-ended mutation policy; accepted [CONSUMER-05](../../done/database-rebuild-consumer-05/database-rebuild-consumer-05.md)
  governs the immediate Repertoire baseline; accepted [CONSUMER-02](../../done/database-rebuild-consumer-02/database-rebuild-consumer-02.md)
  governs selected parent-FEN/outgoing-UCI meaning; accepted [CLEAN-08](../../done/database-rebuild-clean-08/database-rebuild-clean-08.md),
  [CLEAN-09](../../done/database-rebuild-clean-09/database-rebuild-clean-09.md), and [CLEAN-10](../../done/database-rebuild-clean-10/database-rebuild-clean-10.md)
  govern the generated preferred GET/PUT/DELETE contracts.

## Outcome

Repertoire's existing selected trainer transition workflow reads, saves, and removes Preferred Move values through the
generated clean plural operations. A preference remains the outgoing move after the selected transition's parent FEN.
The workflow reads only the current UTC day window `[today, tomorrow)`, applies PUT and DELETE from UTC today onward,
refreshes through the same clean window after mutation, maps clean move/no-preference/unconfigured values into the
current presentation, and permits a legal novel parent FEN without corpus membership.

## Scope

- **Included:** Clean generated preferred transport; UTC today/tomorrow calculation; one-day timeline-to-current-value
  mapping; typed clean error mapping; backend-authoritative mutation refresh; selected parent-FEN/outgoing-UCI
  preservation; removal of corpus membership as a save prerequisite; existing Save, Remove, confirmation, loading,
  retry, stale-response, and no-date presentation behavior; consumer isolation; directly affected unit/component tests,
  Storybook stories, fixtures, adoption guards, and one focused browser journey.
- **Expected areas:** `frontend/src/features/repertoire-builder/preferredMoveApi.ts`, `preferredMoveState.ts`,
  `preferredMoveWorkflowState.ts`, `repertoireWorkflowModel.ts`, `PreferredMovePanel.tsx`,
  `RepertoireBuilderWorkspace.tsx`, `repertoireBuilderTestHelpers.tsx`, `repertoireBuilderStoryHelpers.ts`,
  `repertoireBuilderStoryAssertions.ts`, `frontend/src/features/repertoire-builder/README.md`;
  `preferredMoveApi.test.ts`, `preferredMoveState.test.ts`, `repertoireWorkflowModel.test.ts`,
  `PreferredMovePanel.test.tsx`, `RepertoireBuilderWorkspace.test.tsx`, `RepertoireBuilderWorkspaceWorkflow.test.tsx`,
  and `RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx`; `PreferredMovePanel.stories.tsx`,
  `PreferredMoveWorkflow.stories.tsx`, `RepertoireBuilderWorkspacePreferredMove.stories.tsx`,
  `RepertoireBuilderWorkspace.stories.tsx`, and `RepertoireSessionPanel.stories.tsx`;
  `frontend/src/api/noAdoption.test.ts`, the obsolete preferred-adoption assertion in
  `frontend/src/api/generatedSurface.test.ts`, and `tests/e2e/repertoire-builder-storybook.spec.ts`.
- **Excluded:** Calendar or date-picker UI; future schedule display; rolling or far-future read horizons; caller-side
  interval splits, merges, gaps, overlaps, or normalization; authored repertoire lines, trees, or persistence; backend,
  schema, OpenAPI, generated files, `frontend/src/api/client.ts`, dependency, or clean-contract changes; compatibility
  or fallback behavior; other consumer migration; singular legacy route retirement; visual redesign; broad maintenance;
  Quality validation; completed-record or grilling-record changes; commits, pushes, branches, worktrees, stashes, and
  unrelated or accepted CONSUMER-05 worktree changes.

## Stages

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome
or requiring a new decision. A passing proof remains valid until a later stage changes its command, inputs, exercised
behavior, configuration, dependencies, or environment; later stages rerun only invalidated proof.

1. **pending - Replace the legacy preferred transport with clean timeline state.** Ordered actions:
   1. Replace the singular-route fetch/validation/response seam in `preferredMoveApi.ts` with the central generated
      `getPreferredMoves`, `putPreferredMoves`, and `deletePreferredMoves` operations while preserving the injected
      `PreferredMoveClient` seam and abort behavior.
   2. Derive UTC today and tomorrow for GET `{ query: { fen, from: today, until: tomorrow } }`. Send PUT and DELETE
      bodies with the parent FEN, `effective_from: today`, the selected outgoing move or removal, and no
      `effective_until`.
   3. Map the first complete clean segment for the one-day window into the existing saved/no-saved view model. Derive
      SAN from the parent FEN and UCI; present `no_preference` and `unconfigured` as the existing no-saved-move state.
      Map only the accepted clean error codes and statuses; do not preserve `position_not_found` or timestamp errors.
   4. Keep `preferredMoveState` cancellation, stale-response protection, same-position refresh retention, and mutation
      confirmation, but make every post-mutation confirmation a fresh clean finite GET. Do not use mutation periods to
      perform client-side schedule arithmetic.
   5. Refresh the focused preferred API/state tests for request bodies, today/tomorrow boundaries, tagged values, SAN,
      clean errors, refresh behavior, and novel legal FEN acceptance.
   - **Focused proof:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **180s** and recommended Bash tool
     timeout **210000 ms**:
      `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/preferredMoveApi.test.ts src/features/repertoire-builder/preferredMoveState.test.ts`
   - **Breakpoint:** none. Escalate if the generated response cannot identify the one-day segment, if SAN cannot be
     derived from the parent FEN/UCI, if clean errors cannot remain typed, or if the confirmed current-day/open-ended
     policy requires a contract or caller-side schedule calculation.

2. **pending - Integrate clean parent-transition mutations and remove the corpus gate.** Ordered actions:
   1. Preserve `focusedOwnerTransition`, `preferredPositionFen`, and selected outgoing UCI semantics in
      `preferredMoveWorkflowState.ts`; the mutation FEN remains the selected transition's parent, never the resulting
      position.
   2. Remove `observedInGames`/`saveability` as a prerequisite for Save in `repertoireWorkflowModel.ts`,
      `preferredMoveWorkflowState.ts`, and `PreferredMovePanel.tsx`. Keep position-context loading, error feedback,
      trainer-side ownership, legal selected-move requirements, and current frequency/context presentation independent
      of save permission.
   3. Preserve current Save/Remove labels, confirmation, pending and failure retention, explicit saved-move playback,
      no calendar UI, selected-position navigation, analysis, position context, move-response distribution, and game
      loading. Update the panel's clean failure copy without adding a no-preference action.
   4. Update workspace/component tests and helpers to assert clean GET/PUT/DELETE payloads, parent FEN/outgoing UCI,
      current-day dates, novel-parent Save with absent corpus observation, clean refresh, and unchanged C05 behavior.
      Update `noAdoption.test.ts` to allow only the neutral preferred adapter's central-client imports while retaining
      every existing C05 allowlist entry. Remove only the obsolete preferred-operation prohibition from
      `generatedSurface.test.ts`; keep its accepted generated surface assertions.
   - **Focused proof:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **240s** and recommended Bash tool
     timeout **270000 ms**:
      `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/PreferredMovePanel.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/api/noAdoption.test.ts src/api/generatedSurface.test.ts`
   - **Breakpoint:** none. Escalate if another production consumer uses the neutral preferred adapter, if parent/outgoing
     identity changes, if context/analysis behavior must change to permit novel parents, or if C05's accepted analysis
     lifecycle cannot remain intact.

3. **pending - Refresh focused stories and prove the clean visible workflow.** Ordered actions:
   1. Update the directly affected preferred fixtures, Storybook clients, assertions, and stories from legacy response
      shapes and stale staged vocabulary to the selected-transition clean model. Preserve the existing relationship
      presentation, responsive composition, accessibility, no-calendar behavior, and C05 analysis stories.
   2. Add one bounded Storybook journey that captures the current-day clean GET, saves a legal novel parent transition,
      refreshes to the normalized move result, removes it, and observes the clean unconfigured result. Keep explicit
      no-preference and unconfigured values in the current no-saved-move presentation.
   3. Update the existing Repertoire Storybook browser proof to assert clean payloads and absence of singular legacy
      requests, selected parent-FEN behavior, novel-parent saving, mutation refresh, and no calendar/future schedule UI.
      Do not start a live backend workflow or add a route/server/dependency.
   - **Focused Storybook proof:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **240s** and recommended
     Bash tool timeout **270000 ms**:
     `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx src/features/repertoire-builder/PreferredMovePanel.stories.tsx`
   - **Focused browser proof:** From `G:\ChessMoveTrainer`, command-level timeout **240s** and recommended Bash tool
     timeout **270000 ms**:
     `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "clean preferred timeline and novel parent" --timeout=30000`
   - **Breakpoint:** none. Escalate if the existing Storybook composition cannot show the clean state without a visual
     redesign, if browser proof needs a live backend or new dependency, or if a story-only baseline mismatch requires
     unrelated cleanup.

## Progress and decisions

- **Assessment:** complete - the migration map, affected seams, consumer isolation, focused proof envelope, and baseline
  conflicts were assessed without edits.
- **Date/window decision:** complete - GET uses UTC `[today, tomorrow)`; PUT and DELETE use UTC today as
  `effective_from` with omitted `effective_until`; mutations refresh through the same GET.
- **Stage 1:** complete - clean transport, tagged timeline mapping, date derivation, typed errors, and state refresh;
  breakpoint: none; focused proof passed with 31 tests.
- **Stage 2:** complete - parent-transition integration, corpus-gate removal, C05 preservation, and consumer isolation;
  breakpoint: none; focused proof passed with 48 tests.
- **Stage 3:** complete - focused Storybook fixtures, visible novel-parent journey, and browser proof; breakpoint: none;
  focused Storybook proof passed with 55 tests and browser proof passed with 1 test.
- **Acceptance/closeout:** complete - coordinator accepted the retained focused proof, confirmed no singular preferred
  request remains in production frontend source, refreshed the thin Repertoire signpost, advanced the master plan to
  `RETIRE-01`, and moved this Plan to done.
- **Closeout decision:** accept `CONSUMER-06` because all four finite proof groups passed, the current-day clean workflow
  and legal novel-parent behavior are directly covered, other consumers and singular legacy routes remain intact, and
  the documentation-only closeout invalidated no source proof.

## Proof

1. **Clean preferred transport and timeline state:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **180s**,
   Bash tool timeout **210000 ms**:
   `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/preferredMoveApi.test.ts src/features/repertoire-builder/preferredMoveState.test.ts`.
   Result: 2 test files passed; 31 tests passed.
2. **Parent integration, corpus-gate removal, and isolation:** From `G:\ChessMoveTrainer\frontend`, command-level timeout
   **240s**, Bash tool timeout **270000 ms**:
   `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/PreferredMovePanel.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/api/noAdoption.test.ts src/api/generatedSurface.test.ts`.
   Result: 7 test files passed; 48 tests passed.
3. **Storybook behavior:** From `G:\ChessMoveTrainer\frontend`, command-level timeout **240s**, Bash tool timeout
   **270000 ms**:
    `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx src/features/repertoire-builder/PreferredMovePanel.stories.tsx`.
    Result: 4 test files passed; 55 tests passed.
4. **Repertoire clean preferred browser journey:** From `G:\ChessMoveTrainer`, command-level timeout **240s**, Bash tool
    timeout **270000 ms**:
    `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "clean preferred timeline and novel parent" --timeout=30000`.
    Result: 1 test passed.

These are the complete implementation proof groups for this Plan. No backend, API contract, generation, lint,
formatting, broad type/build, source-size, aggregate, full-suite, repository-hygiene, or Quality validation belongs to
this Plan. Passing behavioral proof is retained until a later stage changes its command, inputs, exercised behavior,
configuration, dependencies, or environment.

## Acceptance

- Repertoire's preferred workflow uses only the generated clean plural GET/PUT/DELETE operations through the approved
  neutral client seam; no production preferred request uses `/api/preferred-move`.
- Current reads request exactly the finite UTC window `[today, tomorrow)` for the selected parent FEN.
- Save and Remove send UTC today as `effective_from`, omit `effective_until`, use the selected parent FEN and outgoing UCI,
  and refresh through the same finite GET.
- Clean move values display with SAN derived from the parent FEN/UCI; clean no-preference and unconfigured values display
  as the current no-saved-move state.
- A legal novel parent FEN can be saved even when corpus observation is false; context and frequency remain informational
  and their accepted requests/meanings remain unchanged.
- Backend-normalized results determine post-mutation display; the frontend performs no schedule interval arithmetic.
- Selected-transition navigation, saved-move playback, analysis, position context, move-response distribution, game
  loading, responsive composition, accessibility behavior, and C05 clean analysis lifecycle remain intact.
- No other production consumer adopts preferred operations, singular legacy routes remain served, and all four focused
  behavioral proof commands pass.

## Escalation boundaries

- Any change to UTC today/tomorrow reads, today-forward open-ended PUT/DELETE behavior, tagged-value presentation, or
  parent-FEN/outgoing-UCI meaning.
- Any request for calendar/date-picker UI, future-period display, a rolling/far-future horizon, authored repertoire
  lines, caller-side interval arithmetic, explicit no-preference controls, or distinction between no-preference and
  unconfigured in the current panel.
- Any backend, schema, OpenAPI, generated-file, client-export, dependency, route, compatibility, fallback, cache, or
  second data-owner change.
- Any migration of another consumer, change to accepted C05/C02 behavior or ownership, or retirement/editing/curation of
  singular `/api/preferred-move` routes; retirement remains RETIRE-05.
- Any need for visual redesign, a new Storybook route/server/dependency, broad baseline cleanup, Quality validation,
  completed-record/grilling-record edit, destructive action, unrelated worktree change, commit, or push.

## Visible result

> In Repertoire, a user can save or remove the selected trainer move for its parent position through the clean preferred
> timeline, including a legal novel parent FEN, and immediately see the backend-resolved current result.
