# Data

- `chess-com/` — committed source inputs
- `database/` — host-side database seed, backup, and export files plus generated schema reference.
  The live database runs in the `chess-database` Docker volume (see `docs/DEVELOPMENT_SERVICES.md`);
  host-side edits under `database/` do not reach the running workers.
- `stockfish/` — ignored local engine files

Database schema source lives in [`src/chess_move_trainer/database/`](../src/chess_move_trainer/database/).
