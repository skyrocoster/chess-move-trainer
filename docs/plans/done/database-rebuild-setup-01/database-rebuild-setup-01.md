# SETUP-01 preferred-move setup - one fixed command initializes obvious preferred moves

> **Status:** done - accepted and applied to the fixed rebuilt database on 2026-09-08

- **Read trigger:** Read before implementing or reviewing the SETUP-01 preferred-move setup command.
- **Upstream:** [approved SETUP-01 grilling handoff](../../../grilling-docs/database-rebuild-setup-01.md) for behavior;
  [database rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) for scope and exclusions.

## Outcome

Add exactly `python -m chess_move_trainer.database preferred-moves setup`. It reads only current accepted game data from
the fixed `data/database/chess.db`, infers the approved deterministic preferred-move schedule, validates the complete
normalized result, and persists it in one all-or-nothing write only when the existing preference schedule is empty.
The command is noninteractive and reports one concise human-readable summary.

## Scope

- **Included:** Trainer outgoing moves at `dgp_ply` 0-29; all accepted games and every eligible occurrence; UTC start
  dates with NULL dates skipped; rolling half-open 90-calendar-day qualification windows; inclusive thresholds of at
  least 21 matching occurrences and at least 80 percent; approved period start, carry-forward, replacement, overlap,
  tie, repeat-signal, open-ended, and no-inferred-no-preference rules; complete validation; empty-schedule refusal;
  atomic persistence; fixed-path CLI behavior; and the defined summary counts.
- **Expected areas:** `src/chess_move_trainer/database/preferred_moves/`; the nearest package-owned game, connection,
  and position-validation seams only as needed for a set-based read and atomic write; `src/chess_move_trainer/database/cli.py`;
  focused tests under `tests/database/preferred_moves/` and `tests/database/test_cli.py`.
- **Excluded:** `src/chess_move_trainer/database/schema_v1.sql` changes; schema, dependency, history, audit,
  proposal, or retained JSON files; review or separate apply steps; alternate database paths; acquisition, update, or
  raw-source mutation; Stockfish; legacy tools; scripts as canonical owners; API, frontend, application, cutover, or
  old-database work; broad maintenance checks; Quality validation; commits; and pushes.

The implementation-facing summary definitions are fixed: examined games are all `datasource_game` rows scanned;
skipped games are rows with NULL `dg_started_at_utc`; malformed non-NULL persisted timestamps are inconsistent data and
fail safely without guessing; qualifying positions are distinct positions receiving a period; periods applied are rows
inserted; and conflicting positions are distinct positions whose overlapping different-move qualifications required the
approved winner or tie rule. There is no itemized report, retained artifact, or additional output mode.

## Stages

1. **done - Pure deterministic inference engine and focused inference tests**
   - Define the in-memory observation and result values, keeping database handles and CLI concerns outside the pure
     rule engine.
   - Implement the approved rolling-window qualification, period construction, carry-forward,
     replacement, overlap, tie, repeat-signal, and final open-ended behavior using the existing preferred-move range
     values and normalization semantics where appropriate.
   - Preserve occurrence multiplicity, exact canonical-position identity, UTC calendar dates, inclusive thresholds, and
     the absence of inferred `no_preference` periods.
   - Add focused examples over already-eligible dated observations for occurrence multiplicity, 21/80-percent
     boundaries, rolling windows, candidate starts, unsupported dates, replacement, overlap winner and tie behavior,
     repeat signals, open-ended final periods, no inferred `no_preference`, and zero candidates.
   - **Expected areas:** a new or extended pure service under `src/chess_move_trainer/database/preferred_moves/` and
     focused unit tests under `tests/database/preferred_moves/`.
   - **Focused proof:** the inference test command in the Proof section.
   - **Breakpoint:** none. Escalate only if an approved behavioral rule cannot be represented without changing it.

2. **done - Package-owned database read, validation, and atomic empty-schedule persistence**
   - Read the current normalized game metadata and ordered occurrences from the rebuilt tables without acquisition,
     update, raw-source access, or per-game command orchestration. Derive trainer ownership from stored trainer color
     and position side to move, and pass only eligible observations to the pure engine.
   - Open and validate the fixed compatible schema, enforce the empty preferred-move schedule precondition before
     mutation, and treat NULL dates as skipped games. Treat malformed non-NULL persisted timestamps or inconsistent
     normalized data as safe failures rather than guessed dates.
   - Add focused database-bound eligibility tests for trainer outgoing moves, inclusion of `dgp_ply` 0 and 29 with
     30 excluded, NULL-date skipping and counting, malformed non-NULL dates failing safely, pooled metadata groups,
     and retained occurrence multiplicity.
   - Validate the complete inferred schedule, including normalized half-open periods and legal moves from their exact
     canonical positions, before inserting any preference row.
   - Insert every resulting period in one transaction and verify rollback leaves all preference rows unchanged after any
     validation or persistence failure. A zero-candidate result succeeds without writes.
   - Return ordinary summary data using the fixed count definitions above, including examined games, skipped games,
     qualifying positions, periods applied, and conflicting positions.
   - **Expected areas:** the package-owned preferred-move service/repository boundary, existing connection and schema
     validation helpers, the nearest game-reading seam if a set-based reader is factored, and focused persistence tests
     under `tests/database/preferred_moves/`. The schema resource is read-only and remains unchanged.
   - **Focused proof:** the setup/repository test command in the Proof section.
   - **Breakpoint:** no human breakpoint. Escalate any need for partial writes, nonempty-schedule updates, date
     fallback, new schema state, or a different validation contract.

3. **done - Thin fixed-path CLI command and focused CLI contract tests**
   - Register exactly `preferred-moves setup` beneath the existing preferred-moves command group.
   - Provide no database option, confirmation prompt, proposal output, JSON mode, alternate path, or separate apply
     command; invoke the package-owned service with `DEFAULT_DATABASE_PATH`.
   - Preserve established interruption, schema, usage, and operational error boundaries, and print only the concise
     successful summary required by the outcome.
   - Prove command help, exact command registration, fixed-path forwarding, noninteractive behavior, successful and
     zero-candidate summaries, existing-schedule refusal, and safe failure reporting.
   - **Expected areas:** `src/chess_move_trainer/database/cli.py` and focused tests under
     `tests/database/preferred_moves/test_cli.py`.
   - **Focused proof:** the preferred-moves CLI command in the Proof section.
   - **Breakpoint:** none. Escalate any request for a new public workflow, output mode, option, or application
     integration.

Stages are sequential; no stages run in parallel. A passing proof item remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment.

## Progress and decisions

- [x] **Stage 1:** accepted - pure inference and rule coverage; proof passed: `timeout 45s .venv/Scripts/python.exe -m pytest -q tests/database/preferred_moves/test_inference.py` (12 passed); breakpoint none.
- [x] **Stage 2:** accepted - database read, complete validation, and atomic persistence; proof passed: `timeout 75s .venv/Scripts/python.exe -m pytest -q tests/database/preferred_moves/test_setup.py tests/database/preferred_moves/test_repository.py` (26 passed); breakpoint none.
- [x] **Stage 3:** accepted - fixed-path CLI contract; isolated proof replaced the blocked aggregate CLI module because its unrelated stale imports prevented collection; proof passed: `timeout 90s .venv/Scripts/python.exe -m pytest -q tests/database/preferred_moves/test_cli.py` (7 passed); approved real invocation succeeded with examined games 12710, skipped games 0, qualifying positions 91, periods applied 108, and conflicting positions 7; breakpoint none.
- Approved product decisions are carried unchanged from the grilling handoff; implementation details may vary only when
  they preserve the stated behavior and boundaries.
- SETUP-01 was accepted after all three focused proofs and the one approved real invocation passed. No independent
  Quality run or broad maintenance suite was requested or required.

## Proof

The following focused proofs and approved outcome invocation ran from the repository root:

1. `timeout 45s .venv/Scripts/python.exe -m pytest -q tests/database/preferred_moves/test_inference.py`
   - command timeout: 45 seconds; required Bash tool timeout: 60000 ms.
2. `timeout 75s .venv/Scripts/python.exe -m pytest -q tests/database/preferred_moves/test_setup.py tests/database/preferred_moves/test_repository.py`
   - command timeout: 75 seconds; required Bash tool timeout: 100000 ms.
3. `timeout 90s .venv/Scripts/python.exe -m pytest -q tests/database/preferred_moves/test_cli.py`
   - command timeout: 90 seconds; required Bash tool timeout: 120000 ms.
   - result: 7 passed in 0.70 seconds. This isolated proof replaced the aggregate CLI module because unrelated stale
     imports prevented that module from collecting.
4. `timeout 600s .venv/Scripts/python.exe -m chess_move_trainer.database preferred-moves setup`
   - command timeout: 600 seconds; required Bash tool timeout: 660000 ms.
   - result: succeeded; examined 12,710 games, skipped 0 games, found 91 qualifying positions, atomically applied 108
     periods, and reported 7 conflicting positions.

Do not substitute lint, formatting, build, source-size, aggregate, complete maintenance, Quality, or application proof.

## Escalation boundaries

- Any change to eligibility, thresholds, rolling-window dates, period starts, carry-forward, replacement, overlap,
  tie, open-ended, missing-date, no-preference, or empty-schedule semantics.
- Any need for an alternate database path, prompt, proposal/review/apply ceremony, public or retained JSON, schema or
  dependency change, inference history, audit state, partial write, game acquisition/update, Stockfish, legacy tool,
  API/frontend/application integration, cutover, or old-database operation.
- Any change to the five summary count definitions or the concise-output-only contract.
- Any acceptance requirement beyond the focused behavioral proofs listed above.

## Visible result

> The fixed setup command inferred and atomically applied 108 preferred-move periods across 91 positions from the rebuilt
> game data without a proposal or review step.
