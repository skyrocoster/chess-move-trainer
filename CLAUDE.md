@AGENTS.md

The general workflow (subagents scout/jesus/vicar, Titan, test discipline) is user-level in `~/.claude/CLAUDE.md`
and is not repeated here.

## Facts every subagent packet must carry

- Run commands as `uv run --no-sync sg ...` from the repository root in Git Bash.
- Narrow tests with `uv run --no-sync sg test run --id <id>`. Find ids with
  `uv run --no-sync sg test list --domain <d>`, and use `--dry-run` first. See `docs/TESTING.md`.
- A new test file must be added to `tests/catalog/domains.toml`.
- Never touch the `chess-database` Docker volume or `data/database/chess.db`.
- Read-only packets never start or stop services; check `uv run --no-sync sg dev status`.
- The per-repo subagent hook (`.claude/hooks/restrict-subagents.js`) allows only scout, jesus and vicar, each
  with an explicit non-Opus model.
