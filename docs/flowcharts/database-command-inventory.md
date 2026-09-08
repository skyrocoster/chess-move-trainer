# DB-09 direct-lifecycle command inventory

This is the current canonical inventory for the DB-09 data-loading surface. It records the
confirmed direct lifecycle, not the historical DB-08 database-file operations. The fixed
destination is exactly `data/database/chess.db`.

## Supported public data-loading surface

There are exactly three public data-loading workflows:

| Workflow | Fixed-destination responsibility | Direct lifecycle boundary |
|---|---|---|
| `setup` | Create the absent `data/database/chess.db`, load complete base game data and the latest valid five-file opening catalogue, and create the schema-defined derived rows. | Refuses a pre-existing file. If this invocation created the database and later fails, it removes only that newly created database. It performs quick local checks only and does not run Stockfish. |
| `update games` | Refetch the newest saved Chess.com month, fill missing months through the current month, and persist new or corrected games and their derived rows directly to `data/database/chess.db`. | Uses saved monthly files as the only fetch ledger; merges by Chess.com game ID, retains omitted games, processes months independently, skips invalid games individually with reasons, and performs quick local checks only. |
| `update openings` | Fetch and publish the latest valid upstream `a.tsv` through `e.tsv` set, without a configured commit/version input, and rebuild the opening catalogue, routes, route moves, and endpoint positions in `data/database/chess.db`. | Validates all five files before publication. An invalid or incomplete set preserves the retained source files and current catalogue. It does not change game data, runs Stockfish, or perform full proof scans. |

Acquisition, source validation, normalization, persistence, canonical-position resolution,
and opening-route publication are internal steps of these workflows. Separate public fetch,
import, rebuild, replacement, snapshot, rollback, recovery, or verification workflows are
not part of the current data-loading surface.

## Separate Stockfish analysis surface

Stockfish remains a separate analysis surface rather than a data-loading workflow. The
package-owned `stockfish benchmark`, `stockfish bulk`, and `stockfish worker` operations may
publish analysis data under their established analysis contract, but `setup`, `update games`,
and `update openings` never invoke them. Internal analysis services may remain separately
owned; they do not add a fourth data-loading workflow.

## Deliberately absent database-file lifecycle machinery

The supported current lifecycle has no neighboring database, candidate database, replacement
or swap operation, snapshot system, rollback command, recovery command, replacement-readiness
gate, dedicated reset/rebuild command, or separate operator verification step. A rare full
rebuild is manual: an operator deliberately removes or moves the fixed database outside these
commands and then runs `setup`. The tool does not automate that destructive action or provide
a resume protocol for a failed setup.

## Retained boundaries

- The old production database remains untouched and is not a source or setup blocker.
- Raw game sources remain retained; no raw-source deletion or unrelated source-policy change
  is part of this lifecycle.
- The approved ten-table schema and its version mechanism remain the schema boundary; no
  lifecycle state, manifest, run-history, or other schema expansion is introduced.
- Legacy scripts remain read-only, noncanonical evidence. No script command, import, wrapper,
  fallback, delegation, or runtime dependency is an accepted DB-09 path.
- Other files under `data/database/` are outside this workflow and are not inspected, cleaned,
  reorganized, or treated as blockers.
- Backend, frontend, HTTP API, application integration, and cutover remain outside the
  pre-application DB-09 gate.

This inventory does not create a database, change the schema or dependencies, authorize
application work, or rewrite the completed DB-08/DB-08A Plans or prior grilling records.
