# DB-07 Grilling Handoff: Stockfish Queue and Worker

**Status:** Coordinator-confirmed historical directional evidence for DB-07. This is the mandatory DB-07 grilling
handoff before its implementation Plan/work begins. It is not implementation authorization and does not select
DB-08.

**Authority retained:** The database-rebuild master plan and the binding direction/schema records remain authoritative
for the DB-07 envelope, exact queue table, quality ordering, target population, sequencing, exclusions, and proof. This
handoff finalizes the bounded DB-07 choices without reopening the ten-table catalogue or DB-06 publication rules.

## Decision basis

The isolated Stockfish 18 experiment and its reviewed report are accepted as sufficient evidence for the Tool profile
decision. The dataset is incomplete (1,822 of 2,520 successful jobs) because 698 checkpoint/manifest writes failed with
Windows `PermissionError`; these were persistence failures rather than Stockfish analysis failures. The successful data
still covers every node budget with profile-driven missingness and includes eight fully covered thread/hash profiles.

The experiment showed that 6.4 million nodes was the strongest measured budget and remained fast on this computer. The
earlier 10–15 second aim was sizing guidance, not a continuing acceptance threshold. DB-07 does not need another
comparative benchmark to reopen or corroborate this choice. The supported benchmark command still receives a bounded
real-engine smoke test as implementation proof.

Relevant evidence:

- `docs/grilling-docs/database-rebuild-db-07-benchmark-experiment.md`
- `experiments/prototypes/stockfish-db07-benchmark/BENCHMARK_RESULTS.md`

## Package and dependency boundary

DB-07 creates the first supported Stockfish implementation in the clean database toolchain under
`chess_move_trainer.database.stockfish`. That package owns Stockfish process control, UCI normalization, the reusable
benchmark, queue operations, target selection, bulk processing, and the standalone worker.

The existing `chess_move_trainer.database.analysis` package remains engine-independent. Stockfish code supplies its
normalized values to the DB-06 validation/publication service; it does not duplicate or bypass those rules. The new
package may compose the existing clean connection, schema, position, and analysis services. It must not import, wrap,
delegate to, copy, or extend the legacy backend/old script implementations. The disposable experiment is behavioral
evidence only; the supported benchmark is rebuilt cleanly.

The public CLI group is `stockfish`, reached through the existing module entry point:

- `python -m chess_move_trainer.database stockfish benchmark`
- `python -m chess_move_trainer.database stockfish bulk`
- `python -m chess_move_trainer.database stockfish worker`

Adapters remain thin Typer commands. Database operations require an explicit database path, and every command that
starts Stockfish requires an explicit executable path. The benchmark additionally receives explicit position-input and
output locations plus proper matrix arguments rather than relying on repository-fixed paths.

## Fixed Browser and Tool profiles

- Engine identity: Stockfish 18, verified at startup.
- Candidate count: MultiPV 5, except positions with fewer than five legal moves.
- Browser: fixed 200,000 nodes.
- Tool: fixed 6,400,000 nodes.
- Both qualities: 6 Stockfish threads and 1,024 MiB hash.
- Worker concurrency: one live Stockfish process at a time for a database.
- Per-analysis watchdog: 30 seconds. The watchdog terminates a hung engine; it never becomes a time-based chess search
  limit.
- Browser and Tool each have an explicit configuration version, initially version 1. A later change to nodes, threads,
  hash, MultiPV, or other result-affecting settings requires the relevant manual version increment while no analysis is
  running.

One process may be reused across sequential jobs. Clear Stockfish's hash before every analysis so fixed-node results do
not depend on earlier positions. A terminal canonical position is normalized and published without asking Stockfish for
candidate lines. After an engine error or timeout, terminate that process before starting any replacement process.

## Single-process guard

`stockfish worker` and `stockfish bulk` use a database-specific Windows named mutex. Its identity is derived from the
normalized database path. A second analysis command does not wait indefinitely: it reports that analysis is already
running and exits nonzero. Enqueuing ordinary requests remains possible while the mutex is held.

This is a Windows kernel-owned lock, not a sentinel or PID file. Windows releases it when its process exits, crashes, is
killed, or the machine restarts. An abandoned lock can therefore be acquired safely without manual cleanup. No SQLite
write transaction is held while Stockfish searches.

## Queue and worker behavior

The exact `derived_analysis_queue` table and its application-enforced invariants remain those in the binding schema
record. DB-07 adds no queue, run, batch, or failure-history table.

- Requests retain the settled atomic maximum-quality behavior: Tool may promote Browser, and no request can downgrade
  Tool.
- The worker claims the oldest available request; mixed Browser/Tool scheduling receives no special priority because
  that edge case is not a product concern.
- A claim gets a fresh random, one-time UUID claim ticket and records its claim time and claimed quality. The ticket is
  unchanged during that analysis; there is no heartbeat.
- A running claim becomes stale after 2 minutes. Reclaiming it replaces the ticket, so any late result from the old
  worker is ignored. A restarted drain may wait only for this known finite remainder before reclaiming; it never waits
  indefinitely.
- Successful publication, all candidate lines, and deleting or releasing the queue row use the binding one-transaction,
  matching-ticket rules. Promotion while Browser is running retains the settled publish-if-eligible and release-for-Tool
  behavior.
- `stockfish worker` drains the current queue and exits. It does not remain resident waiting for later requests.
- Ctrl+C stops immediately, terminates the current engine, and saves no partial result. A controlled stop releases the
  claimed row to `queued` when possible; a hard process death leaves it for the 2-minute stale recovery rule.
- An isolated engine failure is printed and not retried in the same launch. With a matching ticket, the queue row is
  deleted unless it was promoted and must be released for the higher-quality request. Other queued work continues. The
  command exits nonzero after draining if any job failed.

## Bulk behavior

Bulk Tool work remains separate from the live queue and publishes each complete result directly through the DB-06
service. It never inserts its selected targets into `derived_analysis_queue` and never persists a target list or run
record.

The target query remains the authority-defined union of canonical positions reached at plies 0–19 by imported games or
opening routes. Game positions are ordered by descending occurrence count, route-only positions have frequency zero,
and ties are deterministic.

- With no limit, `stockfish bulk` processes every eligible target and exits when complete.
- `--limit N` restricts that launch to the next `N` eligible targets. It is optional, not a default of 25.
- Eligible means no analysis, Browser-only analysis, or Tool analysis made stale by an older configuration or engine
  version. A current Tool result is skipped.
- Targets are read in small bounded pages, but each position is analyzed and published individually and immediately.
  Results are not held for a group-wide write.
- Re-running the command recomputes eligibility from current database state. Successfully published positions are
  skipped, while an interrupted or failed position remains eligible. This provides stop/start progress without a run
  history.
- Ctrl+C immediately discards only the current unfinished result. An isolated failure is reported without an automatic
  same-launch retry; remaining selected targets continue, and the final exit is nonzero when failures occurred.

## Supported benchmark

Rebuild the isolated benchmark's useful behavior cleanly inside `database.stockfish`; do not move its implementation
into production. Keep its broad configurable matrix, deterministic ordering, real Stockfish identity/options,
per-result checkpointing, compatible-run resume, failure continuation, completed-run protection, normalized JSONL,
regenerable JSON/CSV summaries, progress, interruption safety, and finite process watchdogs.

Generalize repository-fixed values into clear CLI arguments, especially the Stockfish executable, position input,
output directory, node budgets, thread counts, hash sizes, repetitions, and shuffle seed. Every generated manifest,
checkpoint, summary, and temporary file belongs below the caller's explicit output directory; the command must not
silently write into `docs/`, the experiment, or another repository-fixed artifact path. An incompatible existing output
directory stops safely rather than mixing evidence.

This command exists for future investigations. DB-07 acceptance does not run a new decision matrix. Its focused real
smoke proves startup, option application, one small analysis, checkpoint/output creation at the requested path, summary
generation, resume/completed behavior, and clean shutdown without interpreting a new budget winner.

## Invocation, exit, and focused proof

All commands are non-interactive, expose useful `--help`, show concise progress, and report their selected database or
artifact location. A clean completion, including no eligible work, exits zero. Invalid arguments, incompatible paths or
database state, wrong engine identity, a held single-process lock, or setup failure exits nonzero before analysis.
Per-position failures continue where specified and produce a nonzero final exit. Ctrl+C exits as an interruption (130)
after bounded engine termination.

Focused proof must cover the clean package/source boundary; CLI help and explicit paths; Stockfish 18 identity and fixed
Browser/Tool option application; normalized MultiPV publication through DB-06; the 30-second watchdog and clean process
termination; the Windows mutex's normal, busy, crash-release, and abandoned-owner behavior; atomic max-quality enqueue;
oldest-first claim; 2-minute stale reclaim; one-time-ticket rejection; running promotion; matching-ticket failure;
worker drain/exit; bulk target order, eligibility, optional limit, bounded paging, direct immediate publication,
stop/start behavior, failure continuation, and interruption; and the bounded benchmark smoke above.

Every executed proof command and engine process must have an explicit finite timeout. No full or comparative benchmark,
maintenance suite, application integration, or independent Quality run is part of DB-07 implementation proof.

## Escalation and exclusions

Escalate rather than changing the selected engine profile, one-process rule, package ownership, queue/schema contract,
quality ordering, target population, retry/history policy, CLI behavior, or proof acceptance. Escalate if correctness
would require a new table, persisted run/failure history, a shared JSON queue, a second concurrent engine, or bypassing
DB-06 validation/publication.

DB-07 includes no backend/API/frontend integration, viewer contract, production route change, application queue drainer,
cutover, database replacement, old-database mutation, or retirement work. Those remain gated to their later slices.
