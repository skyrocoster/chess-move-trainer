# MVC-04 Promotion picker - a controlled picker with unchanged promotion behavior

> **Status:** done - all stages accepted with bounded independent validation

- **Read trigger:** Read after MVC-03 Static board is accepted and before each sequential MVC-04 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md),
  [completed MVC-01 Foundations Plan](../../done/mvc-01-foundations/mvc-01-foundations.md),
  [completed MVC-02 Game loader Plan](../../done/mvc-02-game-loader/mvc-02-game-loader.md), and
  [completed MVC-03 Static board Plan](../../done/mvc-03-static-board/mvc-03-static-board.md)

## Outcome

Confirm or mechanically refine `PromotionPicker` as a controlled visible boundary while preserving its identical
popover/drawer presentation primitives, constrained presentation selection, focus entry and restoration, live
announcements, selection and cancellation, stale/illegal rejection, exact promotion choices, appearance, and
accessibility. Retain `usePromotionController` only as a narrowly justified chess validation/commit/rejection helper;
branch and page workflow remain outside it.

## Scope

- **Included:** Preserve or mechanically refine the existing controlled `PromotionPicker` boundary; parent-controlled
  pending display, color, source and optional anchor elements, presentation selection, selection callback, and cancel
  callback; both Base UI Popover and Drawer primitives; automatic constrained presentation; first-choice focus;
  cancellation and focus restoration; live-region text; accessible names, dialog/group semantics, and axe coverage;
  exact q/r/b/n choices; stale and illegal rejection safety; local CSS appearance, forced-colors behavior, reduced
  motion, and existing promotion/demo and interactive-board reconnection. Retain `usePromotionController` only for
  chess candidate validation, stale-position guarding, trial/legal validation, chess commit, and commit/rejection
  callbacks.
- **Expected areas:**
  `frontend/src/features/board-adapter/PromotionPicker.tsx`,
  `frontend/src/features/board-adapter/PromotionPicker.module.css`,
  `frontend/src/features/board-adapter/PromotionPicker.test.tsx`,
  `frontend/src/features/board-adapter/PromotionPicker.stories.tsx`, and
  `frontend/src/features/board-adapter/PromotionPickerDemo.tsx` only for story-local harness proof when required.
- **Verification-only integration areas:**
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.tsx`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.test.tsx`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspaceBranch.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`,
  `tests/e2e/viewer-branch.spec.ts`, and
  `tests/e2e/viewer-branch-stage4.spec.ts`.
- **Protected baseline:** MVC-01 through MVC-03 completed Plans and their accepted product, test, story, browser,
  and historical records remain unchanged except for a mechanically necessary MVC-04 boundary reconciliation. The
  current clean worktree has no direct dirty overlap with MVC-04 paths.
- **Excluded:** Branch policy, timeline state, chess mutation changes outside the narrow helper, promotion-semantic
  changes, a new promotion workflow, page or branch ownership changes, visual redesign, universal abstraction,
  API/backend/dependency/data changes, destructive cleanup, unrelated files, historical records, `--fix`, commits,
  and pushes.

## Stages

1. **accepted - Controlled visible boundary and narrow-helper regression lock.** Confirm the smallest independently
   renderable visible boundary and preserve the current helper seam before making any source change.

   - **Ordered actions:**
     1. Review `PromotionPicker`'s current controlled props, pending mount behavior, Popover/Drawer branches,
        constrained media selection, focus refs and timing, live region, accessible names, local CSS, and the two
        direct `usePromotionController` consumers. Confirm that the visible component owns presentation only.
     2. Preserve the existing prop and callback shape and make only the smallest mechanical refinement required for a
        controlled boundary. Do not add public customization, move chess mutation into the picker, or introduce page,
        branch, timeline, or universal workflow state. Prefer no production edit when the current boundary already
        satisfies the outcome.
     3. Confirm that `usePromotionController` remains narrow: request-time promotion-candidate validation,
        position-token stale protection, trial/legal validation, chess commit, and commit/rejection callbacks only.
        Do not move branch or page workflow into the hook; preserve current request, stale, illegal, and cancellation
        outcomes.
     4. Extend or reconcile `PromotionPicker.test.tsx` for controlled pending transitions, exact selection and cancel
        intentions, both presentation primitives, focus entry/restoration, live announcements, all four choices,
        stale/illegal rejection, no unintended chess mutation, and focused axe coverage. Use local harness state rather
        than production workflow state.
     5. Inspect the scoped diff and confirm that no integration-only path, branch/timeline behavior, historical record,
        backend/API path, dependency, or unrelated worktree change was absorbed.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/PromotionPicker.test.tsx`

     `npm.cmd run build --prefix frontend`

     `git diff --check`

   - **Breakpoint:** None expected. Stop and escalate if preserving the current controlled contract requires a new API,
     changed promotion semantics, changed focus or accessibility behavior, changed appearance, or moved ownership.

2. **accepted - Comprehensive Storybook states/interactions and browser-visible proof.** Lock the existing picker surface
   through real stories and browser proof without changing its visual direction or semantic contract.

   - **Ordered actions:**
     1. Retain or refine the wide anchored popover, constrained drawer, keyboard selection, native initiation,
        cancellation, stale/illegal rejection fixture, forced-colors, and reduced-motion stories. Add only story-local
        harness behavior needed to prove the controlled boundary; do not add a production promotion workflow.
     2. Ensure Storybook interactions prove exact q/r/b/n selection, Escape and outside/backdrop cancellation, focus
        entry and source restoration, pending live announcements, presentation choice, accessible names, and focused
        axe behavior for both primitives.
     3. Review `PromotionPicker.module.css` for unchanged local geometry, tokens, focus treatment, overflow, forced
        colors, and reduced-motion behavior. Make no global geometry, token-direction, or visual-treatment change.
     4. Run the existing promotion browser surface against the real Storybook iframe, including the branch-facing
        presentation, cancellation, initiation, exact-choice, accessibility, forced-colors, and reduced-motion proof.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend\node_modules\.bin\prettier.cmd --check frontend`

     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-branch.spec.ts`

   - **Breakpoint:** None expected. Stop and escalate rather than choosing new copy, layout, focus treatment,
     accessibility semantics, dependency, primitive, motion, or visual direction.

3. **accepted - Mechanical InteractiveBoardAdapter/viewer reconnection and closeout.** Confirm the visible boundary is
   behaviorally invisible through the existing interactive-board and viewer promotion surfaces, then complete bounded
   independent validation.

   - **Ordered actions:**
     1. Confirm `InteractiveBoardAdapter` supplies the controlled picker boundary and keeps branch snapshots,
        captured context, current FEN/SAN, reset, terminal classification, and traversal gates unchanged. Update it
        only when a mechanically necessary picker-boundary change cannot be consumed without a wiring adjustment.
     2. Reconcile only directly affected interactive-board or viewer assertions/stories if required by the boundary;
        preserve promotion initiation, pending-position immutability, exact q/r/b/n commits, cancellation, stale/illegal
        safety, accessibility, and all existing branch/page ownership.
     3. Run focused component and integration tests, frontend and Storybook builds, lint, formatting, and both existing
        promotion/branch browser specifications. Inspect the scoped diff and verify completed Plans and unrelated
        worktree content remain untouched.
     4. Run the read-only full repository check. Report any unrelated baseline failure rather than repairing or
        absorbing it; never invoke `scripts/check.py --fix`.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/PromotionPicker.test.tsx src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run lint --prefix frontend`

     `frontend\node_modules\.bin\prettier.cmd --check frontend`

     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-branch.spec.ts tests\e2e\viewer-branch-stage4.spec.ts`

     `.venv\Scripts\python.exe scripts\check.py`

     `git diff --check`

     `git status --short --untracked-files=all`

   - **Breakpoint:** None expected. Stop and escalate if visible equivalence, behavior, focus, accessibility,
     promotion semantics, ownership, contract, dependency, destructive, or acceptance proof requires a new decision.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** accepted - the existing production boundary already meets the controlled picker and narrow-helper
  requirements, so no source or test edit was needed. Focused PromotionPicker tests passed (14/14), the frontend build
  and scoped diff check passed, and no breakpoint appeared.
- **Stage 2:** accepted - existing stories and browser coverage already lock Popover/Drawer presentation, keyboard
  selection, cancellation, focus, accessibility, forced colors, reduced motion, and branch-facing behavior, so no edit
  was needed. Storybook build, all 21 Storybook suites (99 tests), lint, Prettier, and targeted viewer-branch Playwright
  (8/8) passed; no breakpoint appeared.
- **Stage 3:** accepted - existing adapter/viewer integration already meets
  the controlled picker boundary, so no edit was needed. Focused tests passed (42/42), targeted branch browser proof
  passed (13/13), and frontend/Storybook builds, lint, Prettier, and diff checks passed. The read-only full check
  reported only unrelated formatting and Board Adapter timeout categories outside MVC-04. After one Plan-only
  formatting repair, fresh bounded Quality validation passed 42/42 focused tests, 13/13 targeted browser tests,
  scoped Prettier, and scoped diff checks. No breakpoint appeared.
- **Decisions:** MVC-01 through MVC-03 are accepted dependencies. The no-redesign controlled boundary, narrow
  `usePromotionController` helper, three sequential stages, existing promotion/branch proof surfaces, clean direct
  overlap status, read-only full check, and escalation boundaries are approved. The current boundary may already
  satisfy much of MVC-04, so evidence and the smallest edits take precedence. No genuine human breakpoint was required,
  and bounded independent Quality accepted MVC-04.

## Proof

- Focused component and integration behavior:
  `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/PromotionPicker.test.tsx src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`
- Frontend build, Storybook, lint, and formatting:
  `npm.cmd run build --prefix frontend`,
  `npm.cmd run build-storybook --prefix frontend`,
  `npm.cmd run lint --prefix frontend`, and
  `frontend\node_modules\.bin\prettier.cmd --check frontend`
- Storybook interaction and accessibility:
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`
- Existing promotion, branch, presentation, focus, accessibility, and exact-choice browser proof:
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-branch.spec.ts tests\e2e\viewer-branch-stage4.spec.ts`
- Final read-only closeout:
  `.venv\Scripts\python.exe scripts\check.py`,
  `git diff --check`, and
  `git status --short --untracked-files=all`
- `scripts/check.py --fix` is prohibited. Any unrelated baseline failure must be reported and remain outside MVC-04.

## Acceptance

- A parent can render `PromotionPicker` with the existing controlled boundary and receive the same exact q/r/b/n
  selection and cancellation intentions without the visible component owning chess, branch, timeline, or page state.
- The wide anchored Popover and constrained Drawer remain the same primitives with the same constrained selection,
  focus entry, source focus restoration, live announcement, dialog/group semantics, accessible names, axe results,
  forced-colors behavior, reduced-motion behavior, local geometry, and appearance.
- Illegal requests and stale or illegal selections leave the position unchanged according to the current semantics;
  valid selections commit the same chess move, FEN, and history through `usePromotionController` when that helper is
  retained.
- `usePromotionController` remains limited to narrow chess validation, stale protection, commit, cancellation, and
  rejection callbacks; no branch policy, timeline state, page workflow, or new promotion workflow enters it.
- Existing `PromotionPickerDemo`, `InteractiveBoardAdapter`, `ViewerWorkspace`, Storybook, promotion browser, branch
  browser, and accessibility behavior remain observably unchanged.
- Focused and full read-only proof passes, with any unrelated baseline failure explicitly reported rather than absorbed.

## Escalation boundaries

- Any new product, visual, interaction, copy, focus, keyboard, accessibility, API, data, dependency, ownership,
  destructive, or acceptance decision.
- Any change to the `PromotionPicker` public prop/callback contract beyond the smallest mechanically necessary
  controlled boundary, or any need for a universal picker/viewer abstraction.
- Any need to move chess mutation, branch policy, timeline state, page workflow, or promotion semantics into or out of
  the approved narrow helper in a way that changes behavior or ownership.
- Any change to Popover/Drawer primitives, constrained presentation selection, focus treatment/restoration, live-region
  copy, dialog/group semantics, exact choices, CSS geometry direction, global tokens, forced-colors behavior, or
  reduced-motion behavior.
- Any backend/API/endpoint/payload/typed-error/contract/dependency/data change, historical-record edit, destructive
  cleanup, unrelated worktree change, formatter repair, `--fix` invocation, commit, or push.
- Any unrelated failure that would need repair or absorption to claim acceptance, or any inability to preserve the
  accepted MVC-01 through MVC-03 baseline.

## Visible result

> The same promotion picker can be controlled and reused while its wide popover, constrained drawer, choices, focus,
> announcements, accessibility, appearance, and viewer behavior remain unchanged.
