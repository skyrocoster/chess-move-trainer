# CLEAN-09 preferred-move interval overlay - A generated PUT can configure a dated outgoing choice

> **Status:** complete - Stages 1 through 4 accepted; CLEAN-09 closed

- **Read trigger:** Read before implementing, validating, repairing, accepting, or closing CLEAN-09.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) governs the
  CLEAN sequence, ownership, generation envelope, coexistence, and exclusions; accepted
  [CLEAN-08](../../done/database-rebuild-clean-08/database-rebuild-clean-08.md) governs the retained preferred-move
  timeline, canonical FEN, error, and generated-client conventions; accepted
  [DB-05](../../done/database-rebuild-db-05/database-rebuild-db-05.md) and
  [SETUP-01](../../done/database-rebuild-setup-01/database-rebuild-setup-01.md) govern preferred-period storage,
  legal moves, half-open dates, normalization, canonical position writes, and accepted setup data; the confirmed
  [database-rebuild API direction](../../../grilling-docs/database-rebuild-api-direction.md) governs outgoing-move
  meaning, novel legal positions, tagged values, and mutation ownership; [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md)
  supplies this Plan schema. The retained CLEAN-09 assessment/research settles the exact mutation contract below.

## Outcome

Add exactly `PUT /api/preferred-moves`, with operation ID `putPreferredMoves`, over the explicit rebuilt database path.
The caller supplies a complete legal public parent FEN, a strict half-open calendar-date interval, and either a legal
outgoing UCI move or explicit no preference. The package atomically canonicalizes the parent, purposefully creates a
novel position when needed, overlays and normalizes the current schedule under the writer lock, and returns the
canonical applied interval, preference, and complete normalized configured schedule. The generated client is updated
immediately while `GET /api/preferred-moves`, singular legacy routes, and production frontend modules remain unchanged.

The successful JSON shape is:

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "effective_from": "2026-01-01",
  "effective_until": null,
  "preference": {"kind": "no_preference"},
  "periods": [
    {
      "effective_from": "2026-01-01",
      "effective_until": null,
      "preference": {"kind": "no_preference"}
    }
  ]
}
```

`periods` contains the complete normalized configured schedule for the canonical parent FEN. It has no derived
`unconfigured` gaps, private IDs, SAN, child position, repertoire line, or history marker.

## Settled contract

- The request body is exactly `{fen, effective_from, effective_until?, preference}`. All mutation inputs are in the
  body; there are no mutation query aliases. `effective_until` omitted and `effective_until: null` both mean an
  exclusive open-ended interval, and the response always emits the field explicitly.
- FEN is a complete legal six-field FEN. Placement, side to move, castling, and legal en-passant define identity;
  counters are validated and the response uses counters `0 1`.
- Dates are strict `YYYY-MM-DD` literals. `effective_from` is required and a finite end must be later than the start.
- The only request preferences are `{kind: "move", uci: "..."}` and `{kind: "no_preference"}`. `unconfigured` is
  derived read state and is rejected by PUT. A no-preference value cannot carry `uci`.
- Top-level and nested unknown body fields are ignored; known invalid values and combinations are rejected. Ordinary
  missing or strict-type body-shape failures retain the established FastAPI 422 validation behavior.
- Successful mutation is always `200 OK`, including a semantic repeat of the same PUT. There is no `changed` flag or
  append-only event semantics; repeats return the same normalized result and do not create duplicate periods.
- Semantic 422 codes are `invalid_fen`, `invalid_effective_from`, `invalid_effective_until`, `invalid_window`,
  `invalid_preference`, `invalid_uci`, and `illegal_move`. Their stable messages are respectively `FEN is invalid`,
  `effective_from must be a literal YYYY-MM-DD date`, `effective_until must be a literal YYYY-MM-DD date`,
  `effective_until must be later than effective_from`, `Preference is invalid`, `UCI move is invalid`, and
  `Move is illegal from the parent FEN`.
- Missing, incompatible, malformed, unreadable, or lock-blocked storage is `503` with
  `{code: "preferred_moves_unavailable", message: "Preferred moves unavailable"}`. Unexpected failures are `500`
  with `{code: "unexpected_failure", message: "Unable to update preferred moves"}`. No `404`, `409`, or `423` is
  introduced.

## Scope

- **Included:**
  - A package-owned complete-FEN mutation request/result capability under
    `src/chess_move_trainer/database/preferred_moves/`, using ordinary Python values only.
  - Reuse of `Preference`, `NormalizedPeriod`, `set_preference`, `normalize_periods`, the existing canonical position
    unit of work, and the existing `BEGIN IMMEDIATE` replacement/verification transaction.
  - Legal novel parent FEN creation, legal outgoing UCI validation, explicit no-preference persistence, strict date
    validation, normalized split/merge/overlap behavior, semantic idempotence, rollback, and serialized concurrency.
  - One thin plural FastAPI PUT adapter, exact response/error models, immediate GET timeline/position-insight proof, and
    coexistence with all singular legacy preferred-move routes.
  - Exactly one additional curated OpenAPI operation, checked-in HeyAPI regeneration, deterministic output, retention of
    the nine existing clean operations, legacy exclusion, and no production frontend adoption.
- **Expected areas:**
  - `src/chess_move_trainer/database/preferred_moves/mutations.py`, bounded changes to
    `preferred_moves/repository.py` and `preferred_moves/__init__.py`.
  - `tests/database/preferred_moves/test_mutations.py`, `test_public_api.py`, and the directly affected retained
    range/repository/concurrency/timeline/setup tests; `tests/database/positions/test_insight.py` only as retained
    direct proof for the shared preference read seam.
  - `backend/app/features/preferred_moves/api_schemas.py` and `router.py`; `backend/app/main.py` only if the existing
    plural router registration unexpectedly differs, which is an escalation rather than a planned edit.
  - `backend/tests/features/preferred_moves/` focused PUT coverage, plus retained plural, singular, and
    `position_insight` HTTP proof.
  - `scripts/api/export_contract.py`, `backend/tests/features/health/test_contract_export.py`,
    `frontend/src/api/client.ts`, `frontend/src/api/generatedSurface.test.ts`, and generator-owned files only under
    `frontend/src/api/generated/`.
  - At closeout only, this Plan moves to `docs/plans/done/database-rebuild-clean-09/` and the live master plan changes
    only its status, next-selectable slice, and slice-results facts so CLEAN-10 is next.
- **Excluded:**
  - DELETE/CLEAN-10, any frontend adoption or calendar UI, repertoire/authored lines, child-position creation,
    history/audit/change tracking, worker/engine behavior, and all consumer migration.
  - Schema, table, column, index, trigger, schema-version, dependency, lifecycle, old-database, migration, fallback,
    compatibility, or transaction-policy changes; no second backend SQL/repository stack.
  - Caller-side date arithmetic, gap/split/merge/overlap handling, SAN, private IDs, generic query language, or a
    `changed`/event response field.
  - Legacy route edits, removal, configuration changes, or curated-contract entry.
  - Changes to completed Plans, SETUP-01 inference meaning, CLEAN-05 read meaning, CLEAN-08 timeline meaning, unrelated
    worktree material, broad maintenance checks, commits, pushes, branches, worktrees, stashes, or other Git operations.

## Stages

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof. The coordinator may split an oversized stage without changing the outcome or requiring a new human decision.

### 1. **complete - Add the package mutation capability and prove storage behavior.**

**Ordered actions**

1. Add ordinary `PreferredMoveMutationRequest`, `PreferredMoveMutationResult`, and `put_preferred_move` values/function
   under `preferred_moves/mutations.py`. Canonicalize complete FENs, validate strict dates before any write, map only
   move/no-preference values, and expose the complete normalized configured schedule.
2. Preserve the accepted DB-05 four-field `PreferredMoveRepository.set` contract while adding the smallest package-owned
   seam for complete-FEN mutation. Reuse `PreferredMoveRepository._amend` and `ranges.set_preference`; do not create a
   second SQL owner.
3. Keep `BEGIN IMMEDIATE` before schedule read. Resolve/create the canonical parent, validate the outgoing move against
   that canonical position, read the fresh locked schedule, overlay it, replace and verify normalized rows, then commit
   the position and schedule together. Roll back on every failure or interruption.
4. Pass the canonical position into the write-side schedule load so malformed persisted UCI is unavailable rather than
   silently preserved. Keep `PositionInsight._read_preference` and `PreferredMoveTimelineRepository.read` meanings
   unchanged.
5. Add package proof for canonical counters/legal en-passant identity, legal novel FENs and one position row, strict
   intervals, move/no-preference values, invalid UCI versus illegal move, overlay normalization, repeat idempotence,
   rollback, malformed storage, lock behavior, and competing writers. Update only focused public-export expectations.

**Proof**

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_mutations.py tests/database/preferred_moves/test_range_semantics.py tests/database/preferred_moves/test_repository.py tests/database/preferred_moves/test_concurrency.py tests/database/preferred_moves/test_timeline.py tests/database/preferred_moves/test_setup.py tests/database/positions/test_insight.py tests/database/preferred_moves/test_public_api.py -q
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 90 .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q -k "preferred_moves or position_service or lower_level_database"
```

Command-level timeout: `90s`. Bash tool timeout: `120000 ms`.

**Escalation boundary:** Any schema or dependency change, second SQL owner, changed canonical identity/date/tag
meaning, write-side position behavior outside the purposeful parent creation, changed lock policy, or inability to
prove rollback and latest-schedule serialization.

**Breakpoint:** none.

### 2. **complete - Add the thin clean PUT and prove HTTP behavior.**

**Ordered actions**

1. Extend `backend/app/features/preferred_moves/api_schemas.py` with an ignored-extra request model, discriminated
   move/no-preference input, normalized-period response, mutation response, and the settled typed mutation errors.
   Keep output models strict and exclude `unconfigured` from stored mutation periods.
2. Add `PUT /api/preferred-moves` with `operation_id="putPreferredMoves"`, the existing
   `get_rebuilt_database_path()` dependency, and no SQL or backend calendar arithmetic. Translate only package values
   and the settled 200/422/503/500 outcomes.
3. Add focused HTTP proof for exact body spelling, null/omitted end, ignored unknowns, known invalid combinations,
   canonical response, normalized schedule, idempotent repeat, novel-FEN creation, lock/malformed/missing storage,
   safe unexpected failure, immediate GET timeline and CLEAN-05 insight postconditions, and unchanged singular legacy
   route registration. Do not edit the singular feature.

**Proof**

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_moves backend/tests/features/preferred_move backend/tests/features/position_insight -q
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Any backend SQL, changed response/status/error/message meaning, query alias, hidden write,
404/409/423 behavior, route conflict, legacy edit, fallback/compatibility behavior, or production frontend import.

**Breakpoint:** none.

### 3. **complete - Curate PUT beside GET and regenerate the client.**

**Ordered actions**

1. Change only the curated allow-list and contract assertions so `/api/preferred-moves` contains `get` and `put`, the
   contract has nine paths and ten operation IDs, all nine prior operations remain, and no legacy path enters.
2. Re-export `putPreferredMoves` and its generated request/response/error types from `frontend/src/api/client.ts`.
   Update `frontend/src/api/generatedSurface.test.ts` to require ten operation functions and both preferred-moves
   methods. Do not edit production frontend modules.
3. Run the accepted generator, permit changes only under `frontend/src/api/generated/`, and prove retained operations,
   legacy exclusion, no production adoption, and byte-identical regeneration.

**Proof**

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000
```

Command-level timeout: `240s`. Bash tool timeout: `300000 ms`; Vitest test timeout: `15000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Any additional operation or path, missing prior operation, legacy operation in the curated
contract, generated artifact outside `frontend/src/api/generated/`, new dependency, production adoption, or
nondeterministic output.

**Breakpoint:** none.

### 4. **complete - Close CLEAN-09 and advance the live slice record.**

**Ordered actions**

1. Review Stages 1 through 3 against this Plan, record concise accepted proof and any invalidated retained proof, and
   confirm every CLEAN-09 acceptance condition. Do not add a redundant aggregate regression command.
2. Move this Plan to `docs/plans/done/database-rebuild-clean-09/`, preserving completed Plans and unrelated baseline
   material unchanged.
3. Update only the live master-plan status, next-selectable slice, and slice-results facts: record CLEAN-09 accepted and
   select CLEAN-10 next. Leave all other master-plan semantics unchanged.

**Proof:** Manual review against `docs/PLAN_TEMPLATE.md`; no automated Plan checker is present. Stages 1 through 3
focused behavioral proof is the retained implementation evidence.

**Escalation boundary:** Any need to revise settled contract, completed or historical records, master-plan content
outside the three named live facts, generated-surface acceptance, unrelated material, or any Git operation.

**Breakpoint:** coordinator acceptance of the recorded evidence; no new product decision.

## Progress and decisions

- **Stage 1:** complete - package mutation, normalized persistence, rollback, concurrency, and retained read proof passed;
  breakpoint: none.
- **Stage 2:** complete - thin PUT adapter, exact response/status mapping, immediate GET/insight proof, and legacy
  coexistence passed 69 focused tests; breakpoint: none.
- **Stage 3:** complete - nine curated paths, ten generated operations, deterministic HeyAPI output, and no production
  adoption passed focused proof; breakpoint: none.
- **Stage 4:** complete - manual closeout review confirmed the acceptance conditions, retained proof, and unchanged
  settled decisions; CLEAN-09 moved to done and CLEAN-10 advanced as next selectable; breakpoint: none.
- **Route decision:** use `PUT /api/preferred-moves` with operation ID `putPreferredMoves`; retain `GET` on the same plural path and all singular legacy routes.
- **Mutation decision:** all FEN, dates, and preference values are in the body; omitted/null end is open-ended; the package returns the full normalized configured schedule.
- **Transaction decision:** one package-owned `BEGIN IMMEDIATE` transaction resolves the parent, reads the fresh schedule, overlays, verifies, and commits or rolls back as one unit.
- **Generation decision:** the curated contract grows from nine operations across nine paths to ten operations across nine paths; DELETE is not added.
- **Retained-proof decision:** CLEAN-05 insight and CLEAN-08 timeline proof are rerun in the focused Stage 1/2 commands because the shared preferred-move write seam is touched; no read meaning changes.
- **User decision:** none; product, API, data, ownership, concurrency, and acceptance decisions are settled by the packet and assessment.

## Proof

- Package mutation, retained ranges/repository/concurrency/timeline/setup/insight behavior: the exact Stage 1 package command above, with `180s` command and `240000 ms` Bash timeouts.
- Package/source ownership and lower-layer boundaries: the exact Stage 1 boundary command above, with `90s` command and `120000 ms` Bash timeouts.
- **Stage 1 accepted:** the package command passed 105 tests in 11.74 seconds with a 180-second command timeout and
  `240000 ms` Bash timeout; the boundary command passed 6 tests with 11 deselected in 0.53 seconds with a 90-second
  command timeout and `120000 ms` Bash timeout. They cover canonical identity, strict dates and tagged values, legal UCI,
  normalization, complete response schedules, idempotence, rollback, malformed/locked storage, serialized concurrency,
  retained timeline/insight behavior, public exports, and package/source boundaries. An earlier 103-test pass was
  superseded after added focused coverage; the final commands are retained.
- Thin HTTP PUT, immediate GET/insight postconditions, lock/storage mapping, and legacy coexistence: the exact Stage 2 command above, with `180s` command and `240000 ms` Bash timeouts.
- **Stage 2 accepted:** the exact HTTP command passed 69 tests in 24.56 seconds. It covers the PUT body and response,
  normalized persistence, semantic and storage errors, lock handling, concurrent observability, immediate plural GET and
  CLEAN-05 insight visibility, dependency override, private-data exclusion, and singular legacy coexistence. Stage 1
  proof remains valid because no package path or dependency changed.
- Nine-path/ten-operation curated contract: the exact Stage 3 contract command above, with `180s` command and `240000 ms` Bash timeout.
- Checked-in HeyAPI generation: the exact Stage 3 generator command above, with `180s` command and `240000 ms` Bash timeout.
- Generated operation surface and no production adoption: the exact Stage 3 Vitest command above, with `240s` command, `300000 ms` Bash timeout, and `15000 ms` test timeout.
- Byte-identical regeneration: the exact Stage 3 generator `--check` command above, with `180s` command and `240000 ms` Bash timeout.
- **Stage 3 accepted:** the contract command passed 4 tests in 13.55 seconds; generation succeeded and refreshed 4
  generated files in 341 ms; the generated-surface/no-adoption proof passed 3 files and 5 tests in 6.95 seconds; and
  deterministic `--check` confirmed byte-identical regeneration across all 17 generated files. Contract, generation,
  and deterministic checks used 180-second command and `240000 ms` Bash timeouts; Vitest used a 240-second command
  timeout, `300000 ms` Bash timeout, and 15000 ms test timeout. This proves nine paths, ten clean operations, retained
  prior operations, PUT types/functions, DELETE and legacy exclusion, full served OpenAPI/reference boundaries, no
  production frontend adoption, and deterministic output. Stage 1 and Stage 2 proof remains valid.
- **Stage 4 accepted:** manual review confirmed the recorded Stage 1 through Stage 3 proof and all CLEAN-09 acceptance
  conditions. No retained proof was invalidated, and no redundant aggregate regression command was run; the Plan is
  closed with CLEAN-10 next.
- No lint, formatting, broad type/build, source-size, aggregate, full-suite, or repository-hygiene command is Plan proof. Passing behavioral proof remains valid until a later affecting change.

## Acceptance

- A legal complete public parent FEN, including an unseen legal position, can be configured without a 404; the parent position is created or reused canonically in the same transaction as its period.
- A move preference is a legal outgoing UCI move after the parent FEN. Explicit no preference is stored distinctly from an uncovered `unconfigured` date.
- Every overlay is half-open, normalized, non-overlapping, adjacency-merged, and serialized against the latest committed schedule. Repeated PUTs are semantically idempotent.
- A successful 200 response exposes canonical FEN counters `0 1`, the explicit applied interval, the applied tagged preference, and the complete normalized configured `periods` schedule without IDs, SAN, child FEN, or repertoire data.
- CLEAN-08 GET timelines immediately show configured periods and derived gaps, and CLEAN-05 insight returns the correct date-resolved preference without changed read semantics.
- Invalid semantic values use the seven settled 422 codes; missing/incompatible/malformed/unreadable/locked storage uses the exact 503 body; unexpected failures use the exact 500 body; no 404/409/423 is introduced.
- Exactly ten clean operation IDs across nine curated paths are generated, all prior operations remain present, `/api/preferred-move` remains served but uncurated, and no production frontend module adopts the client.
- No schema, dependency, lifecycle, worker, frontend, consumer, legacy-retirement, completed-Plan, historical-record, or unrelated baseline change occurs.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, concurrency, or acceptance decision.
- Any change to body field spelling/aliases, tagged values, null/omitted-end meaning, full normalized-schedule response,
  success status, error codes/messages/statuses, canonical FEN identity, legal-move meaning, half-open dates, or lock policy.
- Any schema/table/index/trigger/version change, second SQL owner, backend SQL, non-atomic position-plus-period write,
  hidden read/write behavior, private identity exposure, old-database use, fallback, compatibility adapter, or child/repertoire model.
- Any change to CLEAN-05 resolution, CLEAN-08 timeline coverage, DB-05/SETUP-01 meanings, or inability to preserve their retained proof.
- Any legacy route/configuration/edit/removal/curation, DELETE behavior, extra curated operation, generated path outside
  the approved directory, nondeterministic generation, production frontend adoption, completed Plan edit, unrelated
  change, or Git operation.

## Visible result

> A caller can configure a legal outgoing move or explicit no-preference interval for any legal public parent FEN through generated `putPreferredMoves()` and immediately observe the normalized result through the existing timeline read.
