# Opening Classification Database Preparation

> **Status:** direction settled

This master plan records a broad backend/database destination and its independently selectable slices. It
grants no implementation authority. Focused Plans own implementation details, progress, and proof receipts.

## Destination

> Persist the authorized Lichess opening catalog and prepare exact-position, neutral classification,
> recurrence, route, and initial skyrocoster facts in the existing SQLite database for future calculations,
> without adding a frontend or API.

## Settled direction

- Use `data/database/chess_games.db` and all 3,810 records in the five authorized TSV files under
  `Scratch/prototypes/proto-chess-openings-epd-lookup-2026-08-18.data/`.
- Persist ECO, name, move sequence, exact endpoint position, source provenance, and import-run provenance.
- Exact legal positions remain the primary identity. The existing database already stores one normalized legal
  position per game and ply: exact-position identity excludes move counters while retaining piece placement,
  side to move, castling rights, and legally relevant en-passant state. Preserve the established ownership and
  integrity expectations for game-derived position rows; opening-only positions must not be inserted as if they
  were observed in games.
- Derive the opening hierarchy from replayed positions: deepest earlier named opening as parent, broad families
  and nested variations retained, explicit transposition links, and multiple valid memberships.
- Record every exact named opening encountered in each game, its anchor and provenance, and complete downstream
  route facts. Adaptive-frontier membership is outside this destination.
- Store authoritative event facts and deterministic, rebuildable aggregates for global and opening-route
  recurrence, parent/child conditional branches, overall and color-specific totals, chronology/game sequence,
  results, and ratings needed later. No formulas or thresholds are selected here.
- Keep neutral facts independent from player facts. Support explicit tracked players, initially only skyrocoster;
  resolve the username only at setup/import, then reference the existing stable player-ID UUID (`players.id` in
  the approved model). Do not add or assume a numeric ID or use SQLite `rowid`.
- Imports and reruns are atomic, idempotent, change-aware, and auditable, and never publish partial
  classifications.

## Selectable slices

| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| S1 — Source catalog | All 3,810 authorized opening records and their exact endpoint/provenance facts are inspectable in SQLite without changing existing game-derived position rows. | Existing complete position corpus | Hierarchy, game classification, recurrence, player projections |
| S2 — Relationships | Opening families, nested variations, deepest-earlier parents, transpositions, and multiple memberships are inspectable as replay-derived facts. | S1 | Game classification, personal facts, adaptive frontier |
| S3 — Neutral classification | Every exact named opening reached in accepted games has an anchor, provenance, and downstream route facts independent of any player. | S1, S2, existing game-derived position corpus | Personal recurrence, frontier membership, formulas, training |
| S4 — Facts and aggregates | Authoritative recurrence/branch events and deterministic rebuildable global, route, color, chronology, result, and rating projections agree. | S3 | Thresholds, priority scores, frontier decisions, training history |
| S5 — Tracked-player projection | The initial skyrocoster projection is keyed by the existing stable player-ID UUID, while neutral facts remain unchanged and reusable. | S3, S4 | Other players, username-keyed facts, adaptive frontier, training progression |

## Slice requirements

### S1 — Source catalog storage and opening-owned endpoint identity/provenance

**Outcome:** The complete fixed source catalog is persisted with replayed exact endpoint facts and auditable
source/import provenance.

**Inclusions:** All five TSV files and their 3,810 records; ECO, names, move sequences, exact legal endpoint
positions; source identity and import-run provenance; version/ownership boundaries; atomic, idempotent,
change-aware import behavior; and the explicit choice between a separate opening-owned endpoint identity model
and a compatible extension that preserves existing game-derived position ownership and completeness.

**Exclusions:** Opening relationships, game classification, recurrence projections, player facts, and any
frontend or API surface.

**Focused proof:** Temporary SQLite proof of source counts, legal replay, endpoint identity, provenance,
deterministic output, unchanged rerun behavior, changed-source detection, rollback, and no opening-only rows
masquerading as game-derived position rows;
then bounded inspection of the authorized runtime database.

**Acceptance:** A human can verify all 3,810 records, their endpoint positions and provenance, and can confirm
that failed or repeated imports leave one complete, auditable catalog.

**Escalate if:** The endpoint model cannot be selected without violating existing game-derived position ownership;
a source change requires an unapproved taxonomy update workflow; or a new dependency, API, or data identity is
needed.

### S2 — Opening hierarchy and transposition relationships

**Outcome:** The catalog exposes replay-derived hierarchy and cross-links without reducing valid memberships to
one label.

**Inclusions:** Deepest earlier named opening as parent; broad families; nested variations; explicit
transposition links; and multiple memberships for positions or openings.

**Exclusions:** Classification of captured games, personal tracking, recurrence thresholds, adaptive-frontier
membership, preferred moves, and training.

**Focused proof:** Deterministic fixtures covering parent chains, unnamed continuations, transpositions from
different move orders, broad-plus-nested memberships, and multiple valid memberships.

**Acceptance:** A human can inspect the relationship facts and verify that replay order, not a single label or
move-order shortcut, determines the preserved links.

**Escalate if:** The standard source cannot represent the approved hierarchy, a custom taxonomy or taxonomy
editing is required, or a relationship would require choosing frontier or priority policy.

### S3 — Neutral game classification and downstream route facts

**Outcome:** Every exact named opening encountered in an accepted game is recorded with its anchor,
provenance, and complete downstream route facts, independently of player identity.

**Inclusions:** Replay-based game classification; all encountered named openings; membership anchors and source
provenance; downstream positions/routes reached after each anchor; neutral game and route facts; and atomic
publication with no partial classifications.

**Exclusions:** Player-specific recurrence, adaptive-frontier membership, formulas, thresholds, preferred moves,
training history, engines, and population evidence.

**Focused proof:** Temporary PGN fixtures for nested names, transpositions, multiple memberships, anchors,
downstream routes, and replay failure; deterministic classification comparisons; and completeness checks against
the accepted game-derived position corpus.

**Acceptance:** A human can inspect a game and find every exact named opening it reached, its provenance and
anchor, and all approved downstream route facts, while neutral rows remain present without a tracked player.

**Escalate if:** “Encountered,” anchor, or downstream-route semantics require a frontier or threshold decision,
or a failure can leave any partial classification published.

### S4 — Authoritative recurrence facts and rebuildable aggregates

**Outcome:** Raw event facts remain authoritative and all approved recurrence and branch projections can be
rebuilt deterministically from them.

**Inclusions:** Global and opening-route recurrence; parent/child conditional branch facts; overall and
color-specific totals; chronology and game sequence; results and ratings needed for later calculations; and
rebuild/equality proof between event facts and aggregate projections.

**Exclusions:** Recurrence formulas, thresholds, recency weights, rating weights, priority scores, adaptive
frontier decisions, training progression, and automatic recommendations.

**Focused proof:** Recompute projections from authoritative events in a temporary database and compare exact
results; cover color, chronology, result, rating, route, parent, child, and repeated-game cases; prove atomic
rollback and deterministic rebuilds.

**Acceptance:** A human can inspect both the event facts and their projections, rebuild the projections without
loss of facts, and confirm that no threshold or frontier decision is embedded.

**Escalate if:** A requested aggregate requires a formula, threshold, priority policy, adaptive frontier, or
destructive replacement of authoritative facts.

### S5 — Tracked-player projection for skyrocoster

**Outcome:** Personal classification and recurrence facts are projected for skyrocoster while sharing no
identity with neutral facts and using only the existing stable player-ID UUID.

**Inclusions:** An explicit tracked-player model; setup/import-boundary username resolution; initial
skyrocoster configuration; UUID references through the approved existing player ID; and personal projections
derived from neutral facts and approved recurrence events.

**Exclusions:** Username strings as fact references, numeric IDs, SQLite `rowid`, additional initial players,
adaptive-frontier membership, formulas, thresholds, priority scores, preferred moves, and training progression.

**Focused proof:** Temporary fixtures proving setup-only username lookup, stable UUID references, neutral-fact
independence, skyrocoster-only initial projection, rerun idempotency, and failure rollback.

**Acceptance:** A human can verify skyrocoster’s personal projection by stable UUID, confirm that neutral
classifications remain independent, and confirm that no username or implicit numeric row identifier is used as
the durable reference.

**Escalate if:** The existing stable player-ID UUID cannot be referenced consistently, username lookup must
leak into durable facts, or personal projection requires frontier, priority, training, or additional-player
decisions.

## Slice results

- **S1:** Focused Plan to be created only after this master plan is selected.
- **S2:** Focused Plan to be created after S1 is accepted.
- **S3:** Focused Plan to be created after S1 and S2 are accepted.
- **S4:** Focused Plan to be created after S3 is accepted.
- **S5:** Focused Plan to be created after S3 and S4 are accepted.

## Overall acceptance

All five slices are independently accepted in order. The final database contains the complete authorized
catalog, exact endpoint identity and provenance, replay-derived relationships, neutral classifications and
downstream routes, authoritative event facts, matching rebuildable aggregates, and the skyrocoster projection.
Atomic failure, unchanged rerun, source-change, audit, and no-partial-classification proofs pass. The existing
game-derived position corpus remains complete, correct, and ownership-safe. No frontend files, APIs, engines,
live population integration, or training data are added.

## Exclusions

- Frontend, API, viewer, authentication, authorization, and generic CRUD work.
- Engines, Stockfish, population evidence, external live integration, or automatic recommendations.
- Preferred moves, training history, training progression, adaptive frontiers, frontier formulas, thresholds,
  recency/rating weighting formulas, and branch-priority scoring.
- Custom taxonomy, taxonomy editing, taxonomy updates, and reclassification workflows.
- Adding or assuming numeric player IDs or relying on SQLite `rowid`.
- Changes to completed historical Plans or unrelated worktree files.
