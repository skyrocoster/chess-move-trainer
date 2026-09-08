# DB-09 simple direct database lifecycle - set up and update one usable database

> **Status:** done - direct lifecycle, real database, separate Stockfish proof, and closeout accepted 2026-09-08

- **Read trigger:** Read before implementing the DB-09 direct lifecycle, its focused proof, or its final result recording.
- **Upstream:** [confirmed simple lifecycle](../../../grilling-docs/database-rebuild-simple-lifecycle.md) is the
  current behavioral authority for this correction. The [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md)
  still governs sequencing, the ten-table schema, clean package ownership, the pre-application gate, and legacy
  boundaries, but its conflicting neighbor/candidate/snapshot/replacement/rollback requirements are superseded by the
  confirmed lifecycle. The approved schema and data authorities, DB-01 through DB-08A results, and prior grilling
  records remain historical evidence where they do not conflict. This Plan supersedes conflicting active DB-09
  statements without rewriting or falsifying completed DB-08 history.

## Outcome

An operator has one long-lived SQLite database at `data/database/chess.db`. `setup` creates it once from the complete
base sources, `update games` directly refreshes the saved Chess.com month ledger and persists new or corrected games,
and `update openings` directly refreshes the latest valid five-file opening catalogue. Each operation creates the
schema-defined normalized and derived rows it owns, performs only quick local checks, and reports meaningful failure
without exposing a neighbor, candidate, replacement, snapshot, rollback, recovery, or separate verification workflow.
Stockfish remains a separate bounded operation used by DB-09 proof, not by ordinary setup or updates.

## Scope

- **Included:** The fixed direct destination `data/database/chess.db`; the package-owned three-command public
  data-loading surface `setup`, `update games`, and `update openings`; internal composition of acquisition, source
  validation, normalization, persistence, canonical-position resolution, opening-route publication, and quick checks;
  removal of obsolete database-file lifecycle machinery; direct DB-09 real-data proof; and bounded separate Stockfish
  proof.
- **Expected areas:** `src/chess_move_trainer/database/{cli.py,rebuild/**,games/**,openings/**}` and only the smallest
  shared service seams needed for the three operations; focused tests under `tests/database/` and the existing
  `tests/database/{games,openings,rebuild}/` areas; `docs/flowcharts/{database-command-inventory.md,database-toolchain.md,database-operator-journeys.md,README.md}`;
  the active Plan's related safe example/config documentation; and the final current master-plan result record.
- **Excluded:** Backend/frontend/application integration, HTTP API changes, cutover, old production database mutation
  or deletion, raw game-source deletion, schema/table expansion, dependency changes, legacy-script cleanup, unrelated
  files under `data/database/`, commits, pushes, branches, worktrees, stashes, broad maintenance suites, lint,
  formatting, type/build, source-size, and repository-hygiene checks. Do not rewrite completed Plans or historical
  grilling records. Do not add resume, force, reset, snapshot, swap, backup, rollback, or recovery behavior.

## Stages

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later stage changes its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof. The coordinator may split an oversized stage without changing the approved outcome.

### 1. complete - Document the canonical direction and supported public surface

**Ordered actions**
1. Record the fixed direct destination, three public data-loading operations, setup cleanup boundary, incremental
   game semantics, latest-valid opening semantics, quick-check boundary, Stockfish separation, and manual rare-rebuild
   rule in the current master plan and current flowchart/command-inventory documentation. Do not rewrite the completed
   DB-08 Plan, DB-08A Plan, or prior grilling records.
2. Replace the stale DB-09 command inventory and flowchart language that treats a neighboring database, candidate,
   replacement, snapshot, rollback, recovery, or replacement-readiness gate as supported. Keep the explicit old-database,
   raw-source, legacy-script, schema, and pre-application boundaries.
3. Make the supported CLI inventory describe only `setup`, `update games`, and `update openings` as public data-loading
   workflows. Stockfish commands remain a separate analysis surface; internal services may remain separately owned.
4. Keep other files under `data/database/` outside the workflow and do not inspect, clean, reorganize, or use them as
   setup blockers.

**Focused proof**
- Perform a bounded manual/static review of the edited master/flowchart/command-inventory documentation against the
  confirmed lifecycle and this Plan. Confirm the exact fixed path, exactly three public data-loading workflows,
  separate Stockfish analysis, absent database-file lifecycle machinery, manual rare-rebuild boundary, and the
  explicit old-database/raw-source/schema/legacy boundaries.
- This is a documentation-only stage. It does not own CLI implementation, CLI tests, or help scenarios; those proofs
  are intentionally deferred until Stage 2 has implemented the adapters. No real database is created in this stage.

**Escalation boundary:** Stop for a new public data-loading operation, a changed Stockfish contract, a schema or
dependency decision, an application/cutover decision, or any request to rewrite completed or historical records.

**Breakpoint:** Coordinator review that the master/current flowchart correction records the new direction without
falsifying DB-08 history.

### 2. complete - Establish the direct lifecycle foundation, public adapters, and obsolete-contract removal

**Ordered actions**
1. Make the package-owned lifecycle resolve only to `data/database/chess.db`; do not expose an arbitrary destination,
   neighbor/candidate path, replacement target, snapshot path, or verification target.
2. Add the thin public `setup`, `update games`, and `update openings` adapters in the database CLI and keep business
   rules in package services. Remove public registration and package contracts for separate data fetch/import/rebuild/
   replacement/snapshot/rollback/recovery/verification workflow commands.
3. Remove database-file lifecycle modules and exports that exist solely for managed database candidates, snapshots,
   replacement swaps, rollback, recovery, or exclusive destructive access; do not leave dead public contracts that are
   merely bypassed. Preserve Stockfish candidate-line services, storage, and semantics because those are schema-domain
   analysis data rather than database-file lifecycle machinery.
4. Retain lower-level internal acquisition, normalization, persistence, canonical-position, opening publication, and
   Stockfish services where the three operations compose them. Keep ordinary SQLite transaction boundaries,
   invalid-download prevention, and complete opening-catalogue publication;
   these are local write-integrity rules and must not become user-visible lifecycle recovery behavior.

**Focused proof**
- After the adapters and obsolete database-file contracts have been changed, run the focused package/source-boundary and
  lifecycle CLI tests only:
  `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py tests/database/test_lifecycle_cli.py -q`
  (command timeout `120s`; Bash tool timeout `150000ms`).
- Run finite help scenarios after the CLI adapters exist:
  `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database setup --help`,
  `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database update games --help`, and
  `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database update openings --help` (each command timeout
  `30s`; Bash tool timeout `60000ms`). Prove the old lifecycle commands are absent from supported help and that the
  three new adapters have useful help, required fixed-path behavior, noninteractive invocation, and meaningful
  `0/1/2/130` mapping where applicable.

**Escalation boundary:** Stop if removing the old surface would break an unrelated supported Stockfish/preferred-move
contract, or if correctness appears to require a public reset, resume, force, snapshot, swap, rollback, recovery, or
separate verify command.

**Breakpoint:** None while the three-command boundary and fixed destination remain as confirmed.

### 3. complete - Implement one-time setup into an absent database

**Ordered actions**
1. Check `data/database/chess.db` before any setup mutation. If any file exists, fail clearly and do not replace,
   modify, or clean it.
2. For an absent path, create the approved schema, obtain/import the complete base game data, obtain/import the latest
   valid five-file opening data, and create all required schema-defined positions, occurrences, opening routes, and
   other derived rows. Compose internal services rather than invoking public subcommands or legacy scripts.
3. Do not run Stockfish during setup. Keep the normal setup result limited to quick operation-local checks.
4. If setup created the database and later fails, delete only that newly created `data/database/chess.db`. Do not
   delete source files, pre-existing files, other `data/database/` files, or create a resume/recovery record. A failed
   setup has no supported resume protocol.

**Focused proof**
- Add focused setup scenarios and run:
  `timeout 180s .venv/Scripts/python.exe -m pytest tests/database/test_setup.py -q`
  (command timeout `180s`; Bash tool timeout `210000ms`).
- Cover absent-path success, pre-existing-file refusal with byte preservation, failure after database creation with only
  the new database removed, complete source composition, derived-row creation, no Stockfish invocation, no legacy
  delegation, and quick-check output. Use temporary paths in tests; the production contract remains fixed.

**Escalation boundary:** Stop if setup needs to delete/replace a pre-existing `chess.db`, delete raw sources, alter the
schema catalogue, add persisted progress/failure state, or guarantee resumability.

**Breakpoint:** None; the absent-path and cleanup behavior is settled by the confirmed lifecycle.

### 4. complete - Implement direct incremental game updates

**Ordered actions**
1. Implement `update games` over the saved monthly files as the only fetch ledger. Start at the newest saved month,
   refetch that month, fill missing months through the current month, and process months independently.
2. Validate and publish each accepted month without changing a prior usable source file on malformed or incomplete
   download. Merge refetched games by Chess.com ID: add new games, replace corrected source representations, and retain
   games omitted by a later response.
3. Persist valid new/corrected games directly to `data/database/chess.db`, creating/replacing their normalized game,
   canonical-position, occurrence, and required derived rows through existing transaction composition. Keep completed
   months and valid earlier game commits when a later month fails.
4. Skip malformed, illegal, unsupported, or otherwise rejected games individually, continue valid games, and report
   each skipped game and its reason. Do not add fetch-state, run-history, manifest, or recovery persistence.
5. Keep the command’s final checks quick and local; full integrity, measurements, and DB-09 proof remain separate.

**Focused proof**
- Run the direct update and existing lower-level game behavior set:
  `timeout 210s .venv/Scripts/python.exe -m pytest tests/database/test_update_games.py tests/database/games/test_acquisition.py tests/database/games/test_import_service.py tests/database/games/test_persistence.py -q`
  (command timeout `210s`; Bash tool timeout `240000ms`).
- Cover newest-month refetch, gap filling, new/corrected/omitted UUID behavior, independent month progress, later-month
  failure, malformed/illegal/unsupported per-game reporting, direct derivation, no fetch-state tables, and no network
  call from tests that exercise local persistence.

**Escalation boundary:** Stop if the existing month files and Chess.com identifiers cannot represent the settled merge,
if omitted games require destructive deletion, if a later-month failure needs cross-month rollback, or if a new table,
dependency, raw-source policy, or application contract is required.

**Breakpoint:** None while the saved-month ledger and direct per-game transaction semantics remain sufficient.

### 5. complete - Implement complete latest-valid opening updates

**Ordered actions**
1. Make `update openings` obtain the latest upstream `a.tsv` through `e.tsv` set without a configured commit/version
   input. Keep any resolved upstream revision ephemeral and do not persist source history or a manifest.
2. Stage and validate all five files before publication. An invalid or incomplete set must preserve both the retained
   source files and the current database catalogue.
3. On success, retain only the latest valid five-file set and rebuild opening labels, routes, route moves, and endpoint
   positions together in one catalogue publication transaction. Do not touch game or occurrence data.
4. Report quick operation-local success/failure only; do not expose a separate opening-fetch/import/verify workflow.
   Retain ordinary file publication safeguards, but do not add database snapshot or rollback machinery.

**Focused proof**
- Run the direct opening update and retained source/persistence tests:
  `timeout 210s .venv/Scripts/python.exe -m pytest tests/database/test_update_openings.py tests/database/openings/test_acquisition.py tests/database/openings/test_source.py tests/database/openings/test_persistence.py -q`
  (command timeout `210s`; Bash tool timeout `240000ms`).
- Cover latest-upstream five-file retrieval through injected transport, validation-before-publication, invalid-set
  preservation, successful complete catalogue/route regeneration, route endpoint derivation, unchanged game rows, and
  cleanup of transient source staging artifacts.

**Escalation boundary:** Stop if latest upstream cannot be defined with the existing dependency/transport boundary, if
partial catalogue publication is unavoidable, if source history/pinning persistence is requested, or if opening refresh
requires changing game data or the schema catalogue.

**Breakpoint:** None; the latest-valid complete-set boundary is settled upstream.

### 6. complete - Reconcile focused contracts and retain unaffected proof

**Ordered actions**
1. Update focused configuration examples, package exports, CLI tests, source-boundary tests, command inventory, and
   flowchart consistency checks to the three public workflows and fixed path. Adapt stale assertions rather than
   weakening or skipping them; do not duplicate Stage 2's adapter implementation ownership.
2. Delete or replace candidate-path DB-09 helpers, fixtures, and assertions with direct `data/database/chess.db` path
   checks. Remove candidate/replacement-readiness expectations instead of merely bypassing them. Keep aggregate-only
   proof, privacy boundaries, direct readers, opening recognition, preference emptiness, access-plan measurement
   helpers, and Stockfish candidate-line semantics.
3. Do not rerun or rewrite completed DB-08 snapshot/replacement/rollback proof. Those behaviors are intentionally retired;
   the completed DB-08 Plan remains historical. Retain DB-01 through DB-07 lower-level proof until a shared behavior,
   command, dependency, or environment change invalidates it.
4. Rerun affected DB-08A acquisition and shared CLI/boundary proof where command wiring or latest-upstream behavior
   changed. Retain the accepted lower-level game normalization/persistence and opening parsing proofs where their
   exercised contracts remain unchanged.

**Focused proof**
- Run the focused contract set:
  `timeout 150s .venv/Scripts/python.exe -m pytest tests/database/test_command_inventory.py tests/database/test_configuration_examples.py tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q`
  (command timeout `150s`; Bash tool timeout `180000ms`).
- Confirm no separate fetch/import/verify/rebuild/replacement workflow appears in supported help. Stage 2 owns the
  lifecycle CLI/help proof; retain it here unless this stage changes adapter wiring. If adapter wiring does change,
  rerun the exact finite Stage 2 CLI test and help commands before accepting this stage.

**Escalation boundary:** Stop for any need to edit completed Plans or prior grilling, remove Stockfish analysis-line
semantics, broaden public API ownership, or absorb an unrelated `data/database/` file change.

**Breakpoint:** Coordinator review of the final supported command inventory before real-data population.

### 7. complete - Populate the fixed database and complete direct DB-09 proof

**Ordered actions**
1. Confirm only the exact precondition for `data/database/chess.db`: it must be absent before setup. If it exists,
   stop rather than remove, move, replace, or inspect unrelated files under `data/database/`.
2. Run the supported `setup` against real retained source data and accept only a successful direct database result.
   Then exercise real `update games` and `update openings` scenarios without invoking separate public fetch/import or
   verification commands.
3. Prove the direct database with aggregate integrity/schema/FK checks, game reconstruction and occurrence meanings,
   direct Position Context and Move Response Distribution meanings, opening route/transposition recognition, empty
   preference storage, analysis reads, and measured access paths. Full proof routines remain outside normal commands.
4. Invoke Stockfish separately with the already accepted package/profile and a bounded sample (not from setup or either
   update command), then prove its published/read result independently. Do not add queue/run/history state.
5. Keep all evidence aggregate and privacy-safe. Do not use or mutate the old production database, delete raw sources,
   or treat other files under `data/database/` as blockers.

**Focused proof**
- Real setup scenario: `timeout 900s .venv/Scripts/python.exe -m chess_move_trainer.database setup` (command timeout
  `900s`; Bash tool timeout `930000ms`).
- Real direct game update scenario: `timeout 900s .venv/Scripts/python.exe -m chess_move_trainer.database update games`
  (command timeout `900s`; Bash tool timeout `930000ms`).
- Real direct opening update scenario: `timeout 600s .venv/Scripts/python.exe -m chess_move_trainer.database update openings`
  (command timeout `600s`; Bash tool timeout `630000ms`).
- Separate bounded Stockfish publication: `timeout 360s .venv/Scripts/python.exe -m chess_move_trainer.database stockfish bulk --database data/database/chess.db --executable STOCKFISH18 --limit 1`
  (command timeout `360s`; Bash tool timeout `390000ms`), with `STOCKFISH18` replaced only by the already configured
  executable path.
- Direct DB-09 proof with the final direct path:
  `DB09_DATABASE=data/database/chess.db timeout 300s .venv/Scripts/python.exe -m pytest tests/database/rebuild/test_db09_proof.py tests/database/rebuild/test_db09_measurements.py tests/database/rebuild/test_db09_persistence_performance.py -q`
  (command timeout `300s`; Bash tool timeout `330000ms`).
- These scenarios are the only real-data/engine proof in this Plan; no full maintenance, aggregate, lint, formatting,
  build, type, source-size, or hygiene run is required.

**Escalation boundary:** Stop if `chess.db` already exists, real source acquisition cannot complete, direct incremental
semantics fail against the schema identifiers, a new index/table/dependency is needed beyond evidence-backed scope, or
Stockfish proof requires changing its accepted profile or persistence contract.

**Breakpoint:** Coordinator acceptance of the real direct database and focused DB-09 evidence before any application
slice is considered.

### 8. complete - Record final evidence and close the active Plan

**Ordered actions**
1. Record each accepted stage, exact focused proof, retained proof, and any breakpoint decision in this Plan. State
   plainly that the direct database is usable and that setup/update commands do not run full proof routines.
2. Record the concise accepted DB-09 result in the current master plan only after the direct evidence is accepted. Do not
   rewrite the completed DB-08 or DB-08A records; describe their retired lifecycle machinery as historical rather than
   pretending it was never implemented.
3. After any final command-inventory documentation change, run the bounded consistency check and perform the manual
   template review. Request coordinator acceptance of the visible result and evidence record; mark this Plan done only
   after the direct database, three-command surface, separate Stockfish proof, and exclusions have been accepted. Leave
   the repository uncommitted.

**Focused proof**
- Run the bounded command-inventory consistency check once after final command-inventory documentation changes:
  `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/test_command_inventory.py -q`
  (command timeout `60s`; Bash tool timeout `90000ms`).
- Perform a manual review of this Plan against `docs/PLAN_TEMPLATE.md`; no automated Plan checker is present.

**Escalation boundary:** Stop if final documentation cannot truthfully distinguish the superseded DB-08 history from the
current direct lifecycle, or if closeout requires unrelated cleanup, master-plan expansion, application work, or a new
acceptance decision.

**Breakpoint:** Coordinator acceptance of the final visible result and evidence record.

## Progress and decisions

- **Stage 1:** complete - coordinator accepted the bounded manual/static review of the current master plan and
  flowchart records. They now name the exact `data/database/chess.db` destination, exactly `setup`, `update games`,
  and `update openings` as public data-loading workflows, separate Stockfish analysis, the unsupported database-file
  lifecycle machinery, the manual rare-rebuild rule, and the old-database/raw-source/schema/legacy/pre-application
  boundaries. No source, test, historical record, or real database changed; breakpoint passed 2026-09-08.
- **Stage 2:** complete - coordinator accepted the fixed-path lifecycle seam, the three thin data-loading adapters,
  and removal of obsolete candidate/snapshot/replacement/rollback/recovery/verification modules and exports while
  retaining separate supported domain surfaces. The final focused command passed `24` tests, and the finite `setup`,
  `update games`, `update openings`, and top-level help scenarios all exited `0`, described the non-configurable
  `data/database/chess.db` destination, and omitted retired database-file lifecycle commands. No real database,
  network, or engine operation occurred; breakpoint: none.
- **Stage 3:** complete - coordinator accepted the fixed-path setup composition and its focused temporary-path proof:
  `tests/database/test_setup.py` passed `5` tests. The accepted scenarios cover complete source composition and owned
  derived rows, refusal before side effects with byte preservation, deletion of only a newly created failed database,
  quick checks, and no Stockfish, legacy script, public-subcommand, or real-network use. The lifecycle behavior change
  invalidated only its retained CLI test; `tests/database/test_lifecycle_cli.py` was rerun and passed `7` tests.
- **Stage 4:** complete - coordinator accepted the direct saved-month-ledger update and focused proof. The exact Stage 4
  command passed `49` tests, covering newest-month refetch, gap filling, Chess.com ID correction/omission semantics,
  validation before source publication, independent month and transaction progress, reported per-game rejection,
  direct normalized/derived persistence, absent fetch-state tables, and transport-free local persistence. CLI/help and
  setup behavior were unchanged, so their retained passing proof remains valid.
- **Stage 5:** complete - coordinator accepted the latest-valid five-file opening update and its exact focused proof,
  which passed `64` tests. Injected-transport scenarios and retained lower-level tests prove validation before
  publication, invalid/incomplete preservation, transient-staging cleanup, ephemeral upstream revision, complete
  transactional catalogue/route/move/endpoint regeneration, and unchanged game/occurrence rows. CLI, setup, and game
  update behavior were unaffected, so their accepted proof remains retained.
- **Stage 6:** complete - coordinator accepted the reconciled fixed-path examples, package/source boundaries, command
  inventory checks, and direct-path DB-09 proof helpers. The obsolete rebuild example and candidate-path helper were
  deleted rather than bypassed. The final exact focused command passed `21` tests, and the bounded inventory review
  reconfirmed exactly three public data-loading workflows, separate Stockfish, the manual rare-rebuild rule, retired
  lifecycle absence, and all explicit preservation/pre-application boundaries. Stages 2-5 behavior and help were not
  changed, so their proof remains retained; breakpoint passed 2026-09-08.
- **Stage 7:** complete - the coordinator confirmed the fixed path was absent, then accepted the successful finite real
  `setup`, `update games`, and `update openings` scenarios in order. The updates reported one month/`74` games/zero
  skips and `3,329` opening labels/`3,810` routes/`36,925` route moves. Separate Stockfish 18 Tool-profile proof selected
  and published one result with five ranked candidate lines. After replacing stale historical snapshot expectations
  with direct-lifecycle aggregate and semantic assertions, the exact DB-09 proof command passed `7` tests over `3,598`
  games, `162,277` positions, `183,682` occurrences, one analysis result, and five analysis lines; all `17` measured
  operations completed three repetitions and produced `NO-INDEX`. No source/private details were reported, and no old
  or sibling database, raw source, schema, dependency, application, or unsupported lifecycle operation was touched;
  breakpoint passed 2026-09-08.
- **Stage 8:** complete - the coordinator accepted closeout evidence from the accepted Stages 1-7 ledger, including the fixed direct
  database result, separate Stockfish proof, retained focused tests, and the explicit retired DB-08/DB-08A distinction.
  The exact command-inventory consistency proof passed `1` test:
  `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/test_command_inventory.py -q` (command timeout `60s`;
  Bash tool timeout `90000ms`). Manual review against `docs/PLAN_TEMPLATE.md` confirms the title/visible-result line,
  status, read trigger/upstream, outcome, scope, sequential stages with actions/proof/escalation/breakpoints,
  progress and decisions, proof, and escalation-boundary sections; no design-fidelity section is applicable. The
  visible result and evidence record were accepted, the breakpoint passed 2026-09-08, and the Plan moved to done.

## Proof

- Setup absent/existing/failure-cleanup behavior is proved by `tests/database/test_setup.py` and the finite `setup`
  command scenario in Stage 7.
- Game latest-month refetch, gap filling, ID merge, omission retention, independent month progress, per-game skips,
  direct derivation, and persistence are proved by `tests/database/test_update_games.py` plus the named focused game
  tests in Stage 4.
- Opening latest-upstream five-file acquisition, validation-before-publication, invalid-set preservation, complete
  route regeneration, and games untouched are proved by `tests/database/test_update_openings.py` plus the named focused
  opening tests in Stage 5.
- Stage 1's bounded documentation review proves only that the recorded direction is consistent; it does not claim
  future CLI behavior. Any pre-correction command-inventory or public-help result that assumed the retired lifecycle is
  invalidated by this direction change. Stage 2 proves public help, success/failure behavior, fixed-path behavior, and
  exit mapping after implementing the adapters; Stage 6 proves the reconciled command-inventory and boundary contracts.
- Real direct DB-09 integrity, direct-reader, opening, preference, access-plan, and aggregate evidence is proved by the
  direct-path tests and commands in Stage 7. Stockfish publication/read behavior is separately proved there and is not
  part of setup/update execution.
- Unaffected DB-01 through DB-07 lower-level behavioral proof remains retained until an affecting change invalidates it.
  DB-08 snapshot/replacement/rollback proof is not a requirement for this corrected outcome and remains historical.
- Normal setup and update commands retain only quick operation-local checks; full integrity, access-plan, and DB-09
  proof remain separate Stage 7 evidence and are not folded into the public data-loading workflows.

## Escalation boundaries

- Automatically deleting, replacing, resetting, or moving a pre-existing `data/database/chess.db`.
- Mutating or deleting the old production database, raw game sources, historical workflow records, or unrelated files
  under `data/database/`.
- Adding schema tables/fields, a dependency, fetch-state/run-history/manifest persistence, or a new public command.
- Adding resume, force, reset, snapshot, swap, replacement, rollback, recovery, or separate verification behavior.
- Changing the settled month-ledger/UUID merge/omitted-game semantics or the latest-valid all-five opening publication
  boundary.
- Changing Stockfish profile, queue, analysis-line semantics, or normal setup/update behavior to run analysis.
- Any backend/frontend/API integration, cutover, legacy-script reuse/cleanup, or broad repository maintenance work.
- Any proof failure that can only be absorbed by weakening the confirmed lifecycle or its acceptance boundary.

## Visible result

> `data/database/chess.db` is created once by `setup`, then refreshed directly by `update games` and `update openings`, with real data and separate bounded Stockfish proof accepted before application work begins.
