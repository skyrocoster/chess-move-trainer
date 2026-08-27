# CMT Analysis panel presentation - a complete canonical analysis surface

> **Status:** complete - Stages 1-4 complete; archived after independent validation and human visual approval

- **Read trigger:** Read before every sequential analysis-panel execution stage and at the final closeout.
- **Upstream:** [authoritative CMT mock-up](../../../../experiments/mock-ups/analysis/analysis-panel-cmt.html),
  [completed MVC-08 analysis-panel record](../mvc-08-analysis-panel/mvc-08-analysis-panel.md),
  [completed MP-10 browser-evaluation record](../mp10-browser-evaluation/mp10-browser-evaluation.md), and
  [completed MP-11 branch record](../mp11-position-analysis-branch/mp11-position-analysis-branch.md)

## Outcome

Turn the controlled `frontend/src/features/analysis/AnalysisPanel.tsx` into the production presentation represented by
the user-edited CMT mock-up. The panel will have the compact engine-output header, stale feedback, prominent best line,
accurate win/draw/loss visualization, ranked alternatives, evaluation emphasis, helper/action treatment, and responsive
container behavior, while the viewer continues to own observation, derivation, polling, and deliberate actions.

The implementation must preserve the real product states and behavior: initial/analyze, queued, running, complete,
stale/update, failed/retry, action errors, observation errors/retry, and terminal empty results. The mock-up's update
timeout and refreshed fixture state are not production behavior.

## Scope

- **Included:**
  - A frontend-only display-contract adjustment that carries the existing structured W/D/L permille values as typed
    presentation data, plus existing position/depth/count metadata where it is already available. The derivation seam
    remains `viewer/analysisFormatting.ts`; no backend, API, database, or queue contract changes.
  - A semantic `AnalysisPanel.tsx`/`AnalysisPanel.module.css` replacement using the approved hierarchy: compact header
    and status, stale notice, best-line summary, W/D/L figure and legend, first-ranked evaluation emphasis, ranked
    alternatives, terminal-empty fallback, helper text, and the existing deliberate actions.
  - Existing `design-system/Button` for actions, existing feedback primitives where their severity and live-region
    contracts fit, native `header`/`section`/`figure`/`dl`/`ol`/`status`/`alert` semantics otherwise, and repository
    Material/CMT tokens, forced-colors, reduced-motion, and container-query conventions.
  - Focused AnalysisPanel, formatting, and viewer integration tests; comprehensive AnalysisPanel stories; and bounded
    Storybook/Playwright proof of states, accessibility, geometry, narrow containers, and desktop presentation.
- **Expected areas:**
  `frontend/src/features/analysis/AnalysisPanel.tsx`,
  `frontend/src/features/analysis/AnalysisPanel.module.css`,
  `frontend/src/features/analysis/AnalysisPanel.test.tsx`,
  `frontend/src/features/analysis/AnalysisPanel.stories.tsx`,
  `frontend/src/features/viewer/analysisFormatting.ts`,
  `frontend/src/features/viewer/analysisFormatting.test.ts`,
  `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx` only for mechanical integration evidence,
  `tests/e2e/analysis-panel-storybook.spec.ts`, and `tests/e2e/playwright.config.ts` only to register a new
  Storybook-focused spec if needed. Existing design-system files are imports and precedents, not expected edit targets.
- **Excluded:** Backend or frontend API behavior, Pydantic/TypeScript API schemas, database or queue behavior, new
  dependencies, new design-system ownership, changes to `EvalBar`, board behavior, broad `ViewerWorkspace` or
  `GameContext` layout, PV playback/click behavior, automatic analysis/retry/cancellation, fake timers or local
  refreshed-state simulation, new terminal semantics, speculative engine/profile metadata, external fonts, copied
  experiment HTML/JavaScript, README edits, `Scratch/`, completed or historical Plan edits, unrelated tracked or
  untracked worktree changes, `scripts/check.py --fix`, commits, and pushes.

### Implementation-critical facts and guardrails

- `AnalysisPanel` is presentation-only. `analysisState.ts` owns the one observation, polling, action pending/error,
  retry, and enqueue workflow. `ViewerWorkspace.tsx` supplies the same displayed or temporary-branch FEN to both
  `EvalBar` and the panel through `analysisPanelDisplay`.
- `analysisApi.ts` already validates candidates with `wdl_wins`, `wdl_draws`, and `wdl_losses` as non-negative integers
  summing to 1000. `analysisFormatting.ts` currently converts those values to a flat string using `/ 10`, so the
  panel display contract must evolve to carry safe structured visualization values rather than parse that string.
  The exact internal shape must retain visible one-decimal percentage labels and an accessible aggregate description.
- Existing result data also supplies candidate rank, score kind/value, SAN-convertible UCI PV, per-candidate depth,
  candidate count, terminal classification, and stale/queue state. Current position ply is owned by the viewer and must
  be passed only as display metadata; do not add API fields or invent metadata when no result exists.
- The first candidate is the best-line summary. The ranked ledger represents the remaining candidates with their
  original ranks; a terminal result with zero candidates keeps the existing terminal-empty message and does not invent
  a best line or ledger rows. Preserve the five-candidate bound, SAN fallback, score/mate notation, W/D/L values, and
  all existing deliberate callback ownership.
- Keep action/status semantics distinct: stale/result feedback must not be merged with action errors; observation errors
  remain observation-retry states; queued/running and action-pending must not gain automatic retry or timeout behavior.
- The mock-up's broad direction is authoritative, but its literal colors, font declarations, native button, and script
  are reference material. Map them to repository tokens, the Base UI-backed `Button`, existing feedback components,
  and the real controlled state machine. Keep source and test files within the repository's 500/700-line limits.
- The coordinator packet records 85 pre-existing status entries: the authoritative mock-up is untracked exploration
  work; `frontend/src/features/analysis/` is currently untracked; viewer files are heavily modified/deleted; and no
  `tests/e2e` changes currently exist. Treat that packet as the worktree baseline, preserve every unrelated change,
  and stop if a directly conflicting concurrent edit appears. Do not repeatedly rescan Git during execution; perform
  the final scope audit once unless a direct conflict requires an earlier stop.

## Stages

1. **pending - Display contract and derivation seam.** Carry the existing structured data and metadata required by the
   approved presentation without changing API/workflow ownership.

   - **Ordered actions:**
     1. Re-read this Plan, the authoritative mock-up, the current AnalysisPanel files, `analysisFormatting.ts`,
        `analysisState.ts`, `analysisApi.ts`, and the current viewer call chain. Confirm the packet baseline and edit
        only the approved frontend display/test/story surfaces.
     2. Define the smallest frontend presentation model that supplies normalized W/D/L geometry values, visible
        one-decimal labels, and accessible W/D/L text. Replace the unsafe flat-string-only path in the internal
        `AnalysisPanelLine` display contract; do not parse rendered text and do not change the API candidate types.
     3. Carry existing displayed-ply, best-candidate depth, and candidate-count metadata through the page-owned
        formatter only where a real result supplies it. Preserve score, SAN, fallback, stale, queue, failure, terminal,
        and action derivation exactly; do not add a local success flash or timer.
     4. Add focused formatter fixtures/assertions and update component/story fixtures to exercise structured W/D/L,
        metadata, score kinds, SAN fallback, fewer-than-five lines, and terminal-empty data. Reconnect
        `ViewerWorkspace.tsx` only if the formatter needs the existing current-position ply.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/analysisFormatting.test.ts src/features/analysis/AnalysisPanel.test.tsx`
     and `npm.cmd run build --prefix frontend`.
   - **Breakpoint:** None expected. Stop before presentation work if the structured display model would require an API,
     public consumer, dependency, new state, changed score/SAN/WDL semantics, or a contested contract beyond this
     approved internal frontend seam.

2. **pending - Canonical semantic presentation and tokenized responsive styling.** Implement the mock-up hierarchy in
   the controlled component and its CSS while preserving the established viewer composition.

   - **Ordered actions:**
     1. Build the compact header/status and optional metadata from controlled display values, retaining the labelled
        heading and polite status behavior. Keep stale/result messaging, action errors, and observation errors in
        separate semantic regions.
     2. Render the first candidate as the best-line summary and W/D/L figure; render remaining candidates as an ordered
        ranked ledger with accurate segment widths, legends, accessible labels, scores, SAN text, and evaluation
        emphasis. Preserve the terminal-empty fallback without empty visual scaffolding.
     3. Map Analyze/Update/Retry/Retry-observation to the existing Base UI-backed `Button`, including the existing
        disabled pending behavior and native focus semantics. Use `PanelFeedback`/`FeedbackCore` only where their
        severity and explicit live-region attributes fit; use native semantic text for ordinary statuses.
     4. Replace the minimal CSS with repository-tokenized panel surfaces, borders, spacing, typescale, numeric display,
        container-query reflow, narrow-width action stacking, forced-colors treatment, and reduced-motion behavior.
        Do not copy mock-up literal colors/fonts or add a new design-system primitive.
     5. Review the rendered wide and narrow panel against the authoritative mock-up before moving on. User edits at this
        visual breakpoint are authoritative and must be bounded to this panel outcome, incorporated, and revalidated.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/AnalysisPanel.test.tsx src/features/viewer/analysisFormatting.test.ts src/features/viewer/ViewerWorkspace.test.tsx`
     and `npm.cmd run build --prefix frontend`.
   - **Breakpoint:** Human visual review of the canonical panel at desktop and constrained widths. Pause for any
     unsettled hierarchy, copy, stale/pending action treatment, color, typography, interaction, or accessibility
     direction; do not resolve such a decision by implementation preference.

3. **pending - Complete state, story, browser, and accessibility evidence.** Prove the observable panel contract across
   every meaningful state and composition without moving workflow ownership into the component.

   - **Ordered actions:**
     1. Extend `AnalysisPanel.test.tsx` and `analysisFormatting.test.ts` for initial/missing, queued, running,
        complete, stale, failed, action-error, observation-error, pending actions, terminal-empty, W/D/L geometry and
        labels, metadata, five-line bounds, score/SAN/fallback, callback intent, focus, status/alert/note/list/figure
        semantics, forced-colors-safe CSS, and focused axe coverage.
     2. Reconcile `AnalysisPanel.stories.tsx` with comprehensive controlled fixtures for all states, narrow-content
        behavior, structured W/D/L values, terminal results, action pending/errors, and deliberate interactions. Keep
        `ViewerWorkspace` stories/tests only for mechanical reconnection and shared-observation proof.
     3. Add a focused Storybook Playwright spec, registering it in `playwright.config.ts` only if a new filename is used.
        Exercise direct AnalysisPanel stories at desktop and 320/480/640px container widths, reduced motion, forced
        colors, no horizontal overflow, visible hierarchy, action operability, and axe/semantic checks. Reuse the
        existing bounded Storybook server profile and clean up the process in every case.
     4. Build Storybook before running its interaction suite; use a readiness bound of 30 seconds and confirm port 6006
        is free after cleanup. Report the known historical board-adapter Storybook timeout if it recurs rather than
        absorbing it into this feature.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/AnalysisPanel.test.tsx src/features/viewer/analysisFormatting.test.ts src/features/viewer/ViewerWorkspace.test.tsx`,
     `npm.cmd run build-storybook --prefix frontend`,
     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`, and
     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/analysis-panel-storybook.spec.ts`.
   - **Breakpoint:** None expected after the approved visual direction. Stop if browser evidence reveals a new product,
     primitive, layout, accessibility, dependency, or acceptance decision rather than silently broadening the scope.

4. **pending - Read-only closeout and Plan completion recording.** Confirm the complete in-scope result, then record
   truthful progress and completion only after independent validation and acceptance.

   - **Ordered actions:**
     1. Re-run the focused AnalysisPanel, formatter, viewer, and narrowly relevant branch integration tests; confirm
        one shared observation, displayed-position targeting, deliberate actions, and unchanged EvalBar/workflow seams.
     2. Run frontend build, Storybook build/interactions, lint, read-only Prettier, source-size validation, and the
        complete `.venv/Scripts/python.exe scripts/check.py` suite without `--fix`.
     3. Perform the single final Git scope audit using the coordinator baseline. Confirm the mock-up, all unrelated
        backend/database/workflow/board/design-system changes, untracked analysis material, modified/deleted viewer
        files, and historical records remain preserved; use `git diff --check` for whitespace proof.
     4. After acceptance, update this Plan's progress/status and archive it under
        `docs/plans/done/analysis-panel-cmt/` according to the repository convention. Do not rewrite completed Plans,
        edit the README, commit, or push.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/AnalysisPanel.test.tsx src/features/viewer/analysisFormatting.test.ts src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`,
     `npm.cmd run build --prefix frontend`,
     `npm.cmd run build-storybook --prefix frontend`,
     `npm.cmd run lint --prefix frontend`,
     `frontend/node_modules/.bin/prettier.cmd --check frontend`,
     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/analysis-panel-storybook.spec.ts tests/e2e/viewer-storybook.spec.ts`,
     `.venv/Scripts/python.exe scripts/check.py`, and `git diff --check`.
   - **Breakpoint:** Fresh independent validation and human acceptance of the visible panel are required before
     archival. Unrelated failures are reported, not repaired by this Plan.

## Progress and decisions

- **Stage 1:** complete - proof: required formatter/AnalysisPanel Vitest (18 tests), frontend build, ViewerWorkspace
  integration Vitest (16 tests), ESLint (one existing hook-dependency warning), and read-only Prettier check passed;
  breakpoint: none.
- **Stage 2:** complete - human visual review accepted the approved desktop and constrained presentation against the
  authoritative mock-up; proof: focused AnalysisPanel/formatter/ViewerWorkspace Vitest (34 tests), frontend build,
  ESLint, and read-only Prettier passed; Storybook complete, stale, terminal-empty, observation error, and action-error
  states were inspected at 1280/640/480/320px with no page errors; breakpoint: none.
- **Stage 3:** complete - proof: focused Vitest (35 tests), frontend build, Storybook build, full Storybook
  interaction suite (21 suites/122 tests), focused AnalysisPanel Playwright (4 tests), ESLint (0 errors; one existing
  ViewerWorkspace hook-dependency warning), and read-only Prettier passed; browser proof covered all controlled states,
  semantics/axe, W/D/L geometry, deliberate actions, 320/480/640px bounds, reduced motion, and forced colors; a
  deterministic forced-colors contrast defect in `.sectionNote` was repaired; breakpoint: none.
- **Stage 4:** complete - proof: independent Quality semantic/scope inspection PASS and fresh closeout Quality
  PASS/ready to archive; the complete `.venv/Scripts/python.exe scripts/check.py` run completed all substantive stages
  with Python/frontend lint, Prettier, type-check, Vitest, and builds passing; E2E had 53 passed and one unrelated
  `tests/e2e/viewer-branch.spec.ts:251:7` axe-core “Axe is already running” race, then the wrapper timed out at the
  WebServer tail, so the full suite is not claimed entirely green. `git diff --check` reported zero whitespace errors
  with informational line-ending warnings only; port 6006 had no listener; the bounded final scope audit found no
  conflicting edit and no attributable temporary server/artifact; user approval of the canonical visual result was
  already recorded in Stage 2; breakpoint: none.
- **Decisions:** The CMT mock-up is the authoritative visual direction. W/D/L values are derived in the frontend from
  existing API permille fields; the backend/API contract, analysis workflow, EvalBar, and viewer ownership remain
  unchanged. The prior completed MVC analysis-panel record and all other historical records are preserved.

## Proof

- Component and formatter regression: focused Vitest tests for structured W/D/L values, best/alternate lines, metadata,
  every current state, callback intents, terminal-empty behavior, and axe semantics.
- Viewer integration: focused `ViewerWorkspace` tests retain one observation, current displayed/branch FEN targeting,
  deliberate Analyze/Update/Retry/observation-retry behavior, queue polling, and EvalBar sharing.
- Static checks: `npm.cmd run build --prefix frontend`, `npm.cmd run lint --prefix frontend`,
  `frontend/node_modules/.bin/prettier.cmd --check frontend`, and repository source-size validation through
  `.venv/Scripts/python.exe scripts/check.py`.
- Storybook: `npm.cmd run build-storybook --prefix frontend` followed by the bounded interaction suite at
  `http://127.0.0.1:6006`; start-up is bounded to 30 seconds, cleanup is mandatory, and port 6006 must be confirmed
  free afterward.
- Browser: a focused Storybook Playwright spec checks desktop and 320/480/640px geometry, no horizontal overflow,
  forced colors, reduced motion, action interaction, semantic roles, and axe. The existing viewer Storybook proof is
  rerun when the mechanical integration changes.
- Final read-only audit: `.venv/Scripts/python.exe scripts/check.py`, `git diff --check`, and one final scoped worktree
  review. Never append `--fix`, commit, or push.

## Escalation boundaries

- Any need for backend/API schema fields, changed endpoint behavior, database/queue semantics, a new dependency, or a
  new public component/design-system primitive.
- Any requirement to retain the flat `wdl` string because the structured internal display-contract evolution is
  contested, or any ambiguity in permille units, score interpretation, SAN conversion, terminal semantics, or metadata
  provenance.
- Any request for automatic enqueue/retry/cancellation, a fake refresh timer, a new success/pending product state, PV
  playback, candidate selection, or behavior not represented by the current controlled callbacks.
- Any visual direction, hierarchy, copy, action treatment, typography, color, responsive behavior, keyboard/focus,
  forced-colors, reduced-motion, or accessibility decision not settled by the authoritative mock-up and existing
  repository contracts.
- Any need to change `ViewerWorkspace`/`GameContext` layout beyond mechanical display-data reconnection, duplicate
  observation/polling, or change to the EvalBar/board/branch behavior.
- Any conflict with the packet baseline or concurrent edit in an approved path. Preserve the other edit and return to
  the coordinator rather than merging by assumption.
- Any need to alter completed Plans, historical records, README files, `Scratch/`, unrelated worktree content, or an
  unrelated validation failure; any request to use `--fix`, destructive Git operations, commit, or push.
- Any Storybook/browser server that cannot be started with bounded readiness, cleaned up safely, or verified to leave
  port 6006 free.

## Visible result

> A person can see a repository-styled Analysis panel with a clear best line, accurate W/D/L visualization, ranked
> alternatives, stale/status feedback, and the same safe deliberate analysis actions at wide and narrow widths.
