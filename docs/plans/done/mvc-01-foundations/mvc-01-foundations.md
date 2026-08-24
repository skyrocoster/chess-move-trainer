# MVC-01 Foundations - the unchanged viewer rests on separate chess workflow models

> **Status:** done - MVC-01 accepted after the Stage 3 regression lock and fresh Quality PASS.

- **Read trigger:** Read after the approved modular-viewer-components direction and before each sequential MVC-01 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md)

## Outcome

The current position viewer remains observably unchanged while its internal data boundaries use small shared chess
primitives and separate game, temporary-branch, and analysis workflow models. Existing whole-game, legacy per-ply,
evaluation, branch, accessibility, and viewer semantics remain intact.

## Scope

- **Included:** Type-only foundation seams for FEN/Ply/SAN and side values; a bounded game/position model;
  a separate temporary-branch model; preservation of the existing `analysisApi.ts` and `analysisState.ts`
  API/workflow seams; consumer classification for `stage1GameTypes.ts` and `positionLookup.ts`; compatibility
  exports while consumers are migrated; and focused regression coverage for the protected legacy per-ply client.
- **Expected areas:**
  `frontend/src/features/viewer/chessPrimitives.ts`, `gameModel.ts`, `temporaryBranchModel.ts`,
  `stage1GameTypes.ts`, `positionApi.ts`, `analysisApi.ts`, `analysisState.ts`, `GameLoader.tsx`,
  `GameContext.tsx`, `ViewerWorkspace.tsx`, `AnalysisPanel.tsx`, `positionApi.test.ts`, and
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.tsx`; existing viewer/board tests and stories,
  the named viewer/branch browser specs, and the backend position/evaluation contract tests are evidence surfaces.
- **Excluded:** Component extraction or decoupling, JSX/CSS/DOM redesign, visual or interaction changes, backend
  or endpoint changes, payload/error-contract changes, database work, new dependencies, universal game/opening/tree/
  session models, speculative abstractions, destructive cleanup, historical-record changes, commits, pushes, and
  unrelated worktree changes. Stage 1 does not retire `positionLookup.ts`, fixtures, or legacy mocks.

## Stages

1. **pending - Foundations and consumer classification (immediate Stage 1).**
   - **Ordered actions:** Add the type-only `chessPrimitives.ts`, `gameModel.ts`, and
     `temporaryBranchModel.ts` seams. Keep `stage1GameTypes.ts` as a compatibility/fixture bridge while production
     consumers move to the bounded game model. Move `BranchMove` and `BranchSnapshot` type ownership without changing
     the interactive adapter contract. Preserve `fetchGame`, `fetchPosition`, all analysis client methods,
     validation, endpoint strings, typed failures, and runtime state transitions. Classify every consumer before any
     legacy removal, and add the protected legacy per-ply client regression coverage.
   - **Stage 1 implementation paths:**
     `frontend/src/features/viewer/chessPrimitives.ts`, `gameModel.ts`, `temporaryBranchModel.ts`,
     `stage1GameTypes.ts`, `positionApi.ts`, `analysisApi.ts`, `analysisState.ts`, `GameLoader.tsx`,
     `GameContext.tsx`, `ViewerWorkspace.tsx`, `AnalysisPanel.tsx`, `positionApi.test.ts`, and
     `frontend/src/features/board-adapter/InteractiveBoardAdapter.tsx`. Existing viewer/board tests, stories,
     `positionLookup.ts`, backend contract files, and the named E2E files are read-only evidence for this stage.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer src/features/board-adapter/BoardAdapter.test.tsx src/features/board-adapter/InteractiveBoardAdapter.test.tsx`;
     `npm.cmd run build --prefix frontend`;
     `npm.cmd run build-storybook --prefix frontend`;
     `npm.cmd run lint --prefix frontend`;
     `frontend\node_modules\.bin\prettier.cmd --check frontend`;
     `.venv\Scripts\python.exe -m pytest backend/tests/features/positions backend/tests/features/evaluation -q`;
     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-live-position.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-branch.spec.ts tests\e2e\viewer-branch-stage4.spec.ts`.
   - **Breakpoint:** None is expected because this is type/model-only. Any visual, interaction, accessibility,
     ownership, runtime, or contract difference is an escalation rather than an accepted Stage 1 result.
   - **Escalate if:** A consumer cannot be classified, a type move needs runtime conversion, the legacy per-ply
     contract cannot be regression-tested, or preserving existing worktree edits requires changing behavior.
2. **pending - Proven legacy cleanup.**
   - **Ordered actions:** After Stage 1 proof, migrate fixture/test imports to a fixture-only surface and move
     protected per-ply result types into the API seam if needed. Remove only mocks, default stubs, adapters, or files
     proven to have no production or genuinely reusable consumer. Retain production contracts, warning/error states,
     fixtures still required by Storybook, and all backend routes.
   - **Focused proof:** Run the bounded repository search for `positionLookup`, `fetchPosition`, `stage1GameTypes`,
     `Stage1*`, and the legacy mock names; rerun the focused frontend suite, positions/evaluation pytest suites,
     frontend build, and frontend lint. Re-run the targeted viewer and branch Playwright command from Stage 1.
   - **Breakpoint:** Cleanup is accepted only when consumer classification is complete and the protected legacy
     per-ply tests remain green; no visual decision is expected.
   - **Escalate if:** Any apparently unused symbol is a production contract, reusable state/variant, required story
     fixture, or removal would alter an endpoint, error, accessibility, or observable viewer behavior.
3. **done - Regression lock and MVC-01 acceptance.**
   - **Ordered actions:** Reconfirm the whole-game and legacy position routes, evaluation observation/enqueue/status,
     loading and failure preservation, traversal, temporary-branch lifecycle, analysis targeting, announcements,
     responsive composition, accessibility, and Storybook states. Review the scoped diff and confirm unrelated paths
     and completed historical records were not changed.
   - **Focused proof:** `.venv\Scripts\python.exe scripts\check.py` in read-only mode; `git diff --check`; and a
     final `git status --short`/scoped worktree review. Never use `scripts/check.py --fix` for this Plan.
   - **Breakpoint:** Coordinator acceptance follows green proof and confirmation that the current viewer is unchanged
     relative to the Stage 1 starting worktree. There is no redesign or visual-direction gate.
   - **Escalate if:** Full proof exposes an unrelated baseline failure, requires `--fix`, or completion would require
     absorbing unrelated changes or modifying historical records.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new decision.

## Progress and decisions

- **Stage 1:** accepted - independently PASSed: focused Vitest (11 files/95 tests), frontend build, Storybook build
  (documented non-fatal Windows libuv teardown only), ESLint, Prettier, backend positions/evaluation (75 tests),
  targeted viewer/branch Playwright (20 tests including en-passant), `git diff --check`, and scope audit. Established
  type-only chess/game/temporary-branch seams, preserved analysis separation and all runtime/API contracts, and added
  legacy per-ply coverage. Authorized proof-debt repair only narrowed Storybook mock literals and aligned three loaded
  interactive-board E2E role expectations with the authoritative existing `group`; no runtime behavior changed.
- **Stage 2:** independently accepted PASS - consumer classification was complete: `positionLookup.ts` had only the `positionApi.ts` type
  consumer, so its protected result types moved into `positionApi.ts` and its mocks/default stub were retired;
  `stage1GameTypes.ts` had only fixture/test/story consumers, which now use the fixture-only `viewerFixtures.ts`
  surface and `Game` model types. The required Storybook `Stage1Story.module.css` fixture and named E2E local UUID
  fixture remain. Protected `fetchPosition`, warning/error states, reusable variants, backend routes, and viewer
  behavior were retained.
  - **Proof:** bounded search for `positionLookup`, `fetchPosition`, `stage1GameTypes`, `Stage1*`, and legacy mock
    names; focused frontend Vitest (11 files/95 tests), positions/evaluation pytest (75 tests), frontend build,
    frontend lint, targeted viewer/branch Playwright (20 tests); focused Prettier check; and `git diff --check`.
- **Stage 3:** accepted DONE - coordinator accepted MVC-01 after fresh Quality PASS. The mandatory read-only
  `.venv\Scripts\python.exe scripts\check.py` ran every step: schema/workflow contracts, Ruff lint,
  Python/workflow/frontend tests, ESLint, Prettier, frontend and Storybook builds, size, Storybook interaction/a11y,
  and targeted viewer/branch browser behavior all passed. The repository check exited 1 only for five pre-existing
  unrelated `experiments\prototypes\` Ruff-format files and one board-adapter Storybook axe timeout under parallel
  load; that E2E passed in isolation. Neither issue was repaired. Final diff/scope/contract/behavior audit passed;
  no artifacts or unrelated changes were absorbed.
  - **Proof/decision:** `git diff --check` passed; final `git status --short` and scoped review showed only the
    accepted Stage 1/2 worktree plus this Plan move. No `--fix`, product edits, or proof reruns were performed.

## Proof

- Preserve the exact whole-game `GET /api/games/{game_uuid}/positions` contract with optional `ply` and the legacy
  `GET /api/games/{game_uuid}/positions/{ply}` contract; preserve typed failures and all evaluation observation,
  enqueue, and status behavior.
- Run the focused viewer/board Vitest suite, backend positions/evaluation pytest suites, frontend build/lint,
  Prettier check, Storybook build, and the targeted viewer/branch Playwright specs listed in Stage 1.
- Run the full read-only `.venv\Scripts\python.exe scripts\check.py` only at Stage 3 closeout; do not use `--fix`.
- Stage 3 closeout recorded the fresh Quality PASS above; the two unrelated repository-level blockers remain
  documented and outside MVC-01 scope.

## Escalation boundaries

- Any new product, visual, interaction, accessibility, API, endpoint, payload, error, data, database, dependency,
  destructive, ownership, universal-model, or acceptance decision.
- Any need to decouple visible components, change `ViewerWorkspace` ownership, alter JSX/CSS/DOM semantics, or change
  the current accessibility edits in `InteractiveBoardAdapter.tsx`, its tests, or related viewer/browser proof.
- Any inability to preserve the whole-game route, legacy per-ply route, typed payloads/errors, `AnalysisClient`
  behavior, analysis state transitions, branch semantics, or current viewer behavior.
- Any ambiguous consumer classification, removal of a protected production/reusable state, unrelated failure,
  historical-record edit, formatter fix, commit, or push.

## Visible result

> **Accepted visible result:** At `/viewer`, loading, traversal, branching, analysis, errors, announcements, accessibility, and responsive behavior look and behave the same while game, branch, and analysis data remain separate internally.
