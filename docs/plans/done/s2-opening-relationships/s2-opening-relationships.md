# S2 — Opening hierarchy and transposition relationships - inspectable replay-derived relationships

> **Status:** done - Stage 5 accepted, closeout proof recorded, and archived 2026-08-22

- **Read trigger:** Read before every S2 dispatch and before any opening-relationship schema, derivation, or authorized runtime database action.
- **Upstream:** [Opening Classification Database Preparation master plan](../../../master-plans/opening-classification-database-preparation.md); [accepted S1 Source Catalog Plan](../../done/s1-source-catalog/s1-source-catalog.md)

## Outcome

Persist replay-derived opening parent chains, broad and nested memberships, explicit transposition links, and
all valid position memberships without reducing them to one label. A human can inspect the relationships and
verify that replay order, rather than a lexical or move-order shortcut, preserves the authorized opening facts.

## Scope

- **Included:** All 3,810 records from the accepted S1 manifest; the established four-field exact-position key;
  manifest/source-file/source-row identity; ECO and name facts; replay order; deepest earlier named parent;
  unnamed continuations; broad and nested memberships; different-order transpositions; multiple memberships;
  additive manifest-scoped relationship storage; deterministic derivation; atomic publication; unchanged reruns;
  rollback; and bounded runtime inspection.
- **Expected areas:** `scripts/opening_catalog/**`, `tests/test_opening_catalog.py`, bounded new relationship
  tests when useful, read-only compatibility review of `scripts/chess_com/_replay.py` and existing corpus tests,
  and the authorized runtime target `data/database/chess_games.db`. Expected areas describe ownership, not blanket
  execution authority.
- **Preservation:** The accepted S1 catalog, source/import provenance, four-field identity, opening-owned tables,
  game-derived position ownership and completeness, and unrelated worktree content.
- **Excluded:** Game classification, player facts, recurrence or route facts, thresholds, frontier or priority
  policy, preferred moves, taxonomy editing, frontend, API, dependencies, game-derived position changes,
  `Scratch/` writes, source updates, historical edits, commits, and pushes.

## Stages

1. **accepted - relationship semantics, identity, and additive-schema gate (ORDERED).**
   - **Ordered actions:** Read the accepted S1 manifest and catalog contract; retain source-row identity rather
     than name-only identity or SQLite `rowid`; define replay-path memberships, deepest earlier named parents,
     unnamed continuations, broad/nested memberships, and explicit different-order transposition links; and
     define an additive manifest-scoped extension that leaves S1 catalog/import history and game-derived tables
     unchanged. Use the fixed source facts as bounded fixtures: 3,174 distinct names, 7,927 replay position keys,
     and 2,818 multi-record position memberships.
   - **Focused proof:** Temporary SQLite contract checks show all accepted records remain addressable, exact
     four-field identity is unchanged, duplicate names are not collapsed, and the relationship representation can
     preserve every approved membership and link.
   - **Breakpoint:** None if the extension is additive and ownership-safe; escalate rather than selecting a new
     identity, taxonomy, or relationship policy.
   - **Escalate if:** The standard source cannot represent the settled relationships without collapsing records or
     memberships, changing position ownership, using `rowid`, or requiring destructive migration, a dependency, or
     an excluded policy.

2. **accepted - deterministic derivation and atomic temporary publication (ORDERED).**
   - **Ordered actions:** Replay every accepted source record with the established legal-position semantics; derive
     relationship facts from the accepted manifest and replay paths; publish them atomically to temporary SQLite
     databases; preserve S1 rows and provenance; and support deterministic output, unchanged reruns, and failed
     publication rollback.
   - **Focused proof:** Temporary databases prove complete relationship derivation, deterministic repeated builds,
     schema/version refusal, no partial relationship publication, and unchanged S1 and game-derived signatures.
   - **Breakpoint:** None; proceed only within the Stage 1 additive ownership boundary.
   - **Escalate if:** Derivation requires source mutation, partial publication, replacement of accepted S1 facts,
     or any change to game-derived tables.

3. **accepted - relationship fixtures and regression proof (ORDERED).**
   - **Ordered actions:** Add focused fixtures for parent chains, unnamed continuations, different move-order
     transpositions, broad-plus-nested memberships, and multiple valid memberships; compare replay-derived facts
     against deterministic expected results; and retain existing catalog/corpus preservation regressions.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_catalog.py tests/test_extract_corpus.py -q`,
     plus the bounded relationship fixture tests and temporary SQLite rollback/idempotency assertions.
   - **Breakpoint:** None; the accepted S2 semantics and S1 ownership boundary remain unchanged.
   - **Escalate if:** A regression requires weakening S1 provenance, exact-position identity, game-corpus
     invariants, multiple memberships, or the approved acceptance.

4. **accepted - authorized bounded runtime publication and inspection (ORDERED).**
   - **Ordered actions:** Capture read-only backup, lock, integrity, schema, S1 catalog, relationship, and
     game-derived signatures; verify writer safety; obtain explicit human authorization immediately before writing
     `data/database/chess_games.db`; publish the accepted relationship facts atomically; inspect parent, membership,
     and transposition examples; verify S1 and game-derived rows are unchanged; and repeat the publication to prove
     unchanged rerun behavior. Keep failure injection on temporary or copied databases.
   - **Focused proof:** Authorized runtime inspection with SQLite integrity and foreign-key checks, relationship and
     S1 counts/provenance, pre/post signatures, and unchanged-rerun evidence.
   - **Breakpoint:** Explicit human authorization is required immediately before the runtime database write.
   - **Escalate if:** Lock, backup, integrity, schema, or active-writer safety is uncertain; publication could be
     partial; or any operation would alter, replace, or delete game-derived or accepted S1 data.

5. **completed - independent validation, human acceptance, closeout, and archival (ORDERED).**
   - **Ordered actions:** Obtain fresh independent validation of replay order, parent chains, unnamed continuations,
     transpositions, broad/nested memberships, multiple memberships, atomicity, reruns, and preservation; run the
     full read-only check without `--fix`; review the scoped diff, Plan shape, and unrelated worktree preservation;
     obtain explicit human acceptance; then update this Plan and archive its complete directory under
     `docs/plans/done/s2-opening-relationships/`.
   - **Focused proof:** `.venv\Scripts\python.exe scripts/check.py`; `git diff --check`; manual documentation/template
     review; final `git status --short`; and scoped diff review.
    - **Breakpoint:** Resolved 2026-08-22: fresh independent validation passed, truthful runtime proof was recorded,
      and the user explicitly accepted Stage 5 before archival.
   - **Escalate if:** Closeout requires `--fix`, suppression of unrelated failures, historical edits, scope expansion,
     acceptance changes, or a claim of completion without the required runtime and independent proof.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the approved outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** accepted - the S1 identity remains `(manifest_hash, source_file, source_row_ordinal)`; names,
  ECO, endpoints, and hashes remain facts; SQLite `rowid` and surrogate identity are not used. The approved
  relationship extension is additive and manifest-scoped, with the seven relationship tables, composite foreign
  keys, and no changes to S1 catalog/provenance or game-derived position ownership.
- **Stage 2:** accepted - deterministic replay derivation and atomic temporary publication are implemented and
  proven. Memberships retain every post-move exact four-field position with source-row/ply identity and generated
  UCI/SAN; parent links retain every deepest earlier named endpoint, including ties, without name parsing; and
  transposition links retain canonical source-row pairs only when ordered UCI prefixes differ.
- **Stage 3:** accepted - deterministic TSV fixtures prove parent chains with deepest/tied parents, unnamed
  continuation beyond a named endpoint, different-order transpositions, broad/nested paths, and all memberships
  sharing an exact position; existing atomicity, idempotency, S1 catalog, and corpus regressions remain green.
  Breakpoint: none.
- **Stage 4:** accepted - the explicitly authorized runtime publication completed atomically with run `89c0f110093adff9afce5c7c9ba9ea39f771a703928a985e679b9a16293b6e66`, manifest `22b666b2402ee912c3323acf251e4ae9097ed344a8b2c1315db84fe4bec405b4`, and counts of 3,810 records, 7,927 positions, 36,925 memberships, 3,790 parent links, and 12,077 transposition links. Integrity/FK checks, representative inspection, S1/game-derived preservation, and the unchanged rerun all passed. Decision: retain the additive relationship publication; no rollback or repair was needed.
- **Stage 5:** completed - fresh independent Quality validation passed for replay order, parent chains, unnamed continuations, memberships, transpositions, atomicity, reruns, and preservation. The full read-only check and documentation review were recorded; its unrelated pre-existing failures were not repaired or absorbed. The user explicitly accepted Stage 5 on 2026-08-22, and the complete feature directory was archived.

### Pause record

Stage 2 implementation is limited to `scripts/opening_catalog/schema.py`,
`scripts/opening_catalog/relationships.py`, `scripts/opening_catalog/relationship_persistence.py`,
`scripts/opening_catalog/__init__.py`, and bounded additions to `tests/test_opening_catalog.py`. It adds
`opening_relationship_schema`, `opening_relationship_state`, `opening_relationship_run`,
`opening_relationship_position`, `opening_position_membership`, `opening_parent_link`, and
`opening_transposition_link`. Publication checks the accepted S1 manifest, uses a deterministic run identity,
publishes facts and state in one transaction, and leaves the S1 and game-derived tables untouched.

Temporary full-source receipts are:

- 3,810 records, 7,927 relationship positions, 36,925 post-move memberships, 3,790 parent links, and 12,077
  transposition events.
- 2,818 multi-record position keys, 3,790 records with parents, 20 roots, and 518 transposition positions.
- Independent relationship-table snapshots were identical; the second import returned `unchanged`.
- `PRAGMA foreign_key_check` returned `[]`; injected publication failure left no relationship facts or state;
  incompatible relationship schema version was refused without relationship writes.
- S1 catalog rows and seeded game-derived position rows were unchanged in the bounded preservation regression.

Stage 3 is accepted from its deterministic fixture and regression proof. The next resumption point is Stage 4's
authorized runtime publication and inspection; do not start runtime publication from this pause record.

## Proof

- Temporary SQLite proof covers all accepted records, replay-derived relationship completeness, deterministic repeated
  builds, atomic rollback, no partial publication, S1 provenance preservation, and unchanged game-derived rows.
- `.venv\Scripts\python.exe -m pytest tests/test_opening_catalog.py -q` passed 13 tests; the bounded S1/corpus
  boundary command `.venv\Scripts\python.exe -m pytest tests/test_opening_catalog.py tests/test_extract_corpus.py -q`
  passed 34 tests.
- `.venv\Scripts\python.exe -m pytest tests/test_opening_relationships.py -q` passed 1 deterministic fixture test,
  covering complete expected memberships, parent links, and transposition links through TSV source paths.
- `.venv\Scripts\python.exe -m ruff check scripts/opening_catalog tests/test_opening_catalog.py` passed;
  `.venv\Scripts\python.exe -m ruff format --check scripts/opening_catalog tests/test_opening_catalog.py` passed;
  and `.venv\Scripts\python.exe scripts/check_size.py --source-max 500 --test-max 700` passed for 173 files.
- Stage 3 touched-test checks passed: `.venv\Scripts\python.exe -m ruff check tests/test_opening_relationships.py`,
  `.venv\Scripts\python.exe -m ruff format --check tests/test_opening_relationships.py`, and the size check above.
- Stage 4 runtime preflight confirmed the verified backup `C:\Users\skyro\AppData\Local\Temp\opencode\s2-stage4-runtime-backup-20260821-v1.db`, accepted manifest/catalog match, runtime integrity `ok`, empty foreign-key check, relationship-table absence, no WAL/SHM/journal, lock sentinel `00000000000`, and no matching backend/extraction/writer process. The source replay command reported 3,810 records, 7,927 positions, 36,925 memberships, 3,790 parents, and 12,077 transpositions; the runtime publication command returned `status='success'` with deterministic run ID `89c0f110093adff9afce5c7c9ba9ea39f771a703928a985e679b9a16293b6e66`.
- Post-write `.venv\Scripts\python.exe -c ...` SQLite inspection returned integrity `ok` and `PRAGMA foreign_key_check []`; all seven relationship tables were present at schema version 1. Relationship counts were exactly 7,927 positions, 36,925 memberships, 3,790 parent links, and 12,077 transposition links, with state/run provenance matching the accepted manifest and run. Representative parent, membership, shared-position, and different-order transposition examples were inspected; examples include Amar/Paris parent links, two B78 memberships sharing one exact position, and Cambridge Springs Argentine/Bogoljubow transposition prefixes.
- Deterministic relationship signatures after publication were: schema `5cc6a8a697bb6f2fcb468ef02cf2a76e9ad3f5da223682f1ca29288836ee66b3`, state `3c59c1cd2a989d8c257d05847600e7ccd58b41e9584c8bddd9527a1e457194fe`, run `226b32bdd9455331e67e04a27611297c033148781ad623ae2328c26dce9af947`, positions `17070b9124afbc9becf6207b7a95c079f24e060ab9d7afa0beb7e0ab3643773c`, memberships `068dcf0e49faac468c43817d7a3e21ddd1ec8ee1fb28e3b0b555643733111a11`, parents `1ee8fab09a9d8b555897b0a1a2ad2feef1f90cef67b8140f8ac1face95316045`, and transpositions `3bcf84774cd10d6d325798b4324ce1818489a91a75bc454e5bd43a9c5642c907`.
- The accepted S1 group signature was unchanged at `1118a485b4b7fb6edde6c35adc647ab0ca3310988d465087ee7128c6dabcc217`, and the game-derived group signature was unchanged at `1af90db51620ba12975cfe80be57e556f092e49a4b607ced5d369c0227def957`; all compared S1 rows and game-derived rows matched the verified backup, including 3,810 catalog rows, 510,876 position states, and 639,262 position occurrences.
- The exact repeat command `.venv\Scripts\python.exe -c ... import_relationships(...)` returned `status='unchanged'` with the same run ID, counts, relationship signatures, state, and one successful run; integrity remained `ok`, the foreign-key check remained empty, and no sidecar journal files remained.
- Fresh independent Quality validation passed: SQLite integrity and foreign-key checks were clean; all seven relationship-table signatures and complete content equality were independently reproduced; relationship semantics, deterministic derivation, reruns, and preservation all passed. One packet-only combined relationship-group signature was not reproducible and was nonblocking.
- `.venv\Scripts\python.exe scripts\check.py` was run in read-only mode without `--fix`. S2-specific validation passed; the check retained unrelated pre-existing failures: TypeScript errors in `frontend/src/features/board-adapter/BoardAdapter.stories.tsx` at lines 93 and 98, plus one E2E timeout in `tests/e2e/viewer-live-position.spec.ts:15` with 45 E2E tests passing. These failures were not claimed as passed or repaired.
- `git diff --check`, manual documentation/template review, final path verification, and scoped status/diff review passed. No transient `handoff.md` existed; the complete feature directory was moved to `docs/plans/done/s2-opening-relationships/`.

## Acceptance

Stages 1 through 5 are accepted: a human can inspect the relationship
facts and verify that replay order—not a single label, lexical shortcut, or move-order shortcut—preserves deepest
earlier parents, unnamed continuations, broad/nested memberships, explicit transpositions, and all valid
memberships while the accepted S1 catalog/provenance and game-derived rows remain unchanged. Runtime publication was
atomic, independent validation passed, and final archival completed. The unrelated full-check failures remain outside
S2 scope and were not absorbed.

## Escalation boundaries

- Any inability to add manifest-scoped relationship facts without changing S1 identity, provenance, opening-owned
  ownership, or game-derived position ownership/completeness.
- Any need to collapse duplicate source records, collapse valid memberships, choose a preferred label or move,
  introduce taxonomy editing, frontier/priority policy, thresholds, recurrence, classification, or player facts.
- Any new API, frontend, dependency, source update, `Scratch/` write, destructive migration or replacement, or
  change to accepted S1 data.
- Any unsafe runtime lock, backup, integrity, active-writer, atomicity, partial-publication, or rerun condition.
- Any acceptance, historical-record, unrelated-worktree, commit, push, `--fix`, or closeout decision not already
  settled above.

## Visible result

> A human can inspect the SQLite opening relationships and verify replay-derived parents, broad/nested memberships,
> different-order transpositions, and all valid memberships while the accepted catalog and game-derived corpus stay unchanged.
