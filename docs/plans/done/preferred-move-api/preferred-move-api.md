# Preferred-move API - Skyrocoster can manage one preferred move for an observed position

> **Status:** done - Stages 1 and 2 accepted; workflow closeout complete

- **Read trigger:** Read before implementing the Skyrocoster preferred-move HTTP API or its focused backend tests.
- **Upstream:** [Accepted preferred-move storage Plan](../../done/preferred-move-storage/preferred-move-storage.md)

## Outcome

Skyrocoster can retrieve the current or historical preferred move for one existing game-derived position and can
set/replace or remove that move through a small backend-only API. The API uses the existing append-only storage
histories, keeps counters out of position identity, and never creates or migrates database schema while serving a
request.

## Scope

- **Included:** A fixed-owner `/api/preferred-move` GET/PUT/DELETE lifecycle; strict six-field FEN validation at the
  HTTP boundary and established four-field identity internally; canonical legal UCI input with backend-derived SAN;
  current and effective-time reads; UTC effective-time defaulting and future rejection; typed safe errors; read-only
  schema preflight; bounded read/write connection handling; CORS registration for the two mutation methods; and
  temporary-database API tests for the settled behavior.
- **Expected areas:** `backend/app/features/preferred_move/*.py`, `backend/app/main.py`, and
  `backend/tests/features/preferred_move/*.py`.
- **Excluded:** `scripts/opening_catalog/**`, `data/database/schema.txt`, runtime database files, frontend/UI,
  training or engine behavior, player selection or authentication, schema creation or migration, new dependencies,
  requirement-state API exposure, full history, line saving, comparison, candidate lists, analysis, artificial or
  opening-only position insertion, projections, caches, destructive replacement, commits, pushes, and unrelated
  worktree or historical-document changes. README maintenance is separate; if structural navigation becomes stale,
  the coordinator routes that work separately.

The HTTP contract refined for this Plan is:

- `GET /api/preferred-move?fen=<full FEN>&as_of=<optional aware UTC timestamp>` returns
  `{fen, state, move}`, where `state` is `assigned` or `unassigned`, `fen` is the canonical full six-field FEN,
  and `move` is either `{uci, san}` or `null`. Omitted `as_of` means current time; a supplied value may be any
  valid aware UTC instant, while a blank value is invalid.
- `PUT /api/preferred-move` accepts only `{fen, move_uci, effective_at?}` and returns
  `{fen, changed, effective_at}`. `effective_at` is normalized to canonical UTC; omitted, JSON `null`, or blank
  means one UTC instant captured for that request. The endpoint sets or replaces the event at that effective time.
- `DELETE /api/preferred-move?fen=<full FEN>&effective_at=<optional timestamp>` returns the same mutation shape and
  appends a removal event. Omitted, blank, or otherwise absent mutation time uses one captured current UTC instant.
- Request models forbid extra fields and do not accept a player identifier. Error bodies use `{code, message}` with
  safe messages: validation is 422 (`invalid_fen`, `invalid_move`, `invalid_timestamp`, or
  `future_effective_time`), a valid non-game-derived position is 404 `position_not_found`, unavailable,
  incompatible, or locked storage is 503 `preferred_move_unavailable`, and unexpected failures are 500
  `unexpected_failure`. Requirement-state events remain internal.

## Stages

1. **complete - accepted** - implement the strict API boundary, service/repository adapter, route registration, and schema
   non-creation protection.
   - **Ordered actions:**
     1. Add the bounded `preferred_move` backend package with strict Pydantic response/request/error contracts,
        domain errors, and service validation for canonical six-field FEN, four-field identity, aware UTC parsing,
        blank/default mutation times, past/present acceptance, future rejection, and canonical legal UCI/SAN.
     2. Add the repository adapter using the fixed subject UUID from the positions feature. Open existing databases
        without creating missing files; use a read-only connection for GET and a `mode=rw`, zero-wait connection for
        mutations. Before every operation, perform a non-mutating check of the supported corpus/preferred schema,
        expected preferred tables/columns/version/triggers, and fixed subject ownership. Never call the existing
        schema-ensuring entry point from an API request.
     3. Resolve position existence only through `position_state` joined to `position_occurrence`. Delegate event
        writes/state derivation to the existing append-only storage primitives without schema initialization, keeping
        effective-time/recorded-time/event-id ordering, no-op writes, remove events, and four-field identity intact.
        Wrap mutations in one transaction, map SQLite lock/busy and schema failures to the safe 503 boundary, and
        prevent partial event writes.
     4. Add the router and register it in `backend/app/main.py`; extend CORS only for the already-approved PUT and
        DELETE methods. Keep the response free of requirement state, history, player selection, or fields requiring
        extra storage queries.
   - **Focused proof:** Stage 2 must exercise each route through `TestClient` against an isolated temporary database;
     no product or test implementation is authorized beyond the paths above.
   - **Breakpoint:** None. Stop and escalate if the adapter would need to change `scripts/opening_catalog`, add a
     schema object, expose requirement state, alter event ordering, or choose a different owner or identity.

2. **complete - accepted** - add the focused temporary-database API suite and complete scoped validation.
   - **Ordered actions:**
     1. Add a fixture under `backend/tests/features/preferred_move/` that creates only a temporary SQLite database,
        seeds Skyrocoster and an opponent with existing game-derived occurrences, and initializes the already-approved
        preferred schema only during fixture setup. Patch `CHESS_DATABASE_PATH` to that file and prove the default
        runtime database is not selected or written.
     2. Cover the full lifecycle: unassigned GET is 200, PUT assigns, PUT replaces, DELETE removes, assigned GET
        returns canonical `{uci, san}`, event counts and actions are correct, prior events remain present, and a
        repeated same effective move is a no-op. Verify append-only triggers/history are not bypassed.
     3. Cover counter-insensitive four-field identity with distinct valid FEN counters; current versus `as_of`
        reads; backdated events; same-effective-time ordering; omitted, null, and blank mutation time defaulting;
        blank `as_of` rejection; valid future `as_of`; and future PUT/DELETE effective-time rejection without events.
     4. Cover illegal or malformed UCI, invalid/noncanonical FEN, unknown valid and non-game-derived positions,
        fixed ownership and forbidden player selection, missing/incompatible schema, missing database without file
        creation, lock/busy mapping, safe unexpected 500 handling, temporary-database isolation, and PUT/DELETE CORS
        preflight. Assert error responses contain no storage internals.
     5. Run the focused pytest, scoped Ruff check and format check, source/test size check, and final diff/scope audit.
        Do not change generated schema documentation because this outcome has no schema change.
   - **Focused proof:** The finite commands in **Proof** must pass, with the API suite proving every behavior named in
     this stage and no request creating schema or touching the runtime database.
   - **Breakpoint:** None; this is backend-only and has no visual review. Escalate rather than weakening validation,
     using the runtime database, or accepting a new API/data/dependency decision.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
approved outcome or requiring a new decision.

## Progress and decisions

- **Stage 1:** complete and accepted - proof: existing storage regression (12 passed), import smoke, scoped Ruff
  check/format, source/test size check, and diff check; breakpoint: none.
- **Stage 2:** complete and accepted - proof: preferred-move API suite (17 passed), scoped Ruff check/format,
  source/test size check, and diff/scope audit; all tests used `tmp_path` databases and did not access the runtime
  database; breakpoint: none.
- **Decision:** Ownership is always the existing Skyrocoster subject UUID; clients cannot select a player.
- **Decision:** The API returns only current/as-of state and minimal mutation acknowledgment. It does not expose
  requirement events or promise effective/recorded event metadata that would require extra queries.
- **Decision:** Existing public storage functions that can call `ensure_preferred_move_schema()` are not used on the
  request path; the adapter must preflight and then use only non-initializing append/state primitives.
- **Decision:** Tests may write only their own `tmp_path` database fixtures; no test may write the runtime database.
- **Decision:** Stage 1 uses read-only SQLite URI connections for GET, existing-file `mode=rw` zero-wait connections
  for mutations, and `BEGIN IMMEDIATE`; schema validation is non-mutating and occurs before position access.
- **Decision:** This Plan did not test or write the real database, and no backup was made. Before any future explicitly
  approved test that writes the real database, make one simple filesystem copy immediately before it; use no
  hashing/integrity workflow. This Plan does not authorize a runtime write.

## Proof

All commands below run from the repository root in Git Bash. Each `timeout` is the finite command-level timeout; the
parenthetical value is the required finite `bash` tool timeout in milliseconds. These are execution/closeout commands,
not commands run while writing this Plan.

- `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_move -q`
  (bash tool timeout: `150000` ms).
- `timeout 60s .venv/Scripts/python.exe -m ruff check backend/app/features/preferred_move backend/app/main.py backend/tests/features/preferred_move`
  (bash tool timeout: `90000` ms).
- `timeout 60s .venv/Scripts/python.exe -m ruff format --check backend/app/features/preferred_move backend/app/main.py backend/tests/features/preferred_move`
  (bash tool timeout: `90000` ms).
- `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`
  (bash tool timeout: `90000` ms).
- `timeout 30s git diff --check`
  (bash tool timeout: `60000` ms).
- `timeout 30s git diff --name-only -- backend/app/features/preferred_move backend/app/main.py backend/tests/features/preferred_move docs/plans/done/preferred-move-api/preferred-move-api.md`
  (bash tool timeout: `60000` ms); the final scope audit must contain only approved paths and preserve unrelated
  changes.
- Authoritative closeout: `.venv/Scripts/python.exe scripts/check.py` passed all 11 phases. This is the authoritative
  closeout record; `scripts/check.py --full` was not run.
- Independent Quality inspection validated route/service/repository/contracts, safe errors, schema non-creation,
  fixed ownership, append-only behavior, CORS, and temporary-database isolation.
- Fresh final Quality scope audit returned PASS with no unrelated changes or failures; acceptance was sufficient.

## Acceptance

The outcome is accepted: all three lifecycle operations work for an existing game-derived position under the fixed
Skyrocoster UUID; GET distinguishes assigned, unassigned, and unknown positions; full FEN counters do not change the
four-field identity; canonical UCI/SAN, append-only ordering, replacement, removal, and no-op behavior are proven;
as-of/backdated and default/blank/future time rules are proven; all required 422/404/503/500 boundaries are safe;
CORS covers PUT/DELETE without frontend work; API requests never create or migrate schema; and tests write only an
isolated temporary database. Focused checks, independent Quality inspection, and the authoritative
`.venv/Scripts/python.exe scripts/check.py` closeout passed, with final Quality scope audit PASS. No runtime database
write or backup was made.

## Escalation boundaries

- Any change to the fixed Skyrocoster ownership, existing game-derived position requirement, four-field identity,
  canonical full-FEN boundary, legal UCI/SAN behavior, timestamp rules, no-op semantics, event ordering, or
  append-only storage.
- Any schema creation, migration, table/column/trigger change, runtime database write outside the approved API
  operation, requirement-state exposure, player/auth selection, or artificial position insertion.
- Any new endpoint, response field requiring extra history queries, full-history/line/comparison/analysis feature,
  frontend/UI change, dependency, or CORS expansion beyond the approved API methods.
- Any change to safe error status/code boundaries, leakage of database details, destructive replacement, partial
  writes, or lock handling.
- Any need to modify `scripts/opening_catalog`, `data/database/schema.txt`, unrelated worktree content, historical
  records, README navigation, commits, or pushes. Route README maintenance separately if navigation becomes stale.

## Visible result

> A backend client can safely retrieve, set/replace, and remove Skyrocoster's one preferred move for an existing
> game-derived position, with isolated tests proving the append-only lifecycle and no request-time schema creation.
