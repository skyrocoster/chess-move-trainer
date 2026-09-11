# Database rebuild

> **Status:** direction settled; CLEAN-01 through CLEAN-10, CONSUMER-01, VIEWER-REMOVE-01,
> CONSUMER-02, `POSITION-INSIGHT-01`, and `CONSUMER-03` through `CONSUMER-06` accepted
> **Next selectable slice:** `RETIRE-01` — remove the old game-position route after its retained consumer migrated;
> see the accepted [CONSUMER-06 Plan](../../plans/done/database-rebuild-consumer-06/database-rebuild-consumer-06.md).
> **Acceptance:** The accepted database foundation, SETUP-01, and SETUP-02 remain intact; every clean operation is created and generated individually; every retained production API workflow is migrated individually afterward; and legacy routes are retired only after their final consumers move.

## Destination

Expose the rebuilt chess data through one coherent, reusable HTTP API, keep its checked-in HeyAPI client current after
every new operation, and then move each retained production workflow to that client without compatibility shims,
screen-shaped backend contracts, or a global database cutover.

This master plan records direction and selectable slices. It does not authorize implementation. Each slice requires
coordinator approval and a focused Plan when nontrivial.

## Why this master plan was replaced

The former master plan organized future work as `API-01` through `API-04` around the current frontend screens. The
confirmed [database-rebuild API direction](../../grilling-docs/database-rebuild-api-direction.md) instead settles the
whole useful API first, then migrates individual consumers. It is authoritative for API semantics, repository
placement, generation order, coexistence, migration, and exclusions. This document replaces the old future sequence
rather than retrofitting it, while preserving all completed foundation, SETUP-01, and SETUP-02 evidence.

## Settled direction

### Public capability inventory

Health is already implemented and generated. The remaining operations are created one at a time in this order:

```text
GET     /api/health                         completed by SETUP-02

GET     /api/games                         CLEAN-01
GET     /api/games/{game_uuid}             CLEAN-02
GET     /api/openings                      CLEAN-03
GET     /api/openings/{opening_key}        CLEAN-04
GET     /api/positions/insight             CLEAN-05
GET     /api/analysis                      CLEAN-06
POST    /api/analysis-requests             CLEAN-07
GET     /api/preferred-moves               CLEAN-08
PUT     /api/preferred-moves               CLEAN-09
DELETE  /api/preferred-moves               CLEAN-10
```

Every `CLEAN-*` slice adds exactly one operation, its clean package capability, its thin HTTP adapter, and its focused
proof. Before that slice can be accepted, the operation is added to the curated OpenAPI export and the checked-in
HeyAPI output is regenerated and proven deterministic. Generated output therefore never lags behind an accepted API
operation. No production frontend usage adopts a clean operation during API creation.

### Contract principles

- FEN is the public position identity; SQLite position IDs remain private. Complete legal FENs are canonicalized by
  placement, side to move, castling, and legal en-passant. Game occurrences retain their move counters for replay.
- Legal positions absent from stored games are valid. Reads do not create rows; an analysis request or preferred-move
  edit may resolve/create the internal position as part of that purposeful write.
- Unknown request query/body fields are ignored, additive response fields are tolerated, and known invalid values or
  invalid combinations are rejected.
- The backend owns chess, temporal, filtering, and aggregation meanings. Callers supply explicit context rather than
  rebuilding those meanings.
- Clean and legacy routes coexist temporarily without `/api/v2`, fallback, or compatibility adapters. Only clean
  operations enter the curated OpenAPI/HeyAPI contract.
- Exact field spelling, finite page-size limits, and error codes may be settled in focused planning only when these
  semantics remain unchanged.

### Capability semantics

- **Games:** `GET /api/games` is one typed, rich, combined-filter search over normalized game facts and direct opening,
  position, outgoing-move, length, analysis, and preferred-move relationships. It uses `page`/`page_size`, deterministic
  sorts, and rich summaries rather than full timelines. `GET /api/games/{game_uuid}` returns complete metadata, original
  PGN, and ordered occurrences with outgoing moves.
- **Openings:** the collection and detail operations expose a flat searchable catalogue with reusable API keys, ECO and
  label data, route counts, and reached/deepest game-usage meanings. They do not expose route moves, a hierarchy, or
  Opening Line Library behavior.
- **Position insight:** `GET /api/positions/insight` requires `fen`, `trainer_color`, and `as_of` and always returns
  canonical position data, current opening recognition, trainer-color-filtered experience, observed outgoing moves,
  current analysis state/result, and the date-resolved preference. Its additive counts include the requested-color
  all-games denominator, an all-color imported-game observation flag, explicit outgoing distinct-game/occurrence totals,
  and separate terminal distinct-game/occurrence totals. Existing fields and meanings remain intact. It has no `include`
  or screen-specific variant, returns integer counts rather than percentages or presentation strings, and does not add a
  second-color dataset. Unseen legal positions succeed sparsely without a write; move history contains observed moves
  only, with explicit distinct-game and occurrence meanings; legal-move generation remains in the existing frontend chess
  library.
- **Analysis:** focused observation uses `not_requested -> queued -> running -> ready` without revealing internal row
  existence. Requests ask for the desired result, not Analyze/Update/Retry actions. Quality is optional `browser` or
  `tool`, defaults to `browser`, and exposes no arbitrary engine settings. Repeats/concurrent requests are duplicate-safe
  and sufficient higher-quality results are reused. The contract has one current complete result and live queue state,
  not old batch, attempt, partial-result, downgrade, or persisted-failure history.
- **Preferred moves:** a preference is **the outgoing move after the supplied parent FEN**, not the resulting position or
  a stored repertoire line. Values are tagged `{kind: "move", uci: "..."}` or `{kind: "no_preference"}`; deleting an
  interval produces `unconfigured`. Mutations require `effective_from`, allow an optional exclusive `effective_until`,
  and atomically overlay/remove normalized periods. Reads require a finite `from`/`until` window and return contiguous
  segments covering it, including derived unconfigured gaps. Callers do not calculate splits, merges, gaps, overlaps,
  or active dates.

### Repository ownership

```text
FastAPI routes and HTTP models         backend/app/features/
Database capabilities and queries      src/chess_move_trainer/database/
Generated TypeScript contract          frontend/src/api/generated/
```

The rebuilt package is the only owner of SQL, transactions, canonical chess/data behavior, and reusable reads/writes.
It accepts explicit database paths and returns ordinary Python values without FastAPI or HTTP Pydantic types. Thin
backend feature adapters own routing, HTTP schemas, and status/error translation; they do not add another raw-SQL
`repository.py` stack. One backend dependency supplies the rebuilt database path instead of importing configuration
from the legacy positions repository. The package never imports `backend`.

Package tests remain under `tests/database/<domain>/`; HTTP tests remain under
`backend/tests/features/<feature>/`. Existing handwritten export/generation files remain under `scripts/api/` and
`frontend/openapi-ts.config.ts`; all generated files remain under `frontend/src/api/generated/`; and runtime client
configuration remains in `frontend/src/api/client.ts`.

## Completed foundation retained as evidence

The database foundation is accepted and not reopened. `src/chess_move_trainer/database/` owns the fixed lifecycle,
explicit SQLite access, canonical positions, game acquisition/import/reads, opening acquisition/catalogue recognition,
preferred-move normalization, current analysis publication/reads, and serialized Stockfish queue/worker behavior. The
only public data-loading workflows remain `setup`, `update games`, and `update openings`, targeting
`data/database/chess.db`. Operator commands do not become application HTTP endpoints.

Schema version 1 retains exactly these ten tables:

```text
datasource_game
derived_position
derived_game_position
datasource_opening
derived_opening_route
derived_opening_route_move
derived_analysis_result
derived_analysis_line
derived_analysis_queue
datasource_preferred_move_period
```

There are no feature-specific schema, run, history, projection, manifest, audit, batch, failure, hierarchy, or
classification table families. No old rows migrated; the old database and raw sources remain retained and unmodified.

The accepted `data/database/chess.db` evidence is:

```text
12,710 games
530,725 canonical positions
657,654 game-position occurrences
3,329 opening labels
3,810 opening routes
36,925 route moves
1 analysis result with 5 candidate lines
108 preferred-move periods across 91 positions
0 queued analysis requests
```

The 32-month source ledger held 12,716 records: 12,710 accepted and 6 explicitly rejected, with no duplicate normalized,
source, or database identifiers. Integrity, foreign-key, direct-read performance, ledger, DB-09, and bounded Stockfish
proof passed. SETUP-01 then inferred and atomically applied the accepted 108 periods. No API, frontend, cutover, broad
maintenance run, or old-database operation was part of that acceptance.

- **SETUP-01:** the fixed empty-schedule-only preferred-move inference command is accepted; it now refuses the nonempty
  schedule and added no API/frontend/schema/history behavior.
- **SETUP-02:** health-only deterministic OpenAPI export and checked-in HeyAPI generation are accepted; `getHealth()`
  passed a real bounded call, and no production module adopted it.

Completed evidence remains in the [DB-01](../../plans/done/database-rebuild-db-01/database-rebuild-db-01.md),
[DB-02](../../plans/done/database-rebuild-db-02/database-rebuild-db-02.md),
[DB-03](../../plans/done/database-rebuild-db-03/database-rebuild-db-03.md),
[DB-04](../../plans/done/database-rebuild-db-04/database-rebuild-db-04.md),
[DB-05](../../plans/done/database-rebuild-db-05/database-rebuild-db-05.md),
[DB-06](../../plans/done/database-rebuild-db-06/database-rebuild-db-06.md),
[DB-07](../../plans/done/database-rebuild-db-07/database-rebuild-db-07.md),
[DB-08](../../plans/done/database-rebuild-db-08/database-rebuild-db-08.md),
[DB-08A](../../plans/done/database-rebuild-db-08a/database-rebuild-db-08a.md),
[DB-09](../../plans/done/database-rebuild-db-09/database-rebuild-db-09.md),
[SETUP-01](../../plans/done/database-rebuild-setup-01/database-rebuild-setup-01.md), and
[SETUP-02](../../plans/done/database-rebuild-setup-02/database-rebuild-setup-02.md) Plans. Governing retained references
also include [simple lifecycle](../../grilling-docs/database-rebuild-simple-lifecycle.md),
[database direction](../../grilling-docs/database-rebuild-direction.md),
[schema direction](../../grilling-docs/database-rebuild-schema.md),
[DB-09 proof](../../grilling-docs/database-rebuild-db-09.md),
[SETUP-01 direction](../../grilling-docs/database-rebuild-setup-01.md),
[SETUP-02 direction](../../grilling-docs/database-rebuild-setup-02.md), [Viewer removal direction](../../grilling-docs/database-rebuild-viewer-removal.md), [expanded CONSUMER-02 grilling record](../../grilling-docs/database-rebuild-consumer-02.md), [position-insight enrichment synthesis](../../grilling-docs/database-rebuild-position-insight-enrichment.md), and the generated
[schema reference](../../../data/database/schema.md).

## Selectable slices

All slices are sequential. Each is independently selectable and reviewable, but none is implementation authorization.

| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| `CLEAN-01` | Rich paginated game search is available and generated. | SETUP-02 | No frontend adoption or legacy removal. |
| `CLEAN-02` | Complete game detail by UUID is available and generated. | CLEAN-01 | No game-consumer migration or fallback. |
| `CLEAN-03` | The flat searchable opening catalogue is available and generated. | CLEAN-02 | No route moves, tree, or line library. |
| `CLEAN-04` | Flat opening detail and usage are available and generated. | CLEAN-03 | No hierarchy or frontend adoption. |
| `CLEAN-05` | Complete sparse-capable position insight is available and generated. | CLEAN-04 | No hidden writes, legal-move list, or screen variant. |
| `CLEAN-06` | Focused current analysis observation is available and generated. | CLEAN-05 | No old action/history contract. |
| `CLEAN-07` | Desired-result analysis requests are available and generated. | CLEAN-06 | No arbitrary settings or batch API. |
| `CLEAN-08` | Finite complete preferred-move timelines are available and generated. | CLEAN-07 | No caller-side calendar arithmetic. |
| `CLEAN-09` | Preferred move/no-preference intervals can be overlaid and generated. | CLEAN-08 | No frontend adoption or repertoire lines. |
| `CLEAN-10` | Preferred-move intervals can be removed and the operation is generated. | CLEAN-09 | No legacy removal or data cleanup. |
| `CONSUMER-01` | Status uses generated `getHealth()`. | CLEAN-10 | No other frontend adoption. |
| `VIEWER-REMOVE-01` | Production Viewer is gone; `/viewer` falls through to ordinary Not Found and Repertoire is unchanged. | CONSUMER-01 | No clean API adoption, backend route retirement, or Viewer-only behavior preservation. |
| `CONSUMER-02` | Repertoire loads complete clean game detail into one navigable session: full imported history, immediate moves, one temporary alternative, and explicit parent-based Preferred Move selection. | VIEWER-REMOVE-01 | No Viewer migration, fallback, later-consumer API migration, or legacy-route retirement. |
| `POSITION-INSIGHT-01` | The existing generated position insight adds authoritative game, observation, outgoing-move, and terminal counts. | CLEAN-05, CONSUMER-02 | No new endpoint, schema change, frontend adoption, percentages, presentation strings, or C03 product change. |
| `CONSUMER-03` | Repertoire position context uses the enriched generated clean insight. | POSITION-INSIGHT-01 | No Viewer or move-response migration. |
| `CONSUMER-04` | Repertoire move-response distribution uses clean observed-move insight. | CONSUMER-03 | No new projection. |
| `CONSUMER-05` | Repertoire selected/current-position analysis uses the clean lifecycle. | CONSUMER-04 | No Viewer migration or compatibility layer. |
| `CONSUMER-06` | Repertoire uses clean preferred timelines and interval mutations. | CONSUMER-05 | No calendar UI or authored repertoire lines. |
| `RETIRE-01` | The old game-position route is removed after the retained game consumer migrates. | CONSUMER-06 | No old-database cutover/deletion. |
| `RETIRE-02` | The old position-context route is removed after the retained context consumer migrates. | RETIRE-01 | No recurrence migration. |
| `RETIRE-03` | The old move-response route is removed after its Repertoire consumer migrates. | RETIRE-02 | No new projection. |
| `RETIRE-04` | The old evaluation read/action/status routes are removed after the retained analysis consumer migrates. | RETIRE-03 | No queue-history compatibility. |
| `RETIRE-05` | The old preferred-move operations are removed after the retained Repertoire consumer migrates. | RETIRE-04 | No old-database cleanup. |
| `RETIRE-06` | The unused Opening Line Library route is removed after a final no-consumer audit. | RETIRE-05 | No replacement or rebuild. |

## Slice envelopes

### Clean operation creation

Each `CLEAN-*` slice must preserve the matching capability semantics above and:

1. add or extend the owning explicit-path package capability under `src/chess_move_trainer/database/`;
2. add one thin operation under `backend/app/features/` without backend SQL;
3. add focused package and HTTP contract proof, including read-only/atomic/concurrency behavior where applicable;
4. add only that operation to the curated exporter;
5. run finite client generation and deterministic `--check` proof immediately; and
6. prove all previously accepted clean operations remain generated, no legacy route entered the contract, and no
   production frontend module adopted the client.

The focused Plan for each slice must name exact finite commands and timeouts. Lint, formatting, broad type/build,
source-size, aggregate maintenance, and repository-hygiene checks are not implementation proof.

### Production Viewer removal

`VIEWER-REMOVE-01` is a dedicated frontend removal slice after `CONSUMER-01` and before the remaining retained
consumer migrations. It removes the production Viewer route, navigation, workspace, Viewer-only exploratory play, and
unused Viewer artifacts; relocates only shared capabilities still needed by retained production features; and proves
ordinary Not Found behavior plus unchanged Repertoire behavior. It adopts no clean generated operation, retires no
backend route, and does not preserve a redirect, compatibility surface, or Viewer-only behavior.

### Individual production consumer migrations

These begin only after `CLEAN-10`. Each slice moves one production workflow to the already-generated client, preserves
that workflow's visible behavior except where the clean contract or confirmed slice-specific direction deliberately
changes it, and proves no other consumer moved silently.

| Slice | Current production usage | Clean operations | Primary current area |
|---|---|---|---|
| `CONSUMER-01` | Status health check | `GET /api/health` | `frontend/src/features/status/` |
| `CONSUMER-02` | Repertoire game loading | game detail | `frontend/src/features/repertoire-builder/` |
| `CONSUMER-03` | Repertoire position context | enriched position insight with required trainer color, `as_of`, and approved observation/denominator fields | `frontend/src/features/repertoire-builder/` |
| `CONSUMER-04` | Repertoire move-response distribution | observed moves in position insight | `frontend/src/features/move-response-distribution/`, `repertoire-builder/` |
| `CONSUMER-05` | Repertoire selected/current-position analysis workflow | analysis GET/POST | `frontend/src/features/repertoire-builder/` |
| `CONSUMER-06` | Repertoire preferred resolve/read/write/delete workflow | preferred GET/PUT/DELETE | `frontend/src/features/repertoire-builder/` |

`VIEWER-REMOVE-01` relocates only the shared modules that retained Repertoire behavior still needs; it does not migrate
Repertoire to a clean operation. The remaining consumer slices are Repertoire-only. After `CONSUMER-02`, `CONSUMER-05`
covers the one selected/current-position Repertoire analysis workflow rather than preserving a parent-versus-displayed-
position split. It remains one workflow because it shares one injected analysis client and one user-visible analysis
interaction; a focused assessment may split it only if independent migration is required without changing the outcome.
Any shared-module change that would silently migrate another listed workflow must stop for coordinator scope review.
Unmigrated usages remain explicitly documented as expected legacy usage or expected breakage; no adapter or fallback
hides them.

`CONSUMER-02` is the confirmed expanded game-session slice. Its focused Plan moves Repertoire from the legacy game
lookup and staged preview into a direct generated `getGame()` load, retaining the complete immutable imported main
line at Ply 0. The selected position drives the existing panels; every move advances immediately; a divergent move
creates only one disposable linear branch with a Return to game action; and the selected trainer transition carries
its parent FEN and outgoing UCI for explicit Preferred Move actions. This does not migrate any later consumer API,
retire `/api/games/{game_uuid}/positions`, add a cache or fallback, or introduce persistence or a repertoire tree.

`CONSUMER-06` adopts the clean interval API needed by later calendar work but does not design or build that future
calendar interface. It must remove the current corpus-only save restriction so a legal novel parent FEN can be
configured. The backend continues to own interval calculation.

### Explicit legacy-route retirement

Retirement is separate from consumer migration. Each retirement slice performs a bounded production-consumer audit,
removes only the named legacy HTTP surface and now-unused adapter code, and proves the clean generated operations remain.

| Slice | Legacy surface | Required migrated consumers |
|---|---|---|
| `RETIRE-01` | `/api/games/{game_uuid}/positions` | CONSUMER-02 |
| `RETIRE-02` | `/api/position-context` | CONSUMER-03 |
| `RETIRE-03` | `/api/move-response-distribution` | CONSUMER-04 |
| `RETIRE-04` | `/api/evaluation` GET/POST and `/api/evaluation/status` | CONSUMER-05 |
| `RETIRE-05` | `/api/preferred-move` GET/PUT/DELETE | CONSUMER-06 |
| `RETIRE-06` | `/api/openings/line-library` | no production consumer; final bounded audit required |

Health remains. Route retirement never implies old-database cleanup or deletion.

## Slice results

- **Accepted:** `CLEAN-01` through `CLEAN-10`, `CONSUMER-01`, `VIEWER-REMOVE-01`, `CONSUMER-02`,
  `POSITION-INSIGHT-01`, and `CONSUMER-03` through `CONSUMER-06`.
- **Next selectable:** `RETIRE-01`.

## Risks and escalation boundaries

- Accepted `VIEWER-REMOVE-01` removed Viewer and relocated retained game, position-context, analysis, chess, and board
  modules into neutral ownership. Future consumer slices must preserve those individual workflow boundaries without
  reintroducing compatibility or Viewer behavior.
- The expanded `CONSUMER-02` session outcome crosses the existing game mapping, navigation, move, and Preferred Move
  seams. Its Plan must keep the imported main line immutable, avoid reintroducing staged parent/child state, and prove
  that selected-position workflows remain lazy while later consumer APIs remain unmigrated.
- Current clean package seams include game detail, opening recognition, current analysis reads/publication, queue
  primitives, position resolution, and preferred period normalization. Rich search, flat opening reads, composed
  insight, FEN-facing analysis orchestration, and complete finite timelines need focused assessment, but never justify a
  second backend SQL stack.
- Exact API names may be settled only within the confirmed semantics. Escalate any change to behavior, route direction,
  dependency, accepted schema, ownership, destructive effect, or acceptance.
- Escalate if query proof requires changing the accepted schema, if a new production consumer is discovered, if a
  consumer cannot migrate independently, if Viewer cannot be removed completely, or if a legacy route cannot retire
  after its stated consumers move.

## Exclusions

- No database lifecycle, source update, Stockfish worker, bulk analysis, schema inspection, or other operator command
  becomes an application HTTP endpoint.
- No new table family, opening tree, Opening Line Library rebuild, repertoire-line store, hierarchy, classification,
  recurrence, projection, history, audit, batch, failure, or per-feature state/run data model.
- No automatic preferred-move inference/application beyond accepted SETUP-01. Manual preferred-move HTTP edits are the
  approved behavior and are not excluded by this boundary.
- No old-database row migration, fallback, physical activation, global cutover, cleanup, deletion, or rollback design.
  Raw sources and completed workflow records remain retained.
- `VIEWER-REMOVE-01` performs no clean generated API adoption, backend route retirement, or old-database work.
- No opponent-profile work under `data/chess-com/raw/profiles/`.
- No production frontend adoption during `CLEAN-*`; no legacy operation in curated OpenAPI/HeyAPI; no generic query
  language, `/api/v2`, compatibility adapter, silent cross-consumer migration, loose canonical script, commit, push,
  branch, worktree, stash, broad maintenance closeout, or unrelated change.
