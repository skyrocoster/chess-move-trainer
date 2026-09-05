# DB-07 Stockfish benchmark experiment

> **Status:** approved for the isolated benchmark experiment
> **Scope boundary:** This record settles only the disposable benchmark setup described below. It does not complete
> DB-07 grilling, select the Tool node budget, or authorize the supported database package, CLI, queue, worker, bulk
> analysis, API, frontend, cutover, or retirement work.

## Purpose and stopping point

Create a self-contained Stockfish 18 benchmark experiment that can run a broad fixed matrix unattended, checkpoint
every result, and resume safely. The full run will be started by the user away from the AI. A later, fresh context will
review the resulting evidence and continue the DB-07 decisions.

This experiment proves only that the benchmark is correctly prepared and operable. It is not a live tool and is not
the production benchmark command required later by DB-07. The later supported package/CLI must independently
corroborate any accepted benchmark conclusion.

## Ownership and paths

- Put the experiment under `experiments/prototypes/stockfish-db07-benchmark/`.
- Put all generated manifests, checkpoints, summaries, temporary state, and run artifacts under that experiment's
  ignored `.artifacts/` directory.
- Use `data/stockfish/test_positions.json` as the read-only position input.
- Use the existing Stockfish 18 executable under `data/stockfish/` and verify its identity before running.
- Do not write an unreviewed benchmark report under `docs/benchmarks/`. A later context may deliberately publish a
  compact report after reviewing the completed local dataset.
- Do not import, wrap, delegate to, copy, or extend production backend modules or legacy benchmark/tool
  implementations. This experiment may use the shared `experiments/pyproject.toml` environment and its existing
  `python-chess` dependency.

## Fixed benchmark envelope

The input contains ten selected positions. Every position participates in every measured configuration.

- Engine: Stockfish 18.
- Candidate count: MultiPV 5. Fewer lines are valid only when the position has fewer than five legal moves.
- Search limit: fixed nodes only; no time-based search limit.
- Node budgets: `100000`, `200000`, `400000`, `800000`, `1600000`, `3200000`, and `6400000`.
- Engine threads: `1`, `2`, `4`, and `6`.
- Engine hash: `64`, `256`, and `1024` MiB.
- Repetitions: three balanced rounds.
- Total measured jobs: 10 positions x 7 node budgets x 4 thread settings x 3 hash settings x 3 rounds = 2,520.
- This experiment measures individual engine performance only. It does not benchmark multiple concurrent workers.

Each round contains every configuration exactly once for every position. Use a deterministic, recorded shuffle. Treat
each thread/hash pair as one profile block: start one Stockfish process for that profile, perform its jobs, and close
the process before moving to another profile. Shuffle both profile-block order and the jobs inside each block in a
repeatable way. Do not keep multiple profile engines alive concurrently.

At the start of every profile block, run one unmeasured 200,000-node warm-up using a deterministic position from the
approved input. Clear the transposition hash after the warm-up and before every measured analysis. Measured results
must therefore be independent of earlier positions and execution order.

Use generous explicit finite process watchdogs solely to terminate a hung engine safely. A watchdog is not the chess
search limit and must not silently turn the fixed-node experiment into a timed search.

## Start, resume, and completion behavior

- The user-facing entry point is `start.py` with no flags, arguments, setup questions, or configuration prompts.
- With no compatible prior state, `start.py` creates the benchmark run and starts it.
- With a compatible incomplete run, `start.py` resumes automatically without repeating successful jobs.
- Manifest/input/engine/configuration incompatibility stops clearly and safely rather than mixing evidence.
- After a fully successful run, launching `start.py` reports the completed artifact location and exits without starting
  another run.
- Within one invocation, a failed analysis is recorded and is not retried automatically. The remaining matrix
  continues. The invocation exits nonzero after all available jobs have been attempted if failures remain.
- Explicitly launching `start.py` again retries only failed or otherwise unfinished jobs while retaining prior attempt
  evidence. It must not repeat successful jobs.
- While active, the runner requests that Windows keep the system awake, without permanently changing power settings,
  and always releases that request during normal exit or controlled failure. The display need not be kept awake.
- Interrupts must leave a readable checkpoint and terminate Stockfish cleanly where possible.

## Evidence format

Checkpoint every attempted analysis as it finishes. Do not wait until the suite completes before persisting results.

The local run directory contains at least:

- a versioned manifest describing the full matrix, deterministic ordering/seed, input identity, engine identity and
  options, relevant software and machine metadata, timestamps, and dataset state;
- append-safe JSONL attempt/result records sufficient for exact resumption and duplicate prevention;
- generated JSON and CSV summaries that can be regenerated from the checkpointed records; and
- concise human-readable progress and final status.

Each successful normalized result records enough identity to trace its round, position, engine profile, node budget,
and attempt. Retain wall-clock and engine-reported performance measurements, including nodes and nodes per second,
plus useful reported search measurements such as depth, selective depth, and hash fullness when Stockfish supplies
them. Retain all normalized candidate lines with rank, an explicitly labelled score and score perspective, WDL, and
principal variation. Preserve centipawn and mate scores without conflating them.

Do not retain raw UCI transcripts. Structured normalized results are the evidence. Failures must still retain bounded
structured diagnostics sufficient to identify the job, failure category, process outcome, and safe retry state; do not
write repository log files outside `.artifacts/`.

Summary generation is descriptive only. It must not silently choose or recommend a Tool node budget. The later review
owns interpretation and any decision.

## Focused setup proof and acceptance

The AI must not start the complete 2,520-job benchmark. Before handoff, prove only:

1. structural and chess validation of all ten input positions;
2. exact enumeration of the full 2,520-job matrix with deterministic ordering and no duplicate job identities;
3. a four-analysis live smoke run using one approved position, two node budgets, two engine profiles, and one round in
   an isolated smoke artifact directory;
4. real Stockfish startup, option application, warm-up, per-analysis hash clearing, MultiPV normalization, checkpoint
   persistence, JSON/CSV summary generation, and clean engine shutdown;
5. interruption-safe or preseeded-partial resumption that does not repeat successful jobs;
6. failure recording/continuation and nonzero incomplete outcome without an automatic retry in the same invocation;
7. safe completed-run behavior that does not begin a second benchmark; and
8. `start.py` startup with no arguments and clear progress/artifact reporting.

Every executed proof command and engine process must have an explicit finite timeout. Generated smoke evidence remains
ignored and must not contaminate a future full run.

## Explicit exclusions and later handoff

- No final Tool node-budget decision or interpretation of benchmark winners.
- No full benchmark run by the AI.
- No production `chess_move_trainer.database` benchmark package or supported CLI.
- No database access, target selection, queue, worker, bulk-analysis orchestration, application, API, or frontend work.
- No worker-concurrency benchmark.
- No schema or replacement-database change.
- No raw UCI archive and no tracked unreviewed benchmark dataset.
- No claim that this experiment satisfies DB-07's complete grilling or implementation gate.

After the user completes the run, the next context should inspect the manifest, checkpoint completeness, failure state,
and descriptive summaries before discussing the Tool budget or the remaining DB-07 decisions. Any material change to
the matrix, positions, engine identity, independence rules, or evidence contract is a new decision rather than a silent
implementation adjustment.
