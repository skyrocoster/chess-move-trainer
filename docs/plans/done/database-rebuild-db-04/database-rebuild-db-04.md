# DB-04 opening catalogue and route rebuild - Five validated opening sources become one queryable catalogue

> **Status:** done - all four stages accepted with 87 focused tests passing across retained proofs.

- **Read trigger:** Read before any DB-04 opening catalogue, lookup/replay, or opening CLI implementation or proof.
- **Upstream:** [database-rebuild master plan DB-04](../../../master-plans/database-rebuild/database-rebuild.md#db-04--opening-catalogue-and-route-rebuild); binding [database direction](../../../grilling-docs/database-rebuild-direction.md#44-opening-catalogue-and-lookup) and [database schema](../../../grilling-docs/database-rebuild-schema.md#6-datasource_opening); confirmed [DB-04 grilling handoff](../../../grilling-docs/database-rebuild-db-04.md).

## Outcome

A caller can atomically replace the opening catalogue from exactly `a.tsv` through `e.tsv`, then use importable package services or thin Typer commands to look up a full FEN or replay exactly one PGN. The result uses the existing three opening tables and DB-02 canonical endpoint positions, reports an ordered structured recognition timeline and one deterministic current label, and visibly distinguishes exact routes from transpositions without integrating with the application.

Retained prerequisites are DB-01's compatible schema-v1 database and exact ten-table catalogue, DB-02's legal four-field canonicalization and conflict-safe position resolver, and the accepted DB-03 package/CLI foundation. The current composition seams are `database.connection._open_existing_connection`, `database.schema._assert_compatible_schema`, and `database.positions.repository._PositionUnitOfWork` inside one package-owned transaction, as already composed by `GameRepository.persist`; public FEN identity remains `positions.canonicalize_fen`. No checked-in real upstream TSV population is assumed: DB-04 proves the complete five-file contract with focused synthetic fixtures, while DB-09 owns proof against real rebuilt data.

## Scope

- **Included:** Strict caller-supplied five-file TSV validation; source-PGN legal replay to ordered UCI; semantic `(ECO, name, ordered UCI moves)` deduplication; preservation of distinct transposing routes; complete child-first atomic replacement; canonical endpoint reuse and rollback; isolated FEN lookup and one-game PGN replay; ordered structured recognition, singular-current precedence, route/transposition status, broader recognized families, no-match behavior, human-readable and stable JSON CLI output, settled exits, and package/source-boundary proof.
- **Expected areas:** `src/chess_move_trainer/database/openings/__init__.py`, `src/chess_move_trainer/database/openings/source.py`, `src/chess_move_trainer/database/openings/persistence.py`, `src/chess_move_trainer/database/openings/recognition.py`, `src/chess_move_trainer/database/cli.py`, `tests/database/openings/__init__.py`, `tests/database/openings/conftest.py`, `tests/database/openings/fixtures/catalogue-valid/{a,b,c,d,e}.tsv`, `tests/database/openings/test_source.py`, `tests/database/openings/test_persistence.py`, `tests/database/openings/test_recognition.py`, `tests/database/test_cli.py`, `tests/database/test_package_boundary.py`, and `tests/database/test_source_boundary.py`.
- **Excluded:** Any schema or `schema_v1.sql` change; new tables, columns, manifests, hashes, source/import state, hierarchy, aliases, parent/transposition links, shared-prefix trees, classification, recurrence, intermediate-position membership, opaque move-sequence storage, route history, or permanent per-game result; network fetches or raw-source mutation; changes to `database.games` or the DB-02 position contract; legacy imports/wrappers/copies/delegation; production backend/frontend, HTTP routes, Opening Line Library work, DB-09 real-data proof, cutover, old-database mutation, or deletion.

## Stages

Stages are sequential and never parallel. A passing proof remains retained until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment; later stages run only missing or invalidated proof. The coordinator may split an oversized stage without changing this outcome.

### 1. [x] Parse and normalize the exact five-source catalogue before mutation

**Ordered actions**
1. Add `openings/source.py` with immutable `OpeningRouteSource`, `OpeningSourceError`, and the importable `load_opening_sources(source_dir)` service. `OpeningRouteSource` must expose immutable endpoint data, such as a validated full FEN or canonical fields, rather than retaining a mutable `chess.Board`. Keep source parsing and legal replay independent of storage and CLI concerns; use the existing `python-chess` dependency directly rather than importing private game-normalization or legacy code.
2. Require a readable source directory whose TSV source names are exactly `a.tsv`, `b.tsv`, `c.tsv`, `d.tsv`, and `e.tsv`; reject a missing required file or an additional TSV source. Require each file's header and each data row to have exactly `eco`, `name`, and `pgn`, reject malformed encoding/TSV structure, blank or invalid ECO, empty move text, parse errors, trailing invalid move text, and illegal replay, while preserving the schema-permitted opening name verbatim, including an empty string.
3. Replay every accepted source row from the standard initial position into a non-empty one-based ordered UCI sequence and an immutable final-position representation. Deduplicate only by `(eco, name, moves_uci)` after replay so PGN-formatting variants collapse across files, while different move orders and different labels survive even when their endpoint is shared. Complete validation and deduplication for all five files before returning data to persistence.
4. Add focused synthetic fixtures and parser tests for exact-five enforcement, exact field count, verbatim names, valid ECO, empty/illegal/malformed/trailing move rejection, legal UCI conversion, cross-file formatting duplicate collapse, distinct transposition preservation, and deterministic source-independent results.

**Focused proof**
- Command: `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/openings/test_source.py -q`; working directory: `G:\ChessMoveTrainer`; command timeout: `60s`; Bash tool timeout: `90000ms`.

**Stage acceptance:** The importable source service returns a complete prevalidated semantic route set without touching a database, and every rejected five-file batch produces no partial result.

**Escalation boundary / breakpoint:** No human breakpoint. Stop if real source semantics require a start position other than standard chess, more or fewer columns/files, a new parser dependency, or source provenance/state outside the confirmed contract.

### 2. [x] Publish the complete catalogue through one atomic position-aware transaction

**Ordered actions**
1. Add `openings/persistence.py` with immutable `CataloguePublication`, `OpeningPersistenceError`, `OpeningCatalogueRepository.replace(routes)`, and `import_opening_catalogue(source_dir, repository)`. The import service must call Stage 1 first, so no catalogue mutation begins until all five sources have parsed, replayed, and deduplicated successfully.
2. Follow the existing `GameRepository.persist` composition pattern: open one existing database with `_open_existing_connection`, assert schema compatibility, start one transaction, and bind `_PositionUnitOfWork` to that same package-owned connection. `SchemaIncompatibleError` must escape the openings repository unwrapped, or be mapped before a generic persistence wrapper, so the CLI can reliably distinguish exit 3. Do not expose a SQLAlchemy/sqlite handle or broaden the public position API.
3. Reconstruct a fresh board from each route's immutable final-position data and resolve or create only that endpoint through `_PositionUnitOfWork.resolve_board`, retaining and reusing matching DB-02 positions. Within that same transaction, delete `derived_opening_route_move`, then `derived_opening_route`, then `datasource_opening`; insert one label per `(eco, name)`, one route per semantic route identity, and contiguous move children with `dorm_ply` from 1. Do not delete any canonical position, including an endpoint no longer referenced after replacement.
4. Keep integer IDs internal. Verify after insertion, before commit, that child plies are contiguous, replay is legal, and every replayed final canonical position equals its stored `derived_position_id`. Provide a private deterministic checkpoint hook, matching the repository's existing testing convention, so storage failure and `KeyboardInterrupt` can be injected without product behavior.
5. Test first publication and complete replacement, labels with several routes, routes/labels sharing endpoints, canonical endpoint reuse, unrelated-position retention, child-first deletion, contiguous plies, endpoint equality, and transaction rollback after injected storage failure or interruption. Prove rollback removes newly created endpoints and leaves every prior opening row and route child unchanged; malformed input remains a pre-transaction rejection.

**Focused proof**
- Command: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/openings/test_persistence.py -q`; working directory: `G:\ChessMoveTrainer`; command timeout: `90s`; Bash tool timeout: `120000ms`.

**Stage acceptance:** One transaction either publishes all three opening tables with canonical endpoints or leaves the previous catalogue and position set unchanged, while unrelated canonical positions always survive successful replacement.

**Escalation boundary / breakpoint:** The atomic rollback and prior-catalogue preservation checks are the stage gate. Stop if this requires changing the schema, deleting canonical positions, exposing raw connection ownership, or changing DB-02 canonical identity.

### 3. [x] Derive structured FEN lookup and one-game PGN recognition from persisted routes

**Ordered actions**
1. Add `openings/recognition.py` with `OpeningInputError`, immutable `RecognizedOpening` and `OpeningRecognition`, plus importable `lookup_fen(database_path, fen)` and `replay_pgn(database_path, pgn)` services. Results contain an ordered recognition collection and `current` (`None` on no match); each recognition carries reached ply, ECO, name, and `route` or `transposition` match kind. Database IDs remain absent from the public result.
2. Read only `datasource_opening`, `derived_opening_route`, `derived_opening_route_move`, and endpoint rows in `derived_position`. Reconstruct route order from contiguous child plies and replay stored UCI rather than creating an intermediate-membership projection. Treat malformed persisted route shape, illegal stored replay, or endpoint mismatch as an operational/storage failure rather than silently classifying it.
3. For PGN, accept exactly one standard-start game with or without ordinary headers. Reject empty input, a second game, parser errors, illegal moves, and trailing invalid content. At each encountered ply, match the canonical board to stored endpoints; mark a label `route` only when its complete stored UCI sequence equals the played prefix, otherwise `transposition`. Merge duplicate route evidence for the same label at the same reached ply, preferring `route`, while retaining all tied labels and ordering deterministically by encountered ply and then `(ECO, name)`.
4. Select singular `current` by deepest reached ply, then `route` over `transposition`, then the lexicographically lowest `(ECO, name)` among remaining ties. If later unnamed moves leave theory, retain the latest recognized current label; never expose endpoint labels not yet reached.
5. For a standard full FEN, canonicalize through DB-02's four-field identity and ignore clock fields. Find every directly matching endpoint, replay each matching stored route to derive only the broader labels encountered on that route, merge deterministic duplicates, mark all FEN-derived recognitions `transposition` because no input move history exists, and apply the same current-label precedence. Return an empty collection and `current=None` for a valid unmatched FEN.
6. Test ordered breadcrumbs, deepest/exact/lexical current precedence, all tied labels retained, exact-route versus transposition claims, departure from theory, unreached-future exclusion, repeated evidence merging, full-FEN clock insensitivity, direct FEN matches plus route-derived broader families, and valid no-match results. Test invalid one-game PGN and invalid FEN separately from operational database failures.

**Focused proof**
- Command: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/openings/test_recognition.py -q`; working directory: `G:\ChessMoveTrainer`; command timeout: `90s`; Bash tool timeout: `120000ms`.

**Stage acceptance:** Package callers receive deterministic structured recognition and exactly the settled current label for route, transposition, FEN-family, out-of-theory, tied, and no-match cases without persisted classification or intermediate membership.

**Escalation boundary / breakpoint:** Recognition semantics and precedence are settled; no visual or human breakpoint remains. Stop rather than inventing a different singular-current rule, family relationship, nonstandard start-position contract, or persisted lookup aid.

### 4. [x] Expose thin supported Typer commands and lock package boundaries

**Ordered actions**
1. Re-export the Stage 1-3 public contracts from `openings/__init__.py` and extend `test_package_boundary.py` so `chess_move_trainer.database.openings` and its package services are importable from the installed `src` package. Do not add a dependency or package-data rule for the caller-owned TSV files.
2. In `database/cli.py`, register `openings_app` beneath the existing `app` and add only the approved callbacks: `openings import --source-dir PATH --database PATH`, `openings lookup --database PATH --fen FEN`, and `openings replay --database PATH --pgn-file PATH`. Keep all paths explicit, commands non-interactive, callbacks limited to argument adaptation, service calls, stable rendering, and exception-to-exit mapping.
3. Provide concise human-readable stdout by default and `--json` on every successful openings command. Lock deterministic JSON objects in CLI tests: import reports publication counts; lookup/replay report `recognized` as ordered objects containing `ply`, `eco`, `name`, and `match`, plus `current` as the selected object or `null`. Emit errors only on stderr. A valid unmatched lookup/replay is status 0; catalogue/source or operational/storage failures are 1; invalid Typer use or lookup/replay input is 2; `SchemaIncompatibleError` is 3; and interruption is 130.
4. Extend `test_cli.py` for root/group/command help, exact required options, import/lookup/replay default and JSON output, explicit files, empty stdin independence/non-interactivity, one-game rejection, no-match success, schema incompatibility, operational/source errors, and interruption. Extend boundary tests to prove the openings package imports neither legacy/application modules nor sibling `database.games`, the CLI owns no SQL/parser/business logic, lower-level database/positions packages do not depend on openings, and no runtime wrapper/delegation exists.
5. Complete a bounded source-boundary review of the new `database/openings` modules and the DB-04 legacy conceptual touchpoints named by the master plan. Record that the new implementation was written against the approved contracts and does not copy or incrementally continue legacy implementation or internal contracts; do not claim an automated import scan alone proves absence of copied logic.

**Focused proof**
- Command: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q`; working directory: `G:\ChessMoveTrainer`; command timeout: `90s`; Bash tool timeout: `120000ms`.
- Command: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q`; working directory: `G:\ChessMoveTrainer`; command timeout: `90s`; Bash tool timeout: `120000ms`.
- Review: inspect only the new `src/chess_move_trainer/database/openings/` implementation, its thin `database/cli.py` adapters, and the DB-04 legacy conceptual touchpoints named by the master plan; record exact path/symbol evidence for no copied implementation, legacy import, wrapper, or runtime delegation.

**Stage acceptance:** All three supported commands expose useful help and the package-service behavior with stable default/JSON output and exact exits, while automated boundary checks preserve the clean package/CLI and legacy/application separation.

**Escalation boundary / breakpoint:** No human breakpoint. Stop if stable output requires a contract beyond the settled structured recognition/count data, if exit mapping conflicts with Typer's status-2 usage behavior, or if implementation would require legacy/application integration or a new dependency.

## Progress and decisions

- **Stage 1:** [x] accepted - proof: `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/openings/test_source.py -q` passed 18 tests in 0.50s; complete strict five-source parsing, immutable legal route normalization, deterministic semantic deduplication, and storage independence established.
- **Stage 2:** [x] accepted - proof: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/openings/test_persistence.py -q` passed 8 tests in 1.30s; complete child-first publication, endpoint reuse and retention, endpoint/ply verification, distinct schema errors, and storage/interruption rollback established.
- **Stage 3:** [x] accepted - proof: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/openings/test_recognition.py -q` passed 13 tests in 1.82s; immutable ordered PGN/FEN recognition, exact-route/transposition distinction, current-label precedence, family derivation, no-match/input failure, corruption detection, and read-only behavior established.
- **Stage 4:** [x] accepted - proof: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q` passed 38 tests in 28.93s, and `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` passed 10 tests in 0.72s; supported Typer help/commands, explicit non-interactive inputs, default/JSON output, settled exits, package exports, and enforceable clean boundaries established. A bounded comparison of the new opening modules and CLI adapters with the master-plan-named legacy conceptual touchpoints found no copied implementation, legacy import, wrapper, or runtime delegation.
- **Decision retained:** Source route identity is semantic UCI identity, not raw PGN text, source-row identity, endpoint identity, or integer ID.
- **Decision retained:** FEN has no move history and therefore never claims `route`; PGN may retain its last recognized current label after leaving catalogued theory.
- **Decision retained:** Focused fixtures prove DB-04's full five-file behavior; absence of checked-in real upstream TSV data is not a DB-04 acceptance blocker and DB-09 owns real-data proof.

## Proof

- Stage 1's finite source test proves strict complete input validation and semantic replay/deduplication.
- Stage 2's finite persistence test proves exact-table publication, canonical endpoint behavior, child-first replacement, and rollback.
- Stage 3's finite recognition test proves structured route/transposition/FEN/PGN semantics and current-label selection.
- Stage 4's two finite tests prove supported CLI behavior and enforceable source/package boundaries; its bounded source review covers the non-automatable clean-rewrite comparison.
- No lint, formatting, broad type/build, source-size, aggregate suite, complete suite, or repository-hygiene command is Plan implementation proof. Independent validation and complete maintenance checks are separate workflows if requested.

## Escalation boundaries

- Escalate any need for a table/field/schema-version change, provenance/manifest/import state, hierarchy/family persistence, classification/recurrence/intermediate membership, opaque route storage, route history, or canonical-position deletion/change.
- Escalate a different source-set, PGN/FEN, singular-current, JSON data, invocation, or exit contract; a new dependency; or inability to preserve atomic replacement and the prior working catalogue.
- Escalate any legacy runtime reuse, application/backend/frontend/HTTP integration, Opening Line Library revival, raw/old-database mutation, cutover, deletion, or ownership expansion beyond DB-04.
- Preserve unrelated worktree changes. Execution may edit only the approved DB-04 areas, must not commit/push or create/switch branches, worktrees, or stashes, and must use only a final bounded Git scope audit as directed by the execute workflow.

## Visible result

> Five supplied opening files can be safely rebuilt and queried by FEN or one-game PGN, with clear route/transposition recognition and no application or legacy coupling.
