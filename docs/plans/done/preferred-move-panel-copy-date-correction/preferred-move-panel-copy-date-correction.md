# Preferred-move panel copy/date correction - The runtime card matches the approved date-free panel while retaining effective-date behavior

> **Status:** done - Plan completed after explicit user visual acceptance of the corrected production Storybook result and content-sized overflow behavior

- **Read trigger:** Read before correcting the runtime preferred-move panel, after any context rollover, and at the Stage 3 visual breakpoint.
- **Upstream:** The signed-off Storybook candidate is the primary visual and copy authority: `frontend/src/features/repertoire-builder/PreferredMovePanelExploration.tsx`, `frontend/src/features/repertoire-builder/PreferredMovePanelExploration.module.css`, and `frontend/src/features/repertoire-builder/PreferredMovePanelExploration.stories.tsx`. `experiments/mock-ups/preferred-move/standalone.html` is secondary evidence. Current runtime/workflow/API files govern behavioral and contract meaning. `docs/plans/done/preferred-move-panel-integration/` is historical and remains unchanged.

## Outcome

Correct the production preferred-move panel so its visible copy and composition match the approved Saved → Staged candidate. Every rendered state remains truthful and operable, while effective-date capability stays fully wired in workflow, API, backend, parsing, normalization, request/response, and persistence layers without rendering effective-date UI in the panel.

In matching state specifically, render the title/meta/status pill, Saved → Staged boxes, and exactly two footer actions in order: disabled `Matches saved`, then visible-label `Remove`; render no additional button, helper, consequence, or effective-date content.

## Scope

- **Included:** Runtime panel composition and copy; date-rendering removal from the panel only; action presentation; overflow-safe responsive CSS; focused panel/action/workspace tests, stories, assertion helpers, Storybook proof, and bounded browser visual proof.
- **Expected areas:**
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.module.css`
  - `frontend/src/features/repertoire-builder/PreferredMoveActionButtons.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.test.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.stories.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx`
  - `frontend/src/features/repertoire-builder/repertoireBuilderStoryAssertions.ts`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
- **Excluded:** The approved exploration files and HTML mock-up; `preferredMoveWorkflowState.ts`; `preferredMoveApi.ts`; backend, API, repository, database, parsing, normalization, request/response, and persistence contracts; `PreferredMovePrimitives.tsx` date primitives; shared tokens, shared components outside the expected areas, routes, dependencies, unrelated features, and broad refactors. Do not alter completed historical Plans, unrelated worktree changes, or proof-only `PreferredMoveWorkflow.stories.tsx`. Do not commit or push.

## Design fidelity

- **Authority:** The three `PreferredMovePanelExploration` files govern production visual composition, normal-state copy, geometry, and responsive structure. The standalone mock-up is secondary copy/layout evidence. Existing runtime files remain authoritative for state meaning, effective-date contracts, accessibility, and workflow behavior.
- **Excluded artifact content:** The HTML demo switcher, mock-up scripts, annotations, disposable controls, and any date-only panel presentation not present in the approved outcome.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| Panel hierarchy | `Preferred move` title/meta, status pill, Saved box, connector, Staged box, then the action footer | Bind real runtime metadata, SAN/UCI facts, tones, and action callbacks; retain required semantic names | Stage 1 panel proof and Stage 3 visual review |
| State copy and mapping | First-choice uses the staging-new composition with dynamic `Save <SAN>`; unsavable uses `Not in Corpus` and exact corpus guidance; saved uses the saved composition and `Remove`; replacement uses Saved → Staged with dynamic Save and Remove; matching uses the approved matching composition | Keep truthful exceptional compatibility states without adding date-only content or duplicating consequence/helper copy | Stage 1 and Stage 2 assertions/stories |
| Matching footer | Exactly disabled `Matches saved` followed by visible-label `Remove`, with no extra button, helper, consequence, or effective-date content | Use production Button and Remove implementations and existing callbacks | Stage 1 component proof, Stage 2 workspace proof, and Stage 3 browser review |
| Normal geometry and responsive structure | 256px desktop card, 360px card below the 40rem container breakpoint, 88px Saved/Staged boxes, bottom-pinned actions, and vertical Saved → connector → Staged stacking below the breakpoint | Adjust height, flex, wrapping, `min-width`, and content sizing to prevent clipping; content-sized exceptional shells are allowed only when fixed normal geometry would hide truthful feedback | Stage 1 geometry assertions and Stage 3 checks at desktop, 640px, 480px, and 412px |
| Effective-date capability | `date/dateEdit/onDateChange` panel props, workflow state and return values, persisted `effectiveAt`, request/response forwarding, current blank `effective_at` mutation behavior, and all API/backend validation/history/persistence behavior | Remove only panel effective-date rendering and date-only panel sizing/classes; preserve date primitives for future UI | Stage 1/2 tests with a populated date assert no effective-date text, test ID, button, or helper is rendered |
| Existing interaction truth | Save/remove, saved-box keyboard staging, Remove confirmation/focus restoration, Retry, loading/read-error status, corpus and turn gates, mutation status/retention, live-region semantics, and accessibility checks | Place truthful compatibility feedback within overflow-safe content sizing without changing its behavior | Stage 2 focused proof and Stage 3 browser scenarios |

## Stages

1. **pending** - Correct runtime composition and copy, remove panel date rendering, and preserve contracts
   - **Actions:**
     1. Compare the runtime panel and action implementation with the approved candidate and the retained workflow contract. Keep all panel `date/dateEdit/onDateChange` props and callbacks, workflow state/return values, and API-facing behavior intact.
     2. Replace runtime-owned normal markup and copy with the candidate-derived hierarchy. Map first-choice, unsavable, saved, replacement, and matching states as specified above; use the real dynamic SAN in `Save <SAN>` and retain truthful saved/staged facts.
     3. Remove only effective-date panel markup, date-only test IDs, helpers, consequences, and sizing/classes. Ensure matching has exactly the two required footer buttons and no extra visible content. Keep production Button/Remove semantics, accessible labels, and callbacks.
     4. Update only the focused action and panel unit assertions needed for the new visible labels, action order/disabled state, semantic regions, dynamic move copy, retained hooks, and absence of effective-date UI when a date is populated.
   - **Focused proof:** From `G:\ChessMoveTrainer`, run only `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx"`; command timeout 120s and recommended bash tool timeout 150000ms.
   - **Acceptance:** The focused suite proves candidate composition/copy, matching’s exact two actions, dynamic Save/Remove behavior, preserved panel contract surface, and no effective-date panel rendering without changing workflow/API behavior.
   - **Breakpoint:** No product decision is expected. Escalate before changing the approved hierarchy, copy, action order, normal dimensions, or any preserved date/workflow contract.

2. **pending** - Update workspace assertions/stories and prove truthful edge-state compatibility
   - **Actions:**
     1. Update `repertoireBuilderStoryAssertions.ts`, `RepertoireBuilderWorkspacePreferredMove.stories.tsx`, `RepertoireBuilderWorkspaceWorkflow.test.tsx`, `RepertoireBuilderWorkspace.test.tsx`, and the focused runtime panel stories for the corrected visible composition and date-free panel.
     2. Cover empty, opponent-turn, loading, read-error, mutation, unsavable, saved, replacement, first-choice, and matching states without weakening save/remove, Retry, confirmation, focus restoration, keyboard saved-box staging, API request/response, axe, or no-overflow assertions.
     3. With an effective date populated, assert that the panel renders no effective-date text, test ID, button, helper, or consequence while workflow persisted-date behavior, saved fact `effectiveAt`, and current blank `effective_at` mutation behavior remain covered.
     4. Keep exceptional status, guidance, and error content truthful; do not force fixed normal geometry to clip it and do not introduce a replacement visual treatment without escalation.
   - **Focused proof:** From `G:\ChessMoveTrainer`, run only `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx"`; command timeout 120s and recommended bash tool timeout 150000ms.
   - **Acceptance:** Both focused workspace files prove all listed compatibility states and preserved interaction/API behavior, while assertions and stories reject date-only panel output and retain truthful facts.
   - **Breakpoint:** Escalate if removing date presentation or fitting an exceptional state would require changing workflow ownership, a contract, a genuine control, or the approved normal visual treatment.

3. **pending** - Add overflow proof, make only necessary layout adaptations, and obtain visual acceptance
   - **Actions:**
     1. Add targeted long-copy scenarios using real/dynamic metadata, long SAN/UCI values including promotion `e8=Q+` / `e7e8q`, long status or guidance text, empty/replacement guidance, and action labels. Prove wrapping, flex shrink, `min-width`, content sizing, and action behavior rather than relying on the 256px/360px anchors as permission to clip.
     2. Run only the targeted Storybook test files for the approved exploration authority, runtime panel, preferred-move workspace, and preferred-move workflow: `PreferredMovePanelExploration.stories.tsx`, `PreferredMovePanel.stories.tsx`, `RepertoireBuilderWorkspacePreferredMove.stories.tsx`, and proof-only `PreferredMoveWorkflow.stories.tsx`.
     3. Start Storybook with a finite server timeout when live review is needed: `timeout 90s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run storybook --workspace frontend -- --ci --no-open"` (command timeout 90s; recommended bash tool timeout 120000ms). Use browser operations with a maximum 30-second timeout each.
     4. Review matching, first-choice, saved, replacement, not-in-corpus, empty, opponent-turn, loading, read-error, and mutation at desktop, exactly 640px, 480px, and 412px. Check long metadata, promotion values, guidance/status/actions, card and box heights, stacking/connector direction, clipping, overlap, horizontal overflow, and text escaping. With a populated effective date, verify no effective-date date text, test ID, button, or helper is visible.
     5. Adjust only panel layout mechanics—heights, flex behavior, wrapping, minimum widths, and content sizing—as necessary to keep real content visible while retaining the approved normal anchors. Stop at the explicit user visual breakpoint for review; incorporate any user edit as authoritative and rerun only invalidated proof.
   - **Focused proof:** From `G:\ChessMoveTrainer`, run only `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test-storybook --workspace frontend -- --run src/features/repertoire-builder/PreferredMovePanelExploration.stories.tsx src/features/repertoire-builder/PreferredMovePanel.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx"`; command timeout 120s and recommended bash tool timeout 150000ms. Retain earlier proof until a Stage 3 change invalidates it.
   - **Acceptance:** Targeted Storybook and browser proof passes at all four widths with no clipping, overlap, horizontal overflow, or escaped text; the production panel is visually faithful to the approved candidate and remains date-free at the UI surface without altering effective-date capability.
   - **Breakpoint:** User/coordinator visual acceptance is required before completion. If the approved anchors cannot contain real content without a new visual/product decision, stop and escalate rather than clipping, hiding, or weakening assertions.

Stages are sequential; no stages run in parallel. Later proof is rerun only when a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment.

## Progress and decisions

- **Stage 1:** complete - proof: PASS, 2 focused unit files and 25 tests; breakpoint: preserve the existing panel props/callbacks and all workflow/API contracts while removing only panel date presentation.
- **Stage 2:** complete - proof: PASS, 2 focused workspace unit files and 41 tests; breakpoint: preserve save/remove, Retry, confirmation, keyboard, accessibility, request/response, and truthful exceptional-state behavior.
- **Stage 3:** complete - proof: PASS, targeted Storybook proof for 4 files and 43 tests after bounded stale-story expectation repair; browser review passed at desktop, exact 640px, 480px, and 412px with no clipping, overlap, horizontal overflow, or escaped text; breakpoint: user accepted the corrected production Storybook visuals and content-sized overflow behavior.
- **Decision:** This is a focused correction to the completed integration, not a new product or API design. The approved exploration candidate remains unchanged and is the visual authority.
- **Decision:** Effective-date data and hooks remain fully wired for future UI; only preferred-move panel rendering of effective-date content and date-only layout treatment are removed.
- **Decision:** Runtime Save copy uses the staged move SAN while the reusable action keeps its default `Save` label; matching keeps exactly disabled `Matches saved` followed by `Remove`.
- **Decision:** Fixed 256px/360px card and 88px box sizes are normal-state fidelity anchors, while real content must remain visible through bounded layout adaptations or an escalated decision.
- **Decision:** Workspace assertions and stories now require dynamic `Save <SAN>` labels, exact footer action order, and no effective-date panel output across normal and compatibility states.
- **Acceptance:** User reviewed the corrected production Storybook visuals and content-sized overflow behavior and said, “It'll do, close the plan.” This explicitly accepts the visual result and authorizes closeout.

## Proof

- Panel/action unit files only: PASS — from `G:\ChessMoveTrainer`, command `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx"`; command timeout 120s; bash tool timeout 150000ms; 2 files and 25 tests passed in 6.26s. Covers candidate panel hierarchy/copy, dynamic Save and Remove behavior, exact matching action order/disabled state, retained saved-box keyboard/focus and error/mutation behavior, effective-date contract inputs, and absence of effective-date UI. No dependencies changed.
- Workspace unit files only: PASS — from `G:\ChessMoveTrainer`, command `timeout 120s powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& npm.cmd run test --workspace frontend -- --project=unit --run src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx"`; command timeout 120s; bash tool timeout 150000ms; 2 files and 41 tests passed in 32.93s. Covers workspace edge states, exact dynamic Save and matching action behavior, save/remove confirmation and retention, keyboard/session staging, Retry/error/mutation feedback, accessibility, API request arguments, and populated-date absence from the panel.
- Story-file-targeted Storybook proof: PASS — `PreferredMovePanelExploration.stories.tsx`, `PreferredMovePanel.stories.tsx`, `RepertoireBuilderWorkspacePreferredMove.stories.tsx`, and `PreferredMoveWorkflow.stories.tsx`; 4 files and 43 tests passed after bounded stale-story expectation repair. No checks were rerun during closeout.
- Browser proof: PASS — matching, first-choice, saved, replacement, not-in-corpus, empty, opponent-turn, loading, read-error, and mutation at desktop, exactly 640px, 480px, and 412px; long metadata and promotion `e8=Q+` / `e7e8q`; guidance/status/actions; no clipping, overlap, horizontal overflow, or text escaping; and no effective-date text, test ID, button, or helper with a populated effective date. No checks were rerun during closeout.
- Do not run lint, formatting, broad type/build, source-size, aggregate, E2E, or repository-hygiene checks in this Plan. Passing behavioral proof remains valid until an affecting change.

## Escalation boundaries

- Do not choose or change a product, visual, API, data, dependency, destructive, ownership, or acceptance decision beyond this packet. Escalate any need to change the approved copy, hierarchy, action order, 40rem breakpoint, normal dimensions, or exact matching footer.
- Do not alter workflow state derivation, parsing/normalization, API clients or payloads, backend validation/history/persistence, request/response fields, database/repository contracts, date primitives, routes, shared tokens, or dependencies. Escalate if the date-free panel cannot be achieved while preserving them.
- Do not hide, clip, remove, or weaken a genuine save/remove/Retry/confirmation/keyboard/accessibility/API behavior to fit a card. Escalate if content-sized compatibility layout or bounded CSS adaptation is insufficient.
- Do not modify the approved exploration artifacts or completed historical records. Do not add unapproved ownership paths, and stop at the Stage 3 user visual breakpoint before declaring the outcome complete.

## Visible result

> The live preferred-move panel shows the approved Saved → Staged copy and matching footer with no effective-date UI, while all date persistence and workflow behavior still works and no real text is clipped or overflowing.
