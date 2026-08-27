# Normalize analysis identity across FEN counters - Same position yields one analysis and queue identity

> **Status:** pending - Plan written; stages are unstarted and the live migration gate remains pending.

- **Read trigger:** Read before dispatching each sequential stage of this analysis/evaluation identity migration.
- **Upstream:** none; coordinator-approved assessment facts are the settled input.

## Outcome

Analysis results, candidate selection, and evaluation queue identity use one internal four-field `PositionKey`
for the same board state, even when valid public six-field FENs differ only in halfmove/fullmove counters.
Public callers continue submitting and receiving ordinary valid six-field FENs.

## Scope

- **Included:** Keep strict six-field `canonical_fen` in `backend/app/features/analysis/models.py` and add clearly named `PositionKey` / `position_key_from_fen` behavior. Normalize analysis result/candidate persistence, analysis selection grouping, analysis engine/repository use, and evaluation queue identity to placement, side to move, castling rights, and en-passant state. Update the v1 SQLite schema and a narrowly scoped migration/reset path. Reset disposable analysis results, candidate moves, and active evaluation queue entries without collision merging or winner selection. Preserve historical batch/failure records only when ordinary schema work can keep them straightforward and truthful. Keep public API FEN fields six-field, and normalize exact-FEN identity comparisons in the viewer analysis API/state. Update generated schema documentation and focused tests.
- **Expected areas:** `backend/app/features/analysis/models.py`; `backend/app/features/analysis/schema.py`; `backend/app/features/analysis/repository.py`; `backend/app/features/analysis/selection.py`; `backend/app/features/analysis/engine.py`; `backend/app/features/evaluation/schema.py`; `backend/app/features/evaluation/queue.py`; `backend/app/features/evaluation/service.py`; `backend/app/features/evaluation/api_schemas.py`; `backend/app/features/evaluation/router.py`; narrowly scoped migration support owned by the existing SQLite schema modules; `backend/tests/features/analysis/test_schema_and_models.py`; `backend/tests/features/analysis/test_persistence.py`; `backend/tests/features/analysis/test_engine.py`; `backend/tests/features/analysis/test_operator.py`; `backend/tests/features/analysis/test_coexistence.py`; `backend/tests/features/evaluation/test_schema.py`; `backend/tests/features/evaluation/test_queue.py`; `backend/tests/features/evaluation/test_service.py`; `backend/tests/features/evaluation/test_api.py`; `frontend/src/features/viewer/analysisApi.ts`; `frontend/src/features/viewer/analysisState.ts`; `frontend/src/features/viewer/analysisApi.test.ts`; focused viewer analysis-state tests if needed; `data/database/dump_schema.py`; generated `data/database/schema.txt`.
- **Excluded:** Counter-dependent endgame, fifty-move, repetition, tablebase, or draw semantics; future APIs or pages; stored-game FEN changes; `position_state` and preferred-move schema or behavior; unrelated routes and features; compatibility aliases that expose four-field FENs; a generalized migration framework, new dependency, enterprise backup/recovery, hashing, elaborate integrity or audit infrastructure, or collision tooling; changes to completed historical Plans or unrelated historical data; edits to `docs/plans/active/remove-legacy-position-route/` (there is no direct path overlap, so execution is serialized and its baseline is refreshed only if that Plan changes); commits and pushes.

## Stages

1. **pending - establish the internal key and prove the schema transition in temporary SQLite.**
   - **Ordered actions:** Define the four-field `PositionKey` conversion from a valid six-field FEN while retaining strict `canonical_fen` and public six-field values. Update analysis and evaluation schema ownership and the smallest affected persistence contracts so result/candidate and queue identity are keyed by `PositionKey`. Add a temporary/test database fixture representing v1 six-field rows, counter-only FEN variants, disposable rows, and any straightforward historical batch/failure rows. Implement one ordinary transactional schema transition/reset that clears disposable results, candidates, and active queue entries without merging collisions or selecting winners; leave historical batch/failure records alone only when their meaning remains truthful, otherwise stop for escalation. Do not touch the live database in this stage.
   - **Focused proof:** Temporary SQLite tests build the old and new schema, exercise two valid six-field counter variants, verify one four-field identity, verify disposable analysis/evaluation rows are reset, and verify the selected historical-record behavior. Run the focused analysis/evaluation schema, persistence, and queue pytest coverage.
   - **Breakpoint:** none; live database access is explicitly out of bounds.
   - **Escalation boundary:** Stop if the existing schema cannot express the four-field identity with ordinary transactional changes, if historical batch/failure truth cannot be preserved simply, or if collision handling or a new migration framework appears necessary.
2. **pending - wire normalized identity through backend behavior and viewer comparisons.**
   - **Ordered actions:** Update analysis repository, selection grouping, engine, and evaluation queue/service/API/router paths to derive identity from `PositionKey` while accepting and returning six-field FENs. Ensure counter-only FEN differences deduplicate analysis and queue work, while genuinely different placement, side, castling, or en-passant fields remain distinct. Update `analysisApi.ts` and `analysisState.ts` so exact-FEN comparisons use normalized identity without changing the public FEN shape. Regenerate `data/database/schema.txt` from the supported in-memory schema and retain only the resulting schema artifact changes. Add focused backend and frontend regression tests.
   - **Focused proof:** `.venv/Scripts/python.exe -m pytest backend/tests/features/analysis backend/tests/features/evaluation -q`; `npm.cmd run test --prefix frontend -- --run src/features/viewer/analysisApi.test.ts src/features/viewer/analysisState.test.ts`; `.venv/Scripts/python.exe -m pytest tests/database/test_schema.py -q`; `.venv/Scripts/python.exe data/database/dump_schema.py --check`.
   - **Breakpoint:** none.
   - **Escalation boundary:** Stop if any public caller must send or receive a four-field FEN, if counter-dependent rules are required, if `position_state` or preferred moves must change, or if an unlisted route, dependency, or ownership boundary is implicated.
3. **pending - perform the simple gated live migration/reset and application proof.**
   - **Ordered actions:** Pause for explicit human/coordinator approval immediately before the destructive live stage, confirming the implementation proof and current serialized baseline. After approval, stop every process using SQLite. Make exactly one ordinary file-copy backup from `data/database/chess_games.db` to `data/database/chess_games.db.position-key.backup`, with no hashing or additional recovery system. Run the schema migration/reset transaction against the live database. If it fails, stop, reinstate the original by copying that backup back over `data/database/chess_games.db`, verify the database can be opened, and escalate rather than repairing or retrying by improvisation. If it succeeds, restart the normal application services and run focused application proof using counter-only six-field FEN variants, asserting one analysis identity/queue item and six-field public values; then remove or otherwise keep the temporary backup out of commits according to coordinator closeout direction.
   - **Focused proof:** The temporary-database transition proof plus the focused backend analysis/evaluation pytest, viewer analysis tests, and schema check are rerun after the live transition; the targeted application/API proof confirms the migrated database behaves as specified. Finish with the read-only `.venv/Scripts/python.exe scripts/check.py` closeout.
   - **Breakpoint:** **Human gate required before stopping processes, copying the backup, or changing the live database.** No live migration is performed while writing this Plan.
   - **Escalation boundary:** Do not proceed without the gate. Escalate any migration failure, inability to restore the copied file, unexpected live rows or schema, concurrent change to the serialized baseline, or request for more elaborate recovery/collision behavior.

Stages are sequential; no stages run in parallel.

## Progress and decisions

- **Assessment:** done - the approved four-field identity, six-field public contract, disposable reset policy, exclusions, and simple live-migration requirement were captured; the active legacy-route Plan has no direct path overlap.
- **Stage 1:** pending - proof: temporary SQLite schema-transition/reset tests and focused backend schema/persistence/queue coverage; breakpoint: none.
- **Stage 2:** pending - proof: focused backend analysis/evaluation pytest, viewer Vitest coverage, database schema tests, and generated-schema check; breakpoint: none.
- **Stage 3:** pending - proof: gated live migration/reset followed by focused application proof and full read-only closeout; breakpoint: explicit human approval before the destructive stage.

## Proof

- Temporary SQLite proof covers schema transition, counter-only FEN identity collapse, disposable reset, and truthful handling of historical batch/failure rows.
- `.venv/Scripts/python.exe -m pytest backend/tests/features/analysis backend/tests/features/evaluation -q`
- `npm.cmd run test --prefix frontend -- --run src/features/viewer/analysisApi.test.ts src/features/viewer/analysisState.test.ts`
- `.venv/Scripts/python.exe -m pytest tests/database/test_schema.py -q`
- `.venv/Scripts/python.exe data/database/dump_schema.py --check`
- `.venv/Scripts/python.exe scripts/check.py` in read-only mode for full closeout.

## Escalation boundaries

- Any request to change the public six-field FEN contract, stored-game FENs, `position_state`, preferred moves, future APIs/pages, or counter-dependent chess semantics.
- Any need to merge colliding derived rows, choose winners, rewrite historical batch/failure meaning, add collision tooling, or preserve disposable analysis/queue data.
- Any need for a generalized migration framework, new dependency, enterprise recovery, hashes, migration audit infrastructure, or multiple backup layers; the approved route is one ordinary file copy and restore.
- Any direct path overlap or concurrent baseline change involving `remove-legacy-position-route`; the coordinator must serialize execution and refresh the baseline before dispatch.
- Any failed live migration, failed restoration, unexpected database state, unrelated check failure, or request to commit or push; report and return to the coordinator without absorbing it.

## Visible result

> Submitting two valid six-field FENs that differ only in their counters produces one analysis identity and one evaluation queue item, while callers still receive six-field FENs.
