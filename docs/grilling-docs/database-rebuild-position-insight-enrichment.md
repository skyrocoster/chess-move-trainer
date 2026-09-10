# Database rebuild position-insight enrichment

> **Status:** direction settled
> **Purpose:** unblock `CONSUMER-03` while preserving additive position-insight evolution.

## Decision

Enrich the existing `GET /api/positions/insight` response rather than add another endpoint, use a fallback, or make
the frontend reconstruct missing aggregation meanings. The endpoint returns authoritative integer counts and explicit
denominators. It does not return pre-rounded percentages or presentation strings.

All enrichment calculations belong to the rebuilt package under `src/chess_move_trainer/database/` and read only the
rebuilt `data/database/chess.db`. They do not invoke or read through legacy refresh scripts, recurrence projections,
legacy repositories, or `data/database/chess_games.db`. The thin FastAPI feature only maps package values into the
clean HTTP response. Existing `scripts/api/` contract-export, client-generation, and finite-command helpers remain
current API tooling rather than legacy chess-data calculation paths.

The existing response fields and meanings remain intact. The enrichment adds enough information to reproduce current
Position Reach Frequency behavior and to make outgoing-move denominators and terminal occurrences explicit:

```json
{
  "fen": "<canonical FEN>",
  "trainer_color": "white",
  "as_of": "2026-09-10",
  "observed_in_games": true,
  "experience": {
    "distinct_game_count": 7,
    "occurrence_count": 8,
    "total_game_count": 10
  },
  "observed_move_totals": {
    "distinct_game_count": 7,
    "occurrence_count": 7,
    "terminal": {
      "distinct_game_count": 1,
      "occurrence_count": 1
    }
  },
  "observed_moves": [
    {
      "move_uci": "e2e4",
      "distinct_game_count": 5,
      "occurrence_count": 5
    }
  ],
  "opening": {},
  "analysis": {},
  "preference": {}
}
```

Exact field spelling may be finalized during focused planning without changing these semantics.

## Meanings

- `experience.distinct_game_count` remains the number of distinct games for the requested trainer color that reached
  the position.
- `experience.occurrence_count` remains the number of occurrences of the position in those games.
- `experience.total_game_count` is the complete game denominator for the requested trainer color. Position Reach
  Frequency can therefore render `distinct_game_count / total_game_count`.
- `observed_in_games` states whether the position occurred in any imported game, regardless of requested trainer
  color. It distinguishes game-corpus absence from a zero count in the selected trainer population without exposing
  internal row existence.
- `observed_move_totals.distinct_game_count` is the distinct-game denominator for occurrences having an outgoing
  move.
- `observed_move_totals.occurrence_count` is the complete outgoing-decision denominator. Repeated occurrences count
  as repeated decisions.
- `observed_move_totals.terminal` reports game-ending occurrences separately so they do not dilute outgoing-move
  percentages.
- Each observed move retains its distinct-game and occurrence numerators. The frontend may choose the approved
  numerator/denominator pair for its specific label but does not redefine their meanings.
- The request continues to require one `trainer_color`; the response does not add an unnecessary second-color
  dataset.

## Presentation boundary

The frontend calculates and formats display percentages from the authoritative counts, for example `7 / 10` as
`70%`. It derives SAN from the canonical parent FEN and outgoing UCI through the existing chess library. The API does
not add percentage, rounded-label, SAN, or screen-specific fields.

## Additive evolution

Future generally reusable position statistics may be added as new fields or cohesive peer objects without changing
the existing fields or requiring existing consumers to adopt them. Each addition still updates its backend
calculation and HTTP schema, the curated OpenAPI export, and the checked-in generated client.

Additive evolution does not mean every possible statistic automatically belongs in this operation. Escalate when a
candidate statistic changes an existing denominator or filter meaning, requires new stored data or schema, is
expensive or unbounded for every insight request, is specific to one screen, or belongs to a separate domain or
workflow. The operation retains no `include` variants.

## Planning consequence

`CONSUMER-03` cannot preserve current Position Reach Frequency and Preferred Move saveability meanings against the
previous clean response because its trainer-color all-games denominator and corpus-observation distinction were
absent. A focused clean-contract enrichment must therefore precede frontend `CONSUMER-03` adoption. That prerequisite
does not authorize application integration, later consumer migration, a compatibility read, or legacy-route
retirement.
