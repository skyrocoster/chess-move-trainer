# SETUP-01 preferred-move inference

> **Status:** approved grilling handoff
> **Approved:** 2026-09-08
> **Purpose:** Directional evidence for simple automatic initialization of preferred-move periods from rebuilt game data.

## Operating direction

SETUP-01 should not become a proposal-management workflow. Design the deterministic inference, validate its complete
result, and persist that result. There is no human review pause, retained proposal, separate apply step, interactive
confirmation, or recovery ceremony.

The operation is explicitly requested through:

```text
python -m chess_move_trainer.database preferred-moves setup
```

It always targets `data/database/chess.db`, has no alternate database-path option, and uses only game data already in
that database. It does not fetch or update games, run Stockfish, use a legacy tool, or change application/API behavior.

## Eligible observations

- Examine positions from only the first 30 plies of each game: `derived_game_position.dgp_ply` 0 through 29.
- Count only occurrences where the outgoing move is the trainer's move.
- Pool all accepted games regardless of time class, rating, or result.
- Use the game's UTC start date as the calendar date. A game without that date is skipped and included in the command's
  skipped count; no fallback or guessed date is used.
- Count every eligible occurrence separately. Multiple occurrences in one game or on the same UTC date are not
  collapsed or reweighted.

## Qualification

For each exact canonical position, evaluate rolling half-open 90-calendar-day windows beginning on every distinct date
when that position was played. All eligible trainer-move occurrences for the position inside the window form the
denominator.

A move qualifies in a window only when both are true:

- the trainer played that move at least 21 times; and
- that move accounts for at least 80 percent of eligible plays in the window.

The thresholds are inclusive. Fixed calendar buckets, game-metadata subgroups, and special same-day rules are absent.

## Period construction

- A qualifying preference starts on the first date the qualifying move was played within its qualifying evidence
  window. It is not delayed until the 21st matching play.
- Once established, the move remains preferred through dates without qualifying evidence. Unsupported gaps are not
  emitted as unconfigured gaps.
- A later different move replaces the active move only after satisfying the same 21-play, 80-percent, and 90-day
  qualification rules.
- When qualifying evidence for different moves overlaps, count their actual uses within the overlapping evidence
  dates. The move with the larger raw count wins that overlap. An exact tie preserves the already-active move; if no
  move is active yet, a tie leaves the position unconfigured.
- Repeated qualifying evidence for the active move does not create another period.
- The final inferred move for a position is open-ended. It does not need to reach the database's latest game date.
- Dates before the first qualifying preference remain unconfigured. Inference never creates an explicit
  `no_preference` period: varied or insufficient play is not treated as evidence of user intent.

The resulting schedule for each inferred position is therefore a sequence of contiguous preferred-move periods from
its first accepted signal onward, with the last period indefinite.

## Persistence and command behavior

- The complete `datasource_preferred_move_period` schedule must be empty before setup begins. Any existing row causes a
  clear nonzero failure before mutation.
- Infer and validate the complete normalized schedule before writing. Apply all resulting periods in one transaction;
  any validation or persistence failure applies none of them.
- Invoking the command is the authorization to write. There is no prompt or `--yes` flag.
- A successful run prints only a concise human-readable summary covering examined games, qualifying positions, periods
  applied, skipped observations, and conflicts.
- Finding no qualifying move is a successful zero-change result and leaves the schedule empty so setup can be retried
  after more games exist.
- JSON may be used transiently inside the implementation if useful, but it is not a public proposal, review surface,
  output mode, or retained artifact.

## Boundaries and next gate

SETUP-01 adds no schema, inference history, audit table, application integration, update side effect, or old-database
behavior. It changes only the currently empty preferred-move schedule through the explicit package command above.

This record supersedes the earlier master-plan expectation of a reviewable JSON proposal followed by a separate apply
command. It is approved directional evidence, not implementation authorization. The next step is bounded assessment
and, if warranted, one focused SETUP-01 Plan before implementation.
