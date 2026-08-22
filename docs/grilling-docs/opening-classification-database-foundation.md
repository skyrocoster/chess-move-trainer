# Opening Classification Database Foundation — Confirmed Grilling Synthesis

**Recorded:** 2026-08-21  
**Status:** Confirmed direction and route evidence; one implementation gate remains intentionally open  
**Implementation authority:** None  
**Relationship:** Feeds the [Opening Classification Database Preparation master plan](../master-plans/opening-classification-database-preparation.md). Builds on the [opening position pattern discovery](opening-position-pattern-discovery.md) and the [personal opening classification synthesis](opening-classification-and-progressive-training.md).

## Purpose

This record captures the confirmed decision to prepare backend/database foundations for opening
classification and recurrence. It is historical evidence, not a product specification, schema, focused
Plan, or authorization to edit source code or runtime data.

The approved route is a master plan with five sequential, independently Plan-backed slices. The work is
database-only: no frontend, APIs, engines, population evidence, or training surface is included.

## Confirmed direction

- Use the existing SQLite database at `data/database/chess_games.db` and the five authorized TSV files under
  `Scratch/prototypes/proto-chess-openings-epd-lookup-2026-08-18.data/`.
- Persist all 3,810 opening records with ECO, name, move sequence, exact endpoint position, and source/import
  provenance. The source files are the fixed initial dataset; no live Lichess integration is authorized.
- Keep exact legal positions as the primary identity. The existing database already stores one normalized legal
  position per game and ply: exact-position identity excludes move counters while retaining piece placement,
  side to move, castling rights, and legally relevant en-passant state. Preserve the established ownership and
  integrity expectations for game-derived position rows.
- Derive hierarchy from replayed positions: the deepest earlier named opening is the parent. Keep broad
  families, nested variations, explicit transposition links, and multiple valid memberships.
- Record every exact named opening encountered in each game, including its anchor and provenance, plus the
  complete downstream route facts. Adaptive-frontier membership is deferred.
- Preserve authoritative event-level facts and rebuildable aggregate projections for global and
  opening-route recurrence, parent/child conditional branches, overall and color-specific totals,
  chronology/game sequence, results, and ratings needed by later work. Do not introduce formulas or
  thresholds here.
- Keep neutral opening and game facts independent from player-specific facts.
- Support explicitly tracked players, initially only skyrocoster. Resolve the username only at the setup/import
  boundary, then reference the existing stable player-ID UUID (`players.id` in the approved model) everywhere.
  Do not add or assume a numeric ID and do not rely on SQLite `rowid`.
- Imports and reruns must be atomic, idempotent, change-aware, auditable, and incapable of publishing partial
  classifications.

## Evidence and implementation gate

The authorized source contains 817, 772, 1,250, 614, and 357 records in A–E, respectively, for 3,810 total;
the prototype replayed the records successfully and found distinct endpoint state keys. A bounded current
database check found that 3,021 endpoint keys are not present in the existing game-derived `position_state`
rows. Opening-only endpoint positions must not be inserted as if they were observed in games, and imports must
preserve the correctness of the existing position corpus.
Therefore, the first slice must explicitly settle one of these choices before implementation:

1. a separate opening-owned endpoint identity/reference model; or
2. a compatible extension that preserves the existing game-derived ownership and completeness rules.

This is a planning gate, not permission to choose the model in implementation. No opening-only endpoint may
be inserted as an unowned game-derived position row.

## Approved slice envelope

1. **Source catalog storage and opening-owned endpoint identity/provenance.** Persist the complete source
   catalog and settle the endpoint identity/reference boundary.
2. **Opening hierarchy and transposition relationships.** Build replay-derived parent/child, broad/nested,
   transposition, and multiple-membership facts.
3. **Neutral game classification and downstream route facts.** Record every named opening encountered in a
   game with its anchor, provenance, and downstream route facts, independently of players.
4. **Authoritative recurrence facts and deterministic rebuildable aggregates.** Preserve event facts and derive
   global/route recurrence, branch, color, chronology, result, and rating projections without formulas or
   thresholds.
5. **Tracked-player projection for skyrocoster.** Derive the initial personal projection through the existing
   stable player-ID UUID, with username lookup confined to setup/import.

Each slice has a separate acceptance boundary and must receive its own focused Plan. Slice ordering is
intentional; no parallel implementation is authorized by this record.

## Explicitly deferred or excluded

This direction does not settle or authorize frontend work, APIs, engines, population/live integration,
preferred moves, training history or progression, adaptive-frontier formulas or thresholds, branch-priority
scoring, custom taxonomy or taxonomy editing, taxonomy update/reclassification workflows, additional tracked
players, authentication, generic CRUD, dependency changes, commits, or pushes. The exact endpoint identity
model is deferred only to the first focused slice as described above.
