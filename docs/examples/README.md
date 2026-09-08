# Database configuration examples

These files are examples with safe placeholders, not ready-to-run personal configuration.

- `database-games.example.yaml` documents the private source configuration used by `setup` and
  `update games`.
- The database destination is not configured here: all three data-loading workflows use the fixed
  `data/database/chess.db` path.

Replace placeholders only in a private local copy. Real identity must never be committed,
including usernames, trainer UUIDs, personal paths, secrets, or other personal identifiers.

`update openings` has no YAML configuration file; it obtains and validates the latest complete
five-file opening set as part of that workflow.
