# Code-review inventory

This is an implementation-focused review of the repository as inspected on
2026-09-19. It deliberately excludes `experiments/` and does not discuss visual
or product design. Findings are candidates for change, not claims that a bug is
already reproduced. Fix the P0 and P1 items before adding more features in the
same areas.

## What was inspected

- FastAPI routes, dependencies, cache, and API contract generation.
- The `src/chess_move_trainer/database/` package, SQLite schema, opening lookup,
  Stockfish worker boundaries, and Graphify catalogue tooling.
- React state hooks, generated-client boundary, test configuration, Docker, and
  local-service scripts.
- Existing Graphify reports, which identify the `positions`/`openings` import
  cycle and high-fan-out schema and position-identity APIs.

The review does **not** change or inspect `experiments/`. Existing worktree
changes are treated as owned by another agent; this review records risks rather
than rewriting those changes.

## Priority and working rule

| Priority | Meaning |
| --- | --- |
| P0 | Can violate a documented runtime rule or break correctness when ordinary configuration changes. Address before relying on the affected path. |
| P1 | Likely reliability, security, operational, or maintenance failure as the data or team grows. Schedule next. |
| P2 | Important structural debt or a missing safety net. Address while working in that subsystem. |

Start with the P0 conditional-hook issue in [frontend.md](frontend.md) and the
P0 persistent-service violation in [automation.md](automation.md). Then choose
one bounded slice from [backend.md](backend.md) or [core-data.md](core-data.md),
add a regression test first, and preserve the current public API contract.

## Tool policy candidates

The repository already has pytest, Vitest, Playwright, Ruff, ESLint, Prettier,
and Graphify. The following tools would close specific review gaps; they should
be trialled locally and adopted only if their results are actionable.

| Need | Candidate tools | Expected use |
| --- | --- | --- |
| Dependency and image vulnerabilities | `pip-audit`, `npm audit`, `osv-scanner`, Docker Scout or Trivy | Scan lockfiles and built images; triage reachable production findings. |
| Python types and unsafe patterns | Pyright, Ruff rule expansion, Bandit, Semgrep | Check database boundaries, broad exception handling, subprocess use, and path handling. |
| TypeScript/React correctness | `tsc -b`, ESLint React Hooks rules without suppressions, `eslint-plugin-security` or Semgrep | Catch conditional hooks, contract drift, and unsafe browser/API code. |
| API and schema regression | Schemathesis, `openapi-diff`, Dredd-compatible contract testing | Exercise the served OpenAPI document and fail on breaking contract changes. |
| SQLite and performance evidence | `EXPLAIN QUERY PLAN`, Hypothesis, Locust/k6, `py-spy` | Test query plans and concurrency against a representative database rather than fixtures alone. |
| Runtime diagnosis | OpenTelemetry plus structured JSON logging; Sentry if hosted error collection is acceptable | Correlate request, cache, database, and worker failures without exposing FEN/PGN data unnecessarily. |

These are review recommendations, not an instruction to add CI. `AGENTS.md`
explicitly says all checks are local and no application CI should be added.

## Documents

- [Backend review](backend.md) — route, cache, error, and contract concerns.
- [Core data review](core-data.md) — SQLite, domain package, engine, and
  Graphify concerns.
- [Frontend review](frontend.md) — hook correctness, generated API boundary,
  and state-management concerns.
- [Automation and quality review](automation.md) — Docker, PowerShell, tests,
  dependency supply chain, and review tooling.
