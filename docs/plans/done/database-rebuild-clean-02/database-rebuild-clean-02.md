# CLEAN-02 game detail - A generated API can replay one rebuilt game by UUID

> **Status:** done - accepted; all three stages complete

- **Read trigger:** whenever CLEAN-02 implementation, validation, repair, or acceptance is approved
- **Upstream:** [database-rebuild-api-direction.md](../../../grilling-docs/database-rebuild-api-direction.md) (settled clean API
  semantics and ownership); [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md) (CLEAN-02 scope,
  sequence, and slice envelope); [database-rebuild-clean-01.md](../../done/database-rebuild-clean-01/database-rebuild-clean-01.md)
  (accepted clean games search, database dependency, generation, proof, and baseline); [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md)
  (focused Plan schema)

## Outcome

Add exactly `GET /api/games/{game_uuid}` with operation ID `getGame`, backed in production only by
`data/database/chess.db`. The operation returns complete normalized game metadata, the original PGN, and every ordered
position occurrence with a full six-field FEN and the outgoing UCI move. The existing explicit-path database reader owns
SQL and FEN/data meaning; the FastAPI feature only translates the path, response models, and status/errors. The curated
OpenAPI contract and checked-in HeyAPI client are updated immediately and remain byte-deterministic.

## Scope

- **Included:**
  - Extending the existing explicit-path game reader under `src/chess_move_trainer/database/games/` and exposing its
    ordinary Python capability through the package namespace.
  - `GET /api/games/{game_uuid}` on the existing clean games router, using the existing rebuilt-database dependency.
  - Focused package proof under `tests/database/games/` and `tests/database/test_package_boundary.py`.
  - Focused HTTP proof under `backend/tests/features/games/`.
  - Adding only the detail operation to the curated exporter, regenerating the checked-in HeyAPI output, exposing the
    generated operation and types through `frontend/src/api/client.ts`, and proving deterministic regeneration.
- **Expected areas:**
  - `src/chess_move_trainer/database/games/reading.py`
  - `src/chess_move_trainer/database/games/__init__.py`
  - `tests/database/games/test_reading.py`
  - `tests/database/games/test_search.py` (existing regression input)
  - `tests/database/test_package_boundary.py`
  - `backend/app/features/games/api_schemas.py`
  - `backend/app/features/games/router.py`
  - `backend/tests/features/games/test_api.py`
  - `scripts/api/export_contract.py`
  - `backend/tests/features/health/test_contract_export.py`
  - `frontend/src/api/client.ts`
  - `frontend/src/api/generatedSurface.test.ts`
  - `frontend/src/api/generated/` (generator-owned output only)
- **Excluded:**
  - Any production database other than `data/database/chess.db`; temporary schema-v1 databases are allowed only for
    focused tests.
  - Tables, columns, indexes, triggers, schema versions, migrations, database lifecycle work, dependencies, or SQL in
    the backend.
  - Any operation other than `GET /api/games/{game_uuid}`; no extra clean operation or later CLEAN slice.
  - Frontend feature imports, production frontend adoption, game-consumer migration, fallback, compatibility adapters,
    legacy route removal, old-database migration, cutover, or cleanup.
  - Changes to health behavior or existing legacy routes, including `/api/games/{game_uuid}/positions`.
  - Lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, complete maintenance
    checks, or any Git operation.

## Contract

### Request

`GET /api/games/{game_uuid}` accepts one required path parameter, `game_uuid`, validated as a UUID. There are no
supported query parameters. Unknown query fields are ignored. A malformed UUID receives FastAPI's standard HTTP 422
request-validation response.

### Response

HTTP 200 returns these fields:

```json
{
  "game_uuid": "uuid",
  "source_url": "https://...",
  "original_pgn": "...",
  "trainer_color": "white",
  "trainer_chesscom_uuid": "uuid",
  "opponent_chesscom_uuid": "uuid",
  "trainer_rating": 1500,
  "opponent_rating": 1490,
  "started_at_utc": "2026-08-01T12:00:00Z",
  "ended_at_utc": "2026-08-01T12:30:00Z",
  "trainer_outcome": "win",
  "termination_reason": "resigned",
  "time_control": "300+5",
  "time_class": "blitz",
  "occurrences": [
    {
      "ply": 0,
      "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
      "move_uci": "e2e4"
    }
  ]
}
```

`opponent_chesscom_uuid`, ratings, times, outcome, termination reason, time control, and time class may be null where
the normalized game has no value. Public identity is `game_uuid`; SQLite `game_id` and `position_id` never appear.

Occurrences are sorted in ascending `ply` order and include the final position. Each `fen` has six legal fields: the
first four are the package's canonical placement, side to move, castling rights, and legal en-passant identity; the
last two are that occurrence's stored halfmove and fullmove counters. `move_uci` is the move leaving the occurrence and
is null only for the final occurrence.

### Errors

- Valid UUID absent from the rebuilt database: HTTP 404, `{"code":"game_not_found","message":"Game not found"}`.
- Missing, incompatible, or unreadable rebuilt data: HTTP 503 with the existing clean `games_unavailable` response.
- Unexpected failure: HTTP 500 with the existing clean `unexpected_failure` response.
- Invalid UUID path input: HTTP 422 through FastAPI request validation.

## Baseline preservation

The worktree contains two distinct kinds of material, both preserved exactly:

- **Unrelated pre-existing baseline:** deleted `data/database/README.md`, `data/database/dump_schema.py`,
  `data/database/schema.md`, and `data/database/schema.txt`; and the modified
  `docs/grilling-docs/database-rebuild-api-direction.md`, including its `chess.db` clarification. These are not
  restored, rewritten, staged, or absorbed.
- **Accepted CLEAN-01 accumulated implementation:** the clean rebuilt-database dependency, game-search package and
  tests, clean games adapter and tests, `backend/app/main.py` router coexistence, curated exporter and contract tests,
  handwritten client, generated HeyAPI directory, generated-surface test, package exports, and package-boundary tests.
  CLEAN-02 extends these surfaces only where named above and preserves the accepted search behavior, health operation,
  generated `getGames`/`getHealth` surface, and all legacy routers. User-owned `Scratch/` and `experiments/` material is
  also outside this Plan and remains untouched.

## Stages

1. **completed** - Package game-detail capability and focused package proof.
2. **completed** - Thin HTTP adapter and focused HTTP proof.
3. **completed** - Curated contract, HeyAPI generation, and deterministic proof.

Stages are sequential; no stage runs in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment.

### Stage 1 - Package game-detail capability and proof

Ordered actions:

1. Extend `GameOccurrenceRead` in `src/chess_move_trainer/database/games/reading.py` with the package-owned full-FEN
   representation assembled from the canonical four fields and the stored occurrence counters. Reuse
   `GameReadRepository.read_by_uuid()` and its explicit `database_path`; do not add a query stack, schema object, or
   database write.
2. Export the game-reading dataclasses, error, repository, and full-FEN capability from
   `src/chess_move_trainer/database/games/__init__.py` without importing FastAPI, Pydantic, or backend modules.
3. Extend `tests/database/games/test_reading.py` and `tests/database/test_package_boundary.py` to prove UUID lookup,
   complete metadata and original PGN, ascending occurrences, six-field FEN counters, final null `move_uci`, explicit
   temporary paths, read-only bytes/no sidecars, and the absence of HTTP/backend ownership. Keep the existing search
   regression in the focused command.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/games/test_reading.py tests/database/games/test_search.py tests/database/test_package_boundary.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the package can read one game through an
explicit path, reconstruct replayable occurrences without changing the database, and preserves CLEAN-01 search and
package-boundary behavior.

Escalation boundary: any schema/table/index/trigger/version change, new dependency, backend import, private-ID response
requirement, changed FEN identity or counter meaning, or inability to reuse the existing reader. Breakpoint: none.

### Stage 2 - Thin FastAPI adapter and proof

Ordered actions:

1. Add strict `GameDetailResponse` and occurrence response models in
   `backend/app/features/games/api_schemas.py`, reusing the clean metadata spelling and error conventions.
2. Add `GET /api/games/{game_uuid}` with `operation_id="getGame"` to
   `backend/app/features/games/router.py`. Use `get_rebuilt_database_path()`, call the package reader by UUID, map
   only path/response/status concerns, and leave `backend/app/main.py` and the legacy positions router unchanged.
3. Map absent games to 404 `game_not_found`, package/schema/storage unavailability to 503 `games_unavailable`, and
   unexpected failures to 500 `unexpected_failure`, without exposing internal exception details.
4. Extend `backend/tests/features/games/test_api.py` to prove the exact response, full FEN counters and final null
   move, UUID validation, unknown-query tolerance, not-found/unavailable/unexpected statuses, private-ID exclusion,
   read-only behavior, the default rebuilt path, and legacy-route registration.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/games -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the clean HTTP operation uses the
rebuilt database dependency, returns the approved detail contract, translates failures safely, and coexists with the
legacy route.

Escalation boundary: any backend SQL, legacy database path, fallback, compatibility adapter, route removal, change to
the approved status/field/FEN semantics, or change to another router. Breakpoint: none.

### Stage 3 - Curated OpenAPI, HeyAPI generation, and deterministic proof

Ordered actions:

1. Add only `"/api/games/{game_uuid}": {"get"}` to `APPROVED_OPERATIONS` in `scripts/api/export_contract.py` and
   retain its fail-closed behavior.
2. Update `backend/tests/features/health/test_contract_export.py` to require exactly the three clean paths
   `/api/health`, `/api/games`, and `/api/games/{game_uuid}`, the operation IDs `getHealth`, `getGames`, and `getGame`,
   only their referenced schemas, deterministic export, and exclusion of the legacy positions route. Served OpenAPI
   must remain full.
3. Update `frontend/src/api/client.ts` to re-export `getGame` and its generated types, and update
   `frontend/src/api/generatedSurface.test.ts` to require exactly the three approved SDK operations and paths. Do not
   edit production frontend feature modules.
4. Run the accepted generator command to update only `frontend/src/api/generated/`; do not hand-edit generated output.
5. Run the focused contract proof, generation, frontend API proof, and generator `--check` in order.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the curated exporter contains exactly
the approved health, collection, and detail operations while served OpenAPI and legacy routes remain available.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This immediately regenerates the checked-in HeyAPI
client from the fresh curated contract without requiring a running backend.

```text
.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000
```

Command-level timeout: 240 seconds. Bash tool timeout: `300000 ms`. This proves the generated surface contains exactly
`getHealth`, `getGames`, and `getGame`, and that no production frontend module adopted the client.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves a second generation is byte-identical
for every checked-in generated file.

Escalation boundary: any additional curated operation, generated output outside `frontend/src/api/generated/`, new
dependency, production frontend import, legacy operation entering the contract, or nondeterministic generation.
Breakpoint: none.

## Retained proof and invalidation

CLEAN-01 is accepted with recorded proof of 20 package tests, 9 games HTTP tests, 4 contract-export tests, 4 frontend
API tests, and byte-identical regeneration of 17 generated files. CLEAN-02 changes the games package reader/export
surface and package tests, so the package proof is re-established in Stage 1. It changes the games adapter and HTTP
tests, so the games HTTP proof is re-established in Stage 2. It changes the curated exporter, contract test, handwritten
client, generated-surface test, and generated files, so the contract, frontend surface, generation, and `--check` proof
are re-established in Stage 3. The accepted CLEAN-01 results remain historical evidence and are not rewritten; unaffected
health behavior and legacy-route coexistence remain preserved and are covered by the focused reruns where their inputs
are touched.

## Progress and decisions

- **Stage 1:** completed - from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/games/test_reading.py tests/database/games/test_search.py tests/database/test_package_boundary.py -q`
  passed `22` tests in `1.95s` with a 180-second command timeout and `240000 ms` Bash tool timeout. It re-established
  the affected CLEAN-01 package proof while proving full occurrence FEN counters, ordered replay data, the final null
  move, explicit-path read-only behavior, schema compatibility, private-ID exclusion, and the package boundary;
  breakpoint: none.
- **Stage 2:** completed - from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/games -q`
  passed `12` tests in `78.05s` with a 180-second command timeout and `240000 ms` Bash tool timeout. It re-established
  the affected CLEAN-01 HTTP evidence while proving the clean detail route, full replay FENs, error translation,
  rebuilt-path default, read-only behavior, private-ID exclusion, and coexistence with the collection and legacy route;
  breakpoint: none.
- **Stage 3:** completed - from `G:\ChessMoveTrainer`, the focused exporter pytest passed `4` tests in `4.66s` after
  correcting the in-scope exact schema expectation; generation completed for `17` generated files; the focused API
  Vitest run passed `3` files and `4` tests in `2.90s` after one transient uvicorn-startup retry; and generator
  `--check` proved byte-identical regeneration of all `17` files. The commands used the Plan's explicit 180/240-second
  command wrappers and `240000`/`300000 ms` Bash tool timeouts. Package and HTTP proof remained valid because Stage 3
  changed none of their inputs; breakpoint: none.
- **Database decision:** production reads use only `data/database/chess.db`; the existing clean environment override
  remains the bounded test/deployment seam and never changes legacy behavior.
- **Schema decision:** accepted schema version 1 is used as-is. The unique game UUID, occurrence primary key, existing
  joins, and existing indexes are sufficient; no database object is added.
- **Ownership decision:** package code owns SQL, FEN reconstruction, canonical data meaning, and explicit paths;
  backend code owns HTTP translation only; generated output remains generator-owned.

## Proof

- Package capability, explicit-path behavior, full-FEN occurrence reconstruction, read-only behavior, and CLEAN-01
  package regression: Stage 1 finite pytest command.
- Detail HTTP response, status mapping, rebuilt-path dependency, unknown-query tolerance, read-only behavior, and legacy
  coexistence: Stage 2 finite pytest command.
- Three-operation curated contract and served-route boundary: Stage 3 contract-export pytest command.
- Checked-in HeyAPI surface and no production adoption: Stage 3 focused Vitest command.
- Byte-identical regeneration: Stage 3 generator `--check` command.

No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, or complete maintenance
proof is part of this implementation Plan.

## Acceptance

- `GET /api/games/{game_uuid}` returns complete metadata, the original PGN, and ordered replayable occurrences from the
  rebuilt database.
- Occurrences expose full six-field FENs with occurrence-specific counters, outgoing UCI moves, and a final null move;
  no private SQLite identifiers escape.
- Invalid UUIDs return 422, absent games return the typed 404, unavailable rebuilt data returns 503, and unexpected
  failures return safe 500 responses.
- Unknown query fields are ignored, the clean dependency targets `data/database/chess.db`, reads do not create or alter
  database files, and the legacy positions route remains registered.
- The curated OpenAPI contract contains exactly `/api/health`, `/api/games`, and `/api/games/{game_uuid}`; generated
  HeyAPI exposes exactly `getHealth`, `getGames`, and `getGame`; deterministic `--check` passes.
- No production frontend module adopts the generated client, no schema or dependency changes occur, and CLEAN-01 health,
  search, generation, and legacy behavior remain intact.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, or acceptance decision.
- Any schema/index/version change, new SQL owner, FEN/counter semantic change, private-ID exposure, or inability to use
  the accepted schema-v1 reader.
- Any use of `data/database/chess_games.db`, legacy fallback, migration, physical cutover, or cleanup.
- Any legacy route removal, compatibility adapter, frontend consumer adoption, later CLEAN operation, additional curated
  operation, generated artifact outside the approved directory, commit, push, branch, worktree, stash, or other Git
  operation.

## Visible result

> A user can open one rebuilt training game by UUID, see its original PGN and replayable ordered positions, while the
> generated client exposes `getGame()` beside the accepted clean operations and regeneration remains byte-for-byte stable.
