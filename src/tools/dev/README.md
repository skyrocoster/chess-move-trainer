# sg developer CLI: implementation map

`sg` is the Python developer CLI (`uv run --no-sync sg --help`; also `.venv/Scripts/sg.exe` or
`python -m tools.dev`). For usage see [`docs/TESTING.md`](../../../docs/TESTING.md) and
[`docs/DEVELOPMENT_SERVICES.md`](../../../docs/DEVELOPMENT_SERVICES.md). This page only says where code lives.

## Modules

| Path | Owns |
|---|---|
| `config.py` | Repository paths, service names, budget defaults, fixture profiles, layer roots. |
| `console.py` | `echo`, `fail`, `run` (mandatory finite timeout, `--dry-run` support), `output`, Windows `npm`/`npx` wrapping, process-tree kill. |
| `cli/main.py` | The root Typer app: `setup` (prerequisite report), `where`, and the groups below. |
| `cli/dev_commands.py` | `sg dev ...` argument parsing; calls `services`. |
| `cli/check_commands.py` | `sg check` (run, resume, `--list/--fresh/--from/--only`) and `sg check services`. |
| `cli/test_commands.py` | `sg test list/show/run/profiles/failures/report/catalog`. |
| `cli/screenshot_commands.py` | `sg screenshot`. |
| `services/compose.py` | Compose command building, env-var budgets, Docker preflight. |
| `services/workers.py` | `compose ps` parsing, worker mode, service health, starting and stopping workers. |
| `services/jobs.py` | One-shot worker containers: live-database probe and update jobs with a time budget. |
| `services/lifecycle.py` | The `sg dev` actions: start, stop, restart, rebuild, status, logs, update, setup-db. |
| `checks/full_process.py` | The ordered check inventory, checkpoint in `.stage-check/full-test/`, warnings-as-failure. |
| `test/` | Catalogue loading (`catalog.py`), discovery and cache, selection, profiles, runner commands (`backends.py`), run reports. |
| `screenshots/` | Capture driver (`driver.mjs`), `capture.py`, and the target catalogue (`catalog.py`). |

`driver.mjs` is copied unchanged from the reference tool and is the one file allowed over the size limit.

## How to add things

- **A test domain or test file:** add its path or glob to the owning domain in `tests/catalog/domains.toml`
  (rules in `tests/catalog/README.md`). `sg test list --tree` and `backend/tests/tooling/test_test_catalog.py`
  fail on an unregistered or doubly registered file.
- **A check step:** add a `Step` to `build_steps()` in `checks/full_process.py`, keeping behaviour checks before
  lint and lint before formatting, with a finite timeout. `backend/tests/tooling/test_full_process.py` pins the
  order and the inventory.
- **A screenshot target:** add a `CatalogTarget` to `TARGETS` in `screenshots/catalog.py`. Every route in
  `frontend/src/App.tsx` needs a target or a `ROUTE_EXEMPTIONS` entry
  (`backend/tests/tooling/test_screenshots.py`). Actions must never save, create or delete.
- **A `sg dev` action:** put the Docker logic in `services/lifecycle.py` and the argument parsing in
  `cli/dev_commands.py`; every command goes through `console.run` so `--dry-run` and timeouts apply.

Tests for all of this live in `backend/tests/tooling/` and never call Docker or a browser.
