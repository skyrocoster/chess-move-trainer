# Backend statistics suite — 2026-09-20

## Request and authorization

The user requested a broad suite of new statistics, gave free rein over which useful measurements to add, asked
that the work remain backend-only, and explicitly authorized implementation. No frontend wiring is in scope.

This document is a live record of the repository facts, design choices, implementation progress, proof, and any
limits discovered during the work. It is not a separate implementation Plan.

## Starting decisions

- Extend the existing statistics capability rather than create a parallel reporting system.
- Derive statistics from data the application already owns; do not invent or persist synthetic measurements.
- Keep existing API behavior compatible, including the current next-move distribution.
- Return stable, documented shapes for empty and partially analysed data.
- Cover the new calculations and API contract with focused backend tests.
- Do not change frontend code.

## Progress log

- **Started:** recorded the request, boundaries, and initial compatibility/testing decisions before inspecting the
  statistics implementation.
- **Worktree safety:** unrelated pre-existing changes under `frontend/.storybook/` and `tests/e2e/` were found and
  will be preserved.
- **Mapped the current behavior:** the existing “next move distribution” is derived by the frontend from
  `GET /api/positions/insight`; it is not a dedicated statistics endpoint. The backend also has lower-level
  occurrence readers in `src/chess_move_trainer/database/statistics.py`.
- **Selected the extension:** keep the position-insight contract compatible and add a separate cached
  `GET /api/statistics/overview` endpoint. This avoids making every board-position request calculate corpus-wide
  reports and gives future frontend work one stable backend contract.
- **Selected deterministic inputs:** the new endpoint will require `as_of` for date-sensitive repertoire figures
  and accept optional game-date, trainer-color, and time-class filters. It will not silently depend on the server's
  clock.
- **Implementation started:** the suite is being split into package-owned reporting models/readers and a thin
  FastAPI translation layer, following the existing games and position-insight boundaries.
- **API checkpoint:** `GET /api/statistics/overview` is registered with a strict response contract, validated
  filters, safe 422/500/503 errors, database-signature-aware caching, and no frontend changes. The first focused
  API/contract run passed 16 tests.
- **Core checkpoint:** reporting now reads games, occurrences, openings, opponents, analyses, queue state,
  date-resolved preferences, and training balances through a read-only schema-checked repository.
- **Expansion checkpoint:** game-duration and rating progression, rating-gap and game-length bands, hourly activity,
  opening and opponent averages, analysis line types/multi-PV counts, missing training balances, and timestamp/data
  quality checks were added after the first API checkpoint.
- **Core proof checkpoint:** focused real-SQLite tests now cover every data family, cross-section filtering,
  date-sensitive preferences, analysis coverage, adherence, timestamp quality, and rejection of overlapping active
  preference periods.

## Repository findings

- Game facts already include trainer color, outcome, termination reason, time class/control, both ratings, opponent
  identity, and start/end timestamps.
- Normalized game occurrences include ply, position, outgoing move, and terminal occurrences. They can determine
  game length, recurring positions, move actor, and preferred-move adherence without parsing PGN again.
- Existing analysis results and queue rows support coverage, quality, terminal-analysis, depth, queued, and running
  statistics.
- Date-ranged move preferences and training aggregates support current repertoire coverage, observed adherence, and
  training-balance summaries when an explicit `as_of` date is supplied.
- Opening routes can classify each game by its deepest reached opening using the same deterministic rule as the
  games feature: greatest reached ply, then opening key as a tie-breaker.
- Reads must use the package's read-only SQLite connection and exact schema check. Successful payloads can use the
  existing database-signature-aware response cache.

## Implemented HTTP contract

`GET /api/statistics/overview` has operation ID `getStatisticsOverview`.

Required query:

- `as_of=YYYY-MM-DD` resolves the move-preference schedule without relying on the server clock.

Optional filters:

- `started_on_or_after=YYYY-MM-DD` and `started_on_or_before=YYYY-MM-DD` are inclusive;
- `trainer_color=white|black`;
- `time_class=bullet|blitz|rapid|daily`.

Every section uses the selected games and their occurrences. The only deliberately wider value is
`positions.database_position_count`, which reports all canonical positions held by the database. A game with no
valid start timestamp remains in an unfiltered report but cannot match a start-date filter.

Invalid filters return 422 with `invalid_filter`. A missing or incompatible database returns 503 with
`statistics_unavailable`. Unexpected failures return a detail-free 500 with `unexpected_failure`.

Successful serialized responses use the existing five-minute process-local read cache. The key includes every
validated filter, and any database or SQLite sidecar signature change invalidates cached responses.

## Implemented statistics catalogue

### Games

- Overall total, known/unknown outcomes, win/loss/draw counts, and score rate.
- The same outcome record split by trainer color, time class, time control, normalized termination reason, rating
  difference band, and game-length band.
- Count/minimum/maximum/average/median summaries for trainer rating, opponent rating, rating difference, game length
  in plies, and valid nonnegative game duration in seconds.
- Dated trainer-rating progression: first, last, change, peak, low, and sample count.

Score rate is `(wins + 0.5 * draws) / known outcomes`. It is `null`, not zero, when no known outcome exists.

### Activity and form

- First and last valid game timestamps and the dated-game count.
- Monthly records with average trainer rating.
- Complete seven-day UTC weekday and 24-hour UTC distributions, including zero-count slots.
- Last 10, 25, and 50 dated-game records.
- Current win/loss/draw streak plus longest win, loss, draw, unbeaten, and winless streaks. Unknown outcomes remain
  visible in recent-window totals but are skipped for streak calculation.

### Openings and opponents

- Deepest reached opening per game, using greatest ply then opening key for deterministic ties.
- Classified/unclassified totals, distinct opening count, and the top 25 openings by game count.
- Per-opening outcome record, deepest reached ply, average trainer rating, and average game length.
- Known/unknown opponent-game totals, distinct and repeat-opponent counts, and the top 20 opponents by game count.
- Per-opponent outcome record, average opponent rating, and average trainer-minus-opponent rating difference.

### Positions

- Database and selected-scope position totals, game and occurrence counts, outgoing and terminal occurrence counts,
  trainer-turn and opponent-turn counts, distinct outgoing moves, repeated positions, and average occurrences per
  observed position.
- Fixed ply buckets `0-19`, `20-39`, `40-59`, and `60+`, each with occurrence, game, and position counts.
- The top 20 recurring canonical FENs with game, occurrence, outgoing, and terminal counts. Internal SQLite IDs are
  never returned.

### Analysis

- Selected positions with ready results, browser/tool quality, terminal results, queued/running work, and no request.
- Ready-result coverage rate, total candidate lines, centipawn/mate line counts, multi-PV result count, and average
  line depth.

Queue and ready-result counts are factual and may overlap because this database can retain a result while a newer
analysis request is queued or running.

### Repertoire and training

- Selected positions where it was the trainer's turn, split into active move preference, explicit no preference,
  and unconfigured as of the requested date.
- Preference coverage, positions where the currently preferred move was observed, eligible outgoing trainer moves,
  matching preferred moves, and adherence rate.
- Training-balance count, negative/zero/positive and updated counts, missing balance count, and numeric summary for
  balances matching the currently active preferred move.

Terminal occurrences do not count as adherence opportunities because no outgoing move was played. Overlapping
active preference periods are rejected as malformed storage rather than silently double-counted.

### Data quality

- Missing outcome, ratings, start/end timestamps, time class/control, termination reason, and opponent counts.
- Invalid start/end timestamp counts and end-before-start duration counts.

All rates are fractions from 0 through 1. Rates and numeric summaries use `null` when no denominator/sample exists,
so an empty database has a stable and unambiguous response rather than fabricated zero averages.

## Code ownership

- `src/chess_move_trainer/database/reporting/` owns validated inputs, public report values, read-only SQL, calculations,
  deterministic ranking, and storage/schema error translation.
- `backend/app/features/statistics/` owns the strict HTTP response models and explicit report-to-HTTP translation.
- `backend/app/caching.py` owns the complete statistics cache key.
- `backend/app/main.py` registers the router.
- `tests/database/reporting/` proves core calculations against a real temporary schema.
- `backend/tests/features/statistics/` proves API behavior, filters, empty data, failures, and caching.
- `backend/tests/features/health/test_contract_export.py` pins the new route and operation ID.

No schema migration, persisted aggregate, background job, or frontend file is part of this change.

## Verification

Final focused command:

```text
timeout 180s .venv/Scripts/python.exe -m pytest tests/database/reporting tests/database/test_statistics.py backend/tests/features/statistics backend/tests/features/position_insight backend/tests/features/api_cache/test_read_cache.py backend/tests/features/health/test_contract_export.py -q
```

Result: **47 passed in 3.82 seconds**.

This proves the new core and API suite, preserves the existing direct next-move statistics and position-insight
behavior, exercises the shared response-cache read path, and confirms the complete served OpenAPI path set.

The earlier narrow API/contract checkpoint passed 16 tests, and the final core-only checkpoint passed 9 tests.
No frontend, browser, generated frontend client, live database, or broad repository-hygiene check was needed for the
backend-only outcome.
