# API benchmarks

This folder holds timing data for the HTTP routes in `backend/app/main.py`.
The tests that produce the data live next to the other backend tests in
`backend/tests/benchmarks/test_api_benchmark.py` (synthetic databases) and
`backend/tests/benchmarks/test_api_benchmark_real.py` (real database).

Related review: `docs/grilling-docs/api-caching-review.md`.

## How to run

From the repository root.

Git Bash, synthetic databases only (fast, always works):

```bash
timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v
```

Git Bash, including the real 142 MB database at `data/database/chess.db`
(read-only check included; each test fails if the file changes):

```bash
timeout 500s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v
```

PowerShell, synthetic only:

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v
```

PowerShell, including the real database:

```powershell
$env:CHESS_RUN_API_BENCHMARK_REAL = "1"
.venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v
Remove-Item Env:CHESS_RUN_API_BENCHMARK_REAL
```

Each run writes timestamped JSON files here, for example
`20260914T120000Z-training-requirements-page.json`. A passing synthetic run
writes 11 files (one per endpoint plus two scenario loads); a passing real
run writes 6 files.

## What is measured

Single-request cases (default 5 repeats each, median must pass):

- `health` — `GET /api/health`, cheap baseline with no database read.
- `openings-list` and `openings-detail` — `GET /api/openings` page 1, then
  the first catalogue entry by key.
- `games-list` and `games-detail` — `GET /api/games` page 1, then the first
  game by UUID.
- `training-requirements-page` — page 1 of scored training items. This is
  the endpoint the caching review flags as most expensive.
- `position-insight` — one `GET /api/positions/insight` read.
- `preferred-moves-timeline` — one `GET /api/preferred-moves` read.
- `analysis-observation` — one `GET /api/analysis` read.

Scenario cases (mirror how the frontend actually calls the backend):

- `trainer-practice-full-load` — reads training-requirements pages 1..N
  until `total` is reached, the same loop as
  `frontend/src/features/trainer-practice/trainerPracticeApi.ts`.
- `board-navigation-10-insights` — 10 alternating insight reads, the same
  shape as stepping through board positions.

Real-database cases (`test_api_benchmark_real.py`, opt-in only, default 3
repeats each):

- `real-practice-caro-page1` — the settled Practice Caro request from the
  grilling record: `as_of=2026-09-14`, `training_requirement_lt=0`,
  `opening_key=B10:Caro-Kann Defense`, `opening_match=reached`,
  `page=1`, `page_size=100`.
- `real-global-training-load` — the train-everything load with no opening
  filter, read page by page with per-page timings. Page 1 reveals `total`;
  loads of 12 pages or fewer are read in full, larger loads read the first
  3 pages and record a median-based extrapolation marked `partial: true`.
- `real-position-insight` — one insight read for a known real position
  (Alekhine, white, `as_of=2026-09-14`).
- `real-games-list` — games page 1 against the real game corpus. This
  case proves COLD latency: the server cache is cleared between repeats
  (identical normalized request), and the report carries the warm repeats
  separately as `warm_samples_ms` / `warm_stats`. The games search answers
  from SQL aggregation; the backend cache (TTL 60 s, 64 entries) only
  accelerates repeats of an identical request.
- `real-openings-list` — openings page 1 against the real catalogue.
- `real-analysis-observation` — one analysis read for the same Alekhine
  position.

## Settings you can change

| Variable | Default | Meaning |
| --- | --- | --- |
| `CHESS_API_BENCH_REPEATS` | `5` | Repeats per single-request case. |
| `CHESS_API_BENCH_TIMEOUT_S` | `30` | Per-request timeout in seconds. |
| `CHESS_API_BENCH_OUTPUT` | `docs/benchmarks/API` | Where JSON reports are written. |
| `CHESS_API_BENCH_MAX_MS` | `2000` | Median limit for synthetic requests and scenario totals. |
| `CHESS_RUN_API_BENCHMARK_REAL` | unset | Set to `1` to enable the real-database tests. |
| `CHESS_API_BENCH_REAL_REPEATS` | `3` | Repeats per real single-request case. |
| `CHESS_API_BENCH_REAL_TIMEOUT_S` | `60` | Per-request timeout for real cases in seconds. |
| `CHESS_API_BENCH_MAX_MS_REAL` | `60000` | Median limit for real single requests. |
| `CHESS_API_BENCH_MAX_MS_REAL_GAMES` | `1500` | Cold median limit for the real games list (cache cleared between repeats). |
| `CHESS_API_BENCH_MAX_MS_REAL_LOAD` | `600000` | Limit for the global load total. |

## Reading a report

Each JSON file contains:

- `endpoint` and `params` — the exact request, so the number can be
  reproduced. `fen` values are board positions, not personal data.
- `database` — `kind` (`synthetic` or `real`), file name, and size in bytes.
- `repeats`, `samples_ms`, and `stats` (`count`, `min_ms`, `median_ms`,
  `mean_ms`, `max_ms`).
- `threshold_median_ms` — the limit that applied to this run.
- `total_reported` / `items_returned` — result size, so timing can be read
  next to data volume.
- Cached cases (`games-list`, `openings-list`, `openings-detail`,
  `training-requirements-page` and their `real-` counterparts) set
  `cache_cleared_between_samples: true`, so `samples_ms` / `stats` are cold
  timings, and add `warm_samples_ms` / `warm_stats` from identical repeats
  served from the backend cache.
- Scenario files also include `full_load_total_ms` and either `pages_read`
  or the move count, plus `warm_page1_ms` (one cached page-1 re-read) after
  a cache-cleared load.

Compare runs by `median_ms` for single requests and by
`full_load_total_ms` for the two scenarios. Keep the database file and the
`params` identical when comparing before and after a caching change.
Response bodies are never stored here, only counts and timings.
