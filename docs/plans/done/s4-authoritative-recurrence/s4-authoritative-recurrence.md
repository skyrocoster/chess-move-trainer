# S4 - Authoritative recurrence facts and rebuildable aggregates - inspectable facts with deterministic projections

> **Status:** Done - Stages 1 through 5 complete and accepted; Plan archived.

- **Read trigger:** Read before any S4 recurrence schema, derivation, aggregate, importer, or authorized
  runtime database action.
- **Upstream:** [Opening Classification Database Preparation master plan](../../../master-plans/opening-classification-database-preparation.md);
  [accepted S1 Source Catalog Plan](../../done/s1-source-catalog/s1-source-catalog.md);
  [accepted S2 Opening Relationships Plan](../../done/s2-opening-relationships/s2-opening-relationships.md);
  [accepted S3 Neutral Classification Plan](../../done/s3-neutral-classification/s3-neutral-classification.md);
  [route and recurrence evidence](../../../grilling-docs/opening-training-and-repertoire-preparation.md)

## Outcome

Persist authoritative neutral recurrence and branch event facts for the accepted corpus, then publish additive,
deterministic global and opening-route projections that can be rebuilt from those events without loss, hidden
double-counting, formulas, thresholds, or frontier decisions. A human can inspect raw events and projections while
the accepted S1 catalog, S2 relationships, S3 classifications, and game-derived corpus remain unchanged.

## Scope

- **Included:** Accepted S3 classifications and corpus occurrences; exact four-field recurrence identity; natural
  game/ply and route-membership identities; global occurrence events; opening-route events retaining every accepted
  membership; parent-state/child-move branch events including terminal outcomes; distinct-game and raw-occurrence
  projections; route and membership-inclusive projections; overall and white/black projections; chronology and
  deterministic game sequence; source result and rating context; additive schema/version/run provenance; metadata
  change detection; atomic publication; unchanged reruns; rollback; temporary SQLite proof; authorized runtime
  publication and inspection; and independent closeout validation.
- **Expected areas:** `scripts/opening_catalog/recurrence_contract.py`,
  `scripts/opening_catalog/recurrence_schema.py`, `scripts/opening_catalog/recurrence.py`,
  `scripts/opening_catalog/recurrence_persistence.py`, bounded exports in
  `scripts/opening_catalog/__init__.py`, and `tests/test_opening_recurrence.py`. Read-only compatibility areas
  are `scripts/chess_com/{_schema.py,_replay.py,_persistence.py,_history.py,extract_corpus.py,fetch_games.py}`.
  The authorized runtime artifact is `data/database/chess_games.db`. The archived Plan is
  `docs/plans/done/s4-authoritative-recurrence/s4-authoritative-recurrence.md`.
- **Excluded:** Recurrence formulas, conditional-share formulas, thresholds, recency or rating weights, priority
  scores, adaptive-frontier decisions, automatic recommendations, training progression, tracked-player facts,
  usernames as durable identity, numeric IDs, SQLite `rowid`, source or corpus importer changes, changes to S1,
  S2, S3, or game-derived position ownership, API, frontend, engines, population evidence, new dependencies,
  taxonomy editing, destructive migration or replacement, writes under `Scratch/`, historical edits, commits,
  pushes, and unrelated worktree or database content.

## Stages

1. **complete - authoritative event contract and additive-schema gate (ORDERED).**
   - **Ordered actions:** Verify the accepted S1 manifest, S2 relationship state, S3 classification state, corpus
     schema, corpus identity, and accepted game boundary. Define natural event identities from `position_occurrence`
     and S3 route facts without `rowid`; retain the four-field position key, repeated occurrences, distinct-game
     support, route anchor and source-row membership, move order, terminal outcomes, color, chronology, raw results,
     and ratings. Define deterministic global, route, and parent-state/child-move projection keys while keeping
     raw occurrence and distinct-game counts separate. Define additive schema/version/run/state provenance and
     change detection for the accepted S3/corpus and game metadata inputs without storing player identities.
   - **Focused proof:** Temporary SQLite contract checks show that accepted S1/S2/S3/corpus rows and game metadata
     remain addressable, every natural event identity is stable, multiple memberships and repeated game positions
     remain distinct, and no requested projection requires a formula, threshold, or frontier policy.
   - **Breakpoint:** None; the settled S4 direction is sufficient for this contract gate. Escalate rather than
     selecting a new denominator, identity, ownership model, or data policy.

2. **complete - deterministic derivation and atomic temporary publication (ORDERED).**
   - **Ordered actions:** Implement the bounded S4 recurrence contract, additive schema, deterministic fact
     derivation, and persistence modules. Derive global events from accepted corpus occurrences and route events
     from accepted S3 routes; derive branch events from observed parent-state continuations, including terminal
     outcomes. Build all approved projections from the authoritative events, preserve source metadata as neutral
     context, publish to temporary SQLite databases atomically, and support deterministic independent builds,
     unchanged reruns, schema/version refusal, and failed-publication rollback.
   - **Focused proof:** The S4 temporary database tests prove complete event and projection counts for fixtures,
     exact rebuild/equality from events, stable run identity, independent deterministic output, no partial facts or
     state after derivation/storage failure, and unchanged S1/S2/S3/corpus signatures.
   - **Breakpoint:** None; runtime publication is not part of this stage.

3. **complete - focused recurrence, branch, and preservation regression proof (ORDERED).**
   - **Ordered actions:** Add bounded fixtures for repeated positions in one game, the same position across games,
     nested and multiple opening memberships, route-specific recurrence, different colors, chronology ties,
     results, ratings, parent/child moves, terminal outcomes, and repeated-game input. Compare raw events and every
     projection against deterministic expected facts; prove global counts do not silently become route or
     membership counts; and retain S1, S2, S3, and game-corpus preservation regressions.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_recurrence.py tests/test_opening_classification.py tests/test_opening_catalog.py tests/test_opening_relationships.py tests/test_extract_corpus.py -q`,
     scoped Ruff and format checks, source-size checks, deterministic-signature comparisons, and injected rollback
     assertions.
   - **Breakpoint:** None while the approved raw-fact, projection, and ownership boundaries remain unchanged.

4. **complete - authorized bounded runtime publication and inspection (ORDERED).**
   - **Ordered actions:** Capture a read-only online backup and pre-write signatures for integrity, foreign keys,
     schema versions, S1/S2/S3/corpus facts, game-derived rows, and unrelated tables; verify lock and active-writer
     safety; obtain coordinator/user authorization immediately before writing
     `data/database/chess_games.db`; publish the complete S4 facts and projections atomically; inspect
     representative global, route, branch, color, chronology, result, and rating facts; verify all upstream and
     unrelated signatures remain unchanged; and repeat the import to prove unchanged behavior. Keep failure and
     source-change injection on temporary or copied databases only.
   - **Focused proof:** Authorized runtime inspection proves SQLite integrity, an empty foreign-key check, complete
     S4 provenance and counts, exact event-to-projection rebuild equality, representative repeated/multi-membership
     and branch cases, identical pre/post upstream signatures, unchanged rerun output, and no SQLite sidecars.
   - **Breakpoint:** **Mandatory coordinator/user authorization immediately before the runtime database write.**
     Do not perform or claim runtime publication without that authorization.

5. **complete - independent validation, acceptance, closeout, and archival (ORDERED).**
   - **Ordered actions:** Obtain fresh independent Quality validation of event identity, global/route recurrence,
     branch facts, count separation, metadata context, deterministic rebuilds, atomicity, reruns, and preservation.
     Run the full read-only check without `--fix`; review the scoped diff, Plan shape, documentation, and unrelated
     worktree/database preservation; obtain explicit human acceptance; then archive the complete Plan directory
     under `docs/plans/done/s4-authoritative-recurrence/` only after acceptance.
   - **Focused proof:** `.venv\Scripts\python.exe scripts/check.py`; `git diff --check`; scoped Ruff, format, and
     size checks; documentation/template review; final `git status --short`; scoped diff review; and independent
     comparison of temporary and authorized runtime receipts.
   - **Breakpoint:** Fresh independent validation and explicit human acceptance are required before archival.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the approved outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - proof: temporary SQLite contract fixtures passed; accepted S1/S2/S3/corpus and game metadata remained addressable; natural identities, repeated occurrences, multiple memberships, branch outcomes, additive schema, version refusal, provenance fields, and raw/distinct count separation were verified; no formulas, thresholds, frontier, player, or runtime-database policy was added; breakpoint: none.
- **Stage 2:** complete - proof: the baseline focused receipt passed 51 tests; scoped Ruff, format, source-size,
  and diff checks passed; deterministic independent temporary builds, unchanged reruns, metadata refusal,
  injected storage-failure rollback, and unchanged upstream signatures passed; breakpoint: none, temporary
  databases only.
- **Stage 3:** complete - proof: the focused receipt passed 52 tests; bounded fixtures proved repeated
  positions within and across games, global versus route and membership-inclusive counts, nested/multiple
  memberships, parent/child moves, terminal outcomes, white/black scopes, tied chronology, results, ratings,
  deterministic independent temporary builds, persisted raw route events, and S1/S2/S3/corpus preservation. The regression
  proof exposed and fixed omission of PGN in game-metadata provenance and omission of route events from the
  unchanged-build comparison; both fixes remain neutral and within the approved S4 paths. Scoped Ruff, format,
  source-size, and diff checks passed; breakpoint: none.
- **Stage 4:** complete - proof: authorized runtime publication succeeded under the analysis lock after a retained
  online backup and clean pre-write integrity/foreign-key checks. Published corpus 1 with 12,365 games, 639,262
  occurrences, 2,402,576 route events, 639,262 branch events, and projections of 1,022,770 positions, 4,038,362
  routes, 1,054,491 branches, and 4,158,509 route branches. The run is `51e30f3ca92dff1c0b2871ba02280059bc6aaa250159ee761b3e3b780e4b7e2b`;
  exact event-to-projection rebuild equality, representative fact/projection inspection, unchanged S1/S2/S3/corpus
  and existing-table signatures, clean integrity/FK checks, unchanged idempotent rerun, and no SQLite sidecars all
  passed. The first combined proof process hit MemoryError while retaining duplicate large derivations during its
  rerun, before the publisher transaction; a fresh process completed the unchanged rerun. Stage 5 then completed.
- **Stage 5:** complete - fresh independent Quality validation passed: 52 focused tests, all 11 read-only
   `scripts/check.py` steps, independent event/upstream equality, exact rebuild of all four projection families,
   unchanged signatures for all 35 upstream tables versus the retained backup, runtime integrity `ok` with no
   foreign-key violations or SQLite sidecars, and exclusion compliance. The user explicitly accepted S4; the
   complete Plan is archived. Breakpoint: none.
- **Dependency readiness:** Satisfied. S1, S2, and S3 are accepted; the runtime corpus is accepted; source game rows
  contain the required result, rating, color, and chronology fields; no dependency change is approved.
- **Settled decisions:** Use the existing four-field exact-position identity, accepted S3 route/membership facts,
  natural corpus game/ply identities, neutral source context, additive ownership, atomic publication, and no
  formulas, thresholds, or frontier decisions. Stage 1 also fixes membership-inclusive route keys, parent-kind
  branch keys, separate raw/distinct counts, versioned provenance, and the corpus schema prerequisite. Runtime
  publication was authorization-gated and is complete. No new product, data, dependency, or ownership decisions
  were made during closeout.

## Proof

- Temporary SQLite fixtures and independent database builds cover global and route event completeness, raw versus
  distinct-game count separation, parent/child branches, terminal outcomes, color, chronology, results, ratings,
  multiple memberships, repeated games, exact rebuild equality, deterministic output, version refusal, idempotency,
  rollback, and preservation of S1/S2/S3/corpus facts.
- **Stage 1 receipt:** `.venv\Scripts\python.exe -m pytest tests/test_opening_recurrence.py tests/test_opening_classification.py tests/test_opening_catalog.py tests/test_opening_relationships.py tests/test_extract_corpus.py -q` — 48 passed; scoped Ruff check and format check passed; source-size check passed; `git diff --check` passed. Temporary databases only; `data/database/chess_games.db` was not written and has no S4 tables.
- **Stage 2 receipt:** the same focused pytest command — 51 passed before the Stage 3 regression fixture was
  added; scoped Ruff and format checks, source-size check, and `git diff --check` passed. Deterministic
  independent temporary builds, unchanged reruns, metadata refusal, injected rollback, and upstream signature
  comparisons passed; `data/database/chess_games.db` was not written.
- **Stage 3 receipt:** the same focused pytest command — 52 passed; scoped Ruff check, format check, source-size
  check, and `git diff --check` passed. The new temporary fixture compared expected raw recurrence, route, and
  branch facts plus every projection family, checked the two regression repairs, and preserved upstream
  signatures; `data/database/chess_games.db` was not written.
- **Stage 4 receipt:** inline Python runtime safeguards and importer commands acquired
  `data/database/chess_games.db.analysis.lock`, captured pre-write database SHA-256
  `989df76435f76e6c0ccafc6e078a07af38b8e8e899179b595a351d053b47d6d7` (1,083,215,872 bytes), retained the online
  backup at `C:\Users\skyro\AppData\Local\Temp\opencode\s4-authoritative-recurrence-stage4-backup.db`
  (SHA-256 `889e49500273a962d54fa2b599a72ba9ea11fe74db33b0c512e49937f2942433`), and passed pre/post/final
  `PRAGMA integrity_check` (`ok`) and empty `PRAGMA foreign_key_check`. Publication produced the counts recorded
  above and post-write SHA-256 `dafda6cb4c9c236d049ed13c419a3b7490d9cd2b3067acbcee0a0913140426da` (5,305,114,624
  bytes). The accepted input signatures and all 35 pre-existing table signatures were unchanged; the fresh-process
  rerun returned `status=unchanged` with the same run ID and database identity; exact rebuild and representative
  global/route/branch/color/chronology/result/rating inspection passed; runtime and backup SQLite sidecars were empty.
- **Stage 5 receipt:** fresh independent Quality validation passed 52 focused tests and the full read-only
  `.venv\Scripts\python.exe scripts/check.py` run in all 11 steps. Independent event/upstream equality, exact
  rebuilds of all four projection families, unchanged comparison of all 35 upstream tables against the retained
  backup, runtime integrity `ok`, empty foreign-key checks, no SQLite sidecars, and exclusion compliance all
  passed. Explicit human acceptance of S4 was received before archival.
- `.venv\Scripts\python.exe -m pytest tests/test_opening_recurrence.py tests/test_opening_classification.py tests/test_opening_catalog.py tests/test_opening_relationships.py tests/test_extract_corpus.py -q`.
- `.venv\Scripts\python.exe -m ruff check scripts/opening_catalog tests/test_opening_recurrence.py`.
- `.venv\Scripts\python.exe -m ruff format --check scripts/opening_catalog tests/test_opening_recurrence.py`.
- `.venv\Scripts\python.exe scripts/check_size.py --source-max 500 --test-max 700`.
- Authorized runtime proof includes backup, lock/active-writer preflight, integrity and foreign-key checks, exact
  event/projection rebuild equality, pre/post signatures, representative inspection, unchanged rerun, and no
  sidecar residue. Runtime writing is not authorized by this Plan alone.
- Closeout runs `.venv\Scripts\python.exe scripts/check.py` in read-only mode without `--fix`, alongside
  `git diff --check`, documentation/template review, final status, scoped diff review, fresh independent Quality
  validation, explicit acceptance, and archival only after all required receipts are truthful.

## Acceptance

Stages 1 through 5 are accepted only when a human can inspect authoritative global and opening-route recurrence
events, parent/child branch events, chronology, color, result, and rating context; rebuild every projection exactly
from those events without loss or hidden double-counting; and confirm that no formula, threshold, weight, priority,
frontier, player, or training decision is embedded. S1, S2, S3, the accepted game-derived position corpus, and
unrelated database tables remain unchanged. Runtime publication is atomic, the unchanged rerun is proven, fresh
independent validation passes, and explicit human acceptance is recorded before archival.

## Escalation boundaries

- Any request for a recurrence formula, conditional-share formula, denominator policy, threshold, recency/rating
  weighting, branch priority, adaptive frontier, recommendation, or training decision.
- Any change from exact four-field identity, natural game/ply identity, complete S3 route suffixes, or preserved
  source-row memberships to a collapsed, preferred, first/last-only, truncated, or exclusive policy.
- Any need to store usernames, player UUIDs, numeric IDs, SQLite `rowid`, or player-specific facts in S4 neutral
  data; tracked-player projection belongs to S5.
- Any incomplete or changed game metadata that requires changing the fetch/import owner, accepting a new source
  version, or changing result, rating, color, or chronology semantics.
- Any change to accepted S1/S2/S3 facts, corpus position ownership/completeness, opening-owned identity, or the
  established game-derived schema; any destructive migration or replacement.
- Any new API, frontend, engine, population integration, dependency, taxonomy workflow, source update, `Scratch/`
  write, historical edit, or unrelated worktree/database change.
- Any uncertain lock, backup, integrity, active-writer, atomicity, partial-publication, or rerun condition; runtime
  publication without coordinator/user authorization immediately before the write.
- Any need to run `--fix`, suppress or absorb unrelated failures, alter acceptance, archive without independent
  validation and explicit human acceptance, commit, or push.

## Visible result

> A human can inspect the archived authoritative global and opening-route recurrence events and their branch/context
> projections, rebuild all four projection families exactly, and confirm that accepted catalog, classification,
> game-corpus, and unrelated database facts remain unchanged; independent Quality validation and explicit human
> acceptance are recorded above.
