# Temporary-branch panel redesign - The interactive board has a clear, responsive, accessible temporary-branch panel with copyable FEN context and unchanged branch behavior.

> **Status:** pending - approved scope is ready for sequential implementation; execution requires a fresh non-conflicting baseline in the target paths

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

1. **pending** - **Controlled semantic presentation and copy behavior.** First confirm execution has a fresh, non-conflicting baseline in all target paths; do not merge, overwrite, or absorb concurrent work. Preserve the existing props, callbacks, branch mechanics, test IDs, and `data-board-visual`. Add structured origin/current FEN copy rows with distinct accessible names, exact six-field values, bounded success/failure feedback without branch mutation, full SAN, model-derived current ply, existing Undo/Reset and disabled-action behavior, terminal state, and one polite branch status. Add focused component coverage for names, exact values, copy outcomes, derived ply, status/mechanics preservation, and immutable captured games. **Focused proof:** `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`. **Escalate:** direct concurrent edits in target paths, a required API/dependency/ownership change, or any conflict between the approved presentation and settled branch semantics; no visual breakpoint in this stage.
2. **pending** - **Canonical tokenized responsive styling.** Style only through the local CSS Module using repository Material/CMT tokens. Cover wrapped FEN, tokenized 48px copy targets, SAN, ply, actions, terminal state, and the single polite status across 320px, 480px, and 640px widths without overflow; retain keyboard focus visibility, forced-colors behavior, and reduced-motion behavior. Then pause for the human visual/accessibility breakpoint to verify the real panel below the board and approve or identify a bounded correction. **Focused proof:** component assertions plus the constrained responsive, focus, forced-colors, reduced-motion, and no-overflow checks available in the approved browser evidence. **Escalate:** accessibility or responsive requirements that need global/shared changes, a new token, or an unsettled visual/product decision.
3. **pending** - **Storybook and browser evidence.** Add or update stories for empty, active, action-disabled, promotion, terminal, copy-feedback, and constrained-width states without changing product contracts. Extend only `tests/e2e/viewer-branch.spec.ts` for exact FEN copy/status/names/mechanics, no-overflow, responsive, and accessibility assertions; retain the special-move regression in `tests/e2e/viewer-branch-stage4.spec.ts` as proof-only evidence. **Focused proof:** `npm.cmd run build-storybook --prefix frontend`; `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`; `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`. **Escalate:** a required change outside the approved e2e spec, a browser failure caused by an excluded composition/contract area, or accessibility proof requiring ownership/global/shared changes.
4. **pending** - **Independent validation and closeout.** Run focused Vitest, frontend build/lint/Prettier/size checks, Storybook proof, targeted Playwright proof, and the full read-only repository check. Obtain fresh Quality validation and human acceptance, then inspect Git changes once for the final scope audit; report unrelated changes rather than absorbing them. **Focused proof:** `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/InteractiveBoardAdapter.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`; `npm.cmd run build --prefix frontend`; `npm.cmd run lint --prefix frontend`; `frontend/node_modules/.bin/prettier.cmd --check frontend`; `.venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`; `npm.cmd run build-storybook --prefix frontend`; `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`; `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`; `.venv/Scripts/python.exe scripts/check.py`; final `git diff --check` and scope audit. **Breakpoint:** fresh Quality and human acceptance before marking done. **Escalate:** any failed repair boundary, acceptance failure, or need to modify an excluded area; never commit or push.

## Progress and decisions

- **Stage 1:** pending - proof: focused component and viewer-branch tests; breakpoint: none, subject to the fresh-baseline precondition.
- **Stage 2:** pending - proof: responsive/accessibility browser evidence; breakpoint: human visual/accessibility acceptance of the real panel.
- **Stage 3:** pending - proof: Storybook build/test and targeted Playwright suites; breakpoint: none unless approved evidence exposes a settled-scope conflict.
- **Stage 4:** pending - proof: independent Quality validation, full read-only check suite, and final scope audit; breakpoint: human acceptance and closeout.

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
