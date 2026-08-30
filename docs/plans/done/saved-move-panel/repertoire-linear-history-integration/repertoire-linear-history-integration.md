# Repertoire Linear History Integration - one shared history keeps stored and local positions synchronized

> **Status:** complete - Stage 3 focused proof passed and the signed-off visual review was accepted

- **Read trigger:** Read before implementing the R1 Repertoire Builder history integration or changing its
  focused proof.
- **Upstream:** [Saved Move Panel master plan](../../../../master-plans/saved-move-panel/saved-move-panel.md);
  [completed H1 shared linear Move History Plan](../../../done/saved-move-panel/shared-linear-move-history/shared-linear-move-history.md)

## Outcome

Make `/repertoire` use the completed controlled Move History for one linear representation of its stored prefix
and local SAN line. Selecting any represented Ply, using keyboard navigation, or using Previous/Next keeps the
active history entry, board FEN, current Ply, position description, and repertoire workflow reads on the same
position. Preserve immediate opponent moves, staged bottom-side moves, staging cancellation on navigation, and
linear local replacement that truncates only later continuation.

## Scope

- **Included:** A repertoire-owned controlled input combining the stored prefix and local continuation; arbitrary
  represented-history selection; Previous/Next/Home/End synchronization through one selection path; shared active
  focus and visibility; current board, last-move, current-Ply, position-description, and workflow synchronization;
  existing staging cancellation on navigation; opponent immediacy; local SAN replacement and later-continuation
  truncation; focused unit tests; repertoire Storybook stories and helpers; the existing targeted browser proof; and
  only the feature CSS needed to retain the established layout and constrained-width behavior.
- **Expected areas:** `frontend/src/features/repertoire-builder/positionPickerSession.ts`,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireSessionPanel.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireSessionPanel.module.css` only if needed,
  `frontend/src/features/repertoire-builder/positionPickerSession.test.ts`,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx`,
  `frontend/src/features/repertoire-builder/repertoireBuilderStoryHelpers.ts`,
  `frontend/src/features/repertoire-builder/repertoireBuilderStoryAssertions.ts`,
  `frontend/src/features/repertoire-builder/repertoireBuilderStoryRender.tsx`, and
  `tests/e2e/repertoire-builder-storybook.spec.ts`.
- **Excluded:** Changes to the shared Move History contract or implementation; `/viewer`; R2 state-driven panel,
  effective-date, and Position Reach Frequency work; backend, API, persistence, or storage changes; variations,
  multiple preferred moves, training behavior, new dependencies or tokens, Line Library work, new browser profiles,
  `Scratch/`, historical records, commits, pushes, and unrelated changes.

## Stages

1. **complete** - Extend the pure session selection/navigation seam for the combined stored prefix and local line.
   - **Ordered actions:** Keep the repertoire session as the owner of current position and local continuation while
     deriving one absolute-Ply linear representation from the complete stored prefix followed by local moves. Add
     the pure selection and bounds behavior needed to select any represented prefix or local Ply and to map it back
     to `currentPosition`, `currentPly`, and the local continuation cursor without dropping later local moves during
     navigation. Clear `stagedMove` on every history transition. Preserve the existing append path: an accepted
     replacement at a supported local cursor truncates only later local positions and move records, bottom-side moves
     remain staged, and opposing moves remain immediate. Add focused pure tests for prefix/local ordering, arbitrary
     selection, Previous/Next/Home/End bounds, staging cancellation, opponent immediacy, and replacement truncation.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/repertoire-builder/positionPickerSession.test.ts`
     (bash tool timeout: `150000 ms`) passed (12 tests; Vitest duration 1.12s).
   - **Breakpoint:** None for the settled linear model; pause before implementation if selecting or playing from an
     earlier stored-prefix position cannot be expressed without changing move identity or branch semantics.
   - **Escalate if:** Prefix/local identities, earlier-prefix play, or replacement requires a new move, branch, or
     ownership rule.
2. **complete** - Replace plain SAN presentation with controlled shared Move History and route all navigation through
   the session selection path.
   - **Ordered actions:** Build the controlled Move History input from the stored prefix plus the full local line,
     using their existing absolute Ply and SAN values, and pass the session's current Ply as the controlled active
     value. Replace the duplicate plain SAN paragraph in the repertoire session surface with the shared component;
     do not alter the shared component's contract. Route Move History selection, its keyboard Previous/Next/Home/End
     callbacks, and BoardControl Previous/Next through one repertoire selection handler that cancels promotion and
     staging/workflow drafts before updating the session. Derive control bounds from the combined represented history,
     keep active focus and automatic visibility with the shared component, and ensure the selected session position
     drives the board FEN, last move, current-Ply/origin text, position description, and preferred-move/context
     workflow reads. Preserve the accepted board and evaluation behavior, saved-move play path, opponent immediacy,
     and bottom-side staging semantics. Add focused synchronization assertions for click, keyboard, buttons, active
     row, board position, description, current Ply, workflow FEN, staging cancellation, and no duplicate plain text.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
     (bash tool timeout: `150000 ms`) passed (43 tests; Vitest duration 15.37s).
   - **Breakpoint:** None for composition; preserve H1's CMT styling, focus, scrolling, reduced-motion, and
     forced-colour behavior rather than creating a new repertoire visual hierarchy.
   - **Escalate if:** Integration requires a Move History contract change, a new route owner, a new visual hierarchy,
     or behavior outside the approved linear session and workflow boundaries.
3. **complete** - Update focused tests, stories, existing browser proof, and prepare wide/constrained human visual
   review.
   - **Ordered actions:** Extend repertoire unit coverage and Storybook helpers/assertions for stored-prefix and local
     entries, arbitrary selection, active-row focus/visibility, Home/End bounds, navigation cancellation, opponent
     immediacy, and replacement truncation. Update the existing repertoire Workspace and Session Panel stories so
     the shared history is demonstrable at wide and constrained widths, including a stored prefix plus local line and
     a staged navigation case. Update `tests/e2e/repertoire-builder-storybook.spec.ts` to prove the combined history,
     synchronized board/current Ply/description/workflow state, represented bounds, and preserved layout/accessibility
     behavior. Run the focused Storybook and browser proof, then stop for human review at 1280x900 and 412x915 of
     active-row visibility, keyboard focus, constrained layout, and absence of horizontal overflow.
   - **Focused proof:** `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/repertoire-builder`
     (bash tool timeout: `360000 ms`); then `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`
     (bash tool timeout: `660000 ms`).
    - **Breakpoint:** None; the user explicitly signed off the required 1280x900 and 412x915 visual review of
      active-row visibility, keyboard focus, constrained layout, and absence of horizontal overflow.
   - **Escalate if:** The review requires a new visual direction, a new browser profile, changes to accepted controls,
     or behavior outside this slice.

Stages are sequential; no stage runs in parallel. A passing proof item remains valid until a later change affects
its command, inputs, exercised behavior, configuration, dependencies, or environment.

## Progress and decisions

- **Stage 1:** complete - proof: focused pure session test passed (12 tests; Vitest duration 1.12s); breakpoint:
  none; the settled single-line model is preserved and no earlier-prefix play rule was added.
- **Stage 2:** complete - proof: combined session and Workspace synchronization test passed (43 tests; Vitest
  duration 15.37s); breakpoint: none; shared Move History contract and route ownership remain unchanged.
- **Stage 3:** complete - Storybook proof passed (33 tests; Vitest duration 16.35s), targeted browser proof passed
  (6 tests; Playwright duration 44.5s); breakpoint: none; the user explicitly accepted the required 1280x900 and
  412x915 visual review covering active-row visibility, keyboard focus, constrained layout, and absence of
  horizontal overflow.
- **Decision:** The completed H1 controlled Move History remains unchanged; repertoire session state remains the
  owner of the combined stored-prefix/local-line selection and synchronization.

## Proof

- Stage 1 pure session proof: `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/repertoire-builder/positionPickerSession.test.ts`
  (bash tool timeout: `150000 ms`) passed (12 tests; Vitest duration 1.12s).
- Stage 2 session and Workspace synchronization proof: `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
  (bash tool timeout: `150000 ms`) passed (43 tests; Vitest duration 15.37s).
- Stage 3 Storybook proof: `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/repertoire-builder`
  (bash tool timeout: `360000 ms`) passed (33 tests; Vitest duration 16.35s).
- Stage 3 targeted browser proof: `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`
  (bash tool timeout: `660000 ms`) passed (6 tests; Playwright duration 44.5s).
- Stage 1, Stage 2, and Stage 3 implementation and focused behavioral proofs are complete. The user explicitly
  signed off the required 1280x900 and 412x915 human visual review. Lint, formatting, broad build, source-size,
  aggregate, and maintenance checks are outside this Plan.

## Acceptance

- One shared linear history covers the stored prefix and local moves; click, keyboard, and button navigation
  synchronize the active row, board FEN, current Ply, position description, and workflow reads.
- Home and End reach the represented bounds, while staging cancellation, opponent immediacy, and linear local
  truncation/replacement remain intact.
- The plain SAN duplicate and persistence changes are absent, focused automated proof passes, and wide/constrained
  human review passes.
- **User visual sign-off:** The user accepted the required 1280x900 and 412x915 review, including active-row
  visibility, keyboard focus, constrained layout, and absence of horizontal overflow.

## Escalation boundaries

- Any need for a new prefix/local identity, earlier-prefix play rule, branch or variation model, or changed
  truncation semantics.
- Any change to the shared Move History contract, Viewer behavior, public route ownership, accepted board/evaluation
  behavior, workflow mutation authority, backend/API/data/storage, or persistence.
- Any new dependency, token, browser profile, destructive behavior, Line Library decision, training behavior, or
  multiple-preferred-move behavior.
- Any visual review that needs a new hierarchy or design direction rather than the existing CMT styling, or any
  acceptance decision beyond the approved synchronization and linear-history outcome.

## Visible result

> On `/repertoire`, a human can select any stored-prefix or local move in one Move History—or use its keyboard and
> Previous/Next navigation—and see the active row, board, current Ply, description, and workflow state agree while
> staging, opponent immediacy, and linear replacement continue to behave as before.
