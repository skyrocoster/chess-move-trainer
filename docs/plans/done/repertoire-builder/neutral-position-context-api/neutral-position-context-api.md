# Neutral position-context API - safe recurrence context for one FEN

> **Status:** accepted - A1 is complete; focused proof and independent Quality validation passed.

- **Read trigger:** Read before implementing the A1 neutral position-context endpoint, its backend adapter,
  router registration, or focused API tests.
- **Upstream:** [Repertoire Builder master plan](../../../master-plans/repertoire-builder/repertoire-builder.md);
  [accepted S4 authoritative recurrence Plan](../../../done/s4-authoritative-recurrence/s4-authoritative-recurrence.md);
  [accepted preferred-move API Plan](../../../done/preferred-move-api/preferred-move-api.md)

## Outcome

Add a read-only FEN-based backend endpoint that reports whether an exact position exists in the accepted corpus and
returns distinct-game recurrence for Skyrocoster's stable game-color scopes, White and Black. The endpoint gives later
Viewer and Repertoire work neutral context without changing recurrence facts, preferred moves, or storage.

## Scope

- **Included:** Strict six-field FEN HTTP validation mapped to the established four-field position identity; a
  read-only adapter over accepted S4 recurrence facts/projections; overall corpus existence; distinct-game White and
  Black counts; safe invalid-input and unavailable/incompatible-storage errors; and router registration.
- **Expected areas:** `backend/app/features/position_context/`, `backend/app/main.py`, and
  `backend/tests/features/position_context/`.
- **Excluded:** Preferred-move changes or mutations, side-to-move counts, S5 or schema changes, recurrence edits,
  frontend work, speculative APIs or fields, new dependencies, runtime database writes, and changes to accepted
  S4 or preferred-move contracts.

## Stages

1. **done - Implement the bounded read-only endpoint.**
   - **Ordered actions:** Define the request, response, and safe-error contracts for only the approved FEN,
     overall-existence, and White/Black distinct-game result; validate an unmodified full FEN at the HTTP boundary;
     map it to the exact four-field identity; read accepted S4 projection data through a non-initializing,
     read-only adapter; preserve `color_scope` as Skyrocoster's stable game color; distinguish zero personal-color
     recurrence from absent overall corpus existence; map missing or incompatible recurrence storage safely; and
     register the router without touching existing recurrence or preferred-move code.
   - **Focused proof:** Scoped import/route-registration smoke plus Ruff and format checks for the new feature and
     `backend/app/main.py`; the adapter must not create schema, open a write connection, or write the runtime DB.
   - **Breakpoint:** None expected. Escalate if the accepted S4 state/projection cannot be read without selecting a
     new manifest, denominator, identity, ownership rule, schema policy, or API field.
2. **done - Prove isolation and close the repository change.**
   - **Ordered actions:** Add isolated temporary SQLite API fixtures covering valid and invalid full FEN, overall
     existence, White/Black distinct-game counts, zero personal-color counts, absent overall positions, and
     unavailable/incompatible storage. Prove that requests do not create schema, mutate any database, alter
     recurrence facts, or affect the preferred-move API; then run focused validation, size checks, diff checks, and
     the full read-only repository closeout.
   - **Focused proof:** The focused pytest, scoped Ruff/format/size checks, and `git diff --check` listed below.
   - **Breakpoint:** None expected. Report unrelated baseline failures rather than repairing or absorbing them.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
approved outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** done - endpoint, adapter, contracts, and registration are implemented in the approved areas; breakpoint:
  none.
- **Stage 2:** done - isolated API proof and repository closeout passed; breakpoint: none.
- **Plan:** accepted/done - independent Quality validation passed with no semantic or scope discrepancy. No next
  focused Plan was created or started.
- **Settled decisions (accepted):** S4 recurrence projections are authoritative; position identity remains the exact
  four-field key; `color_scope` means Skyrocoster's stable game color; counts are distinct games; overall existence is
  separate from a zero White or Black count; the request path is read-only and non-initializing; tests use temporary
  databases. Quality confirmed the exact four-field identity, stable White/Black game-color counts, zero-vs-absent
  distinction, safe 422/503 errors, and no writes, schema, or sidecars.

## Accepted proof

All commands ran from the repository root in Git Bash. Each command had a finite command-level timeout; the
parenthetical value is the finite `bash` tool timeout.

- `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/position_context -q`
  (bash tool timeout: `150000` ms) - **7 passed**.
- `timeout 60s .venv/Scripts/python.exe -m ruff check backend/app/features/position_context backend/app/main.py backend/tests/features/position_context`
  (bash tool timeout: `90000` ms) - **passed**.
- `timeout 60s .venv/Scripts/python.exe -m ruff format --check backend/app/features/position_context backend/app/main.py backend/tests/features/position_context`
  (bash tool timeout: `90000` ms) - **passed**.
- `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`
  (bash tool timeout: `90000` ms) - **passed**.
- `timeout 30s git diff --check` (bash tool timeout: `60000` ms) - **passed**.
- Full read-only closeout: `timeout 180s .venv/Scripts/python.exe scripts/check.py`
  (bash tool timeout: `240000` ms), without `--fix` - **all 11 steps passed**.
- Independent Quality validation - **PASS**: 7 tests, Ruff/format/size checks, and semantic/scope audit passed.

## Escalation boundaries

- Any new denominator, identity, ownership model, schema creation or migration, recurrence mutation, personal
  projection, dependency, runtime write, speculative endpoint or response field, or changed API policy.
- Any alteration to accepted S4 recurrence facts/projections, `color_scope` semantics, exact four-field identity,
  preferred-move behavior, safe unavailable-storage handling, or the approved distinction between zero personal scope
  and absent overall corpus existence.
- Any need to edit frontend, recurrence scripts/schema, the generated database schema, historical records, unrelated
  worktree content, commit, push, or use `--fix`.

## Visible result

> **Accepted A1 result:** A client can request one full FEN and receive safe neutral corpus existence plus White/Black
> distinct-game context without creating schema or changing stored data. V1 is next, but has not been created or started.
