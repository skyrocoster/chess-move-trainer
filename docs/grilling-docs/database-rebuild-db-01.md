# DB-01 database schema substrate handoff

> **Status:** confirmed by the user on 2026-09-04
> **Purpose:** mandatory DB-01 implementation handoff for focused planning

## Authority and authorization

This handoff finalizes DB-01 implementation and acceptance details. It remains subordinate to
`docs/grilling-docs/database-rebuild-direction.md` and `docs/grilling-docs/database-rebuild-schema.md`, which remain
the only binding product, data, and schema authorities for the database-rebuild envelope. It does not add to or
reopen the ten-table catalogue, authorize implementation, authorize application integration, or authorize any change
to the old database.

## Confirmed outcome

DB-01 creates and reopens an empty neighboring SQLite database containing exactly the ten approved catalogue tables,
their approved constraints, and `PRAGMA user_version = 1`. It also provides supported schema creation and inspection
commands and publishes a deterministic human-readable schema reference.

## Confirmed implementation boundary

- The permanent common package namespace is `src/chess_move_trainer/`. DB-01 owns
  `chess_move_trainer.database`; later tool packages depend inward on its database services.
- Permanent production package, command, and artifact names do not use transitional terms such as “new,”
  “replacement,” or “rebuilt.” Workflow records may retain the approved master-plan terminology.
- One package-owned, versioned `.sql` resource is the sole executable DDL definition. Schema DDL must not be
  duplicated in Python builders, commands, validation lists, or generated-reference code.
- SQLAlchemy Core 2.0.52 is the default for synchronous connections, queries, and transaction control. Direct SQLite
  operations remain allowed where exact SQLite behavior requires them, including PRAGMAs and later slice-specific
  backup or queue operations.
- SQLAlchemy ORM, asynchronous database access, generic repository machinery, and framework-specific objects in
  public service contracts are excluded. Public services return ordinary application data.
- One package-owned connection factory accepts an explicit database path and access mode. Every connection enables
  and verifies foreign-key enforcement.
- The default SQLite lock wait is five seconds. Commands accept an optional finite `--lock-timeout SECONDS` override;
  zero, negative, and unlimited values are rejected.
- Schema inspection opens the database read-only. DB-01 establishes no WAL or journal-mode policy.

SQLAlchemy 2.0.52 and Typer 0.27.2 are already pinned in `requirements.txt` and were proven installed and resolvable.
That dependency declaration is a settled prerequisite, not DB-01 implementation progress.

## Creation and version behavior

- An absent or truly empty target may be initialized transactionally.
- Schema creation and `PRAGMA user_version = 1` succeed as one complete operation.
- Repeating creation against an exact compatible v1 database succeeds without changing it.
- A nonempty v0 database, mismatched schema, or other schema version is rejected without modification.
- There is no repair, recreation, migration, overwrite, or `--force` path.
- Compatibility checking must not introduce a second hand-maintained catalogue. It compares generically against a
  temporary or reference database built from the canonical `.sql` resource, or uses an equivalently single-sourced
  mechanism.

## Supported command contract

Typer 0.27.2 owns the shared thin, non-interactive command family. DB-01 supports:

```text
python -m chess_move_trainer.database schema create
python -m chess_move_trainer.database schema inspect
```

- Both commands require `--database PATH`.
- There is no active-database default or environment-variable fallback.
- The target's parent directory must already exist.
- Successful report output goes to stdout and diagnostics go to stderr.
- Exit status `0` means success, `1` means an operational or file failure, `2` means invalid command usage, and `3`
  means an incompatible existing creation target.
- CLI adapters contain no schema or connection business logic.
- Existing setup and legacy scripts remain untouched. DB-01 adds permanent `setup-tools.ps1` as the clean toolchain
  setup surface. Its first responsibility is installing this repository as an editable Python package without
  reinstalling dependencies; later slices may extend it only with toolchain setup, never database business logic.

## Inspection and generated reference

- `schema inspect` generically describes any readable SQLite database. It must not hard-code or duplicate the approved
  catalogue and is not itself the strict compatibility gate.
- Inspection of a missing path does not create a database.
- Inspection emits deterministic human-readable Markdown to stdout.
- Optional `--output PATH` writes the same Markdown using atomic replacement after successful inspection.
- The DB-01 workflow generates `data/database/schema.md` from a fresh conforming database. The file is clearly marked
  as generated and is linked separately from `docs/README.md`.
- Existing legacy `data/database/schema.txt` remains untouched.

## Focused acceptance and proof

Focused DB-01 proof must establish:

- the exact ten-table user-table inventory and absence of unlisted user tables;
- every approved field, primary key, foreign key, `UNIQUE`, `CHECK`, and foreign-key action from the binding schema
  catalogue;
- `PRAGMA user_version = 1`, foreign-key enforcement after reopen, `foreign_key_check`, and integrity checking;
- safe initial creation, exact-v1 repeatability, and non-destructive rejection of incompatible targets;
- read-only inspection, missing-path safety, deterministic Markdown, atomic output, and generated-reference freshness;
- useful command help, required explicit inputs, non-interactive operation, and the confirmed exit meanings;
- importable package ownership and inward dependency direction; and
- no legacy-tool or production-backend import, wrapper, copy, or runtime delegation.

SQLite-created internal autoindexes are allowed. No extra application-selected index, authorizer, guard table, schema
ledger, or other machinery is added solely for DB-01 proof.

## Exclusions

DB-01 includes no feeders, source acquisition, canonical chess-position logic, populated data rows, analysis,
application readers, API or frontend changes, production default database path, migration, cutover, old-database
modification or deletion, or extra schema/history/state/run tables. Broad lint, formatting, build, aggregate,
source-size, and repository-maintenance checks are not DB-01 implementation proof.

## Escalation boundary

Return to the user before changing any catalogue table, field, key, check, foreign-key action, version, or index;
adding a runtime dependency; adopting ORM or asynchronous access; changing the public command or exit contract;
introducing a default active path, destructive behavior, migration machinery, or legacy reuse; or touching a production
application consumer. Implementation difficulties that would require any excluded table or behavior are decisions,
not permission to expand DB-01.

## Decision rationale

- A common product namespace gives later tools one durable inward dependency boundary; a `database_tools` island would
  age poorly, and production backend ownership is forbidden before DB-09.
- A versioned SQL resource keeps exact SQLite DDL directly reviewable and avoids fragmented procedural ownership.
- SQLAlchemy Core reduces repetitive query code without the hidden state and coupling of an ORM.
- Typer keeps the large later command family consistent and testable with thin adapters.
- Generic inspection remains useful across schema versions without requiring parallel field lists.
- Stable `schema.md` naming is suitable for eventual production use; transitional naming is not.
