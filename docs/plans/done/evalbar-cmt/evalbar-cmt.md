# Responsive EvalBar continuation - The evaluation rail forms one responsive visual object with the chessboard

> **Status:** done

- **Read trigger:** Read before every sequential EvalBar execution stage, at the visual breakpoint, and at final closeout.
- **Upstream:** [adopted EvalBar mock-up](../../../../experiments/mock-ups/evalbar/evalbar.html), [active analysis-panel Plan](../analysis-panel-cmt/analysis-panel-cmt.md), [completed MVC-07 EvalBar Plan](../../done/mvc-07-evaluation-bar/mvc-07-evaluation-bar.md), and [completed MP-10 browser-evaluation Plan](../../done/mp10-browser-evaluation/mp10-browser-evaluation.md)

## Outcome

Replace the current controlled EvalBar with a canonical React/CSS integration of the adopted mock-up. The rail will
remain page-owned in presentation and analysis semantics, will preserve the current evaluation behavior and
accessibility contract, and will form one responsive visual object with the actual rendered chessboard. It will match
the board's border-box height, stay flush to its edge, and remain beside the board at supported narrow widths.

## Scope

- **Included:** A tokenized 30px vertical evaluation rail with the adopted fill, centered compact readout, midline,
  seam, radii, state styling, reduced-motion behavior, and forced-colors treatment; a page-owned short readout added
  alongside the existing accessible value; preserved White-relative score mapping, clamping, mate formatting,
  pending/stale/failed behavior, and orientation-aware fill; a viewer-owned board/eval stage supporting both static and
  interactive board visuals; a stable actual-board marker/ref, `useLayoutEffect`, border-box measurement, cleaned-up
  `ResizeObserver`, and board-element replacement handling; responsive workspace composition; focused component,
  display-model, workspace/stage, Storybook, axe, and Playwright geometry proof.
- **Expected areas:** `frontend/src/features/analysis/EvalBar.tsx`, `frontend/src/features/analysis/EvalBar.module.css`,
  `frontend/src/features/analysis/EvalBar.test.tsx`, `frontend/src/features/analysis/EvalBar.stories.tsx`,
  `frontend/src/features/viewer/evalBarDisplay.ts`, `frontend/src/features/viewer/evalBarDisplay.test.ts`,
  `frontend/src/features/viewer/BoardEvalStage.tsx`, `frontend/src/features/viewer/BoardEvalStage.module.css`,
  `frontend/src/features/viewer/BoardEvalStage.test.tsx`, `frontend/src/features/viewer/ViewerWorkspace.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.module.css`, `frontend/src/features/viewer/ViewerWorkspace.test.tsx`,
  `frontend/src/features/viewer/ViewerWorkspace.stories.tsx` only for bounded composition fixtures,
  `frontend/src/features/board-adapter/BoardAdapter.tsx`, `frontend/src/features/board-adapter/BoardAdapter.test.tsx`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.tsx`,
  `frontend/src/features/board-adapter/InteractiveBoardAdapter.test.tsx`, and
  `tests/e2e/viewer-storybook.spec.ts`. Keep any extraction bounded to the 500-line handwritten source limit and do
  not introduce broader adapter abstractions.
- **Excluded:** Backend, API, engine, database, queue, analysis polling, and analysis-state changes; changed score
  units, meter semantics, accessible state text, candidate behavior, or orientation meaning; board-library replacement,
  movement, branch, navigation, or context-panel behavior; copied mock-up HTML/CSS/JavaScript or its standalone
  script; new dependencies, global design-system ownership, global token redesign, new routes, broad board-adapter
  redesign, unrelated worktree changes, `Scratch/`, active or completed historical Plan edits, README edits unless a
  genuinely new public architecture or structural convention is introduced, `scripts/check.py --fix`, commits, and
  pushes.

### Implementation-critical facts and guardrails

- `ViewerWorkspace` owns `useAnalysisState`, `evaluationDisplay`, and the one shared observation used by EvalBar and
  AnalysisPanel. Do not move client calls, polling, enqueue/retry behavior, or workflow ownership into EvalBar or the
  stage.
- Preserve `evalBarDisplay.ts` semantics: neutral and no-analysis values are 50; CP values use the existing
  `50 + (score_value / 1000) * 50` mapping with 0-100 clamping; `mate_given` is 100; signed mate values map to 100
  or 0. Keep full existing accessible state text. Use `formatScore` for the compact CP/mate readout and the adopted
  neutral `0.00` readout without parsing accessible text.
- Positive scores are White-relative. White orientation fills from the bottom and Black orientation fills from the
  top, keeping the fill on White's displayed side. Retain the Base UI Meter role/name, 0-100 range, clamped
  `aria-valuenow`, non-focus behavior, and `aria-valuetext`.
- The mock-up's standalone `ResizeObserver` script is design guidance, not code to copy. The repository's actual
  board elements are nested inside adapters with below-board disclosure or branch chrome, so parent flex/grid stretch
  would measure the wrong height. Mark the static `.boardGraphic` and interactive `.board` as the actual visual;
  resolve that marker within the React-owned stage, measure `getBoundingClientRect().height` (including borders) in a
  `useLayoutEffect`, observe changes with a cleaned-up `ResizeObserver`, and rebind when React replaces the visual.
- The seam is concrete: the rail is 30px wide, has zero layout gap, no left border, a right-side radius, and a
  border-box height equal to the actual square board. The board supplies the shared seam treatment and has the left
  radius when staged. The board remains the sizing source; the rail must reserve its width rather than stack on narrow
  layouts.
- Map mock-up colors to existing Material/CMT roles (`background`/`on-background`, `outline-variant`, `outline`,
  `primary`/`on-primary`, `secondary`, and `shadow`) and use existing radii/elevation tokens. Do not add literal theme
  colors or a new design-system primitive.
- The active `analysis-panel-cmt` Plan is still in progress and shares `ViewerWorkspace.tsx`; it explicitly excludes
  EvalBar and broad board-layout redesign. Do not dispatch this Plan while that Plan can still edit the shared path.
  The coordinator must first close it or establish a fresh non-conflicting baseline. Preserve all unrelated and
  historical records.
- This is an internal component/layout change, so README maintenance is not expected. Re-evaluate only if the
  implementation creates a genuinely new public architecture or documented structural convention.

## Stages

1. **accepted - Controlled readout and actual-board measurement seam.** Establish the controlled presentation data and
   React-owned geometry seam without changing evaluation ownership or semantics.

   - **Ordered actions:**
     1. Re-read this Plan, the active analysis-panel Plan, the adopted mock-up, the completed EvalBar records, and only
        the named EvalBar, display, board-adapter, workspace, and focused test/story files. Confirm the active-Plan
        dispatch gate and stop before editing if a direct concurrent change exists.
     2. Extend the controlled EvalBar display contract with a short readout. Derive CP, mate, retained-candidate,
        pending, stale, failed, and neutral readouts from existing page-owned values; preserve every existing full
        accessible state string, 0-100 meter value, state marker, and clamp behavior.
     3. Add a stable `data-board-visual` marker or equivalent narrowly scoped ref contract to the actual square visual
        in both board adapters. Do not change board rendering, movement, branch, disclosure, or error behavior.
     4. Add `BoardEvalStage` if needed for clarity and the source-size limit. It must resolve the actual visual within
        the stage, measure its border-box height in `useLayoutEffect`, apply that height to the rail shell, observe
        future size changes with `ResizeObserver`, disconnect on cleanup, and re-resolve after board-element
        replacement. Do not copy the mock-up's script or use viewport/fixed board heights.
     5. Keep `ViewerWorkspace` as the sole owner of analysis derivation and pass the existing display object through
        the stage without a second observation or workflow seam.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/EvalBar.test.tsx src/features/viewer/evalBarDisplay.test.ts src/features/viewer/BoardEvalStage.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/board-adapter/BoardAdapter.test.tsx src/features/board-adapter/InteractiveBoardAdapter.test.tsx`

     `npm.cmd run build --prefix frontend`

   - **Breakpoint:** None expected. Stop and escalate if the measurement seam requires a changed API, score/state
     contract, dependency, workflow owner, or broader board-adapter redesign.

2. **accepted - Canonical visual seam and responsive workspace composition.** Integrate the adopted rail appearance and
   place it beside the real board in both wide and constrained compositions.

   - **Ordered actions:**
     1. Replace the current pill/minimum-height EvalBar CSS with the reference hierarchy: vertical full-height track,
        30px rail, white/black fill, centered compact readout, midline, right radius, no left rail border, and shared
        board-side seam. Keep Base UI Meter semantics and existing state/orientation selectors.
     2. Tokenize all colors, borders, radii, shadows, typography, and spacing with the existing Material/CMT roles.
        Preserve state distinction for neutral, pending, and best-line displays, and add reduced-motion and
        forced-colors handling consistent with repository conventions.
     3. Recompose `ViewerWorkspace` around the board/eval stage, remove the obsolete independent EvalBar grid gap/track,
        preserve the context panel and controls, and keep the toolbar aligned to the board rather than the rail.
     4. At narrow widths keep the rail horizontally beside the board, reserve its fixed width, and let the board shrink
        within the available container. Do not stack the rail or permit horizontal overflow. Keep static and interactive
        board behavior unchanged.
     5. Run the rendered wide and constrained composition against the adopted reference and pause at the visual
        breakpoint before adding broad test coverage.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/EvalBar.test.tsx src/features/viewer/evalBarDisplay.test.ts src/features/viewer/BoardEvalStage.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run lint --prefix frontend`

   - **Breakpoint:** Human visual review at desktop and constrained widths for neutral, pending, CP, mate,
     stale-retained, failed-retained, White orientation, and Black orientation. User edits at this breakpoint are
     authoritative, must stay bounded to this outcome, and must be incorporated and revalidated before Stage 3.
   - **Escalate if:** Any seam dimension, state color, readout treatment, mobile arrangement, typography, focus,
     motion, or accessibility decision is not settled by the adopted reference and repository contracts.

3. **accepted - Complete component, Storybook, accessibility, and browser geometry evidence.** Prove the integrated rail
   across states, orientations, board modes, and responsive sizes.

   - **Ordered actions:**
     1. Expand EvalBar and display-model tests for neutral/unknown, queued/running, CP, positive and negative mate,
        `mate_given`, stale and failed retained candidates, clamping, readout/full accessible text separation,
        orientation, meter semantics, non-focus behavior, and axe coverage.
     2. Add stage/workspace assertions for the actual-board marker, board replacement rebind, shared observation,
        static and interactive composition, and preservation of existing controls/context behavior. Keep adapter tests
        limited to the mechanical marker/ref contract.
     3. Reconcile EvalBar stories for every controlled state and orientation, with an isolated fixed-height harness. Use
        existing viewer wide/constrained stories for the real board-stage composition; keep `ViewerWorkspace.stories.tsx`
        below 500 lines and extract no unrelated fixtures.
     4. Extend `tests/e2e/viewer-storybook.spec.ts` using the existing Storybook server profile. At desktop and
        constrained 320/480/640px widths, assert actual board and rail top/height agreement within 1 CSS pixel, exact
        board-right/rail-left contact with no seam gap, rail-side fill direction, no horizontal overflow, stage
        centering, toolbar alignment, meter semantics, axe, forced colors, and reduced motion.
     5. Build Storybook before its interaction suite; bound readiness to 30 seconds, clean up every server, and confirm
        port 6006 is free. Report unrelated historical Storybook failures rather than absorbing them.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/EvalBar.test.tsx src/features/viewer/evalBarDisplay.test.ts src/features/viewer/BoardEvalStage.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/board-adapter/BoardAdapter.test.tsx src/features/board-adapter/InteractiveBoardAdapter.test.tsx`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`

   - **Breakpoint:** None expected after the Stage 2 visual acceptance. Stop if browser evidence reveals a new
     product, layout, accessibility, dependency, ownership, or acceptance decision.
   - **Escalate if:** Exact height/contact proof cannot pass at all required sizes without relaxing the approved
     geometry or using an unapproved sizing strategy.

4. **accepted - Fresh independent validation and read-only closeout.** Confirm the complete in-scope result and archive
   only after independent UI/browser acceptance.

   - **Ordered actions:**
     1. Request fresh independent Quality validation of the controlled EvalBar, display-model semantics, board-stage
        measurement/replacement, both board modes, responsive seam geometry, accessibility, and unchanged analysis
        ownership. Repair only a coordinator-authorized in-scope defect; after one failed repair, return to the
        coordinator.
     2. Re-run focused Vitest, frontend build, Storybook build/interactions, targeted Viewer Storybook Playwright,
        frontend lint, read-only Prettier, and source-size validation.
     3. Run the complete `.venv/Scripts/python.exe scripts/check.py` suite without `--fix`. Report unrelated failures;
        do not repair them through this Plan.
     4. Perform one final Git scope audit against the coordinator baseline and `git diff --check`. Confirm that the
        adopted mock-up, active/completed Plans, unrelated worktree changes, backend/API/analysis surfaces, and
        historical records remain preserved.
     5. After acceptance, record truthful progress and move this Plan to `docs/plans/done/evalbar-cmt/` according to
        repository convention. Do not alter the adopted mock-up, other Plans, README, or unrelated content.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/analysis/EvalBar.test.tsx src/features/viewer/evalBarDisplay.test.ts src/features/viewer/BoardEvalStage.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/board-adapter/BoardAdapter.test.tsx src/features/board-adapter/InteractiveBoardAdapter.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`

     `.venv/Scripts/python.exe scripts/check.py`

     `git diff --check`

   - **Breakpoint:** Fresh independent Quality validation and final human acceptance of the visible responsive rail are
     required before archival. No `--fix`, commit, or push is authorized.
   - **Escalate if:** Final proof needs scope expansion, acceptance relaxation, a new contract/dependency/architecture,
     historical-record edits, README maintenance, or repair of an unrelated failure.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage only when the approved
outcome and decisions remain unchanged.

## Progress and decisions

- **Stage 1:** accepted - proof: independent Quality validation passed 59/59 focused tests, frontend build, and
  `git diff --check`; controlled `shortValue`, actual-board markers, React-owned `BoardEvalStage` measurement/
  replacement/cleanup seam, and sole `ViewerWorkspace` analysis ownership accepted; breakpoint: none.
- **Stage 2:** accepted - human visual acceptance recorded after review of the canonical wide, constrained, 320px,
  and Black-oriented rail treatment; proof: focused Vitest passed 39/39; frontend build passed; frontend lint passed
  with one existing `ViewerWorkspace.tsx` exhaustive-deps warning; changed-path Prettier check passed; reduced-motion/
  forced-colors geometry check passed; breakpoint: none.
- **Stage 3:** accepted - proof: focused Vitest passed 64/64 tests; frontend build passed; Storybook build passed; all
  21 Storybook interaction suites passed with 126/126 tests; targeted Viewer Storybook Playwright passed 3/3 tests;
  browser evidence covered desktop and 320/480/640px constrained widths, <=1 CSS pixel top/height agreement, exact
  board-right/rail-left contact, 30px rail width, no stage overflow, toolbar alignment, White/Black fill direction,
  representative readouts/states, meter semantics, axe, forced colors, and reduced motion; a later full interaction
  rerun reported only unrelated historical PromotionPicker, typescale, and ViewerWorkspace runner failures
  (`__test` availability/timeouts), so no unrelated repair was absorbed; port 6006 was confirmed free after cleanup;
  breakpoint: none.
- **Stage 4:** accepted - case-worker proof: focused Vitest 64/64; frontend build; Storybook build and interactions
  126/126; targeted Viewer Storybook Playwright 3/3; frontend lint, read-only Prettier, and source-size validation;
  complete read-only `.venv/Scripts/python.exe scripts/check.py` passed all 14 checks, including E2E and Storybook
  interaction/accessibility suites; `git diff --check` passed with normal Windows line-ending warnings. Independent
  Quality additionally passed the targeted Black Subject Storybook Playwright 1/1, the complete 14-check suite, and
  the scope audit; no artifacts or listening Storybook process remained. The prior `ERR_CONNECTION_REFUSED` was
  classified as a tool-timeout/process-termination artifact, not a product failure; the Stage 2 visual breakpoint was
  already accepted; breakpoint: none.
- **Overall:** all four stages accepted; Plan complete.
- **Decisions:** The mock-up is the adopted visual reference, but its standalone JavaScript is not canonical. The
  React implementation will measure the marked actual square board visual with a cleaned-up observer and will not
  measure adapter chrome. Existing White-relative evaluation, meter, accessibility, orientation, state, and shared
  observation contracts remain unchanged. Stage 3 uses the existing viewer stories for real static/interactive board
  composition and an isolated fixed-height EvalBar harness for controlled state coverage. Browser centering proof is
  anchored to the complete board/rail stage, while toolbar proof remains aligned to the board visual. The active
  analysis-panel Plan is a dispatch dependency because of the shared `ViewerWorkspace.tsx` path.

## Proof

- Focused Vitest covers EvalBar rendering, display-model derivation, stage measurement/replacement, workspace
  composition, and the mechanical board markers/ref contract.
- Storybook covers neutral, pending, completed CP/mate, stale, failed-retained, and both orientations using repository
  tokens and isolated fixed-height/component fixtures.
- Targeted Storybook Playwright evidence covers desktop and constrained 320/480/640px sizes, actual board/rail
  top-edge and border-box height agreement within 1 CSS pixel, zero seam gap, no horizontal overflow, orientation fill,
  toolbar alignment, axe, reduced motion, forced colors, and meter semantics.
- Static closeout runs frontend build/lint, read-only Prettier, source-size validation, the complete read-only
  `.venv/Scripts/python.exe scripts/check.py` suite, and one final `git diff --check`/scope audit. Storybook startup is
  bounded and port 6006 cleanup is mandatory.

## Acceptance

- The rail and the actual rendered square board have matching top edges and identical outer border-box heights within
  1 CSS pixel at desktop and constrained 320/480/640px widths, including after responsive resize and board-element
  replacement.
- The rail begins exactly at the board's right edge with no layout gap. The rail has no left border; the board/shared
  seam is one continuous tokenized hairline; the board has the left radius and the rail has the right radius.
- The rail is fixed at 30px wide, remains beside the board on narrow containers, reserves its width by shrinking the
  board, and never stacks or creates horizontal overflow.
- The compact centered readout matches the adopted reference: neutral/unknown uses `0.00`, CP and mate values use
  existing formatting, and the full state-specific accessible text remains available through the existing meter
  semantics.
- Neutral, queued/running, completed, stale-retained, failed-retained, CP, mate, `mate_given`, White orientation, and
  Black orientation preserve current behavior. Positive White-relative values fill from the displayed White side.
- The Base UI meter remains named `Evaluation`, retains the 0-100 range and safe clamping, remains non-focusable, and
  passes focused axe, reduced-motion, and forced-colors proof.
- One page-owned analysis observation still feeds EvalBar and AnalysisPanel. No backend/API/engine/queue/polling,
  board movement, branch, or context behavior changes.
- Fresh independent Quality validation passes, the complete read-only repository check passes without `--fix`, and
  unrelated worktree changes and historical records remain intact.
- No README change is made unless implementation creates a genuinely new public architecture or structural convention;
  any such need is an escalation rather than an assumption.

## Escalation boundaries

- Any change to score units, White-relative interpretation, CP/mate/`mate_given` formatting, clamping, meter range or
  name, accessible state text, pending/stale/failed behavior, analysis observation, polling, enqueue/retry behavior, or
  API/backend/engine contracts.
- Any inability to measure the actual square board in both static and interactive modes with the bounded marker/ref,
  `useLayoutEffect`, border-box measurement, cleaned-up `ResizeObserver`, and replacement rebind; do not substitute
  viewport sizing, adapter-root stretch, copied standalone JavaScript, or a new dependency.
- Any need for a broader `BoardAdapter`/`InteractiveBoardAdapter` redesign, a new public component/design-system
  primitive, a board-library change, or ownership outside `ViewerWorkspace`/the existing presentation boundary.
- Any visual decision not settled by the adopted mock-up or existing repository contracts, including rail width,
  readout copy, state colors, seam border, radii, shadow, typography, mobile arrangement, focus, reduced motion, or
  forced-colors treatment. Use the Stage 2 human breakpoint rather than guessing.
- Any conflict with `analysis-panel-cmt` or the coordinator baseline, any need to absorb unrelated changes or failures,
  any edit to active/completed historical Plans or the adopted mock-up, any README architecture change, or any request
  for destructive Git operations, `--fix`, commit, or push.
- Any unbounded browser/Storybook startup, failed cleanup, occupied port 6006 owned by another process, relaxed
  geometry acceptance, or repair-loop failure beyond one coordinator-authorized in-scope repair.

## Visible result

> The evaluation rail forms one responsive visual object with the chessboard, matching its rendered height and shared edge at every supported size while retaining correct evaluation behavior.
