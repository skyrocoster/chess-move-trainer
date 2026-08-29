# Viewer position-count integration - Viewer shows neutral recurrence statistics

> **Status:** accepted/done - V2 complete; independent Quality validation passed and the Plan is archived

- **Read trigger:** Read before each V2 execution stage, before changing the position-context client/state/component or
  Viewer/GameContext composition, and at final closeout.
- **Upstream:** [Repertoire Builder master plan](../../../../master-plans/repertoire-builder/repertoire-builder.md);
  [confirmed Repertoire Builder direction](../../../../grilling-docs/DONE/repertoire-builder-direction.md);
  [accepted A1 neutral position-context API Plan](../../../../plans/done/repertoire-builder/neutral-position-context-api/neutral-position-context-api.md);
  [accepted V1 Viewer Flip/navigation Plan](../../../../plans/done/repertoire-builder/viewer-flip-navigation/viewer-flip-navigation.md);
  [accepted Game Context presentation Plan](../../../../plans/done/game-context-cmt/game-context-cmt.md);
  [accepted AnalysisPanel Plan](../../../../plans/done/analysis-panel-cmt/analysis-panel-cmt.md)

## Outcome

Add the shared neutral recurrence statistic to the existing Viewer context. For the currently displayed FEN, Viewer
shows the accepted A1 White and Black distinct-game scopes as `Seen in N games as White/Black` or `Never seen as
White/Black`. Empty Viewer remains unchanged. Captured-game navigation and temporary branches refresh context from
the displayed FEN, while Flip changes only orientation and does not change recurrence scope or lookup meaning.

## Scope

- **Included:** A typed frontend client for `GET /api/position-context`, abortable displayed-FEN state, a focused
  position-context component, additive GameContext/Viewer composition, token-local presentation only where needed,
  focused component/state/client tests, existing Viewer stories, and bounded extensions to existing Viewer browser
  proof.
- **Expected areas:** `frontend/src/features/viewer/positionContextApi.ts`,
  `frontend/src/features/viewer/positionContextApi.test.ts`,
  `frontend/src/features/viewer/positionContextState.ts`,
  `frontend/src/features/viewer/positionContextState.test.ts`,
  `frontend/src/features/viewer/PositionContext.tsx`,
  `frontend/src/features/viewer/PositionContext.module.css` only if local token styling is needed,
  `frontend/src/features/viewer/PositionContext.test.tsx`,
  `frontend/src/features/viewer/PositionContext.stories.tsx`,
  `frontend/src/features/viewer/GameContext.{tsx,test.tsx,stories.tsx}`,
  `frontend/src/features/viewer/ViewerWorkspace.{tsx,test.tsx,stories.tsx}` only for composition and regression proof,
  and existing `tests/e2e/viewer*.spec.ts` files only where their current Viewer proof needs the V2 assertions.
- **Excluded:** Backend/API/A1 changes; S4 recurrence or schema changes; preferred moves; persistence; personal
  projections; side-to-move counts; new routes or dependencies; changes to V1 Flip/navigation, analysis, branch,
  disclosure, metadata ordering, or layout ownership; `BoardControl`, `BoardEvalStage`, `EvalBar`, or `AnalysisPanel`
  redesigns; universal abstractions; new browser profiles/specs; new visible loading/error treatment; visual redesign;
  README or historical-record changes; runtime database writes; `--fix`; commits; pushes; and unrelated worktree
  changes.

## Stages

1. **complete - Establish the typed client and displayed-FEN state seam.** Add the smallest frontend boundary needed to
   read A1 without changing its contract.
   - **Ordered actions:** Re-read this Plan, A1, V1, and the named current client/state/viewer surfaces before editing.
     Preserve the coordinator baseline and stop for a direct collision in the shared Viewer files. Implement a typed
     position-context client that sends the full six-field displayed FEN, validates the exact A1 response while
     respecting the accepted four-field identity, and maps only the accepted typed failures. Add abortable state that
     does not request an empty Viewer, discards stale responses, and follows `analysisFen` when a temporary branch is
     active. Keep non-success handling safe and consistent with existing local conventions; do not invent a new visible
     loading/error treatment. Add client and state tests for valid results, zero-versus-absent results, malformed or
     extra response data, typed HTTP failures, empty FEN input, displayed-FEN changes, branch FEN, and stale requests.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/viewer/positionContextApi.test.ts src/features/viewer/positionContextState.test.ts`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** Stop if the accepted A1 endpoint, full-FEN boundary, four-field identity, failure mapping, abort
     behavior, or displayed-branch target requires a new API, data, cache, debounce, persistence, or user-facing error
     decision.

2. **complete - Compose the statistic into GameContext and Viewer.** Make the approved count result visible without
   moving existing context or analysis ownership.
   - **Ordered actions:** Re-read the current `GameContext`, `ViewerWorkspace`, branch tests, and V1 orientation proof.
     Add the White/Black seen/never-seen presentation for successful A1 results, retaining the exact existing metadata
     order and controlled AnalysisPanel child seam. Wire Viewer context to `analysisFen`, so captured navigation and
     every temporary branch position refresh the statistic; preserve the current position while Flip only changes
     orientation and never reinterprets the recurrence scopes. Preserve empty `No game loaded`, navigation, branch,
     analysis, disclosure, focus, accessibility, constrained-layout, and overflow behavior. Add focused tests for
     initial/intermediate/final positions, positive counts, zero counts, absent positions, branch refresh, navigation,
     Flip preservation, empty state, failure safety, and focused axe coverage. Add direct stories for seen, zero, absent,
     branch/displayed-FEN, constrained, and accessibility states. If the existing Viewer story file would exceed the
     source-size limit, extract only bounded fixtures inside the Viewer test/story area without changing behavior.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/viewer/PositionContext.test.tsx src/features/viewer/GameContext.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** A visual review is required for the statistic in the existing wide and constrained Game Context.
     Stop rather than guessing if the result needs a new hierarchy, copy, token, responsive rule, landmark, focus
     behavior, public prop contract, Viewer ownership rule, or visible loading/error treatment.

3. **complete - Prove the integrated Viewer stories and browser behavior.** Demonstrate the result at the existing
   Storybook and application Viewer surfaces without adding a browser profile or new product surface.
   - **Ordered actions:** Build Storybook before its interaction suite. Extend existing Viewer stories and browser specs
     only as needed to prove positive White/Black counts, `Never seen` zero/absent behavior, displayed-FEN refresh after
     navigation and temporary branch moves, unchanged context through Flip, empty Viewer preservation, accessibility,
     constrained fit, forced colors, and no horizontal overflow. Keep Storybook startup bounded to 30 seconds, clean up
     only the proof server, and confirm port 6006 is free. Use the configured Storybook command without `--url`; V1
     recorded that argument as unsupported by the configured runner.
   - **Focused proof:**
     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-live-position.spec.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`

     Each command has a recommended finite `bash` tool timeout of `360000` ms. Storybook startup health has a separate
     maximum of 30 seconds and the server must not remain running after proof.
   - **Breakpoint:** Stop if existing browser surfaces cannot prove the selected displayed-FEN behavior without a new
     profile/spec, a changed route, a new selector contract, a layout redesign, or an acceptance change.

4. **accepted/done - Complete read-only validation and prepare coordinator closeout.** Confirm the approved V2 result and
   preserve the packet baseline before the coordinator-owned independent Quality route.
   - **Ordered actions:** Re-run focused client/state/component/viewer tests, frontend build, Storybook build and
     interactions, lint, read-only Prettier, source-size validation, and the bounded existing Viewer/branch browser
     proof. Run the governing repository closeout command without `--fix` or `--full`. Perform one final Git scope audit
     against the coordinator baseline plus whitespace proof; preserve A1/V1 material, unrelated worktree edits,
     backend/API files, historical records, and all excluded surfaces. Report unrelated failures rather than repairing
     or absorbing them. Independent Quality validation and final acceptance remain coordinator-owned after execution and
     are not implementation actions in this Plan.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/viewer/positionContextApi.test.ts src/features/viewer/positionContextState.test.ts src/features/viewer/PositionContext.test.tsx src/features/viewer/GameContext.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend`

     `timeout 120s npm.cmd run lint --prefix frontend`

     `timeout 120s frontend/node_modules/.bin/prettier.cmd --check frontend/src/features/viewer tests/e2e/viewer.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-live-position.spec.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`

     `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-live-position.spec.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`

     `timeout 30s git diff --check`

     `timeout 600s .venv/Scripts/python.exe scripts/check.py`

     Recommended finite `bash` tool timeouts are respectively `150000`, `150000`, `360000`, `360000`, `150000`,
     `150000`, `90000`, `360000`, `60000`, and `660000` ms. The repository closeout is intentionally the governing
     command without `--full`, as directed by the coordinator.
   - **Breakpoint:** Coordinator-owned independent Quality validation, successful bounded Storybook cleanup with port
     6006 confirmation, final acceptance, and a clean scope audit are required before archival. Stop for any unrelated
     failure requiring repair or any scope, acceptance, contract, ownership, or safety expansion.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the approved
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - typed client and displayed-FEN state seam, with the focused client/state proof passing;
  breakpoint remained unchanged.
- **Stage 2:** complete - Viewer/GameContext composition and focused presentation proof, with existing context,
  analysis, branch, disclosure, layout, and accessibility ownership preserved.
- **Stage 3:** complete - Storybook and existing Viewer browser proof, with no new browser profile, selector contract,
  or visual direction.
- **Stage 4:** accepted/done - read-only validation and final scope audit passed. Final Luna's focused six-file Viewer
  proof passed 58 tests; frontend build, Storybook build/interactions (28 files/149 tests), lint, and source-size
  validation passed; the bounded Viewer browser set passed 28 tests; and the governing repository closeout passed after
  the format-only Viewer README table alignment. Generated outputs were removed, port 6006 was free, and no `--fix`
  was used.
- **Fresh independent Quality:** PASS - independently reran 58 focused tests, frontend build, lint, source-size
  validation, 27 Viewer browser tests, diff checks, and semantic/scope checks. The targeted Prettier warning in
  pre-existing baseline portions of `tests/e2e/viewer-branch.spec.ts` is not a V2 finding; V2-added lines comply.
- **Settled decision:** Recurrence follows the displayed `analysisFen`, including temporary branches. While a temporary
  branch is active, recurrence lookup uses the displayed temporary-branch FEN rather than the captured
  `currentPosition.fen`, matching the existing analysis targeting behavior. Flip changes orientation only and must not
  change recurrence color scope or create a semantically different lookup.
- **Displayed branch FEN proof:** The approved temporary branch case displays
  `rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1`; it retains `Seen in 7 games as White` and
  `Seen in 6 games as Black` through Flip.
- **Preserved decisions:** A1 returns overall existence plus distinct White/Black game-color counts; `color_scope` is
  Skyrocoster's stable recorded game color, never side to move. Positive counts use `Seen in N games as White/Black`;
  zero counts and absent overall positions use `Never seen as White/Black`. Empty Viewer remains unchanged.
- **Supported Storybook command:** Use `npm.cmd run build-storybook --prefix frontend` followed by
  `npm.cmd run test-storybook --prefix frontend`; the configured runner does not support `--url`.
- **README boundary:** The separately updated `frontend/src/features/viewer/README.md` and `frontend/README.md` were
  preserved as unrelated baseline material and required no validation.

## Proof

- Client/state proof validates the exact full-FEN request boundary, strict response shape, A1 typed failures, stale
  response protection, empty-state no-request behavior, and displayed temporary-branch targeting.
- Component and Viewer proof validates White/Black recurrence copy, positive/zero/absent distinctions, navigation and
  branch refresh, Flip preservation, existing Game Context child order, focused axe, and unchanged empty/disclosure/
  analysis behavior.
- Storybook and existing Viewer/branch browser proof validates wide/constrained presentation, accessibility, forced
  colors, overflow, displayed-FEN behavior, and the absence of new product controls or route surfaces.
- Final validation uses finite lint, read-only Prettier, source-size, whitespace, and the governing
  `.venv/Scripts/python.exe scripts/check.py` closeout without `--fix` or `--full`; Storybook cleanup and the one final
  coordinator-baseline scope audit are mandatory.
- Final Luna proof passed: the six focused Viewer files passed 58 tests; frontend build passed; Storybook build and
  interactions passed 28 files/149 tests; lint and source-size passed; the bounded Viewer browser set passed 28 tests;
  and `.venv/Scripts/python.exe scripts/check.py` passed all checks after the format-only Viewer README table alignment,
  without `--fix` or `--full`. Generated outputs were removed and port 6006 was confirmed free.
- Fresh independent Quality validation passed 58 focused tests, frontend build, lint, source-size validation, 27 Viewer
  browser tests, diff checks, and semantic/scope checks. The targeted read-only Prettier warning in pre-existing
  baseline portions of `tests/e2e/viewer-branch.spec.ts` was preserved and classified as not a V2 finding; V2-added
  lines were compliant.
- The separately updated `frontend/src/features/viewer/README.md` and `frontend/README.md` were preserved outside V2;
  no validation was required for those README updates.

## Acceptance

- A loaded Viewer displays both neutral recurrence scopes using `Seen in N games as White/Black` or `Never seen as
  White/Black`, with distinct game-color counts and the approved zero-versus-absent distinction.
- The request uses the full displayed FEN. Captured navigation and temporary branch moves, undo/reset, and replacement
  refresh the statistic for the displayed position; no stale result replaces the current result.
- Flip preserves the same displayed position and recurrence meaning. It never converts White/Black game-color scopes
  into side-to-move or orientation scopes and does not trigger a semantically different lookup.
- Empty Viewer still shows its existing empty context and static board behavior. Existing GameContext metadata order,
  AnalysisPanel child composition, navigation, branch, disclosure, focus, accessibility, responsive fit, and overflow
  behavior remain intact.
- Only the approved frontend client/state/component, Viewer/GameContext composition, focused tests/stories, and bounded
  existing Viewer browser proof change. A1, V1, backend/S4/schema/storage, preferred moves, routes, dependencies,
  historical records, and unrelated worktree changes remain untouched.
- Focused proof, Storybook proof, existing Viewer/branch browser proof, coordinator-owned independent Quality validation,
  final acceptance, scope audit, and the governing repository closeout pass.

## Escalation boundaries

- Any change to the accepted A1 endpoint, full-FEN HTTP boundary, exact four-field identity, response fields, typed
  failures, distinct-game denominator, stable ownership, or S4 recurrence facts.
- Any proposal to use the captured FEN during a temporary branch, side-to-move counts, personal projections, subject
  identity, caching/debouncing/persistence, automatic selection, or a semantically different Flip lookup.
- Any new visible loading/error treatment, copy or hierarchy not settled by the approved direction and existing local
  conventions; any change to GameContext public ownership, metadata order, AnalysisPanel composition, branch/analysis
  targeting, disclosure, focus, accessibility, responsive layout, or Viewer page ownership.
- Any new dependency, design-system primitive, route, universal abstraction, browser profile/spec, product control,
  visual direction, destructive action, runtime database write, or acceptance relaxation.
- Any direct collision with the coordinator baseline, especially the accepted V1 changes in shared Viewer source/tests/
  stories/browser files or the untracked A1 backend feature. Preserve both edits and return to the coordinator; do not
  merge by assumption.
- Any source/test file-size violation, unbounded command or server, failed Storybook cleanup or occupied port 6006,
  unrelated validation failure requiring repair, `--fix`, commit, push, historical-record edit, or absorption of
  unrelated worktree changes.

## Visible result

> **Accepted V2 result (done):** Viewer shows neutral White/Black recurrence statistics for the currently displayed
> `analysisFen`, including temporary branches, while Flip, empty state, and existing Viewer behavior remain unchanged.
