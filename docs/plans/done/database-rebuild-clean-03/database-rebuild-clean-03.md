# CLEAN-03 opening catalogue - A generated API can browse rebuilt openings

> **Status:** done - accepted; all three stages complete

- **Read trigger:** whenever CLEAN-03 implementation, validation, repair, or acceptance is approved
- **Upstream:** [database-rebuild-api-direction.md](../../../grilling-docs/database-rebuild-api-direction.md) (settled API
  semantics and ownership); [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md) (CLEAN-03
  scope and slice envelope); [database-rebuild-clean-01.md](../../done/database-rebuild-clean-01/database-rebuild-clean-01.md)
  (accepted opening-key/game-filter behavior, clean database dependency, generation, and proof);
  [database-rebuild-clean-02.md](../../done/database-rebuild-clean-02/database-rebuild-clean-02.md) (accepted clean
  operation coexistence, generation, and retained proof); [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md) (focused Plan
  schema)

## Outcome

Add exactly `GET /api/openings`, with operation ID `getOpenings`, over the rebuilt database at
`data/database/chess.db`. It returns a flat, searchable, finite catalogue of opening labels with reusable `ECO:Name`
keys, route counts, distinct games that reached each opening, and distinct games for which it was the deterministic
deepest recognition. The package owns SQL and aggregation; the FastAPI layer only translates HTTP. The operation is
added immediately to the curated OpenAPI contract and the checked-in HeyAPI client is regenerated and proven
deterministic.

## Scope

- **Included:**
  - An explicit-path, read-only package capability under `src/chess_move_trainer/database/openings/`.
  - Reuse of the canonical opening-key helper by both the catalogue and CLEAN-01 game filtering.
  - The flat `/api/openings` collection on the existing openings router, using the clean rebuilt-database dependency.
  - Strict HTTP response and error models, focused package proof, focused HTTP proof, and legacy-route coexistence
    proof.
  - Addition of only `/api/openings` to the curated exporter, immediate HeyAPI regeneration, generated-client surface
    proof, and byte-identical regeneration proof.
- **Expected areas:**
  - `src/chess_move_trainer/database/openings/catalogue.py`
  - `src/chess_move_trainer/database/openings/__init__.py`
  - `src/chess_move_trainer/database/games/search.py`
  - `tests/database/openings/test_catalogue.py`
  - `tests/database/games/test_search.py`
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
  - Tables, columns, indexes, triggers, schema versions, migrations, dependencies, or database lifecycle work.
  - Backend SQL, a backend repository/service SQL stack, legacy database configuration, fallback, or compatibility
    adapters. The package remains the only owner of catalogue SQL and aggregation.
  - Route moves, route IDs, route details, hierarchy/tree data, the Opening Line Library, an opening detail route, or
    any later CLEAN operation.
  - Changes to the existing `/api/openings/line-library` implementation or its legacy data contract; it remains
    registered outside the curated contract.
  - Production frontend feature imports, consumer migration, generated-client adoption, legacy-route removal, broad
    maintenance, Quality work, complete test/fix runs, or Git operations.

## Contract

### Request

`GET /api/openings` accepts these query parameters. Omitted filters do not constrain the result. Unknown query fields
are ignored.

- `page`: positive integer, default `1`.
- `page_size`: integer from `1` through `100`, default `50`.
- `search`: optional text. It is trimmed, matched case-insensitively as a substring against either the ECO or opening
  name, and ignored when blank.
- `eco_from` and `eco_to`: optional inclusive ECO bounds. Values are trimmed and normalized to uppercase; each must be
  an ECO code from `A00` through `E99`, and `eco_from` cannot be greater than `eco_to`.
- `sort`: default `eco_asc`. Supported values are `eco_asc`, `eco_desc`, `name_asc`, `name_desc`,
  `route_count_asc`, `route_count_desc`, `games_reached_asc`, `games_reached_desc`, `games_deepest_asc`, and
  `games_deepest_desc`.

Search and ECO bounds combine with AND. Every sort uses `key ASC` as its final tie-breaker. Counts have no null sort
case because the response returns zero for no usage.

The API key is exactly the reusable `ECO:Name` value from `opening_api_key()`. The `(do_eco, do_name)` unique
constraint makes this construction injective, including names containing additional colons; parsing splits only the
first colon. A defensive conflicting-key check must fail as unavailable rather than silently overwrite or merge data.
Malformed persisted labels that cannot form a safe key are also operational data failures, not invented keys. The
current rebuilt target has no such labels or key collisions.

### Response

HTTP 200 returns a finite page:

```json
{
  "items": [
    {
      "key": "A00:Amar Opening",
      "eco": "A00",
      "name": "Amar Opening",
      "route_count": 1,
      "games_reached": 1,
      "games_deepest": 1
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 3329,
  "total_pages": 67,
  "has_next": true
}
```

`route_count` counts persisted routes for the ECO/name label. `games_reached` counts distinct games with any stored
occurrence matching any route endpoint for that label. `games_deepest` counts distinct games whose CLEAN-01 deepest
opening selection is that label: greatest matched ply wins and an equal-ply tie uses the lexicographically smallest
API key. Multiple routes or repeated occurrences never inflate a distinct-game count.

The catalogue includes labels even when their usage is zero. Zero-result searches return an empty `items` list,
`total` zero, `total_pages` zero, and `has_next` false. A page beyond the end is valid and returns no items. The
response contains no private SQLite identifiers, route moves, route IDs, hierarchy, or detail data.

### Errors

- Known invalid values or combinations return HTTP 422:
  `{"code":"invalid_filter","message":"Invalid opening filter"}`.
- Missing, incompatible, unreadable, or malformed rebuilt data returns HTTP 503:
  `{"code":"openings_unavailable","message":"Openings unavailable"}`.
- Unexpected failures return HTTP 500:
  `{"code":"unexpected_failure","message":"Unable to load openings"}`.
- Primitive values that FastAPI cannot coerce may use its standard request-validation 422 response. There is no
  collection-level 404.

## Repository and route decisions

- The package read capability will use an explicit `database_path`, the existing read-only connection boundary, and
  schema-v1 compatibility checks. Package-owned SQL will load labels, routes, and matched game occurrences; ordinary
  package Python will perform reached/deepest aggregation, filtering, pagination, and sorting.
- The existing private key helpers in `games/search.py` will delegate to `openings.keys`, preserving CLEAN-01 behavior
  while preventing catalogue and game-filter key drift. This shared change requires the affected CLEAN-01/CLEAN-02
  game-search proof to be rerun.
- The clean HTTP adapter belongs in the existing `backend/app/features/openings/router.py`, alongside the legacy
  literal `/openings/line-library` route. The new literal `/openings` route uses `get_rebuilt_database_path()` and does
  not use the legacy openings `repository.py` or `service.py`. `main.py` already mounts this router and should not need
  a registration change. Literal routes remain ahead of any future dynamic detail route; no detail route is added here.
- The backend catalogue models will be isolated in `catalogue_api_schemas.py` so the legacy Line Library models remain
  unchanged. The clean models reject unknown response fields.
- No schema/index/dependency change is required. The accepted v1 tables and existing position-first game-position
  index are sufficient for the bounded catalogue joins; a performance need for a new index is an escalation.

## Baseline preservation

The following pre-existing unrelated worktree material is preserved exactly and is not restored, rewritten, staged, or
absorbed:

- deleted `data/database/README.md`;
- deleted `data/database/dump_schema.py`;
- deleted `data/database/schema.md`;
- deleted `data/database/schema.txt`; and
- modified `docs/grilling-docs/database-rebuild-api-direction.md`, including its `chess.db` clarification.

CLEAN-01 and CLEAN-02 are accepted accumulated implementation, not new work to redesign. Their clean database
dependency, package capabilities, games adapter, all accepted generated operations, package-boundary proof, legacy
routers, and generated output remain in place. The production target remains only `data/database/chess.db`; the old
database path and old routes are not migrated or removed.

## Stages

1. **completed** - Package catalogue capability, canonical key reuse, and focused package proof.
2. **completed** - Thin HTTP adapter on the existing openings router and coexistence proof.
3. **completed** - Curated contract, HeyAPI generation, and deterministic proof.

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment.

### Stage 1 - Package catalogue capability and proof

Ordered actions:

1. Add the explicit-path opening catalogue read capability in `src/chess_move_trainer/database/openings/catalogue.py`
   with ordinary dataclasses for the query, entries, page, and package errors. Export its public capability from the
   openings package without importing backend, FastAPI, or HTTP models.
2. Read schema-v1 labels and routes, count routes per label, and join route endpoints to stored game occurrences.
   Count reached games distinctly; reduce each `(game, opening)` to its greatest matched ply; select each game's
   greatest ply and lexicographically smallest reusable key for deepest usage. Do not read route moves for this
   response.
3. Keep validation, search matching, ECO bounds, pagination, sorting, key validation, SQL, read-only behavior, and
   aggregation in the package. Use the canonical `openings.keys` helper from both the catalogue and games search.
4. Add focused temporary schema-v1 fixtures covering labels with multiple routes, shared route endpoints, repeated
   game matches, equal-depth ties, colon-containing names, zero usage, every filter/sort family, pagination,
   deterministic repeated reads, missing/incompatible data, unchanged bytes, no sidecars, explicit paths, and the
   package boundary. Extend the existing game-search regression only as needed for canonical key reuse.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/openings/test_catalogue.py tests/database/games/test_search.py tests/database/test_package_boundary.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves package-owned catalogue aggregation,
key compatibility with CLEAN-01, explicit-path schema-v1 reads, deterministic behavior, read-only behavior, and the
package boundary.

Escalation boundary: any schema/index/version change, new dependency, backend import, private-ID requirement, changed
reached/deepest meaning, or inability to perform the read with accepted schema v1. Breakpoint: none.

### Stage 2 - Thin HTTP adapter and proof

Ordered actions:

1. Add strict catalogue response and error models in `backend/app/features/openings/catalogue_api_schemas.py`.
2. Add `GET /api/openings` with `operation_id="getOpenings"` to the existing openings router, using
   `get_rebuilt_database_path()` and the package capability. Keep backend SQL out of the clean path and leave the
   legacy Line Library implementation and literal route registered.
3. Translate package validation failures to the typed 422 response, schema/storage failures to the typed 503 response,
   and unexpected failures to the safe typed 500 response. Unknown query fields remain ignored.
4. Add focused HTTP fixtures/tests for the exact response and counts, all filters/sorts and defaults, zero results,
   unknown fields, invalid values/combinations, missing/incompatible/unexpected failures, default target access,
   unchanged database bytes/no sidecars, no private IDs, clean dependency separation from the legacy path, and both
   `/api/openings` and `/api/openings/line-library` remaining registered.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/openings backend/tests/features/games -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the new clean HTTP operation and
re-establishes affected CLEAN-01/CLEAN-02 games HTTP behavior while proving legacy openings coexistence.

Escalation boundary: backend SQL, legacy database use, fallback, compatibility adapter, route removal, changed HTTP
fields/statuses/meanings, or a router conflict that cannot preserve the literal legacy route. Breakpoint: none.

### Stage 3 - Curated contract, HeyAPI generation, and deterministic proof

Ordered actions:

1. Add only `"/api/openings": {"get"}` to `APPROVED_OPERATIONS` in `scripts/api/export_contract.py`; keep the exporter
   fail-closed.
2. Update `backend/tests/features/health/test_contract_export.py` to require exactly the four clean paths
   `/api/health`, `/api/games`, `/api/games/{game_uuid}`, and `/api/openings`, with operation IDs
   `getHealth`, `getGames`, `getGame`, and `getOpenings`. Require only their referenced schemas, deterministic export,
   full served OpenAPI, and exclusion of `/api/openings/line-library`.
3. Update `frontend/src/api/client.ts` to re-export `getOpenings` and its generated types, and update
   `frontend/src/api/generatedSurface.test.ts` to require exactly the four clean SDK operations and paths. Do not
   edit production frontend feature modules.
4. Run the accepted generator to update only `frontend/src/api/generated/`; do not hand-edit generated output.
5. Run the focused contract proof, generation, generated-surface proof, and byte-identical `--check` in order.

Proof, from `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves the curated contract contains exactly
the accepted clean operations plus `/api/openings`, while served legacy routes remain available but uncurated.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This immediately regenerates the checked-in HeyAPI
output from the fresh curated contract.

```text
.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000
```

Command-level timeout: 240 seconds. Bash tool timeout: `300000 ms`. This proves the generated SDK exposes exactly the
four approved clean operations and that no production frontend module adopted it.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`. This proves byte-identical regeneration of every
checked-in generated file.

Escalation boundary: any additional curated operation, generated output outside `frontend/src/api/generated/`, new
dependency, production frontend import, legacy operation entering the contract, or non-deterministic generation.
Breakpoint: none.

## Retained proof and invalidation

- CLEAN-01 and CLEAN-02 Plans remain historical records and are not rewritten.
- Reusing the canonical key helper changes shared `games/search.py` input, so the game-search package proof is
  re-established in Stage 1 and the games HTTP proof is rerun in Stage 2.
- The new openings router code is exercised with the existing legacy openings tests in Stage 2; the legacy fixture and
  Line Library data model are not changed.
- Updating the exporter, contract assertions, handwritten client, generated-surface test, and generated files
  invalidates prior contract and generation proof. Stage 3 re-establishes health, games, game detail, and openings
  together.
- Unaffected foundation, database rebuild, CLEAN-01/CLEAN-02 detail-reader behavior, and legacy behavior remain
  retained evidence unless a later implementation change touches their inputs. Passing behavioral proof remains valid
  until such an affecting change.

## Progress and decisions

- **Stage 1:** completed - from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/openings/test_catalogue.py tests/database/games/test_search.py tests/database/test_package_boundary.py -q`
  passed `42` tests with a 180-second command timeout and `240000 ms` Bash tool timeout. It proves catalogue filters,
  sorting, pagination, reached/deepest counts and ties, zero usage, colon-containing canonical keys, explicit schema-v1
  paths, read-only/no-sidecar behavior, and package ownership; it also re-establishes the affected CLEAN-01 game-search
  proof after canonical helper reuse; breakpoint: none.
- **Stage 2:** completed - from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/openings backend/tests/features/games -q`
  passed `47` tests in `78.73s` with a 180-second command timeout and `240000 ms` Bash tool timeout. It proves the clean
  catalogue response, filters, pagination, typed errors, default rebuilt database, read-only/private-ID behavior, and
  coexistence with the legacy Line Library and all accepted games routes. Stage 1 proof remained valid because package
  inputs were unchanged; breakpoint: none.
- **Stage 3:** completed - from `G:\ChessMoveTrainer`, the Plan's focused contract-export pytest passed `4` tests;
  generation completed for `17` generated files; the focused API Vitest run passed `4` tests; and generator `--check`
  proved byte-identical regeneration of all `17` files. Commands used the Plan's explicit 180/240-second command
  wrappers and `240000`/`300000 ms` Bash tool timeouts. Stage 1 and Stage 2 proof remained valid because generation
  changed no package or backend behavior; breakpoint: none.
- **Database decision:** production reads target only `data/database/chess.db`; the existing
  `CHESS_REBUILT_DATABASE_PATH` seam is for bounded tests/deployment configuration and does not change legacy behavior.
- **Schema decision:** accepted schema version 1 is used as-is; no table, column, index, trigger, or schema-version
  change is authorized.
- **Ownership decision:** the package owns SQL, key reuse, filtering, pagination, sorting, and usage aggregation; the
  backend owns HTTP models/status translation; generated output remains generator-owned.

## Proof

- Package catalogue, key compatibility, deterministic aggregation, explicit-path behavior, read-only behavior, and
  package ownership: Stage 1 finite pytest command.
- Clean HTTP response, filters, errors, rebuilt target, read-only behavior, and legacy route coexistence: Stage 2
  finite pytest command.
- Four-operation curated contract and served-route boundary: Stage 3 contract-export pytest command.
- Checked-in generated HeyAPI surface and no production adoption: Stage 3 focused Vitest command.
- Byte-identical regeneration: Stage 3 generator `--check` command.

No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, or complete maintenance
proof is part of this implementation Plan.

## Acceptance

- `GET /api/openings` with operation ID `getOpenings` returns the exact flat paginated contract from rebuilt
  `data/database/chess.db`.
- Search discovers names and ECO codes; ECO bounds, pagination, finite limits, sorts, ties, and invalid combinations
  behave exactly as specified.
- `ECO:Name` keys match CLEAN-01 game filters, including names containing colons.
- Route counts and distinct reached/deepest game counts have the stated meanings; unused labels return zero counts.
- Package tests prove explicit paths, schema-v1 compatibility, package ownership, deterministic reads, and no writes or
  SQLite sidecars.
- HTTP tests prove strict response/error translation, unknown-field tolerance, clean rebuilt-path use, safe failures,
  private-ID exclusion, and coexistence with `/api/openings/line-library`.
- The curated OpenAPI contract contains exactly health, games collection, game detail, and openings collection. The
  legacy Line Library remains outside it and served OpenAPI remains available.
- Checked-in HeyAPI exposes exactly `getHealth`, `getGames`, `getGame`, and `getOpenings`; generation `--check` passes.
- No schema, index, dependency, backend SQL, frontend production adoption, later CLEAN work, or legacy removal occurs.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, or acceptance decision.
- Any schema/index/version change, performance requirement that needs a new index, or inability to aggregate with schema
  v1.
- Any change to key format, search matching, ECO filters, pagination defaults/limits, sort names/ties, usage meanings,
  zero/null behavior, error codes/statuses, or private-identity policy.
- Any key collision or malformed target label requiring a different key encoding rather than the approved unavailable
  failure.
- Any use of the legacy database, fallback, migration, cutover, compatibility adapter, legacy route removal, future
  detail route, frontend consumer adoption, later CLEAN slice, new dependency, or generated artifact outside the
  approved directory.
- Any failure to preserve the existing literal `/api/openings/line-library` route and all accepted CLEAN-01/CLEAN-02
  operations.

## Visible result

> A user can request a searchable page of rebuilt opening labels with stable keys, route counts, and distinct reached/deepest game usage, while the generated client exposes `getOpenings()` beside the accepted clean operations.
