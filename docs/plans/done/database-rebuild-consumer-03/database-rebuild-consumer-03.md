# Repertoire clean position context - Existing reach and corpus behavior stays intact

> **Status:** done - accepted 2026-09-10

- **Read trigger:** Before assessing, implementing, validating, repairing, accepting, or closing
  `CONSUMER-03` Repertoire position-context work.
- **Upstream:** [CONSUMER-03 direction](../../../grilling-docs/database-rebuild-consumer-03.md) (primary product
  behavior); [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) (sequence,
  ownership, and boundaries); [position-insight enrichment](../../../grilling-docs/database-rebuild-position-insight-enrichment.md)
  (clean response meanings); accepted [CONSUMER-02 Plan](../../done/database-rebuild-consumer-02/database-rebuild-consumer-02.md)
  (selected-position and session boundaries); accepted [POSITION-INSIGHT-01 Plan](../../done/database-rebuild-position-insight-01/database-rebuild-position-insight-01.md)
  (generated enriched operation); and [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md).

## Outcome

Migrate Repertoire's existing position-context workflow from the legacy position-context request to the generated
`getPositionInsight()` operation. The selected position remains lazy, the board-bottom color becomes the requested
trainer color, and the existing frequency, compact summary, absence, loading/error, and corpus-gated saveability
behavior remains unchanged.

## Scope

- **Included:** Direct generated position-insight transport through the approved central API module; the required
  `fen`, `trainer_color`, and request-time UTC date-shaped `as_of`; a narrow C03 context/domain mapping; selected-FEN
  loading, cancellation, stale-response protection, retry, and board-flip refetch; frequency and Repertoire model
  updates; preserved user-facing error meanings; test and Storybook injection fixtures; the explicit client-adoption
  guard; and focused unit, Storybook, and browser proof.
- **Expected areas:** `frontend/src/features/position-context/`,
  `frontend/src/features/position-reach-frequency/`, the position-context workflow/model/panel/helper/test/story
  areas under `frontend/src/features/repertoire-builder/`, `frontend/src/api/noAdoption.test.ts`, and
  `tests/e2e/repertoire-builder-storybook.spec.ts`. The existing `frontend/src/api/client.ts` export and generated
  client surface are expected to be retained, not regenerated or redesigned.
- **Excluded:** Backend or database work; schema or API contract changes; generated artifact changes; fallback,
  compatibility, or dual-read adapters; reconstruction of the old `overall_exists`/color-count response; a second
  cache; presentation redesign; `/api/position-context` retirement; Viewer work; C04 observed-move adoption; C05
  analysis migration; C06 preferred-move migration; other route retirement; dependency changes; broad maintenance;
  edits to the master plan, completed Plans, or grilling records during implementation; and any commit or push.

## Stages

1. **accepted - Establish the clean transport, C03 context boundary, and derived meanings.** Ordered actions:
   replace the legacy request in the existing injectable position-context seam with a direct
   `getPositionInsight()` call imported only from `frontend/src/api/client.ts`; pass the current selected FEN, the
   bottom-board `ChessSide` as `trainer_color`, and `new Date().toISOString().slice(0, 10)` as a neutral request-time
   UTC `as_of`; keep that date implementation-only and independent of Preferred Move date state; map the generated
   result into only the context facts C03 needs, tolerating additive opening, observed-move, analysis, and preference
   fields; preserve the existing safe failure mapping and loading copy; and update the context state seam so its
   request identity includes the selected FEN, trainer color, and refresh key while retaining cancellation and stale
   response protection. Update the pure Repertoire and Position Reach Frequency models to use
   `experience.distinct_game_count`, `experience.total_game_count`, and `observed_in_games`, and update their focused
   fixtures/tests. Extend the direct-adoption guard for the one approved C03 runtime import without allowing direct
   generated-directory imports.
   - **Focused proof:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **180 seconds** and recommended
     coordinator Bash tool timeout **210000 ms**:
     `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/position-context/positionContextApi.test.ts src/features/position-context/positionContextState.test.ts src/features/position-reach-frequency/positionReachFrequencyModel.test.ts src/features/position-reach-frequency/PositionReachFrequency.test.tsx src/features/repertoire-builder/repertoireWorkflowModel.test.ts`
   - **Breakpoint:** escalate if the generated operation cannot be called directly with all three required inputs,
     if the clean result cannot provide the approved counts and observation flag, if additive fields require a new
     contract, or if preserving the existing user-facing loading/error meanings requires a product decision.

2. **accepted - Wire the clean context through Repertoire while preserving later-consumer boundaries.** Ordered
   actions: pass `bottomColor` into context loading from `usePreferredMoveWorkflow`; continue requesting only
   `session.currentPosition.fen`, never the Preferred Move parent FEN; update the context client prop, panel types,
   model consumers, test clients, and Repertoire fixtures; preserve `Seen in N games as White/Black`, the selected
   color's distinct-game count, and the existing zero-versus-absent behavior; use `observed_in_games` for corpus-gated
   saveability; preserve loading, retry, cancellation, and error rendering; and prove that move-response, analysis,
   and preferred-move clients remain on their current legacy workflows. Do not consume the same insight response's
   observed moves, analysis, opening, or preference fields.
   - **Focused proof:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds** and recommended
     coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx src/api/noAdoption.test.ts`
   - **Breakpoint:** escalate if a shared-module change silently migrates C04-C06, if selected context follows a
     preferred-move parent instead of the current displayed FEN, if flipping the board cannot refetch for the new
     bottom color, or if saveability can no longer distinguish globally unseen from observed-but-zero-for-this-color.

3. **accepted - Refresh Storybook fixtures and prove the visible C03 journey.** Ordered actions: update the existing
   Position Reach Frequency, Session Panel, and Repertoire workspace fixtures and assertions to represent one
   trainer-color insight at a time; add focused coverage for white/black requests, board-flip refetch, selected-color
   zero, globally unseen, loading/error, and unchanged compact copy/saveability; keep the settled responsive layout,
   accessibility behavior, and presentation unchanged; and add or update one focused Playwright scenario named for
   position context following the trainer color. The browser scenario must use the existing bounded Storybook setup,
   not a new application route or visual direction.
   - **Focused proof:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds** and recommended
     coordinator Bash tool timeout **270000 ms**:
      `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/position-reach-frequency/PositionReachFrequency.stories.tsx src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`
   - **Focused browser proof:** from `G:\ChessMoveTrainer`, command-level timeout **240 seconds** and recommended
     coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "position context follows trainer color" --timeout=30000`
   - **Breakpoint:** escalate if the existing Storybook composition cannot show the confirmed states without a visual
     redesign, if the browser proof needs a new dependency or server, or if a story exposes later-consumer fields as
     newly adopted UI.

4. **accepted - Coordinator closeout evidence, not an implementation behavior stage.** After Stages 1-3 are accepted,
   the coordinator records the focused proof, preserved boundaries, and any retained proof in this Plan. Only then
   may the coordinator advance the live master plan's next selectable slice from `CONSUMER-03` to `CONSUMER-04`.
   This closeout does not authorize changes to completed Plans, grilling records, backend routes, or any later consumer.
   - **Focused proof:** manual review of this Plan, the confirmed C03 grilling record, the enrichment record, and the
     live master-plan passages; no additional behavioral command.
   - **Breakpoint:** escalate any contradiction in approved behavior, ownership, generated-client usage, route
     retirement timing, or later-consumer isolation.

Stages are sequential; no stage runs in parallel. A passing proof remains valid until a later stage changes its
command, inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only proof they
invalidate.

## Progress and decisions

- **Assessment:** done - the repository seams, generated call shape, as-of recommendation, behavior meanings,
  injection points, hidden coupling risks, and focused proof groups were assessed without edits.
- **Plan setup:** done - the approved assessment was recorded before product or test implementation started.
- **Scope correction:** `PreferredMoveWorkflow.stories.tsx` directly consumes the changed context fixture and is now
  included in Stage 3's Storybook proof. This is a necessary fixture/proof correction with no behavior, direction, or
  acceptance change.
- **Stage 1:** accepted 2026-09-10 - the generated transport, narrow context mapping, trainer-color request identity,
  derived frequency/summary/saveability meanings, and direct-adoption guard are implemented. The focused command in
  Proof item 1 passed **47/47 tests across 5 files** with its 180-second command timeout and 210000 ms Bash tool
  timeout. No fallback, generated-artifact change, or later-consumer adoption was introduced.
- **Stage 2:** accepted 2026-09-10 - Repertoire now requests context for `session.currentPosition.fen` and the current
  board-bottom trainer color; flipping refetches without changing the selected position. The focused command in Proof
  item 2 passed **31/31 tests across 5 files** with its 240-second command timeout and 270000 ms Bash tool timeout.
  Stage 1 proof remains valid, and C04-C06 clients remain unmigrated.
- **Stage 3:** accepted 2026-09-10 - after an interrupted Flash attempt left partial fixture work, a fresh Luna session
  bounded and completed the stage. The final Storybook command in Proof item 3 passed **51/51 tests**, and the focused
  browser command in Proof item 4 passed **1/1 scenario**. Stage 1 and Stage 2 proof remained valid.
- **Stage 4:** accepted 2026-09-10 - the coordinator reviewed the retained proof and final scope, advanced the master
  plan to `CONSUMER-04`, and moved this completed Plan to `docs/plans/done/`.

## Proof

1. **Clean transport/state/frequency/model behavior - PASS, 47/47 tests across 5 files.** Workdir
   `G:\ChessMoveTrainer\frontend`; command-level timeout **180 seconds**; recommended coordinator Bash tool timeout
   **210000 ms**:
   `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/position-context/positionContextApi.test.ts src/features/position-context/positionContextState.test.ts src/features/position-reach-frequency/positionReachFrequencyModel.test.ts src/features/position-reach-frequency/PositionReachFrequency.test.tsx src/features/repertoire-builder/repertoireWorkflowModel.test.ts`
2. **Repertoire workflow and adoption/later-consumer isolation - PASS, 31/31 tests across 5 files.** Workdir
   `G:\ChessMoveTrainer\frontend`; command-level timeout **240 seconds**; recommended coordinator Bash tool timeout
   **270000 ms**:
   `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx src/api/noAdoption.test.ts`
3. **Changed Storybook fixtures and play assertions - PASS, 51/51 tests.** Workdir `G:\ChessMoveTrainer\frontend`;
   command-level timeout **240 seconds**; recommended coordinator Bash tool timeout **270000 ms**:
    `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/position-reach-frequency/PositionReachFrequency.stories.tsx src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`
4. **Focused browser journey - PASS, 1/1 scenario.** Workdir `G:\ChessMoveTrainer`; command-level timeout **240
   seconds**; recommended coordinator Bash tool timeout **270000 ms**:
   `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "position context follows trainer color" --timeout=30000`

These are the complete implementation proof groups for this Plan. No lint, formatting, broad type/build, source-size,
aggregate maintenance, repository-hygiene, Quality, complete-suite, backend, generation, or route-retirement proof is
included.

## Acceptance

- Repertoire's production position-context request uses only generated `getPositionInsight()` through the central API
  module, with the current selected FEN, the board-bottom trainer color, and a non-visible UTC `YYYY-MM-DD` `as_of`.
- Only the selected current position is loaded. Flipping the board preserves the position and refetches insight for the
  opposite bottom color, with existing loading/cancellation behavior.
- Position Reach Frequency uses `experience.distinct_game_count` over `experience.total_game_count`, and the frontend
  retains its existing formatted percentage. Occurrence totals do not replace the distinct-game meaning.
- The compact summary remains exactly `Seen in N games as White/Black` when the selected color has experience, and
  `Never seen as White/Black` otherwise; it does not gain a denominator or percentage.
- An observed position with zero selected-color experience remains an available `0 of N`/`0%` position and remains
  saveable. A globally unseen position retains the existing absent presentation and remains blocked by the corpus
  gate.
- Existing loading and user-facing error meanings remain equivalent, additive insight fields are tolerated, and C03
  does not adopt observed moves, analysis, opening recognition, or preference data.
- C04 move-response, C05 analysis, and C06 preferred-move workflows remain on their current consumers; no
  `/api/position-context` retirement or other route retirement occurs.
- No fallback, compatibility layer, second cache, backend/database/API contract change, visual redesign, dependency
  change, generated-artifact change, or unrelated worktree change is introduced.
- All four focused proof groups pass. Proof remains retained until a later change invalidates its command, inputs,
  behavior, configuration, dependencies, or environment.

## Escalation boundaries

- Any change to the settled product behavior, response field meanings, distinct-game or total-game denominators,
  selected-color filtering, global observation semantics, loading/error copy, canonical FEN/date behavior, or
  saveability gate.
- Any need for a backend, database, schema, API route, OpenAPI, generated-client, dependency, cache, or second SQL/data
  owner change.
- Any need for a fallback, dual read, compatibility adapter, old response-shape reconstruction, second-color dataset,
  route retirement, Viewer behavior, or old-database read.
- Any request to make `as_of` product-visible, couple it to Preferred Move date editing, or choose a different date
  meaning than the approved request-time UTC date-shaped value.
- Any newly discovered production consumer, shared-module ownership conflict, direct generated-directory import, or
  silent migration of C04-C06.
- Any need for a visual redesign, new Storybook/server/dependency setup, broad maintenance, Quality validation, master
  plan change before acceptance, completed-record edit, commit, or push.

## Visible result

> In Repertoire, the selected position keeps its existing reach-frequency, compact summary, absence, loading/error, and
> corpus-saveability behavior, and flipping the board reloads that context for the new bottom color.
