# Test catalogue

`domains.toml` is the authoritative test taxonomy for Chess Move Trainer. It answers three questions: which
domain owns a test, what that domain is responsible for, and how to run exactly that test. Case names are
**discovered** from the frameworks, so the catalogue never keeps a second copy of the test list.

Every `sg` command here is shorthand for `uv run --no-sync sg`.

## How the catalogue works

- **Domains** are coherent product responsibilities or distinct infrastructure (`games`, `preferred-moves`,
  `repertoire-builder`, `database-lifecycle`, `tooling`). A test belongs to the domain whose invariant fails
  when the test fails; a test that spans two domains lives where the consumer-visible contract is, and
  secondary interests become tags, not duplicates.
- **Layers are orthogonal**: the same domain can appear under `backend` (every Python test in `backend/tests`
  and `tests/`), `frontend` (Vitest unit project), `frontend-api` (Vitest tests that need the live backend,
  run with `frontend/vitest.api.config.ts`) and `e2e` (Playwright). Layer comes from file location and runner,
  never from the TOML.
- **Paths attach metadata**: `[domains.<id>] paths` and `[domains.<id>.subdomains.<name>] paths` are
  repository-relative globs. A test file must match exactly one domain or subdomain; `sg test list` fails when
  a file matches none or several.
- **Fixture profiles** are `none`, `temp-db`, `live-services`, `browser` and `real-db`. The live database is
  never a fixture except for the opt-in `real-db` tests, which only run through `sg test profiles real-data`.
- **Profiles** are fixed, bounded suites: `quick` (all Python tests and the frontend unit project, no
  services), `smoke` (a small offline cross-section), `full` (quick plus the live-backend API test and every
  Playwright spec, needs healthy services), `e2e` (Playwright only) and `real-data` (explicit opt-in).

## Where does a new test go?

1. Run `sg test list --tree` and read the closest domain with `sg test show <domain>`.
2. Name the invariant and check that no existing case already owns it. Prefer extending a file that proves
   adjacent behaviour.
3. Choose the **lowest layer** that can prove it: backend behaviour in `backend/tests/features/<feature>/` or
   `tests/database/`, frontend logic in a `*.test.ts(x)` beside its feature under `frontend/src/`, and
   Playwright in `tests/e2e/` only when the real browser and app boundary is under test.
4. Name the file after the behaviour (`test_preferred_move_api.py`, `PreferredMovePanel.test.tsx`).
5. **Register it in the same change**: add its path or glob to the owning domain (or subdomain) in
   `domains.toml`. An unregistered test file fails `sg test list`, `sg test run` and the guard test
   `backend/tests/tooling/test_test_catalog.py`.
6. Run only the new case and its neighbours, dry-run first (`sg test run --id <id> --dry-run`).

## IDs

Ids are stable logical names, independent of physical folder moves:

| Layer | Shape | Example |
|---|---|---|
| Python (pytest) | `backend.<domain>[.<subdomain>].<file-slug>::<node-id>` | `backend.health.test-health::test_health_returns_ok` |
| Frontend Vitest | `frontend.<domain>[.<subdomain>].<file-slug>` | `frontend.status.status-view-test` |
| Live-backend client | `frontend-api.<domain>.<subdomain>.<file-slug>` | `frontend-api.health.client.health-client-test` |
| Playwright | `e2e.<domain>.<spec-slug>::<title-slug>` | `e2e.health.status-page-spec::<title-slug>` |

Vitest files are selectable **file groups**: one id selects every test in that file. A file/group id without
`::` selects every case in that file for pytest and Playwright too. `sg test show <id>` prints the details and
the exact `run` command.

## Rules that `sg test` enforces

- `run --id` must resolve to a real case or file group; zero matches fail with close matches.
- A domain/layer selection that resolves to zero units fails.
- `real_data` cases (fixture `real-db`) are refused by `run`; only `profiles real-data` runs them.
- `list`, `show` and `catalog` are read-only and never build, export or start a development service.
- Every run persists a report under `build/test-results/<run-id>/summary.json`; soft budgets warn and hard
  per-command deadlines kill the process tree. `failures` and `report` read the newest run.
- Discovery that fails is never cached.
