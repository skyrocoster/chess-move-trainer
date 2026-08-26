# MVC-09 Game context - the same context presentation with separate page-specific boundaries

> **Status:** complete - accepted by user after case-worker execution; independent Quality validation did not complete because the validation run was interrupted/cancelled twice, and the user explicitly accepted closeout without it. No independent Quality PASS is claimed.

- **Read trigger:** Read after MVC-08 Analysis panel is accepted and before each sequential MVC-09 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-08 Analysis panel Plan/result](../../done/mvc-08-analysis-panel/mvc-08-analysis-panel.md)

## Outcome

Separate the game metadata, safe source attribution, position disclosure, and already-controlled `AnalysisPanel`
behind page-specific controlled boundaries while retaining the current grouping, order, copy, layout, default-open
behavior, safe source rules, empty state, Ply/SAN copy, and accessibility semantics. `ViewerWorkspace` remains the page
owner of game/position and analysis state and owns the narrow local composition that keeps `AnalysisPanel` in its current
visual position.

## Scope

- **Included:** The smallest call-site-derived context boundary and local composition seam; context disclosure and
  metadata/source presentation; preservation of source URL safety; mechanical viewer reconnection; current empty,
  initial, intermediate, and final position presentation; focused tests; comprehensive context and composition
  Storybook states/interactions with relevant accessibility coverage; viewer integration proof; read-only closeout; and
  this active Plan record.
- **Expected areas:**
  `frontend/src/features/viewer/GameContext.tsx`,
  `frontend/src/features/viewer/stage1SourceSafety.ts` for preservation-only changes if mechanically necessary,
  `frontend/src/features/viewer/GameContext.module.css` for preservation-only changes if mechanically necessary,
  `frontend/src/features/viewer/GameContext.test.tsx`,
  `frontend/src/features/viewer/GameContext.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
   `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`, and
   `docs/plans/done/mvc-09-game-context/mvc-09-game-context.md`.
- **Excluded:** `AnalysisPanel.tsx` and `AnalysisPanel.module.css`; `ViewerWorkspace.module.css`; the design-system
  `Disclosure`; APIs, backend, contracts, dependencies, and models; new metadata, source, opening, or analysis
  behavior; universal frameworks or slot systems; visual, layout, typography, color, motion, focus, keyboard, or
  accessibility redesign; README maintenance; destructive cleanup; edits to completed Plans or historical records;
  unrelated worktree changes; `scripts/check.py --fix`; commits; and pushes.

### Implementation-critical facts and guardrails

- `GameContext.tsx` currently owns the `Game Context` disclosure, `defaultOpen`, empty-state gating, metadata rows, and
  source attribution. Its accepted MVC-08 boundary currently accepts an `analysisPanel?: AnalysisPanelProps` prop and
  renders the controlled panel after the metadata rows. Remove that AnalysisPanel-specific ownership without changing
  the rendered disclosure structure, grouping, order, or location.
- `AnalysisPanel` is already controlled from MVC-08. Preserve its display/callback contract, DOM, copy, accessibility,
  action behavior, and separate module CSS. Do not move analysis state, derivation, polling, client work, or callbacks
  into `GameContext`.
- `ViewerWorkspace.tsx` owns the game, selected position, single analysis observation, analysis display derivation, and
  deliberate analysis callbacks. It must continue to own the local composition that places the existing controlled
  `AnalysisPanel` in the same context area without duplicating observation work.
- The exact local seam may be selected from the current call site, but it must be narrow and page-specific. A generic
  local composition mechanism is acceptable only when it preserves the current DOM and does not become a public or
  universal slot/customization framework.
- Preserve the `Disclosure` summary `Game Context`, its uncontrolled `defaultOpen` behavior, the metadata order `Ply`,
  `Last move`, `Source`, the empty `No game loaded` state, `Initial position`, current SAN, source link target/rel,
  and `Source unavailable` behavior.
- Preserve `safeSourceUrl` exactly: only HTTPS `www.chess.com` live/daily game paths without a query or hash produce a
  link; invalid, unsafe, or missing values remain unavailable.
- Preserve the accepted MVC-05 through MVC-08 dirty baseline. Current relevant files are intentionally modified, and
  completed MVC-05 through MVC-08 Plans, `evalBarDisplay.ts`, workflow/check changes, README changes, test
  reorganizations, experiments, and all other tracked/untracked content must remain untouched.
- Current relevant source and test files are within repository size limits. Re-check source/test sizes after each stage;
  escalate rather than crossing the approved path boundary if preserving the outcome requires an extraction with new
  ownership or semantics.
- Storybook/browser proof must use bounded startup/readiness, stop only the process started for proof, and confirm port
  6006 is free afterward. Do not kill an unrelated port owner or wait unboundedly.

## Stages

1. **complete - Smallest controlled context boundary and local composition seam.** Separate context metadata/source and
   disclosure presentation from the AnalysisPanel-specific contract while preserving the exact current DOM, grouping,
   order, default-open behavior, CSS, and visual location.

   - **Ordered actions:**
     1. Re-read the master plan and accepted MVC-08 result, inspect the bounded context and viewer surfaces, and
        inspect the current dirty worktree. Preserve the accepted MVC-05 through MVC-08 baseline and every unrelated
        tracked/untracked change.
     2. Define the minimum call-site-derived boundary: `GameContext` owns only context disclosure and metadata/source
        display; `ViewerWorkspace` owns game/position and analysis state plus the local composition of the existing
        controlled `AnalysisPanel`. Do not introduce a universal slot API or public customization surface.
     3. Mechanically remove the AnalysisPanel-specific ownership from `GameContext` and reconnect the existing panel
        through the selected narrow local seam. Keep the same disclosure panel, metadata-before-analysis order,
        conditional empty state, and context grid location.
     4. Preserve `stage1SourceSafety.ts`, `GameContext.module.css`, and all source-link, disclosure, metadata, and
        accessibility behavior unless a mechanically necessary non-visual adjustment is proven.
     5. Run focused context/viewer/component regression proof and inspect the scoped diff, file sizes, CSS, and status
        for analysis, visual, semantic, API, historical-record, or unrelated-worktree changes.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate if exact grouping, DOM, order, default-open behavior, source
     behavior, accessibility, analysis placement, or ownership requires a broader interface or any unsettled decision.

2. **complete - Focused context states and composition evidence.** Prove the separated boundary across all settled
   metadata, source, disclosure, accessibility, and AnalysisPanel-placement states without changing presentation.

   - **Ordered actions:**
     1. Reconcile `GameContext.test.tsx` around the controlled context boundary and cover empty, initial,
        intermediate, and final positions; exact Ply/SAN and initial-position copy; default-open semantics; safe,
        unsafe, and missing source values; link target/rel; no unsafe link; and relevant axe/accessibility semantics.
     2. Retain or add viewer assertions proving metadata remains before the analysis presentation, the panel remains in
        the existing disclosure/group, and the page still supplies the already-controlled analysis display and
        callbacks without duplicate workflow or observation work.
     3. Reconcile `GameContext.stories.tsx` and the bounded viewer stories with comprehensive empty, position, source,
        constrained, default-open, accessibility, and composed context/analysis states. Exercise only existing settled
        interactions; do not invent disclosure, metadata, source, or analysis behavior.
     4. Build Storybook before interaction proof. Start only the repository Storybook server needed for proof, bound
        readiness to 30 seconds, clean it up in all cases, and confirm port 6006 is free afterward.
     5. Run focused tests, Storybook interactions, lint, read-only formatting, file-size checks, and `git diff --check`.
        Inspect context CSS, stories, and DOM assertions for unchanged geometry, colors, forced-colors behavior, copy,
        order, focus, and accessibility direction.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop rather than choosing new metadata, source, disclosure, copy, order, layout,
     focus/accessibility semantics, browser expectation, dependency, or Storybook direction.

3. **complete - Viewer reconnection and read-only closeout.** Confirm the separated context boundary is behaviorally
   invisible in the viewer, then complete focused, Storybook, browser, and repository proof.

   - **Ordered actions:**
     1. Re-run the focused context, AnalysisPanel, and viewer integration tests. Confirm the same game/position data,
        metadata order, source behavior, disclosure state, context location, and AnalysisPanel placement remain visible;
        confirm the same page-owned analysis observation still drives the EvalBar and panel.
     2. Run the frontend build, Storybook build and interactions, lint, read-only formatting, and the existing viewer
        Storybook browser specification. Use bounded startup and mandatory cleanup; confirm port 6006 is free.
     3. Run the complete repository check exactly as `.venv/Scripts/python.exe scripts/check.py` in read-only mode.
        Never append `--fix`; report unrelated baseline failures rather than repairing or absorbing them.
     4. Inspect `git diff --check`, the scoped diff, source/test file sizes, and complete worktree status. Confirm
        AnalysisPanel source/CSS, `ViewerWorkspace.module.css`, Disclosure, APIs/contracts, completed Plans, historical
        records, and every unrelated tracked/untracked change remain preserved.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`

     `.venv/Scripts/python.exe scripts/check.py`

     `git diff --check`

     `git status --short --untracked-files=all`
   - **Breakpoint:** None expected. Stop and escalate if acceptance requires any unsettled behavior, ownership,
     contract, dependency, destructive, visual, accessibility, README, historical-record, unrelated-worktree, or
     validation decision. Storybook/browser cleanup and port-6006 confirmation are mandatory.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome or
requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - `GameContext` now owns only the context disclosure and metadata/source presentation, while
  `ViewerWorkspace` composes the existing controlled `AnalysisPanel` through a narrow local child seam. Focused Vitest
  passed (3 suites, 34 tests), the frontend build passed, `git diff --check` passed, and source/test sizes remain within
  limits; breakpoint: none.
- **Stage 2:** complete - strengthened `GameContext` tests and Storybook states/interactions for empty, initial,
  intermediate, final, safe/unsafe/missing source, exact Ply/SAN, default-open disclosure, controlled-child placement,
  composition, and accessibility. Viewer integration assertions retain metadata-before-analysis order and the existing
  disclosure composition. Focused Vitest passed (3 suites, 42 tests), Storybook build passed, bounded Storybook
  interactions passed (21 suites, 121 tests), lint exited successfully with the pre-existing `ViewerWorkspace.tsx`
  hook warning, scoped formatting passed, source/test sizes passed, and `git diff --check` passed; breakpoint: none.
- **Stage 3:** complete for case-worker execution - focused tests, frontend and Storybook builds/interactions, lint,
  Prettier, viewer browser proof, diff, status, and the full read-only check were run; the full check reports seven
  unrelated/concurrency-sensitive full-suite E2E timing failures while all other check steps passed. Independent Quality
  validation did not complete because the validation run was interrupted/cancelled twice; the user explicitly accepted
  closeout without it, and no independent Quality PASS is claimed.
- **Decisions:** MVC-08 is the accepted prerequisite. Stage 1 selected the existing call site's narrow local child
  composition: `GameContext` no longer imports or accepts an AnalysisPanel-specific interface, and `ViewerWorkspace`
  renders the existing controlled `AnalysisPanel` as its child. `GameContext` owns only context disclosure and
  metadata/source presentation; `ViewerWorkspace` remains the page owner of game/position and analysis state. The
  rendered disclosure structure, grouping, order, and location are preserved; no universal/public slot framework,
  visual redesign, or human visual decision is authorized or expected.
- Stage 3 diagnosed the repository-wide Prettier warning against the Stage 1 diff: the multiline `GameContext` opening
  tag in `ViewerWorkspace.tsx` was slice-introduced. It was normalized to Prettier's single-line form only; no semantic
  behavior changed and `--fix` was not used.
- **Closeout:** The user subsequently made test-suite/Quality-agent improvements as the authoritative baseline; this
  record does not enumerate or alter them.

## Proof

- **Stage 1 result:** focused context/AnalysisPanel/viewer tests, the frontend build, and `git diff --check` passed;
  the exact commands are listed below.
- **Stage 2 result:** focused context/AnalysisPanel/viewer tests, Storybook build/interactions, lint, scoped
  formatting, source/test size checks, and `git diff --check` passed. Storybook readiness was bounded to 30 seconds,
  the proof server was cleaned up, and port 6006 was confirmed free. The repository-wide read-only Prettier check
  still reports the accepted dirty-baseline formatting issue in `ViewerWorkspace.tsx`; that production path was not
  changed in this stage. No production source, CSS, API, backend, dependency, or unrelated worktree content changed.
- Focused context, accepted AnalysisPanel, and viewer integration:
  `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`.
- Frontend build: `npm.cmd run build --prefix frontend`.
- Storybook build and interaction proof:
  `npm.cmd run build-storybook --prefix frontend` and
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`.
- Lint and formatting: `npm.cmd run lint --prefix frontend` and
  `frontend/node_modules/.bin/prettier.cmd --check frontend`.
- Viewer browser proof:
  `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`.
- **Stage 3 result:** focused Vitest passed (3 suites, 42 tests); frontend and Storybook builds passed; bounded
  Storybook interactions passed (21 suites, 121 tests) with readiness within 30 seconds, cleanup, and port 6006 free;
  lint exited successfully with the known `ViewerWorkspace.tsx` hook warning; Prettier passed; viewer browser proof
  passed (2 tests); `git diff --check` passed; scoped source/test sizes remained within limits. The exact full
  read-only `.venv/Scripts/python.exe scripts/check.py` completed with frontend tests, Python tests, workflow, Ruff,
  ESLint, Prettier, builds, Storybook interactions, and source-size checks passed, but repository E2E reported 7/50
  failures and 43 passed under the full 6-worker run (board-adapter/design-system/responsive-shell/viewer branch and
  viewer Storybook timing failures), classified by the case-worker as unrelated/concurrency-sensitive. No E2E repair
  was absorbed because the required focused viewer browser proof passed and no E2E surface was changed in Stage 3.
- **Closeout result:** Independent Quality validation did not complete because its validation run was
  interrupted/cancelled twice. The user explicitly accepted closeout without independent Quality validation; no
  independent Quality PASS is claimed. The user's subsequent test-suite/Quality-agent improvements remain the
  authoritative baseline and were not enumerated or altered for this closeout.
- Full read-only closeout: `.venv/Scripts/python.exe scripts/check.py`, `git diff --check`, and
  `git status --short --untracked-files=all`. Never use `--fix`.
- Operational proof is bounded: Storybook readiness is at most 30 seconds, cleanup is mandatory, and port 6006 must be
  confirmed free afterward. Unrelated failures are reported rather than repaired.

## Acceptance

- `GameContext` owns only the current context disclosure and metadata/source presentation; it has no AnalysisPanel-
  specific analysis workflow or ownership.
- `AnalysisPanel` remains an independently controlled MVC-08 component, receives the same page-owned display data and
  callbacks, and remains in the same disclosure grouping, visual location, and metadata-before-analysis order.
- `ViewerWorkspace` remains the sole page owner of game/position and analysis state, derivation, deliberate actions,
  polling, and observation; no duplicate analysis observation or workflow work is introduced.
- Empty, initial, intermediate, and final positions retain the same `No game loaded`, Ply, SAN, and `Initial position`
  output; the `Game Context` disclosure remains expanded by default.
- Safe source attribution retains the exact HTTPS `www.chess.com` live/daily allowlist, target/rel attributes, and
  unavailable output for unsafe or missing values.
- Metadata/source/disclosure DOM, order, grouping, geometry, forced-colors behavior, focus behavior, and accessibility
  semantics remain unchanged; relevant focused axe coverage and viewer integration proof pass.
- Focused tests, Storybook states/interactions, frontend build, lint, formatting, viewer browser proof, and source/test
  size checks pass. `.venv/Scripts/python.exe scripts/check.py` completed with 43/50 E2E tests passing and seven
  unrelated/concurrency-sensitive timing failures reported, not absorbed. Independent Quality validation did not
  complete, and the user accepted closeout without it; no independent Quality PASS is claimed.
- No API/backend/contract/dependency/model/visual/semantic/automatic-action change, universal slot framework, README
  maintenance, historical-record rewrite, `--fix`, commit, push, or unrelated-worktree modification is introduced.

## Escalation boundaries

- Any change to behavior, copy, source allowlist or link attributes, default-open behavior, metadata meaning, grouping,
  order, layout, DOM, focus, keyboard, motion, color, typography, or accessibility semantics.
- Any change to AnalysisPanel source/CSS, analysis display/callback behavior, analysis state, derivation, polling,
  deliberate action, observation sharing, or workflow ownership.
- Any need for a broader/public/universal slot, customization, viewer, game, opening, tree, session, or analysis
  abstraction; any new dependency, API/backend/contract/model/data change; or ownership outside this page-specific
  composition.
- Any path expansion beyond the approved Plan and listed context/viewer surfaces, including `ViewerWorkspace.module.css`,
  design-system `Disclosure`, READMEs, completed Plans, or historical records.
- Any destructive effect, reset/reformat/absorption of unrelated tracked or untracked content, use of `--fix`, commit,
  push, or repair of an unrelated validation failure.
- Any source/test file-size violation that cannot be resolved within the listed paths without changing ownership or
  semantics.
- Any Storybook/browser server that is not bounded, cannot be cleaned up, or leaves port 6006 ownership unconfirmed.

## Visible result

> The same game context and analysis presentation remain in the same place and read the same, while metadata, source,
> disclosure, and analysis have separate page-specific controlled boundaries.
