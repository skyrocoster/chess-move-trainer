# Static Position to Analysis Roadmap — Consolidated Grilling Record

**Recorded:** 2026-08-15  
**Status:** Confirmed design-review evidence  
**Implementation authority:** None  
**Supersedes:** `single-game-viewer.md`, `pgn-to-fen-extraction.md`, and `stockfish-feasibility.md`

## Purpose and document relationship

This record owns the preserved direction and unanswered decisions for MP-06 onward. The
[master plan](../master-plans/static-position-to-analysis.md) owns milestone order, dependencies, and human gates.
Focused Plans may be created only after the applicable later milestone has completed fresh grilling.

## Shipped foundation: MP-01 through MP-05 (Slice 1)

MP-01 through MP-05 replaced the original broad Slice 1 and were implemented and accepted between
2026-08-15 and 2026-08-18. Their archived focused Plans are the detailed delivery receipts:

- [MP-01: verified technology foundation](../plans/done/verified-technology-foundation/verified-technology-foundation.md)
- [MP-02: Material design foundation](../plans/done/material-design-foundation/material-design-foundation.md)
- [MP-03: responsive site shell](../plans/done/responsive-site-shell/responsive-site-shell.md)
- [MP-04: safe read-only board adapter](../plans/done/safe-read-only-board-adapter/safe-read-only-board-adapter.md)
- [MP-05: integrated static viewer](../plans/done/integrated-static-viewer/integrated-static-viewer.md)

Together they delivered a reusable, responsive application foundation that safely displays one static chess
position:

- React Router composes the preserved backend-health page at `/`, the read-only workspace at `/viewer`, and an
  in-shell **Page not found** state. Both pages use the responsive application shell; viewer context remains owned
  by the viewer workspace.
- A fixed dark Material 3 token system, system-font typescale, CSS Modules, focus treatment, shared feedback
  primitives, and selective render-error containment form the visual and feedback foundation.
- The application-owned board adapter is the only production boundary to `react-chessboard`. It accepts strict
  standard FEN, optional orientation and coordinate visibility, and a required contextual label; it is a bounded,
  container-responsive, read-only board with a complete textual position description.
- `chess.js` validates FEN before rendering. Whitespace or invalid input is rejected rather than normalized or
  replaced with a starting position, and invalid input or unexpected board-render failure produces the contained,
  accessible **Position unavailable** state.
- Component tests, Storybook states, browser checks, and human accessibility review established the accepted proof
  surface. Automated accessibility checks supplement rather than replace human review.

The foundation deliberately did not add stored positions, PGN replay, traversal, board movement, highlighting,
analysis arrows, Stockfish, or persistence. The board remains read-only through MP-10, and package capabilities do
not authorize product behavior. Later work should reuse the established shell, workspace, board, styling, feedback,
and testing boundaries rather than recreate them or expose speculative APIs and controls.

The implemented frontend stack is summarized in the [documentation router](../README.md). The accepted visual and
board treatments remain available in the advisory [design guide](../design-guides/static-position-to-analysis.md)
and [MP-04 board reference](../design-guides/mp04-board-adapter-reference.html).

No accepted backend position corpus, extraction workflow, position schema, storage API, PGN parser, Stockfish
integration, or user-position persistence exists yet. Standard FEN is the intended interchange direction, but
MP-06 must independently settle and verify backend validation, source data, schema, ownership, normalization,
failure handling, rerun policy, and proof. Every milestone from MP-06 onward requires fresh grilling before focused
planning or implementation; the envelopes below grant no implementation authority.

## Later milestone envelopes

The following sections preserve direction only. Every unanswered branch remains open until that milestone's grilling.

### MP-07 — arbitrary stored-FEN display

#### Tangible claim

> We can pull any stored FEN into the safe read-only position viewer.

This slice connects persisted positions to the reusable board. It does not allow direct piece movement. Selection UX, APIs, loading states, missing-position behavior, and route/state ownership are unanswered.

### MP-08 — complete-game traversal

#### Tangible claim

> We can walk through stored FENs in order to reproduce a complete game.

Relevant decisions preserved from the superseded single-game-viewer discussion:

- one activation advances or reverses exactly one ply;
- Previous is disabled at the initial position;
- Next is disabled at the final position;
- the initial design had only Previous and Next traversal controls;
- no custom PGN parser or chessboard renderer should be created; and
- safe external attribution to the source game was desired.

Direct board editing remains excluded. Traversal changes which stored position is displayed; it does not mutate a position.

### MP-09 — persisted backend Stockfish analysis

#### Tangible claim

> Backend Stockfish can analyze stored FENs, persist their statistics, and reuse prior results instead of rediscovering them.

This replaces the earlier ambiguous Stockfish direction with an explicit backend milestone. Preserved feasibility evidence includes:

- Stockfish accepts FEN input;
- batch analysis of existing games is feasible on the documented local scale;
- MultiPV Top 3 was previously selected as useful for training context; and
- engine depth, analysis settings, schema identity, invalidation, progress, packaging, and operational workflow were not settled.

All details require MP-09 grilling. In particular, “same FEN” identity, engine/version/settings identity, stale-result handling, analysis fields, and rerun policy must not be inferred from the milestone title.

### MP-10 — browser Stockfish evaluation

#### Tangible claim

> Stockfish can read and evaluate the currently displayed read-only position in the browser.

This is separate from backend batch analysis and persistence. The position remains read-only. Browser engine technology, loading, resource limits, cancellation, MultiPV behavior, result ownership, and whether any browser result is persisted are unanswered.

No policy was selected for browser-generated evaluation persistence. That question belongs to MP-10 grilling and must account for the later unknown-FEN persistence milestone.

### MP-11 — browser position editing

#### Tangible claim

> A user can edit a chess position in the browser.

This milestone is intentionally vague and requires fresh grilling. It is the first milestone that may allow pieces to move independently of traversing a stored game.

Unanswered areas include legal versus free-form editing, side to move, castling and en-passant state, promotion, clearing/resetting, validation, accessibility, and how an edited position is represented.

### MP-12 — persist and analyze unknown FENs

#### Tangible claim

> A previously unknown position can be recorded and analyzed once so its Stockfish result can be reused.

This milestone is intentionally vague and requires fresh grilling. Persistence of user-created positions is not authorized earlier in the roadmap.

Unanswered areas include identity and normalization, provenance, duplicate handling, analysis settings, write API, validation, security boundaries, stale engine results, and whether persistence is automatic or explicitly requested.

## Unanswered-decision tree

MP-07: arbitrary stored-FEN display
├── settle selection and navigation model
├── settle frontend/backend data boundary
├── settle loading, missing, and malformed states
└── settle URL and application-state ownership

MP-08: complete-game traversal
├── reconfirm fixture and source attribution
├── settle control and keyboard behavior
├── settle move/game context displayed around the board
└── settle end states and traversal proof

MP-09: persisted backend Stockfish analysis
├── settle engine packaging and invocation
├── settle depth, MultiPV, limits, and result fields
├── settle analysis-result identity and invalidation
├── settle batch workflow, progress, cancellation, and recovery
└── settle persisted schema and verification

MP-10: browser Stockfish evaluation
├── select browser engine technology
├── settle resource and cancellation behavior
├── settle evaluation presentation
├── settle browser/backend result relationships
└── settle session-only versus persisted results

MP-11: browser position editing
├── settle editing semantics and legality
├── settle complete FEN-state controls
├── settle validation and reset behavior
└── settle accessible interaction

MP-12: persist and analyze unknown FENs
├── settle provenance and authorization boundary
├── settle normalization and duplicate behavior
├── settle write and analysis triggering
└── settle reuse, invalidation, and failure recovery
```

None of these open branches blocks recording the broad roadmap. Each blocks planning or implementing its corresponding later slice.

## Superseded and replaced decisions

This consolidated record intentionally replaces several older framings:

1. **Implementation starting point:** the FEN corpus is not first. Five independently reviewable foundation milestones precede it; the corpus is MP-06.
2. **Viewer scope:** MP-05 displays one static starting position. Complete-game replay is MP-08.
3. **Board interaction:** no current milestone before the later editing slice permits picking up and moving pieces merely to alter a position.
4. **Stockfish environments:** backend and browser Stockfish are not one combined implementation decision. They are separate milestones with separate purposes.
5. **Backend Stockfish purpose:** backend analysis is persisted per position and reused, subject to later grilling of identity and invalidation.
6. **Browser Stockfish purpose:** browser analysis evaluates a displayed read-only position; persistence remains undecided.
7. **Document ownership:** this one record replaces the three narrower grilling documents. The master plan
   references this record rather than absorbing its MP-06 onward detail.

## Repository evidence carried forward

The superseded records documented the following facts, which future assessment must verify before relying on them operationally:

- the frontend is React and TypeScript;
- the repository did not yet have a chess library or chessboard dependency when the earlier records were created;
- captured games retained verbatim PGN;
- the earlier dataset contained 694 games;
- all 694 examined PGNs reportedly included a `CurrentPosition` header suitable as a replay oracle;
- the expected extracted scale was approximately 27,800 positions and small for SQLite;
- the earlier single-game fixture used the standard starting position and contained 44 plies; and
- Stockfish feasibility was considered practical on the documented local hardware.

These are historical repository facts, not permanent contracts. Assessment and each later grilling must retrieve current facts rather than assume they remain unchanged.

## Explicit exclusions from this record

This record does not:

- create a focused Plan or master plan;
- approve any source, dependency, schema, or data edit;
- select exact component names or filesystem paths;
- authorize installation of the selected technology stack before focused planning;
- settle any milestone after MP-05;
- authorize a database migration;
- authorize downloading or packaging Stockfish;
- authorize browser automation or live services;
- authorize implementation, ordering, dispatch, validation, commit, or push; or
- promise that future requirements can never require change.

## Completion rationale

The MP-01 through MP-05 foundation is implemented and accepted. Its durable summary and delivery receipts are
recorded above.

The later milestone frontier is intentionally not opened here. Each later milestone carries an explicit grilling prerequisite and an unanswered-decision branch. This preserves a coherent master-plan direction without pretending that later product behavior has already been designed.

The user explicitly confirmed this consolidated understanding and authorized recording it in detail while atomically deleting the three superseded grilling records.
