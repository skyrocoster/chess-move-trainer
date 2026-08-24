# S5 - Tracked-player projection for skyrocoster - inspectable personal facts keyed by stable player UUID

> **Status:** Closed - abandoned after failed and interrupted Stage 4 runtime publication; the database was restored to S1-S4, and the overall S5 outcome was not accepted.

- **Read trigger:** Read before any tracked-player schema, identity resolution, personal projection, importer, or authorized runtime database action.
- **Upstream:** [Opening Classification Database Preparation master plan](../../../master-plans/opening-classification-database-preparation.md);
  [accepted S3 Neutral Classification Plan](../../done/s3-neutral-classification/s3-neutral-classification.md);
  [accepted S4 Authoritative Recurrence Plan](../../done/s4-authoritative-recurrence/s4-authoritative-recurrence.md)
- **Closeout:** [S5 tracked-player projection retrospective](../../../grilling-docs/s5-tracked-player-projection-retrospective.md)

## Intended outcome (not delivered)

The Plan intended to persist additive personal classification and approved recurrence projections for the initially
configured player skyrocoster. It would resolve the configured username only at the setup/import boundary, then key
every durable personal fact by the existing stable player-ID UUID, implemented by `players.uuid`. Neutral S3
classifications and authoritative S4 events were to remain independent, reusable, and unchanged. Runtime delivery
failed, the backup was restored, and this intended outcome was not accepted.

## Scope

- **Included:** One explicit tracked-player model; skyrocoster-only initial configuration; case-insensitive
  setup/import-boundary username resolution requiring exactly one existing player; agreement between the resolved
  UUID and accepted corpus ownership; UUID foreign-key references through `players.uuid`; personal classification
  associations derived from accepted neutral S3 facts; personal position, route, branch, and route-branch
  projections derived from accepted S4 recurrence events; preservation of exact four-field positions, natural
  game/ply identities, source-row memberships, color, chronology, result, rating, and raw-versus-distinct count
  semantics; additive schema/version/run/state provenance; input change detection; deterministic builds; atomic
  publication; unchanged reruns; rollback; temporary SQLite proof; authorized runtime publication; and independent
  closeout validation.
- **Expected areas:** `scripts/opening_catalog/tracked_player_*.py`, bounded exports in
  `scripts/opening_catalog/__init__.py`, `tests/test_opening_tracked_player.py`, read-only compatibility review of
  `scripts/opening_catalog/{classification_*,recurrence_*}.py`, `scripts/chess_com/{config.yaml,_schema.py}`,
  and the existing player/game/corpus schema. The authorization-gated runtime artifact is
  `data/database/chess_games.db`; this archived Plan is
  `docs/plans/done/s5-tracked-player-projection/s5-tracked-player-projection.md`.
- **Excluded:** Additional initial players; username strings as durable fact references; a new or literal
  `players.id` column; numeric player IDs; SQLite `rowid`; changes to the Chess.com fetcher, corpus importer,
  configuration ownership, accepted S1/S2/S3/S4 facts, game-derived corpus, players, games, or source data;
  formulas, denominator policies, thresholds, recency or rating weights, priority scores, preferred moves,
  adaptive-frontier decisions, recommendations, training history or progression; API, frontend, authentication,
  authorization, engines, population evidence, dependencies, taxonomy workflows, destructive migration or
  replacement, `Scratch/` writes, historical edits, commits, pushes, and unrelated worktree or database content.

## Stages

1. **complete as temporary proof only - tracked-player identity contract and additive-schema gate.**
   - **Ordered actions:** Verify the accepted S3 and S4 states, accepted corpus, existing player schema, and current
     single-player configuration. Resolve `skyrocoster` case-insensitively at the setup/import boundary, require
     exactly one match, and require its UUID to equal the accepted corpus subject UUID. Treat the master plan's
     stable player-ID UUID as the implemented `players.uuid`; do not add `players.id`. Define the tracked-player,
     personal-classification, projection, schema, run, and accepted-state ownership using UUID foreign keys,
     natural composite keys, and `WITHOUT ROWID`. Define S3/S4 input signatures and upstream preservation
     signatures without adding username columns to durable personal fact or projection tables.
   - **Focused proof:** Temporary SQLite contract checks show unique username-to-UUID resolution, corpus agreement,
     stable UUID references, additive ownership, natural identities, complete access to accepted S3/S4 inputs, no
     player fields in neutral tables, and no username, numeric-ID, `rowid`, formula, threshold, priority, or frontier
     columns in personal fact/projection tables.
   - **Breakpoint:** None while `players.uuid` is accepted as the existing stable player-ID UUID and the approved
     additive ownership boundary is sufficient. Escalate rather than adding a new identity, configuration contract,
     or personal policy.

2. **complete as temporary proof only - deterministic derivation and atomic temporary publication.**
   - **Ordered actions:** Implement the bounded identity contract, additive schema, personal derivation, and
     persistence modules. Derive personal classification associations from accepted neutral S3 facts for games
     belonging to the resolved player. Derive personal position, route, branch, and route-branch projections only
     from authoritative S4 events while retaining approved membership, color, chronology, result, rating, and
     raw-versus-distinct count semantics. Publish the complete tracked-player state, facts, projections, and run
     provenance atomically in temporary SQLite databases. Refuse missing or ambiguous username resolution,
     UUID/corpus disagreement, incompatible schema versions, or changed inputs; support deterministic independent
     builds, stable run identity, unchanged reruns, and failed-publication rollback.
   - **Focused proof:** Temporary database tests prove exact S3/S4-to-personal derivation equality,
     skyrocoster-only output, stable UUID keys, deterministic independent builds, identical rerun status and run ID,
     input-change refusal, no partial accepted state or personal facts after derivation/storage failure, and
     unchanged neutral and upstream signatures.
   - **Breakpoint:** None; runtime database publication is not part of this stage.

3. **complete as temporary proof only - focused identity, projection, rollback, and preservation regression proof.**
   - **Ordered actions:** Add bounded fixtures for case-insensitive setup lookup, missing and ambiguous usernames,
     UUID/corpus mismatch, player participation by color, nested and multiple opening memberships, repeated
     positions and games, route-specific recurrence, parent/child and terminal branches, chronology, results, and
     ratings. Compare every personal fact and projection with deterministic expected S3/S4-derived output. Prove
     usernames are absent from durable references, only skyrocoster is configured, global and membership-inclusive
     counts remain distinct, failures roll back completely, and S1 through S4, corpus, game, player, and unrelated
     rows remain unchanged.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest tests/test_opening_tracked_player.py
     tests/test_opening_recurrence.py tests/test_opening_classification.py -q`, scoped Ruff and format checks,
     source-size checks, deterministic-signature comparisons, foreign-key checks, and injected rollback assertions.
   - **Breakpoint:** None while the approved UUID, neutral-fact, projection, and ownership semantics remain
     unchanged.

4. **failed and restored - authorized runtime publication did not deliver S5 data.**
   - **Actions attempted:** A retained backup and bounded safety checks preceded authorized runtime attempts. The
     first attempt exhausted Python memory while materializing 2,402,576 route events. A later bounded-memory
     attempt was interrupted during a large transaction before successful publication and closeout. The backup was
     restored.
   - **Observed proof:** The restored runtime database retains S1-S4 and corpus 1 for skyrocoster's UUID. It has no
     S5 tables, tracked-player state, personal classification rows, or personal projection rows. No runtime S5
     capability was delivered.
   - **Breakpoint:** Closed by the user's decision to abandon the four copied/materialized S5 projections rather
     than attempt another runtime publication.

5. **cancelled - overall validation and acceptance were not run.**
   - **Closeout:** The runtime outcome could not be validated or accepted because publication failed and the backup
     was restored. Archival records abandonment and preserves historical evidence; it does not signify successful
     acceptance.
   - **Breakpoint:** None. The overall S5 outcome is explicitly not accepted.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the approved outcome or requiring a new human decision.

## Progress and decisions

- **Stage 1:** completed as temporary proof only - focused proof: `8 passed`; scoped Ruff, format, size, and `git diff --check` passed.
  Fresh independent Quality validation passed after proving deterministic current manifest/corpus selection,
  historical and unrelated state isolation, run-metadata independence, selected-fact change detection, UUID-only
  durable identity, full upstream preservation coverage, and strict additive-schema validation.
- **Stage 2:** completed as temporary proof only - focused proof: `13 passed`; scoped Ruff, format, size, and `git diff --check` passed.
  Fresh independent Quality validation confirmed exact personal S3/S4 derivation, deterministic equivalent builds,
  unchanged reruns with stable run identity, changed-input refusal with prior-state preservation, atomic rollback,
  and unchanged upstream facts in temporary SQLite databases.
- **Stage 3:** completed as temporary proof only - focused proof across tracked-player, recurrence, and classification suites: `32 passed`;
  scoped Ruff, format, size, and `git diff --check` passed. Rich temporary fixtures prove both player colors,
  multiple memberships, route and move/terminal branch facts, chronology, result/rating evidence,
  raw-versus-distinct counts, exact fresh S3/S4 equality, refusal, rollback, and upstream preservation.
- **Stage 4:** failed and restored - the user authorized runtime publication with a retained external backup. The
  first importer call resolved identity safely but exhausted Python memory while materializing 2,402,576 route
  events. A later bounded-memory attempt was interrupted during a large transaction before successful publication
  and closeout. The backup was restored. The current runtime database retains S1-S4 and contains no S5 tables,
  personal state, classification, or projection data.
- **Stage 5:** cancelled - independent overall acceptance and successful-delivery closeout were not run. This Plan
  is archived as an abandoned historical record, not as an accepted outcome.
- **Dependency state:** S3 and S4 remain accepted, runtime-published, independently validated, and archived. Corpus
  1 remains owned by skyrocoster's accepted subject UUID.
- **Terminal decision:** The user abandoned the four copied/materialized S5 personal projection tables. Future work
  is to use the existing corpus and S4 facts directly and add only separately settled missing capabilities. The
  identity/schema/derivation work remains temporary proof and no S5 runtime capability is claimed.

## Proof

- Temporary SQLite fixtures cover setup-only username resolution, missing and ambiguous resolution, UUID/corpus
  agreement, player color, classifications, routes and memberships, recurrence and branch projections, chronology,
  results, ratings, deterministic output, version/input refusal, idempotency, rollback, and neutral/upstream
  preservation.
- `.venv\Scripts\python.exe -m pytest tests/test_opening_tracked_player.py
  tests/test_opening_recurrence.py tests/test_opening_classification.py -q`.
- `.venv\Scripts\python.exe -m ruff check scripts/opening_catalog
  tests/test_opening_tracked_player.py`.
- `.venv\Scripts\python.exe -m ruff format --check scripts/opening_catalog
  tests/test_opening_tracked_player.py`.
- `.venv\Scripts\python.exe scripts/check_size.py --source-max 500 --test-max 700`.
- Runtime attempts proved the need for production-scale resource, time, cancellation, interruption, and recovery
  criteria. The first attempt exhausted memory; the later large transaction was interrupted; the retained backup
  was restored. The restored database has no S5 tables or personal projection data, while S1-S4 remain.
- Documentation closeout uses reciprocal-link review, terminal-state review, `git diff --check`, and scoped status
  and diff inspection. It does not convert temporary test evidence into runtime acceptance.

## Acceptance

**Not accepted.** Stages 1 through 3 produced useful temporary implementation and test evidence, but Stage 4 did
not publish a retained runtime projection. The first runtime attempt exhausted memory, the later large transaction
was interrupted, and the backup was restored. Stage 5 was cancelled. The archived location marks this Plan as a
terminal historical record only; it must not be read as successful delivery or acceptance.

## Escalation boundaries

- Any requirement for a literal new `players.id` column instead of the existing stable `players.uuid`, or any new
  numeric, implicit, or alternative player identity.
- Any missing or ambiguous username resolution, UUID/corpus mismatch, username leakage into durable facts, or need
  to change the existing Chess.com configuration or importer ownership.
- Any additional tracked player or new configuration format, source, update workflow, or ownership model.
- Any personal fact that cannot be derived solely from accepted neutral S3 classifications and authoritative S4
  events while retaining exact four-field, natural game/ply, route-membership, color, chronology, result, rating,
  and raw-versus-distinct semantics.
- Any recurrence formula, denominator policy, threshold, recency/rating weighting, branch priority, preferred move,
  adaptive frontier, recommendation, or training decision.
- Any change to accepted S1/S2/S3/S4 facts, corpus or game ownership/completeness, player source rows, source data,
  or existing schema; any destructive migration or replacement.
- Any new API, frontend, authentication, authorization, engine, population integration, dependency, taxonomy
  workflow, `Scratch/` write, historical edit, or unrelated worktree/database change.
- Any uncertain lock, backup, integrity, active-writer, atomicity, rollback, partial-publication, or rerun condition;
  runtime publication without immediate coordinator/user authorization.
- Any need to run `--fix`, suppress unrelated failures, rewrite the failed outcome as accepted, commit, or push.

## Visible result

> S1-S4 and skyrocoster's corpus remain available after restoration, but S5 delivered no retained runtime tables, personal projection data, or user-facing capability; the copied projection approach is abandoned and not accepted.
