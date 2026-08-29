# Clickable analysis candidates - Every displayed legal candidate can activate the existing first-move branch

> **Status:** accepted/done - V3 complete; fresh final Quality validation passed and the Plan is archived

- **Read trigger:** Read when implementing V3 clickable analysis candidates in the repertoire viewer.
- **Upstream:** none; scope and decisions are settled by the approved coordinator assessment packet.

## Outcome

Every displayed legal analysis candidate, including Best line, is an accessible pointer and keyboard control
that activates the viewer's existing legal branch-move and promotion path, exactly as board drag does. Only the
candidate's first UCI move is applied. Existing SAN, score, WDL, five-line, terminal, polling, observation,
navigation, Flip, and recurrence behavior remain unchanged, with no backend, engine, persistence, or state
contract change.

## Scope

- **Included:** Preserve the first UCI move in the formatted candidate model; expose an optional controlled
  activation callback; wire it through ViewerWorkspace to the existing legal branch handler and PromotionPicker;
  retain current candidate presentation and actions; add bounded component/story/browser proof for pointer,
  keyboard, accessibility, promotion, branch FEN, Flip, focus, constrained layouts, and no-enqueue behavior.
- **Expected areas:** `frontend/**/AnalysisPanel*` source, tests, stories, and local CSS; `frontend/**/analysisFormatting*`
  source and tests; `frontend/**/ViewerWorkspace*` source, tests, stories, and bounded existing viewer helpers or
  fixtures; the existing `viewer-storybook`, `viewer-branch`, and `viewer-branch-stage4` E2E coverage; this active
  Plan only.
- **Excluded:** Backend/API/engine contracts, new chess or promotion logic, PV playback, persistence, repertoire
  workflow changes, route or dependency changes, shared redesign, new browser profiles or specs, unrelated files,
  runtime writes, formatter `--fix`, commits, and pushes.

## Stages

1. **complete** - Preserve candidate activation data without changing the visible analysis contract.
   - **Actions:**
     1. Trace the existing formatted candidate model and retain the first UCI move while leaving SAN, score,
        WDL, five-line, terminal, and existing action data intact.
     2. Add the smallest optional controlled callback needed for candidate activation, keeping the current
        presentation and ownership boundaries; do not introduce PV playback or duplicate chess rules.
     3. Add focused formatting and AnalysisPanel proof that the first UCI move is preserved, the existing fields
        and actions remain available, and the optional callback remains compatible when absent.
   - **Focused proof:** Existing Viewer `analysisFormatting` tests and AnalysisPanel component/story tests, limited
     to candidate-model preservation and unchanged rendering/actions.
   - **Escalation boundary:** Stop if the existing formatter has no stable first UCI value, or if the callback
     requires a new public/API/state contract, new move ownership, or a product/visual decision.
   - **Breakpoint:** none; preserve the current visual analysis presentation.
2. **complete** - Activate candidates through the existing legal branch and promotion ownership.
   - **Actions:**
     1. Pass the optional activation callback from ViewerWorkspace to AnalysisPanel and route activation into the
        existing legal branch-move handler.
     2. Reuse the existing PromotionPicker path for promotion moves; apply only the first UCI move and do not
        enqueue or play later principal-variation moves.
     3. Prove normal, Best line, alternative, promotion, branch-FEN, Flip, no-enqueue, and focus semantics while
        preserving analysis polling/observation, navigation, V1 Flip, and V2 recurrence behavior.
   - **Focused proof:** Existing ViewerWorkspace/component tests and stories covering legal branch activation,
     promotion ownership, first-move-only behavior, focus retention/return, and the listed viewer states.
   - **Escalation boundary:** Stop if the existing handler or PromotionPicker cannot accept the first UCI move
     without new chess logic, state ownership, queue behavior, or an API/engine contract change.
   - **Breakpoint:** none; board and promotion ownership remain with the existing viewer path.
3. **complete** - Demonstrate the accessible pointer/keyboard control in existing Storybook and browser proof.
   - **Actions:**
     1. Update the existing viewer stories and only the bounded helpers or fixtures needed to expose Best and
        alternative candidate activation without changing unrelated story setup.
     2. Extend the existing `viewer-storybook`, `viewer-branch`, and `viewer-branch-stage4` E2E coverage for
        pointer and keyboard activation, accessibility semantics, promotion, constrained layouts, and no-overflow
        behavior; do not add a browser profile or a new browser spec.
     3. Use the supported configured Storybook command and existing browser harness with bounded readiness (30
        seconds) and scoped cleanup; preserve the existing navigation and observation assertions.
   - **Focused proof:** Existing Storybook interaction/accessibility stories and the three named E2E suites, with
     checks for normal/Best/alternative activation, promotion, branch FEN, Flip, focus, no enqueue, and constrained
     no-overflow rendering.
   - **Escalation boundary:** Stop if proof needs a new route, browser profile/spec, visual direction, dependency,
     or behavior outside the approved candidate-activation outcome.
   - **Breakpoint:** none; no new visual direction is authorized.
4. **complete** - Complete the read-only closeout; accepted after the bounded final closeout and fresh final Quality
   validation.
   - **Actions:**
     1. Perform the read-only closeout and bounded cleanup for any test servers or runtime artifacts, scoped to
        this work; do not use `--fix` or absorb unrelated failures.
     2. Run the full closeout exactly as `timeout 600s .venv/Scripts/python.exe scripts/check.py` with a 660000 ms
        tool timeout, then record truthful Plan progress and proof results.
     3. Stop after the Plan record is current; validation is complete and no further implementation decision is made.
   - **Focused proof:** The focused tests and browser proof from stages 1-3 plus the exact full closeout command;
     all commands and server readiness checks use explicit finite timeouts.
   - **Escalation boundary:** Report any unrelated failure or any acceptance, scope, contract, ownership, or
     destructive issue to the coordinator; after one authorized repair failure, return to the coordinator.
   - **Breakpoint:** none; fresh final Quality validation passed and the Plan is accepted/done.

Stages are sequential; no parallel implementation stages are authorized.

## Progress and decisions

- **Stage 1:** complete - candidate formatting preserves only the first UCI move while retaining current display
  fields/actions; 20 focused tests passed; breakpoint: none.
- **Stage 2:** complete - Viewer routes candidates through the existing legal branch and PromotionPicker paths;
  28 focused tests passed across normal/Best/alternative, Flip, branch, first-only, illegal, no-enqueue, and
  promotion focus-cancel-commit cases; breakpoint: none.
- **Stage 3:** complete - updated AnalysisPanel stories, added ViewerWorkspaceAnalysis stories/helper, and extended
  the three existing Viewer/branch E2E specs; Storybook passed 29 files/154 tests, bounded browser proof passed 27
  tests, and build/Storybook/lint/targeted format/size checks passed; breakpoint: none.
- **Stage 4:** complete - the initial exact full closeout was blocked only by prior V1/V2 README table formatting
  in `frontend/README.md` and `frontend/src/features/viewer/README.md`. One authorized Quality FIX formatted exactly
  those files, whitespace/table alignment only. Fresh final Quality PASS included targeted README Prettier, the exact
  full closeout at 11/11, diff check, no artifacts/listeners, and a clean repair scope; breakpoint: none.
- **Closeout decision:** accept V3 as done. The README updater separately updated the analysis and Viewer READMEs for
  V3; no validation was required for that documentation update. No implementation or test scope was expanded.
- **Supported Storybook command:** `npm.cmd run build-storybook --prefix frontend` followed by
  `npm.cmd run test-storybook --prefix frontend` (the Stage 3 Storybook proof passed 29 files/154 tests).

## Proof

- Focused `analysisFormatting`, AnalysisPanel, and ViewerWorkspace tests prove first-UCI preservation, optional
  callback compatibility, existing fields/actions, first-move-only activation, legal branching, promotion, focus,
  Flip, branch-FEN, and no enqueue.
- Existing Storybook stories and the configured Storybook command prove accessible pointer/keyboard controls and
  constrained no-overflow rendering without changing the established visual presentation.
- Existing `viewer-storybook`, `viewer-branch`, and `viewer-branch-stage4` E2E suites prove normal, Best, and
  alternative activation plus promotion, navigation/observation preservation, Flip, recurrence, focus, and
  constrained layout behavior.
- Quality semantic validation passed: 48 focused tests, build/lint/size checks, 27 browser tests, and scope/semantics
  review. The initial full closeout was blocked only by prior V1/V2 README table formatting; one authorized Quality
  FIX formatted exactly `frontend/README.md` and `frontend/src/features/viewer/README.md`, whitespace/table alignment
  only. Fresh final Quality validation passed targeted README Prettier and the exact full closeout command with 11/11
  checks, followed by a passing diff check; no artifacts or listeners remained and the repair scope was clean.
- Full closeout is exactly `timeout 600s .venv/Scripts/python.exe scripts/check.py` with tool timeout `660000` ms;
  no `--fix`.
- Final Stage 4 run: `timeout 600s .venv/Scripts/python.exe scripts/check.py` with tool timeout `660000` ms stopped
  after 2.2s at Prettier check; the reported files were `frontend/README.md` and
  `frontend/src/features/viewer/README.md`. This unrelated baseline failure was reported rather than absorbed.
- Stage 4 cleanup removed generated `artifacts/check-failure.log`; no test server was left running, and ports 5666,
  6006, and 8444 were free.

## Escalation boundaries

- Escalate any new product, visual, API, engine, data, dependency, route, destructive, ownership, or acceptance
  decision rather than selecting one.
- Escalate if the existing legal branch handler or PromotionPicker path cannot implement first-UCI activation
  without changing its contract or adding duplicate chess logic.
- Escalate unrelated failures and preserve unrelated worktree or Scratch content; do not commit or push.

## Visible result (accepted)

> A user can focus any displayed legal analysis candidate, including Best line, press Enter or Space or click it,
> and reach the same legal branch or promotion result as a board drag, with only its first move applied.
