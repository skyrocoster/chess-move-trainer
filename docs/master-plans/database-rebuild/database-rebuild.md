# Database rebuild

> **Status:** completed database foundation and `SETUP-01`; `SETUP-02` is next
> **Acceptance:** The rebuilt foundation and automatic preferred-move setup were accepted on 2026-09-08.

## Purpose and current starting point

The database rebuild is complete. The repository now has one package-owned SQLite foundation at
`data/database/chess.db`, populated with the accepted real game and opening data and proven through direct reads and
separate bounded Stockfish analysis. This document records that foundation as one completed capability; it no longer
uses the historical DB-01 through DB-09 sequence as its organizing structure.

The next selectable work is `SETUP-02` grilling for tools that control and manage APIs. This document does not authorize
that work, application integration, physical database activation, old-database cleanup, or deletion. Each later outcome
remains separately gated by its required grilling, coordinator approval, and a focused Plan when nontrivial.

## Completed database foundation

### Package ownership and supported operations

The importable package under `src/chess_move_trainer/database/` owns the rebuilt database behavior. Its ownership is
split into cohesive services with shared behavior below the thin Typer adapters:

- `connection.py`, `schema.py`, `inspection.py`, `publication.py`, `lifecycle.py`, and `statistics.py` own explicit
  SQLite access, schema creation/inspection, generated publication, the fixed lifecycle, and measurements.
- `positions/` owns legal position validation, canonicalization, and opaque transaction-scoped position resolution.
- `games/` owns Chess.com archive acquisition, retained raw-month storage, normalization, persistence, and reads.
- `openings/` owns the fixed five-file source, acquisition, normalized catalogue publication, and lookup/replay.
- `preferred_moves/` owns current period normalization, resolution, and atomic storage edits.
- `analysis/` owns normalized result validation, current result/line publication, and reads.
- `stockfish/` owns configuration, engine process control, the database mutex, target selection, queue, benchmark,
  bulk analysis, and worker execution. `rebuild/proof.py` contains the retained read-only proof helpers.

The supported command family is entered with `python -m chess_move_trainer.database` and currently exposes:

- `schema create` and `schema inspect` for explicit-path schema work and deterministic inspection;
- `openings lookup` and `openings replay` for isolated database-level opening recognition;
- `preferred-moves list`, `resolve`, `set`, and `unset` for current dated preference storage;
- `stockfish benchmark`, `bulk`, and `worker` for benchmark artifacts, direct on-demand publication, and queued work.

Only three commands are public **data-loading lifecycle workflows**:

```text
python -m chess_move_trainer.database setup
python -m chess_move_trainer.database update games
python -m chess_move_trainer.database update openings
```

The lifecycle adapters use the fixed destination and return useful automation-safe output and exit status. Other
operator commands take explicit database or input paths as appropriate. CLI adapters contain no business logic, and no
required database operation is canonical under `scripts/`.

### Database and position boundary

The current schema is version 1 with exactly these ten catalogue tables:

```text
datasource_game
derived_position
derived_game_position
datasource_opening
derived_opening_route
derived_opening_route_move
derived_analysis_result
derived_analysis_line
derived_analysis_queue
datasource_preferred_move_period
```

The schema also has `PRAGMA user_version = 1`, the catalogue constraints and indexes, and no feature-specific schema,
run, history, projection, manifest, or audit table families. `derived_position` gives every valid position one stable
identity from placement, side to move, castling rights, and the fully legal en-passant square. Halfmove and fullmove
counters are stored on game occurrences but are not part of position identity.

`schema_v1.sql` is the executable DDL and `data/database/schema.md` is the generated current reference. The checked-in
`data/database/schema.txt` still describes the older multi-table DDL and old script owners; it is retained evidence,
not a basis for present-tense claims about the rebuilt runtime database. Package connections use explicit paths,
foreign-key enforcement, finite SQLite lock waits, and read-only access where inspection or reading requires it.

### Games, raw sources, and occurrences

Chess.com acquisition is package-owned. It discovers the participant archive, validates the exact HTTPS month URLs, and
stores retained raw responses under `data/chess-com/raw/games/YYYY/MM.json`. Existing historical month files are the
ledger and are skipped. The newest saved month is refetched during `update games`; its valid response is merged by
Chess.com UUID so new and corrected games are included while omitted local games remain. Later missing months through
the current month are acquired independently. Every candidate month is validated before an atomic same-directory raw
file publication, so a malformed or incomplete response cannot replace the prior usable file.

Normalization filters and validates games before persistence. Accepted standard games publish `datasource_game`,
`derived_game_position`, and shared `derived_position` rows. A normal update commits each accepted game independently;
corrected game facts are replaced atomically. `setup` uses the complete retained source set and bulk-imports the
accepted game data in one outer database transaction. Invalid games are reported rather than destructively omitted, and
raw sources remain independent of normalized acceptance.

### Openings and direct recognition

Opening acquisition resolves one current commit from the fixed Lichess `chess-openings` source, retrieves `a.tsv`
through `e.tsv`, stages and validates the complete five-file set, and publishes the source files with rollback-protected
file swaps. Windows cannot make the whole directory swap atomic, so an abrupt crash during those swaps can expose a
mixed revision that an idempotent rerun repairs. The database catalogue replacement is one transaction: labels, routes,
contiguous route moves, and canonical endpoint positions are published together. An invalid or incomplete source leaves
the prior valid catalogue usable.

`openings lookup` recognizes a complete FEN without writing, and `openings replay` replays one standard-start PGN.
Recognition returns ordered labels and the current label while distinguishing exact route matches from transpositions,
matching persisted canonical endpoints without exposing unreached future variations. This is an isolated package/tool
capability, not the excluded Opening Line Library HTTP surface.

### Preferred-move storage

`datasource_preferred_move_period` stores normalized half-open UTC calendar-date periods. A period can contain a legal
preferred move or an explicit no-preference value; a date with no row is unconfigured. The package supports listing,
resolving, setting, and unsetting periods with legal-position validation, overlap-safe normalization, and atomic writer
transactions.

The package now also supports `preferred-moves setup`, the fixed empty-schedule-only inference command accepted in
SETUP-01. It examines trainer moves in the first 30 plies through rolling 90-day windows, requires at least 21 matching
plays and an inclusive 80-percent share, validates the complete result, and writes it atomically without a proposal or
review step. The accepted real invocation populated 108 periods across 91 positions; any later invocation refuses the
now-nonempty schedule.

### Analysis, queue, and Stockfish

The package validates and atomically publishes one current complete `derived_analysis_result` and its
`derived_analysis_line` children per canonical position, enforcing terminal behavior, legal complete lines, quality,
and no-downgrade rules. `derived_analysis_queue` is a live six-column queue with queued/running states, claim tokens,
finite stale-claim recovery, and no persisted failure or run history.

`stockfish benchmark` runs an explicit resumable benchmark and writes contained artifacts. `stockfish bulk` selects
eligible positions on demand and publishes results directly; `stockfish worker` drains queued requests. Bulk and worker
engine work is serialized behind the database mutex, while the benchmark remains a separate artifact-producing
operation. All Stockfish work is separate from the three setup/update workflows. Setup and updates never run Stockfish
or populate analysis as a side effect.

### Direct lifecycle and transaction boundaries

The fixed direct lifecycle is deliberately small:

- `setup` succeeds only when `data/database/chess.db` is absent. It creates schema v1, acquires/uses the retained game
  sources and latest valid opening source, imports the data, and performs only quick local checks. If setup fails after
  creating the file, it removes only that newly created database and its exact sidecars; it does not remove sources or
  replace a pre-existing database.
- `update games` uses the retained raw-month ledger, refetches and merges the newest saved month, fills later months,
  and imports each published month through independent transactions. It does not persist fetch-state, ETags, or a
  current-month flag.
- `update openings` validates the complete five-file source before replacing the catalogue in one transaction and does
  not change game data.

Full integrity checks, measurements, direct capability queries, and Stockfish analysis are separate from setup and
updates. The supported lifecycle uses only the fixed database file and has no alternate-file operation, replacement or
swap, snapshot, rollback, recovery, reset, dedicated rebuild, replacement-readiness, or separate verification workflow.
For a rare full rebuild an operator deliberately moves or removes the fixed database outside these commands and then
runs `setup`; no command automates that destructive action.

### Accepted real-data proof

The accepted database at `data/database/chess.db` contains:

```text
12,710 games
530,725 canonical positions
657,654 game-position occurrences
3,329 opening labels
3,810 opening routes
36,925 route moves
1 analysis result with 5 candidate lines
108 preferred-move periods across 91 positions
0 queued analysis requests
```

The source ledger covered 32 months and 12,716 records: 12,710 accepted games and 6 explicitly rejected games, with
zero duplicate normalized, source, or database identifiers and exact UUID-to-start-month agreement. Integrity checks
passed (`integrity_check = ok`, no foreign-key violations), the accepted database remains `DELETE` journal mode with
`FULL` synchronous setting and no journal/WAL/SHM sidecars, and the measured direct access paths passed their proof
thresholds. The retained focused evidence includes the 512-game/2,560-occurrence regression under one second, the
ledger-only proof, and complete DB-09 proof. A separate bounded Stockfish 18 Tool-profile run published the one result
and five lines above. SETUP-01 later examined all 12,710 accepted games, skipped none, reported seven positions with
overlapping qualifying evidence, and atomically applied the 108 preferred-move periods. No API, frontend, application
cutover, broad maintenance run, or old-database operation was part of either acceptance.

### Safety and application boundary

No rows migrate from the old database. Raw month files and historical workflow records remain retained, the old
database remains unmodified, and legacy scripts remain read-only noncanonical evidence until separately authorized
retirement. No new table or schema machinery is introduced outside the ten-table catalogue.

The clean package currently targets `data/database/chess.db`. The existing application still has bounded legacy
consumer references: `backend/app/features/positions/repository.py:10-11` defaults to `data/database/chess_games.db`
and permits `CHESS_DATABASE_PATH`, while current backend feature consumers and the registered
`/api/openings/line-library` surface still describe the old application boundary. The rebuilt package proof did not
change backend, frontend, HTTP contracts, or application routes. Those consumers are future replacement touchpoints,
not evidence that the application has already cut over.

## Historical evidence and provenance

The following completed records are preserved as historical proof and are not selectable slices or current lifecycle
instructions:

- [DB-01 Plan](../../plans/done/database-rebuild-db-01/database-rebuild-db-01.md)
- [DB-02 Plan](../../plans/done/database-rebuild-db-02/database-rebuild-db-02.md)
- [DB-03 Plan](../../plans/done/database-rebuild-db-03/database-rebuild-db-03.md)
- [DB-04 Plan](../../plans/done/database-rebuild-db-04/database-rebuild-db-04.md)
- [DB-05 Plan](../../plans/done/database-rebuild-db-05/database-rebuild-db-05.md)
- [DB-06 Plan](../../plans/done/database-rebuild-db-06/database-rebuild-db-06.md)
- [DB-07 Plan](../../plans/done/database-rebuild-db-07/database-rebuild-db-07.md)
- [DB-08 Plan](../../plans/done/database-rebuild-db-08/database-rebuild-db-08.md)
- [DB-08A Plan](../../plans/done/database-rebuild-db-08a/database-rebuild-db-08a.md)
- [DB-09 Plan](../../plans/done/database-rebuild-db-09/database-rebuild-db-09.md)
- [SETUP-01 Plan](../../plans/done/database-rebuild-setup-01/database-rebuild-setup-01.md)

The governing evidence is:

- [`database-rebuild-simple-lifecycle.md`](../../grilling-docs/database-rebuild-simple-lifecycle.md) for the fixed
  direct lifecycle;
- [`database-rebuild-direction.md`](../../grilling-docs/database-rebuild-direction.md) for approved product and data
  direction;
- [`database-rebuild-schema.md`](../../grilling-docs/database-rebuild-schema.md) and
  [`data/database/schema.md`](../../../data/database/schema.md) for the catalogue boundary;
- [`database-rebuild-db-09.md`](../../grilling-docs/database-rebuild-db-09.md) for the accepted direct proof handoff;
- [`database-rebuild-setup-01.md`](../../grilling-docs/database-rebuild-setup-01.md) for the approved simple automatic
  preferred-move inference direction;
- the current package source and focused database tests for implemented behavior, not for reopening completed scope.

## Completed SETUP-01

### Automatic preferred-move setup inference

**In plain English:** Use obvious repeated choices in real rebuilt play data to initialize preferred-move periods with
one simple, explicit, empty-schedule-only command.

The approved [SETUP-01 grilling handoff](../../grilling-docs/database-rebuild-setup-01.md) and
[completed Plan](../../plans/done/database-rebuild-setup-01/database-rebuild-setup-01.md) govern the result. The focused
inference, database, and CLI proofs passed, and the one real invocation applied 108 periods across 91 positions. The
fixed command now refuses to run again because the schedule is nonempty. It added no schema, history, proposal, update,
legacy, API, frontend, or application behavior.

## Selectable future work

Select one outcome at a time. Its required grilling must produce a coordinator-approved handoff before implementation
work or a nontrivial focused Plan begins. This sequence starts from the completed foundation and SETUP-01 above.

| Outcome | Human-visible result | Depends on | Boundary that remains true |
|---|---|---|---|
| SETUP-02 | New approved tools for controlling and managing APIs are explored and installed, with downstream API slices amended as needed. | SETUP-01 accepted | No pre-existing API is silently redesigned here. |
| API-01 | The game viewer reads rebuilt game metadata and ordered occurrences through a new backend contract. | SETUP-01 accepted | No old database fallback or old contract compatibility solely for migration. |
| API-02 | Position Context and Move Response Distribution read rebuilt tables directly, with distinct-game and occurrence meanings preserved. | API-01 accepted | No recurrence, branch, or materialized statistics dataset without a new approved requirement. |
| API-03 | Viewer Analyze, Update, and Retry use the rebuilt queue and current analysis results. | API-02 accepted | No old queue, batch history, partial-result, or downgrade contract. |
| API-04 | The repertoire application reads and edits dated preferred-move periods, including no-preference and unconfigured states. | API-03 accepted | No future preference-history editor or historical-game evaluation. |
| CUT-01 | A separately assessed application activation and live proof make the rebuilt database active while preserving the old database. | API-04 accepted | Exact physical activation, configuration, switch, rollback, and the required handling of the excluded Opening Line Library route require fresh grilling; this document does not choose them. |
| RETIRE-01 | After accepted cutover, remaining old-database references are cleaned and the old database is deleted only after separate immediate authorization. | CUT-01 accepted | Exact file inventory, backup/restore, cleanup, and deletion proof require fresh grilling; raw sources and historical records are never deleted. |

Application integration, physical activation, rollback design, and old-database retirement remain future work. The
registered `/api/openings/line-library` surface remains excluded rather than rebuilt; any future activation assessment
must account for its current old-schema registration before activation. Nothing in this master plan authorizes a
cutover, deletion, or cleanup operation.

## Continuing exclusions

- No migration or modification of old database rows; no raw-source deletion; raw-source changes are limited to the
  supported safe game-month and opening-source acquisition/publication behavior already described; no unrelated
  raw-source mutation is authorized. No deletion of historical workflow records.
- No expansion beyond the exact ten-table schema catalogue and no fetch-state, manifest, source-history, classification,
  recurrence, hierarchy, projection, audit, batch, failure, or per-feature state/run table families.
- No Opening Line Library application endpoint, page, integration, or rebuild.
- No opponent-profile work under `data/chess-com/raw/profiles/`.
- No preferred-move inference/application outside the accepted fixed, empty-schedule-only SETUP-01 command; no inferred
  no-preference values and no fabricated or migrated preference rows.
- No legacy database tool is patched, wrapped, imported, copied, or made a fallback. Legacy files remain evidence until
  a separately authorized retirement outcome.
- No application/API/frontend integration is authorized merely because this foundation is complete; each later outcome
  remains separately gated, and no cutover or destructive operation is authorized by this document.
- No loose one-off script becomes canonical for database behavior, and no commits, pushes, branches, worktrees, stashes,
  or unrelated record changes are implied.
