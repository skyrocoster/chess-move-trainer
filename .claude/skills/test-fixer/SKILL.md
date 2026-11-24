---
name: test-fixer
description: Run Chess Move Trainer's full check (`sg check`: every test, build, lint and format step) and repair every failure until it passes cleanly. Use when the user asks for the full check, "test-fixer", or final repository-wide proof. Not for focused feature work.
---

# Test fixer (Chess Move Trainer)

Drives this repository's complete check to a clean pass. Running the whole check is the goal here, so this
overrides the "targeted tests only" rule for this task. This skill overrides the user-level `test-fixer`. The
full command reference is [`docs/TESTING.md`](../../../docs/TESTING.md).

## Rules

- Run everything from the repository root in Git Bash as `uv run --no-sync sg ...`, with an explicit finite
  timeout on every command. The full check is long: run it in the background and read the output when it ends.
- Never weaken, skip or delete a valid test, add a warning suppression, or edit an allow-list to go green.
  Warnings are failures; the only allowed warning is the npm `EBADENGINE` Node-version warning.
- Never touch the `chess-database` Docker volume or `data/database/chess.db`.
- Preserve unrelated worktree changes. Do not commit or push unless asked.

## Steps

1. Services are shared. Run `uv run --no-sync sg dev status` first. If backend, frontend or datasette are not
   healthy, run `uv run --no-sync sg dev start` (never start Uvicorn or Vite directly, never `docker compose down`).
2. Show the inventory with `uv run --no-sync sg check --list` and state it to the user in one short block.
3. Run `uv run --no-sync sg check`. It stops at the first failure and resumes there next time. Use `--fresh` to
   discard progress and start at check 1.
4. On a failure, read the terminal output and `.stage-check/full-test/latest-failure.log`, then fix the root cause:
   - One failing test: reproduce it with `uv run --no-sync sg test run --id <id>` (find ids with
     `sg test failures`). Delegate that single id to `vicar` (model `haiku`) with the command, the real failure
     output and write scope; escalate to `jesus` (model `sonnet`) if it fails twice or the cause is unclear.
     Small repairs can be done directly.
   - A non-test check (dependencies, TypeScript, build, config): fix the cause, then rerun just that check with
     `uv run --no-sync sg check --only "<name>"`.
5. Repair behaviour failures (tests, build, end-to-end) before lint and format. For style failures, run the
   tool's own fixer (`ruff check --fix`, `ruff format`, Prettier) over the same scope and review the diff. A
   behaviour change reruns from the earliest affected check with `sg check --from "<name>"`.
6. Repeat until `uv run --no-sync sg check` reports every step passed in one fresh run
   (`PASS complete full-test process`) against the final worktree. Any later edit needs the affected checks rerun.

## Report

The final passing command and result, each failure found and its cause, files changed, and anything unresolved.
If stopped on a blocker: the failing check, exact command and the relevant output.
