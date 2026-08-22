# MP-10 Browser Evaluation - evaluate the displayed read-only position from the browser

> **Status:** done - Stage 5 independent validation and read-only closeout passed; final human acceptance recorded and Plan archived

- **Read trigger:** Read after the confirmed MP-10 synthesis and before every MP-10 dispatch; re-read the
  applicable stage before execution.
- **Upstream:** [confirmed MP-10 grilling synthesis](../../../grilling-docs/mp10-browser-evaluation.md),
  [static-position to analysis master plan](../../../master-plans/static-position-to-analysis.md), and the
  accepted [MP-09 Plan](../../done/mp09-persisted-backend-stockfish-analysis/mp09-persisted-backend-stockfish-analysis.md).

## Outcome

Deliver browser evaluation for the currently displayed read-only position: the browser deliberately requests
backend evaluation and presents five ranked candidate lines with White-relative scores, win/draw/loss
percentages, and an always-reserved accessible eval bar beside the board. An eligible persisted result loads
automatically without triggering computation; a missing result appears only after deliberate Analyze; a stale
result stays visible and labelled until deliberate Update atomically replaces it. Work already queued or running
survives navigation, disconnection, and restart and is observed and polled automatically. Failure is shown
clearly with no automatic retry and no partial result; deliberate retry is available. The board stays read-only.
This matters because a human can evaluate the displayed position from the product UI while the backend Stockfish
analysis system built by MP-09 performs, stores, and reuses the work.

## Scope

- **Included:** Backend evaluation surface (read eligibility/result with no computation; deliberate enqueue for
  Analyze/Update/Retry; status/observe for polling; strict canonical six-field FEN validation and request-size
  bounds; typed schemas and error codes); one durable FIFO queue for evaluation work with exact-FEN concurrent
  dedupe, survival across navigation/disconnection/restart, requeue-from-start on interruption, and automatic
  observation of already queued/running positions; five bounded workers, one engine each, on the exact fixed
  MP-09 profile (`mp09-balanced-nodes-v2-200000`: Stockfish 18, 200,000 nodes, MultiPV 5, Threads 1, Hash 128
  MiB, engine WDL); terminal classification persisted immediately without launching Stockfish; clear failure
  with no automatic retry, no partial result, and deliberate retry; frontend analysis client, status state
  machine and observation polling, AnalysisPanel in the existing context panel responsive below the board,
  five ranked lines (White-relative score, SAN with move numbers, W/D/L percentages, standard `+/-M` mate
  notation, text-only with no PV playback or board changes), stale labelling, failure presentation; an
  application-owned accessible vertical EvalBar beside the board aligned to board orientation with
  neutral/queued-running/best-line states and a textual accessible value, backed by the installed Base UI Meter
  primitives; trusted local/private deployment with no auth and strict validation.
- **Expected areas:** `backend/app/features/analysis/**` (read-only reuse of models, repository, engine,
  locking, errors), `backend/app/features/evaluation/**` (new MP-10-owned queue and API surface; exact table
  names left to the bounded implementation stage), `backend/app/main.py` (bounded API mounting and CORS method
  widening for the evaluation surface only), `backend/tests/features/evaluation/**` and focused additions under
  `backend/tests/features/analysis/**`, `frontend/src/features/viewer/**` (analysisApi, AnalysisPanel, EvalBar,
  ViewerWorkspace/GameContext integration, tests, stories, CSS), `tests/e2e/viewer*.spec.ts`, this Plan, and
  bounded MP-10 current-state/wording updates in `docs/master-plans/static-position-to-analysis.md` at final
  closeout only. Touch `backend/app/features/positions/**` only if a shared boundary defect is proven required.
- **Excluded:** Editing, piece movement, or board changes; PV playback; persistence of unknown positions or
  their provenance (MP-12); authentication, accounts, or authorization; user-adjustable engine settings;
  automatic new or stale computation triggered by reading, opening, or navigating; any cancellation surface;
  browser-side evaluation; full-corpus execution; corpus/benchmark/setup tooling changes; dependency changes;
  unrelated refactors; completed Plan edits; the roadmap; `Scratch/`; commits; pushes; and formatter execution
  through `--fix`.
- **Preservation:** The worktree contains unrelated uncommitted MP-09 delivery, BoardControl, workflow, and
  experiment changes, and a pre-existing unrelated Ruff failure in `scripts/stockfish_analysis/analyze_menu.py`
  (lint I001/E501 plus format) reported by the last full check. Record `git status --short` before and after
  every stage, edit only the dispatched MP-10 paths, never reset or rewrite another change, and distinguish
  unrelated check failures from MP-10 failures. The full check is required to pass at closeout; the known
  unrelated Ruff failure must be resolved by its owner before closeout and MP-10 must not absorb or edit that
  file without separate authorization.

## Dispatch gate (prerequisite)

- MP-10 execution stages begin only after MP-09 final acceptance is confirmed as recorded. The working-tree
  master plan records MP-09 accepted on 2026-08-20 after all five stages, including independent validation and
  final human acceptance; the committed HEAD version lags and is not authority. Confirm the recorded acceptance
  at dispatch before Stage 1 starts. This preserves the strict `MP-06 -> MP-07 -> MP-08 -> MP-09 -> MP-10`
  order and changes no agreed sequence.
- The corpus-fill (full-corpus analysis using the MP-09 tooling) is still running and is the only remaining
  running work. Preserve it: MP-10 never stops, rewrites, or races it, and the MP-10 queue worker pool respects
  the same `AnalysisRunLock`/busy discipline so it never writes the database while the fill holds the lock.
  Stage 2 live-write proof must not be authorized or run while it conflicts with the active MP-09 analysis
  lock/job; a safe read-only live proof comes first, and any bounded write waits for a free lock and explicit
  authorization.

## Stages

1. **accepted - durable queue, evaluation service foundation, and offline fake-engine proof (ORDERED).**
   - **Ordered actions:** Define the MP-10-owned durable FIFO evaluation queue as an independently named and
     versioned persistence surface with explicit initialization and refusal when missing/incompatible (mirroring
     MP-09's analysis-schema discipline; exact table names are a bounded implementation choice). Enforce the
     invariants: one queued work item per canonical exact six-field FEN, exact-FEN concurrent dedupe, FIFO
     order, explicit queued/running/done/failed states, requeue-from-start for interrupted or restarted running
     work, and no partial result ever persisted. Reuse the MP-09 analysis models and repository for canonical
     FEN validation, eligibility (missing/eligible/stale), result reads, and atomic publication; the read path
     never triggers computation. Persist terminal classification immediately without launching Stockfish using
     the MP-09 result shape (typed terminal kind, zero candidates). Build the bounded five-worker pool on the
     fixed `mp09-balanced-nodes-v2-200000` profile, one engine per worker, workers never writing SQLite, short
     coordinator transactions, and lock/busy coexistence with the MP-09 `AnalysisRunLock`. Record clear failure
     states with no automatic retry and support deliberate retry. Add strict request validation and size bounds.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/evaluation backend/tests/features/analysis -k "queue or dedupe or enqueue or observe or terminal or eligibility or requeue or restart or failure or retry or lock or busy or validation or schema" -q`;
     the complete offline evaluation/analysis suite. All proof is offline, uses fake engines and temporary
     databases, and asserts no live DB, engine, service, download, or runtime install.
   - **Breakpoint:** independent review must accept offline queue ordering, dedupe, durability/requeue, schema
     isolation, terminal classification without engine, no-computation reads, failure/no-auto-retry semantics,
     and lock/busy coexistence before any HTTP surface or live effect.
   - **Escalate if:** queue ownership, atomicity, restart durability, requeue, or dedupe requires a dependency,
     a destructive operation, a changed MP-09 contract, or a contested schema-ownership decision.

2. **accepted - backend HTTP API, observation contract, and gated bounded live proof (ORDERED).**
   - **Ordered actions:** Add the evaluation HTTP surface under `/api`: read eligibility and result for the
     displayed FEN (no computation), deliberate enqueue for Analyze/Update/Retry with strict canonical FEN
     validation and request-size bounds, and status/observe returning queued/running/done/failed states and
     completion so the frontend can poll and observe already queued/running work without side effects. Use
     typed Pydantic schemas with exact keys and typed error codes mirroring the positions router. Widen CORS
     methods only for the evaluation surface (currently GET-only) and mount the router in `create_app` without
     changing other surfaces. Prove the full API offline with fake engines and temporary databases, including
     eligible-read-never-computes, enqueue/dedupe, status transitions, terminal classification, validation, and
     size-bound rejection. Then run a safe read-only live proof against the live database using the existing
     MP-09 results (83 results, 381 candidates): eligible reads return persisted results without computation,
     missing/stale classification is correct, and terminal classification is instant. Stop before any write.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/evaluation -k "api or endpoint or observe or enqueue or status or validation or bounds" -q`;
     then the complete offline evaluation suite; then the read-only live inspection cited from its authorized
     breakpoint below.
   - **Breakpoint:** explicit human authorization is required before any live database write, and the
     corpus-fill must not hold the MP-09 analysis lock at that time (verify lock state; wait or coordinate;
     never race). After that bounded authorization, enqueue one missing FEN with the verified engine, observe
     queued -> running -> done, verify atomic publication, prove duplicate enqueue dedupe, and exercise
     deliberate retry. Destructive failure injection uses only temporary or copied databases. Require human
     acceptance of the API behavior, no-computation reads, and observation contract before Stage 3.
   - **Escalate if:** the live write cannot proceed safely alongside the corpus-fill, CORS/method widening is
     contested, or the API contract requires a new product or security decision.

3. **pending - frontend analysis surface in the existing context panel (ORDERED).**
   - **Ordered actions:** Add a strict frontend analysis client mirroring the positionApi validation style.
     Build the status state machine and observation polling: eligible results load automatically without
     triggering computation; missing results show a deliberate Analyze action; stale results display labelled
     and require deliberate Update; already queued/running positions are observed and polled automatically;
     failure shows clearly with no automatic retry and a deliberate Retry action. Present all five ranked lines
     with White-relative typed scores and standard `+/-M` mate notation, SAN with move numbers, and W/D/L
     percentages; lines are text-only with no PV playback and never change the board. Place AnalysisPanel inside
     the existing context panel (GameContext surface), responsive below the board on constrained layouts.
   - **Focused proof:** `npm.cmd run test --prefix frontend -- --run` targeted analysisApi, AnalysisPanel,
     ViewerWorkspace, and GameContext test files; Storybook stories for every panel state (eligible, missing,
     stale, queued, running, completed, failed); component and accessibility assertions.
   - **Breakpoint:** human and visual review accepts the panel states, controls, stale labelling, failure
     presentation, and responsive behavior before the eval bar integration.
   - **Escalate if:** the panel requires a new surface, a changed interaction, a dependency, or automatic
     computation.

4. **accepted - application-owned EvalBar and ViewerWorkspace integration (ORDERED).**
   - **Ordered actions:** Build the application-owned EvalBar backed by the installed Base UI Meter primitives:
     always reserved, vertical, beside the board, aligned to the board's orientation; neutral before analysis,
     queued/running state while work is pending, best-line evaluation when a complete result exists; and a
     textual accessible value describing the state and evaluation for assistive technology and keyboard users.
     Integrate it beside the BoardAdapter in ViewerWorkspace so it flips with the board and never covers board
     content. Component tests, Storybook stories, and keyboard/assistive-technology review for all states.
   - **Focused proof:** `npm.cmd run test --prefix frontend -- --run` targeted EvalBar and ViewerWorkspace
     tests; Storybook stories for neutral/queued-running/best-line states; axe and keyboard/AT checks.
   - **Breakpoint:** visual and accessibility review; user edits at this visual breakpoint are authoritative and
     must be bounded, incorporated, validated, and continued.
   - **Escalate if:** the eval bar requires a different implementation than the installed Base UI Meter, a new
     dependency, or a changed accessibility contract.

5. **accepted - independent validation, full closeout, bounded master-plan wording, and archival (ORDERED).**
   - **Ordered actions:** Run fresh independent Quality validation across queue semantics, no-computation
     reads, deliberate Analyze/Update/Retry, durable FIFO and dedupe, requeue-on-interruption, observation and
     polling, terminal classification, failure presentation, eval bar states and accessible value, and
     responsive panel behavior. Resolve only coordinator-authorized in-scope defects. Run the full read-only
     closeout `.venv\Scripts\python.exe scripts\check.py` without `--fix`; it is required to pass. The known
     unrelated `scripts/stockfish_analysis/analyze_menu.py` Ruff failure must be resolved by its owner before
     closeout; MP-10 does not edit that file, and if it still fails at closeout, report the exact failure and
     escalate rather than pass with failures. Perform documentation link/template review and scoped `git diff
     --check`. After implementation acceptance, apply the bounded master-plan wording/current-state update:
     replace the MP-10 slice-row "cancel" gate wording and the MP-10 section's fresh-grilling framing with the
     settled contract, and record MP-10 current state, without changing other milestones or the roadmap. Update
     this Plan's progress/status, obtain explicit human acceptance, move the complete Plan directory to
     `docs/plans/done/mp10-browser-evaluation/`, and repair links atomically. Never commit or push.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/evaluation backend/tests/features/analysis -q`;
     `.venv\Scripts\python.exe scripts\check.py` in read-only mode without `--fix`; documentation link/template
     review; `git diff --check` on MP-10 paths; final `git status --short` and scoped diff review proving
     unrelated dirty work is preserved. Real Stockfish and live-DB commands are not part of ordinary checks and
     are cited from their separately authorized stage evidence rather than rerun automatically.
   - **Breakpoint:** fresh independent validation must pass, the full read-only check must pass (with the
     unrelated failure resolved by its owner, not absorbed), and the human must explicitly accept the persisted
     evaluation behavior before archival.
   - **Escalate if:** validation requires widening scope, suppressing an unrelated failure, using `--fix`,
     editing the unrelated failing file, changing acceptance, editing the master plan before implementation
     acceptance, or rewriting historical records.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the outcome. The five-stage shape keeps offline semantics, live effects, frontend presentation, the eval bar,
and final independent acceptance behind distinct evidence gates; Plan authoring itself is not an implementation
stage.

## Progress and decisions

- **Stage 1:** accepted after independent validation - delivered on 2026-08-20: the MP-10-owned versioned evaluation schema
  (`evaluation_schema`, `evaluation_queue`) with explicit init and refusal, exact-FEN dedupe, FIFO ordering,
  queued/running/done/failed transitions, requeue-from-start and restart durability, terminal classification
  without engine launch, no-computation eligibility/result reads, deliberate analyze/update/retry semantics,
  clear failure with no automatic retry, and a bounded five-worker pool on the fixed MP-09 profile with
  `AnalysisRunLock`/busy coexistence. Proof: focused filter 40 passed (33 deselected); complete offline
  evaluation/analysis suite 73 passed; Ruff lint clean; scoped and repo-wide format checks pass; source-size
  check passed; workflow tests 10 passed. All proof used fake engines and temporary databases; no HTTP, frontend,
  live database, live engine, download, or runtime install occurred. Breakpoint: independent review must accept
  offline queue ordering, dedupe, durability/requeue, schema isolation, terminal classification without engine,
  no-computation reads, failure/no-auto-retry semantics, and lock/busy coexistence. Breakpoint accepted after
  independent semantic review of all Stage 1 invariants.
- **Stage 2:** accepted after independent validation and human acceptance on 2026-08-21 - backend API and offline
  proof delivered; the focused API filter passed 16 tests
  (26 deselected), the complete offline evaluation suite passed 42 tests, scoped Ruff and format checks passed,
  and the source-size check passed. The authorized read-only live inspection found 3,157 analysis results and
  15,731 candidates, not the earlier 83/381 baseline; the live database has no `evaluation_*` tables, so the
  mounted API correctly returned typed `evaluation_unavailable` for a read and made no database change. The
  analysis lock file exists, but active ownership cannot be established safely without a lock acquisition. The
  authorized live-write attempt then acquired `AnalysisRunLock`, passed read-only integrity and backup checks,
  verified the configured Stockfish identity against the fixed profile, and stopped at evaluation-schema
  initialization with `sqlite3.OperationalError: database is locked`; no evaluation tables or queue rows were
  added. The retained temporary recovery copy is 204,771,328 bytes with SHA-256
  `e0194fa8493725a37dffeed81f290e4dfd2bb846de0e6bce16d024be93662181` and integrity `ok`; the live database
  remains integrity `ok` with 3,157 results and 15,731 candidates, but its SHA-256 differs from that copy,
  making the live state/lock coordination uncertain. The acquired lock was released cleanly. Breakpoint satisfied:
  the bounded freshness check established safe conditions for the continuation; the normal `AnalysisRunLock` was
  acquired and released cleanly, and the human accepted the API/no-computation/observation contract.
- **Stage 3:** accepted after an independent fresh Quality result of **PASS** and the user's explicit acceptance
  of the visual breakpoint on 2026-08-21 - the frontend implementation was completed within
  `frontend/src/features/viewer/**`:
  strict `analysisApi`, `AnalysisPanel` and CSS, `GameContext`/`ViewerWorkspace` integration, focused tests, and
  all seven Storybook states. Stage 3 acceptance is complete; Stage 4 remains pending/not started.
- **Stage 4:** complete/accepted on 2026-08-21 after fresh independent Quality validation passed and the user
  explicitly accepted the visual/accessibility breakpoint, saying, “We'll accept that for now.” Delivered the
  application-owned Base UI Meter EvalBar, shared analysis state, orientation handling, accessible textual
  values, and a separate reserved `ViewerWorkspace` grid track. Initial Quality validation found a 26px
  board/context center delta and a 52px toolbar/board width delta; one repair failed and the workflow stopped.
  The user then explicitly approved a fresh case/direction to reserve EvalBar outside board alignment width.
  The fresh Luna correction changed only `ViewerWorkspace.tsx` and `ViewerWorkspace.module.css`; established
  e2e assertions were unchanged.
- **Stage 5:** accepted on 2026-08-21 after fresh independent Quality validation passed, the full read-only check
  passed, bounded documentation checks passed, and the user explicitly authorized final closeout with “close out”.
  The complete Plan directory was archived after the MP-10 current-state and settled no-cancellation wording were
  recorded in the master plan.

## Proof

- Offline deterministic proof uses fake UCI engines and temporary databases; it covers queue FIFO ordering,
  exact-FEN dedupe, durable restart recovery, requeue-from-start, terminal classification without engine
  launch, no-computation eligibility/result reads, deliberate enqueue/retry, failure with no automatic retry,
  request validation and size bounds, schema init/refusal, lock/busy coexistence, and the HTTP API contract.
- Stage 1 focused proof passed on 2026-08-20: the required queue/dedupe/enqueue/observe/terminal/eligibility/
  requeue/restart/failure/retry/lock/busy/validation/schema filter passed 40 tests (33 deselected), and the
  complete offline evaluation/analysis suite passed 73 tests. Scoped and repo-wide Ruff lint and format checks
  passed, the source-size check passed, and the workflow tests passed (10). This evidence used only fake engines
  and temporary databases and launched no engine, network, service, or live-database operation.
- Independent Stage 1 validation accepted all recorded invariants: the focused proof remained 40 passed with 33
  deselected, the complete offline evaluation/analysis suite remained 73 passed, scoped Ruff and format checks
  were clean, and the source-size check passed.
- Stage 2 API proof passed on 2026-08-21: the required API/endpoint/observe/enqueue/status/validation/bounds
  filter passed 16 tests (26 deselected), the complete offline evaluation suite passed 42 tests, scoped Ruff
  lint and format checks were clean, and the source-size check passed. The proof used temporary databases and
  fake/no engines; no live database write, live engine, download, install, or destructive injection occurred.
- Stage 2 read-only live inspection queried the existing MP-09 database without mutation: 3,157
  `analysis_result` rows and 15,731 `analysis_candidate` rows matched the fixed profile, the API read returned
  `503 evaluation_unavailable` because the live database has no evaluation schema, and database size/mtime were
  unchanged. The analysis lock file existed, but lock ownership/job activity was not inferred without acquiring
  the lock. No live write, engine run, download, install, or destructive injection was performed.
- Stage 2 live-write continuation was blocked on 2026-08-21 after the proper `AnalysisRunLock` was acquired:
  pre-write `PRAGMA integrity_check` passed; a temporary SQLite backup was created and independently checked
  (`204,771,328` bytes, SHA-256 `e0194fa8493725a37dffeed81f290e4dfd2bb846de0e6bce16d024be93662181`,
  integrity `ok`); configured Stockfish 18 matched profile
  `mp09-balanced-nodes-v2-200000`; and `initialize_evaluation_schema` failed before mutation with
  `sqlite3.OperationalError: database is locked`. Read-only post-check found no `evaluation_*` objects, the
  same 3,157/15,731 analysis counts, and integrity `ok`, but the live database SHA-256 differed from the
  retained backup. No enqueue, live evaluation, queue transition, publication, dedupe, retry, or live result
  write ran; the acquired lock was released cleanly. The backup is retained outside the repository for safe
  recovery coordination.
- Post-live-block regression proof passed on 2026-08-21: the focused API/endpoint/observe/enqueue/status/
  validation/bounds filter passed 16 tests (26 deselected). Stage 2 is accepted and Stage 3 has not started.
- Stage 3 frontend proof passed on 2026-08-21: the focused command covered 4 files and passed 37 tests; the
  frontend build passed; the Storybook build passed with the documented non-fatal Windows UV teardown assertion;
  whole-frontend lint passed; scoped Prettier, scoped `git diff --check`, and the source-size check passed.
- Stage 3 browser validation passed on 2026-08-21: all required states and controls, stale/failure presentation,
  and five completed lines were confirmed. At 480px, the context/`AnalysisPanel` was below the board with no
  horizontal overflow. The temporary Quality captures `eligible.png`, `failed.png`, `completed.png`, and
  `constrained-analysis-below-board.png` recorded these visual observations.
- Stage 4 focused proof passed on 2026-08-21: Vitest passed 4 files/31 tests; Viewer Storybook Playwright
  passed 2 tests; frontend build, Storybook build, lint, Prettier, scoped diff check, and source-size guard
  passed. Storybook build also produced the documented non-fatal Windows Storybook UV teardown assertion.
  Browser evidence showed 0px wide board/context center delta, 0px toolbar/board width delta, and no
  overlap/overflow; constrained 640/480/320 layouts stayed centered with EvalBar beside the board and context
  below. White/black orientations and neutral/queued/running/best-line accessible meter values were verified,
  along with a single polling owner and installed Base UI Meter usage. Fresh independent Quality result: PASS.
- Stage 5 closeout proof passed on 2026-08-21: fresh independent Quality validation was **PASS**. Backend focused
  proof passed 85 tests; targeted frontend proof passed 5 files/42 tests; targeted browser proof passed 7 tests;
  and the full Playwright suite passed 35 tests. Semantic and browser review confirmed deliberate Analyze/Update/
  Retry, queue/dedupe/requeue/polling/terminal/failure behavior, five ranked White-relative lines, accessible
  panel states, the Base UI EvalBar, orientation, the shared polling owner, responsive non-overlaying layout, and
  no board mutation, PV playback, automatic computation, or automatic retry. The full read-only
  `.venv\Scripts\python.exe scripts\check.py` passed every check without `--fix`. The user explicitly accepted
  the final persisted evaluation behavior and authorized closeout with “close out”.
- The coordinator-authorized live-write continuation passed on 2026-08-21 after the bounded freshness check
  resolved the stale corpus-fill note: the temporary proof command
  `PYTHONPATH="G:/ChessMoveTrainer" ./.venv/Scripts/python.exe "C:/Users/skyro/AppData/Local/Temp/opencode/mp10_live_proof.py"`
  rechecked the retained recovery copy
  (`204,771,328` bytes, SHA-256 `e0194fa8493725a37dffeed81f290e4dfd2bb846de0e6bce16d024be93662181`,
  integrity `ok`) and the live database (`integrity ok`, `3,157` results, `15,731` candidates, no
  `evaluation_*` objects, no WAL/SHM/journal sidecars). The normal `AnalysisRunLock` was acquired before
  schema/enqueue writes and released cleanly; the worker's normal lock was independently probed as
  unavailable while running and reacquired/released after completion. The genuinely missing non-terminal
  eligible FEN was `rnbqk1nr/pppp1ppp/8/4p3/4P3/2b2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 4` (24 legal moves).
  Evaluation schema initialization committed with exactly `evaluation_schema`, `evaluation_queue`, and
  `evaluation_queue_fifo`; enqueue returned `queued`, duplicate enqueue returned `already_queued` with one
  queue row, and observation saw `queued -> running -> done` with zero polling busy errors. Verified Stockfish
  identity was `Stockfish 18`, version `18`, binary SHA-256
  `c86215fa1977d53b82ed854540a4c7b025be4cd042276c85ba3de53fb9118911` under the fixed
  `mp09-balanced-nodes-v2-200000` profile (`200,000` nodes, MultiPV `5`, Threads `1`, Hash `128` MiB,
  engine WDL). The published result was eligible with five candidates, ranks `1..5`, and matching profile;
  exact counts changed to `3,158` results and `15,736` candidates (deltas `+1` and `+5`), with integrity
  `ok`. Deliberate failure/retry was exercised only on a copied temporary database: `requeued -> failed ->
  retried` and final `queued`; the copy was removed. The focused regression
  `.venv\Scripts\python.exe -m pytest backend/tests/features/evaluation -k "api or endpoint or observe or
  enqueue or status or validation or bounds" -q` passed `16` tests (`26` deselected). Stage 2 human acceptance
  was recorded on 2026-08-21 for the API/no-computation/observation behavior, with the explicit instruction,
  “yes but stop there.” Stage 2 is complete and Stage 3 has not started.
- **Stop decision (2026-08-21):** The human explicitly accepted Stage 2 and instructed, “yes but stop there.” Do
  not begin Stage 3 in this dispatch; it remains pending/not started.
- Focused pytest filters and the complete offline evaluation/analysis suite are defined per stage above.
- Frontend proof uses targeted Vitest component tests, Storybook stories for every panel and eval bar state,
  and axe/keyboard/assistive-technology checks.
- Browser proof uses the existing e2e suite: `node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts` targeted viewer specs, plus the full e2e set at closeout.
- Live proof (Stage 2 only, after explicit authorization and a free analysis lock) is bounded: read-only
  eligibility/result inspection over existing MP-09 results first, then one missing-FEN enqueue with the
  verified engine, dedupe, status observation, and deliberate retry; destructive injection only on
  temporary/copied databases.
- The ordinary full closeout command is `.venv\Scripts\python.exe scripts\check.py` without `--fix`; final
  acceptance requires it to pass. Real Stockfish and live-DB commands are never part of ordinary checks.

## Escalation boundaries

- Any different product behavior, browser-side evaluation, adjustable engine settings, cancellation model,
  automatic new/stale computation, partial-result presentation, auth, dependency, or acceptance shortcut.
- Any contested schema-ownership decision between the MP-09 analysis namespace and the MP-10-owned queue
  surface; any need to race, stop, or rewrite the running corpus-fill; any live write while the MP-09 analysis
  lock is held.
- Any need to edit the master plan before implementation acceptance, edit the roadmap, modify a completed Plan,
  absorb unrelated dirty changes or failures, inspect `Scratch/`, run `--fix`, commit, or push.

## Visible result

> A human viewing a read-only position can deliberately analyze it and see five ranked lines with scores and win/draw/loss percentages plus an accessible eval bar beside the board, with eligible results reused, stale results labelled until a deliberate update, and no cancellation, automatic retry, or board movement.
