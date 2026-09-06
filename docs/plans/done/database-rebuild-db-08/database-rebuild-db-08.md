# DB-08 rebuild, snapshot, and replacement operations - safely refresh and replace a rebuilt neighbour

> **Status:** completed - all eight DB-08 stages and the final flowchart review are accepted

- **Read trigger:** Read before DB-08 implementation or focused proof, after DB-07 acceptance.
- **Upstream:** `docs/grilling-docs/database-rebuild-direction.md`, especially sections 2.3-2.5, 3.1, 3.8-3.10,
  4.1-4.2, and the settled DB-08 sections 7-9; the DB-08 envelope in
  `docs/master-plans/database-rebuild/database-rebuild.md`; retained assessment evidence from
  `docs/flowcharts/database-toolchain.md` and `docs/flowcharts/database-operator-journeys.md`; and the accepted
  DB-01 through DB-07 Plans as historical implementation evidence. The current direction record is the binding
  grilling result; no additional product interview is required for this Plan.

## Outcome

An operator can refresh an empty or existing rebuilt neighbour from retained local sources, verify a partial database
or replacement-ready database, create a safe standalone snapshot, build and validate a managed candidate, replace the
neighbour only after an automatic verified snapshot and exclusive-access check, and roll back safely. An interruption
is recovered by the next normal idempotent rerun; no recovery command or permanent run/failure history is added.

## Scope

- **Included:** A package-owned DB-08 orchestration area under `src/chess_move_trainer/database/rebuild/`; thin
  additions to `src/chess_move_trainer/database/cli.py`; one read-only verifier shared by refresh, snapshot,
  replacement, rollback, and later proof; idempotent refresh over the existing schema, openings, and games services;
  opening-only partial checkpoints and complete replacement-readiness checks; the factual supported invocation or small
  preset for the settled initial 25-position serial Tool mixture; safe SQLite snapshots with verified rolling-three
  retention; managed temporary-candidate creation beside one configured rebuilt-neighbour destination; exclusive
  replacement and rollback; interrupted-candidate rerun recovery; focused package/CLI/source-boundary proof; and the
  final reconciliation of the three database flowchart documents.
- **Expected areas:** `src/chess_move_trainer/database/rebuild/**`,
  `src/chess_move_trainer/database/cli.py`, and only the smallest existing DB-01-DB-07 service seams needed for
  composition; `tests/database/rebuild/**`, focused additions to `tests/database/test_cli.py`,
  `tests/database/test_package_boundary.py`, and `tests/database/test_source_boundary.py`; and, only in the final
  stage, `docs/flowcharts/database-toolchain.md`, `docs/flowcharts/database-operator-journeys.md`, and
  `docs/flowcharts/README.md` where routing or legend wording is stale.
- **Excluded:** Application cutover or application configuration, production backend/frontend/API changes, any modification,
  snapshot, replacement, or deletion of the old database, raw-source modification or network acquisition during
  refresh, schema/table/index changes, migrations, new run/failure/audit/history/manifest tables, a recovery command,
  parallel Stockfish engines or `--workers`, opponent profiles, the Opening Line Library, DB-09 real-data proof,
  later API slices, legacy implementation reuse, completed historical Plan edits, and broad maintenance or Quality
  checks. Existing component commands remain available and are changed only by a bounded additive adjustment needed
  to expose the settled initial-analysis invocation.

## Stages

1. **completed - Establish the package-owned orchestration and CLI boundary.**
   - **Ordered actions:**
     1. Add the DB-08-owned importable rebuild/operations package with ordinary typed configuration, outcomes, and
        errors. Keep business logic out of `database/cli.py`; depend inward on the accepted DB-01-DB-07 services and
        never import, wrap, copy, or delegate to legacy scripts or production application modules.
     2. Define one explicit configuration value for the rebuilt-neighbour destination and a package-owned temporary
        candidate beside it. Do not expose repeated arbitrary source/destination pairs for replacement operations.
     3. Register one coherent rebuild command group for refresh, verify, snapshot, managed replacement, and rollback.
        Choose exact spellings and flags within the existing explicit-path, noninteractive Typer conventions, provide
        useful help and meaningful `0/1/2/3/130`-compatible outcomes, and preserve all existing component command
        registrations and behavior.
     4. Keep the future API-03 queue worker separate from direct serial bulk publication; do not add `--workers`.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_configuration.py tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` from `G:\ChessMoveTrainer`; command timeout `90s`, Bash tool timeout `120000ms`. Add finite help invocations for the resolved rebuild group and each resolved command, each with command timeout `30s` and Bash tool timeout `60000ms`.
   - **Escalation boundary:** Stop for a new dependency, public raw database handle, arbitrary active/candidate path contract, legacy/runtime delegation, changed existing component CLI behavior, parallel Stockfish design, or a new persisted state family.
   - **Breakpoint:** none; exact command spelling and internal module layout are bounded implementation details under the settled behavior.

2. **completed - Deliver the standalone structural/readiness verifier.**
   - **Ordered actions:**
     1. Implement one read-only verifier that accepts a rebuilt database, managed candidate, or SQLite snapshot and
        reuses the same service from every DB-08 operation.
     2. Check exact v1 compatibility, `PRAGMA user_version`, SQLite integrity, foreign-key integrity, and the
        database facts needed to distinguish a structurally valid partial database from a complete replacement-ready
        candidate.
     3. Treat an opening-only database as a valid preserved partial checkpoint, not corruption; require both ready
        openings and imported games for replacement readiness. Do not overload the existing informational
        `schema inspect` command.
     4. Keep verification read-only, deterministic, automation-safe, and explicit about the target kind in output and
        exit behavior.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_verification.py tests/database/test_cli.py -q -k "verify or inspection"` from `G:\ChessMoveTrainer`; command timeout `90s`, Bash tool timeout `120000ms`. Cover valid partial, valid ready, malformed, incompatible, corrupt, foreign-key-invalid, and snapshot targets without creating or changing a missing target.
   - **Escalation boundary:** Stop if readiness needs guessed application data, a new table/state record, schema mutation, a different integrity meaning, or an application/API contract.
   - **Breakpoint:** none; exact checks and status mapping are factual Plan implementation work within the settled structural-versus-ready distinction.

3. **completed - Compose the idempotent refresh and partial-checkpoint behavior.**
   - **Ordered actions:**
     1. Implement one refresh service and CLI path that treats an empty database as the first build, consumes retained
        local raw months and caller-owned opening TSV files, and never performs network acquisition.
     2. Reuse the existing schema creation, opening import, and game import services without shelling out to their
        CLIs. Keep those lower-level commands available for focused reruns and diagnosis.
     3. Run opening and game stages independently. Preserve a successful opening publication and its canonical
        positions when the game stage is unavailable; allow unrelated stages to continue after another stage fails;
        retain per-valid-game commits and safe correction/rerun behavior; and report an unsuccessful overall refresh
        until every required stage and the final verifier pass.
     4. Recompute eligibility and skip already-satisfied work on rerun without adding run history, failure rows, or
        source manifests. Distinguish an opening-only partial checkpoint from a replacement-ready database.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_refresh.py tests/database/games/test_import_service.py tests/database/openings/test_persistence.py -q` from `G:\ChessMoveTrainer`; command timeout `120s`, Bash tool timeout `150000ms`. Prove empty-build/refresh equivalence, independent-stage continuation, opening-only preservation, final readiness failure, skip/resume, committed-game survival, corrected-game rerun, no network access, and unchanged lower-level command contracts.
   - **Escalation boundary:** Stop if refresh requires raw-source edits outside the settled DB-03 current-month behavior, migration, all-or-nothing cross-stage transactions, permanent progress/failure records, application consumers, or a different opening/game readiness rule.
   - **Breakpoint:** none; the user has settled the independent-stage and partial-checkpoint behavior.

4. **completed - Prove the settled serial initial-analysis invocation.**
   - **Ordered actions:**
     1. Inspect the accepted DB-07 target selector and direct bulk path to determine the smallest supported invocation or
        preset that selects the already-settled mixture of 25 commonly reached and technical-sample positions.
     2. Add only the bounded package/CLI support needed to invoke that mixture predictably after games and openings are
        available. Keep Tool analysis serial, resumable, directly published, and outside the queue worker path; do not
        add `--workers` or a target-list table.
     3. Preserve existing `stockfish bulk` behavior and prove that no queue rows are introduced by direct bulk work and
        that the later queue worker remains relevant only to API-03 requests.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_initial_analysis.py tests/database/stockfish/test_targets.py tests/database/stockfish/test_bulk.py tests/database/test_cli.py -q -k "initial or stockfish"` from `G:\ChessMoveTrainer`; command timeout `90s`, Bash tool timeout `120000ms`. Use deterministic/fake-engine proof for exact mixture selection, serial invocation, resumability, direct publication, and queue separation; retain the accepted one-position real-engine smoke rather than running a full initial analysis.
   - **Escalation boundary:** Stop if the 25-position requirement needs parallel engines, a new persisted target/run record, a changed DB-07 profile, a new queue contract, or a changed acceptance threshold.
   - **Breakpoint:** none; the exact invocation is factual work explicitly deferred by the direction record.

5. **completed - Implement safe snapshots and managed candidate staging.**
   - **Ordered actions:**
     1. Implement standalone snapshot creation with SQLite's backup facility, including WAL-safe behavior, explicit
        verification through the shared verifier, deterministic operator output, and atomic artifact handling.
     2. Retain no more than the three newest verified pre-operation snapshots, deleting older snapshots only after the
        new snapshot verifies. Do not add scheduled or off-device backup behavior.
     3. Build a candidate in the configured neighbour's temporary sibling path using the same refresh operation and
        verifier. Keep isolated candidate construction and safe snapshot/verification compatible with other local work.
     4. Ensure a failed or incomplete candidate never replaces the working neighbour and leaves no permanent recovery
        record.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_snapshots.py tests/database/rebuild/test_candidate.py -q` from `G:\ChessMoveTrainer`; command timeout `120s`, Bash tool timeout `150000ms`. Prove fresh and WAL-safe backup, snapshot verification, rolling-three retention, standalone invocation, candidate isolation, partial-candidate failure, and preservation of the working neighbour.
   - **Escalation boundary:** Stop if SQLite backup cannot produce a consistent verified snapshot, candidate staging needs arbitrary path pairs, retention needs a database table, or raw-source/old-database backup is requested.
   - **Breakpoint:** none; the backup mechanism, rolling-three rule, and managed destination/candidate relationship are settled.

6. **completed - Add exclusive replacement and rollback.**
   - **Ordered actions:**
     1. Verify the managed candidate and obtain exclusive access to the rebuilt-neighbour destination before mutation.
        Fail clearly when another process owns the destination; never terminate or forcibly interrupt another process.
     2. For replacement, automatically create and verify a fresh snapshot of the current neighbour, apply rolling-three
        retention, and only then replace the neighbour with the verified candidate. Do not change application
        configuration or touch the old database.
     3. For rollback, select the newest verified pre-replacement snapshot by default or an explicitly selected retained
        older snapshot, verify it again, preserve the current neighbour before overwrite, and restore only the managed
        neighbour path.
     4. Keep replacement and rollback exclusive while allowing safe verification, snapshotting, and isolated candidate
        work to coexist as settled.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_replacement.py tests/database/rebuild/test_rollback.py tests/database/test_cli.py -q -k "replace or rollback"` from `G:\ChessMoveTrainer`; command timeout `120s`, Bash tool timeout `150000ms`. Prove busy-access failure without process termination, automatic fresh snapshot, candidate verification ordering, rolling retention, atomic successful swap, failed-swap preservation, default/explicit rollback selection, re-verification, current-neighbour preservation, and old-database byte/path non-involvement.
   - **Escalation boundary:** Stop if exclusive access cannot be demonstrated, replacement needs an application cutover, rollback needs old-database access, or a destructive operation cannot preserve a verified recovery point.
   - **Breakpoint:** none; the user has settled the replacement and rollback safety boundary.

7. **completed - Prove interruption recovery and the complete focused DB-08 contract.**
   - **Ordered actions:**
     1. Exercise interruption, crash-like failure, and partial temporary-candidate cases. Confirm that the working
        neighbour remains active and the next normal refresh or staging run resumes idempotently without a recover
        command.
     2. Add only affected CLI, package-boundary, and source-boundary assertions for explicit inputs, noninteractive
        help, output channels, statuses, no legacy/runtime delegation, and no new persistence machinery.
     3. Run the final focused DB-08 behavioral set after all operation stages; retain unaffected DB-01-DB-07 proof and
        rerun earlier proof only when a later change invalidates its command, inputs, behavior, dependencies, or
        environment.
   - **Focused proof:** `timeout 150s .venv/Scripts/python.exe -m pytest tests/database/rebuild tests/database/test_cli.py tests/database/test_package_boundary.py tests/database/test_source_boundary.py -k "rebuild or refresh or verify or snapshot or replace or rollback" -q` from `G:\ChessMoveTrainer`; command timeout `150s`, Bash tool timeout `180000ms`. This is the focused DB-08 set only; it must not include application tests, full maintenance checks, or broad repository checks.
   - **Escalation boundary:** Stop for any new command contract, dependency, persistence/history mechanism, application/API integration, old-database operation, or failure that can only be absorbed by weakening the settled safety behavior.
   - **Breakpoint:** none; coordinator review is only required if proof exposes a genuine settled-boundary conflict.

8. **completed - Reconcile the database flowcharts after the real behavior exists.**
   - **Ordered actions:**
     1. Update `docs/flowcharts/database-toolchain.md` and `docs/flowcharts/database-operator-journeys.md` only after
        the implemented command names and invocation behavior are real. Remove stale DB-08 candidate labels and show
        refresh, structural versus replacement-ready verification, automatic snapshot-before-replacement, managed
        candidate staging, exclusive replacement/rollback, and rerun-based recovery.
     2. Correct the operator chain to show serial direct bulk publication separately from the API-03 queue worker, retain
        acquisition as a separate step, and show opening-only partial checkpoints versus replacement readiness.
     3. Update `docs/flowcharts/README.md` legend/routing text only where the implemented command surface or decision-
        support status changed. Do not edit the flowcharts earlier in the Plan or edit historical records.
     4. Add a bounded documentation-consistency proof that checks the three flowchart documents agree with the settled
        command surface and contain no stale candidate behavior.
   - **Focused proof:** `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_flowchart_consistency.py -q` from `G:\ChessMoveTrainer`; command timeout `60s`, Bash tool timeout `90000ms`. This proof is limited to the three named flowchart documents and DB-08 behavior terms; it is not a repository-wide documentation or hygiene check.
   - **Escalation boundary:** Stop if reconciliation would require reopening DB-08 behavior, changing the old-database/cutover boundary, or editing user-owned flowchart meaning beyond the implemented command surface.
   - **Breakpoint:** final coordinator review of the visible diagrams; no earlier documentation stage is required.

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. The final flowchart reconciliation is
deliberately the last stage.

## Progress and decisions

- **Stage 1:** completed - package/configuration/CLI boundary accepted. Proof: 24 focused configuration/package/source-boundary tests passed in 0.70s; the focused rebuild CLI test passed in 1.25s; all six finite rebuild-group/command help invocations exited 0. The managed sibling candidate and `rebuild refresh|verify|snapshot|replace|rollback` boundary are established; breakpoint: none.
- **Stage 2:** completed - shared read-only structural/readiness verifier accepted. Proof: 15 focused verifier/CLI tests passed in 3.72s with 64 unrelated tests deselected; the directly affected package/source-boundary proof passed 15 tests in 0.66s before a verifier-only classification correction and remains valid. Opening-only and empty targets are valid partial checkpoints, games-plus-openings are replacement-ready, and incompatible, corrupt, foreign-key-invalid, missing, and unavailable targets have distinct outcomes; breakpoint: none.
- **Stage 3:** completed - idempotent local refresh and partial-checkpoint orchestration accepted. Proof: 18 focused refresh/game/opening tests passed in 3.72s; the focused rebuild CLI test passed in 0.76s and three refresh/verify CLI tests passed in 2.99s with 64 unrelated tests deselected before a service-only no-op correction and remain valid. Identical explicit sources are compared to current normalized output and skipped without persisted hashes or run state; changed sources still use the accepted atomic opening publication and transactional game-correction paths; breakpoint: none.
- **Stage 4:** completed - `stockfish bulk --preset initial` selects 20 positions in the accepted common ordering
  plus five fixed technical positions covering checkmate, stalemate, legal en passant, promotion, and castling;
  overlaps are removed before common-position backfill so the deterministic total remains 25. The existing bulk
  path remains serial, resumable, directly published, and queue-free, and `--limit` remains available for ordinary
  bulk use but cannot be combined with this preset. Proof: the prescribed focused fake-engine command passed 24
  tests with 57 deselected in 10.66s; retained earlier proof was unaffected. Breakpoint: none.
- **Stage 5:** completed - `rebuild snapshot` creates and verifies an atomic WAL-safe SQLite backup before applying
  rolling-three retention, and `rebuild candidate` refreshes and verifies only the configured neighbour's managed
  sibling candidate without accepting arbitrary destination paths or modifying the neighbour. Focused proof: 8 tests
  passed in 2.98s; breakpoint: none.
- **Stage 6:** completed - replacement and rollback verify their source, serialize cooperating DB-08 operations,
  and hold a Windows destination-file guard through the verified recovery snapshot and atomic `ReplaceFileW` swap.
  A separate plain SQLite writer is rejected without termination or neighbour mutation; rollback supports newest-by-
  default and explicit retained snapshots and preserves the current neighbour first. Focused proof: 14 tests passed
  with 68 deselected in 8.80s after correcting the initial cooperative-mutex-only exclusivity gap; breakpoint: none.
- **Stage 7:** completed - interruption after opening publication, a crash-like game-stage failure, and an empty
  managed candidate all leave the neighbour unchanged and recover through the next normal idempotent candidate run.
  Rebuild CLI interruptions consistently return 130, unexpected operational failures return 1, and no recovery
  command or persistent run/failure state was added. Final focused DB-08 proof: 74 tests passed with 79 deselected
  in 23.68s; breakpoint: none.
- **Stage 8:** completed - the toolchain and operator-journey diagrams now show the implemented six-command rebuild
  surface, valid partial versus replacement-ready states, separate acquisition, direct serial initial analysis versus
  API-03 queue work, managed candidate isolation, verified snapshot ordering, exclusive replacement/rollback, and
  ordinary-rerun recovery. The bounded consistency proof passed 1 test in 0.71s after final command-label, edge, and
  legend corrections; the coordinator Markdown review accepted both diagrams.

## Proof

- The stage-specific finite pytest and CLI-help commands above are the only implementation proof prescribed by this Plan.
- Proof covers refresh equivalence, independent-stage progress, structural versus replacement readiness, initial serial
  analysis selection, SQLite backup safety, rolling-three retention, managed candidate isolation, exclusive replacement,
  rollback, interruption rerun, CLI behavior, source boundaries, and final flowchart consistency.
- No lint, formatting, broad type/build, source-size, aggregate maintenance, full suite, application E2E, or Quality
  validation belongs to DB-08. Retained DB-01-DB-07 behavioral proof is reused until an affecting change invalidates it.

## Escalation boundaries

- Escalate any product, API, data, schema, dependency, ownership, destructive, concurrency, or acceptance decision not
  already settled in `database-rebuild-direction.md:864-966`.
- Escalate any request to modify, snapshot, replace, delete, or migrate the old database; change application
  configuration or cutover; modify raw sources outside DB-03's approved current-month behavior; or add API/frontend work.
- Escalate any need for `--workers`, concurrent Stockfish engines, persistent run/failure/audit/history state, a target
  list table, a shared JSON queue, arbitrary replacement paths, or a dedicated recovery command.
- Escalate any need to wrap, import, copy, delegate to, patch, or incrementally continue legacy tools, or to use
  production `backend/app` modules before DB-09.
- Escalate if the final flowcharts cannot truthfully express the implemented behavior without reopening the settled
  DB-08 decisions.

## Visible result

> An operator can refresh, verify, snapshot, replace, or roll back the rebuilt neighbour safely, and an interrupted
> candidate is recovered by the next normal rerun without touching the old database.
