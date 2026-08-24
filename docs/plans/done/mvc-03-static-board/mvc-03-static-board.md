# MVC-03 Static board - an unchanged controlled static position display

> **Status:** done - all stages accepted with independent validation

- **Read trigger:** Read after MVC-02 Game loader is accepted and before each sequential MVC-03 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md),
  [completed MVC-01 Foundations Plan](../../done/mvc-01-foundations/mvc-01-foundations.md), and
  [completed MVC-02 Game loader Plan](../../done/mvc-02-game-loader/mvc-02-game-loader.md)

## Outcome

`BoardAdapter` is independently usable as a controlled static-position display with the same rendering, orientation,
coordinates, generated descriptions, invalid and unrenderable fallback, disclosure, unique `useId` accessibility
wiring, appearance, sizing, and accessibility. `ViewerWorkspace` retains its current static-board integration and all
viewer behavior remains unchanged.

## Scope

- **Included:** Preserve or mechanically refine the existing `BoardAdapter` controlled boundary; prove prop updates,
  static non-interactivity, orientation, coordinate visibility, generated position descriptions, strict invalid-FEN
  handling, unexpected render-failure containment, disclosure behavior, unique `useId`/`aria-describedby` wiring,
  local geometry, appearance, forced-colors behavior, and accessibility. Retain or add focused component tests,
  comprehensive Storybook states/interactions, existing board-adapter browser proof, and mechanical static-path
  viewer integration proof.
- **Expected areas:**
  `frontend/src/features/board-adapter/BoardAdapter.tsx`,
  `frontend/src/features/board-adapter/BoardAdapter.module.css`,
  `frontend/src/features/board-adapter/BoardAdapter.test.tsx`,
  `frontend/src/features/board-adapter/BoardAdapter.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`,
  `tests/e2e/board-adapter-storybook.spec.ts`, and the relevant existing viewer browser proof.
- **Protected baseline:** The accepted uncommitted MVC-02 work remains outside this Plan and must be preserved
  exactly: the MVC-02 changes to `GameLoader.tsx`, `GameLoader.test.tsx`, and `GameLoader.stories.tsx`, the completed
  MVC-02 Plan record under `docs/plans/done/mvc-02-game-loader/`, and its master-plan completion link.
- **Excluded:** Interactive movement, dragging, branch policy, interactive-board behavior, visual redesign, geometry
  globalization, new universal abstractions, page workflow changes, backend/API/data/dependency changes, endpoint or
  contract changes, destructive cleanup, unrelated worktree changes, historical-record rewrites, `--fix`, commits,
  and pushes.

## Stages

1. **accepted - Controlled adapter boundary and focused regression lock.** Establish the smallest independently usable
   static component boundary using the existing props and behavior. The current adapter already satisfies much of this
   contract, so inspect and preserve it before making only necessary edits.

   - **Ordered actions:**
     1. Review the current `BoardAdapter` props, validation/model flow, package isolation, shared unavailable state,
        static board semantics, disclosure, CSS geometry, and `useId` association against this Plan and the master-plan
        acceptance.
     2. Make only the smallest mechanical source changes required to keep the adapter controlled and independently
        renderable; do not add movement, package options, workflow state, new public customization, or a universal
        board abstraction.
     3. Extend or reconcile `BoardAdapter.test.tsx` for controlled prop changes, identical generated descriptions,
        orientation and coordinates, invalid and unrenderable fallback, non-interactivity, disclosure persistence, and
        distinct matching description IDs when multiple instances render.
     4. Inspect the scoped diff and confirm no MVC-02 file, historical record, interactive-board path, backend/API path,
        dependency, or unrelated worktree change was absorbed.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx`
     `npm.cmd run build --prefix frontend`
     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate if the current controlled contract, rendering, semantics,
     accessibility, or appearance cannot be preserved mechanically.

2. **accepted - Comprehensive Storybook and browser states/interactions.** Lock the complete existing static-board
   surface through real component stories and browser proof without changing its visual direction or semantic
   contract.

   - **Ordered actions:**
     1. Retain or update the seven existing Board Adapter stories for valid starting and rich positions, Black
        orientation, hidden coordinates, constrained sizing, invalid FEN, and expanded description; add only meaningful
        interaction coverage required for the controlled boundary and unique accessibility wiring.
     2. Preserve Storybook interaction coverage for collapsed and expanded disclosure, keyboard operation, static
        non-interactivity, generated description content, bounded square sizing at `320px`, `480px`, and `640px`,
        forced colors, and focused axe behavior.
     3. Retain or mechanically update `tests/e2e/board-adapter-storybook.spec.ts` so it exercises the real Storybook
        iframe, all meaningful stories, accessibility, sizing, disclosure, and forced-colors behavior.
     4. Review `BoardAdapter.module.css` for unchanged local geometry, package appearance, semantic tokens, overflow,
        and forced-colors behavior; do not globalize component geometry or select a new visual treatment.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`
     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`
     `npm.cmd run lint --prefix frontend`
     `frontend\node_modules\.bin\prettier.cmd --check frontend`
     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\board-adapter-storybook.spec.ts`
   - **Breakpoint:** None expected. Stop and escalate rather than choosing new copy, layout, focus treatment,
     disclosure behavior, accessibility semantics, dependency, or visual direction.

3. **accepted - Mechanical static-viewer reconnection and regression closeout.** Reconnect or confirm the static-board
   branch in `ViewerWorkspace` and prove that the page-owned workflow and visible viewer remain behaviorally
   unchanged.
   - **Ordered actions:**
     1. Update `ViewerWorkspace.tsx` only if needed to consume the controlled static adapter boundary; retain the
        current empty/loading/failure/reset fallback path, board label/orientation/FEN derivation, page layout,
        announcements, analysis state, and `InteractiveBoardAdapter` path unchanged.
     2. Extend or reconcile `ViewerWorkspace.test.tsx` and `ViewerWorkspace.stories.tsx` only for static-board
        integration evidence, preserving assertions for empty, loading, typed failure, reset, constrained layout,
        accessibility, loaded traversal, branch, analysis, and announcements.
     3. Run focused frontend, Storybook, lint, formatting, Board Adapter browser, and viewer browser proof; inspect the
        scoped diff and verify that the protected MVC-02 baseline and historical records remain untouched.
     4. Run the final read-only repository check. Report known unrelated baseline failures rather than repairing or
        absorbing them; never invoke `scripts/check.py --fix`.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
     `npm.cmd run build --prefix frontend`
     `npm.cmd run build-storybook --prefix frontend`
     `npm.cmd run lint --prefix frontend`
     `frontend\node_modules\.bin\prettier.cmd --check frontend`
     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\board-adapter-storybook.spec.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-live-position.spec.ts`
     `.venv\Scripts\python.exe scripts\check.py`
     `git diff --check`
   - **Breakpoint:** No human breakpoint is expected. Pause and escalate if visible equivalence, ownership,
     interaction, accessibility, contract, dependency, destructive, or acceptance proof requires a new decision.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** accepted - the existing source already satisfies the controlled static boundary, so only focused tests
  changed. Coverage now locks controlled prop updates and unique matching `useId` descriptions alongside the existing
  rendering, fallback, disclosure, non-interactivity, and accessibility proof. BoardAdapter Vitest passed (9/9), the
  frontend build and `git diff --check` passed, and no breakpoint appeared.
- **Stage 2:** accepted - the seven stories and browser proof now lock keyboard disclosure, generated descriptions,
  static semantics, unique IDs, fallback, forced colors, axe, and bounded sizing. Storybook build, all 21 Storybook
  suites (99 tests), lint, full frontend Prettier, targeted Board Adapter Playwright (1/1), focused BoardAdapter Vitest
  (9/9), and `git diff --check` passed. One MVC-03 test-formatting issue was corrected deterministically without
  `--fix`; no breakpoint appeared.
- **Stage 3:** accepted - existing `ViewerWorkspace` wiring already satisfies the
  controlled static boundary, so no viewer edit was needed. Focused Vitest passed (23/23), all 21 Storybook suites
  passed (99 tests), targeted browser proof passed (8/8), and frontend/Storybook builds, lint, Prettier, and
  `git diff --check` passed. The read-only full check reported only unrelated formatting in five experiment files and
  the protected Stockfish script plus the known transient Board Adapter axe timeout (47/48 browser tests). Bounded
  independent Quality validation passed 23/23 focused tests, the targeted Board Adapter browser spec, scoped
  formatting, and diff checks. No breakpoint appeared.
- **Decisions:** MVC-01 and MVC-02 are accepted dependencies. The no-redesign controlled boundary, three sequential
  stages, protected MVC-02 dirty baseline, read-only final check, and escalation boundaries are approved. Existing
  BoardAdapter behavior is evidence to preserve, not a reason to rewrite it. Known unrelated baseline failures remain
  report-only. The user's concurrent `.opencode/agents/scout.md` model change and
  `scripts/stockfish_analysis/analyze_positions.py` change are separately protected unrelated work and do not block
  this frontend slice. No genuine human decision was required, and independent Quality accepted MVC-03.

## Proof

- Focused adapter and viewer behavior:
  `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
- Frontend build, Storybook, lint, and formatting:
  `npm.cmd run build --prefix frontend`
  `npm.cmd run build-storybook --prefix frontend`
  `npm.cmd run lint --prefix frontend`
  `frontend\node_modules\.bin\prettier.cmd --check frontend`
- Storybook interaction and accessibility:
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`
- Board Adapter and viewer browser proof:
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\board-adapter-storybook.spec.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-live-position.spec.ts`
- Final read-only closeout:
  `.venv\Scripts\python.exe scripts\check.py`
  `git diff --check`
  `git status --short`
- `scripts/check.py --fix` is prohibited. Existing unrelated baseline failures, including known experiment formatting
  failures or transient Board Adapter Storybook timeouts, must be reported and remain outside this Plan.

## Acceptance

- A parent can render `BoardAdapter` with the existing controlled props and receive the same board appearance,
  orientation, coordinate visibility, generated description, invalid/unrenderable fallback, disclosure behavior,
  sizing, and accessibility semantics.
- Each rendered board has a unique matching `useId` description association; the package's draggable or focusable
  semantics do not escape the static adapter boundary.
- The seven meaningful Storybook states and their keyboard, disclosure, sizing, forced-colors, and axe evidence remain
  green without visual redesign.
- `ViewerWorkspace` retains the same static fallback and all existing viewer loading, failure, reset, traversal,
  branch, analysis, announcement, responsive, and accessibility behavior.
- Focused and full read-only proof passes, with any unrelated baseline failure explicitly reported rather than absorbed.

## Escalation boundaries

- Any new product, visual, behavior, interaction, accessibility, API, data, dependency, destructive, ownership, or
  acceptance decision.
- Any change to the `BoardAdapter` public contract beyond the smallest mechanically necessary controlled boundary;
  any movement, dragging, branch, analysis, or page workflow ownership inside the static adapter.
- Any change to package appearance, focus treatment, disclosure semantics, generated-description copy, invalid fallback,
  CSS geometry direction, global tokens, or component geometry globalization.
- Any backend/API/endpoint/payload/typed-error/contract change, universal abstraction, historical-record edit,
  unrelated worktree change, formatter repair, `--fix` invocation, commit, or push.
- Any unrelated failure that would need repair or absorption to claim acceptance, or any inability to preserve the
  protected MVC-02 dirty worktree exactly.

## Visible result

> The viewer's static chess board can be reused independently while looking, reading, sizing, and behaving exactly as it does today.
