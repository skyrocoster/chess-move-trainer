# Repertoire board-derived preferred-move state - equivalent board positions retain the complete panel experience

> **Status:** done - all stages accepted with focused model, workflow, Storybook, and browser proof

- **Read trigger:** Read before changing `/repertoire` preferred-move state derivation, local-position navigation,
  the focused repertoire workflow tests, or the existing preferred-move workspace story used for browser proof.
- **Upstream:** [Completed preferred-move design-system alignment Plan](../../done/repertoire-preferred-move-design-system-alignment/repertoire-preferred-move-design-system-alignment.md)

## Outcome

On `/repertoire`, preferred-move panel state for a displayed local position is identical whether that position is
reached by direct board play, Previous/Next, history-row selection, or keyboard navigation. The active local
transition is derived from the session's currently displayed position and local cursor (or the existing staged-move
semantics), rather than one-shot `playedMoveFocus` event history. Preferred data is resolved from the move's
originating position without changing API or persistence contracts.

## Scope

- **Included:** Position-derived matching/unsaved-played state; played move, match text, effective date, and Edit/
  Remove/Add action availability; direct e4 followed by Previous and Next, history-row selection, or keyboard return
  to e4; the existing local session and preferred-move workflow seams.
- **Expected areas:**
  - `frontend/src/features/repertoire-builder/positionPickerSession.ts`
  - `frontend/src/features/repertoire-builder/repertoireWorkflowModel.ts`
  - `frontend/src/features/repertoire-builder/preferredMoveWorkflowState.ts`
  - `frontend/src/features/repertoire-builder/repertoireWorkflowModel.test.ts`
  - `frontend/src/features/repertoire-builder/positionPickerSession.test.ts`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx`
- **Excluded:** API/client, backend, data, storage, persistence, route ownership, and dependencies; changes to
  `RepertoireBuilderWorkspace.tsx` session-status ownership, board notice, navigation copy, or board wiring; the
  existing parent-position meaning of staged previews; loaded stored-prefix meaning; Reset, Flip, edit/cancel,
  mutation, promotion, and opponent-move behavior; `PreferredMovePanel`, `RepertoireSessionPanel`, shared feedback
  components, CSS, copy, roles, live-region semantics, accessibility contracts, and design-system work; new browser
  specs or profiles; broad lint, formatting, type, build, source-size, aggregate, or maintenance checks; unrelated
  worktree changes, `Scratch/`, historical records, commits, and pushes.

## Stages

1. **complete** - Establish the pure session/model seam for the currently displayed local transition.
   - **Ordered actions:** Re-read the current session and workflow contracts before editing. Identify the local move
     that produced the selected committed position from the session cursor, while retaining the current staged-move
     parent semantics. Derive the transition and its originating position from session data rather than event order.
     Preserve bottom-color/side-to-move saveability, current-position context, and the existing four panel states.
     Add only the smallest pure helper/model coverage needed for committed local and staged positions.
   - **Focused proof:** From `frontend`, run
     `timeout 180s npm exec vitest run src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/positionPickerSession.test.ts --testTimeout=10000 --hookTimeout=10000`.
     The command-level timeout is `180s`; use a finite Bash tool timeout of `210000 ms`.
   - **Breakpoint:** None while the existing session representation supplies the transition and staged-preview
     semantics remain unchanged.
   - **Escalate if:** A pure derivation requires changing the session/API contract, changing the meaning of a staged
     preview, or adding new position ownership.
2. **complete** - Integrate position-derived preferred data and remove navigation dependence on one-shot focus.
   - **Ordered actions:** Update `preferredMoveWorkflowState.ts` to derive the active transition on every session
     position change. Resolve the preferred response for the transition's originating position through the existing
     typed client/hook seam, without changing request or persistence contracts. Ensure leaving a local child removes
     its played presentation and returning to the same child reconstructs it, including the persisted effective date
     and action guards. Preserve explicit draft/mutation reset behavior, Edit/Remove targeting, current-position
     context/reach frequency, Reset, Flip, loaded prefixes, promotion, opponent moves, and the transient
     `sessionStatus` action announcement.
   - **Focused proof:** From `frontend`, run
     `timeout 180s npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx --testTimeout=10000 --hookTimeout=10000`.
     The command-level timeout is `180s`; use a finite Bash tool timeout of `210000 ms`. The regression scenario must
     use an assigned preferred move for the parent e4 position and verify direct play, Previous, Next, history-row
     selection, and keyboard navigation all restore the same full `matching-played` panel.
   - **Breakpoint:** None if the existing client types, parent-position mutation targeting, status ownership, and
     feedback/accessibility contracts remain unchanged.
   - **Escalate if:** The fix needs a public API/client change, persistence or cache contract, altered mutation
     targeting, changed status precedence/copy, or a change to any settled panel or accessibility behavior.
3. **complete** - Add the focused existing Storybook regression for direct play and local navigation parity.
   - **Ordered actions:** Extend `RepertoireBuilderWorkspacePreferredMove.stories.tsx`'s existing assigned board-play
     scenario to play e4, assert the complete matching-played panel, move Previous to the initial position, then return
     with Next or the controlled history path and assert the same played label, match text, effective date, Edit, and
     Remove. Keep the existing navigation announcement, stories, selectors, and all unrelated workflow scenarios
     unchanged; do not add a browser spec.
   - **Focused proof:** From `frontend`, run
     `timeout 300s npm run test-storybook -- --run src/features/repertoire-builder --testTimeout=10000 --hookTimeout=10000`.
     The command-level timeout is `300s`; use a finite Bash tool timeout of `360000 ms`.
   - **Breakpoint:** None; this is behavioral Storybook proof of an unchanged visual and accessibility surface.
   - **Escalate if:** The regression requires a new story surface, visual direction, copy, role/live-region change,
     dialog change, or a new browser profile/spec.
4. **complete** - Prove the existing wide and constrained repertoire browser surface.
   - **Ordered actions:** With the existing Storybook server available, run the registered repertoire browser proof.
     Confirm the assigned board-play story exercises the direct-to-Previous/Next parity path and that existing wide,
     constrained, keyboard, staged, stored-prefix, mutation, promotion, and accessibility scenarios remain intact.
   - **Focused proof:** From the repository root, run
     `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`.
     The command-level timeout is `600s`; use a finite Bash tool timeout of `660000 ms`.
   - **Breakpoint:** None; visual review is verification at the existing wide/constrained states, not a new design
     decision.
   - **Escalate if:** Browser proof exposes changed hierarchy, overflow, focus, accessibility, feedback semantics,
     unrelated failures, or a need for a new browser surface.

Stages are sequential; no parallel stages. A passing proof item remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof. These are behavioral proofs only; complete maintenance and independent validation remain separate workflows.

## Progress and decisions

- **Dependency gate:** complete - the assessment found the defect in workflow-owned event focus; the existing session,
  model, typed preferred client, panel, and controlled history are available.
- **Decision:** The canonical identity is the displayed local transition from session position/local cursor, with the
  existing staged move treated as a parent-position preview.
- **Decision:** Preferred data remains keyed to the move's originating position; no API, persistence, or storage
  contract changes are authorized.
- **Decision:** `sessionStatus` remains Workspace-owned transient action feedback, and the completed design-system
  alignment remains unchanged.
- **Stage 1:** complete - `positionPickerSelectedTransition` now derives a staged transition from its current parent
  or a committed local transition and source position from the selected cursor/session state. Focused tests prove
  reconstruction after Previous/Next and preserve staged semantics; 2 files and 25 tests passed.
- **Stage 2:** complete - workflow state now derives the active own-color transition from the selected session and
  reads preferred data from its source position rather than retaining one-shot focus. A focused workspace regression
  proves direct e4, parent Previous, Next, history-row selection, and ArrowRight return restore the full matching
  panel; 2 files and 36 tests passed.
- **Stage 3:** complete - the existing `AssignedBoardPlay` story now proves the complete direct matching panel,
  normal saved parent after Previous, and identical matching panel after Next. Focused Storybook proof passed 5 files
  and 44 tests.
- **Stage 4:** complete - the existing browser proof passed all 7 scenarios after correcting its stale final action-
  status expectation to the intentionally preserved Next-navigation announcement. Direct -> Previous -> Next panel
  parity, wide/constrained layout, keyboard/focus, staged and loaded-prefix behavior, mutation, promotion, feedback,
  accessibility, and overflow checks passed.

## Proof

- Pure model/session regression from `frontend`:
  `timeout 180s npm exec vitest run src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/positionPickerSession.test.ts --testTimeout=10000 --hookTimeout=10000`
  (command-level timeout `180s`; Bash tool timeout `210000 ms`); **passed after Stage 1: 2 files, 25 tests**.
- Focused workspace/workflow regression from `frontend`:
  `timeout 180s npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx --testTimeout=10000 --hookTimeout=10000`
  (command-level timeout `180s`; Bash tool timeout `210000 ms`). It must compare direct e4 play with Previous/Next,
  history-row, and keyboard return to the same e4 position. **Passed after Stage 2: 2 files, 36 tests**.
- Existing repertoire Storybook interactions from `frontend`:
  `timeout 300s npm run test-storybook -- --run src/features/repertoire-builder --testTimeout=10000 --hookTimeout=10000`
  (command-level timeout `300s`; Bash tool timeout `360000 ms`); **passed after Stage 3: 5 files, 44 tests**.
- Existing bounded browser proof from the repository root, with Storybook already available:
  `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`
  (command-level timeout `600s`; Bash tool timeout `660000 ms`); **passed after the bounded stale-assertion repair:
  7 tests in 37.9 seconds**.
- Passing behavioral proof remains valid until a later affecting change invalidates its command, inputs, exercised
  behavior, configuration, dependencies, or environment.

## Acceptance

- Starting with an assigned e4 preference, direct local e4 play, Previous then Next, controlled history-row selection,
  and keyboard navigation back to e4 all produce the same displayed board transition and `data-state="matching-played"`.
- Each route shows `Played move: e4 (e2e4)`, `This move matches your preferred move.`, the persisted effective date,
  Edit, and Remove, with no missing panel content and no stale content from another position.
- The parent initial position still shows its normal saved state; staged previews still use the existing parent-position
  workflow semantics; reach frequency remains tied to the existing current-position/context behavior.
- Loaded stored prefixes, Reset, Flip, edit/cancel, successful and failed mutations, promotion, opponent moves,
  session-status action announcements, feedback components, copy, roles, live regions, focus, and accessibility remain
  behaviorally unchanged.
- The focused Vitest, Storybook, and existing browser proofs pass without unrelated path changes or new maintenance
  work.

## Escalation boundaries

- Any API/client, backend, data, persistence, storage, dependency, route-owner, or public prop change.
- Any change to the established staged-preview parent-position semantics, loaded-prefix semantics, mutation targeting,
  session-status ownership/precedence/copy, or bottom-color ownership.
- Any preferred-panel copy, visual hierarchy, CSS, design-system feedback, dialog, role/live-region, focus, keyboard,
  accessibility, responsive, or overflow decision.
- Any new browser spec/profile, broad maintenance check, unrelated failure requiring repair, concurrent baseline
  collision, historical-record edit, `Scratch/` change, commit, or push.

## Visible result

> Returning to a local e4 position by navigation or history shows the same complete preferred-move panel as playing e4 directly.
