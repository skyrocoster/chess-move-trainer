# Testing, checks and screenshots

This page owns how to run tests, the full check, and UI screenshots. Everything goes through the `sg` developer
CLI. Starting and stopping the Docker services is covered in [`DEVELOPMENT_SERVICES.md`](DEVELOPMENT_SERVICES.md).

## Bootstrap

Run once from the repository root in Git Bash (first-time setup is described in
[`DEVELOPMENT_SERVICES.md`](DEVELOPMENT_SERVICES.md#first-time-setup)), then run every command as:

```bash
uv sync --frozen
uv run --no-sync sg --help
```

In the catalogue README and below, `sg` is shorthand for `uv run --no-sync sg`; the commands here are written out
in full so they can be copied. Every shell command needs an explicit finite timeout (for example
`timeout 300 uv run --no-sync sg test run --id ...`).

## Running tests: `sg test`

Tests are organised in a catalogue of domains (health, games, openings, analysis, and so on). The catalogue file
is `tests/catalog/domains.toml`; its rules, id shapes and "where does a new test go" guidance are in
[`tests/catalog/README.md`](../tests/catalog/README.md). Test names are discovered from pytest, Vitest and
Playwright, so there is no second copy of the test list to maintain.

```bash
# Domain tree with the number of discovered tests per layer. Add --tree to list files, --json for scripts.
uv run --no-sync sg test list
uv run --no-sync sg test list --domain health --tree
uv run --no-sync sg test list --layer e2e

# Details and the exact run command for a domain, file group or single test id.
uv run --no-sync sg test show health
uv run --no-sync sg test show backend.health.test-health::test_cors_allows_frontend_origin

# Run exactly one test or file group. Use --dry-run first to see the commands without running them.
uv run --no-sync sg test run --id backend.health.test-health::test_cors_allows_frontend_origin --dry-run
uv run --no-sync sg test run --id backend.health.test-health::test_cors_allows_frontend_origin
uv run --no-sync sg test run --id frontend.health.status-view-test

# Run every test of a domain or layer.
uv run --no-sync sg test run --domain health --layer backend

# Newest run: failures with exact rerun commands, and the saved summary.
uv run --no-sync sg test failures
uv run --no-sync sg test report
```

Rules `sg test` enforces:

- **Zero matches fail.** An `--id` that matches nothing, or a domain/layer selection that resolves to zero tests,
  is an error (close matches are shown), never a silent pass.
- **Every new test file must be registered** in `tests/catalog/domains.toml` in the same change. An unregistered
  file makes `sg test list`, `sg test run` and `backend/tests/tooling/test_test_catalog.py` fail.
- Every run saves a report under `build/test-results/<run-id>/summary.json`; `failures` and `report` read the
  newest run (or `--run <run-id>`).
- `list`, `show` and `catalog` are read-only and never start a service.

Example ids: `backend.health.test-health::test_cors_allows_frontend_origin` (one pytest case),
`frontend.health.status-view-test` (every test in `StatusView.test.tsx`),
`frontend-api.health.client.health-client-test` (needs the live backend).

### Profiles

```bash
uv run --no-sync sg test profiles quick --dry-run
uv run --no-sync sg test profiles quick
```

| Profile | What it runs | Needs services |
| --- | --- | --- |
| `quick` | Every Python test and the frontend unit project | No |
| `smoke` | A small offline cross-section: health API, status page, database connection | No |
| `full` | `quick` plus the live-backend API client test and every Playwright spec | Yes: check `sg dev status` |
| `e2e` | Playwright browser specs only, against the live services | Yes |
| `real-data` | Opt-in tests that read the real database file | See below |

Playwright reuses healthy services; it does not start its own when they are already running. Do not run the whole
`full` profile as a first step; start with the narrowest `--id`.

**Real-data is opt-in and env-gated.** These tests are skipped unless a `CHESS_RUN_REAL_*` variable enables them
(`CHESS_RUN_REAL_DB_SMOKE`, `CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE`; the API benchmark uses
`CHESS_RUN_API_BENCHMARK_REAL`, see [`benchmarks/API/README.md`](benchmarks/API/README.md)). They read the real
database file and verify it is unchanged. `sg test run` refuses them; only `sg test profiles real-data` runs them.
Which database files are live and which are host exports is explained in [`../data/README.md`](../data/README.md).

## The full check: `sg check`

The full check is the complete local maintenance run. It is different from focused feature proof: it runs every
defined test, build and quality check, stops at the first problem, and remembers where to continue after the
problem is fixed.

```bash
# Show the ordered inventory (authoritative) without running it.
uv run --no-sync sg check --list

# Start at check 1, or resume at the remembered failure.
uv run --no-sync sg check

# Discard progress and start at check 1.
uv run --no-sync sg check --fresh

# Restart at one exact or uniquely matching check, for example after a fix invalidates earlier proof.
uv run --no-sync sg check --from "Ruff lint"

# Run exactly one matching check without changing the checkpoint.
uv run --no-sync sg check --only "TypeScript"

# Fail unless backend, frontend and datasette are healthy (this is also check 7).
uv run --no-sync sg check services
```

The current order (from `sg check --list`) is: Compose configuration, Python dependency integrity, Node
dependency integrity, TypeScript, Python tests (including opt-in real tests), frontend unit tests, development
service preflight, frontend real-backend API tests, frontend production build, Playwright end-to-end tests, source
size limits, Ruff lint, ESLint, Ruff formatting, Prettier formatting. Behaviour checks come first, then lint, then
formatting. Every check has its own finite timeout.

State is written to ignored, machine-local files under `.stage-check/full-test/`:

- `state.json` identifies the next check. It points at the running check before it starts, so an interruption
  safely reruns that check.
- `latest-failure.log` holds the complete output of the first failed check.

On a failure, fix that one issue and run `sg check` again: the failed check reruns and the rest continue. A
completed run deletes the checkpoint and failure log. If the check inventory changes while a checkpoint exists,
the old checkpoint is rejected and the run starts at check 1.

### Failure and warning policy

The run stops immediately for a nonzero exit, a timeout, or warning output even when the command exits
successfully. Pytest runs with `-W error`, ESLint with `--max-warnings 0`, and pytest, Vitest and Playwright stop
at their first failure. The only allowed warning is the local npm `EBADENGINE` warning when the installed Node
version is outside the repository's Node 24 pin. Do not suppress any other warning, and do not skip, weaken or
delete a valid test to move the checkpoint.

### Repair loop

1. Run `uv run --no-sync sg check` until it stops.
2. Read the terminal output and, if needed, `.stage-check/full-test/latest-failure.log`.
3. Repair only the first failure.
4. Run the same command to resume at that check.
5. If the repair could affect a check that already passed, use `--from` with the earliest affected check. For
   example, changing Python source after Ruff passed means rerunning from the Ruff checks.
6. Finish only when the run prints `PASS complete full-test process` in one fresh pass over the final files.

Before the service preflight or any browser work, follow [`DEVELOPMENT_SERVICES.md`](DEVELOPMENT_SERVICES.md):
reuse healthy services, read logs before restarting an unhealthy one, and never start Uvicorn or Vite directly.
The full check does not install optional scanners, commit changes, or add CI.

## Screenshots: `sg screenshot`

Captures UI screenshots plus a JSON manifest for visual review. The frontend (`http://127.0.0.1:8444`) and
backend must be healthy first (`uv run --no-sync sg dev status`).

```bash
# Named targets, viewports and groups, without capturing.
uv run --no-sync sg screenshot --list

# Home page at the default desktop viewport.
uv run --no-sync sg screenshot

# One named target at the review viewport group, or a route, or label=/route.
uv run --no-sync sg screenshot trainer --viewport review
uv run --no-sync sg screenshot /analysis --viewport 1280x800 --full-page

# Every named application target.
uv run --no-sync sg screenshot --all
```

Named targets: `home` (`/`), `repertoire` (`/repertoire`), `trainer` (`/trainer`), `analysis` (`/analysis`),
`not-found`. Viewports: `desktop` 1440x900 (default), `wide`, `laptop`, `tablet`, `mobile`, `surface`,
`surface-portrait`, or any `WIDTHxHEIGHT`; the group `review` is surface, surface-portrait and mobile. Output goes
to a timestamped folder under `build/screenshots/` (or `--output <dir>`). `--strict` exits non-zero when a page
logs console, page or network errors. Run `uv run --no-sync sg screenshot --help` for the remaining options
(`--wait-for`, `--selector`, `--timeout-ms`).
