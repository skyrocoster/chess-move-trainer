# Database rebuild

> **Status:** direction settled
> **Approval:** The destination and the strict 15-slice envelope were explicitly approved for this master plan.

## Destination

Build and prove a replacement SQLite database from first principles, rebuild the required data-feeding tools, adapt
the current required API/backend/frontend consumers only after the database foundation is proven, activate the
neighboring replacement safely, and perform old-database retirement only as a separately authorized final operation.

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
- **Authority/evidence boundary:** Only `docs/grilling-docs/database-rebuild-direction.md` and
  `docs/grilling-docs/database-rebuild-schema.md` are binding authorities for this envelope and its requirements.
  Current implemented source is nonbinding evidence only. Old/other Plans, master plans, grilling docs, and historical
  workflow records are irrelevant and must not be consulted for slice scope or requirements.
- No table, projection, history, audit, manifest, classification, recurrence, player, or other machinery may be
  created unless it is in the authoritative replacement catalogue or later justified by a new approved requirement.
- The nine `DB-*` slices are strictly first. **Absolute gate:** no `API-*` slice may be assessed or implemented until
  `DB-09` has proven the rebuilt database foundation with real rebuilt data. Before that gate, production
  `backend/app`, frontend, and other application-consumer modules remain untouched. Database slices may create or
  rebuild only the exact schema and isolated database-owned feeder/rebuild/analysis tools needed to populate and prove
  the neighboring database; existing production modules are current-state evidence or later replacement targets, not
  pre-gate implementation targets.
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
Any genuine product, ownership, API, dependency, destructive, or acceptance decision discovered by grilling is an
escalation, not an AI choice.

## Selectable slices

| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| DB-01 | An empty neighboring SQLite database has the exact replacement schema and version mechanism. | none | No feeders, readers, APIs, cutover, or deletion. |
| DB-02 | Canonical legal-only position identity is available to rebuilt database producers. | DB-01 | No old-position migration or consumer/API work. |
| DB-03 | Raw Chess.com games rebuild into normalized game and occurrence facts. | DB-02 | No old corpus/player/fetch-state machinery. |
| DB-04 | The five opening TSV sources rebuild into the exact opening/route tables and an isolated lookup/replay capability. | DB-03 | No classification, recurrence, hierarchy, or manifest machinery. |
| DB-05 | Preferred moves persist as editable UTC calendar-date periods. | DB-04 | No history editor or historical-game evaluation. |
| DB-06 | Complete Stockfish result sets and candidate lines persist atomically. | DB-05 | No analysis history, failure history, or API changes. |
| DB-07 | The measured Tool budget and minimal live analysis queue/worker are proven. | DB-06 | No API/frontend contract changes or persisted run history. |
| DB-08 | Idempotent rebuild, snapshot, neighboring replacement, rollback, and interruption operations are available. | DB-07 | No application cutover or old-database deletion. |
| DB-09 | Real rebuilt data proves the database/tool foundation and direct access paths. | DB-08 | No HTTP routes, frontend integration, or cutover. |
| API-01 | The game viewer reads rebuilt game and occurrence data. | DB-09 | No old API-shape compatibility. |
| API-02 | Position Context and Move Response Distribution read rebuilt tables directly. | API-01 | No recurrence or materialized projections. |
| API-03 | Viewer Analyze/Update/Retry uses the rebuilt queue and result lifecycle. | API-02 | No old queue/history contract compatibility. |
| API-04 | Preferred-move application behavior uses rebuilt editable periods. | API-03 | No future preference-history editor. |
| CUT-01 | The neighboring rebuilt database becomes active with focused live proof. | API-04 | The old database remains intact. |
| RETIRE-01 | Production references are cleaned and the old database is deleted as the authorized final operation. | CUT-01 | No raw-source or historical-record deletion. |

## Slice results

No focused slice result exists until a slice is selected and completed. After completion, record only one concise
accepted result or Plan link per slice, for example:

`- **DB-01:** <focused Plan path> — exact schema substrate accepted; proof: <focused evidence link>.`

The focused Plan owns implementation progress and detailed evidence; this section must not become an implementation
queue or progress log.

## Slice envelopes

### DB-01 — Rebuilt SQLite schema substrate

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize slice-specific details. The
grilling must bound the single DDL owner, SQLite connection/foreign-key setup, `PRAGMA user_version` handling,
generated-schema publication, and introspection proof without inventing tables or reopening the catalogue.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L47-L109,L139-L165,L864-L879`; `docs/grilling-docs/database-rebuild-schema.md:L18-L181`.
- **Visible result:** A new empty neighboring database can be created and reopened with `datasource_game`,
  `derived_position`, `derived_game_position`, `datasource_opening`, `derived_opening_route`,
  `derived_opening_route_move`, `derived_analysis_result`, `derived_analysis_line`, `derived_analysis_queue`, and
  `datasource_preferred_move_period`, plus `PRAGMA user_version = 1`, with the catalogue constraints and no old
  feature schema/run/state tables.
- **Scope and current-state touchpoints:** Create one isolated database-owned schema/bootstrap owner for the exact
  catalogue. The fragmented DDL in `scripts/chess_com/fetch_games.py:create_schema`,
  `scripts/chess_com/_schema.py:ensure_corpus_schema`, `scripts/opening_catalog/schema.py:ensure_schema` and related
  schema functions, `backend/app/features/analysis/schema.py:initialize_analysis_schema`,
  `backend/app/features/evaluation/schema.py:initialize_evaluation_schema`, and
  `data/database/dump_schema.py:assemble_supported_schema` is current-state evidence only; production `backend/app`
  modules are not pre-gate implementation targets.
- **Prerequisites:** none beyond approval of this slice's grilling handoff.
- **Explicit exclusions:** No source ingestion, analysis execution, API route, frontend change, cutover, migration,
  or deletion.
- **Focused proof:** Fresh database schema/table inventory contains no unlisted tables; `PRAGMA user_version`,
  foreign-key enforcement, and exact key/check definitions are inspected. No authorizer or other extra machinery is
  added solely to reject future unlisted table creation.
- **Escalate if:** A required field or table differs from the schema catalogue, or a proposed migration/history table
  is needed merely to preserve old machinery.
- **Handoff/selection criterion:** Select DB-02 only after the empty schema and generated reference are accepted.

### DB-02 — Canonical position substrate

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the bounded producer audit,
legal-only en-passant probes, canonical validation boundary, and position repository/storage handoff without changing
the settled four-field identity.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L167-L232`; `docs/grilling-docs/database-rebuild-schema.md:L240-L293`.
- **Visible result:** Rebuilt producers create or reuse permanent integer `dp_position_id` rows uniquely by placement,
  side to move, castling rights, and fully legal en-passant square; standalone valid preference positions are
  supported.
- **Scope and current-state touchpoints:** Build the isolated database-owned canonicalization/rebuild primitive around
  the current logic represented by `scripts/chess_com/_replay.py:build_states`, opening route replay, preference
  position validation, and the current `backend/app/features/positions/repository.py:database_path`/
  `PositionRepository` behavior. The backend path is evidence only before DB-09. Coordinate every FEN/key producer;
  the current replay path uses classic FEN en-passant behavior.
- **Prerequisites:** DB-01 accepted.
- **Explicit exclusions:** No old `position_state.state_id` or text-key migration, no halfmove/fullmove identity,
  actor/analysis fields, API contract, or frontend change.
- **Focused proof:** Canonical uniqueness, legal and pinned en-passant normalization, invalid-position rejection,
  stable reuse, and permanent retention when references are removed.
- **Escalate if:** A producer cannot use the legal-only identity consistently, or a library/version choice changes the
  authority-defined chess meaning.
- **Handoff/selection criterion:** Select DB-03 only after canonical position proof is accepted.

### DB-03 — Game and occurrence rebuild

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the raw acquisition and
normalization boundary, archive/month traversal, latest-known merged raw month representation, historical-file
skip/current-month refetch rules, safe atomic current-month update, UUID merge behavior, trainer identity/configuration,
per-game transaction boundaries, correction handling, and focused fixture coverage without reviving corpus or
fetch-state persistence.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L111-L123,L234-L346,L678-L699`; `docs/grilling-docs/database-rebuild-schema.md:L185-L236,L297-L335,L744-L755`.
- **Visible result:** A complete raw-to-normalized Chess.com rebuild uses existing historical month files as retained,
  skipped ledger entries; safely and atomically refetches the current-month file and merges raw games by Chess.com UUID
  into the latest-known month representation (new games are added, corrected games replace their earlier source
  representation, and omitted games remain), never deletes a raw source, and leaves the prior usable month file intact
  when a fetch is malformed or incomplete; it feeds accepted standard games into `datasource_game`,
  `derived_game_position`, and `derived_position`. Acquisition and normalization remain distinct bounded stages:
  each valid normalized game commits independently, and a corrected game replaces its normalized facts atomically only
  after complete validation.
- **Scope and current-state touchpoints:** Rebuild the end-to-end behavior currently in
  `scripts/chess_com/fetch_games.py:request`, `save_json`, `upsert_month`, `mark_state`, and `run`,
  `scripts/chess_com/extract_corpus.py`, `scripts/chess_com/_replay.py:replay_game`,
  `scripts/chess_com/_persistence.py:persist_fixture` and `_persist_game`,
  and the game portion of `scripts/refresh_chess_com.py`. The current `fetch_state`-driven behavior is evidence only;
  the rebuilt tool must use raw month files as the ledger, skip existing historical files, safely and atomically
  refetch and UUID-merge the current month, must not persist ETags/current-month flags/fetch history, and must preserve
  the merged raw month representation independently of normalized acceptance.
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

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize source-row deduplication, route
identity, the reusable isolated database/tool-level opening lookup/replay capability over the new route tables, endpoint
creation, child-first publication ordering, and malformed-source rollback proof without reviving manifest or hierarchy
machinery.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L348-L462,L774-L805`; `docs/grilling-docs/database-rebuild-schema.md:L339-L449,L757-L766,L824-L830`.
- **Visible result:** The five `a.tsv` through `e.tsv` sources publish `datasource_opening`,
  `derived_opening_route`, `derived_opening_route_move`, and endpoint positions as one complete validated catalogue,
  with a reusable isolated database/tool-level opening lookup/replay capability over those route tables.
- **Scope and current-state touchpoints:** Rebuild `scripts/opening_catalog/importer.py:load_source` and
  `import_catalog`, route replay, and the relevant behavior currently represented by
  `scripts/opening_catalog/relationships.py` and `relationship_persistence.py`. DB-04 owns the persisted catalogue
  and route data plus the reusable isolated database/tool-level opening lookup/replay capability over the new route
  tables: PGN replay returns ordered recognized labels and the current label; exact source-route versus transposition
  distinction and FEN matching are supported without exposing unreached future variations or storing permanent
  per-game classification. This is not an HTTP route, production backend integration, or revival of
  `/api/openings/line-library`; DB-09 owns proof of this capability against rebuilt data.
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

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize date parsing, locked overlap
checks, split/shorten/delete behavior, standalone-position input, and storage-only proof without reopening the settled
period semantics.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L593-L649,L807-L814`; `docs/grilling-docs/database-rebuild-schema.md:L657-L712,L811-L822`.
- **Visible result:** An empty-start database stores editable `datasource_preferred_move_period` rows using half-open
  UTC calendar dates, distinguishing preferred move, explicit no preference, and unconfigured dates.
- **Scope and current-state touchpoints:** Replace the append-only behavior in
  `scripts/opening_catalog/preferred_move.py` and `preferred_move_schema.py` with the catalogue's four-field period
  storage; the backend repository/service are later application touchpoints.
- **Prerequisites:** DB-04 accepted.
- **Explicit exclusions:** No migration of current preference rows, event/action/actor/history tables, no update/delete
  triggers, no preference-history screen, and no API/frontend contract work.
- **Focused proof:** Legal move validation, NULL no-preference semantics, date canonical checks, non-overlap under
  concurrent writers, and preservation of dates outside edits.
- **Escalate if:** Timestamp precision, historical-game evaluation, or an extra state column becomes necessary.
- **Handoff/selection criterion:** Select DB-06 only after period storage and concurrency proof are accepted.

### DB-06 — Analysis result and line persistence

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize engine-output normalization,
  canonical terminal classification, publication transaction boundaries, and exact constraint probes without adding
  analysis history or changing the catalogue.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L464-L550,L700-L729`; `docs/grilling-docs/database-rebuild-schema.md:L453-L565`.
- **Visible result:** Each canonical position can retain at most one latest complete successful
  `derived_analysis_result` and its complete `derived_analysis_line` children, published atomically.
- **Scope and current-state touchpoints:** Build an isolated database-owned analysis storage/publication tool for the
  exact result/line tables and quality/version semantics. The old storage in
  `backend/app/features/analysis/schema.py:initialize_analysis_schema` and
  `backend/app/features/analysis/repository.py:AnalysisRepository.eligibility`/`publish` is current-state evidence
  only before DB-09; production backend integration belongs to API-03.
- **Prerequisites:** DB-05 accepted.
- **Explicit exclusions:** No old `analysis_schema`, profile/fingerprint identity, batch-run, failure, completion,
  wall-time, partial-PV, or append-only result history; no API/frontend work.
- **Focused proof:** WDL sum, score domain, legal complete PVs, terminal/no-line behavior, no-downgrade replacement,
  stale replacement rejection, and no partial publication on failure.
- **Escalate if:** Result identity requires occurrence counters, or a proposed field is only diagnostic/provenance data
  excluded by the catalogue.
- **Handoff/selection criterion:** Select DB-07 only after complete result/line persistence is proven.

### DB-07 — Analysis queue and Stockfish worker

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to run the required small real Stockfish
  benchmark and finalize the fixed Tool node budget, stale threshold, claim-token lifecycle, worker concurrency, and
  bulk/direct-publication boundaries without creating run or failure history.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L552-L591,L700-L740`; `docs/grilling-docs/database-rebuild-schema.md:L569-L653,L768-L801`.
- **Visible result:** The rebuilt `derived_analysis_queue` coordinates controlled database work requests and a rebuilt
  standalone worker claims, executes, and publishes complete results using the measured Tool budget. Browser/Tool
  quality ordering and retry behavior are observable and safe under local concurrency; production viewer integration is
  deferred to API-03.
- **Scope and current-state touchpoints:** Build a standalone database-owned queue/Stockfish worker tool sufficient to
  populate and prove the rebuilt analysis tables, including direct bulk publication and controlled queue exercises.
  `backend/app/features/evaluation/queue.py:enqueue`, `claim_next`, `complete`, `fail`, and `requeue_running`,
  `backend/app/features/evaluation/service.py:_drain`/`run_session`, and the analysis paths in
  `backend/app/features/analysis/engine.py` and `runner.py` are current-state evidence only before DB-09. The
  benchmark evidence may use `scripts/stockfish_analysis/benchmark_stockfish.py`; the production backend/application
  queue integration is deferred to API-03.
- **Prerequisites:** DB-06 accepted.
- **Explicit exclusions:** No API route or frontend contract changes, no shared JSON queue, completed/failed/batch/run
  history, target-list table, or guessed Tool budget.
- **Focused proof:** Benchmark evidence around the 10–15 second target, atomic max-quality UPSERT, stale reclaim,
  compare-and-swap token rejection, promotion while running, matching-token failure handling, and complete publication.
- **Escalate if:** The benchmark cannot establish a safe fixed budget, or correctness requires persisted failure/run
  records or a different queue contract.
- **Handoff/selection criterion:** Select DB-08 only after the benchmark decision and queue/worker proof are accepted.

### DB-08 — Rebuild, snapshot, and replacement operations

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize safe SQLite backup calls,
  snapshot naming/verification, rolling-three retention, idempotent refresh boundaries, neighboring-file replacement,
  rollback, and interruption recovery without activating the replacement.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L80-L123,L94-L109,L864-L879`; `docs/grilling-docs/database-rebuild-schema.md:L119-L157,L716-L766`.
- **Visible result:** Initial creation is an empty refresh; later refreshes are resumable and idempotent; destructive or
  replacing operations create and verify consistent SQLite snapshots; neighboring replacement files can be built and
  rolled back safely.
- **Scope and current-state touchpoints:** Rework the isolated database/rebuild-tool orchestration represented by
  `scripts/refresh_chess_com.py` and the existing importer/analysis CLI entry points. The database path/connection
  helpers in `backend/app/features/positions/repository.py` are current-state evidence only before DB-09. Keep raw
  month files as the fetch ledger and use the SQLite backup facility rather than copying a live WAL database; no
  production backend/application/frontend module is a pre-gate implementation target.
- **Prerequisites:** DB-07 accepted.
- **Explicit exclusions:** No application activation, old-database modification/deletion, off-device disaster-recovery
  system, scheduled backup, or raw-source deletion.
- **Focused proof:** Empty-build versus refresh equivalence, skip/resume behavior, verified rolling snapshots, WAL-safe
  backup, interrupted rebuild recovery, neighboring replacement validation, and rollback without touching the old DB.
- **Escalate if:** Safe backup/rollback cannot be demonstrated with SQLite, or a proposed operation needs old-row
  migration or old-database mutation.
- **Handoff/selection criterion:** Select DB-09 only after replacement operations are proven without cutover.

### DB-09 — Rebuilt-database proof gate

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize the real-data fixture/sample,
  integrity assertions, measured access paths/indexes, direct capability queries, analysis sample, and acceptance
  thresholds without turning this gate into API work.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L742-L772,L774-L805,L864-L879`; `docs/grilling-docs/database-rebuild-schema.md:L119-L157,L716-L742,L781-L830`.
- **Visible result:** A rebuilt neighboring database containing real regenerated games, openings, positions,
  preference storage, and analysis data passes a documented proof gate for integrity and direct current-capability
  reads. DB-09 explicitly owns the database-level opening lookup proof: PGN replay produces the ordered recognized
  endpoints/current label, exact sequence and FEN lookup distinguish route and transposition matches, and lookup does
  not expose unreached future variations or imply the excluded Opening Line Library application surface. The initial
  25-position analysis mixture and on-demand bulk selection are proven without a persisted target list. The activation
  candidate contains no migrated or fabricated preference rows.
- **Scope and current-state touchpoints:** Exercise the rebuilt database directly against the data/tool outputs from
  DB-02 through DB-08, including the query meanings later consumed by
  `backend/app/features/position_context`, `move_response_distribution`, positions, openings, preferred move, and
  analysis features. These `backend/app` areas are named as later consumer evidence only; DB-09 performs no production
  backend/application/frontend integration. Measure indexes/access paths against real rebuilt data rather than
  synthetic laboratories.
- **Prerequisites:** DB-08 accepted.
- **Explicit exclusions:** No HTTP route, frontend, application-consumer, cutover, or deletion work.
- **Focused proof:** Foreign-key/check integrity, game viewer reconstruction, distinct-game Position Context,
  occurrence-based Move Response Distribution, opening route/transposition recognition, preference states, analysis
  quality/terminal behavior, initial 25 positions, bulk ordering, and measured query access paths. Prove preferred,
  explicit no-preference, and unconfigured states plus period transaction semantics in a disposable focused proof
  database or a fully rolled-back transaction; confirm the activation candidate remains empty of preference rows unless
  the user makes a real choice.
- **Escalate if:** Any named current capability needs a table outside the ten-table catalogue, or the rebuilt SQLite
  workload fails measured integrity/performance/concurrency requirements.
- **Handoff/selection criterion:** This is the absolute gate. Only after DB-09 is accepted may API-01 through API-04
  be assessed, planned, or implemented. DB-09's accepted evidence is the handoff for the first production consumer
  slice.

### API-01 — Game viewer read path

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
- **Prerequisites:** DB-09 accepted; no API/backend/application-consumer slice may start earlier.
- **Explicit exclusions:** No old database fallback, old contract compatibility layer, statistics projections, or
  Opening Line Library surface.
- **Focused proof:** Focused backend position tests, frontend position API/state tests, representative game navigation,
  exact PGN availability, final occurrence behavior, nullable metadata, and canonical FEN reconstruction.
- **Escalate if:** The viewer requires data excluded from `datasource_game`, `derived_game_position`, or
  `derived_position`, or the only proposed solution is preserving old storage contracts.
- **Handoff/selection criterion:** Select API-02 only after the rebuilt viewer path passes focused proof.

### API-02 — Direct statistics read paths

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

**Grilling REQUIRED** before this slice's implementation Plan/work begins, to finalize readiness evidence, replacement
path/configuration, maintenance-mode timing, switch/rollback mechanics, the active-path audit including the excluded
old Opening Line Library route, the required pre-activation disable/de-registration of that route, and live focused
scenarios without deleting or modifying the old database.

- **Authority:** `docs/grilling-docs/database-rebuild-direction.md:L80-L109,L881-L889`; `docs/grilling-docs/database-rebuild-schema.md:L10-L14,L716-L742`.
- **Visible result:** The required application and tools use the proven neighboring rebuilt database as the active
  database; games and openings are ready, incomplete optional Tool analysis does not block activation, and the excluded
  `/api/openings/line-library` surface was disabled/de-registered before activation rather than rebuilt.
- **Scope and current-state touchpoints:** Cutover configuration currently centers on
  `backend/app/features/positions/repository.py:DEFAULT_DATABASE_PATH`, `DATABASE_PATH_ENV`, and `database_path`,
  together with script/worker path consumers identified in the current implementation map. Validate all API and
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

These areas identify where execution may need to work; they do not override the destination or schema catalogue.

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
- No commits, pushes, branches, worktrees, stashes, unrelated record changes, or implementation authorization is
  implied by this document.
