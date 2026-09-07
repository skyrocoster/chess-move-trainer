# Database rebuild

> **Status:** direction settled
> **Approval:** The destination, approved slice envelope, and clean from-scratch package/CLI rewrite of every required
> tool were explicitly approved for this master plan.

## Destination

Build and prove a replacement SQLite database from first principles; replace every required database-feeding,
rebuild, analysis, and maintenance tool with a clean from-scratch package and CLI implementation; adapt the current
required API/backend/frontend consumers only after the database foundation is proven; activate the neighboring
replacement safely; and perform old-database retirement only as a separately authorized final operation.

## Settled direction

- The replacement is one physical SQLite database with exactly the ten catalogue tables and database-wide
  `PRAGMA user_version`; the exact table and field names are those in the schema catalogue.
- No rows migrate from the old database. Existing historical month files are retained and skipped; DB-03's later
  approved refetch behavior may safely and atomically update only the current-month month file by merging games by
  Chess.com UUID into the latest-known month representation (new games are added, corrected games replace their
  earlier source representation, and omitted games remain). No raw source is deleted, and a malformed or incomplete
  fetch must leave the prior usable month file intact. The old database remains untouched until separately authorized
  retirement; this master plan itself authorizes none of that work.
- Existing API paths, request shapes, response shapes, schemas, and models are not compatibility requirements.
  Backend and frontend contracts may change together around demonstrated current capabilities.
- **Clean tool rewrite:** Every required schema, canonicalization, Chess.com acquisition, game import, opening import
  and lookup, preferred-move storage, Stockfish analysis, queue/worker, benchmark, rebuild, snapshot, replacement,
  rollback, and proof tool is implemented from the ground up. Existing tools may be read to understand concepts,
  source formats, user workflows, and known edge cases, but they are not an implementation base: new tools must not
  import, wrap, delegate to, patch, copy, or incrementally continue their code or internal contracts.
- **Package and CLI boundary:** New tool logic belongs to cohesive importable packages with explicit ownership and
  dependency direction, not loose scripts. Shared behavior lives in package services rather than being duplicated
  between commands. Every operator-facing operation is exposed through a supported thin CLI entry point with useful
  `--help`, explicit configuration and path inputs, automation-safe non-interactive behavior, and meaningful exit
  status; CLI adapters contain no business logic. Exact package names and command names are finalized by the relevant
  slice grilling, with the common namespace and conventions established in DB-01.
- The new toolchain is built and proven alongside the legacy tools under distinct package and command paths. Legacy
  tools remain read-only evidence until their replacements have passed their slice gates and RETIRE-01 later authorizes
  their cleanup; no legacy command name, module layout, or test-helper compatibility is required.
- **No `scripts/` canon:** At completion of this rebuild, nothing under `scripts/` is canonical for any required
  database-feeding, retrieval, rebuild, analysis, proof, or maintenance operation. Every required capability must have a
  clean package-owned replacement and, when operator-facing, a supported thin CLI outside the legacy script surface. A
  legacy script cannot remain as an accepted command, fallback, wrapper target, delegated runtime path, or DB-09 proof
  path. If an old capability is proven unnecessary, it need not be rebuilt, but its script still does not become
  canonical. Legacy files remain read-only evidence until RETIRE-01 authorizes physical cleanup.
- **Authority/evidence boundary:** Only `docs/grilling-docs/database-rebuild-direction.md` and
  `docs/grilling-docs/database-rebuild-schema.md` are binding product, data, and schema authorities for this envelope.
  This master plan's approved sequencing and clean-tool-rewrite rules govern implementation. Current implemented source
  is nonbinding evidence only: legacy tool source is read-only conceptual evidence and a later retirement inventory,
  while production application source is a later replacement touchpoint only within its named slice. Old/other Plans,
  master plans, grilling docs, and historical workflow records are irrelevant and must not be consulted for slice scope
  or requirements.
- No table, projection, history, audit, manifest, classification, recurrence, player, or other machinery may be
  created unless it is in the authoritative replacement catalogue or later justified by a new approved requirement.
- The database/tool sequence through `DB-09` is strictly first. **Absolute gate:** no `API-*` slice may be assessed or
  implemented until `DB-09` has proven the rebuilt database foundation with real rebuilt data. Before that gate, production
  `backend/app`, frontend, and other application-consumer modules remain untouched. Database slices may create or
  extend only the exact new schema and isolated package-owned feeder/rebuild/analysis toolchain needed to populate and
  prove the neighboring database; existing production modules are current-state evidence or later replacement targets,
  not pre-gate implementation targets.
- Every slice has a required grilling before its implementation Plan/work begins. Grilling finalizes only
  slice-specific factual and implementation details; it must not reopen settled authority decisions.
- Only one slice is active at a time. A selected slice receives its required grilling first, then its own focused Plan
  when nontrivial, then implementation and focused proof. The next slice is selectable only after the preceding slice's
  result and proof are accepted.
- `CUT-01` activates the neighboring replacement without deleting the old database, but only after the excluded
  `/api/openings/line-library` surface has been disabled/de-registered. After activation, no active registered
  production route or required tool path may reach old-schema tables or the old database. This is a cutover safety
  prerequisite, not a rebuild of that surface or the final cleanup; incomplete optional Tool analysis does not block
  activation when games and openings are ready.
- `RETIRE-01` is the final slice and final destructive operation. After cutover, safety, and rollback proof, it
  comprehensively cleans and audits production references to the old database, obtains separate explicit deletion
  authorization immediately before deletion, and only then deletes the old database. Raw source files and historical
  workflow records are never part of that deletion.
- After this document is written, Luna must read the finished master plan end to end and iteratively refine it until
  the sequence, boundaries, references, grilling gates, proof gates, and handoffs are workable.

## Master-level selection rule

This master plan records selectable outcomes; it does not authorize implementation, cutover, deletion, or any focused
Plan. Select exactly one slice at a time in the order below. Before any selected slice's implementation Plan/work
begins, its **Grilling REQUIRED** gate must settle its bounded questions and produce a coordinator-approved handoff.
For every slice that adds or changes a tool, that handoff must name the new package ownership, dependency boundary,
public CLI entry points, invocation and exit behavior, and focused package/CLI and source-boundary proof without
inheriting the legacy layout. Internal shared services need not invent separate commands when they are not
operator-facing.
Any genuine product, ownership, API, dependency, destructive, or acceptance decision discovered by grilling is an
escalation, not an AI choice.

**NEXT slice after DB-08A:** `DB-09` — Rebuilt-database proof gate.

## Selectable slices

| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| DB-01 | An empty neighboring SQLite database has the exact replacement schema and version mechanism. | none | No feeders, readers, APIs, cutover, or deletion. |
| DB-02 | Canonical legal-only position identity is available to rebuilt database producers. | DB-01 | No old-position migration or consumer/API work. |
| DB-03 | Raw Chess.com games rebuild into normalized game and occurrence facts. | DB-02 | No old corpus/player/fetch-state machinery. |
| DB-04 | The five opening TSV sources rebuild into the exact opening/route tables and an isolated lookup/replay capability. | DB-03 | No classification, recurrence, hierarchy, or manifest machinery. |
| DB-05 | Preferred moves persist as editable UTC calendar-date periods. | DB-04 | No history editor, historical-game evaluation, or setup inference. |
| DB-06 | Complete Stockfish result sets and candidate lines persist atomically. | DB-05 | No analysis history, failure history, or API changes. |
| DB-07 | The measured Tool budget and minimal live analysis queue/worker are proven. | DB-06 | No API/frontend contract changes or persisted run history. |
| DB-08 | Idempotent rebuild, snapshot, neighboring replacement, rollback, and interruption operations are available. | DB-07 | No application cutover or old-database deletion. |
| DB-08A | The remaining current-use operator/tool surface is assessed, and any required rebuilt tool gaps—including Chess.com retrieval/API support—are finished or proven unnecessary before real-data proof. | DB-08 | No application HTTP API, DB-09 proof, opponent-profile work, raw-policy change, or legacy compatibility. |
| DB-09 | Real rebuilt data proves the database/tool foundation and direct access paths. | DB-08A | No HTTP routes, frontend integration, or cutover. |
| SETUP-01 | Reviewed setup inference produces and explicitly applies proposals for preferred-move periods. | DB-09 (and DB-05 transitively) | No automatic preference application, nonempty-target overwrite, or API/frontend work. |
| SETUP-02 | Exploration & installation of new tools for controlling & managing APIs. Downstream API slices amended to accept new tools | SETUP-01 | Any pre-existing APIs. |
| API-01 | The game viewer reads rebuilt game and occurrence data. | SETUP-01 | No old API-shape compatibility. |
| API-02 | Position Context and Move Response Distribution read rebuilt tables directly. | API-01 | No recurrence or materialized projections. |
| API-03 | Viewer Analyze/Update/Retry uses the rebuilt queue and result lifecycle. | API-02 | No old queue/history contract compatibility. |
| API-04 | Preferred-move application behavior uses rebuilt editable periods. | API-03 | No future preference-history editor. |
| CUT-01 | The neighboring rebuilt database becomes active with focused live proof. | API-04 | The old database remains intact. |
| RETIRE-01 | Production references are cleaned and the old database is deleted as the authorized final operation. | CUT-01 | No raw-source or historical-record deletion. |

## Slice results

Record only one concise accepted result or Plan link per completed slice; the focused Plan owns detailed progress and
evidence.

- **DB-01:** [focused Plan](../../plans/done/database-rebuild-db-01/database-rebuild-db-01.md) — exact schema substrate,
  safe package/CLI creation and inspection, and generated reference accepted; proof is retained in the Plan.
- **DB-02:** [focused Plan](../../plans/done/database-rebuild-db-02/database-rebuild-db-02.md) — canonical legal-only
  identity, conflict-safe stable storage, and opaque transaction composition accepted; proof is retained in the Plan.
- **DB-03:** [focused Plan](../../plans/done/database-rebuild-db-03/database-rebuild-db-03.md) — raw acquisition and
  normalized game/occurrence rebuilding accepted with 119 focused tests passing in 15.97 seconds. After DB-03 was
  completed, a separate offline run of the supported tools rebuilt 4,102 games, 209,802 occurrences, and 176,539
  canonical positions in a disposable database, with zero N+1, non-final NULL-move, or foreign-key failures; it made
  no network request and did not modify the production database or retained raw files.
- **DB-04:** [focused Plan](../../plans/done/database-rebuild-db-04/database-rebuild-db-04.md) — strict five-file opening
  parsing, atomic catalogue/route publication, isolated FEN/PGN recognition, and supported Typer commands accepted with
  87 focused tests passing across retained proofs in 33.27 seconds; real rebuilt-data proof remains owned by DB-09.
- **DB-05:** [focused Plan](../../plans/done/database-rebuild-db-05/database-rebuild-db-05.md) — normalized current
  preferred-move periods, atomic supported-writer edits, exact package/CLI boundaries, and three-state resolution
  accepted with 71 focused tests passing across retained proofs in 16.62 seconds; setup inference remains deferred to
  SETUP-01.
- **DB-06:** [focused Plan](../../plans/done/database-rebuild-db-06/database-rebuild-db-06.md) — engine-independent
  analysis validation, canonical terminal and legal candidate-line enforcement, quality/version publication rules, and
  atomic rollback-safe result-set persistence accepted with 72 focused tests passing in 2.57 seconds; queue, worker,
  benchmark, and operator commands remain deferred to DB-07.
- **DB-07:** [focused Plan](../../plans/done/database-rebuild-db-07/database-rebuild-db-07.md) — clean Stockfish 18
  process control, bounded benchmark persistence, exact queue transactions, deterministic bulk targets, serial worker
  recovery, and thin operator commands accepted with 76 tests passing across retained proofs in 21.38 seconds; API and
  frontend integration remain deferred to API-03.
- **DB-08A:** [focused Plan](../../plans/done/database-rebuild-db-08a/database-rebuild-db-08a.md) — Lichess
  opening-source acquisition, configuration examples, and DB-09 command inventory accepted with 186 focused tests
  passing in the consolidated offline proof; the five opening files can be safely fetched from one pinned upstream
  commit, example YAML configs are provided, and the DB-09 command inventory proves only clean package commands remain.

The focused Plan owns implementation progress and detailed evidence; this section must not become an implementation
queue or progress log.

## Slice envelopes

### DB-01 — Rebuilt SQLite schema substrate

**In plain English:** Create a new, empty database with only the agreed tables, rules, and version number.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize slice-specific details. The
grilling must bound the single DDL owner, SQLite connection/foreign-key setup, `PRAGMA user_version` handling,
generated-schema publication, the common new package namespace and CLI conventions, and introspection proof without
inventing tables or reopening the catalogue.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L47-L109,L139-L165,L864-L879`; `docs/grilling-docs/database-rebuild-schema.md:L18-L181`.
- **Visible result:** A new empty neighboring database can be created and reopened with `datasource_game`,
  `derived_position`, `derived_game_position`, `datasource_opening`, `derived_opening_route`,
  `derived_opening_route_move`, `derived_analysis_result`, `derived_analysis_line`, `derived_analysis_queue`, and
  `datasource_preferred_move_period`, plus `PRAGMA user_version = 1`, with the catalogue constraints and no old
  feature schema/run/state tables.
- **Scope and current-state touchpoints:** From scratch, establish the dedicated importable database-tool package and
  its common CLI conventions, with one package-owned schema/bootstrap service and thin create/inspect commands for the
  exact catalogue. The fragmented DDL in `scripts/chess_com/fetch_games.py:create_schema`,
  `scripts/chess_com/_schema.py:ensure_corpus_schema`, `scripts/opening_catalog/schema.py:ensure_schema` and related
  schema functions, `backend/app/features/analysis/schema.py:initialize_analysis_schema`,
  `backend/app/features/evaluation/schema.py:initialize_evaluation_schema`, and
  `data/database/dump_schema.py:assemble_supported_schema` is read-only conceptual evidence only and must not be
  imported, wrapped, copied, or used as the new schema owner; production `backend/app` modules are not pre-gate
  implementation targets.
- **Prerequisites:** none beyond approval of this slice's grilling handoff.
- **Explicit exclusions:** No source ingestion, analysis execution, API route, frontend change, cutover, migration,
  or deletion.
- **Focused proof:** The new package imports without legacy tool dependencies; its supported CLI creates and inspects a
  fresh database with useful help and failure exit behavior; schema/table inventory contains no unlisted tables; and
  `PRAGMA user_version`, foreign-key enforcement, and exact key/check definitions are inspected. No authorizer or other
  extra machinery is added solely to reject future unlisted table creation.
- **Escalate if:** A required field or table differs from the schema catalogue, or a proposed migration/history table
  is needed merely to preserve old machinery.
- **Handoff/selection criterion:** Select DB-02 only after the empty schema and generated reference are accepted.

### DB-02 — Canonical position substrate

**In plain English:** Give every legal chess position one stable identity that all database tools can share.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the bounded producer audit,
legal-only en-passant probes, canonical validation boundary, and position repository/storage handoff without changing
the settled four-field identity.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L167-L232`; `docs/grilling-docs/database-rebuild-schema.md:L240-L293`.
- **Visible result:** Rebuilt producers create or reuse permanent integer `dp_position_id` rows uniquely by placement,
  side to move, castling rights, and fully legal en-passant square; standalone valid preference positions are
  supported.
- **Scope and current-state touchpoints:** Implement the isolated canonicalization/repository service from scratch
  inside the new database-tool package so every later producer shares one implementation. The concepts represented by
  `scripts/chess_com/_replay.py:build_states`, opening route replay, preference position validation, and the current
  `backend/app/features/positions/repository.py:database_path`/`PositionRepository` behavior are read-only evidence;
  none is imported or copied. The backend path is evidence only before DB-09. Coordinate every FEN/key producer; the
  current replay path demonstrates the classic FEN en-passant behavior that the new implementation must replace.
- **Prerequisites:** DB-01 accepted.
- **Explicit exclusions:** No old `position_state.state_id` or text-key migration, no halfmove/fullmove identity,
  actor/analysis fields, API contract, or frontend change.
- **Focused proof:** Canonical uniqueness, legal and pinned en-passant normalization, invalid-position rejection,
  stable reuse, and permanent retention when references are removed.
- **Escalate if:** A producer cannot use the legal-only identity consistently, or a library/version choice changes the
  authority-defined chess meaning.
- **Handoff/selection criterion:** Select DB-03 only after canonical position proof is accepted.

### DB-03 — Game and occurrence rebuild

**In plain English:** Turn saved Chess.com game files into clean game and move-by-move position records without losing raw data.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the raw acquisition and
normalization boundary, archive/month traversal, latest-known merged raw month representation, historical-file
skip/current-month refetch rules, safe atomic current-month update, UUID merge behavior, trainer identity/configuration,
per-game transaction boundaries, correction handling, new package services and supported acquisition/import CLI
commands, and focused fixture coverage without reviving corpus or fetch-state persistence.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L111-L123,L234-L346,L678-L699`; `docs/grilling-docs/database-rebuild-schema.md:L185-L236,L297-L335,L744-L755`.
- **Visible result:** A complete raw-to-normalized Chess.com rebuild uses existing historical month files as retained,
  skipped ledger entries; safely and atomically refetches the current-month file and merges raw games by Chess.com UUID
  into the latest-known month representation (new games are added, corrected games replace their earlier source
  representation, and omitted games remain), never deletes a raw source, and leaves the prior usable month file intact
  when a fetch is malformed or incomplete; it feeds accepted standard games into `datasource_game`,
  `derived_game_position`, and `derived_position`. Acquisition and normalization remain distinct bounded stages:
  each valid normalized game commits independently, and a corrected game replaces its normalized facts atomically only
  after complete validation.
- **Scope and current-state touchpoints:** Write new package-owned Chess.com acquisition and game-normalization services
  plus thin supported CLI commands from scratch. The end-to-end concepts currently represented by
  `scripts/chess_com/fetch_games.py:request`, `save_json`, `upsert_month`, `mark_state`, and `run`,
  `scripts/chess_com/extract_corpus.py`, `scripts/chess_com/_replay.py:replay_game`,
  `scripts/chess_com/_persistence.py:persist_fixture` and `_persist_game`,
  and the game portion of `scripts/refresh_chess_com.py` are read-only evidence, not code or CLI entry points to adapt.
  The new tool must use raw month files as the ledger, skip existing historical files, safely and atomically refetch and
  UUID-merge the current month, must not persist ETags/current-month flags/fetch history, and must preserve the merged
  raw month representation independently of normalized acceptance.
- **Prerequisites:** DB-02 accepted.
- **Explicit exclusions:** No rows migrate; no edits to historical month files, no raw-source deletion, and no raw-file
  update outside the bounded current-month refetch/UUID-merge behavior described above; no `players`, `games`,
  `fetch_state`, `corpus`, fingerprint, run-history, source-version, or failure tables; no API, production
  backend/application, or frontend consumer work.
- **Focused proof:** Archive-list and monthly-request behavior, retained raw-month representation, historical-file skip,
  safe current-month refetch and atomic UUID merge for new/corrected/omitted games, protection of the prior usable file
  on malformed/incomplete fetches, standard/trainer, non-standard, trainer-absent, malformed, illegal, interrupted,
  and valid/invalid-correction cases; exact N+1 occurrence and outgoing-move invariants. Raw acquisition must not be
  confused with the per-valid-game normalized transaction proof.
- **Escalate if:** Archive participant identity is unavailable, or correction/skip behavior would require stored
  history or destructive removal contrary to the authorities.
- **Handoff/selection criterion:** Select DB-04 only after the rebuilt game result and focused proof are accepted.

### DB-04 — Opening catalogue and route rebuild

**In plain English:** Turn the five opening files into a validated catalogue of opening names, move routes, and final positions.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize source-row deduplication, route
identity, the reusable isolated database/tool-level opening lookup/replay capability over the new route tables, endpoint
creation, child-first publication ordering, new package services and supported catalogue/lookup CLI commands, and
malformed-source rollback proof without reviving manifest or hierarchy machinery.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L348-L462,L774-L805`; `docs/grilling-docs/database-rebuild-schema.md:L339-L449,L757-L766,L824-L830`.
- **Visible result:** The five `a.tsv` through `e.tsv` sources publish `datasource_opening`,
  `derived_opening_route`, `derived_opening_route_move`, and endpoint positions as one complete validated catalogue,
  with a reusable isolated database/tool-level opening lookup/replay capability over those route tables.
- **Scope and current-state touchpoints:** Write new package-owned opening catalogue and lookup/replay services plus thin
  supported CLI commands from scratch. `scripts/opening_catalog/importer.py:load_source` and `import_catalog`, route
  replay, `scripts/opening_catalog/relationships.py`, and `relationship_persistence.py` are read-only conceptual
  evidence and are neither dependencies nor implementation targets. DB-04 owns the persisted catalogue and route data
  plus the reusable isolated database/tool-level opening lookup/replay capability over the new route tables: PGN replay
  returns ordered recognized labels and the current label; exact source-route versus transposition distinction and FEN
  matching are supported without exposing unreached future variations or storing permanent per-game classification.
  This is not an HTTP route, production backend integration, or revival of `/api/openings/line-library`; DB-09 owns
  proof of this capability against rebuilt data.
- **Prerequisites:** DB-03 accepted.
- **Explicit exclusions:** No `opening_source_manifest`, `opening_source_file`, import-run/state, parent-link,
  transposition-link, classification, recurrence, shared-prefix, intermediate-position, opaque-sequence, or
  historical-route machinery; no HTTP route, production backend integration, or Opening Line Library application
  surface.
- **Focused proof:** All five source files, legal replay, duplicate label/route collapse, transposition preservation,
  contiguous child plies, endpoint equality, isolated lookup/replay of ordered recognized labels and current label,
  route-versus-transposition and FEN matching, unreached-future exclusion, and atomic rejection leaving the prior
  active catalogue unchanged. DB-09 proves the capability against rebuilt data.
- **Escalate if:** A source or route requirement cannot be represented by the exact three route/catalogue tables and
  canonical positions, or a current consumer contradicts the explicit Opening Line Library exclusion.
- **Handoff/selection criterion:** Select DB-05 only after the catalogue and route result and focused proof are
  accepted.

### DB-05 — Preferred-move period persistence

**In plain English:** Store and safely edit which move, if any, is preferred for each position on each calendar date.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize date parsing, locked overlap
checks, split/shorten/delete behavior, standalone-position input, and storage-only proof without reopening the settled
period semantics.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L593-L649,L807-L814`; `docs/grilling-docs/database-rebuild-schema.md:L657-L712,L811-L822`.
- **Visible result:** An empty-start database stores editable `datasource_preferred_move_period` rows using half-open
  UTC calendar dates, distinguishing preferred move, explicit no preference, and unconfigured dates.
- **Scope and current-state touchpoints:** Implement the package-owned preferred-move period repository/service from
  scratch with the catalogue's four-field period storage. `scripts/opening_catalog/preferred_move.py` and
  `preferred_move_schema.py` are read-only conceptual evidence, not code to adapt; the backend repository/service are
  later application touchpoints.
- **Prerequisites:** DB-04 accepted.
- **Explicit exclusions:** No migration of current preference rows, event/action/actor/history tables, no update/delete
  triggers, no preference-history screen, no setup inference or automatic application (deferred to SETUP-01), and no
  API/frontend contract work.
- **Focused proof:** Legal move validation, NULL no-preference semantics, date canonical checks, non-overlap under
  concurrent writers, and preservation of dates outside edits.
- **Escalate if:** Timestamp precision, historical-game evaluation, or an extra state column becomes necessary.
- **Handoff/selection criterion:** Select DB-06 only after period storage and concurrency proof are accepted.

### DB-06 — Analysis result and line persistence

**In plain English:** Store one complete current Stockfish analysis and all its candidate lines for each position.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize engine-output normalization,
  canonical terminal classification, publication transaction boundaries, and exact constraint probes without adding
  analysis history or changing the catalogue.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L464-L550,L700-L729`; `docs/grilling-docs/database-rebuild-schema.md:L453-L565`.
- **Visible result:** Each canonical position can retain at most one latest complete successful
  `derived_analysis_result` and its complete `derived_analysis_line` children, published atomically.
- **Scope and current-state touchpoints:** Implement a new package-owned analysis storage/publication service from
  scratch for the exact result/line tables and quality/version semantics. The old storage in
  `backend/app/features/analysis/schema.py:initialize_analysis_schema` and
  `backend/app/features/analysis/repository.py:AnalysisRepository.eligibility`/`publish` is current-state evidence
  only before DB-09 and must not become a dependency of the new service; production backend integration belongs to
  API-03.
- **Prerequisites:** DB-05 accepted.
- **Explicit exclusions:** No old `analysis_schema`, profile/fingerprint identity, batch-run, failure, completion,
  wall-time, partial-PV, or append-only result history; no API/frontend work.
- **Focused proof:** WDL sum, score domain, legal complete PVs, terminal/no-line behavior, no-downgrade replacement,
  stale replacement rejection, and no partial publication on failure.
- **Escalate if:** Result identity requires occurrence counters, or a proposed field is only diagnostic/provenance data
  excluded by the catalogue.
- **Handoff/selection criterion:** Select DB-07 only after complete result/line persistence is proven.

### DB-07 — Analysis queue and Stockfish worker

**In plain English:** Measure the right Stockfish workload and provide a safe queue and worker for analysis requests.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to review the required small real Stockfish
benchmark evidence and finalize the fixed Tool profile, stale threshold, claim-token lifecycle, worker concurrency, and
bulk/direct-publication boundaries without creating run or failure history. The approved handoff is
[`database-rebuild-db-07.md`](../../grilling-docs/database-rebuild-db-07.md); it accepts the completed isolated experiment
as the sizing evidence and does not require another comparative benchmark run.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L552-L591,L700-L740`; `docs/grilling-docs/database-rebuild-schema.md:L569-L653,L768-L801`.
- **Visible result:** The rebuilt `derived_analysis_queue` coordinates controlled database work requests and a rebuilt
  standalone worker claims, executes, and publishes complete results using the measured Tool budget. Browser/Tool
  quality ordering and retry behavior are observable and safe under local concurrency; production viewer integration is
  deferred to API-03.
- **Scope and current-state touchpoints:** Under the first supported clean-toolchain Stockfish package,
  `chess_move_trainer.database.stockfish`, write a new benchmark, target selector, queue service, and standalone
  Stockfish worker from scratch, exposed through thin `stockfish benchmark`, `stockfish bulk`, and `stockfish worker`
  CLI commands sufficient to populate and prove the rebuilt analysis tables, including direct bulk publication and
  controlled queue exercises. The Tool profile is fixed at 6,400,000 nodes, 6 threads, and 1,024 MiB hash with one
  engine process; Browser remains fixed at 200,000 nodes and uses the same process settings.
  `backend/app/features/evaluation/queue.py:enqueue`, `claim_next`, `complete`, `fail`, and `requeue_running`,
  `backend/app/features/evaluation/service.py:_drain`/`run_session`, and the analysis paths in
  `backend/app/features/analysis/engine.py` and `runner.py` are current-state evidence only before DB-09. The
  old `scripts/stockfish_analysis/benchmark_stockfish.py` is also evidence only. The isolated DB-07 experiment is
  accepted sizing evidence but remains a disposable reference rather than an implementation base; the supported
  benchmark is rebuilt cleanly for future use and receives only a bounded operational smoke during this slice.
  Production backend/application queue integration is deferred to API-03.
- **Prerequisites:** DB-06 accepted.
- **Explicit exclusions:** No API route or frontend contract changes, no shared JSON queue, completed/failed/batch/run
  history, target-list table, or guessed Tool budget.
- **Focused proof:** Retain the reviewed experiment as the budget evidence; prove the clean supported benchmark with
  only the handoff's bounded real-engine smoke. Prove the selected fixed engine profile, one-process Windows lock,
  atomic max-quality UPSERT, 2-minute stale reclaim, one-time claim-ticket rejection, promotion while running,
  matching-ticket failure handling, worker drain/exit, resumable direct bulk publication, and complete publication.
- **Escalate if:** The selected fixed profile is unsafe in the supported implementation, or correctness requires
  persisted failure/run records, concurrent engines, or a different queue contract.
- **Handoff/selection criterion:** Select DB-08 only after the benchmark decision and queue/worker proof are accepted.

### DB-08 — Rebuild, snapshot, and replacement operations

**In plain English:** Make database rebuilds repeatable and safely prepare snapshots, replacement files, recovery, and rollback.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize safe SQLite backup calls,
  snapshot naming/verification, rolling-three retention, idempotent refresh boundaries, neighboring-file replacement,
  rollback, interruption recovery, and the new orchestration CLI command set without activating the replacement.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L80-L123,L94-L109,L864-L966`; `docs/grilling-docs/database-rebuild-schema.md:L119-L157,L716-L766`.
- **Visible result:** Initial creation is an empty refresh; later refreshes are resumable and idempotent; destructive or
  replacing operations create and verify consistent SQLite snapshots; neighboring replacement files can be built and
  rolled back safely.
- **Focused Plan:** [active DB-08 Plan](../../plans/active/database-rebuild-db-08/database-rebuild-db-08.md).
- **Scope and current-state touchpoints:** Write a new package-owned orchestration service and thin supported CLI
  commands for refresh, snapshot, managed neighboring replacement, verification, rerun-based interruption recovery,
  and rollback. The behavior represented by `scripts/refresh_chess_com.py`, the existing importer/analysis CLI entry
  points, and the database path/connection helpers in `backend/app/features/positions/repository.py` is read-only
  conceptual evidence only and must not be wrapped or reused. Keep raw month files as the fetch ledger and use the
  SQLite backup facility rather than copying a live WAL database; no production backend/application/frontend module is
  a pre-gate implementation target.
- **Prerequisites:** DB-07 accepted.
- **Explicit exclusions:** No application activation, old-database modification/deletion, off-device disaster-recovery
  system, scheduled backup, raw-source deletion, dedicated recovery command, or parallel Stockfish operation.
- **Focused proof:** Empty-build versus refresh equivalence, skip/resume behavior, verified rolling snapshots, WAL-safe
  backup, interrupted rebuild recovery, neighboring replacement validation, and rollback without touching the old DB.
- **Escalate if:** Safe backup/rollback cannot be demonstrated with SQLite, or a proposed operation needs old-row
  migration or old-database mutation.
- **Handoff/selection criterion:** Select DB-08A only after replacement operations are proven without cutover.

### DB-08A — Remaining rebuilt operator and tool surface

**In plain English:** Before real-data proof, rebuild the complete external Chess.com retrieval journey and ensure every
required current-use operator/tool journey is available through the rebuilt package and supported CLI, with no accepted
database-tool path under `scripts/`.

**Grilling REQUIRED** before this slice's assessment Plan/work begins, to bound the complete operator/tool inventory,
the distinction between rebuilt, incomplete, missing, and legacy paths, and any remaining factual support needed by
DB-09. The assessment must explicitly trace Chess.com game retrieval and external Chess.com API support; the existing
`games acquire` command is evidence, not proof that the complete retrieval journey is finished. Grilling may settle
factual package, command, transport, and proof details, but it may not reopen whether required retrieval is rebuilt or
allow a path under `scripts/` to remain canonical.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L33-L45,L111-L123,L678-L699,L864-L976`; the clean
  tool-rewrite and sequencing rules in this master plan; and the accepted DB-01 through DB-08 Plans as historical
  implementation evidence.
- **Visible result:** A bounded inventory maps every operator-visible step needed to create, refresh, verify, analyze,
  and prove the rebuilt database to a package-owned supported operation or an explicit finding that the capability is
  unnecessary. No required journey may remain incomplete, legacy-only, or satisfied by a command under `scripts/`.
  Required current-use gaps are finished with focused package/CLI proof, including a clean from-scratch replacement for
  the complete external Chess.com retrieval/API journey. The inventory distinguishes external Chess.com retrieval/API
  support from later application HTTP API slices.
- **Scope and current-state touchpoints:** Assess the supported package and CLI surface under
  `src/chess_move_trainer/database/`, the retained raw-source paths under `data/chess-com/raw/`, and the legacy
  acquisition/tool evidence named in the current-state map, including `scripts/chess_com/fetch_games.py`,
  `scripts/chess_com/_cli.py`, and `scripts/refresh_chess_com.py`. Trace archive discovery, month retrieval, raw
  publication/retention, local import, opening/reference inputs, Stockfish benchmark/bulk/worker, verification,
  snapshot/replacement, and the exact commands DB-09 will use. Implement every required current-use tool gap from
  scratch in new package-owned areas and thin CLIs, explicitly including complete Chess.com retrieval; do not silently
  revive legacy code, treat a command name as a complete journey, or retain any `scripts/` command as an accepted path,
  fallback, implementation dependency, or DB-09 invocation.
- **Prerequisites:** DB-08 accepted.
- **Explicit exclusions:** No DB-09 real-data proof, schema or table changes, speculative persistence, opponent profiles,
  raw-source policy change, application HTTP API, backend/frontend integration, cutover, old-database handling, Opening
  Line Library work, or legacy wrapping/copying/delegation. This slice does not authorize network-scale service design;
  it addresses only the local trainer's required external Chess.com retrieval/API support. It also does not authorize
  early deletion of legacy scripts; noncanonical legacy files remain read-only evidence until RETIRE-01.
- **Focused proof:** Retain an evidence-backed operator/tool inventory; run only focused package/CLI tests for each
  identified gap; prove source boundaries and explicit inputs/meaningful exits; and, for Chess.com retrieval/API support,
  cover archive discovery, exact month URL handling, current-month refetch/UUID merge, historical skip, safe raw
  publication, transport failure behavior, and separation from local database import without requiring a broad live
  network run. The accepted DB-09 command map and source-boundary proof must show no command, import, wrapper, fallback,
  delegation, or runtime dependency under `scripts/`.
- **Escalate if:** A missing tool requires changing raw-source retention, standard-game/trainer filtering, opponent-profile
  exclusion, schema/persistence, a new dependency, an application HTTP API, legacy reuse, or an acceptance requirement
  beyond the current direction.
- **Handoff/selection criterion:** Select DB-09 only after the inventory is accepted and every required tool gap has
  passed its focused proof, or the corresponding capability—not its legacy implementation—has been explicitly accepted
  as unnecessary. The exact DB-09 command path must use only the rebuilt package and supported CLI surface.

### DB-09 — Rebuilt-database proof gate

**In plain English:** Build the neighboring database with real data and prove its integrity, speed, and direct read capabilities.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the real-data fixture/sample,
  integrity assertions, measured access paths/indexes, direct capability queries, analysis sample, and acceptance
  thresholds without turning this gate into API work.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L742-L772,L774-L805,L864-L966`; `docs/grilling-docs/database-rebuild-schema.md:L119-L157,L716-L742,L781-L830`.
- **Visible result:** A rebuilt neighboring database containing real regenerated games, openings, positions,
  empty preference storage, and analysis data passes a documented proof gate for integrity and direct current-capability
  reads. DB-09 explicitly owns the database-level opening lookup proof: PGN replay produces the ordered recognized
  endpoints/current label, exact sequence and FEN lookup distinguish route and transposition matches, and lookup does
  not expose unreached future variations or imply the excluded Opening Line Library application surface. The initial
  25-position analysis mixture and on-demand bulk selection are proven without a persisted target list. The activation
  candidate contains no migrated, inferred, or fabricated preference rows.
- **Scope and current-state touchpoints:** Exercise the rebuilt database directly using only the new package services
  and supported CLIs delivered by DB-01 through DB-08A; no legacy tool or command may participate in the accepted proof.
  Cover the query meanings later consumed by
  `backend/app/features/position_context`, `move_response_distribution`, positions, openings, preferred move, and
  analysis features. These `backend/app` areas are named as later consumer evidence only; DB-09 performs no production
  backend/application/frontend integration. Measure indexes/access paths against real rebuilt data rather than
  synthetic laboratories.
- **Prerequisites:** DB-08A accepted.
- **Explicit exclusions:** No HTTP route, frontend, application-consumer, cutover, or deletion work.
- **Focused proof:** Foreign-key/check integrity, game viewer reconstruction, distinct-game Position Context,
  occurrence-based Move Response Distribution, opening route/transposition recognition, preference states, analysis
  quality/terminal behavior, initial 25 positions, bulk ordering, and measured query access paths. Prove preferred,
  explicit no-preference, and unconfigured states plus period transaction semantics in a disposable focused proof
  database or a fully rolled-back transaction; confirm the activation candidate remains empty of preference rows unless
  the user makes a real choice and that no setup proposal is treated as canonical state. Demonstrate supported CLI
  help, explicit inputs, successful automation-safe invocation, and meaningful failure exits; a source-boundary review
  must also show no copied legacy implementation, legacy import, wrapper, or runtime delegation in the new toolchain.
- **Escalate if:** Any named current capability needs a table outside the ten-table catalogue, or the rebuilt SQLite
  workload fails measured integrity/performance/concurrency requirements.
- **Handoff/selection criterion:** This is the absolute gate before any application consumer. Only after DB-09 is
  accepted may SETUP-01 be assessed, planned, or implemented. API-01 remains gated until SETUP-01 is accepted; after
  that, API-01 through API-04 may proceed in order. DB-09's accepted evidence is the handoff for SETUP-01.

### SETUP-01 — Reviewed preferred-move setup inference

**In plain English:** Use real rebuilt play data to propose, review, validate, and explicitly apply preferred-move periods
without mistaking observed play for user intent.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the exact percentage, bounded span,
grouping, same-day, ambiguity, gap, final-boundary, JSON proposal, and command details without silently writing preference
state during generation.

- **Authority:** Coordinator-approved SETUP-01 expansion; the master-plan clean-rewrite, package/CLI, sequencing, and
  grilling-gate rules.
- **Visible result:** A package-owned, supported one-time setup workflow reads rebuilt game/occurrence data and identifies
  positions where the trainer repeatedly selected the same move at high density over a bounded period. It generates a
  deterministic, reviewable JSON proposal and never silently treats observed play as preference intent. A separate
  explicit supported command validates an edited proposal and atomically applies it only to an empty
  `datasource_preferred_move_period` schedule.
  A qualifying candidate requires strictly more than 20 matching plays (minimum 21). High density combines matching-play
  count, a high share of the trainer's choices from the position, and a bounded calendar span; exact percentage, span,
  grouping, same-day, ambiguity, gap, final-boundary, JSON-contract, and command details remain for grilling.
- **Scope and current-state touchpoints:** Implement a cohesive importable setup-inference package/service and thin
  supported CLI commands from scratch under the clean-rewrite rules, using the real rebuilt data proven by DB-09 and the
  DB-05 preferred-move storage. The legacy preferred-move and analysis/setup concepts remain read-only evidence and are
  not implementation dependencies.
- **Prerequisites:** DB-09 accepted; DB-05 storage is therefore proven transitively.
- **Explicit exclusions:** No API/frontend work, automatic application, overwrite of a nonempty schedule, persisted
  inference/projection/history tables, schema changes, legacy tool reuse, or fabricated/migrated preference rows.
- **Focused proof:** Trainer-side filtering; minimum-count, share, and span rules; deterministic generation;
  ambiguity/noise/return-to-an-earlier-move cases; review metadata; proposal validation; empty-target enforcement;
  non-overlap and legal-move validation; atomic apply/rollback; supported CLI help, explicit inputs, outputs, and
  meaningful exits; and real-data review without exposing row-level private data.
- **Escalate if:** Inference needs a new table/state, automatic writes, majority/confidence behavior outside approved
  threshold semantics, or replacement of a nonempty target schedule.
- **Handoff/selection criterion:** Select API-01 only after SETUP-01 is accepted with deterministic proposal and safe
  empty-schedule application proof.

### API-01 — Game viewer read path

**In plain English:** Update the game viewer to load games and move-by-move positions from the rebuilt database.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the rebuilt viewer read
  contract, nullable metadata handling, position reconstruction, focused API/browser proof, and the exact backend/
  frontend coordination without preserving old shapes merely for compatibility.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L287-L290,L678-L699`; `docs/grilling-docs/database-rebuild-schema.md:L185-L335,L824-L830`.
- **Visible result:** The `/viewer` application reads rebuilt game metadata and ordered occurrences through a new
  backend contract and renders the current viewer capability.
- **Scope and current-state touchpoints:** Rework `backend/app/features/positions/router.py` and
  `backend/app/features/positions/repository.py:PositionRepository`, plus
  `frontend/src/features/viewer/positionApi.ts` and viewer state/components. Existing route and model shapes are
  evidence only.
- **Prerequisites:** DB-09 and SETUP-01 accepted; no API/backend/application-consumer slice may start earlier.
- **Explicit exclusions:** No old database fallback, old contract compatibility layer, statistics projections, or
  Opening Line Library surface.
- **Focused proof:** Focused backend position tests, frontend position API/state tests, representative game navigation,
  exact PGN availability, final occurrence behavior, nullable metadata, and canonical FEN reconstruction.
- **Escalate if:** The viewer requires data excluded from `datasource_game`, `derived_game_position`, or
  `derived_position`, or the only proposed solution is preserving old storage contracts.
- **Handoff/selection criterion:** Select API-02 only after the rebuilt viewer path passes focused proof.

### API-02 — Direct statistics read paths

**In plain English:** Calculate Position Context and Move Response Distribution directly from the rebuilt data.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize direct SQL shapes, color/actor
  derivation, filtering, indexes already measured by DB-09, and focused acceptance without introducing projections.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L742-L772`; `docs/grilling-docs/database-rebuild-schema.md:L824-L830`.
- **Visible result:** Position Context counts distinct games and Move Response Distribution counts occurrences and
  outgoing moves directly from the rebuilt tables, separating trainer choices from opponent responses.
- **Scope and current-state touchpoints:** Rebuild
  `backend/app/features/position_context/router.py`, `backend/app/features/move_response_distribution/router.py`,
  their repositories/services, and the corresponding frontend API/state modules. Existing recurrence/projection readers
  are replaced rather than revived.
- **Prerequisites:** API-01 accepted; DB-09 remains the absolute database gate.
- **Explicit exclusions:** No recurrence, branch, corpus, or materialized statistics tables; no old response-shape
  compatibility solely for migration.
- **Focused proof:** Repeated-position distinct-game counts, occurrence counts, final-occurrence separation, trainer
  color filters, actor derivation, and focused frontend rendering/API tests.
- **Escalate if:** Direct rebuilt queries cannot meet measured requirements without a new approved persisted dataset.
- **Handoff/selection criterion:** Select API-03 after both statistic capabilities pass focused proof.

### API-03 — Viewer analysis path

**In plain English:** Connect the viewer's Analyze, Update, and Retry actions to the rebuilt analysis queue and results.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize rebuilt request/result contracts,
  Browser/Tool quality presentation, stale/running behavior, and backend/frontend coordination without retaining old
  queue or batch-history semantics.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L700-L740`; `docs/grilling-docs/database-rebuild-schema.md:L453-L653,L768-L809`.
- **Visible result:** Viewer Analyze, Update, and Retry requests use the rebuilt queue; current complete results and
  candidate lines are read from the rebuilt analysis tables; backend and frontend contracts change together.
- **Scope and current-state touchpoints:** This is the first production integration of DB-07's proven queue/worker.
  Rebuild `backend/app/features/evaluation/router.py`, evaluation service, analysis repository/models, and
  `frontend/src/features/viewer/analysisApi.ts`, `analysisState.ts`, formatting, and evaluation-bar consumers.
  Existing `backend/app/features/analysis/*` and evaluation code are current-state evidence, not target contracts.
- **Prerequisites:** API-02 accepted; DB-09 and DB-07's worker are already proven.
- **Explicit exclusions:** No old `position_key`/FEN queue compatibility, batch history, failure API, partial result,
  downgrade, or separate application queue drainer contract.
- **Focused proof:** Request deduplication/promotion, result eligibility, complete PV display, no-downgrade behavior,
  running replacement visibility, retry/recovery, focused backend tests, and frontend API/state tests.
- **Escalate if:** A consumer requires diagnostic history or a result identity outside canonical position semantics.
- **Handoff/selection criterion:** Select API-04 after analysis API and viewer proof pass.

### API-04 — Preferred-move application path

**In plain English:** Update the repertoire app to read and edit dated preferred-move choices from the rebuilt database.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the application contract for
  period reads/writes, explicit no preference, unconfigured state, UTC date handling, and frontend behavior without
  adding the excluded history editor.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L807-L814`; `docs/grilling-docs/database-rebuild-schema.md:L657-L712,L811-L822`.
- **Visible result:** The `/repertoire` application reads and edits rebuilt preferred-move periods, including current
  preference, explicit no preference, and unconfigured dates.
- **Scope and current-state touchpoints:** Rebuild `backend/app/features/preferred_move/repository.py`, `service.py`,
  and `router.py`, plus `frontend/src/features/repertoire-builder/preferredMoveApi.ts` and its consumers. The current
  append-only script/schema behavior is replaced.
- **Prerequisites:** API-03 accepted; DB-09 and DB-05 storage are already proven.
- **Explicit exclusions:** No old event API compatibility, actor/history display, future history editor, or historical
  game evaluation.
- **Focused proof:** Current-date reads, dated edits, split/shorten/delete semantics, no-preference versus missing
  row, illegal move rejection, concurrent writes, focused backend API and frontend API tests.
- **Escalate if:** The application needs timestamp precision or an additional state not represented by the catalogue.
- **Handoff/selection criterion:** Select CUT-01 only after API-01 through API-04 have all passed focused proof.

### CUT-01 — First parallel-database cutover

**In plain English:** Make the rebuilt database active, prove the live app and rollback work, and keep the old database untouched.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize readiness evidence, replacement
path/configuration, maintenance-mode timing, switch/rollback mechanics, the active-path audit including the excluded
old Opening Line Library route, the required pre-activation disable/de-registration of that route, and live focused
scenarios without deleting or modifying the old database.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L80-L109,L881-L889`; `docs/grilling-docs/database-rebuild-schema.md:L10-L14,L716-L742`.
- **Visible result:** The required application and tools use the proven neighboring rebuilt database as the active
  database; games and openings are ready, incomplete optional Tool analysis does not block activation, and the excluded
  `/api/openings/line-library` surface was disabled/de-registered before activation rather than rebuilt.
- **Scope and current-state touchpoints:** Activate only the new package-owned services and supported CLI/worker entry
  points. Cutover configuration currently centers on
  `backend/app/features/positions/repository.py:DEFAULT_DATABASE_PATH`, `DATABASE_PATH_ENV`, and `database_path`,
  together with legacy script/worker path consumers identified in the current implementation map. These are cutover
  evidence and replacement/retirement targets, not tool implementations to retain. Validate all API and
  frontend consumers from API-01 through API-04. Because `/api/openings/line-library` is excluded, has no production
  application caller, and is currently registered against old tables, disable/de-register it before replacement
  activation; CUT-01 owns that safety prerequisite and does not rebuild the surface. Remaining dead implementation,
  configuration, and client references are reserved for RETIRE-01's final cleanup.
- **Prerequisites:** API-04 accepted, plus fresh safety/rollback evidence and the earlier DB-09 proof. Before the
  replacement becomes active, the excluded `/api/openings/line-library` route must be disabled/de-registered and that
  state must have focused proof.
- **Explicit exclusions:** No old-database deletion, raw-source deletion, historical-record modification, silent
  fallback to the old database, or Opening Line Library rebuild/integration. No comprehensive cleanup of remaining
  dead production references; that cleanup belongs to RETIRE-01 after cutover.
- **Focused proof:** Live health, viewer, statistics, analysis request, and preferred-move scenarios against the
  rebuilt database; pre-activation proof that the excluded route is disabled/de-registered; after activation, an
  active-path audit of registered production routes and required tool/worker paths proving that none reaches old-schema
  tables or the old database; rollback switch proof; and proof that the old database file remains intact.
- **Escalate if:** Any required capability or active registered production route/tool path still reaches old tables or
  the old database, the excluded route cannot be disabled/de-registered before activation, or rollback/cutover
  evidence is incomplete.
- **Handoff/selection criterion:** RETIRE-01 is not selectable until cutover and rollback evidence are accepted. Its
  separate deletion authorization must be obtained immediately after its cleanup audit and immediately before
  deletion.

### RETIRE-01 — Explicit final old-database retirement

**In plain English:** Remove remaining old-database references and, only with final approval, safely delete the old database.

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the production-reference
inventory and final cleanup/audit, including the already-proven pre-cutover disable/de-registration of the excluded
Opening Line Library route, remaining obsolete endpoint/code/configuration/client references where in scope, exact old
database file list, WAL-safe old-database snapshot/restore verification, authorization record, cleanup-before-delete
ordering, post-deletion proof, and the distinction between restoring the retired old database and rolling back the
active rebuilt database. This grilling may not authorize deletion by itself.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L33-L45,L80-L109,L881-L889`; `docs/grilling-docs/database-rebuild-schema.md:L10-L14,L834-L957,L959-L1469`.
- **Visible result:** After CUT-01's pre-activation de-registration, final retirement comprehensively cleans and audits
  all remaining production code/configuration/path/table references to the old database or old production schema,
  including obsolete Opening Line Library implementation files and clients where in scope. The excluded surface is
  never rebuilt or integrated. After that cleanup audit, separate explicit deletion authorization is obtained
  immediately before the old database is deleted as the final destructive operation. The active rebuilt database
  remains recoverable through its approved snapshot/rollback process. A verified old-database snapshot provides a
  separate restore path for the retired old database; it is not represented as rollback of the active rebuilt database.
- **Scope and current-state touchpoints:** Identify the exact old database file set before any cleanup; the current
  default is `data/database/chess_games.db` from `backend/app/features/positions/repository.py:10`, subject to any
  explicitly configured path, and related WAL/SHM sidecars must be accounted for. Then audit and clean production
  references currently concentrated in
  `backend/app/features/positions/repository.py`, `scripts/chess_com/_cli.py`,
  `scripts/chess_com/fetch_games.py`, `scripts/stockfish_analysis/analyze_positions.py`,
  `scripts/stockfish_analysis/benchmark_stockfish.py`, `scripts/stockfish_analysis/analyze_menu.py`, and
  `scripts/scout_db_query.py`, plus the excluded Opening Line Library references in
  `backend/app/features/openings/router.py`, `backend/app/features/openings/service.py`,
  `backend/app/features/openings/repository.py`, the route registration in `backend/app/main.py:9,30`, and
  `frontend/src/features/openings/openingsApi.ts`. Verify CUT-01's pre-activation route de-registration, then remove
  remaining dead production code/configuration/path/table references to the old database/schema, including obsolete
  Opening Line Library implementation files/clients where in scope; do not rebuild the excluded surface. Tests,
  Storybook, and historical records are not production requirements; handle affected nonproduction evidence only
  insofar as the selected cleanup Plan needs focused proof. Remove obsolete production DDL references only after
  replacement behavior is proven.
- **Prerequisites:** CUT-01 accepted, including retained proof that the excluded `/api/openings/line-library` route was
  disabled/de-registered before activation; the exact old database file(s), including any related WAL/SHM sidecars, are
  identified; a consistent, verified, WAL-safe SQLite backup specifically of the old database has been created and
  successfully restored in an isolated location; and active rebuilt-database cutover/rollback proof is accepted. A
  pre-cleanup production-reference inventory is prepared. The remaining production references must be cleaned and the
  final audit accepted first; then separate explicit deletion authorization must be recorded immediately before
  deletion with no intervening product operation.
- **Explicit exclusions:** No raw-source deletion or modification, no deletion of historical workflow records, no
  cleanup of unrelated paths, no Opening Line Library rebuild or integration, and no deletion based solely on this
  master plan. Its route de-registration is a CUT-01 safety prerequisite; RETIRE-01 only cleans remaining obsolete
  references and performs the separately authorized final deletion.
- **Focused proof:** The exact old file list is recorded; the old database is backed up with SQLite's WAL-safe backup
  facility and restored successfully before cleanup; active rebuilt-database rollback is proved separately; CUT-01's
  pre-activation route de-registration remains verified; remaining old-database/schema production code/configuration/
  path/table references, including obsolete Opening Line Library implementation files/clients where in scope, are
  removed; the production reference scan passes after the comprehensive cleanup; explicit deletion authorization is
  the immediately preceding authorization; deletion occurs only after that authorization; and post-deletion
  startup/health plus active rebuilt snapshot/rollback evidence pass. No rollback after deletion is promised without
  the verified old-database snapshot.
- **Escalate if:** Any production reference remains, the old database is still needed for rollback, authorization is
  absent, or the proposed cleanup reaches raw sources or historical records.
- **Handoff/selection criterion:** This is the terminal slice. No later slice, repair, or destructive follow-up is
  implied; any new need requires fresh coordinator assessment.

## Current-state implementation map (nonbinding evidence)

These areas are a read-only concept map and later retirement inventory. Database-tool slices must not implement inside,
import, wrap, copy, or preserve these legacy tool modules; they build the new package and CLI boundaries described
above. Later API slices may replace the named production consumers within their own envelopes. Nothing here overrides
the destination or schema catalogue.

- **Database path and connections:** `backend/app/features/positions/repository.py:10-62` (`DEFAULT_DATABASE_PATH`,
  `DATABASE_PATH_ENV`, `database_path`, `open_read_only_connection`);
  `backend/app/features/preferred_move/repository.py:106-139`; `backend/app/features/evaluation/service.py:349-353`.
- **Current schema ownership:** `scripts/chess_com/fetch_games.py:create_schema`,
  `scripts/chess_com/_schema.py:ensure_corpus_schema`, `scripts/opening_catalog/schema.py:ensure_schema` and its
  relationship schema, classification/recurrence/preferred schema modules,
  `backend/app/features/analysis/schema.py:initialize_analysis_schema` and
  `migrate_position_key_schema`, `backend/app/features/evaluation/schema.py:initialize_evaluation_schema`, and
  `data/database/dump_schema.py:assemble_supported_schema`.
- **Game import/replay:** `scripts/chess_com/fetch_games.py`, `scripts/chess_com/_replay.py:replay_game` and
  `build_states`, `scripts/chess_com/_persistence.py:persist_fixture` and `_persist_game`,
  `scripts/chess_com/extract_corpus.py`, and `scripts/refresh_chess_com.py`.
- **Opening ingestion:** `scripts/opening_catalog/importer.py:load_source` and `import_catalog`,
  `scripts/opening_catalog/relationships.py`, and `relationship_persistence.py`.
- **Analysis and worker:** `backend/app/features/analysis/repository.py:AnalysisRepository`, `engine.py`, `runner.py`,
  `selection.py`, `backend/app/features/evaluation/queue.py`, `evaluation/service.py`, and
  `scripts/stockfish_analysis/analyze_positions.py` plus `benchmark_stockfish.py`.
- **Preferred moves:** `scripts/opening_catalog/preferred_move.py`, `preferred_move_schema.py`,
  `backend/app/features/preferred_move/repository.py`, `service.py`, and `router.py`.
- **Chess.com acquisition:** `scripts/chess_com/fetch_games.py:request` (116-123), `save_json` (175-178),
   `upsert_month` (181-225), `mark_state` (228-243), and `run` (246-343) currently fetch archive/month URLs, write raw
  JSON, update old `games`/`players`, and use old `fetch_state` ETag/current flags. The rebuilt DB-03 target uses
  raw month files as the fetch ledger, skips existing historical files, refetches the current month, merges games by
  Chess.com UUID into a latest-known month representation, and keeps raw retention separate from normalized per-game
  transactions.
- **Current API consumers:** positions, evaluation, position-context, move-response-distribution, and preferred-move
  routers have current application consumers; frontend `positionApi.ts`, `analysisApi.ts`, `positionContextApi.ts`,
  `moveResponseDistributionApi.ts`, and `preferredMoveApi.ts` are corresponding evidence.
- **Opening lookup ownership and boundary:** DB-04 owns persisted catalogue/routes and the reusable isolated
  database/tool-level lookup/replay capability; DB-09 owns proof against rebuilt data. The current backend
  route/service/repository are `backend/app/features/openings/router.py:33-57`,
  `service.py:57-69`, and `repository.py:104-190`; they read old line-library/projection tables and have no caller
  beyond route registration. `frontend/src/App.tsx:16-34` has no opening route; the only frontend fetch definition is
  `frontend/src/features/openings/openingsApi.ts:169-190`, used only by tests/Storybook. The
  `/api/openings/line-library` application surface remains excluded and is not rebuilt; its production route
  registration must be disabled/de-registered before CUT-01 activates the replacement, while remaining obsolete
  implementation/client/configuration references are cleaned in RETIRE-01. Any future production lookup integration
  requires a new assessment after DB-09 rather than reviving it.
- **Focused proof areas:** Existing feature tests under `backend/tests/features/positions`, `evaluation`, `analysis`,
  `preferred_move`, `position_context`, `move_response_distribution`, and `openings`, plus the corresponding frontend
  API/state tests, are current evidence and must be replaced or adapted only within selected implementation slices.
  New database-tool tests target the new package services and supported CLIs and must not import legacy tool helpers or
  use legacy commands as their proof path.

## Explicit exclusions

- No old database rows migrate, and no old database is modified before separately authorized retirement. No raw source
  is deleted. Existing historical month files remain retained and skipped; the only raw-file update described by this
  envelope is DB-03's safe, atomic current-month refetch/UUID-merge behavior, with malformed or incomplete fetches
  leaving the prior usable month file intact. This master plan itself authorizes no such work.
- No old API/request/response/model contract is preserved solely for compatibility.
- No PostgreSQL or managed service absent measured SQLite need.
- No `Opening Line Library` endpoint/page/application integration or rebuild; it has no current production application
  consumer. Its registered production route must be disabled/de-registered before CUT-01 activation, and RETIRE-01
  cleans remaining obsolete production references before the old database is deleted.
- No opponent-profile tables or changes under `data/chess-com/raw/profiles/`.
- No fetch-state, manifest/hash, source-history, classification, recurrence, hierarchy, projection, audit, batch,
  failure, or per-feature schema/state/run table families.
- No persisted statistics or bulk target projections without a later measured requirement and approved decision.
- No scheduled or off-device backup system.
- No future preference-history editor or historical-game evaluation.
- No API/backend/application-consumer slice before DB-09 passes.
- No legacy database tool is patched, wrapped, imported, copied, or incrementally refactored into the replacement, and
  no legacy module layout, command name, internal contract, or test-helper compatibility is required. Legacy tools are
  not removed early; they remain read-only evidence until their replacements are accepted and RETIRE-01 owns cleanup.
- No new business logic lives in loose one-off scripts or CLI adapters; it belongs to the new importable packages and is
  reached through their supported entry points.
- No commits, pushes, branches, worktrees, stashes, unrelated record changes, or implementation authorization is
  implied by this document.
