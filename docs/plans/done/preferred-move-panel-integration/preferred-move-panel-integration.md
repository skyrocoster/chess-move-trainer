# Preferred move panel integration - The runtime workspace shows the approved Saved → Staged panel without losing workflow behavior

> **Status:** done - all three stages accepted; production visual parity approved

- **Read trigger:** Read before implementing or validating the runtime preferred-move panel integration; reread after any context rollover or coordinator breakpoint.
- **Upstream:** The signed-off production-backed Storybook candidate is the visual authority: [`PreferredMovePanelExploration.tsx`](../../../frontend/src/features/repertoire-builder/PreferredMovePanelExploration.tsx), [`PreferredMovePanelExploration.module.css`](../../../frontend/src/features/repertoire-builder/PreferredMovePanelExploration.module.css), and [`PreferredMovePanelExploration.stories.tsx`](../../../frontend/src/features/repertoire-builder/PreferredMovePanelExploration.stories.tsx). [`standalone.html`](../../../experiments/mock-ups/preferred-move/standalone.html) is secondary visual/copy evidence. Existing preferred-move workflow, API, caller, and focused-test files govern runtime meaning and behavior.

## Outcome

Replace the runtime preferred-move presentation with the approved low-duplication Saved → Staged design. Normal runtime states should have the approved dark token styling, fixed card and choice-box geometry, exact approved copy, responsive stacking, and production controls, while all existing save/remove workflow, confirmation, loading, error, date-gate, corpus, turn, mutation-retention, saved-move staging, and accessibility behavior remains truthful and operable.

## Scope

- **Included:** Runtime preferred-move markup and CSS; dynamic mapping from the existing position model; preserved genuine controls and feedback; focused component/workspace tests, Storybook stories, assertion helpers, responsive proof, and visual acceptance.
- **Expected areas:**
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.module.css`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.test.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.stories.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`
  - `frontend/src/features/repertoire-builder/repertoireBuilderStoryAssertions.ts`
- **Excluded:** Workflow hooks and model derivation, API clients and payloads, backend code, `RepertoireSessionPanel` and workspace caller contracts, shared tokens, shared design-system components, unrelated routes, broad refactors, and repository-maintenance checks. The three exploration Storybook files remain unchanged and are not deleted in this Plan.

## Design fidelity

- **Authority:** The approved Storybook candidate governs visual composition and interaction presentation. `standalone.html` supplies secondary settled copy and visual evidence. Existing runtime files govern behavior and repository meaning.
- **Excluded artifact content:** HTML demo switcher, mock-up scripts, toast, catalogue alternatives, and any runtime-independent fixture state implementation.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| Candidate normal card and Saved → Staged structure | Low-duplication hierarchy, dark surface, `Preferred move` heading/meta, status pill, Saved box, connector, Staged box, action row | Bind labels, moves, dates, tones, and actions to `RepertoirePositionModel`; retain runtime semantic labels where needed for accessibility | Stage 1 panel tests and desktop visual breakpoint |
| Candidate normal geometry | 256px desktop card; each choice box 88px; action row at the bottom | Exceptional loading/error/gate content may use a content-sized compatibility shell if fixed height would clip truthful feedback | Stage 1 component proof; visual review at desktop |
| Candidate normal states | Exact four selected presentations: `staging_new`, `not_in_corpus`, `idle_saved`, and `matches`; exact “Not in Corpus” copy | Map runtime relationships and dynamic SAN/UCI/date values into these presentations; add necessary runtime variants without inventing product states | Stage 2 relationship and edge-state tests/stories |
| Candidate controls | Production Button geometry, visible-label Remove, disabled “Matches saved”, primary before Remove | Use the existing `Button` and `RemovePreferredMoveButton`; keep dynamic Save labels where required by the model | Stage 1/2 action assertions and keyboard proof |
| Candidate responsive breakpoint | A 40rem container query stacks Saved, downward connector, and Staged; narrow card is 360px and boxes remain 88px | Apply the query to the canonical runtime panel container and verify actual session-lane widths in addition to Storybook | Stage 3 checks at desktop, 640px boundary, and constrained 412/480px widths |
| Existing runtime behavior | Saved-box keyboard staging, Remove confirmation/focus restoration, date-gate description, loading/error/Retry, corpus and turn gates, mutation retention, live status semantics | Place preserved controls or exceptional feedback in an ancillary/content-sized compatibility area when the approved normal card has no room | Stage 2 focused component/workspace proof and visual breakpoint |

## Stages

1. **completed** - Canonical runtime presentation and styles
   - **Actions:**
     1. Read the approved candidate and current panel contract, then retain the existing model derivation and callbacks.
     2. Replace only the panel’s normal relationship markup and presentation styles with candidate-derived Saved → Staged composition. Keep `data-state`, focused test IDs, semantic section/heading structure, and production Button/Remove implementations stable where possible.
     3. Map `first-choice` to `staging_new`, `saved` to `idle_saved`, and `matching` to `matches`. Render `replacement` with the same Saved → Staged structure using dynamic saved/staged facts and Save/Remove behavior.
     4. Preserve saved-box activation as a real keyboard button with its existing accessible name when the saved move is playable.
     5. Update the focused panel tests/story assertions for approved visible labels, status text, box dimensions, action ordering, and token-backed responsive CSS.
   - **Focused proof:** `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/PreferredMovePanel.test.tsx"` from `G:\ChessMoveTrainer`; command timeout 120s; recommended bash tool timeout 150000ms.
   - **Breakpoint:** No product decision. Escalate before changing the approved normal composition or removing a genuine control because of space constraints.

2. **completed** - Retained edge-state behavior and workspace proof
   - **Actions:**
     1. Preserve `empty`, `unknown`, loading, typed read errors, `ownTurn=false`, `saveability=unsavable`, and pending mutation states without presenting false normal-state facts.
     2. Render `saveability=unsavable` with the approved “Not in Corpus” treatment while retaining saved facts and Remove when present; preserve blocked staged facts when present. Do not assume an unsavable context cannot have an assigned preferred move.
     3. Keep the disabled Change effective date action and accessible unavailable-date description, Remove confirmation dialog, Retry actions, live mutation status, and disabled persistence controls. If these cannot fit inside the fixed normal card, keep them in a clearly associated ancillary/content-sized area rather than hiding them.
     4. Update focused workspace tests, preferred-move stories, workspace stories, and assertion helpers without weakening API-call, confirmation, keyboard, axe, or no-overflow assertions.
   - **Focused proof:** `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx"` from `G:\ChessMoveTrainer`; command timeout 120s; recommended bash tool timeout 150000ms.
   - **Breakpoint:** If the approved card cannot preserve date-gate, confirmation, feedback, or unsavable-saved behavior without a new visual treatment, pause for coordinator/user direction.

3. **completed** - Focused behavioral and visual proof, then parity decision
   - **Actions:**
     1. Run the affected preferred-move and workspace Storybook stories only, including normal states, replacement, empty, loading/error, pending mutation, saved-box keyboard activation, confirmation, and constrained responsive scenarios.
     2. Review the canonical runtime panel at desktop width, exactly at the 640px container boundary, and at the existing constrained 412px plus 480px widths. Check card/box geometry, stacking, connector direction, clipping, overlap, overflow, and the ancillary compatibility content.
     3. Confirm the approved candidate files remain unchanged during integration and compare production output against them. Do not remove exploration files until production parity is established and the coordinator/user accepts cleanup.
     4. After parity acceptance, handle exploration-file deletion as a separate cleanup decision and proof action; it is not part of the integration implementation stage.
   - **Focused proof:** `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test-storybook --workspace frontend -- --run src/features/repertoire-builder/PreferredMovePanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx"` from `G:\ChessMoveTrainer`; command timeout 120s; recommended bash tool timeout 150000ms.
   - **Browser proof:** When live inspection is needed, start Storybook with `timeout 90s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run storybook --workspace frontend -- --ci --no-open"`; command timeout 90s; recommended bash tool timeout 120000ms. Use browser navigation/assertion operations with a recommended 30s per-operation timeout, then stop the temporary server. Review the affected workspace stories at desktop, 640px, 412px, and 480px widths.
   - **Breakpoint:** User/coordinator visual acceptance of production parity. User edits at this breakpoint are authoritative and must be incorporated before cleanup.

## Progress and decisions

- **Stage 1:** complete - proof: focused PreferredMovePanel unit suite passed (15 tests) after Stage 2 compatibility edits; breakpoint: none; canonical Saved → Staged runtime presentation and token-backed geometry are in place, with existing saved-box activation, date action, and Remove confirmation retained.
- **Stage 2:** complete - proof: focused workspace unit suites passed (41 tests); breakpoint: none; edge states, Not in Corpus treatment, retained facts, controls, workflow contracts, and accessibility assertions remain covered.
- **Stage 3:** completed - retained proof: focused Storybook passed (3 files / 42 tests), PreferredMovePanel unit proof passed (15 tests), and workspace focused unit proof passed (41 tests). Browser proof passed at desktop, exact 640px, 412px, and 480px, covering geometry, stacking, connectors, no overflow, matching/date-gate behavior, read-error Retry, Remove confirmation/focus restoration, and keyboard saved-box staging. User approved production visual parity, including the intentional content-sized compatibility adaptations at all four widths. Breakpoint: passed; no unexplained visual drift.
- **Decision:** Keep the approved exploration Storybook files unchanged throughout integration for traceability. Deletion, if desired, occurs only after production parity and explicit coordinator/user acceptance.
- **Stage 1 decision:** Use runtime-owned Saved/Staged presentation markup so the approved visible labels and fixed geometry can be adopted without changing the existing workflow/model, action, or shared primitive contracts. Retain runtime semantic names for the saved-choice region and saved-box activation.
- **Stage 2 decision:** Present unsavable contexts with the approved `Not in Corpus` status and copy while retaining assigned saved facts, blocked staged facts, disabled date action, and Remove. Update workspace assertions to the approved visible copy without weakening request, confirmation, keyboard, axe, or no-overflow checks.

## Proof

- `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/PreferredMovePanel.test.tsx"` — CWD `G:\ChessMoveTrainer`; command timeout 120s; **RETAINED PASS (15 tests)**; proves canonical panel composition, controls, semantic labels, fixed geometry/token CSS assertions, gates, and accessibility assertions.
- `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx"` — CWD `G:\ChessMoveTrainer`; command timeout 120s; **RETAINED PASS (41 tests)**; proves save/remove requests, confirmation, refresh retention, saved-box keyboard staging, date gate, failures, retained edge states, and axe coverage.
- `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test-storybook --workspace frontend -- --run src/features/repertoire-builder/PreferredMovePanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx"` — CWD `G:\ChessMoveTrainer`; command timeout 120s; **RETAINED PASS (3 files / 42 tests)**; proves affected Storybook interaction stories in headless Chromium.
- Live browser review at desktop, exact 640px, 412px, and 480px — **RETAINED PASS**; proves visual geometry, 40rem stacking, downward connector, no clipping/overflow, compatibility content placement, matching/date-gate behavior, read-error Retry, Remove confirmation/focus restoration, and keyboard saved-box staging. User approved production parity, including intentional content-sized shells (`325–532px`) and runtime compatibility controls.
- Do not run lint, formatting, broad type/build, source-size, aggregate, E2E maintenance, or repository-hygiene checks in this Plan. Passing behavioral proof remains valid until a later stage changes its command, inputs, exercised behavior, configuration, dependency, or environment.

- **Closeout:** completed - Stage 3 visual parity was explicitly approved by the user; all retained proof remained valid, no checks were rerun, the three exploration Storybook files remain unchanged, and the Plan moved to `docs/plans/done/preferred-move-panel-integration/`.

## Escalation boundaries

- Do not change workflow state derivation, API contracts, request payloads, backend behavior, caller contracts, shared tokens, shared primitives, dependencies, routes, or unrelated ownership.
- Escalate if preserving the disabled date action, Remove confirmation, saved-unsavable Remove, loading/error feedback, or accessibility semantics requires a new product or visual decision.
- Escalate if the 40rem breakpoint, fixed normal dimensions, approved copy, Saved → Staged direction, or action order must change.
- Do not delete or alter the approved exploration files until production parity is proven and cleanup is explicitly accepted.

## Visible result

> The live repertoire workspace shows the approved Saved → Staged preferred-move card while saves, removes, gates, errors, pending states, and keyboard behavior still work.
