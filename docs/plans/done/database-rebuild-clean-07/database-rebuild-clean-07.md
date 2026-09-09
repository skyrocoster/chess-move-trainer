# CLEAN-07 desired analysis requests - a generated POST queues one current FEN result safely

> **Status:** done / accepted - Stages 1 through 4 complete; CLEAN-08 is next selectable

- **Read trigger:** Read before implementing, validating, repairing, accepting, or closing CLEAN-07.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) governs the
  CLEAN sequence, analysis semantics, ownership, generation envelope, and exclusions; accepted
  [CLEAN-06](../../done/database-rebuild-clean-06/database-rebuild-clean-06.md) governs the exact current
  observation shape, lifecycle precedence, result validation, HTTP errors, and generated-surface conventions;
  [database-rebuild API direction](../../../grilling-docs/database-rebuild-api-direction.md) confirms the desired-result
  request rather than action-shaped evaluation calls; [database-rebuild schema](../../../grilling-docs/database-rebuild-schema.md)
  and accepted [DB-07](../../done/database-rebuild-db-07/database-rebuild-db-07.md) govern the unchanged
  six-column queue, quality order, claim preservation, and atomic worker publication; [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md)
  supplies this Plan schema.

## Outcome

Add exactly `POST /api/analysis-requests`, with operation ID `requestAnalysis`, over the explicit rebuilt database path.
The caller supplies a public FEN and optionally requests the fixed `browser` or `tool` quality, defaulting to `browser`.
The package canonicalizes the FEN, reuses a sufficient current result, or atomically creates/reuses one canonical
position and inserts or promotes one live queue request. The HTTP response always uses the accepted CLEAN-06
`{fen, state, result}` observation, so a caller sees the current complete result while work is queued or running and
can immediately poll `GET /api/analysis` without learning database internals.

## Scope

- **Included:**
  - A package-owned desired-result request capability under `database.analysis` that validates the public FEN and
    quality, owns quality sufficiency, composes one SQLite write transaction, and returns the CLEAN-06 observation
    representation plus only private package disposition needed for HTTP status translation.
  - Fixed quality semantics: `browser < tool`; a complete higher-quality result always satisfies a lower request; an
    equal-quality result satisfies the request only when its configuration version and Stockfish version are current.
  - Sufficient-result reuse with HTTP `200` and `state: "ready"` when no live request remains; equal or higher live work
    is reused with HTTP `202` and its observed `queued` or `running` state; lower live work is raised through the
    accepted max-quality UPSERT while preserving an active claim timestamp and token; newly queued work returns `202`.
  - Purposeful creation of a legal novel canonical position. Position creation and queue insertion/promotion commit
    together or roll back together. Canonical FEN counters are returned as `0 1`.
  - The exact CLEAN-06 successful result fields: `fen`, `state`, nullable `result`, and within `result` only quality,
    configuration version, settings, engine name/version, terminal kind, and complete ordered lines.
  - Thin HTTP body/status/error translation only. The body is `{fen, quality?}`; `fen` is required, `quality` defaults
    to `browser`, unknown body fields are ignored, and known invalid FEN/quality values use `422` with `invalid_fen` or
    `invalid_quality`.
  - `503` `{code: "analysis_unavailable", ...}` for missing, incompatible, malformed, or locked rebuilt data;
    `500` `{code: "unexpected_failure", ...}` for unexpected failures; no `404` or `409` transition contract.
  - One curated OpenAPI operation and deterministic checked-in HeyAPI output, with no production frontend adoption.
- **Expected areas:**
  - `src/chess_move_trainer/database/analysis/requests.py`, bounded shared-observation changes under
    `src/chess_move_trainer/database/analysis/`, and package exports in `analysis/__init__.py`.
  - Bounded package-private transaction participants in
    `src/chess_move_trainer/database/positions/repository.py` and
    `src/chess_move_trainer/database/stockfish/queue.py`; existing public resolver, queue, worker, and publication
    behavior must remain unchanged.
  - `tests/database/analysis/test_requests.py`, focused additions to retained analysis/queue/position tests, and
    `tests/database/test_package_boundary.py` only for the new package surface or directly invalidated seams.
  - `backend/app/features/analysis_requests/`, purely mechanical serializer reuse from the observation feature if
    needed, and the bounded router registration in `backend/app/main.py`.
  - `backend/tests/features/analysis_requests/` plus directly affected CLEAN-06, position-insight, legacy evaluation,
    and coexistence tests.
  - `scripts/api/export_contract.py`,
    `backend/tests/features/health/test_contract_export.py`, `frontend/src/api/client.ts`,
    `frontend/src/api/generatedSurface.test.ts`, and generator-owned files only under
    `frontend/src/api/generated/`.
  - At closeout only, this Plan moves to `docs/plans/done/database-rebuild-clean-07/` and the master plan changes
    only its live status, next-selectable slice, and slice-results facts so CLEAN-08 is next.
- **Excluded:**
  - Stockfish worker, engine, bulk analysis, engine invocation, worker scheduling, or changes to the accepted queue
    claim/completion lifecycle; the request only enqueues or promotes live work.
  - Arbitrary engine settings, action names, retry/update/analyze contracts, batch/history/attempt/failure/partial/
    downgrade concepts, timestamps or requested-quality response fields, private IDs/tokens, or row-existence
    disclosure.
  - Schema, index, dependency, lifecycle, table-family, migration, old-database, fallback, compatibility, or
    transaction-policy changes; backend SQL or a second backend repository stack.
  - Legacy route edits, removal, or curated-contract entry. `/api/evaluation` and other legacy routes remain served and
    uncurated.
  - CLEAN-08 and all later slices, production frontend imports/adoption, frontend behavior changes, broad maintenance
    checks, completed Plan edits, unrelated work, Git operations, and any inspection or alteration of user-owned
    deleted data docs/scripts or the modified grilling record at closeout.

## Stages

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its
command, inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or
invalidated proof. The coordinator may split an oversized stage without changing the outcome or requiring a new human
decision.

1. **complete - Add package request orchestration and prove atomic/concurrent behavior.**
   - **Ordered actions:**
     1. Add the ordinary package request/result values and typed validation/storage errors under `analysis/requests.py`.
        Normalize complete legal FENs through the accepted canonicalization and normalize quality to `browser` or
        `tool`, defaulting only at the request boundary. Keep the public package free of FastAPI/Pydantic and private
        database handles.
     2. Mechanically share CLEAN-06 observation materialization and precedence where needed. Add package-private
        transaction-participant seams for canonical position resolution and queue max-quality UPSERT/live-row
        validation rather than duplicating SQL or changing `PositionRepository`/`QueueService` public behavior.
     3. Orchestrate one `BEGIN IMMEDIATE` transaction: validate the compatible schema, resolve/create the canonical
        position, read the complete current result, determine sufficiency against the fixed current profile/version,
        inspect live work, then either reuse the sufficient result or insert/promote one queue row. Preserve running
        claim identity/timestamp during promotion. Materialize the observation before commit so position creation and
        queue mutation are all-or-nothing.
     4. Add focused proof for current and stale same-quality results, higher-quality reuse, missing results, queued and
        running coexistence, Browser-to-Tool promotion, novel legal FENs and counter-insensitive identity, malformed
        inputs/storage, rollback after an injected transaction failure, repeated requests, concurrent same-quality
        requests, concurrent Browser/Tool requests, one position/one queue row, no duplicate work, and no engine call.
        Rerun directly affected CLEAN-05/06 observation and position package proof and accepted queue proof in the same
        stage.
   - **Proof:**
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/analysis/test_requests.py tests/database/analysis/test_observation.py tests/database/analysis/test_repository.py tests/database/analysis/test_transaction_composition.py tests/database/analysis/test_public_api.py tests/database/stockfish/test_queue.py tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.
   - **Escalation boundary:** Any schema/index/dependency change, second SQL owner, non-atomic position-plus-queue
     behavior, changed canonical FEN/result/quality meaning, changed queue claim or worker behavior, private-ID output,
     or inability to prove concurrent duplicate safety.
   - **Breakpoint:** none.

2. **complete - Add the thin desired-result HTTP operation and prove postconditions/coexistence.**
   - **Ordered actions:**
     1. Add `backend/app/features/analysis_requests/` body/error models. Accept strict required `fen` and optional
        strict `quality` with default `browser`, ignore unknown body fields, and expose no settings, action, queue, or
        history fields. Reuse the exact CLEAN-06 observation response models/serializer mechanically where possible.
     2. Register `POST /api/analysis-requests` with `operation_id="requestAnalysis"` and
        `get_rebuilt_database_path()`. Translate only package validation/storage values and the settled `200`/`202`/
        `422`/`503`/`500` statuses. Do not import legacy configuration or add SQL. Return `200` for a ready reused
        result; return `202` for existing live or newly queued work, retaining any current complete result in the body.
     3. Prove defaulting, unknown-field tolerance, invalid FEN/quality, exact success/error bodies, canonical counters,
        novel-FEN creation, sufficient-result reuse, live duplicate/promotion behavior, no 404/409, missing and
        incompatible storage, malformed data, dependency selection, no backend enqueue/engine invocation, and an
        immediate `GET /api/analysis` observation of the POST postcondition. Prove the new clean route coexists with
        untouched legacy evaluation routes.
   - **Proof:**
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/analysis_requests backend/tests/features/analysis_observation backend/tests/features/position_insight backend/tests/features/evaluation/test_api.py backend/tests/features/analysis/test_coexistence.py -q`
     Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.
   - **Escalation boundary:** Any backend SQL, altered response shape/status/error meaning, action/history field,
     legacy adapter change, fallback/compatibility behavior, route conflict, worker/engine invocation, or production
     frontend import.
   - **Breakpoint:** none.

3. **complete - Curate exactly eight clean operations and regenerate the client.**
   - **Ordered actions:**
     1. Add only `"/api/analysis-requests": {"post"}` to `APPROVED_OPERATIONS`. Update contract proof to require
        exactly health plus CLEAN-01 through CLEAN-07, operation ID `requestAnalysis`, the existing six clean operation
        IDs, and no legacy path in the curated contract while retaining the full served OpenAPI schema.
     2. Re-export `requestAnalysis` and its generated request/response/error types from `frontend/src/api/client.ts`.
        Update `frontend/src/api/generatedSurface.test.ts` to require exactly eight generated operation functions and
        eight curated paths, with no production feature imports or adoption.
     3. Run the accepted generator. Permit changes only in `frontend/src/api/generated/`, then prove byte-identical
        regeneration and preservation of all prior generated operations.
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
     `frontend/src/api/generated/`, new dependency, legacy operation in the contract, production frontend adoption,
     missing prior operation, or nondeterministic generation.
   - **Breakpoint:** none.

4. **complete - Close out CLEAN-07 and advance the live slice record.**
   - **Ordered actions:**
     1. Review Stages 1 through 3 against this Plan, record concise accepted proof and any invalidated retained proof,
        and confirm every CLEAN-07 acceptance condition passed. Do not add a redundant aggregate regression command.
     2. Move this Plan to `docs/plans/done/database-rebuild-clean-07/`, preserving completed Plans unchanged and
        preserving unrelated deleted data docs/scripts and the modified grilling record.
     3. Update only the live master-plan status, next-selectable slice, and slice-results facts: record CLEAN-07
        accepted and select CLEAN-08 next. Leave all other master-plan semantics unchanged.
   - **Proof:** Manual review against `docs/PLAN_TEMPLATE.md`; no automated Plan checker is present. The accepted
     Stage 1, Stage 2, and Stage 3 focused proofs are the closeout evidence. Passing behavioral proof remains retained
     until a later affecting change invalidates it.
   - **Escalation boundary:** Any need to revise settled semantics, completed Plans, historical records, master-plan
     content outside the three named live facts, generated-surface acceptance, or unrelated worktree material.
   - **Breakpoint:** coordinator acceptance of the recorded evidence; no new product decision.

## Progress and decisions

- **Stage 1:** complete - package request orchestration, atomic novel-FEN creation, quality sufficiency, queue
  promotion, and duplicate/concurrency proof passed 55 focused tests; breakpoint: none.
- **Stage 2:** complete - thin POST adapter, exact CLEAN-06 observation response, status/error translation, immediate
  GET postcondition, and legacy coexistence passed 53 focused tests; breakpoint: none.
- **Stage 3:** complete - exactly eight curated/generated clean operations, deterministic HeyAPI output, and no
  production adoption passed focused proof; breakpoint: none.
- **Stage 4:** complete - manual closeout review retained the accepted Stage 1 through Stage 3 proof, confirmed all
  CLEAN-07 acceptance conditions, and selected CLEAN-08 without a new product or semantic decision; breakpoint: none.
- **Route decision:** use `POST /api/analysis-requests` with operation ID `requestAnalysis`; no action-shaped request
  contract and no consumer adoption belong to this slice.
- **Body decision:** use `{fen, quality?}`, with required FEN, default Browser quality, ignored unknown fields, and
  known invalid values rejected with `422`.
- **Response decision:** reuse the exact CLEAN-06 `{fen,state,result}` representation. A sufficient ready result is
  `200`; live or newly queued work is `202` and may retain a nullable or complete current result.
- **Transaction decision:** one package-owned immediate write transaction must contain canonical position resolution and
  queue insertion/promotion; any failure rolls both back. Existing resolver/queue public contracts remain intact.
- **Quality decision:** Browser is below Tool; higher quality always satisfies; equal quality requires current
  configuration and Stockfish versions. No arbitrary settings are accepted.
- **User decision:** none; all product, API, data, ownership, concurrency, and acceptance decisions are settled by the
  supplied CLEAN-07 packet and upstream evidence.

## Proof

- Package, transaction, concurrency, and directly affected retained behavior:
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/analysis/test_requests.py tests/database/analysis/test_observation.py tests/database/analysis/test_repository.py tests/database/analysis/test_transaction_composition.py tests/database/analysis/test_public_api.py tests/database/stockfish/test_queue.py tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q`
  — command timeout `180s`; Bash tool timeout `240000 ms`.
- **Stage 1 accepted:** the package command passed 55 tests in 8.05 seconds. It covered canonicalization, sufficient and
  stale-result handling, queue reuse/promotion, active-claim preservation, atomic rollback, concurrent duplicate and
  mixed-quality requests, malformed/locked storage, intended side effects, package boundaries, and retained position
  insight/observation behavior. An earlier 53-test pass was superseded by added focused coverage; the final run is the
  retained proof.
- **Stage 1 re-established after Stage 2:** a non-semantic package import-boundary correction required for backend
  importability invalidated the earlier Stage 1 proof. The exact Stage 1 command then passed 55 tests in 8.31 seconds
  with the same 180-second command timeout and `240000 ms` Bash timeout; this later pass is retained.
- HTTP behavior and legacy coexistence:
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/analysis_requests backend/tests/features/analysis_observation backend/tests/features/position_insight backend/tests/features/evaluation/test_api.py backend/tests/features/analysis/test_coexistence.py -q`
  — command timeout `180s`; Bash tool timeout `240000 ms`.
- **Stage 2 accepted:** the exact HTTP command passed 53 tests in 4.35 seconds. It covers exact observation responses,
  default Browser quality, ignored body fields, 200/202 disposition behavior, immediate GET postconditions,
  promotion/claim preservation, validation, typed 503/500 errors, clean dependency selection, legacy coexistence, and
  retained clean routes.
- Exactly eight curated operations and served-schema retention:
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q`
  — command timeout `180s`; Bash tool timeout `240000 ms`.
- HeyAPI generation:
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py`
  — command timeout `180s`; Bash tool timeout `240000 ms`.
- Generated operation surface and no production adoption:
  `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000`
  — command timeout `240s`; Bash tool timeout `300000 ms`.
- Byte-identical regeneration:
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
  — command timeout `180s`; Bash tool timeout `240000 ms`.
- **Stage 3 accepted:** after one in-scope contract-test correction for the new POST method, the contract command passed
  4 tests in 5.05 seconds; HeyAPI generation succeeded and updated 4 generated files; the generated-surface/no-adoption
  proof passed 3 files and 4 tests in 2.12 seconds; and deterministic `--check` confirmed byte-identical regeneration
  across all 17 generated files. Contract, generation, and deterministic checks used 180-second command and `240000 ms`
  Bash timeouts; Vitest used a 240-second command timeout, `300000 ms` Bash timeout, and 15000 ms test timeout. This
  proves exactly eight clean operations, prior-operation retention, legacy exclusion, full served OpenAPI retention, no
  production frontend adoption, and deterministic output. Stage 1 and Stage 2 proof remains valid.
- **Stage 4 accepted:** manual review confirmed the accepted Stage 1 through Stage 3 proof and every CLEAN-07
  acceptance condition; no retained proof was invalidated, and no redundant aggregate regression was run. The Plan is
  closed as accepted and CLEAN-08 is the next selectable slice.
- No lint, formatting, broad type/build, source-size, aggregate, full-suite, or repository-hygiene command is Plan
  implementation proof. No engine or worker run is part of CLEAN-07.

## Acceptance

- Exactly one canonical position and one live queue row result from novel and concurrent duplicate requests; failed
  position-plus-queue transactions leave neither mutation.
- Browser-to-Tool promotion is duplicate-safe and preserves an active claim identity/timestamp; no lower request
  downgrades live work.
- A sufficient current result is reused with `200`/`ready`; equal live, promoted, queued, and running work returns
  `202` with the accepted live observation; a current complete result remains visible when live work coexists.
- Immediate `GET /api/analysis` observes the POST postcondition, including canonical FEN and lifecycle state.
- The response is exactly the CLEAN-06 observation contract and contains no private identifiers, queue tokens,
  timestamps, requested quality, actions, attempts, failures, or history.
- Invalid known inputs use `422`; missing/incompatible/malformed/locked rebuilt data uses `503 analysis_unavailable`;
  unexpected failures use `500 unexpected_failure`; no `404` or `409` is introduced.
- Exactly eight clean operations are curated and generated, including `requestAnalysis`; all prior clean operations
  remain present; legacy routes remain served but unpublished; generated output is deterministic; no production frontend
  module adopts the client.
- The schema, dependencies, worker/engine behavior, legacy routes, completed Plans, and unrelated user-owned material
  remain unchanged.

## Escalation boundaries

- Any new or changed schema/table/index, dependency, lifecycle, data model, transaction policy, or destructive behavior.
- Any change to public FEN canonicalization, quality ordering/sufficiency, current-result meaning, lifecycle precedence,
  queue claim/promotion semantics, atomicity, status/error meaning, response fields, or operation method/path.
- Any backend SQL, second repository stack, worker/engine invocation, arbitrary engine setting, action/history/failure
  contract, private ID/token/timestamp exposure, 404/409 transition, fallback, or compatibility adapter.
- Any legacy route/configuration/edit/removal/curation, extra curated operation, generated path outside
  `frontend/src/api/generated/`, nondeterministic generation, production frontend adoption, CLEAN-08+ behavior,
  completed Plan edit, unrelated change, or Git operation.

## Visible result

> A caller can request the current analysis for a public FEN through generated `requestAnalysis()`, receive either the
> existing complete result or a safe live queue observation, and poll `getAnalysis()` without seeing database internals.
