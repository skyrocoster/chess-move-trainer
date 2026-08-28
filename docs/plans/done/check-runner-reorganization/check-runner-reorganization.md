# Check runner reorganization - Plain `check.py` becomes a ~2-minute fail-fast quick suite; `--full` keeps the complete coverage.

> **Status:** done - all stages complete

- **Read trigger:** Read before implementing or validating the check-runner quick/full reorganization.
- **Upstream:** [Check runner reorganization grilling synthesis](../../grilling-docs/check-runner-reorganization.md)

## Outcome

Running `.venv/Scripts/python.exe scripts/check.py` becomes a fast, boring, fail-fast quality loop for a
Python-comfortable, non-TypeScript/React-expert user doing AI-assisted coding: roughly two minutes, two
concise lines per check (start, then PASS/FAIL/TIMEOUT with duration), stopping at the first failure with a
short excerpt, an overwritten `artifacts/check-failure.log`, and a practical native rerun command. `--full`
keeps the complete suite (production and Storybook builds, Storybook validation and coverage, E2E), and the
AI `--fix` policy in `AGENTS.md` is updated so an AI may run deterministic formatting/lint fixes after a
read-only check, inspect the resulting diff, and never use it for semantic repair.

## Scope

- **Included:** the quick/full runner split; fail-fast sequential execution; finite per-check subprocess
  timeouts with the `--timeout-multiplier` CLI override; two-line START/PASS/FAIL/TIMEOUT output with
  durations; failure excerpt plus `artifacts/check-failure.log` overwrite and stale-log removal on success;
  native rerun guidance; a TypeScript type-check step in quick; a minimal Vitest worker cap at six if
  supported; quiet helper success output needed for the two-line contract; the AGENTS.md AI `--fix` policy
  and quick/`--full` wording; the active Plan and the confirmed grilling synthesis.
- **Expected areas:**
  - `scripts/checks/steps.py`
  - `scripts/checks/cli.py`
  - `scripts/checks/schema.py` (quiet success output only)
  - `scripts/checks/workflow.py` (quiet success output only)
  - `scripts/checks/storybook.py` (quiet success output and optional timeout parameter only; the settled
    bounded `test-storybook` command is untouched)
  - `scripts/checks/coverage.py` (quiet success output only; gap report retained)
  - `scripts/tests/test_check.py`
  - `frontend/vitest.config.ts` (worker cap only)
  - `AGENTS.md` (AI `--fix` policy and quick/`--full` wording, additive text only)
  - `docs/grilling-docs/check-runner-reorganization.md` (written during planning as historical evidence)
  - `docs/plans/active/check-runner-reorganization/check-runner-reorganization.md` (this Plan)
- **Excluded:** new dependencies (for example pytest-xdist) and any new concurrency machinery; product,
  backend, API, and data code; `tests/e2e/playwright.config.ts` and E2E harness changes; the settled
  Vitest project structure and the settled `test-storybook` wiring; dashboards, structured JSON/reporting
  frameworks, cross-group concurrency, historical timing databases, and adaptive orchestration; done Plans
  and historical records (including the completed Storybook/Vitest migration Plan); README implementation
  edits — `scripts/README.md` and other README updates are follow-up README maintenance the coordinator
  routes to `readme-updater` after structural behavior changes; commits and pushes; unrelated worktree
  changes.

## Stages

1. **complete** - **Runner core and CLI.** Update `scripts/checks/steps.py`, `scripts/checks/cli.py`,
   quiet helper success output, and the necessary `scripts/tests/test_check.py` behavior updates.
   - **Ordered actions:**
     1. In `steps.py`: add `timeout: float | None = None` to the `Step` dataclass; add a per-step timeout
        table with these defaults (seconds): Source size 60, Ruff lint 120, Ruff format 120, Prettier 180,
        ESLint 300, TypeScript type check 300, Python tests 600, Workflow tests 180, Frontend tests (unit
        project) 600, Frontend build 900, Storybook build 900, Storybook validation 300, End-to-end tests
        1800, and the fix steps 120 each. Rewrite `run_step` to print a START line, run via
        `subprocess.Popen` + `communicate(timeout=...)` with the existing capture/encoding options, on
        `TimeoutExpired` call `stop_process_tree` and report TIMEOUT with elapsed time and limit, on
        success report PASS with duration, and on failure report FAIL with duration, print a short excerpt
        (the tail, roughly the last 20 lines, of merged stdout+stderr), write the full merged output to
        `artifacts/check-failure.log` (creating `artifacts/` as needed, overwriting), and print the log
        path. Keep the documented Storybook-build Windows teardown special-case exactly. Add a
        `remove_stale_failure_log()` helper that deletes `artifacts/check-failure.log` when present.
     2. In `cli.py`: define the ordered quick list (Database schema freshness, Workflow contract, Source
        size, Ruff lint, Ruff format, Prettier, ESLint, TypeScript type check, Python tests, Workflow
        tests, Frontend tests) and the full list (quick plus Frontend build, Storybook build, Storybook
        coverage, Storybook validation, End-to-end tests); add `--full` and `--timeout-multiplier`
        (float, default 1.0) options; apply the multiplier to every step timeout; run checks sequentially
        and stop at the first failure; wrap the in-process checks (schema, workflow, coverage, storybook
        validation) in the same START/RESULT lines with durations; on failure print a native rerun command
        derived from the step's command (noting cwd when not the repository root); update `--list` to
        print the effective list (quick by default, full with `--full`) with tags and timeouts; call
        `remove_stale_failure_log()` when a run fully succeeds; preserve `--fix` (fix steps then
        verification), `--only`, `--from`, `--no-build`, `--quiet` (suppresses START lines), and the
        category selectors `--lint`, `--python`, `--frontend`, `--e2e`, `--build`, `--storybook`.
     3. Give `run_storybook_validation` an optional `timeout` parameter defaulting to the existing
        `STORYBOOK_TEST_TIMEOUT_SECONDS` (300) so the multiplier applies; do not change its command.
        Quiet the success prints in `schema.py`, `workflow.py`, `storybook.py`, and `coverage.py`; keep
        the schema failure `--fix` guidance, the coverage gap report, and the storybook validation failure
        output as the excerpt.
     4. Update `scripts/tests/test_check.py` behavior tests to the new model: default quick membership and
        order, `--full` membership, fail-fast stop on the first failure, `--only`/`--from`/`--no-build`/
        `--storybook`/`--fix` behavior, `--list` output, and capsys assertions adjusted for the removed
        success prints. Keep the file within the 700-line test limit.
   - **Focused proof:**
     - `timeout 60s .venv/Scripts/python.exe -m ruff check scripts` (bash tool timeout `120000ms`)
     - `timeout 60s .venv/Scripts/python.exe -m ruff format --check scripts` (bash tool timeout `120000ms`)
     - `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700` (bash
       tool timeout `120000ms`)
     - `timeout 120s .venv/Scripts/python.exe -m pytest scripts/tests/test_check.py -q` (bash tool timeout
       `180000ms`)
     - `timeout 120s .venv/Scripts/python.exe -m pytest scripts/tests -q` (bash tool timeout `180000ms`)
   - **Acceptance:** rewritten tests pass; Ruff, format, and size checks pass; the Storybook-build Windows
     teardown special-case and the settled `test-storybook` command are byte-for-byte unchanged.
   - **Exclusions:** no new dependencies; no changes to `tests/e2e/playwright.config.ts`, frontend
     build/test scripts, or the Vitest project structure.
   - **Escalate:** any need to change the settled `storybook.py` command, the Vitest project structure, or
     the Storybook-build teardown special-case; any failure that would require product-code repair.
2. **complete** - **Runner tests, worker cap, and quick sanity.** Add `scripts/tests/test_check.py` unit
   tests for the new runner mechanics, apply the minimal Vitest worker cap if supported, and verify the
   quick-suite time and output shape.
   - **Ordered actions:**
     1. Add mocked unit tests for: timeout application (`Step.timeout` and `--timeout-multiplier`),
        `TimeoutExpired` producing a TIMEOUT line and process-tree stop, failure writing
        `artifacts/check-failure.log` (inject a temp path) and printing the excerpt, success removing a
        stale failure log, and fail-fast ordering in `main`. Keep the file within the 700-line test limit;
        split into a second test module only if required, without creating generalized helper architecture.
     2. If supported by the settled Vitest 4 config, cap Vitest workers at six in `frontend/vitest.config.ts`
        (for example `poolOptions.forks.maxForks: 6`, or the threads equivalent if the settled config uses
        threads); verify the default pool first; add no dependency.
     3. Run the quick suite once to confirm roughly two minutes warm and the two-line per-check output with
        no noisy success output.
   - **Focused proof:**
     - `timeout 120s .venv/Scripts/python.exe -m pytest scripts/tests/test_check.py -q` (bash tool timeout
       `180000ms`)
     - `timeout 120s .venv/Scripts/python.exe -m pytest scripts/tests -q` (bash tool timeout `180000ms`)
     - only if the worker cap is added: `timeout 300s npm.cmd run test --prefix frontend -- --run --project=unit`
       (bash tool timeout `360000ms`)
     - `timeout 300s .venv/Scripts/python.exe scripts/check.py` (bash tool timeout `360000ms`)
   - **Acceptance:** new tests pass; the quick suite completes in roughly two minutes warm with exactly two
     concise lines per check; the worker cap (if added) keeps unit tests green and does not alter the
     settled Vitest project structure.
   - **Exclusions:** no parallelization machinery, no new dependencies, no E2E config changes.
   - **Escalate:** the quick suite materially exceeds roughly two minutes warm on this machine; the worker
     cap changes settled migration behavior; any decision to add a concurrency dependency.
3. **complete** - **AGENTS.md policy wording, full closeout, and follow-up routing.** Update `AGENTS.md`,
   run the full `--full` closeout, audit scope, and route README maintenance.
   - **Ordered actions:**
     1. Update `AGENTS.md` wording (additive text only): plain `scripts/check.py` is the quick ~2-minute
        suite; `.venv/Scripts/python.exe scripts/check.py --full` is the complete closeout; record the AI
        `--fix` policy — an AI may invoke `scripts/check.py --fix` after a read-only check identifies
        deterministic formatting/lint issues, must inspect the resulting diff, and must not use it for
        semantic repair.
     2. Run the full closeout `.venv/Scripts/python.exe scripts/check.py --full` wrapped with the explicit
        finite command-level timeout `timeout 1800s` and bash tool timeout `1860000ms`; report any
        baseline/unrelated failures with evidence rather than absorbing them.
     3. Run the final scope audit `timeout 60s sh -c 'git diff --check && git status --short'` (bash tool
        timeout `90000ms`); report unrelated worktree changes; never commit or push.
     4. Record `scripts/README.md` (the `check.py` row: quick suite plus `--full`) and any other README
        updates as follow-up README maintenance for the coordinator to route to `readme-updater`; do not
        edit READMEs in this Plan.
   - **Focused proof:**
     - inspect the AGENTS.md diff (policy wording present, additive only)
     - `timeout 1800s .venv/Scripts/python.exe scripts/check.py --full` (bash tool timeout `1860000ms`)
     - `timeout 60s sh -c 'git diff --check && git status --short'` (bash tool timeout `90000ms`)
   - **Acceptance:** the `--full` closeout passes or unrelated baseline failures are reported with
     evidence; `git diff --check` is clean; the AGENTS.md policy is recorded; README follow-up is routed to
     the coordinator.
   - **Exclusions:** README implementation edits; done Plan and historical record changes; commits and
     pushes; absorbing or repairing unrelated baseline failures.
   - **Escalate:** any requirement to fix unrelated baseline failures (report only); any product, visual,
     API, data, dependency, destructive, ownership, or acceptance decision.

Stages are sequential. No stage may start before the preceding stage's proof and escalation boundary are
resolved.

## Progress and decisions

- **Stage 1:** complete - runner core and CLI implemented: `Step.timeout` and per-step defaults; `run_step`
  rewritten with `Popen` + `communicate(timeout=...)`, process-tree stop on `TimeoutExpired`, START/
  PASS/FAIL/TIMEOUT lines with durations, 20-line excerpt, `artifacts/check-failure.log` overwrite, stale-log
  removal helper, and rerun guidance; the Storybook-build Windows teardown special-case preserved unchanged;
  `cli.py` defines `QUICK_NAMES`/`FULL_NAMES`, adds `--full` and validated `--timeout-multiplier`, runs
  checks sequentially and stops at the first failure, wraps in-process checks (schema, workflow, coverage,
  storybook validation) in the same status lines, updates `--list`, and preserves `--fix`, `--only`,
  `--from`, `--no-build`, `--quiet`, and the category selectors; quiet success output applied in
  `schema.py`, `workflow.py`, `storybook.py`, and `coverage.py`; `run_storybook_validation` gained the
  optional `timeout` parameter (default 300s) with its settled command untouched; `test_check.py` rewritten
  for quick/full membership and order, fail-fast stopping, selectors, `--fix`, `--list`, multiplier
  validation/reach, and the storybook validation wiring. Proof passed: `ruff check scripts`, `ruff format
  --check scripts`, `check_size.py`, `pytest scripts/tests/test_check.py` (18 passed), and
  `pytest scripts/tests` (26 passed), each with explicit finite timeouts. One repair cycle fixed a missing
  `Step` import, long lines via the deterministic formatter on the changed files, and the `--storybook`
  coverage routing. Breakpoint: none.
- **Stage 2:** complete - added 7 mocked runner-mechanics tests to `scripts/tests/test_check.py`: timeout
  application (`Step.timeout` and `--timeout-multiplier` reaching `communicate(timeout=...)`), default
  timeout when a step has none, `TimeoutExpired` producing a TIMEOUT line plus process-tree stop, failure
  writing `artifacts/check-failure.log` (temp path injected) and printing the 20-line excerpt, stale-log
  removal on success (and no-op when absent), and fail-fast ordering with a middle-step failure that skips
  stale-log removal. The file is 413 lines, under the 700-line limit, no split needed. Capped the Vitest
  unit project at six workers in `frontend/vitest.config.ts` using `maxWorkers: 6` with
  `sequence.groupOrder: 1`: Vitest 4.1.5 removed `poolOptions` (top-level `maxWorkers` is the supported
  option, default pool is `forks`), and projects with differing `maxWorkers` require distinct
  `groupOrder`, so the unit project owns its group while the Storybook project config is untouched. Proof
  passed with explicit finite timeouts: `pytest scripts/tests/test_check.py` (25 passed),
  `pytest scripts/tests` (33 passed), `npm run test --prefix frontend -- --run --project=unit` (34 files,
  257 tests), and the warm quick suite (53.6s total, two concise lines per check, no noisy success output;
  fail-fast demonstrated when the first quick run stopped at Ruff format). One bounded deterministic
  repair: `ruff format` applied to the new test file after the quick suite flagged it; focused proof
  reran green. Breakpoint: none.
- **Stage 3:** complete - AGENTS.md policy recorded with a narrow
  replacement of the two applicable command bullets: plain `scripts/check.py` is the fast fail-first local
  suite (~2 minutes, stops at the first failure), `--full` is the complete local closeout suite (builds,
  Storybook, E2E), `--fix` stays explicit and deterministic, and an AI may invoke `scripts/check.py --fix`
  without asking again only after a read-only check identifies deterministic formatting/lint issues, must
  inspect the resulting diff, and must not use it for semantic repair; the existing MANDATORY SAFETY
  finite-timeout line already covers the timeout rule and was left untouched, and the pre-existing
  `>=24 <25` engines edit in AGENTS.md is preserved. Full closeout
  `timeout 1800s .venv/Scripts/python.exe scripts/check.py --full` passed all 16 checks: quick suite green,
  Frontend build 10.9s, Storybook build 14.2s, Storybook coverage 0.0s (retained gap report), Storybook
  validation 26.5s, End-to-end tests 46.6s, total ~153s. Final audit: `git diff --check` is clean on all
  Plan paths (AGENTS.md, active Plan, scripts/checks, scripts/tests/test_check.py, frontend/vitest.config.ts);
  it also surfaced one concurrent unrelated edit to `.opencode/skills/grilling/SKILL.md` (a new "Grilling
  Q&A Template" section with trailing whitespace on the Recommendation line) that appeared after Stage 2;
  it is outside Plan scope and is reported, not absorbed. README follow-up completed by coordinator-routed
  `readme-updater`: only `scripts/README.md` was edited, updating the `check.py` row to the quick suite
  (~2 min, stops at the first failure), the `--full` complete closeout suite, and explicit deterministic
  `--fix`; no validation was required and no other READMEs changed. Fresh independent Quality validation
  returned PASS: 25 focused `test_check.py` tests, all 33 `scripts/tests`, Ruff lint/format, source-size,
  the quick suite (all 11 checks with concise START/PASS output), scoped approved diff clean, implementation
  scope clean, full membership supported, and the prior Stage 3 `--full` run (all 16 checks, ~153s). The
  unrelated `.opencode/skills/grilling/SKILL.md` trailing whitespace remains outside scope and is not this
  Plan's failure. Breakpoint: none; Plan closed to done.

## Proof

- Focused per-stage commands are listed inside each stage with explicit finite command-level timeouts and
  finite bash tool timeouts.
- Full closeout (Stage 3) uses exactly `timeout 1800s .venv/Scripts/python.exe scripts/check.py --full`
  (bash tool timeout `1860000ms`); baseline/unrelated failures are reported, not absorbed.
- Final audit uses `timeout 60s sh -c 'git diff --check && git status --short'` (bash tool timeout
  `90000ms`).
- Independent Quality validation (coordinator-routed after implementation): returned PASS - re-ran the
  focused pytest proofs (25 `test_check.py` tests, all 33 `scripts/tests`), Ruff lint/format and source-size
  checks, the quick suite (all 11 checks with concise START/PASS output), and the scoped approved diff
  check; confirmed implementation scope clean and full membership supported (prior Stage 3 `--full` run
  passed all 16 checks in ~153s).

## Escalation boundaries

- Stop before edits when an expected-area path has a direct concurrent change; preserve unrelated dirty
  worktree content.
- Any new dependency (for example pytest-xdist) or new concurrency machinery requires escalation.
- Any change to the settled Vitest project structure, the `test-storybook` command wiring, or the
  Storybook-build Windows teardown special-case requires escalation.
- Removing or weakening coverage under `--full`, editing done Plans or historical records, or changing
  product/backend/E2E behavior requires escalation.
- Any requirement to repair unrelated baseline failures is reported, not absorbed; after one failed
  authorized repair, return to the coordinator.
- Do not commit or push.

## Visible result

> Running `.venv/Scripts/python.exe scripts/check.py` finishes in about two minutes and stops at the first
> failing check with a short excerpt, a failure log at `artifacts/check-failure.log`, and a rerun command;
> `.venv/Scripts/python.exe scripts/check.py --full` still runs the complete suite including builds,
> Storybook, and E2E.