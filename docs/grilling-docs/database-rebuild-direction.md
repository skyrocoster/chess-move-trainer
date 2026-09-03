# Database rebuild direction

> Decision evidence recorded and extended on 3 September 2026. This document defines the agreed discovery boundary
> for rebuilding the database table by table. It is not a Plan and does not authorize database deletion, schema
> changes, data migration, application changes, cutover, or implementation.

## 1. Authority, intent, and survival rule

### 1.1 Intent

Rebuild the database and all related APIs, scripts, and tools from first principles. The existing application now
provides enough real usage to identify what data is needed and how it must be accessed. Existing tables and pipelines
are evidence of what was previously attempted; they are not architecture that must be preserved.

The rebuild must understand every surviving data field and use. It should remove accidental complexity, unsupported
history, speculative projections, and machinery added for abandoned or failed directions.

### 1.2 What may justify persisted data

A table or persisted derived dataset is justified only by:

1. a current application capability; or
2. a tool the user actively uses.

Version one preserves current, demonstrated user capabilities rather than current internal contracts. Existing API
paths, request shapes, response shapes, schemas, and models may be replaced. Frontend and backend contracts may change
together.

Reachable code, tests, documents, old Plans, and historical scripts are evidence, not proof that a capability or table
must survive. New capabilities will be designed separately when their requirements exist. This rebuild must not add
speculative foundations for them.

### 1.3 Reset boundary

- No rows from the current database will migrate.
- Raw external source files are the only retained inputs.
- Existing Stockfish analysis, classifications, projections, queues, run records, preferred moves, and all other
  database content will be discarded rather than migrated.
- Required tool-derived data will be regenerated using rebuilt tools.
- These decisions do not authorize deletion or modification of the current database or any source file. The existing
  system remains evidence until a separately approved replacement process establishes what may be removed.

Newly generated derived data may still be persisted. Persistence is decided by actual usage and practical cost.
Expensive Stockfish output is worth storing, while cheap statistics may be calculated on demand. “Derived” does not
automatically mean disposable, and “currently stored” does not automatically justify persistence.

## 2. Database-wide direction

These rules apply across the table areas that follow. They are settled direction, not final DDL or an implementation
sequence.

### 2.1 Operating boundary

- The application serves one local trainer. Other chess players are not application users.
- The backend, import and rebuild tools, Stockfish workers, and maintenance processes may run concurrently on one
  Windows computer.
- Network-scale multi-user operation is not required.
- No API should be built before an actual application requirement needs it.
- All persisted timestamps use UTC. UK date and time formatting is a presentation concern only.
- The application may enter maintenance mode during core rebuild work.
- Optional Tool analysis may remain incomplete when an otherwise valid rebuilt database becomes active.

### 2.2 Physical database and technology

The rebuilt database uses SQLite. Assessment did not identify SQLite as the underlying problem in the existing system.
The more evident problems are fragmented schema ownership, speculative materialized data, large projections, and
complicated publication and history machinery.

Embedded storage is preferred for this single-user local application. PostgreSQL or another managed service is
acceptable only if measured concurrency, integrity, performance, or operational requirements show that the rebuilt
SQLite workload cannot be served safely.

The design uses **one physical database**, not separate generated-data and user-state databases. Cross-database joins
and the loss of enforceable foreign keys would add more complexity than the physical separation removes. Generated and
user-owned table areas must instead have clear logical ownership and lifecycle boundaries.

Keep the design simple. Add indexes only for real access paths and measure rebuilt queries against real rebuilt data.
Do not build synthetic performance laboratories around the old database.

### 2.3 Schema compatibility, snapshots, and rollback

- The database has one database-wide schema version. It does not have one `*_schema` table per feature or a permanent
  migration audit ledger. The exact storage shape of the database-wide version remains part of the later catalogue.
- Before a schema migration, bulk rebuild, destructive maintenance operation, or another operation capable of removing
  or replacing substantial data, create one consistent full database snapshot.
- Use the database engine's safe backup mechanism. For SQLite, do not copy a live `.db` file without accounting for WAL
  state; use SQLite's backup facility to produce a consistent snapshot.
- Keep a rolling maximum of the three newest pre-operation snapshots. Remove older snapshots only after the new
  snapshot has been verified.
- No scheduled backup is required. Same-drive snapshots protect against application and operator mistakes, not disk
  loss. Off-device disaster recovery is deferred until the application becomes genuinely live.
- Database snapshots do not protect raw source files. Raw-source filesystem backup remains a separate concern.

### 2.4 Rebuild, replacement, and failure behavior

- Initial creation and later refresh use the same idempotent tools. The initial build is a refresh against an empty
  database, not a separate code path.
- A tool skips work whose current output already satisfies its requirement and can resume expensive work without
  restarting the entire run.
- Structural source failures and foundational integrity failures stop the affected build.
- Isolated computational failures do not discard other successful work and remain retryable.
- Resumability state must support the actual retry workflow. It does not justify permanent batch histories, failure
  rows, or audit tables.
- Game import commits each valid game separately. Completed games survive interruption and a rerun continues safely.

The first redesigned database is built alongside the existing database. The existing database is not modified,
replaced, or deleted. Application cutover is separately approved. For later full rebuilds of the redesigned database,
build and validate a neighbouring replacement file before switching the application to it. A rebuilt database may
become active after games and openings are ready; it does not wait for all Tool analysis to finish.

### 2.5 Raw-source policy

- Do not introduce enterprise-style content-addressed storage, persistent file hashes, accepted-manifest pointers, or
  import audit histories without a current functional need.
- Replaceable external records use a latest-known snapshot model. A new profile fetch may replace the previous raw
  profile file rather than creating permanent profile history.
- Irreplaceable records such as individual games may have source-specific retention behavior.
- Raw Chess.com month files are the fetch ledger. Existing historical month files are skipped; the current month is
  fetched again. No database `fetch_state`, stored ETag, current-month flag, or fetch-history table is required.
- Refetching the current month merges raw games by Chess.com game UUID: previously fetched games remain, new games are
  added, and a corrected game replaces the earlier source representation. No per-game version history is retained.
- A schema version or minimal resumable-job state may exist when safe operation requires it. This is not blanket
  authorization for families of schema, run, or state tables.

## 3. Table-by-table rebuild areas

This section gives each justified persisted area one consistent home. Names and shapes shown here are conceptual unless
the text explicitly states a key or constraint. They do not replace the still-required actual-name and field catalogue,
and they do not settle column types, foreign-key actions, indexes, or DDL that this record does not already decide.

Each area answers the same questions:

- **Purpose and ownership:** why persistence exists and which kind of data it owns;
- **Conceptual shape and integrity:** only the fields, identities, and constraints already settled;
- **Write and lifecycle:** how rows are created, replaced, retained, or removed;
- **Read use:** which approved capability needs the rows; and
- **Keep out:** facts and machinery that must not be added to that area.

### 3.1 Database-wide schema version

**Purpose and ownership**

One database-wide version identifies schema compatibility for the physical database. This is database maintenance
metadata, not feature data and not a historical audit record.

**Conceptual shape and integrity**

The record settles only that there is one database-wide schema version. It does not settle whether this is represented
by a dedicated table, SQLite metadata, or another straightforward mechanism. That storage choice belongs in the later
actual-name and field catalogue.

**Write and lifecycle**

The version changes when the database schema changes. Safe schema operations follow the snapshot and rollback rules in
section 2.3.

**Read use**

Rebuilt application and maintenance processes use it only to determine database compatibility.

**Keep out**

- per-feature `*_schema` tables;
- a permanent migration audit ledger; and
- schema, run, and state table families inherited only from the previous pipeline structure.

### 3.2 `position`

**Purpose and ownership**

`position` owns canonical chess-position identity shared by games, opening endpoints, Stockfish analysis, queue work,
and preferred moves. It prevents each feature from inventing a different position key.

**Conceptual shape and integrity**

A unique position is identified by:

1. piece placement;
2. side to move;
3. castling rights; and
4. an en-passant square only where a **fully legal** en-passant capture exists.

```text
position
- position_id
- placement
- side_to_move
- castling_rights
- legal_en_passant

UNIQUE (placement, side_to_move, castling_rights, legal_en_passant)
```

`position_id` is an internal integer identity. Halfmove and fullmove counters do not participate in shared identity;
they belong to a game occurrence.

FEN en-passant markers are normalized to `-` when no legal capture exists, including when an adjacent pawn is pinned
and the apparent capture would expose or leave its king in check. A genuine legal en-passant capture retains the square.

Research against the pinned local versions found:

- python-chess 1.11.2 defaults to legal-only en-passant FEN generation and uses legal-only en-passant state for its
  repetition and transposition key;
- chess.js 1.4.0 defaults to legal-only en-passant FEN output;
- Stockfish 18 uses fully legal en-passant relevance in its normal move-generated repetition and hash behavior,
  although its FEN parser may retain a pseudo-legal pinned-pawn marker at the root; finite probes found no evaluation
  or legal-move difference after legal-only normalization; and
- the current repository deliberately uses classic `en_passant="fen"` behavior end to end, so legal-only normalization
  must be coordinated across rebuilt frontend and backend key producers rather than patched in isolation.

**Write and lifecycle**

Approved workflows create canonical positions as needed. In particular, game occurrences and opening endpoints refer
to them, analysis is keyed to them, and a preferred move may create a valid canonical position that does not occur in
an imported game or opening route.

Once created, a position is retained even when no game, opening, analysis, queue item, or preference currently points
to it. Permanent retention is a deliberate single-user simplification that preserves stable IDs and avoids cleanup
rules.

**Read use**

The game viewer, direct repertoire statistics, opening lookup, analysis, and preferred-move capabilities all join
through canonical position identity.

**Keep out**

- halfmove and fullmove counters;
- a duplicated full display FEN for each occurrence;
- Stockfish results or candidate lines;
- a redundantly stored trainer or opponent actor; and
- feature-specific position identities.

### 3.3 `game`

**Purpose and ownership**

`game` owns one normalized, trainer-oriented record for each accepted standard Chess.com game. It also retains the exact
source PGN because copying and sharing that PGN is a current requirement and because its headers, clock annotations,
comments, and formatting must remain available.

**Conceptual shape and integrity**

```text
game_id
chesscom_game_uuid
source_url
original_pgn
trainer_color
trainer_chesscom_uuid
opponent_chesscom_uuid       nullable
trainer_rating               nullable per-game snapshot
opponent_rating              nullable per-game snapshot
started_at_utc               nullable
ended_at_utc                 nullable
trainer_outcome              nullable: win | loss | draw
termination_reason           nullable
time_control_source          nullable, e.g. 120+1
time_class                   nullable, e.g. bullet | blitz | rapid
```

Each game has an internal integer `game_id`. Its Chess.com game UUID remains unique and searchable so users may continue
loading or sharing by external UUID while occurrence rows use a compact integer foreign key.

The configured trainer Chess.com UUID is currently `0101b08a-ce8b-11ee-b2fd-e90263e5548c`. Accepted games retain that
identity and the trainer's color because trainer color is required for core statistics. The intake skip rule is in
section 4.1. The opponent UUID is optional and must be NULL when unavailable rather than causing an otherwise valid
game to be rejected.

A game with valid moves may still be imported when its start time, end time, trainer outcome, rating, termination
reason, or time class is unknown. Consumers must handle these nullable facts explicitly. When PGN and Chess.com's
separate numeric end timestamp disagree, use Chess.com's numeric timestamp while preserving the exact PGN.

Game-archive participant UUID is the selected source identity for trainer and opponent because it exists in-band on all
24,738 participant objects across the retained 12,369-game archive and was stable for repeated accounts. It is
undocumented on the monthly archive endpoint, so this is strong local evidence rather than a vendor guarantee. Profile
`player_id` is documented as non-changing but is absent from game archives and requires profile fetching, which is
excluded. There is no known direct UUID-to-`player_id` mapping.

**Write and lifecycle**

Only standard chess games starting from the normal initial board enter `game`. Retention is additive by Chess.com game
UUID: omission from a later monthly response does not remove an earlier raw or normalized game. A valid corrected
response replaces only that game's normalized metadata and occurrences, after complete validation, in one transaction.
An invalid correction leaves the previous working normalized game intact. No per-game version history is retained.

**Read use**

The game viewer reads normalized game metadata and exact PGN. Position Context and Move Response Distribution use
trainer color and the relationship to ordered occurrences.

**Keep out**

- a normalized opponent display-name column;
- a shared players or opponents table;
- `rated`, `tcn`, Chess.com's ECO URL, White or Black accuracy, tournament, and match fields;
- initial and final FEN columns; and
- other player or source details that have no current runtime reader.

Excluded source facts remain in raw JSON and, where present, the exact PGN.

### 3.4 `game_position`

**Purpose and ownership**

`game_position` owns one ordered occurrence of a canonical position inside a normalized game. It preserves the sound
separation between one deduplicated row per unique position and one row per occurrence in a game.

**Conceptual shape and integrity**

```text
game
  └── game_position(game_id, ply, position_id, move_uci, halfmove_clock, fullmove_number)
                           │
                           └── position
```

Each `(game_id, ply)` occurrence is distinct. An occurrence stores the move **leaving** that position, not the move that
entered it. For a game with N moves there are N+1 occurrence rows and N non-null outgoing UCI moves. The initial
occurrence has no incoming move; the final occurrence has no outgoing move. The move entering an occurrence is the
previous occurrence's outgoing move.

If a position repeats in one game, all occurrences refer to the same `position_id` while remaining distinct by game and
ply. A full display FEN is reconstructed from the shared four-field position identity plus the occurrence's halfmove and
fullmove counters. SAN is derived from the source position and UCI move.

**Write and lifecycle**

The game importer writes all occurrences for one fully validated game. Each valid game commits separately. A successful
game correction replaces that game's metadata and complete occurrence set in the same transaction; an invalid
correction does not disturb the working rows.

**Read use**

The viewer uses ordered occurrences for navigation. Direct repertoire statistics count games or occurrences from these
rows. Bulk Tool analysis uses their occurrence counts to prioritize positions.

**Keep out**

- an incoming move duplicated from the previous row;
- SAN duplicated beside UCI;
- full FEN text duplicated for every occurrence;
- opening classifications, recurrence copies, or branch projections; and
- a stored trainer or opponent actor.

Storing both incoming and outgoing moves would duplicate one fact on adjacent rows and permit contradictions.

### 3.5 `opening`

**Purpose and ownership**

`opening` owns one semantic opening label from the retained `lichess-org/chess-openings` source. Labels are reference
data for current opening lookup, not game classification or repertoire-statistics machinery.

**Conceptual shape and integrity**

```text
opening
- opening_id
- eco
- name

UNIQUE (eco, name)
```

Identical ECO and name rows become one opening even when the source supplies multiple move routes to that label.

**Write and lifecycle**

The opening catalogue is generated from the latest complete validated source set. It mirrors that source: labels no
longer present are not preserved merely as catalogue history. The opening tables are published together as one unit;
one malformed or illegal route rejects the entire update and leaves the previous working catalogue active.

Canonical positions, Stockfish analysis, and preferences survive an opening-source removal or change.

**Read use**

Opening lookup returns semantic labels reached by route or endpoint recognition. The game viewer may derive an opening
from normalized move history without storing a per-game classification.

**Keep out**

- a permanent `parent_opening_id`;
- game-classification state;
- recurrence or position-branch projections; and
- source history retained only for auditing.

### 3.6 `opening_route`

**Purpose and ownership**

`opening_route` owns one source move sequence that reaches an opening label. One opening may have multiple routes.

**Conceptual shape and integrity**

```text
opening_route
- route_id
- opening_id
- endpoint_position_id
```

The route refers to its semantic `opening` and its unique canonical endpoint `position`. Opening relationships are
route-dependent because routes can transpose, the same position may match multiple labels, and sequence ancestry can
differ from position ancestry.

**Write and lifecycle**

Routes are rebuilt and published with the complete opening catalogue. Removed or changed routes do not remain in the
active catalogue.

**Read use**

Route identity supports the visible distinction between an exact source-sequence `route` match and a different
sequence reaching the same endpoint as a `transposition` match.

**Keep out**

- a shared-prefix tree;
- one forced permanent opening hierarchy;
- a permanent parent opening;
- a position link for every intermediate ply; and
- historical route versions.

A shared prefix tree is unnecessary complexity for tens of thousands of route moves.

### 3.7 `opening_route_move`

**Purpose and ownership**

`opening_route_move` owns the explicit ordered UCI moves belonging to one opening route.

**Conceptual shape and integrity**

```text
opening_route_move
- route_id
- ply
- move_uci

PRIMARY KEY (route_id, ply)
```

The explicit child rows preserve order and permit normal validation. One opaque text or JSON move sequence is rejected.

**Write and lifecycle**

Rows are generated by replaying the source PGN for a route and are replaced as part of the complete opening-catalogue
publication.

**Read use**

Short route sequences are replayed for validation, opening recognition, route-versus-transposition comparison, and
selection of opening-route positions for bulk analysis.

**Keep out**

- intermediate `position_id` links;
- a duplicate opaque move-sequence value; and
- shortcut membership or hierarchy data not present in the source.

Intermediate positions are recreated by replaying the short route when analysis, validation, or lookup needs them.

### 3.8 `analysis_result`

**Purpose and ownership**

`analysis_result` owns the latest complete successful Stockfish result set for a canonical position. Analysis is
separate from `position` because engine output has a different lifecycle, principal variations are one-to-many, and
engine or settings changes must not mutate canonical chess facts.

**Conceptual shape and integrity**

The result is keyed to `position_id` and records:

- quality level: Browser or Tool;
- that level's explicit manually incremented configuration version;
- the actual settings used;
- the Stockfish version;
- result-level output needed by the viewer; and
- for a terminal position, the ending reason.

Each position retains at most one successful result set plus its child candidate lines. A terminal position has a
successful result with an ending reason and no candidate lines, distinguishing “analysed and finished” from “not
analysed.” Full occurrence counters never participate in analysis identity merely because one game occurrence was
selected first.

The exact column names and types remain for the later field catalogue.

**Write and lifecycle**

Browser fills a missing result but never replaces Tool. Tool may replace Browser. A same-level result may be replaced
when its explicit configuration version or Stockfish version changes. The old result remains visible while a
replacement is calculated, and replacement is published only when the complete result and all candidate lines are
ready. Interrupted or failed searches never publish partial output.

**Read use**

The viewer reads the current complete result and candidate lines. Both viewer-triggered requests and the bulk Tool use
the same coherent analysis capability.

**Keep out**

- analysis fields on the canonical `position` row;
- append-only result history;
- partial search output;
- completion timestamps retained merely for diagnostics;
- total wall time; and
- occurrence halfmove or fullmove counters.

### 3.9 `analysis_line`

**Purpose and ownership**

`analysis_line` owns one ranked candidate line belonging to a complete `analysis_result`.

**Conceptual shape and integrity**

Each candidate retains:

- rank;
- a centipawn-or-mate score from White's point of view, where positive favors White and negative favors Black;
- displayed depth;
- WDL values; and
- the complete principal variation as one ordered JSON list of legal UCI moves.

The application always reads the complete principal variation and may select the next move from it. Browser and Tool
both request five candidate lines. A complete result may contain fewer only when the position has fewer than five legal
moves.

The exact column names and types remain for the later field catalogue.

**Write and lifecycle**

All lines for a result are published atomically with their parent complete result. They are replaced with that result,
not appended as engine history.

**Read use**

The viewer presents candidate evaluations and consumes complete principal variations.

**Keep out**

- candidate selective depth;
- node counts;
- per-line engine time;
- separately normalized one-row-per-PV-move storage; and
- partial candidate lines.

Temporary benchmarks collect their own measurements rather than adding diagnostic persistence here.

### 3.10 Minimal analysis work queue

**Purpose and ownership**

A minimal database work queue owns only live operational coordination for viewer Analyze, Update, and Retry requests.
It is safer for concurrent local processes than recreating locking, deduplication, and crash recovery around one shared
mutable JSON file.

**Conceptual shape and integrity**

The queue contains only live state needed to coordinate work, including:

- position;
- requested quality;
- queued or running state; and
- request time.

The final table name, exact columns, claim marker, and recovery details are not settled DDL in this record. They must be
kept as small as the actual local retry workflow permits.

**Write and lifecycle**

A worker claims work transactionally, runs Stockfish outside the database transaction, publishes one complete
successful result, and removes the queue row. Interrupted running work automatically becomes available again. An
isolated Stockfish error is printed for that run, the work is skipped, no database failure record is retained, and
other work continues. The missing result can be requested again later.

**Read use**

The viewer writes live requests; a rebuilt worker drains them. This replaces the existing state in which the backend
can enqueue requests but no production caller drains the queue.

**Keep out**

- completed-job history;
- failed-job rows;
- batch history;
- permanent run records;
- a general audit trail; and
- a shared JSON queue beside the database.

### 3.11 Preferred-move periods

**Purpose and ownership**

This user-owned area stores the preferred move, explicit no-preference choice, or absence of configuration for a
position across editable UTC calendar-date periods. No current preferred-move rows migrate; the rebuilt database starts
empty.

**Conceptual shape and integrity**

The final table name is not settled. Its deliberately small conceptual shape is:

```text
position_id
effective_from
effective_until
move_uci          nullable
```

Periods use half-open date ranges: `effective_from` is included and `effective_until` is excluded. A NULL end means the
period continues indefinitely. A preference displayed as 1–5 January is stored as `[2025-01-01, 2025-01-06)`, allowing
the next period to start on 6 January without overlap. Periods for one position must not overlap.

A covering row with a UCI move means that move was preferred. A covering row with NULL `move_uci` means deliberately
no preference. No covering row means unconfigured. No extra state column is required. A preferred move may be any legal
move from the position; it is not limited to moves observed in games or opening routes. SAN is derived for display.

**Write and lifecycle**

- Historical periods are editable, not append-only.
- Periods may be inserted, moved, shortened, extended, replaced, or deleted.
- Reselecting a move creates another effective period rather than erasing the earlier period.
- Adding or changing a dated period automatically splits or shortens overlapping periods while preserving the meaning
  of dates outside the edited range.
- Deleting a period leaves those dates unconfigured. Choosing “No preferred move” creates an explicit period with NULL
  `move_uci`.
- The ordinary viewer action starts a preference today and continues it until changed. Choosing another move ends the
  previous period; choosing “No preferred move” starts an explicit no-preference period today.
- A preference may create a standalone valid canonical position. That position then follows `position` retention rules.

**Read use**

The current preferred-move capability reads the period covering the relevant UTC calendar date and distinguishes a
move, explicit no preference, and unconfigured time.

**Keep out**

- an extra state column;
- timestamp-precision semantics;
- no-update or no-delete triggers;
- append-only history restrictions;
- a requirement that the move already occur in a game or opening route;
- a preference-history editing screen in this rebuild; and
- evaluation of historical games against the preference applicable on their played date.

The storage must permit a future preference-history editing screen, but that screen is required future work rather
than part of this rebuild. Historical-game evaluation is also future work.

### 3.12 Data deliberately kept out of tables

The first rebuild does not create tables for the following:

- Chess.com fetch state, ETags, current-month flags, or fetch history;
- accepted-manifest pointers, persistent source hashes, or source import audit history;
- per-game source version history;
- normalized players, opponents, or opponent profiles;
- per-game opening classifications;
- recurrence copies or recurrence events;
- position, branch, corpus, or other speculative materialized projections;
- persisted Position Context or Move Response Distribution summaries unless a focused measurement of the real rebuilt
  query later proves one necessary;
- persisted bulk-analysis target lists or priority projections;
- completed, failed, batch, or general run history;
- write-only audit histories;
- separate feature schema tables; or
- old pipeline state retained only because code, tests, or documents still mention it.

This negative register is as binding as the table areas above. A later measured requirement may justify a new decision;
the current system's table inventory alone does not.

## 4. Cross-table capability contracts

The table areas are justified by the following demonstrated capabilities. These are behavior boundaries for later
assessment, not preserved API contracts and not an implementation plan.

### 4.1 Chess.com game intake

The rebuilt system must fetch Chess.com games, retain the raw game responses, and process accepted inputs into the
`game`, `game_position`, and `position` facts needed by the viewer.

Raw month files are the fetch ledger described in section 2.5. Refetching the current month merges by Chess.com game
UUID: earlier games remain, new games are added, and a corrected representation replaces the previous source
representation. If a later monthly response omits a previously fetched game, the local raw and normalized game remain.

Only standard games starting from the normal initial board are normalized. Non-standard variants such as `oddschess`
remain in raw JSON but create no runtime game, occurrence, position, statistic, or analysis rows.

A game is skipped when neither participant has the configured trainer Chess.com UUID because trainer color is required
for core statistics. No normalized game or occurrence rows are stored for it.

A standard game with malformed PGN or an illegal move is skipped, a warning is printed for that run, and other games
continue. The failure is not stored, and one hundred percent coverage is not required. A correction is fully validated
before replacement; a valid correction replaces one game's metadata and occurrences in one transaction, while an
invalid correction leaves the previous working normalized game untouched.

Existing corpus fingerprints, run histories, accepted-state pointers, and publication structure are not requirements.

### 4.2 Stockfish analysis

The rebuilt system supports both bulk offline Stockfish analysis and individual Analyze, Update, or Retry requests from
the viewer. Both use one coherent capability, and successful analysis is persisted because it is expensive to
reproduce.

There are two ordered quality levels:

```text
Browser < Tool
```

- Browser provides relatively quick viewer-triggered results.
- Tool provides durable deeper analysis.
- Browser fills a missing result but never replaces Tool. Tool may replace Browser.
- A request is skipped when the stored result already matches that quality level's current configuration version and
  Stockfish version.
- Each quality level has one explicit manually incremented configuration version rather than an automatic settings
  hash. The result still records the actual settings and Stockfish version used.
- Changing a level's configuration version or Stockfish version makes an older result eligible for replacement while
  preserving the no-downgrade rule.
- Browser and Tool both request five candidate lines, with fewer allowed only when fewer than five legal moves exist.
- Browser uses a fixed 200,000-node budget.
- Tool also uses a fixed node budget. Its exact value remains to be chosen by a small real benchmark around a target of
  roughly 10–15 seconds per position on the user's computer. A time limit is not used.
- If Browser work is already running when Tool is requested, Browser finishes and may be shown before Tool runs and
  replaces it.
- An old result remains visible while a same-level replacement is calculated after a configuration or Stockfish-version
  change. Replacement is published only when complete.
- Interrupted or failed searches never publish partial candidate lines.

Initial setup analyses 25 positions in total: a mixture of commonly reached positions and a small technical sample.
The resumable bulk Tool analysis is then available for the user to run in their own time. It defaults to one worker, and
an explicit `--workers` option may increase parallelism.

Later bulk Tool selection includes every unique position reached from imported games or opening routes for plies `0`
through `19`, where moves in full moves 1 through 10 are about to be played. The position after `10...` is excluded
because it begins move 11. Work is ordered by descending count of `game_position` occurrences. Positions seen only by
replaying opening routes have frequency zero and run afterward. This is an on-demand tool query, not a persisted target
or projection table. Repeated exact positions inside one game's opening are too rare to justify more elaborate priority
semantics.

### 4.3 Direct repertoire statistics

Position Context and Move Response Distribution remain key current capabilities. Their visible meaning survives; their
existing APIs, models, recurrence tables, and projection tables do not.

These statistics are calculated directly from `game`, `game_position`, and `position`. They do not require opening
classification.

**Position Context** counts distinct games containing a position. Repeated appearances of the position in one game do
not inflate the context count. It supports filtering by whether the trainer played White or Black.

```text
COUNT(DISTINCT game_id) for a position and trainer color
```

**Move Response Distribution** counts position occurrences and the one outgoing move from each occurrence. If one game
reaches the position twice, both decisions count. Actual moves form the denominator. Final occurrences where the game
ended are reported separately and do not dilute move percentages.

```text
COUNT(*) grouped by outgoing move_uci for a position and derived actor
```

The statistic distinguishes and never blends:

- **my choices**, where the position's side to move equals the trainer's color; and
- **opponent responses**, where the position's side to move differs from the trainer's color.

The actor is derived from `game.trainer_color` and `position.side_to_move`; it is not stored redundantly. Straightforward
indexes may support these access paths, but indexes do not justify duplicate recurrence facts or materialized
projections.

### 4.4 Opening catalogue and lookup

The retained source is `lichess-org/chess-openings`: five TSV files, `a.tsv` through `e.tsv`, containing about 3,810
rows with exactly `eco`, `name`, and `pgn`. The raw files contain no explicit hierarchy, aliases, transposition links,
intermediate memberships, or “identifiable at ply” marker. Routes, endpoints, and recognition are derived by replaying
the source PGNs.

While replaying a PGN, collect recognized opening endpoints in encountered ply order. The latest or deepest match is
current; earlier recognized labels provide the breadcrumb. If unnamed moves follow, the last recognized label remains
the PGN's current opening until another named endpoint is reached.

For example, source routes naming `A` after move 1, `A-1` after move 2, and `A-1a` after move 3 produce:

```text
current: A-1a
recognized:
- A at move 1
- A-1 at move 2
- A-1a at move 3
```

The hierarchy is the ordered set encountered on that PGN route, not a forced tree inferred from label spelling.

An exact source-sequence match is a `route` match. Reaching the same endpoint position through another sequence is a
`transposition` match. Both are returned with the distinction visible. A FEN lookup returns every directly matching
opening and its broader recognized families; it never returns unreached future variations. A standalone FEN with no
catalogued matching position has no opening. A PGN can still report its last recognized opening after leaving
catalogued theory because it retains move history.

Permanent per-game classification rows are not stored. A request replays or uses normalized game positions, matches
opening endpoints, compares route moves for route-versus-transposition status, and derives the ordered recognized
result. Persist classification later only if a measured current bulk use requires it.

### 4.5 Preferred-move behavior

Preferred-move storage supports preferred versus not preferred. Alternative “also acceptable” rules are future work.
Preference applies with UTC calendar-date precision, and the editable half-open periods in section 3.11 distinguish a
selected move, explicit no preference, and unconfigured time.

The rebuild starts with no preference rows. It does not add the future preference-history editor or evaluate historical
games against the preference applicable on their played date.

## 5. Explicitly excluded capabilities

### 5.1 Opponent profiles

Shared opponent-profile support is new functionality and is excluded. Raw files under
`data/chess-com/raw/profiles/` remain untouched for a separate future project. A permitted sample found 11,735 JSON
files; the first two contained flat Chess.com profile responses with stable-looking `player_id` and `username` fields
plus mutable profile attributes. Available source data does not justify tables or ingestion in this rebuild.

The nullable opponent Chess.com UUID on `game` is retained source identity, not opponent-profile functionality. A future
opponent project may correlate archive UUIDs and profile identities from retained raw data.

### 5.2 Opening Line Library

The repository has an Opening Line Library backend endpoint, frontend API client, and Storybook work, but no current
application page exposes it. It is unfinished or new functionality and is excluded from this rebuild.

### 5.3 Historical and stopped work

The following do not define required behavior:

- the stopped Chess.com refresh direction;
- abandoned tracked-player tables and code;
- speculative or unconsumed projection tables;
- write-only audit histories;
- schema, state, and run table families inherited only from previous pipeline structure; and
- tests or stories for features with no current application or actively used tool consumer.

## 6. Current-use evidence retained for assessment

A user-authorized Flash case-worker traced current production paths. The assessment found:

- the game viewer reads corpus, game, occurrence, and position data;
- evaluation UI reads stored analysis and can enqueue requests, but the running backend has no production queue
  drainer;
- Position Context reads recurrence game and position-derived data;
- Move Response Distribution reads position and branch-derived data;
- preferred-move APIs currently reuse append-only storage that conflicts with the settled mutable-period requirement;
- the Opening Line Library has no rendered application route;
- some recurrence projections are current readers' dependencies, while other projections have no reader; and
- opening classification and recurrence writers are currently reached only through tests or the stopped refresh
  orchestration, so the normalized opening-reference importer and lookup preparation must be redesigned rather than
  silently reviving that pipeline.

These findings classify existing dependencies. They do not authorize keeping the corresponding tables, names,
projections, or contracts. The table-by-table direction in section 3 is governed by demonstrated capabilities, not by
the current dependency graph.

## 7. Remaining factual work before planning

The product and operating choices needed for this conceptual model are settled. The remaining work is assessment that
will provide planning inputs, not another speculative interview and not a Plan embedded in this record:

1. run a small real Stockfish benchmark around the 10–15-second Tool target and choose the exact fixed node budget;
2. produce an actual-name table and field catalogue with keys, checks, ownership, readers, writers, and lifecycle;
3. map every current live and declared non-live table to survive, replace, drop, or never create;
4. define the rebuilt APIs and tools required by the approved current capabilities;
5. choose straightforward indexes for the real access paths and check the actual rebuilt queries on real rebuilt data;
6. define creation, validation, first parallel-database cutover, later replacement, backup, and rollback ordering; and
7. define focused acceptance proof and the point at which any removal of the old database may be separately authorized.

The actual-name catalogue must resolve the deliberately conceptual names in section 3 without reopening settled table
responsibilities. In particular, it must not invent tables for the negative register merely because the existing system
has them.

## 8. Continuation boundary

The grilling interview is complete unless later assessment reveals a genuine product decision. Do not reopen settled
questions merely because table names, fields, APIs, indexes, or implementation ordering still need factual work.

The next routed work is to produce the exact replacement catalogue and API and tool boundary from this record, then
define safe ordering and focused proof before seeking implementation approval. No part of this record authorizes
implementation, application cutover, modification or deletion of the old database, removal of generated data, or
modification of retained raw source files.
