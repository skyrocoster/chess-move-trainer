# DB-04 opening catalogue and route rebuild — grilling handoff

> **Status:** confirmed
> **Scope:** slice-specific implementation decisions for DB-04
> **Authority:** subordinate to the settled database-rebuild master plan and its two binding direction/schema documents

## Shared understanding

DB-04 will rebuild a complete opening catalogue from caller-supplied `a.tsv` through `e.tsv` files into the existing
`datasource_opening`, `derived_opening_route`, and `derived_opening_route_move` tables. It will reuse DB-02's canonical
position service for route endpoints and will add no table or column.

The slice also provides an isolated package-level lookup/replay capability and thin Typer commands. It does not create
an HTTP route, alter the production backend or frontend, classify games, store intermediate route membership, or revive
the excluded Opening Line Library application surface.

## Settled implementation decisions

### Source contract and route identity

- The caller supplies one source directory containing the exact five opening inputs `a.tsv`, `b.tsv`, `c.tsv`,
  `d.tsv`, and `e.tsv`. DB-04 does not fetch them over the network.
- Import is a strict all-or-nothing batch. The five files must have the exact `eco`, `name`, and `pgn` columns and the
  expected field count. Missing sources, malformed rows, invalid ECO values, empty or illegal move text, and incomplete
  input reject the batch rather than being skipped.
- Opening names are retained verbatim, including a schema-permitted empty string.
- Legal replay converts source move text to ordered UCI moves. Route identity is
  `(ECO, name, ordered replayed UCI moves)`, not raw PGN spelling or source-row identity.
- Formatting-only duplicates of that semantic identity collapse across all five files. Distinct move orders remain
  distinct routes even when they reach the same endpoint. Different labels may legitimately share one route or one
  endpoint.

### Ownership and dependency direction

- New code is owned by `chess_move_trainer.database.openings`, following the established `database.positions` and
  `database.games` package pattern.
- The openings package may depend on the package-owned database and canonical-position services. Those lower-level
  services must not depend on openings.
- Source parsing/legal replay, catalogue publication, and lookup/replay are importable services. Typer callbacks are
  thin adapters and contain no business logic.
- New code must not import, wrap, delegate to, patch, copy, or incrementally continue the legacy opening-catalogue
  implementation or its internal contracts.

### Endpoint creation and atomic publication

- All five sources are parsed, normalized, deduplicated, and legally replayed before catalogue mutation begins.
- Only each route's final canonical position is referenced by the opening tables. No permanent intermediate-position,
  hierarchy, parent, transposition-link, shared-prefix, classification, recurrence, manifest, or history data is added.
- Publication uses one database transaction. It resolves or creates canonical endpoint positions through the existing
  position transaction boundary, deletes `derived_opening_route_move` children first, then
  `derived_opening_route`, then `datasource_opening`, and publishes the complete replacement catalogue.
- Existing canonical positions are retained even when no rebuilt route references them. Any publication error or
  interruption rolls back newly created endpoints and all catalogue changes, leaving the prior active catalogue intact.
- Integer database IDs are internal storage details, not route identity or a caller-visible ordering contract.

### Lookup and replay semantics

- PGN replay returns a structured recognition timeline containing every reached opening label in encountered ply order,
  plus one current label.
- Results distinguish an exact stored move-route match from a position-only transposition match. A transposition never
  becomes an exact-route claim merely because it shares an endpoint.
- The current label is selected by deepest reached ply, then exact-route match over transposition, then deterministic
  `(ECO, name)` ordering when labels remain tied. All tied labels remain present in the recognition timeline.
- FEN lookup uses DB-02's legal canonical four-field identity while accepting a standard full FEN input. Clock fields
  are not position identity. It returns every directly matching opening and the broader families derivable by replaying
  stored routes; because FEN supplies no move history, it does not claim an exact move-route match.
- Lookup/replay derives recognition from the three opening tables and canonical endpoint positions. It does not persist
  classification, family relationships, or intermediate memberships.
- Unreached future labels and variations are never exposed. A valid query with no recognized opening returns an empty
  recognition list and no current label.

### Supported Typer CLI

The existing `python -m chess_move_trainer.database` Typer application gains an `openings` command group with:

- `openings import --source-dir PATH --database PATH`
- `openings lookup --database PATH --fen FEN`
- `openings replay --database PATH --pgn-file PATH`

`openings replay` accepts exactly one game per invocation, with or without normal PGN headers. Empty input, multiple
games, illegal moves, or trailing invalid content is rejected rather than ignored.

Successful commands are human-readable by default and provide stable machine-readable output with `--json`. Errors go
to stderr, commands are non-interactive, and all paths/configuration are explicit. Exit behavior is:

- `0`: success, including a valid lookup/replay with no match;
- `1`: malformed catalogue source or operational/storage failure;
- `2`: invalid Typer usage or invalid lookup/replay input;
- `3`: incompatible database schema; and
- `130`: interruption.

## Focused proof and acceptance

The focused Plan should proceed sequentially through source parsing/replay, atomic persistence, lookup/replay, and thin
CLI integration. It must directly prove:

- all five required files, strict row validation, legal replay, semantic duplicate collapse, and transposition
  preservation;
- contiguous one-based route plies, endpoint equality, canonical endpoint reuse, and retention of unrelated positions;
- child-first complete replacement and rollback that leaves the prior catalogue unchanged after malformed input,
  storage failure, or interruption;
- ordered recognition, current-label precedence, exact-route versus transposition behavior, FEN matches and broader
  families, tied labels, valid no-match behavior, and unreached-future exclusion;
- Typer help, explicit inputs, default and JSON output, non-interactive operation, and the settled exit statuses; and
- package/source-boundary checks proving no legacy import, wrapper, runtime delegation, or copied implementation.

Prospective finite proof commands for Sol to refine in the focused Plan are:

- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/openings -q`
  (command timeout `120s`; Bash tool timeout `150000ms`)
- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q`
  (command timeout `90s`; Bash tool timeout `120000ms`)
- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q`
  (command timeout `90s`; Bash tool timeout `120000ms`)

No lint, formatting, broad type/build, source-size, aggregate, or repository-hygiene command is implementation proof.
The actual upstream TSV population is not checked into this repository, so DB-04 proves the complete five-file contract
with focused fixtures. DB-09 remains responsible for proof against real rebuilt data.

## Escalation and exclusions

Escalate rather than improvise if the result needs a table or field outside the approved catalogue, persisted source
provenance or hierarchy, a different singular-current semantic, a new dependency, legacy runtime reuse, production
backend/frontend integration, or a schema/authority change.

DB-04 excludes classification, recurrence, manifests, source/import state, parent or transposition links, shared-prefix
or intermediate-position records, opaque-sequence or historical-route machinery, HTTP and application work, cutover,
old-database mutation or deletion, raw-source mutation, and application Opening Line Library work.
