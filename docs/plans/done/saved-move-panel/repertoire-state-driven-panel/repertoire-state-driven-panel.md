# Repertoire State-Driven Panel - four truthful saved-move states and current-position reach frequency

> **Status:** complete - Stage 3 automated proof passed and the required human visual review was accepted

- **Read trigger:** Read before implementing R2 Repertoire State-Driven Panel behavior or changing its focused
  tests, stories, or browser proof.
- **Upstream:** [Saved Move Panel master plan](../../../../master-plans/saved-move-panel/saved-move-panel.md);
  [settled saved move panel direction](../../../../grilling-docs/saved-move-panel-redesign.md); [D1 Persisted
  Effective-Date Read Contract](../../../done/saved-move-panel/persisted-effective-date-read-contract/persisted-effective-date-read-contract.md);
  [F1 Position Reach Frequency](../../../done/saved-move-panel/position-reach-frequency/position-reach-frequency.md);
  [R1 Repertoire Linear History Integration](../../../done/saved-move-panel/repertoire-linear-history-integration/repertoire-linear-history-integration.md)

## Outcome

Make `/repertoire` present the four settled saved-move states—no saved move, saved move, matching played move, and
unsaved played move—while displaying the persisted effective date truthfully, showing Position Reach Frequency for
the current position, and keeping shared history, board, workflow reads, and focus synchronized. Existing explicit
date and preferred-move mutation behavior remains authoritative.

## Scope

- **Included:** Repertoire-owned state derivation for the four settled panel states; last-played matching and
  unsaved-move focus; persisted `effective_at` display with UTC `Today` presentation when applicable; date changes
  through the existing UTC calendar and explicit Add/Edit/Save/Remove mutation paths; current-position
  `PositionReachFrequency` using the existing context and bottom/repertoire colour; preservation of loading,
  error, unsavable, staging, opponent-immediacy, and linear replacement semantics; focused unit tests; repertoire
  stories, helpers, assertions, and render fixtures; the existing targeted browser proof; and only existing-system
  styling needed by the panel composition.
- **Expected areas:**
  `frontend/src/features/repertoire-builder/{repertoireWorkflowModel.ts,repertoireWorkflowModel.test.ts,preferredMoveWorkflowState.ts,PreferredMovePanel.tsx,PreferredMovePanel.module.css,PreferredMovePanel.stories.tsx,RepertoireSessionPanel.tsx,RepertoireSessionPanel.module.css,RepertoireSessionPanel.stories.tsx,RepertoireBuilderWorkspace.tsx,RepertoireBuilderWorkspace.test.tsx,RepertoireBuilderWorkspace.stories.tsx,repertoireBuilderStoryHelpers.ts,repertoireBuilderStoryAssertions.ts,repertoireBuilderStoryRender.tsx,repertoireBuilderTestHelpers.tsx}`;
  `tests/e2e/repertoire-builder-storybook.spec.ts`.
- **Excluded:** Backend, API, storage, schema, migration, `as_of`, or persistence changes; new persistence or
  automatic saves; `recorded_at`; Move History contract or implementation changes; variations, multiple preferred
  moves, the mock Local Session strip, **Not now**, board/evaluation redesign, training changes, new dependencies,
  tokens, or browser profiles; Line Library; maintenance checks; historical rewrites; `Scratch/`; commits; pushes;
  and unrelated worktree changes.

## Stages

1. **complete** - Extend the repertoire workflow/model seam for truthful state-driven behavior and last-played focus.
    - **Ordered actions:** R1 Stage 3 focused Storybook and browser proof has passed and its active Plan is closed.
      Preserve the R1 linear session owner and current worktree changes. Extend the pure repertoire model and workflow
      state to distinguish no saved move, saved move,
     matching played move, and unsaved played move; retain the move and preferred response needed for last-played
     matching; preserve staged moves versus immediately played opponent moves; clear transient focus on navigation,
     Flip, load, reset, and other established position transitions; and expose the existing position context and
     preferred effective-date metadata to the panel without changing API contracts or adding a route owner. Hydrate
     the persisted date by its UTC calendar day and retain explicit mutation/date semantics. Add focused pure-model
     and Workspace regression assertions for the four states, date reload truth, navigation/reset behavior, and
     existing linear-session behavior.
   - **Focused proof:**
     `timeout 180s npm.cmd run test --prefix frontend -- --run --project=unit src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
     (bash tool timeout: `210000 ms`).
   - **Breakpoint:** None while the settled four-state model can be derived from the existing repertoire session and
     D1/F1 read seams.
   - **Escalate if:** Last-played matching requires a new identity, branch/variation rule, route owner, mutation,
     API field, recorded-date interpretation, or a change to staging, opponent immediacy, or linear truncation.
2. **complete** - Compose the current-position frequency component and the state-driven preferred-move panel.
   - **Ordered actions:** Pass the current session position context to `PositionReachFrequency` with the bottom
     repertoire colour, so it reloads on every accepted history transition and preserves available, zero, absent,
     and unavailable semantics. Replace the static preferred-move presentation with the four settled state branches,
     keeping SAN/UCI, existing Play/Edit/Remove behavior, explicit Add/Save behavior, staged navigation cancellation,
     and no automatic persistence. Display the selected preferred move's persisted effective date as UTC `Today` or
     the existing calendar date and retain date changes through the existing explicit mutation paths. Preserve the
     shared Move History composition, board/evaluation behavior, accessibility, and existing CMT tokens/primitives.
     Extend focused Workspace assertions for frequency FEN/color synchronization, effective-date display/change,
     state actions, matching and unsaved focus, and preservation of existing workflow behavior.
   - **Focused proof:** Re-run the Stage 1 unit command above because panel composition and Workspace behavior affect
     its exercised inputs and assertions (bash tool timeout: `210000 ms`).
   - **Breakpoint:** None for composition while existing CMT styling, hierarchy, focus, reduced-motion, and
     forced-colour behavior remain sufficient.
   - **Escalate if:** Frequency requires a denominator or colour rule change; date change requires a new date-only
     persistence action or automatic save; or composition requires a new visual hierarchy, token, dependency, or
     shared-component contract.
3. **complete** - Update the R2 review and browser proof surfaces, then complete the required human visual review.
   - **Ordered actions:** Extend the repertoire Workspace, Session Panel, and Preferred Move Panel stories with all
     four saved-move states, persisted date/Today cases, matching and unsaved last-played focus, current-position
     frequency states, stored-prefix/local-history transitions, keyboard focus/visibility, and constrained layouts.
     Update the bounded story helpers, assertions, render fixtures, and existing targeted browser spec to prove
     state actions, synchronized current FEN/Ply/description/workflow reads, selected-colour frequency, effective
     date, accessibility, and absence of horizontal overflow. Run the focused Storybook and browser proof, then stop
     for human review at 1280x900 and 412x915 of the exact R2 panel visuals, active focus, constrained layout, and
     existing CMT styling. User edits at this breakpoint are authoritative and must be incorporated before
     continuation.
   - **Focused proof:**
     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/repertoire-builder`
     (bash tool timeout: `360000 ms`); then
     `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`
     (bash tool timeout: `660000 ms`).
    - **Breakpoint:** Accepted. The user reviewed the exact R2 composition at 1280x900 and 412x915, including the
      exact R2 panel visuals, active focus, constrained layout, existing CMT styling, and absence of horizontal
      overflow.
   - **Escalate if:** Review requests a new product state, accepted control, visual direction, token, browser
     profile, or acceptance criterion outside this R2 outcome.

Stages are sequential; no stage runs in parallel. A passing proof item remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment; later stages rerun only missing
or invalidated proof.

## Progress and decisions

- **Dependency gate:** D1 and F1 are done, behaviorally proven, and user accepted. R1 is complete with Storybook proof
  passed (33 tests in 16.35s), targeted browser proof passed (6 tests in 44.5s), and user wide/constrained sign-off
  recorded.
- **Stage 1:** complete - focused unit proof passed (43 tests; Vitest duration 13.35s); breakpoint none.
- **Stage 2:** complete - focused unit proof passed (45 tests; Vitest duration 14.02s); breakpoint none while
  existing CMT composition remains sufficient.
- **Stage 3:** complete - focused Storybook and browser proof passed; the user accepted the exact R2 wide/constrained
  human visual breakpoint at 1280x900 and 412x915, including the exact R2 panel visuals, active focus, constrained
  layout, existing CMT styling, and absence of horizontal overflow.
- **Decision:** `effective_at` is the D1 selected preferred-move event's persisted effective timestamp, not
  `recorded_at`; unassigned states remain null. Display uses its UTC calendar day and the settled friendly `Today`
  presentation when applicable.
- **Decision:** Position Reach Frequency reads the current session FEN and selects the bottom/repertoire colour; its
  D1/F1 contracts, colour-correct denominator, and available/zero/absent/unavailable semantics remain unchanged.
- **Decision:** Existing explicit preferred-move mutation authority remains in force. No automatic persistence,
  separate date persistence contract, **Not now** action, variation model, or multiple preferred move is added.
- **Decision:** R2 visual acceptance is complete; no product or visual changes were requested after review at 1280x900
  and 412x915.

## Proof

- Unit regression:
  `timeout 180s npm.cmd run test --prefix frontend -- --run --project=unit src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
  (bash tool timeout: `210000 ms`) - passed (45 tests; Vitest duration 14.02s).
- Focused Storybook regression:
  `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/repertoire-builder`
  (bash tool timeout: `360000 ms`) - passed (44 tests; 14.81s).
- Existing targeted browser regression:
  `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`
  (bash tool timeout: `660000 ms`) - passed (7 tests; 41.5s).
- Human visual review: The user accepted the exact R2 panel presentation at 1280x900 and 412x915, including active
  focus, constrained layout, existing CMT styling, and absence of horizontal overflow.
- R1's same focused Storybook and browser commands are a prerequisite closeout proof, not R2 proof. No lint,
  formatting, build, source-size, aggregate, or maintenance command is required by this Plan. Passing behavioral
  proof remains valid until an affecting change invalidates it.

## Acceptance

- `/repertoire` truthfully presents no saved move, saved move, matching played move, and unsaved played move, with
  last-played focus and existing explicit actions; **Not now** and automatic persistence are absent.
- An assigned preferred move displays its persisted UTC effective date, using `Today` for the current UTC day, and
  date changes remain within the existing explicit mutation paths without exposing `recorded_at` or changing D1
  read semantics.
- Position Reach Frequency follows the current FEN and selected repertoire colour through click, keyboard, Previous,
  Next, Home, End, local play, opponent play, and history transitions, preserving all F1 states and denominator
  rules.
- Shared history, active focus/visibility, board FEN and last move, current Ply, position description, workflow reads,
  staging cancellation, opponent immediacy, and linear replacement/truncation remain synchronized and accessible at
  wide and constrained sizes without horizontal overflow.
- The focused unit, Storybook, and browser proof passes, and human review accepts the exact R2 presentation at
  1280x900 and 412x915.
- **User visual sign-off:** The user accepted the exact R2 panel visuals, active focus, constrained layout, existing
  CMT styling, and absence of horizontal overflow at both required sizes.

## Escalation boundaries

- Any new or changed API, data, storage, schema, migration, `as_of`, `recorded_at`, mutation, persistence,
  dependency, route owner, or shared Move History/Position Reach Frequency contract.
- Any automatic date or preferred-move persistence, date-only mutation, variation/branch semantics, multiple
  preferred moves, training behavior, board/evaluation redesign, or change to accepted staging, opponent, or linear
  truncation behavior.
- Any change to F1's authoritative current-position identity, stable repertoire colour, denominator, orientation
  independence, or available/zero/absent/unavailable semantics.
- Any new token, visual hierarchy, copy direction, accepted control, browser profile, accessibility direction, or
  acceptance decision beyond the settled four-state outcome and existing CMT system.
- Any R1 proof/record collision, unrelated failure, unrelated worktree or historical-record change, `Scratch/`
  change, maintenance request, commit, or push.

## Visible result

> On `/repertoire`, a person can see the truthful saved-move state and effective date for the current workflow, verify
> current-position reach frequency, and navigate the shared history while the panel, board, and focus agree.
