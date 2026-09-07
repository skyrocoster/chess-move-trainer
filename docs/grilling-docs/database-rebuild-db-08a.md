# Database rebuild DB-08A tool-surface handoff

> **Status:** approved direction for direct month targeting followed by Lichess acquisition planning
> **Date:** 2026-09-06
> **Authority:** User decisions in the DB-08A grilling; the settled clean-rewrite, package/CLI, sequencing, schema, and retention boundaries in `docs/master-plans/database-rebuild/database-rebuild.md` remain in force.

## Purpose

Finish the required package-owned retrieval surface before DB-09. Legacy files under `scripts/` are read-only
reference material: new code must not import, wrap, call, copy, patch, or delegate to them. Existing accepted clean
implementations under `src/chess_move_trainer/database/` remain the implementation base for their already rebuilt
capabilities.

DB-08 is complete and DB-08A remains the next master-plan slice. No new master plan or second toolchain is required.

## Verified lifecycle inventory

The supported package already provides the following lifecycle operations through
`python -m chess_move_trainer.database`:

1. `games acquire` discovers Chess.com archives, retrieves listed months, skips retained historical files, safely
   UUID-merges the current month, and atomically publishes raw month files without touching SQLite.
2. `schema create` and `schema inspect` own the exact replacement schema.
3. `games import` rebuilds normalized game, occurrence, and canonical-position data from local raw months.
4. `openings import`, `openings lookup`, and `openings replay` consume and inspect a caller-supplied local five-file
   opening catalogue.
5. `preferred-moves` commands own preferred-move period storage.
6. `stockfish benchmark`, `stockfish bulk`, and `stockfish worker` own analysis operation.
7. `rebuild refresh`, `verify`, `snapshot`, `candidate`, `replace`, and `rollback` own repeatable local rebuild and
   neighboring-file safety operations.

The remaining required retrieval work is bounded to targeted Chess.com month selection and package-owned retrieval
of the five Lichess opening source files. No other required database-lifecycle retrieval gap was found.

Old corpus, classification, recurrence, relationship, tracked-player, run/history, manifest, fetch-state, interactive
analysis-menu, standalone Stockfish-setup, ad-hoc SQL, and preferred-move line-input capabilities are not required
replacement lifecycle operations and are not revived.

## Direct change: targeted Chess.com month acquisition

The existing clean implementation at `src/chess_move_trainer/database/games/acquisition.py` is retained. It is not a
legacy tool and must not be discarded or rebuilt. Add operator-selected `games acquire --month YYYY-MM` behavior to
that package-owned implementation and its thin CLI.

Settled behavior:

- Month input uses the exact `YYYY-MM` calendar form.
- Archive discovery remains authoritative. A selected month must resolve through the exact listed Chess.com month URL;
  the option must not construct or accept an arbitrary month URL.
- Only the selected month is processed.
- A missing historical month may be retrieved and atomically published.
- An existing historical month remains retained and is skipped; no overwrite or force mode is introduced.
- The selected current month keeps the accepted refetch and UUID-merge behavior.
- Future, malformed, conflicting, or unlisted month selections fail meaningfully without changing a usable raw file.
- Acquisition remains separate from SQLite import.
- The existing all-eligible-month behavior remains unchanged when `--month` is omitted.

This is an approved direct change. It receives focused package/CLI proof and must be accepted before planning the
Lichess acquisition work.

## Planned change: Lichess opening-source acquisition

Create a new clean package-owned implementation at
`src/chess_move_trainer/database/openings/acquisition.py`, with a thin `openings acquire` command registered in
`src/chess_move_trainer/database/cli.py`. Existing opening import, source parsing, and recognition remain in place;
legacy opening scripts are reference-only.

Settled behavior:

- The fixed canonical upstream is `https://github.com/lichess-org/chess-openings`, whose opening data is provided
  under CC0 1.0.
- Each invocation uses the latest default-branch state. It resolves that state to one commit before retrieving files,
  so one run cannot mix revisions.
- The command retrieves exactly `a.tsv`, `b.tsv`, `c.tsv`, `d.tsv`, and `e.tsv` from that resolved commit.
- The complete set must pass the accepted strict TSV and legal-PGN source validation before publication.
- Publication stages and validates the complete set, then atomically replaces each fixed file while retaining the
  prior bytes for rollback. Any handled retrieval, validation, publication, or interruption failure restores the
  prior usable set. Windows cannot atomically replace an existing nonempty five-file directory in one operation, so
  an abrupt process or machine crash during the file swaps may temporarily leave mixed revisions; an idempotent rerun
  repairs that state. This practical Windows behavior is explicitly accepted and does not introduce version-directory,
  pointer, manifest, or source-history machinery.
- The resolved commit is reported for traceability but is not a required input and does not add schema, manifest,
  source-history, or audit persistence.
- The upstream is not configurable and there is no arbitrary URL or mirror mode.
- `openings acquire` remains separate from `rebuild refresh`; the rebuild remains offline and consumes an explicit
  local source directory.
- Versioned example YAML configuration files use safe placeholders and contain no personal identifiers or secrets.
- Acceptance uses focused offline transport and filesystem proof only. It covers default-branch revision resolution,
  immutable-revision downloads, exact file-set validation, unchanged-content behavior, atomic replacement, failure
  preservation, CLI help, explicit inputs, and meaningful exits. No live GitHub request is required. DB-09 owns the
  later real-catalogue import and database proof.

## Boundaries and sequencing

- First execute and accept only the direct Chess.com month-selection change.
- Then assess and write a focused DB-08A Plan for Lichess acquisition, configuration examples, the durable
  lifecycle/legacy-tool command inventory, and focused proof.
- Planning the Lichess work does not authorize its implementation.
- No schema change, application API/frontend work, DB-09 real-data proof, cutover, old-database handling, raw game
  policy change, legacy compatibility layer, or legacy script cleanup is included.
- Escalate any need for a new dependency, configurable upstream, persisted source/version history, partial-file
  publication, legacy runtime reuse, or application integration.
