# S1 — Source catalog storage and opening-owned endpoint identity/provenance - inspectable catalog without changing the game corpus

> **Status:** done - accepted and archived 2026-08-21

- **Read trigger:** Read before every S1 dispatch and before any catalog schema, importer, or authorized runtime database action.
- **Upstream:** [Opening Classification Database Preparation master plan](../../../master-plans/opening-classification-database-preparation.md); [confirmed database-foundation synthesis](../../../grilling-docs/opening-classification-database-foundation.md)

## Outcome

Persist all 3,810 authorized opening records with ECO, name, move sequence, exact replayed endpoint,
source/import provenance, atomic rerun behavior, and ownership-safe endpoint identity in
`data/database/chess_games.db`. A human can inspect the complete catalog without opening-only endpoints
being represented as game-derived position rows.

## Scope

- **Included:** The five authorized TSV files as strictly read-only input; canonical opening-catalog schema and importer; legal replay and exact endpoint facts; source identity, provenance, schema/import version boundaries, and change-aware import runs; atomic and idempotent publication; temporary SQLite proof; and explicitly authorized bounded runtime import and inspection.
- **Expected areas:** `scripts/opening_catalog/**`, `tests/test_opening_catalog.py`, `tests/test_extract_corpus.py`, and compatibility review of `scripts/chess_com/{_schema.py,_replay.py,_persistence.py,_history.py,extract_corpus.py}`. The authorized input is `Scratch/prototypes/proto-chess-openings-epd-lookup-2026-08-18.data/*.tsv`; the runtime artifact is `data/database/chess_games.db`.
- **Excluded:** Opening hierarchy, game classification, recurrence, player facts, frontend, API, engines, live source integration, taxonomy updates or reclassification workflows, destructive migration or replacement, dependency changes, modifications under `Scratch/`, historical records, commits, pushes, and unrelated worktree or runtime-database content.

## Stages

1. **completed - contract and endpoint-ownership gate (ORDERED).**
   - **Ordered actions:** Read the five TSV files without modification; verify the fixed A–E source counts and `eco`, `name`, `pgn` contract; replay records with the established legal-position semantics; compare endpoint keys with the existing game-derived corpus without writing; and define the durable source identity, provenance, catalog/import version, and changed-source policy. Present the two approved endpoint choices—separate opening-owned endpoint identity or a compatible extension that preserves game-derived ownership and completeness—for coordinator/human selection.
   - **Focused proof:** Temporary read-only source/replay and SQLite comparison proving 3,810 records, successful legal replay, deterministic four-field endpoint keys, and the known separation between opening endpoints and existing game-derived states.
   - **Breakpoint:** Coordinator/human approval of the endpoint ownership model and durable source/provenance contract is required before canonical schema or importer work.
   - **Escalate if:** Either model violates existing game-derived ownership, source identity or source-change semantics remain unresolved, or the contract requires taxonomy updates, a dependency, an API, or a destructive migration.
2. **completed - offline schema and deterministic importer (ORDERED).**
   - **Ordered actions:** Implement the selected versioned schema and canonical importer in the bounded opening-catalog area; parse and replay the fixed TSV source; persist one auditable source record per authorized record with its endpoint facts and provenance; record import-run status and source fingerprint/change information; and publish atomically to temporary databases without mutating game, corpus, analysis, or evaluation tables.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_catalog.py -q` against temporary SQLite databases, including schema version refusal, complete initial publication, deterministic output, and no partial publication on replay or storage failure.
   - **Breakpoint:** None; this stage may proceed only from the recorded Stage 1 model and provenance decision.
   - **Escalate if:** The selected model cannot be implemented without changing existing position ownership/completeness, adding a dependency, or publishing partial data.
3. **completed - focused regression and ownership proof (ORDERED).**
   - **Ordered actions:** Add fixtures for legal replay, endpoint identity, source/import provenance, unchanged reruns, changed-source detection, rollback, and duplicate prevention; retain and run the existing corpus import regressions; compare existing game-derived position rows before and after catalog publication; and prove opening-only endpoints cannot masquerade as `position_state` or `position_occurrence` game facts.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_catalog.py tests/test_extract_corpus.py -q`; scoped Ruff, format, and source-size checks; and temporary SQLite assertions over catalog counts, provenance, run history, rollback, and unchanged corpus rows.
   - **Breakpoint:** None; proceed only when the focused proof passes and the selected ownership boundary remains unchanged.
   - **Escalate if:** A regression requires weakening corpus invariants, changing game-derived identity, suppressing an unrelated failure, or changing acceptance.
4. **completed - authorized bounded runtime publication and inspection (ORDERED).**
   - **Ordered actions:** Capture read-only baseline integrity, table, catalog, and existing-position facts; verify the database lock/backup and writer-safety conditions; obtain explicit human authorization; run the fixed-source importer against `data/database/chess_games.db`; verify all 3,810 records, endpoints, provenance, successful run history, and unchanged game-derived rows; then repeat the import to prove unchanged behavior. Keep failure/source-change injection on temporary or copied databases only.
   - **Focused proof:** The authorized bounded runtime inspection, with pre/post integrity and row-signature comparison, catalog/run counts, provenance inspection, and unchanged-rerun evidence. No ordinary check may write the runtime database.
   - **Breakpoint:** Explicit human authorization is required immediately before any runtime database write.
   - **Escalate if:** Lock ownership, backup, integrity, or active-writer safety is uncertain; the runtime schema differs unexpectedly; or any operation would replace, delete, or alter existing game-derived, analysis, or evaluation data.
5. **completed - independent validation, closeout, and archival (ORDERED).**
   - **Ordered actions:** Obtain fresh independent validation of catalog completeness, endpoint ownership, provenance, idempotency, change detection, rollback, and corpus preservation; run the full read-only check without `--fix`; review the scoped diff, documentation shape, and unrelated worktree preservation; record truthful progress and final acceptance in this Plan; and archive the complete Plan directory only after acceptance.
   - **Focused proof:** `.venv\Scripts\python.exe scripts\check.py`; `git diff --check`; documentation/template review; final `git status --short`; and scoped diff review. Unrelated failures are reported and escalated rather than absorbed.
   - **Breakpoint:** Fresh independent validation and explicit human acceptance are required before archival.
   - **Escalate if:** Closeout requires `--fix`, historical edits, scope expansion, acceptance changes, destructive cleanup, or claiming completion without the runtime and independent proof.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the approved outcome or requiring a new product decision.

## Progress and decisions

- **Stage 1:** completed - all five sources contained 3,810 legal records with distinct endpoint keys; 789 endpoints overlapped game states and 3,021 did not. The user approved separate opening-owned tables.
- **Stage 2:** completed - implemented the versioned opening-owned schema and deterministic importer with manifest, file, row, version, and run provenance. Changed sources and failures do not replace the accepted catalog.
- **Stage 3:** completed - 31 focused catalog/corpus tests passed with rollback, unchanged-rerun, source-change, deterministic, provenance, and ownership coverage; scoped Ruff, format, size, and diff checks passed.
- **Stage 4:** completed - the user authorized runtime publication. Integrity and foreign-key checks passed; 3,810 records and five source files were published; an unchanged rerun remained idempotent; all existing game-position rows and 16 pre-existing table counts remained unchanged.
- **Stage 5:** completed - independent Quality validation passed, the user accepted S1, and the Plan was archived. The full read-only check had only unrelated pre-existing failures in excluded board-adapter/promotion work; no S1-scoped check failed.
- **Decision:** Opening endpoints use separate opening-owned tables with the established four-field exact-position key. Opening-only endpoints are never inserted into game-derived position tables. Immutable source manifests and row provenance identify the accepted source; changed manifests fail pending explicit approval.

## Proof

- `.venv\Scripts\python.exe -m pytest tests/test_opening_catalog.py tests/test_extract_corpus.py -q`.
- Temporary SQLite assertions cover all 3,810 records, legal replay, exact endpoint identity, provenance, deterministic output, unchanged reruns, changed-source detection, rollback, and no opening-only game-derived rows.
- Scoped Ruff, format, and source-size checks run without formatter mutation; runtime proof is bounded and explicitly authorized.
- `.venv\Scripts\python.exe scripts\check.py` runs at closeout in read-only mode without `--fix`, alongside `git diff --check` and documentation/template review.
- Independent runtime validation found 3,810 distinct catalog rows, five source-file records, one accepted manifest, two successful runs, zero replay mismatches, SQLite integrity `ok`, and zero foreign-key violations.
- Backup comparison confirmed identical signatures for 510,876 `position_state` and 639,262 `position_occurrence` rows; 789 endpoints overlap game states and all 3,021 opening-only endpoints remain outside game-derived tables.
- The full read-only check reported unrelated existing board-adapter/promotion formatting, size, TypeScript-story, and six end-to-end failures. They are outside S1 and were not absorbed.

## Escalation boundaries

- Any unresolved endpoint model, durable source identity/provenance contract, source-change or version policy, or acceptance change.
- Any schema migration, dependency, API, live source integration, destructive replacement, or alteration of game-derived position ownership or completeness.
- Any unsafe runtime lock, backup, integrity, or active-writer condition; any partial publication risk; or any need to write under `Scratch/`.
- Any hierarchy, classification, recurrence, player, frontend, engine, taxonomy, historical-record, commit, push, or unrelated-worktree change.
- Any need to run `--fix`, suppress or absorb unrelated failures, or archive without independent validation and human acceptance.

## Visible result

> A human can inspect all 3,810 authorized opening records, their exact legal endpoints and provenance, verify safe repeated imports, and confirm that the existing game-derived position corpus is unchanged and ownership-safe.
