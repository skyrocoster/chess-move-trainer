# DB-09 package command inventory

This is the durable command inventory for the DB-09 lifecycle. DB-09 may use only the
package-owned commands listed here and their package-owned services. The commands remain
noninteractive, use explicit paths or configuration, and keep their established exit and
failure behavior.

## Supported package command surface

| DB-09 lifecycle step | Supported command | Package-owned responsibility |
|---|---|---|
| Create or inspect the rebuilt database schema | `schema create --database PATH`; `schema inspect --database PATH` | Create or verify the compatible schema and render a deterministic inspection. |
| Acquire retained Chess.com source data | `games acquire --config PATH --raw-root PATH` | Fetch the configured archive/month data into the raw month ledger; this is the network-facing games step. |
| Import retained games into the database | `games import --config PATH --raw-root PATH --database PATH` | Read local raw months and publish normalized game and position data without network access. |
| Acquire the opening source set | `openings acquire --source-dir PATH` | Resolve one fixed Lichess commit, retrieve and validate `a.tsv` through `e.tsv`, and publish the local five-file source set. Timing options are `--request-timeout` and `--request-delay`; there is no YAML acquisition config. |
| Import the opening catalogue | `openings import --source-dir PATH --database PATH` | Strictly parse the explicit five-file source directory and publish the catalogue. |
| Inspect opening recognition | `openings lookup --database PATH --fen FEN`; `openings replay --database PATH --pgn-file PATH` | Look up one FEN or replay one PGN through the imported catalogue. |
| Manage preferred moves | `preferred-moves list`; `preferred-moves resolve`; `preferred-moves set`; `preferred-moves unset` | Read and write the package-owned preferred-move periods and resolve their effective state. |
| Run direct Stockfish population or benchmark work | `stockfish benchmark`; `stockfish bulk`; `stockfish worker` | Run the explicit benchmark, direct initial/bulk analysis, or the supported queue worker and publish package-owned results. |
| Refresh local rebuilt data | `rebuild refresh --config PATH` | Build or resume the configured neighbor from explicit retained local sources; it does not acquire from the network. |
| Stage a candidate | `rebuild candidate --config PATH` | Build or resume only the managed sibling candidate from explicit retained local sources. |
| Verify a lifecycle target | `rebuild verify --config PATH` | Verify the neighbor, managed candidate, or an explicit snapshot and report structural/replacement readiness. |
| Create a retained snapshot | `rebuild snapshot --config PATH` | Create the package-owned verified WAL-safe snapshot. |
| Replace the configured neighbor | `rebuild replace --config PATH` | Reverify, snapshot, and atomically swap only the managed neighbor under the established boundary. |
| Roll back the configured neighbor | `rebuild rollback --config PATH` | Reverify a retained snapshot, preserve the current neighbor, and restore only the configured neighbor. |
| Prove the real-data foundation | The DB-09 proof uses the commands above, especially `schema inspect`, `openings lookup`, `openings replay`, and the rebuild verification commands. | DB-09 is a proof gate, not a second command surface and not an authorization for application routes or cutover. |

## Legacy scripts classification

The relevant legacy families are retained only as historical context. The package commands above
are the replacements or the authority-excluded boundary for DB-09:

| Legacy family | Classification | DB-09 meaning |
|---|---|---|
| `scripts/chess_com/` schema/DDL helpers, including the old `create_schema` and `_schema.py` family | **Replaced** | Use `schema create` and `schema inspect`; do not import or call the old schema helpers. |
| `scripts/chess_com/` fetch, archive, raw-ledger, and replay helpers, including the old `request`, `save_json`, `upsert_month`, `mark_state`, and `run` family | **Replaced** | Use `games acquire`, `games import`, and the package-owned normalization services. |
| `scripts/opening_catalog/` schema, classification, recurrence, and catalogue helpers | **Replaced** | Use the package-owned opening source loader, `openings acquire`, `openings import`, `openings lookup`, and `openings replay`. |
| `scripts/chess_com/_replay.py` and other legacy replay/opening/preference helpers | **Replaced or authority-excluded/noncanonical** | They are evidence for historical behavior only; they are not DB-09 runtime or proof dependencies. |
| `scripts/refresh_chess_com.py` and legacy refresh wrappers | **Authority-excluded/noncanonical** | Rebuild refresh and the supported games commands are the only accepted lifecycle path. |
| `scripts/check.py` and maintenance/test wrappers | **Authority-excluded/noncanonical** | Maintenance tooling is not a DB-09 lifecycle command or proof substitute. |

**No `scripts/` command, import, wrapper, fallback, or delegation is permitted in the accepted
DB-09 path.** A legacy name appearing in this classification does not make that script an
acceptable command, compatibility target, fallback, or implementation dependency.

## Boundary

This inventory does not add a schema, persistence, API, frontend, cutover, old-database, or
real-data implementation. Application cutover remains outside DB-08/DB-09, and historical plans
and private data remain outside this document.
