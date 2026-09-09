# CLEAN-05 position insight - A generated API can inspect one rebuilt position

> **Status:** done - accepted

- **Read trigger:** whenever CLEAN-05 implementation, validation, repair, acceptance, or closeout is approved
- **Upstream:** [database-rebuild.md](../../../master-plans/database-rebuild/database-rebuild.md) (authoritative
  CLEAN order, position-insight semantics, ownership, exclusions, and slice envelope); accepted
  [CLEAN-01](../../done/database-rebuild-clean-01/database-rebuild-clean-01.md),
  [CLEAN-02](../../done/database-rebuild-clean-02/database-rebuild-clean-02.md),
  [CLEAN-03](../../done/database-rebuild-clean-03/database-rebuild-clean-03.md), and
  [CLEAN-04](../../done/database-rebuild-clean-04/database-rebuild-clean-04.md) Plans (retained clean package,
  adapter, generation, and proof seams); [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md) (focused Plan schema)

## Outcome

Add exactly `GET /api/positions/insight`, with operation ID `getPositionInsight`, over the rebuilt database at
`data/database/chess.db`. A caller supplies one complete legal FEN, `trainer_color`, and `as_of`; the generated
operation returns one canonical, sparse-capable position view containing current opening recognition,
trainer-color-scoped experience, observed outgoing moves, current analysis state/result, and the preference resolved for
the requested date.

The package owns canonical chess identity, SQL, temporal resolution, filtering, aggregation, distinct-game and
occurrence meanings, and read-only behavior. The FastAPI adapter owns only HTTP parameters, strict response models, and
status/error translation. The curated OpenAPI contract and checked-in HeyAPI client are updated in the same slice.

## Settled HTTP shape

The successful JSON response uses these exact public fields:

```json
{
  "fen": "canonical six-field FEN with 0 1 counters",
  "trainer_color": "white",
  "as_of": "2026-09-09",
  "opening": {
    "key": "C20:King's Pawn Game",
    "eco": "C20",
    "name": "King's Pawn Game",
    "ply": 8,
    "match": "route"
  },
  "experience": {
    "distinct_game_count": 12,
    "occurrence_count": 18
  },
  "observed_moves": [
    {
      "move_uci": "e2e4",
      "distinct_game_count": 9,
      "occurrence_count": 11
    }
  ],
  "analysis": {
    "state": "ready",
    "result": {
      "quality": "browser",
      "configuration_version": 1,
      "settings": {},
      "engine_name": "Stockfish",
      "engine_version": "18",
      "terminal_kind": null,
      "lines": []
    }
  },
  "preference": {"kind": "move", "uci": "e2e4"}
}
```

`opening` is either the current `{key, eco, name, ply, match}` label or `null`; `match` is `route` or `transposition`.
`experience` and `observed_moves` are scoped to the supplied trainer color. `observed_moves` contains only stored
outgoing moves and is ordered by distinct-game count descending, then UCI ascending; both counts retain their explicit
distinct-game and occurrence meanings. `analysis.result` is `null` when no complete result exists and otherwise contains
the public current result fields and normalized candidate lines (`rank`, `score_kind`, `score_value`, `wdl_wins`,
`wdl_draws`, `wdl_losses`, `pv_uci`, and `depth`) without a position ID. A queued or running request may coexist with
the returned current result; state precedence is `running`, then `queued`, then `ready` when only a result exists, then
`not_requested`. `preference` is one of the three tagged values named above.

The error body is `{code, message}` with `code` limited to `invalid_fen`, `invalid_trainer_color`, `invalid_as_of`,
`position_insight_unavailable`, or `unexpected_failure`. The operation has no 404 response: an unseen legal position is a
sparse success.

## Scope

- **Included:**
  - An explicit-path package capability returning ordinary Python dataclasses and values, with no FastAPI, Pydantic, or
    backend imports.
  - Required query fields `fen`, `trainer_color` (`white` or `black`), and `as_of` (strict `YYYY-MM-DD` date literal).
    Unknown query fields remain ignored.
  - Canonical position data represented by the canonical four-field identity and a normalized public six-field FEN with
    counters `0 1`; request counters do not change identity.
  - Current opening recognition as one current label or `null`, using the existing public `ECO:Name` key and match
    meaning; route moves, route IDs, and an opening hierarchy are not returned.
  - Experience counts filtered to the supplied trainer color: `distinct_game_count` and `occurrence_count`.
  - `observed_moves`, containing only stored outgoing moves for that trainer-color scope, each with canonical UCI,
    distinct-game count, and occurrence count. Results use deterministic `distinct_game_count DESC, move_uci ASC`
    ordering; legal moves are not generated.
  - Current analysis state `not_requested`, `queued`, `running`, or `ready`, plus the one current complete result when
    available. The result exposes only public quality/result/line data and never a private position ID. A live queued or
    running request may coexist with the current stored result.
  - Date-resolved preference values tagged `{kind: "move", uci: "..."}`, `{kind: "no_preference"}`, or
    `{kind: "unconfigured"}`. The package performs date resolution; callers do not calculate gaps or intervals.
  - A legal FEN absent from stored games succeeds with empty experience/moves, no opening, `not_requested` analysis, and
    `unconfigured` preference without creating a `derived_position` row or any other database change.
  - Strict HTTP models and deterministic typed errors: invalid FEN, color, or date returns 422; missing, incompatible,
    malformed, or unreadable rebuilt data returns 503 with `position_insight_unavailable`; unexpected failures return
    500 with `unexpected_failure`. There is no 404 for an unseen legal position.
  - Exactly one new curated operation and generated-client operation while retaining `getHealth`, `getGames`,
    `getGame`, `getOpenings`, and `getOpeningByKey`.
- **Expected areas:**
  - `src/chess_move_trainer/database/positions/` for composition, read-only position lookup, ordinary public values,
    and exports; existing `analysis/`, `openings/`, `preferred_moves/`, and `stockfish/` package seams only where
    necessary to compose their accepted read meanings.
  - `tests/database/positions/` plus directly affected retained primitive/boundary tests under
    `tests/database/{analysis,openings,preferred_moves,stockfish}/` and `tests/database/test_package_boundary.py`.
  - `backend/app/features/position_insight/` and the bounded router registration in `backend/app/main.py`, using the
    existing `get_rebuilt_database_path()` dependency without changing the legacy position feature.
  - `backend/tests/features/position_insight/` plus directly relevant retained clean and legacy-coexistence tests under
    `backend/tests/features/{games,openings,positions,position_context,move_response_distribution}/`.
  - `scripts/api/export_contract.py` and `backend/tests/features/health/test_contract_export.py`.
  - `frontend/src/api/client.ts`, `frontend/src/api/generatedSurface.test.ts`, and generator-owned output only under
    `frontend/src/api/generated/`; existing generator configuration and orchestrator remain unchanged unless a direct
    tooling defect is discovered and escalated.
  - At closeout only: this Plan and the live status/next-selectable/slice-results facts in
    `docs/master-plans/database-rebuild/database-rebuild.md`.
- **Excluded:**
  - Any schema, table, column, index, trigger, schema-version, dependency, database lifecycle, or old-database change.
  - Hidden writes, position resolution that creates rows during a read, legal-move generation, `include`, screen-shaped
    variants, caller-side date/interval arithmetic, generic query languages, or compatibility/fallback adapters.
  - Any operation besides `GET /api/positions/insight`; CLEAN-06 and later behavior; frontend production adoption;
    consumer migration; legacy route changes or retirement; legacy operation entry into the curated contract.
  - Backend SQL, direct SQLite access, or chess/temporal/filter/aggregation meaning in the HTTP adapter.
  - Changes to accepted CLEAN-01..04 behavior, their done Plans, SETUP-02 tooling, unrelated deleted `data/database/*`
    documentation/scripts, or the modified API-direction grilling record.
  - Lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, complete maintenance
    checks, commits, pushes, branches, worktrees, stashes, or other Git operations.

## Baseline preservation

The accepted CLEAN-01..04 implementations, generated five-operation surface, legacy routes, SETUP-02 tooling, and all
completed historical Plans remain in place. The assessment found unrelated current worktree material that must be
preserved exactly: deleted `data/database/README.md`, `data/database/dump_schema.py`, `data/database/schema.md`, and
`data/database/schema.txt`, plus the modified `docs/grilling-docs/database-rebuild-api-direction.md`. This Plan does not
restore, rewrite, stage, absorb, or otherwise clean up that material.

## Stages

1. **complete** - Composed package position insight capability and focused package proof.
2. **complete** - Thin FastAPI operation and focused HTTP/coexistence proof.
3. **complete** - Curated contract, HeyAPI generation, generated-surface proof, and deterministic proof.
4. **complete** - Closed out the Plan and corrected only the live master-plan status, next-selectable slice, and slice-results
   facts after all acceptance proof passes.

Stages are sequential; no stage runs in parallel. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Later stages rerun only missing or invalidated
proof.

### Stage 1 - Package position insight capability and proof

Ordered actions:

1. Add or extend the package-owned position insight capability under `src/chess_move_trainer/database/positions/` with
   immutable ordinary Python values for the request and complete response sections. Use an explicit `database_path` and
   the accepted schema-v1/read-only connection boundary.
2. Canonicalize the complete input FEN through the accepted position rules, look up an existing position without calling
   the write resolver, and compose the accepted opening recognition, analysis result/queue, and preferred-date seams.
   Keep all direct SQL, distinct-game/occurrence aggregation, trainer-color filtering, deterministic ordering, malformed
   data checks, and private-ID removal inside package ownership.
3. Prove existing positions and unseen legal positions, counter-insensitive canonical identity, opening/no-opening cases,
   trainer-color experience and move counts, deterministic ordering, analysis states/results, date-resolved preference,
   invalid inputs, malformed/incompatible storage, unchanged database bytes, no SQLite sidecars, explicit temporary
   paths, and the package boundary. Extend retained primitive tests only when a touched seam requires regression proof.

Proof, from working directory `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/positions/test_insight.py tests/database/test_position_repository.py tests/database/openings/test_recognition.py tests/database/analysis/test_reading.py tests/database/stockfish/test_queue.py tests/database/preferred_moves/test_repository.py tests/database/test_package_boundary.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

Escalation boundary: any schema/index/version change, write during a read, new SQL owner, private-ID output, changed
canonical FEN or date/analysis/preference meaning, or inability to compose the accepted schema-v1 seams. Breakpoint:
none.

### Stage 2 - Thin FastAPI adapter and proof

Ordered actions:

1. Add strict position-insight success and error models under `backend/app/features/position_insight/` and register one
   `GET /api/positions/insight` operation with `operation_id="getPositionInsight"`. Use `get_rebuilt_database_path()`;
   do not modify the legacy `/api/position-context` or game-position adapter.
2. Translate only HTTP inputs, package values, and the settled 422/503/500 errors. Keep SQL, chess validation,
   temporal resolution, filtering, aggregation, and sparse-read behavior in the package.
3. Prove the exact response, required fields and invalid values, unknown-query tolerance, unseen legal FEN behavior,
   analysis/preference states, private-ID exclusion, read-only bytes/no sidecars, clean dependency selection, and
   coexistence of accepted clean and legacy routes.

Proof, from working directory `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/position_insight backend/tests/features/games backend/tests/features/openings backend/tests/features/positions backend/tests/features/position_context backend/tests/features/move_response_distribution -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

Escalation boundary: backend SQL, legacy path/configuration, route removal or relocation, fallback/compatibility code,
changed HTTP fields/statuses/meanings, a route conflict that cannot preserve legacy registration, or any frontend
consumer import. Breakpoint: none.

### Stage 3 - Curated contract, HeyAPI generation, and deterministic proof

Ordered actions:

1. Add only `"/api/positions/insight": {"get"}` to `APPROVED_OPERATIONS` in `scripts/api/export_contract.py` and
   retain fail-closed export behavior.
2. Update the contract test to require exactly the six clean paths (health, CLEAN-01 through CLEAN-05), their six
   operation IDs, only referenced schemas, deterministic export, full served OpenAPI, and exclusion of every legacy path.
3. Re-export `getPositionInsight` and its generated types from `frontend/src/api/client.ts`; update
   `frontend/src/api/generatedSurface.test.ts` to require exactly the six clean operations and paths. Do not edit
   production frontend feature modules.
4. Run the accepted generator to update only `frontend/src/api/generated/`, then run the focused contract, generation,
   generated-surface, and deterministic checks in order.

Proof, from working directory `G:\ChessMoveTrainer` in Git Bash:

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000
```

Command-level timeout: 240 seconds. Bash tool timeout: `300000 ms`.

```text
.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check
```

Command-level timeout: 180 seconds. Bash tool timeout: `240000 ms`.

These checks prove the six-operation clean contract, retained CLEAN-01..04 generation, legacy exclusion, no production
frontend adoption, and byte-identical regeneration.

Escalation boundary: any additional curated operation, generated artifact outside `frontend/src/api/generated/`, new
dependency, production frontend import, legacy operation entering the contract, or nondeterministic generation.
Breakpoint: none.

### Stage 4 - Closeout and live master-plan correction

Ordered actions:

1. Confirm Stages 1 through 3 and all acceptance conditions passed; record concise proof, decisions, and retained-proof
   invalidation in this Plan.
2. Move this completed Plan to `docs/plans/done/database-rebuild-clean-05/` only as the normal Plan closeout operation;
   preserve CLEAN-01..04 done Plans unchanged.
3. Update only the live master-plan facts needed to correct its stale summary: set the next selectable slice to
   `CLEAN-06`, record CLEAN-01 through CLEAN-05 as accepted in `Slice results`, and leave the inventory, semantics,
   exclusions, and historical evidence unchanged. Do not update any completed historical Plan.

Proof: no additional behavioral command. The Stage 3 focused contract, generated-surface, and `--check` proof plus the
recorded Stage 1/2 proofs are the closeout evidence; document review is manual because no coordinator-supplied Plan
checker is present.

Escalation boundary: any need to revise settled slice semantics, historical records, or any master-plan section beyond
the live status/next-selectable/slice-results facts named above. Breakpoint: none.

## Progress and decisions

- **Stage 1:** complete - package insight capability and sparse/read-only proof passed with 61 tests; breakpoint: none.
- **Stage 2:** complete - thin HTTP adapter and clean/legacy coexistence proof passed with 113 tests; breakpoint: none.
- **Stage 3:** complete - exactly six clean operations are curated and generated, focused contract and generated-surface
  proof passed, and regeneration is byte-identical; breakpoint: none.
- **Stage 4:** complete - manual closeout review confirmed all four stages accepted, retained proof remains valid, and no
  additional behavioral command was run; the live master plan now selects CLEAN-06 next; breakpoint: none.
- **Database decision:** use only the accepted schema-v1 rebuilt database path, with the existing
  `CHESS_REBUILT_DATABASE_PATH` dependency seam; no schema object or database activation is added.
- **Ownership decision:** the package owns SQL and all chess/temporal/filter/aggregation meaning; the backend owns HTTP
  translation; generated files remain generator-owned; production frontend modules remain untouched.
- **Contract decision:** the new clean operation is `GET /api/positions/insight` / `getPositionInsight`; the curated
  contract grows from five to exactly six clean operations and continues to exclude legacy routes.

## Proof

- **Stage 1 accepted:** from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/positions/test_insight.py tests/database/test_position_repository.py tests/database/openings/test_recognition.py tests/database/analysis/test_reading.py tests/database/stockfish/test_queue.py tests/database/preferred_moves/test_repository.py tests/database/test_package_boundary.py -q`
  passed 61 tests in 7.61 seconds with a 180-second command timeout and `240000 ms` Bash timeout. It covered
  canonicalization, sparse unseen positions without writes, trainer-color counts and ordering, opening recognition,
  analysis precedence, date-resolved preferences, invalid storage, immutable ordinary values, explicit temporary paths,
  unchanged database bytes/no sidecars, and package import boundaries. No later edit has invalidated this proof.
- **Stage 2 accepted:** from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/position_insight backend/tests/features/games backend/tests/features/openings backend/tests/features/positions backend/tests/features/position_context backend/tests/features/move_response_distribution -q`
  passed 113 tests in 83.03 seconds with a 180-second command timeout and `240000 ms` Bash timeout. It covered the exact
  HTTP response, validation, unknown query tolerance, sparse read, analysis/preference states, private-ID exclusion,
  read-only behavior, dependency overrides, typed 503/500 translation, and clean/legacy route coexistence. Stage 1 proof
  remains valid because no package path or dependency it established changed.
- **Stage 3 accepted:** from `G:\ChessMoveTrainer`,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q`
  passed 4 tests in 5.17 seconds with a 180-second command timeout and `240000 ms` Bash timeout. The matching generation
  command produced 17 checked-in files with the same timeout bounds. The focused
  `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000`
  proof passed 3 files and 4 tests in 1.64 seconds with a 240-second command timeout and `300000 ms` Bash timeout after
  one expectation-only correction. Finally,
  `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
  passed with a 180-second command timeout and `240000 ms` Bash timeout, confirming byte-identical regeneration of all
  17 files. These prove exactly six curated/generated clean operations, retained prior operations, legacy exclusion,
  no production frontend adoption, and deterministic output. No Stage 3 edit invalidated Stage 1 or Stage 2 proof.
- Package capability, canonical identity, sparse/read-only behavior, experience and move meanings, current analysis,
  date-resolved preference, explicit paths, schema handling, and package ownership: Stage 1 finite pytest command.
- HTTP response, validation/errors, sparse behavior, clean dependency, private-ID exclusion, read-only behavior, and
  accepted clean/legacy route coexistence: Stage 2 finite pytest command.
- Six-operation curated contract and served-route boundary: Stage 3 contract-export pytest command.
- Checked-in HeyAPI surface and no production adoption: Stage 3 focused API Vitest command.
- Byte-identical regeneration: Stage 3 generator `--check` command.

No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, Quality, or complete maintenance
proof is part of this Plan. Passing behavioral proof remains valid until a later change affects its command, inputs,
exercised behavior, configuration, dependencies, or environment.

## Acceptance

- Exactly one new clean operation, `GET /api/positions/insight`, is available with `getPositionInsight` and no other
  CLEAN-06+ operation is added.
- Explicit-path package reads are correct and read-only; an unseen legal FEN returns sparse success without creating a
  position row, sidecar, or other database change.
- Required FEN, trainer-color, and date context, canonical identity, trainer-color-filtered experience, observed outgoing
  moves, opening recognition, current analysis state/result, and date-resolved preference meanings are proven.
- HTTP validation, unknown-field tolerance, and typed unavailable/unexpected failures are deterministic; no unseen-position
  404 exists.
- The curated OpenAPI contract contains exactly health and CLEAN-01 through CLEAN-05, the generated client exposes those
  six operations, legacy routes remain served but uncurated, and generation `--check` passes byte-identically.
- No production frontend module adopts the generated client, no schema/dependency/legacy change occurs, and unrelated
  current worktree changes remain untouched.

## Escalation boundaries

- Any new product, API, data, dependency, destructive, ownership, or acceptance decision.
- Any change to the accepted schema/indexes, canonical FEN identity, trainer-color/occurrence/distinct-game meaning,
  opening recognition, analysis lifecycle, preference tags/date resolution, error/status behavior, operation path/method,
  or sparse-read guarantee.
- Any write during a read, old-database use, migration, fallback, compatibility adapter, legacy route change, frontend
  production adoption, CLEAN-06+ behavior, or new consumer discovery.
- Any additional curated operation, generated artifact outside the approved directory, generator nondeterminism, or new
  dependency.
- Any need to modify completed CLEAN-01..04 Plans, absorb unrelated deletions or grilling changes, or perform commit,
  push, branch, worktree, stash, or broad maintenance work.

## Visible result

> A user can request one rebuilt position with explicit color and date context and receive its canonical insight, while the generated client exposes `getPositionInsight()` beside the five accepted clean operations.
