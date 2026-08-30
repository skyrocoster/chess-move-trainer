# Repertoire Preferred-Move Design-System Alignment - /repertoire presents targeted feedback through existing shared components

> **Status:** done - all stages accepted with focused behavioral and browser proof

- **Read trigger:** Read before changing the `/repertoire` preferred-move or session feedback presentation, its
  focused stories/tests, or its bounded browser proof.
- **Upstream:** none - approved coordinator assessment; completed repertoire workflow and session records remain
  historical evidence and are not amended.

## Outcome

Align the `/repertoire` preferred-move panel's errors and mutation status, plus the parent session status, with the
existing design-system feedback components. Preserve every existing message, role, live-region attribute, test marker,
confirmation behavior, workflow contract, and accessibility meaning while leaving context, instructions, headings, and
all other preferred-move behavior unchanged.

## Scope

- **Included:**
  - Render each preferred-move failure through `PanelFeedback` with `severity="error"` and consumer-owned
    `role="alert"`, preserving one alert per failure and the exact existing failure text.
  - Render the preferred-move mutation status through `InlineFeedback` with `severity="information"`,
    `role="status"`, and `aria-live="polite"`, preserving the exact mutation text.
  - Render the parent `session-status` through an information `InlineFeedback` presentation while preserving its
    exact text, `role="status"`, `aria-live="polite"`, stable `data-testid="session-status"` marker, Workspace
    ownership, and use as the board notice.
  - Make only the feature-local CSS adjustments needed after replacing the raw feedback paragraphs.
  - Update the focused repertoire stories and tests to guard the shared presentations, exact wording, roles, live
    regions, test marker, unchanged actions, confirmation, accessibility, and constrained layout.
  - Keep `RemoveConfirmation` feature-local and unchanged. Its direct `@base-ui/react/alert-dialog` composition,
    focus behavior, wording, buttons, and token-based local CSS remain authoritative.
- **Expected areas:**
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.module.css`
  - `frontend/src/features/repertoire-builder/RepertoireSessionPanel.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireSessionPanel.module.css`
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.stories.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx`
  - `frontend/src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`
  - `tests/e2e/repertoire-builder-storybook.spec.ts` only for bounded assertion maintenance if existing selectors
    require it; otherwise it is proof-only.
- **Excluded:** Any `frontend/src/features/design-system` source, API, or token change; a shared AlertDialog or any
  other new primitive; new dependencies; copy changes; API, data, storage, persistence, workflow, route-owner, or
  backend changes; changes to context, loading, instructions, headings, dates, preferred-move actions, board notice
  ownership, focus behavior, or accessibility contracts; unrelated design-system cleanup; broad lint, formatting,
  build, source-size, aggregate, or maintenance checks; new browser profiles/specs; `Scratch/`; historical records;
  commits; pushes; and unrelated worktree changes.

## Stages

1. **complete** - Align the source composition with the existing feedback system without changing behavior.
   - **Ordered actions:** Re-read the current `FeedbackProps`, `InlineFeedback`, `PanelFeedback`, the preferred-move
     panel, and the session boundary before editing. Replace only the three raw preferred-move error paragraphs with
     `PanelFeedback severity="error" role="alert"`, without headings or wording changes. Replace only the mutation
     status paragraph with `InlineFeedback severity="information" role="status" aria-live="polite"`. Replace the
     parent session status presentation with an information `InlineFeedback`, keeping the stable
     `session-status` marker and live semantics on one outer status element so the shared feedback core does not
     create duplicate live regions. Preserve `sessionStatus` state ownership and its board `notice` use. Remove only
     obsolete raw-message CSS; retain panel structure, typography for context/instructions/headings, dialog CSS, and
     all action/layout behavior. Do not alter any design-system component or add a shared dialog wrapper.
   - **Focused proof:** Static source review against the existing `FeedbackProps` contract and the retained semantic
     checklist: one `role="alert"` per conditional failure, one status live region per status presentation, exact
     messages, stable `session-status` marker, and unchanged local AlertDialog composition. No broad repository check
     is authorized.
   - **Breakpoint:** None while the existing feedback APIs preserve the required marker and live-region semantics.
   - **Escalate if:** Preserving the marker requires a shared feedback API change, a status severity or live-region
     decision, a copy change, a new token/visual hierarchy, or any change to `RemoveConfirmation`.
2. **complete** - Add focused regression guards for the shared presentations and unchanged workflow boundary.
   - **Ordered actions:** Extend the existing PreferredMovePanel and RepertoireSessionPanel Storybook interactions
     to assert the error/status wrapper semantics without coupling to new product behavior. Retain exact error,
     mutation, session-status, action, and dialog assertions. Strengthen the Workspace and workflow tests/stories
     only where needed to prove the `session-status` marker remains a polite status, errors remain separate alerts,
     and the existing workflow, board notice, confirmation, keyboard, and accessibility paths are unchanged. Do not
     add a new browser spec or modify shared design-system tests.
   - **Focused proof:** From `frontend`, run
     `timeout 180s npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx --testTimeout=10000 --hookTimeout=10000`.
     The command-level timeout is `180s`; use a finite Bash tool timeout of `210000 ms`.
   - **Breakpoint:** None if the focused tests retain exact text, role/live-region, marker, action, dialog, and
     accessibility expectations.
   - **Escalate if:** A regression guard requires changing a public prop, API/data behavior, copy, workflow state,
     confirmation/focus model, or shared design-system contract.
3. **complete** - Prove the aligned presentation through the existing Storybook and browser surfaces.
   - **Ordered actions:** Run the focused repertoire Storybook interactions for `PreferredMovePanel/ErrorFeedback`,
     `PreferredMovePanel/SavingMutation`, the Session Panel status stories, and the existing Workspace preferred-move
     stories. Then run the registered browser proof at its existing wide and constrained sizes. Confirm exactly one
     alert per rendered failure, information feedback for mutation/session statuses, exact wording, preserved
     `session-status` marker and polite live semantics, unchanged AlertDialog role/name/focus/cancel/remove flow,
     keyboard accessibility, and no horizontal overflow. Use only existing Storybook/browser surfaces; do not add a
     visual direction, browser profile, or general maintenance pass.
   - **Focused proof:** From `frontend`, run
     `timeout 300s npm run test-storybook -- --run src/features/repertoire-builder --testTimeout=10000 --hookTimeout=10000`.
     The command-level timeout is `300s`; use a finite Bash tool timeout of `360000 ms`. With the existing Storybook
     server available, from the repository root run
     `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`.
     The command-level timeout is `600s`; use a finite Bash tool timeout of `660000 ms`.
   - **Breakpoint:** Human visual review is verification at the existing wide/constrained states, not a new design
     choice. Stop if the shared presentations introduce an unacceptable hierarchy, density, focus, responsive, or
     accessibility result that requires a new direction.
   - **Escalate if:** Any proof exposes changed wording, duplicate announcements, changed workflow/dialog behavior,
     overflow, a new visual or accessibility requirement, an unrelated failure, or a need for a shared primitive.

Stages are sequential; no parallel stages. A passing proof item remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. No lint, formatting, broad type/build,
source-size, aggregate, or other repository-hygiene command is required by this Plan.

## Progress and decisions

- **Dependency gate:** complete - the assessment route is approved; no active matching Plan existed; existing feedback
  components and the local Base UI dialog are available.
- **Decision:** Preferred-move failures use `PanelFeedback` with `severity="error"` and consumer-owned
  `role="alert"`; mutation and parent session statuses use `InlineFeedback` with `severity="information"`,
  `role="status"`, and `aria-live="polite"`.
- **Decision:** Context, instructions, headings, wording, contracts, behavior, and ownership remain unchanged.
- **Decision:** `RemoveConfirmation` remains feature-local and unchanged. No shared AlertDialog primitive is justified
  for this single consumer without an established shared contract.
- **Stage 1:** complete - the three failures now use error `PanelFeedback`; mutation and session statuses use
  information `InlineFeedback`; exact messages, alert/status roles, polite live semantics, the `session-status`
  marker, Workspace ownership, board notice behavior, and the feature-local AlertDialog composition were retained.
  Static diff review found only the four bounded source/style paths and removal of obsolete message CSS; no tests
  were authorized for this stage.
- **Stage 2:** complete - focused story and workspace/workflow guards now cover separate exact-text alerts,
  informational mutation/session statuses, polite live semantics, the stable session marker, staged workflow, and
  unchanged dialog/action behavior. Focused Vitest proof passed: 2 files and 35 tests.
- **Stage 3:** complete - focused Storybook proof passed 5 files and 44 tests; the existing Playwright repertoire
  proof passed all 7 tests across wide and constrained states. Exact feedback semantics, the stable session marker,
  dialog actions/focus, keyboard accessibility, and overflow checks passed without further edits or a visual
  breakpoint.

## Proof

- Focused unit regression:
  `timeout 180s npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx --testTimeout=10000 --hookTimeout=10000`
  from `frontend`; command-level timeout `180s`; Bash tool timeout `210000 ms`; **passed after Stage 2: 2 files,
  35 tests**.
- Focused Storybook regression:
  `timeout 300s npm run test-storybook -- --run src/features/repertoire-builder --testTimeout=10000 --hookTimeout=10000`
  from `frontend`; command-level timeout `300s`; Bash tool timeout `360000 ms`; **passed after Stage 3: 5 files,
  44 tests**.
- Existing bounded browser regression:
  `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`
  from the repository root, with the existing Storybook server; command-level timeout `600s`; Bash tool timeout
  `660000 ms`; **passed after Stage 3: 7 tests in 41.1 seconds**.
- These commands directly prove the targeted feedback roles/live regions, exact text, stable session marker,
  confirmation flow, keyboard/accessibility behavior, wide/constrained presentation, and overflow behavior. Passing
  behavioral proof remains valid until an affecting later change invalidates it.

## Acceptance

- Each rendered preferred-move failure appears exactly once through `PanelFeedback` with `severity="error"` and
  `role="alert"`, retaining its exact existing message.
- Mutation and parent session statuses appear through information `InlineFeedback` while retaining exact text,
  `role="status"`, `aria-live="polite"`, and the parent `session-status` test marker; session state remains owned by
  the Workspace and continues to feed the board notice.
- Context, instructions, headings, all preferred-move states/actions, dates, workflow/API behavior, accessibility
  meaning, and wording remain unchanged.
- `RemoveConfirmation` remains the same feature-local direct Base UI AlertDialog with the same title, description,
  focus behavior, Cancel/Remove actions, and accessible `alertdialog` flow; no shared dialog primitive is added.
- Focused Vitest, Storybook, and existing browser proof pass at the existing wide and constrained scenarios without
  horizontal overflow or unrelated path changes.

## Escalation boundaries

- Any shared design-system source/API/token change, shared AlertDialog extraction, new dependency, or new primitive.
- Any copy, severity, role/live-region, focus, accessibility, visual hierarchy, responsive, overflow, or acceptance
  decision not settled by the existing components and this Plan.
- Any preferred-move, date, session, board-notice, API, data, persistence, workflow, route-owner, backend, or
  dependency change.
- Any new browser profile/spec, broad design-system cleanup, maintenance check, unrelated failure requiring repair,
  historical-record edit, `Scratch/` change, concurrent baseline collision, commit, or push.

## Visible result

> On `/repertoire`, preferred-move errors and statuses and the parent session status use the repository's existing
> feedback language and semantics, while the workflow, wording, confirmation dialog, and accessible behavior remain
> unchanged.
