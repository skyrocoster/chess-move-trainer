# Preferred-move storage - One lean, directly queryable capability over existing exact positions

> **Status:** done - Stages 1 through 3 accepted; runtime backup retained

- **Read trigger:** Read before implementing preferred-move storage, its Python access layer, line saving, or the
  authorized runtime database action.
- **Upstream:** [Preferred-move storage decisions](../../../grilling-docs/preferred-move-storage-decisions.md);
  [canonical Caro-Kann historical synthesis](../../../grilling-docs/caro-kann-next-move-experiment.md);
  [AI-readable SQLite schema](../../../data/database/schema.txt);
  [accepted MP-06 corpus Plan](../../done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md);
  [accepted S4 recurrence Plan](../../done/s4-authoritative-recurrence/s4-authoritative-recurrence.md);
  [S5 projection retrospective](../../../grilling-docs/ABANDONED/s5-tracked-player-projection-retrospective.md)

## Outcome

The accepted implementation provides one lean preferred-move capability for a stable player UUID and existing exact
four-field game-derived positions. It will preserve two append-only histories, derive current/effective/as-known and
date-range state directly, compare games at their end time, and prove the accepted Caro-Kann line before a separately
approved runtime database update. Writing this Plan provides no implementation authority beyond later separately
approved stage execution.

## Scope

- **Included:** Existing `position_state` ownership; one preferred move per stable player UUID and exact position,
  shared across routes/transpositions; independent requirement active/inactive and preferred move set/remove histories;
  user-selected effective UTC time plus database-recorded time; direct current/effective/as-known/date-range derivation;
  legal canonical UCI plus validated SAN snapshots; game-end-time comparison; unchanged-write no-ops; minimal tested
  Python access; legal line replay; atomic own-color decision saving; the accepted Caro-Kann line; and the explicit,
  human-approved runtime copy/apply/read-back/restore procedure. Storage and database runs remain clear, lean, and
  simplistic because prior copied-projection failures exposed the cost of operational complexity.
- **Expected areas:** `scripts/opening_catalog/*preferred_move*.py`, bounded exports in
  `scripts/opening_catalog/__init__.py`, `tests/test_opening_preferred_move.py`, the existing supported schema
  owners and generated `data/database/schema.txt`, and the authorized runtime artifact
  `data/database/chess_games.db`. The two linked documentation records are
  `docs/grilling-docs/preferred-move-storage-decisions.md` and this Plan.
- **Excluded:** API, frontend, training, engine, population, authentication, new dependencies, contract expansion,
  automatic requirement selection, thresholds, formulas, coverage rules, ranking, recommendations, route-specific
  preferences, unobserved-position insertion, line tables, current projections, caches, copied projections, rebuild
  or publication frameworks, source/reason fields, hashes, integrity scans, manifests, run records, enterprise backup
  machinery, destructive replacement, partial writes, `Scratch/`, historical edits, unrelated changes, commits, and
  pushes.

## Stages

1. **complete - lean append-only storage, minimal Python access, and direct query proof.**
   - **Ordered actions:** Confirm the existing stable UUID and four-field `position_state` ownership boundaries.
     Add only the two narrow append-only histories: requirement active/inactive and preferred move set/remove. Keep
     ownership, action, move as applicable, user-selected effective UTC time, and database-recorded time; add no source
     or reason fields. Validate and store canonical legal UCI with a SAN snapshot from the exact state. Derive present,
     effective-time, as-known-at-recorded-time, and exact-UTC date-range state directly from history. Resolve same
     effective times by later-recorded event; make unchanged repeat writes no-ops. Compare later games at `games.end_time`
     and return not judged unless the requirement was active and a preference existed then.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_preferred_move.py -q`; scoped Ruff
     check and format check; `.venv\Scripts\python.exe scripts/check_size.py --source-max 500 --test-max 700`;
     exact tests for backdating, future scheduling, corrected effective timelines, as-known history, tied effective
     times, no-op writes, all move/no-move periods, illegal moves, independent requirement/preference combinations,
     and game-end-time comparison.
   - **Breakpoint:** None while the approved identity, two-history, direct-derivation, and no-projection boundaries
     remain unchanged. Do not insert a position absent from existing game-derived `position_state`.

2. **complete - legal line replay/validation and atomic own-color saving.**
   - **Ordered actions:** Replay and validate `1.e4 c6 2.d4 d5 3.e5 c5` from the exact starting position using the
     existing chess validation boundary. Resolve only existing game-derived positions, identify Skyrocoster's three
     Black-to-move decisions, and atomically save active requirements plus preferred choices `c6`, `d5`, and `c5` at
     effective time `2024-09-03T06:00:00Z`. Preserve independent histories, reject illegal or unobserved positions,
     leave no partial writes on failure, and make a repeated unchanged save a no-op. Persist no line table.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_preferred_move.py -q`, including the
     exact acceptance line, Black-only ownership, canonical UCI/SAN snapshots, active requirements, atomic failure
     rollback, illegal-line rejection, unobserved-position rejection, and unchanged repeat-save proof; scoped Ruff,
     format, size, and `git diff --check` checks.
   - **Breakpoint:** None; runtime `data/database/chess_games.db` is not touched by this stage. Escalate rather than
     adding a line table, alternate line ownership, or a new replay contract.

3. **complete - human-approved runtime application and read-back.**
   - **Ordered actions:** Obtain explicit human approval immediately before the data modification. Make a full file
     copy of `data/database/chess_games.db`, confirm matching file size only, apply the small schema and accepted line
     directly to the runtime database, read back the three Black choices and active requirements at
     `2024-09-03T06:00:00Z`, and restore the copy on failure. Ordinary tests may use a copied database. Do not add
     hashes, integrity scans, manifests, publication/run records, or enterprise backup machinery.
   - **Focused proof:** Run the focused preferred-move tests against a copied database; record the file-size-only
     backup match; inspect the runtime read-back for the exact three positions, choices, active requirements, effective
     time, direct history, and no-op rerun; and prove that a copied-database failure restores the copy without partial
     accepted state. Runtime proof must not substitute a new integrity or backup framework.
   - **Breakpoint:** **Mandatory explicit human approval immediately before copying and modifying the runtime
     database.** The Plan and document-writing phase do not authorize this write. Stop and escalate on any uncertain
     copy, restore, ownership, partial-write, or read-back condition.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing the
approved outcome or requiring a new human decision.

## Progress and decisions

- **[x] Stage 1:** complete - proof: focused preferred-move tests (5 passed), scoped Ruff check/format,
  source/test size, schema freshness, and diff checks; breakpoint: none.
- **[x] Stage 2:** complete - proof: 12 focused tests plus independent exact-line, legality, atomic rollback,
  ownership, no-op, scope, and runtime-untouched validation; breakpoint: runtime database remains untouched.
- **[x] Stage 3:** complete - proof: focused access test, matching file size, direct runtime read-back, and
  restore-on-failure procedure; breakpoint: immediate human approval was received and satisfied.
- **Decision:** Requirements and preferences remain independent; active plus move is satisfied, active plus no move is
  choice needed, and inactive plus move is stored out-of-scope.
- **Decision:** Stage 3 applied only Skyrocoster's stable UUID `0101b08a-ce8b-11ee-b2fd-e90263e5548c`, Black's three
  exact existing positions, and the accepted line at effective UTC `2024-09-03T06:00:00Z`; the backup remains
  retained at `data/database/chess_games.db.backup.preferred-move-stage3-20260824`.
- **Decision:** This Plan records direction and proof boundaries only. It does not authorize implementation, commits,
  pushes, or runtime writes until the coordinator separately approves the relevant stage.

## Proof

- `.venv\Scripts\python.exe -m pytest tests/test_opening_preferred_move.py -q` for all focused storage, query, line,
  atomicity, and acceptance behavior.
- Scoped `.venv\Scripts\python.exe -m ruff check ...` and
  `.venv\Scripts\python.exe -m ruff format --check ...` for changed Python paths.
- `.venv\Scripts\python.exe scripts/check_size.py --source-max 500 --test-max 700`.
- `git diff --check`, scoped status/diff review, and generated-schema freshness review when the supported schema
  changes.
- Stage 1 focused proof on 2026-08-24: `.venv\Scripts\python.exe -m pytest tests/test_opening_preferred_move.py -q`
  (5 passed); scoped Ruff check and format check passed; size check passed; generated schema is current; `git diff
  --check` passed. The runtime database was not modified.
- Stage 2 focused and independent proof on 2026-08-24: `.venv\Scripts\python.exe -m pytest
  tests/test_opening_preferred_move.py -q` (12 passed); scoped Ruff check and format check, size, schema freshness,
  database-schema tests, and `git diff --check` passed. Temporary-database probes confirmed the exact three Black
  decisions, shared effective time, no-op replay, rejection boundaries, and atomic rollback. The runtime database
  remained untouched.
- Stage 3 runtime proof on 2026-08-24 after immediate approval: the complete ignored backup
  `data/database/chess_games.db.backup.preferred-move-stage3-20260824` was created without collision; source and copy
  sizes matched at `5,413,478,400` bytes. Runtime read-back resolved Skyrocoster to
  `0101b08a-ce8b-11ee-b2fd-e90263e5548c` and exactly these existing Black positions/moves: after `1.e4` (`...e3`) ->
  `c7c6`/`c6`, after `1.e4 c6 2.d4` (`...d3`) -> `d7d5`/`d5`, and after `1.e4 c6 2.d4 d5 3.e5` (`-`) ->
  `c6c5`/`c5`. Direct requirement histories were `[inactive, active]`, preferred histories were `[no move, move]`,
  combined histories were `[not_required, satisfied]`, and all three current states were `satisfied`; all six events
  stored effective UTC `2024-09-03T06:00:00.000000Z`, the canonical representation of the exact requested instant.
  Event counts were exactly three requirement and three preferred-move events, with no extra or partial rows. The
  unchanged line operation rerun returned `changed=False`, all six item changes false, and counts remained `(3, 3)`.
  Runtime proof command succeeded; focused `.venv\Scripts\python.exe -m pytest tests/test_opening_preferred_move.py -q`
  passed (`12 passed in 0.94s`). The backup was retained; no restore was needed. Independent Quality reproduced the
  runtime read-back and no-op proof, confirmed the backup and pre-write database sizes matched, and ran the full
  read-only `.venv\Scripts\python.exe scripts/check.py`; preferred-move checks passed, while unrelated existing
  experiment formatting, frontend Storybook typing, and viewer end-to-end failures were reported without repair.

## Acceptance

The implementation is acceptable only when a human can inspect direct append-only requirement and preference histories,
derive current/effective/as-known/date-range state without projections, confirm game-end-time judgment semantics, and
replay the exact line `1.e4 c6 2.d4 d5 3.e5 c5` to save Skyrocoster's Black choices `c6`, `d5`, and `c5` with active
requirements at exactly `2024-09-03T06:00:00Z`. Repeated unchanged saves are no-ops, illegal or unobserved positions
are rejected, failures leave no partial writes, and runtime modification occurs only after the explicit Stage 3 human
approval and supports copy restoration on failure.

## Escalation boundaries

- Any change from one preferred move per stable player UUID plus existing exact four-field position, shared across
  routes/transpositions.
- Any third history, current projection, cache, copied projection, rebuild/publication framework, source/reason field,
  run record, or automatic coverage/selection/threshold/formula rule.
- Any insertion of an unobserved position, line table, route-specific preference, API, UI, training surface, engine,
  population source, dependency, or contract expansion.
- Any change to canonical legal UCI plus validated SAN, effective-time/recorded-time ordering, as-known history,
  later-recorded tie resolution, future/backdated behavior, no-op semantics, or game-end-time judgment.
- Any change to the acceptance line, Skyrocoster Black ownership, the three active requirements, or exact effective
  time `2024-09-03T06:00:00Z`.
- Any runtime operation without explicit immediate human approval, matching-file-size-only copy confirmation, direct
  schema/line application, read-back, or restore-on-failure; any request for hashes, integrity scans, manifests,
  publication/run records, or enterprise backup machinery.
- Any change to accepted S1-S4 ownership, destructive replacement, partial writes, historical records, unrelated
  worktree content, commits, or pushes.

## Visible result

> A human can inspect one lean direct-history preferred-move capability, replay the accepted Caro-Kann line with the
> three Black choices and active requirements at `2024-09-03T06:00:00Z`, and approve or reject the later runtime update
> without any user-facing surface or copied projection framework.
