# MVC-08 Analysis panel - the same analysis presentation with page-owned display data

> **Status:** done - accepted after independent validation

- **Read trigger:** Read after MVC-07 Evaluation bar is accepted and before each sequential MVC-08 stage.
- **Upstream:** [Modular viewer components master plan](../../../master-plans/modular-viewer-components.md) and
  [completed MVC-07 Evaluation bar Plan/result](../../done/mvc-07-evaluation-bar/mvc-07-evaluation-bar.md)

## Outcome

Make `AnalysisPanel` independently renderable from page-owned display data and callbacks while preserving the current
missing, loading, queued, running, complete, stale, failed, error, terminal, and retry/update presentation; deliberate
Analyze/Update/Retry and observation-retry intentions; five ranked lines; SAN, WDL, and score formatting; DOM; and
accessibility. `ViewerWorkspace` remains the page owner of analysis state and derivation. `analysisState.ts` and
`AnalysisClient` remain the workflow and API seams.

## Scope

- **Included:** The smallest call-site-derived controlled display and callback boundary; page-owned derivation and
  intent wiring; mechanical integration where the existing `GameContext` path requires it; preservation of the current
  observation instance, queue polling, action/retry ownership, copy, DOM, formatting, CSS, focus behavior, live
  announcements, alerts, ranked-line output, terminal empty result, focused tests, Storybook states/interactions,
  relevant axe coverage, viewer integration proof, and read-only validation.
- **Expected areas:**
  `frontend/src/features/viewer/AnalysisPanel.tsx`,
  `frontend/src/features/viewer/analysisFormatting.ts`,
  `frontend/src/features/viewer/AnalysisPanel.module.css` for preservation-only changes,
  `frontend/src/features/viewer/AnalysisPanel.test.tsx`,
  `frontend/src/features/viewer/AnalysisPanel.stories.tsx`, and, only for mechanical controlled reconnection,
  `frontend/src/features/viewer/GameContext.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`, and narrowly relevant branch integration proof.
- **Excluded:** Semantic changes to `analysisState.ts` or `AnalysisClient`; endpoint, payload, typed-error, backend,
  database, dependency, or API changes; analysis-semantic changes; automatic enqueue/retry behavior; new product
  states or copy; visual, layout, typography, color, focus, motion, or accessibility redesign; universal viewer,
  game, opening, tree, session, or analysis abstractions; speculative customization; changes outside the approved
  integration surfaces; README maintenance; destructive cleanup; edits to completed Plans, historical records, or
  the master plan; absorption or reset of unrelated worktree changes; `scripts/check.py --fix`; commits; and pushes.

### Implementation-critical facts and guardrails

- `AnalysisPanel.tsx` currently imports `AnalysisClient` and `AnalysisState`, optionally owns `useAnalysisState`,
  derives visible state/action availability, formats SAN/WDL/score output, and calls workflow methods. The controlled
  component must consume only the minimum display data and callbacks supported by the current call site; it must not
  expose `AnalysisState`, `AnalysisClient`, polling, enqueue methods, FEN workflow inputs, or public customization.
- `ViewerWorkspace.tsx` owns the single `useAnalysisState` observation for the displayed or temporary-branch FEN and
  already supplies that observation to both the evaluation bar and analysis presentation. Preserve that one
  observation, page-owned derivation, deliberate action methods, observation retry, and queue polling.
- Preserve the current visible contract exactly: loading/unavailable/error copy, missing Analyze prompt, queued and
  running status, completed and stale result presentation, failed Retry presentation, Update behavior, five ranked
  lines, SAN conversion and fallback, WDL percentages, CP/mate/mate-given score text, terminal empty results, alerts,
  polite status announcements, list labeling, button behavior, and focused axe coverage.
- Preserve `AnalysisPanel.module.css` geometry, spacing, typography references, state colors, forced-colors rules, and
  layout. Any CSS edit must be mechanically necessary and non-visual.
- Handwritten TypeScript/TSX source must remain at or below 500 lines per file and handwritten tests at or below 700
  lines. If a focused extraction is needed solely to satisfy these limits, preserve the settled outcome and escalate if
  it would change ownership, semantics, or public direction.
- The current worktree contains accepted MVC-05/MVC-06/MVC-07 changes, including dirty `ViewerWorkspace.tsx` and
  `ViewerWorkspace.stories.tsx`, dirty evaluation/branch/navigation surfaces, the untracked completed MVC-07 Plan and
  `evalBarDisplay.ts`, and the accepted MVC-07 master-plan link. It also contains unrelated workflow/agent and README
  edits, check-script/helper changes, test reorganizations, and experiment files. Preserve all of these exactly;
  inspect scoped diffs and status before and after every stage.
- The known unrelated full-check baseline is a possible timeout in
  `tests/e2e/board-adapter-storybook.spec.ts`. Report it without repairing or absorbing it if it recurs.
- Storybook/browser proof must use bounded startup/readiness, stop only the process started for proof, and confirm port
  6006 is free afterward. Do not kill an unrelated port owner or wait unboundedly.

## Stages

1. **complete - Controlled boundary, page-owned derivation, and intent wiring.** Establish the smallest controlled
   display/callback boundary and reconnect it without changing the current presentation or workflow ownership.

   - **Ordered actions:**
     1. Re-read the master plan and accepted MVC-07 result, inspect the current AnalysisPanel implementation, formatting,
        CSS, focused tests/stories, `analysisState.ts`, `AnalysisClient`, the GameContext/ViewerWorkspace call chain,
        relevant branch assertions, and the current dirty worktree. Preserve accepted and unrelated changes.
     2. Define only the minimum controlled shape supported by the existing call site: page-derived display/state data,
        visible messages/results, pending/error values, and deliberate action/retry callbacks. Do not expose workflow
        state, client methods, polling, FEN ownership, or speculative customization from `AnalysisPanel`.
     3. Move the existing presentation derivation and formatting helpers to the page-owned side using the approved
        formatting surface, retaining every current branch, string, score interpretation, SAN fallback, WDL value, and
        five-line limit. Keep `analysisState.ts` and `AnalysisClient` as seams rather than semantic targets.
     4. Refine `AnalysisPanel.tsx` to render the existing section, heading, status, alerts, result lines, empty terminal
        result, and action buttons from controlled values and emit the same deliberate intentions. Do not change its
        DOM, labels, copy, accessibility attributes, focus behavior, or automatic observation behavior.
     5. Reconnect through `GameContext.tsx` and `ViewerWorkspace.tsx` only as mechanically required so the page-owned
        state and derivation feed the panel while the same observation continues to feed the EvalBar and panel.
     6. Reconcile focused component/integration assertions and inspect the scoped diff, file sizes, CSS, and status for
        workflow, API, visual, semantic, historical-record, README, or unrelated-worktree changes.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop and escalate if preserving the current contract requires new state semantics,
     copy, accessibility, visual direction, automatic action, workflow ownership, API behavior, or a public interface
     beyond the settled controlled boundary.

2. **complete - Complete focused states, interactions, and accessibility evidence.** Prove the controlled presentation
   across every meaningful settled state without changing its visual or semantic direction.

   - **Ordered actions:**
     1. Update `AnalysisPanel.test.tsx` to render controlled fixtures and callback spies rather than owning workflow
        state. Cover missing/loading, queued/running, complete, stale, failed/error, terminal empty, action-pending and
        error presentation, deliberate Analyze/Update/Retry/observation-retry intentions, five ranked lines, SAN
        formatting and fallback, CP/mate/mate-given scores, WDL percentages, exact accessible text, status/alert/list
        semantics, non-focus behavior, and focused axe coverage.
     2. Preserve workflow proof at the existing viewer/branch integration seam as needed for observation retry, queue
        polling, displayed branch FEN targeting, and the single shared observation. Do not duplicate polling or client
        behavior in the visible component.
     3. Reconcile `AnalysisPanel.stories.tsx` with the controlled contract and provide comprehensive missing/loading,
        queued, running, complete, stale, failed/error, terminal empty, action-pending/error, five-line, SAN,
        WDL/score, and accessibility stories. Add interactions only for the settled deliberate actions and observation
        retry; do not invent workflow behavior.
     4. Build Storybook before interaction proof. Start only the repository Storybook server needed for proof, bound
        readiness to 30 seconds, clean it up in all cases, and confirm port 6006 is free afterward.
     5. Run Storybook interactions, lint, formatting checks, file-size checks, and `git diff --check`. Inspect CSS and
        stories for unchanged geometry, colors, forced-colors behavior, motion, copy, and accessibility direction.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `git diff --check`
   - **Breakpoint:** None expected. Stop rather than choosing new copy, state meaning, score/WDL/SAN behavior, visual
     treatment, focus/accessibility semantics, browser expectation, dependency, or Storybook direction.

3. **complete - Viewer reconnection and read-only closeout.** Confirm that the controlled extraction is behaviorally
   invisible in the viewer, then complete focused, Storybook, browser, and repository proof.

   - **Ordered actions:**
     1. Re-run focused panel, viewer, and narrowly relevant branch integration tests. Confirm the same displayed or
        temporary-branch FEN is observed, deliberate actions target that FEN, polling/retry stays in `analysisState.ts`,
        and the completed observation remains shared with the EvalBar without duplicate client observation.
     2. Run the frontend build, Storybook build and interactions, lint, read-only formatting, and the existing viewer
        Storybook browser specification. Use bounded startup/readiness and mandatory cleanup; confirm port 6006 is free.
     3. Run the complete repository check exactly as `.venv/Scripts/python.exe scripts/check.py` in read-only mode. Never
        append `--fix`; report unrelated baseline failures instead of repairing them.
     4. Inspect `git diff --check`, the scoped diff, source/test file sizes, and complete worktree status. Confirm the
        AnalysisPanel CSS, page layout, analysis workflow/API seams, completed Plans, historical records, and every
        unrelated tracked/untracked change remain preserved.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

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

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - `AnalysisPanel` now consumes only controlled display data and callbacks while derivation and
  deliberate intent wiring remain page-owned. Focused Vitest passed (24 tests), the frontend build and targeted
  Prettier check passed, and `git diff --check` passed. Source/test sizes remain within limits; breakpoint: none.
- **Stage 2:** complete - focused tests passed (30 tests); frontend and Storybook builds passed; all 21 Storybook
  suites/118 interaction tests passed with one bounded worker; lint, Prettier, source-size, and `git diff --check`
  passed; and port 6006 was confirmed free. The default parallel Storybook run exhausted machine memory before the
  bounded rerun passed. Breakpoint: none.
- **Stage 3:** complete - focused Vitest passed (3 suites, 33 tests), frontend and Storybook builds passed, bounded
  Storybook interactions passed (21 suites, 118 tests), viewer browser proof passed (2 tests), and lint, Prettier,
  source-size, `git diff --check`, and the full read-only `.venv/Scripts/python.exe scripts/check.py` passed.
  Breakpoint: none.
- **Independent validation:** passed - Fresh Quality validation passed the focused 3 suites/33 tests, frontend
  lint/Prettier/build, Storybook build, 21 suites/118 interactions, viewer browser proof (2 tests), source-size/diff
  checks, and full read-only check. No blockers or repairs.
- **Decisions:** MVC-07 is the accepted prerequisite. The visible boundary is controlled with page-owned derivation;
  `analysisState.ts` and `AnalysisClient` remain workflow/API seams; the CSS is preservation-only; no support design
  skill or human visual decision is required; README maintenance is not expected or authorized.

## Proof

- Focused component and viewer integration:
  `npm.cmd run test --prefix frontend -- --run src/features/viewer/AnalysisPanel.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`
  and the narrowly relevant branch proof when changed or required.
- Frontend build: `npm.cmd run build --prefix frontend`.
- Storybook build and interaction proof:
  `npm.cmd run build-storybook --prefix frontend` and
  `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`.
- Lint and formatting: `npm.cmd run lint --prefix frontend` and
  `frontend/node_modules/.bin/prettier.cmd --check frontend`.
- Viewer browser proof:
  `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`.
- Full read-only closeout: `.venv/Scripts/python.exe scripts/check.py`, `git diff --check`, and
  `git status --short --untracked-files=all`. Never use `--fix`.
- Operational proof is bounded: Storybook readiness is at most 30 seconds, cleanup is mandatory, and port 6006 must be
  confirmed free afterward. Unrelated failures are reported rather than repaired.

## Acceptance

- `AnalysisPanel` is independently renderable from controlled display data and callbacks and does not consume
  `AnalysisState`, `AnalysisClient`, polling, enqueue methods, or page workflow state.
- The same loading, missing, queued, running, complete, stale, failed, error, terminal, retry/update, observation
  retry, five-line, SAN, WDL, score, copy, DOM, focus, live-region, alert, list, and axe behavior remains visible.
- `ViewerWorkspace` remains the sole page owner of the analysis observation, derivation, and workflow; the EvalBar and
  panel continue to use the same observation with no duplicate polling or client work.
- `AnalysisPanel.module.css` remains visually unchanged except for a proven mechanical non-visual adjustment; source
  and test file limits remain satisfied.
- Focused tests, Storybook states/interactions, accessibility, frontend build, lint, formatting, viewer browser proof,
  and `.venv/Scripts/python.exe scripts/check.py` pass. Known unrelated failures are reported, not absorbed.
- No API/backend/dependency/visual/semantic/automatic-action change, README maintenance, historical-record rewrite,
  `--fix`, commit, push, or unrelated-worktree modification is introduced.

## Escalation boundaries

- Any new product behavior, state, copy, score interpretation, SAN/WDL formatting, terminal rule, retry/update rule,
  automatic action, visual direction, layout, typography, color, motion, focus, keyboard, accessibility, or browser
  expectation.
- Any need for `AnalysisPanel` to consume `AnalysisState`, `AnalysisClient`, FEN workflow inputs, polling, enqueue
  methods, or to own analysis workflow; any duplicate observation or changed EvalBar/panel integration semantics.
- Any public customization API, universal analysis/viewer abstraction, new dependency, backend/API/endpoint/payload/
  typed-error/analysis-contract change, data change, or ownership outside the approved page composition.
- Any CSS change beyond a mechanically necessary non-visual adjustment; README, master-plan, completed-Plan, or
  historical-record edit; destructive cleanup; reset/reformat/absorption of unrelated worktree content; `--fix`;
  commit; push; or repair of an unrelated validation failure.
- Any Storybook/browser server that is not bounded, cannot be cleaned up, or leaves port 6006 ownership unconfirmed.

## Visible result

> The same analysis panel looks and reads the same, while the page supplies its display data and owns every analysis decision.
