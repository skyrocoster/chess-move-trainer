# DB-02 canonical position substrate - give every rebuilt producer one stable legal-only position identity

> **Status:** done - Stage 1 and Stage 2 accepted; complete DB-02 outcome accepted

- **Read trigger:** Read with `docs/grilling-docs/database-rebuild-db-02.md` before any DB-02 implementation or proof work.
- **Upstream:** `docs/grilling-docs/database-rebuild-db-02.md` is the confirmed implementation handoff; `docs/master-plans/database-rebuild/database-rebuild.md` governs selection, clean rewrite, package/CLI rules, and the DB-02 envelope; `docs/grilling-docs/database-rebuild-direction.md` lines 167-232 and `docs/grilling-docs/database-rebuild-schema.md` lines 240-293 remain the binding position authorities; the accepted `docs/plans/done/database-rebuild-db-01/database-rebuild-db-01.md` supplies retained prerequisite proof.

## Outcome

Rebuilt database producers can validate a replayed board or complete FEN and create or reuse one permanent integer
position ID for the exact legal-only canonical identity. The shared service supports otherwise unreferenced valid
preference positions and composes safely into future all-or-nothing producer transactions.

## Scope

- **Included:** One from-scratch service owned by `chess_move_trainer.database.positions`; explicit validated board and complete-six-field-FEN entry points; ordinary canonical identity/result data and clear package errors; canonical castling order; fully legal en-passant retention and approved normalization/rejection behavior; exact-compatible-v1 precondition with no target creation or alteration; a narrow reusable package-internal compatibility assertion and existing-target read-write open path; atomic conflict-safe create-or-reuse; stable IDs across reopen; permanent retention; a package-owned opaque transaction/unit-of-work boundary for one-off and future grouped writes; focused behavioral, concurrency, transaction, and recursive clean-boundary proof.
- **Expected areas:** `src/chess_move_trainer/database/positions/**` with implementation-driven module filenames; `src/chess_move_trainer/database/connection.py` only for a package-internal existing-target read-write path that cannot create a missing file; `src/chess_move_trainer/database/schema.py` only to factor a side-effect-free exact-v1 assertion reusable on an already-open internal connection; `src/chess_move_trainer/database/__init__.py` only where public ordinary-data/position-service exports are needed; new focused `tests/database/test_position_canonicalization.py`, `tests/database/test_position_en_passant.py`, `tests/database/test_position_repository.py`, `tests/database/test_position_transactions.py`, and `tests/database/test_position_concurrency.py`; and narrow affected checks in `tests/database/test_connection.py`, `tests/database/test_schema_creation.py`, `tests/database/test_package_boundary.py`, and `tests/database/test_source_boundary.py`. The source-boundary test must scan `src/chess_move_trainer/database/**/*.py` recursively so the new subpackage cannot evade clean-source checks.
- **Excluded:** `src/chess_move_trainer/database/schema_v1.sql`, schema version and all table/column/key/check/index definitions; any change to public DB-01 connection/schema creation, inspection, publication, CLI, and setup contracts or behavior; `requirements.txt`, `pyproject.toml` dependency metadata, and every dependency change; operator CLI additions; raw database objects in public contracts; update/delete/cleanup APIs; old-position migration and old-database access; source ingestion and DB-03+ game/opening/preference/analysis/queue records or services; production `backend/app`, frontend, APIs, E2E, and all legacy/source evidence paths; master-plan or completed historical-record edits; broad maintenance checks.

## Stages

1. **accepted - Establish the validated canonical identity boundary.**
   - First add focused tests for both explicit inputs: valid replayed `chess.Board` instances and complete six-field FEN strings. Prove canonical board placement, side to move, `KQkq` castling ordering, and exclusion of valid halfmove/fullmove counters from identity.
   - Add the from-scratch `chess_move_trainer.database.positions` canonicalization boundary using only the pinned chess library and package-owned code. Return ordinary immutable data suitable for storage; do not expose an accepted raw four-field input and do not mutate caller boards.
   - Validate both input forms within the service. Accept and normalize a normal classic/pseudo-only target to `-` when no fully legal capture exists, including no-capturer and pinned cases; retain a genuine legal target; reject malformed targets and geometrically or otherwise impossibly inconsistent en-passant state rather than repairing it.
   - Reject malformed or invalid positions before storage, including missing kings, pawns on the first/eighth rank, impossible castling rights, invalid side/counters, and other position-invalidity reported through the approved chess meaning.
   - Focused proof from `G:\ChessMoveTrainer`: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_position_canonicalization.py tests/database/test_position_en_passant.py -q` (Bash tool timeout `120000ms`). Every subprocess started by a test must also have its own explicit finite timeout.
   - **Acceptance:** Both public input forms produce the same exact canonical identity where appropriate; counters cannot affect identity; castling is canonical; all approved en-passant branches and invalid-position examples behave exactly as confirmed; invalid inputs cannot reach a write path.
   - **Escalate:** Validation would change the settled identity, interpret legal-only en passant differently, require a dependency change, or require trusting a caller-supplied four-field key.
   - **Breakpoint:** none; chess meaning and input policy are confirmed upstream.

2. **accepted - Add conflict-safe permanent storage and opaque transaction composition.**
   - First add repository and transaction tests against disposable DB-01-created compatible databases. Cover missing,
     existing-empty, nonempty-v0, mismatched-v1, and malformed targets remaining absent or byte-for-byte unmodified;
     invalid-input no-write; one integer ID/row for repeated identity; distinct rows when each of placement, side, valid
     castling rights, or legal en passant differs; and stable reuse after close/reopen.
   - Narrowly refactor DB-01 internals without changing their public contracts: add an internal existing-target
     read-write open path whose SQLite mode cannot create a missing file, and factor an internal exact-v1 compatibility
     assertion from the canonical schema comparison. The assertion must inspect without writing the target, reject
     empty and incompatible databases with the existing clear package schema error, and leave the same internal
     connection clean for a following transaction. `create_schema()` keeps its accepted create/repeat behavior;
     `probe_connection()` remains a connection-settings probe rather than becoming a schema API; no new helper is
     exported as an operator or public producer contract.
   - Add a public package-owned transaction/unit-of-work boundary that owns connection and transaction lifetime while exposing no `sqlite3` or SQLAlchemy object. Let a future producer resolve multiple positions and later add its own package operation in one all-or-nothing boundary; keep one-off create/reuse as a convenience over that same behavior.
   - Before any position write, open the target through that non-creating internal path and assert exact DB-01 v1
     compatibility on the same internal connection. Raise clear package errors for missing, empty, or incompatible
     targets with no create, migration, repair, schema alteration, or race-prone call to `create_schema()`.
   - Implement atomic conflict-safe create-or-reuse against the existing four-column UNIQUE constraint. Concurrent writers for one identity must all resolve the same integer ID and leave exactly one row; lock waits remain finite. Provide no update, delete, or cleanup operation.
   - Prove rollback in `tests/database/test_position_transactions.py` by creating a position inside grouped work and
     forcing later work to fail, then observing no partial row. In that same file, prove successful multi-position
     composition through only the opaque unit-of-work surface, without DB-03+ records or raw-handle access. Using
     focused fixture setup only, remove a reference and verify the position row remains permanently.
   - Put the concurrent-writer scenario in `tests/database/test_position_concurrency.py`: use finite package lock waits,
     coordinate independent writers resolving one identity, and require that every writer completes successfully with
     the same stable integer ID and the database contains exactly one row for that identity.
   - Focused storage, transaction, and concurrency proof from `G:\ChessMoveTrainer`: `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_position_repository.py tests/database/test_position_transactions.py tests/database/test_position_concurrency.py -q` (Bash tool timeout `150000ms`). This command specifically proves grouped rollback/composability without DB-03+ records or raw-handle exposure through `test_position_transactions.py`, and one-row/one-ID finite-lock concurrency through `test_position_concurrency.py`. Every subprocess started by a test must also have its own explicit finite timeout.
   - Focused affected DB-01-internal proof from `G:\ChessMoveTrainer`: `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_connection.py tests/database/test_schema_creation.py -q` (Bash tool timeout `150000ms`). Prove the internal existing-target opener cannot create a missing file, the compatibility assertion leaves missing/empty/incompatible targets untouched and accepts exact v1, and the accepted public `create_schema()` and `probe_connection()` behavior remains unchanged.
   - Mandatory recursive package/source-boundary proof from `G:\ChessMoveTrainer`: `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` (Bash tool timeout `90000ms`). Change `tests/database/test_source_boundary.py` to enumerate Python sources recursively under `src/chess_move_trainer/database/`, including every file in `positions/`, before applying its import, DDL-owner, wrapper, copied-legacy, and CLI-thinness assertions; also prove internal compatibility/connection helpers are not promoted to public raw-handle contracts.
   - Retain accepted DB-01 proof and passing Stage 1 proof unless Stage 2 changes their exercised inputs, exports, canonicalization, package discovery, dependencies, or environment. Rerun only an affected command. In the final execution scope audit, confirm the DB-01 SQL resource, CLI modules/contracts, setup, dependencies, master plan, completed records, legacy evidence, and production application paths were not changed.
   - **Acceptance:** Only a compatible pre-created v1 target can be used; missing, empty, and incompatible targets remain
     unmodified; the internal refactor preserves public DB-01 behavior; identity reuse is atomic under independent
     finite-lock concurrent writers and stable across reopen; each identity field distinguishes rows; invalid and
     rolled-back work leaves no row; successful grouped work is composable through an opaque package boundary;
     reference removal never deletes the position; recursive scanning covers the new subpackage; and no update/delete
     API, CLI, schema/dependency change, raw-handle exposure, or forbidden dependency/source direction exists.
   - **Escalate:** Conflict safety needs a schema/index change; compatibility cannot be established before writing; grouped writes cannot share the package-owned opaque transaction; raw handles must become public; or implementation requires DB-03+ records, a CLI/dependency addition, legacy/backend edits, or old-database access.
   - **Breakpoint:** none; completion proceeds to coordinator acceptance only after the focused proof ledger and final scope audit pass.

## Progress and decisions

- **Stage 1:** accepted - latest retained proof: from `G:\ChessMoveTrainer`, `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_position_canonicalization.py tests/database/test_position_en_passant.py -q` (Bash tool timeout `120000ms`) — 20 passed in 0.26s; breakpoint: none.
- **Stage 2:** accepted - retained proof: repository/transaction/concurrency command — 9 passed in 1.19s; affected DB-01 internal command — 24 passed in 0.72s; recursive package/source-boundary command — 7 passed in 0.30s; breakpoint: none.
- **Retained prerequisite:** DB-01 is accepted. Its completed Plan retains exact-v1 schema, connection, finite-lock, foreign-key, package, setup, inspection, publication, and CLI evidence; rerun only a narrow item invalidated by a DB-02 change.
- **Settled decisions:** Ownership is `chess_move_trainer.database.positions`; public inputs are replayed boards and complete FENs; pseudo-only/no-capturer/pinned en passant normalizes to `-` while impossible state is rejected; the target must already be exact compatible v1; transactions are package-owned and opaque; positions are permanent; public CLI entry points are none.

## Proof

- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_position_canonicalization.py tests/database/test_position_en_passant.py -q` (Bash tool timeout `120000ms`) proves canonicalization, complete-input validation, counter exclusion, canonical castling, legal-only en passant, and malformed/invalid rejection.
- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_position_repository.py tests/database/test_position_transactions.py tests/database/test_position_concurrency.py -q` (Bash tool timeout `150000ms`) proves no-write schema preconditions, same-ID reuse, all four distinguishing dimensions, reopen stability, permanent retention, all-writers-successful finite-lock one-row/one-ID concurrency, and—through the transaction file specifically—grouped rollback and successful opaque composition without DB-03+ records or raw-handle exposure.
- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_connection.py tests/database/test_schema_creation.py -q` (Bash tool timeout `150000ms`) proves the new internal existing-target/compatibility path is non-creating and side-effect-free for missing, empty, and incompatible targets while accepted public DB-01 connection and schema-creation behavior remains unchanged.
- `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` (Bash tool timeout `90000ms`) proves recursive coverage of all Python files under the database package, inward ownership, no legacy/backend import, wrapper, copy, or delegation, no Python DDL, and no public raw-handle/helper expansion. The final scope audit confirms no DB-01 SQL-resource/CLI or dependency change; unaffected DB-01 proof is retained rather than rerun.
- Passing behavioral proof remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment. No lint, formatting, broad type/build, source-size, aggregate/full suite, `scripts/check.py`, maintenance, backend, frontend, browser, or unrelated test belongs to this Plan.

## Escalation boundaries

- Return to the user before changing the exact four identity fields, fully legal en-passant meaning, permanent-retention rule, `derived_position` schema/constraints, or schema version.
- Escalate any dependency or CLI addition, raw SQLite/SQLAlchemy public contract, inability to make create-or-reuse atomic, or inability to compose grouped all-or-nothing writes through the opaque package boundary.
- Escalate any migration, schema creation/repair, old-database access, update/delete/cleanup, legacy reuse, source ingestion, DB-03+ producer implementation, or production backend/application/frontend/API requirement.

## Visible result

> Every rebuilt database producer can safely reuse the same permanent integer ID for the same valid legal-only chess position, including standalone preference positions.
