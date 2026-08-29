# Viewer Flip/navigation - the Viewer toolbar flips orientation without changing position

> **Status:** accepted/done - V1 complete; independent Quality validation passed and the Plan is archived

- **Read trigger:** Read before each V1 execution stage, before changing the Viewer toolbar or workspace orientation,
  and at final closeout.
- **Upstream:** [Repertoire Builder master plan](../../../../master-plans/repertoire-builder/repertoire-builder.md);
  [accepted A1 neutral position-context API Plan](../../../../plans/done/repertoire-builder/neutral-position-context-api/neutral-position-context-api.md);
  [accepted Board control toolbar Plan](../../../../plans/done/board-control-toolbar/board-control-toolbar.md);
  [accepted Viewer composition Plan](../../../../plans/done/integrated-static-viewer/integrated-static-viewer.md)

## Outcome

Add an accessible Flip control to the existing Viewer Previous/Next toolbar. A person can flip the board while the
displayed FEN, game, ply, navigation position, local branch and analysis context remain unchanged. Empty Viewer starts
White at the bottom, while a loaded game initially uses its recorded `subject_color`.

## Scope

- **Included:** The controlled Flip callback and toolbar button; page-owned Viewer orientation state; orientation-aware
  board, board-label, and evaluation-bar presentation; preservation of existing navigation, branch, analysis,
  loading, reset, focus, disabled-navigation, constrained-layout, and accessibility behavior; focused component and
  workspace tests; existing Viewer stories; and bounded existing Viewer browser proof.
- **Expected areas:**
  `frontend/src/features/viewer/BoardControl.tsx`,
  `frontend/src/features/viewer/BoardControl.module.css` only if the local three-control layout needs adjustment,
  `frontend/src/features/viewer/BoardControl.test.tsx`,
  `frontend/src/features/viewer/BoardControl.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`,
  `tests/e2e/viewer-storybook.spec.ts`,
  `tests/e2e/viewer-live-position.spec.ts`,
  `tests/e2e/viewer.spec.ts` only where its existing Viewer assertions are applicable, and this Plan record.
- **Excluded:** Backend/API/A1 changes; preferred moves; persistence; schema, storage, or S5 work; routes; new
  dependencies; universal abstractions; shared design-system changes; redesigns of `BoardAdapter`, `BoardEvalStage`,
  `EvalBar`, or `AnalysisPanel`; repertoire “me” semantics; new browser profiles or unrelated specs; product or
  visual redesign; README or historical-record changes; runtime database writes; `--fix`; commits; pushes; and
  unrelated worktree changes.

## Stages

1. **complete - Add the controlled Flip seam and page-owned orientation state.** Implement the smallest callback and
   state boundary needed by the existing Viewer composition.
   - **Ordered actions:** Re-read this Plan and the accepted upstream records, then inspect the named current toolbar,
     workspace, test, story, and browser surfaces before editing. Preserve the existing Previous/Next public behavior,
     page-owned traversal, temporary-branch handling, loading gates, and focus semantics. Add an accessible Flip
     control using the existing toolbar, token, and icon conventions; do not add a generic navigation abstraction.
     Keep the standard-start base orientation White and derive a loaded game's initial base orientation from
     `game.subject_color`. Make Flip change only the orientation, pass that orientation through the existing board and
     evaluation-bar seams, and update the contextual board label. Resetting or successfully loading a new game must
     retain the existing reset behavior and ensure the newly displayed game starts at its recorded color; flipping must
     not change FEN, game, ply, navigation index, branch snapshot, analysis context, loading state, or persisted data.
     Extend focused tests for empty White orientation, Black-subject initial orientation, Flip state, unchanged current
     position/context, reset/new-load behavior, and preserved Previous/Next behavior.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** None expected. Stop and escalate rather than choosing a new orientation, branch, loading, reset,
     persistence, focus, accessibility, or shared-component rule.

2. **complete - Prove stories and existing Viewer browser surfaces.** Make the complete V1 result inspectable at wide
   and constrained widths without changing the Viewer layout contract.
   - **Ordered actions:** Reconcile BoardControl and ViewerWorkspace stories with the three-control toolbar and the
     settled orientation behavior. Extend only the existing Viewer browser specs where needed. Prove accessible
     Pointer and keyboard activation, focus retention/movement, disabled Previous/Next behavior, three-button toolbar
     semantics, responsive label/icon presentation, and no horizontal overflow. Prove that empty Viewer starts White,
     the Black-subject story and live loaded game start Black, Flip changes the board label and evaluation-bar direction,
     and the same displayed ply/FEN/context remains active. Use the existing Storybook server profile; bound startup
     health to 30 seconds, clean up only the server started for proof, and confirm port 6006 is free.
   - **Focused proof:**
     `timeout 300s npm.cmd run build-storybook --prefix frontend`

      `timeout 300s npm.cmd run test-storybook --prefix frontend`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-live-position.spec.ts`

     Each command has a recommended finite `bash` tool timeout of `360000` ms. Storybook startup health has a separate
     maximum of 30 seconds and must not be left running after proof.
   - **Breakpoint:** A bounded browser review is required for constrained fit, focus visibility, orientation labels,
     evaluation-bar direction, and overflow. Escalate if this requires a new visual direction, primitive, selector,
     browser profile/spec, or acceptance change.

3. **accepted/done - Complete read-only validation and the final scope audit.** Confirm the accepted V1 result and preserve
   unrelated worktree material before the Plan can close.
   - **Ordered actions:** Re-run the focused component/workspace tests, frontend build, Storybook build and interactions,
     lint, read-only formatting, size validation, and existing Viewer browser proof. Request fresh independent Quality
     validation of orientation, position/context preservation, accessibility, responsive fit, and unchanged navigation
     and branch behavior. Perform one final Git scope audit against the coordinator baseline plus whitespace proof;
     report unrelated failures rather than repairing or absorbing them. Do not update the master plan or historical
     records as part of implementation closeout, and do not use `--fix`.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     `timeout 300s npm.cmd run build-storybook --prefix frontend`

      `timeout 300s npm.cmd run test-storybook --prefix frontend`

     `timeout 120s npm.cmd run lint --prefix frontend`

     `timeout 120s frontend/node_modules/.bin/prettier.cmd --check frontend/src/features/viewer tests/e2e/viewer.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-live-position.spec.ts`

     `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-live-position.spec.ts`

     `timeout 30s git diff --check`

     Recommended finite `bash` tool timeouts are respectively `150000`, `150000`, `360000`, `360000`, `150000`,
     `150000`, `90000`, `360000`, and `60000` ms. Full closeout is:

     `timeout 600s .venv/Scripts/python.exe scripts/check.py`

     The full-check command has a recommended finite `bash` tool timeout of `660000` ms and must run without
     `--fix`.
   - **Breakpoint:** Fresh independent Quality validation, successful bounded Storybook cleanup with port-6006
     confirmation, and a clean final scope audit are required before archival. Stop for any unrelated failure that
     would require repair or scope absorption.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the approved
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - controlled Flip seam, page-owned orientation state, and focused regression proof passed;
  21 focused tests, frontend build, lint, and format proof passed; breakpoint: none.
- **Stage 2:** complete - stories and existing Viewer browser proof passed; 21 focused tests, frontend build, Storybook
  build, Storybook tests (27 files/139 tests), relevant Viewer Playwright (8 tests), ESLint/Prettier/size/diff proof
  passed; port 6006 was cleaned; breakpoint: none.
- **Stage 3:** accepted/done - read-only checks and exact full closeout passed, with one deterministic formatting-only
  repair in `tests/e2e/viewer.spec.ts`; fresh independent Quality validation passed its focused checks and semantic/scope
  audit. Quality found Flip's independent state and the replacement-loading test adequately demonstrate preserved loading
  semantics; no acceptance failure remains. Breakpoint: unrelated failures are reported rather than absorbed.
- **Settled decisions:** V1 is the next slice after accepted A1. Empty Viewer uses White at the bottom; a loaded game
  initially uses its recorded `subject_color`. Flip changes only board, board-label, and evaluation-bar orientation.
  Existing FEN, game, ply, navigation, local branch, analysis, loading, reset, accessibility, and persistence behavior
  remains unchanged. A1, backend/API boundaries, preferred-move behavior, schema/storage, and later Repertoire slices
  are not touched.
- **Closeout decisions:** The only repair was deterministic Prettier formatting in the approved Viewer browser spec;
  no semantic, product, visual, API, ownership, dependency, or acceptance decision changed. The planned Storybook
  `--url` argument was unsupported by the configured Vitest command, so the supported configured command without
  `--url` was used as a bounded substitution and passed; this did not change product scope or acceptance.

## Proof

- Focused BoardControl and ViewerWorkspace Vitest proof, frontend build, Storybook build/interactions, lint, read-only
  Prettier, source-size validation, and existing Viewer browser specs use the finite commands recorded in the stages.
- Storybook startup is bounded to 30 seconds, cleanup is mandatory, and port 6006 must be confirmed free afterward.
- Final whitespace proof is `timeout 30s git diff --check`; the final repository closeout is
  `timeout 600s .venv/Scripts/python.exe scripts/check.py`, without `--fix`.
- The final scope audit verifies that only the approved Viewer surfaces and this V1 Plan record changed; unrelated
  worktree material and other historical records remain preserved.
- Stage 3 results: focused tests 21/21, frontend build, Storybook build, lint, Prettier check, size check, relevant
  Viewer browser proof 8/8, `git diff --check`, and the exact full `.venv/Scripts/python.exe scripts/check.py`
  closeout (all 11 steps reported PASS) succeeded twice with a 600s command timeout and 660000ms tool timeout, without
  `--fix`. The planned Storybook `--url` argument was unsupported before test execution with Vitest `Unknown option
  '--url'`; the supported configured `timeout 300s npm.cmd run test-storybook --prefix frontend` was used as the bounded
  substitution and passed 27 files/139 tests.
- Fresh independent Quality validation passed its rerun of the 21 focused tests, frontend build, lint, Prettier, size,
  8 Viewer Playwright tests, and diff check; its semantic/scope audit passed. Quality found Flip's independent state and
  the replacement-loading test adequately demonstrate preserved loading semantics, with no acceptance failure. The
  separately updated README signpost at `frontend/src/features/viewer/README.md` required no validation and was not
  changed in this closeout.

## Escalation boundaries

- Any unsettled orientation, temporary-branch, loading, reset, persistence, or current-position interpretation.
- Any new product or visual direction, icon/affordance choice that cannot use the established local convention,
  inaccessible constrained layout, changed focus or disabled-navigation semantics, or acceptance relaxation.
- Any edit to backend/API/A1, preferred moves, persistence, schema/storage/S5, routes, dependencies, universal
  abstractions, shared design-system code, `BoardAdapter`, `BoardEvalStage`, `EvalBar`, or `AnalysisPanel`.
- Any new browser profile/spec beyond bounded changes to the existing Viewer specs, destructive cleanup, `--fix`,
  commit, push, historical-record edit, or absorption of unrelated worktree changes.
- Any Storybook startup/cleanup failure, occupied port 6006 owned by another process, unbounded command, or unrelated
  validation failure requiring repair.

## Visible result

> **Accepted V1 result (done):** The Viewer toolbar includes an accessible Flip control that changes board orientation
> while the same position, navigation state, and Viewer context remain visible.
