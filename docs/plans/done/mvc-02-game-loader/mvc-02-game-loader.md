# MVC-02 Game loader - a controlled reusable form with an unchanged viewer

> **Status:** done - all stages accepted with independent validation

- **Read trigger:** Read after MVC-01 Foundations is accepted and before each sequential MVC-02 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-01 Foundations Plan](../../done/mvc-01-foundations/mvc-01-foundations.md)

## Outcome

`GameLoader` becomes a controlled reusable form while preserving its current UUID/Ply validation, loading and typed
failure presentation, reset behavior, disclosure, constrained layout, keyboard/focus behavior, accessibility, and
appearance. `ViewerWorkspace` remains the owner of request, abort, lookup, numeric Ply conversion, and all page
workflow logic, so loading a game through `/viewer` remains observably unchanged.

## Scope

- **Included:** Replace the loader's hybrid input ownership with the smallest controlled boundary using the existing
  `gameUuid`, `ply`, change callbacks, status values, `GameLoaderValues`, and callback payloads where mechanically
  possible. Keep validation presentation local to the form, emit validated submit/reset intentions, and preserve the
  existing disclosure, loading, failure, responsive, focus, and accessibility behavior. Add focused component proof,
  comprehensive Storybook states/interactions, and mechanical viewer reconnection proof.
- **Expected areas:**
  `frontend/src/features/viewer/GameLoader.tsx`,
  `frontend/src/features/viewer/GameLoader.module.css`,
  `frontend/src/features/viewer/GameLoader.test.tsx`,
  `frontend/src/features/viewer/GameLoader.stories.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx`,
  and the relevant existing viewer browser proof in
  `tests/e2e/viewer.spec.ts`, `tests/e2e/viewer-storybook.spec.ts`, and
  `tests/e2e/viewer-live-position.spec.ts`.
- **Excluded:** Request, abort, lookup, numeric Ply conversion, game state, traversal, branch, analysis,
  announcement, and other page workflow logic inside `GameLoader`; changes to `positionApi.ts`, backend routes,
  payloads, typed API contracts, dependencies, database, unrelated components, generic form abstractions, visual
  redesign, new product behavior, layout or token direction, destructive cleanup, unrelated worktree changes,
  historical records, commits, and pushes. Do not use `scripts/check.py --fix`.

## Stages

1. **accepted - Controlled form boundary.** Make the form values parent-controlled without moving any request or page
   workflow into the reusable component. Preserve the existing value/change names and callback payloads where
   mechanically possible; adapt zero-prop tests and stories with local controlled harnesses rather than restoring
   production-owned input state. Keep UUID/Ply validation, trimmed submit values, blank Ply as `""`, typed status
   display, loading disablement, reset emissions, default-open disclosure, and current DOM/accessibility semantics.
   Confirm by bounded diff review that lookup, abort, request identifiers, numeric conversion, and page state remain in
   `ViewerWorkspace`.
   - **Ordered actions:**
     1. Refine `GameLoader` to consume its current value props and change callbacks as the authoritative input state.
     2. Preserve local validation feedback and the existing `GameLoaderValues`, status, failure-copy, loading, reset,
        disclosure, and form-control behavior without adding a request concern.
     3. Reconcile only the directly affected local test/story harnesses needed to render the controlled boundary.
     4. Review the scoped diff and search the loader for forbidden lookup, abort, request, conversion, and page-workflow
        ownership before proceeding.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameLoader.test.tsx`
     and `npm.cmd run build --prefix frontend`.
   - **Breakpoint:** None expected. Escalate if preserving the existing prop/callback contracts requires a new API shape,
     changes behavior, or moves workflow ownership.

2. **accepted - Focused behavior and comprehensive Storybook evidence.** Lock the reusable component's current
   behavior with focused tests and Storybook states/interactions, without changing its visual direction or semantic
   contract.
   - **Ordered actions:**
     1. Extend `GameLoader.test.tsx` for controlled value updates and exact callback payloads, valid and invalid UUID/Ply
        submission, blank Ply, trimmed submission, all typed failures, loading/reset behavior, and validation clearing.
     2. Add disclosure collapse/expand, native keyboard/focus order, invalid and live-region semantics, constrained
        container-query behavior, forced-colors preservation, and focused axe coverage where the existing boundary
        can prove them without redesign.
     3. Update `GameLoader.stories.tsx` with a story-local controlled harness and comprehensive empty, loading, each
        typed failure, constrained, disclosure, validation/submit/reset, and keyboard/accessibility interaction states.
     4. Verify the module CSS retains the existing geometry, tokens, focus treatment, container query, and forced-colors
        rules; make only mechanical corrections required by the controlled boundary.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameLoader.test.tsx`
     `npm.cmd run build-storybook --prefix frontend`
     `npm.cmd run lint --prefix frontend`
     `frontend\node_modules\.bin\prettier.cmd --check frontend`
   - **Breakpoint:** None expected. Stop and escalate rather than choosing a new copy, layout, focus treatment,
     disclosure behavior, accessibility semantic, dependency, or visual direction.

3. **accepted - Viewer reconnection and regression lock.** Reconnect the controlled form mechanically and prove that the
   page-owned workflow and visible viewer remain unchanged.
   - **Ordered actions:**
     1. Update `ViewerWorkspace` only as needed to supply controlled values and receive loader intentions; retain its
        lookup call, AbortController/request-id guards, blank-to-undefined numeric conversion, reset behavior, typed
        failure mapping, failure preservation, traversal, branch, analysis, and announcement ownership.
     2. Update `ViewerWorkspace.test.tsx` and `ViewerWorkspace.stories.tsx` only for the changed boundary and preserve
        assertions for one request, explicit and blank Ply, loading/reset, abort/stale-result protection, typed failures,
        active-game preservation, constrained layout, and accessibility.
     3. Run the focused frontend, Storybook, lint, formatting, and viewer browser proof; inspect the scoped diff and
        verify no backend, dependency, historical, or unrelated worktree changes were absorbed.
     4. Run the final read-only repository check and record unrelated baseline failures as reported failures rather than
        repairing or absorbing them.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameLoader.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
     `npm.cmd run build --prefix frontend`
     `npm.cmd run build-storybook --prefix frontend`
     `npm.cmd run lint --prefix frontend`
     `frontend\node_modules\.bin\prettier.cmd --check frontend`
     `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-live-position.spec.ts`
   - **Breakpoint:** No human breakpoint is expected. After green proof, visible equivalence is verified against the
     existing wide, constrained, loading, failure, disclosure, keyboard/focus, accessibility, and forced-colors
     surfaces. Pause and require coordinator/human direction if any visual, behavioral, interaction, accessibility,
     ownership, contract, dependency, destructive, or acceptance decision appears.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** accepted - `GameLoader` now consumes required parent-controlled UUID/Ply values and change callbacks;
  story and test harnesses provide local control without restoring production-owned input state. The focused suite
  passed (10/10), the frontend build and `git diff --check` passed, and a bounded search confirmed no lookup, abort,
  request, numeric-conversion, or page-workflow ownership entered the component. No breakpoint appeared.
- **Stage 2:** accepted - focused proof now covers controlled updates and callback values, validation clearing,
  trimmed and blank-Ply submission, every typed failure, loading/reset, disclosure, keyboard focus order, ARIA and
  live-region semantics, constrained/forced-colors preservation, axe, and Storybook interactions. GameLoader Vitest
  passed (18/18); Storybook build, lint, Prettier, and `git diff --check` passed. The documented non-fatal Windows
  Storybook libuv teardown assertion and jsdom canvas warning did not fail proof. No breakpoint appeared.
- **Stage 3:** accepted - `ViewerWorkspace` already supplied the complete
  controlled boundary, so no workspace source change was needed. Focused Vitest passed (32/32); frontend and
  Storybook builds, lint, Prettier, targeted viewer Playwright (7/7), and `git diff --check` passed. The read-only full
  check passed 47/48 browser tests and reported only the previously documented unrelated failures: five experiment
  formatting files and one Board Adapter Storybook timeout. Independent Quality reran 32/32 focused tests, build,
  lint, Prettier, Storybook, and 7/7 targeted browser tests successfully; it reproduced the five unrelated experiment
  formatting failures and found the Board Adapter timeout transient on focused rerun. No `--fix` ran and no
  breakpoint appeared.
- **Decisions:** MVC-01 is the accepted dependency. The controlled boundary, page-owned workflow, no-redesign
  direction, sequential stages, and read-only final check are approved. Unrelated baseline failures must be reported,
  not absorbed. No genuine human decision was required. Independent Quality accepted MVC-02 without repair.

## Proof

- Focused component and integration behavior:
  `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameLoader.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
- Frontend type/build, Storybook, lint, and formatting:
  `npm.cmd run build --prefix frontend`
  `npm.cmd run build-storybook --prefix frontend`
  `npm.cmd run lint --prefix frontend`
  `frontend\node_modules\.bin\prettier.cmd --check frontend`
- Viewer route, Storybook composition, constrained behavior, accessibility, loading, reset, typed failure, and live
  whole-game behavior:
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-live-position.spec.ts`
- Final read-only closeout:
  `.venv\Scripts\python.exe scripts\check.py`
  `git diff --check`
  `git status --short`
- Never run `.venv\Scripts\python.exe scripts\check.py --fix`. Existing unrelated baseline failures are reported
  and remain outside this Plan.

## Acceptance

- A parent-controlled `GameLoader` emits the same validated `GameLoaderValues` and reset intentions while preserving
  raw change callbacks, trimmed submit values, blank Ply behavior, validation copy, typed failure copy, loading state,
  and reset availability.
- Disclosure, constrained layout, keyboard/focus order, live announcements, invalid-state semantics, axe coverage,
  forced-colors behavior, tokens, geometry, and appearance remain equivalent to the current component.
- `/viewer` retains request/abort/lookup ownership in `ViewerWorkspace`, performs the same numeric Ply conversion, and
  preserves loading, reset, stale-result protection, typed failure, active-game preservation, traversal, branch,
  analysis, announcements, responsive composition, and browser behavior.
- Focused and full read-only proof is green, or any unrelated baseline failure is explicitly reported without being
  absorbed into MVC-02.

## Escalation boundaries

- Any new product behavior, visual direction, copy, layout, focus, keyboard, accessibility, or acceptance decision.
- Any change to the component prop/callback contract beyond the smallest mechanically necessary controlled boundary.
- Any movement of request, abort, lookup, numeric Ply conversion, page state, or viewer workflow into `GameLoader`.
- Any API, endpoint, payload, typed-error, backend, data, database, dependency, destructive cleanup, universal
  abstraction, or ownership change.
- Any inability to preserve current disclosure, constrained, keyboard/focus, accessibility, appearance, loading,
  failure, reset, or viewer behavior.
- Any unrelated worktree change, historical-record modification, formatter repair, `--fix` invocation, commit, or push.
- Any unrelated failure that would need to be repaired or absorbed to claim acceptance.

## Visible result

> At `/viewer`, the Game Loader is parent-controlled and reusable, but its validation, loading, failure, reset,
> disclosure, accessibility, responsive appearance, and surrounding viewer behavior look and behave exactly as before.
