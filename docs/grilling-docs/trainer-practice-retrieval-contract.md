# Trainer practice retrieval contract

**Status:** Grilling synthesis, 14 September 2026; amended later the same day with benchmark findings and advice.  
**Purpose:** Record the settled backend interaction needed to retrieve practice material. This is not a frontend design or an implementation Plan.

The settled decisions below are unchanged. The amendment adds measured timings from `docs/benchmarks/API/` and new advice that follows from those numbers. Nothing in the amendment changes the endpoint, the filters, or the response shape.

## Goal

A trainer page must support a direct action such as **Practice Caro**. That action retrieves every position currently requiring training within the chosen opening scope. The same underlying API must also support:

- every position requiring training across all openings;
- filtering by opening;
- filtering by the learner's colour;
- combining opening, learner colour, and training-required filters.

The immediate objective is to prove data retrieval and its response shape so the frontend can later be designed around a stable contract. The frontend interaction itself is deliberately unsettled.

## Settled decisions

### Reuse the existing training-requirements API

The retrieval contract is based on:

```http
GET /api/positions/training-requirements
```

A separate trainer-session endpoint is not currently needed.

### Filters combine

The API supports both a global “train everything requiring training” action and a narrower action such as “train the white Caro-Kann positions requiring training.” Supplied filters intersect rather than replacing one another.

- `training_requirement_lt=0` selects positions whose existing score says training is required.
- `trainer_color=white|black` limits results to the learner's repertoire colour. Omitting it means either colour.
- `opening_key=<exact key>` selects an opening route.
- `opening_match=reached` selects games that reached that opening, even when they later reached a more specific named variation.
- `as_of=<YYYY-MM-DD>` supplies the scoring date.
- `page` and `page_size` retain the existing pagination contract.

“Requires training” keeps its existing scoring meaning. This work does not introduce a new due-date or scheduling model.

### Meaning of “Practice Caro”

The user selected **reached-opening scope**.

“Practice Caro” means every matching position from games that reached the base Caro-Kann opening, including games that continued into deeper named Caro-Kann variations. It does not mean only games whose deepest classification is the base opening.

The runtime action should carry the exact opening key returned by the opening catalogue, rather than sending the display text `Caro` as an approximate search. The intended request is equivalent to:

```http
GET /api/positions/training-requirements
  ?as_of=<today>
  &training_requirement_lt=0
  &opening_key=<exact Caro-Kann base key>
  &opening_match=reached
  &page=1
  &page_size=100
```

`trainer_color=white` or `trainer_color=black` can be added when a colour is selected. Further pages are requested when `total` exceeds the results already loaded.

The openings catalogue remains available for discovering or verifying stable keys:

```http
GET /api/openings?search=Caro&page=1&page_size=100&sort=name_asc
```

Catalogue entries expose `key`, `eco`, `name`, `route_count`, `games_reached`, and `games_deepest`. The catalogue is flat; it does not expose an explicit parent/child opening hierarchy.

## Stable response shape

The training-requirements response envelope contains:

- `as_of`;
- `scoring_policy`;
- `items`;
- `page`;
- `page_size`;
- `total`.

Each item contains the data needed to present and check a board prompt:

- canonical `fen`;
- `trainer_color`;
- `preferred_move_uci`;
- encounter, hit, and miss evidence;
- scoring and training-adjustment values;
- `training_required`;
- `correct_answers_needed`.

Repeated occurrences and transpositions remain aggregated under the existing canonical position and preferred-move identity. Existing ordering and pagination semantics remain unchanged.

## Work and proof completed during this discussion

The existing endpoint already supported training-score and exact-opening filtering. The missing server-side learner-colour filter was added through the existing query model, repository, route, and API contract.

Focused proof covered global training-required retrieval, opening filtering, learner-colour filtering, combined opening-and-colour filtering, invalid colour, and valid empty results:

```text
timeout 60s .venv/Scripts/python.exe -m pytest backend/tests/features/position_training_requirements/test_api.py tests/database/positions/test_training_requirements_discovery.py backend/tests/features/health/test_contract_export.py
```

Result: **37 passed in 5.38 seconds**. No frontend files were changed.

### Caro-Kann proof against the real database (added later 14 September 2026)

The open question from the first session is now closed. `test_real_database_caro_reached_scope_includes_deeper_variation` in `backend/tests/features/position_training_requirements/test_real_database.py` proves the approved **Practice Caro** request against the real database at `data/database/chess.db`:

```http
GET /api/positions/training-requirements
  ?as_of=2026-09-14
  &training_requirement_lt=0
  &opening_key=B10:Caro-Kann%20Defense
  &opening_match=reached
  &page=1
  &page_size=100
```

It returns 200 with the settled envelope, and the representative black position `rnbqkbnr/pp2pppp/8/3p4/8/1B6/PPPP1PPP/RNBQK1NR b KQkq - 0 1` with preferred move `g8f6` appears under `reached` but not under `deepest`. The test also checks the underlying route data directly: games exist that record both the base `B10 / Caro-Kann Defense` route and a deeper `Caro-Kann Defense: ...` route, so `reached` scope behaves as decided. The request is read-only; the test fails if the database bytes change.

### Benchmark proof (added later 14 September 2026)

A permanent benchmark suite now times every API route. Synthetic-database cases live in `backend/tests/benchmarks/test_api_benchmark.py`; opt-in real-database cases live in `backend/tests/benchmarks/test_api_benchmark_real.py`. Reports go to `docs/benchmarks/API/`; the guide is `docs/benchmarks/API/README.md`. Counts and timings only; response bodies are never stored.

```text
timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark.py -q
```

Result: **9 passed in about 7 seconds** (small synthetic database).

```text
timeout 500s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v
```

Result: **6 passed in about 10 minutes** (real 148,500,480-byte database, read-only verified). The games case dominates the time: three repeats near 90 seconds each.

## Benchmark findings (added later 14 September 2026)

Medians from `docs/benchmarks/API/`. Synthetic means a 100 KB database with 3 games; real means `data/database/chess.db` (148,500,480 bytes). Test-process timings, so browser-facing times will be higher.

| Request | Synthetic median | Real median |
| --- | --- | --- |
| `GET /api/health` | 3 ms | not measured (no database work) |
| `GET /api/analysis` (one position) | 52 ms | 50 ms |
| `GET /api/openings` page 1 of 50 | 43 ms | 321 ms (3,329 catalogue entries) |
| `GET /api/preferred-moves` timeline | 43 ms | not measured on real data |
| `GET /api/positions/training-requirements` page 1 | 51 ms | 6,000 ms Caro filter (4 items); 5,671 ms global (8 items, whole load in 1 page) |
| `GET /api/positions/insight` (one position) | 155 ms | 2,170 ms |
| `GET /api/games` page 1 of 50 | 55 ms | 88,522 ms (12,710 games) |

What these numbers establish:

- **Game search is the slowest endpoint by a distance.** Page 1 costs about 90 seconds because `GameSearchRepository.search` in `src/chess_move_trainer/database/games/search_repository.py:86-122` loads all 12,710 games and related rows into Python before returning 50 summaries. At 50 per page, a full traversal would be 255 pages.
- **Training pages cost about 6 seconds regardless of result size.** The Caro page holds 4 items and the global load holds 8 items, yet both cost 5.7–6.0 seconds. Each page repeats the full-corpus scan and Python scoring in `training_requirements_repository.py:93-199`, so per-page cost is uniform. The whole train-everything result on current data is 8 items in 1 page: about 5.7 seconds per Practice click, sequential.
- **Insight costs 2.2 seconds on real data and the frontend doubles it.** One request opens the database three times (`insight_repository.py:74,94,95`) and loads all opening routes into Python. `positionContextApi.ts` and `moveResponseDistributionApi.ts` each send this request per board position, so one position change costs about 4.4 seconds on current data; 20 position changes cost about 88 seconds.
- **The openings catalogue is cheap per page but large.** 321 ms per page with 3,329 entries means 67 pages. The trainer frontend loads them all on mount with 4 at a time (`trainerPracticeApi.ts:135-173`), which is roughly 5.5 seconds per full catalogue load.
- **Analysis is flat at 50 ms on both databases.** Single-position indexed read; the 1-second polling loop in `analysisState.ts` is not a concern.
- **Every database endpoint pays a ~45 ms floor on tiny data.** All synthetic database reads land at 43–55 ms while health answers in 3 ms. That floor is the per-request connection open, `PRAGMA` setup, schema check, and close from `connection.py:66-85`.

## New advice (added later 14 September 2026)

This advice follows from the numbers above. It changes no settled decision.

1. **Narrow the games query before anything else.** 90 seconds per page cannot be fixed with a cache: 255 pages of 50 would need caching of the entire corpus, and the first load after any write or restart still takes 90 seconds. Push filtering, sorting, and paging into SQL so page 1 reads closer to 50 rows.
2. **Narrow the training scan second.** 6 seconds per page for 4–8 items is the same full-scan pattern at smaller scale. The entire current train-everything result is 8 items, so once the scan is narrowed, caching the whole filtered result per address becomes cheap and effective.
3. **Give insight one database connection per request and share the frontend request.** Reusing a single connection removes two of the three per-request opens, and one shared TanStack Query key for `positionContextApi.ts` and `moveResponseDistributionApi.ts` halves the 4.4-seconds-per-move cost. Then apply the short 30–60 second backend cache from `api-caching-review.md`.
4. **Cache the openings catalogue with a long lifetime.** Catalogue rows change only on re-import, so 10–30 minutes in backend memory turns the 5.5-second full catalogue load into an instant repeat load. Clear it when the database file is replaced (see question 21 in `api-caching-review.md`).
5. **Leave analysis and health alone.** 50 ms and 3 ms need no work; keep analysis polling uncached or at 1–2 seconds so queued results are never hidden.

Suggested next measurement after any fix above: rerun the two benchmark commands and compare `median_ms` for `real-games-list`, `real-global-training-load`, and `real-position-insight` against 88,522 ms, 5,671 ms, and 2,170 ms.

## Remaining open questions

The generic `opening_match=reached` contract and the representative Caro-Kann example are both proven (see above). The following remain outside this decision:

- how opening and colour choices look or behave in the frontend;
- session length, randomization, ordering, or persistent session snapshots;
- whether opening and line context should be embedded in every collection item or retrieved from `/api/positions/insight` for the active position;
- explicit opening-family hierarchy or arbitrary multi-opening collections;
- changes to scoring or scheduling semantics.
