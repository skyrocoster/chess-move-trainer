# MP-09 Persisted Backend Stockfish Analysis - safely build and reuse exact-FEN backend analysis

> **Status:** done - Stage 5 independent validation and read-only closeout passed; final human acceptance recorded and Plan archived

- **Read trigger:** Read after the confirmed MP-09 synthesis and before every MP-09 dispatch; re-read the applicable
  stage before execution.
- **Upstream:** [confirmed MP-09 grilling synthesis](../../../grilling-docs/mp09-persisted-backend-stockfish-analysis.md),
  [static-position to analysis master plan](../../../master-plans/static-position-to-analysis.md), and accepted
  [MP-08 Plan](../../done/mp08-complete-game-traversal/mp08-complete-game-traversal.md).

## Outcome

Deliver independently versioned backend analysis storage and explicit safe operator tooling that provisions and
qualifies Stockfish 18, analyzes selected accepted game positions, and visibly reports exact-six-field-FEN reuse,
staleness, replacement, recovery, and corpus-wide preflight without adding a frontend or reading API. This matters
because later milestones can build on durable, reproducible analysis rather than repeatedly running an engine.

## Scope

- **Included:** Explicit checksum-verified ignored-local Stockfish setup with executable override; frozen
  `mp09-balanced-nodes-v1` and approved `mp09-balanced-nodes-v2` benchmark evidence; explicit analysis-schema initialization; exact-six-field-
  FEN identity; current result plus ranked Top-5 candidates; White-relative typed score and engine WDL; complete
  legal UCI PV; settings/profile eligibility; selected-game batching including ply zero; deduplication, resume,
  atomic stale replacement, run/final-failure records, bounded workers, single-run locking, hash/new-game isolation,
  watchdog/retry/circuit breaker, two-level Ctrl+C, child cleanup, extraction coexistence, and guarded opening-first
  `--all` preflight.
- **Expected areas:** `backend/app/features/analysis/**`, `backend/tests/features/analysis/**`,
  `scripts/stockfish_analysis/**`, `tests/stockfish_analysis/**`, `.gitignore`,
  `docs/benchmarks/mp09-stockfish-18-node-budget-v1.json`,
  `docs/benchmarks/mp09-stockfish-18-node-budget-v2.json`, this Plan, the confirmed synthesis, and bounded MP-09
  current-state/provenance updates in `docs/master-plans/static-position-to-analysis.md`. Touch
  `scripts/chess_com/**` or `tests/test_extract_corpus.py` only if focused coexistence proof exposes a required
  preservation defect; do not change MP-06 ownership or schema version.
- **Excluded:** Frontend and API consumption; browser Stockfish; unknown-FEN persistence; pruning; opening names,
  popularity, corpus statistics, external theory, tablebases, books, authentication, CRUD, GPU work, automatic
  analysis, full-corpus execution, dependency changes, unrelated refactors, completed Plan edits, `Scratch/`
  access, commits, pushes, and formatter execution through `--fix`.
- **Preservation:** The worktree already contains unrelated uncommitted MP-08, workflow, frontend, backend, and
  documentation changes. Record `git status --short` before and after each stage, edit only the dispatched MP-09
  paths, never reset or rewrite another change, and distinguish unrelated check failures from MP-09 failures.

## Stages

1. **accepted - offline contracts, schema/persistence foundation, safe provisioning implementation, and fake-engine lifecycle proof (ORDERED).**
   - **Ordered actions:** Implement a modular backend analysis boundary and thin explicit setup/benchmark/analyzer
     commands. Define an independent singleton analysis-schema version, active profile/settings fingerprint, exact
     FEN current-result and ranked-candidate tables, append-only batch summaries, and final per-position failures.
     Require explicit initialization and refuse missing/incompatible schemas everywhere else. Implement complete
     in-memory result validation and one-transaction parent/candidate publication without `INSERT OR REPLACE`, no
     corpus-row FK, and temporary-DB extraction coexistence proof. Implement but do not run the pinned official
     Stockfish 18 AVX2 setup path: bounded network access, provisional release/checksum verification, zip-slip-safe
     temporary extraction, executable/version verification, atomic ignored-local install, and explicit path
     override. Build deterministic fake-UCI boundaries for managed MultiPV, engine-emitted WDL, White typed scores,
     mate-zero distinction, full legal PVs, terminal/fewer-move completion, hash clear plus new-game token,
     per-worker ownership, tracked child cleanup, and a true hard watchdog that terminates node-only searches.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/analysis tests/stockfish_analysis -k "schema or setup or checksum or serialization or terminal or atomic or coexist or lifecycle or timeout" -q`;
     `.venv\Scripts\python.exe scripts\stockfish_analysis\setup_stockfish.py --help`;
     `.venv\Scripts\python.exe scripts\stockfish_analysis\benchmark_stockfish.py --help`;
     `.venv\Scripts\python.exe scripts\stockfish_analysis\analyze_positions.py --help`. All proof is offline, uses
     fake engines and temporary databases, and asserts no live DB, engine, service, download, or runtime install.
   - **Breakpoint:** independent review must accept offline setup/schema refusal, atomicity, lifecycle, and
     coexistence proof before authorizing any network, real engine, or live database effect.
   - **Escalate if:** safe setup, independent schema ownership, old-result readability, hard child cleanup, required
     result fields, or extraction preservation needs a dependency, destructive operation, or changed contract.

2. **accepted - verified Stockfish 18 setup and semantic-equivalence profile qualification (ORDERED).**
   - **Ordered actions:** After explicit network/runtime authorization, verify CPU AVX2 support and the currently
     known official `sf_18` asset, archive SHA-256
     `6f6c272ebd6ea594377715235c8a7326f75940ef4f4f856f45106028fe6ae900`, installed binary checksum, and reported
     Stockfish 18 identity; stop on any mismatch. Before engine observation, deterministically freeze the 24-FEN
     corpus fixture required by `mp09-balanced-nodes-v1`. Run clean-hash/new-game repeated MultiPV-5 trials at
     50k/100k/200k/400k candidate nodes against the repeated 800k reference. Apply, without tuning, the synthesis's
     exact repeatability, 87.5% Top-1, Top-3 overlap, typed-score, WDL-drift, 15/25-second runtime, and 30-second
     watchdog criteria. Select the lowest qualifying budget and preserve checksums, fixture/source evidence,
      metrics, one/five-worker duration, memory, and disk projections. Version 1 honestly failed because exact Top-1
      agreement did not reach 21/24 at any candidate budget; preserve that report unchanged at
      `docs/benchmarks/mp09-stockfish-18-node-budget-v1.json`. On 2026-08-20 the user approved
      `mp09-balanced-nodes-v2`: cleanly rerun the same frozen fixtures, budgets, reference, engine, and all other
      version-1 gates, replacing exact Top-1 agreement with a 24/24 semantic-equivalence gate. Each candidate best
      move must appear in the reference Top 3, match score kind, and lose no more than 20 cp and 0.020 White-WDL
      expectation from the side-to-move reference best; mate results retain the same-winner/two-ply rules. Preserve
      version-2 evidence at `docs/benchmarks/mp09-stockfish-18-node-budget-v2.json`. Prove graceful quit plus
      forced-cleanup fallback leaves no tracked child.
   - **Focused proof:** `.venv\Scripts\python.exe scripts\stockfish_analysis\setup_stockfish.py` and
     `.venv\Scripts\python.exe scripts\stockfish_analysis\benchmark_stockfish.py`, run only after their explicit
     authorization; inspect the report against the frozen rubric; rerun focused real-engine smoke with the selected
     profile and verify no child PID remains. Normal checks remain offline.
    - **Breakpoint:** automatic stop if no version-2 candidate qualifies or fixture, CPU, URL/checksum, identity, UCI options,
     PV/WDL, repeatability, watchdog, or cleanup evidence fails. Otherwise require human acceptance of the selected
     profile/report before implementing live selected-game persistence. Any rubric change requires a recorded new
     version and approval before a clean rerun.
   - **Escalate if:** another Stockfish build/release, changed quality/cost policy, tablebase/book, dependency, or
     watchdog above the accepted safety envelope would be required.

3. **in progress - selected-game operator flow, reuse/staleness, workers, run records, and recovery with a live-DB gate (ORDERED).**
   - **Ordered actions:** Accept one or more explicit accepted game UUIDs; select all plies including zero, rebuild
     strict six-field FENs, deduplicate exact FEN, and report eligible/skipped/stale/missing counts. Implement
     canonical eligibility over schema/profile, binary checksum/reported identity, node budget, MultiPV 5, Threads
     1, Hash 128 MiB, WDL and every result-affecting option. Use one top-level OS-released Windows lock, default one
     worker and ceiling six, one engine per worker, no worker SQLite writes, and short coordinator transactions.
     Preserve stale rows until a completely validated atomic overwrite. Record append-only batch summaries and
     final failures only; retry once with a fresh engine, continue after final failure, and stop dispatch after
     three consecutive final failures. First Ctrl+C stops dispatch and drains/persists active work; second closes
     and forcibly terminates tracked engines. Prove idempotent resume, interruption, stale replacement, concurrent
     invocation refusal, SQLite busy handling, and failure paths offline with fake engines and temporary/copied
     databases before requesting live access.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/analysis tests/stockfish_analysis -k "selection or dedup or eligible or stale or worker or lock or resume or retry or circuit or interrupt or busy" -q`;
     then the complete focused offline suite. At the explicit live breakpoint run
     `.venv\Scripts\python.exe scripts\stockfish_analysis\analyze_positions.py --init-schema`, followed by
     `.venv\Scripts\python.exe scripts\stockfish_analysis\analyze_positions.py --game 0007925c-5a8d-11f0-9740-f690a301000f --workers 1`
     and the same selection again to prove reuse. Inspect analysis rows and run summaries; do destructive failure
     injection only on temporary/copied databases.
   - **Breakpoint:** explicit human authorization is required immediately before analysis-schema initialization or
     any write to `data/database/chess_games.db`. After the authorized representative run, require human acceptance
     of ply-zero inclusion, exact-FEN dedup, complete Top-5/fewer/terminal shape, reuse, stale safety, run/failure
     history, interruption/resume evidence, and no leaked engine child before Stage 4.
   - **Escalate if:** live schema creation is not isolated, selected-game validity is ambiguous, another writer
     cannot fail safely, or correct Windows interruption/cleanup cannot be proven without broader process control.

4. **accepted - opening-first corpus-wide preflight and explicit confirmation safety, without a full run (ORDERED).**
   - **Ordered actions:** Add `--all` only after selected-game acceptance. Deduplicate by exact FEN and order by its
     minimum corpus ply then deterministic FEN tie-breaker. Perform a non-mutating preflight that prints
     eligible/skipped/stale/missing counts, active engine/profile/settings, worker count and total hash memory, disk
     projection, projected duration, watchdog, and lock implications before confirmation. Require interactive
     confirmation, add an explicit noninteractive confirmation flag, and provide preflight-only operation. Prove
     refusal, EOF, invalid confirmation, preflight failure, and preflight-only are non-mutating. Do not confirm or
     run the full current corpus in MP-09.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/analysis tests/stockfish_analysis -k "all or opening or preflight or projection or confirmation" -q` and, against the live database read-only after
     authorization, `.venv\Scripts\python.exe scripts\stockfish_analysis\analyze_positions.py --all --preflight-only --workers 5`.
   - **Breakpoint:** human review accepts opening-first ordering, counts, settings/profile, 640 MiB engine-hash
     projection, disk/duration estimates, confirmation wording, and non-mutation. Full-corpus confirmation remains
     outside MP-09 acceptance.
   - **Escalate if:** reliable counts/projections require mutation, queue identity differs from exact FEN, opening
     order cannot be established, or acceptance would require a full-corpus run.

5. **done - independent validation, read-only closeout, delivery records, and human acceptance (ORDERED).**
   - **Ordered actions:** Run fresh independent validation across provisioning safety, schema isolation,
     serialization, exact-FEN selection, eligibility, atomic stale replacement, resume/failures/interruption,
     extraction coexistence, real-engine benchmark/smoke, representative live selected-game evidence, and
     non-mutating `--all` preflight. Resolve only coordinator-authorized in-scope defects. Update this Plan's
     progress/proof, the master plan's bounded MP-09 accepted current state, and the synthesis provenance without
     changing completed Plans or MP-10 onward contracts. Obtain explicit human acceptance, move the complete Plan
     directory from active to `docs/plans/done/`, and repair links atomically. Never commit or push.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/analysis tests/stockfish_analysis -q`;
     `.venv\Scripts\python.exe scripts\check.py` in read-only mode without `--fix`; documentation link/template
     review; `git diff --check` on MP-09 paths; final `git status --short` and scoped diff review proving unrelated
     dirty work is preserved. Real Stockfish and live-DB commands are not part of ordinary checks and are cited
     from their separately authorized stage evidence rather than rerun automatically.
   - **Breakpoint:** fresh independent validation must pass and the human must explicitly accept the persisted
     selected-game result, reuse/recovery behavior, benchmark/profile, and corpus-wide preflight before archival.
   - **Escalate if:** validation requires widening scope, suppressing an unrelated failure, using `--fix`, rerunning
     the full corpus, changing acceptance, or rewriting historical records.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the outcome. The five-stage shape keeps real external effects, live database mutation, corpus-wide behavior, and
final independent acceptance behind distinct evidence gates; Plan authoring itself is not an implementation stage.

## Progress and decisions

- **Stage 1:** accepted - coordinator-split Stage 1A delivered the independently versioned exact-FEN schema,
  validation, atomic persistence, explicit initialization/refusal, run/failure records, and extraction coexistence.
  Stage 1B delivered the offline pinned provisioning implementation and managed fake-engine lifecycle boundary.
  After one exact lifecycle repair, fresh final Quality validation passed all 42 focused tests, Ruff, format, CLI
  help, and size proof. No network, real engine, service, runtime install, or live-database action ran.
- **Stage 2:** accepted - the authorized setup verified the pinned Stockfish 18 archive, checksum, AVX2 support, and
  real-engine lifecycle. The frozen 24-FEN version-1 benchmark completed, but exact Top-1 agreement was 16/24 at
  50k, 15/24 at 100k, 17/24 at 200k, and 16/24 at 400k versus the required 21/24, so no budget qualified. Every
  repeatability, Top-3, score, WDL, runtime, watchdog, PV, and cleanup gate passed. The honest failed report is
  retained. On 2026-08-20 the user selected the recommended strict semantic-equivalence option: all 24 fixtures
  must choose a reference Top-3 move within 20 cp and 0.020 WDL expectation of the reference best, while every
  other version-1 gate remained. The clean rerun selected `mp09-balanced-nodes-v2-200000`: semantic equivalence
  passed 24/24, Top-3 overlap was 0.833333, cp drift median/p90 was 4/13, candidate/reference maximums were
  0.406/2.094 seconds, and the watchdog retained 27.906 seconds of margin. Fresh Quality validation independently
  recomputed both reports and accepted the bounded real-engine smoke. The later live authorization below remained
  limited to the exact representative Stage 3 proof.
- **Stage 2 acceptance recorded before Stage 3 execution:** on 2026-08-20 the user explicitly accepted
  `mp09-balanced-nodes-v2-200000`, with strict 24/24 semantic equivalence and evidence at
  `docs/benchmarks/mp09-stockfish-18-node-budget-v2.json`. This acceptance authorizes offline Stage 3 implementation
  and proof only. A later explicit authorization is recorded above for only the exact Stage 3 live breakpoint proof;
  broader live effects remain unauthorized.
- **Stage 3:** accepted - offline selected-game selection, exact-FEN deduplication, eligibility/reuse/staleness,
  bounded worker orchestration, run/failure records, interruption/recovery, lock/busy/failure safety, and temporary
  database proof are implemented and accepted. On 2026-08-20 the user
  explicitly authorized only the exact live breakpoint proof: initialize the independent analysis schema in
  `data/database/chess_games.db`, run selected game
  `0007925c-5a8d-11f0-9740-f690a301000f` twice with `--workers 1`, the accepted
  `mp09-balanced-nodes-v2-200000` profile, Stockfish 18, and its canonical 200,000-node settings, then inspect
  rows and run history read-only. This authorization excludes broader games, destructive failure injection on the
  live database, and unrelated writes. The authorized proof is complete. On 2026-08-20 the user explicitly
  accepted Stage 3's selected-game persistence, reuse, recovery, and live non-leak evidence, and authorized Stage 4
  implementation and read-only preflight only. Full-corpus execution remains excluded.
- **Stage 4:** accepted - on 2026-08-20 the user accepted the bounded opening-first preflight and its safeguards. The
  queue is ordered by minimum corpus ply ascending with an exact six-field FEN ascending tie-breaker. The preflight
  found 515,515 unique exact FENs: 83 eligible, 83 skipped, 0 stale, and 515,432 missing. It used the accepted
  Stockfish 18 profile `mp09-balanced-nodes-v2-200000` with binary SHA-256
  `c86215fa1977d53b82ed854540a4c7b025be4cd042276c85ba3de53fb9118911`, 200,000 nodes, MultiPV 5, Threads 1,
  Hash 128 MiB, and WDL enabled. Five workers projected 640 MiB total engine hash, 702,518,066 bytes (669.97 MiB)
  of result storage, and 33,759.8 seconds (9.38 hours) of duration, with a 30-second watchdog and a non-acquired
  top-level lock implication. The user accepted the strictly read-only preflight message, the warning that a
  confirmed operation writes full-corpus results, the exact interactive `ANALYZE ALL` confirmation, explicit
  `--confirm-all` noninteractive confirmation, and `--preflight-only`. Refusal, EOF, invalid confirmation, and
  preflight failure remain non-mutating safeguards. Live database SHA-256, size, mtime, analysis row counts (83
  results, 381 candidates, 2 runs, 0 failures), and lock state were identical before and after; no Stockfish
  process remained. No confirmation was supplied and no corpus analysis ran; full-corpus execution remains
  excluded.
- **Stage 5:** done - on 2026-08-20, independent validation passed all MP-09 scope checks across provisioning safety,
  schema isolation, serialization, exact-FEN selection, eligibility, atomic stale replacement, resume/failures/
  interruption, extraction coexistence, real-engine benchmark/smoke, representative live selected-game evidence,
  and non-mutating `--all` preflight. The initial read-only full check reported one unrelated Sol workflow-contract
  blocker. The user authorized its bounded correction and instructed that only the failed workflow-contract
  validation be rerun; that narrow fresh validation passed. The entire full check was not rerun after the repair.
  The user gave final human acceptance for MP-09 and authorized archiving; this complete feature directory was moved
  atomically to `docs/plans/done/mp09-persisted-backend-stockfish-analysis/`, with no `handoff.md` present to remove.

## Proof

- Offline deterministic proof uses fake UCI engines and temporary databases; it covers setup without networking,
  explicit schema refusal/init, typed score/WDL/full-PV serialization, terminal/fewer-move outcomes, hash/new-game
  isolation, eligibility, atomic stale replacement, workers/locking, timeout/retry/circuit breaker, both Ctrl+C
  levels, child cleanup, extraction preservation, and confirmation non-mutation.
- Stage 1A focused proof passed on 2026-08-20: 12 backend analysis tests, 3 schema-CLI tests, scoped Ruff and format
  checks, and the repository size check. Fresh Quality review independently accepted schema isolation, canonical
  identity/profile handling, typed result validation, atomic rollback, append-only records, and extraction
  coexistence. This evidence used only temporary databases and launched no engine or network operation.
- Stage 1B focused proof passed on 2026-08-20, followed by fresh final Quality validation after one exact
  `asyncio.Event` exit-poll repair: all 42 Stage 1 tests, scoped Ruff and format checks, all three CLI help commands,
  and the repository size check passed. Quality accepted checksum-first safe provisioning, managed MultiPV/WDL/PV
  conversion, hash/new-game isolation, bounded tracked-child watchdog cleanup, and non-mutating offline behavior.
- Stage 2 setup and the frozen `mp09-balanced-nodes-v1` run completed on 2026-08-20. The official archive checksum
  matched, the binary reported Stockfish 18, all 45 focused tests passed, and 240 benchmark observations completed
  without a leaked child or live-database mutation. No candidate met the exact Top-1 gate, so the report records no
  selected profile and the then-planned Stage 3 did not start under that failed gate.
- The user-approved `mp09-balanced-nodes-v2` clean rerun completed on 2026-08-20 and selected 200,000 nodes under
  the strict 24/24 semantic-equivalence gate. Its 240 fresh observations project 46.89 hours with one worker or
  9.38 hours with five for 515,515 exact FENs, with about 669.97 MiB projected result storage. Fresh Quality
  validation passed all 50 focused tests, independently recomputed the unchanged v1 and qualified v2 reports,
  verified the installed binary and one bounded real result, and observed no leaked process or live-database write.
- Stage 3 offline implementation proof passed on 2026-08-20: the required focused selection/deduplication,
  eligibility/staleness, worker, lock, resume, retry, circuit-breaker, interruption, and busy set passed 11 tests;
  the complete offline analysis and operator suite passed 58 tests. Scoped Ruff and format checks passed. These
  tests used fake engines and temporary databases only; the live representative operator proof was pending before
  this dispatch.
- Stage 3 live proof completed on 2026-08-20 under the narrowly recorded authorization. The selected game was
  accepted and structurally valid with 83 occurrences at plies 0-82 and no gaps; it produced 83 distinct exact
  six-field FENs, including a persisted ply-zero starting position, so no live deduplication collision occurred.
  `analyze_positions.py --db data/database/chess_games.db --engine
  data/stockfish/stockfish-windows-x86-64-avx2.exe --profile-id mp09-balanced-nodes-v2-200000 --init-schema`
  initialized schema version 1. The same command shape with `--workers 1 --watchdog 30 --shutdown-timeout 5
  --game 0007925c-5a8d-11f0-9740-f690a301000f` returned run 1 `success` (selected 83, missing 83, completed
  83, failed 0), then run 2 `success` (selected 83, eligible/skipped 83, completed 0, failed 0), proving reuse.
  Read-only inspection found 83 current results, 381 candidate rows, no orphans, no failures, two append-only
  success runs, and one profile/settings identity: `mp09-balanced-nodes-v2-200000`, Stockfish 18, the verified
  binary checksum, 200,000 nodes, MultiPV 5, Threads 1, Hash 128 MiB, and WDL enabled. Result shape was 73
  complete Top-5 roots, 1/2/3/4-candidate roots of 5/2/1/1, and 1 terminal checkmate root; all 83 results and
  381 candidates passed model validation with complete legal PVs. No Stockfish task remained after the live
  execution.
  No destructive live failure injection or broader-game operation ran.
- The post-live bounded offline proof passed: 11 focused selection, deduplication, eligibility, staleness, worker,
  lock, resume, retry, circuit-breaker, interruption, and busy tests passed (47 deselected).
- Stage 4 offline proof passed on 2026-08-20: the required opening/all/preflight/projection/confirmation filter
  passed 8 tests, the complete focused offline analysis suite passed 64 tests, scoped Ruff and format checks passed,
  and the source-size check passed. The proof covers exact-FEN opening-first ordering, counts and projections,
  refusal/EOF/invalid-confirmation/preflight-failure/preflight-only non-mutation, and the 640 MiB five-worker hash
  projection using only temporary databases and no full-corpus execution.
- Stage 4 live read-only preflight completed on 2026-08-20 with explicit database, verified engine, accepted profile,
  `--all --preflight-only --workers 5`. It found 515,515 unique exact FENs: 83 eligible/skipped, 0 stale, and
  515,432 missing. It reported Stockfish 18, checksum
  `c86215fa1977d53b82ed854540a4c7b025be4cd042276c85ba3de53fb9118911`, profile
  `mp09-balanced-nodes-v2-200000`, 640 MiB total hash, 702,518,066 bytes (669.97 MiB) projected storage,
  33,759.8 seconds (9.38 hours) projected duration at five workers, a 30-second watchdog, and a non-acquired
  top-level lock implication. Database SHA-256, size, mtime, analysis row counts (83 results, 381 candidates, 2
  runs, 0 failures), and lock existence were identical before and after; no Stockfish process remained. No
  confirmation was supplied and no corpus analysis ran. On 2026-08-20 the user accepted the opening-first ordering,
  counts, accepted profile/settings, 640 MiB hash projection, storage and duration estimates, confirmation wording
  and safeguards, live non-mutation, and continued exclusion of full-corpus execution.
- Stage 5 closeout completed on 2026-08-20: independent validation passed all MP-09 scope checks. The initial
  read-only full check reported one unrelated Sol workflow-contract blocker; the user authorized its bounded
  correction and instructed that only the failed workflow-contract validation be rerun, and that narrow fresh
  validation passed. The entire full check was not rerun after the repair. The user then gave final human acceptance
  for MP-09 and authorized archival.
- Separately authorized real-engine proof verifies the provisional official Stockfish 18 AVX2 facts, frozen
  benchmark/profile qualification, watchdog margin, proof metadata, and process cleanup.
- Separately authorized live proof is complete for only the independent schema, representative game, reuse run, and
  read-only durable inspection recorded above; it did not execute `--all` or destructive failure injection.
- The ordinary full closeout command is `.venv\Scripts\python.exe scripts\check.py` without `--fix`; this closeout
  used the already-recorded initial full check and the explicitly instructed narrow workflow-contract rerun instead
  of rerunning the entire full suite after the bounded unrelated repair. The scoped documentation link/template review
  passed: MP-09 links resolve, the archived Plan has the required headings and done status, and no active MP-09
  reference or directory remains. Scoped `git diff --check` passed with no whitespace diagnostics; the untracked
  archived Plan and MP-09 synthesis no-index checks returned the expected status 1 for content differences and no
  whitespace diagnostics. Ordinary checks remain offline and never download or launch Stockfish.

## Escalation boundaries

- Any different product, frontend/API behavior, engine release/build, official asset/checksum, benchmark rubric,
  result identity, settings eligibility, schema ownership, dependency, destructive operation, process privilege,
  full-corpus execution, or acceptance shortcut.
- Missing AVX2 support; unavailable or changed official URL/checksum; reported identity other than the verified
  expected Stockfish 18 identity; absent Clear Hash/UCI_ShowWDL/MultiPV/proof fields; no qualifying node budget; or
  benchmark/watchdog/child-cleanup failure.
- Inability to keep a stale result readable through an atomic replacement, serialize SQLite writes safely, retain
  analysis through corpus extraction/removal, or enforce one top-level run and bounded workers on Windows.
- Any need to inspect `Scratch/`, modify a completed Plan, absorb unrelated dirty changes/failures, run `--fix`,
  commit, or push.

## Visible result

> An operator can explicitly analyze every position in a selected stored game once, rerun it to see safe exact-FEN reuse, and inspect a guarded opening-first full-corpus preflight without exposing analysis in the UI or API.
