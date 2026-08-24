# Preferred-Move Storage Decisions — Focused Grilling Synthesis

**Consolidated:** 2026-08-24  
**Status:** Completed focused grilling; historical and directional evidence only  
**Implementation authority:** None  
**Relationship:** This record settles the preferred-move storage questions left open in the [canonical Caro-Kann
historical synthesis](caro-kann-next-move-experiment.md). It is not a schema, implementation specification, runtime
authorization, or product surface.

Writing this record and the linked [focused Plan](../plans/done/preferred-move-storage/preferred-move-storage.md)
does not implement or authorize source, tests, schema, or runtime database changes. Implementation requires separate
approval of each Plan stage; the runtime database stage has its own human approval breakpoint.

## Purpose and evidence

The repository already owns game-derived positions in `position_state`, keyed by the exact four-field state of piece
placement, side to move, castling rights, and legally relevant en-passant state. `players.uuid` is the stable player
identity. The earlier copied/materialized tracked-player projection was abandoned after runtime failures; future work
must query existing facts directly and add only the missing preferred-move capability.

Relevant evidence:

- [Canonical historical synthesis](caro-kann-next-move-experiment.md), especially its identity, manual-authority, and
  open-storage sections.
- [Existing supported SQLite schema](../../data/database/schema.txt), including `players`, `position_state`, and
  `position_occurrence`.
- [Accepted MP-06 corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md) for existing
  game-derived position ownership.
- [Accepted S4 recurrence Plan](../plans/done/s4-authoritative-recurrence/s4-authoritative-recurrence.md) for neutral
  recurrence boundaries.
- [S5 projection retrospective](ABANDONED/s5-tracked-player-projection-retrospective.md) for the failed copied
  projection approach and the direct-query direction.

## Settled storage direction

### Identity and histories

- Store one preferred move per stable player UUID plus the existing exact four-field position. The same position is
  shared across routes and transpositions.
- Keep two narrow append-only histories:
  1. requirement active/inactive; and
  2. preferred move set/remove.
- Requirements and preferences are independent. Their present combination means:
  - active requirement plus preferred move: **satisfied**;
  - active requirement plus no preferred move: **choice needed**; and
  - inactive requirement plus preferred move: **stored, out-of-scope**.
- Derive present and historical state directly from those histories. Do not add current projections, caches, copied
  projections, or a rebuild/publication framework.

### Event facts and time

- Events contain ownership, action, and move as applicable, a user-selected effective time, and a database-recorded
  time. They contain no source or reason fields.
- Backdating and future scheduling are supported.
- The effective timeline can be corrected while the as-known-at-recorded-time history remains available.
- For the same effective time, the later-recorded event wins.
- Re-saving unchanged state is a no-op and creates no redundant history event.
- Exact UTC date and time are supported. Date-range queries return every move and no-move period rather than hiding
  gaps.

### Move representation and validation

- Store the canonical legal UCI move together with a validated SAN snapshot.
- Validate the move from the exact four-field position and reject an illegal move.
- No move may cause insertion of an unobserved position. Initial scope is limited to existing game-derived
  `position_state` rows.

## Derived comparisons

Later game comparison uses the game end time. A game is judged only when both the requirement was active and the
preferred move was present at that game end time. Otherwise it is **not judged**. Backdated events affect older games
according to their effective time, while recorded-time views retain what was known when each event was recorded.

There is no automatic requirement selection, coverage rule, threshold, formula, ranking, or recommendation.

## Line input and acceptance case

Line input may replay and validate a line, then atomically save the decision positions belonging to the player's own
color. There is no line table. The line must use existing game-derived positions and must not partially save on
validation or persistence failure.

The acceptance line is:

> `1.e4 c6 2.d4 d5 3.e5 c5`

It assigns Skyrocoster's Black choices `c6`, `d5`, and `c5`, with active requirements at the three Black-to-move
positions. Every resulting event has effective time exactly `2024-09-03T06:00:00Z`. Repeating the accepted save after
the state is unchanged is a no-op.

## Implementation and runtime boundary

The eventual capability is database storage plus a minimal tested Python access layer only. It has no API, UI, or
training surface and does not expand dependencies or contracts. Storage and database runs remain clear, lean, and
simplistic because the prior copied-projection failures exposed the cost of operational complexity.

When the runtime database is eventually updated:

1. Make a full file copy of `data/database/chess_games.db`.
2. Confirm matching file size only.
3. Apply the small schema and accepted line directly to the runtime database.
4. Read back the accepted result.
5. Restore the copy on failure.

Ordinary tests may use a copied database. This process explicitly does not add hashes, integrity scans, manifests, run
records, or enterprise backup machinery. The runtime operation is a human-approved breakpoint and is not authorized by
this synthesis or the Plan alone.

## Explicit exclusions

- Product source, tests, schema, runtime database, API, UI, and training implementation in this record.
- Current projections, caches, copied/materialized personal projections, rebuilds, publication frameworks, and run
  records.
- Unobserved-position insertion, automatic requirement selection, thresholds, formulas, coverage rules, ranking, or
  engine/population selection of a preferred move.
- Source/reason fields, route-specific preferences, a line table, dependency expansion, and contract expansion.
- Hashes, integrity scans, manifests, enterprise backup machinery, destructive replacement, partial writes, commits,
  pushes, and historical-record edits.

## Safe conclusion

The settled direction is one lean, direct, user-authoritative preferred-move capability over existing exact positions.
Its histories preserve both effective reality and recorded knowledge without materialized projections. The focused Plan
defines later proof in three sequential stages and stops for explicit human approval before modifying the runtime
database.

## Cross-links

- [Focused preferred-move storage Plan](../plans/done/preferred-move-storage/preferred-move-storage.md)
- [Documentation Router](../README.md)
- [Canonical Caro-Kann historical synthesis](caro-kann-next-move-experiment.md)
