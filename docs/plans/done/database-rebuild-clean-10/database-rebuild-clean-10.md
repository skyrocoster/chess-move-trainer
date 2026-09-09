# CLEAN-10 preferred-move interval removal - A generated DELETE can uncover a dated outgoing choice

> **Status:** accepted - Stages 1 through 4 complete; Plan closed

- **Read trigger:** Read before implementing, validating, repairing, accepting, or closing CLEAN-10.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) governs the
  CLEAN sequence, ownership, generation envelope, coexistence, and consumer boundary; accepted
  [CLEAN-09](../../done/database-rebuild-clean-09/database-rebuild-clean-09.md) governs the retained preferred-move
  mutation response, canonical FEN, error, transaction, and generated-client conventions; accepted
  [CLEAN-08](../../done/database-rebuild-clean-08/database-rebuild-clean-08.md) governs the retained timeline and
  derived-gap behavior; accepted [DB-05](../../done/database-rebuild-db-05/database-rebuild-db-05.md) and
  [SETUP-01](../../done/database-rebuild-setup-01/database-rebuild-setup-01.md) govern preferred-period storage,
  canonical position writes, half-open dates, normalization, and accepted setup data; the confirmed
  [database-rebuild API direction](../../../grilling-docs/database-rebuild-api-direction.md) governs outgoing-move
  meaning, legal novel FENs, tagged values, and package/backend ownership; the retained CLEAN-10 assessment/research
  settles the exact removal contract below; [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md) supplies this Plan schema.

## Outcome

Add exactly `DELETE /api/preferred-moves`, with operation ID `deletePreferredMoves`, over the explicit rebuilt database
path. The caller supplies a complete legal public parent FEN and a required half-open calendar-date interval. The package
atomically removes configured coverage, preserves and normalizes the remaining schedule, and returns the canonical FEN,
removed interval, and complete remaining configured periods. It stores no `unconfigured` value: existing clean GET and
CLEAN-05 insight reads derive that state immediately. The checked-in generated client is updated while PUT/GET,
singular legacy routes, and production frontend modules remain unchanged.

The successful JSON shape is:

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "effective_from": "2026-02-01",
  "effective_until": "2026-03-01",
  "periods": [
    {
      "effective_from": "2026-01-01",
      "effective_until": "2026-02-01",
      "preference": {"kind": "move", "uci": "e2e4"}
    }
  ]
}
```

`periods` is the complete normalized configured schedule after removal. It contains only stored move and explicit
no-preference periods; it contains no derived gaps, IDs, SAN, child positions, history markers, action fields, or
`changed` flag. An empty remaining schedule is `"periods": []`.

## Scope

- **Included:**
  - A package-owned `PreferredMoveRemovalRequest`, `PreferredMoveRemovalResult`, and `delete_preferred_move` capability
    under `src/chess_move_trainer/database/preferred_moves/`, using ordinary immutable Python values and explicit paths.
  - The exact body `{fen, effective_from, effective_until?}`. `effective_until` omitted or `null` means an exclusive
    open-ended interval. There is no preference field; unknown top-level or nested fields, including an unknown
    `preference`, remain ignored. Mutation query aliases are not supported.
  - Complete legal six-field FEN validation and canonicalization by placement, side to move, castling, and legal
    en-passant, with response counters normalized to `0 1`; strict literal `YYYY-MM-DD` dates and a finite end later
    than the start.
  - Reuse of `unset_preference`, `normalize_periods`, the existing canonical-position unit of work, and the existing
    `BEGIN IMMEDIATE` replacement/verification transaction. Removal stores no unconfigured period.
  - Finite and open-ended removal, full/partial split and shortening, removal across multiple periods, repeated and
    non-intersecting semantic no-ops, rollback, malformed-storage safety, and serialized DELETE/PUT concurrency.
  - Accepted DB-05 no-op write semantics: an unseen legal FEN creates its canonical parent in the locked transaction
    even when no preference period is created; an existing position is reused. A repeated DELETE remains `200` and
    does not duplicate the position or periods.
  - One thin plural FastAPI DELETE adapter with exact response/error translation, immediate GET timeline and
    CLEAN-05 insight proof, unchanged PUT proof, and coexistence with all singular legacy preferred-move routes.
  - Exactly one additional curated OpenAPI operation, checked-in HeyAPI regeneration, deterministic output, retention
    of the ten accepted clean operations, legacy exclusion, and no production frontend adoption.
- **Expected areas:**
  - `src/chess_move_trainer/database/preferred_moves/mutations.py` and bounded public exports in
    `preferred_moves/__init__.py`; existing `ranges.py` and `repository.py` are reused seams and are not semantic
    redesign targets.
  - `tests/database/preferred_moves/test_mutations.py`, `test_range_semantics.py`, `test_repository.py`,
    `test_concurrency.py`, `test_timeline.py`, `test_setup.py`, `test_public_api.py`, and retained
    `tests/database/positions/test_insight.py` proof where the shared preference read seam is exercised.
  - `backend/app/features/preferred_moves/api_schemas.py` and `router.py`; `backend/app/main.py` only if the existing
    plural router registration unexpectedly differs, which is an escalation rather than a planned edit.
  - `backend/tests/features/preferred_moves/` plus retained plural, singular legacy, and `position_insight` HTTP proof.
  - `scripts/api/export_contract.py`, `backend/tests/features/health/test_contract_export.py`,
    `frontend/src/api/client.ts`, `frontend/src/api/generatedSurface.test.ts`, and generator-owned files only under
    `frontend/src/api/generated/`.
  - At closeout only, this Plan moves to `docs/plans/done/database-rebuild-clean-10/` and the live master plan changes
    only its status, next-selectable slice, and slice-results facts.
- **Excluded:**
  - Any stored `unconfigured` value, preference field or preference validation for DELETE, caller-side date/gap/
    split/merge arithmetic, action/history/audit/event semantics, `changed`, SAN, private IDs, child positions,
    repertoire lines, calendar UI, or consumer integration.
  - Schema, table, column, index, trigger, schema-version, dependency, lifecycle, old-database, migration, fallback,
    compatibility, or transaction-policy changes; no second SQL or backend repository owner.
  - Changes to GET, PUT, CLEAN-01 through CLEAN-09 meanings, CLEAN-05 resolution, CLEAN-08 timeline construction,
    DB-05/SETUP-01 semantics, or the singular legacy feature and its routes.
  - Production frontend adoption, calendar work, legacy removal or curation, data cleanup, old-database work,
    completed Plan edits, restoration of unrelated deleted data documentation/scripts, modification of the API-direction
    grilling record, broad maintenance checks, Quality validation, commits, pushes, branches, worktrees, stashes, or
    unrelated changes.

## Baseline preservation

Preserve unrelated and historical material exactly. In particular, do not restore or absorb the existing deleted
`data/database/README.md`, `data/database/dump_schema.py`, `data/database/schema.md`, or `data/database/schema.txt`,
and do not rewrite the modified `docs/grilling-docs/database-rebuild-api-direction.md` or any completed Plan.

## Settled contract

- The request body is exactly `{fen, effective_from, effective_until?}`. All mutation inputs are in the body. Omitted
  and `null` `effective_until` both mean an exclusive open-ended interval, and the response always emits the field
  explicitly. Unknown body fields are ignored; missing or strict-type body failures retain FastAPI's established 422.
- FEN is a complete legal six-field FEN. Counters are validated but ignored for identity; the response uses counters
  `0 1`. Dates are strict literals, `effective_from` is required, and a finite end must be later than the start.
- Success is always `200`, including empty schedules, non-intersecting removal, semantic repeats, and removal from an
  unseen legal FEN. The response is `{fen, effective_from, effective_until, periods}` with the complete remaining
  normalized configured schedule and no `preference`, `changed`, action, or history field.
- Removal uses half-open `[effective_from, effective_until)` semantics. It deletes all intersecting stored coverage,
  preserves fragments outside the interval, and re-normalizes adjacency without creating an `unconfigured` row.
- A legal unseen FEN resolves/creates one canonical parent inside the same locked transaction even when the resulting
  schedule is empty. This is a purposeful preferred-move edit under the accepted DB-05 semantics, not a read behavior.
- Every supported mutation acquires `BEGIN IMMEDIATE` before reading the schedule. A later DELETE or PUT lock holder
  reads the latest committed normalized schedule; its operation controls shared dates while non-overlapping effects
  remain. All failures and interruptions roll back position and schedule changes together.
- Semantic 422 errors are:
  - `invalid_fen` / `FEN is invalid`
  - `invalid_effective_from` / `effective_from must be a literal YYYY-MM-DD date`
  - `invalid_effective_until` / `effective_until must be a literal YYYY-MM-DD date`
  - `invalid_window` / `effective_until must be later than effective_from`
- Missing, incompatible, malformed, unreadable, or lock-blocked storage is `503` with
  `{code: "preferred_moves_unavailable", message: "Preferred moves unavailable"}`.
- Unexpected failures are `500` with
  `{code: "unexpected_failure", message: "Unable to delete preferred moves"}`.
- No `404`, `409`, or `423` is introduced. GET timeline and CLEAN-05 insight derive `unconfigured` from the absence
  of stored coverage; PUT remains unchanged.

## Stages

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof. The coordinator may split an oversized stage without changing the outcome or requiring a new human decision.

### 1. **complete - Add package removal and prove atomic schedule behavior.**

**Ordered actions**

1. Add immutable ordinary `PreferredMoveRemovalRequest`, `PreferredMoveRemovalResult`, and `delete_preferred_move`
   values/function in `mutations.py`; validate and canonicalize the complete FEN and strict interval before any write.
2. Reuse `PreferredMoveRepository._amend` and `ranges.unset_preference`; do not add SQL, a second repository, or a new
   stored state. Keep the writer lock before parent resolution and schedule read, pass the canonical position into the
   schedule load, replace and verify normalized rows, and commit or roll back as one unit.
3. Export only the intended package contracts. Preserve `PreferredMoveRepository.unset`, PUT behavior, timeline reads,
   and `PositionInsight._read_preference` meanings.
4. Add focused proof for finite/open-ended removal, full and partial removal, split/shorten behavior, no-op and repeat,
   empty existing schedules, legal novel FEN parent creation without a preference row, canonical counters/legal
   en-passant identity, malformed storage, lock failure, rollback/interruption, and DELETE/PUT latest-schedule
   serialization. Retain direct GET/insight and PUT regression proof.

**Proof** from `G:\ChessMoveTrainer`:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_mutations.py tests/database/preferred_moves/test_range_semantics.py tests/database/preferred_moves/test_repository.py tests/database/preferred_moves/test_concurrency.py tests/database/preferred_moves/test_timeline.py tests/database/preferred_moves/test_setup.py tests/database/positions/test_insight.py tests/database/preferred_moves/test_public_api.py -q
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Any schema/dependency change, second SQL owner, changed canonical identity/date/tag meaning,
changed lock policy, non-atomic parent-plus-schedule write, stored unconfigured value, or inability to prove rollback
and latest-committed DELETE/PUT serialization. If evidence indicates that an unseen no-op DELETE must remain entirely
no-write rather than create/reuse the canonical parent, stop and escalate; the accepted DB-05 mutation semantics require
the parent resolution behavior stated above.

**Breakpoint:** none.

### 2. **complete - Add the thin clean DELETE and prove HTTP/read coexistence.**

**Ordered actions**

1. Extend `api_schemas.py` with an ignored-extra DELETE request model and strict removal response model. Keep the
   response periods limited to move/no-preference configured values and emit `effective_until` explicitly.
2. Add `DELETE /api/preferred-moves` with `operation_id="deletePreferredMoves"` and the existing
   `get_rebuilt_database_path()` dependency. Translate only package values and the settled `200/422/503/500` outcomes;
   add no SQL, query alias, calendar arithmetic, or legacy dependency.
3. Add focused HTTP proof for exact body spelling, omitted/null end, ignored unknown fields including `preference`, strict
   FEN/date/window errors, canonical response, empty/no-op/repeat behavior, novel-FEN creation, finite/open removal,
   lock/malformed/missing storage, safe unexpected-failure translation, immediate GET unconfigured segments, immediate
   CLEAN-05 insight unconfigured state, retained PUT behavior, and unchanged singular legacy route registration.

**Proof** from `G:\ChessMoveTrainer`:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_moves backend/tests/features/preferred_move backend/tests/features/position_insight -q
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Any backend SQL, changed body/response/status/error/message meaning, preference field
behavior, hidden write beyond accepted novel-parent mutation, `404/409/423`, route conflict, legacy edit, fallback,
compatibility behavior, or production frontend import.

**Breakpoint:** none.

### 3. **complete - Curate DELETE beside GET/PUT and regenerate the client.**

**Ordered actions**

1. Add only `"/api/preferred-moves": {"delete"}` to `APPROVED_OPERATIONS` and update contract assertions to require
   exactly 9 curated paths and 11 operation IDs: all prior ten plus `deletePreferredMoves`. The served OpenAPI remains
   full, and every legacy path remains excluded from the curated export.
2. Re-export `deletePreferredMoves` and its generated request/response/error types from `frontend/src/api/client.ts`.
   Update `frontend/src/api/generatedSurface.test.ts` to require 11 operation functions and GET/PUT/DELETE on the plural
   preferred-moves path. Do not edit production frontend modules.
3. Run the accepted generator, permitting changes only under `frontend/src/api/generated/`, then prove retained
   operations, legacy exclusion, no production adoption, and byte-identical regeneration.

**Proof** from `G:\ChessMoveTrainer`:

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
contract, generated artifact outside `frontend/src/api/generated/`, new dependency, production adoption,
nondeterministic output, or failure to retain the exact 9-path/11-operation count.

**Breakpoint:** none.

### 4. **complete - Close CLEAN-10 and advance the live slice record.**

**Ordered actions**

1. Review Stages 1 through 3 against this Plan and all acceptance conditions. Record concise accepted proof and any
   invalidated retained proof; do not add a redundant aggregate regression command.
2. Move this Plan to `docs/plans/done/database-rebuild-clean-10/`, preserving completed Plans and unrelated baseline
   material unchanged.
3. Update only the live master-plan status, next-selectable slice, and slice-results facts: record CLEAN-01 through
   CLEAN-10 accepted and select `CONSUMER-01` next. Do not execute, plan, or start CONSUMER-01 in this slice.

**Proof:** Manual review against `docs/PLAN_TEMPLATE.md`; no automated Plan checker is present. Stages 1 through 3
focused behavioral proof is the retained implementation evidence.

**Escalation boundary:** Any need to revise settled contract, no-op novel-FEN creation, completed or historical record,
master-plan content outside the three named live facts, generated-surface acceptance, unrelated material, or any Git
operation.

**Breakpoint:** coordinator acceptance of the recorded evidence; no new product or consumer decision.

## Progress and decisions

- **Stage 1:** complete - package removal, normalized persistence, rollback, and DELETE/PUT concurrency proof passed 123
  focused tests; breakpoint: none.
- **Stage 2:** complete - thin DELETE adapter, exact response/status mapping, immediate GET/insight proof, retained PUT,
  and legacy coexistence passed 83 focused tests; breakpoint: none.
- **Stage 3:** complete - 9 curated paths, 11 generated operations, deterministic HeyAPI output, prior-operation
  retention, legacy exclusion, and no production adoption passed focused proof; breakpoint: none.
- **Stage 4:** complete - closeout review accepted the retained Stage 1 through Stage 3 proof, moved this Plan to done,
  and advanced only the live master-plan facts to `CONSUMER-01`; breakpoint: none.
- **Route decision:** use `DELETE /api/preferred-moves` with operation ID `deletePreferredMoves`; retain GET/PUT on the
  same plural path and all singular legacy routes.
- **Removal decision:** all FEN and dates are in the body; omitted/null end is open-ended; no preference field exists;
  the response returns the complete remaining normalized configured schedule.
- **Transaction decision:** reuse one package-owned `BEGIN IMMEDIATE` transaction that resolves/reuses the parent, reads
  the fresh schedule, removes coverage, verifies, and commits or rolls back as one unit.
- **No-op decision:** an unseen legal no-op DELETE creates/reuses the canonical parent but creates no preference row,
  following accepted DB-05 `unset` semantics.
- **Generation decision:** the curated contract grows from 10 operations across 9 paths to 11 operations across 9 paths;
  no additional path or consumer operation is added.
- **Retained-proof decision:** CLEAN-05 insight, CLEAN-08 timeline, and CLEAN-09 PUT proof are rerun through the focused
  package/HTTP commands because the shared preferred-move write seam is exercised; no read meaning changes.
- **User decision:** none; product, API, data, ownership, concurrency, generation, and acceptance decisions are settled
  by the packet and assessment.

## Proof

- Package removal, retained ranges/repository/concurrency/timeline/setup/insight behavior, public exports, and PUT
  regression: the exact Stage 1 command above, with `180s` command and `240000 ms` Bash timeouts.
- **Stage 1 accepted:** after one focused assertion correction, the exact package command passed 123 tests in 15.84
  seconds. It covers finite/open full and partial removal, split/shorten/no-op behavior, novel canonical position creation
  without a preference row, idempotence, rollback, malformed/locked storage, latest-committed DELETE/PUT concurrency,
  complete configured result periods, public exports, retained PUT behavior, and immediate timeline/insight unconfigured
  meanings.
- DELETE response, validation/errors, no-op and novel-FEN behavior, storage failures, immediate GET/insight behavior,
  retained PUT, dependency selection, and singular legacy coexistence: the exact Stage 2 command above, with `180s`
  command and `240000 ms` Bash timeouts.
- **Stage 2 accepted:** after one test-helper correction, the exact HTTP command passed 83 tests in 33.25 seconds. It
  covers the DELETE contract, canonical 200 response, semantic 422 and deterministic 503/500 translation, finite/open
  removals, no-op/repeat/novel-position behavior, immediate GET timeline and insight postconditions, retained PUT,
  dependency override, private-data exclusion, and singular legacy coexistence. Stage 1 remains valid because no package,
  dependency, or configuration path changed.
- Nine-path/11-operation curated contract and served-route boundary: the exact Stage 3 contract command above, with
  `180s` command and `240000 ms` Bash timeout.
- Checked-in HeyAPI generation: the exact Stage 3 generator command above, with `180s` command and `240000 ms` Bash
  timeout.
- Generated operation surface and no production adoption: the exact Stage 3 Vitest command above, with `240s` command,
  `300000 ms` Bash timeout, and `15000 ms` test timeout.
- Byte-identical regeneration: the exact Stage 3 generator `--check` command above, with `180s` command and `240000 ms`
  Bash timeout.
- **Stage 3 accepted:** the contract command passed 4 tests in 12.08 seconds. Generation succeeded, reported 282 ms,
  and refreshed 4 of the 17 checked-in generated files. The first generated-surface run exposed only an expected-schema
  assertion; after correcting that approved test, the same command passed 3 files and 5 tests in 3.11 seconds.
  Deterministic `--check` then passed, reporting 233 ms and byte-identical regeneration of all 17 files. Contract,
  generation, and deterministic checks used 180-second command and `240000 ms` Bash timeouts; Vitest used a 240-second
  command timeout, `300000 ms` Bash timeout, and 15000 ms test timeout. This proves exactly 9 clean paths and 11
  operations, retained prior operations, GET/PUT/DELETE on the plural path, resolved schema references, all legacy
  exclusion, no production frontend adoption, and deterministic output. Stage 1 and Stage 2 proof remains valid.
- **Stage 4 accepted:** manual closeout review found no invalidated retained proof or acceptance expansion. The Plan is
  complete and recorded in `docs/plans/done/database-rebuild-clean-10/`; the live master plan records `CLEAN-01` through
  `CLEAN-10` accepted and `CONSUMER-01` as next selectable. No additional behavioral command was run.

No lint, formatting, broad type/build, source-size, aggregate, full-suite, Quality, or repository-hygiene command is
Plan proof. Passing behavioral proof remains valid until a later change affects its command, inputs, exercised behavior,
configuration, dependencies, or environment.

## Acceptance

- A legal complete public parent FEN, including an unseen legal position, can be used with DELETE without a 404; the
  canonical parent is created or reused in the same transaction even when no period remains.
- DELETE removes configured move and explicit no-preference coverage over the exact half-open interval, stores no
  unconfigured value, preserves outside fragments, and leaves one normalized non-overlapping schedule.
- Empty, repeated, and non-intersecting removals are successful `200` operations with no duplicate periods or positions.
- A successful response exposes only canonical FEN counters `0 1`, the explicit removed interval, and complete remaining
  configured `periods`; it has no preference, changed flag, IDs, SAN, child FEN, or history.
- Latest-committed serialized DELETE/PUT operations preserve non-overlapping effects and give the later writer control of
  shared dates; failures and interruptions roll back parent and schedule changes together.
- CLEAN-08 GET immediately derives unconfigured segments for removed dates, CLEAN-05 insight returns unconfigured for
  removed dates, and PUT behavior remains unchanged.
- The four DELETE semantic 422 codes, exact 503 body, exact 500 body, and absence of 404/409/423 are proven.
- Exactly 11 clean operation IDs across 9 curated paths are generated; all ten earlier clean operations remain, the
  singular legacy route remains served but uncurated, and no production frontend module adopts the client.
- No schema, dependency, lifecycle, worker, frontend, consumer, legacy-retirement, completed-Plan, historical-record,
  data-cleanup, or unrelated baseline change occurs.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, concurrency, or acceptance decision.
- Any change to body field spelling/aliases, ignored-unknown behavior, preference-field behavior, null/omitted-end
  meaning, full remaining-schedule response, success status, error codes/messages/statuses, canonical FEN identity,
  half-open dates, or lock policy.
- Any disagreement with the accepted no-op novel-FEN creation behavior; a request to make it entirely no-write is a
  coordinator decision, not an implementation detail.
- Any schema/table/index/trigger/version change, second SQL owner, backend SQL, non-atomic parent-plus-schedule write,
  hidden read/write behavior, private identity exposure, old-database use, fallback, compatibility adapter, or child/
  repertoire model.
- Any change to CLEAN-05 resolution, CLEAN-08 timeline coverage, CLEAN-09 PUT behavior, DB-05/SETUP-01 meanings, or
  inability to preserve retained proof.
- Any legacy route/configuration/edit/removal/curation, extra curated operation, generated path outside the approved
  directory, nondeterministic generation, production frontend adoption, CONSUMER-01 work, completed Plan edit,
  unrelated change, or Git operation.

## Visible result

> A caller can remove a dated preferred outgoing choice through generated `deletePreferredMoves()` and immediately see the
> removed dates as `unconfigured` in the existing clean timeline and position insight reads.
