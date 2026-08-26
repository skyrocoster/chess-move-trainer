# MVC-06 Navigation controls - the same toolbar with page-owned navigation capabilities

> **Status:** done - all execution stages and independent validation accepted

- **Read trigger:** Read after MVC-05 Interactive branch board is accepted and before each sequential MVC-06 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-05 Interactive branch board Plan/result](../../done/mvc-05-interactive-branch-board/mvc-05-interactive-branch-board.md)

## Outcome

Keep the current navigation toolbar visually and behaviorally identical while refining `BoardControl` into a
capability/callback-based visible boundary. `ViewerWorkspace` retains timeline, loading, temporary-branch, boundary,
announcement, and traversal ownership; `BoardControl` owns no timeline state or ply-boundary arithmetic.

## Scope

- **Included:** The smallest explicit capability and callback boundary supported by the current call site; mechanical
  page reconnection; preservation of toolbar semantics, labels, icons, native disabled behavior, focus movement,
  empty state, loading gate, temporary-branch gate, and existing callbacks; focused tests; Storybook states and
  interactions; viewer navigation integration assertions; and read-only proof. The module CSS is preservation-only and
  must not receive visual-direction changes.
- **Expected areas:**
  `frontend/src/features/viewer/BoardControl.tsx`,
  `frontend/src/features/viewer/BoardControl.module.css`,
  `frontend/src/features/viewer/BoardControl.test.tsx`,
  `frontend/src/features/viewer/BoardControl.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx` only for mechanical capability derivation and reconnection,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`, and
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx` only for navigation assertions.
- **Excluded:** Playback, skip, flip, or any new navigation behavior; visual, layout, typography, color, motion,
  focus, keyboard, label, or accessibility-direction changes; branch workflow or chess semantics; backend/API,
  payload, typed-error, frontend production contract, data, or dependency changes; universal viewer/game/opening/
  tree/session abstractions; speculative customization; README maintenance; destructive cleanup; edits to completed
  Plans, historical records, or the master plan; absorption or reset of unrelated worktree changes;
  `scripts/check.py --fix`; commits; and pushes.

## Implementation-critical facts and worktree guardrails

- `BoardControl` currently receives `currentPly` and `finalPly`, derives `hasGame`, and computes disabled states in
  `BoardControl.tsx:6-25`. The controlled boundary must replace numeric timeline inputs with explicit capabilities and
  retain the two existing direction callbacks without adding public customization.
- `ViewerWorkspace` already owns `currentIndex`, game positions, loading state, branch state, announcements, and the
  `handlePrevious`/`handleNext` traversal handlers in `ViewerWorkspace.tsx:81-94,306-332`. It must derive the
  capabilities, including loading/branch gates and page-owned boundaries, and remain the single owner of traversal.
- Preserve the existing `Toolbar.Root`/`Toolbar.Button` structure, `aria-label` values, `focusableWhenDisabled={false}`,
  icon/label order, empty copy, callback intent, and all CSS geometry, container-query, focus, and forced-colors rules.
- The required `BoardControl` files and `ViewerWorkspace.test.tsx` were clean at assessment. `ViewerWorkspace.tsx`
  and `ViewerWorkspace.stories.tsx` already contain retained MVC-05 changes and are overlapping baseline surfaces; only
  the approved MVC-06 navigation wiring and assertions may be reconciled.
- Preserve the untracked completed MVC-05 Plan, the MVC-05 master-plan link, current interactive-board/branch changes,
  completed Plans, historical records, and every unrelated worktree change. Do not reset or reformat them.
- Known unrelated worktree material includes workflow/agent files, `AGENTS.md`, README formatting, check-script and
  check-helper changes, test reorganizations, and `experiments/mock-ups/*`. README maintenance is not expected or
  authorized for this slice.

## Stages

1. **complete - Controlled capability boundary and page reconnection.** Moved navigation capability ownership to
   `ViewerWorkspace` while preserving the current rendered toolbar and traversal behavior.

   - **Ordered actions:**
     1. Re-read the master plan and accepted MVC-05 result, then inspect the current `BoardControl` props and symbols,
        its CSS/test/story coverage, the `ViewerWorkspace` call site and traversal handlers, and the current scoped
        worktree state. Preserve all MVC-05 and unrelated changes.
     2. Define only the minimum call-site-derived visible boundary: explicit display/capability inputs and the existing
        Previous/Next callbacks. Remove timeline-valued visible inputs and do not add public customization or a
        universal navigation abstraction.
     3. Keep `ViewerWorkspace` responsible for current position/index, game availability, loading and temporary-branch
        gates, boundary capability derivation, announcements, traversal guards, branch discard behavior, and existing
        callbacks. Do not change traversal, loading, branch, or announcement semantics.
     4. Refine `BoardControl.tsx` to render the same empty state and toolbar from capabilities and callbacks without
        timeline state or ply-boundary arithmetic. Preserve the existing DOM structure, labels, icons, disabled
        behavior, focus movement, and callback intent. Inspect `BoardControl.module.css` and leave its visual rules
        unchanged unless a mechanically necessary, non-visual adjustment is proven.
     5. Reconcile `BoardControl.test.tsx` and the navigation assertions in `ViewerWorkspace.test.tsx` so they prove
        explicit capabilities while retaining empty, initial/final, enabled callback, loading, temporary-branch,
        in-memory traversal, loading-gate, and focus-preservation behavior.
     6. Inspect the scoped diff and confirm that no MVC-05 branch behavior, public contract, CSS direction, historical
        record, README, or unrelated worktree change was absorbed.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate if the capability boundary requires a new navigation rule,
     changed callback/public API, changed empty/loading/branch/focus/accessibility behavior, CSS or visual decision,
     changed MVC-05 semantics, or ownership outside the approved page-specific composition.

2. **complete - Storybook states and viewer navigation integration proof.** Preserved the real Storybook toolbar and
   workspace navigation presentation while proving the new capability boundary through existing interactions.

   - **Ordered actions:**
     1. Reconcile `BoardControl.stories.tsx` with explicit capability inputs while retaining Empty, initial/final,
        intermediate callback, Loading, Constrained, and KeyboardToolbar states. Ensure keyboard Enter, ArrowRight,
        Space, disabled, and label behavior remain covered; add only the minimum temporary-branch capability state
        coverage needed to prove the existing gate.
     2. Retain or refine the navigation assertions in `ViewerWorkspace.stories.tsx` for initial, intermediate, final,
        loading, replacement failure, and temporary-branch gating. Do not redesign or rewrite the existing MVC-05
        branch stories.
     3. Build Storybook before interaction proof. Start the repository Storybook server with
        `npm.cmd run storybook --prefix frontend -- --ci --port 6006` under a bounded runner, poll a responsive Storybook
        or iframe URL for no more than 30 seconds, and treat a responsive HTTP redirect as ready. If startup does not
        become responsive within 30 seconds, stop and escalate rather than waiting longer.
     4. Run Storybook interaction and viewer browser proof with explicit bounded command timeouts. Always stop only the
        server started for this proof in cleanup/finally handling, then confirm port 6006 is free. Do not kill an
        unrelated process occupying the port; report and escalate instead.
     5. Run lint and formatting checks without write-mode formatting, then inspect the diff for unchanged CSS and
        preserved Storybook/browser expectations.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend\node_modules\.bin\prettier.cmd --check frontend`

      `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-storybook.spec.ts`

      Storybook startup health is bounded to 30 seconds; each Storybook, test-runner, and browser command uses a
      300-second (300000 ms) runner timeout and must perform mandatory server cleanup and port-6006 confirmation. A
      responsive redirect counts as ready.
   - **Breakpoint:** None expected. Stop and escalate rather than choosing new copy, layout, focus treatment,
     accessibility semantics, browser expectation, primitive, dependency, visual direction, or navigation behavior.

3. **complete - Read-only closeout and worktree preservation.** Confirmed the page-owned capability wiring is behaviorally
   invisible, then complete bounded independent validation without repairing unrelated failures.

   - **Ordered actions:**
     1. Re-run the focused component/workspace tests, frontend build, Storybook build and interactions, lint, formatting,
        and viewer browser proof from the preceding stages.
     2. Run the full repository check exactly as
        `.venv\Scripts\python.exe scripts\check.py` in read-only mode with an explicit bounded command timeout of
        600 seconds (600000 ms), sufficient for the suite. Never append `--fix`.
     3. Inspect `git diff --check`, the scoped diff, and complete worktree status. Confirm that BoardControl CSS,
        labels, focus movement, empty/loading/branch behavior, completed MVC-05 changes, completed Plans, historical
        records, and unrelated worktree content remain preserved.
     4. Report unrelated baseline failures without repairing, formatting, resetting, staging, committing, or pushing.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend\node_modules\.bin\prettier.cmd --check frontend`

     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-storybook.spec.ts`
   - **Full closeout proof:**
     `.venv\Scripts\python.exe scripts\check.py` — read-only, runner timeout exactly bounded at 600 seconds
     (600000 ms), never `--fix`.

     `git diff --check`

     `git status --short --untracked-files=all`
   - **Breakpoint:** None expected. Stop and escalate if acceptance requires any behavior, ownership, contract,
     dependency, destructive, historical-record, unrelated-worktree, README, or validation decision not settled by
     this Plan. Storybook/browser servers must be cleaned up and port 6006 confirmed free before closeout.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - `BoardControl` now consumes `hasGame`, `canGoPrevious`, and `canGoNext` plus the existing
  callbacks; `ViewerWorkspace` owns game, boundary, loading, and branch capability derivation. Focused tests passed
  18/18, the frontend build passed with the retained chunk warning, and `git diff --check` passed with normal
  line-ending warnings. A coordinator-approved mechanical story-argument migration was required for the Stage 1
  TypeScript build; no Stage 2 interactions were added.
- **Stage 2:** complete - Storybook capability, boundary, loading, temporary-branch, label, disabled-state, and
  navigation assertions passed 21 suites/102 tests. The Storybook build completed with the documented non-fatal
  Windows teardown assertion; viewer Playwright passed 2/2 in 15.4 seconds using the Git-Bash-normalized command;
  lint passed with one retained warning; targeted Prettier formatting of the two approved Stage 1 files was followed
  by a clean frontend Prettier check, focused tests passing 18/18, and `git diff --check`. PowerShell was not used,
  Playwright managed its configured servers, and port 6006 had no listener afterward.
- **Stage 3:** complete - focused tests passed 18/18; frontend and Storybook builds passed; Storybook passed 21
  suites/102 tests; lint passed with one retained warning; Prettier passed; viewer Playwright passed 2/2; and
  `git diff --check` passed. The 600-second-bounded full read-only check completed in 221 seconds with 47/48 E2E
  tests passing; the sole failure was an unrelated timeout in `board-adapter-storybook.spec.ts`, which was reported
  and not repaired or absorbed. Worktree status remained unchanged, PowerShell was not used, and port 6006 had no
  listener after cleanup.
- **Decisions:** MVC-05 is an accepted prerequisite. The toolbar is a no-redesign controlled boundary; page-owned
  capabilities preserve loading and temporary-branch gates; CSS is preservation-only; README maintenance is not
  expected or authorized; no new navigation, model, endpoint, dependency, or historical-record change is approved.

## Proof

- Focused behavior and page reconnection:
  `npm.cmd run test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
- Frontend type/build proof: `npm.cmd run build --prefix frontend`
- Storybook build and interaction proof:
  `npm.cmd run build-storybook --prefix frontend` and
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`
- Lint and formatting proof:
  `npm.cmd run lint --prefix frontend` and
  `frontend\node_modules\.bin\prettier.cmd --check frontend`
- Viewer browser proof:
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer-storybook.spec.ts`
  - Storybook/browser operational rules: health startup maximum 30 seconds; a responsive redirect is ready; every
  Storybook/test-runner/browser command uses a 300-second (300000 ms) bounded timeout; cleanup is mandatory; and port
  6006 must be confirmed free afterward.
- Full read-only closeout:
  `.venv\Scripts\python.exe scripts\check.py` with a 600-second (600000 ms) command timeout, plus
  `git diff --check` and `git status --short --untracked-files=all`. `--fix` is prohibited.
- Independent Quality validation passed using Git Bash only: focused MVC-06 Vitest passed 18/18 in 14.37 seconds,
  viewer Playwright passed 2/2 in 16.9 seconds, and `git diff --check` passed. Playwright managed and cleaned up its
  configured server; ports 6006 and 5666 had no listeners afterward. The unrelated full-check Board Adapter timeout
  remained separately reported and was not rerun, repaired, or absorbed.

## Acceptance

- `BoardControl` renders the same toolbar, empty state, labels, icons, disabled states, callback behavior, focus
  movement, constrained presentation, and accessibility semantics while receiving explicit capabilities rather than
  timeline values.
- `BoardControl` owns no timeline state or ply-boundary arithmetic, and its module CSS remains visually unchanged.
- `ViewerWorkspace` remains the owner of timeline/current-position state, boundary capability derivation, loading and
  temporary-branch gates, traversal handlers, branch discard behavior, and announcements.
- Existing empty, loading, initial, intermediate, final, replacement-failure, and temporary-branch navigation
  behavior remains unchanged; no playback, skip, flip, or new navigation behavior appears.
- Focused tests, Storybook interactions, viewer browser proof, lint, formatting, frontend build, and the full
  read-only repository check pass. Unrelated baseline failures are reported rather than absorbed.
- Storybook/browser servers are cleaned up and port 6006 is confirmed free; completed MVC-05 work, historical
  records, and unrelated worktree changes remain untouched.

## Escalation boundaries

- Any new product, navigation, visual, layout, typography, color, motion, focus, keyboard, label, accessibility,
  browser, API, data, dependency, destructive, ownership, or acceptance decision.
- Any need to retain timeline values or ply-boundary arithmetic in the visible `BoardControl` contract, introduce a
  public customization API, change callback semantics, or create a universal navigation/viewer abstraction.
- Any change to loading, empty, temporary-branch, traversal, announcement, branch-discard, or MVC-05 chess semantics.
- Any backend/API/endpoint/payload/typed-error/production-contract/data/dependency change, README maintenance,
  historical-record edit, destructive cleanup, formatter repair, `--fix` invocation, commit, or push.
- Any need to modify CSS direction or the existing labels, focus movement, keyboard behavior, accessibility semantics,
  Storybook expectations, or browser proof.
- Any unrelated worktree change, occupied port owned by another process, Storybook health failure after 30 seconds,
  unbounded test/server wait, failure to clean up and confirm port 6006, or unrelated validation failure that would
  require repair or absorption.

## Visible result

> The same navigation toolbar looks and behaves the same, while `ViewerWorkspace` supplies its capabilities and owns
> all timeline and traversal decisions.
