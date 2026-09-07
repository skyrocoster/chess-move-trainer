# Database configuration examples

These files are examples with safe placeholders, not ready-to-run personal configuration.

- `database-games.example.yaml` is shared by `games acquire` and `games import`.
- `database-rebuild.example.yaml` is consumed by the `rebuild` commands.

Replace placeholders only in a private local copy. Real identity must never be committed,
including usernames, trainer UUIDs, personal paths, secrets, or other personal identifiers.

The fixed `openings acquire` command has no YAML configuration file; provide its source directory
explicitly with `--source-dir`.
