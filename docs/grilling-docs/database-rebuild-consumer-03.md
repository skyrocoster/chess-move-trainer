# Database rebuild CONSUMER-03 direction

> **Status:** confirmed 2026-09-10
> **Purpose:** directional evidence for assessing and planning `CONSUMER-03`; this record does not authorize implementation

## Outcome

Migrate Repertoire's existing position-context workflow from the legacy position-context request to the enriched generated
`getPositionInsight()` operation without redesigning its presentation or adopting any later Repertoire consumer workflow.

## Confirmed behavior

- The selected Repertoire position remains the only position whose context is loaded.
- The color shown at the bottom of the board remains the trainer color supplied to position insight. Flipping the board
  refetches context for the newly selected color; a brief use of the existing loading behavior is acceptable.
- Position Reach Frequency continues to show the number of distinct games that reached the position out of the total
  eligible games for that trainer color, together with the existing frontend-formatted percentage.
- The compact context summary remains `Seen in N games as White/Black`; it does not gain a denominator or percentage.
- If the position was observed in imported games but has zero experience for the selected trainer color, the frequency
  panel continues to show `0 of N`, while the compact summary continues to say `Never seen as White/Black`.
- Only a position never observed in any imported game uses the existing global absent presentation.
- Corpus presence continues to control the current Preferred Move saveability restriction. Removing that restriction
  remains part of `CONSUMER-06`, not this slice.
- Existing loading and user-facing error behavior should be preserved unless the clean generated client's fixed contract
  requires a strictly equivalent mapping.

## Data interpretation

- Reach Frequency uses `experience.distinct_game_count` as its numerator and `experience.total_game_count` as its
  denominator. Occurrence totals do not replace the distinct-game meaning of the existing `N of M games` presentation.
- `observed_in_games` supplies the all-color corpus-presence distinction needed by the current absent and saveability
  behavior.
- The clean request requires `fen`, `trainer_color`, and `as_of`. Planning may settle the implementation-only source of
  `as_of` because C03 does not display or adopt the response's date-resolved preference.

## Slice boundaries

- Use the checked-in generated position-insight client directly; do not add a fallback or compatibility adapter.
- Although one position-insight response also contains observed moves, analysis, opening recognition, and preference,
  C03 consumes only the fields needed for the existing position-context workflow.
- Do not migrate move-response distribution (`CONSUMER-04`), analysis (`CONSUMER-05`), or preferred-move reads and
  mutations (`CONSUMER-06`).
- Do not retire `/api/position-context`; route retirement remains `RETIRE-02`.
- Do not restore Viewer behavior, redesign Repertoire, add a second cache, or change backend/database contracts.

## Planning acceptance direction

Focused proof should establish the generated clean request and required inputs, preserved selected-position and
board-flip behavior, preserved frequency/summary/absence/saveability meanings, tolerance of additive response fields,
and continued isolation of later consumer workflows and the legacy route-retirement slice.
