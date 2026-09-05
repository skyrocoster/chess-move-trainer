# DB-05 preferred-move period persistence — grilling handoff

> **Status:** coordinator-approved handoff
> **Confirmation:** The user confirmed this shared understanding on 2026-09-05.
> **Authorization:** This handoff settles DB-05 details for focused planning. It does not authorize implementation.

## Authority and outcome

This handoff is bounded by the DB-05 envelope in
`docs/master-plans/database-rebuild/database-rebuild.md` and only the direction/schema authority ranges named there.
It refines those decisions without reopening the ten-table catalogue or canonical position identity.

DB-05 will provide package-owned storage and supported CLI operations for the current effective preferred-move
schedule. For each canonical position and UTC calendar date, the schedule resolves to one of three states: a preferred
legal move, explicit no preference, or unconfigured. Periods are editable current truth, not history or provenance.

## Settled storage and editing semantics

- DB-05 uses the existing four-column `datasource_preferred_move_period` table unchanged. It adds no table, column,
  trigger, or `PRAGMA user_version` change and migrates no existing preference data.
- Periods use strict UTC calendar dates and half-open `[effective_from, effective_until)` boundaries. The start is
  included, the end is excluded, and a NULL end means indefinitely.
- A covering row with a UCI move is preferred, a covering row with a NULL move is explicit no preference, and no
  covering row is unconfigured.
- The stored schedule is only the current effective schedule. Amendments discard prior edit boundaries and do not
  retain who, when, or how a value changed.
- Callers amend date ranges rather than physical row identities. A set operation overlays a preferred move or explicit
  no-preference state onto the requested range. An unset operation removes configuration from the requested range.
- An amendment automatically splits or shortens intersected periods, preserves every date outside the requested range,
  and merges adjacent periods containing the same state. Returning to an earlier move therefore remains represented by
  distinct nonadjacent periods.
- Reads never create rows. An unknown valid position lists no periods and resolves as unconfigured. A write may create
  a valid standalone canonical position in the same transaction as its first preference period.

## Position and date input

- Public preferred-move operations identify positions using exactly the four meaningful FEN fields: piece placement,
  side to move, castling rights, and en-passant square.
- DB-02's shared canonical-position service validates and canonicalizes that input, including legal-only en-passant
  normalization. Halfmove and fullmove clocks are neither accepted as preferred-move input nor part of position
  matching.
- Dates accept only the literal `YYYY-MM-DD` calendar form. Timestamps, timezone conversion, relative values such as
  `today`, and defaulting from the system clock are not supported.
- `effective_from` is always explicit. An omitted end means an indefinite period. A finite end must be strictly later
  than its start.
- A non-NULL UCI move must be legal from the canonical source position before publication.

## Ownership and dependency direction

- New code is owned by `chess_move_trainer.database.preferred_moves`, following the established sibling-feature
  package pattern.
- The package may depend on package-owned database connection/schema services and DB-02 canonical-position services.
  Those lower-level services must not depend on preferred moves.
- Preferred moves must not depend on games, openings, production backend/application modules, frontend code, or legacy
  scripts. Range normalization, validation, resolution, and persistence are importable package services; Typer
  callbacks remain thin adapters without business logic.
- New code must not import, wrap, delegate to, patch, copy, or incrementally continue
  `scripts/opening_catalog/preferred_move.py`, `scripts/opening_catalog/preferred_move_schema.py`, or their internal
  contracts. Those files remain read-only conceptual evidence.

## Atomicity and no-overlap guarantee

- Every supported write acquires the SQLite writer reservation with `BEGIN IMMEDIATE` before reading the schedule it
  will amend. It uses the established finite lock timeout and never relies on a schedule read before the lock.
- Position resolution/creation, range normalization, replacement writes, and post-normalization validation occur on
  one connection in one transaction. Any validation, storage, lock, or interruption failure rolls back the complete
  amendment.
- Before commit, periods for the position are ordered and checked pairwise. Every finite interval has end greater than
  start, no period overlaps its successor, and an indefinite period cannot precede another period.
- The no-overlap guarantee covers all supported package and CLI writers, including concurrent local writers. Direct
  manual SQL mutation that bypasses the package is unsupported. DB-05 does not add overlap triggers or other machinery
  solely to police arbitrary writers.

## Supported Typer CLI

The existing `python -m chess_move_trainer.database` application gains a `preferred-moves` command group with:

- `preferred-moves list --database PATH --fen FOUR_FIELD_FEN`
- `preferred-moves resolve --database PATH --fen FOUR_FIELD_FEN --date YYYY-MM-DD`
- `preferred-moves set --database PATH --fen FOUR_FIELD_FEN --from YYYY-MM-DD [--until YYYY-MM-DD]
  (--move UCI | --no-preference)`
- `preferred-moves unset --database PATH --fen FOUR_FIELD_FEN --from YYYY-MM-DD [--until YYYY-MM-DD]`

`set` requires exactly one of `--move` or `--no-preference`. `unset` creates an unconfigured gap rather than an
explicit no-preference period. `list` returns the normalized stored periods; `resolve` returns exactly one of the three
settled states for the requested date.

Commands are non-interactive, never read stdin, use explicit paths and inputs, and provide useful `--help`.
Successful commands are human-readable by default and support stable machine-readable output with `--json`. Errors go
to stderr. Exit behavior is:

- `0`: success, including empty lists, unconfigured resolution, and an unset range with nothing to remove;
- `1`: operational, storage, or lock failure;
- `2`: invalid invocation, date, four-field FEN, period, or move;
- `3`: incompatible database schema; and
- `130`: interruption with the active transaction rolled back.

## Future-facing decisions that do not expand DB-05

- A future editor may display multiple date-window rows with add/remove controls. Submitted rows are editing inputs;
  after saving and reloading, the editor should show one row per normalized period actually stored, which may be fewer
  than the submitted rows after merging. This is an API-04 handoff, not DB-05 frontend design or implementation.
- Bullet, Blitz, Rapid, or other time-control-specific preference scopes are deliberately deferred. Time control is not
  added to canonical position identity or the DB-05 preference-period key. A future schema version may add and migrate
  that independent schedule dimension when its product behavior is ready.
- Historical-game inference is not part of DB-05. The master plan now assigns deterministic reviewable proposal
  generation and separate explicit empty-schedule application to SETUP-01 after DB-09.

## Focused proof and acceptance

The focused Plan should proceed sequentially through range/service semantics, transactional persistence and
concurrency, thin CLI integration, and focused boundary proof. It must directly prove:

- preferred move, explicit no-preference, and unconfigured resolution, including empty and indefinite schedules;
- strict date and four-field FEN validation, legal-only en-passant canonicalization, legal move enforcement, canonical
  position reuse, and same-transaction standalone-position creation;
- insertion, overlay, split, shorten, extend, replace, unset, return to an earlier move, adjacent-equal merging, and
  exact preservation of all dates outside an amendment;
- pairwise non-overlap, complete rollback after validation/storage failure or interruption, finite lock behavior, and
  two concurrent supported writers without lost updates or overlapping committed periods;
- CLI help, explicit inputs, mutual exclusivity, default and JSON output, non-interactive operation, and settled exit
  statuses; and
- package/source-boundary checks proving the dependency direction and absence of legacy import, wrapper, runtime
  delegation, or copied implementation.

Prospective finite proof commands for Sol to refine in the focused Plan are:

- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves -q`
  (command timeout `120s`; Bash tool timeout `150000ms`)
- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q`
  (command timeout `90s`; Bash tool timeout `120000ms`)
- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q`
  (command timeout `90s`; Bash tool timeout `120000ms`)

No lint, formatting, broad type/build, source-size, aggregate, or repository-hygiene command is DB-05 implementation
proof. Existing accepted schema and canonical-position proof remains valid because DB-05 changes neither contract.

## Exclusions and escalation

DB-05 excludes schema changes, migration, event/action/actor/history or audit machinery, update/delete/overlap triggers,
historical-game inference or evaluation, time-control scoping, API/backend/frontend contract work, preference-history UI,
cutover, old-database mutation or deletion, and legacy implementation reuse.

Escalate rather than improvise if implementation requires a new table, column, state, trigger, dependency, timestamp
precision, time-control dimension, historical-game behavior, direct-SQL enforcement, non-current edit history, or any
production application integration.
