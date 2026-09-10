# POSITION-INSIGHT-01 position-insight enrichment - Counts make reach and move denominators reproducible

> **Status:** done - accepted on 2026-09-10; `CONSUMER-03` is the next selectable master-plan slice

- **Read trigger:** Before assessing, implementing, validating, repairing, accepting, or closing the
  `POSITION-INSIGHT-01` prerequisite.
- **Upstream:** [position-insight enrichment synthesis](../../../grilling-docs/database-rebuild-position-insight-enrichment.md)
  (settled response semantics); [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md)
  (order, ownership, and exclusions); accepted [CLEAN-05 Plan](../../done/database-rebuild-clean-05/database-rebuild-clean-05.md)
  (retained position-insight package, HTTP, generation, and proof seams); and [PLAN_TEMPLATE.md](../../../PLAN_TEMPLATE.md).

## Outcome

Additively enrich the existing generated `GET /api/positions/insight` response with authoritative integer counts and
explicit denominators sufficient to reproduce Position Reach Frequency and outgoing-move/terminal statistics. Preserve
every current field and meaning, keep the response on the existing `getPositionInsight` operation, and leave all
production frontend consumers unmigrated. This slice is the clean-contract prerequisite for `CONSUMER-03`.

The additions are:

```json
{
  "observed_in_games": true,
  "experience": {
    "distinct_game_count": 7,
    "occurrence_count": 8,
    "total_game_count": 10
  },
  "observed_move_totals": {
    "distinct_game_count": 7,
    "occurrence_count": 7,
    "terminal": {
      "distinct_game_count": 1,
      "occurrence_count": 1
    }
  }
}
```

`observed_in_games` is true exactly when the canonical position occurs in any imported game, independent of the
requested trainer color and independent of internal position-row existence. `experience.total_game_count` counts every
imported game with the requested trainer color, including games that never reached the position. The outgoing totals
include only requested-color occurrences with a non-null outgoing move; repeated occurrences remain repeated decisions.
The nested `terminal` totals count requested-color occurrences represented by a null outgoing move and do not dilute
the outgoing denominator. Existing `observed_moves` entries retain their trainer-color-scoped distinct-game and
occurrence meanings. No percentages, SAN, ranking, or other presentation strings are returned.

## Scope

- **Included:** The package-owned read-only position-insight query, immutable ordinary Python values and public exports;
  sparse insight totals; focused package and HTTP tests; strict HTTP response models and mapping; the existing curated
  OpenAPI response; checked-in HeyAPI regeneration and deterministic proof; handwritten central type exports if required;
  generated-surface assertions; no-production-adoption proof; and this Plan's closeout documentation/master-plan
  transition.
- **Expected areas:** `src/chess_move_trainer/database/positions/insight.py`,
  `src/chess_move_trainer/database/positions/__init__.py`, `tests/database/positions/test_insight.py`,
  `tests/database/test_package_boundary.py`, `backend/app/features/position_insight/api_schemas.py`,
  `backend/app/features/position_insight/router.py`, `backend/tests/features/position_insight/conftest.py`,
  `backend/tests/features/position_insight/test_api.py`, `backend/tests/features/health/test_contract_export.py`,
  `scripts/api/export_contract.py`, `scripts/api/generate_client.py`, `frontend/openapi-ts.config.ts`,
  `frontend/src/api/client.ts`, `frontend/src/api/generatedSurface.test.ts`, and generator-owned output under
  `frontend/src/api/generated/`; the active Plan and live master plan at closeout only.
- **Excluded:** Any schema, migration, index, projection, table, cache, dependency, database lifecycle, new endpoint,
  route retirement, fallback/dual read/compatibility adapter, `include`, frontend integration or C03 product change,
  C04-C06 adoption, percentages/SAN/rank/presentation strings, second-color response data, backend SQL outside package
  ownership, execution or reuse of legacy refresh/recurrence scripts, legacy repositories or projection reads,
  `data/database/chess_games.db`, other legacy API/database changes, edits to completed historical records, broad
  maintenance, and any commit, push, branch, worktree, or stash.

## Settled implementation facts

- The route remains `/api/positions/insight` with operation ID `getPositionInsight`; `backend/app/main.py` and route
  registration are retained.
- `datasource_game.dg_trainer_color` is the source for `total_game_count`. `derived_game_position` joined to
  `datasource_game` is the source for observation, recurrence, outgoing, terminal, and existing per-move counts.
- A null `dgp_move_uci` is terminal. Position occurrence count continues to include terminal occurrences; outgoing totals
  exclude them. Distinct counts use game IDs, while occurrence counts count rows.
- A legal position absent from `derived_position`, or present only as an unobserved internal row, succeeds sparsely with
  `observed_in_games: false`, zero selected-position counts, and the requested-color total-game denominator. Reads must
  not create rows, sidecars, or other database changes.
- Extend the existing bounded position-statistics read rather than add a projection, table, cache, or second SQL owner.
  The implementation should obtain corpus totals and selected-position aggregates in one read-only statistics query (for
  example, an aggregate/CTE result that still permits current stored-row validation and deterministic per-move ordering).
  Existing opening, analysis, preference, canonicalization, error, and connection seams remain owned as they are.
- Every chess-data calculation in this slice runs through `src/chess_move_trainer/database/` against rebuilt
  `data/database/chess.db`. Do not execute or reuse legacy refresh/recurrence scripts, legacy repositories or
  projections, or `data/database/chess_games.db`. The allowed `scripts/api/` commands only export the clean contract,
  regenerate its client, and enforce finite proof; they are not legacy data-calculation paths.
- Exact Python/Pydantic class names may be chosen in implementation within the approved field semantics. Recommended
  names are `PositionInsightObservedMoveTotals` and `PositionInsightTerminalTotals`, with corresponding HTTP models.
- Existing generated operations must remain. The endpoint is already in `scripts/api/export_contract.py`'s allow-list;
  no new allow-list operation is authorized. Generated files remain generator-owned, and production feature modules must
  not import the enriched insight operation.
- Preserve unrelated current worktree material recorded by CLEAN-05: deleted `data/database/README.md`,
  `data/database/dump_schema.py`, `data/database/schema.md`, and `data/database/schema.txt`, plus the modified
  `docs/grilling-docs/database-rebuild-api-direction.md`. Do not restore, absorb, or clean up those changes.

## Stages

Stages are sequential; no stage runs in parallel. Each stage has ordered actions, a focused proof, a boundary, and a
breakpoint. A passing proof remains valid until a later change affects its command, inputs, exercised behavior,
configuration, dependencies, or environment; later stages rerun only invalidated proof.

1. **accepted** - **Package enrichment and focused proof**
   - [x] Extend the package response dataclasses and public `positions` exports without changing existing fields or
     meanings.
   - [x] Extend the current position-statistics read in `insight.py` so it reports the requested-color game total,
     all-color corpus observation, outgoing distinct/occurrence totals, terminal distinct/occurrence totals, and the
     existing per-move values from the accepted schema-v1 tables.
   - [x] Ensure the sparse path performs the denominator/observation read while still returning a legal sparse success;
     preserve read-only connection mode, no row creation, no sidecars, stored-value validation, and deterministic move
     ordering.
   - [x] Add package proof for zero/nonzero counts, other-color-only observation, recurrence, terminal exclusion from
     outgoing denominators, total-game denominators including games that never reached the position, sparse behavior,
     and unchanged database bytes/sidecars. Include package-boundary export assertions.
   - **Focused proof:** command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q`
   - **Stage boundary:** No backend model/SQL, HTTP mapping, generated output, frontend feature, schema object, or
     master-plan acceptance change is part of this stage.
   - **Breakpoint:** none; escalate if the approved meanings cannot be derived from schema v1 in one bounded read-only
     statistics query.

2. **accepted** - **HTTP contract and focused proof**
   - [x] Add strict nonnegative integer response models and the strict boolean observation field under
     `backend/app/features/position_insight/`.
   - [x] Map the package values without adding backend SQL, changing the route/operation ID, altering error/status
     translation, or removing legacy coexistence.
   - [x] Extend the HTTP fixtures and exact response assertions for zero/nonzero, other-color-only, recurrence,
     terminal, denominator, sparse, private-ID exclusion, unknown-query tolerance, and read-only behavior.
   - **Focused proof:** command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
     `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/position_insight -q`
   - **Stage boundary:** The existing clean route remains the only insight endpoint; no production frontend module is
     changed.
   - **Breakpoint:** none; escalate if HTTP translation requires changing package ownership, current errors, or any
     settled response meaning.

3. **accepted** - **Curated OpenAPI, HeyAPI generation, determinism, and no adoption proof**
   - [x] Confirm the existing `/api/positions/insight` allow-list entry remains unchanged and the curated exporter
     includes the enriched response schemas while excluding legacy operations.
   - [x] Update only handwritten central type exports and generated-surface expectations required by the new generated
     types; do not modify production frontend feature modules or generator configuration unless a direct tooling defect
     is discovered and escalated.
   - [x] Regenerate only `frontend/src/api/generated/`, preserving all accepted operations, then prove the generated
     surface and the existing no-production-adoption guard.
   - **Focused proof:** run these in order:
     - Curated contract — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
       `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q`
     - Client generation — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
       `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py`
     - Generated surface/no adoption — command-level timeout **240 seconds**; Bash tool timeout **300000 ms**:
       `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000`
     - Deterministic `--check` — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
       `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`
   - **Stage boundary:** No new curated operation, generated artifact outside `frontend/src/api/generated/`, client
     dependency, production adoption, or legacy contract entry is authorized.
   - **Breakpoint:** none; escalate if generation is nondeterministic or changes an accepted operation surface.

4. **accepted** - **Documentation closeout and master-plan acceptance transition**
   - [x] Confirm Stages 1-3 passed and record concise proof, decisions, and which CLEAN-05 proof was rerun or retained.
   - [x] Keep this Plan pending until implementation acceptance; at closeout, record the accepted
     `POSITION-INSIGHT-01` result and move the master plan's next selectable slice to `CONSUMER-03` only after all
     acceptance conditions pass.
   - [x] Review this Plan, the enrichment synthesis, and the changed live master-plan passages for aligned semantics,
     ownership, dependency order, exclusions, and preserved historical records.
   - **Focused proof:** manual document review only; no additional behavioral command.
   - **Stage boundary:** Do not edit the accepted CLEAN-05 Plan or any historical Plan, and do not start C03 work.
   - **Breakpoint:** escalate any contradiction in approved behavior, ownership, acceptance, or later-slice timing.

## Progress and decisions

- [x] **Assessment:** retained - the package, HTTP, generated-contract, proof, ownership, and exclusion map is recorded
  in the completed assessment and upstream synthesis.
- [x] **Plan setup:** complete - this Plan and the live master-plan prerequisite amendment were reviewed; no product or
  test implementation is included.
- [x] **Stage 1:** accepted - package dataclasses, public exports, the single read-only statistics query, sparse
  denominator/observation behavior, and focused tests were completed in the approved four-file scope. Proof passed:
  `20 passed` for the Stage 1 command with its 180-second command timeout and 240000 ms tool timeout.
- [x] **Stage 2:** accepted - strict HTTP models, direct package-value mapping, and exact response coverage were
  completed in the approved four-file backend scope without package edits or backend SQL. Proof passed: `17 passed`
  for the Stage 2 command with its 180-second command timeout and 240000 ms tool timeout; Stage 1 proof remains
  retained.
- [x] **Stage 3:** accepted - curated contract assertions, central type exports, generated-surface expectations, and
  generator-owned output were updated without changing the allow-list, operation IDs, tooling/configuration, or any
  production feature module. Proof passed in order: curated contract `4 passed`; client generation succeeded;
  generated surface/no adoption `6 passed`; deterministic check reported `18 files byte-identical`. Stages 1-2 proof
  remains retained.
- [x] **Stage 4:** accepted - manual review found the Plan, enrichment synthesis, and live master-plan transition
  aligned on semantics, ownership, dependency order, exclusions, and preserved historical records. All acceptance
  conditions passed, `POSITION-INSIGHT-01` was accepted, and `CONSUMER-03` became the next selectable slice without
  starting C03 work.
- **Retained-proof rule:** Accepted CLEAN-01 through CLEAN-04, C02, schema-v1, ownership, route coexistence, and
  historical CLEAN-05 records remain retained. CLEAN-05's superseded package/HTTP response-shape and generated-schema
  proof was replaced by the passing Stage 1-3 proof recorded above; canonicalization, opening, analysis, preference,
  error, and no-write expectations remain retained regression evidence.

## Proof

1. Package behavior — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
   `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest tests/database/positions/test_insight.py tests/database/test_package_boundary.py -q`
2. HTTP behavior — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
   `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/position_insight -q`
3. Curated contract — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
   `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe -m pytest backend/tests/features/health/test_contract_export.py -q`
4. Client generation — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
   `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py`
5. Generated surface/no adoption — command-level timeout **240 seconds**; Bash tool timeout **300000 ms**:
   `.venv/Scripts/python.exe scripts/api/finite.py 240 npx.cmd vitest run --config frontend/vitest.api.config.ts --testTimeout 15000`
6. Deterministic `--check` — command-level timeout **180 seconds**; Bash tool timeout **240000 ms**:
   `.venv/Scripts/python.exe scripts/api/finite.py 180 .venv/Scripts/python.exe scripts/api/generate_client.py --check`

These are the complete implementation proof set for this Plan. No lint, formatting, broad type/build, source-size,
aggregate maintenance, repository-hygiene, or complete-suite proof is included.

## Acceptance

- The existing `/api/positions/insight` path and `getPositionInsight` operation ID remain unchanged.
- Every current response field and meaning remains intact, and the approved `observed_in_games`,
  `experience.total_game_count`, `observed_move_totals`, and nested terminal totals are present as authoritative
  boolean/integer data.
- Package and HTTP proof demonstrates correct zero/nonzero, other-color-only, recurrence, terminal, and denominator
  semantics; sparse legal positions remain successful and read-only with no row, byte, or sidecar change.
- SQL, chess, filtering, aggregation, and storage meaning remains package-owned; no schema or database object changes
  occur; legacy routes continue to coexist.
- The curated OpenAPI response and checked-in HeyAPI client are current and deterministic; every accepted generated
  operation remains; no legacy operation enters the generated contract; and no production frontend module adopts insight.
- No C03, C04-C06, frontend integration, fallback, compatibility adapter, route retirement, or historical-record change
  is included.

## Escalation boundaries

- Any schema, migration, index, projection, table, cache, dependency, database lifecycle, new endpoint, route
  retirement, fallback/dual read/compatibility adapter, or second SQL owner.
- Any change to existing field names or meanings, trainer-color filtering, occurrence/distinct-game meaning, terminal
  representation, canonical FEN/date/error behavior, sparse success, read-only behavior, or operation path/ID.
- Any percentage, SAN, rank, presentation string, second-color dataset, private-ID exposure, unbounded query, or
  production frontend adoption.
- Any legacy API/database change, C03 or later consumer work, generated output outside the approved directory,
  any execution or reuse of legacy data scripts/repositories/projections, any read of `data/database/chess_games.db`,
  generator nondeterminism, dependency change, or need to modify a completed historical record.
- Any request for lint, formatting, broad type/build, source-size, aggregate maintenance, repository-hygiene,
  branch/worktree/stash, commit, or push work.

## Visible result

> A later consumer can read a position's complete game denominator and move/terminal counts from the same generated
> insight endpoint without guessing or receiving preformatted percentages.
