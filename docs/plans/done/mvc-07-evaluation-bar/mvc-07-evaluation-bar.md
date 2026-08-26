# MVC-07 Evaluation bar - the same evaluation display with page-owned derivation

> **Status:** done - accepted after independent validation

- **Read trigger:** Read after MVC-06 Navigation controls is accepted and before each sequential MVC-07 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-06 Navigation controls Plan/result](../../done/mvc-06-navigation-controls/mvc-06-navigation-controls.md)

## Outcome

Refine `EvalBar` into a controlled, independently designable visible display while preserving the current evaluation
states, meter values, orientation, accessible text, styling, and shared analysis observation behavior. `ViewerWorkspace`
continues to own analysis workflow and derives the display data; `EvalBar` only renders that controlled display.

## Scope

- **Included:** The smallest call-site-derived controlled display boundary; page-owned derivation of the existing
  neutral, queued/running, completed, stale/failed, score, meter, orientation, and accessible-value states; mechanical
  viewer reconnection; unchanged `EvalBar` DOM and module CSS; focused component tests; comprehensive Storybook states,
  interactions, and relevant axe coverage; shared-observation integration assertions; and read-only proof.
- **Expected areas:**
  `frontend/src/features/viewer/EvalBar.tsx`,
  `frontend/src/features/viewer/EvalBar.module.css` for preservation-only changes if mechanically required,
  `frontend/src/features/viewer/EvalBar.test.tsx`,
  `frontend/src/features/viewer/EvalBar.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx` only for page-owned display derivation and mechanical
  reconnection, and
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx` for shared-observation and viewer integration proof.
  `tests/e2e/viewer-storybook.spec.ts` is verification-only unless an exact existing expectation requires scoped,
  behavior-preserving maintenance.
- **Excluded:** Analysis client, polling, enqueue/retry actions, analysis ownership, endpoint/API/backend behavior,
  payloads, typed errors, analysis semantics, new product behavior, visual or layout redesign, changes to fonts,
  colors, typography, focus, motion, or accessibility direction; universal viewer/game/opening/tree/session models;
  new dependencies, data or database work, speculative public customization, README maintenance, destructive cleanup,
  edits to completed Plans, historical records, or the master plan; modification or absorption of unrelated worktree
  changes; `scripts/check.py --fix`; commits; and pushes.

## Implementation-critical facts and worktree guardrails

- `EvalBar.tsx` currently accepts `orientation` and `analysisState`, derives display state and accessible copy from
  analysis observations, maps CP and mate scores to the meter, and renders the Base UI meter. The visible component
  must stop consuming workflow state and receive only the smallest controlled display data needed by the existing
  call site; do not add a general visualization or customization API.
- `ViewerWorkspace.tsx` owns `useAnalysisState` and currently passes the same `analysisState` to both `EvalBar` and
  `GameContext`/`AnalysisPanel`. Keep that single observation and keep `AnalysisClient`, polling, enqueue actions, and
  all workflow transitions outside `EvalBar`.
- Preserve the current display mapping exactly: neutral/no-analysis and unavailable states, queued/running pending
  states, completed best-line state, stale/failed wording, CP/mate/mate-given meter values and clamping, white/black
  orientation, meter label/value semantics, and existing accessible text.
- `EvalBar.module.css` is preservation-only. Retain its geometry, orientation rules, state styling, transitions,
  forced-colors behavior, and semantic/global token usage without introducing visual direction.
- Existing `ViewerWorkspace.tsx` and `ViewerWorkspace.stories.tsx` contain dirty accepted MVC-05/MVC-06 work and are
  overlapping baseline surfaces. Preserve them exactly except for the approved MVC-07 derivation/reconnection need.
  The current worktree also contains unrelated workflow and README edits, board/navigation changes, check-script and
  test reorganizations, untracked completed MVC-05/MVC-06 Plans, experiments, and helper modules. Do not reset,
  reformat, stage, or absorb any of them.
- The MVC-06 result records an unrelated `tests/e2e/board-adapter-storybook.spec.ts` timeout in the full check. If
  that baseline failure recurs, report it without repairing or claiming it as an MVC-07 failure.

## Stages

1. **complete - Controlled display boundary and page-owned derivation.** Move evaluation display derivation out of the
   visible component while keeping the rendered result and analysis workflow unchanged.

   - **Ordered actions:**
     1. Re-read the master plan and accepted MVC-06 result, then inspect the current `EvalBar` implementation, CSS,
        focused tests/stories, `ViewerWorkspace` analysis hook and call sites, the shared-observation integration test,
        and the current dirty worktree. Preserve all accepted and unrelated changes.
     2. Define only the smallest controlled display contract supported by the current call site: orientation plus
        pre-derived display state, meter value, and accessible value (or an equivalent minimum shape). Do not expose
        `AnalysisState`, analysis candidates, client methods, polling state, or public customization options from the
        visible component.
     3. Move the existing display mapping and score-to-meter derivation to the page-owned side of the boundary. Keep
        every current branch and value unchanged, including neutral, queued/running, completed, stale/failed,
        CP/mate/mate-given, orientation, clamping, and accessible copy behavior.
     4. Refine `EvalBar.tsx` to render the same Base UI meter, DOM structure, labels, attributes, state markers, and
        controlled values. Leave `EvalBar.module.css` unchanged unless a mechanically necessary non-visual adjustment
        is proven.
     5. Reconcile only the focused component tests and the existing shared-observation assertion needed to prove the
        new boundary; do not move `AnalysisClient` or duplicate observation work.
     6. Inspect the scoped diff and confirm that no analysis workflow, API contract, CSS direction, completed record,
        or unrelated worktree change was absorbed.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/EvalBar.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate if preserving the current display contract requires changed
     semantics, accessible copy, meter mapping, public customization, workflow ownership, CSS direction, or any
     decision outside this Plan.

2. **complete - Complete focused states and Storybook evidence.** Prove the controlled display across every meaningful
   settled state without changing its visual or semantic direction.

   - **Ordered actions:**
     1. Expand `EvalBar.test.tsx` to cover neutral/no-analysis and unavailable states, queued and running pending
        states, completed CP and mate variants, stale and failed states with and without a retained candidate,
        white/black orientation, meter values and clamping, exact accessible values, non-focus behavior, and focused
        axe coverage.
     2. Reconcile `EvalBar.stories.tsx` with the controlled contract and add comprehensive neutral, queued, running,
        completed, stale, failed, CP/mate, orientation, and accessible-value stories. Use story interactions only to
        assert settled display data, labels, state attributes, meter values, and accessibility; do not invent behavior.
     3. Build Storybook before interaction proof. Start only the repository Storybook server needed for proof, bound
        readiness to 30 seconds, clean it up in all cases, and confirm port 6006 is free afterward. Do not kill an
        unrelated process occupying that port.
     4. Run the Storybook interaction suite, lint, and read-only formatting checks. Inspect the CSS diff and confirm
        that geometry, colors, state styling, forced colors, motion, and orientation rules remain unchanged.
     5. Review the focused diff for exact state/copy preservation and ensure `tests/e2e/viewer-storybook.spec.ts` needs
        no edit; escalate before changing it unless an existing expectation is mechanically stale because of the
        approved controlled boundary.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate rather than choosing new copy, state semantics, meter behavior,
     visual treatment, focus/accessibility behavior, dependency, browser expectation, or Storybook direction.

3. **complete - Viewer reconnection and read-only closeout.** Confirm that the page-owned derivation is behaviorally
   invisible in the viewer, then complete focused, browser, and full read-only proof.

   - **Ordered actions:**
     1. Reconnect the controlled `EvalBar` through `ViewerWorkspace.tsx` using the existing `analysisState` as the
        source for page-owned display derivation. Preserve the same observation instance for the bar and
        `GameContext`/`AnalysisPanel`; do not add a second client observation, poller, enqueue action, or workflow seam.
     2. Retain or refine `ViewerWorkspace.test.tsx` so it proves the empty display and the shared completed observation
        remain behaviorally identical, including the existing single-observation assertion and accessible best-line
        output.
     3. Re-run focused Vitest, frontend build, Storybook build and interaction proof, lint, formatting, and the existing
        viewer Storybook browser specification. Use bounded Storybook startup and mandatory cleanup/port confirmation.
     4. Run the complete repository check exactly as `.venv/Scripts/python.exe scripts/check.py` in Git Bash, read-only,
        without `--fix`. Report unrelated baseline failures without repairing or absorbing them.
     5. Inspect `git diff --check`, the scoped diff, and complete worktree status. Confirm that the CSS, viewer layout,
        analysis workflow/API seams, completed Plans, historical records, and all unrelated tracked and untracked
        changes remain preserved.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/EvalBar.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`

     `.venv/Scripts/python.exe scripts/check.py`

     `git diff --check`

     `git status --short --untracked-files=all`
   - **Breakpoint:** None expected. Stop and escalate if acceptance requires a behavior, ownership, API/contract,
     dependency, visual, accessibility, historical-record, unrelated-worktree, README, or validation decision not
     settled by this Plan. Storybook/browser servers must be cleaned up and port 6006 confirmed free before closeout.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - `EvalBar` now receives controlled display state, meter value, accessible value, and
  orientation while `ViewerWorkspace` owns the unchanged derivation. Focused Vitest passed (2 files, 18 tests), the
  frontend build passed, and `git diff --check` passed; only existing warnings were observed. Breakpoint: none.
- **Stage 2:** complete - 16 focused `EvalBar` tests passed; the Storybook build and all 21 suites/113 interaction
  tests passed; lint, Prettier, and `git diff --check` passed; and port 6006 was confirmed free after cleanup. Existing
  non-fatal Windows teardown, chunk-size, lint, and jsdom canvas warnings were unchanged. Breakpoint: none.
- **Stage 3:** complete - focused Vitest passed (2 files, 30 tests), frontend and Storybook builds passed, all 21
  Storybook suites/113 tests passed, lint and Prettier passed, viewer browser proof passed (2 tests), cleanup completed
  and `git diff --check` passed. The initial full read-only check exposed MVC-07's 509-line `ViewerWorkspace.tsx` size
  violation; the authorized extraction repair restored it to 436 lines. Fresh final validation passed the complete
  read-only suite twice, and the coordinator stopped the proven repository Storybook process and confirmed port 6006
  free. Breakpoint: none.
- **Independent validation:** failed closeout because MVC-07's inline derivation caused the 509-line
  `ViewerWorkspace.tsx` size violation. One deterministic repair is authorized: extract only that derivation to the
  same-feature `evalBarDisplay.ts` helper, preserving page ownership and behavior, then run fresh final validation.
  Fresh Quality validation passed all acceptance proof after that repair. Quality identified the lingering port owner
  as this repository's Storybook process; the coordinator terminated its process tree and confirmed port 6006 free.
- **Decisions:** MVC-06 is the accepted prerequisite. The visible boundary is controlled with page-owned derivation;
  `AnalysisClient` and `analysisState.ts` remain workflow seams; CSS is preservation-only; no support design skill or
  human visual decision is required unless the settled no-redesign direction cannot be preserved.

## Proof

- Focused component and viewer integration:
  `npm.cmd run test --prefix frontend -- --run src/features/viewer/EvalBar.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
- Frontend build: `npm.cmd run build --prefix frontend`
- Storybook build and interaction proof:
  `npm.cmd run build-storybook --prefix frontend` and
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`
- Lint and formatting:
  `npm.cmd run lint --prefix frontend` and
  `frontend/node_modules/.bin/prettier.cmd --check frontend`
- Viewer browser proof:
  `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`
- Full read-only closeout: `.venv/Scripts/python.exe scripts/check.py`, `git diff --check`, and
  `git status --short --untracked-files=all`. Never append `--fix`.
- Storybook/browser operational rules: readiness is bounded to 30 seconds, cleanup is mandatory, and port 6006 must be
  confirmed free afterward. Unrelated baseline failures are reported rather than repaired.

## Acceptance

- `EvalBar` is independently renderable from controlled display data and owns no `AnalysisState`, analysis client,
  polling, enqueue action, or page workflow.
- The current neutral, queued/running, completed, stale/failed, CP/mate/mate-given, orientation, meter, accessible
  value, forced-colors, geometry, and non-focus behavior remain unchanged.
- `ViewerWorkspace` remains the sole page owner of analysis derivation and workflow, and the same analysis observation
  continues to drive both the evaluation bar and analysis presentation without duplicate observation work.
- Focused tests, Storybook states/interactions, axe coverage, frontend build, lint, formatting, viewer browser proof,
  and the full read-only repository check pass. Known unrelated failures are reported rather than absorbed.
- No backend/API/dependency/visual/semantic/ownership change, historical-record rewrite, `--fix`, commit, or push is
  introduced, and all pre-existing dirty worktree content remains intact.

## Escalation boundaries

- Any new product behavior, display state, copy, score interpretation, meter range/mapping, orientation rule, focus or
  accessibility behavior, visual direction, layout, typography, color, motion, or browser expectation.
- Any need for `EvalBar` to consume `AnalysisState`, `AnalysisClient`, polling, enqueue/retry behavior, or to own
  analysis workflow; any duplicate observation or change to `AnalysisPanel`/`GameContext` integration semantics.
- Any public customization API, universal viewer/analysis abstraction, new dependency, backend/API/endpoint/payload/
  typed-error/analysis-contract change, data change, or ownership outside the approved page composition.
- Any need to change `EvalBar.module.css` beyond a mechanically necessary non-visual adjustment, edit the master plan,
  completed Plans, historical records, README files, or verification expectations for changed behavior.
- Any need to reset, reformat, absorb, stage, commit, push, or otherwise modify unrelated tracked or untracked worktree
  content; any use of `scripts/check.py --fix`; or any unrelated validation failure that requires repair.
- Any occupied proof port owned by another process, unbounded Storybook/browser wait, failed cleanup, or inability to
  confirm port 6006 is free.

## Visible result

> The same evaluation bar looks and reads the same, while `ViewerWorkspace` supplies its derived display data and owns
> all analysis decisions.
