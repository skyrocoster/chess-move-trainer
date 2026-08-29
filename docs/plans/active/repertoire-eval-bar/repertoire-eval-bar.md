# Repertoire Evaluation Bar - The displayed repertoire board has the viewer's evaluation rail

> **Status:** pending - approved dual-analysis identity captured; execute only after all three upstream repertoire Plans are completed and closed

- **Read trigger:** Read before executing the approved `/repertoire` evaluation-rail integration.
- **Upstream:** [`repertoire-position-description`](../repertoire-position-description/repertoire-position-description.md), [`repertoire-session-panel`](../repertoire-session-panel/repertoire-session-panel.md), and [`repertoire-staged-move-preview`](../repertoire-staged-move-preview/repertoire-staged-move-preview.md)

## Outcome

`/repertoire` shows the same accessible, fixed-width evaluation rail used by `/viewer` directly beside
the board. The rail follows the displayed board FEN, including an upstream staged child preview, while
the existing repertoire `AnalysisPanel`, candidate activation, preferred-move workflow, and Add/Save
metadata remain explicitly anchored to the canonical parent position during staging.

## Scope

- **Included:** Compose the existing `BoardEvalStage`, `EvalBar`, and `evaluationDisplay` directly;
  independently observe the final displayed board FEN for the rail; preserve the parent analysis state
  for the existing AnalysisPanel and candidate/workflow paths; mirror the viewer's 30px rail geometry,
  orientation, score/mate, neutral/pending/stale/failed/unavailable, accessibility, sizing, and responsive
  behavior; add focused repertoire tests, Storybook interaction coverage, and bounded browser proof.
- **Expected areas:**
  `frontend/src/features/repertoire-builder/{RepertoireBuilderWorkspace.tsx,RepertoireBuilderWorkspace.module.css,RepertoireBuilderWorkspace.test.tsx,RepertoireBuilderWorkspace.stories.tsx,PreferredMoveWorkflow.stories.tsx}`;
  `tests/e2e/repertoire-builder-storybook.spec.ts`; regression targets
  `frontend/src/features/{viewer/{BoardEvalStage.tsx,BoardEvalStage.module.css,evalBarDisplay.ts,ViewerWorkspace.test.tsx,evalBarDisplay.test.ts},analysis/{EvalBar.tsx,EvalBar.test.tsx}}`;
  `frontend/src/features/repertoire-builder/README.md` only for post-implementation ownership review and
  routing to `readme-updater` if it is actually stale.
- **Excluded:** Changes to `BoardEvalStage`, `EvalBar`, viewer score mapping, or viewer visual semantics
  unless a focused regression identifies a narrow shared-contract correction; changes to the existing
  `AnalysisPanel`/candidate behavior; automatic enqueueing; backend/API/schema/dependency/persistence
  changes; staged-preview, position-description, session-panel, preferred-move, opponent-move, promotion,
  navigation, or history behavior; unrelated layout redesign or text extraction; speculative README edits;
  unrelated worktree changes; commits and pushes.

## Stages

1. **pending** - Confirm the closed upstream baseline and wire the explicit dual analysis identities.
   - Do not begin until `repertoire-position-description`, then `repertoire-session-panel`, then
     `repertoire-staged-move-preview` have each completed, closed, and left their final Workspace,
     `PositionDescription`, `RepertoireSessionPanel`, CSS, test, and Storybook baselines available. Never
     execute this Plan in parallel with an upstream Plan.
   - Read the final `RepertoireBuilderWorkspace` baseline only after those closures. Confirm that the
     upstream `displayedPosition` (or its final equivalent) is the board/description source and that
     `session.currentPosition` remains the canonical parent source for the existing analysis/workflow.
   - Keep the parent state explicit in `RepertoireBuilderWorkspace`: retain the existing
     `useAnalysisState(session.currentPosition.fen, ...)` for `analysisPanelDisplay`, candidate activation,
     and preferred-move behavior. Add a separate, clearly named read-only analysis state for the displayed
     FEN and pass it to `evaluationDisplay` only. The eval observation must not call `handleAction`, enqueue
     analysis, re-key the AnalysisPanel, or alter workflow callbacks.
   - Pass the existing `analysisClient` and `analysisPollIntervalMs` to both observations using the current
     read-only `AnalysisClient` contract. Do not add a client, endpoint, cache, schema, persistence, or
     automatic enqueue path. Preserve hook cancellation and stale-result protection from `useAnalysisState`.
   - Import `evaluationDisplay` directly from its existing viewer helper and use the existing
     `BoardOrientation`/`session.orientation`; do not duplicate score, mate, meter, or state mapping logic.
   - Add the narrowest focused Workspace assertions needed to prove distinct parent/displayed FEN requests,
     child evaluation after staging, unchanged parent analysis identity, and no preferred-move PUT or enqueue
     caused by the eval observation. Keep the final upstream component boundaries intact.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `120000 ms`.
   - **Breakpoint:** stop and escalate if the closed staged-preview baseline lacks a stable displayed-position
     source, if two observations require a new public/API contract, if the eval observation can trigger an
     action, or if preserving parent analysis/workflow identity requires changing the approved upstream behavior.

2. **pending** - Compose the viewer-faithful board/rail stage and responsive repertoire layout.
   - Render `BoardEvalStage` as the repertoire workspace's direct `board` grid item around the existing
     interactive board, rather than nesting it inside a competing board wrapper. Pass the final displayed-FEN
     `evaluationDisplay` result and `session.orientation` to the stage.
   - Preserve the extracted `PositionDescription` and `RepertoireSessionPanel` boundaries and all current
     controls, session, analysis, loading, navigation, promotion, preferred-move, and status ownership.
   - In `RepertoireBuilderWorkspace.module.css`, use the viewer-faithful wide arrangement: board stage spans
     the first two named grid cells, the session region occupies the third, and the columns are
     `minmax(0, 1fr) 30px minmax(0, 1fr)`. Keep controls below the board with the rail column empty and keep
     the full-width position-description and analysis rows from the closed upstream baseline.
   - In the constrained container, keep the stage across the board and 30px rail columns, move session
     content below the board, retain controls below the board with the rail column empty, and preserve the
     upstream full-width rows. Keep `min-inline-size: 0`, the stage's fixed 30px rail, and no-overflow behavior.
     Do not edit `BoardEvalStage.module.css` unless focused proof identifies a narrow shared correction.
   - Add or adjust only focused tests/stories that assert the rail is beside the actual `[data-board-visual]`,
     its shell is 30px and board-height matched, its orientation follows Flip without score inversion, and
     the board/session/controls/description placement is correct at wide and constrained widths.
   - **Focused proof:** from `frontend`, rerun
     `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/viewer/BoardEvalStage.test.tsx src/features/analysis/EvalBar.test.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `120000 ms`.
   - **Breakpoint:** stop if the viewer-faithful 30px geometry requires redesigning the board, controls,
     session panel, position description, analysis panel, or any upstream layout contract; do not silently
     restyle or extract another stage component.

3. **pending** - Regression-guard display semantics, dual identity, Storybook behavior, and browser geometry.
   - Complete `RepertoireBuilderWorkspace.test.tsx` coverage for neutral/no-result, completed CP, mate,
     pending, stale/failed-retained, failed-without-candidate, and unavailable display semantics through the
     existing `evaluationDisplay` contract. Keep direct helper semantics covered by the existing viewer tests;
     change those tests only for a proven shared-contract correction.
   - Prove a staged bottom-side move requests the staged child FEN for the eval rail while the parent FEN
     remains the AnalysisPanel/workflow identity. Prove Flip changes `data-orientation` and fill direction
     without changing the evaluated FEN or score meaning. Prove no `enqueue`, preferred-move PUT, history,
     candidate-path, Add/Save, or session-parent mutation is caused by the eval observation.
   - Update `RepertoireBuilderWorkspace.stories.tsx` using its existing wide, constrained, stored-black,
     staged, Flip, promotion, and workflow fixtures. Add only the minimum controlled analysis fixture or
     visible assertion needed to make the two FEN identities explicit. Update `PreferredMoveWorkflow.stories.tsx`
     only if its Workspace selectors or shared upstream baseline require it; preserve all workflow scenarios.
   - Extend `tests/e2e/repertoire-builder-storybook.spec.ts` with bounded assertions for wide and constrained
     rail placement, exact 30px width, board/rail height alignment, orientation/fill direction, meter ARIA
     semantics, representative display states, staged-child evaluation, parent-anchored AnalysisPanel/workflow,
     no overflow, and accessibility. Keep the existing repertoire workflow coverage.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/viewer/evalBarDisplay.test.ts src/features/viewer/ViewerWorkspace.test.tsx src/features/analysis/EvalBar.test.tsx src/features/viewer/BoardEvalStage.test.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `120000 ms`.
   - **Story proof:** from `frontend`, run
     `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`;
     Bash tool timeout: `180000 ms`. If `PreferredMoveWorkflow.stories.tsx` is changed, run the same bounded
     command targeting that story file with the same test and hook timeouts and Bash timeout.
   - **Bounded browser proof:** with the existing Storybook server available, from the repository root run
     `npm exec playwright test tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`;
     runner timeout: `30000 ms`; Bash tool timeout: `180000 ms`.
   - **Viewer regression proof:** from the repository root run
     `npm exec playwright test tests/e2e/viewer-storybook.spec.ts --timeout=30000 --workers=1`;
     runner timeout: `30000 ms`; Bash tool timeout: `180000 ms`.
   - **Breakpoint:** stop if the rail observes the parent instead of the displayed child, if a staged eval
     request changes parent analysis/workflow behavior, if any state/score/mate/orientation/ARIA semantics
     differ from viewer, if geometry overflows, or if any upstream boundary changes.

4. **pending** - Fresh independent Quality validation of the observable dual-identity UI.
   - A fresh Quality session validates only the approved repertoire source, focused tests/stories, bounded E2E
     surface, and reused viewer contracts read-only. It must not edit, format, repair, commit, or absorb
     unrelated failures.
   - At wide and constrained widths, verify that the rail is directly beside the displayed board, remains 30px
     wide, tracks the board height, follows White/Black orientation, and has no horizontal overflow.
   - Exercise or inspect neutral, pending, completed CP, mate, stale, failed, and unavailable states; verify
     accessible meter naming/value text, reduced-motion behavior, forced-colors behavior, and focused axe scans.
   - Exercise staging, Flip, promotion, navigation, preferred-move Add/Save failure/success, candidate
     activation, and workflow reads. Confirm the rail follows displayed FEN while AnalysisPanel, candidate,
     preferred context, mutation identity, history, and parent session remain canonical; confirm no staging PUT
     or automatic enqueue occurs.
   - **Breakpoint:** return to the coordinator for any browser result that calls the approved dual identity,
     visible placement, reused viewer semantics, accessibility, responsive behavior, or upstream boundary into
     question. Report unrelated failures without repairing them here.

5. **pending** - Route only necessary ownership documentation and run repository closeout.
   - After implementation and Quality validation, determine whether the structural/layout integration makes
     `frontend/src/features/repertoire-builder/README.md` stale. If so, route only that documentation change
     to `readme-updater`; the case-worker must not edit it speculatively. No README change is expected merely
     from consuming the existing viewer-owned stage.
   - From the repository root, run `.venv/Scripts/python.exe scripts/check.py` without `--fix`; the closeout
     runner has no additional supported CLI timeout flag, so use Bash tool timeout `180000 ms` and record the
     exact result. Do not use `--fix` for semantic repair.
   - Preserve truthful stage progress and proof; move this Plan to `docs/plans/done/` only through coordinator
     closeout.
   - **Breakpoint:** report the exact failing command and stop for any unrelated baseline failure, failed repair
     loop, documentation-ownership ambiguity, or request to commit or push.

## Progress and decisions

- **Stage 1:** pending - upstream closure and explicit parent/displayed analysis wiring not implemented; breakpoint: preserve the approved staged-preview parent identity and use a read-only displayed-FEN observation.
- **Stage 2:** pending - viewer-faithful rail composition and wide/constrained grid integration not implemented; breakpoint: preserve all three closed upstream component boundaries and layout contracts.
- **Stage 3:** pending - focused Vitest, Storybook, and bounded browser proof not run; breakpoint: preserve viewer state/score/accessibility semantics and no eval-triggered workflow actions.
- **Stage 4:** pending - requires fresh independent Quality validation of the observable dual-identity UI; breakpoint: no repair or unrelated-failure absorption.
- **Stage 5:** pending - requires conditional README routing and repository closeout without `--fix`.
- **Decision:** execute strictly after `repertoire-position-description`, then `repertoire-session-panel`, then `repertoire-staged-move-preview` are completed and closed; never execute these Plans in parallel.
- **Decision:** the eval rail independently observes the displayed board FEN, including `session.stagedMove.position` or the final upstream displayed-position equivalent.
- **Decision:** the existing AnalysisPanel, candidate activation, preferred context/workflow, mutation request identity, and Add/Save metadata remain anchored to `session.currentPosition.fen` during staging.
- **Decision:** reuse `BoardEvalStage`, `EvalBar`, `evaluationDisplay`, `useAnalysisState`, and the existing read-only `AnalysisClient` contract directly; no automatic enqueueing, backend/API/schema/dependency/persistence change is approved.
- **Decision:** keep parent and displayed analysis identities explicit in implementation names and tests; the eval observation must never invoke analysis actions or workflow callbacks.

## Proof

- Repertoire and reused viewer component regression (`frontend`; Vitest test timeout `10000 ms`, hook timeout `10000 ms`; Bash tool timeout `120000 ms`):
  `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/viewer/evalBarDisplay.test.ts src/features/viewer/ViewerWorkspace.test.tsx src/features/analysis/EvalBar.test.tsx src/features/viewer/BoardEvalStage.test.tsx --testTimeout=10000 --hookTimeout=10000`
- Repertoire Workspace Storybook interactions (`frontend`; test timeout `10000 ms`, hook timeout `10000 ms`; Bash tool timeout `180000 ms`):
  `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`
- Optional preferred-workflow Storybook regression when that story is changed (`frontend`; test timeout `10000 ms`, hook timeout `10000 ms`; Bash tool timeout `180000 ms`):
  `npm run test-storybook -- --run src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx --testTimeout=10000 --hookTimeout=10000`
- Repertoire Storybook browser proof (repository root; Playwright runner timeout `30000 ms`, one worker; Bash tool timeout `180000 ms`):
  `npm exec playwright test tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`
- Viewer regression browser proof (repository root; Playwright runner timeout `30000 ms`, one worker; Bash tool timeout `180000 ms`):
  `npm exec playwright test tests/e2e/viewer-storybook.spec.ts --timeout=30000 --workers=1`
- Full repository closeout (repository root; `scripts/check.py` exposes no additional CLI timeout; Bash tool timeout `180000 ms`; no `--fix`):
  `.venv/Scripts/python.exe scripts/check.py`

## Escalation boundaries

- Do not execute until all three upstream Plans are completed, closed, and their final source/test/story/CSS
  baselines are available. Never execute in parallel with them.
- Do not change `PositionDescription`, `RepertoireSessionPanel`, staged-preview behavior, preferred-move
  behavior, opponent semantics, promotion, navigation, history, or the existing AnalysisPanel/candidate
  contract to solve eval-bar integration.
- Do not let the displayed-FEN observation enqueue, mutate, persist, re-key, or otherwise invoke parent
  analysis/workflow actions. Stop if the existing `useAnalysisState` contract cannot support the independent
  read-only observation without a new public/API/data/dependency contract.
- Do not change `EvalBar` score mapping, state semantics, orientation meaning, accessible contract, fixed 30px
  sizing, board-height synchronization, reduced-motion behavior, forced-colors behavior, or viewer layout
  without a separately approved narrow shared correction.
- Stop for any new product, visual, ownership, API, data, dependency, destructive, or acceptance decision,
  including a request to auto-enqueue staged evaluations, persist evaluation data, merge the two analysis
  identities, or redesign the wide/constrained workspace.
- README ownership maintenance is conditional and delegated to `readme-updater`; preserve unrelated files,
  active/historical Plans, and worktree changes. Never commit or push.

## Visible result

> `/repertoire` shows the viewer-identical 30px evaluation rail beside the displayed board, including staged previews, while its AnalysisPanel and preferred-move workflow remain anchored to the canonical parent.
