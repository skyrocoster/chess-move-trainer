# Check Runner Reorganization — Canonical Historical Grilling Synthesis

**Canonical consolidation:** 2026-08-28
**Status:** Historical and directional evidence from the confirmed user decisions; no implementation authority
**Implementation authority:** The active Plan at `docs/plans/active/check-runner-reorganization/check-runner-reorganization.md`
**Relationship:** Durable record of the confirmed quick/full check-runner policy that the active Plan implements.

## Confirmed decisions

1. Plain `scripts/check.py` becomes a roughly two-minute quick suite.
2. `--full` runs expensive production builds, Storybook checks, and E2E.
3. Check groups run sequentially and stop at the first failure (fail-fast).
4. Individual test runners may use up to six workers where safely supported; six is the ceiling for the
   user's Ryzen 5 3600 / 16 GB machine. Do not force new concurrency machinery without measured benefit.
5. Output is two concise lines per check: start, then PASS/FAIL/TIMEOUT with duration. No noisy successful
   test output.
6. Failure console output is a short useful excerpt; complete output is overwritten at
   `artifacts/check-failure.log`. A successful run removes stale failure logs. Do not accumulate logs or
   clutter the root.
7. Every subprocess gets a sensible finite per-check timeout. E2E has a generous outer timeout because
   duration varies; retain per-test timeout behavior. No automatic E2E retry.
8. Preserve simple named targeting (`--python`, `--frontend`, `--e2e`, etc.). On failure, provide a
   practical native command for narrower reruns. Do not build a generalized argument-forwarding abstraction.
9. `--fix` remains explicit. AI policy changes so an AI may invoke `scripts/check.py --fix` after a
   read-only check identifies deterministic formatting/lint issues, must inspect the resulting diff, and
   must not use it for semantic repair.
10. The quick suite includes a TypeScript type check but excludes production, Storybook, and browser builds.
11. No dashboards, structured JSON/reporting frameworks, cross-group concurrency, historical timing
    databases, adaptive orchestration, or elaborate architecture.
12. Preserve complete coverage under `--full`, unless repository facts reveal a genuine conflict requiring
    escalation.

## Coordinator refinements (approved)

- The timeout override is one simple discoverable CLI option `--timeout-multiplier` (float, default 1.0)
  applied to per-step defaults — not an environment-only setting.
- README maintenance (for example the `scripts/README.md` check-suite row) is follow-up routed by the
  coordinator to `readme-updater` after structural behavior changes; it is not an implementation-stage edit.
- The Storybook/Vitest migration Plan is complete (moved to `docs/plans/done/`). Its resulting behavior —
  the Vitest `unit`/`storybook` projects, the bounded `test-storybook` wiring, and the Storybook-build
  Windows teardown special-case — is preserved.
- Full closeout is `.venv/Scripts/python.exe scripts/check.py --full` wrapped with an explicit finite
  command-level timeout and finite bash tool timeout; baseline/unrelated failures are reported, not absorbed.
- Quality validation is fresh and coordinator-routed after implementation.

## Excluded

Dependencies, product code, dashboards/JSON/history stores, cross-check concurrency, adaptive
orchestration, E2E config changes, done Plans, historical records, and README implementation edits.