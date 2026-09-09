# CLEAN-01 games search - A generated API can search the rebuilt games database

> **Status:** done - accepted; Stages 1 through 3 complete

- **Read trigger:** whenever CLEAN-01 implementation, validation, repair, or acceptance is approved
- **Upstream:** [database-rebuild-api-direction.md](../../../grilling-docs/database-rebuild-api-direction.md) (settled API
  semantics and ownership); [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md) (CLEAN-01
  scope and slice envelope); [database-rebuild-setup-02.md](../../done/database-rebuild-setup-02/database-rebuild-setup-02.md)
  (accepted curated exporter, HeyAPI generator, central client, and proof seams)

## Outcome

Add exactly `GET /api/games`, backed by the rebuilt SQLite database at `data/database/chess.db`. It provides one
reusable, rich, paginated game search whose filters can be combined, while the rebuilt database package owns SQL,
canonical chess handling, filtering, aggregation, and deterministic ordering. The FastAPI layer only translates HTTP
parameters, response models, and errors. The operation is added to the curated OpenAPI contract and the checked-in
HeyAPI client is regenerated and proven deterministic.

The result is a summary collection, not a game timeline. Each summary contains normalized game metadata, the selected
deepest opening classification, game length, and useful analysis/preferred-move coverage counts. Internal SQLite game,
position, opening, and route IDs never appear in the response.

## Scope

- **Included:**
  - A package-owned, explicit-path game-search capability under `src/chess_move_trainer/database/games/`.
  - A clean backend database-path dependency whose default is the package-owned
    `data/database/chess.db` path. The clean route never imports the legacy positions repository path provider.
  - `GET /api/games` with the approved combined filters, finite pagination, deterministic sorts, rich summaries, and
    typed HTTP error translation.
  - Focused package tests under `tests/database/games/` and focused HTTP tests under
    `backend/tests/features/games/`.
  - Addition of only `/api/games` to the curated exporter, checked-in HeyAPI regeneration, and byte-identical
    generation proof.
  - Updating the handwritten generated-client export and generated-surface tests without production adoption.
- **Expected areas:**
  - `src/chess_move_trainer/database/games/`
  - `src/chess_move_trainer/database/openings/`
  - `tests/database/games/`
  - `tests/database/test_package_boundary.py`
  - `backend/app/dependencies.py`
  - `backend/app/features/games/`
  - `backend/app/main.py`
  - `backend/tests/features/games/`
  - `scripts/api/export_contract.py`
  - `backend/tests/features/health/test_contract_export.py`
  - `frontend/src/api/client.ts`
  - `frontend/src/api/generatedSurface.test.ts`
  - `frontend/src/api/generated/` (generator-owned output only)
- **Excluded:**
  - Any database other than `data/database/chess.db` in production behavior; in tests, only temporary schema-v1
    databases and the rebuilt target are allowed.
  - Schema, table, index, trigger, or schema-version changes.
  - Backend SQL, SQLite connections, or chess/filter aggregation in the FastAPI feature.
  - Full game timelines, PGN detail, game-detail routes, openings collection/detail, position insight, analysis, or
    preferred-move operations.
  - Production frontend imports, consumer migration, legacy route removal, legacy database migration/fallback, or
    compatibility adapters.
  - Database lifecycle commands, Stockfish, new dependencies, `/api/v2`, generic query languages, broad refactors,
    lint, formatting, broad type/build, source-size, aggregate, hygiene, Quality, complete test/fix, commits, pushes,
    branches, worktrees, and stashes.

## Approved HTTP contract

### Request

`GET /api/games` accepts these query parameters. Omitted filters do not constrain the result.

- `page`: positive integer, default `1`.
- `page_size`: integer from `1` through `100`, default `50`.
- `started_at_from`, `started_at_to`, `ended_at_from`, `ended_at_to`: inclusive RFC3339 UTC timestamp bounds.
- `trainer_color`: `white` or `black`.
- `trainer_outcome`: `win`, `loss`, or `draw`.
- `termination_reason`: non-empty reason, matched case-insensitively and exactly after trimming.
- `trainer_rating_min`, `trainer_rating_max`, `opponent_rating_min`, `opponent_rating_max`: non-negative integer
  bounds; a missing rating does not match a rating bound.
- `opponent_chesscom_uuid`: exact public opponent identity.
- `time_class`: `bullet`, `blitz`, `rapid`, or `daily`.
- `time_control`: exact normalized `dg_time_control_source` value.
- `opening_key`: stable API key formatted as `ECO:Name`.
- `opening_match`: required together with `opening_key`; `reached` means the game reached that opening at any
  occurrence, while `deepest` means it is the deterministic deepest opening classification for the game.
- `contains_fen`: complete legal six-field FEN, canonicalized before matching any stored occurrence.
- `move_fen`: complete legal six-field FEN identifying the parent position.
- `move_uci`: required together with `move_fen`; it must be legal from the canonical parent position and match the
  stored outgoing move from that position.
- `min_length_plies`, `max_length_plies`: inclusive game-length bounds.
- `analysis_coverage`: `none`, `partial`, or `complete`.
- `preferred_coverage`: `none`, `partial`, or `complete`.
- `sort`: `started_at_desc` by default, or `started_at_asc`, `length_desc`, `length_asc`, `trainer_rating_desc`,
  `trainer_rating_asc`, `opponent_rating_desc`, `opponent_rating_asc`, `opponent_uuid_asc`, `opponent_uuid_desc`,
  `game_uuid_asc`, or `game_uuid_desc`.

Opening-key construction is reusable and does not contain a private opening ID. For deepest selection, the greatest
matched ply wins; ties use the lexicographically smallest API key. Null values sort last, and non-UUID sorts use
`game_uuid ASC` as the final tie-breaker. Unknown query fields are ignored. Known invalid values or combinations are
rejected. Invalid bound ordering, incomplete `opening_key`/`opening_match`, incomplete `move_fen`/`move_uci`, invalid
FEN, and illegal outgoing moves are invalid combinations or values.

### Response

HTTP 200 returns:

```json
{
  "items": [
    {
      "game_uuid": "uuid",
      "source_url": "https://...",
      "trainer_color": "white",
      "trainer_chesscom_uuid": "uuid",
      "opponent_chesscom_uuid": "uuid",
      "trainer_rating": 1063,
      "opponent_rating": 1200,
      "started_at_utc": "2026-01-01T12:00:00Z",
      "ended_at_utc": "2026-01-01T12:30:00Z",
      "trainer_outcome": "win",
      "termination_reason": "resigned",
      "time_control": "600+5",
      "time_class": "rapid",
      "occurrence_count": 61,
      "length_plies": 60,
      "deepest_opening": {
        "key": "C20:King's Pawn Game",
        "eco": "C20",
        "name": "King's Pawn Game",
        "ply": 8
      },
      "coverage": {
        "distinct_position_count": 60,
        "analyzed_position_count": 1,
        "preferred_position_count": 4,
        "analysis_coverage": "partial",
        "preferred_coverage": "partial"
      }
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 12710,
  "total_pages": 255,
  "has_next": true
}
```

`occurrence_count` includes the final position and `length_plies` is the greatest stored ply. Coverage is calculated
over distinct canonical positions in the game: an analysis result or at least one preferred period makes that
position covered. A zero-result page is valid and returns an empty `items` list; a page beyond the end is not a 404.
The collection does not return PGN, occurrences, timelines, SQLite IDs, opening IDs, or route IDs.

### Errors

The adapter translates package validation failures to HTTP 422 with `GamesErrorResponse` code `invalid_filter` and
does not expose internal exception details. Missing or incompatible rebuilt data returns HTTP 503 with code
`games_unavailable`. Unexpected failures return HTTP 500 with code `unexpected_failure`. Primitive values that cannot
be coerced by FastAPI may use its standard request-validation response; domain values and combinations are handled by
the typed games error response. There is no collection-level 404.

## Baseline preservation

The assessment found these pre-existing unrelated changes. They are historical/user-owned baseline and must be
preserved exactly; this Plan does not authorize restoring, rewriting, staging, or absorbing them:

- deleted `data/database/README.md`;
- deleted `data/database/dump_schema.py`;
- deleted `data/database/schema.md`;
- deleted `data/database/schema.txt`;
- modified `docs/grilling-docs/database-rebuild-api-direction.md`, including the appended `(THIS IS chess.db)`
  clarification.

The accepted SETUP-02 files and generated health client are retained evidence. Only generator-owned files changed by
the CLEAN-01 contract are expected to change during Stage 3. The legacy `backend/app/features/positions/` path and
routes remain untouched.

## Stages

1. **complete** - Package game-search capability and focused package proof.
2. **complete** - Thin FastAPI adapter and focused HTTP proof.
3. **complete** - Curated contract plus generated HeyAPI output and focused deterministic proof.

Stages are sequential; no stage runs in parallel. A passing proof remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment.

### Stage 1 - Package game-search capability and proof

Ordered actions:

1. Add a reusable opening API-key helper under `src/chess_move_trainer/database/openings/` using the approved
   `ECO:Name` representation, without adding schema data or exposing database IDs.
2. Add the package-owned game-search capability under `src/chess_move_trainer/database/games/`, with an explicit
   `database_path` constructor or argument and ordinary Python dataclasses for the query, summaries, coverage, page,
   and package errors.
3. Keep SQL, canonical FEN handling, legal outgoing-move validation, opening reached/deepest aggregation, coverage
   calculation, bound validation, pagination, and deterministic sort/tie/null behavior in the package. Use the
   existing read-only connection and schema-compatibility seams. Do not add an index or other schema object.
4. Export the capability from the games package as appropriate and add focused tests using temporary schema-v1
   databases. Cover every filter family, combined filters, pagination limits, deterministic repeated reads, summary
   shape/private-ID exclusion, read-only bytes/sidecar behavior, and the package boundary.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py tests/database/games/test_reading.py tests/database/test_package_boundary.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the new package capability works
against explicit temporary paths, preserves the existing game reader, remains outside backend/HTTP ownership, and
does not mutate the database or schema.

Escalation boundary: any need for a new table, column, index, trigger, schema version, private-ID response field, or
different filter meaning. Breakpoint: none.

### Stage 2 - Thin FastAPI adapter and proof

Ordered actions:

1. Add `backend/app/dependencies.py` with `REBUILT_DATABASE_PATH_ENV = "CHESS_REBUILT_DATABASE_PATH"` and
   `get_rebuilt_database_path()`, defaulting to
   `chess_move_trainer.database.lifecycle.DEFAULT_DATABASE_PATH`. This is the clean path seam; do not import or
   modify `backend.app.features.positions.repository.database_path()` and do not use its `chess_games.db` default.
2. Add `backend/app/features/games/` response and error models with strict extra-field behavior and a thin router
   registered from `backend/app/main.py`. Set `operation_id="getGames"` and preserve all existing routers, including
   the legacy whole-game positions route.
3. Translate typed query parameters into the package capability and package errors into the approved 422/503/500
   responses. Keep all SQL, SQLite access, chess validation, and aggregation out of the backend feature.
4. Add focused HTTP fixtures and tests using temporary schema-v1 rebuilt databases plus a bounded request against the
   default `data/database/chess.db`. Prove unknown query fields are ignored, invalid combinations are rejected,
   summaries contain no private IDs, reads create no SQLite sidecars or data changes, the default clean dependency is
   the rebuilt path, and the legacy route remains registered rather than removed.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/games -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the HTTP operation reads the rebuilt
database through the clean dependency, presents the approved contract, translates failures safely, and coexists with
legacy routes without adopting or removing them.

Escalation boundary: any backend SQL, use of the legacy database seam, change to another router, legacy-route removal,
fallback, compatibility adapter, or change to the approved HTTP semantics. Breakpoint: none.

### Stage 3 - Curated OpenAPI, HeyAPI generation, and deterministic proof

Ordered actions:

1. Add only `"/api/games": {"get"}` to `scripts/api/export_contract.py` and generalize health-only wording or helper
   names only as needed to describe the now-approved health-plus-games contract. Keep the exporter fail-closed.
2. Update `backend/tests/features/health/test_contract_export.py` to assert that the curated contract contains exactly
   `/api/health` and `/api/games`, retains `getHealth` and `getGames`, includes only their referenced schemas, remains
   deterministic, and excludes the legacy game-position path. Served OpenAPI remains full; only the new clean route is
   added to it.
3. Update `frontend/src/api/client.ts` to re-export `getGames` and its generated types, and update
   `frontend/src/api/generatedSurface.test.ts` to require exactly `getHealth` and `getGames` and exactly the two
   curated paths. Do not edit production frontend feature modules.
4. Run the accepted generator command to update only `frontend/src/api/generated/`; do not hand-edit generated output.
5. Run the focused backend contract proof, frontend API tests, and generator `--check` proof below in order.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the curated exporter includes the
new operation while preserving the health operation, full served routes, and docs boundary.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This regenerates the checked-in HeyAPI output from
the fresh curated contract without requiring a running backend.

```text
.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000
```

Command-level timeout: 240 seconds. Bash tool timeout: `300000 ms`. This proves the generated surface contains exactly
the two approved SDK operations and that no production frontend module adopted the generated client.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves a second generation is byte-identical
for every checked-in generated file.

Escalation boundary: any additional curated operation, generated output outside `frontend/src/api/generated/`, new
dependency, production frontend import, legacy operation entering the contract, or non-deterministic generation.
Breakpoint: none.

## Progress and decisions

- **Stage 1:** complete - proof: `scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/games/test_search.py tests/database/games/test_reading.py tests/database/test_package_boundary.py -q` — 20 passed; breakpoint: none.
- **Stage 2:** complete - proof: `scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/games -q` — 9 passed; breakpoint: none.
- **Stage 3:** complete - proof: contract export `4 passed`; generation completed; API surface `4 passed`; `--check` byte-identical for 17 files; breakpoint: none.
- **Baseline decision:** preserve the unrelated deletions and grilling-document edit listed above exactly.
- **Database decision:** all clean behavior uses `data/database/chess.db`; the dedicated clean environment override is
  `CHESS_REBUILT_DATABASE_PATH` for bounded tests or deployment configuration and never changes legacy behavior.
- **Schema decision:** use accepted schema version 1 as-is; no search index or schema amendment is authorized.

## Proof

- Package behavior and boundary: the Stage 1 finite pytest command — 20 passed.
- Clean rebuilt-path HTTP behavior, combined filters, pagination, errors, read-only behavior, and legacy coexistence:
  the Stage 2 finite pytest command — 9 passed.
- Curated contract and served-route boundary: the Stage 3 focused backend pytest command — 4 passed.
- Checked-in generated HeyAPI surface and no production adoption: the Stage 3 focused Vitest command — 4 passed.
- Byte-identical regeneration: the Stage 3 generator `--check` command — 17 files unchanged.

No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, or complete maintenance
proof is part of this implementation Plan.

## Acceptance

- `GET /api/games` returns deterministic rich summaries from the rebuilt `data/database/chess.db`.
- Every approved filter family combines correctly, including opening reached/deepest, canonical FEN, outgoing move,
  length, analysis, and preferred coverage.
- Pagination is finite; sorting handles nulls and ties deterministically.
- No private SQLite identifiers or full timelines escape.
- Package tests prove explicit-path operation, schema-v1 compatibility, read-only behavior, and package ownership of
  SQL/chess/filter/aggregation semantics.
- HTTP tests prove the clean rebuilt path, typed error translation, unknown-field tolerance, and legacy coexistence.
- The curated OpenAPI contract contains exactly `/api/health` and `/api/games`; legacy routes remain outside it.
- Checked-in HeyAPI exposes exactly `getHealth` and `getGames`, and deterministic `--check` passes.
- No production frontend module adopts the generated client.

## Escalation boundaries

- Any new product, visual, API, data, dependency, destructive, ownership, or acceptance decision.
- Any schema/index/version change or inability to express a required filter using accepted schema version 1.
- Any use of `data/database/chess_games.db`, the legacy path provider, old-database fallback, migration, or cutover.
- Any change to settled field names, defaults, limits, opening meanings, coverage meanings, canonical FEN behavior,
  outgoing-move pair, sort/tie/null rules, error translation, or private-identity policy.
- Any legacy route removal, compatibility adapter, production frontend adoption, or later CLEAN operation.
- Any new dependency or generated artifact outside the approved paths.

## Visible result

> A user can request a filtered, paginated list of training games from the rebuilt database, while the generated client
> exposes `getGames()` beside `getHealth()` and regeneration remains byte-for-byte stable.
