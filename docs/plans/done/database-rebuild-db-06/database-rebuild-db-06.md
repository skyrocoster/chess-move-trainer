# DB-06 Analysis Persistence - One complete current result per canonical position

> **Status:** done - DB-06 accepted with 72 focused tests passing in 2.57 seconds.

- **Read trigger:** Read when reviewing accepted DB-06 evidence or preparing the DB-07 handoff.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md#db-06--analysis-result-and-line-persistence), [approved DB-06 grilling handoff](../../../grilling-docs/database-rebuild-db-06.md), and binding direction/schema evidence at `database-rebuild-direction.md:L464-L550,L700-L729` and `database-rebuild-schema.md:L453-L565`.

## Outcome

For an existing canonical position, an importable database package accepts normalized engine-independent analysis, validates its terminal state and complete legal candidate lines, and atomically retains at most one latest complete result. Tool outranks Browser; same-level configuration or engine changes can refresh a result; duplicate, stale, lower-quality, invalid, interrupted, or failed submissions do not expose partial data and return the appropriate bounded outcome.

## Scope

- **Included:** Public normalized analysis values, validation errors, and saved/not-saved publication outcomes; neutral-root terminal classification; complete legal PV and candidate-line validation; quality/version eligibility; existing-position lookup; transactional result/line replacement with an immediate pre-write recheck; and focused behavioral proof.
- **Expected areas:** New package code under `src/chess_move_trainer/database/analysis/`, likely including `__init__.py`, `models.py`, `validation.py`, and `repository.py`; focused tests under `tests/database/analysis/`, likely including `test_public_api.py`, `test_models.py`, `test_validation.py`, `test_repository.py`, and `test_atomic_publication.py`. Compose, without changing, `src/chess_move_trainer/database/connection.py`, `schema.py`, `schema_v1.sql`, `positions/canonicalization.py`, `positions/repository.py`, and the existing package `__init__.py` files. Modify `tests/database/test_package_boundary.py` or `test_source_boundary.py` only if the new package actually changes one of their enumerated expectations.
- **Excluded:** Schema/DDL changes, migrations, CLI or `cli.py`, raw Stockfish/UCI parsing, queue or worker behavior, benchmark commands, analysis history, diagnostics/provenance fields, occurrence counters, API/backend/frontend work, application integration, cutover, and all DB-07 work. Do not depend on legacy backend analysis storage.

## Stages

1. **completed - Define the engine-independent public contract and pure input-domain validation.**
   - **Ordered actions:**
     1. Add immutable/public normalized values for result metadata and candidate lines without accepting raw engine output or exposing database handles.
     2. Represent the two quality levels, configuration version, signed White-POV score kind/value, WDL values, PV payload, and displayed depth using only the catalogue's settled domains. Require settings to encode a JSON object, with no required keys.
     3. Add bounded validation and storage error types plus a saved/not-saved outcome whose reason clearly distinguishes expected duplicate, stale/outdated, and lower-quality rejection from unexpected storage failure.
     4. Export only the intended ordinary package contracts from `analysis/__init__.py`; preserve the existing package/source dependency direction.
   - **Likely paths:** `src/chess_move_trainer/database/analysis/models.py`, `validation.py`, `__init__.py`; `tests/database/analysis/test_public_api.py`, `test_models.py`.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_public_api.py tests/database/analysis/test_models.py -q` proves the public namespace, settings-object validation, score domain, nonnegative WDL values with sum 1000, and settled scalar domains. Run through `bash` with tool timeout `120000` milliseconds.
   - **Breakpoint/escalation:** No human or visual breakpoint. Escalate if a public field, score bound, settings key, quality level, or error contract is needed beyond the approved evidence.

2. **completed - Validate the neutral root, terminal policy, and complete candidate lines.**
   - **Ordered actions:**
      1. Reconstruct a supplied canonical position's four identity fields as a neutral board with halfmove clock `0`, fullmove number `1`, and no repetition history; Stage 3 owns loading those fields for an existing `dp_position_id`.
     2. Derive terminal status from that neutral board, recognizing only `checkmate`, `stalemate`, and `insufficient_material`; keep repetition and fifty/seventy-five-move outcomes nonterminal.
     3. Require terminal results to have the derived terminal kind and zero lines. For nonterminal positions require exactly `min(5, legal root move count)` lines, contiguous ranks, distinct legal root moves, and nonempty PVs that remain legal at every move from the canonical root.
     4. Keep complete PVs as one ordered JSON array; reject partial, malformed, illegal, duplicate-root, rank-hole, and incorrect-line-count input before publication.
   - **Likely paths:** `src/chess_move_trainer/database/analysis/validation.py` and private repository helpers only as needed; `tests/database/analysis/test_validation.py`.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_validation.py -q` proves canonical terminal classification, terminal/no-line behavior, legal complete PVs, contiguous ranks, distinct legal root moves, and the five-or-fewer line-count rule. Run through `bash` with tool timeout `120000` milliseconds; Stage 1 proof remains valid unless these edits affect its inputs or behavior.
   - **Breakpoint/escalation:** No human or visual breakpoint. Escalate if terminality would require occurrence counters, a non-neutral root, a fourth terminal kind, caller-supplied terminal authority, or a different definition of PV completeness.

3. **completed - Publish one complete result and all lines transactionally.**
   - **Ordered actions:**
     1. Open only an existing compatible schema-v1 database through the current connection/schema boundaries and look up the supplied position ID; never resolve or create a position.
     2. Validate the complete normalized submission before changing stored rows, then begin one package-owned write transaction for the parent result and all child lines.
     3. Immediately before writing, re-read the stored result for the position and apply the settled eligibility rules: Tool may replace Browser; Browser never replaces Tool; an identical same-quality configuration/engine result is not saved; and a changed configuration version or engine version may refresh the same quality.
     4. Commit the complete parent and replacement line set together, using the existing PK/FK design for one current result per position. Keep any current-result inspection private or limited to the smallest package-owned read needed for eligibility/outcomes; do not add a general read API.
     5. Return a clear saved or package-level `not saved` result. Leave the stored result untouched for duplicate, stale/outdated, lower-quality, or expected recheck rejection; do not introduce a DB-06 cross-version token mechanism.
   - **Likely paths:** `src/chess_move_trainer/database/analysis/repository.py`, `__init__.py`; `tests/database/analysis/test_repository.py`.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_repository.py -q` proves existing-position-only behavior, one result per position, Tool-over-Browser/no downgrade, duplicate not-saved behavior, same-level configuration/engine refresh, complete parent/line replacement, and the preserved current result while a replacement transaction is uncommitted. Run through `bash` with tool timeout `120000` milliseconds.
   - **Breakpoint/escalation:** No human or visual breakpoint. Escalate if atomic publication needs DDL, a new identity field, a queue transition, occurrence data, a new quality ordering, or any version/token rule contrary to the no-analysis-running operating rule.

4. **completed - Prove rollback, transaction recheck, replacement, and package boundaries.**
   - **Ordered actions:**
     1. Add a deterministic test-only failure seam or equivalent controlled injection, private to the package/test boundary, and force failure after partial replacement work; verify rollback leaves the previous complete result and every previous line intact with no partial rows.
     2. Exercise a bounded controlled interleaving at the publication recheck so an outdated, duplicate, or lower-quality submission observes the current stored result, returns `not saved` with a reason, and cannot overwrite it. Do not model engine/configuration changes as occurring during a running analysis and do not add expected-state tokens.
     3. Verify a successful replacement removes all old child lines and commits exactly the new complete line set; verify validation and interruption/failure paths publish nothing partial.
     4. If implementation changes an existing package/source-boundary enumeration, update and run only the affected bounded test; otherwise leave those existing tests unchanged.
   - **Likely paths:** `tests/database/analysis/test_atomic_publication.py`, with conditional bounded edits/tests in `tests/database/test_package_boundary.py` or `tests/database/test_source_boundary.py` only when their enumerated expectations change.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_public_api.py tests/database/analysis/test_models.py tests/database/analysis/test_validation.py tests/database/analysis/test_repository.py tests/database/analysis/test_atomic_publication.py -q` proves the complete focused acceptance set, including WDL sum, score domain, settings-object validation, terminal/no-line behavior, legal complete PVs, line-count/rank/root-move invariants, existing-position requirement, quality/version policy, transaction recheck, all-line replacement, stale/duplicate non-publication, and rollback/no partial publication. Run through `bash` with tool timeout `120000` milliseconds. If a boundary enumeration changed, additionally run the affected command with the same command-level prefix, for example `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py -q`.
   - **Breakpoint/escalation:** No human or visual breakpoint. Stop and escalate rather than deciding if proof exposes a catalogue/schema change, diagnostic/provenance field, raw engine parsing, position creation, CLI/API/application work, queue/worker behavior, or inconsistency with the operating rule.

## Progress and decisions

- **Stage 1:** completed - immutable engine-independent models, deliberate public exports, settings-object validation, scalar domains, WDL sum, and nonempty PV representation are implemented; after Stage 2 added the required public exports, refreshed focused proof passed 40 tests in 0.30 seconds; breakpoint: none.
- **Stage 2:** completed - neutral-root classification and complete legal candidate-line validation are implemented; 16 focused tests passed in 0.31 seconds; breakpoint: none.
- **Stage 3:** completed - existing-position publication, atomic parent/line replacement, transaction-time eligibility recheck, quality/version outcomes, and prior-result visibility until commit are implemented; 9 focused tests passed in 1.48 seconds; breakpoint: none.
- **Stage 4:** completed - deterministic rollback, first-publication failure, transaction-time duplicate/lower-quality rechecks, exact line replacement, invalid-input preservation, and private test-seam behavior are proven; the focused aggregate passed 72 tests in 2.57 seconds; no package/source-boundary enumeration changed.

## Proof

- Stage 1, refreshed after Stage 2 changed its public exports: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_public_api.py tests/database/analysis/test_models.py -q` from `G:\ChessMoveTrainer`, with bash tool timeout `120000` milliseconds - **40 passed in 0.30s**. This proves the Stage 1 public contract and pure input-domain invariants and remains retained until affected by later edits.
- Stage 2: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_validation.py -q` from `G:\ChessMoveTrainer`, with bash tool timeout `120000` milliseconds - **16 passed in 0.31s**. This proves neutral-root terminal classification and complete legal candidate-line validation and remains retained until affected by later edits.
- Stage 3: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_repository.py -q` from `G:\ChessMoveTrainer`, with bash tool timeout `120000` milliseconds - **9 passed in 1.48s**. This proves existing-position-only publication, exact stored result/lines, quality/version outcomes, complete line replacement, and old-result visibility until commit. Stage 1 was refreshed after its public export changed with **40 passed in 0.30s**; Stage 2 remained valid because its implementation and inputs were unaffected.
- Final focused acceptance: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_public_api.py tests/database/analysis/test_models.py tests/database/analysis/test_validation.py tests/database/analysis/test_repository.py tests/database/analysis/test_atomic_publication.py -q` from `G:\ChessMoveTrainer`, with bash tool timeout `120000` milliseconds - **72 passed in 2.57s**. This supersedes the stage-level proof and establishes the complete DB-06 behavior, including deterministic rollback and no partial publication. Neither bounded package/source-boundary test enumerates `database.analysis`, so neither required an edit or run.
- Run only the finite focused commands named by the active stage. Every command uses the explicit command-level `timeout 90s` and an explicit `bash` tool timeout of `120000` milliseconds.
- Retain each passing stage's evidence until a later edit changes its command, inputs, exercised behavior, configuration, dependencies, or environment. Rerun only missing or invalidated focused proof; do not run `scripts/check.py`, lint, formatting, build, full-suite, source-size, aggregate, or other hygiene checks for this Plan.
- Acceptance is met by the 72-test focused aggregate; no package/source-boundary enumeration was affected.

## Escalation boundaries

- Escalate instead of deciding on any schema/catalogue or migration change, occurrence counter, diagnostic/provenance field, new quality ordering or identity rule, raw Stockfish/UCI parsing, position creation, CLI/API/backend/frontend/application integration, cutover, queue/worker/benchmark behavior, or cross-version expected-state/token mechanism.
- Escalate any behavior that would allow Browser to replace Tool, save an identical same-quality configuration/engine result, publish partial lines, treat repetition or fifty/seventy-five-move outcomes as canonical terminal states, or change engine/configuration versions while analysis is running.

## Visible result

> For an existing chess position, the database shows one complete current analysis and all legal candidate lines—or clearly reports why a submission was not saved—without exposing partial data.
