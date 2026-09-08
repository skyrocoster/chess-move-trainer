# Simple database setup and update lifecycle

> **Status:** confirmed direction
> **Confirmed:** 2026-09-07
> **Purpose:** Directional evidence for replacing the overcomplicated DB-09 database-file lifecycle.

## What is being corrected

DB-09 drifted into treating the rebuilt database as a neighboring candidate that needed snapshots, replacement,
rollback, recovery, and activation-readiness ceremony. That is not the desired operating model.

The intended result is one long-lived SQLite database at `data/database/chess.db`. Initial population should be quick
and easy. Afterward, ordinary commands should retrieve current source data, persist new or corrected data directly in
that database, and create the derived data required by those changes. A complete rebuild is expected to be rare.

Other files currently under `data/database/` are outside this correction and must not be cleaned up, reorganized, or
treated as blockers.

## Supported workflow

The public data-loading workflow has only three end-to-end operations:

1. `setup`
2. `update games`
3. `update openings`

Fetching, persistence, and derivation are internal steps of those operations. Separate fetch/import commands are not
part of the supported public data-loading workflow. Stockfish operations remain separate because analysis is not part
of ordinary data loading.

### Initial setup

- `setup` operates only on the fixed destination `data/database/chess.db`.
- It succeeds only when no file exists at that path. If any file already exists there, it fails with a clear message.
- It creates the schema, obtains and imports the complete base game data, obtains and imports the latest opening data,
  and creates the required position, occurrence, opening-route, and other schema-defined derived data.
- It does not run Stockfish analysis. DB-09 may run a small separate analysis sample solely to prove that the analysis
  tooling built in earlier slices works.
- If setup creates the database and then fails, it deletes only that incomplete database created by the failed setup
  invocation. It never deletes or replaces a file that existed before setup started.
- There is no resume or recovery protocol for a failed setup.

### Game updates

- Saved Chess.com monthly source files remain the fetch ledger; no separate fetch-state table is introduced.
- `update games` starts with the newest month file already saved. It refetches that month because the previous fetch may
  have happened partway through the month, then fetches every missing month through the current month. This naturally
  refreshes the current month when it is already the newest saved month.
- Refetched month data is merged by Chess.com game ID: new games are added, corrected games replace their prior source
  representation, and games omitted by a later response are retained.
- New games and valid corrections are persisted directly to `data/database/chess.db`; their required normalized and
  derived rows are created or replaced as appropriate.
- Months are processed independently. If later acquisition fails, successfully completed earlier months remain in the
  source files and database. A later run naturally continues from the newest successfully saved month.
- A malformed, illegal, or unsupported game is skipped individually. Other valid standard games continue, and the
  command reports each skipped game and its reason.

### Opening updates

- `update openings` fetches the latest upstream versions of all five opening files; no configured commit/version is
  required for the normal update workflow.
- Only the latest valid five-file source set is retained. Older opening-source versions are not archived.
- All five files are validated before publication. If any file is invalid, neither the retained source set nor the
  current database catalogue is replaced.
- A successful update rebuilds the opening catalogue and routes together from the complete five-file set. It does not
  alter game data.

## Deliberately absent machinery

The supported database lifecycle has no neighboring database, candidate database, snapshot system, replacement or
swap operation, rollback command, recovery command, replacement-readiness gate, dedicated destructive rebuild command,
or separate operator verification step.

For the rare full rebuild, the operator manually removes or moves `data/database/chess.db` and then runs `setup`.
That destructive action is not automated by the tool.

This removal concerns database lifecycle candidates. Stockfish candidate analysis lines are schema-domain data and are
not changed by this direction correction.

## Retained correctness boundaries

Removing lifecycle protection does not mean deliberately permitting internally inconsistent writes. Ordinary SQLite
transactions remain around one logical persistence operation, the five-file opening catalogue is published together,
and invalid downloads do not replace valid source files. These are local write-integrity rules, not snapshots or an
operator-facing rollback system.

Each public operation performs only quick checks needed to confirm its own work and returns a meaningful success or
failure status. Full integrity scans, access-plan measurements, and DB-09 proof routines do not run during normal setup
or updates. There is no separate supported verification command.

## DB-09 consequence

DB-09 must stop proving that a neighboring candidate is replacement-ready. Its real-data gate instead proves:

- first-time setup into a previously absent `data/database/chess.db`;
- direct incremental game updating, including latest-month refetch, gap filling, correction handling, and derivation;
- direct complete opening refresh and route regeneration;
- the required direct read meanings and database integrity;
- a separate bounded Stockfish sample showing the existing analysis tools work; and
- quick, clear CLI success and failure behavior for the three supported data-loading operations.

DB-09 does not authorize application integration, cutover, deletion of an old production database, raw game-source
deletion, schema expansion, or cleanup of unrelated files under `data/database/`.
