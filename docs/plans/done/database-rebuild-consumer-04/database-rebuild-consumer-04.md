# Repertoire observed-move distribution - True outgoing-occurrence pie

> **Status:** done - accepted 2026-09-10

- **Read trigger:** Before assessing, implementing, validating, repairing, accepting, or closing
  `CONSUMER-04` Repertoire move-response distribution work.
- **Upstream:** [database rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) (sequence,
  ownership, migration, and retirement boundaries); [CONSUMER-04 direction](../../../grilling-docs/database-rebuild-consumer-04.md)
  (settled product semantics); accepted [CONSUMER-03 Plan](../../done/database-rebuild-consumer-03/database-rebuild-consumer-03.md)
  (independent position-context seam and later-consumer boundary); and [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md).

## Outcome

Repertoire's Move responses pie uses the existing generated `getPositionInsight()` operation and answers:

> Among outgoing-move occurrences of the selected position in the selected trainer color's imported games, what
> percentage were move X?

Repeated position occurrences count separately, terminal occurrences have no outgoing move and are excluded, and the
complete raw pie represents the outgoing occurrence denominator before display rounding.

## Scope

- **Included:** Direct clean Position Insight transport through the existing injectable move-response client/state
  seam; request-time UTC `YYYY-MM-DD` `as_of`; response identity and count validation; legal UCI validation and
  frontend SAN derivation; occurrence-based model calculations and deterministic ranking; top-five plus expandable
  Other aggregation; distinct no-matching-games versus no-recorded-next-moves states; existing loading, retry,
  cancellation, stale-response, selection, responsive, and accessibility behavior; removal of per-reply opening
  names and obsolete overlap messaging; directly affected Repertoire fixtures, tests, and stories; and the approved
  generated-client adoption guard.
- **Expected areas:**
  `frontend/src/features/move-response-distribution/` production files, focused tests, and stories;
  directly affected move-response fixtures, tests, helpers, and stories under
  `frontend/src/features/repertoire-builder/`; and
  `frontend/src/api/noAdoption.test.ts` for the approved runtime import allowance. The existing bounded browser
  command is proof for the already-existing Storybook scenarios; it does not authorize a new route, server, or
  dependency.
- **Excluded:** C03 position-context behavior or transport; analysis and Preferred Move workflows; production
  workspace or Tabs redesign; backend, database, schema, OpenAPI, generated artifact, or dependency changes;
  fallback, dual-read, compatibility adapter, second cache, or new projection; date filtering or Preferred Move date
  coupling; legacy `/api/move-response-distribution` retirement; Viewer work; C05/C06 migration; other consumer
  migration; route retirement; visual direction changes; broad maintenance; edits to completed historical Plans or
  grilling records; and any commit or push.

The production `RepertoireBuilderWorkspace` wiring, `frontend/src/api/client.ts`, generated files, and
`positionContextApi.ts` remain unchanged unless a directly conflicting implementation fact makes a tiny
within-outcome correction essential; otherwise execution stops for escalation.

## Stages

1. **pending - Establish clean transport, validation, mapping, SAN, and occurrence domain behavior.** Ordered
   actions: keep the `MoveResponseDistributionClient` injection contract and replace its default handwritten legacy
   request with `getPositionInsight({ query: { fen, trainer_color, as_of }, signal })` through
   `frontend/src/api/client.ts`; use a request-time UTC date without exposing or sharing Preferred Move date state;
   narrow the clean response while tolerating additive fields; validate the requested position identity, trainer color,
   required count types, legal unique UCI moves, and reconciliation between observed move counts and
   `observed_move_totals.occurrence_count`; derive SAN from the selected FEN plus each UCI without mutating the board
   between moves; map clean errors to the existing move-response failure seam; update the adoption allowlist; rank
   replies by descending occurrence count with deterministic UCI tie-breaking; and update state emptiness to use
   `experience.distinct_game_count` and the outgoing occurrence total while retaining cancellation and stale-result
   protection. Do not add terminal counts to the denominator.
   - **Focused proof:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **180 seconds** and recommended
     coordinator Bash tool timeout **210000 ms**:
     `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/move-response-distribution/moveResponseDistributionApi.test.ts src/features/move-response-distribution/moveResponseDistributionModel.test.ts src/features/move-response-distribution/moveResponseDistributionState.test.tsx`
   - **Breakpoint:** escalate if the generated response cannot provide the approved counts, if outgoing totals cannot
     reconcile without changing backend semantics, if legal SAN cannot be derived from clean UCI data, if an error
     requires a new contract, or if C03 sharing/coupling appears necessary.

2. **pending - Rebuild the pie presentation and Repertoire integration behavior around occurrences.** Ordered actions:
   update model views, chart values/tooltips/description, control metrics and accessible labels to say occurrences and
   recorded outgoing moves; remove opening-name rendering and the overlap note; preserve the five-common-plus-Other
   disclosure, sector selection, keyboard behavior, selected-UCI reset, responsive layout, reduced-motion and
   forced-colors boundaries; preserve loading, unavailable/retry, no matching games, and matching-games-without-next-
   moves meanings; refresh focused component tests; update directly affected Repertoire integration fixtures/assertions;
   and prove the C03 context client remains an independent workflow while the move-response client receives the same
   selected FEN and trainer color through its existing seam.
   - **Focused proof:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds** and recommended
     coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/move-response-distribution/MoveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/api/noAdoption.test.ts`
   - **Breakpoint:** escalate if preserving the settled empty-state distinction, top-five/Other interaction,
     accessibility behavior, or stale/cancellation behavior requires a product or visual decision; if any shared
     change silently migrates C03, analysis, or Preferred Move; or if an out-of-bound test edit becomes necessary.

3. **pending - Refresh fixtures and stories and prove the visible Storybook journey.** Ordered actions: update all
   move-response feature stories and directly affected Repertoire story fixtures to use occurrence totals whose raw
   values reconcile; cover repeated occurrences, terminal-only/no-next-move data, deterministic ties, Other
   aggregation, SAN labels, no opening names, both empty meanings, loading/error/retry, selection, accessibility,
   constrained layouts, and representative responsive states; retain the existing Storybook composition and browser
   scenarios; then run the focused Storybook and bounded browser proof. Do not create a new browser route, server, or
   visual direction.
   - **Focused Storybook proof:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds** and
     recommended coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/move-response-distribution/MoveResponseDistribution.stories.tsx src/features/move-response-distribution/MoveResponseDistributionChart.stories.tsx src/features/move-response-distribution/MoveResponseDistributionControls.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`
   - **Focused browser proof:** from `G:\ChessMoveTrainer`, command-level timeout **240 seconds** and recommended
     coordinator Bash tool timeout **270000 ms**:
     `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "response distribution integration|dense distribution label cluster" --timeout=30000`
   - **Breakpoint:** escalate if the existing Storybook composition or bounded browser proof needs a new dependency,
     server, route, visual direction, or an edit outside the approved frontend product/test/story paths.

4. **done - Coordinator closeout and slice advancement, after implementation proof is accepted.** Ordered actions:
   record truthful progress, decisions, focused proof, preserved boundaries, and the visible result in this active
   Plan; advance the live database-rebuild master plan's next selectable slice from `CONSUMER-04` to `CONSUMER-05`;
   and move this Plan directory from `docs/plans/active/database-rebuild-consumer-04/` to
   `docs/plans/done/database-rebuild-consumer-04/`. This is documentation-only closeout after Stages 1-3 and does not
   invalidate accepted source proof. Completed historical Plans and grilling records remain unchanged.
   - **Focused proof:** manual review of this Plan, the retained focused proof, the C04 direction, the accepted C03
     Plan, and the live master-plan boundary; no additional behavioral command.
   - **Breakpoint:** escalate any contradiction in approved semantics, ownership, generated-client usage, consumer
     isolation, route retirement timing, acceptance, or retained proof.

Stages are sequential; no stage runs in parallel. A passing proof remains valid until a later stage changes its
command, inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only proof they
invalidate.

## Progress and decisions

- **Assessment:** done - the approved repository seams, generated operation, mapping, validation, UI boundaries,
  fixture impacts, and focused proof groups were assessed without edits.
- **Plan setup:** done - this Plan records the approved outcome and sequential implementation boundary before Stage 1.
- **Stage 1:** done - proof: clean transport, mapping, SAN, validation, occurrence model, and state behavior;
  breakpoint: none.
- **Stage 1 decision:** use the generated Position Insight operation through the existing injectable client seam;
  map only validated trainer-game and outgoing-occurrence facts, derive legal SAN per candidate, rank by occurrence
  count then UCI, and distinguish no matching games from matching games without next moves.
- **Stage 2:** done - proof: occurrence-based pie, empty/error/accessibility behavior, and Repertoire integration;
  breakpoint: none.
- **Stage 2 decision:** retain the existing chart geometry, five-plus-Other disclosure, selection, focus,
  responsive, reduced-motion, and forced-colors behavior while replacing presentation metrics with outgoing
  occurrences and removing opening and overlap content. Keep the existing generic `no-games` transport state while
  rendering the model's distinct no-games and no-next-moves messages.
- **Stage 3:** done - proof: updated Storybook fixtures/stories and bounded browser scenarios;
  breakpoint: none.
- **Stage 3 decision:** refresh existing move-response and Repertoire fixtures with reconciled outgoing-occurrence
  totals, keep deterministic SAN/top-five-plus-Other and empty-state coverage, and migrate only the two named browser
  scenarios' stale visible assertions. The narrow E2E scope correction also waits for the existing Storybook journey to
  settle before tab assertions and uses distribution-scoped responsive bounds at 320px because the unrelated existing
  Game Loader grid exceeds that viewport; no other browser scenarios were edited.
- **Stage 4:** done - proof: coordinator closeout review accepted the retained focused evidence, advanced the live
  master plan to `CONSUMER-05`, and moved this Plan to done; breakpoint: none.
- **Closeout decision:** accept `CONSUMER-04` because all four finite proof groups passed, the production source no
  longer contains the legacy move-response route request, the generated-client adoption remains isolated, and the
  documentation-only closeout invalidated no source proof.

## Proof

1. **Transport, domain, and state behavior:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **180
   seconds**, Bash tool timeout **210000 ms**:
   `timeout 180s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/move-response-distribution/moveResponseDistributionApi.test.ts src/features/move-response-distribution/moveResponseDistributionModel.test.ts src/features/move-response-distribution/moveResponseDistributionState.test.tsx`
   **passed: 3 files, 32 tests, 1.40 seconds** after the Stage 2 model presentation update invalidated the retained
   result; the existing deterministic floating-point assertion repair remains in place.
2. **Component and Repertoire integration behavior:** from `G:\ChessMoveTrainer\frontend`, command-level timeout
   **240 seconds**, Bash tool timeout **270000 ms**:
   `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/move-response-distribution/MoveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/api/noAdoption.test.ts`
   **passed: 4 files, 27 tests, 14.66 seconds**.
3. **Storybook behavior:** from `G:\ChessMoveTrainer\frontend`, command-level timeout **240 seconds**, Bash tool
   timeout **270000 ms**:
    `timeout 240s npm exec vitest -- --project storybook --run --testTimeout=30000 src/features/move-response-distribution/MoveResponseDistribution.stories.tsx src/features/move-response-distribution/MoveResponseDistributionChart.stories.tsx src/features/move-response-distribution/MoveResponseDistributionControls.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`
    **passed: 4 files, 26 tests, 14.01 seconds**.
4. **Visible browser behavior:** from `G:\ChessMoveTrainer`, command-level timeout **240 seconds**, Bash tool timeout
    **270000 ms**:
    `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "response distribution integration|dense distribution label cluster" --timeout=30000`
    **passed: 2 tests, 19.3 seconds**.

These are the complete implementation proof groups for this Plan. No lint, formatting, broad type/build, source-size,
aggregate maintenance, repository-hygiene, backend, generation, or route-retirement proof is included.

## Acceptance

- No Repertoire production request to `/api/move-response-distribution` remains.
- Generated Position Insight is called with the selected FEN, selected trainer color, request-time UTC `as_of`, and
  cancellation signal through the existing move-response client/state seam.
- The pie uses `observed_moves[].occurrence_count` over `observed_move_totals.occurrence_count`, counts repeated
  occurrences, excludes terminals, and totals 100% before display rounding.
- SAN is derived from the selected FEN and legal UCI; replies rank deterministically by occurrence count and UCI tie-
  break; five common moves and expandable Other remain.
- Opening labels and overlap wording are removed; occurrence counts and recorded-outgoing-move meanings appear in chart,
  controls, tooltips, and accessible text.
- No-matching-trainer-games and matching-games-without-recorded-next-moves remain distinct, with loading, error,
  retry, cancellation, stale-response, selection, responsive, and accessibility behavior preserved.
- C03 position context, analysis, Preferred Move, backend/contract/schema/generated output, and the legacy route remain
  unchanged.
- All four focused finite proof groups pass.

## Escalation boundaries

- Any backend, API contract, schema, OpenAPI, generated artifact, dependency, fallback, cache, second data owner, or
  shared-owner change.
- Inability to derive SAN from legal clean UCI data or reconcile observed totals without changing backend semantics.
- Any need to change the settled five-plus-Other interaction, empty-state meanings, date meaning, accessibility
  behavior, or visual direction.
- Any silent migration of C03, analysis, Preferred Move, another production consumer, or any route retirement.
- Any need to edit outside the approved frontend product/test/story paths, except the approved adoption guard.
- Any unrelated worktree conflict, destructive action, completed-record edit, commit, push, or broad maintenance run.

## Visible result

> Repertoire's Move responses tab shows a true occurrence-based pie: SAN moves, top five plus Other, terminal positions
> excluded, and no reply opening labels.
