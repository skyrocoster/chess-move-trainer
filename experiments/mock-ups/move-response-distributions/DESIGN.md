# Move response distributions

> Noncanonical design evidence only. This document is not an implementation Plan and does not authorize
> product changes.

## Outcome and signed-off evidence

The approved direction is focused **01C, “Grouped tail with disclosure”**. The default composition is a classic pie
with up to five highest-ranked common replies, each labelled with SAN and a rounded percentage. Remaining replies are
one grey **Other** sector and disclosure control. The archived comparison remains at:

- `experiments/mock-ups/move-response-distributions/` — signed-off focused default page.
- `experiments/mock-ups/move-response-distributions/archive/round-02-catalogue/` — preserved Round 02 catalogue and
  rejected alternatives; reference-only.

The first integration target is **Repertoire Builder**. Viewer integration is excluded initially, although the
distribution presentation should be composable for later reuse.

## Mental model and composition

The panel answers: “From this current position, what replies occurred in games matching the selected repertoire
colour?” It is a response-distribution view, not a recommendation engine and not a second board.

In Repertoire Builder, compose it in the existing position/session context area, alongside the existing
`PositionReachFrequency` presentation. The existing board, current line, position description, controls, and analysis
remain owned by `RepertoireBuilderWorkspace`; the new panel supplies the distribution card and its interaction model.
Reuse the existing `InteractiveBoardAdapter`/`BoardEvalStage` board rather than adding the mock-up's separate preview
board to canonical UI. The exact child insertion point within the current session-panel composition is a planning
detail to confirm.

The visible hierarchy is:

1. Current position and selected repertoire colour context.
2. A distribution card with a classic labelled pie and equivalent text controls.
3. Common replies ranked first; a grey Other row/sector only when a tail exists.
4. Expanded tail controls when Other is disclosed.

The mock-up's framing copy, simulated-corpus labels, raw CSS values, and exploration stamp are not product copy or
canonical tokens. Production styling uses CSS Modules with existing Material/CMT tokens and semantic roles for
selection, muted Other, surfaces, borders, and status.

## User-visible behaviour

- The backend request is keyed by the current canonical position and selected repertoire colour. A position or colour
  change replaces the prior result; stale responses must not overwrite the new panel.
- The frontend ranks the complete returned move set by the supplied stable rank, presents ranks 1–5, and groups all
  remaining replies into Other. If there is no tail, Other is omitted.
- Common sectors and their text controls invoke the same move-selection path. Selecting a reply passes its UCI through
  the Repertoire Builder's existing `handleMoveIntent`/`applyMove` flow and advances according to that flow to the
  resulting position. It does not create a separate preview or mutation path.
- Other is never a move. Its grey sector and text control only toggle disclosure. When expanded, each tail reply gets
  its own text control and uses the same move-selection path as a common reply.
- The selected reply is visibly identified in the control list and current-position context. Selecting a new position
  clears the old distribution selection and requests the replacement distribution.

### States and transitions

The panel has explicit states, independent of the chart library:

- **Loading:** retain the panel heading and colour context, show a bounded loading message/skeleton, and announce the
  pending request. Do not present stale replies as belonging to the new position.
- **Available:** show the pie, ranked controls, and Other disclosure when applicable.
- **No games / no data:** a successful response with zero matching games (or no move rows) shows an explanatory empty
  panel instead of an empty chart. It offers no misleading Other control.
- **Unavailable:** an invalidated or failed data source shows a clear unavailable message and retry action while
  leaving the board and existing local move flow usable.

Retry requests the current position/colour only. Loading, replacement, and error messages use a live status where
useful; a move-selection status remains owned by the existing workspace flow.

## Data semantics and endpoint contract shape

The dedicated endpoint should accept a canonical parent FEN and `color=white|black`, and return normalized position
data in this shape (exact route name and error-code names remain to be settled):

```json
{
  "fen": "<canonical parent FEN>",
  "color": "black",
  "matching_game_count": 12480,
  "replies": [
    {
      "rank": 1,
      "child_uci": "e7e5",
      "san": "e5",
      "distinct_game_count": 4118,
      "opening_name": null
    }
  ]
}
```

Contract invariants:

- `matching_game_count` is the number of distinct games of the requested game colour containing the parent position.
- Each reply is a `branch_kind=move` row for the parent position and selected `color_scope`; `child_uci` is the stable
  interaction key, `san` is the move label, and `distinct_game_count` is the count used by the UI. `raw_event_count`
  must not drive the distribution.
- Replies include the complete move set needed for frontend disclosure. `rank` is 1-based and deterministic for the
  accepted data snapshot: descending `distinct_game_count`, then a stable UCI tie-break. The frontend does not
  re-rank by arrival order.
- `opening_name` is nullable/optional. Include a name only when classification is reliable; an unclassified move stays
  valid and displays no placeholder.
- The frontend computes each rounded percentage from
  `distinct_game_count / matching_game_count * 100`. These are percentages of matching games, not mutually exclusive
  shares. Other sums the tail branch counts and uses the same denominator.

**Repeated-parent edge case:** one game can reach the same parent position more than once and take different child
moves. The chosen semantics de-duplicate within each `(parent position, child move, colour)` branch, so that game
contributes at most once to each branch's `distinct_game_count`; it is not globally de-duplicated across child moves.
Consequently branch percentages, and the sum represented by the pie labels, can exceed 100%. The UI must not describe
the sectors as mutually exclusive games or silently force global de-duplication.

The backend should follow the existing accepted, read-only recurrence-scope pattern: query
`opening_recurrence_branch_projection` by the parent four-field position key, `branch_kind`, and colour scope, with
the parent matching-game count from the corresponding normalized position data. A successful zero result is data, not
an infrastructure error. The endpoint's invalid/unavailable/unexpected failures should follow the existing
`{code,message}` response-envelope style used by position context.

## Ownership and repository seams

**Backend owns:** accepted-scope lookup, position/colour validation, projection queries, distinct branch counts,
deterministic ranks, SAN/child-position normalization exposed by the contract, and reliable optional classification
lookup. It does not group the top five or own disclosure/presentation state.

**Frontend owns:** request lifecycle, loading/empty/unavailable models, top-five and tail grouping, rounded labels,
chart/list composition, selection/disclosure state, announcements, and dispatch into the existing move flow. Follow
the separation demonstrated by:

- `frontend/src/features/position-reach-frequency/PositionReachFrequency.tsx`
- `frontend/src/features/position-reach-frequency/positionReachFrequencyModel.ts`
- `frontend/src/features/viewer/positionContextApi.ts`

The builder's integration seam is in
`frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`: `applyMove` and `handleMoveIntent` are
the existing move paths. The feature must not mutate repertoire records merely by displaying or selecting a reply;
existing workflow semantics remain authoritative.

The move-level source is `opening_recurrence_branch_projection` in `data/database/schema.txt`, whose relevant fields
are the parent position key, `branch_kind`, `child_uci`, `color_scope`, `raw_event_count`, and
`distinct_game_count`. The current position-context implementation in
`backend/app/features/position_context/` is the repository precedent for strict contracts, accepted read-only data,
and explicit unavailable failures.

## Accessibility, responsive, and motion requirements

- Keep the text controls as a complete non-colour interaction path. A chart sector must call the same callback as its
  corresponding control, but the chart must never be the only way to identify or choose a move.
- Move controls are keyboard-operable buttons with an accessible SAN/name, count, percentage, and optional opening
  name. Use `aria-pressed` for selected move controls.
- Other is a disclosure button with `aria-expanded` and `aria-controls` pointing at the tail region. Its accessible
  name must say that it reveals or hides replies; it must not sound like a playable move. Keep focus predictable when
  opening and closing the region.
- Expose loading, empty, unavailable, and move-selection changes through a suitable status/live region without
  duplicating the same announcement in every control.
- Preserve visible focus, text labels, and contrast in forced-colors mode; sector colours and swatches are supplemental,
  not the only state cue. Respect reduced motion and avoid chart animation as a prerequisite for comprehension.
- At 412px and narrower, stack the chart and controls, allow secondary text to wrap, keep SAN/count/percentage
  readable, and prevent horizontal overflow. The text list remains the reliable mobile reading order.

## Focused behavioural proof expectations

Implementation assessment should cover only the feature's focused behaviour:

1. API/model contract: selected colour and canonical position are sent; strict success, empty, unavailable, and
   failure responses map to the four visible states; optional opening names do not create placeholders.
2. Semantics: top five are ranked from stable inputs, all remaining rows appear under Other, Other is omitted without a
   tail, and branch counts use distinct-per-branch semantics including the repeated-parent overlap case.
3. Interaction: every common sector/control pair selects the same UCI; tail controls do likewise after disclosure;
   Other never calls move application; selected moves advance through the existing builder seam.
4. Accessibility/responsiveness: keyboard operation, `aria-expanded`/`aria-controls`, live status, visible focus,
   forced-colors/reduced-motion behaviour, and no horizontal overflow at 412px.

## Exclusions and escalation boundaries

- Viewer is out of the first integration scope.
- No new canonical board, separate preview state, recommendation ranking, raw-event chart, global game de-duplication,
  or repertoire mutation is part of this design.
- Recharts is available to this experiment but is **not** a canonical frontend dependency. Choosing Recharts (or an
  existing/alternative chart primitive) for product UI is an explicit implementation dependency decision; it must be
  resolved during planning rather than inferred from this mock-up.
- Planning must resolve the endpoint path/error codes, exact insertion point in the existing session-panel layout,
  SAN derivation/normalization source, and the reliability/lookup boundary for optional opening names. None of these
  boundaries authorizes implementation or reopens the signed-off 01C composition.
