# DB-02 canonical position substrate handoff

> **Status:** confirmed by the user on 2026-09-04
> **Purpose:** mandatory DB-02 implementation handoff for focused planning

## Authority and prerequisite

This handoff finalizes DB-02 implementation and acceptance details. It is subordinate to the DB-02 envelope and
clean-rewrite rules in `docs/master-plans/database-rebuild/database-rebuild.md` and to the position authorities in
`docs/grilling-docs/database-rebuild-direction.md` lines 167-232 and
`docs/grilling-docs/database-rebuild-schema.md` lines 240-293. DB-01 is accepted; its completed Plan retains the
prerequisite proof for the exact v1 schema, explicit database paths, finite lock waits, foreign-key enforcement,
SQLAlchemy Core connection handling, and package conventions.

## Confirmed outcome and ownership

DB-02 provides one clean, from-scratch canonicalization and storage service under
`chess_move_trainer.database.positions`. It creates or reuses permanent integer
`derived_position.dp_position_id` rows for all rebuilt producers. The identity is exactly canonical piece placement,
side to move, castling rights in `KQkq` order (or `-`), and a fully legal en-passant square (or `-`). Halfmove and
fullmove counters never participate in identity. Future producer packages depend inward on this shared service and
must not invent independent position keys.

The service depends only on DB-01 database services, the Python standard library, SQLAlchemy Core already owned by
the package, and the pinned `chess==1.11.2` library. It returns ordinary package data and errors; framework, raw
`sqlite3`, and raw SQLAlchemy objects do not cross the public producer boundary.

## Inputs, canonicalization, and validation

- Provide explicit public entry points for replayed `chess.Board` positions and complete six-field FEN strings.
  Both are validated by the service. There is no trusted public four-field/storage-key input.
- Complete FEN input validates all six fields. Valid halfmove and fullmove fields are accepted but discarded from
  shared identity.
- Valid canonical output uses the board field, `w` or `b`, canonical castling ordering, and legal-only en passant.
- A normal classic/pseudo-only en-passant marker with no fully legal capture is accepted and normalized to `-`.
  This includes no-capturer and pinned-capturer positions. A genuinely legal en-passant capture retains its target.
- A geometrically or otherwise impossibly inconsistent en-passant target is invalid rather than repaired. Malformed or invalid
  positions, including missing kings, pawns on the first or eighth rank, impossible castling rights, and inconsistent
  en-passant geometry, are rejected before storage.

## Storage, schema, and transaction contract

- The existing DB-01 `derived_position` table, columns, constraints, and schema version remain unchanged. DB-02 adds
  no schema objects, migration, repair, or compatibility layer.
- Every operation requires an already-created, exactly compatible DB-01 v1 database. A missing, empty, or incompatible
  target raises a clear package error before any position write and remains unmodified; it is not silently created,
  migrated, repaired, or altered. DB-02 may reuse a narrow package-internal, side-effect-free compatibility assertion
  factored from DB-01 schema internals, but does not add a public schema API or change `create_schema()` behavior.
- Create-or-reuse is atomic and conflict-safe. Concurrent writers resolving the same identity receive one stable
  integer ID backed by one row; distinct values in any identity field can create distinct rows. Reopening the database
  preserves ID reuse.
- The package owns an opaque transaction/unit-of-work boundary that future producer services can compose into one
  all-or-nothing write. It exposes position resolution, commit on successful completion, and rollback on failure
  without exposing a raw database handle. A one-off create/reuse operation may use the same boundary internally.
- Position rows are permanent even after references disappear. There is no update, delete, or cleanup API.

## Package and CLI boundary

**Public CLI entry points: none.** Canonical position identity is an internal shared service, not an operator-facing
operation. This satisfies the package/CLI rule because internal shared services need not invent commands; later
operator commands call DB-02 through their package services. The existing DB-01 schema CLI and its behavior remain
unchanged.

## Producer handoffs

- DB-03 passes every replayed game board through DB-02 and composes position creation with each valid game's
  transaction.
- DB-04 uses the same service for opening endpoints and intermediate replay positions inside its grouped catalogue
  publication transaction.
- DB-05 uses the complete-FEN entry point for standalone preferred-move writes and may create a valid position with no
  other reference.
- DB-06 and DB-07 consume the shared integer identity for analysis and queue work and must not invent keys.
- Current legacy replay/opening/preference tools and production backend code remain read-only conceptual evidence and
  stay untouched before the DB-09 gate.

## Focused acceptance and proof expectations

Proof covers valid board and full-FEN canonicalization; castling order; counter exclusion; legal, no-capturer,
pseudo-only, and pinned en passant; impossible en-passant rejection; malformed and invalid position rejection;
same-key reuse and each-field distinction; concurrent conflict-safe reuse; reopen stability; permanent retention after
a test reference is removed; invalid-input no-write; grouped rollback and future composability without DB-03+ record
services; missing/empty/incompatible-schema rejection without target changes; and clean package/source boundaries.
Source-boundary proof must scan Python files recursively under `src/chess_move_trainer/database/`, including the new
`positions/` subpackage. Retain unaffected DB-01 proof. Run only DB-02-focused tests, narrow tests for affected DB-01
connection/schema internals, and package/source-boundary checks; the DB-01 CLI and executable schema remain unchanged.

## Exclusions and escalation

No old-position migration or old-database access; no schema, table, column, constraint, index, or version change; no
dependency or CLI addition; no source ingestion, game/opening/preference/analysis/queue producer implementation; no
production backend/application/frontend/API work; and no edits, imports, wrappers, delegation, copying, or compatibility
contracts involving legacy evidence.

Escalate before changing the four-field identity or legal-only meaning; changing schema/version; adding a dependency or
CLI; exposing raw database handles; introducing update/delete/cleanup; touching legacy, old-database, backend, API, or
frontend paths; or if grouped all-or-nothing producer transactions cannot be composed through the opaque package
boundary.
