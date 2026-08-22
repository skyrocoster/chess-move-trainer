# Board control toolbar - Previous and Next stay visible beneath the board

> **Status:** done - both stages and independent Quality validation accepted

- **Read trigger:** Read before changing the board controls, their focused tests or stories, or viewer browser assertions.
- **Upstream:** Approved coordinator assessment and the noncanonical visual reference [`experiments/mock-ups/control-bar/control-bar.html`](../../../../experiments/mock-ups/control-bar/control-bar.html).

## Outcome

Previous and Next appear in an always-visible, token-styled Base UI toolbar beneath the chess board in both canonical viewers. The aesthetic change preserves current one-ply navigation, consumer-owned state and handlers, loading and boundary disabling, focus behavior, accessible names, and Lucide chevrons.

## Scope

- **Included:** Replace the `BoardControl` Disclosure with an appropriately labelled `Toolbar.Root` containing exactly two registered `Toolbar.Button` controls; preserve the public props and disabled calculations; use native disabled semantics via supported `focusableWhenDisabled={false}` behavior; adapt the reference bar, focus treatment, and responsive icon/label presentation to existing tokens, CSS Modules, forced colors, and a local container query; add exactly three concise JSX comments marking future skip-controls (First/Last), Play/Pause, and Flip insertion sections.
- **Expected areas:** `frontend/src/features/viewer/BoardControl.{tsx,module.css,test.tsx,stories.tsx}`; focused `frontend/src/features/viewer/{ViewerWorkspace,MockedGameViewer}.{test,stories}.tsx` assertions and `tests/e2e/viewer*.spec.ts` only when needed to reflect removal of the Disclosure or to prove the approved presentation.
- **Excluded:** Visible or functional First, Last, Play, Pause, or Flip controls; placeholders; future-control props, handlers, state, behavior, or tests; changes to consumer source behavior, navigation ownership, or workspace layout; broad design-system work; dependencies; backend work; the unrelated active Stockfish Plan; and edits to the visual-reference mock-up, which remains untouched and noncanonical.

## Stages

1. **complete - Convert `BoardControl` to the responsive toolbar.**
   - **Ordered actions:** Preserve the existing props, game/loading/boundary calculations, and callbacks while replacing Disclosure and generic design-system Button composition with an `aria-label="Board controls"` Base UI `Toolbar.Root` and exactly two native `Toolbar.Button` children. Keep accessible names exactly `Previous` and `Next`, use the installed `ChevronLeft` and `ChevronRight`, and set `focusableWhenDisabled={false}` so disabled controls retain native semantics and cannot activate. Add exactly three concise JSX source comments—one each for the future First/Last skip section, Play/Pause section, and Flip section—without rendering or testing any future function. Rework the component CSS around a local container and descendant query so the bar remains beneath the board, token-driven labels can collapse to icon-only presentation without overflow, focus and disabled states remain clear, and forced-colors behavior remains usable. Update the focused component tests and stories to remove Disclosure assumptions and cover toolbar semantics, exactly two controls, preserved names/icons/actions/disabled states, and representative unconstrained/constrained presentation.
   - **Focused proof:** `npm.cmd test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx`; focused Storybook review of empty, boundary, intermediate, loading, and constrained states.
   - **Escalation boundary:** Stop if correct Base UI registration or native disabling requires changing the shared design-system Button, if a new dependency is needed, or if the approved two-control layout cannot be achieved locally.
   - **Breakpoint:** None expected. Pause only if implementation exposes a genuinely unsettled visual choice rather than a fit-based responsive adjustment.
2. **complete - Prove both canonical consumers and close regressions.**
   - **Ordered actions:** Run the focused consumer suites and change only assertions made stale by removal of the Disclosure or by the approved toolbar presentation; do not rework consumer state, handlers, source layout, or navigation. Exercise the relevant viewer and Storybook browser surfaces at wide and constrained widths, verifying that the bar follows the board, visible labels collapse responsively while accessible names remain, focus indication and native disabled states are clear, no horizontal overflow appears, and no First/Last, Play/Pause, Flip, placeholder, or extra toolbar control is rendered. Confirm keyboard and pointer activation still move exactly one ply and retain existing loading and initial/final boundaries. Finish with the full read-only repository check.
   - **Focused proof:** `npm.cmd test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/MockedGameViewer.test.tsx`; `node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-live-position.spec.ts` when those relevant assertions are used or updated; wide/constrained live browser inspection.
   - **Escalation boundary:** Stop if proof requires changing consumer behavior or layout ownership, expanding E2E scope beyond the viewer surfaces, or choosing a new product, interaction, or visual direction.
   - **Breakpoint:** No human visual breakpoint is expected; escalate only a genuine unresolved choice.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the approved outcome.

## Progress and decisions

- **Stage 1:** complete - `BoardControl` now uses an always-visible, responsive Base UI toolbar with exactly Previous and Next plus the three approved future-section comments. Proof: focused component tests (3 passed), targeted ESLint, frontend build, Storybook build, and targeted Prettier check passed; Storybook emitted only the documented non-fatal Windows libuv teardown assertion. Breakpoint: none required.
- **Stage 2:** complete - focused consumer tests passed (20/20), focused viewer Playwright tests passed (7/7), and wide/constrained browser proof confirmed compact placement, responsive labels, keyboard operation, native disabled states, and no overflow or future controls. The case-worker full check found one transient Board Adapter axe timeout and the unrelated Sol workflow-agent allowlist failure; independent Quality reran the full suite with all 35 E2E tests passing and only the same unrelated workflow-contract failure remaining. Breakpoint: none required.
- **Settled decisions:** The toolbar renders only Previous and Next; accessible names, icons, props, calculations, and consumer ownership remain unchanged. Base UI toolbar buttons use supported native disabled semantics locally. The three future sections exist only as exactly three concise JSX comments. The mock-up is visual reference only and remains untouched.
- **Closeout decision:** Independent Quality returned PASS and authorized acceptance. `.opencode/agents/coordinator-caseworker-sol.md` remains an unrelated pre-existing workflow-contract failure and was reported rather than absorbed.

## Acceptance

- Both `ViewerWorkspace` and `MockedGameViewer` show one always-visible toolbar immediately beneath the board, labelled `Board controls` and containing only Previous and Next.
- Previous and Next preserve their exact accessible names, Lucide chevrons, one-ply callbacks, keyboard/pointer operation, focus behavior, loading disabling, and initial/final boundary disabling.
- The token-styled bar has a clear focus treatment, remains usable in forced colors, and changes from labelled controls to an accessible icon-only treatment at a container-based constrained width without overflow.
- Exactly three concise future-section comments are present in `BoardControl`; no future control is visible or represented by code, props, handlers, state, placeholders, behavior, or tests.
- Focused component/consumer proof, relevant wide/constrained browser proof, and the full read-only check pass without unrelated scope being absorbed.

## Proof

- `npm.cmd test --prefix frontend -- --run src/features/viewer/BoardControl.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/MockedGameViewer.test.tsx` - focused component and both canonical-consumer regressions.
- `node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\viewer.spec.ts tests\e2e\viewer-storybook.spec.ts tests\e2e\viewer-live-position.spec.ts` - relevant viewer route, Storybook accessibility/responsiveness, and live one-ply traversal proof where needed.
- Wide and constrained browser inspection - placement beneath the board, responsive labels, accessible names, keyboard focus, disabled appearance/behavior, forced colors, overflow, and absence of all future controls.
- `.venv\Scripts\python.exe scripts\check.py` - final read-only repository closeout; do not use `--fix` without separate authorization.

## Escalation boundaries

- Any new product or interaction behavior, materially different visual direction, API/data/backend work, dependency change, destructive action, or altered acceptance criterion.
- Any need to change shared design-system code, canonical consumer state/handler ownership, one-ply navigation, public `BoardControl` props, accessible names, or workspace layout.
- Any proposal to render or implement First, Last, Play, Pause, Flip, placeholders, or supporting future-control code beyond the three approved comments.
- Any unrelated failure is reported rather than repaired or absorbed.

## Visible result

> Previous and Next are always visible in a responsive control bar directly beneath the chess board, with no other controls shown.
