# AI database schema document - AI can navigate the supported SQLite schema without system-table queries

> **Status:** done - independently validated and accepted

- **Read trigger:** Before changing the schema-document generator, its freshness integration, or the supported
  SQLite DDL assembly used by this document.
- **Upstream:** Approved coordinator assessment for the AI database schema case; [Documentation Router](../../README.md)

## Outcome

Maintain one deterministic, AI-readable schema document at `data/database/schema.txt`. The document describes the
repository-supported SQLite schema without runtime data, stays reproducible from the existing DDL owners, and cannot
become stale without the normal read-only quality path reporting clear regeneration guidance.

## Scope

- **Included:** Rework `data/database/dump_schema.py`; assemble the supported schema in an in-memory SQLite database
  from the existing DDL owners in dependency order; render deterministic Markdown-compatible text with do-not-edit and
  source metadata, navigation, tables, columns, nullability/defaults, primary-key order, constraints, foreign keys,
  indexes, triggers, and canonical SQL; add focused generator tests; add read-only freshness verification and explicit
  deterministic regeneration to `scripts/check.py`; link the document from `docs/README.md`; and generate the initial
  artifact.
- **Expected areas:** `data/database/dump_schema.py`, `data/database/schema.txt`, `tests/test_database_schema.py`,
  `scripts/check.py`, `scripts/tests/test_check.py`, and `docs/README.md`. The schema assembly must use
  `scripts/chess_com/fetch_games.py:create_schema`, `scripts/chess_com/_schema.py`,
  `scripts/opening_catalog/{schema.py,classification_schema.py,recurrence_schema.py}`,
  `backend/app/features/analysis/schema.py`, and `backend/app/features/evaluation/schema.py` without changing their
  schema contracts.
- **Preservation:** The ignored `data/database/chess_games.db` remains untouched; the unrelated untracked
  `docs/plans/active/storybook-quality-pipeline/storybook-quality-pipeline.md` and
  `docs/plans/active/s5-tracked-player-projection/s5-tracked-player-projection.md` remain unchanged; completed
  Plans, grilling records, and unrelated worktree content remain unchanged.
- **Excluded:** Runtime database writes or migrations; runtime data, row counts, timestamps, or system-table queries
  by AI consumers; new top-level scripts or dependencies; API/frontend behavior; `dev.ps1`; application CI; schema
  ownership changes; completed Plan or grilling edits; changes to the unrelated active Storybook or S5 Plans;
  commits; pushes; and unrelated repairs.

## Stages

1. **complete - Implement the canonical generator and deterministic focused proof.**
   - **Ordered actions:** Define the fixed in-memory DDL assembly order: base fetch schema, corpus schema, opening
     catalog and relationships, classification, recurrence, analysis, and evaluation. Render metadata from the
     resulting schema without reading the runtime database or including data-dependent values. Add the generated
     header, source references, stable navigation, structural details, and canonical SQL. Use a complete in-memory
     render before replacing the artifact, and preserve an explicit read/check operation for callers that must not
     mutate files.
   - **Focused proof:** `tests/test_database_schema.py` proves every approved schema namespace/object is represented,
     required key and relationship details are present, forbidden runtime data is absent, and two independent renders
     are byte-identical. The focused generator proof uses temporary/in-memory SQLite only.
   - **Breakpoint:** None while the existing DDL owners reproduce the supported schema without changing their
     contracts or touching the runtime database.
   - **Escalate if:** The complete supported schema cannot be assembled from the named owners, requires a new
     migration/ownership model, or differs from the approved schema without an approved contract change.

2. **complete - Integrate freshness verification and explicit check regeneration.**
   - **Ordered actions:** Add a read-only freshness verification step to `scripts/check.py` that compares the checked
     artifact with a fresh deterministic render and reports the exact `.venv\Scripts\python.exe scripts\check.py --fix`
     remediation for missing or stale output. Add deterministic schema regeneration to the existing `--fix` sequence
     before verification, keep default mode strictly non-mutating, and update the mode/help text as needed. Extend
     `scripts/tests/test_check.py` to prove default ordering, fix ordering, stale/missing failure behavior, and clear
     remediation without invoking a write in read-only mode.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_database_schema.py scripts/tests/test_check.py -q`;
     scoped Ruff and format checks for the changed Python files; and a subprocess or helper-level proof that the
     freshness check leaves the artifact and runtime database unchanged.
   - **Breakpoint:** None while `scripts/check.py` remains read-only by default and regeneration is confined to its
     explicit `--fix` path.
   - **Escalate if:** Default verification would need to mutate files, actionable remediation cannot be reported,
     or the shared check contract requires unrelated workflow changes.

3. **complete - Publish the artifact, router integration, closeout proof, and Quality readiness.**
   - **Ordered actions:** Generate the initial `data/database/schema.txt` without opening or modifying
     `data/database/chess_games.db`; add the canonical schema link to `docs/README.md`; review the generated document
     for AI navigation; run focused proof and the full explicit fix proof; then run the full default read-only check
     and review only the intended diff and status.
     Record the case as ready for fresh independent Quality validation rather than absorbing unrelated failures.
   - **Focused proof:** `.venv\Scripts\python.exe scripts\check.py --fix` (explicitly authorized for deterministic
     regeneration), `.venv\Scripts\python.exe scripts\check.py` (read-only closeout), `git diff --check`, final
     `git status --short`, scoped diff review, and the focused generator/check tests. Confirm explicit regeneration is
     source-only and produces the same bytes as the generator tests.
   - **Breakpoint:** Fresh independent Quality validation is required after implementation because the shared check
     behavior and generated schema contract change. No runtime database authorization is part of this Plan.
   - **Escalate if:** Closeout needs runtime database access, a new dependency or migration path, a default-check
     mutation, a change to acceptance, or repairs outside this Plan's paths.

Stages are sequential; no stage runs in parallel. The coordinator may split an oversized stage without changing the
approved outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - changed `data/database/dump_schema.py` and `tests/test_database_schema.py`; focused
  generator proof: `.venv\Scripts\python.exe -m pytest tests/test_database_schema.py -q` (5 passed), Ruff check and
  format check passed, two independent 84,569-byte renders were identical with SHA-256
  `1afe4ad18a6e9a1f525f8596c2d57ede7b487bfb32a6c8d894442151fd424e`, and coverage was 46 tables, 13 indexes, and
  4 triggers; the runtime database was untouched.
- **Stage 2:** complete - `.venv\Scripts\python.exe -m pytest tests/test_database_schema.py
  scripts/tests/test_check.py -q` passed (10 tests); scoped Ruff and format checks passed; tests prove read-only
  freshness, actionable stale/missing remediation, explicit fix ordering, deterministic regeneration, and no
  runtime-database mutation; breakpoint: none while the check contract remains intact.
- **Stage 3:** complete and independently accepted - the artifact is 86,319
  raw bytes with SHA-256 `f506fa198fa2f94385611953958a1de69414e0d2a3b97454d48a6c55c56890be`; fresh normalized renders
  were identical at 84,569 bytes with SHA-256 `1afe4ad18a6e9a1f525f8596c2d57ede7b487bfb32a6c8d894442151fd424e`,
  and `schema_is_current=True`. The document covers 46 tables, 13 indexes, and 4 triggers; the router link exists,
  setup.ps1 has no schema references, focused proof is 10 passed, and the runtime database remained at
  5,305,114,624 bytes with mtime_ns `1787430725035096700`. The required default check passed schema freshness,
  workflow, Ruff, Python/workflow tests, ESLint, source-size, and Storybook interaction checks, but exited with
  unrelated concurrent frontend/Storybook failures: 2 frontend test failures, one board-adapter Prettier warning,
  frontend build type errors in `AnalysisPanel.stories.tsx` and `ViewerWorkspace.stories.tsx`, a Storybook-build
  nonzero/libuv teardown failure, and 5 end-to-end failures in board-adapter/viewer Storybook and live-position
  coverage; none were repaired. Fresh Quality validation passed the schema outcome and independently bounded the
  remaining full-check failures to unrelated concurrent frontend/Storybook work.
- **Decision:** `data/database/schema.txt` remains the single generated artifact; the ignored runtime database is not
  the source of truth and is never modified by this case.
- **Decision:** The existing DDL owners are assembled in memory in dependency order; metadata inspection is a
  generation-time implementation detail, not an AI-use-time requirement.
- **Decision:** Default `scripts/check.py` remains read-only. Its explicit `--fix` path is the approved mutation path
  for deterministic regeneration.
- **Decision:** The user rejected installation bootstrap as an integration point because it is not run regularly; no
  bootstrap, scheduler, hook, dependency, CI, or dev-launcher integration is part of this Plan.
- **Decision:** Fresh independent Quality validation accepted the artifact and read-only integration. Unrelated
  concurrent frontend/Storybook failures remain outside scope and were not repaired or attributed to this case.

## Proof

- `.venv\Scripts\python.exe -m pytest tests/test_database_schema.py scripts/tests/test_check.py -q`.
- Latest Stage 2 run: 10 passed; scoped `ruff check` and `ruff format --check` passed for the four changed Python
  paths, and the helper-level proof preserved both the artifact and runtime-database sentinel.
- Two independent generator renders compare byte-for-byte; focused tests cover complete object/relationship details,
  missing/stale artifact failures, remediation text, and read-only behavior.
- Scoped `ruff check` and `ruff format --check` for changed Python files, plus `git diff --check`.
- `.venv\Scripts\python.exe scripts/check.py --fix` is the explicitly authorized regeneration proof; default
  checks remain the read-only freshness detector and report that exact remediation for missing or stale output.
- `.venv\Scripts\python.exe scripts/check.py` is the required full read-only closeout proof.
- Review `git status --short` and the scoped diff to prove only approved paths changed and the Storybook Plan remains
  untouched.
- Stage 3 closeout: `.venv\Scripts\python.exe scripts\check.py` confirmed schema freshness and the owned focused
  checks remain green; `git diff --check` passed. The full-check failures are bounded to concurrent frontend/
  Storybook work and are reported without repair or attribution to this schema case.
- Fresh independent Quality validation passed: focused pytest reported 10 passed; generator freshness, two-render
  byte stability, 46-table/13-index/4-trigger coverage, scoped Ruff and formatting, and `git diff --check` passed.
  Quality confirmed the runtime database was unchanged and classified the remaining full-check failures as unrelated
  concurrent frontend/Storybook work.

## Acceptance

The generated document covers the complete repository-supported schema, is byte-stable and discoverable from
`docs/README.md`, and gives an AI tables, columns, key order, constraints, foreign keys, indexes, triggers, and
canonical SQL without querying SQLite system tables at use time. Default checks never mutate files and fail on missing
or stale output with clear remediation. `scripts/check.py --fix` regenerates the artifact without modifying the
ignored runtime database. Focused proof, schema-owned portions of full read-only closeout, scoped diff review, and
fresh independent Quality validation pass; unrelated concurrent frontend/Storybook failures are recorded without
being absorbed into this case.

## Escalation boundaries

- The runtime database must become the document source of truth, or any operation must write, migrate, lock, repair,
  or otherwise modify `data/database/chess_games.db`.
- Existing DDL owners cannot reproduce the complete supported schema, or a new schema owner, migration framework,
  dependency, or data contract is required.
- Default checks would need to regenerate or mutate files, or the existing `--fix` contract cannot safely own the
  deterministic write.
- The document format, artifact location, schema ownership, acceptance, or AI-consumer behavior needs a new material
  decision beyond the approved scope.
- Work would touch `dev.ps1`, application CI, API/frontend behavior, completed Plans, grilling records, the unrelated
  Storybook Plan, `Scratch/`, commits, pushes, or unrelated worktree changes.
- Full closeout would require suppressing unrelated failures, using destructive operations, or skipping fresh
  independent Quality validation.

## Visible result

> `data/database/schema.txt` is a deterministic, linked, AI-readable description of the complete supported SQLite
> schema; normal checks detect staleness without writing, while the explicit fix path regenerates it without touching
> the runtime database.
