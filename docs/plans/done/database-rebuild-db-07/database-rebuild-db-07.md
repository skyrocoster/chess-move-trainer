# DB-07 Stockfish queue and worker - a bounded Stockfish worker drains requests and publishes complete analysis

> **Status:** completed - all six stages accepted with focused proof; DB-07 is closed.

- **Read trigger:** Read before implementing the first supported Stockfish engine, benchmark, queue worker, or direct bulk analysis for DB-07.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md#db-07--analysis-queue-and-stockfish-worker); [DB-07 grilling handoff](../../../grilling-docs/database-rebuild-db-07.md); binding queue and analysis direction at `database-rebuild-direction.md:L552-L591,L700-L740`; binding schema at `database-rebuild-schema.md:L569-L653,L768-L801`; accepted [DB-06 handoff](../../../grilling-docs/database-rebuild-db-06.md) and [DB-06 Plan](../../done/database-rebuild-db-06/database-rebuild-db-06.md); accepted benchmark evidence at `database-rebuild-db-07-benchmark-experiment.md` and `experiments/prototypes/stockfish-db07-benchmark/BENCHMARK_RESULTS.md`.

## Outcome

Create the first clean supported Stockfish implementation under `chess_move_trainer.database.stockfish`. It owns Stockfish process control and UCI normalization, the reusable future-use benchmark, exact live queue operations, authority-defined bulk target selection, serial Tool bulk analysis, and a standalone drain-and-exit worker. The engine-independent `database.analysis` package remains the DB-06 validation/publication owner.

## Scope

- **Included:**
  - Stockfish 18 startup identity verification, normalized White-POV scores/WDL/PVs, fixed Browser and Tool profiles, MultiPV 5 with fewer lines only when fewer legal moves exist, 30-second per-analysis watchdog, per-analysis hash clearing, and one reusable live engine process at a time.
  - A database-specific Windows kernel named mutex for `stockfish bulk` and `stockfish worker`, with finite acquisition, normal release, busy failure, crash release, and abandoned-owner recovery.
  - The exact existing `derived_analysis_queue` table only: atomic max-quality UPSERT, FIFO oldest claim, fresh immutable random UUID claim tokens, two-minute stale reclaim, no heartbeat, CAS/token rejection, pre-publication recheck, promotion while Browser runs, matching-token failure handling, and atomic result/line plus queue deletion/release.
  - A narrow package-internal, engine-independent DB-06 transaction-participant seam in `analysis/repository.py`. It is not a general public API or raw connection contract; existing `AnalysisRepository.publish()` delegates to it so DB-06 validation, pre-write recheck, outcomes, replacement, and rollback semantics remain unchanged.
  - Bulk’s on-demand union of imported-game and opening-route positions at plies 0–19, deterministic frequency ordering, eligibility rules, bounded-page reads, optional positive `--limit`, immediate direct DB-06 publication, restart recomputation, interruption handling, and failure continuation without same-launch retry.
  - A clean benchmark rebuilt from the settled observable behavior: explicit executable/input/output and matrix arguments, deterministic ordering, per-result checkpointing, compatible resume, completed-run protection, normalized JSONL, regenerable summaries, bounded artifact-write retry/reporting, failure continuation, output containment, and finite watchdogs.
  - Thin Typer commands under `python -m chess_move_trainer.database stockfish benchmark|bulk|worker` with useful help and settled exits: 0 success/no work/completed no-op, 1 operational/lock/engine/per-position failure, 2 usage error, 3 incompatible schema, and 130 interruption.
- **Expected areas:** `src/chess_move_trainer/database/stockfish/*.py`; `src/chess_move_trainer/database/analysis/repository.py`; focused tests under `tests/database/stockfish/`; `tests/database/analysis/test_transaction_composition.py`; stockfish-specific additions to `tests/database/test_cli.py`; and `tests/database/test_package_boundary.py` or `test_source_boundary.py` only if their enumerated expectations change.
- **Excluded:** `schema_v1.sql` and generated schema references; new tables, indexes, migrations, run/target/failure history, shared JSON queues, API/backend/frontend integration, application queue draining, cutover, legacy backend or old benchmark reuse, prototype code movement/copying, multiple concurrent engines, quality scheduling, full/comparative benchmark execution, lint/format/build/source-size/aggregate maintenance checks, and an independent Quality phase.

## Stages

Stages are sequential; no stage may run in parallel with another. A passing proof remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependency, or environment.

1. **completed - Build the clean engine and Windows mutex foundation.**
   - **Ordered actions:**
     1. Add fixed profile/configuration values: Browser 200,000 nodes; Tool 6,400,000 nodes; both Threads=6, Hash=1024 MiB, MultiPV=5, configuration version 1; Stockfish 18 identity verification; no time-based chess limit.
     2. Wrap one Stockfish process with finite startup/operation handling, White-POV score and WDL normalization, complete PV conversion, terminal-position handling, hash clear before every analysis, and termination before replacement after error or watchdog expiry.
     3. Implement a standard-library `ctypes` Windows named mutex whose name derives from the normalized database path. Treat a finite timeout as busy, accept `WAIT_ABANDONED` as acquired ownership, and always release/close handles when possible.
     4. Add fake-engine tests and real child-process mutex tests for clean release, busy behavior, owner crash, and abandoned acquisition.
   - **Focused proof:** Bash tool timeout `120000` ms; command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_engine.py tests/database/stockfish/test_mutex.py -q
     ```
   - **Breakpoint/escalation:** None. Escalate if correctness requires a new dependency, a cross-session/global mutex contract, a second live engine, a different fixed profile, or raw engine parsing in `database.analysis`.

2. **completed - Rebuild the supported benchmark without using prototype code.**
   - **Ordered actions:**
     1. Add deterministic matrix/specification models and explicit CLI inputs for executable, position input, output directory, node budgets, thread settings, hash sizes, repetitions, and shuffle seed. Keep MultiPV 5 and finite watchdog behavior settled rather than adding a sizing decision.
      2. Add manifest compatibility checks, per-result append-safe checkpointing, normalized JSONL attempts, regenerable JSON/CSV summaries, concise progress, failure continuation, interruption safety, and completed-run no-op behavior.
      3. Ensure every manifest, checkpoint, summary, and temporary file stays below the caller’s explicit output directory; incompatible existing state stops safely rather than mixing evidence.
      4. Make checkpoint and summary persistence resilient to a bounded transient Windows `PermissionError` or sharing violation: retry the current artifact write only a finite number of times, keep each JSONL record append-safe, and use temporary/atomic replacement without leaving repository logs. A permanent artifact-write failure must stop and report nonzero, preserve earlier readable records, and remain distinct from a Stockfish chess-analysis failure.
      5. Prove matrix/checkpoint behavior with fake engines and injected artifact writers: transient write failures recover within the finite retry budget, while permanent failures stop safely without corrupting earlier records or classifying the failure as engine analysis. Do not run a full matrix or interpret a new winner.
   - **Focused proof:** Bash tool timeout `120000` ms; command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_benchmark.py -q
     ```
   - **Breakpoint/escalation:** None. Escalate if checkpoint safety requires repository-fixed paths, a new persisted run/history table, prototype reuse, or a comparative benchmark decision.

3. **completed - Compose DB-06 publication with exact queue transactions.**
   - **Ordered actions:**
     1. Add the private engine-independent transaction-participant seam in `analysis/repository.py`; make the existing public `publish()` delegate to it and preserve all accepted DB-06 behavior.
     2. Implement queue service operations against only the existing six-column `derived_analysis_queue`: max-quality UPSERT without destroying claims, FIFO claim of queued or two-minute-stale running work, fresh UUID token replacement, and matching-token release/delete/failure operations.
     3. Make queue completion own one `BEGIN IMMEDIATE`, check the current token and requested quality, invoke the DB-06 seam for pre-publication recheck and complete parent/line replacement, then conditionally delete or release the queue row before the same commit. A stale token must publish or mutate nothing.
     4. Add controlled failure/interleaving tests proving rollback, promotion, no downgrade, stale rejection, matching-token failure, and no partial result/line publication.
   - **Focused proof:** Bash tool timeout `120000` ms; command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_repository.py tests/database/analysis/test_atomic_publication.py tests/database/analysis/test_transaction_composition.py tests/database/stockfish/test_queue.py -q
     ```
     Retain the accepted DB-06 model/validation proof unless this seam changes their inputs or behavior.
   - **Breakpoint/escalation:** Stop if the seam needs public raw connections, duplicated DB-06 validation/result SQL, a schema change, a new token/version rule, or a different queue contract.

4. **completed - Implement authority-defined targets and direct bulk Tool analysis.**
   - **Ordered actions:**
     1. Replay opening routes legally and create/reuse canonical positions for pre-move plies 0–19 through the existing position ownership; union them with imported-game positions from the same ply range.
     2. Order game positions by descending occurrence count, assign route-only positions frequency zero, apply a deterministic tie-break, and read candidates in bounded stable pages rather than persisting a target list.
     3. Mark eligible positions as missing, Browser-only, or stale Tool configuration/engine; skip current Tool results. Analyze and publish each position immediately through public DB-06 publication, never through the queue.
     4. Implement unlimited default processing and positive `--limit N`, stop/start recomputation, Ctrl+C discard of only the unfinished result, isolated failure reporting/continuation without same-launch retry, and nonzero final failure status.
   - **Focused proof:** Bash tool timeout `120000` ms; command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_targets.py tests/database/stockfish/test_bulk.py -q
     ```
   - **Breakpoint/escalation:** Escalate if route replay requires a new table, target/run history, a different ply population/order, queue insertion, group-wide publication, or a new retry policy.

5. **completed - Implement the drain-and-exit worker.**
   - **Ordered actions:**
     1. Acquire the database-specific mutex before engine work and fail promptly when another bulk/worker command owns it; ordinary queue enqueue remains outside this guard.
     2. Claim the oldest available request, run outside SQLite transactions at the immutable claimed quality, reuse one process sequentially, clear hash before each analysis, and start a replacement only after terminating a failed or timed-out process.
     3. Complete through the stage-3 transaction seam, including Browser-to-Tool promotion, matching-token failure, stale-token discard, and conditional delete/release.
      4. If mutex acquisition follows a crash and the only remaining row is `running` but younger than two minutes, compute the known remaining stale interval, wait only that interval with finite polling, then reclaim and finish the row. Never report the queue complete while this row remains unreclaimable, and never wait indefinitely.
      5. Drain current queued and reclaimable work, then exit rather than watching forever. Ctrl+C must immediately terminate the current engine, discard partial output, release the claim when possible, and return 130; hard death relies on stale recovery. Continue isolated failures and return nonzero after draining.
      6. Add fake-clock proof for the younger-running-row recovery, including finite polling, reclaim at the two-minute boundary, and subsequent publication; retain the existing stale-token and hard-death coverage.
   - **Focused proof:** Bash tool timeout `120000` ms; command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_worker.py -q
     ```
   - **Breakpoint/escalation:** Escalate if safe drain/exit requires indefinite waiting, heartbeats, concurrent engines, persisted failure history, or a different mutex/claim lifecycle.

6. **completed - Add thin CLI adapters and bounded real-engine proof.**
   - **Ordered actions:**
     1. Register the `stockfish` Typer group in `database/cli.py`; keep adapters free of SQL, engine parsing, and orchestration logic. Require explicit database and executable paths where applicable; require explicit benchmark input/output and matrix arguments.
     2. Add focused help, required-path, invalid-argument, lock-busy, schema, engine-identity, isolated-failure, and interruption exit tests.
     3. Add a pytest-managed real benchmark smoke using exactly one approved position, one low node budget (`100000`), one thread setting (`1`), one hash setting (`64` MiB), and one repetition. The test creates a temporary one-position input from approved position data and a temporary output directory under `tmp_path`, invokes the exact same supported command twice, and verifies one analysis/checkpoint/summary, output containment, clean shutdown, and compatible completed-run behavior. It must not compare budgets or profiles and must not write tracked benchmark artifacts.
     4. Add a separate pytest-managed real worker/publication smoke with one temporary schema-v1 database and one approved position at the fixed Tool profile: 6,400,000 nodes, Threads=6, Hash=1024 MiB, MultiPV=5, configuration version 1. Verify complete DB-06 parent/lines, queue finalization, and clean shutdown.
   - **Focused proof:** Bash tool timeout `120000` ms; command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -k stockfish -q
     ```
     Bash tool timeout `240000` ms; command timeout `180s` for the one-position real benchmark smoke:
     ```bash
     timeout 180s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_real_benchmark_smoke.py -q
     ```
     Bash tool timeout `240000` ms; command timeout `180s` for the separate one-position real worker/publication smoke:
     ```bash
     timeout 180s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_real_worker_publication_smoke.py -q
     ```
     Run package/source-boundary tests only if their enumerated expectations were changed; if so, use Bash tool timeout `120000` ms and command timeout `90s`:
     ```bash
     timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q
     ```
   - **Breakpoint/escalation:** Escalate rather than changing the command surface, fixed Tool profile, accepted proof size, output ownership, or any application integration boundary.

## Progress and decisions

- **Stage 1:** completed - fixed profiles, Stockfish 18 identity verification, engine normalization/lifecycle, and Windows mutex behavior implemented. After Stage 2 extended retained engine metrics, focused proof was rerun and passed: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_engine.py tests/database/stockfish/test_mutex.py -q` (`11 passed in 1.21s`; Bash tool timeout `120000` ms). Breakpoint: none.
- **Stage 2:** completed - deterministic configurable benchmark, resumable contained artifacts, completed-run protection, and bounded artifact-write recovery implemented without prototype runtime reuse. Focused proof passed: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_benchmark.py -q` (`8 passed in 0.70s`; Bash tool timeout `120000` ms). Breakpoint: no full/comparative run.
- **Stage 3:** completed - DB-06 publication delegates through a private transaction participant; FIFO/stale claims, max-quality promotion, token-CAS rejection, matching-token failure, rollback, and atomic queue completion are implemented. After Stage 5 extended queue recovery support, focused proof was rerun and passed: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_repository.py tests/database/analysis/test_atomic_publication.py tests/database/analysis/test_transaction_composition.py tests/database/stockfish/test_queue.py -q` (`26 passed in 4.74s`; Bash tool timeout `120000` ms). Stages 1-2 proof remained valid. Breakpoint: none.
- **Stage 4:** completed - legal route replay, canonical target union, deterministic bounded paging, exact eligibility, mutex-guarded fixed-Tool analysis, direct publication, restart/limit handling, interruption, and isolated failure continuation are implemented. Focused proof passed: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_targets.py tests/database/stockfish/test_bulk.py -q` (`10 passed in 4.49s`; Bash tool timeout `120000` ms). Breakpoint: none.
- **Stage 5:** completed - mutex-guarded serial draining, immutable-quality claims, engine reuse/replacement, atomic completion, finite young-claim crash recovery, interruption cleanup, and isolated failure continuation are implemented. Focused proof passed: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_worker.py -q` (`9 passed in 3.23s`; Bash tool timeout `120000` ms). Breakpoint: none.
- **Stage 6:** completed - thin `stockfish benchmark|bulk|worker` adapters and settled exit mapping are implemented. CLI proof passed: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -k stockfish -q` (`10 passed, 54 deselected in 0.74s`; Bash tool timeout `120000` ms). The bounded real benchmark proof passed: `timeout 180s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_real_benchmark_smoke.py -q` (`1 passed in 2.55s`; Bash tool timeout `240000` ms). The separate fixed-Tool worker/publication proof passed: `timeout 180s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_real_worker_publication_smoke.py -q` (`1 passed in 3.72s`; Bash tool timeout `240000` ms). All artifacts were temporary, no sizing conclusion was made, earlier proof remained valid, and boundary tests were not required because no explicit enumeration changed. Breakpoint: none.
- Retain passing stage proof until an affecting later change invalidates it. Do not run `scripts/check.py`, lint, formatting, builds, source-size checks, aggregate maintenance, full benchmark, or independent Quality validation for this Plan.

- **Closeout:** accepted with 76 tests passing across the retained focused proofs in 21.38 seconds. No escalation boundary was crossed.

## Proof

- Focused fake-engine and injected-writer tests prove UCI normalization, fixed options, watchdog termination, mutex lifecycle, deterministic benchmark resume/checkpoint behavior, bounded transient artifact-write recovery, permanent persistence failure reporting without damaged earlier records or engine-failure misclassification, queue CAS/stale/promotion/failure invariants, target union/order/eligibility/paging, bulk interruption/failure continuation, worker drain/exit, and CLI exits.
- The one-position real benchmark smoke proves only real startup, option application, requested output/checkpoint/summary containment, clean shutdown, and exact-command completed-run protection; it is not sizing evidence.
- The separate one-position real worker smoke proves the accepted Tool profile and complete DB-06 publication through the queue transaction seam. Focused fake-clock worker proof separately proves that a post-crash younger `running` row is waited out only for its finite remaining stale interval, then reclaimed and completed.

## Acceptance

- The first supported `database.stockfish` package is clean of legacy/prototype runtime dependencies and exposes the three approved thin CLI commands with explicit paths and meaningful exits.
- Real Stockfish 18 proof establishes the fixed Browser/Tool options, MultiPV normalization, per-analysis hash clearing, 30-second watchdog, clean termination, and complete DB-06 publication at the selected Tool profile.
- The Windows named mutex enforces one worker/bulk engine per database and recovers after normal exit, a busy owner, owner crash, and abandoned ownership without stale lock-file cleanup.
- Queue proof establishes max-quality enqueue, FIFO and stale claims, one-time-ticket rejection, promotion while running, matching-ticket failure, and one-transaction result/line publication plus conditional queue deletion or release.
- Bulk proof establishes the exact target population and deterministic order, current-result eligibility, unlimited default and optional positive limit, bounded paging, immediate direct publication, restart progress, interruption, and failure continuation without queue or history rows.
- Worker proof establishes finite young-claim recovery, drain-and-exit behavior, immediate Ctrl+C handling, no same-launch retry, and nonzero completion after isolated failures.
- A transient Windows artifact-write `PermissionError` or sharing violation is retried finitely and can complete without losing earlier readable checkpoint records.
- A permanent manifest/checkpoint/summary write failure stops with a nonzero persistence error, leaves earlier readable records intact, writes no repository log, and is not reported as a Stockfish chess-analysis failure.
- The bounded real benchmark smoke remains exactly one approved position, one low node budget, one thread setting, one hash setting, and one repetition; it produces no sizing conclusion or broad benchmark evidence.
- No schema, history, target-list, shared queue, concurrent-engine, API/backend/frontend, cutover, maintenance-suite, or independent Quality work enters DB-07.

## Escalation boundaries

- Do not decide a new engine/profile, quality order, target population/order, retry/history policy, CLI contract, dependency, mutex namespace contract, schema/DDL shape, or acceptance threshold.
- Escalate any need for a new table/index, migration, persisted run/failure/target history, shared JSON queue, second concurrent engine, API/backend/frontend integration, legacy/prototype reuse, raw UCI parsing in `database.analysis`, public raw database handles, or bypassed/duplicated DB-06 validation/publication.
- Escalate any behavior that allows Browser to replace Tool, saves duplicate same-quality current results, publishes partial lines, holds SQLite during search, waits indefinitely, watches forever, or changes engine/configuration versions while analysis is running.

## Visible result

> A user can run `stockfish worker` to safely drain live requests, or `stockfish bulk` to resumably publish eligible Tool analyses, and each completed position shows one complete validated result with all candidate lines and no partial queue state.
