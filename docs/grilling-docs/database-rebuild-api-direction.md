# Database rebuild API direction

> **Status:** confirmed on 2026-09-09
> **Purpose:** Durable direction for replacing the staged API portion of the database-rebuild master plan.
> **Authority:** This records the decisions reached with the user. It is not a Plan, implementation authorization,
> application cutover, or frontend integration approval.

## Why this direction was settled first

The existing database-rebuild master plan proceeds through separate `API-01` through `API-04` outcomes shaped around
the current frontend features. Before continuing that sequence, the user chose to inventory the whole useful HTTP
surface and settle a coherent API philosophy.

The user accepts that the clean API may break current frontend features. Compatibility endpoints and old-contract
fallbacks are not required. The resulting frontend breakages must instead be documented for later repair.

When planning resumes, the intended route is to **replace the current database-rebuild master plan as a whole**, not
retrofit these decisions into its existing API stages. That replacement remains future planning work; this record does
not edit or authorize execution of the master plan.

## API ethos

The API should expose reusable chess and training capabilities rather than database tables or endpoints named after
current screens. Reads should return substantial answers for common work, while commands that change state should
remain focused.

The settled rules are:

- Use FEN as the public position identity. SQLite row identifiers remain private.
- Accept a complete legal FEN, canonicalize the position-defining placement, side-to-move, castling, and legal
  en-passant fields, and retain game-occurrence move counters where they matter to game replay.
- Permit legal positions that have never appeared in a stored game.
- Keep reads free of hidden writes. The first purposeful analysis request or preferred-move edit may resolve and create
  an internal position row when needed.
- Ignore unknown request query/body fields and allow clients to ignore additional response fields. Still reject known
  fields with invalid values and known invalid combinations.
- Let the backend own chess, temporal, filtering, and aggregation meaning. A caller supplies context such as trainer
  color, date, FEN, and a requested date window; it does not reconstruct those meanings itself.
- Use ordinary typed HTTP parameters and models rather than a generic query language.
- Export every approved clean operation through the curated OpenAPI contract and generate the complete typed
  TypeScript client with HeyAPI. Legacy operations remain outside that contract even if temporarily registered.

## Approved public capability inventory

The directional public surface is:

```text
GET     /api/health

GET     /api/games
GET     /api/games/{game_uuid}

GET     /api/openings
GET     /api/openings/{opening_key}

GET     /api/positions/insight

GET     /api/analysis
POST    /api/analysis-requests

GET     /api/preferred-moves
PUT     /api/preferred-moves
DELETE  /api/preferred-moves
```

These path names express the agreed shape. Planning may settle exact field spelling, finite page-size limits, and
error codes without changing the semantics recorded here.

## Games: rich search and complete detail

`GET /api/games` is one general rich-search collection. It uses typed query parameters rather than separate endpoints
per search or a text query language. Its searchable families include:

- normalized game facts such as date/time, trainer color, outcome, termination reason, trainer and opponent ratings,
  opponent identity, time class, and time control;
- opening identity and explicit `reached` versus `deepest` opening-match meaning;
- whether a game contains a canonical FEN;
- whether a particular outgoing UCI move was played from a specified FEN;
- game length;
- analysis and preferred-move coverage state;
- supported deterministic sort choices.

Filters may be combined. The collection uses familiar `page` and `page_size` pagination, not opaque cursors and not an
unbounded all-results response.

Each result is a rich summary: normalized game metadata, deepest opening classification, game length, and useful
training-coverage counts. It does not include the full position timeline. `GET /api/games/{game_uuid}` returns the
complete game metadata, original PGN, and ordered position occurrences with the outgoing move from each occurrence.

## Openings: flat catalogue, not a line library

`GET /api/openings` provides a flat, searchable and paginated catalogue. It supports name and ECO discovery and returns
an API-level opening key, ECO, label, route count, and game-usage meanings such as games that reached the opening and
games for which it was the deepest recognition. `GET /api/openings/{opening_key}` returns one flat opening record and
its usage summary.

The same opening key is reusable in game filters and position insight. The API does not expose opening route move
sequences, hierarchy, parent/child trees, repertoire ownership, or the excluded Opening Line Library behavior.

## Position insight: one composed read

`GET /api/positions/insight` is the shared substantial position read. It requires all three inputs:

```text
fen
trainer_color
as_of
```

The response always includes the canonical position, current opening recognition, game experience, observed outgoing
move history, analysis state/current result, and preferred move resolved for `as_of`. There is no `include` mechanism
and no screen-specific variant.

`trainer_color` is required because the backend, not the frontend, filters stored games and determines whether outgoing
moves at that FEN represent trainer choices or opponent responses. Counts retain explicit distinct-game and occurrence
meanings.

The move-history section contains only moves observed in stored games. It does not duplicate legal-move generation
already owned by the frontend chess library. Novel legal moves remain valid inputs to preferred-move and analysis
commands, where the backend validates them.

A legal FEN absent from stored games returns a successful sparse insight: zero experience, empty observed move history,
no opening when unrecognized, analysis `not_requested`, and an `unconfigured` date-resolved preference. The read does
not create a database position.

## Analysis: desired result and focused polling

Analysis has one simple observable lifecycle:

```text
not_requested -> queued -> running -> ready
```

`GET /api/analysis?fen=...` provides focused polling. It does not reveal whether an internal position row already
exists: both a missing internal row and an existing position without analysis are `not_requested`.

`POST /api/analysis-requests` asks for a desired result instead of exposing frontend button actions such as Analyze,
Update, or Retry. It accepts FEN and an optional quality preset of `browser` or `tool`, defaulting to `browser`. It does
not expose arbitrary Stockfish settings. Repeating a request is safe, concurrent requests do not create duplicate queue
work, and an existing sufficient or higher-quality result satisfies the request. The command resolves and creates the
internal position when necessary.

The HTTP contract follows the rebuilt database boundary: one current complete result and live queued/running state,
without old batch, attempt, partial-result, downgrade, or persisted failure-history concepts.

## Preferred moves: dated outgoing choices from a FEN

The core semantic rule is:

```text
FEN before the move + date period -> preferred outgoing move
```

A preferred move is not the resulting child position and is not a stored repertoire line. At most one preference state
is active for one canonical FEN on any calendar date. Transpositions naturally share the same preference because they
share the same canonical position.

The two stored values use explicit tagged shapes:

```json
{"kind": "move", "uci": "d5e4"}
```

```json
{"kind": "no_preference"}
```

`kind: "move"` requires a legal outgoing UCI move from the supplied FEN. `kind: "no_preference"` carries no move; a
request that combines it with a UCI move is a known invalid combination and is rejected. Removing stored configuration
for an interval produces the third resolved state, `unconfigured`.

For mutations, `effective_from` is required and `effective_until` is optional. The end is exclusive: it is the first
date on which the value no longer applies. A `PUT` overlays a move or explicit no-preference value on the requested
interval, while `DELETE` removes configuration from the requested interval. The backend validates, splits, merges, and
normalizes periods atomically and may resolve/create the internal parent position as part of a write.

`GET /api/preferred-moves` requires a FEN and a finite `from`/`until` window. It returns contiguous normalized segments
covering the whole requested window, including derived `unconfigured` gaps. The caller does not calculate gaps,
overlaps, splits, merges, or the active value for each date.

No repertoire route, authored line, parent/child repertoire relationship, or hierarchy is introduced. A novel line is
handled as independent position-to-next-move preferences. Analysis of the child FEN creates that child position when
needed.

## Generated contract and frontend transition

The health-only OpenAPI export from `SETUP-02` becomes the base for the approved complete public contract. Every clean
operation above should be included for HeyAPI generation. Existing legacy endpoints are not retained in the generated
contract merely to keep current frontend code working.

Known frontend consequences to inventory during later assessment include:

- replacing the legacy game-position contract with game collection/detail reads;
- replacing separate position-context and move-response-distribution calls with position insight;
- replacing action-shaped evaluation calls and status polling with desired-result analysis requests and focused state;
- replacing the old single preferred-move surface with finite timeline reads and interval mutations;
- removing the current frontend rule that prevents saving a preferred move for a position absent from the played-game
  corpus;
- adopting the generated HeyAPI client after the clean contract exists.

Frontend repair is deliberately later work. No compatibility adapter, old-database fallback, application cutover, or
silent production adoption is authorized here.

## Repository ownership and placement

The clean API uses a two-layer repository boundary:

```text
FastAPI routing and HTTP models        backend/app/features/
Database capabilities and queries     src/chess_move_trainer/database/
Generated TypeScript contract         frontend/src/api/generated/
```

The rebuilt database package remains the only owner of SQL, database transactions, canonical chess/data semantics,
and reusable read/write capabilities. New game search, opening catalogue reads, position insight, analysis status, and
preferred-move timeline construction belong beside their owning domains under
`src/chess_move_trainer/database/`. They accept an explicit database path and return ordinary Python values without
FastAPI requests, responses, status codes, or Pydantic HTTP models.

Thin feature adapters under `backend/app/features/` own routers, HTTP request/response schemas, status/error mapping,
and only the small amount of orchestration needed to call the package capability. New backend features do not create
another raw-SQL `repository.py` layer. The intended dependency is `backend` importing the clean package; the package
never imports `backend`.

Focused package tests remain under `tests/database/<domain>/`, while HTTP contract tests remain under
`backend/tests/features/<feature>/`. The established handwritten export/generation tools remain under `scripts/api/`,
HeyAPI configuration remains at `frontend/openapi-ts.config.ts`, generated files remain confined to
`frontend/src/api/generated/`, and the handwritten runtime configuration wrapper remains
`frontend/src/api/client.ts`.

A single backend dependency should supply the rebuilt database path instead of importing path configuration from the
legacy positions repository. Exact transitional module names and coexistence with legacy feature code remain for the
replacement master-plan assessment; no `v2` URL or package namespace is implied by this placement decision.

The clean routes will be added alongside the legacy routes while current production usages await their individual
migration slices. Legacy operations may remain registered during that interval, but they stay outside the curated
OpenAPI/HeyAPI contract and are not wrapped by compatibility adapters. Each old route is eligible for removal only
after all of its concrete production consumers have moved to the clean generated client. No temporary `/api/v2` URL or
package tree is introduced.

## Boundaries retained

- No database lifecycle, source update, Stockfish worker, bulk analysis, schema inspection, or other operator command is
  converted into an application HTTP endpoint by this direction.
- No Opening Line Library, opening tree, repertoire-line store, or new hierarchy/classification/projection table family
  is implied.
- No old-database migration, fallback, physical activation, cleanup, or deletion is authorized.
- Completed Plans and earlier grilling records remain historical evidence and are not rewritten.
- Focused package read services and direct queries needed to implement this public surface require later assessment and
  planning; this record does not authorize them.

## Planning consequence

The next planning activity should assess and write a replacement database-rebuild master plan around this whole API
surface and its later frontend repair/cutover consequences. It should not preserve the old `API-01` through `API-04`
sequence merely for continuity. The replacement must continue to recognize the accepted database foundation,
`SETUP-01`, and `SETUP-02` as completed evidence while preserving unrelated and historical records.

The replacement master plan should use this order:

1. Create the approved new HTTP operations one at a time, without adopting them in production frontend code during
   those API-creation slices.
2. Immediately after each new operation is created, update the curated OpenAPI export and regenerate the checked-in
   HeyAPI output. Each slice therefore leaves its newly approved operation available through the generated client
   rather than postponing contract generation until the whole backend surface exists.
3. After the clean API surface is complete, inventory every concrete production use of the current APIs and create one
   replacement slice for each usage. Shared old endpoints used by different production workflows are not a reason to
   combine those frontend replacements; each usage moves independently to the generated clean client with focused
   proof of that workflow.
4. Keep still-unmigrated frontend usages explicitly documented as expected breakage until their individual slice is
   accepted. Assess legacy endpoint retirement only after their production usages have been replaced; do not remove or
   preserve an old route silently as part of an unrelated slice.

This deliberately separates clean contract construction from consumer migration while still keeping the OpenAPI and
HeyAPI artifacts current after every API addition.

(THIS IS chess.db)