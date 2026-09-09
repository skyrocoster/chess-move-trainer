# CLEAN-06 current analysis observation - A generated API can poll one FEN's live analysis state

> **Status:** done - Stages 1 through 4 accepted

- **Read trigger:** Read whenever CLEAN-06 implementation, validation, repair, acceptance, or closeout is approved.
- **Upstream:** [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md) is authoritative for the CLEAN order, analysis semantics, ownership, generation envelope, and exclusions; accepted [CLEAN-05](../../done/database-rebuild-clean-05/database-rebuild-clean-05.md) supplies the current FEN, result, queue, and sparse-read seams; accepted [DB-06](../../done/database-rebuild-db-06/database-rebuild-db-06.md) supplies current-result and publication invariants; [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md) supplies this Plan schema.

## Outcome

Add exactly `GET /api/analysis`, with operation ID `getAnalysis`, over the explicit rebuilt database path. A caller supplies
one complete legal `fen` query value and receives its canonical six-field FEN, the live analysis state, and at most one
complete current result. The operation is read-only, sparse-capable, generated immediately, and does not expose internal
position identity or any CLEAN-07 request behavior.

## Scope

- **Included:**
  - A package-owned FEN-facing observation capability returning immutable ordinary Python values. It canonicalizes FEN,
    looks up an existing position without resolving or creating one, reads the accepted complete current result, reads the
    live queue state, and applies `running`, `queued`, `ready`, then `not_requested` precedence.
  - The exact successful shape `{fen, state, result}`. `result` is nullable and contains only `quality`,
    `configuration_version`, `settings`, `engine_name`, `engine_version`, `terminal_kind`, and complete ordered lines
    containing `rank`, `score_kind`, `score_value`, WDL values, `pv_uci`, and `depth`.
  - Mechanical extraction/reuse of the accepted canonical-position lookup, current-result materialization, and queue-state
    validation helpers only where needed. CLEAN-05's public behavior remains unchanged and its directly invalidated proof
    is rerun.
  - A thin FastAPI adapter with required `fen`, ignored unknown query fields, strict success/error models, operation ID
    `getAnalysis`, and `get_rebuilt_database_path()` dependency use. Invalid or missing FEN is 422; missing, incompatible,
    or malformed rebuilt data is 503 with `analysis_unavailable`; unexpected failures are 500 with `unexpected_failure`.
    There is no 404 for an unseen legal FEN.
  - One curated OpenAPI operation and its checked-in HeyAPI operation, with no production frontend adoption.
- **Expected areas:**
  - `src/chess_move_trainer/database/analysis/observation.py`, bounded changes to
    `src/chess_move_trainer/database/analysis/reading.py` and `__init__.py`, and private reusable read helpers under
    `src/chess_move_trainer/database/positions/` and `src/chess_move_trainer/database/stockfish/queue.py`.
  - `tests/database/{analysis,stockfish,positions}/` and `tests/database/test_package_boundary.py`.
  - `backend/app/features/analysis_observation/`, the bounded router registration in `backend/app/main.py`, and the
    existing rebuilt-database dependency seam.
  - `backend/tests/features/analysis_observation/`, focused position-insight tests, legacy evaluation/coexistence tests,
    `scripts/api/export_contract.py`, `backend/tests/features/health/test_contract_export.py`,
    `frontend/src/api/client.ts`, `frontend/src/api/generatedSurface.test.ts`, and generator-owned output only under
    `frontend/src/api/generated/`.
  - At closeout only, this Plan's move to `docs/plans/done/database-rebuild-clean-06/` and the live status,
    next-selectable slice, and slice-results facts in the master plan.
- **Excluded:**
  - `POST /api/analysis-requests`, queue mutation, enqueueing, engine invocation, worker changes, quality-request input,
    arbitrary settings, batch/history/attempt/failure/partial/downgrade concepts, and any other CLEAN-07+ behavior.
  - Internal position IDs, queue tokens, requested qualities, timestamps, database row-existence disclosure, 404s, hidden
    writes, sidecars, compatibility/fallback adapters, or caller-side canonical/data logic.
  - Schema, index, dependency, lifecycle, old-database, legacy evaluation, route-retirement, or legacy-contract changes;
    production frontend imports; changes to accepted CLEAN-01 through CLEAN-05 meanings; completed Plan edits; unrelated
    files; broad maintenance checks; commits, pushes, branches, worktrees, stashes, or other Git operations.

## Stages

1. **complete - Add the package FEN-facing observation capability and focused proof.**
   - **Ordered actions:**
     1. Add package-owned observation request/result/state values and typed errors under `analysis/`, preserving the existing
        ID-facing `AnalysisReadRepository` behavior while exposing no private ID in the new capability.
     2. Reuse the accepted result materialization and validation. Mechanically extract the existing position lookup and live
        queue-state checks into private reusable seams where necessary, and keep CLEAN-05's response, sparse behavior, and
        precedence unchanged. Use one explicit read-only schema-v1 observation path; never call the position write resolver.
     3. Prove existing and unseen legal FENs, counter-insensitive identity, all lifecycle states, result/queue coexistence,
        complete-result and malformed-data handling, invalid input, unchanged database bytes/no sidecars, explicit paths,
        package ownership, and the directly invalidated CLEAN-05 package proof.
   - **Proof:**
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/analysis tests/database/stockfish/test_queue.py tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.
   - **Escalation boundary:** Any schema/index/version change, write during observation, new SQL owner, changed canonical
     FEN/result/queue meaning, private-ID output, or inability to share helpers without changing CLEAN-05.
   - **Breakpoint:** none.

2. **complete - Add the thin FastAPI operation and focused HTTP/coexistence proof.**
   - **Ordered actions:**
     1. Add strict `AnalysisObservationResponse`, result/line, and `{code, message}` error models under
        `backend/app/features/analysis_observation/`; use only the package capability for data and meaning.
     2. Register `GET /api/analysis` with `operation_id="getAnalysis"` and the rebuilt database dependency. Translate only
        query validation, package values, and the settled 422/503/500 statuses. Do not edit the legacy evaluation adapter.
     3. Prove the exact success shape, required/invalid FEN handling, unknown-query tolerance, sparse unseen reads,
        state/result precedence, malformed and unavailable storage, read-only behavior, no engine/enqueue call, private-ID
        exclusion, clean dependency selection, and coexistence with legacy evaluation routes.
   - **Proof:**
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/analysis_observation backend/tests/features/position_insight backend/tests/features/evaluation/test_api.py backend/tests/features/analysis/test_coexistence.py -q`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.
   - **Escalation boundary:** Any backend SQL, legacy route/configuration change, fallback/compatibility adapter, changed
     HTTP field/status/meaning, queue or worker mutation, route conflict, or production frontend import.
   - **Breakpoint:** none.

3. **complete - Curate, generate, and prove the seven-operation client surface.**
   - **Ordered actions:**
     1. Add only `"/api/analysis": {"get"}` to `APPROVED_OPERATIONS`. Update the contract proof to require exactly the
        seven clean paths and operation IDs while retaining the full served schema and excluding every legacy path.
     2. Re-export `getAnalysis` and its generated types from `frontend/src/api/client.ts`; update the generated-surface
        proof to require exactly seven operation functions and paths. Do not edit production feature modules.
     3. Run the accepted generator to update only `frontend/src/api/generated/`, then prove regeneration is byte-identical.
   - **Proof:**
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

     `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000`
     Command-level timeout: `240s`. Bash tool timeout: `300000 ms`.

     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.
   - **Escalation boundary:** Any additional curated operation, generated artifact outside
     `frontend/src/api/generated/`, new dependency, production frontend adoption, legacy operation in the contract, or
     nondeterministic generation.
   - **Breakpoint:** none.

4. **pending - Close out CLEAN-06 and advance the live master-plan slice.**
   - **Ordered actions:**
     1. Review Stages 1 through 3 against this Plan, record concise accepted proof and retained-proof invalidation, and
        confirm all CLEAN-06 acceptance conditions passed. No additional behavioral command is required.
     2. Move this Plan to `docs/plans/done/database-rebuild-clean-06/`, preserving all earlier completed Plans unchanged.
     3. Update only the live master-plan status, next-selectable slice, and slice-results facts: record CLEAN-06 accepted and
        select CLEAN-07 next. Leave all other master-plan semantics and historical records unchanged.
   - **Proof:** Manual review against `docs/PLAN_TEMPLATE.md`; no coordinator-supplied Plan checker is present. The accepted
     Stage 1, Stage 2, and Stage 3 focused proofs are the closeout evidence.
   - **Escalation boundary:** Any need to revise settled semantics, historical records, the master plan outside the named
     live facts, or the acceptance boundary.
   - **Breakpoint:** coordinator acceptance of the recorded evidence; no new product decision.

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof. The coordinator may split an oversized stage without changing the outcome or requiring a new decision.

## Progress and decisions

- **Stage 1:** complete - package observation and retained CLEAN-05 behavior passed 108 focused tests; breakpoint: none.
- **Stage 2:** complete - thin HTTP adapter and legacy coexistence proof passed 42 focused tests; breakpoint: none.
- **Stage 3:** complete - exactly seven clean operations are curated and generated with deterministic output;
  breakpoint: none.
- **Stage 4:** complete - closeout and live master-plan correction accepted; breakpoint: none.
- **Route decision:** use `GET /api/analysis` with required `fen` and operation ID `getAnalysis`; no quality or request-action
  input belongs to this observation slice.
- **Package decision:** retain the accepted ID-facing analysis reader for existing callers, add a separate FEN-facing
  observation capability, and share only mechanical canonical/result/queue read helpers so CLEAN-05's contract does not change.
- **Dependency decision:** after the first proof attempt exposed an import cycle, move shared position identity logic to
  dependency-neutral `database/_position_identity.py`; this changes no public behavior and the final proof re-established
  CLEAN-05.
- **Contract decision:** the new response is top-level `{fen, state, result}`; legacy evaluation fields and history concepts are
  not carried forward.
- **User decision:** none; exact field spelling is settled within the master-plan semantics and this focused Plan.

## Proof

- **Stage 1 accepted:** from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/analysis tests/database/stockfish/test_queue.py tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q`
  passed 108 tests in 7.88 seconds with a 180-second command timeout and `240000 ms` Bash timeout after the dependency-neutral
  import-cycle correction. It covered canonical and sparse FEN reads, immutable complete results, all lifecycle states and
  precedence, malformed storage, read-only bytes/no sidecars, queue/result coexistence, explicit paths, package boundaries,
  and retained CLEAN-05 position insight. No accepted proof remains invalidated.
- Package behavior and directly invalidated CLEAN-05 behavior: `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/analysis tests/database/stockfish/test_queue.py tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q` — command timeout `180s`; Bash tool timeout `240000 ms`.
- **Stage 1 accepted:** the package command passed 108 tests in 7.88 seconds after the dependency-direction repair. It
  covers canonical and sparse FEN reads, immutable results, lifecycle precedence, malformed storage, read-only behavior,
  queue/result coexistence, package boundaries, and the retained CLEAN-05 position-insight behavior.
- HTTP behavior and legacy coexistence: `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/analysis_observation backend/tests/features/position_insight backend/tests/features/evaluation/test_api.py backend/tests/features/analysis/test_coexistence.py -q` — command timeout `180s`; Bash tool timeout `240000 ms`.
- **Stage 2 accepted:** the HTTP command passed 42 tests in 2.84 seconds. It covers the exact response, lifecycle/result
  precedence, sparse reads, unknown queries, validation, typed 503/500 errors, dependency overrides, read-only behavior,
  private-ID exclusion, no enqueue/engine behavior, and coexistence with untouched legacy evaluation. Stage 1 proof
  remains valid because no package path or dependency changed.
- Curated seven-operation contract: `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q` — command timeout `180s`; Bash tool timeout `240000 ms`.
- HeyAPI generation: `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py` — command timeout `180s`; Bash tool timeout `240000 ms`.
- Generated surface: `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000` — command timeout `240s`; Bash tool timeout `300000 ms`.
- Byte-identical regeneration: `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check` — command timeout `180s`; Bash tool timeout `240000 ms`.
- **Stage 3 accepted:** the contract command passed 4 tests in 4.89 seconds; HeyAPI v0.99.0 generation succeeded and
  updated 4 generated files; the focused generated-surface/no-adoption proof passed 3 files and 4 tests in 2.49 seconds;
  and deterministic `--check` confirmed byte-identical regeneration across all 17 generated files. The contract,
  generation, and deterministic commands used 180-second command and `240000 ms` Bash timeouts; Vitest used a
  240-second command timeout, `300000 ms` Bash timeout, and 15000 ms test timeout. This establishes exactly seven clean
  operations, prior-operation retention, legacy exclusion, no production frontend adoption, and deterministic output.
  No package/backend path or dependency changed, so Stage 1 and Stage 2 proof remains valid.
- **Stage 4 accepted:** manual review confirmed Stages 1 through 3 and all CLEAN-06 acceptance conditions; no later edit
  invalidated retained proof, and no additional behavioral command was required. The Plan was closed and the live master
  plan advanced CLEAN-07 as the next selectable slice.
- No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, or full-suite proof is part of this
  Plan. Passing behavioral proof is retained until an affecting change invalidates it.

## Acceptance

- Exactly seven clean operations are curated and generated: health plus CLEAN-01 through CLEAN-06; no CLEAN-07 operation is
  added.
- `getAnalysis` accepts only the required public FEN observation input and returns canonical sparse/read-only lifecycle and
  current-result semantics, including running/queued coexistence precedence and no internal identifiers.
- Unseen legal FENs return 200 with `not_requested`/`null` without creating rows, sidecars, or a 404; malformed or unavailable
  rebuilt data and unexpected failures use the settled typed statuses.
- CLEAN-05 remains behaviorally correct; legacy evaluation routes remain served but uncurated; no enqueue, worker, engine,
  request, history, or production frontend behavior is introduced.
- HeyAPI regeneration is deterministic, generated output is confined to its approved directory, and unrelated changes remain
  untouched.

## Escalation boundaries

- Any new product, API, data, schema, index, dependency, lifecycle, destructive, ownership, concurrency, or acceptance
  decision.
- Any change to canonical FEN identity, complete-result/line validation, lifecycle precedence, sparse-read or read-only
  behavior, error/status meanings, operation path/method, or public fields.
- Any write during GET, queue/worker/engine mutation, private-ID or queue-token exposure, old-database use, fallback,
  compatibility adapter, legacy route edit/removal/curation, CLEAN-07+ behavior, or production frontend adoption.
- Any additional curated operation, generated artifact outside `frontend/src/api/generated/`, new dependency, nondeterministic
  generation, need to edit completed Plans, unrelated worktree cleanup, or Git operation.

## Visible result

> A user can poll one rebuilt FEN and see its current analysis state and complete result through the generated `getAnalysis()` client, without exposing database internals or request-history behavior.
