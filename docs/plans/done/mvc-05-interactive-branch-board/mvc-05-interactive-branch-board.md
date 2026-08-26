# MVC-05 Interactive branch board - controlled branch presentation with unchanged behavior

> **Status:** done - all execution stages and independent validation accepted

- **Read trigger:** Read after MVC-04 Promotion picker is accepted and before each sequential MVC-05 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-04 Promotion picker Plan/result](../../done/mvc-04-promotion-picker/mvc-04-promotion-picker.md)

## Outcome

Keep the current interactive board and temporary-branch presentation visually and behaviorally identical while
refining `InteractiveBoardAdapter` into a controlled visible boundary. The adapter renders controlled branch data and
emits user intentions; `ViewerWorkspace` retains branch workflow ownership, including branch state, mutation,
snapshot/lifetime behavior, reset tokens, captured-ply context, analysis targeting, and navigation gates.

## Scope

- **Included:** The smallest controlled adapter boundary supported by the existing call site; mechanical page
  reconnection; preservation of the existing branch snapshot shape; legal and illegal movement; Undo and Reset;
  SAN/FEN output; terminal classification; promotion-picker integration; accessible piece labels, board labels,
  live status, focus, reduced-motion, forced-colors, and existing local CSS treatment; focused tests and Storybook
  states/interactions; viewer branch integration tests/stories; existing branch browser proof; and bounded README
  responsibility-table maintenance when the ownership descriptions become stale.
- **Expected areas:**
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.tsx`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.module.css`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.test.tsx`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx` only for mechanical reconnection,
  `frontend/src/features/viewer/ViewerWorkspaceBranch.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`,
  `frontend/src/features/board-adapter/README.md`, and
  `frontend/src/features/viewer/README.md` only for bounded structural documentation reconciliation.
  `frontend/src/features/viewer/temporaryBranchModel.ts` is the protected snapshot-shape reference and is not an
  implementation target unless a mechanically necessary, existing-shape adjustment is proven.
- **Verification-only integration areas:**
  `tests/e2e/viewer-branch.spec.ts` and `tests/e2e/viewer-branch-stage4.spec.ts`.
- **Excluded:** Visual redesign; layout, typography, color, focus, keyboard, motion, or accessibility-direction
  changes; chess mutation, legal/illegal behavior, SAN/FEN, terminal, promotion, or branch-lifetime semantic changes;
  changes to `BranchSnapshot` meaning; backend/API/contract/data/dependency changes; universal game/opening/tree/
  session/viewer models; speculative abstractions or public customization; destructive cleanup; historical Plan or
  master-plan edits; unrelated worktree changes; `scripts/check.py --fix`; commits; and pushes.

## Stages

1. **complete - Controlled boundary and semantic regression lock.** Established the smallest controlled visible boundary
   without changing the adapter's rendered result or the page-owned branch semantics.

   - **Ordered actions:**
     1. Re-read the MVC master plan and accepted MVC-04 result, then inspect the current adapter props and symbols,
        `BranchSnapshot`, the `ViewerWorkspace` call site, reset effects, promotion seam, and existing focused tests.
     2. Record the current controlled display data and user-intention requirements from the existing call site. Define
        only the minimum prop/callback boundary needed to separate rendering from page-owned branch workflow; do not
        add public customization or a universal board/branch abstraction.
     3. Keep `ViewerWorkspace` responsible for branch state and mutation, branch snapshot/lifetime, reset-token and
        captured-ply behavior, analysis FEN selection, and traversal gates. Preserve the existing snapshot fields and
        the current `temporaryBranchModel.ts` shape.
     4. Refine `InteractiveBoardAdapter.tsx` and its CSS only as mechanically required to consume controlled branch
        data and emit movement, promotion, Undo, and Reset intentions. Preserve the current DOM structure, test IDs,
        accessible labels, status copy, promotion picker connection, local geometry, forced-colors, and reduced-motion
        behavior.
     5. Reconcile `InteractiveBoardAdapter.test.tsx` and `ViewerWorkspaceBranch.test.tsx` so they prove controlled
        rendering/intention flow as well as the existing legal/illegal movement, exact SAN/FEN, terminal, promotion,
        reset, captured-context, navigation-gate, analysis-target, and no-automatic-enqueue behavior.
     6. Inspect the scoped diff and confirm that no branch snapshot contract, historical record, backend/API path,
        dependency, or unrelated worktree change was absorbed.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build --prefix frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate if the controlled boundary requires a changed branch snapshot,
     changed chess/promotion/terminal semantics, a new public API or universal abstraction, a visual/accessibility
     decision, or ownership beyond the approved page-specific composition.

2. **complete - Storybook states/interactions and browser-visible proof.** Preserved the existing interactive-board and
   viewer branch stories while proving the controlled boundary through the real Storybook surface.

   - **Ordered actions:**
     1. Retain or refine `InteractiveBoardAdapter.stories.tsx` states for empty captured ply, active branch, Undo and
        Reset, and integrated promotion. Use only story-local harness behavior needed to observe controlled data and
        intentions.
     2. Retain or refine the viewer branch stories for initial branch presentation, navigation gating, promotion,
        castling, en passant, terminal classification, and replacement-load discard.
     3. Ensure Storybook interactions cover legal movement, illegal rejection without mutation, exact SAN/FEN output,
        Undo/Reset, promotion initiation and cancellation/selection, captured-ply context, disabled traversal, status
        announcements, accessible board/piece labels, and the existing presentation at wide and constrained sizes.
     4. Review both module CSS and make no visual-direction change. Reconcile the board-adapter and viewer README
        responsibility tables only if the controlled ownership move makes their current descriptions stale.
     5. Run the Storybook build and interaction suites, frontend lint, and frontend formatting checks.
     6. Run both existing branch Playwright specifications against the real Storybook iframe; do not weaken or rewrite
        expected behavior to accommodate the refactor.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend\node_modules\.bin\prettier.cmd --check frontend`

     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-branch.spec.ts tests\e2e\viewer-branch-stage4.spec.ts`
   - **Breakpoint:** None expected. Stop and escalate rather than choosing new copy, layout, focus treatment,
     accessibility semantics, browser expectations, primitive, dependency, or visual direction.

3. **complete - Viewer reconnection and read-only closeout.** Confirmed that the page-owned branch workflow remains
   behaviorally identical after reconnection, then complete bounded independent validation.

   - **Ordered actions:**
     1. Reconcile `ViewerWorkspace.tsx` and the mocked adapter in `ViewerWorkspaceBranch.test.tsx` only as mechanically
        required by the controlled boundary.
     2. Verify that page-level branch filtering by `viewKey` and `resetToken`, captured origin FEN/ply, replacement
        loading discard, analysis targeting, traversal gates, and reset behavior remain unchanged.
     3. Re-run the focused component and viewer branch tests, frontend build, Storybook build, lint, formatting, and
        both existing branch browser specifications.
     4. Inspect the final scoped diff, `git diff --check`, and worktree status. Confirm completed Plans, the master
        plan, historical records, and unrelated worktree content remain untouched.
     5. Run the full read-only repository check. Report unrelated baseline failures rather than repairing or absorbing
        them; never invoke `scripts/check.py --fix`.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run lint --prefix frontend`

     `frontend\node_modules\.bin\prettier.cmd --check frontend`

     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-branch.spec.ts tests\e2e\viewer-branch-stage4.spec.ts`

     `.venv\Scripts\python.exe scripts\check.py`

     `git diff --check`

     `git status --short --untracked-files=all`
   - **Breakpoint:** None expected. Stop and escalate if acceptance requires a behavior, ownership, contract,
     dependency, destructive, historical-record, unrelated-worktree, or validation decision not settled by this Plan.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - the adapter now consumes a controlled branch snapshot and emits movement, promotion,
  Undo, and Reset intentions while `ViewerWorkspace` owns chess mutation, notices, promotion state, terminal
  classification, snapshots, and resets. Focused Vitest passed 14/14, the frontend build passed with only the retained
  non-fatal warnings, and `git diff --check` passed with line-ending warnings. A mechanical story harness contract
  update was required for the TypeScript build; Storybook behavior remains Stage 2 proof.
- **Stage 2:** complete - adapter and viewer stories now exercise controlled branch state, illegal movement,
  Undo/Reset, promotion, special positions, statuses, exact FEN/SAN, and accessibility while preserving the existing
  promotion story baseline. Storybook passed 21 suites/101 tests, its build passed with retained non-fatal warnings,
  lint reported no errors and one retained Stage 1 hook warning, Prettier passed, both branch Playwright specs passed
  13/13, and `git diff --check` passed. The Storybook server was stopped and port 6006 was confirmed free. The two
  feature READMEs remain accurate, so no README maintenance is needed.
- **Stage 3:** complete - no further edits were required. Focused Vitest passed 14/14, the frontend and Storybook
  builds passed, lint had no errors and the retained hook warning, Prettier passed, branch Playwright passed 13/13,
  and the full read-only repository check passed on its completed 600-second rerun. `git diff --check` passed with
  normal line-ending warnings and worktree status showed no generated changes. The initial 120-second full-check run
  timed out; it made no repairs, and its transient workflow-contract output did not reproduce on the passing rerun.
- **Decisions:** MVC-04 is an accepted prerequisite. The existing `BranchSnapshot` shape, page-owned branch lifetime,
  unchanged visual/behavioral result, no-redesign boundary, existing branch stories/browser proof, bounded README
  reconciliation, and read-only full check are approved. No new model, dependency, endpoint, or historical-record
  change is approved.

## Proof

- Focused component and viewer branch behavior:
  `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`
- Frontend build:
  `npm.cmd run build --prefix frontend`
- Storybook build and interaction proof:
  `npm.cmd run build-storybook --prefix frontend` and
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`
- Lint and formatting:
  `npm.cmd run lint --prefix frontend` and
  `frontend\node_modules\.bin\prettier.cmd --check frontend`
- Existing branch browser proof:
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-branch.spec.ts tests\e2e\viewer-branch-stage4.spec.ts`
- Full read-only closeout:
  `.venv\Scripts\python.exe scripts\check.py`, `git diff --check`, and
  `git status --short --untracked-files=all`
- Independent Quality validation passed: focused Vitest passed 14/14 in 6.66 seconds, both branch Playwright specs
  passed 13/13 in 20.62 seconds, and `git diff --check` passed in 0.044 seconds. The bounded Storybook server became
  ready on its first health poll and was stopped afterward; ports 6006, 5666, and 8444 were confirmed free.
- `scripts/check.py --fix` is prohibited. Any unrelated baseline failure must be reported and remain outside MVC-05.

## Acceptance

- `InteractiveBoardAdapter` renders the same board and temporary-branch presentation while consuming controlled branch
  data and emitting user intentions rather than owning page-specific branch workflow.
- `ViewerWorkspace` retains branch state/mutation, snapshot and lifetime behavior, reset-token and captured-ply
  semantics, analysis targeting, replacement-load discard, and navigation gates.
- Legal and illegal movement, Undo/Reset, exact SAN/FEN, castling, en passant, terminal classification, q/r/b/n
  promotion, promotion cancellation, accessibility labels/statuses, and existing browser proof remain unchanged.
- Existing CSS geometry, responsive/constrained behavior, focus behavior, reduced-motion, forced-colors, and Storybook
  presentation remain unchanged.
- Focused, Storybook, browser, and full read-only checks pass; unrelated baseline failures are reported rather than
  absorbed.

## Escalation boundaries

- Any new product, visual, interaction, copy, focus, keyboard, accessibility, API, data, dependency, destructive,
  ownership, or acceptance decision.
- Any need to change the `InteractiveBoardAdapter` public contract beyond the smallest call-site-derived controlled
  boundary, change `BranchSnapshot`, or introduce a universal board/branch/viewer model.
- Any need to move chess mutation or promotion behavior in a way that changes semantics, branch lifetime, terminal
  classification, SAN/FEN, stale/illegal handling, or ownership outside the approved page-specific composition.
- Any change to layout, CSS geometry, typography, colors, focus treatment, motion preferences, accessible names,
  live-region behavior, Storybook expectations, or existing browser proof.
- Any backend/API/endpoint/payload/typed-error/contract/dependency/data change, historical-record edit, destructive
  cleanup, unrelated worktree change, formatter repair, `--fix` invocation, commit, or push.
- Any unrelated validation failure that would need repair or absorption to claim acceptance, or any inability to
  preserve the accepted MVC-01 through MVC-04 baseline.

## Visible result

> The same interactive temporary branch looks and behaves the same, while the page owns branch workflow and the board
> renders controlled data and reports user intentions.
