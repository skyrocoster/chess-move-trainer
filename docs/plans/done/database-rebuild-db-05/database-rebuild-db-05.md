# DB-05 preferred-move periods - safely store and amend the current dated schedule

> **Status:** done - all four stages accepted with 71 focused tests passing across retained proof

- **Read trigger:** Read before any DB-05 implementation or focused proof, and resume from the first pending stage.
- **Upstream:** `docs/master-plans/database-rebuild/database-rebuild.md` DB-05 envelope and sequencing;
  coordinator-approved `docs/grilling-docs/database-rebuild-db-05.md`; DB-05 authority in
  `docs/grilling-docs/database-rebuild-direction.md:593-649,807-814` and
  `docs/grilling-docs/database-rebuild-schema.md:657-712,811-822`.

## Outcome

Provide a package-owned preferred-move service and supported thin CLI that safely stores, lists, resolves, and amends
the normalized current schedule for a canonical chess position over half-open UTC calendar-date ranges. A date resolves
to a preferred legal move, explicit no preference, or unconfigured; standalone positions and concurrent supported
writers remain safe without changing schema v1.

## Scope

- **Included:** `chess_move_trainer.database.preferred_moves`; pure strict-date and range-overlay semantics; four-field
  FEN adaptation through DB-02 canonicalization; legal UCI validation; read-only list/resolve behavior; transactional
  set/unset persistence; standalone canonical-position creation on writes; `preferred-moves list`, `resolve`, `set`, and
  `unset`; stable human and JSON output; focused service, concurrency, CLI, and source-boundary proof.
- **Expected areas:** `src/chess_move_trainer/database/preferred_moves/**`,
  `src/chess_move_trainer/database/cli.py`, `tests/database/preferred_moves/**`,
  `tests/database/test_cli.py`, `tests/database/test_package_boundary.py`, and
  `tests/database/test_source_boundary.py`.
- **Excluded:** any edit to `schema_v1.sql`, `schema.py`, generated schema references, or `PRAGMA user_version`; migration,
  new tables/columns/indexes/triggers/state; provenance or history; setup inference or application (SETUP-01);
  historical-game evaluation; games/openings dependencies; time-control scope; production API/backend/frontend/UI;
  legacy implementation reuse; cutover, deletion, Quality validation, maintenance checks, commits, or pushes.

## Stages

1. **accepted - Define normalized range and resolution semantics as pure package behavior.**
   1. Add the `chess_move_trainer.database.preferred_moves` package with ordinary immutable values for the three
      resolution states and normalized periods, exposing semantic operations without exposing SQLAlchemy or sqlite3
      handles. Keep internal module/class names implementation-local where the handoff does not settle them.
   2. Accept only literal `YYYY-MM-DD` dates and explicit starts; reject timestamps, relative/system-clock values,
      impossible dates, and finite ends not strictly after their starts. Preserve NULL/omitted end as indefinite.
   3. Implement deterministic set and unset overlays over ordered half-open periods: split or shorten intersections,
      preserve both outside fragments exactly, remove configuration for unset, merge adjacent equal move or explicit
      no-preference states, reject overlap/invalid normalized output, and keep a returned earlier move as a separate
      nonadjacent period.
   4. Implement date resolution over normalized periods, including empty schedules and indefinite final periods, with
      an unambiguous distinction among preferred move, explicit no preference, and unconfigured.
   5. Add focused pure tests at `tests/database/preferred_moves/test_range_semantics.py` covering insertion, overlay,
      split, shortening, extension, replacement, no-op unset, gap creation, adjacency merging, return to an earlier
      move, all three resolution states, strict boundaries, and exact preservation outside amendments.
   - **Focused proof:** `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_range_semantics.py -q`
     (command timeout `60s`; Bash tool timeout `90000ms`).
   - **Acceptance:** The pure service produces one deterministic, pairwise-valid normalized schedule for every settled
     amendment case and resolves boundary dates according to half-open semantics.
   - **Exclusions:** No database connection, schema edit, position creation, CLI registration, inference, or UI behavior.
   - **Escalate if:** Overlay behavior needs another stored state, meaningful retained edit boundaries, timestamp
     precision, or a product rule not settled by the handoff.
   - **Breakpoint:** none.

2. **accepted - Persist reads and amendments atomically through canonical positions and SQLite writer locking.**
   1. Add repository/service contracts under `preferred_moves` that open only an explicit existing database through the
      package connection boundary, enforce exact schema-v1 compatibility, and retain the established finite lock
      timeout. Translate malformed/incompatible/storage/lock failures into bounded preferred-move errors without
      hiding interruption.
   2. At the preferred-move boundary, require exactly four FEN fields. Adapt those fields through the existing DB-02
      canonical validation and legal-only en-passant normalization without changing canonical identity or accepting
      halfmove/fullmove counters. Reconstruct a legal board from the canonical source position for move validation.
   3. Make list and resolve read-only: canonicalize the supplied position, look it up by all four identity fields, return
      empty/unconfigured when absent, and never create a position or preference row.
   4. For every set/unset, acquire `BEGIN IMMEDIATE` before reading the position schedule. On the same configured
      connection, resolve or create the canonical position using the established opaque DB-02 unit-of-work composition,
      validate any non-NULL UCI move as legal from that position, read the locked schedule, apply Stage 1 normalization,
      replace the position's schedule, and verify ordered rows pairwise before commit.
   5. Ensure every failure or `KeyboardInterrupt` rolls back position creation and period replacement together. Never
      use a pre-lock schedule. Supported concurrent writers must serialize: after the first writer commits, the second
      lock holder reads that fresh committed schedule before applying its overlay. Nonoverlapping effects from both
      writers survive; on shared dates the later serialized overlay governs the intersection while preserving the first
      amendment outside it. No stale-read lost update, overlap, or indefinite period before another row may commit.
   6. Add focused persistence tests at `tests/database/preferred_moves/test_repository.py` and
      `tests/database/preferred_moves/test_concurrency.py` for schema compatibility, canonical reuse, legal-only
      en-passant matching, unknown reads, same-transaction standalone creation, legal/illegal UCI, every amendment
      shape, normalized reload, injected failure/interruption rollback, finite lock behavior, and two competing writers
      proving fresh post-lock reads, preservation outside the later overlay, later-writer control of the intersection,
      and absence of overlapping committed rows.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_repository.py tests/database/preferred_moves/test_concurrency.py -q`
     (command timeout `120s`; Bash tool timeout `150000ms`).
   - **Acceptance:** All supported writes lock before reading and commit one legal, normalized, non-overlapping current
      schedule; reads never create; standalone position creation and schedule publication share one rollback boundary;
      concurrent proof demonstrates serializable overlays: both writers' nonoverlapping effects survive, the later
      overlay governs shared dates, the earlier overlay survives outside them, and no stale-read overwrite or overlap
      commits.
   - **Exclusions:** No direct-SQL policing, trigger, schema/version/reference change, broad DB-01 rerun, or broad DB-02
     rerun. Their accepted contracts remain valid because this stage consumes rather than changes them.
   - **Escalate if:** The package-owned connection and canonical-position composition cannot support `BEGIN IMMEDIATE`
     on one connection without changing their settled public meaning; arbitrary SQL must be policed; or correctness
     requires schema, identity, dependency, or lock-policy changes.
   - **Breakpoint:** none.

3. **accepted - Expose the exact noninteractive `preferred-moves` CLI surface as thin adapters.**
   1. Register one `preferred-moves` Typer group in `src/chess_move_trainer/database/cli.py` with exactly `list`,
      `resolve`, `set`, and `unset`; keep all validation, normalization, resolution, and persistence in importable
      preferred-move services.
   2. Implement the exact flags from the handoff: explicit `--database` and `--fen`; `resolve --date`; set/unset
      `--from` and optional `--until`; and set's exactly-one-of `--move`/`--no-preference`. Add `--json` to each command
      for stable machine output without adding implicit paths, dates, prompts, or stdin reads.
   3. Render list as normalized stored periods and resolve as exactly one settled state. Make successful default output
      clear and stable, and JSON deterministic with explicit state and NULL values where relevant. Treat empty list,
      unconfigured resolution, and no-op unset as successful.
   4. Map invalid invocation/date/four-field-FEN/range/move to exit `2`, incompatible schema to `3`, operational/storage/
      lock failure to `1`, interruption after complete rollback to `130`, and all success cases to `0`; emit errors only
      on stderr.
   5. Extend `tests/database/test_cli.py` using the established subprocess timeout and `CliRunner` conventions to prove
      group/command help, exact required and mutually exclusive flags, default/JSON output, no stdin dependence, all
      exit meanings, legal and no-preference writes, list/resolve/unset behavior, and interruption rollback.
   - **Focused proof:** `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q -k preferred_moves`
     (command timeout `90s`; Bash tool timeout `120000ms`).
   - **Acceptance:** All four supported commands are discoverable, noninteractive thin adapters with exact inputs,
     deterministic outputs, settled success/error channels, and exit statuses `0/1/2/3/130`.
   - **Exclusions:** No SETUP-01 proposal/apply command, API route, frontend, default date/path, extra command, or CLI
     business logic.
   - **Escalate if:** Typer cannot express the settled invocation or exit behavior without changing the command/flag
     contract, or output requires an unsettled product/API contract.
   - **Breakpoint:** none.

4. **accepted - Prove package ownership and the complete focused DB-05 boundary.**
   1. Export the intended importable preferred-move public contracts from its package `__init__` and add focused public
      import/API proof at `tests/database/preferred_moves/test_public_api.py` without promoting database handles or
      lower-level internals.
   2. Extend AST/text source-boundary checks so preferred moves may depend only on package database/position services;
      games, openings, backend, frontend, scripts, legacy modules, subprocess wrappers, and copied/delegated legacy
      implementation remain absent. Prove lower-level database and position packages do not import preferred moves and
      the CLI remains free of SQL/database-driver/chess business logic.
   3. Retain unaffected Stage 1-3 evidence. Run only the new public API test and DB-05-selected package/source-boundary
      cases; rerun the exact command for Stage 1, 2, or 3 only if Stage 4 edits actually invalidate that stage's evidence.
      Do not run a complete preferred-moves aggregate, schema/reference tests, or canonical-position suites because
      Stage 4 does not ordinarily invalidate those accepted results.
   4. Review the resulting behavior against every handoff acceptance item and confirm no schema/reference, SETUP-01,
      production application, or unrelated path entered the implementation scope.
   - **Focused proof:**
     - `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_public_api.py -q`
       (command timeout `60s`; Bash tool timeout `90000ms`).
     - `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q -k preferred_moves`
       (command timeout `90s`; Bash tool timeout `120000ms`).
     - `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q -k preferred_moves`
       (command timeout `90s`; Bash tool timeout `120000ms`; run only if Stage 4 changes invalidate Stage 3 evidence).
   - **Acceptance:** Focused proof covers all three states, all normalized amendment shapes, canonical and legal move
     behavior, rollback/concurrency, the exact CLI, and one-way dependency/source ownership with no excluded machinery.
   - **Exclusions:** No lint, formatting, broad type/build, source-size, aggregate/full suite, schema regeneration,
     Quality workflow, SETUP-01, application integration, commit, or push.
   - **Escalate if:** Final proof exposes a new product, schema, dependency, ownership, destructive, or acceptance
     decision, or a directly related failure cannot be repaired within DB-05 after one bounded attempt.
   - **Breakpoint:** Coordinator acceptance of the complete focused result and proof before selecting DB-06.

Stages were executed sequentially and never in parallel. Passing proof was retained unless a later edit affected its
command, inputs, behavior, configuration, dependency, or environment. All stages and the final coordinator breakpoint
were accepted; no transient handoff existed at closeout.

## Progress and decisions

- **Stage 1:** accepted on 2026-09-05 - `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_range_semantics.py -q` passed with 29 tests in 0.23 seconds (Bash tool timeout `90000ms`); breakpoint: none.
- **Stage 2:** accepted on 2026-09-05 - `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_repository.py tests/database/preferred_moves/test_concurrency.py -q` passed with 19 tests in 1.91 seconds (Bash tool timeout `150000ms`); Stage 1 proof remains retained; breakpoint: none.
- **Stage 3:** accepted on 2026-09-05 - `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q -k preferred_moves` passed with 16 selected tests and 38 deselected in 13.87 seconds (Bash tool timeout `120000ms`); Stages 1-2 proof remains retained; breakpoint: none.
- **Stage 4:** accepted on 2026-09-05 - `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/preferred_moves/test_public_api.py -q` passed with 3 tests in 0.25 seconds (Bash tool timeout `90000ms`), and `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q -k preferred_moves` passed with 4 selected tests and 10 deselected in 0.36 seconds (Bash tool timeout `120000ms`); Stages 1-3 proof remained retained; final coordinator breakpoint accepted before DB-06.
- **Decision:** The existing four-column table and `PRAGMA user_version = 1` remain unchanged; DB-05 performs no schema
  or generated-reference work.
- **Decision:** Stored rows are normalized current truth only: range amendments preserve outside dates and merge
  adjacent equal states; edit provenance and intentional duplicate boundaries are discarded.
- **Decision:** Public position input is exactly four-field FEN. Reads do not create positions; writes may create one in
  the same locked transaction. DB-02 canonical identity and legal-only en-passant meaning remain unchanged.
- **Decision:** Every supported write uses `BEGIN IMMEDIATE` before schedule reads and the established finite timeout;
  direct SQL bypass is unsupported and receives no trigger protection.
- **Decision:** Historical inference/setup belongs only to SETUP-01; time-control scope and application/UI integration
  remain future work.

## Proof

- Pure tests demonstrate strict calendar parsing, half-open boundaries, all overlay/unset transformations, adjacency
  merging, return to an earlier move, pairwise validity, and preferred/no-preference/unconfigured resolution.
- Persistence tests demonstrate exact-v1 compatibility, four-field canonical matching, legal-only en-passant handling,
  legal move enforcement, unknown read behavior, standalone creation, one-transaction publication, complete rollback,
  finite lock handling, and concurrent serializable overlays: fresh post-lock reads, preservation of nonintersecting
  effects, later-overlay precedence on shared dates, and no overlapping committed rows.
- CLI tests demonstrate exact help/options, noninteractive explicit inputs, human and stable JSON output, stderr errors,
  mutual exclusivity, and exit statuses `0/1/2/3/130`.
- Package/source tests demonstrate importability, one-way dependencies, a thin SQL-free CLI, no raw handle exposure,
  and no legacy import, wrapper, runtime delegation, copied implementation, or excluded package dependency.

## Escalation boundaries

- Any table, column, index, trigger, migration, schema-reference, or `PRAGMA user_version` change.
- Any fourth preference state, timestamp precision, time-control dimension, retained edit provenance/history, or
  direct-SQL enforcement requirement.
- Any dependence on games, openings, backend, frontend, scripts, legacy code, or inversion of the lower-layer ownership
  direction.
- Any setup inference/application, historical-game evaluation, API/UI behavior, cutover, old-database mutation, or
  destructive operation.
- Any change to the exact four-field public FEN input, canonical identity meaning, legal-move rule, CLI commands/flags,
  lock policy, exit meanings, or acceptance criteria.

## Visible result

> An operator can list, resolve, set, and unset a position's dated preferred move safely, with normalized periods and no overlapping result even when supported local writers compete.
