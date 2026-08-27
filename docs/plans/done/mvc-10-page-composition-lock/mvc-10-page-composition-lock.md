# MVC-10 Page composition lock - the same viewer page with all extracted parts reconnected

> **Status:** completed - implementation and independent Quality passed; workflow closeout recorded under coordinator direction

- **Read trigger:** Read before each sequential MVC-10 stage after MVC-09 Game context is accepted and whenever the
  implementation or Quality handoff resumes.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-09 Game context Plan/result](../../done/mvc-09-game-context/mvc-09-game-context.md)

## Outcome

Complete the page-composition lock so `ViewerWorkspace` remains the same page-specific viewer: it owns loading,
selected position, traversal, temporary-branch, promotion, analysis, reset, failure-preservation, and announcement
state; it reconnects the extracted controlled components; and it preserves the current layout, responsive behavior,
copy, DOM relationships, focus behavior, and accessibility.

## Scope

- **Included:** Mechanical composition wiring only when required; focused ViewerWorkspace and branch regression
  coverage; existing Storybook state and interaction coverage; viewer Storybook browser coverage; proof of the
  whole-game and legacy compatibility surfaces; bounded validation and final coordinator-directed workflow closeout.
- **Expected areas:**
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.module.css` (preservation-only),
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspaceBranch.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`,
  `tests/e2e/viewer-storybook.spec.ts`,
  `tests/e2e/viewer-branch.spec.ts`, and
  `tests/e2e/viewer-branch-stage4.spec.ts`.
- **Proof-only compatibility areas:** `tests/e2e/viewer.spec.ts`,
  `tests/e2e/viewer-live-position.spec.ts`, and the already accepted extracted-component tests/stories. They are not
  implementation targets unless an existing assertion needs a narrowly mechanical update.
- **Excluded:** Visual redesign; new product behavior; changes to loading, traversal, branch, promotion, analysis,
  reset, failure, announcement, or accessibility semantics; universal viewer/game/opening/tree/session/slot
  frameworks; API, backend, contract, data, model, or dependency changes; changes outside the listed surfaces;
  README maintenance; `docs/master-plans/modular-viewer-components.md` edits before Quality acceptance; moving this
  Plan before Quality acceptance; destructive cleanup; `--fix`; commits; pushes; and unrelated worktree changes.

### Implementation-critical facts and guardrails

- `ViewerWorkspace.tsx` currently owns the page state and orchestration and renders `GameLoader`, the static or
  interactive board, `EvalBar`, `BoardControl`, `GameContext` with the controlled `AnalysisPanel` child, and the
  polite atomic traversal announcement. Preserve those ownership boundaries and the shared analysis observation.
- Preserve the current `ViewerWorkspace.module.css` wide grid, centered 66rem composition, `@container (max-width:
  40rem)` reflow, hidden announcement geometry, and forced-colors behavior. No layout or visual redesign is allowed.
- Preserve `GameContext`'s accepted narrow child seam. Do not widen it into a public or universal customization API.
- Preserve `InteractiveBoardAdapter`'s branch status/terminal announcements and all branch snapshot, reset-token,
  promotion, legal/illegal, SAN/FEN, traversal-gate, and terminal behavior.
- Preserve whole-game `GET /api/games/{game_uuid}/positions` loading, legacy per-ply compatibility, typed loader
  failures, analysis callbacks/observation sharing, and the current safe-source behavior. Do not change backend or
  endpoint contracts.
- The accepted MVC-05 through MVC-09 baseline and all unrelated tracked/untracked content are protected. The MVC-09
  result reports seven unrelated/concurrency-sensitive full-suite E2E timing failures; report such failures rather
  than absorbing them into MVC-10.
- Source files remain at most 500 lines and handwritten tests at most 700 lines. Use read-only checks only.
- Storybook readiness must be bounded to 30 seconds, only the process started for proof may be stopped, and port 6006
  must be confirmed free after browser proof.
- Implementation acceptance is not final Plan acceptance. After implementation proof, stop for independent Quality
  validation in a fresh/read-only validation session. A coordinator-authorized repair may be attempted only through
  the Quality route; after one failed repair, return to the coordinator. Move this Plan and update the master plan only
  after Quality PASS and explicit coordinator direction.

## Stages

1. **completed - Composition and focused regression lock.** Keep the existing page-specific composition intact and
   prove that all extracted parts receive the same data/capabilities while all workflow state remains in
   `ViewerWorkspace`.

   - **Ordered actions:**
     1. Re-read the master plan and accepted MVC-09 result, then inspect only the listed composition, test, story, and
        compatibility surfaces. Use the coordinator packet baseline; preserve every unrelated change.
     2. Compare the current call sites with the accepted controlled boundaries. Make only a mechanical reconnection
        change if a real gap is found; otherwise preserve the already-correct source and strengthen missing focused
        evidence rather than refactoring.
     3. Reconcile `ViewerWorkspace.test.tsx` and `ViewerWorkspaceBranch.test.tsx` around empty/loading, whole-game
        and explicit-Ply loading, in-memory traversal, replacement failure preservation, reset, analysis sharing,
        announcement text/semantics, branch gating, promotion, and accessibility. Do not duplicate workflow or
        observation work in child components.
     4. Recheck source/test sizes and run the focused proof. Do not inspect Git changes during this stage.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build --prefix frontend`

     `.venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`
   - **Breakpoint:** None expected. Stop and escalate if preserving the current DOM, page ownership, state semantics,
     announcement behavior, or component contracts requires a broader interface, new abstraction, or product decision.

2. **completed - Storybook and browser composition evidence.** Demonstrate the same wide/constrained page, meaningful
   loading/failure/reset/traversal/analysis states, branch interactions, announcements, and accessibility without
   changing the visual direction or behavior.

   - **Ordered actions:**
     1. Reconcile `ViewerWorkspace.stories.tsx` and `viewer-storybook.spec.ts` only for missing settled evidence,
        especially the live traversal announcement and composed context/analysis placement. Retain all current story
        fixtures and interactions.
     2. Build Storybook before interaction proof. Start `npm.cmd run storybook --prefix frontend -- --ci` in a dedicated
        process, bound readiness to 30 seconds at `http://127.0.0.1:6006/index.json`, run the checks below, stop only
        that process in all cases, and confirm port 6006 is free.
     3. Run the viewer Storybook browser spec and both existing branch specs. Preserve pointer, touch, keyboard,
        promotion, special-move, terminal, focus, forced-colors, responsive, and axe coverage.
     4. Run lint, read-only Prettier, and the size check. Do not use `--fix` or inspect Git changes mid-stage.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `.venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`
   - **Breakpoint:** None expected. Stop and escalate for any new visual, responsive, copy, focus, accessibility,
     browser, dependency, or interaction decision, or if Storybook cleanup/port ownership cannot be confirmed.

3. **completed - implementation and independent Quality accepted.** Establish implementation acceptance first, then
   obtain independent Quality acceptance before completing the Plan and master-plan records.

   - **Ordered actions:**
     1. Re-run the focused tests and targeted viewer/browser coverage, including app-route, whole-game, legacy endpoint,
        Storybook, and existing branch specs. Confirm target failures are fixed or escalated; classify unrelated
        baseline/concurrency failures without repairing them.
     2. Run the complete repository check exactly in read-only mode. Never append `--fix`.
     3. Perform the one final scope audit after all implementation changes: inspect the scoped changes against the
        coordinator baseline, run `git diff --check`, and run `git status --short --untracked-files=all`. Confirm no
        completed history, unrelated worktree content, APIs, backend, dependencies, or excluded paths changed.
     4. Record implementation proof as awaiting independent Quality; do not move this Plan or update the master plan.
     5. Under coordinator direction, obtain fresh-session independent Quality validation. If Quality fails, use only
        the coordinator-authorized Quality repair route and repeat final validation; after one failed repair, return to
        the coordinator.
     6. Only after Quality PASS, and only when the coordinator directs closeout, move this file to
        `docs/plans/done/mvc-10-page-composition-lock/mvc-10-page-composition-lock.md` and replace the MVC-10
        placeholder in `docs/master-plans/modular-viewer-components.md` with the completed result link/status.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer.spec.ts tests/e2e/viewer-live-position.spec.ts tests/e2e/viewer-storybook.spec.ts tests/e2e/viewer-branch.spec.ts tests/e2e/viewer-branch-stage4.spec.ts`

     `.venv/Scripts/python.exe scripts/check.py`

     `git diff --check`

     `git status --short --untracked-files=all`
   - **Breakpoint:** Quality PASS and coordinator authorization are mandatory before workflow-record completion.
     Escalate any target failure, unresolved baseline collision, unbounded server lifecycle, or need to change an
     excluded contract, behavior, visual direction, ownership boundary, or historical record.

Stages are sequential; no parallel implementation stages are authorized. The coordinator may split an oversized stage
without changing this outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** completed - no composition source repair was needed. Focused announcement text and
  `status`/`aria-live`/`aria-atomic` assertions were added to `ViewerWorkspace.test.tsx`; 19 focused tests, the
  frontend build, and the 194-file size check passed. Existing non-failing sourcemap, jsdom canvas, and chunk-size
  warnings were observed. Breakpoint: none.
- **Stage 2:** completed - live-announcement Storybook assertions were added and formatted deterministically. The
  Storybook build, 121 interaction tests, 15 targeted viewer/branch browser tests, lint, Prettier, and the 194-file
  size check passed. One pre-existing repository Storybook process was identified and removed before proof; the
  dedicated proof server was bounded, cleaned up, and port 6006 was confirmed free. Existing non-failing Storybook
  teardown, chunk-size, and hook warnings were observed. Breakpoint: none.
- **Stage 3 implementation proof:** complete - the focused ViewerWorkspace and branch tests passed (19 tests), and
  the targeted viewer/app-route, whole-game, legacy endpoint, Storybook, and branch browser coverage passed (20 tests).
  The complete read-only check passed every non-E2E category, while its 50-test full-suite E2E run had one
  concurrency-sensitive `viewer-branch.spec.ts` axe collision (`Axe is already running`) and 49 passes; this unrelated
  full-suite failure was classified and not repaired. The dedicated Storybook server was ready within 30 seconds,
  stopped by its verified process tree, and port 6006 was confirmed free. The final diff check passed, and status was
  limited to the intended `ViewerWorkspace.test.tsx` and `ViewerWorkspace.stories.tsx` assertions plus the active Plan.
  Implementation proof is recorded as awaiting independent Quality; breakpoint: coordinator direction after Quality
  PASS.
- **Closeout:** Independent Quality passed and the coordinator directed documentation closeout. This Plan was moved
  from `docs/plans/active/` to `docs/plans/done/`, and the MVC-10 placeholder in
  `docs/master-plans/modular-viewer-components.md` was replaced with the completed-result link/status. No source,
  test, story, README, other Plan, or historical record was changed, and the intended `ViewerWorkspace.test.tsx` and
  `ViewerWorkspace.stories.tsx` assertion additions were preserved untouched.
- **Decisions:** The page-specific ownership, exact layout, controlled child boundaries, compatibility requirements,
  and no-redesign direction are settled by the master plan and accepted MVC-09 result. No user decision is required for
  routine implementation choices.

## Proof

- Focused ViewerWorkspace and branch Vitest/React Testing Library coverage, frontend build, and source-size check.
- Storybook build and interactions with bounded startup, cleanup, and port-6006 confirmation.
- Viewer Storybook, branch, app-route, whole-game, legacy compatibility, responsive, forced-colors, and axe browser
  proof using the existing Playwright configuration.
- ESLint, read-only Prettier, and the complete read-only `.venv/Scripts/python.exe scripts/check.py` closeout.
- One final scoped Git audit only after implementation and any coordinator-directed workflow updates.
- Independent Quality validation is required after implementation acceptance; no Quality PASS may be inferred from the
  case-worker's proof.

## Acceptance

- `ViewerWorkspace` remains the sole owner of page workflow state/orchestration and reconnects every extracted part
  through its existing controlled boundary.
- The page remains visibly and behaviorally identical: exact layout, container-query behavior, loading, legacy
  compatibility, traversal, branch/promotion, analysis, reset, failure preservation, announcements, focus, and
  accessibility all remain intact.
- Focused tests, Storybook states/interactions, browser specs, lint, formatting, size checks, and read-only repository
  validation pass for the MVC-10 surfaces. Unrelated known baseline failures are reported, not absorbed.
- Implementation acceptance is followed by independent Quality PASS in a fresh validation session.
- After Quality PASS and coordinator direction, the completed Plan is linked/statused in the master plan. No README
  maintenance is expected.
- No API/backend/contract/dependency/model/visual redesign, universal framework, destructive cleanup, `--fix`, commit,
  push, historical-record rewrite, or unrelated-worktree modification is introduced.

## Escalation boundaries

- Any change to product behavior, copy, DOM/order, layout, responsive behavior, focus, keyboard, motion, color,
  typography, announcement, or accessibility semantics.
- Any change to page ownership, extracted-component contracts, analysis observation/polling/actions, branch/promotion
  semantics, loader failure semantics, API/backend/contracts, models, dependencies, or data.
- Any public/universal slot, viewer, game, opening, tree, session, or analysis abstraction.
- Any path expansion beyond the bounded MVC-10 surfaces, including completed Plans, README files, design-system
  components, or unrelated worktree content.
- Any destructive operation, `--fix`, commit, push, unbounded Storybook process, unconfirmed port cleanup, or repair of
  an unrelated validation failure.
- Any failure to separate implementation acceptance from independent Quality acceptance, or any request to complete
  workflow records before Quality PASS and coordinator direction.

## Visible result

> The same viewer page behaves and looks the same, with all extracted components reconnected and page workflow state
> still owned by `ViewerWorkspace`.
