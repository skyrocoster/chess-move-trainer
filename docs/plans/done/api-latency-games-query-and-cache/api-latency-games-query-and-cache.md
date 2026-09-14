# API latency: games query optimization and selective caching - cold games list under 1.5 seconds and safe repeat reads

> **Status:** done 2026-09-14 - all five stages complete; cold games list 991.77 ms against the 1.5 s target with exact parity, repeat reads served from backend cache, tripwire tightened to 1,500 ms.

- **Read trigger:** Read before changing games search data access, adding backend response caching, adjusting games/training/openings benchmark tripwires, or archiving this Plan.
- **Upstream:**
  - `docs/grilling-docs/api-performance-and-caching-direction.md` — governing approved direction (2026-09-14). Authority: outcome, acceptance target, cache scope, freshness rules, exclusions.
  - `docs/grilling-docs/api-caching-review.md` — cache boundary opinions (full request address as key, 200-only responses, clear-on-write, in-process memory, database-file metadata guard). Authority: implementation guidance; partially superseded on ordering (games optimization is first, per the direction record) and on cache headers (approved decision: none).
  - `docs/grilling-docs/trainer-practice-retrieval-contract.md` — settled `GET /api/positions/training-requirements` contract. Read trigger: any change touching that endpoint's caching, keys, or invalidation.
  - `docs/benchmarks/API/README.md` and the reports in `docs/benchmarks/API/` — benchmark conventions and measured baselines, including `20260914T130514Z-real-games-list.json` (median 88,522.39 ms, 50 of 12,710, `data/database/chess.db`, 148,500,480 bytes).

## Outcome

A cold `GET /api/games` request against the real 12,710-game database returns its page in at most 1.5 seconds instead of the measured 88.5 seconds, because the search reads per-game aggregates in SQL instead of deserializing and chess-validating every stored occurrence in Python. All existing filters, totals, ordering, response fields, statuses, and edge cases stay exactly as they are. In addition, repeated identical `GET /api/positions/training-requirements` and `GET /api/openings` requests are served from small backend-memory caches. Relevant successful writes invalidate cached training data immediately, while detectable selected-database changes invalidate affected cached reads before the next hit. Games-list caching is added only if the post-optimization measurement shows caching still has real value.

## Scope

- **Included:**
  - Rewriting `GameSearchRepository.search` (`src/chess_move_trainer/database/games/search_repository.py`) so per-game aggregates (occurrence count, length plies, distinct/analyzed/preferred position counts, deepest opening) are computed by SQL aggregation, with filters, ordering, totals, pagination, and error classes preserved.
  - Boundary tests that encode current semantics before the rewrite and must still pass after it (`tests/database/games/test_search.py`).
  - A real-database full-result parity comparison between the previous and new implementations for two fixed representative queries, recorded as totals, ordered UUIDs, and canonical-result hashes rather than copied response bodies.
  - Synthetic and real benchmark runs proving the cold games-list median; tightening the games benchmark tripwire default afterwards.
  - Separate process-local, thread-safe `cachetools.TTLCache` namespaces and wiring for `GET /api/positions/training-requirements` (TTL 60 s, maximum 128 entries), `GET /api/openings` and `GET /api/openings/{opening_key}` (TTL 900 s, maximum 128 entries), and conditionally `GET /api/games` (TTL 60 s, maximum 64 entries, per the Stage 3 measurement gate). The bounds fit the current single-process deployment while preventing query variation from causing unbounded memory growth.
  - Canonical cache keys built after existing request validation/defaulting from HTTP method, route identity, every normalized response-affecting parameter, resolved database path, and (for training) resolved policy values; query-string ordering does not create a different semantic key. Only immutable serialized payloads from `200` responses are cached. Before a hit and again before publishing a completed miss, the selected SQLite main file and relevant `-wal`, `-shm`, and journal sidecars are checked using existence, resolved path, size, nanosecond modification time, and available file identity; a signature change advances the cache generation, clears entries, and forces a miss.
  - Whole-cache invalidation after each successful `POST /api/positions/training-requirements/answers`, `PUT /api/preferred-moves`, and `DELETE /api/preferred-moves`, plus on any database-file signature change.
  - New focused cache tests under `backend/tests/features/api_cache/`.
- **Expected areas:**
  - `src/chess_move_trainer/database/games/search_repository.py` (small helpers under `src/chess_move_trainer/database/games/` allowed)
  - `tests/database/games/test_search.py`
  - `backend/app/caching.py` (new)
  - `backend/app/features/position_training_requirements/router.py`
  - `backend/app/features/openings/router.py`
  - `backend/app/features/preferred_moves/router.py` (invalidation hooks only)
  - `backend/tests/features/api_cache/` (new)
  - `backend/tests/benchmarks/test_api_benchmark.py` and `backend/tests/benchmarks/test_api_benchmark_real.py` (directly relevant cold/warm scenarios and games tripwire only)
  - `docs/benchmarks/API/README.md` (tripwire row and notes only) and generated report JSON files under `docs/benchmarks/API/`
  - `backend/tests/features/games/test_api.py`, `backend/tests/features/position_training_requirements/test_api.py`, `backend/tests/features/openings/test_catalogue_api.py`, `backend/tests/features/preferred_moves/test_put_api.py`, `backend/tests/features/preferred_moves/test_delete_api.py` as proof targets; edit them only if a stage's behavior change requires it
- **Excluded:** Any database schema change, migration, or new index (escalation required first); training-requirements repository rewrite; caching of position insight, analysis observation, preferred-move timeline, health, writes, or error responses; `Cache-Control` or other browser caching headers; response-contract changes; frontend changes; Redis or any shared/disk/multi-worker cache; dependency additions (`cachetools==5.5.2` is already pinned in `requirements.txt`); lint/formatting/type/size/aggregate hygiene checks; commit, push, stash, branch, or worktree operations; unrelated worktree changes.

## Stages

1. **pending - Encode games-search semantics boundaries and record the pre-change evidence.**
   - **Ordered actions:**
     1. Extend `tests/database/games/test_search.py` with boundary tests that pass against the CURRENT implementation before anything changes: (a) timestamp bounds with fractional seconds and exact-bound equality (a game exactly at `started_at_to` stays matched, per `_stored_timestamp` normalization in `search_validation.py:136-139`); (b) deepest-opening tie-break — two opening labels reaching the same maximum ply select the lexicographically smaller `ECO:Name` key; (c) a zero-occurrence game summarizes as `occurrence_count 0`, `length_plies 0`, coverage `"none"`/`"none"`; (d) `started_at_desc` ordering places a game with no `started_at_utc` before dated games (NULLs first, per `_compare_nullable`); (e) pagination determinism across repeated identical searches.
     2. Record the real-database baseline for two fixed queries against `data/database/chess.db`: default page 1, and `opening_key=B10:Caro-Kann Defense` with `opening_match=reached` and `sort=length_asc`. For each result, record `total`, `total_pages`, ordered page UUIDs, and a SHA-256 hash of the complete canonical `GameSearchPage`; record the database main/sidecar signature too. Do not copy response bodies into the Plan.
   - **Focused proof:**
     ```text
     timeout 120s .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py -q
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.

     ```text
      timeout 300s .venv/Scripts/python.exe - <<'PY'
      import dataclasses
      import hashlib
      import json
      from pathlib import Path
      from chess_move_trainer.database.games import GameSearchQuery, GameSearchRepository
      DB = "data/database/chess.db"
      cases = {
          "default": GameSearchQuery(),
          "caro_reached_length_asc": GameSearchQuery(
              opening_key="B10:Caro-Kann Defense", opening_match="reached", sort="length_asc"
          ),
      }
      main = Path(DB).resolve()
      out = {"database_signature": {}}
      for path in (main, *(Path(str(main) + suffix) for suffix in ("-wal", "-shm", "-journal"))):
          if not path.exists():
              out["database_signature"][str(path)] = None
              continue
          stat = path.stat()
          out["database_signature"][str(path)] = {
              "size": stat.st_size,
              "mtime_ns": stat.st_mtime_ns,
              "device": getattr(stat, "st_dev", None),
              "inode": getattr(stat, "st_ino", None),
          }
      for name, query in cases.items():
          result = GameSearchRepository(DB).search(query)
          raw = json.dumps(dataclasses.asdict(result), sort_keys=True, separators=(",", ":"), default=str)
          out[name] = {
              "total": result.total,
              "total_pages": result.total_pages,
              "game_uuids": [item.game_uuid for item in result.items],
              "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
          }
      print(json.dumps(out, indent=2))
      PY
      ```
      Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `360000` ms. Record the printed metadata in Progress and decisions together with the database signature.
   - **Escalation boundary:** Stop before proceeding if any new boundary test fails against the current implementation — that means the encoded semantics are wrong, not the implementation.
   - **Breakpoint:** None expected.

2. **pending - Rewrite the games search to SQL aggregation with parity proof.**
   - **Ordered actions:**
     1. Rewrite `GameSearchRepository.search`: one grouped SQL pass over `datasource_game LEFT JOIN derived_game_position` computing `occurrence_count` (`COUNT`), `length_plies` (`COALESCE(MAX(dgp_ply), 0)`), `distinct_position_count` (`COUNT(DISTINCT derived_position_id)`), `analyzed_position_count` and `preferred_position_count` (`COUNT(DISTINCT CASE WHEN EXISTS ... END)` against `derived_analysis_result` and `datasource_preferred_move_period`); push only provably safe scalar filters into SQL `WHERE` (trainer color/outcome, rating bounds, opponent UUID, time class/control); evaluate `contains_fen`/`move_fen` as SQL `EXISTS` matching the four stored canonical components (`dp_placement`, `dp_side_to_move`, `dp_castling_rights`, `dp_legal_en_passant`, plus `dgp_move_uci` for the move filter) — equivalent to the current canonical-position identity because `_stored_position` (`search_validation.py:64-74`) guarantees stored components are canonical; evaluate opening `reached` as SQL `EXISTS` on `do_eco`/`do_name` parsed from the `ECO:Name` key; compute per-(game, key) maximum ply as a small grouped result and keep the deepest-opening selection and tie-break in Python (current rule: max ply, ties by smallest key); keep timestamp bounds and `termination_reason` filtering in Python over the compact aggregate rows, reusing the existing helpers, unless measurements later demand SQL push-down with exact `_stored_timestamp` parity.
     2. Preserve by construction: `total`/`total_pages`/`has_next` from the fully filtered set, the twelve sort orders with NULL placement and `game_uuid` ascending tie-break, page slicing, error classes (`GameSearchValidationError`, `GameSearchSchemaError`, `GameSearchStorageError`), read-only mode, and the exact schema-v2 assertion.
     3. Confirm the database main/sidecar signature still matches Stage 1, then rerun the same two-query canonical-hash snippet. Totals, total pages, ordered page UUIDs, and complete-result hashes must match the Stage 1 values exactly. If the database changed, stop and re-establish a valid pre-change baseline rather than comparing different data.
   - **Focused proof:**
     ```text
     timeout 120s .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py backend/tests/features/games/test_api.py -q
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.
    - **Escalation boundary:** Stop if the parity comparison shows any total, page count, ordering, or canonical-result hash difference, or if any existing or new test fails. Do not adjust tests to match new behavior — that would be semantic drift.
   - **Breakpoint:** None expected.

3. **pending - Prove the cold games latency target and set the caching gate.**
   - **Ordered actions:**
     1. Run the synthetic benchmark suite.
     2. Run the opt-in real-database benchmark suite.
     3. Compare against the baselines: real games list was median 88,522.39 ms with `total_reported` 12,710; synthetic games-list median must remain within its existing 2,000 ms limit.
     4. Record the gate decision for Stage 5: cache `GET /api/games` only if the measured real median exceeds 1,000 ms; otherwise record the skip decision.
   - **Focused proof:**
     ```text
     timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.

     ```text
     timeout 500s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `600000` ms.
   - **Acceptance within this stage:** real games-list `median_ms` ≤ 1,500 and `total_reported` == 12,710.
   - **Escalation boundary:** If the real median exceeds 1,500 ms, STOP — per the approved direction the implementation must return for a new decision rather than reach the target through a schema, migration, or index change.
   - **Breakpoint:** The Stage 3 gate decision (cache games or skip) is recorded here; it applies the approved direction, it is not a new product decision.

4. **pending - Add the process-local cache and wire training-requirements and openings reads.**
   - **Ordered actions:**
     1. Add `backend/app/caching.py` with separate bounded `cachetools.TTLCache` namespaces: training (TTL 60 s, maximum 128 entries) and openings (TTL 900 s, maximum 128 entries). Guard cache state with `threading.RLock` because sync route handlers run on FastAPI's threadpool. Add per-key single-flight coordination so concurrent identical misses invoke the underlying reader once rather than multiplying expensive work; compute outside the global lock, wake all waiters on success or failure, and never retain failed results.
     2. Build canonical keys only after the existing request model has validated, normalized, and supplied defaults. Include route identity, every response-affecting field (independent of query-string order), the resolved database path, and for training the resolved policy values from `get_training_requirement_policy`. Cache an immutable serialized payload from a successful response and construct a fresh response with the existing body, media type, and headers for each caller. Never cache 409 `training_requirements_stale`, 422, 500, or 503, and never create the database file on a miss (the existing 503 tests must keep passing unchanged).
     3. Track a cache generation under the lock. Whole-cache invalidation increments it; an in-flight computation may publish only when its captured generation and a post-computation database signature still match. This prevents a slow read that began before a write from repopulating stale data after invalidation.
     4. Build the database signature from the resolved main path and existing SQLite `-wal`, `-shm`, and journal sidecars, including existence, size, `st_mtime_ns`, and available file identity. Check it before serving a hit and before publishing a miss; a change increments the generation, clears all namespaces, and forces recomputation.
     5. Wire `GET /api/positions/training-requirements`, `GET /api/openings`, and `GET /api/openings/{opening_key}`, and clear all small namespaces after each successful `POST /api/positions/training-requirements/answers`, `PUT /api/preferred-moves`, and `DELETE /api/preferred-moves`.
     6. Add no `Cache-Control` or other browser caching headers (approved decision).
     7. Add focused tests under `backend/tests/features/api_cache/` covering: identical repeat calls the underlying reader once and preserves the exact response; semantically identical reordered inputs share a key; all normalized response-affecting inputs remain distinct; TTL expiry and maximum-size eviction; no caching of error statuses; invalidation after each of the three writes; main-file replacement and WAL/sidecar signature invalidation; concurrent identical misses call the underlying reader once and return consistent bodies; invalidation during an in-flight read prevents stale publication; a failed leader wakes waiters without caching the failure.
   - **Focused proof:**
     ```text
     timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/api_cache backend/tests/features/position_training_requirements/test_api.py backend/tests/features/openings/test_catalogue_api.py backend/tests/features/preferred_moves/test_put_api.py backend/tests/features/preferred_moves/test_delete_api.py -q
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.
   - **Escalation boundary:** Stop before caching anything other than the two listed read groups, before TTLs outside 30–60 s (training) or 10–30 minutes (openings), before per-entry invalidation complexity, or before any new dependency or service.
   - **Breakpoint:** None expected.

5. **pending - Apply the conditional games cache decision and refresh final proof.**
   - **Ordered actions:**
     1. If the Stage 3 gate says cache (real median > 1,000 ms): add a separate games namespace (TTL 60 s, maximum 64 entries), wire `GET /api/games` with every normalized filter/page/sort field in its canonical key, extend the cache tests, and keep the real games benchmark proving COLD latency by clearing the cache between repeats (the cache module's clear operation is the sanctioned seam).
     2. If the gate says skip: record that decision and the measured median in Progress and decisions; do not add games caching.
     3. Extend only the directly relevant benchmark scenarios to report cold and warm behavior separately for cached training/opening reads and, when the gate adds it, games reads. Explicitly clear the server cache between cold samples and reuse an identical normalized request for warm samples.
     4. Either way: tighten the real games tripwire default `CHESS_API_BENCH_MAX_MS_REAL_GAMES` in `backend/tests/benchmarks/test_api_benchmark_real.py` from 120,000 to no more than the approved 1,500 ms cold limit, and update the matching row and note in `docs/benchmarks/API/README.md` (documenting that the case proves cold latency and how caching interacts with repeats).
     5. Rerun the focused games, cache, and benchmark proof so every result reflects the final state.
   - **Focused proof:**
     ```text
     timeout 120s .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py backend/tests/features/games/test_api.py backend/tests/features/api_cache -q
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.

     ```text
     timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `180000` ms.

     ```text
     timeout 500s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v
     ```
     Working directory: `G:\ChessMoveTrainer`. Bash tool timeout: `600000` ms.
   - **Acceptance within this stage:** the tightened tripwire passes; the final real report records the cold games median against the 1.5 s target.
   - **Escalation boundary:** Stop before widening cache scope or altering any other benchmark case.
   - **Breakpoint:** None expected.

Stages are sequential; no parallel stages. A passing proof item remains valid until a later stage changes its command, inputs, exercised behavior, configuration, dependencies, or environment; later stages run only missing or invalidated proof (Stage 5 deliberately reruns the affected suites and benchmarks).

## Progress and decisions

- **Stage 1:** done 2026-09-14 - proof: `tests/database/games/test_search.py` 20 passed; real-database canonical-hash baseline captured (see below); breakpoint: none.
- **Stage 1 evidence:** default query `total` 12710, `total_pages` 255, page-UUID hash `8ba12fa15d20f7aeb65c0a5320455599ab1fff789c79af2c7f6d7cef6864b315`; `B10:Caro-Kann Defense` reached/length_asc `total` 3983, `total_pages` 80, hash `856031b4ea0887506b8c9277ab21ae64f9545f0488e01adaf020cc470acb5cd9`; database `data/database/chess.db` size 148,500,480 bytes, mtime_ns 1789381777077355900, no `-wal`/`-shm`/`-journal` sidecars.
- **Stage 1 correction:** the Plan text described `started_at_desc` as placing undated games before dated games (NULLs first); the current implementation places them last (`_compare_nullable` returns 1 for a `None` left side regardless of direction, and the pre-existing ordering test already showed the undated game last). The new boundary test encodes the actual NULLs-last behavior for both `started_at_desc` and `started_at_asc`.
- **Stage 2:** done 2026-09-14 - proof: `tests/database/games/test_search.py` plus `backend/tests/features/games/test_api.py` 34 passed, 1 skipped; real-database parity comparison exact (see below); breakpoint: none.
- **Stage 2 evidence:** database signature unchanged from Stage 1 (148,500,480 bytes, same mtime_ns, no sidecars); default query `total` 12710, pages 255, hash `8ba12fa15d20f7aeb65c0a5320455599ab1fff789c79af2c7f6d7cef6864b315`; Caro reached/length_asc `total` 3983, pages 80, hash `856031b4ea0887506b8c9277ab21ae64f9545f0488e01adaf020cc470acb5cd9` — all identical to Stage 1. Scalar filters, FEN/move `EXISTS`, opening `reached` `EXISTS`, and grouping run in SQL; timestamp bounds, termination, length/coverage, deepest selection and tie-break, all twelve sorts, pagination, error classes, read-only mode, and schema assertion preserved in Python.
- **Stage 3:** done 2026-09-14 after an authorized SQL-only rework round - proof: synthetic `backend/tests/benchmarks` 9 passed; real `test_api_benchmark_real.py` 6 passed; gate decision recorded (CACHE games, see below); breakpoint: none.
- **Stage 3 gate decision: CACHE `GET /api/games`.** Post-rework median is 1,029.06 ms (samples 931.45 / 1112.73 / 1029.06 ms, `total_reported` 12710, report `docs/benchmarks/API/20260914T145857Z-real-games-list.json`), which exceeds the 1,000 ms gate. Margin is thin (~3%), but the rule is mechanical and the approved games-cache shape (TTL 60 s, 64 entries) applies.
- **Stage 3 evidence:** `docs/benchmarks/API/20260914T145357Z-real-games-list.json` — samples 2808.06 / 2629.07 / 2721.31 ms, median 2721.31 ms, `total_reported` 12710 (correct), old 120,000 ms tripwire still in place. Improvement is real (88,522 ms to 2,721 ms, ~32x) but over the 1.5 s limit. Breakdown of one direct search (2725.8 ms): `_load_games` 116 ms, grouped aggregates 2296 ms, openings full-corpus 178 ms / 50-game page 4 ms. The aggregate query's per-row `EXISTS` probes against `derived_analysis_result` and `datasource_preferred_move_period` dominate.
- **Stage 3 diagnostic (read-only, no product change):** the same counts as three join-driven grouped queries cost 228 + 89 + 130 = 447 ms combined on the same database, i.e. a SQL-only restructure (no schema, migration, or index change) would plausibly bring the cold total to roughly 700 ms. Not implemented: Stage 3 orders STOP over further tuning without a new decision.
- **Stage 4:** done 2026-09-14 - proof: `backend/tests/features/api_cache` (17 new tests) plus `position_training_requirements/test_api.py`, `openings/test_catalogue_api.py`, `preferred_moves/test_put_api.py`, `test_delete_api.py` — 92 passed; breakpoint: none.
- **Stage 4 notes:** `backend/app/caching.py` holds the training (60 s/128) and openings (900 s/128) `TTLCache` namespaces, per-key single-flight, whole-cache generation, and main/sidecar signature guard; routers serialize successful reads with Starlette-identical JSON bytes and return fresh `Response` objects; all three writes clear the whole cache on success only. One fix during implementation: invalidation clears a live namespace registry (every created namespace registers itself) after a unit test showed a privately created namespace surviving a signature change.
- **Stage 5:** done 2026-09-14 - proof: focused suites 57 passed, 1 skipped; synthetic benchmarks 9 passed; real benchmarks 6 passed with the tightened 1,500 ms games tripwire; breakpoint: none.
- **Stage 5 evidence:** games namespace (TTL 60 s, 64 entries) wired into `GET /api/games` with all normalized fields in the key; preferred-move writes invalidate it via whole-cache clear. Final `docs/benchmarks/API/20260914T151656Z-real-games-list.json`: cold samples 991.77/1127.32/952.20 ms (median 991.77 ms, `total_reported` 12710, `cache_cleared_between_samples: true`), warm median 4.24 ms. Cached training/opening scenarios report cold and warm separately; both scenario loads record `warm_page1_ms` after a cache-cleared walk. `CHESS_API_BENCH_MAX_MS_REAL_GAMES` default is now 1500; `docs/benchmarks/API/README.md` documents the cold proof and warm reporting.
- **Baseline evidence to preserve:** real games list median 88,522.39 ms (50 of 12,710, `data/database/chess.db` 148,500,480 bytes, `docs/benchmarks/API/20260914T130514Z-real-games-list.json`); real global training load ~5.7 s; real position insight ~2.17 s; real openings list ~321 ms; real analysis ~50 ms. The dominant cold cost is per-occurrence `chess.Board` construction via `_stored_position` (`search_validation.py:64-74`) for every game's occurrences, loaded whole by `search()` (`search_repository.py:79-130`).
- **Settled decisions (from `docs/grilling-docs/api-performance-and-caching-direction.md`):** optimize the games query before caching; preserve all filters, totals, ordering, response fields, statuses, and edge cases; real cold games-list median ≤ 1.5 seconds on the same database; no schema, migration, or index change (stop and return for a new decision instead); cache training requirements and the opening catalogue in process-local backend memory; decide games caching from post-optimization measurements; invalidate after relevant successful writes and when the selected database file changes; no browser caching and no `Cache-Control` headers; no frontend changes; no failed-response, health, or rapid analysis/queue caching; no response-contract changes. TTL values 60 s (training) and 900 s (openings) sit inside the `api-caching-review.md` opinion ranges (30–60 s; 10–30 min) and are settled implementation choices.
- **Unresolved decisions:** none. The games-cache gate (add caching only if the measured real median exceeds 1,000 ms; otherwise skip and record) applies the approved direction; if the executor judges the gate ambiguous, stop instead of guessing.

## Proof

Results are recorded here as stages complete. A passing proof item remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment.

- **Stage 1 semantic guard:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py -q` from `G:\ChessMoveTrainer`, Bash tool timeout `180000` ms — done, 20 passed.
- **Stage 1 real parity baseline:** bounded read-only two-query canonical-hash snippet over `data/database/chess.db` (Stage 1 proof block), Bash tool timeout `360000` ms — done; default total 12710/pages 255/hash `8ba12fa1…`, Caro total 3983/pages 80/hash `856031b4…`, DB 148,500,480 bytes, no sidecars.
- **Stage 2 semantic guard:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py backend/tests/features/games/test_api.py -q` from `G:\ChessMoveTrainer`, Bash tool timeout `180000` ms — done, 34 passed, 1 skipped (also re-run clean after the authorized SQL-only rework).
- **Stage 2 parity comparison:** Stage 1 vs rewritten results on the unchanged `data/database/chess.db`; totals, page counts, ordered UUIDs, and canonical-result hashes must match exactly — done, all identical (both hashes above reproduced exactly).
- **Stage 3 synthetic benchmarks:** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v` from `G:\ChessMoveTrainer`, Bash tool timeout `180000` ms — done, 9 passed, 6 skipped.
- **Stage 3 real benchmarks:** `timeout 500s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v` from `G:\ChessMoveTrainer`, Bash tool timeout `600000` ms — done, 6 passed; final median 991.77 ms ≤ 1,500 ms, `total_reported` == 12,710 (reached after one user-authorized SQL-only rework round; first measurement was 2,721 ms and stopped per the escalation boundary).
- **Stage 4 cache proof:** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/api_cache backend/tests/features/position_training_requirements/test_api.py backend/tests/features/openings/test_catalogue_api.py backend/tests/features/preferred_moves/test_put_api.py backend/tests/features/preferred_moves/test_delete_api.py -q` from `G:\ChessMoveTrainer`, Bash tool timeout `180000` ms — done, 92 passed.
- **Stage 5 final reruns:** focused `tests/database/games/test_search.py backend/tests/features/games/test_api.py backend/tests/features/api_cache` — done, 57 passed, 1 skipped; synthetic benchmarks — done, 9 passed; real benchmarks with the 1,500 ms games tripwire — done, 6 passed.

## Stopping

- Stop and escalate rather than silently expanding scope when: the real cold games median exceeds 1,500 ms in Stage 3 (the approved direction forbids reaching the target through schema, migration, or index work); the parity comparison shows any result difference; a stage would need a schema/index change, a new dependency, a cache service, browser caching headers, or TTLs outside the settled ranges; benchmark or test infrastructure cannot run for environmental reasons; or a directly conflicting concurrent edit to an expected area appears.
- Stop and report when the Stage 3 gate measurement is ambiguous rather than choosing for the user.

## Escalation boundaries

- Any database schema change, migration, or new index — requires a new user decision (approved direction item 4).
- Any change to the response contract, statuses, pagination semantics, sort orders, or error codes of the games, training-requirements, or openings endpoints.
- Any new dependency, cache service, disk cache, multi-worker cache design, or `Cache-Control`/browser caching header.
- Any widening of cached endpoints beyond training-requirements, openings, and the gated games list — in particular position insight, analysis observation, the preferred-move timeline, health, or the 409 stale response.
- Any commit, push, stash, branch, or worktree operation, or any disturbance of unrelated worktree changes.

## Archive

- On acceptance: set **Status** to done with one progress line, fill every pending proof-ledger entry with its actual command and result, and move this directory to `docs/plans/done/api-latency-games-query-and-cache/`.
- The generated benchmark JSON files in `docs/benchmarks/API/` remain the durable measurement record; keep the before/after `real-games-list` reports alongside the totals, ordered UUIDs, and canonical hashes recorded in this Plan.
- Passing behavioral proof is retained until an affecting change; independent validation and complete test/fix runs are separate workflows when requested.

## Visible result

> Opening the games list returns page 1 of the 12,710-game database within 1.5 seconds on a cold request instead of roughly 88.5 seconds, repeated training-requirements and opening-catalogue requests reuse backend work until expiry or invalidation, and the next lookup after a successful training write does not reuse the earlier cached result.
