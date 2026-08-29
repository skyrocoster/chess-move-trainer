# Repertoire Session Panel - one cohesive right-side session region

> **Status:** Done - all stages accepted; focused, browser, Quality, and repository closeout proof passed

- **Read trigger:** Read before executing the approved `/repertoire` session-region extraction.

## Outcome

`/repertoire` has one `RepertoireSessionPanel` component boundary for all visible right-side session content:
Local SAN history, the staged/session status message, and the complete existing bordered `PreferredMovePanel`
composition. The exact staged sentence, `My move staged: e4.`, is visible once through the accessible live
session-status presentation. Existing preferred-move presentation and workflow behavior remain unchanged.

## Scope

- **Included:** Extract the session-region presentation into
  `frontend/src/features/repertoire-builder/RepertoireSessionPanel.tsx`, with its session-region styles in
  `RepertoireSessionPanel.module.css`. Compose the unchanged `PreferredMovePanel` internally; keep the
  Workspace as the owner of session state, workflow state, callbacks, and board notice behavior. Remove the
  duplicate exact staged sentence by making the existing `session-status` live message the single displayed
  sentence and removing the separate duplicate staged paragraph. Update focused tests, Storybook checks, and
  the bounded repertoire Storybook E2E assertions.
- **Expected areas:**
  `frontend/src/features/repertoire-builder/{RepertoireSessionPanel.tsx,RepertoireSessionPanel.module.css,RepertoireBuilderWorkspace.tsx,RepertoireBuilderWorkspace.module.css,RepertoireBuilderWorkspace.test.tsx,RepertoireBuilderWorkspace.stories.tsx,PreferredMoveWorkflow.stories.tsx}`;
  `tests/e2e/repertoire-builder-storybook.spec.ts`; README ownership maintenance is routed separately to
  `readme-updater` after the structural change.
- **Excluded:** `PreferredMovePanel.tsx` and `PreferredMovePanel.module.css` unless an explicit breakpoint is
  approved; the separate position-description work; board, controls, eval, analysis, loading, navigation,
  promotion, or visual redesign; API, backend, data, dependency, or public-workflow contract changes; unrelated
  repertoire text extraction; unrelated worktree changes; commits and pushes.

## Stages

1. **complete** - Extract and wire the cohesive session component from the closed position-description baseline.
   - Confirm that `docs/plans/active/repertoire-position-description/repertoire-position-description.md` is
     completed and closed before reading the final `RepertoireBuilderWorkspace` and CSS baseline. Do not execute
     this stage in parallel with that Plan, and preserve its shared `PositionDescription`, grid, test, and story
     changes.
   - Add `RepertoireSessionPanel.tsx` with an internal prop composition for `sanHistory`, `sessionStatus`,
     `sideToMove`, and the existing preferred-workflow view/actions needed by `PreferredMovePanel`. Render one
     root session boundary (using the stable `repertoire-session` test marker) containing the Local SAN history
     label/content, the single `session-status` paragraph, and `PreferredMovePanel`.
   - Keep `sessionStatus` as the visible `role="status" aria-live="polite"` message. Remove only the separate
     Workspace staged paragraph and its `.staged` styling so staged feedback remains visible once; retain the
     `PreferredMovePanel`'s distinct detailed `Staged move: ...` instruction used by Add/Edit.
   - Add `RepertoireSessionPanel.module.css` for the moved `.session`, history, and status presentation. Keep
     the preferred panel border, controls, spacing, and all private preferred-panel behavior in
     `PreferredMovePanel.tsx` and `PreferredMovePanel.module.css`.
   - Replace the inline region at `RepertoireBuilderWorkspace.tsx:402-438` with the new component. Do not move
     `sessionStatus` state or its setters, because the same status is passed to the board as `notice` and is
     updated by move, navigation, promotion, and mutation workflows.
   - Preserve the existing `session-san-history`, `session-status`, `saved-move`, date-control, action, dialog,
     and accessibility semantics. The staged-specific assertions will be redirected to `session-status` in the
     next stage because `staged-move` is no longer a separate displayed node.
   - Update the minimum staged/Flip assertions in `RepertoireBuilderWorkspace.test.tsx` needed for the removed
     `staged-move` node before running Stage 1 proof; broader boundary and Storybook/E2E assertions remain in
     Stage 2.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `120000 ms`.
   - **Breakpoint:** stop and escalate if the closed position-description baseline cannot be preserved, if
     removing the duplicate requires changing workflow status semantics beyond the single live presentation, or
     if `PreferredMovePanel` must change to preserve its existing behavior.

2. **complete** - Regression-guard the full session/preferred boundary and observable behavior.
   - Complete `RepertoireBuilderWorkspace.test.tsx` staging, Flip, mutation-failure, and accessibility assertions
     to prove the exact staged sentence occurs once through `session-status` and that the
     `repertoire-session` boundary contains the history, status, and preferred panel; retain history,
     preferred-move, date, error, confirmation, navigation, local-play, and no-Undo/Reset coverage.
   - Update `RepertoireBuilderWorkspace.stories.tsx` helpers and stories at the existing staging/status checks,
     including `verifyStandardWorkspace`, `StagedMy`, `OpponentImmediate`, `FlipCancellation`,
     `KeyboardAndAccessibility`, and preferred-move stories, to assert the one outer boundary and the single
     staged sentence without changing story scenarios.
   - Update `PreferredMoveWorkflow.stories.tsx` only where its Workspace-based staged/status selectors require
     the new single-node presentation; preserve read-error and opponent-local-only behavior.
   - Update `tests/e2e/repertoire-builder-storybook.spec.ts` selectors that depended on `staged-move`, while
     retaining bounded wide/constrained, preferred workflow, overflow, and accessibility coverage.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `120000 ms`.
   - **Story proof:** from `frontend`, run
     `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `180000 ms`; repeat for `PreferredMoveWorkflow.stories.tsx` with the same finite
     `--testTimeout=10000 --hookTimeout=10000` flags and Bash tool timeout `180000 ms`.
   - **Bounded browser proof:** with the existing Storybook server available, from the repository root run
     `npm exec playwright test tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`;
     Bash tool timeout: `180000 ms`.
   - **Breakpoint:** stop if any preferred-move state, date, action, confirmation, status, accessibility, or
     overflow behavior changes; do not absorb unrelated baseline failures or broaden the extraction.

3. **complete** - Route ownership documentation after the structural product change.
   - After Stages 1-2 complete, route `frontend/src/features/repertoire-builder/README.md` to `readme-updater`.
     The updater should reflect that `RepertoireSessionPanel` owns the right-side session composition,
     `RepertoireBuilderWorkspace` owns the page/state orchestration, and `PreferredMovePanel` owns the nested
     preferred-move UI.
   - The case-worker must not edit or silently absorb this README maintenance. README edits do not require
     Quality validation; preserve all unrelated documentation and historical records.
   - **Breakpoint:** return to the coordinator if the ownership update requires documenting a broader component
     redesign or conflicts with the closed position-description baseline.

4. **complete** - Fresh independent Quality validation of the observable UI.
   - A fresh Quality session validates only the approved source and test paths read-only; it must not edit,
     format, repair, commit, or absorb unrelated failures.
   - At wide and constrained widths, verify that one `RepertoireSessionPanel` boundary contains the history,
     the single visible exact staged sentence, the live status behavior, and the complete preferred-move box.
   - Exercise or inspect staged move, Flip cancellation, opponent/local play, saved move, effective date,
     Edit/Save, Play saved move, Remove confirmation, errors, loading, mutation feedback, and navigation.
     Confirm the preferred border and controls are visually unchanged, no horizontal overflow exists, and the
     focused accessibility scan remains clean.
   - **Breakpoint:** return to the coordinator for any browser result that calls the approved boundary,
     duplicate-removal behavior, preferred presentation, or closed position-description baseline into question.

5. **complete** - Run repository closeout and prepare the Plan for coordinator closeout.
   - From the repository root, run `.venv/Scripts/python.exe scripts/check.py` without `--fix`;
     Bash tool timeout: `180000 ms`. The closeout runner has no additional supported CLI timeout flag; the
     Bash timeout remains finite.
   - Record only truthful stage progress and proof in the coordinator's execution record; do not add transient
     logs to this Plan. Move this Plan to `docs/plans/done/` only through the coordinator's closeout process.
   - **Breakpoint:** report the exact failing command and stop for any unrelated baseline failure, any failed
     repair loop, or any request to commit or push.

## Progress and decisions

- **Stage 1:** complete - Luna added and wired `RepertoireSessionPanel`, removed the duplicate staged
  presentation, preserved the closed position-description baseline and unchanged `PreferredMovePanel`, and the
  focused Workspace regression passed 14/14 tests.
- **Stage 2:** complete - Luna updated the focused Workspace, Storybook, and bounded browser guards; Workspace
  regression passed 14/14, Workspace stories passed 21/21, Preferred workflow stories passed 2/2, and the
  repertoire Storybook browser suite passed 6/6 after a temporary server was started and cleanly stopped.
- **Stage 3:** complete - `readme-updater` updated the repertoire-builder README with the Workspace,
  `RepertoireSessionPanel`, and nested `PreferredMovePanel` ownership boundaries; no Quality validation is
  required for that documentation-only edit.
- **Stage 4:** complete - after one authorized deterministic E2E race repair, a fresh read-only Quality session
  passed the approved boundary, single-status, wide/constrained, workflow, overflow, and accessibility validation;
  its independent bounded browser run passed 6/6.
- **Stage 5:** complete - Luna reduced the enlarged Workspace story through a behavior-neutral assertion-helper
  extraction, the focused Workspace Storybook suite passed 21/21, README formatting was repaired by
  `readme-updater`, and `.venv/Scripts/python.exe scripts/check.py` passed without `--fix`.
- **Decision:** this is a separate Plan, not an amendment to the position-description Plan; execution is
  strictly serialized after that Plan is completed and closed.
- **Decision:** `session-status` remains the one visible live staged sentence; the separate duplicate staged
  paragraph is removed, while PreferredMovePanel's distinct detailed staged instruction remains.
- **Decision:** no public prop, API, workflow, visual-style, or preferred-panel contract changes are approved.
- **Decision:** aggregate Flip-cancellation proof keeps the transient status assertion in the Storybook play
  function while bounded E2E verifies the deterministic post-play state, removing the observed timing race.
- **Decision:** the Workspace story assertion-helper extraction is a behavior-neutral size-limit repair and does
  not change story exports, scenarios, or acceptance.

## Proof

- Repertoire component regression: `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`
  (`frontend`; Bash tool timeout `120000 ms`).
- Repertoire Workspace Storybook interactions: `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`
  (`frontend`; Bash tool timeout `180000 ms`).
- Preferred workflow Storybook interactions: the same `npm run test-storybook -- --run` command targeting
  `src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`, with `--testTimeout=10000
  --hookTimeout=10000` and Bash tool timeout `180000 ms`.
- Bounded browser evidence: `npm exec playwright test tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`
  (repository root; Bash tool timeout `180000 ms`), including wide and constrained widths, overflow, and
  accessibility checks.
- Full repository closeout: `.venv/Scripts/python.exe scripts/check.py` (repository root; no `--fix`; Bash
  tool timeout `180000 ms`).
- README maintenance is delegated to `readme-updater` and is not a Quality-validation target.

## Escalation boundaries

- Do not execute until the position-description Plan is completed, closed, and its final Workspace/CSS/test/story
  baseline is available. Never execute these Plans in parallel.
- Do not alter or absorb the shared position-description component, placement, disclosure behavior, or its tests.
- Do not change `PreferredMovePanel.tsx` or `PreferredMovePanel.module.css` unless a minimal necessary change is
  identified and the coordinator explicitly approves the scope correction.
- Do not replace the single live status with a new wording, hidden-only behavior, or a new public contract to
  solve duplicate presentation without coordinator approval.
- Stop for any new product, visual, ownership, API, data, dependency, destructive, accessibility, or acceptance
  decision; preserve the approved border, controls, workflow semantics, and closed baseline.
- Route README ownership maintenance to `readme-updater`; the case-worker must not edit it or make documentation
  cleanup part of product execution.
- Preserve unrelated worktree changes and historical records; never commit or push.

## Visible result

> `/repertoire` shows one cohesive right-side session panel containing history, one accessible staged/status message, and the unchanged bordered Preferred move workflow.
