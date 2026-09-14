# API slowness and caching review

**Status:** Review only, 14 September 2026
**Purpose:** Record what was checked about slow API responses and possible caching, and list the questions that need answers before any caching work starts.
**Rule followed:** No code was built or changed for this review. This is not a Plan and does not approve implementation.

Prior related record: `docs/grilling-docs/trainer-practice-retrieval-contract.md` defines the current `GET /api/positions/training-requirements` contract. It makes no caching decision.

## What was checked

Backend routes registered in `backend/app/main.py:25-32`:

- `GET /api/health` in `backend/app/features/health/router.py:8-10`
- `GET /api/games` and `GET /api/games/{game_uuid}` in `backend/app/features/games/router.py:127-229`
- `GET /api/openings` and `GET /api/openings/{opening_key}` in `backend/app/features/openings/router.py:67-140`
- `GET /api/preferred-moves`, `PUT /api/preferred-moves`, `DELETE /api/preferred-moves` in `backend/app/features/preferred_moves/router.py:200-295`
- `GET /api/positions/insight` in `backend/app/features/position_insight/router.py:137-165`
- `GET /api/positions/training-requirements` and `POST /api/positions/training-requirements/answers` in `backend/app/features/position_training_requirements/router.py:127-235`
- `POST /api/analysis-requests` in `backend/app/features/analysis_requests/router.py:40-74`
- `GET /api/analysis` in `backend/app/features/analysis_observation/router.py:87-108`

Database boundary and repositories checked:

- `src/chess_move_trainer/database/connection.py:66-85`
- `src/chess_move_trainer/database/positions/training_requirements_repository.py:93-199`
- `src/chess_move_trainer/database/games/search_repository.py:79-130`
- `src/chess_move_trainer/database/positions/insight_repository.py` and `insight_readers.py`
- `backend/app/dependencies.py:21-41`
- `backend/app/features/position_training_requirements/router.py:138-167`

Frontend callers checked:

- `frontend/src/api/client.ts:16-17`
- `frontend/src/features/trainer-practice/trainerPracticeApi.ts:12-14,135-261`
- `frontend/src/features/status/StatusPage.tsx:7`
- `frontend/src/features/analysis/analysisState.ts:12-13,82-182`
- `frontend/src/features/repertoire-builder/preferredMoveApi.ts:375-432`
- `frontend/src/features/repertoire-builder/positionContextApi.ts:115-122`
- `frontend/src/features/repertoire-builder/moveResponseDistributionApi.ts:205-212`

Other checks:

- `data/database/chess.db` exists and is about 142 MB. `data/chess-com` is about 39 MB. `data/stockfish` is about 109 MB.
- `requirements.txt` and `pyproject.toml` list `FastAPI==0.115.6` and `SQLAlchemy==2.0.52`, with no cache library such as Redis.
- `docs/benchmarks/` is empty.
- `docs/plans/done/trainer-practice-retrieval-panel/trainer-practice-retrieval-panel.md` records test run times, not API response times.
- `tests/e2e/`, `backend/tests/`, and the last 15 git commits contain no latency numbers and no prior caching decision.
- Search for `cache`, `lru_cache`, `redis`, `ETag`, `Cache-Control`, and `If-None-Match` in `backend/` and `src/` found no server-side response cache.

Backend runs at `http://localhost:5666`. Frontend runs at `http://localhost:8444`.

## Finding 1: There is no server-side response cache today

The backend sets no `Cache-Control` or `ETag` headers and keeps no in-memory copy of prior responses.

Concrete example: every call to `GET /api/positions/training-requirements?as_of=2026-09-14&training_requirement_lt=0&page=1&page_size=100` runs the full repository work again, even if the same address was requested one second earlier with the same database file.

The only `cache` word in Python source is a short-lived helper used during data import, for example `position_cache` in `src/chess_move_trainer/database/positions/repository.py:126-211`. That helper is discarded when the import finishes. It does not make repeated API reads faster.

The frontend uses TanStack Query, but that is page-local request state. Example: `frontend/src/features/status/StatusPage.tsx:7` uses `gcTime: 0`, which discards the health result as soon as the page is left. `frontend/src/features/trainer-practice/trainerPracticeApi.ts:190-261` keeps loaded training items in local variables during one load only. There is no shared frontend store of openings, games, insight, or training results across visits.

Result: caching is a real gap, but adding it without answering the questions below could return old training data after a user has submitted a new answer.

## Finding 2: Every request opens the database from scratch

`src/chess_move_trainer/database/connection.py:74-78` creates an engine with `poolclass=NullPool`, then `engine.dispose()` runs after each use in `connection.py:79-85` and `connection.py:106-112`.

What this means in plain steps:

1. A request arrives, for example `GET /api/games?page=1&page_size=50`.
2. The route receives only a file path from `backend/app/dependencies.py:21-24`.
3. The repository opens a new SQLite connection to `data/database/chess.db`.
4. It reads, closes the connection, and discards the engine.
5. The next request repeats all of step 3 and 4.

There is no kept-open pool of database connections. For a 142 MB SQLite file, open, setup (`PRAGMA foreign_keys = ON`, `PRAGMA busy_timeout` in `connection.py:137-145`), schema check, and close work happens on every API call.

This alone may not explain all slowness, but it adds repeated cost to every endpoint, including small ones such as one opening lookup.

## Finding 3: Two endpoints read far more data than one page needs

### 3a. Training requirements reads the whole corpus, then returns one page

`TrainingRequirementRepository.discover` in `src/chess_move_trainer/database/positions/training_requirements_repository.py:93-199` does this order:

1. Load all preferences with `_load_preferences`.
2. Loop over all rows from `_load_occurrences`, which selects across game, position, and game tables without a page filter.
3. Load all opening matches with `_load_opening_matches`.
4. Load all training aggregates with `_load_training_aggregates`.
5. Score matching groups in Python.
6. Only at the end, return the requested `page` and `page_size`.

The route default is `page_size=50` in `backend/app/features/position_training_requirements/router.py:150`. The trainer frontend asks for `page_size=100` in `frontend/src/features/trainer-practice/trainerPracticeApi.ts:12,117-122`.

Concrete effect: asking for page 1 still pays the cost of reading and scoring everything, then throws away all but 100 rows.

### 3b. Game search loads every game before filtering

`GameSearchRepository.search` in `src/chess_move_trainer/database/games/search_repository.py:86-122` does this order:

1. `_load_games`, `_load_occurrences`, and `_load_openings` load games and related rows into Python memory.
2. Two more full loads read analyzed position IDs and preferred-move position IDs.
3. Python code filters with `_matches`, sorts with `_compare_games`, then slices out one page with `matched[start : start + request.page_size]`.

Concrete effect: `GET /api/games?page=1&page_size=50` still reads the full game set before returning 50 summaries.

A cache would hide this cost on repeat requests, but it would not remove the first-load cost. The first load after every write or cache clear would still be slow.

## Finding 4: The frontend can turn one user action into many API calls

This matters because a backend cache and a frontend request change solve different parts of the problem.

Examples found in the current code:

- Trainer practice full load: `fetchTrainingRequirements` in `frontend/src/features/trainer-practice/trainerPracticeApi.ts:198-252` loops page 1, 2, 3, and so on until `loadedItems.length` reaches `total`. If 850 positions need training and `page_size` is 100, that is 9 sequential backend calls for one **Practice Caro** action. Each of those 9 calls currently repeats the full-corpus work from Finding 3a.
- Opening catalogue full load: `fetchOpeningChoices` in `frontend/src/features/trainer-practice/trainerPracticeApi.ts:135-173` reads page 1, then reads remaining pages with up to 4 calls at once. A full catalogue load can therefore send many `GET /api/openings?page=N&page_size=100&sort=name_asc` calls together.
- Analysis polling: `frontend/src/features/analysis/analysisState.ts:130-133,156-157` calls `GET /api/analysis?fen=...` every 1000 ms while the result is `queued` or `running`, up to 60 tries. That is by design while waiting for Stockfish, but it means one open analysis panel can call the same address 60 times.
- Double insight reads: both `positionContextApi.ts:115-122` and `moveResponseDistributionApi.ts:205-212` call `GET /api/positions/insight` with the same `fen`, `trainer_color`, and `as_of` when the board position changes. Moving through 20 positions can therefore send about 40 insight requests.
- Status page: `StatusPage.tsx:7` calls `GET /api/health` on every mount with no retained cache. This endpoint is cheap today because `health/router.py:8-10` returns `{"status":"ok"}` without touching the database, so this one is not a concern unless health is later made to check the database.

Result: even if each backend response is only a little slow, trainer practice and board navigation multiply that cost.

## Finding 5: Some data changes rarely, some data changes on every answer

Caching is only safe if old results are cleared or updated when the underlying data changes.

Data that changes rarely:

- Opening catalogue rows used by `GET /api/openings`.
- Game records and opening routes used by `GET /api/games`, unless a new import replaces `data/database/chess.db`.
- Preferred-move periods change only when a user sends `PUT /api/preferred-moves` or `DELETE /api/preferred-moves`.

Data that can change on every training answer:

- `POST /api/positions/training-requirements/answers` records a hit or miss and updates training state in `src/chess_move_trainer/database/positions/training_answers.py`.
- After that write, the next `GET /api/positions/training-requirements?as_of=<same date>` for the same `fen` and `trainer_color` should show the new score, not the cached old score.
- `POST /api/analysis-requests` can change what a later `GET /api/analysis?fen=...` returns, from queued to complete.

The `as_of=<YYYY-MM-DD>` date adds another wrinkle. A response cached for `as_of=2026-09-13` must not be returned for `as_of=2026-09-14`, and a 409 `training_requirements_stale` response means the stored training state is newer than the requested date. Cache keys must include the full address, including `as_of`, `trainer_color`, `opening_key`, `opening_match`, `page`, and `page_size`.

## Finding 6: No measurements exist yet, so the slowest part is not proven

There are no benchmark files in `docs/benchmarks/`. There are no response-time logs or targets in plans, tests, or git history.

Known numbers are test-suite times, not user-facing API times:

- 37 tests passed in 5.38 seconds in `docs/grilling-docs/trainer-practice-retrieval-contract.md:103`.
- 1 real-database test in 14.28 seconds and 1 Playwright test in 58.7 seconds in `docs/plans/done/trainer-practice-retrieval-panel/trainer-practice-retrieval-panel.md:111-116`.

Those numbers do not say which endpoint is slow, how slow it is in milliseconds, whether the time is database reading, Python scoring, JSON encoding, Docker file sharing, or frontend sequential paging, or whether the database file, machine, or query was representative.

Adding a cache before measuring risks caching the wrong layer. Example: if most time is JSON encoding of 100 full training items, caching the Python objects without caching the final JSON helps less than expected. If most time is the full SQLite scan, a database index or a narrower SQL query may help more than a cache.

## Questions that need answers before caching work

Each question names why it matters and gives a concrete example from this repository.

### A. Goals and measurements

1. Which exact action feels slow? Please name the page and button, for example “Trainer Practice page, after I choose Caro-Kann and select Practice,” or “Repertoire Builder, after I change board position,” or “Game list, after I change a filter.”
2. What is slow in numbers? For that action, what response time are you seeing, and what response time would count as fixed? Example: “Page 1 of training requirements takes 4,200 ms and should take under 500 ms.”
3. How should we measure it? Can we use a fixed database file, a fixed request such as `GET /api/positions/training-requirements?as_of=2026-09-14&training_requirement_lt=0&opening_key=<exact Caro-Kann key>&opening_match=reached&page=1&page_size=100`, and repeat it 5 times locally? Where should the result be saved so later work can compare against it?
4. Is the first load the problem, repeat loads, or both? Example: first Practice load is slow but pressing Practice again is fast, or both are slow.
5. How much data is typical? How many training items, games, and openings are in the slow case? Example: total 850 training items at 100 per page, or total 12,000 games.

### B. Correctness and freshness

6. After `POST /api/positions/training-requirements/answers`, how quickly must the next training list show the new result? Is “immediately on the next request” required, or is “within 60 seconds” acceptable?
7. After `PUT /api/preferred-moves` or `DELETE /api/preferred-moves`, how quickly must training requirements, insight, and game summaries reflect the change?
8. After `POST /api/analysis-requests`, should `GET /api/analysis?fen=<same FEN>` keep polling the database, or may it return a cached “queued” answer for a short time?
9. Can responses for an old `as_of` date be kept longer than today’s date? Example: may `as_of=2026-08-01` be cached for a day while `as_of=<today>` is cached for only one minute?
10. What should happen on a write: clear the whole cache, clear only matching entries such as the same `fen` and `trainer_color`, or update cached entries in place?

### C. Scope: what to cache first

11. Which endpoint should be fixed first? Options are training requirements, game search, openings catalogue, position insight, analysis observation, or preferred-move timeline. Only one should be first so the change stays small.
12. Should the opening catalogue be cached longer than training data? Catalogue rows change rarely, while training scores change on every answer.
13. Should error responses be cached? Example: if `as_of` is invalid and returns 422, or state is stale and returns 409, should the same bad request return the cached error or run validation again?
14. Is the trainer full-pagination behavior staying? `fetchTrainingRequirements` currently loads every page until `total` is reached. If that stays, a cache helps repeat Practice loads. If it changes to lazy loading, the cache design changes too.

### D. Frontend behavior

15. Should the frontend send fewer requests, keep the same requests, or is backend caching enough? Example: keep 9 sequential training page calls and cache each page on the server, or change the frontend to request fewer pages.
16. Should the two insight callers share one result? `positionContextApi.ts` and `moveResponseDistributionApi.ts` request the same `GET /api/positions/insight` address for the same board position. May they share one frontend request?
17. Should analysis polling stay at every 1000 ms up to 60 tries? If yes, should those polling responses bypass or use a very short cache so queued work is not hidden?
18. Should the status page keep `gcTime: 0` for `GET /api/health`? That address is cheap today, so no change is likely needed unless health starts checking the database.

### E. Technical limits and operations

19. Where may cached data live? Options are in backend process memory only, in a separate local service, on disk next to `data/database/chess.db`, or only as HTTP cache headers that tell the browser it may reuse a response. Process memory is simplest but disappears on backend reload. A separate service adds setup and Docker work.
20. How many users and processes matter? Is this one local user with one backend container, or could two requests write and read at the same time? SQLite uses file locks and a 5 second busy timeout in `connection.py:16,137-145`, so concurrent writes plus a cache need careful ordering.
21. What happens when `CHESS_REBUILT_DATABASE_PATH` points to a replaced database file? Should replacing the file clear all cached responses?
22. Should fixes to the SQL queries come before caching? Example: add a narrower `WHERE` clause and index for training requirements and game search so each page reads only its page, then add a cache only if still needed.
23. What is explicitly out of scope? Examples: Stockfish engine speed, PGN import speed, Playwright test time, and Storybook startup time are separate from API response caching unless you say otherwise.

## Opinions: basic, run-of-the-mill defaults

Added 14 September 2026 at your request. These are opinions only, not decisions. They describe the plain caching you would expect on a small project like this one: in-memory backend cache per endpoint, short lifetimes, full request address as the key, and clear-on-write. No Redis, no separate cache server, no special algorithm.

The default pattern behind most answers below is:

- Keep the stored response in backend process memory for a short time.
- Use the full request address as the key, including `as_of`, `trainer_color`, `opening_key`, `opening_match`, `fen`, `page`, and `page_size`.
- Cache only successful `200` responses, not validation or server errors.
- Clear affected entries as soon as a related write succeeds.
- Add `Cache-Control: private, max-age=<seconds>` on cached GETs so the intent is visible, while the backend memory remains the real store.

### A. Goals and measurements

1. Which exact action feels slow?
**Opinion:** Start with the trainer **Practice** load that calls `GET /api/positions/training-requirements` in `frontend/src/features/trainer-practice/trainerPracticeApi.ts:190-252`. Reason: Finding 3a and Finding 4 show this path repeats full-corpus work once per page, so one Practice click can trigger 9 slow calls. Fix this path first, then check board navigation. Leave `GET /api/health` alone because `backend/app/features/health/router.py:8-10` does no database work.

2. What is slow in numbers?
**Opinion:** Set two plain targets and keep them. Example default: one training-requirements page under 500 ms on the local Docker backend, and one full Practice load of up to 1,000 items under 3 seconds. Reason: a per-page target catches the repository cost, and a full-load target catches the frontend page loop. Adjust the numbers after the first 5-run timing in question 3.

3. How should we measure it?
**Opinion:** Yes, use one fixed local setup and save it in `docs/benchmarks/`, which is empty today. Suggested default: fixed `data/database/chess.db` file name and size recorded, one fixed request such as `GET /api/positions/training-requirements?as_of=<today>&training_requirement_lt=0&opening_key=<exact Caro-Kann key>&opening_match=reached&page=1&page_size=100`, 5 repeats with backend already running via `dev.ps1 status`, record each time plus `total`. Reason: this is the smallest repeatable check that matches the settled Practice Caro contract.

4. Is the first load the problem, repeat loads, or both?
**Opinion:** Assume both until measured, but expect basic caching to help repeat loads only. Reason: the first load after a write or restart still runs `TrainingRequirementRepository.discover` in `src/chess_move_trainer/database/positions/training_requirements_repository.py:93-199` end to end. If first loads must also be fast, the SQL query needs narrowing first; a cache alone will not fix it.

5. How much data is typical?
**Opinion:** Record `total`, `page`, and `page_size` from the slow response and keep them with the timing. Reason: 85 items in 1 page and 8,500 items in 85 pages need different fixes. The trainer code already exposes `total` in `trainerPracticeApi.ts:204-259`, so copy that number into the benchmark note.

### B. Correctness and freshness

6. After `POST /api/positions/training-requirements/answers`, how quickly must the next training list show the new result?
**Opinion:** Immediately on the next request. Reason: the user just answered a position and expects the score and `correct_answers_needed` for that `fen` and `trainer_color` to change. Basic approach: when the answer write in `src/chess_move_trainer/database/positions/training_answers.py` succeeds, delete cached training-requirements pages that could contain that `fen` and `trainer_color`. A 60-second delay would show a wrong score right after the user acted.

7. After `PUT /api/preferred-moves` or `DELETE /api/preferred-moves`, how quickly must dependent reads reflect the change?
**Opinion:** Immediately on the next request. Reason: preferred moves feed training scoring, insight, and game summaries. Basic approach: on a successful PUT or DELETE in `backend/app/features/preferred_moves/router.py:231-295`, clear cached entries for training requirements, position insight, and preferred-move timeline. This is a small app, so clearing those three groups is simpler and safer than trying to update each cached row in place.

8. After `POST /api/analysis-requests`, should `GET /api/analysis?fen=<same FEN>` use a cache?
**Opinion:** Either no cache or a very short cache of 1 to 2 seconds. Reason: `frontend/src/features/analysis/analysisState.ts:130-157` polls every 1000 ms waiting for `queued` to become complete. Caching `queued` for 30 seconds would hide the result the user is waiting for. If a cache is added here at all, keep it at 1 to 2 seconds only to absorb double requests.

9. Can responses for an old `as_of` date be kept longer than today's date?
**Opinion:** Yes. Reason: `as_of=2026-08-01` refers to a closed day and its training state does not move, while `as_of=<today>` moves with every answer. Basic default: keep past-date training pages up to 60 minutes, keep today’s pages 30 to 60 seconds. Always include the full `as_of` value in the cache key so 13 September never returns 14 September data, and never cache the 409 `training_requirements_stale` response.

10. What should happen on a write: clear the whole cache, clear only matching entries, or update in place?
**Opinion:** Clear matching groups; if that is awkward to implement, clear the whole small in-memory cache. Reason: this backend serves one local user and a handful of endpoints, so clearing everything on a write is correct and easy to reason about. Do not update cached JSON in place. Example: answer submit clears training-requirements entries; preferred-move PUT or DELETE clears training, insight, and timeline entries; analysis request clears only that `fen` analysis entry.

### C. Scope: what to cache first

11. Which endpoint should be fixed first?
**Opinion:** `GET /api/positions/training-requirements` first. Reason: it combines the most expensive backend work from Finding 3a with the most multiplied frontend calls from Finding 4. Second would be `GET /api/games`, which has the same full-load pattern in `src/chess_move_trainer/database/games/search_repository.py:86-122`.

12. Should the opening catalogue be cached longer than training data?
**Opinion:** Yes. Reason: `GET /api/openings` rows change only on re-import or catalogue rebuild, while training scores change per answer. Basic default: openings 10 to 30 minutes, training requirements for today 30 to 60 seconds. Clear openings cache only on import or explicit catalogue change.

13. Should error responses be cached?
**Opinion:** No. Cache only `200` responses. Reason: 422 invalid input, 409 stale date, and 503 unavailable are cheap to recompute and caching them can lock in a wrong answer. Example: if `as_of` is mistyped and returns 422, the next corrected date must run validation fresh. If training state moves and returns 409, that decision must be rechecked each time.

14. Is the trainer full-pagination behavior staying?
**Opinion:** Yes, keep `fetchTrainingRequirements` loading all pages until `total` is reached, as defined in `trainerPracticeApi.ts:198-252` and the prior contract. Reason: changing to lazy loading is a separate product change with its own ordering and session questions. Basic caching fits the current behavior: cache each page by its full address so repeat Practice loads reuse pages 1 to N.

### D. Frontend behavior

15. Should the frontend send fewer requests, or is backend caching enough for now?
**Opinion:** Backend caching is enough for the first step; do not rewrite trainer paging yet. Reason: keeping `page_size=100` and the page loop unchanged in `trainerPracticeApi.ts:12-14,190-261` keeps the change small. Revisit fewer or larger pages only if the benchmark in question 3 still misses its target after backend caching plus query narrowing.

16. Should the two insight callers share one result?
**Opinion:** Yes, share one request for the same `fen`, `trainer_color`, and `as_of`. Reason: `positionContextApi.ts:115-122` and `moveResponseDistributionApi.ts:205-212` ask for the same `GET /api/positions/insight` address on the same board position. Basic frontend fix: one TanStack Query key per position plus color and date, read by both callers. This is ordinary request deduplication, not a special method. It halves insight traffic when stepping through positions.

17. Should analysis polling stay at every 1000 ms up to 60 tries?
**Opinion:** Yes, keep the interval and limit in `analysisState.ts:12-13,130-157`, and keep those polling reads fresh. Reason: the interval is the user-visible wait for Stockfish. Either bypass the backend cache for `GET /api/analysis` while polling, or use a 1 to 2 second lifetime. Do not apply the 30 to 60 second training lifetime here.

18. Should the status page keep `gcTime: 0` for `GET /api/health`?
**Opinion:** Yes, leave `StatusPage.tsx:7` as is. Reason: health returns `{"status":"ok"}` with no database read, so there is nothing meaningful to cache. Only revisit if health is later changed to check the database or disk.

### E. Technical limits and operations

19. Where may cached data live?
**Opinion:** In backend process memory only. Reason: this is the standard smallest step for one container and one SQLite file. It needs no new entry in `requirements.txt`, no new service in `compose.yaml`, and no extra port. Accept the known limit: a backend restart or image rebuild clears it, which is safe because the next request simply rereads `data/database/chess.db`. Add `Cache-Control: private, max-age=<seconds>` headers to document intent, but do not rely on the browser as the only store.

20. How many users and processes matter?
**Opinion:** Build for one local user and one backend worker, and write that assumption down. Reason: SQLite uses a file lock with a 5 second busy timeout in `connection.py:16,137-145`. With one writer at a time, clear-on-write in the same process is correct. If a second worker or user is added later, process memory is no longer shared and the cache design must be revisited. Do not add a shared cache server until that need is real.

21. What happens when `CHESS_REBUILT_DATABASE_PATH` points to a replaced database file?
**Opinion:** Clear the whole backend cache when the path value, file size, or last-write time changes. Reason: `backend/app/dependencies.py:21-24` allows the database file to be swapped by environment. Serving old pages for a new file would show positions and scores from the wrong dataset. Checking path plus file metadata on each request is a cheap, ordinary guard.

22. Should fixes to the SQL queries come before caching?
**Opinion:** Yes, narrow the queries first, then add the small cache. Reason: Finding 3 shows training requirements and game search read the full corpus for one page. Basic order: add `WHERE` filters and indexes so page 1 reads closer to 100 rows, keep Python scoring only for the rows on that page where possible, then cache the resulting page for 30 to 60 seconds. Caching first would only hide the full scan on repeat hits and leave first loads slow.

23. What is explicitly out of scope?
**Opinion:** Keep Stockfish engine speed, PGN import speed, Playwright run time, Storybook startup, and the `dev.ps1` container setup out of scope. Reason: the complaint is slow API reads in the app at `http://localhost:5666` and `http://localhost:8444`. Engine queue work lives outside the HTTP handlers in `src/chess_move_trainer/database/stockfish/`, and import plus test time do not change what the user waits for on Practice or board moves.

## Suggested next step, not a decision

Pick one slow action from Section A, record its exact request address and total item count, and time it 5 times against a named database file before choosing between a narrower database query, a smaller frontend request pattern, or a cache. Save that timing where future work can find it, since `docs/benchmarks/` is currently empty.
