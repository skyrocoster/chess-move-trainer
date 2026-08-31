# Preferred Move Panel — selected design reference

**Document type:** detailed component design reference and implementation handoff

**Status:** noncanonical exploration. This document is explicitly **not a Plan** and does not change
the product, tests, Plans, or the selected HTML.

**Selected mock-up:** [02-staged-move-is-the-proposal-final-choice.html](./02-staged-move-is-the-proposal-final-choice.html)

The HTML is the visual reference. This document records the selected component behavior, the settled
grilling decisions, and the repository facts a future implementation must respect. A future Plan must
reference this document and match the selected HTML, but this document contains no stages, sequence,
checklist, estimate, or progress record.

## 1. Noncanonical status and reading guide

This is an exploration under `experiments/`. It is not a canonical product contract until the user
explicitly adopts it. The selected HTML is a self-contained review sheet; it is not a React component,
does not import application code, and its buttons do not persist data.

The selected panel is the composition inside `article#live-panel` in
`experiments/mock-ups/preferred-move-panel/02-staged-move-is-the-proposal-final-choice.html`.
The outer wordmark, hero, demo controls, side cards, coverage disclosure, and footer are review-sheet
chrome, not `/repertoire` UI. The HTML itself says that its demo controls are not panel actions at
`02-staged-move-is-the-proposal-final-choice.html:1337-1351`, and its script only writes demo feedback
at `02-staged-move-is-the-proposal-final-choice.html:1730-1734`.

This reference uses two labels consistently:

- **Current repository** means behavior observed in the cited source, story, test, or API file today.
- **Selected design** means the behavior and presentation described here, including the confirmed
  grilling decisions below. Where the selected HTML is only illustrative or differs from a settled
  decision, this document says so directly.

## 2. Settled grilling decisions — recorded exactly

The following decisions are fixed for this exploration and must not be reopened as product questions:

- Replace the old panel-state approach with a relationship model derived from: saved choice present/absent, staged move present/absent, and staged matching/differing from saved.
- `unsavable` and `opponent-turn` are gating conditions, not panel states. Loading, mutations, and errors are transient conditions, not separate layouts.
- Presentations:
  1. no saved + no staged: both boxes visible and empty; no panel actions;
  2. no saved + staged: first-choice proposal; `Save` and `Change effective date`;
  3. saved + no staged: saved plus empty staged box; `Change effective date` and `Remove`;
  4. saved + staged different: replacement proposal; all three actions;
  5. saved + staged matching: already saved; `Change effective date` and `Remove`, no `Save`.
- Remove explicit Edit mode. Every played move becomes staged.
- Clicking the `Current saved choice` box plays and stages that move. It is mouse/keyboard accessible, focus-visible, and has a descriptive accessible name. It immediately replaces any temporary staged proposal without confirmation because staging is nonpersistent.
- `matching-played` and `unsaved-played` cease to be preferred-panel view states. Preserve move-history facts elsewhere only if still needed.
- Consequence sentences use fixed component-owned templates populated from relationship/model data, e.g. `Save d4 to replace e4`; the model owns facts/relationship, not finished prose.
- `Save` persists staged move. `Remove` deletes only the saved choice and retains any staged move. Keep existing removal confirmation.
- `Change effective date` is an independent date-only persistence interaction for an existing saved choice. For a first choice, it becomes available once a move is staged so the initial effective date can be chosen before Save.
- Exact panel action labels only: `Save`, `Change effective date`, `Remove`. Remove Add, Edit, Cancel edit, and Play saved move buttons. The play-saved capability moves to the clickable saved-choice box.
- Canonical future implementation must create properly abstracted design tokens and reusable primitives/components before composing the panel. `Save` and `Remove` must at minimum be reusable button components. Explain likely token/component boundaries grounded in current repo patterns, but do not turn this document into ordered Plan stages.
- Maintain one date display, one consequence statement, and one empty-state explanation. No visible design/meta commentary in the product panel. Normalize icon/text spacing through shared button layout rules.

## 3. Purpose, mental model, terminology, and non-goals

### Purpose

The panel should answer one practical question at the position currently shown by the board:

> What preferred move is saved now, and what move am I proposing to save next?

The user should not need to infer persistence from labels such as “played,” “prepared,” or “edited.”
The saved value is a server-confirmed fact. The staged value is a local, reversible board choice. A
staged value that differs from the saved value is also the proposal that `Save` would persist.

### Mental model

The panel has two peer boxes and one relationship:

1. **Current saved choice** is the persisted value for the focused source position. Its effective date
   belongs to this fact.
2. **Staged move** is the current local board choice. It is not persisted until `Save` succeeds.
3. The connector and one consequence sentence describe whether the staged value is a first choice, a
   replacement, or already the saved value. There is no third proposal, played, or prepared box.

The board may display the child position after the staged move, while the source position remains the
preferred-move record's FEN identity. This distinction is part of the workflow contract in
`frontend/src/features/repertoire-builder/positionPickerSession.ts` (`selectPositionPickerMove` and
`positionPickerSelectedTransition`).

### Terminology

| Term | Meaning in the selected design |
| --- | --- |
| **Current saved choice** | The last confirmed preferred move assigned to the focused source position. |
| **Staged move** | A legal move currently selected for the source position but not yet persisted. |
| **Proposal** | The staged move considered as the next value that `Save` would persist. |
| **Source position** | The position before the move; its full FEN identifies the preferred record. |
| **Child preview** | The board position after a staged move, without committing that move to Move History. |
| **Effective date** | The UTC timestamp from which a persisted event is active; the UI shows its UTC calendar day. |
| **Saveability** | Whether the known position is present in the accepted corpus and may accept a preferred-move write. |

### Non-goals

The preferred panel is not a move-tree editor, analysis recommendation, second board, automatic-save
surface, opponent-turn workflow, owner/player selector, or replacement for Move History. It does not
show every preferred-move event, expose a historical `as_of` control, or turn an invalid/unavailable
position into a saveable one. It must not duplicate the same move under “played,” “prepared,” and
“proposed” labels.

## 4. Boundary of the selected HTML

The selected review sheet establishes the visual direction, not a literal DOM or API implementation.
The panel composition is visible at `02-staged-move-is-the-proposal-final-choice.html:1353-1398`:

- a panel shell with an accent rule;
- a header with `Preferred move`, a descriptive heading, and a short status pill;
- two peer choice boxes;
- a relationship connector;
- one optional consequence sentence;
- an action footer.

The “Two boxes, one honest mutation” explanation at
`02-staged-move-is-the-proposal-final-choice.html:1322-1325` is rationale for this reference, not
product copy. Likewise, `Design thesis`, `Demo controls`, `Chosen model`, `State coverage`, and
`Implementation hand-off` are not visible panel text. The review sheet's exact implementation has three
illustrative artifacts that the settled decisions correct for the future product:

1. `renderActions` always creates a `Save` button, disabling it when `canSave` is false, at
   `02-staged-move-is-the-proposal-final-choice.html:1662-1671`. The selected product contract
   withholds `Save` entirely whenever the relationship has no mutation or is already matching.
2. The HTML's `no-saved-staged` fixture sets `showDate: false` at
   `02-staged-move-is-the-proposal-final-choice.html:1521-1532`. The settled product contract instead
   exposes `Change effective date` once a first-choice move is staged, so the initial date can be chosen
   before `Save`.
3. The HTML renders `unsavable` and `opponent-turn` through a “pointless” alternate message at
   `02-staged-move-is-the-proposal-final-choice.html:1674-1694`. The settled product decision treats
   those as gating conditions, not panel states or deletion instructions. They must not become extra
   `data-state` layouts or “pointless” product copy.

The HTML's saved box is a noninteractive `section` at
`02-staged-move-is-the-proposal-final-choice.html:1364-1371`; the selected product behavior extends
that visual box into an accessible play-and-stage control. No HTML change is made by this document.

## 5. Detailed panel anatomy

The anatomy below describes the product-facing panel, not the review-sheet chrome.

### 5.1 Panel shell

Use the existing preferred-move section/landmark and heading relationship rather than copying the
HTML's `article` literally. The current section is `PreferredMovePanel` in
`frontend/src/features/repertoire-builder/PreferredMovePanel.tsx`, with
`aria-labelledby="preferred-move-heading"`. Keep one clear panel heading and a compact shell that can
fit in the session column.

The selected HTML uses a four-pixel top accent and a raised dark surface
(`.panel-card` and `.panel-card::before` at `02-staged-move-is-the-proposal-final-choice.html:382-451`).
In canonical CSS, the accent and surface must be semantic tokens, not the HTML's raw `--blue`, `--amber`,
`--mint`, or `--coral` literals.

### 5.2 Header

The header contains:

- a small `Preferred move` feature kicker;
- a heading equivalent to “What is saved, and what is staged?”;
- a concise textual status, such as ready, already saved, or a transient operation status.

The status may have a dot or accent colour as decorative support, but its text must carry the meaning.
The selected HTML's status-pill geometry is at `02-staged-move-is-the-proposal-final-choice.html:488-522`.
Do not expose `matching-played`, `unsaved-played`, `add`, or `edit` as user-facing state names.

### 5.3 Left box: Current saved choice

The left box is always labelled exactly **`Current saved choice`** when the relationship facts are
available. It contains:

- a decorative assigned/empty indicator, with text doing the semantic work;
- one prominent SAN value, such as `e4`;
- optional supporting UCI, such as `e2e4`, for unambiguous technical detail;
- the one saved-record effective-date display when a saved record exists.

When empty, keep the labelled box and use a short empty value such as `No saved choice yet.` Do not
call an empty value current. The selected HTML's saved-box structure and value treatment are at
`02-staged-move-is-the-proposal-final-choice.html:546-579` and
`02-staged-move-is-the-proposal-final-choice.html:1577-1592`.

When assigned, the whole choice box is the play-and-stage control. It must be a real keyboard-focusable
button or an equivalently accessible control, with a descriptive name such as “Current saved choice:
e4; play and stage this move.” The date is noninteractive text in that box if the box itself is a
button; the independent date action lives in the footer so interactive elements are not nested.

### 5.4 Connector

The connector is a visual relationship cue, never a control. At wide widths it sits between the boxes;
when they stack it points down. Its supporting word may read `stage a move`, `first choice`, `replace`,
or `matches`, but it must not add a second full explanation of the consequence.

The selected arrow and connector are at `02-staged-move-is-the-proposal-final-choice.html:707-731`.
The arrow, connector, and status dot are decorative and must not be focusable or announced as unexplained
controls.

### 5.5 Right box: Staged move

The right box is labelled exactly **`Staged move`**. It contains:

- an empty/proposal/matching indicator as decorative support;
- one staged SAN value and optional UCI detail when a move exists;
- one empty-state explanation when no move exists.

The right box is also the proposal surface when a staged move differs from the saved value. There is no
third proposal box. A staged move is never described as server-confirmed merely because it is visible on
the board.

The selected HTML's staged-box layout and empty treatment are at
`02-staged-move-is-the-proposal-final-choice.html:562-679` and
`02-staged-move-is-the-proposal-final-choice.html:1594-1613`.

### 5.6 Consequence statement

Show one consequence statement only when the relationship has a meaningful persistence reading. It is
an inset block below the boxes, not a third move container. It is populated by fixed component-owned
templates from facts supplied by the model; it is not arbitrary prose emitted by the model.

The selected visual places this block at `02-staged-move-is-the-proposal-final-choice.html:733-781`.
The sentence is authoritative; the accent, arrow, and background are supporting cues.

### 5.7 Date treatment

Show one visible date display, tied to the saved record when one exists. The value is a human-readable
UTC calendar day. The selected sample is `29 Aug 2026` at
`02-staged-move-is-the-proposal-final-choice.html:1369-1370`; the current product formats the same
underlying UTC day as ISO-like `YYYY-MM-DD` through `formatUtcDate` in
`frontend/src/features/design-system/CalendarDateUtils.ts`.

For an existing saved choice, `Change effective date` opens the date interaction and persists only the
date change. The saved move and any staged proposal remain separate facts. For a first choice, the same
action becomes available after staging and selects a pending initial date; `Save` persists that date
with the staged move. A pending first-choice date must not be labelled as the date of a saved record.
If the date-picker trigger itself displays the selected day, it is the one visible date display; do not
also print the same day in the saved box. Its accessible name may include the value even when the visual
label remains only `Change effective date`.

### 5.8 Action footer

The footer contains the actions in this order whenever the relationship and gates allow them:

1. **`Save`** — primary when a staged first choice or differing replacement can be persisted;
2. **`Change effective date`** — secondary date maintenance;
3. **`Remove`** — subordinate destructive action, still clearly labelled.

The selected HTML's footer and common icon/text rule are at
`02-staged-move-is-the-proposal-final-choice.html:784-891`. The product must not show `Add`, `Edit`,
`Save replacement`, `Cancel edit`, or `Play saved move` as panel actions. `Cancel` remains valid inside
the existing removal confirmation dialog and is not a normal panel action.

### 5.9 Transient feedback region

Loading, mutation, and error information belongs in the same panel shell. These conditions do not create
new relationship layouts. Use the existing `PanelFeedback` and `InlineFeedback` patterns where they fit,
keeping one readable status or alert for each distinct condition and avoiding duplicate narration with
the session status owned by `RepertoireSessionPanel`.

## 6. Relationship model and full condition matrix

### 6.1 Relationship facts

The stable presentation reading is derived from three facts:

1. Is a confirmed saved choice present?
2. Is a local staged move present?
3. If both are present, do their canonical UCI values match?

SAN is displayed, but canonical UCI is the comparison identity. The relationship model should own facts
such as saved move, staged move, equality, effective date, source FEN, own-turn, saveability, and pending
operation. It should not own finished consequence sentences.

The current `RepertoirePositionModel` in
`frontend/src/features/repertoire-builder/repertoireWorkflowModel.ts` does not yet have this shape. It
exposes the old `RepertoirePositionState` union (`no-saved`, `saved`, `matching-played`, and
`unsaved-played`), `savedMove`, `effectiveAt`, and focused played data. That is a current repository
fact, not the selected design API.

### 6.2 Normal relationship readings and actions

| Confirmed saved choice | Staged move | Comparison | Selected presentation | Visible panel actions |
| --- | --- | --- | --- | --- |
| Absent | Absent | N/A | Both boxes are visible and empty. The right box has the one instruction to stage a legal move. | None. |
| Absent | Present | N/A | First-choice proposal. The saved box is empty; the staged box contains the move; the consequence says it can become the current saved choice. | `Save`; `Change effective date`. |
| Present | Absent | N/A | Saved choice plus an empty staged box. | `Change effective date`; `Remove`. |
| Present | Present | Different UCI | Replacement proposal. Both boxes are filled; one consequence names the new and old move. | `Save`; `Change effective date`; `Remove`. |
| Present | Present | Matching UCI | Already saved. Both boxes show the same move; the no-change consequence is shown. | `Change effective date`; `Remove`; no `Save`. |

The action list is visibility, not merely disabled styling. An action whose prerequisite is absent is
withheld. A visible action may still be disabled while a mutation is pending.

### 6.3 Gating conditions

The following conditions overlay the relationship matrix. None is a sixth panel state, alternate panel
title, or invitation to delete a session/database record.

| Condition | Selected meaning and action effect |
| --- | --- |
| `ownTurn` is false / opponent turn | The preferred panel offers no owner staging or saving action. Opponent moves remain a board/session concern. A saved box, if retained as read-only context, is not clickable on the wrong turn; `Change effective date` and `Remove` are not offered as owner actions there. Do not expose a new opponent-turn layout or preferred-panel state. |
| `saveability === "unsavable"` | `Save` and first-choice date selection are gated off. Do not present a fake save-ready consequence. `Change effective date` and `Remove` remain governed by confirmed saved presence and API validity rather than by a new “remove state” action; in the supported no-saved case, no persistence actions appear. |
| `saveability === "unknown"` | Do not enable `Save` or treat the position as unsavable. Wait for context or show a typed context condition. |
| Preferred read loading | Saved presence is not yet known. Do not show an empty saved box as a confirmed unassigned result; withhold relationship facts and persistence actions while retaining the same panel shell. |
| Context read loading | Saveability is not yet known. Withhold gated persistence actions and show one loading status. |
| Preferred/context read error | Show typed feedback and withhold actions needing the failed fact. A read error is not an empty state. |
| Mutation pending | Keep last confirmed saved data and the staged proposal. Disable relevant persistence controls so the request cannot be duplicated; show one polite operation status. |

The exact behavior above keeps `unsavable`, `opponent-turn`, loading, mutations, and errors as
conditions on the relationship, not as new visible layouts. The selected HTML demonstrates blocked
illustrations for review only; those illustrations do not override this contract.

### 6.4 Current versus selected state treatment

| Concern | Current repository | Selected design |
| --- | --- | --- |
| Panel branch identity | `PreferredMovePanel` branches on `model.state` and `draftMode`. | A relationship reading is derived from saved/staged presence and UCI comparison; no explicit Edit mode. |
| Played alternative | `lastPlayedMove` creates `matching-played` or `unsaved-played`. | Those names leave the preferred panel. A still-local owner move is `Staged move`; history facts remain where needed. |
| Staging | `session.stagedMove` exists, but the workflow only enters an add draft automatically for an unassigned response. | Every owner move played for this decision is staged regardless of whether it matches the saved choice. |
| Saved play | `onPlaySavedMove` appends a local continuation and produces a focused played reading. | Clicking the saved box plays and stages the saved move, producing saved + staged matching without a mutation or confirmation. |
| Actions | `Add`, `Edit`, `Save replacement`, `Cancel edit`, and `Play saved move` exist. | Only `Save`, `Change effective date`, and `Remove` are normal panel actions. |
| Matching | Current matching branch exposes `Edit` and `Remove`. | Matching exposes `Change effective date` and `Remove`, with no `Save`. |

## 7. Interaction semantics

### 7.1 Selecting a move from the board or analysis

The selected behavior treats an owner move selected through the board or an analysis candidate as a
staged move immediately. It does not require clicking `Edit` first. The current path is
`RepertoireBuilderWorkspace.handleMoveIntent` → `applyMove` →
`selectPositionPickerMove` in `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`
and `frontend/src/features/repertoire-builder/positionPickerSession.ts`.

For an owner-colour move, the session currently returns `disposition: "staged"`, keeps the source
`currentPosition`, stores `stagedMove`, and displays the child preview; this is covered by
`positionPickerSession.test.ts` test “stages a bottom-side move without changing the current position”.
The selected panel calls this result `Staged move`, not `Played move` or a persisted event.

Selecting another legal owner move replaces the staged value locally without confirmation and without a
`PUT`. The latest move controls the right box and consequence. Promotion remains subject to the current
promotion picker; the canonical UCI includes the promotion suffix.

Opponent-colour moves may still advance the local continuation according to the current session model.
That board/history behavior is outside the preferred panel's owner-action relationship and remains
gated from `Save`.

### 7.2 Clicking the saved-choice box

When a confirmed saved move exists, the entire `Current saved choice` box is the play-saved capability.
It must:

- work with pointer click, Enter, and Space;
- have a visible `:focus-visible` treatment;
- expose a descriptive accessible name that includes the move and says it will play and stage the move;
- immediately replace a different temporary staged move without a confirmation;
- update the board to the child preview and the right box to the matching staged move;
- make the presentation saved + staged matching, so `Save` is withheld;
- make no persistence request and not claim that a new save occurred.

The current `onPlaySavedMove` callback instead calls `appendPositionPickerMove`, commits a local history
entry, and announces `Saved move played locally: ...` in
`frontend/src/features/repertoire-builder/preferredMoveWorkflowState.ts`. That is the behavior to
adapt, not the selected result. The selected capability must not remain as a separate `Play saved move`
button.

### 7.3 Save

`Save` is the one explicit move-persistence action:

- no saved + staged persists the first choice;
- saved + staged different replaces the saved choice;
- saved + staged matching has no `Save` action and cannot issue a no-op save;
- no staged, unknown, unsavable, opponent-turn, loading, error, illegal, or pending conditions cannot
  issue a move save;
- saving does not itself advance Move History or optimistically replace the confirmed saved box.

The request uses the source position's full FEN and the staged move's canonical UCI. Its effective date
is the selected UTC date when present, or the server's current UTC instant when omitted/blank. The
current client sends this through `putPreferredMove` in
`frontend/src/features/repertoire-builder/preferredMoveApi.ts`.

After successful `Save`, clear the local staged proposal and pending first-choice date, refresh the
preferred read, and announce the confirmed result once. The resulting settled reading is saved + no
staged, with `Change effective date` and `Remove`. Until the response and refreshed read succeed, retain
the old saved fact and staged proposal.

### 7.4 Remove

`Remove` is available only for a confirmed saved choice. It never removes a staged move. Keep the
existing `RemoveConfirmation` in
`frontend/src/features/repertoire-builder/PreferredMovePanel.tsx`:

- trigger the alert dialog;
- keep the current saved fact visible while the dialog is open;
- `Cancel` closes the dialog without a request and restores focus to the trigger;
- the dialog's `Remove` confirms and starts `DELETE /api/preferred-move`;
- retain the saved fact while the delete is pending or failed;
- after success, clear only the saved choice and its date, retain any staged move, refresh the read, and
  announce the confirmed result.

Therefore, removing from saved + staged different produces no saved + staged: the right box remains and
`Save` plus `Change effective date` are available. Removing from saved + no staged produces two empty
boxes and no actions. This differs from the current `runMutation`, which clears `session.stagedMove`
after every successful mutation in `preferredMoveWorkflowState.ts`.

The existing dialog title and description are `Remove preferred move?` and `This removes the saved move
for the current position.`; `RemoveConfirmation` uses `AlertDialog` focus management and should retain
that confirmation contract.

### 7.5 Change effective date

`Change effective date` is independent of move replacement:

- for an existing saved choice, it opens the date-only interaction and persists the new date without
  changing the saved UCI/SAN or the staged move;
- for a first choice, it is hidden until a move is staged, then selects a pending initial date for the
  subsequent `Save`;
- future days remain unavailable through `CalendarDate` and the server remains authoritative for
  timestamp validation;
- date-only pending/success/failure is reported as an operation, not as a new relationship layout;
- after a successful existing-record date change, the saved move remains in the same relationship
  reading and the one displayed date becomes the newly confirmed UTC day;
- a failed date operation retains the last confirmed date and any local staged/date input needed for a
  retry, without claiming success.

The current `DateControl` in `PreferredMovePanel.tsx` calls `onDateChange`, and
`CalendarDate` in `frontend/src/features/design-system/CalendarDate.tsx` normalizes a selected day to
UTC midnight and closes the popover. The current workflow only stores this as local `explicitDate`;
there is no date-only callback or mutation in `usePreferredMoveWorkflow`. This is a known canonical
impact boundary, not permission to change the settled user behavior.

### 7.6 Loading, pending, errors, and stale responses

- While either read is loading, preserve the panel shell but do not represent unknown saved presence as
  “No saved choice yet.” Withhold actions that depend on the missing result.
- While a mutation is pending, preserve the last confirmed saved box and the staged proposal, disable
  persistence triggers consistently, and use a polite status such as `Saving preferred move...`.
- On a typed read or mutation error, use the existing alert pattern, preserve confirmed/staged facts,
  and allow a meaningful retry. Do not change a failed operation into an optimistic success.
- When a position changes, abort/ignore stale reads and reset staging/date/mutation workflow for the old
  source position. A proposal for a previous FEN must never appear against a new position.

The read hooks clear response data on a new FEN and abort replaced requests in
`frontend/src/features/repertoire-builder/preferredMoveState.ts` (`usePreferredMoveState`) and
`frontend/src/features/viewer/positionContextState.ts` (`usePositionContextState`). The workflow also
increments a mutation id and aborts its controller in `usePreferredMoveWorkflow`.

## 8. Copy templates and anti-duplication rules

### 8.1 Component-owned templates

The relationship/model supplies structured facts (`saved.san`, `staged.san`, presence, equality,
saveability, and operation condition). The component owns the fixed templates. The minimum consequence
templates are:

| Relationship | Template |
| --- | --- |
| No saved + staged different/first choice | `Save {stagedSan} as the current saved choice.` |
| Saved + staged different | `Save {stagedSan} to replace {savedSan}.` |
| Saved + staged matching | `{savedSan} is already the current saved choice.` |
| Saved + no staged | No consequence sentence; the staged-box empty explanation is sufficient. |
| No saved + no staged | No consequence sentence; the staged-box empty explanation is sufficient. |

The first-choice empty explanation is one template populated with the saved fact when needed, for
example `Stage a legal move to propose the first saved choice.` or `Stage a legal move to propose
replacing e4.` The component must choose one explanation for the current empty staged box, not render
both a card explanation and a duplicate instruction elsewhere.

Gating and errors use typed status/feedback copy, not consequence templates. Do not encode the words
“pointless,” “matching-played,” or “unsaved-played” in the product panel.

### 8.2 Duplication rules

- **One date:** the saved effective date appears once. A pending first-choice date is shown once as a
  pending selection and is not repeated in the consequence or duplicated between the saved box and the
  date-picker trigger.
- **One consequence:** state the single persistence implication once. Do not repeat replacement copy in
  the connector, a paragraph, and a button label.
- **One empty explanation:** the empty staged box explains the next legal move action. Do not repeat the
  same instruction in a second empty card or footer paragraph.
- **One move value per fact:** each saved/staged fact gets one prominent SAN and optional UCI detail. Do
  not add a third “played move” value for the same staged proposal.
- **One context surface:** recurrence counts and corpus context remain in `PositionReachFrequency` and
  the concise panel context/feedback area; they are not copied into both boxes.
- **No review-sheet language:** design thesis, demo controls, state coverage, exploratory stamps, and
  handoff annotations never appear in product UI.
- **Action labels are exact:** normal panel actions are only `Save`, `Change effective date`, and
  `Remove`. Dialog `Cancel`, calendar `Clear date`, and calendar `Close` belong to their primitives.

## 9. Visual hierarchy, tokens, and responsive behavior

### 9.1 Hierarchy

The strongest visual order is:

1. panel heading and concise status;
2. saved/staged move values;
3. one relationship consequence;
4. effective date maintenance;
5. primary/secondary/subordinate actions.

The saved box is calm and stable. The staged box is visually distinct when it is a proposal and positive
but non-actionable when it matches. A status accent can reinforce ready, positive, blocked, or destructive
meaning, but text and action availability must remain sufficient without colour.

### 9.2 Existing token foundation

The current repository's reusable foundation is in `frontend/src/styles/cmt-tokens.css`:

- spacing is exactly 4/8/12/16/24/32/48 (`--cmt-spacing-*`);
- radii are 4/8/12 with an 8px default;
- elevation is reserved for major/floating emphasis;
- focus uses `--cmt-focus-ring-color`, `--cmt-focus-ring-width`, and
  `--cmt-focus-ring-separation`;
- information, success, warning, and error feedback roles use dedicated `--cmt-*` accent/container
  tokens.

Surface and text roles come from the Material theme, for example
`frontend/src/styles/material/material-theme-builder-css-export/css/dark.css`, which defines
`--md-sys-color-surface-container`, `--md-sys-color-surface-container-high`,
`--md-sys-color-on-surface`, `--md-sys-color-on-surface-variant`, and outline roles.
Typography is system-ui and role-based in `frontend/src/styles/cmt-typescale.css`. The HTML's raw
dark-theme values and private `--mono` typeface are review-sheet styling, not canonical token names.

The future component must translate the selected HTML's geometry into this foundation rather than copy
one-off values. The HTML approximates 20px panel padding, 15px box padding, a 10px box gap, a 17px
vertical rhythm, and an 8px action gap at
`02-staged-move-is-the-proposal-final-choice.html:453-457`,
`02-staged-move-is-the-proposal-final-choice.html:539-565`, and
`02-staged-move-is-the-proposal-final-choice.html:827-850`. The canonical scale should use the closest
approved tokens, normally 16/24/8 rather than new 15/17/20 tokens.

### 9.3 Semantic colour roles

Likely reusable semantic boundaries are:

- saved/persisted surface and text roles using Material surface/on-surface tokens;
- proposal/ready roles mapped to the existing warning family only where “ready to save” is intended;
- matching/confirmed roles mapped to the existing success family;
- blocked/error roles mapped to the existing error family;
- informational pending roles mapped to the existing information family;
- a shared outline/divider role and the existing focus ring.

If the panel needs dedicated semantic aliases, define them as reusable design tokens with documented
meaning, not as raw colours in `PreferredMovePanel.module.css`. Forced-colour behavior must collapse to
system `Canvas`, `CanvasText`, `ButtonBorder`, `Highlight`, and `HighlightText` roles.

### 9.4 Button hierarchy and icon/text geometry

Use the existing `Button` primitive in
`frontend/src/features/design-system/Button.tsx` and its token-driven CSS in
`frontend/src/features/design-system/Button.module.css` as the geometry baseline. It already uses
`inline-flex`, centered alignment, `gap: var(--cmt-spacing-8)`, shared size/padding families, and the
repository focus ring.

- `Save` is filled primary only when it is a valid next step.
- `Change effective date` is secondary/tonal and never competes with the consequence.
- `Remove` is visibly destructive but quiet/subordinate, retaining strong contrast and focus.
- Every icon is decorative support beside visible text, with `aria-hidden="true"`.
- Icons have a stable square box and the shared 8px label gap; no action defines a private icon gap.
- Pending and disabled controls retain readable labels and cannot be activated twice.

The selected HTML uses inline SVG icons at `02-staged-move-is-the-proposal-final-choice.html:1563-1575`.
The canonical implementation can use the installed icon system, but icon choice must not change the
visible labels or accessible names.

### 9.5 Responsive layout

- At wide widths, the boxes are peers in one row with the connector between them.
- At narrow widths, the boxes stack in reading order: saved, connector, staged; the connector points
  down; the action group wraps in the fixed order Save, Change effective date, Remove.
- Long SAN/UCI and error text wrap without page-level horizontal overflow.
- The panel remains usable inside the session column. `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.module.css`
  moves the session below the board at a 40rem container width, and
  `tests/e2e/repertoire-builder-storybook.spec.ts` checks the 412px constrained surface.
- The selected HTML uses review-sheet breakpoints near 800px and 560px at
  `02-staged-move-is-the-proposal-final-choice.html:1119-1265`; those values describe the visual
  direction, not a requirement to add unrelated page breakpoints.

## 10. Accessibility contract

### 10.1 Structure and names

- Keep one labelled section/region headed by the preferred-move heading.
- Give each box a visible label exactly `Current saved choice` and `Staged move`.
- Use a real button or equivalent button semantics for the saved-choice play-and-stage box.
- The saved-choice accessible name must identify the move and the action, for example “Current saved
  choice: e4; play and stage this move.”
- Use real buttons for `Save`, `Change effective date`, and `Remove`; visible text must be part of each
  accessible name.
- Do not make arrows, status dots, decorative box icons, or connector text focusable.

### 10.2 Keyboard and focus

- Tab order follows the visual reading order: saved choice, date/action controls as presented, then
  `Save`, `Change effective date`, and `Remove` according to the selected action order.
- Enter and Space activate the saved-choice control and all buttons.
- `:focus-visible` must be obvious on every dark surface and use the existing focus tokens.
- The panel must not intercept Move History's Arrow, Home, or End navigation. `MoveHistory` owns those
  keys in `frontend/src/features/move-history/MoveHistory.tsx` (`handleKeyDown`).
- After a successful mutation, keep focus on a sensible surviving control; do not jump to the page top.

### 10.3 Announcements

- Read failures and mutation failures use `role="alert"` through the existing feedback contract.
- Pending operations use one polite `role="status"`/`aria-live="polite"` message.
- A confirmed add/replace/remove/date result is announced once through the existing session status and/or
  panel status, not duplicated in multiple identical live regions.
- The relationship change is understandable from labels, move values, consequence, and action
  availability; colour is not required to understand it.

`FeedbackCore` forwards consumer-supplied live-region attributes and uses decorative Lucide icons in
`frontend/src/features/design-system/feedback/FeedbackCore.tsx`; `InlineFeedback` and `PanelFeedback`
are the existing wrappers. Do not build a second custom alert system.

### 10.4 Removal confirmation and date focus

- Opening `Remove` moves focus into the existing alert dialog.
- The dialog has the current title, description, `Cancel`, and `Remove` controls.
- Escape and cancel close without a request; focus returns to the triggering `Remove` button.
- The date popover uses the existing `CalendarDate` `initialFocus` and `finalFocus` behavior, so focus
  returns to `Change effective date`/its date trigger after closing.
- Future dates are disabled in the calendar, but typed server feedback remains available for invalid or
  rejected timestamps.

### 10.5 Non-colour, contrast, and motion requirements

State meaning must survive monochrome and forced-colour modes through visible labels, status text,
border/shape treatment, action availability, and focus rings. Do not rely on the saved check, proposal
arrow, or status colour alone. Respect `prefers-reduced-motion`; do not animate relationship changes in
a way that hides a pending or failed persistence result.

## 11. Current repository mapping: ownership and data flow

### 11.1 Page/session ownership

| Exact path and symbol | Current repository responsibility | Selected design implication |
| --- | --- | --- |
| `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx` — `RepertoireBuilderWorkspace` | Owns the page session, displayed child preview, board intents, candidate moves, history selection, Flip/Reset, and workflow wiring. | Keep board/session truth here. The panel must not create a second FEN, history cursor, or owner. |
| `frontend/src/features/repertoire-builder/positionPickerSession.ts` — `PositionPickerSession`, `selectPositionPickerMove`, `positionPickerSelectedTransition` | Stores prefix, local continuation, local moves, current source position, orientation, and `stagedMove`; staged owner moves preview the child without entering history. | `stagedMove` supplies the right box. Committed `localMoves` remain a separate history fact. |
| `frontend/src/features/repertoire-builder/RepertoireSessionPanel.tsx` — `RepertoireSessionPanel` | Composes controlled Move History, Position Reach Frequency, one live session status, and nested `PreferredMovePanel`. | Keep one history and one session status; do not duplicate them inside the preferred panel. |
| `frontend/src/features/move-history/MoveHistory.tsx` — `MoveHistory` | Renders stored prefix plus committed local continuation and owns keyboard navigation/focus restoration. | A staged proposal must not be inserted into Move History. |
| `frontend/src/features/position-reach-frequency/PositionReachFrequency.tsx` — `PositionReachFrequency` | Presents recurrence/frequency context from `PositionContextResponse`. | Keep frequency and corpus context separate from the two move boxes. |

`RepertoireBuilderWorkspace` currently computes `displayedPosition` from
`session.stagedMove?.position ?? currentPosition` and passes `workflow.stagedMove`, `workflow.positionModel`,
date, mutation, errors, and callbacks through `RepertoireSessionPanel`. That is the correct ownership
direction for the selected design, even though the callback names and model fields need adaptation.

### 11.2 Current preferred workflow

| Exact path and symbol | Current behavior | Selected difference |
| --- | --- | --- |
| `frontend/src/features/repertoire-builder/repertoireWorkflowModel.ts` — `RepertoirePositionModel`, `deriveRepertoirePositionModel` | Derives `saveability`, personal context, `savedMove`, `effectiveAt`, and the old four-value `state` from preferred data and focused played data. Assigned saved moves are exposed only when `sideToMove === bottomColor`. | Derive a relationship from confirmed saved/staged facts and canonical UCI equality. Keep saveability/turn/date facts, but stop making old played names the panel presentation API. |
| Same file — `PreferredMoveDraftMode`, `beginPreferredMoveDraft`, `stagePreferredMoveDraft`, `cancelPreferredMoveDraft` | Maintains explicit `add`/`edit` drafts; idle staging is only promoted to an add draft for an unassigned response. | Remove explicit Edit-mode semantics. Staging is the normal local proposal lifecycle. |
| `frontend/src/features/repertoire-builder/preferredMoveWorkflowState.ts` — `usePreferredMoveWorkflow` | Reads preferred data for the source FEN, reads context for current FEN, owns draft/date/mutation/error state, runs add/save/remove, and refreshes after success. | Replace add/edit callback distinctions with staged Save, independent date operation, and Remove that retains staging. |
| Same file — `runMutation` | Uses `PUT` for add/save and `DELETE` for remove, retains state on failure, clears draft/date/staging after any success, then increments `refreshToken`. | Preserve confirmed-only/error-safe behavior, but clear only the facts appropriate to each operation; Remove must retain staged move. |
| Same file — `onPlaySavedMove` | Reconstructs UCI, appends a local move, and sets `Saved move played locally: ...`. | Move this capability to the saved box and make it play plus stage rather than a separate panel button. |
| `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx` — `PreferredMovePanel` | Renders branches for saved, matching-played, unsaved-played, and no-saved; accepts `onAdd`, `onEdit`, `onSave`, `onCancelEdit`, `onPlaySavedMove`, and `onRemove`. | Compose the two-box relationship and only the three normal panel actions. |
| Same file — `DateControl` and `RemoveConfirmation` | `DateControl` wraps `CalendarDate`; `RemoveConfirmation` already uses `AlertDialog` with focus management and the required removal confirmation. | Retain the date primitive and removal confirmation semantics, adding the independent date-only persistence callback. |
| `frontend/src/features/repertoire-builder/PreferredMovePanel.module.css` | Uses existing surface, typography, spacing, and focus tokens but has a single flat panel layout. | Add token-driven peer boxes, relationship connector, consequence, responsive stacking, and saved-box focus treatment without raw mock-up colours. |

The current model uses `lastPlayedMove` and `lastPlayedPreferredMove` to inspect a focused committed local
transition. The selected visual may show the same user decision as staged, but it must not erase the
domain distinction between a child preview and a committed local line. Source FEN and local history
ownership remain unchanged.

### 11.3 Read flow and saveability

1. `usePreferredMoveWorkflow` chooses `playedTransition?.sourcePosition.fen` for a focused own-colour
   transition, otherwise `session.currentPosition.fen`, and passes that to `usePreferredMoveState`.
2. `usePositionContextState` reads context for `session.currentPosition.fen`.
3. `deriveRepertoirePositionModel` maps an assigned/unassigned preferred response and context to saved
   visibility, effective date, personal count, and saveability.
4. The selected relationship presentation combines that confirmed saved fact with `session.stagedMove`.
5. `Save`, date persistence, and `Remove` call typed workflow callbacks; success refreshes the read.

The current preferred client uses full FEN request identity while the backend stores the four position
fields. `preferredMoveApi.ts` validates the returned full FEN, assigned/unassigned shape, legal
canonical UCI, and typed failure code before the UI trusts it.

Saveability is specifically `context.overall_exists` in `deriveRepertoirePositionModel`: `true` is
savable even when the personal count is zero; `false` is unsavable; null context is unknown. The tests
“maps bottom color to its personal count and keeps zero savable,” “marks an absent overall position
unsavable,” and “keeps context unknown until a response exists” in
`frontend/src/features/repertoire-builder/repertoireWorkflowModel.test.ts` confirm this distinction.

### 11.4 API and backend contracts

| Exact path and symbol | Current contract | Selected panel use |
| --- | --- | --- |
| `frontend/src/features/repertoire-builder/preferredMoveApi.ts` — `PreferredMoveResponse` | `{ fen, state: "assigned" | "unassigned", move: { uci, san } | null, effective_at }`. | Assigned response fills the saved box; unassigned response confirms its empty state. |
| Same file — `fetchPreferredMove` | `GET /api/preferred-move?fen=<full FEN>&as_of=<optional>`. | Read current saved fact; historical `as_of` is not a panel control. |
| Same file — `putPreferredMove` | `PUT /api/preferred-move` with `{ fen, move_uci, effective_at? }`. | `Save` sends source FEN plus staged canonical UCI. A same-move/new-date request is the likely transport for date-only maintenance, subject to the remaining technical contract gap in section 14. |
| Same file — `deletePreferredMove` | `DELETE /api/preferred-move?fen=<full FEN>&effective_at=<optional>`. | `Remove` sends source/focused FEN and effective timestamp after confirmation. |
| `frontend/src/features/viewer/positionContextApi.ts` — `PositionContextResponse`, `fetchPositionContext` | `GET /api/position-context?fen=...` returns `overall_exists`, side counts, and totals. | Supplies saveability and recurrence context; it is not an assignment response. |
| `backend/app/features/preferred_move/router.py` — `preferred_move`, `put_preferred_move`, `delete_preferred_move` | Exposes GET/PUT/DELETE and maps typed validation, not-found, unavailable, and unexpected errors. | Keep UI messages based on safe typed codes, not internal details. |
| `backend/app/features/preferred_move/api_schemas.py` — `PreferredMoveRequest`, `PreferredMoveResponse`, `PreferredMoveMutationResponse` | Strict request/response models; no proposal field and no player field. | Proposal remains client-local; fixed ownership remains server-side. |
| `backend/app/features/preferred_move/service.py` — `_validated_fen`, `_mutation_timestamp`, `_canonical_move`, `get_preferred_move`, `set_preferred_move`, `remove_preferred_move` | Validates canonical FEN/legal UCI/UTC timestamps, rejects future mutation times, and maps storage state to assigned/unassigned. | Do not bypass legal-move, source-FEN, or future-date validation in the UI. |
| `backend/app/features/preferred_move/repository.py` — `PreferredMoveRepository.position`, `state_at`, `append` | Resolves existing game-derived positions, reads effective state, and appends events without creating schema. | A visually staged proposal is not a server event; an unsavable/not-found position cannot be faked into a save. |
| `scripts/opening_catalog/preferred_move.py` — `_set_preferred_move`, `_state_from_events`, `state_at` | Maintains append-only set/remove events and effective-time replay. | Replacement and removal remain timeline events; the UI's “current” means the confirmed read at the current instant. |
| `backend/app/features/position_context/router.py` and `service.py` — `position_context`, `get_position_context` | Returns neutral recurrence/corpus context for a full FEN. | Keep this context outside the saved/staged relationship facts. |

The backend README at `backend/app/features/preferred_move/README.md` confirms fixed-owner GET/PUT/DELETE
scope and no schema creation. `backend/tests/features/preferred_move/test_api.py` confirms explicit
unassigned responses, append-only set/replace/remove history, strict fixed ownership, UTC behavior, and
typed errors. `tests/opening_catalog/test_preferred_move.py` confirms lower-level effective-time and
append-only event semantics.

## 12. Abstraction contract for a canonical implementation

The selected direction requires reusable abstractions rather than a panel-specific collection of raw
styles and one-off button markup. The boundaries below are design contracts, not ordered work stages.

### 12.1 Tokens

Use or extend the repository's token layers before composing the panel:

- global foundation spacing, radii, elevation, and focus tokens from
  `frontend/src/styles/cmt-tokens.css`;
- Material surface, text, outline, and primary/secondary roles from the existing theme exports;
- fixed feedback severity roles for information, success, warning, and error;
- semantic preferred-panel aliases only if they have reusable meaning, such as persisted surface,
  proposal surface, matching surface, and blocked surface.

Token names must describe role, not a mock-up colour. The component CSS must not introduce private raw
hex values for the selected dark theme. If a token is feature-specific rather than globally reusable,
keep the alias boundary explicit and document the role.

### 12.2 Reusable primitives

Likely primitive boundaries, grounded in existing repo patterns, are:

- a relationship/panel region primitive that owns heading association and status placement;
- a `PreferredMoveChoiceBox` accepting `saved`/`staged`, empty/value content, and optional saved-box
  activation semantics;
- a move-value primitive that renders SAN as the primary value and UCI as supporting detail;
- a relationship connector primitive that is decorative and responsive;
- a component-owned consequence formatter with fixed templates;
- an effective-date control built on `CalendarDate` and UTC utilities;
- a shared action layout primitive that establishes icon box size, 8px icon/text gap, focus, disabled,
  pending, and wrapping behavior;
- a removal confirmation wrapper retaining the current `AlertDialog` contract.

### 12.3 Required reusable Save and Remove components

`Save` and `Remove` must be reusable button components at minimum, rather than anonymous `<Button>`
instances embedded only in this panel. They should share the existing `Button` geometry and expose
consistent semantics for:

- fixed visible labels (`Save` or `Remove`);
- pending and disabled behavior;
- keyboard activation and the repository focus ring;
- decorative icon handling and the shared icon/text gap;
- optional operation status integration without duplicate announcements.

`Remove` may compose the reusable destructive trigger with `RemoveConfirmation`; the confirmation is
part of the interaction contract, while the underlying button remains reusable. `Change effective date`
can use the same shared action layout and the existing `Button` primitive, but it must not be silently
renamed to `Edit` or `Date`.

### 12.4 Model/presentation boundary

The panel should receive a relationship model and operation callbacks. It should not decide source FEN,
legal move validity, owner identity, current history, or whether a board move is committed. Fixed copy
templates belong to the component/presentation layer; the model supplies structured facts. This prevents
the old `model.state` and finished-prose coupling from returning under a new name.

## 13. Likely canonical impact map and focused coverage

This is a descriptive impact map, not an implementation sequence.

### 13.1 Areas likely to change or be assessed

| Exact path | Why it is relevant |
| --- | --- |
| `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx` | Main visual composition; remove old branch/action vocabulary, add two-box relationship, saved-box activation, exact actions, date operation, and transient feedback treatment. |
| `frontend/src/features/repertoire-builder/PreferredMovePanel.module.css` | Translate selected peer-box hierarchy, semantic accents, consequence, focus-visible saved box, responsive stack, and button wrapping onto existing tokens. |
| `frontend/src/features/repertoire-builder/repertoireWorkflowModel.ts` | Add/derive relationship facts without using `matching-played` or `unsaved-played` as panel view states; preserve canonical UCI and source-position facts. |
| `frontend/src/features/repertoire-builder/preferredMoveWorkflowState.ts` | Make every owner play staged, move saved-play behavior to staging, add date-only operation semantics, preserve staging after Remove, and retain confirmed-only mutation behavior. |
| `frontend/src/features/repertoire-builder/positionPickerSession.ts` | Preserve staged-preview versus committed-history semantics while supporting the saved-box play-and-stage path. |
| `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx` and `repertoireBuilderWorkspaceModel.ts` | Remove special `savedMovePlayable`/`isPlayedSavedMove` panel-button path without breaking local board, candidate, promotion, source-FEN, or history behavior. |
| `frontend/src/features/repertoire-builder/RepertoireSessionPanel.tsx` | Keep one controlled history and one session status while passing the selected relationship props. |
| `frontend/src/features/design-system/Button.tsx` and `Button.module.css` | Supply the reusable Save/Remove button contract or a semantic wrapper aligned with the existing token-driven Button. |
| `frontend/src/features/design-system/CalendarDate.tsx`, `CalendarDateUtils.ts`, and related CSS | Preserve UTC-day normalization, future-day blocking, popover focus return, and one date display while enabling date-only persistence. |
| `frontend/src/features/design-system/feedback/FeedbackCore.tsx`, `InlineFeedback.tsx`, `PanelFeedback.tsx` | Preserve typed alert and polite status semantics without duplicate live-region narration. |
| `frontend/src/features/repertoire-builder/preferredMoveApi.ts` and `backend/app/features/preferred_move/*` | Assess the date-only transport. Existing move set/remove contracts should remain strict, fixed-owner, legal, and append-only. |
| `frontend/src/features/repertoire-builder/README.md` and feature stories | Current prose names add/save/play/edit behavior and will need to distinguish selected behavior if the exploration is adopted. |

### 13.2 Existing focused frontend tests and stories requiring adaptation

These files currently prove the old UI vocabulary or the domain behavior that the selected UI must
preserve:

- `frontend/src/features/repertoire-builder/PreferredMovePanel.stories.tsx` — stories
  `UnassignedSavable`, `AssignedSaved`, `EditReplacement`, `MatchingPlayed`, `UnsavedPlayed`,
  `Loading`, `ErrorFeedback`, and `SavingMutation` currently assert `Add`, `Edit`, `Save replacement`,
  `Cancel edit`, `Play saved move`, old `data-state` values, and played prose. They need selected
  relationship fixtures and exact action-label assertions.
- `frontend/src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx` — `LocalLineSession`,
  `SavedMove`, `MatchingPlayed`, and `UnsavedPlayed` currently compose the old panel callbacks and
  labels; the history/frequency assertions should remain while panel expectations move to the new
  relationship readings.
- `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx` —
  `AssignedBoardPlay`, `UnsavedPlayedConstrained`, `EditReplacement`, `DatedAdd`, `MutationFailure`,
  and `RemoveConfirmation` cover board preview, replacement, date, failure retention, and removal.
  Their board/history/API assertions remain valuable, while old panel names and saved-play behavior
  need adaptation.
- `frontend/src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx` — `ReadErrors` and
  `OpponentLocalOnly` cover separate alerts and local opponent behavior. They should keep those domain
  guarantees while dropping any implication that opponent turn is a preferred-panel state.
- `frontend/src/features/repertoire-builder/repertoireWorkflowModel.test.ts` — the parameterized
  “derives the %s state from saved and last-played workflow data” test currently locks in old state
  names; the saveability, own-turn visibility, effective-date, and canonical comparison facts still
  need coverage under the relationship model. The “starts and cancels explicit Add/Edit drafts” and
  “stages only a bottom-color move and preserves the Add/Edit mode” tests specifically encode behavior
  the selected design removes.
- `frontend/src/features/repertoire-builder/positionPickerSession.test.ts` — tests “stages a bottom-side
  move without changing the current position,” “derives a staged transition from its current parent
  without committing it,” “navigates combined history through represented bounds and cancels staging,”
  and “plays a saved move through the same strict local continuation” protect preview/history/source
  facts that must not be lost.
- `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx` — tests for staging,
  Add, Edit replacement, matching/unsaved played panels, saved local play, date normalization,
  navigation/Flip/Reset cancellation, alerts, and overflow require updated panel queries but retain
  their board, history, source-FEN, and failure-retention assertions.
- `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx` — tests
  “requires confirmation before Remove and only clears the saved move after success,” “uses UTC-midnight
  for a selected date and clears it only after success,” “retains the staged move and date when a
  mutation fails,” saved promotion play, local candidate activation, and accessibility should cover
  the selected Remove-retains-staged and saved-box keyboard semantics.
- `frontend/src/features/repertoire-builder/preferredMoveState.test.ts` — `usePreferredMoveState`
  null-position, full-FEN, abort/stale-response, typed-failure, and effective-date tests protect the
  read condition overlay.
- `frontend/src/features/repertoire-builder/preferredMoveApi.test.ts` — `fetchPreferredMove`,
  `putPreferredMove`, and `deletePreferredMove` tests protect strict response validation, full-FEN
  identity, legal UCI, promotion, typed errors, and UTC request encoding. A date-only transport test
  would belong here if the chosen wire shape uses the existing client.
- `tests/e2e/repertoire-builder-storybook.spec.ts` — the Storybook proof covers wide/constrained
  placement, no overflow, staging, stored prefixes, opponent-local play, navigation/Flip cancellation,
  assignment/replacement, date, failure retention, removal confirmation, keyboard activation, and Axe.
  Its current `expectPreferredMoveState` helper and old action/name assertions need relationship-based
  replacements.

### 13.3 Existing backend/storage tests to preserve or extend

- `backend/tests/features/preferred_move/test_api.py` — `test_lifecycle_returns_explicit_unassigned_state_and_preserves_append_only_history`,
  `test_same_effective_move_is_a_noop_without_a_new_event`, UTC timestamp tests, invalid/future-time
  tests, full-FEN identity, fixed ownership, not-found, unavailable schema/database, safe errors, lock,
  and CORS tests define the server boundary. A date-only interaction must not weaken these contracts.
- `tests/opening_catalog/test_preferred_move.py` — `test_effective_recorded_and_tied_correction_timelines`,
  `test_independent_streams_validate_moves_and_reject_unobserved_positions`, history replay, and line
  replay tests define append-only/effective-time behavior beneath the API.

## 14. Stable design invariants

These invariants are the durable handoff. A future Plan must preserve them when translating the design
into canonical code:

1. The panel relationship is derived from saved presence, staged presence, and canonical saved/staged
   comparison; it is not driven by old `matching-played` or `unsaved-played` view-state names.
2. The left box means the last confirmed persisted choice for the focused source position.
3. The right box means a local staged move. A staged move is not confirmed persistence.
4. Every owner move played for the preferred decision is staged immediately; explicit Edit mode does not
   exist.
5. A staged differing move is the replacement/first-choice proposal that `Save` would persist.
6. A staged matching move is already saved and has no `Save` action.
7. The saved-choice box is the accessible play-and-stage capability and replaces any temporary staged
   proposal without confirmation.
8. `Save` persists only the staged move at the source FEN, with legal canonical UCI and the selected UTC
   effective date where applicable.
9. `Remove` never removes staging and never runs before the existing confirmation.
10. `Change effective date` is independent date-only persistence for an existing saved choice; for a
    first choice it selects the initial date once a move is staged and `Save` persists it.
11. Only `Save`, `Change effective date`, and `Remove` are normal panel action labels.
12. `unsavable` and `opponent-turn` gate the relationship actions; they do not create panel states.
13. Loading, mutations, and errors are transient conditions in the same shell, never alternate settled
    layouts or optimistic persistence claims.
14. The effective date is shown once, the consequence once, and the empty-state explanation once.
15. Move History remains the only history surface; a staged child preview is not inserted into it.
16. The panel does not own a second source of FEN, owner identity, legal-move validation, or history
    cursor.
17. Confirmed saved data remains visible during pending/failing mutations; staged/date input is retained
    when a mutation fails so the user can recover.
18. State meaning is available through text, semantic grouping, action availability, non-colour indicators,
    contrast, and focus treatment.
19. Save/Remove and the shared action layout retain reusable component semantics, visible labels,
    consistent icon/text spacing, pending/disabled behavior, and focus treatment.
20. The relationship remains understandable when boxes stack on narrow screens and the page does not
    overflow horizontally.
21. Review-sheet annotations and demo controls never enter the product panel.

## 15. Genuine remaining implementation fact

No product decision in the brief remains open. One technical API-shape fact must be resolved by a future
canonical implementation without changing the settled interaction: the current frontend workflow has no
date-only callback, and the backend exposes move `PUT` plus removal `DELETE`, not a named date-only
endpoint. The implementation must choose whether `Change effective date` uses a same-move `PUT` with a
new `effective_at` or adds a dedicated date-only wire operation. Either choice must preserve independent
date semantics, append-only/effective-time storage, fixed ownership, UTC validation, and the staged move
unchanged. This is an API transport decision, not a reason to reopen the label, action visibility, or
user mental model.
