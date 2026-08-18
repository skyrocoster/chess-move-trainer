# Static Position to Analysis Workspace - Master Plan

> **Status:** Destination agreed; this document authorizes no implementation. MP-01 through MP-06 are
> accepted. MP-07 through MP-12 remain unselected and require fresh grilling before planning or
> implementation.

## What This Document Is

This master plan records only the destination and sequencing relevant to MP-07 onward. It is a roadmap,
not an implementation Plan, queue, work order, schema, API contract, or authority to change data.

The accepted MP-01 through MP-06 implementation is summarized as the starting baseline below. Its
detailed decisions and delivery evidence remain in the archived Plans under `docs/plans/done/`. The
[grilling record](../grilling-docs/static-position-to-analysis-roadmap.md) is directional evidence for
MP-07 onward, not implementation authority. MP-06's decisions are settled by its
[grilling record](../grilling-docs/mp06-validated-fen-corpus.md) and archived Plan.

Present-tense destination language describes desired behavior unless explicitly identified as current
state. When a milestone is selected, routing must independently decide whether direct delivery or a
focused Plan is appropriate.

## Product Outcome

> A human can progress from the accepted read-only position viewer to stored-game review, backend and
> browser analysis, position editing, and explicit persistence of previously unknown positions.

### Success Means

- **Human can see:** Stored positions and complete games appear safely in the existing workspace, with
  distinct backend and browser analysis states.
- **Human can do:** Traverse a captured game, inspect reusable analysis, evaluate the displayed position,
  and eventually create and explicitly persist an unknown position.
- **The product preserves:** `/` remains the health/status page; malformed positions never silently become
  the starting position; the board remains read-only through MP-10; unfinished features are not exposed.

## Current State

MP-01 through MP-06 were accepted between 2026-08-15 and 2026-08-18. Their archived Plans are the durable
completion records:

- [Verified technology foundation](../plans/done/verified-technology-foundation/verified-technology-foundation.md)
- [Material design foundation](../plans/done/material-design-foundation/material-design-foundation.md)
- [Responsive site shell](../plans/done/responsive-site-shell/responsive-site-shell.md)
- [Safe read-only board adapter](../plans/done/safe-read-only-board-adapter/safe-read-only-board-adapter.md)
- [Integrated static viewer](../plans/done/integrated-static-viewer/integrated-static-viewer.md)
- [Validated FEN corpus](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md)

The resulting fixed baseline is:

- `/` is the health/status page inside the responsive application shell.
- `/viewer` displays the standard starting position through the application-owned, safe read-only board
  adapter; unmatched routes show an in-shell not-found state.
- Material tokens, reusable feedback states, Storybook, component tests, accessibility checks, and browser
  tests support the existing frontend.
- MP-06 extraction owns the version-1 corpus schema (`corpus`, `corpus_game`, `position_state`,
  `position_occurrence`, `corpus_schema`, `corpus_run`) in `data/database/chess_games.db`, identified by
  the subject UUID `0101b08a-ce8b-11ee-b2fd-e90263e5548c`.
- The accepted corpus holds 12,365 games (6,185 as White, 6,180 as Black), 639,262 ordered occurrences
  including ply zero, 510,876 unique position states, four `oddschess` exclusions, and zero replay
  failures.
- `scripts/chess_com/extract_corpus.py` replays and updates the corpus idempotently with atomic
  publication; fetching and extraction remain separate explicit commands.
- No stored-position selection, game traversal, engine analysis, board editing, or user-position
  persistence is present. MP-07 must not assume retrieval APIs or selection contracts; its fresh
  grilling settles them.

## Governing Principles

- Deliver and accept milestones strictly in order: `MP-06 -> MP-07 -> MP-08 -> MP-09 -> MP-10 -> MP-11
  -> MP-12`.
- Complete fresh grilling before focused planning or implementation of each milestone. Milestone names and
  prior directional notes do not settle schemas, APIs, migrations, engines, settings, or interactions.
- Keep third-party behavior behind application-owned boundaries where replacement is credible.
- Treat expected data and operational failures as accessible typed states; contain unexpected render
  failures without replacing the whole application.
- Preserve the board adapter's strict FEN safety contract. Invalid or malformed data never falls back to
  the starting position.
- Keep the board read-only through MP-10. Editing begins only in MP-11; persistence of unknown positions
  begins only in MP-12.
- Require human acceptance after every milestone. Automated accessibility and regression checks support,
  but do not replace, responsive, keyboard, touch, assistive-technology, and human review.

## Destination

```text
Accepted baseline: static read-only viewer and validated FEN corpus
  -> MP-07 arbitrary stored-position display
  -> MP-08 complete-game traversal
  -> MP-09 persisted backend Stockfish analysis
  -> MP-10 browser evaluation
  -> MP-11 browser position editing
  -> MP-12 persist and analyze unknown positions
```

### MP-06 - Validated FEN Corpus

> Create a complete, validated, ordered position corpus for the accepted captured games.

MP-06 is accepted. Its [grilling record](../grilling-docs/mp06-validated-fen-corpus.md) settled the
source and replay oracle, corpus ownership, schema, normalization, duplicate identity, ordered per-game
positions including ply zero, the deduplicated unique index, lossless replayable FEN state, idempotent
reruns, partial-failure recovery, and completeness evidence. The archived
[Validated FEN corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md) is the
durable delivery record; all four human-gated stages shipped and were accepted on 2026-08-18. The
delivered corpus holds 12,365 accepted games, 639,262 ordered occurrences including ply zero, 510,876
unique position states, four `oddschess` exclusions, and zero replay failures. No further MP-06 grilling,
planning, or implementation work remains.

**Boundary:** No viewer integration, traversal, engine analysis, or ungrilled migration/data rewrite.

### MP-07 - Arbitrary Stored-Position Display

> Display any accepted stored FEN through the safe read-only viewer.

Fresh grilling must settle position selection and navigation, frontend/backend ownership, URL versus
application state, and accessible loading, missing, malformed, and recovery behavior.

**Boundary:** No silent starting-position fallback, sequential game traversal, editing, or analysis.

### MP-08 - Complete-Game Traversal

> Reproduce an accepted stored game by traversing its positions in order.

Fresh grilling must reconfirm the fixture and source attribution, then settle the position pointer,
pointer and keyboard controls, visible game context, and initial/final boundary behavior. Traversal changes
only the displayed stored position.

**Boundary:** No stored-data mutation, piece movement, editing, or engine analysis.

### MP-09 - Persisted Backend Stockfish Analysis

> Analyze stored positions in the backend and visibly reuse eligible persisted results.

Fresh grilling must settle engine packaging and invocation, depth and resource limits, MultiPV, result
fields, position/result identity, engine/version/settings invalidation, batching, progress, cancellation,
recovery, persistence schema, and verification.

**Boundary:** No browser engine, unknown-position persistence, or automatic analysis of user-created data.

### MP-10 - Browser Evaluation

> Evaluate the currently displayed read-only position in the browser.

Fresh grilling must select the browser engine and settle loading, resource limits, cancellation, MultiPV,
result ownership and presentation, failure recovery, and whether results are session-only or persisted.

**Boundary:** No editing and no assumption that browser-generated results are durable.

### MP-11 - Browser Position Editing

> Let a human edit a position through an accessible browser interaction model.

Fresh grilling must settle legal versus free-form editing, complete FEN state controls, promotion,
clearing and reset, validation, representation of edited state, and equivalent keyboard, pointer, and
touch interaction.

**Boundary:** No automatic persistence or analysis of unknown positions and no mutation of stored games.

### MP-12 - Persist and Analyze Unknown Positions

> Explicitly record and analyze a previously unknown position so its accepted result can be reused.

Fresh grilling must settle provenance and authorization, identity and normalization, duplicate behavior,
validation and security boundaries, explicit write and analysis triggering, settings, stale-result
handling, reuse, and failure recovery.

**Boundary:** No broader CRUD, authentication, authorization, or automatic persistence policy beyond the
accepted contract.

## Small Visible Slices

Dependencies mean accepted by a human, not merely implemented or green in automation.

| Slice | Requires | Human can see | Human can do | Human gate |
|---|---|---|---|---|
| MP-06 (accepted 2026-08-18) | MP-05 | Complete corpus and replay/completeness evidence | Review extraction, rerun, and recovery proof | Met: source, validity, completeness, and idempotency accepted |
| MP-07 | MP-06 | A selected stored FEN and its loading/failure states | Address or select a stored position safely | Accept representative success, missing, and malformed cases |
| MP-08 | MP-07 | Ordered current, initial, and final game states | Traverse a complete accepted game | Accept pointer, keyboard, context, and boundaries |
| MP-09 | MP-08 | Backend analysis with observable reuse | Request analysis and verify reuse/recovery | Accept identity, invalidation, operations, and persistence |
| MP-10 | MP-09 | Browser evaluation for the displayed position | Start, observe, cancel, and recover evaluation | Accept resource, result, cancellation, and failure behavior |
| MP-11 | MP-10 | Edited and validation states distinct from stored state | Edit, correct, and reset a position | Accept semantics, complete FEN state, keyboard, and touch |
| MP-12 | MP-11 | Durable analysis and reuse for an unknown position | Explicitly persist, analyze, and reuse it | Accept provenance, identity, duplicates, staleness, and failures |

## Cross-Cutting Constraints

- Preserve `/`, the responsive shell, Material semantic styling, and the application-owned board adapter.
- Do not expose controls, props, APIs, schemas, or engine workflows before their milestone settles them.
- Reverify data, fixtures, package metadata, engine feasibility, and operational assumptions when relevant;
  historical notes are not permanent facts.
- Keep backend batch analysis and browser evaluation separately owned unless a later grilled decision
  explicitly defines their relationship.
- Preserve unrelated worktree changes and avoid adjacent refactors not required by the selected outcome.

## Verification Standard

Every selected milestone requires focused automated coverage for its observable behavior and applicable
empty, loading, malformed, missing, interrupted, cancellation, boundary, and recovery states. It must also
include regression proof for `/` and the board safety contract, representative wide and constrained human
review for visual work, keyboard and pointer review, touch review when exposed, and explicit human
acceptance before the next milestone starts.

The selected route must define exact proof commands and representative data. Documentation-impacting work
must pass `.venv\Scripts\python.exe scripts\check_docs.py --check`.

## Open Decisions

All implementation-level decisions for MP-07 through MP-12 remain open until the fresh grilling named in
each milestone; MP-06 decisions are settled by its archived Plan. These gates do not change the agreed
destination or sequence.

## Explicitly Outside This Master Plan

- Implementation, package installation, data migration, focused Plan creation, or work-order authority.
- Replacement of the health page, visual system, shell, router, or safe board boundary.
- Piece movement before MP-11 or unknown-position persistence before MP-12.
- Generic product CRUD, authentication, authorization, notifications, or unrelated operational systems.
- Assumptions that existing game data, schemas, fixtures, engines, or settings are trustworthy without
  milestone-specific verification.

## Provenance

The [static-position to analysis grilling record](../grilling-docs/static-position-to-analysis-roadmap.md)
settled MP-01 through MP-05 and preserved directional envelopes for MP-06 through MP-12. The
[MP-06 grilling record](../grilling-docs/mp06-validated-fen-corpus.md) settled MP-06's contract. Archived
Plans own the accepted implementation history for MP-01 through MP-06. This shortened master plan
supersedes its former duplicated MP-01 through MP-05 descriptions, source inventories, acceptance scripts,
and delivery receipts.
