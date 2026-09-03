# Database inventory and uses assessment

> Historical discovery evidence only. This document is not implementation authorization and does not authorize
> pruning, retention changes, schema changes, data changes, or resurrection of stopped work.

## Revised user goal

Before considering any pruning, fully document the shared database so that every table is understandable. The future
documentation must use actual table names, not shorthand such as S1/S2/S3/S4, and must cover:

- every table, its columns, keys, constraints, and purpose;
- parent/child relationships and foreign keys that make updates or deletions difficult;
- every script, backend area, frontend-facing API path, test, and relevant document that reads or writes each table;
- what each consumer does, including insert, update, upsert, delete, scoped replacement, or append-only behavior;
- lifecycle, ownership, transaction boundaries, failure behavior, destructive effects, and lock cautions; and
- evidence-based possible waste or redundancy, clearly separated from facts and never treated as a deletion decision.

The current request is documentation and discovery only. No schema or database row may be changed.

## What was inspected and how to interpret it

The repository router was read first (`docs/README.md:1-21`). The existing generated schema was then compared with its
in-memory generator and DDL owners (`data/database/dump_schema.py:45-57,217-262`; `data/database/schema.txt:8-18`).
The shared runtime directory contains `data/database/chess_games.db`, its `-wal` and `-shm` sidecars, and
`chess_games.db.analysis.lock`. The database and backup patterns are ignored by `.gitignore:35-40`.

A read-only `sqlite_master` inventory of the runtime database found **49 live tables, 15 indexes, 8 triggers, and no
views**. The current supported object sets are also asserted by `tests/database/test_schema.py:6-83,86-119`.
Selected read-only population checks found analysis results/candidates, audit rows, corpus rows, opening facts and
projections, and preferred-move events; the counts below are a dated assessment snapshot, not a schema contract.

There are four distinct categories of evidence:

1. **Live supported schema:** objects present in `chess_games.db` and assembled by `dump_schema.py`.
2. **Declared but non-live/abandoned schema:** `scripts/opening_catalog/tracked_player_schema.py:21-31,210-255`
   declares nine tables, but the generator does not assemble them and the runtime database does not contain them.
   The archived tracked-player record says the runtime database was restored without them
   (`docs/plans/done/s5-tracked-player-projection/s5-tracked-player-projection.md:1-17,91-105,125-136`).
3. **Test-only and legacy definitions:** temporary fixture schemas and the old version-1 analysis/evaluation shapes
   used by migration tests. They explain contracts and historical behavior but are not current runtime objects.
4. **Unaccepted partial refresh work:** `docs/plans/active/chess-com-refresh/chess-com-refresh.md:1-5,30-43`
   explicitly says the direction was stopped and rejected. `scripts/refresh_chess_com.py` may be searched as a
   repository reference, but neither its design nor its partial hooks are approved behavior.

The assessment did not run Git status/diff commands because the case-worker assessment/planning guardrail forbids
those commands. No files were edited before this synthesis, and unrelated work must remain preserved.

## Authoritative paths and configuration

- Runtime database: `data/database/chess_games.db`.
- Structural generated reference: `data/database/schema.txt`; it describes structure only and does not describe
  runtime uses or row data (`schema.txt:1-6`). It must not be edited manually.
- Generator: `data/database/dump_schema.py`; it assembles the supported DDL in memory and does not open the runtime DB.
- Database notes: `data/database/README.md:1-34`.
- Documentation router: `docs/README.md:1-21`.
- Fetch configuration: `scripts/chess_com/config.yaml:1-2`, containing username `skyrocoster` and subject UUID
  `0101b08a-ce8b-11ee-b2fd-e90263e5548c`.
- Fetch defaults/settings: `scripts/chess_com/fetch_games.py:86-98` and
  `scripts/chess_com/_cli.py:14-17,89-96`.
- Backend path override: `backend/app/features/positions/repository.py:10-12,50-62` uses
  `CHESS_DATABASE_PATH`; backend read adapters open `mode=ro` connections.
- Stockfish defaults: `scripts/stockfish_analysis/analyze_menu.py:11-17,203-209`.
- Refresh configuration adapter: `scripts/refresh_chess_com.py:80-134,422-449`; this is part of the stopped,
  unaccepted direction and must not be resumed.

The main DDL owners are `scripts/chess_com/fetch_games.py:create_schema` (`fetch_games.py:138-167`),
`scripts/chess_com/_schema.py:ensure_corpus_schema` (`_schema.py:21-125`),
`scripts/opening_catalog/schema.py:ensure_schema` and `ensure_relationship_schema`,
`classification_schema.py:ensure_classification_schema`, `recurrence_schema.py:ensure_recurrence_schema`,
`preferred_move_schema.py:ensure_preferred_move_schema`,
`backend/app/features/analysis/schema.py:initialize_analysis_schema`, and
`backend/app/features/evaluation/schema.py:initialize_evaluation_schema`.

## Live table inventory

These are the 49 runtime tables, grouped by ownership and purpose. The names are the database names to use in future
documentation.

### Fetch and accepted game corpus

`players`, `games`, `fetch_state`, `corpus`, `corpus_game`, `position_state`, `position_occurrence`, `corpus_schema`,
`corpus_run`.

`fetch_games.py:create_schema` owns `players`, `games`, and `fetch_state`. It upserts player identity and fetched game
metadata, and tracks monthly ETags/current-month state. `_schema.py:ensure_corpus_schema` owns the corpus metadata,
accepted membership, deduplicated position states, per-game occurrences, schema version, and corpus run history.

### Opening source catalogue

`opening_catalog_schema`, `opening_source_manifest`, `opening_source_file`, `opening_import_run`,
`opening_catalog_state`, `opening_catalog`.

These preserve the fixed five-file source manifest, file hashes, import history, accepted manifest pointer, and replayed
opening records. They are owned by `scripts/opening_catalog/schema.py` and `importer.py`.

### Opening relationships

`opening_relationship_schema`, `opening_relationship_state`, `opening_relationship_run`,
`opening_relationship_position`, `opening_position_membership`, `opening_parent_link`,
`opening_transposition_link`.

These preserve replay-derived positions, source-row membership, parent/child links, and transpositions for an accepted
manifest. They are owned by `schema.py`, `relationships.py`, and `relationship_persistence.py`.

### Opening classification

`opening_classification_schema`, `opening_classification_state`, `opening_classification_run`,
`opening_classification_game`, `opening_classification_anchor`, `opening_classification_route`.

These associate accepted corpus games with catalogue records and preserve anchor and route facts. They are owned by
`classification_schema.py`, `classification.py`, and `classification_persistence.py`.

### Opening recurrence and projections

`opening_recurrence_schema`, `opening_recurrence_state`, `opening_recurrence_run`, `opening_recurrence_game`,
`opening_recurrence_occurrence`, `opening_recurrence_route_event`, `opening_recurrence_branch_event`,
`opening_recurrence_position_projection`, `opening_recurrence_route_projection`,
`opening_recurrence_branch_projection`, `opening_recurrence_route_branch_projection`.

The first group records accepted recurrence inputs/events; the last four are derived count/projection tables consumed by
backend repertoire and context features. They are owned by `recurrence_schema.py`, `recurrence.py`, and
`recurrence_persistence.py`.

### Preferred-move history

`opening_preferred_move_schema`, `opening_preferred_move_requirement_event`, `opening_preferred_move_event`.

The two event tables are append-only effective-time histories. Their schema and protections are owned by
`preferred_move_schema.py`; access and event creation are in `preferred_move.py` and
`preferred_move_history.py`.

### Stockfish analysis

`analysis_schema`, `analysis_result`, `analysis_candidate`, `analysis_batch_run`, `analysis_position_failure`.

`analysis_result` is the current result keyed by four-field `position_key`; `analysis_candidate` stores up to five
candidate lines per result. Batch summaries and final failures are immutable audit records. The schema is owned by
`backend/app/features/analysis/schema.py:9-23,200-283`.

### Evaluation queue

`evaluation_schema`, `evaluation_queue`.

`evaluation_queue` is the durable exact-position FIFO work queue. Its schema and FIFO index are owned by
`backend/app/features/evaluation/schema.py:10-15,137-169`; transitions are in `evaluation/queue.py:100-267`.

### Other live schema objects

The 15 indexes are `evaluation_queue_fifo`, `one_current_month`, `opening_catalog_endpoint_idx`,
`opening_classification_anchor_position_idx`, `opening_classification_route_game_idx`,
`opening_import_run_manifest_idx`, `opening_parent_link_parent_idx`, `opening_position_membership_position_idx`,
`opening_preferred_move_lookup`, `opening_preferred_move_requirement_lookup`,
`opening_recurrence_branch_event_parent_idx`, `opening_recurrence_occurrence_position_idx`,
`opening_recurrence_route_event_position_idx`, `opening_transposition_link_position_idx`, and
`position_occurrence_state_idx` (`schema.txt:73-88,1614-1837`).

The 8 triggers are `analysis_batch_run_no_delete`, `analysis_batch_run_no_update`, `analysis_failure_no_delete`,
`analysis_failure_no_update`, `opening_preferred_move_no_delete`, `opening_preferred_move_no_update`,
`opening_preferred_move_requirement_no_delete`, and `opening_preferred_move_requirement_no_update`
(`schema.txt:90-98,1839-1925`). No views were found.

## Declared but non-live tracked-player tables

The abandoned implementation declares exactly these nine additional tables:

`opening_tracked_player_schema`, `opening_tracked_player`, `opening_tracked_player_state`,
`opening_tracked_player_run`, `opening_player_classification_game`, `opening_player_position_projection`,
`opening_player_route_projection`, `opening_player_branch_projection`, and
`opening_player_route_branch_projection`.

They are temporary historical proof, not part of the live supported schema. Their DDL has foreign keys to players,
accepted recurrence state, neutral classification facts, and recurrence projections. Their publication uses scoped
delete-and-reinsert behavior (`tracked_player_schema.py:255-497`; `tracked_player_persistence.py:173-274`), but no
runtime cleanup or re-publication is authorized.

## Readers and writers by repository area

This is a retained map for the future catalogue. Every entry must eventually be expanded to exact symbol and line
references in a usage matrix.

### Fetch and corpus scripts

- `fetch_games.py:181-243,246-343` writes `players`, `games`, and `fetch_state` using player/game upserts and
  monthly state updates. `create_schema` creates the same objects.
- `_history.py:19-35,59-189,192-257` reads games and corpus membership, writes/updates `corpus_run`, reconciles stale
  runs, computes fingerprints, and validates the accepted set.
- `_persistence.py:33-224` reads and writes `corpus_game`, `position_state`, and `position_occurrence`; it also
  performs targeted removal and orphan cleanup.
- `extract_corpus.py:59-205` owns corpus publication, calling the above routines and replaying games.
- `_cli.py:33-65` reads `corpus_run` through a read-only connection for reports.

### Opening scripts

- `importer.py:220-397` reads source TSVs and writes source manifest/file/catalog/run/state tables. It is first-write-once
  for a manifest and refuses a changed accepted source.
- `relationship_persistence.py:105-358` reads accepted catalogue facts and replaces all relationship rows for one
  manifest inside one transaction.
- `classification.py` and `classification_persistence.py:110-247,287-296` read corpus, game, position, catalogue,
  and relationship data, then replace classification rows for one manifest/corpus scope.
- `recurrence.py` and `recurrence_persistence.py:241-487` read accepted classification/corpus/game data, build
  recurrence events and projections, and replace one manifest/corpus scope.
- `preferred_move.py:60-452` and `preferred_move_history.py:28-198` read players, games, positions, and both event
  histories. `set_requirement`, `set_preferred_move`, and line saving append events; the line operation uses a
  savepoint.
- Tracked-player modules read accepted neutral facts and recurrence projections and write only the non-live abandoned
  tables. Tests in `tests/opening_catalog/test_tracked_player.py` are temporary proof, not runtime use.

### Backend and analysis

- `backend/app/main.py:4-30` mounts health, positions, evaluation, preferred-move, position-context,
  move-response-distribution, and opening routers.
- Positions (`backend/app/features/positions/repository.py:125-215`) read `corpus`, `corpus_game`, `games`,
  `position_occurrence`, `position_state`, and `corpus_schema` through a read-only connection.
- Analysis selection (`backend/app/features/analysis/selection.py:85-204`) reads accepted corpus membership and
  game-derived occurrences/states; `analysis/repository.py:26-170` reads and transactionally writes
  `analysis_result` and `analysis_candidate`, and `:172-243` appends batch/failure audit rows.
- Evaluation (`backend/app/features/evaluation/queue.py:100-321`) reads and mutates `evaluation_queue`; the service
  (`evaluation/service.py:132-360`) reads analysis results/candidates and runs queue workers.
- Opening Line Library (`backend/app/features/openings/schema_validation.py:14-119` and
  `openings/repository.py:192-427`) reads catalogue state, catalogue records, parent links, memberships,
  transpositions, and recurrence route projections.
- Position context (`backend/app/features/position_context/repository.py:118-212`) reads recurrence state,
  recurrence game, and position projections.
- Move response distribution (`backend/app/features/move_response_distribution/repository.py:124-214`) reads
  recurrence state, position projections, and branch projections.
- Preferred-move API storage (`backend/app/features/preferred_move/repository.py:65-205`) reads players and
  game-derived positions and appends `opening_preferred_move_event`. The backend validates the requirement table but
  does not write it; the offline preferred-move line writer can write both event histories.
- `scripts/stockfish_analysis/analyze_positions.py:15-26,51-68,193-347` initializes/reports analysis schema and
  invokes analysis/evaluation code. The full analysis path also has a port-clearing side effect and is separate from
  this documentation request.

### Frontend indirect access

The frontend has no SQLite access. It calls backend APIs: games/positions through
`frontend/src/features/viewer/positionApi.ts:124-125`, evaluation through
`frontend/src/features/viewer/analysisApi.ts:338-388`, position context through
`positionContextApi.ts:133`, opening lines through
`frontend/src/features/openings/openingsApi.ts:179-180`, move distributions through
`frontend/src/features/move-response-distribution/moveResponseDistributionApi.ts:228-229`, and preferred moves
through `frontend/src/features/repertoire-builder/preferredMoveApi.ts:236-286`. Future documentation should record
these as API-to-backend-to-table paths, not as direct table readers.

## Relationships, blockers, and destructive behavior

The generated schema is the structural authority for all composite keys and foreign keys. The principal reverse
dependency chains are:

- `players` is a parent of `games` (white and black UUIDs), `corpus`, and preferred-move/tracked-player identities.
- `games` is a parent of `corpus_game` and `position_occurrence`; `corpus` is a parent of `corpus_game`, `corpus_run`,
  and many manifest/corpus-scoped state and projection records.
- `position_state` is a parent of `position_occurrence` and both preferred-move event tables. `position_occurrence` is
  referenced by classification anchors/routes and recurrence occurrences/events.
- `opening_source_manifest` is a parent of source files, catalogue state/catalogue rows, relationship state/run and
  positions, classification state/run, and recurrence state/run. `opening_source_file` is a parent of catalogue rows
  and source-row relationship/classification/recurrence records.
- `opening_catalog` is a parent of relationship memberships, parent/transposition links, classification anchors, and
  recurrence route projections. Classification game -> anchor -> route is a child chain; classification state is an
  input parent for recurrence state/game -> occurrence -> route/branch events.
- `analysis_result` is the only declared cascading parent: deleting one result cascades to its
  `analysis_candidate` rows. `analysis_batch_run` is the parent of `analysis_position_failure` with `NO ACTION`, and
  append-only triggers independently prevent deleting or updating both audit tables.
- Preferred-move events point with `NO ACTION` to `players` and the exact composite `position_state` identity, and
  their triggers prevent update/delete. Most other foreign keys also use `NO ACTION`.

This means parent deletion may fail when child rows exist, even where a relationship is only logically represented by
manifest/corpus columns rather than a declared foreign key. The future relationship document must list both declared
and logical dependencies, in both directions, and explain safe deletion order. Foreign-key enforcement is enabled by
the production initializers and adapters via `PRAGMA foreign_keys = ON`; arbitrary raw SQLite connections must not be
assumed to enforce it.

Known destructive or risky paths include:

- `_persistence.py:88-116,119-139` deletes corpus membership, unshared game occurrences, and orphan position states.
  `_clear_corpus` is defined but was not observed in the current `extract_corpus.publish` path; its invocation status
  remains uncertain and it must not be treated as safe cleanup.
- `extract_corpus.py:80-130` removes changed/removed game-derived rows inside `BEGIN IMMEDIATE`; rollback paths are
  at `:148-193`. A separate run-history write can survive or follow the publication transaction.
- Relationship, classification, and recurrence publication delete and rebuild one scope inside a transaction
  (`relationship_persistence.py:223-327`, `classification_persistence.py:175-247`,
  `recurrence_persistence.py:429-487`). A failure should roll back that scope, but each accepted namespace has its
  own transaction.
- `analysis/schema.py:286-320` is a destructive version-1-to-version-2 migration: it deletes analysis candidates,
  analysis results, and evaluation queue rows, drops their tables, recreates them, and updates schema versions.
- `fetch_games.py:237-243,278-305` resets `fetch_state.is_current` before marking the selected month, and writes raw
  JSON outside the database transaction.
- `evaluation/queue.py:51-65` and analysis persistence use `BEGIN IMMEDIATE`, rollback, and bounded busy retries.
  Backend read adapters use read-only URIs; preferred-move writes use `mode=rw` with timeout zero.
- The `-wal`, `-shm`, and `.analysis.lock` files are operational state. The lock may indicate an active or stale
  analysis owner; it must never be removed as documentation cleanup.

## Transaction and failure notes

- Fetch schema creation commits explicitly; fetched months use separate transactions, so a successful month may remain
  after a later month fails. Network/raw-file effects are outside the SQLite transaction.
- Corpus schema/subject initialization uses connection context transactions. Corpus publication first writes run history
  in short commits, then uses `BEGIN IMMEDIATE` for reconciliation and validation. The CLI opens with `timeout=0`, so
  contention fails fast as `CorpusBusyError`.
- Opening catalogue and derived publishers use connection context transactions, delete old scoped rows, insert the new
  facts, mark the run successful, and insert accepted state. Failed runs are recorded separately where implemented.
- Preferred-move single writes use a connection transaction; line writes use `SAVEPOINT preferred_move_line` with
  rollback-to-savepoint on failure (`preferred_move.py:282-327`).
- Analysis result/candidate publication and batch/failure append use explicit immediate writer transactions
  (`analysis/repository.py:90-170,172-243`). Evaluation transitions use the shared immediate transaction helper with
  three short busy retries (`evaluation/queue.py:51-65`).
- The stopped refresh script delegates corpus, classification, and recurrence separately and does not provide
  cross-stage rollback (`refresh_chess_com.py:348-368`). This is a risk to document as historical code behavior only,
  not an approved refresh design.

## Current population and use snapshot

The following values were obtained through finite, read-only queries against the runtime database. They are evidence
for later review, not durable truth and should be refreshed before any pruning decision:

- `analysis_result`: 201,178; `analysis_candidate`: 992,749; `analysis_batch_run`: 5;
  `analysis_position_failure`: 6; `evaluation_queue`: 1.
- `corpus`: 1; `corpus_run`: 3; `fetch_state`: 31; `position_occurrence`: 639,262.
- `opening_source_manifest`: 1; `opening_source_file`: 5; `opening_catalog`: 3,810;
  `opening_position_membership`: 36,925; `opening_parent_link`: 3,790; `opening_transposition_link`: 12,077.
- `opening_recurrence_game`: 12,365; `opening_recurrence_position_projection`: 1,022,770;
  `opening_recurrence_route_projection`: 4,038,362;
  `opening_recurrence_branch_projection`: 1,054,491;
  `opening_recurrence_route_branch_projection`: 4,158,509.
- `opening_preferred_move_event`: 13; `opening_preferred_move_requirement_event`: 3. Each live schema/state table
  was observed as present, generally with its singleton or accepted row.

Counts for the very large `games`, `players`, `corpus_game`, `position_state`,
`opening_recurrence_occurrence`, `opening_recurrence_route_event`, and
`opening_recurrence_branch_event` tables were not retained because bounded count attempts exceeded their finite
timeouts. A future documentation pass must record those as measured values or explicitly unknown, never infer them.

## Hypotheses for later waste/redundancy review

These are hypotheses, not deletion recommendations:

| Candidate | Evidence | Confidence and required caution |
|---|---|---|
| Abandoned tracked-player declarations | Nine tables exist in `tracked_player_schema.py` but are absent from the live database and supported generator; the archived outcome says they were abandoned. | High confidence that they are non-live; historical source/tests must be preserved until separately approved cleanup. |
| `analysis_batch_run` and `analysis_position_failure` retention | The runtime has 5 and 6 rows. Production code writes them and append-only triggers protect them; no production reader was found in the retained search. | High confidence that they are audit-only/write-only in current application use. Review retention policy, not table deletion, later. |
| `analysis_candidate.fen` repeated data | Every candidate is written with the result FEN, while result reading uses the parent result FEN and candidate fields; direct candidate-FEN consumption was not found. | Low/medium confidence possible column redundancy; validate compatibility and historical meaning before any change. |
| Recurrence event and projection layers | Projection tables are very large and are rebuildable from recurrence facts/events, while backend APIs read projections. | Medium confidence that some storage is derived/rebuildable; events may be required for provenance and deterministic rebuilds. No removal is safe without a retention and rebuild decision. |
| Classification route versus recurrence route event data | Both carry route identities and position/move fields; recurrence publication explicitly derives from classification and stores authoritative recurrence events. | Medium confidence structural overlap; likely intentional boundary preservation. Confirm all rebuild and audit uses first. |
| Fetched games outside accepted membership | `fetch_games.py` stores fetched games broadly, while `_history.py:_select_games` accepts only chess games involving the configured subject. | Medium/low confidence cache-retention candidate; excluded rows may be needed for future policy or provenance. |
| `_clear_corpus` | It contains broad deletion logic but was not observed in the active publish path, which uses targeted removal helpers instead. | High risk if called; invocation/dead-code status must be confirmed before any cleanup or refactor. |

The opening run/state tables, `fetch_state`, source manifests, and position tables should not be called waste merely
because they are historical, singleton, cached, or derived: each has observed contract or dependency uses. The future
register must distinguish “not directly read by an API” from “unused.”

## Proposed durable documentation set

The next focused Plan should create one linked set under `docs/database/`:

- `docs/database/README.md`: scope, database files/sidecars, configuration, live/non-live terminology, and navigation;
- `docs/database/table-catalog.md`: one actual-name entry for every live and declared non-live table, including
  column meanings, keys, constraints, owner, readers, writers, lifecycle, and risk;
- `docs/database/usage-matrix.md`: path/symbol references for all scripts, backend features, API routes, frontend
  indirect callers, tests, and historical/stopped references;
- `docs/database/relationships-and-lifecycle.md`: forward and reverse dependency map, foreign-key blockers, logical
  dependencies, mutation ordering, transactions, locks, rollback, and destructive effects; and
- `docs/database/pruning-register.md`: evidence, population snapshot, confidence, validation needed, and explicit
  non-recommendation status for every possible candidate.

The existing generated `data/database/schema.txt` should remain the structural companion, not be overloaded with
runtime use narratives. `docs/README.md` should link the new landing page after approval.

## Exhaustive future completeness method

1. Enumerate live objects from read-only `sqlite_master`, then enumerate the supported in-memory DDL through
   `dump_schema.py`; compare names, counts, columns, indexes, triggers, foreign keys, and views.
2. Enumerate every additional DDL definition in repository Python, including `tracked_player_schema.py`, migration
   helpers, temporary test fixtures, and legacy schemas. Mark each object live, supported-but-empty, declared
   non-live, test-only, legacy, or historical.
3. Search backend, scripts, frontend API code, tests, and docs for exact table names and for SQL/SQLite patterns:
   `CREATE`, `DROP`, `ALTER`, `INSERT`, `UPDATE`, `DELETE`, `REPLACE`, `ON CONFLICT`, `executemany`, `sqlite_master`,
   `PRAGMA`, read-only URIs, connection opens, commits, savepoints, and locks. Resolve dynamic table constants and
   aliases manually.
4. Create one usage record for every relevant reference, classified as reader, writer, schema validator, test fixture,
   historical record, or stopped/unaccepted code. Map frontend endpoints only through their backend feature.
5. Generate a bidirectional FK graph from `PRAGMA foreign_key_list`/DDL and add logical edges not enforced by SQLite,
   especially manifest/corpus-scoped relationships and derived projections. Record delete behavior in both directions.
6. Record mutation style, transaction boundary, failure/rollback behavior, owner, lifecycle, lock/timeout, and
   destructive effect for every table with writes or cleanup.
7. Capture a read-only population snapshot with command, date, database path, and finite timeout. Separate measured
   counts from unknown counts and never include raw sensitive rows.
8. Run a focused documentation validator that proves every discovered table has an exact catalogue entry, every
   relevant code reference has a usage record, every FK/logical edge appears in both directions, all live indexes and
   triggers are covered, and no candidate section is phrased as authorization to delete.

The finite discovery command retained for the next pass is:

```text
timeout 45s ".venv/Scripts/python.exe" scripts/scout_db_query.py "SELECT type, name, tbl_name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
```

Its bash tool timeout must be `45000` ms. A focused structural regression command is:

```text
timeout 60s ".venv/Scripts/python.exe" -m pytest tests/database/test_schema.py -q
```

Its bash tool timeout must be `60000` ms. No broad lint, build, type, aggregate, live-network, or full Stockfish run is
needed for documentation proof.

## Exclusions and approvals still required

This synthesis does not authorize:

- deletion, archival, compaction, retention changes, or schema/data migration;
- changes to `chess_games.db`, WAL/SHM files, lock files, raw data, or backups;
- changes to product APIs, frontend behavior, scripts, configuration ownership, or the stopped refresh direction;
- removing or rewriting abandoned tracked-player code or historical Plans/grilling records;
- treating any candidate as redundant without owner confirmation, dependency analysis, backup/recovery proof, and a
  separately approved acceptance policy; or
- commit, push, destructive Git operation, or unrelated cleanup.

User approval is required before any pruning, retention policy, schema/data change, behavior change, ownership change,
or attempt to revive the rejected refresh design. The present deliverable is only a durable handoff for that later,
auditable documentation effort.
