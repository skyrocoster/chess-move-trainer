# CLEAN-04 opening detail - A generated API can inspect one rebuilt opening

> **Status:** done - accepted; all three stages complete

- **Read trigger:** whenever CLEAN-04 implementation, validation, repair, or acceptance is approved
- **Upstream:** [database-rebuild-api-direction.md](../../../grilling-docs/database-rebuild-api-direction.md) (settled API
  semantics and ownership); [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md) (CLEAN-04
  scope, sequence, and slice envelope); [database-rebuild-clean-01.md](../../done/database-rebuild-clean-01/database-rebuild-clean-01.md)
  (accepted opening-key/game-filter behavior, clean database dependency, generation, and proof);
  [database-rebuild-clean-02.md](../../done/database-rebuild-clean-02/database-rebuild-clean-02.md) (accepted clean
  operation coexistence, generation, and retained proof); [database-rebuild-clean-03.md](../../done/database-rebuild-clean-03/database-rebuild-clean-03.md)
  (accepted opening catalogue key and aggregation behavior, router, generation, and proof); [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md)
  (focused Plan schema)

## Outcome

Add exactly `GET /api/openings/{opening_key}`, with operation ID `getOpeningByKey`, backed in production only by
`data/database/chess.db`. It returns one flat opening item using the existing six-field catalogue shape: reusable public
key, ECO, name, route count, distinct games reached, and distinct games deepest. The package owns key parsing, SQL, and
aggregation; the FastAPI layer remains a thin HTTP adapter. The operation is added immediately to the curated OpenAPI
contract and the checked-in HeyAPI client is regenerated and proven deterministic.

## Scope

- **Included:**
  - An explicit-path, read-only package detail read under `src/chess_move_trainer/database/openings/`, reusing the
    existing catalogue entry and reached/deepest aggregation.
  - `GET /api/openings/{opening_key}` on the existing openings router, after both existing literal opening routes.
  - Typed malformed-key, not-found, unavailable, and unexpected-failure HTTP responses.
  - Focused package, HTTP, curated-contract, generated-surface, and deterministic-generation proof.
  - Addition of only the detail operation to the curated exporter and immediate HeyAPI regeneration.
- **Expected areas:**
  - `src/chess_move_trainer/database/openings/catalogue.py`
  - `src/chess_move_trainer/database/openings/__init__.py`
  - `tests/database/openings/test_catalogue.py`
  - `tests/database/test_package_boundary.py`
  - `backend/app/features/openings/catalogue_api_schemas.py`
  - `backend/app/features/openings/router.py`
  - `backend/tests/features/openings/test_catalogue_api.py`
  - `backend/tests/features/health/test_contract_export.py`
  - `scripts/api/export_contract.py`
  - `frontend/src/api/client.ts`
  - `frontend/src/api/generatedSurface.test.ts`
  - `frontend/src/api/generated/` (generator-owned output only)
- **Excluded:**
  - Any production database other than `data/database/chess.db`; temporary schema-v1 databases are allowed only for
    focused tests.
  - Tables, columns, indexes, triggers, schema versions, migrations, dependencies, database lifecycle work, or a new
    SQL owner.
  - Backend SQL, route moves, route details, hierarchy/tree data, Opening Line Library behavior, or private SQLite IDs.
  - Changes to `/api/openings/line-library`, other legacy routes, legacy configuration, fallback, migration, cutover,
    or compatibility adapters.
  - Frontend production imports or consumer adoption, CLEAN-05 and later, broad refactors, lint, formatting, broad
    type/build, source-size, aggregate, repository-hygiene, Quality, complete maintenance checks, or Git operations.

## Contract

### Request

`GET /api/openings/{opening_key}` accepts one required string path parameter. It is the exact reusable `ECO:Name`
value produced by `opening_api_key()` and used by CLEAN-01 filters and the CLEAN-03 catalogue. There are no supported
query parameters; unknown query fields are ignored.

The current target contains no slash-containing labels. Current keys with spaces, colons, apostrophes, plus signs, and
Unicode are supported by percent-encoding the complete path segment. For example:

- `A00:Amar Opening` becomes `/api/openings/A00%3AAmar%20Opening`.
- `C20:King's Pawn Game` becomes `/api/openings/C20%3AKing%27s%20Pawn%20Game`.
- `A09:Réti Opening` becomes `/api/openings/A09%3AR%C3%A9ti%20Opening`.

The generated HeyAPI runtime already applies `encodeURIComponent()` to string path parameters. A raw `?` or `#` is a
URL delimiter and must be encoded as `%3F` or `%23`; `%` must be `%25`, `+` should be `%2B`, and `/` would be `%2F`.
This transport encoding does not change the public key returned in JSON or used by CLEAN-01/CLEAN-03.

Malformed key syntax, such as `not-a-key`, `A0:Alpha`, or `A00:`, returns HTTP 422:

```json
{"code":"invalid_opening_key","message":"Invalid opening key"}
```

A request without a detail path segment is not a detail request: `/api/openings` remains the existing collection route.
The framework's unmatched-path behavior is not redefined by this operation.

### Response

HTTP 200 reuses the existing `OpeningCatalogueItemResponse` shape and contains exactly these public fields:

```json
{
  "key": "A00:Amar Opening",
  "eco": "A00",
  "name": "Amar Opening",
  "route_count": 1,
  "games_reached": 1,
  "games_deepest": 1
}
```

`route_count` counts persisted routes for the label. `games_reached` counts distinct games with any stored occurrence
matching any route endpoint. `games_deepest` counts distinct games for which the label wins CLEAN-01/CLEAN-03 deepest
selection: greatest matched ply wins, with the lexicographically smallest public key breaking equal-depth ties. Multiple
routes or repeated occurrences never inflate distinct-game counts. The response contains no route moves, route IDs,
hierarchy, tree, or private database identifiers.

### Errors

- A syntactically valid key absent from readable rebuilt data returns HTTP 404:
  `{"code":"opening_not_found","message":"Opening not found"}`.
- Missing, incompatible, unreadable, malformed, or colliding rebuilt data returns HTTP 503 with the existing
  `openings_unavailable` error and message `Openings unavailable`.
- Unexpected failures return HTTP 500 with `unexpected_failure` and message `Unable to load opening`.
- Primitive/path parsing failures not handled as package key validation may use FastAPI's standard 422 response.

The literal `/api/openings/line-library` route remains registered and unchanged, including its legacy behavior and
exclusion from the curated contract. Because Starlette route matching is ordered, the dynamic route is registered after
`/api/openings` and `/api/openings/line-library`. Any future one-segment static opening route must likewise precede the
dynamic route; no future route is added by this Plan.

## Repository and route decisions

- Add a package-level `read_opening(database_path, opening_key) -> OpeningCatalogueEntry | None` capability and export
  it from the openings package. Keep the existing `OpeningCatalogueEntry`; do not create a second detail aggregate or
  response shape.
- Parse the key inside the package with `parse_opening_api_key()`, translating malformed input to the package validation
  boundary. The backend does not parse keys or own SQL.
- Reuse the catalogue reader's existing label loading, collision detection, route-count query, usage query, deepest
  tie-break, and entry construction. A valid absent key returns `None`; persisted malformed labels or collisions remain
  storage failures.
- Use the existing explicit-path read-only connection and schema-v1 compatibility checks. Do not read
  `derived_opening_route_move`.
- Add the route only to `backend/app/features/openings/router.py`, after both literal routes. `backend/app/main.py` is
  unchanged because the router is already mounted.
- Reuse `OpeningCatalogueItemResponse` for success and add detail-specific error typing without changing the accepted
  collection error contract.
- Add only `"/api/openings/{opening_key}": {"get"}` to `scripts/api/export_contract.py`. The curated contract and
  generated surface therefore grow from four to exactly five clean operations.
- The current key helper accepts arbitrary non-empty name characters, but the rebuilt target has zero slash-containing
  labels. A normal one-segment route is sufficient for all current keys. A future persisted slash requires escalation;
  this Plan does not change key semantics or introduce a greedy path converter.

## Baseline preservation

The accepted baseline includes unrelated deletions of `data/database/README.md`, `data/database/dump_schema.py`,
`data/database/schema.md`, and `data/database/schema.txt`, plus the modified
`docs/grilling-docs/database-rebuild-api-direction.md`, including its `chess.db` clarification. These records are
preserved exactly and are not restored, rewritten, or absorbed. The master-plan header's older next-selectable label is
also not cleaned up; its CLEAN-04 inventory/slice row and this approved Plan govern the work.

CLEAN-01 through CLEAN-03 are accepted accumulated implementation. Their clean rebuilt-database dependency, games
search/detail capabilities, opening catalogue, accepted generated operations, package-boundary proof, HTTP adapters,
legacy routers, exporter, handwritten client, and generated output remain in place. The production target remains only
`data/database/chess.db`; no old database is read or changed.

The accepted rebuilt-data baseline is 12,710 games, 530,725 canonical positions, 657,654 occurrences, 3,329 opening
labels, 3,810 opening routes, and 36,925 route moves. This Plan does not rebuild or modify that database.

## Stages

1. **completed** - Package opening-detail capability and focused package proof.
2. **completed** - Thin FastAPI detail adapter and focused HTTP/coexistence proof.
3. **completed** - Curated contract, HeyAPI generation, and deterministic proof.

Stages are sequential; no stage runs in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment.

### Stage 1 - Package opening-detail capability and proof

Ordered actions:

1. Extend `src/chess_move_trainer/database/openings/catalogue.py` with the explicit-path `read_opening` capability,
   reusing `OpeningCatalogueEntry`, existing key parsing, label/collision loading, usage aggregation, and deterministic
   deepest selection.
2. Export the capability from `src/chess_move_trainer/database/openings/__init__.py` without importing backend, FastAPI,
   or HTTP models.
3. Extend `tests/database/openings/test_catalogue.py` and `tests/database/test_package_boundary.py` to prove exact
   detail fields, equality with the catalogue aggregate, encoded-safe current-key fixtures, valid absent and malformed
   keys, explicit temporary paths, schema-v1 failures, unchanged bytes, no sidecars, and package ownership.

Proof, from working directory `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/openings/test_catalogue.py tests/database/test_package_boundary.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the detail read uses the accepted
package path, key, SQL, and aggregation seams without changing the existing catalogue meaning or database.

Escalation boundary: any schema/table/index/trigger/version change, new dependency, backend import, private-ID output,
second aggregate meaning, or inability to reuse schema-v1 catalogue reads. Breakpoint: none.

### Stage 2 - Thin FastAPI adapter and proof

Ordered actions:

1. Extend `backend/app/features/openings/catalogue_api_schemas.py` with strict detail error typing while reusing the
   existing six-field success model.
2. Add `GET /api/openings/{opening_key}` with `operation_id="getOpeningByKey"` to the existing openings router after
   `/openings` and `/openings/line-library`. Use `get_rebuilt_database_path()` and the package capability only.
3. Translate package validation to the typed 422, `None` to the typed 404, schema/storage failures to the typed 503,
   and unexpected failures to the safe typed 500. Leave the collection and legacy Line Library behavior unchanged.
4. Extend `backend/tests/features/openings/test_catalogue_api.py` to prove exact response shape and counts, current
   percent-encoded keys, malformed/absent/unavailable/unexpected cases, unknown-query tolerance, default rebuilt path,
   private-ID exclusion, read-only behavior, route ordering, and literal Line Library registration.

Proof, from working directory `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/openings backend/tests/features/games -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the detail adapter uses the rebuilt
dependency, preserves accepted games routes, and keeps the legacy opening route separate and registered.

Escalation boundary: backend SQL, legacy database use, fallback, compatibility adapter, route removal or relocation,
changed collection/detail fields, changed reached/deepest meanings, or a router conflict that cannot preserve the
literal Line Library route. Breakpoint: none.

### Stage 3 - Curated contract, HeyAPI generation, and deterministic proof

Ordered actions:

1. Add only `"/api/openings/{opening_key}": {"get"}` to `APPROVED_OPERATIONS` in
   `scripts/api/export_contract.py`; retain fail-closed export behavior.
2. Update `backend/tests/features/health/test_contract_export.py` to require exactly the five clean paths
   `/api/health`, `/api/games`, `/api/games/{game_uuid}`, `/api/openings`, and `/api/openings/{opening_key}`, with
   operation IDs `getHealth`, `getGames`, `getGame`, `getOpenings`, and `getOpeningByKey`. Require only referenced
   schemas, deterministic export, full served OpenAPI, and exclusion of `/api/openings/line-library`.
3. Update `frontend/src/api/client.ts` to re-export `getOpeningByKey` and its generated types, and update
   `frontend/src/api/generatedSurface.test.ts` to require exactly the five clean operations and paths. Do not edit
   production frontend feature modules or add handwritten URL encoding.
4. Run the accepted generator using `.venv/Scripts/python.exe scripts/api/generate_client.py`; update only
   `frontend/src/api/generated/`.
5. Run the focused contract proof, generation, generated-surface proof, and deterministic `--check` in order.

Proof, from working directory `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000
```

Command-level timeout: 240 seconds. Bash tool timeout: `300000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. These checks prove the new operation is curated and
generated immediately, all accepted clean operations remain present, legacy operations remain uncurated, and generation
is byte-identical on the second run.

Escalation boundary: any additional curated operation, generated output outside `frontend/src/api/generated/`, new
dependency, production frontend import, legacy operation entering the contract, non-deterministic generation, or
generator behavior requiring a handwritten encoding change. Breakpoint: none.

## Retained proof and invalidation

CLEAN-03 is accepted with recorded proof of 42 package tests, 47 openings/games HTTP tests, 4 contract-export tests, 4
focused API Vitest tests, and byte-identical regeneration of 17 generated files. CLEAN-01 and CLEAN-02 remain accepted
historical evidence with their package, HTTP, contract, generated-surface, and deterministic-generation proof.

Stage 1 changes the catalogue package and package exports, so the CLEAN-03 package/catalogue and package-boundary proof
is re-established. The CLEAN-01 games search code and key helper are not changed, so its unaffected package proof remains
retained.

Stage 2 changes the openings adapter and route, so the CLEAN-03 openings HTTP and legacy-coexistence evidence is
re-established. The combined openings/games command also re-establishes accepted CLEAN-01/CLEAN-02 games HTTP behavior.
The legacy Line Library implementation and data contract remain unchanged.

Stage 3 changes the curated exporter, contract assertions, handwritten client, generated-surface assertions, and
generator-owned output. It therefore re-establishes contract, generated-surface, generation, and `--check` proof for all
five clean operations. Stage 3 does not change package or backend behavior, so passing Stage 1 and Stage 2 proof remains
valid after it. Any later change to the database input, affected configuration, dependencies, or exercised behavior
invalidates the corresponding proof and requires a focused rerun.

## Progress and decisions

- **Stage 1:** completed - from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/openings/test_catalogue.py tests/database/test_package_boundary.py -q`
  passed `32` tests in `2.06s` with a 180-second command timeout and `240000 ms` Bash tool timeout after correcting one
  in-scope test index assertion. It proves exact flat detail values, shared catalogue aggregation, colon/Unicode keys,
  absent and malformed keys, explicit paths, read-only/no-sidecar behavior, schema handling, and package ownership;
  breakpoint: none.
- **Stage 2:** completed - from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/openings backend/tests/features/games -q`
  passed `53` tests in `79.73s` with a 180-second command timeout and `240000 ms` Bash tool timeout. It proves encoded
  current keys, exact detail values, typed 422/404/503/500 handling, unknown-query tolerance, default rebuilt-database
  access, read-only/private-ID behavior, literal Line Library precedence, and accepted games-route coexistence. Stage 1
  proof remained valid because package inputs were unchanged; breakpoint: none.
- **Stage 3:** completed - from `G:\ChessMoveTrainer`, the focused contract-export pytest passed `4` tests in `4.47s`;
  generation completed for `17` checked-in generated files; the focused API Vitest run passed `3` files and `4` tests
  in `1.63s`; and generator `--check` proved byte-identical regeneration of all `17` files. Commands used the Plan's
  explicit 180/240-second command wrappers and `240000`/`300000 ms` Bash tool timeouts. Stage 1 and Stage 2 proof
  remained valid because this stage changed no package or backend behavior; breakpoint: none.
- **Database decision:** production reads target only `data/database/chess.db`; the existing
  `CHESS_REBUILT_DATABASE_PATH` seam remains for bounded tests/deployment configuration and never changes legacy
  behavior.
- **Key decision:** retain the exact `ECO:Name` key. All current target keys are representable as percent-encoded
  single path segments. Slash-containing future data is an escalation boundary, not new behavior in CLEAN-04.
- **Schema decision:** accepted schema version 1 is used as-is; no schema object or dependency is added.
- **Ownership decision:** the package owns parsing, SQL, aggregation, and explicit paths; the backend owns HTTP
  translation; generated output remains generator-owned.

## Proof

- Package detail fields, key validation, shared catalogue aggregation, explicit-path behavior, schema compatibility,
  read-only behavior, and package ownership: Stage 1 finite pytest command.
- Detail HTTP contract, percent-encoded current keys, typed statuses, unknown-query tolerance, rebuilt-path dependency,
  read-only behavior, private-ID exclusion, route ordering, and legacy coexistence: Stage 2 finite pytest command.
- Five-operation curated contract and served-route boundary: Stage 3 contract-export pytest command.
- Checked-in HeyAPI surface and no production adoption: Stage 3 focused Vitest command.
- Byte-identical regeneration: Stage 3 generator `--check` command.

No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, or complete maintenance
proof is part of this implementation Plan.

## Acceptance

- `GET /api/openings/{opening_key}` with operation ID `getOpeningByKey` returns the exact six-field flat item from the
  rebuilt database.
- The public key remains the CLEAN-01/CLEAN-03 `ECO:Name` key, including names containing additional colons; current
  spaces, apostrophes, plus signs, and Unicode work through standard percent-encoded paths.
- Route count, distinct reached games, and distinct deepest games have exactly the accepted CLEAN-03 meanings.
- Malformed keys return typed 422, valid absent keys return typed 404, unavailable rebuilt data returns typed 503, and
  unexpected failures return safe typed 500. Unknown query fields are ignored.
- `/api/openings` and `/api/openings/line-library` remain registered; the latter is unchanged and outside the curated
  contract.
- The curated OpenAPI contract contains exactly the five clean operations, and checked-in HeyAPI exposes exactly
  `getHealth`, `getGames`, `getGame`, `getOpenings`, and `getOpeningByKey`.
- Generation `--check` passes byte-identically.
- No schema, index, dependency, backend SQL, route-move/tree behavior, legacy change, frontend adoption, later CLEAN
  work, or private-ID exposure occurs.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, or acceptance decision.
- Any change to the accepted `ECO:Name` key, CLEAN-01/CLEAN-03 aggregation meanings, error/status semantics, or public
  six-field response.
- Any current database label containing `/`, or any requirement to support arbitrary future slash-containing labels;
  the normal one-segment route cannot capture decoded `%2F` and a greedy path route would require review.
- Any collision or malformed persisted label that cannot use the accepted unavailable-data behavior.
- Any schema/index/version change, performance requirement needing a new index, new SQL owner, legacy path, fallback,
  migration, cutover, compatibility adapter, route relocation/removal, or change to the Line Library contract.
- Any production frontend adoption, CLEAN-05 or later work, additional curated operation, new dependency, generated
  artifact outside the approved directory, handwritten path-encoding workaround, commit, push, branch, worktree, or
  stash.

## Visible result

> A user can request one rebuilt opening by its reusable key and receive its label, route count, and distinct reached/deepest game usage, while the generated client exposes `getOpeningByKey()` beside the four accepted clean operations.
