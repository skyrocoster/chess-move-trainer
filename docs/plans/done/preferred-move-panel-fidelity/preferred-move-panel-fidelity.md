# Preferred Move Panel Fidelity - `/repertoire` stays readable and faithful to the selected two-box design

> **Status:** done - all three stages accepted; required human visual sign-off passed

- **Read trigger:** Read before changing the `/repertoire` `PreferredMovePanel`, its preferred-move primitives or
  styles, focused stories/tests, or bounded browser proof. Re-read the declared design references before the visual
  breakpoint.
- **Upstream:** [`experiments/mock-ups/preferred-move-panel/DESIGN.md`](../../../experiments/mock-ups/preferred-move-panel/DESIGN.md);
  [`experiments/mock-ups/preferred-move-panel/02-staged-move-is-the-proposal-final-choice.html`](../../../experiments/mock-ups/preferred-move-panel/02-staged-move-is-the-proposal-final-choice.html);
  [`docs/grilling-docs/design-exploration-funnel.md`](../../../grilling-docs/design-exploration-funnel.md);
  completed baseline [`docs/plans/done/preferred-move-panel/preferred-move-panel.md`](../../done/preferred-move-panel/preferred-move-panel.md);
  historical directional record [`docs/grilling-docs/DONE/saved-move-panel-redesign.md`](../../../grilling-docs/DONE/saved-move-panel-redesign.md)
  only as non-authoritative history. The historical record's referenced `experiments/mock-ups/saved-moves/saved-move.html`
  is absent and is not a dependency.

## Outcome

Make the implemented `/repertoire` preferred-move panel visually readable and faithful to the current selected
two-box design, especially inside the desktop session column, while preserving the accepted workflow, accessibility
semantics, and disabled effective-date behavior.

## Scope

- **Included:** Component-width-aware responsive layout; readable peer boxes; exact visible labels without appended
  punctuation; saved → connector → staged order; responsive connector direction and spacing; a token-backed circular
  consequence arrow; header and footer wrapping; and focused component/browser regression coverage.
- **Expected areas:**
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.module.css`
  - `frontend/src/features/repertoire-builder/PreferredMovePrimitives.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePrimitives.module.css`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.test.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.stories.tsx`
  - `tests/e2e/repertoire-builder-storybook.spec.ts`
- **Excluded:** Enabling, persisting, redesigning, or otherwise changing effective-date behavior; the disabled
  `Change effective date` action and `Date changes are temporarily unavailable` message remain unchanged. No API,
  storage, backend, model, Save/Remove semantics, board/history/session behavior, review-sheet chrome, dependency,
  page-grid, global-token, shared-Button-API, global redesign, historical-record, or unrelated test/maintenance work.

## Design fidelity

- **Authority:** `DESIGN.md` is the current semantic and repository-aware design authority. The selected HTML is the
  visual composition authority only for `article#live-panel`. The exploration funnel establishes that later user
  refinement supersedes earlier branches. The completed Plan records the implementation baseline and intentionally
  deferred date behavior.
- **Excluded artifact content:** The selected HTML's wordmark, hero, demo controls, side cards, coverage disclosure,
  annotations, footer, raw colors, private font, and review-sheet copy are not product UI.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| `DESIGN.md` §§5.1–5.6; HTML `#live-panel` and `.two-boxes` | One labelled panel shell, two peer boxes, saved → connector → staged order, one consequence | Use current panel/primitive ownership and CMT/Material tokens; no literal HTML values | Component proof retains the structure; visual breakpoint confirms readable hierarchy |
| `DESIGN.md` §§5.3, 5.5, 8.2 | Visible labels exactly `Current saved choice` and `Staged move`; no appended colon | Keep the saved-box accessible name descriptive and unchanged | Component proof checks exact visible labels and accessible saved-box activation |
| `DESIGN.md` §9.5; HTML media rules near lines 1165–1240 | Narrow component widths stack saved, connector, staged; connector points down; actions wrap in Save/date/Remove order | Use a local container-aware query or equivalent; do not change the page grid | Browser proof plus human review at the desktop session-column width and 412px |
| `DESIGN.md` §5.6; HTML `.consequence::before` near lines 749–764 | One fixed consequence sentence with a circular accent arrow cue | Use installed icons and semantic tokens rather than raw HTML colors | Component/browser review confirms the cue supports, but does not replace, the sentence |
| `DESIGN.md` §§5.8–5.9, 9.4; existing `Button` | Existing action labels, hierarchy, focus, feedback, and no-overflow semantics | Adjust only local wrapping/alignment around existing Button/action primitives | Component and browser proof retain actions, roles, focus, and no overflow |
| Completed Plan §§7–8 and 146–163 | Disabled date action, exact unavailable message, no calendar/request, no date contract change | None | All proof keeps the date action disabled and request-free |

## Stages

1. **completed - Correct the panel and primitive visual composition.** Translate the selected two-box composition to the
   available component width without changing workflow semantics.
   - **Ordered actions:** Re-read the selected `DESIGN.md`, the selected HTML panel boundary, and the completed Plan's
     date decision. Inspect the existing panel at the desktop session-column width and at 412px. Remove only the
     visible label punctuation that conflicts with the exact design labels. Add the local component/container-aware
     responsive behavior needed to stack the boxes, point the connector down, and wrap the header/footer readably at a
     narrow panel width. Add the circular consequence-arrow treatment using existing semantic tokens and installed
     icons. Preserve the current Button primitives, action labels/order, feedback, focus, relationship semantics, and
     disabled date scaffold. Do not change page layout or global tokens.
   - **Focused proof:** Bounded source review of only the changed JSX/CSS against the fidelity table, including a check
     that no date/API/workflow path was changed and that review-sheet content was not copied.
   - **Breakpoint:** Stop if the local responsive treatment cannot make the actual session column readable without a
     page-grid, global-token, shared-Button-API, or visual-direction decision.

2. **completed - Add focused component regression guards.** Make the remaining visual contract observable without
   coupling tests to implementation-private markup.
   - **Ordered actions:** Extend the existing `PreferredMovePanel` tests/stories to check exact visible box labels,
     saved-box accessible activation, saved/connector/staged DOM order, connector decorative semantics, consequence
     presence and circular-cue styling contract, action order/wrapping contract, and unchanged disabled-date
     messaging. Keep relationship, feedback, dialog, and action behavior assertions intact. Add only the focused
     assertions needed for the component-width layout; do not add a new browser surface or alter product semantics.
   - **Focused proof:** From `frontend`, run
     `timeout 150s npm exec -- vitest run --project unit src/features/repertoire-builder/PreferredMovePanel.test.tsx src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx`
     with Bash tool timeout `180000` ms.
   - **Breakpoint:** Stop if an assertion requires changing an accessible name, action label, date behavior, workflow
     contract, shared primitive API, or acceptance decision. Passing behavioral proof remains valid until a later stage
     changes its command inputs or exercised behavior.

3. **completed - Run bounded browser proof and obtain visual sign-off.** Prove the implemented panel in the existing
   Storybook surface, then stop at the required visual breakpoint.
   - **Ordered actions:** Use the existing `tests/e2e/repertoire-builder-storybook.spec.ts` scenarios and add only
     bounded checks needed to exercise the desktop session-column width and the 412px constrained width. Confirm exact
     labels, saved/connector/staged order and direction, readable wrapping, accessibility, action order, disabled-date
     request-free behavior, and no horizontal overflow. Perform human visual review against `article#live-panel` in
     the selected HTML; automated DOM, accessibility, and overflow checks do not establish fidelity alone.
   - **Focused proof:** From the repository root, run
     `timeout 180s npx playwright test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`
     with Bash tool timeout `240000` ms.
   - **Breakpoint:** Human visual sign-off is required at the desktop session-column width and 412px constrained
     width. Stop and return to the coordinator if either appearance requires a new visual direction, page-grid change,
     global token/API change, or any excluded behavior change. Do not treat the selected HTML's enabled date action or
     review-sheet chrome as acceptance requirements.

Stages are sequential; no stage runs in parallel. A passing proof item remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment. No lint, formatting, build, broad
type, source-size, aggregate, or repository-hygiene checks are required by this Plan.

## Progress and decisions

- **Dependency gate:** complete - the outcome, paths, upstream roles, exclusions, proof, and visual breakpoint are
  approved; no active matching Plan existed.
- **Decision:** `DESIGN.md` governs semantics and repository meaning; the selected HTML governs only the panel
  composition inside `article#live-panel`. Earlier saved-move-panel direction is historical evidence only.
- **Decision:** The disabled effective-date action and exact unavailable message remain unchanged; no date persistence
  or transport work is part of this Plan.
- **Stage 1:** completed - visual composition correction uses the named `preferred-move-panel` inline-size container with a 40rem local threshold, exact visible box labels, stacked saved/connector/staged order, a downward decorative connector, readable left-aligned action wrapping, and a token-backed circular consequence cue; the existing Button/action semantics and disabled date scaffold remain unchanged. Proof: bounded source and final diff review plus diagnostic Storybook inspection of the replacement story at approximately 368px and 349px panel widths confirmed one-column saved/connector/staged layout, downward connector transform, Save/date/Remove order with left-aligned actions, no document/body overflow, and a 24px circular consequence cue; no date/API/workflow path or review-sheet content changed. Breakpoint: not triggered; browser inspection was diagnostic only and Stage 3 visual sign-off remains pending.
- **Stage 2:** completed - focused component guards now cover the exact unpunctuated labels, saved-box activation,
  saved/connector/staged order, decorative connector and circular consequence cue contracts, action wrapping/order,
  and unchanged disabled-date messaging. Proof: the focused Vitest command passed 23 tests across 2 files with its
  150-second command timeout and `180000` ms Bash tool timeout. Only the focused panel test changed, so retained Stage
  1 browser evidence remains valid; the semantic/API/date breakpoint was not triggered.
- **Stage 3:** completed - the focused Playwright scenario `proves preferred panel fidelity at the desktop session
  column and 412px` passed in 11.6 seconds with a 180-second command timeout and `240000` ms Bash tool timeout. It
  covers labels, order/direction, wrapping/containment, decorative and accessibility semantics, the circular cue,
  Save/date/Remove order, disabled-date request-free behavior, and overflow at both target widths. The broader spec
  run also passed this scenario twice but reported four unrelated existing position-summary failures; those are
  report-only and were not repaired. Breakpoint: passed - the user approved both the desktop session-column and 412px
  constrained appearances on 2026-09-01.
- **Closeout:** completed - focused component and browser proof passed, the required visual breakpoint passed, and the
  Plan moved to `docs/plans/done/preferred-move-panel-fidelity/` without running unrelated maintenance checks.

## Proof

- From `frontend` (finite command timeout 150 seconds; Bash tool timeout `180000` ms):
  `timeout 150s npm exec -- vitest run --project unit src/features/repertoire-builder/PreferredMovePanel.test.tsx src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx`
- From the repository root (finite command timeout 180 seconds; Bash tool timeout `240000` ms):
  `timeout 180s npx playwright test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`
- These are the only required implementation checks. Passing behavioral proof is retained until an affecting change;
  independent Quality validation and complete maintenance runs remain separate workflows.

## Acceptance

The panel is faithful to the selected two-box design, readable in the desktop session column, and stacked correctly at
narrow component widths. It displays the exact labels `Current saved choice` and `Staged move`, keeps the connector and
circular consequence cue semantically decorative, wraps the header/footer in Save/date/Remove order, preserves
accessibility and no-overflow behavior, and leaves the accepted workflow plus disabled effective-date behavior
unchanged. Focused component proof, bounded browser proof, and human visual sign-off at the desktop session-column and
412px constrained widths all pass.

## Escalation boundaries

- Any new or changed product behavior, visual direction, copy beyond the settled exact labels, action semantics,
  accessibility contract, API, persistence, model, ownership, date behavior, board/history/session behavior, or
  acceptance criterion.
- Any need to change the page grid, global tokens, shared Button API, dependency set, or a global design-system
  primitive.
- Any inability to achieve readable component-width behavior with local panel/primitives changes.
- Any browser or human review failure requiring excluded work, review-sheet content, broad redesign, maintenance work,
  historical edits, or unrelated failure repair.

## Visible result

> On `/repertoire`, the preferred-move panel clearly presents its saved and staged choices at both the desktop
> session-column width and the 412px constrained width, without changing workflow or disabled date behavior.
