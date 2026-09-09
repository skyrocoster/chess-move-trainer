# CLEAN-08 preferred-move timelines - A generated API can read a complete finite FEN timeline

> **Status:** done - accepted; Stages 1 through 4 complete

- **Read trigger:** Read before implementing, validating, repairing, accepting, or closing CLEAN-08.
- **Upstream:** [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md) governs the
  CLEAN sequence, ownership, generation envelope, coexistence, and exclusions; accepted
  [CLEAN-07](../../done/database-rebuild-clean-07/database-rebuild-clean-07.md) governs the retained eight-operation
  generated surface and focused proof conventions; accepted [DB-05](../../done/database-rebuild-db-05/database-rebuild-db-05.md)
  and [SETUP-01](../../done/database-rebuild-setup-01/database-rebuild-setup-01.md) govern preferred-period storage,
  canonical identity, legal moves, half-open dates, normalization, and accepted setup data; the confirmed
  [database-rebuild API direction](../../../grilling-docs/database-rebuild-api-direction.md) governs the public preferred-
  move meaning and finite timeline direction; [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md) supplies this Plan schema.

## Outcome

Add exactly `GET /api/preferred-moves`, with operation ID `getPreferredMoves`, over the explicit rebuilt database path.
The caller supplies a complete legal public parent FEN and required finite `from`/`until` dates. The package returns the
canonical FEN and a complete normalized timeline covering the half-open window `[from, until)`. Stored move and explicit
no-preference periods are clipped to the window, and every uncovered date is returned as a derived `unconfigured`
segment. The generated client is updated immediately while the legacy singular preferred-move routes and production
frontend remain unchanged.

The successful JSON shape is:

```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "from": "2026-01-01",
  "until": "2026-04-01",
  "segments": [
    {
      "from": "2026-01-01",
      "until": "2026-02-01",
      "preference": {"kind": "move", "uci": "e2e4"}
    },
    {
      "from": "2026-02-01",
      "until": "2026-04-01",
      "preference": {"kind": "unconfigured"}
    }
  ]
}
```

## Scope

- **Included:**
  - A package-owned, explicit-path read capability under `src/chess_move_trainer/database/preferred_moves/` returning
    ordinary Python values without FastAPI, Pydantic, HTTP status, or private database handles.
  - Exact query aliases `fen`, `from`, and `until`. All are required; dates are strict `YYYY-MM-DD` calendar literals,
    `from < until` is required, and there is no default, open-ended, relative, timestamp, timezone, or new maximum-
    duration input. Unknown query fields are ignored.
  - Complete legal six-field FEN validation and canonicalization. Counters are validated but ignored for identity and
    the returned public FEN always uses counters `0 1`; legal en-passant identity follows the accepted canonical rules.
  - Half-open `[from, until)` window arithmetic owned by the package. Stored periods are clipped, open-ended periods are
    clipped at `until`, uncovered gaps are derived, segments are ascending/nonempty/nonoverlapping, coverage is exact,
    and adjacent equal values are merged.
  - Tagged values exactly `{kind: "move", uci: "..."}`, `{kind: "no_preference"}`, and derived
    `{kind: "unconfigured"}`. No SAN, position ID, stored-period identity, or mutation data is exposed.
  - Empty schedules and legal unseen positions as HTTP 200 with one complete unconfigured segment and no position or
    period write. There is no 404.
  - Typed HTTP errors: provided invalid values use 422 codes `invalid_fen`, `invalid_from`, `invalid_until`, or
    `invalid_window`; missing/incompatible/malformed/unreadable/lock-blocked storage uses 503
    `preferred_moves_unavailable`; unexpected failures use 500 `unexpected_failure`. No 409 or 423 is introduced.
  - One plural clean FastAPI feature and route registration, with the existing singular legacy route remaining served but
    outside the curated contract.
  - Exactly one curated OpenAPI operation, checked-in HeyAPI regeneration, deterministic generation proof, and no
    production frontend adoption.
- **Expected areas:**
  - `src/chess_move_trainer/database/preferred_moves/timeline.py` or the smallest equivalent package seam;
    bounded changes to `preferred_moves/repository.py` and `preferred_moves/__init__.py` only as needed to retain one
    package SQL/read owner.
  - `tests/database/preferred_moves/test_timeline.py`, focused public/boundary additions, and directly affected
    `tests/database/positions/test_insight.py` coverage only if a shared range or storage seam changes.
  - `backend/app/features/preferred_moves/`, `backend/app/main.py`, and
    `backend/tests/features/preferred_moves/`; the legacy `backend/app/features/preferred_move/` implementation is a
    coexistence boundary, not an edit target.
  - `scripts/api/export_contract.py`, `backend/tests/features/health/test_contract_export.py`,
    `frontend/src/api/client.ts`, `frontend/src/api/generatedSurface.test.ts`, and generator-owned files only under
    `frontend/src/api/generated/`.
  - At closeout only, this Plan moves to `docs/plans/done/database-rebuild-clean-08/` and the live master plan changes
    only its status, next-selectable slice, and slice-results facts so CLEAN-09 is next.
- **Excluded:**
  - PUT/DELETE operations and all CLEAN-09/CLEAN-10 behavior; no preferred-period overlay, removal, position creation,
    mutation, or hidden write.
  - Schema, table, column, index, trigger, schema-version, dependency, lifecycle, old-database, migration, fallback,
    compatibility, or transaction-policy changes; no second backend SQL/repository stack.
  - Caller-side calendar arithmetic, gap/split/merge/overlap handling, active-date resolution, generic query language,
    repertoire lines, authored lines, hierarchy, calendar UI, consumer migration, or production frontend imports.
  - Legacy route edits, removal, configuration changes, or curated-contract entry; legacy `/api/preferred-move` routes
    remain served and uncurated.
  - Changes to CLEAN-01 through CLEAN-07 meanings, completed Plans, SETUP-01 inference, unrelated worktree material,
    broad maintenance checks, commits, pushes, branches, worktrees, stashes, or other Git operations.

## Baseline preservation

Preserve unrelated and historical material exactly. In particular, do not restore or absorb the existing deleted
`data/database/README.md`, `data/database/dump_schema.py`, `data/database/schema.md`, or `data/database/schema.txt`,
and do not rewrite the modified `docs/grilling-docs/database-rebuild-api-direction.md` or any completed Plan.

## Stages

Stages are sequential; no stages run in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof. The coordinator may split an oversized stage without changing the outcome or requiring a new human decision.

### 1. **complete - Add the package timeline capability and focused package proof.**

**Ordered actions**

1. Add ordinary package request/result/segment values and typed validation, schema, storage, and lock error handling.
   Accept complete legal FENs through the accepted canonicalization while retaining the existing DB-05 four-field
   package mutation/list contracts.
2. Reuse the existing package connection, schema, canonical-position lookup, preferred-period loading, and range
   normalization seams. Keep SQL and all FEN/date/clip/gap meaning in the package; do not add a second repository stack.
   Use a read-only explicit database access path and never call the write position resolver.
3. Implement `[from, until)` clipping and cursor-based gap derivation. Normalize adjacent equal values, retain separate
   values across gaps or differing states, clip open-ended rows, and return one unconfigured segment for an empty or
   unseen schedule.
4. Treat malformed persisted dates, ranges, moves, canonical position data, incompatible/missing/unreadable storage,
   and a lock that cannot be read within the finite timeout as bounded package failures rather than guessed data.
5. Add focused proof for canonical counters and legal en-passant identity, every boundary and gap shape, exact coverage,
   deterministic ordering, adjacent merging, empty/unseen read-only behavior, malformed storage, locked storage, no
   sidecars, explicit paths, package exports, and package ownership.
6. Do not replace `PositionInsight._read_preference` or alter CLEAN-05 `as_of` semantics. If a shared range/repository
   seam is changed, rerun the directly affected CLEAN-05 package proof in this stage; otherwise retain its accepted proof.

**Proof** from `G:\ChessMoveTrainer`:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_timeline.py tests/database/preferred_moves/test_range_semantics.py tests/database/preferred_moves/test_repository.py tests/database/preferred_moves/test_public_api.py tests/database/positions/test_insight.py tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q -k "preferred_moves or position_service or lower_level_database or timeline or insight"
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Any schema/index/version/dependency change, write during GET, position creation, second SQL
owner, changed FEN identity, changed half-open/date/tag meaning, changed CLEAN-05 resolution, private-ID output, or
inability to map locked/malformed storage safely.

**Breakpoint:** none.

### 2. **complete - Add the thin clean HTTP operation and prove HTTP/coexistence behavior.**

**Ordered actions**

1. Add strict plural-feature response and error models. Expose exactly `{fen, from, until, segments}` and segment
   `{from, until, preference}` fields with a discriminated preference union. Use HTTP aliases for the reserved `from`
   name while keeping the wire spelling exact.
2. Register `GET /api/preferred-moves` with `operation_id="getPreferredMoves"` and
   `get_rebuilt_database_path()`. Translate only query values, package values, and the settled 422/503/500 outcomes;
   add no SQL or legacy configuration dependency.
3. Prove required query aliases, strict dates, ordering, exact response shape, unknown-query tolerance, canonical FEN,
   clipping/gaps, empty/unseen reads, read-only bytes/sidecars, malformed/incompatible/missing/locked storage, safe
   unexpected failures, clean dependency selection, and coexistence with all singular legacy preferred-move routes.

**Proof** from `G:\ChessMoveTrainer`:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_moves backend/tests/features/preferred_move backend/tests/features/position_insight -q
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Backend SQL, changed status/error/field/alias meaning, route conflict, legacy route edit,
fallback/compatibility behavior, hidden write, 404/409/423 behavior, or production frontend import.

**Breakpoint:** none.

### 3. **complete - Curate exactly nine clean operations and regenerate the client.**

**Ordered actions**

1. Add only `"/api/preferred-moves": {"get"}` to `APPROVED_OPERATIONS`. Update contract assertions to require exactly
   health plus CLEAN-01 through CLEAN-08 and operation ID `getPreferredMoves`, while retaining the full served OpenAPI
   schema and excluding every legacy path.
2. Re-export `getPreferredMoves` and its generated request/response/error types from `frontend/src/api/client.ts`.
   Update `frontend/src/api/generatedSurface.test.ts` to require exactly nine generated operations and nine curated paths;
   do not edit production frontend feature modules.
3. Run the accepted generator, permitting changes only under `frontend/src/api/generated/`, then prove prior operations,
   legacy exclusion, no production adoption, and byte-identical regeneration.

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

Command-level timeout: `240s`. Bash tool timeout: `300000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: `180s`. Bash tool timeout: `240000 ms`.

**Escalation boundary:** Any additional curated operation, missing prior operation, legacy operation in the contract,
generated artifact outside `frontend/src/api/generated/`, new dependency, production adoption, or nondeterministic output.

**Breakpoint:** none.

### 4. **complete - Close out CLEAN-08 and advance the live slice record.**

**Ordered actions**

1. Review Stages 1 through 3 against this Plan, record concise accepted proof and any invalidated retained proof, and
   confirm every CLEAN-08 acceptance condition. Do not add a redundant aggregate regression command.
2. Move this Plan to `docs/plans/done/database-rebuild-clean-08/`, preserving all completed Plans and the unrelated
   baseline material unchanged.
3. Update only the live master-plan status, next-selectable slice, and slice-results facts: record CLEAN-08 accepted and
   select CLEAN-09 next. Leave all other master-plan semantics unchanged.

**Proof:** Manual review against `docs/PLAN_TEMPLATE.md`; no automated Plan checker is present. Stages 1 through 3
focused behavioral proof is the retained implementation evidence. Passing proof remains valid until an affecting change.

**Escalation boundary:** Any need to revise settled semantics, completed or historical records, master-plan content
outside the three named live facts, generated-surface acceptance, unrelated material, or any Git operation.

**Breakpoint:** none; coordinator acceptance of the recorded evidence is recorded.

## Progress and decisions

- **Stage 1:** complete - package timeline, half-open clipping/gap semantics, read-only behavior, and focused package
  proof passed 82 tests with 11 intentionally deselected; breakpoint: none.
- **Stage 2:** complete - thin plural HTTP operation, typed failures, and singular legacy-route coexistence passed 53
  focused tests; breakpoint: none.
- **Stage 3:** complete - exactly nine curated/generated clean operations and deterministic HeyAPI output passed
  focused proof; breakpoint: none.
- **Stage 4:** complete - closeout and live master-plan correction recorded after coordinator acceptance;
  breakpoint: none.
- **Route decision:** use `GET /api/preferred-moves` with operation ID `getPreferredMoves`; legacy singular routes remain
  served and uncurated.
- **Window decision:** required strict `from`/`until` dates use the half-open `[from, until)` convention, with package-
  owned clipping, gap derivation, exact coverage, and no maximum-duration cap.
- **Response decision:** use top-level `{fen, from, until, segments}` and tagged segment preferences exactly as settled in
  the Outcome section.
- **Read decision:** complete legal FENs, including unseen positions, are successful read-only inputs; no position is
  created. Lock-blocked, malformed, incompatible, missing, or unreadable storage is unavailable rather than guessed.
- **CLEAN-05 decision:** retain `PositionInsight._read_preference` and `resolve_date` meanings; rerun CLEAN-05 package
  proof only if implementation changes a shared seam that can affect `as_of` resolution.
- **User decision:** none; product, API, data, ownership, generation, and acceptance decisions are settled by the packet
  and retained upstream evidence.

## Proof

- Package timeline, preferred-range regression, public exports, package boundary, source ownership, and directly affected
  CLEAN-05 proof: the finite Stage 1 command above, with its `180s` command and `240000 ms` Bash timeouts.
- **Stage 1 accepted:** the exact Stage 1 command passed 82 tests with 11 deselected in 9.89 seconds. It covers canonical
  FEN/counters, strict dates, clipping and open ends, derived gaps, half-open boundaries, adjacent-value merging,
  immutability, malformed/missing/incompatible/lock-blocked storage, unchanged bytes/no sidecars, package/source
  boundaries, and CLEAN-05 insight behavior. The included CLEAN-05 proof passed and remains valid.
- Clean HTTP response, validation, unknown-query tolerance, canonical/unseen/read-only behavior, storage failures,
  dependency selection, and legacy coexistence: the finite Stage 2 command above, with its `180s` command and `240000 ms`
  Bash timeout.
- **Stage 2 accepted:** the exact HTTP command passed 53 tests in 13.66 seconds. It covers exact aliases and response,
  input validation, canonical FEN, all preference tags, clipping/gaps, unseen and empty read-only success, storage
  failures, dependency overrides, safe unexpected-failure translation, private-field exclusion, operation ID, and
  coexistence with unchanged singular legacy routes. Stage 1 remains valid because no package path or dependency changed.
- Exactly nine curated operations and served-route boundary: the Stage 3 contract-export command, `180s` command and
  `240000 ms` Bash timeout.
- Checked-in HeyAPI generation: the Stage 3 generator command, `180s` command and `240000 ms` Bash timeout.
- Generated operation surface and no production adoption: the Stage 3 Vitest command, `240s` command and `300000 ms` Bash
  timeout, with `--testTimeout 15000`.
- Byte-identical regeneration: the Stage 3 generator `--check` command, `180s` command and `240000 ms` Bash timeout.
- **Stage 3 accepted:** the contract command passed 4 tests in 12.23 seconds; generation succeeded across 17 generated
  files and refreshed the 4 changed generator outputs; the generated-surface/no-adoption proof passed 3 files and 5
  tests in 7.45 seconds; and deterministic `--check` confirmed byte-identical regeneration of all 17 files. Contract,
  generation, and deterministic checks used 180-second command and `240000 ms` Bash timeouts; Vitest used a 240-second
  command timeout, `300000 ms` Bash timeout, and 15000 ms test timeout. This proves exactly nine clean operations,
 prior-operation retention, legacy exclusion, no production frontend adoption, and deterministic output. Stage 1 and
 Stage 2 proof remains valid.
- **Stage 4 accepted:** manual review confirmed the accepted Stages 1 through 3 evidence and every CLEAN-08 acceptance
  condition; no retained proof was invalidated. The Plan was closed and moved to the done record, and only the live
  master-plan status, next-selectable slice, and slice-results facts were updated to record CLEAN-08 accepted and
  CLEAN-09 next. No automated Plan checker or redundant aggregate regression command was run.
- No lint, formatting, broad type/build, source-size, aggregate, full-suite, or repository-hygiene command is Plan proof.

## Acceptance

- Exactly one clean operation, `GET /api/preferred-moves` / `getPreferredMoves`, is available and generated.
- Valid requests return canonical FEN counters `0 1`, echo the strict finite window, and return ascending nonempty
  segments that exactly cover `[from, until)` with no overlap or uncovered date.
- Stored move and explicit no-preference values, clipped open-ended periods, derived gaps, empty schedules, unseen legal
  positions, adjacent equal merging, and half-open boundaries have the settled meanings.
- Reads never create positions or periods and leave database bytes and target sidecars unchanged.
- Invalid provided inputs use the four typed 422 codes; missing/incompatible/malformed/unreadable/lock-blocked storage
  uses 503 `preferred_moves_unavailable`; unexpected failures use 500 `unexpected_failure`; no 404, 409, or 423 exists.
- CLEAN-05 `as_of` resolution remains unchanged, and all accepted CLEAN-01 through CLEAN-07 operations remain generated.
- The singular legacy preferred-move route remains served but uncurated; no production frontend module adopts the client.
- No schema, dependency, lifecycle, mutation, frontend, consumer, legacy-retirement, or unrelated baseline change occurs.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, concurrency, or acceptance decision.
- Any change to exact query aliases, complete-FEN/canonical identity, `[from, until)` inclusivity, segment fields, tagged
  values, gap/merge/clip behavior, status/error meanings, operation path/method, or operation ID.
- Any schema/table/index/trigger/version change, second SQL owner, backend SQL, hidden write, position creation, lock-policy
  change, old-database use, fallback, compatibility adapter, or private identity exposure.
- Any change to CLEAN-05 date resolution, SETUP-01 meanings, accepted DB-05 storage semantics, or inability to preserve
  their retained proof.
- Any legacy route/configuration/edit/removal/curation, extra curated operation, generated path outside the approved
  directory, nondeterministic generation, production frontend adoption, CLEAN-09/10 behavior, completed Plan edit,
  unrelated change, or Git operation.

## Visible result

> A caller can request a public parent FEN and finite dates and receive a complete generated preferred-move timeline with every configured value and unconfigured gap represented without doing calendar arithmetic.
