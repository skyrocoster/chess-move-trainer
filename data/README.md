# Data

## The one rule: the host files are never the live database

The ignored host seed/export file is `data/database/chess-seed.db`. The live
database is selected separately inside the containers:

- **Inside** the backend and worker containers, `data/database/chess.db` resolves
  to the **live database** in the `chess-database` Docker volume (full volume
  name `chess-move-trainer_chess-database`).
- **Inside** the Datasette container, `/data/chess.db` is the same live volume.
- **On your computer** (the host), `data/database/chess-seed.db` is a separate
  seed/export copy. It goes stale the moment any worker writes.

The host seed file and the live volume file are different roles and locations.
If a file is not in the volume, it is not live. Today the live database is
about 155 MB with an active write-ahead log, while the host seed copy is about
145 MB with no log.

## Live database (the real one)

- Stored in the `chess-database` Docker volume, nowhere else.
- Mounted at `/workspace/data/database` in the backend, worker, and worker-six
  containers, and at `/data` in the Datasette container.
- Browse it at <http://localhost:8666> (managed `datasette` service).
- Full service rules are in [`docs/DEVELOPMENT_SERVICES.md`](../docs/DEVELOPMENT_SERVICES.md).

## Host files under `data/database/` (never live)

All `*.db` files here are ignored by git. Only `schema.md` is tracked.

| File | What it is | Who writes it | Who reads it |
| --- | --- | --- | --- |
| `chess-seed.db` | Ignored local seed/export copy for host-side pytest, benchmarks, and proof scripts. Stale unless freshly exported. Nothing automatic creates or refreshes it. | You, via the `docker cp` export in `docs/DEVELOPMENT_SERVICES.md`, or a host-side `setup` run. | Host test runs that default to `data/database/chess-seed.db` (they skip when no export exists). Never the app. |
| `chess.db.backup.pre-wal` | Manual backup snapshot taken before a write-ahead-log change. | You, by hand. | You, by hand, if a restore is ever needed. |
| `schema.md` | Generated schema reference (tracked by git). | `python -m chess_move_trainer.database schema inspect --database <path> --output data/database/schema.md`. | Readers who want the table layout without opening the database. |

Do not hand-edit any file in this directory, and do not copy the host `chess-seed.db`
into a container: containers cannot see host-side edits.

## Is my host seed copy stale? Check in seconds

Compare hashes of the host seed copy and the live volume file:

```bash
# Host seed copy:
sha256sum data/database/chess-seed.db

# Live database (same command shape, different file):
docker exec chess-move-trainer-backend-1 sha256sum /workspace/data/database/chess.db
```

Different hashes mean the host seed copy is stale. To refresh it: stop the workers
first, copy out of a container, restart, then re-hash to confirm. The exact
commands are in [`docs/DEVELOPMENT_SERVICES.md`](../docs/DEVELOPMENT_SERVICES.md).

The live database itself stays current without any export: a cold
`uv run --no-sync sg dev start` refreshes games and
openings in the volume before the services start, and
`uv run --no-sync sg dev update` refreshes them on a
live stack with workers paused. The host CLI (`setup`, `update games`, `update
openings`) targets the host seed path by default and accepts an explicit
`--database` option; it is not part of the container startup path.

## Other directories

- `chess-com/` — committed source inputs (tracked by git).
- `stockfish/` — ignored local engine files.
- Database schema source lives in [`src/chess_move_trainer/database/`](../src/chess_move_trainer/database/).
