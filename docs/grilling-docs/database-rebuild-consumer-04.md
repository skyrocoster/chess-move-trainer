# Database rebuild CONSUMER-04 direction

> **Confirmed:** 2026-09-10
> **Purpose:** durable product direction for planning `CONSUMER-04`; this record is not implementation authorization.

## Outcome

Repertoire's move-response pie chart answers:

> Among recorded occurrences of this position in the selected trainer's games, what percentage of the next moves were X?

The clean Position Insight response already contains the authoritative observed-move counts needed for this meaning.

## Settled behavior

- Every occurrence of the selected position that has an outgoing move is one sample.
- Repeated occurrences in one game count separately. This is an edge case and is not expected to materially change the ordinary result.
- An occurrence where the game ended at the selected position has no next move and is excluded from the distribution.
- A move's percentage uses its `occurrence_count` divided by `observed_move_totals.occurrence_count`. The complete pie therefore represents 100% of recorded outgoing-move occurrences, subject only to display rounding.
- Moves are ranked deterministically by occurrence count.
- Keep the current five most frequent moves plus the expandable **Other** grouping.
- Continue to label moves with standard algebraic notation (SAN), derived in the frontend from the selected FEN and the clean UCI move.
- Remove per-reply opening names. The chart remains focused on move, occurrence count, and percentage rather than requesting a new child-position opening projection.
- Preserve the meaningful empty-state distinction between no matching trainer games and no recorded next moves.

## Scope boundary

- `CONSUMER-04` migrates the Repertoire move-response workflow to observed moves from the existing generated Position Insight operation.
- It does not add or change a backend operation, database capability, schema, or generated contract.
- It does not retire `/api/move-response-distribution`; that remains a later `RETIRE-03` slice.
- It does not migrate analysis or preferred-move workflows, add a compatibility fallback, or introduce a new projection.

## Rejected alternatives

- Distinct-game percentages were rejected because overlapping per-move game counts do not form a true pie distribution.
- Excluding terminal games only from a distinct-game denominator was rejected in favor of directly counting outgoing-move occurrences.
- UCI-only or combined SAN/UCI labels were rejected for the primary presentation.
- Showing every move as a separate slice or hiding the long tail was rejected in favor of the existing top-five-plus-Other interaction.
- Expanding the backend to provide per-reply opening names, or repeating the parent position's opening name on every reply, was rejected.
