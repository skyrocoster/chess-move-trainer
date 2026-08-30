# Viewer History and Context Replacement - `/viewer` shows synchronized linear move history

> **Status:** done; V1 accepted

- **Read trigger:** Read before implementing V1, changing the Viewer history/context composition, or changing its
  focused proof.
- **Upstream:** [Saved Move Panel master plan](../../../../master-plans/saved-move-panel/saved-move-panel.md); [settled
  redesign](../../../../grilling-docs/saved-move-panel-redesign.md); completed [Shared Linear Move History
  Foundation](../../../done/saved-move-panel/shared-linear-move-history/shared-linear-move-history.md); completed
  [Position Reach Frequency](../../../done/saved-move-panel/position-reach-frequency/position-reach-frequency.md)

## Outcome

`/viewer` replaces Game Context in place with the shared controlled linear Move History. A person can select the
initial position or any SAN move, use the existing and history keyboard navigation, and see the board, active history
entry, announcement, and truthful Ply update together. The replacement retains safe source attribution and Ply
information, and shows Position Reach Frequency for the loaded subject/repertoire colour without changing when board
orientation is flipped. Existing board, evaluation, loading, reset, source-safety, and linear temporary-branch
behavior remain unchanged.

## Scope

- **Included:** Viewer-owned controlled wiring from `game.positions` into `MoveHistory`; shared state synchronization
  with `currentIndex`, Previous/Next, click selection, Arrow-key navigation, Home, End, board FEN, announcement, and
  active-row focus/visibility; in-place replacement of the route's Game Context presentation with retained safe source
  and Ply information; one `PositionReachFrequency` using the loaded game's existing `subject_color`; preservation of
  `analysisFen`-keyed context refreshes, flip independence, loading/unavailable/absent states, constrained CMT layout,
  and existing linear branch discard/gating behavior; focused Viewer stories and browser proof.
- **Expected areas:** `frontend/src/features/viewer/{ViewerWorkspace.tsx,ViewerWorkspace.module.css,ViewerWorkspace.test.tsx,ViewerWorkspaceBranch.test.tsx,ViewerWorkspace.stories.tsx}`; a narrowly scoped viewer-owned replacement component/test under `frontend/src/features/viewer/` only if extraction is needed; `frontend/src/features/viewer/README.md` only if the structural composition makes its current ownership description stale; and `tests/e2e/{viewer-storybook.spec.ts,viewer-live-position.spec.ts}`. Existing `GameContext` source-safety code/tests may be moved only when required by the replacement composition, with its URL safety preserved.
- **Excluded:** `/repertoire` and R1/R2 work; preferred-move mutations or effective-date presentation; backend/API,
  database, schema, storage, or position-context contract changes; H1/F1 contract changes; variations or branch
  authoring; training/session changes; board, evaluation, or BoardControl redesign; new dependencies, design-system
  tokens, primitives, or route state; simultaneous both-colour frequency presentation; Line Library work; new browser
  profiles or unrelated specs; historical records, `Scratch/`, commits, pushes, and unrelated worktree changes.

## Stages

1. **complete** - Integrate controlled Move History with Viewer state and preserve branch semantics.
   - **Ordered actions:** Re-read the named Viewer, H1, and F1 surfaces. Build the controlled history input from the
     accepted ordered game positions, keeping the initial position and SAN/Ply values truthful. Keep
     `ViewerWorkspace` as the page-state owner and make history selection resolve through the existing current-index
     navigation seam so click, Previous/Next, Arrow keys, Home, and End cannot diverge. Preserve explicit loaded Ply
     form state, board and announcement updates, loading/reset behavior, and the existing rule that navigation while a
     temporary branch is active follows the current branch discard/gating behavior rather than creating a variation.
     Extend focused workspace and branch tests for active-row synchronization, board/Ply/announcement changes, bounds,
     and branch preservation.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx` (recommended finite bash tool timeout: `150000 ms`).
   - **Breakpoint:** None while the existing controlled H1 contract and Viewer linear navigation semantics remain
     sufficient.
   - **Escalate if:** History selection requires a new branch/variation rule, a different state owner, a non-linear
     history model, a changed loaded-Ply contract, or a change to board/evaluation behavior.

2. **complete** - Replace the in-place context composition and wire current-position frequency.
   - **Ordered actions:** Replace the Viewer route's current Game Context/Position Context composition in the existing
     context location; do not add a competing sidebar card or leave a second plain-text history. Retain a truthful
     `Ply X of Y` and safe source attribution using the existing source-safety boundary. Render the reusable
     `PositionReachFrequency` for `game.subject_color`, using the existing `positionContextState.context` keyed by
     `analysisFen`; do not derive its colour from board flip or side to move. Preserve empty, loading/unavailable,
     zero/absent, branch, and source-link behavior, and keep the board/evaluation/analysis composition unchanged.
     Update focused Viewer tests and stories to assert one selected-colour frequency result, source/Ply retention,
     replacement loading/failure behavior, and no duplicate context presentation.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx` (recommended finite bash tool timeout: `150000 ms`). This reruns Stage 1 proof because the route composition and its exercised behavior change.
   - **Breakpoint:** None while the approved in-place replacement, CMT styling, fixed subject/repertoire colour, and F1
     state semantics remain directly usable.
   - **Escalate if:** Source/Ply retention needs a new API or ownership contract; `subject_color` cannot represent the
     accepted subject/repertoire colour; the composition needs a new visual hierarchy or token; or frequency requires
     changing its denominator, position identity, loading semantics, or both-colour presentation.

3. **complete** - Prove the Viewer result in Storybook and focused browser scenarios, then complete visible review.
   - **Ordered actions:** Reconcile existing Viewer stories with the replacement surface and synthetic fixtures, covering
     initial, intermediate, final, subject-colour, constrained, unavailable, and branch-relevant states. Add play
     assertions for history selection/navigation, active focus, source/Ply retention, selected-colour frequency, and
     flip preservation. Extend only the existing Viewer Storybook and live-app browser specs to prove no horizontal
     overflow, accessibility, forced-colour/reduced-motion compatibility where already covered, and the same behavior
     in the route. Review the result at wide and constrained sizes; user edits at this visual breakpoint are
     authoritative and must be incorporated before closeout. Route only genuinely stale Viewer README ownership text
     to the documentation owner; do not broaden documentation work.
   - **Focused proof:**
     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/viewer` (recommended finite bash tool timeout: `360000 ms`).

     `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts` (recommended finite bash tool timeout: `660000 ms`).

     `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-live-position.spec.ts` (recommended finite bash tool timeout: `660000 ms`).
   - **Breakpoint:** Explicit human visual review of the Viewer replacement at wide and constrained presentations. The
     review is limited to legibility, active-row/focus treatment, source/Ply placement, frequency clarity, responsive
     overflow, and existing accessibility conventions; a request that changes product direction requires escalation.
   - **Escalate if:** Browser proof requires a new server profile, new route/API/data behavior, new dependency, visual
     system, variation behavior, unrelated repair, or acceptance decision.

Stages are sequential; no stages run in parallel. A passing proof item remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only proof that
is missing or invalidated by their changes. Maintenance checks are separate and are not part of this Plan.

## Progress and decisions

- **Stage 1:** complete - shared controlled Move History is integrated through the existing Viewer navigation seam;
  focused route/branch proof passed 31 tests in 24.45s; breakpoint: none.
- **Stage 2:** complete - the in-place context now retains source/Ply and uses one subject-colour Position Reach
  Frequency keyed by the current analysis FEN; focused route/branch proof passed 31 tests in 21.82s; breakpoint: none.
- **Stage 3:** complete - selector-scoped live proof and invalidated focused route/branch proof pass; Storybook behavior
  and browser proof pass; wide and constrained artifacts were reviewed and explicitly accepted by the user; breakpoint:
  none.
- **Decision:** `ViewerWorkspace` remains the route state owner; H1 `MoveHistory` and F1 `PositionReachFrequency`
  remain shared feature dependencies rather than being changed or duplicated.
- **Decision:** The loaded game's existing `subject_color` supplies the selected subject/repertoire colour. Board Flip
  changes orientation only and cannot change frequency denominator or selected colour.
- **Decision:** V1 is frontend route integration only. D1 effective-date behavior, repertoire presentation, and all
  backend/storage contracts remain for later slices.
- **Visual acceptance:** The user explicitly accepted the wide and constrained visual result represented by
  `test-results/viewer-stage3-wide.png` and `test-results/viewer-stage3-constrained.png`.
- **Acceptance:** complete; V1 is accepted and the Plan is done.

## Proof

- Final focused Viewer units: `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx` with bash tool timeout `150000 ms` - passed 2 files / 31 tests in 22.20s.
- Storybook behavior: `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/viewer` with bash tool timeout `360000 ms` - passed 76/76 in 21.68s.
- Storybook browser: `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts` with bash tool timeout `660000 ms` - passed 6/6 in 34.1s.
- Live route: `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-live-position.spec.ts` with bash tool timeout `660000 ms` - passed 3/3 in 12.0s after scoping exact `Initial position` visibility assertions to the Move History button; no product behavior changed.
- Accepted visual artifacts: `test-results/viewer-stage3-wide.png` (1280x1242) and `test-results/viewer-stage3-constrained.png` (480x2135) were reviewed and explicitly accepted by the user.
- Viewer ownership README: separately refreshed at `frontend/src/features/viewer/README.md` to describe shared MoveHistory and PositionReachFrequency composition.
- Completed H1 and F1 behavioral receipts remain valid unless their files or exercised contracts change; no broad,
  lint, formatting, type/build, source-size, aggregate, or maintenance suite is required here.

## Escalation boundaries

- Any new product, visual, accessibility-acceptance, API, data, dependency, destructive, ownership, route-state, or
  acceptance decision not settled by the master plan, H1, F1, or accepted Viewer behavior.
- Any need to change Move History's controlled contract, Position Reach Frequency's selected-colour/denominator
  semantics, position identity, `analysisFen` ownership, or `subject_color` meaning.
- Any variation tree, branch authoring, multiple preferred moves, training/session redesign, board/evaluation change,
  new endpoint, persistence, schema, migration, or database write.
- Any duplicate Game Context/history surface, unsafe source-link handling, stale source/Ply information, or frequency
  value that follows board orientation or side to move.
- Any conflict with the active Line Library Plan, completed historical records, unrelated worktree changes, Scratch,
  or a request for commits, pushes, `--fix`, or broad maintenance work.

## Visible result

> In `/viewer`, a person can select or keyboard-navigate a move, see the board, active history, source/Ply, and
> subject-colour reach frequency stay truthful together, and flip the board without changing that position evidence.
