# Repertoire Builder Direction — Confirmed Product Synthesis

**Status:** Confirmed directional synthesis
**Implementation authority:** None
**Relationship:** This historical record preserves the confirmed Repertoire Builder direction and links to the
[direction-settled Master Plan](../../plans/active/repertoire-builder/repertoire-builder.md). It does not authorize
implementation, API changes, schema changes, dependency installation, database writes, or Plan execution.

## Purpose and boundary

This record consolidates the confirmed product direction for a manual Repertoire Builder. It is directional evidence,
not an implementation specification. Every implementation slice requires its own focused Plan and an explicit
coordinator execution route. The eight slices are sequential and must never run in parallel.

The abandoned S5 tracked-player projection remains abandoned and not accepted. Future work uses accepted S4 facts and
the existing corpus directly; it does not revive, repair, or reinterpret S5.

## Confirmed destination

Chess Move Trainer will add a `/repertoire` page and a **Repertoire Builder** navigation entry. The page uses the
Viewer-style workspace layout and opens at the standard starting position with White at the bottom.

The user may instead start from an existing game UUID and ply. That state displays the complete game prefix through the
selected ply, followed by the local session moves. The initial alternate-game orientation places Skyrocoster's actual
recorded game color at the bottom.

## Board and session semantics

- The bottom color means **me**. Only decisions made when the side to move matches the bottom color are stored as
  preferred moves.
- Opponent moves are local context only. They can vary between branches and are never persisted.
- There is one local line at a time: a compact SAN list, no move tree, and no line table.
- The shared navigation bar provides **Previous**, **Next**, and **Flip**. There are no separate Undo or Reset
  controls for this workflow.
- Previous and Next traverse local session history. Going back and then playing another move discards only the later
  local continuation; persisted preferred moves remain unchanged.
- Flip is available during the line, keeps the current position, cancels any pending unsaved response, and
  reinterprets which color is “me.” The Flip/navigation capability is implemented and proven in Viewer first, then
  reused by Repertoire Builder.

## Preferred-move interaction

- A saved move is shown only when the side to move matches the bottom color. An opposite-orientation preferred move is
  hidden on opponent turns.
- An existing move opens read-only and shows its SAN and UCI, with explicit **Edit**, **Play saved move**, and
  confirmed **Remove** actions.
- Add and Edit select one legal move by board drag/drop or by clicking any displayed legal engine candidate, including
  the rank-1 **Best line**. Candidate activation behaves exactly like a legal board drag.
- On “my” turns, a selected move is staged and requires explicit **Add** or **Save**. On opponent turns, a selected
  move advances immediately and is never persisted.
- Remove uses the existing append-only DELETE API.
- A position absent from the entire accepted corpus remains navigable but is unsavable under the existing
  storage/API boundary. A position with zero occurrences in Skyrocoster's requested bottom-color scope but existing
  elsewhere in the corpus shows **Never seen as White/Black** and remains savable.

## Neutral position context

A new neutral, FEN-based position-context endpoint is separate from the preferred-move API. It reports overall corpus
eligibility and distinct-game recurrence for the stable subject's requested game-color scopes, `white` and `black`.
The scopes mean the color Skyrocoster played in the game, not the side to move in the requested position.

The endpoint uses accepted S4 recurrence facts or direct accepted recurrence data, including `color_scope` and
`distinct_game_count`. It does not create a schema, revive S5, store a username identity, or add a materialized
personal projection.

The shared context statistic is integrated into Viewer first and then reused in Repertoire Builder. Repertoire Builder
shows the count for the current bottom color; Viewer exposes the shared White/Black statistic. The UI displays
**Seen in N games as White/Black** or **Never seen as White/Black** while retaining the separate overall-existence
signal needed for saveability.

## Date behavior

There is one reusable styled UTC calendar-date component using the explicitly approved `react-day-picker` dependency
inside the established Base UI Popover and design tokens.

- The component has no editable time.
- Blank means effective now.
- A selected date maps to `00:00 UTC`.
- Future dates are unavailable.
- The date applies to Add, Edit/replace, and Remove mutations and clears after each successful mutation.

## Analysis and Viewer-first reuse

Repertoire Builder reuses the full existing AnalysisPanel controls. Candidate rows and the rank-1 Best line become
clickable through an optional/shared controlled callback. The behavior is proven in Viewer first, including the same
legal-move and promotion path as a board drag, then reused in Repertoire Builder.

Flip/navigation, the neutral position statistic, and clickable analysis moves are all Viewer-first capabilities. Viewer
work is split into independent slices so each shared boundary is proven before the new page consumes it.

## API, storage, and identity boundaries

The completed [preferred-move API Plan](../../plans/done/preferred-move-api/preferred-move-api.md) is an accepted
foundation, not a new slice. Its existing GET/PUT/DELETE lifecycle remains authoritative.

The following boundaries remain fixed:

- one manually selected preferred move;
- fixed stable Skyrocoster UUID ownership, with no player selection or authentication identity;
- exact four-field position identity: placement, side to move, castling, and legally relevant en-passant state;
- full six-field FEN at the HTTP boundary;
- legal canonical UCI and backend-derived SAN;
- existing game-derived corpus positions only;
- append-only preferred-move history, including removal events; and
- no schema change or request-time schema creation.

Engine output, recurrence, and context facts inform the interface but never silently select or persist a preferred
move.

## Confirmed ordering rationale

The approved sequence is:

1. **A1 — Neutral position-context API.** API-first is limited to this narrow neutral endpoint because the
   preferred-move API already exists.
2. **V1 — Viewer Flip/navigation.** Prove the shared Flip capability in the existing Viewer.
3. **V2 — Viewer position-count integration.** Prove the shared neutral statistic in Viewer.
4. **V3 — Viewer clickable analysis moves.** Prove all displayed legal candidates, including Best line, in Viewer.
5. **R1 — Reusable UTC calendar component.** Create only this settled non-Viewer reusable dependency/component.
6. **R2 — Repertoire Builder scaffold.** Keep the route, navigation, layout, and standard starting board thin; do not
   create temporary workflow contracts or placeholder persistence.
7. **W1 — Position picker and local session mechanics.** Establish prefix/local-line, move, orientation, and
   navigation semantics before persistence.
8. **W2 — Complete preferred-move workflow.** Add preferred reads, staging, Add/Save, Edit, Play, Remove, date
   behavior, context/saveability messaging, and the existing API integration.

No slice runs in parallel. This ordering avoids speculative APIs, duplicate Viewer capabilities, premature generic
components, scaffold contracts that must be replaced, and persistence being mixed into unproven session mechanics.

## Explicit exclusions

- Reviving, repairing, or publishing the abandoned S5 tracked-player projection.
- New schema objects, migrations, recurrence rebuilds, materialized personal projections, caches, or line/tree storage.
- Username identity, player selection, authentication, authorization, or additional ownership models.
- Speculative APIs, session-storage contracts, multiple preferred moves, automatic preferred-move selection, or
  automatic engine/population authority.
- Changes to accepted S4 facts, the existing corpus, the completed preferred-move API contract, or append-only history.
- Separate Undo/Reset controls, move trees, broad repertoire architecture, universal Viewer/session/workspace
  frameworks, or unrelated visual redesign.
- Dependencies other than the explicitly approved `react-day-picker` dependency.
- README edits, completed-plan edits, historical rewrites, runtime database writes, commits, and pushes.
