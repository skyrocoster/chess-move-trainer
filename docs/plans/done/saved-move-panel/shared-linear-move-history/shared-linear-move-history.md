# Shared Linear Move History - CMT Storybook history with keyboard navigation

> **Status:** complete - user-accepted visual breakpoint; post-edit verification deferred to the user

- **Read trigger:** Read before implementing the shared Move History foundation or changing its focused proof.
- **Upstream:** [Saved move panel redesign](../../../../grilling-docs/saved-move-panel-redesign.md) and [Saved Move Panel master plan](../../../../master-plans/saved-move-panel/saved-move-panel.md)

## Outcome
Provide a reusable, controlled linear Move History feature that presents the initial position and SAN moves with clear active-state, click selection, automatic scrolling, and accessible keyboard previous/next/start/end navigation. It is proven in Storybook using the existing CMT design language so `/viewer` and `/repertoire` can integrate it in later slices without sharing route state or domain ownership.

## Scope
- **Included:** A shared chess-domain Move History component and its controlled types/navigation model; initial-position and SAN move presentation; active-row synchronization; click selection; keyboard previous/next/Home/End navigation; predictable accessible focus; automatic active-row scrolling; reduced-motion behavior; forced-colour behavior; focused unit tests; and a synthetic interactive Storybook story.
- **Expected areas:** `frontend/src/features/move-history/{moveHistoryTypes.ts,moveHistoryModel.ts,MoveHistory.tsx,MoveHistory.module.css,moveHistoryModel.test.ts,MoveHistory.test.tsx,MoveHistory.stories.tsx}`; `frontend/.storybook/main.ts` only to add the explicit story-discovery glob for the new shared feature when required. Keep handwritten source under 500 lines and handwritten tests under 700 lines.
- **Excluded:** `/viewer` or `/repertoire` wiring; changes to `BoardControl`, `GameContext`, viewer state, repertoire sessions, preferred moves, effective dates, Position Reach Frequency, backend/API contracts, database or storage; board/evaluation behavior; new dependencies; variation or tree behavior; Line Library work; route redesign; and unrelated records or worktree changes.

## Stages
1. **complete** - Define and prove the shared controlled history contract and pure linear navigation model.
   - **Ordered actions:** Establish ownership under `frontend/src/features/move-history/` rather than the low-level design-system folder because the component owns chess-domain concepts such as Ply, SAN, and the initial position while serving multiple future consumers. Define a domain-neutral controlled entry type, active-Ply selection callback, initial-position representation, linear bounds, and previous/next/Home/End navigation semantics without importing Viewer or Repertoire state. Add pure tests for initial-position handling, move ordering, active selection, bounds, and the absence of branch/variation behavior.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/move-history/moveHistoryModel.test.ts` (bash tool timeout: `120000 ms`).
   - **Breakpoint:** None; the controlled contract and linear semantics are settled by the upstream direction.
   - **Escalate if:** The shared contract requires route-owned state, a variation/tree model, a new identity, or a product decision about history semantics.
2. **complete** - Implement the CMT-styled controlled component and focused accessibility behavior.
   - **Ordered actions:** Render the initial position and SAN moves as an accessible linear history with a clear active row. Implement click selection and keyboard previous/next/Home/End navigation through the controlled callback, preserve predictable focus when the active entry changes, and scroll the active entry into view. Use existing CMT tokens and typography, established focus treatment, reduced-motion handling, and forced-colour-safe styling; do not create a low-level design-system primitive or add a dependency. Add focused component tests for controlled synchronization, click and keyboard selection, focus behavior, active-row scrolling, initial position, reduced motion, forced colours, and axe coverage.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/move-history/MoveHistory.test.tsx` (bash tool timeout: `120000 ms`).
   - **Breakpoint:** None for product direction; preserve the existing CMT visual and accessibility conventions rather than inventing a palette or layout system.
   - **Escalate if:** Styling needs new global tokens, a new primitive ownership decision, a dependency, route integration, or behavior beyond the settled linear keyboard and focus contract.
3. **complete** - Demonstrate the reusable result in Storybook and complete the accepted human breakpoint.
   - **Ordered actions:** Add a synthetic Storybook story for an initial position plus a representative linear SAN history with play assertions for click selection, active synchronization, keyboard previous/next/Home/End navigation, and accessible focus. Add only the Storybook discovery configuration needed for `frontend/src/features/move-history/**/*.stories.@(ts|tsx)`. Review the story at a usable narrow and wide presentation, including active-row visibility and focus treatment, before closeout.
   - **Focused proof:** `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/move-history` (bash tool timeout: `300000 ms`).
    - **Breakpoint:** Accepted. The user rejected the initial visual design, made authoritative edits at the required breakpoint, and accepted the revised direction by instructing closeout. User-owned post-edit verification is deferred by explicit instruction.
   - **Escalate if:** The visual review requires a new design system, route-specific composition, a change to accepted controls, horizontal overflow that cannot be fixed within the bounded component, or any excluded behavior.

Stages are sequential; no stage runs in parallel. A passing stage receipt remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment.

## Progress and decisions
- **Stage 1:** complete - proof: focused pure navigation tests passed (10 tests; Vitest duration 3.61s); breakpoint: none.
- **Stage 2:** complete - proof: focused component, accessibility, focus, and scrolling tests passed (7 tests; Vitest duration 1.57s); breakpoint: none.
- **Stage 3:** complete - pre-edit focused Storybook interaction proof passed (2 tests; Vitest duration 3.20s); the human visual/accessibility breakpoint is complete and accepted after the user's authoritative redesign.
- **Post-edit verification:** The user is running all post-edit tests/checks outside this workflow; revalidation and the listed closeout selectors are deferred by explicit user instruction. The retained pre-edit proofs do not validate the later user edits.
- **Decision:** Ownership is the shared domain feature `frontend/src/features/move-history/`, not `frontend/src/features/design-system/`, because SAN/Ply/initial-position semantics are domain-specific while the component is shared by future route consumers.

## Proof
- Stage 1 pure model proof: `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/move-history/moveHistoryModel.test.ts` (bash tool timeout: `120000 ms`) passed (10 tests; Vitest duration 3.61s).
- Stage 2 component and accessibility proof: `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/move-history/MoveHistory.test.tsx` (bash tool timeout: `120000 ms`) passed (7 tests; Vitest duration 1.57s).
- Stage 3 browser-backed Storybook proof: `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/move-history` (bash tool timeout: `300000 ms`) passed (2 tests; Vitest duration 3.20s); this historical receipt predates the accepted human visual/accessibility breakpoint.
- The Stage 1, Stage 2, and Stage 3 focused proofs above were captured before the user's visual edits and are preserved as historical receipts; they do not validate the later edits.
- Because the Storybook discovery configuration changes, closeout may run only required invalidated selectors: `timeout 900s .venv/Scripts/python.exe scripts/check.py --only "Storybook build" -q` (bash tool timeout: `900000 ms`), `timeout 300s .venv/Scripts/python.exe scripts/check.py --only "TypeScript type check" -q` (bash tool timeout: `300000 ms`), `timeout 300s .venv/Scripts/python.exe scripts/check.py --only "ESLint check" -q` (bash tool timeout: `300000 ms`), `timeout 180s .venv/Scripts/python.exe scripts/check.py --only "Prettier check" -q` (bash tool timeout: `180000 ms`), and `timeout 60s .venv/Scripts/python.exe scripts/check.py --only "Source size check" -q` (bash tool timeout: `60000 ms`). Do not repeat valid focused proof or run a route E2E suite for this foundation-only outcome.
- The post-edit revalidation and the closeout selectors listed above were not run in this workflow and are deferred to the user by explicit instruction; no post-edit passing evidence is claimed.
- Quality independently audits retained evidence and fills only missing or invalidated checks. Closeout uses `scripts/check.py --only` selectors only for required gaps; no `--fix` is authorized by this Plan. For this closeout, that user-owned verification is outside the workflow.

## Escalation boundaries
- Any request to wire the component into `/viewer` or `/repertoire`, change `BoardControl`, `GameContext`, repertoire session semantics, or introduce route-owned state belongs to a later master-plan slice.
- Any request for variations, branch management, a move tree, multiple preferred moves, training behavior, board/evaluation changes, Position Reach Frequency, effective-date behavior, backend/API/data/storage work, or Line Library ownership is outside H1.
- Any need for a new dependency, global token, design-system primitive, identity, API, schema, migration, destructive action, or changed acceptance decision requires coordinator escalation.
- Any inability to keep source under 500 lines or tests under 700 lines requires splitting the stage without changing the outcome or escalating if the outcome would change.

## Visible result
> A human can open the Move History Storybook story, select the initial position or any SAN move, navigate with keyboard previous/next/Home/End, and see the active row remain clearly focused and in view using CMT styling.
