# `/repertoire` responsive columns — repository-aware design synthesis

> Noncanonical design evidence only. This document is not a Plan and does not authorize implementation.

## A1 — Authority and status

This synthesis records the user-signed-off responsive `/repertoire` direction. The visual authority is the
signed artifact at:

`experiments/mock-ups/rearranged-rep/round-03-responsive-columns/`

That artifact carries forward catalogue **Idea 03: Centered pill** from the earlier divider exploration and
settles the container-width 3 → 2 → 1 composition. Its fake content, exploration labels, and review-sheet
chrome are not product requirements. This document is the repository-aware hand-off for assessment and
planning; it remains noncanonical until explicitly adopted.

## A2 — User-visible outcome and fidelity anchors

The `/repertoire` workspace should use its available horizontal space more effectively while making the
relationship between the board, session information, and engine output immediately legible:

- The visible stage reads **Board | Session | Engine** at wide widths.
- The board and its history are one working lane; session facts and preferred-move workflow are a second;
  the real engine analysis is a third.
- Only the internal boundaries move. The stage's left and right edges remain fixed while resizing
  redistributes panel width.
- A centered, compact pill is the visual cue for every live vertical splitter. It is quiet at rest and
  becomes more prominent on hover, focus, or active drag.
- The same lane order and hierarchy survive the medium regrouping and the narrow stack without inventing
  draggable separators where they no longer help.

The important fidelity anchors are the composition, the width thresholds, the panel minimums, the fixed
outer edges, the centered-pill anatomy, and the deliberate widening of the bounded workspace. The review
artifact's dark colours, fake corpus values, mode readout, and `Idea 03 · drag` label are not to be copied
into production UI.

## A3 — Responsive composition and resizing rules

Breakpoints are measured from the available **workspace stage/container width**, not assumed from the browser
viewport. The shell's 240px desktop sidebar and main padding mean viewport width is not a reliable proxy for
the stage.

| Stage width | Composition | Live separators | Minimums and reset |
| --- | --- | --- | --- |
| `>= 1040px` | One horizontal group: Board, Session, Engine. | Board/Session and Session/Engine, both vertical and live. | Board 320px, Session 280px, Engine 360px. Reset restores the intended three-panel defaults. |
| `700px–1039px` | Board owns a full-width row. A separate horizontal group below it contains Session and Engine. | One vertical Session/Engine separator in the lower group. No Board/lower-row separator. | Session 280px and Engine 360px. Reset restores the intended lower-row defaults. |
| `< 700px` | Board, Session, Engine as full-width rows in that order. | None. No vertical separator is rendered. | The panels stack and reflow; there is no resize affordance to preserve. |

The artifact's reference defaults are approximately Board 390px, Session 325px, Engine 420px at wide
widths, and Session 350px / Engine 380px in the medium lower row. These are visual/default-layout anchors,
not permission to violate a minimum or overflow a narrower stage. Defaults must be made valid for the
current inner width and clamped when necessary.

The selected mechanism is `react-resizable-panels` v4.12.3. Each live group owns its internal layout and
uses the library's public layout API for Reset. Resize state is ephemeral for the page session; persistence
of user layouts is excluded unless separately approved. A mode change may replace the active group with the
appropriate group for that mode, but it must not move the outer stage edges or duplicate lane content.

## A4 — Production composition and ownership mapping

The route is `frontend/src/App.tsx`: `/repertoire` lazy-loads
`frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx` inside the shared AppShell.
`frontend/src/features/app-shell/AppShell.module.css` supplies a 240px desktop sidebar and main padding
(24px on desktop, 16px in the narrow shell). The responsive stage belongs to the repertoire workspace, not
to a redesign of AppShell or Viewer.

### Responsive stage ownership

`RepertoireResponsiveStage` is the feature-local reusable component that owns the three-lane stage. Its
measured/query owner is the named `repertoire-workspace-stage` container, and that owner makes the `1040px`
and `700px` mode decisions from the available stage width. The old anonymous `.repertoire` container and its
obsolete grid query are replaced in implementation; they are not compatibility boundaries to retain.

`PillSeparator`, reset/layout helpers, measurement, valid-default calculation, and mode switching remain
private to `RepertoireResponsiveStage` unless implementation evidence demonstrates that a narrower extraction
is necessary. They are not generic lane APIs.

Today the workspace renders board plus evaluation, controls, position description, the combined
`RepertoireSessionPanel`, and a full-width `AnalysisPanel`. The signed direction deliberately regroups those
same real pieces into the three lanes below rather than adding new product surfaces.

### Page framing above the stage

`RepertoireBuilderWorkspace` keeps the existing visible heading, `GameLoader`, and origin description above
the responsive stage. The origin text and its `session-origin` identity remain page-owned. These elements do
not become one of the three resizable lanes.

### Board lane

The standalone `RepertoireBoardLane` is the composition of exactly one controlled `MoveHistory` with the real:

- `BoardEvalStage`, wrapping the existing `InteractiveBoardAdapter` and the evaluation display for the
  **displayed** position;
- `BoardControl`, retaining Previous, Next, and Flip semantics; and
- controlled `MoveHistory`, using the complete represented stored prefix/local continuation and the current
  active ply.

`MoveHistory` is currently supplied by `RepertoireSessionPanel`; it must move to `RepertoireBoardLane` without
creating a second history model or changing its controlled callbacks. `RepertoireBoardLane` is the only lane
that renders this controlled history. A staged owner move remains a child preview and is not inserted into
history; committed opponent/local continuation moves retain their existing history semantics.

### Session lane

The Session lane contains the real:

- `PositionReachFrequency`, driven by the workflow's position-context response and selected colour;
- the one existing live session-status surface (`session-status`, `role="status"`, polite live updates);
- `PreferredMovePanel`, driven by the existing workflow model, confirmed saved value, staged value, date
  capability, mutation state, errors, and callbacks; and
- `PositionDescription`, composed into this lane by `RepertoireBuilderWorkspace` from its current page-level
  position.

`RepertoireSessionPanel` remains by name and story boundary, but becomes session-facts only: it contains
`PositionReachFrequency`, the single live session status, and `PreferredMovePanel`. It removes Move History
responsibility and history props rather than introducing slots or retaining a mega-prop facade. The workflow
and content must still be mounted once: no duplicated `MoveHistory`, status live region, preferred panel, or
API requests.

The Session semantic wrapper is local workspace composition, not a generic reusable lane abstraction.

The existing `position-description-row` wrapper, `PositionDescription` disclosure, `aria-expanded` behavior,
and position-summary semantics should be preserved where possible after the move into the Session lane.

### Engine lane

The Engine lane is a local workspace semantic wrapper containing the real `AnalysisPanel`, composed into the
lane by `RepertoireBuilderWorkspace` with its existing action callbacks and candidate-move selection path. It
is not a generic reusable lane abstraction. Do not replace it with the mock-up's illustrative engine list.

`RepertoireBuilderWorkspace` currently and intentionally has two analysis states:

- `parentAnalysisState` produces `analysisDisplay` for the source/current position and powers
  `AnalysisPanel`;
- `displayedAnalysisState` produces `displayedEvaluationDisplay` for the displayed child preview and powers
  `BoardEvalStage`.

The layout change must preserve this distinction, `viewKey`, all state hooks and callbacks, game loading and
reset, move/promotion/history flows, Flip, origin text, and the existing API contracts. Lane placement must
not collapse the two FEN/analysis meanings or create a second orchestration state.

## A5 — Interaction and accessibility requirements

### Splitter interaction

- Every rendered separator is the library separator control, not a custom drag implementation. It has a
  clear accessible name such as `Board and Session boundary` or `Session and Engine boundary`.
- The library's keyboard/focus resize behavior remains available. The visual pill is not a separate control,
  and its label/grip decoration is not announced as another action.
- The library-owned hit target must be materially larger than the visual pill and usable with coarse and fine
  pointers. The artifact demonstrates approximately 28px coarse and 18px fine resize targets around a much
  smaller visual marker; exact dimensions may translate to repository conventions while preserving that
  affordance.
- Use an obvious `:focus-visible` treatment with sufficient contrast on the separator and adjacent surfaces.
  Do not make hover the only discovery or feedback mechanism.
- The narrow stack renders no separators, so keyboard users must not encounter inert separator controls in
  the one-column mode.

### Existing content semantics

Retain the current semantics and focused accessibility expectations:

- status, alert, and polite live-region behavior from `InlineFeedback`, `PanelFeedback`,
  `PreferredMovePanel`, `AnalysisPanel`, and the workspace session status;
- `MoveHistory`'s accessible navigation, controlled active ply, `aria-current="step"`, and keyboard
  Previous/Next/Home/End behavior;
- `PositionDescription`'s disclosure button, `aria-expanded`, and position summary semantics;
- descriptive names and focus-visible behavior for preferred-move controls and its removal dialog; and
- no reliance on colour alone for lane identity, status, saved/staged meaning, or separator state.

Run the layout through forced-colors mode using system Canvas/CanvasText/ButtonBorder/Highlight roles. Respect
`prefers-reduced-motion`: splitter and lane transitions must not be required to understand state, and motion
should be disabled or reduced without hiding pending/error feedback.

## A6 — Styling and deliberate space use

The current `RepertoireBuilderWorkspace.module.css` has an anonymous inline-size container and a
`max-inline-size: 66rem` workspace cap. That cap is likely too narrow for the signed-off horizontal-space
outcome. Widening the workspace to a deliberate bounded value consistent with the artifact—up to about
1540px— is a **fidelity requirement**, not an accidental side effect of replacing the grid. The wider stage
must still remain inside AppShell's main column, respect its padding, keep `min-inline-size: 0`, and avoid
document-level horizontal overflow. The replacement stage container is named `repertoire-workspace-stage`;
the old anonymous `.repertoire` container and obsolete grid query must not remain as the responsive owner.

### Named container and query ownership

- `repertoire-workspace-stage` is the responsive stage container owned by `RepertoireResponsiveStage`. It is
  the measured/query owner for the `1040px` and `700px` mode decisions.
- Retain the existing `board-control`, `preferred-move-panel`, and `analysis-panel` internal containers under
  their respective components.
- Add `position-description` to the root of `PositionDescription` and scope its existing queries to that name.
- Add `board-eval-stage` to a `BoardEvalStage` host and scope its internal query to that name. Preserve
  Viewer grid placement; this does not redesign Viewer.
- `MoveHistory`, `PositionReachFrequency`, `InteractiveBoardAdapter`, and the Board, Session, and Engine lane
  wrappers do not need container names because they do not own responsive queries.

Use CSS Modules, the existing CMT spacing/radius/focus tokens, Material surface/text/outline roles, and
semantic feedback roles. Translate the artifact's contrast and density into repository tokens instead of
copying its raw hex colours or private typography.

### Centered-pill anatomy

Each separator reserves a quiet internal slot while keeping the outer stage fixed. The visual marker is a
small vertical rounded pill centred in that slot. The artifact shows roughly a 12px slot with a muted 4px ×
52px pill at rest; hover, focus, and active drag raise it to roughly 6px × 72px and the selected accent role.
Those dimensions are proportion/density anchors, not new global tokens. The implementation may use the
nearest repository values, but must preserve:

1. a discoverable resting cue;
2. a clear warm/high-contrast interaction state;
3. no heavy full-height rule that reads as a fourth panel; and
4. a larger invisible/library-owned target than the visible pill.

The mock-up's `Idea 03 · drag` wording, mode annotations, measured pixel readouts, lineage card, and
noncanonical stamp are review-only and must not be product copy.

## A7 — Real states and content replacing mock data

The layout is a rearrangement, not a new data model. Replace every static mock value with the current
repository-owned state:

- Board position, orientation, last move, promotion state, notice, and child preview come from
  `PositionPickerSession`, `InteractiveBoardAdapter`, and the existing workspace callbacks.
- Move rows come from `positionPickerHistory(session)` and the controlled `MoveHistory` input. Do not add a
  static sample line or put a staged preview into history.
- Reach frequency and corpus context come from `PositionContextResponse` through the existing
  `usePreferredMoveWorkflow`/`usePositionContextState` path and `PositionReachFrequency`; loading, unavailable, zero,
  and unsavable readings remain meaningful.
- Session status is the existing workspace message, including load, legal/illegal move, promotion,
  navigation, staging, saved-move, and reset feedback. Keep one live session-status message.
- Preferred move content is the actual `PreferredMovePanel` relationship and gating behavior: unknown/loading,
  empty, first choice, saved, replacement, matching, opponent-turn, unsavable, pending mutation, typed read
  error, mutation failure, retry, disabled effective-date capability, and removal confirmation as currently
  supported. No mock date, corpus count, or fake move is acceptable.
- Position description is derived by `createPositionModel` from the displayed FEN/orientation and retains its
  real summary, inventories, castling, en-passant, and clock facts.
- Engine output, stale/queued/running/done/failed status, candidate lines, WDL, terminal/no-line cases,
  action errors, and retry/update/analyze controls come from the existing `AnalysisPanel` display contract.

The heading, loader, origin, all existing loading/error/empty/pending states, and API-backed content must
remain available in every composition. The responsive change must not introduce a fake “mode” product state.

## A8 — Contracts, dependencies, and exclusions

Existing contracts remain unchanged:

- game lookup and stored-position loading through the current `GameLoader`/`fetchGame` contract;
- evaluation observation GET, enqueue POST, and status polling through `analysisApi`;
- preferred move GET/PUT/DELETE through `preferredMoveApi`;
- position context GET through `positionContextApi`; and
- the current in-memory position-picker and preferred-move workflow semantics.

`react-resizable-panels` v4.12.3 is the selected production mechanism. Its production declaration moves from
the repository-root `package.json` to `frontend/package.json`; the lockfile workspace metadata must be updated
while retaining one resolved v4.12.3 version. This remains implementation work outside this documentation edit.
It is not permission to silently replace the selected library with a custom splitter.

Explicit exclusions:

- no API, backend, database, domain, game-position, evaluation, preferred-move, or position-context change;
- no mock content, review-sheet copy, or illustrative local data in production;
- no persistence of panel layouts or new user preferences unless separately approved;
- no new move-history, FEN, analysis, or preferred-workflow state created by the layout;
- no broad AppShell redesign and no unrelated Viewer redesign; and
- no requirement that obsolete DOM-parent assumptions or raw CSS-grid-regex tests remain unchanged when they
  contradict the semantic lane composition.

## A9 — Allowed implementation adaptations versus prohibited drift

### Canonical implementation must preserve

The implementation must preserve the A3 composition table, thresholds, panel minimums, fixed outer edges,
Reset behavior, centered-pill treatment, lane order, the `RepertoireResponsiveStage` and
`RepertoireBoardLane` boundaries, the session-facts-only `RepertoireSessionPanel` boundary, the local Session
and Engine wrappers, the named container/query ownership in A6, existing state/API contracts, and the
accessibility requirements in A5. These are the settled design invariants.

### It may translate onto repository conventions

It may use CSS Modules and CMT/Material tokens instead of the artifact's raw styles; choose the exact internal
DOM nesting inside the settled component/container boundaries; use an equivalent reliable measurement
mechanism owned by `RepertoireResponsiveStage`; clamp defaults for available space; and preserve existing test
IDs/ARIA attributes where that does not duplicate content. The selected dependency may be installed according
to workspace conventions, but must land in `frontend/package.json` with the corresponding lockfile metadata.
Mock-up headings and other review-only text are not authoritative.

### It must not drift into

Viewport-only breakpoints, a permanently capped 66rem stage that defeats the signed space-use outcome, retaining
the anonymous `.repertoire` stage or obsolete grid query, moving the stage's outer edges while dragging,
separators in narrow mode, a custom replacement for `react-resizable-panels`, putting history back into
`RepertoireSessionPanel`, adding slots or a mega-prop facade, generic reusable lane abstractions, duplicated
workflow/API state, static mock cards, collapsed parent/displayed analysis state, or unrelated product behavior
changes.

## A10 — Focused validation targets and human visual breakpoint

Validation should remain focused on this design and the existing repertoire behavior, not become a broad
lint/build/aggregate-suite proof requirement. Target:

1. `RepertoireBuilderWorkspace.test.tsx` and `RepertoireBuilderWorkspaceWorkflow.test.tsx`: existing
   loading, reset, move, promotion, history, preferred workflow, status, and dual-analysis behavior remain
   intact after lane composition changes.
2. Repertoire stories, story helpers, story assertions, and affected component stories: replace DOM-parent or
   raw CSS-grid assertions with semantic lane/component presence, order, state, and controlled interaction
   assertions. Preserve important IDs and ARIA semantics where practical, but test the new lane boundaries
   and named query owners rather than obsolete ancestry.
3. `tests/e2e/repertoire-builder-storybook.spec.ts`: representative wide, medium, and narrow surfaces,
   existing preferred-move/error/loading states, history/current semantics, no horizontal overflow, axe
   expectations, and keyboard/focus behavior.
4. Splitter-specific checks: accessible separator names, focus-visible styling, keyboard resizing, panel
   minimums, fixed stage edges during internal resizing, Reset restoration, and absence of separators below
   700px. Check both 1039/1040px and 699/700px container boundaries rather than relying only on viewport size.

The required human visual breakpoint is a review of the actual `/repertoire` composition at one wide stage,
one medium stage, and one narrow stage, including a drag/reset pass and a check immediately around both
breakpoint boundaries. The reviewer must confirm that the wider bound improves horizontal use without
escaping AppShell, that the medium Board row is genuinely full width, and that the narrow stack has no
vertical separator or overflow. This is a visual decision point, not an authorization contained in this
document.

## A11 — Settled decisions and implementation risks

### Settled

- Centered pill (catalogue Idea 03) is selected.
- The composition is container-width responsive: 3 columns at `>=1040px`, Board plus a resizable Session/
  Engine row at `700px–1039px`, and a separator-free Board → Session → Engine stack below `700px`.
- Board, Session, and Engine minimums are 320px, 280px, and 360px respectively.
- Outer stage edges stay fixed; only internal widths redistribute.
- Reset restores intended defaults through the selected library mechanism.
- Better horizontal-space use and the regrouping are core outcomes, so the 66rem cap must be deliberately
  reconsidered against a bound of up to about 1540px inside AppShell.
- `RepertoireResponsiveStage` is the feature-local reusable stage component. `repertoire-workspace-stage` is
  its measured/query owner for both mode decisions; the anonymous `.repertoire` container and obsolete grid
  query are replaced.
- `RepertoireBoardLane` owns the real `BoardEvalStage`, `BoardControl`, and exactly one controlled `MoveHistory`.
  `RepertoireSessionPanel` remains by name/story boundary but owns session facts only: reach frequency, the
  single live session status, and `PreferredMovePanel`; it has no history responsibility or history props, and
  no slots or mega-prop facade are introduced. `PositionDescription` and `AnalysisPanel` are composed by the
  workspace into the Session and Engine lanes respectively, whose semantic wrappers remain local composition.
- The exact named-container ownership in A6 is settled, including `position-description` and `board-eval-stage`;
  Viewer grid placement remains unchanged. `PillSeparator`, reset/layout helpers, measurement, defaults, and
  mode switching stay private to `RepertoireResponsiveStage` unless implementation evidence requires a narrower
  extraction.
- `react-resizable-panels` remains v4.12.3 and moves from the root declaration to `frontend/package.json`; the
  lockfile workspace metadata is updated without introducing another resolved version. This is implementation
  work, not a change to the selected mechanism.
- Existing state hooks, callbacks, displayed/parent analysis distinction, `viewKey`, loader/reset, origin,
  move/promotion/history flow, and API contracts remain authoritative.

### Risks for assessment/planning

- The `RepertoireSessionPanel` split must preserve its session-facts-only boundary while moving exactly one
  controlled `MoveHistory` into `RepertoireBoardLane`; a careless composition can duplicate history, the live
  status, or a workflow owner, or reintroduce history props through a facade.
- Container breakpoints must be based on the actual `repertoire-workspace-stage` width. The AppShell sidebar,
  main padding, and replacement of the anonymous container make viewport/media-query-only reasoning unreliable.
- The wider workspace bound may expose latent intrinsic-width or overflow issues in MoveHistory,
  PreferredMovePanel, PositionDescription, or AnalysisPanel; minimums and wrapping must be validated together.
- The `position-description` and `board-eval-stage` query scopes must not leak into Viewer or alter Viewer grid
  placement; omitting either host name can make local responsive behavior depend on unrelated ancestors.
- Mode changes can remount different `Group` trees. Layout defaults, focus, pending workflow state, and
  separator presence must remain coherent when the stage crosses a threshold.
- Moving the library declaration to `frontend/package.json` must update lockfile workspace metadata while
  retaining one resolved v4.12.3 version; an incorrect workspace entry or duplicate resolution can break the
  production import even though the library choice is settled.

## A12 — Adoption boundary

**Preserve:** the A3 composition and resizing invariants, A4 component boundaries and composition ownership, the
exact named-container/query ownership in A6, A5 accessibility semantics, A6 space-use and pill anatomy, A7
real-content/state mapping, and A8 contract exclusions.

**Translate:** nonsemantic DOM structure inside the settled boundaries, CSS/token values, the equivalent
measurement mechanism used by `RepertoireResponsiveStage`, and valid default-layout calculation onto repository
conventions, provided the preserved invariants remain observable. Do not translate away the required component
or container names, or add a history facade to `RepertoireSessionPanel`.

**Exclude:** all mock-up-only text/data and review chrome, including fake board/engine/corpus values, lineage
and mode annotations, measured-width readouts, noncanonical stamps, and any custom mock controls.

The design evidence ends at this boundary. It supplies meaning and constraints for a future assessment and
Plan; it does not select implementation stages or authorize product changes.
