# Temporary-branch panel redesign - The interactive board has a clear, responsive, accessible temporary-branch panel with copyable FEN context and unchanged branch behavior.

> **Status:** done - implementation, focused proof, responsive/accessibility acceptance, fresh Quality validation, and final human acceptance completed

- **Read trigger:** Read before implementing the approved temporary-branch panel redesign or validating its closeout.
- **Upstream:** Approved case outcome and noncanonical reference [`experiments/mock-ups/temp branch/tempbranch.html`](../../../../experiments/mock-ups/temp%20branch/tempbranch.html); no master Plan.

## Outcome

Translate the approved noncanonical reference into the real `InteractiveBoardAdapter` panel immediately below the interactive board. The canonical panel will present exact origin and current six-field FEN values with accessible copy controls and bounded polite success/failure feedback, while retaining the separate full SAN branch line, model-derived current ply (`originPly + moves.length`), Undo/Reset actions, terminal state, action-disabled behavior, and one polite branch status. The result uses repository Material/CMT tokens and real React patterns without changing branch ownership or mechanics.

## Scope

- **Included:** Controlled semantic presentation and copy behavior in `InteractiveBoardAdapter`; local responsive and accessible styling; focused component, Storybook, and existing viewer-branch browser evidence for presentation, copy, responsiveness, and accessibility. Preserve existing props, callbacks, mechanics, test IDs, and `data-board-visual`.
- **Expected areas:**
  - `frontend/src/features/board-adapter/InteractiveBoardAdapter.tsx`
  - `frontend/src/features/board-adapter/InteractiveBoardAdapter.module.css`
  - `frontend/src/features/board-adapter/InteractiveBoardAdapter.test.tsx`
  - `frontend/src/features/board-adapter/InteractiveBoardAdapter.stories.tsx`
  - `tests/e2e/viewer-branch.spec.ts` only for presentation/copy/responsive/accessibility assertions
- **Proof-only areas:** `frontend/src/features/viewer/ViewerWorkspace.tsx`, `frontend/src/features/viewer/ViewerWorkspaceBranch.test.tsx`, `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`, `tests/e2e/viewer-branch-stage4.spec.ts`, and existing viewer/BoardEvalStage composition.
- **Excluded:** EvalBar and all eval/analysis/engine work; BoardEvalStage; APIs, backend, and data contracts; branch mutation, promotion, navigation gates, lifetime/discard, terminal semantics, `BranchSnapshot` meaning, and `ViewerWorkspace` ownership; static `BoardAdapter`, position narration, `GameContext`, `AnalysisPanel`, shared/global components or tokens, routes, dependencies, shell/layout; prototype edits; README, history, or other Plan edits; unrelated dirty worktree content; `Scratch/`; and `--fix`.

## Stages

1. **done** - **Controlled semantic presentation and copy behavior.** Confirmed a fresh, non-conflicting target-path baseline, then added structured origin/current FEN copy rows with distinct accessible names, exact six-field values, bounded success/failure feedback without branch mutation, full SAN, model-derived current ply, and focused regression coverage while preserving settled branch behavior. **Focused proof:** `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx` passed (2 files, 15 tests). **Escalate:** direct concurrent edits in target paths, a required API/dependency/ownership change, or any conflict between the approved presentation and settled branch semantics; no visual breakpoint in this stage.
2. **done** - **Canonical tokenized responsive styling.** Styled only through the local CSS Module using repository Material/CMT tokens. Browser inspection confirmed wrapped FEN, 48px copy targets, visible focus, forced-colors support, reduced-motion behavior, and no overflow at 320px, 480px, and 640px. Human visual/accessibility acceptance was received. **Focused proof:** focused tests passed (2 files, 15 tests), frontend build passed, and bounded browser inspection passed. **Escalate:** accessibility or responsive requirements that need global/shared changes, a new token, or an unsettled visual/product decision.
3. **done** - **Storybook and browser evidence.** Added stories for empty, active, action-disabled, promotion, terminal, copy-feedback, and constrained-width states without changing product contracts. Extended only `tests/e2e/viewer-branch.spec.ts` for exact FEN copy/status/names/mechanics, no-overflow, responsive, focus, forced-colors, reduced-motion, and axe assertions; retained the special-move regression as proof-only evidence. **Focused proof:** Storybook build and safely bounded test-storybook passed; targeted Playwright passed (17 tests). **Escalate:** a required change outside the approved e2e spec, a browser failure caused by an excluded composition/contract area, or accessibility proof requiring ownership/global/shared changes.
4. **done** - **Independent validation and closeout.** Focused Vitest, frontend build/lint/Prettier/size checks, Storybook build and accepted Stage 3 Storybook test proof, targeted Playwright evidence, the full read-only repository check, and final scope audit passed. Fresh Quality returned PASS after one authorized formatting-only repair. Two intermittent pre-existing browser races and pre-existing `AGENTS.md` whitespace were reported rather than absorbed; all changed-path evidence passed, no service remained listening on 6006, 5666, or 8444, and final human acceptance was received. **Escalate:** acceptance failure or need to modify an excluded area; never commit or push.

## Progress and decisions

- **Stage 1:** done - exact FEN rows, accessible copy controls, bounded copy feedback, derived ply, and unchanged branch behavior are covered; focused component and viewer-branch proof passed (2 files, 15 tests); breakpoint: none.
- **Stage 2:** done - implementation and responsive/accessibility browser inspection passed at 320px, 480px, and 640px; human visual/accessibility acceptance received.
- **Stage 3:** done - all named Storybook states are covered; safely bounded Storybook build/test passed; targeted viewer-branch and special-move Playwright proof passed (17 tests); breakpoint: none.
- **Stage 4:** done - fresh Quality PASS; focused tests (15), builds, lint, Prettier, size, Storybook evidence, targeted browser evidence, full read-only check, cleanup, and final scope audit passed; final human acceptance received.
- **Closeout:** done - accepted implementation retained in the approved paths; unrelated worktree changes and reported pre-existing flakes were not absorbed; Plan moved to `docs/plans/done/temporary-branch-redesign/`.

## Proof

- Focused component tests cover exact six-field origin/current FEN presentation, distinct accessible copy controls, bounded success/failure feedback, full SAN, `originPly + moves.length`, disabled actions, terminal state, status, and unchanged branch mechanics/captured-game immutability.
- Storybook covers empty, active, action-disabled, promotion, terminal, copy-feedback, and constrained-width states.
- Existing viewer/BoardEvalStage composition and proof-only viewer files remain unchanged unless inspection is needed to validate composition.
- Browser evidence covers exact copy/status/names/mechanics, responsive no-overflow at 320/480/640, keyboard focus, forced colors, reduced motion, and axe accessibility; the special-move regression remains green.
- Closeout runs the focused commands in the stages, including the full read-only `.venv/Scripts/python.exe scripts/check.py`, then performs final `git diff --check` and a target-path scope audit.

## Escalation boundaries

- Stop before implementation if any target path has direct concurrent edits; preserve the unrelated dirty worktree and active Plan/history records, including collision-sensitive EvalBar work. Do not merge, overwrite, or absorb concurrent changes.
- Escalate if copy behavior needs a new dependency or API, permission behavior is unsettled, or exact FEN copying cannot be implemented within the approved component boundary.
- Escalate if preserving the full separate SAN line conflicts with the reference, or if terminal semantics, branch mutation, promotion, navigation gates, lifetime/discard, `BranchSnapshot`, captured-game immutability, or `ViewerWorkspace` ownership would need to change.
- Escalate if accessibility or responsive styling requires global/shared ownership, new tokens, shell/layout changes, or any excluded path.
- Escalate any need for EvalBar, BoardEvalStage, eval/analysis/engine, backend/API/data, route, dependency, prototype, or other Plan/history changes; report unrelated failures rather than absorbing them.

## Visible result

> The interactive board has a clear, responsive, accessible temporary-branch panel with copyable FEN context and unchanged branch behavior.
