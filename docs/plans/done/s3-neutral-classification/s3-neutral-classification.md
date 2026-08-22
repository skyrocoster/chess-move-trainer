# S3 — Neutral game classification and downstream route facts - inspectable neutral opening routes for accepted games

> **Status:** done - all five stages accepted; independent Quality validation passed and the Plan is archived

- **Read trigger:** Read before any S3 classification schema, derivation, import, or authorized runtime database action.
- **Upstream:** [Opening Classification Database Preparation master plan](../../../master-plans/opening-classification-database-preparation.md); [accepted S1 Source Catalog Plan](../../done/s1-source-catalog/s1-source-catalog.md); [accepted S2 Opening Relationships Plan](../../done/s2-opening-relationships/s2-opening-relationships.md); [route and classification evidence](../../../grilling-docs/opening-training-and-repertoire-preparation.md)

## Outcome

Persist additive, neutral classification facts for all accepted games. Every exact S1 catalog endpoint reached by
an accepted game is recorded with its game/ply anchor, immutable catalog provenance, all matching memberships, and
the complete observed downstream route through the game's accepted final occurrence. The facts remain independent
of player identity and cannot be partially published.

## Scope

- **Included:** Accepted corpus games and their game-derived occurrences; exact four-field endpoint matching against
  the accepted S1 manifest; catalog identity `(manifest_hash, source_file, source_row_ordinal)`; game/ply anchors;
  S2 relationship and multiple-membership provenance; raw downstream route occurrences from each anchor through the
  accepted game end; additive versioned schema and import-run provenance; deterministic derivation; atomic temporary
  publication; unchanged reruns; failure rollback; bounded runtime publication and inspection after authorization;
  and focused neutral-classification fixtures and regressions.
- **Expected areas:** `scripts/opening_catalog/**`, `tests/test_opening_classification.py`, bounded additions to
  `tests/test_opening_catalog.py` and `tests/test_extract_corpus.py`, read-only compatibility review of
  `scripts/chess_com/{_schema.py,_replay.py,_persistence.py,_history.py,extract_corpus.py}`, and the authorized
  runtime target `data/database/chess_games.db`.
- **Excluded:** Player recurrence or projection, adaptive-frontier membership, formulas, thresholds, aggregate
  totals or denominator policy, preferred moves, training history, engines, population evidence, frontend, API,
  source changes, game-corpus mutation, dependency changes, taxonomy editing or reclassification workflows,
  destructive migration or replacement, `Scratch/` writes, historical edits, commits, pushes, and unrelated
  worktree content.

## Stages

1. **pending - neutral identity, route contract, and additive-schema gate (ORDERED).**
   - **Ordered actions:** Verify the accepted S1 manifest, catalog row identity, S2 relationship state, and accepted
     corpus boundary. Specify exact endpoint matching as the definition of “encountered”; preserve every matching
     catalog membership; identify anchors by catalog provenance plus `game_uuid` and `ply`; and define the raw route
     as the complete observed suffix from each anchor through the accepted final occurrence. Keep the four-field
     position key and natural game occurrence identity authoritative, without SQLite `rowid`, player references, or
     exclusive-label reduction. Define additive S3 schema, manifest/version provenance, and publication-state
     ownership without changing S1, S2, or game-derived tables.
   - **Focused proof:** Temporary SQLite contract checks show accepted catalog rows, relationship memberships, and
     accepted game occurrences remain addressable; exact keys and composite identities are preserved; multiple
     memberships remain distinct; and the proposed S3 tables cannot require opening-only rows in game-derived
     position tables.
   - **Breakpoint:** None if the approved raw-fact semantics and additive ownership boundary remain sufficient.
   - **Escalate if:** Encounter semantics become first/last-only, inherited-membership, truncated, frontier-bound, or
     threshold-bound; route totals require an aggregate denominator decision; or the schema needs a new identity,
     ownership model, dependency, destructive migration, or mutation of accepted source/corpus facts.
2. **pending - deterministic derivation and atomic temporary publication (ORDERED).**
   - **Ordered actions:** Derive endpoint matches from the accepted catalog and accepted game occurrences; emit all
     source-row-specific anchors and raw route suffix facts; retain exact four-field route positions, game/ply order,
     corpus move provenance, manifest identity, and S2 membership context; and publish the complete classification to
     temporary SQLite databases atomically with deterministic run/version records, source compatibility checks, and
     unchanged-rerun behavior.
   - **Focused proof:** Temporary databases prove deterministic repeated derivation, complete accepted-game and
     occurrence coverage, S1/S2 preservation, manifest/version refusal, unchanged reruns, and no S3 facts or
     publication state after an injected derivation or storage failure.
   - **Breakpoint:** None; runtime database publication is not part of this stage.
   - **Escalate if:** Derivation requires reinterpreting the approved endpoint/route contract, changing game-derived
     position ownership, accepting a changed source without approval, or allowing any partial publication.
3. **pending - focused classification and preservation regression proof (ORDERED).**
   - **Ordered actions:** Add deterministic PGN/SQLite fixtures for nested endpoint names, taxonomy transpositions,
     repeated endpoint encounters, multiple matching memberships, anchors at different plies, complete routes to
     game end, terminal anchors, and replay failure. Compare expected raw facts and route order; prove all accepted
     games and occurrences are covered; verify neutral facts contain no player dependency; and retain S1, S2, and
     game-corpus preservation regressions.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_classification.py tests/test_opening_catalog.py tests/test_extract_corpus.py -q`, plus scoped Ruff, format, size, deterministic-signature, and injected rollback assertions.
   - **Breakpoint:** None; proceed only while the approved raw-fact and ownership boundaries remain unchanged.
   - **Escalate if:** A fixture exposes a need for preferred labels, membership collapsing, route truncation, a
     recurrence or threshold policy, weakened four-field identity, changed S1/S2 facts, or absorbed unrelated
     failures.
4. **complete - authorized bounded runtime publication and inspection (ORDERED).**
   - **Ordered actions:** Capture read-only backup, lock, integrity, schema, S1, S2, and game-derived signatures;
     verify active-writer safety; obtain explicit human authorization immediately before writing
     `data/database/chess_games.db`; publish the accepted S3 facts atomically; inspect representative anchors,
     memberships, and complete routes; verify S1/S2 and game-derived signatures are unchanged; and repeat the
     publication to prove unchanged behavior. Keep failure injection on temporary or copied databases.
   - **Focused proof:** Authorized runtime inspection proves SQLite integrity, an empty foreign-key check, complete
     classification counts and provenance, representative nested/transposed/multiple-membership routes, identical
     pre/post S1/S2/corpus signatures, and an unchanged rerun with no sidecar publication residue.
   - **Breakpoint:** Explicit human authorization is required immediately before the runtime database write.
   - **Escalate if:** Backup, lock, integrity, schema, active-writer, or atomicity conditions are uncertain; runtime
     versions differ; or any operation would alter, replace, or delete accepted S1, S2, or game-derived data.
5. **pending - independent validation, acceptance, closeout, and archival (ORDERED).**
   - **Ordered actions:** Obtain fresh independent Quality validation of endpoint matching, anchors, provenance,
     memberships, route completeness, atomicity, reruns, and preservation; run the full read-only check without
     `--fix`; review the scoped diff and Plan shape; obtain explicit human acceptance; then archive the complete Plan
     directory only after the outcome and proof are accepted.
   - **Focused proof:** `.venv\Scripts\python.exe scripts/check.py`; `git diff --check`; scoped Ruff, format, and
     size checks; documentation/template review; final `git status --short`; and independent comparison of the
     temporary and authorized runtime receipts. Unrelated failures remain reported outside S3.
   - **Breakpoint:** Fresh independent validation and explicit human acceptance are required before archival.
   - **Escalate if:** Closeout requires `--fix`, suppression of unrelated failures, historical edits, scope expansion,
     acceptance changes, destructive cleanup, or claiming completion without runtime and independent proof.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the approved outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** accepted - Independent Quality PASS: focused Plan-boundary tests 37 passed; S1/S2 regressions 14 passed; corpus regression 21 passed; Ruff/format/size/diff checks passed; 38/38 temporary SQLite contract checks passed; runtime DB untouched; scope clean.
- **Stage 2:** accepted - deterministic derivation and atomic publication passed in temporary SQLite databases only. The proof covered all accepted games, exact endpoint anchors, separate source-row memberships, inclusive route suffixes, manifest/version compatibility, independent deterministic facts, unchanged reruns, S1/S2/corpus preservation, and derivation/storage rollback with no partial S3 facts or publication state. Breakpoint: none; Stage 3 was the next ordered boundary.
- **Independent Stage 2 validation receipt (recorded before Stage 3 execution):** Quality PASS - 44 Plan-boundary tests; Ruff, format, size, and diff checks passed; independent temporary-SQLite proofs passed for deterministic independent outputs, unchanged rerun/same run ID, S1/S2/corpus preservation, version/manifest refusal with no S3 state, derivation failure with no tables, and storage failure with all S3 facts rolled back. Runtime DB untouched; scope clean.
- **Stage 3:** accepted - focused nested, transposition, repeated/multiple-membership, route-completeness,
  neutral-determinism, and replay/storage regressions passed; breakpoint: none. Stage 4 remains pending and was
  not executed.
- **Independent Stage 3 Quality receipt (accepted before Stage 4 execution):** Quality PASS - Plan-boundary tests
  44 passed; fixture/rollback trio 3 passed; 3 accepted games, 8 anchors, and 25 route facts independently
  confirmed; nested/transposition/repeated/multi-membership/terminal-route/determinism/preservation/rollback
  evidence confirmed; Ruff, format, size, and diff checks passed; runtime publication remains pending; scope clean.
- **Stage 4:** accepted - bounded runtime publication and inspection passed; explicit human authorization was
  supplied immediately before the runtime write.
- **Stage 5:** accepted - independent Quality validation, full read-only checks, scoped review, explicit acceptance,
  and archival passed; breakpoint: none.
- **Independent Stage 5 Quality receipt (2026-08-22):** Quality PASS - 44 focused tests passed; Ruff passed;
  format passed for 13 files; size passed for 179 files; and `git diff --check` passed. The full read-only
  `.venv\Scripts\python.exe scripts\check.py` passed all 11 checks, including Python, frontend, workflow, E2E,
  and build checks. Independent read-only SQLite proof passed all 80/80 checks: integrity was ok with an empty
  foreign-key check; one successful run/state was present; counts were 12,365 games, 49,608 anchors, 2,402,576
  routes, and 49,608 complete groups; exact set-based re-derivation matched in both directions; every route was
  the complete inclusive suffix; all accepted games were covered; and all provenance/occurrence joins were
  complete. Manifest `22b666b2402ee912c3323acf251e4ae9097ed344a8b2c1315db84fe4bec405b4` and run
  `1045b3e04de0fb622beb5333228f5ac708797552304c63dec957fbde2f5bea95` matched; the unchanged rerun returned the
  same run ID. All 19 S1/S2/corpus tables were byte-identical pre/post; only six additive S3 tables were added;
  no partial state or SQLite sidecars remained; and the scope was clean. Exclusions remained preserved: no
  player, aggregate/formula, frontier/training, API/frontend, dependency/source, corpus/S1/S2 mutation, or rowid
  changes. Explicit human acceptance was supplied for closeout.
- **Decision:** “Encountered” is an exact accepted S1 catalog endpoint match. A route is the complete observed suffix from that anchor through the accepted final occurrence. Matching memberships remain separate raw facts and are not aggregated in S3. S1’s four-field position identity, catalog row identity, opening-owned separation, and no-`rowid` rule remain unchanged.

## Proof

- Temporary SQLite fixtures cover exact endpoint matching, nested names, taxonomy transpositions, repeated encounters,
  multiple memberships, anchors, complete downstream routes, terminal routes, deterministic comparisons, accepted-game
  and occurrence completeness, and replay/storage rollback with no partial S3 facts or publication state.
- Stage 1 receipt: Independent Quality PASS recorded 37 focused Plan-boundary tests, 14 S1/S2 regression tests, 21
  corpus regression tests, passing Ruff/format/size/diff checks, 38/38 temporary SQLite contract checks, untouched
  runtime DB, and clean scope.
- Stage 2 temporary proof: `.venv\Scripts\python.exe -m pytest tests/test_opening_classification.py
  tests/test_opening_catalog.py tests/test_opening_relationships.py tests/test_extract_corpus.py -q` passed 44
  tests; the classification fixtures proved deterministic independent databases, 1 accepted game, 2 separate
  memberships/anchors, 4 inclusive route facts, S1/S2/corpus preservation, version refusal, and derivation/storage
  rollback with no partial S3 rows. Scoped Ruff passed; scoped Ruff format check passed for 12 files; source-size
  check passed for 179 files; and `git diff --check` passed (with unrelated LF/CRLF normalization warnings only).
- Independent Stage 2 validation: Quality PASS for the 44 Plan-boundary tests, Ruff/format/size/diff checks, and
  independent temporary-SQLite proofs covering deterministic independent outputs, unchanged rerun/same run ID,
  S1/S2/corpus preservation, version/manifest refusal with no S3 state, derivation failure with no tables, and
  storage failure with all S3 facts rolled back. Runtime DB untouched; scope clean.
- Stage 3 focused proof: `.venv\Scripts\python.exe -m pytest
  tests/test_opening_classification.py tests/test_opening_catalog.py tests/test_extract_corpus.py -q` passed 44
  tests. The deterministic PGN/SQLite fixture covered 3 accepted games, 8 anchors, 25 inclusive route facts,
  nested names, taxonomy transposition pairs, repeated endpoints at plies 4 and 8, separate memberships, anchors
  at different plies, terminal anchors, complete suffixes to plies 6/9/5, independent subject identities with
  identical classification rows, and unchanged rerun output. S1/S2/corpus boundary signatures were unchanged.
- Stage 3 rollback receipt: `.venv\Scripts\python.exe -m pytest
  tests/test_opening_classification.py::test_stage3_rich_fixture_covers_routes_memberships_and_neutral_determinism
  tests/test_opening_classification.py::test_stage2_storage_failure_rolls_back_every_classification_fact
  tests/test_opening_catalog.py::test_replay_failure_records_failed_run_without_catalog_rows -q` passed 3;
  replay failure left no catalog rows or accepted state, and injected S3 storage failure left every S3 fact table
  empty. Scoped Ruff passed; scoped Ruff format check passed for 12 files; source-size check passed for 179 files;
  and scoped `git diff --check` passed. Runtime DB untouched; scope clean.
- **Independent Stage 3 Quality receipt:** accepted before Stage 4 execution; 44 Plan-boundary tests and the
  three fixture/rollback checks passed, with independent confirmation of 3 accepted games, 8 anchors, 25 routes,
  nested/transposed/repeated/multiple-membership/terminal-route/determinism/preservation/rollback evidence, and
  clean scoped static proof.
- **Stage 4 runtime receipt (2026-08-22):** read-only SQLite online backup captured at
  `C:\Users\skyro\AppData\Local\Temp\opencode\s3-stage4-runtime-backup-20260822-luna.db`; backup integrity was
  `ok` with an empty foreign-key check. The runtime was `delete` journal mode, had no S3 classification tables
  before publication, and reported S1/S2/corpus schema versions `1/1/1` with accepted manifest
  `22b666b2402ee912c3323acf251e4ae9097ed344a8b2c1315db84fe4bec405b4`. The backend service was observed using
  the repository's read-only database connection path and the frontend was static; the database mtime and
  SQLite `data_version` stayed stable during the bounded preflight. `BEGIN IMMEDIATE` was acquired before the
  additive schema operation and again for the fact publication and unchanged rerun; no service/process was
  stopped or destructively handled.
- **Stage 4 publication:** run `1045b3e04de0fb622beb5333228f5ac708797552304c63dec957fbde2f5bea95`, status
  `success`, schema/catalog/relationship versions `1/1/1`, corpus `1`; counts were `12,365` games, `49,608`
  anchors, and `2,402,576` complete route facts. Every anchor matched its S1 provenance, every route group
  covered the inclusive anchor-to-final suffix, and all `12,365` accepted games had final-ply coverage. Runtime
  inspection found representative nested S2 links (`a.tsv` rows 17/12), transposition links (`a.tsv` rows
  459/681 at ply 4), and a classified route position with 2,023 distinct S2 membership rows. The S3 table set,
  version, neutral columns, and WITHOUT ROWID contract were verified; no player fields or SQLite `rowid` usage
  was introduced.
- Runtime S1 endpoint keys were unique, so the multiple-membership representative is explicitly a classified
  route position joined to its distinct S2 memberships rather than a duplicate S1 endpoint; the approved exact
  endpoint and source-row identity semantics were not changed.
- **Stage 4 preservation and rerun:** pre/post S1 signatures were
  `e25bc453325b2442812b60f57bdfb782c9bac50716225e7ed646b03acf0d9580`;
  S2 signatures were `71f66a2d0f2dbc193e7f70005b9201d6dd77a88850ed3ae3640974fcba27f9cd`; corpus signatures were
  `00fe68d38a4792217acd358a14a903cec1c8186a1f084c2942548589f818fb8f`; and S1/S2/corpus schema signatures
  were unchanged. Post-publication integrity was `ok`, the foreign-key check was empty, and `-wal`, `-shm`,
  and `-journal` sidecars were absent. The repeated publication returned `unchanged` with the same run ID and
  stable S3 receipts (`12,365/49,608/2,402,576`).
- `.venv\Scripts\python.exe -m pytest tests/test_opening_classification.py tests/test_opening_catalog.py tests/test_extract_corpus.py -q` and scoped Ruff, format, and source-size checks.
- Stage 4 focused proof: the same Plan-boundary pytest command passed 44 tests; `.venv\Scripts\python.exe -m
  ruff check scripts/opening_catalog tests/test_opening_classification.py tests/test_opening_catalog.py
  tests/test_extract_corpus.py` passed; scoped `ruff format --check` reported 12 files already formatted;
  `scripts/check_size.py --source-max 500 --test-max 700` passed for 179 files; and `git diff --check` passed
  with only the existing LF/CRLF normalization warnings. The authorized runtime inspection, complete-count and
  route-group checks, preservation signatures, and unchanged rerun all passed.
- Authorized runtime proof covers SQLite integrity, foreign keys, S3 counts and provenance, representative anchors and
  routes, pre/post S1/S2/game-derived signatures, and unchanged rerun behavior.
- **Stage 5 closeout proof:** Independent Quality PASS confirmed the focused 44-test suite, Ruff, 13-file format,
  179-file size, and `git diff --check` results. The full read-only `.venv\Scripts\python.exe scripts\check.py`
  passed all 11 checks. Independent SQLite proof passed 80/80 checks and confirmed the successful manifest/run,
  12,365 games, 49,608 anchors, 2,402,576 routes, 49,608 complete groups, bidirectional exact set re-derivation,
  complete inclusive suffixes, accepted-game coverage, complete provenance/occurrence joins, byte-identical S1/S2/
  corpus tables, six additive S3 tables only, no partial state or sidecars, and preserved exclusions. The scoped
  review was clean, explicit acceptance was recorded, and the complete feature directory was archived.
- `.venv\Scripts\python.exe scripts/check.py` runs at closeout in read-only mode without `--fix`, alongside
  `git diff --check`, documentation/template review, final status, scoped diff review, and fresh independent Quality
  validation.

## Escalation boundaries

- Any change from exact endpoint matching, complete observed suffix routes, or source-row-specific memberships to a
  first/last-only, inherited, truncated, frontier, threshold, preferred-label, or exclusive-membership policy.
- Any aggregate total, denominator, recurrence, formula, priority, player, training, engine, population, API,
  frontend, dependency, source, taxonomy, or acceptance decision.
- Any change to S1/S2 identity, provenance, additive ownership, the exact four-field game-position identity, corpus
  ownership/completeness, or the no-SQLite-`rowid` boundary.
- Any source/schema-version mismatch, destructive migration or replacement, partial-publication risk, unsafe runtime
  lock/backup/integrity/active-writer condition, or need to write under `Scratch/`.
- Any historical-record, unrelated-worktree, commit, push, `--fix`, suppression of unrelated failures, or archival
  decision outside the approved closeout sequence.

## Visible result

> Final visible result: A human can inspect every exact catalog opening reached by an accepted game, its immutable source provenance and game anchor, and every observed downstream route while all memberships remain visible and failed publication leaves no partial classification.
