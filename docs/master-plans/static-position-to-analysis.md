# Static Position to Analysis Workspace - Master Plan

> **Status:** Destination agreed; this document authorizes no implementation. MP-01 (verified technology
> foundation) is accepted 2026-08-15 and archived to `docs/plans/done/verified-technology-foundation/`;
> MP-02 (Material design tokens and reusable UI primitives) is accepted 2026-08-16 and archived to
> `docs/plans/done/material-design-foundation/`; MP-03 through MP-05 remain unselected, but their
> destination boundaries are settled by the grilling record; MP-06 onward remain unselected and ungrilled.
> Selecting a milestone still requires `to-plan`, which independently decides whether direct delivery or a
> focused Plan is appropriate.

## What This Document Is

This document records the broad product destination and the strict sequence of independently
reviewable human outcomes for Chess Move Trainer. It is a lightweight roadmap, not an implementation
Plan, queue, work order, or authority to install packages or change the application.

The detailed [static-position to analysis grilling record](../grilling-docs/static-position-to-analysis-roadmap.md)
owns the confirmed technology decisions, the boundaries of MP-01 through MP-05, and the detailed
direction and unanswered-decision trees for MP-06 onward. This master plan preserves the destination,
dependencies, exclusions, human gates, and stop conditions without reproducing that rationale.

Present-tense language in the destination sections describes desired behavior, not shipped behavior.
Current behavior is stated only in **Current State**. Implementation status belongs in
`docs/plans/active/`; delivery receipts belong here only after reconciliation. A focused Plan may
refine one milestone, but it must preserve the milestone boundary, strict dependency sequence, and
fresh-grilling gates recorded here.

## Why This Change Exists

Before MP-01, the frontend was a backend-health status page rather than a chess workspace, with no
selected chess dependencies, Storybook surface, or layered accessibility proof. MP-01 now supplies the
verified component-development foundation while production remains status-only; the product foundation
still needs to be built through small, independently acceptable milestones.

The destination progresses from verified component-development technology, through Material primitives,
the responsive shell, a safe board adapter, and their integrated static viewer. Only after that
foundation is accepted does it add stored positions, traversal, backend analysis, browser analysis,
editing, and persistence. This sequence prevents a temporary compatibility harness from becoming
production UI and prevents speculative controls or unfinished analysis behavior from appearing early.

## Product Outcome

> A human can move from a verified, accessible static-position workspace to reviewing stored games and
> sequential engine analysis, with user-created positions introduced only after their editing and
> persistence rules have been deliberately designed.

### Success Means

- **Human can see:** The application grows from a verified component-development foundation into a
  coherent accessible workspace with a static board, stored-game traversal, and separate backend and
  browser analysis surfaces.
- **Human can do:** Review the foundation in its development surface, use the accepted static viewer,
  inspect stored positions, traverse games, request or inspect the applicable analysis, and eventually
  create, persist, and reuse a position through separately accepted milestones.
- **The product preserves:** `/` remains the backend-health page after MP-03 adopts the shell;
  malformed positions never silently become the starting position; the board remains read-only through
  MP-10; and unimplemented features are not presented as working controls.

## Governing Principles

- Deliver milestones in the strict order
  `MP-01 → MP-02 → MP-03 → MP-04 → MP-05 → MP-06 → MP-07 → MP-08 → MP-09 → MP-10 → MP-11 → MP-12`.
- A milestone is independently judgeable by a human. Internal setup is acceptable for MP-01 only
  because its temporary Foundation Check is itself the human-reviewable compatibility outcome.
- Preserve the existing `/` status behavior. MP-01 must not change production `/`; MP-03 adopts the
  shell on `/` without changing the status purpose or its success/failure behavior.
- Keep third-party behavior behind application-owned boundaries where replacement is credible. Package
  capability does not authorize product capability.
- Keep application appearance in Material semantic tokens and CSS Modules. Do not scatter literal
  colors, add inline application CSS, or create a second visual implementation in Storybook.
- Use native CSS media queries for shell viewport transitions and CSS container queries for reusable
  workspace reflow. Do not use JavaScript resize state for ordinary layout switching.
- Use React component state and context for the confirmed foundation; do not add a global state library
  without a later real ownership decision.
- Expected product failures are typed UI states; unexpected render failures use selective
  `react-error-boundary` containment.
- Keep the board read-only through MP-10. Movement/editing begins only at MP-11 and does not follow
  merely from a rendering dependency supporting drag-and-drop.
- Require fresh grilling before focused planning or implementation of every milestone from MP-06
  onward. Do not infer schemas, APIs, engine settings, storage policy, or interaction details from a
  milestone name or an older record.
- Automated accessibility checks supplement keyboard, responsive, assistive-technology, and human
  review; they never replace WCAG 2.2 AA acceptance.

## Current State

The following are verified repository facts after MP-01 acceptance on 2026-08-15 and MP-02 acceptance
on 2026-08-16:

- The archived Plan at `docs/plans/done/verified-technology-foundation/verified-technology-foundation.md:3,49-65`
  records all 13 ordered stages shipped and MP-01 accepted. Its receipt remains the durable completion
  record; this master plan records the current implementation evidence and milestone relationship.
- `frontend/package.json:9-54` contains the selected exact runtime packages, Storybook configuration,
  accessibility tooling, and `storybook`, `build-storybook`, and `test-storybook` scripts.
- `frontend/src/features/foundation/FoundationCheck.tsx:1-135` exercises global CSS, CSS Modules, router
  context, Base UI, Lucide, chess.js valid/invalid FEN handling, safe static react-chessboard rendering,
  and react-error-boundary containment.
- `frontend/src/features/foundation/FoundationCheck.test.tsx:16-35` provides the component-level axe proof;
  `FoundationCheck.stories.tsx:17-59` provides Storybook states and interaction proofs.
- `frontend/.storybook/main.ts:3-10` and `preview.tsx:1-4` configure the Storybook Vite surface and shared
  application CSS.
- `tests/e2e/foundation-accessibility.spec.ts:8-34` provides the browser axe proof, and
  `tests/e2e/playwright.config.ts:7-25` starts the Storybook server alongside the existing application
  servers for that proof.
- `frontend/src/App.tsx:1-4` still renders only `StatusPage`; production has no router, shell, viewer, or
  board. `frontend/src/features/status/StatusPage.tsx:7-39` still owns the health loading, success, and
  accessible failure states.
- Existing automated coverage still includes the status/health tests in
  `frontend/src/features/status/StatusPage.test.tsx`, `tests/e2e/status.spec.ts`, and
  `backend/tests/features/health/test_health.py`.
- The full local check passed during the assessment, including documentation, frontend tests, lint,
  build, source-size, and end-to-end checks.
- `frontend/src/app.css:1-28` remains the existing global stylesheet for the unchanged production status
  page; the shell, board adapter, and viewer remain later milestones.
- `backend/app/main.py:7-17` creates the FastAPI app and includes only the health router.
- The worktree contains captured-game data paths, including `data/database/chess_games.db`, but their
  contracts and ownership are not assumed by this destination; MP-06 must verify them.
- The archived Plan at `docs/plans/done/material-design-foundation/material-design-foundation.md` records
  MP-02 stages 1-9 shipped and independently validated; its Shipped table records each stage's outcome.
- `frontend/src/styles/material/material-theme-provenance.json` records the fixed dark Material 3 scheme,
  seed `#3F51B5`, Tonal Spot, and standard contrast, with hash-verified archive and runtime members; only
  the extracted `css/dark.css` member is imported into Storybook.
- `frontend/src/styles/cmt-tokens.css` and `frontend/src/styles/cmt-typescale.css` carry the
  application-owned `--cmt-*` feedback/foundation tokens and the complete `--md-sys-typescale-*` system-ui
  roles.
- `frontend/src/features/design-system/feedback/` ships the shared `FeedbackCore` plus the
  `InlineFeedback`, `PanelFeedback`, and `PageFeedback` wrappers and `feedbackTypes.ts`.
- `frontend/src/features/design-system/` ships the `TokenOverview`, `TypescaleSpecimen`,
  `FoundationSpecimen`, `CombinedComposition`, and `AccessibilityReview` Storybook stories with focused
  tests; `tests/e2e/design-system-accessibility.spec.ts` provides the verification-only browser axe proof.
- Production `/` remains visually and structurally unchanged because MP-02 is Storybook-only; the
  temporary MP-01 Foundation Check remains in place until MP-05.
- This file is the master-plan artifact being revised. The detailed grilling record's older statements
  about the pre-MP-01 repository are historical metadata and are not current-state evidence.

The current production composition is intentionally small:

```text
+---------------- current / ----------------+
| Chess Move Trainer                         |
| Backend connected and healthy              |
| or Backend unavailable: <message>          |
+--------------------------------------------+
```

The current frontend toolchain baseline that MP-01 must preserve is React `19.0.0`, React DOM
`19.0.0`, TypeScript `5.7.3`, Vite `6.0.11`, and Node `>=22 <23`.

## Destination

The desired destination is a strict sequence, not one screen exposing every future capability at
once:

```text
MP-01  verified technology foundation
  -> MP-02  Material tokens and reusable UI primitives
  -> MP-03  responsive site shell
  -> MP-04  safe read-only board adapter
  -> MP-05  integrated static viewer
  -> MP-06  validated FEN corpus
  -> MP-07  arbitrary stored-position display
  -> MP-08  complete-game traversal
  -> MP-09  persisted backend Stockfish analysis
  -> MP-10 browser Stockfish evaluation
  -> MP-11 browser position editing
  -> MP-12 persist and analyze unknown positions
```

The first five milestones replace the former single broad static-foundation envelope. The later
renumbering is:

```text
former broad static-foundation envelope -> MP-01 through MP-05
former validated FEN corpus             -> MP-06
former arbitrary stored-position display -> MP-07
former complete-game traversal          -> MP-08
former persisted backend analysis       -> MP-09
former browser evaluation               -> MP-10
former browser position editing         -> MP-11
former unknown-position persistence     -> MP-12
```

### MP-01 - Verified Technology Foundation

**Desired tangible claim:**

> We created and verified the application's component-development technology foundation.

MP-01 installs and configures the selected production and development stack and proves compatibility
through a temporary development-only Storybook **Foundation Check**. It is a harness for compatibility
and toolchain proof, not production UI, the final token system, the shell, the board adapter, the viewer,
or the shared error architecture.

The confirmed selected runtime and foundation packages are:

- `react-router-dom` `7.18.2` for route composition;
- `react-chessboard` `5.12.0` behind an application-owned adapter;
- `chess.js` `1.4.0` for FEN validation and position inspection;
- `@base-ui/react` `1.7.0` for selected accessible structural behavior;
- `lucide-react` `1.31.0` for local semantic icons; and
- `react-error-boundary` `6.1.3` for selective unexpected-render-failure containment.

The development and proof stack includes Storybook `10.5.8` with `@storybook/react-vite`,
`@chialab/vitest-axe` `0.19.1`, `@axe-core/playwright` `4.13.0`, and only the Storybook accessibility
and workflow integrations required by the accepted proof. Exact pins and compatibility must be
rechecked immediately before installation, but a different technology must not be substituted silently.

The Foundation Check exercises, at minimum:

- shared global CSS loading;
- CSS Modules;
- a Lucide icon;
- a Base UI structural primitive;
- React Router context;
- `chess.js` validation of one known valid and one known invalid FEN;
- `react-chessboard` rendering of a safe static position; and
- `react-error-boundary` containment of a deliberately exercised render failure.

MP-01 also proves that the Storybook and layered accessibility toolchains build and execute. It uses
the same committed CSS and future application-owned boundaries rather than publishing a parallel
component API.

MP-01 must not:

- change the existing `/` page or its styling;
- create `/viewer` or production route composition;
- establish the final Material palette, typescale, shell, board adapter, or shared error architecture;
- expose the Foundation Check as reusable product UI;
- enable movement, legal interaction, PGN parsing, stored data, Stockfish, or persistence; or
- begin MP-02 in the same milestone.

The Foundation Check is temporary. MP-05 must remove it after real stories and consumers replace every
compatibility proof it provided; it must not remain as a duplicate diagnostics page that can drift from
production components.

### MP-02 - Material Design Tokens and Reusable UI Primitives

**Desired tangible claim:**

> We created the reusable visual and feedback language for the application.

MP-02 owns the official Material Theme Builder export, its recorded source seed and generation
settings, semantic dark color variables, system-font typescale variables, and the common spacing,
shape, elevation, and focus decisions required by real consumers. It also owns reusable inline,
panel-level, and page-level feedback presentations with shared semantic structure and accessibility
treatment.

Storybook is the human-reviewable surface for these primitives. Stories cover real token and feedback
states rather than inventing a second application. The fixed dark theme is implemented; theme readiness
does not create a light theme or switcher.

MP-02 does not apply the site shell, create production routes, create the board adapter, or add
position behavior. It consumes MP-01's verified toolchain and leaves the existing `/` composition
unchanged until MP-03.

### MP-03 - Responsive Site Shell

**Desired tangible claim:**

> We created a reusable responsive application shell and adopted it on the existing status page.

MP-03 owns the text-only identity **Chess Move Trainer**, real-destination navigation, desktop top and
left regions, main-content boundary, responsive shell media queries, and narrow-screen drawer behavior.
The drawer uses the selected Base UI structural primitive for opening, focus containment, dismissal,
focus restoration, and keyboard behavior. Icons are local Lucide imports with accessible names on
icon-only controls.

Desktop shows a top bar and visible left sidebar. On narrow screens the left navigation becomes a real
menu drawer. Navigation contains only destinations that exist; it does not show disabled future links.

MP-03 adopts the shell on `/` and preserves the current status page's purpose, loading, healthy, and
unavailable behavior. It does not create `/viewer`, a board, or a viewer-owned contextual panel. The shell
consumes the already-shipped MP-02 visual language — `--md-sys-*` roles, `--cmt-*` foundation tokens, and
the `system-ui` typescale in `frontend/src/styles/cmt-tokens.css` and `cmt-typescale.css` — rather than
reauthoring shell styling; any shell-level feedback reuses the shipped MP-02 feedback primitives.

Desired shell composition:

```text
Wide:
+----------------------------------------------------------------+
| Chess Move Trainer                         [real destinations] |
+------------------+---------------------------------------------+
| navigation        | existing status page                        |
| real links        | Backend connected and healthy               |
+------------------+---------------------------------------------+

Constrained:
+--------------------------------+
| Chess Move Trainer        [≡] |
+--------------------------------+
| status page content            |
| drawer opens with focus       |
+--------------------------------+
```

### MP-04 - Safe Read-Only Board Adapter

**Desired tangible claim:**

> We created a reusable component that safely displays a chess position.

MP-04 places `react-chessboard` behind an application-owned adapter. The adapter owns the application
contract for accepted FEN input, validation before rendering, read-only configuration, orientation,
coordinate visibility, bounded fluid sizing, accessible label and textual position description, and
contained **Position unavailable** handling. Consumers do not import the package directly and
package-specific state does not escape the adapter.

`chess.js` validates and inspects positions. Invalid input never silently becomes the standard starting
position. `react-chessboard` remains a rendering dependency; its movement, highlighting, arrows,
drag-and-drop, and event capabilities are not exposed. Theme values passed to it originate in MP-02's
semantic token contract, and the contained **Position unavailable** state reuses the shipped MP-02
`PanelFeedback`/`PageFeedback` primitives.

Storybook proves the valid starting-position and invalid-position states, orientation and coordinate
configurations actually supported by the adapter, and relevant accessibility descriptions. MP-04 does
not create `/viewer`, traverse positions, move pieces, parse PGN, access stored data, or run Stockfish.

### MP-05 - Integrated Static Viewer

**Desired tangible claim:**

> We created a page that safely displays one position inside the reusable application workspace.

MP-05 owns production React Router composition, durable `/viewer`, the viewer workspace, and the
viewer-owned context region. It integrates the MP-04 adapter with the standard starting position and
preserves `/`. The viewer workspace adopts the shipped MP-02 tokens, typescale, and feedback primitives
for its own structural and feedback presentation.

The viewer workspace lives inside the shell's main-content region and owns both the primary board area
and its contextual panel. On desktop the intentionally empty context panel remains visible for
composition review. On constrained layouts context stacks below primary content, and an empty context
region is omitted rather than consuming vertical space.

Desired viewer composition:

```text
Wide:
+----------------------------------------------------------------+
| Chess Move Trainer                         [Viewer]            |
+------------------+---------------------------------------------+
| site navigation   | viewer workspace                            |
|                   | +----------------------+------------------+ |
|                   | | read-only starting  | intentionally    | |
|                   | | position board     | empty context   | |
|                   | +----------------------+------------------+ |
+------------------+---------------------------------------------+

Constrained:
+--------------------------------+
| Chess Move Trainer        [≡] |
+--------------------------------+
| viewer                         |
| +----------------------------+ |
| | read-only starting board  | |
| +----------------------------+ |
| (empty context omitted)        |
+--------------------------------+
```

At MP-05 acceptance, real shell, primitive, board, error, router, and viewer stories or consumers
must replace every Foundation Check compatibility proof. The temporary MP-01 harness is removed as a
required part of MP-05; it is not retained as a second product surface.

MP-05 does not connect stored data, traverse games, permit piece movement, highlight squares, draw
arrows, run Stockfish, or persist a position.

### MP-06 - Validated FEN Corpus

**Desired tangible claim:**

> We created a complete, validated list of chess positions for the captured games and stored it properly.

MP-06 is the first deliberately ungrilled milestone. Its grilling must confirm the current source and
replay oracle, schema and ownership, normalization and duplicate identity, idempotency and partial
failure behavior, reruns, and observable completeness proof.

Directional inputs preserved for grilling include ordered per-game positions, a derived deduplicated
unique-position index, ply zero, `python-chess`, a separate idempotent extraction step, first-run
backfill, lossless replayable per-game FENs, and preservation of board state, side to move, castling,
and en-passant state. These inputs are not implementation authority before MP-06 grilling.

MP-06 does not connect the corpus to the viewer or authorize a schema, migration, or data rewrite before
its gate is complete.

### MP-07 - Arbitrary Stored-Position Display

**Desired tangible claim:**

> We can pull any stored FEN into the safe read-only position viewer.

MP-07 connects an accepted stored position to the MP-04 adapter. Its grilling must settle selection and
navigation, frontend/backend data boundaries, loading and missing-position behavior, malformed data,
and URL/application-state ownership.

Direct piece movement remains excluded. MP-07 does not infer a traversal model from the presence of
multiple stored positions.

### MP-08 - Complete-Game Traversal

**Desired tangible claim:**

> We can walk through stored FENs in order to reproduce a complete game.

MP-08's grilling must reconfirm the fixture and source attribution and settle the control and keyboard
model, displayed game context, boundary states, and traversal proof. Earlier directional evidence
included one-ply Previous/Next behavior with Previous disabled initially and Next disabled finally, but
that evidence remains subject to the MP-08 gate.

Traversal changes which stored position is displayed; it does not mutate a position or permit board
editing.

### MP-09 - Persisted Backend Stockfish Analysis

**Desired tangible claim:**

> Backend Stockfish can analyze stored FENs, persist their statistics, and reuse prior results instead of
> rediscovering them.

MP-09's grilling must settle engine packaging and invocation, depth, MultiPV, limits and result fields,
position/result identity, engine/version/settings identity, stale-result invalidation, batch workflow,
progress, cancellation, recovery, persisted schema, and verification. No engine download or packaging
is authorized merely by this envelope.

### MP-10 - Browser Stockfish Evaluation

**Desired tangible claim:**

> Stockfish can read and evaluate the currently displayed read-only position in the browser.

MP-10 is separate from MP-09's backend batch analysis and persistence. Its grilling must select browser
engine technology and settle loading, resource limits, cancellation, MultiPV, result ownership,
presentation, and session-only versus persisted browser results.

The position remains read-only. MP-10 does not authorize an editing interaction or infer a policy for
persisting browser-generated evaluation.

### MP-11 - Browser Position Editing

**Desired tangible claim:**

> A human can edit a chess position in the browser.

MP-11 requires fresh grilling. The gate must settle legal versus free-form editing, side to move,
castling and en-passant state, promotion, clearing and reset, validation, accessibility, and the
representation of an edited position.

This is the first milestone that may allow pieces to move independently of traversing a stored game.
It does not authorize persistence or analysis of an unknown position.

### MP-12 - Persist and Analyze Unknown Positions

**Desired tangible claim:**

> A previously unknown position can be recorded and analyzed once so its Stockfish result can be reused.

MP-12 requires fresh grilling. Its gate must settle provenance and authorization, identity and
normalization, duplicate behavior, write and analysis triggering, validation and security boundaries,
analysis settings, stale results, explicit-versus-automatic persistence, and failure recovery.

Persistence of user-created positions is not authorized before MP-12.

## Cross-Cutting Constraints

- The [grilling record](../grilling-docs/static-position-to-analysis-roadmap.md) is the detailed
  technology reference for MP-01 through MP-05 and the directional reference for MP-06 through MP-12.
  It explicitly states that MP-06 onward requires fresh grilling and is not implementation authority.
- The selected React, TypeScript, Vite, and Node baseline remains unchanged by MP-01. A package pin
  must be checked immediately before installation but may not be silently replaced with a different
  technology or a toolchain upgrade.
- MP-01 has no production `/` change, no `/viewer`, and no final product components. MP-03 is the first
  milestone that changes the production status page's structural presentation, and it must preserve its
  behavior.
- Storybook stories reuse committed Material tokens and CSS Modules. Storybook is not a second
  implementation of product components and the Foundation Check is removed by MP-05.
- The shell is site-wide. A viewer-specific context panel belongs inside the viewer workspace, not in
  the global shell.
- Board safety takes precedence over visual plausibility: invalid input is an accessible unavailable
  state, never an automatic starting-position fallback.
- The board remains read-only through MP-10. Mutation begins only at MP-11.
- No milestone may expose a control, public prop, API, schema, or engine workflow before that behavior
  is settled and its milestone is selected.
- Human acceptance is required after every milestone. Automated checks provide regression evidence but
  do not replace human review.
- Current data, historical game counts, fixtures, package metadata, engine feasibility, and operational
  assumptions must be reverified at the applicable milestone rather than inherited as permanent facts.
- Unrelated worktree changes remain outside every milestone's scope.

## Small Visible Slices

Each row is a destination milestone, not implementation status. Dependencies mean “accepted by a
human,” not merely merged or green in automation.

| Slice | Requires accepted | Human can see | Human can do | Explicit boundary | Human gate |
|---|---|---|---|---|---|
| MP-01 | - | A temporary Storybook Foundation Check visibly proves the selected stack and layered toolchain. | Open/run the check and inspect each valid, invalid, structural, and failure state. | No production `/` change, product UI, viewer, final primitives, shell, adapter, data, movement, or engine. | Confirm the harness, Storybook build, accessibility layers, baseline checks, and unchanged `/`. |
| MP-02 | MP-01 | Material tokens and reusable feedback primitives appear in reviewable Storybook states. | Inspect token/state variants and keyboard/focus feedback behavior. | No shell, route, board adapter, or production routing change. | Review dark semantic roles, typography, states, focus, and contrast at the primitive layer. |
| MP-03 | MP-02 | `/` has the reusable desktop shell and narrow-screen navigation transformation. | Navigate the existing status page and open, dismiss, and restore focus from the drawer. | No `/viewer`, board, or viewer context panel. | Confirm status behavior, wide/constrained shell, keyboard, pointer, and accessibility behavior. |
| MP-04 | MP-03 | Valid and invalid FEN states render through one safe read-only board adapter. | Inspect supported orientation/coordinate configurations and the unavailable state. | No `/viewer`, stored data, traversal, movement, or Stockfish. | Verify validation, containment, accessibility, sizing, and package isolation. |
| MP-05 | MP-04 | `/viewer` shows one safe starting position inside the reusable workspace. | Open `/viewer`, use the shell, and inspect the read-only board at wide and constrained sizes. | No stored data, traversal, movement, analysis, persistence, or retained Foundation Check. | Confirm viewer composition, `/` preservation, safety, accessibility, and Foundation Check retirement. |
| MP-06 | MP-05 | A complete validated corpus and replay/completeness evidence are available. | Run or review the accepted corpus workflow and verify rerun/failure proof. | No viewer integration or ungrilled schema/storage policy. | Confirm source, replay, completeness, idempotency, and failure evidence. |
| MP-07 | MP-06 | Any accepted stored FEN appears in the safe read-only viewer. | Select or address a stored position and observe loading, success, missing, and malformed states. | No game traversal or editing. | Display representative positions and verify safe missing/malformed handling. |
| MP-08 | MP-07 | A stored game has clear ordered current, initial, and final states. | Advance and reverse through the accepted traversal workflow. | No board mutation or engine analysis. | Traverse the accepted fixture with pointer and keyboard paths. |
| MP-09 | MP-08 | A stored position has reviewable backend analysis and an observable reuse result. | Use the accepted backend analysis workflow and repeat it under the accepted identity policy. | No browser engine or unknown-position persistence. | Verify reuse, invalidation, operational states, and recovery. |
| MP-10 | MP-09 | The displayed read-only position has browser evaluation feedback. | Start, observe, and cancel or recover from the accepted browser evaluation workflow. | No piece editing or assumed browser-result persistence. | Verify resource, loading, cancellation, failure, and result behavior. |
| MP-11 | MP-10 | The workspace distinguishes an edited position and its accepted validation state. | Edit and reset/correct a position through the grilled accessible interaction model. | No automatic persistence or analysis of unknown positions. | Verify editing semantics, complete FEN state, keyboard, touch, and validation. |
| MP-12 | MP-11 | An unknown position has durable accepted analysis and a visible reuse result. | Explicitly persist, analyze, and reuse it under the grilled policy. | No broader CRUD, authorization, or provenance beyond the accepted contract. | Verify identity, provenance, duplicates, stale results, and failures. |

## Slice Delivery Receipts

| Slice | State | Evidence |
|---|---|---|
| MP-01 | Accepted 2026-08-15 | Archived Plan at `docs/plans/done/verified-technology-foundation/verified-technology-foundation.md` records all 13 shipped stages; implementation evidence is in `frontend/src/features/foundation/`, `frontend/.storybook/`, and `tests/e2e/foundation-accessibility.spec.ts`; the full local check passed and production `/` remains unchanged because MP-01 is development-only. |
| MP-02 | Accepted 2026-08-16 | Archived Plan at `docs/plans/done/material-design-foundation/material-design-foundation.md` records all 9 shipped stages; implementation evidence is in `frontend/src/styles/`, `frontend/src/features/design-system/`, and `tests/e2e/design-system-accessibility.spec.ts`; production `/` remains visually and structurally unchanged because MP-02 is Storybook-only. |

## MP-01 - Verified Technology Foundation

**Human can see**

> A temporary Storybook Foundation Check visibly exercises the selected application technology and
> accessibility toolchains without presenting itself as production UI.

**Human can do**

> A developer can start or build Storybook, inspect every Foundation Check state, and verify that the
> existing production `/` behavior remains unchanged.

**Before**

```text
frontend/
  package.json       React + Vite + Vitest baseline only
  src/App.tsx        StatusPage only
  no .storybook/     no stories

production /         health status page
```

**After**

```text
development-only Storybook Foundation Check
+------------------------------------------------------+
| global CSS + CSS Module                              |
| Lucide icon + Base UI structural primitive           |
| React Router context                                 |
| valid FEN -> safe board                             |
| invalid FEN -> unavailable proof                    |
| deliberate render failure -> contained fallback     |
| Storybook/axe + Vitest/axe + browser axe toolchain  |
+------------------------------------------------------+

production /         unchanged health status page
```

**Included**

- Exact selected dependency families and pinned versions recorded by the grilling record, subject to
  immediate package-metadata verification before installation.
- Package scripts and lockfile updates required to build, run, test, and accessibility-check the
  development foundation.
- Storybook configuration using the selected Vite framework and only required integrations.
- A temporary Foundation Check that exercises global CSS, CSS Modules, Lucide, Base UI, router context,
  valid/invalid `chess.js` FEN handling, safe `react-chessboard` rendering, and deliberate
  `react-error-boundary` containment.
- Sufficient Storybook, component-level axe, and browser axe configuration to prove that the selected
  toolchains build and execute at their intended layers.
- Explicit development-only ownership and a removal condition tied to MP-05.

**Explicitly excluded**

- Any change to production `/`, its styling, its status behavior, or its existing acceptance surface.
- `/viewer`, production route composition, final Material tokens, typescale, shell, board adapter,
  shared error architecture, and reusable product components.
- Board movement, legal-move interaction, PGN, stored data, Stockfish, persistence, and speculative
  application APIs.
- Retaining the compatibility harness after MP-05.

**Prerequisite**

None. MP-01 was accepted on 2026-08-15 as the first independently valuable milestone. Its completed
implementation and stage evidence are recorded in the archived Plan named above; this master plan does
not authorize implementation or replace that receipt.

**Human acceptance script**

1. Start the temporary Storybook surface and confirm its development-only label and available states.
2. Open the Foundation Check and confirm shared global CSS and CSS Modules are loaded.
3. Confirm a Lucide icon and a Base UI structural primitive render with the expected accessible names
   and behavior.
4. Confirm router context is available without changing production route composition.
5. Exercise one valid FEN and confirm a safe static board renders; exercise one invalid FEN and confirm
   the proof distinguishes it from the starting position.
6. Deliberately exercise the render-failure path and confirm the error boundary contains it.
7. Run the selected Storybook/axe, Vitest/axe, and browser-axe proof paths and inspect failures rather
   than treating automated results as complete WCAG proof.
8. Open `/` through the existing browser path and confirm its health success and unavailable states are
   unchanged.

**Automated gate**

- Package installation resolves the selected exact versions on the existing React/TypeScript/Vite/
  Node baseline without an unrelated toolchain upgrade.
- Storybook development and static-build commands succeed.
- Focused component tests and `@chialab/vitest-axe` checks cover the Foundation Check states.
- Storybook accessibility checks and the `@axe-core/playwright` browser proof execute at their intended
  layers.
- Existing frontend tests, the existing `/` Playwright tests, lint, and build remain green.
- The documentation checker passes after any documentation-only change.

**Stop condition**

> Stop when the selected stack and proof layers are verified, production `/` is unchanged, and the
> human accepts the Foundation Check. Do not begin MP-02 in the same milestone.

## MP-02 - Material Design Tokens and Reusable UI Primitives

**Human can see**

> Storybook shows the accepted dark Material semantic roles, system-font typescale, and reusable
> feedback states in coherent reviewable compositions.

**Human can do**

> A reviewer can inspect the primitive states, focus treatment, and representative contrast behavior
> without entering a product workflow.

**Before / After**

```text
Before: MP-01 compatibility harness only

After: Storybook
+------------------------------------------------+
| semantic dark roles and typescale              |
| inline feedback | panel feedback | page state  |
| focus / disabled / error examples              |
+------------------------------------------------+
```

**Included**

- Official Material Theme Builder export with recorded source seed/settings.
- Semantic dark color roles, system-font typescale roles, and common spacing, shape, elevation, and
  focus decisions needed by real consumers.
- Reusable inline, panel-level, and page-level feedback presentations.
- Storybook stories using the same committed tokens and CSS Modules as the application.

**Explicitly excluded**

The site shell, production route changes, board adapter, chess behavior, stored data, engine behavior,
light theme, and theme switching.

**Prerequisite**

Accepted MP-01. The Foundation Check remains available only as a compatibility proof until MP-05; it
does not become MP-02 product UI.

**Human acceptance script**

1. Review the semantic dark roles and typescale in Storybook at representative wide and constrained
   compositions.
2. Inspect inline, panel, and page feedback in normal, focus, and failure states.
3. Confirm consumers use semantic roles rather than page-local literal colors.
4. Confirm keyboard focus remains visible and the review surface does not imply a light theme or theme
   switcher.

**Stop condition**

> Stop when the token and primitive language is human-accepted. Do not create the site shell or board
> adapter in this milestone.

## MP-03 - Responsive Site Shell

**Human can see**

> The existing `/` status page appears inside a reusable desktop shell and transforms into a narrow-screen
> navigation composition.

**Human can do**

> A human can navigate the real destination and open, dismiss, keyboard-dismiss, and restore focus from
> the narrow-screen drawer.

**Included**

- Text-only Chess Move Trainer identity.
- Desktop top bar, visible left navigation, and main-content boundary.
- Narrow-screen Base UI drawer with real focus management and dismissal behavior.
- Real-destination navigation only.
- Adoption by `/` while preserving loading, healthy, and unavailable status behavior.

**Explicitly excluded**

`/viewer`, board rendering, viewer-owned context, stored data, traversal, analysis, editing, and fake or
disabled future destinations.

**Prerequisite**

Accepted MP-02.

**Human acceptance script**

1. Open `/` at a wide viewport and confirm the shell and unchanged health purpose.
2. Confirm the top and left regions, main-content boundary, identity, and real navigation.
3. Use a constrained viewport and open the drawer with pointer and keyboard input.
4. Dismiss it with the accepted close, outside, and keyboard paths and confirm focus restoration.
5. Exercise backend-success and backend-unavailable states and confirm their accessible status/alert
   semantics remain intact.
6. Confirm no viewer route or board is presented.

**Stop condition**

> Stop when the shell is accepted on `/` at wide and constrained layouts. Do not create `/viewer` in
> this milestone.

## MP-04 - Safe Read-Only Board Adapter

**Human can see**

> Storybook and focused component surfaces show valid and invalid positions rendered through one
> application-owned, accessible, read-only adapter.

**Human can do**

> A reviewer can inspect supported orientation and coordinate configurations and deliberately exercise
> invalid input without receiving a misleading starting position.

**Included**

- `chess.js` validation and position inspection boundary.
- `react-chessboard` isolation behind the adapter.
- Standard-FEN application contract, read-only configuration, orientation, coordinate visibility, and
  bounded fluid sizing.
- Accessible label, orientation, textual position description, and shared unavailable-state integration.
- Valid, invalid, and relevant configuration stories.

**Explicitly excluded**

`/viewer`, stored data, traversal, PGN parsing, movement, highlighting, arrows, Stockfish, persistence,
and package-specific state escaping the adapter.

**Prerequisite**

Accepted MP-03.

**Human acceptance script**

1. Open the valid starting-position story and confirm the board is static, bounded, and readable.
2. Inspect orientation and coordinate configurations that the adapter actually supports.
3. Exercise invalid or unsupported FEN input and confirm an accessible Position unavailable state.
4. Confirm the surrounding shell/story surface survives the invalid state.
5. Inspect the accessibility label, orientation, and textual position description.
6. Confirm no movement handlers, analysis arrows, or inactive future props are exposed.

**Stop condition**

> Stop when the adapter's safety and accessibility contract is accepted. Do not create `/viewer` or
> connect stored data in this milestone.

## MP-05 - Integrated Static Viewer

**Human can see**

> `/viewer` displays the standard starting position inside the accepted shell, workspace, and board
> adapter composition.

**Human can do**

> A human can open `/viewer`, use the shared navigation at wide and constrained sizes, and inspect the
> static board and its contained failure behavior.

**Before / After**

```text
Before: production / inside the accepted shell; no viewer route

After:
/		status page inside shared shell
/viewer	read-only starting board + viewer-owned context
```

**Included**

- Production React Router composition with durable `/viewer`.
- Viewer workspace inside the shell's main-content region.
- Viewer-owned primary board and contextual panel.
- Desktop empty context visibility and constrained empty-context omission.
- MP-04 adapter integrated with the standard starting position, white at the bottom, and coordinates.
- Preservation of `/` and its status behavior.
- Removal of the temporary MP-01 Foundation Check after all its compatibility proofs have real stories
  or consumers.

**Explicitly excluded**

Stored data, corpus access, traversal, movement, highlighting, arrows, Stockfish, persistence, and any
retained duplicate diagnostics page.

**Prerequisite**

Accepted MP-04. MP-01 through MP-04 must be human-accepted in order; the Foundation Check retirement is
part of MP-05 acceptance.

**Human acceptance script**

1. Open `/` and confirm the existing status behavior remains available in the shell.
2. Open `/viewer` at a wide viewport and confirm the board, coordinates, white orientation, workspace,
   and intentionally empty context panel.
3. Use a constrained viewport and confirm the board remains bounded, the shell drawer works, and empty
   context is omitted.
4. Inspect board label, orientation, textual description, and invalid-position containment.
5. Confirm no stored data, movement, traversal, analysis, persistence, fake content, or speculative
   navigation appears.
6. Confirm the temporary Foundation Check is no longer retained after real stories/consumers replace
   its proofs.

**Stop condition**

> Stop when the static viewer and Foundation Check retirement are accepted. Do not begin MP-06 corpus
> work in the same milestone.

## MP-06 - Validated FEN Corpus

**Human can see**

> Reviewable evidence shows that the accepted captured games have a complete, valid, ordered position
> corpus.

**Human can do**

> A reviewer can use the accepted corpus workflow and verify replay, completeness, rerun, and failure
> evidence.

**Explicitly excluded**

Viewer integration, traversal UI, engine analysis, and any schema, ownership, migration, or failure
policy not settled by MP-06 grilling.

**Prerequisite**

Accepted MP-05 and completed fresh MP-06 grilling.

**Human acceptance script**

1. Use the currently verified captured-game source and accepted corpus workflow.
2. Confirm the initial position and required ordered positions are present and replay-valid.
3. Confirm the accepted per-game and unique-position evidence is distinguishable.
4. Repeat the workflow and exercise the accepted partial-failure and idempotency behavior.
5. Confirm no viewer or traversal behavior was added beyond the accepted milestone.

**Stop condition**

> Stop when corpus completeness and its proof are accepted. Do not begin MP-07 until the MP-06 gate is
> complete.

## MP-07 - Arbitrary Stored-Position Display

**Human can see**

> The read-only viewer displays a selected stored FEN rather than only its built-in starting position.

**Human can do**

> A human can select or address an accepted stored position and observe the accepted loading, success,
> missing, and malformed states.

**Explicitly excluded**

Game traversal, board editing, analysis, and ungrilled URL, API, or application-state decisions.

**Prerequisite**

Accepted MP-06 and completed fresh MP-07 grilling.

**Human acceptance script**

1. Enter the accepted stored-position workflow from `/viewer`.
2. Display representative positions, including one unlike the starting position.
3. Confirm loading, missing, and malformed feedback is local, accessible, and recoverable.
4. Confirm malformed data cannot silently fall back to the starting position.
5. Confirm the board remains read-only and MP-05 behavior remains intact.

**Stop condition**

> Stop when any accepted stored FEN can be safely displayed and its failure states are accepted. Do not
> add sequential traversal in this milestone.

## MP-08 - Complete-Game Traversal

**Human can see**

> The workspace makes the current position and the beginning and end of an accepted stored game clear.

**Human can do**

> A human can move exactly through the accepted ordered positions using the grilled traversal model.

**Explicitly excluded**

Piece movement, editing, Stockfish, and changes to stored position data.

**Prerequisite**

Accepted MP-07 and completed fresh MP-08 grilling, including fixture and source-attribution confirmation.

**Human acceptance script**

1. Open an accepted stored game at its initial position.
2. Traverse forward and backward through representative positions using the accepted pointer and
   keyboard paths.
3. Confirm initial and final boundary behavior and accepted game context.
4. Confirm traversal changes only the displayed stored position and does not mutate it.

**Stop condition**

> Stop when a complete stored game can be reviewed and its boundary behavior is accepted. Do not add
> engine analysis or editing in this milestone.

## MP-09 - Persisted Backend Stockfish Analysis

**Human can see**

> An accepted stored position has backend analysis available with an observable reuse result on a later
> request.

**Human can do**

> A human can use the accepted backend analysis workflow and verify that an unchanged eligible result is
> reused rather than recomputed.

**Explicitly excluded**

Browser Stockfish, user-created-position persistence, and engine settings or schemas not settled by
MP-09 grilling.

**Prerequisite**

Accepted MP-08 and completed fresh MP-09 grilling.

**Human acceptance script**

1. Select an accepted stored position with an accepted analysis request.
2. Start backend analysis and confirm accepted completion and failure states.
3. Repeat the request and confirm the accepted persisted-reuse behavior.
4. Exercise accepted identity, invalidation, progress, cancellation, and recovery cases.
5. Confirm no browser engine or editable-board behavior was introduced.

**Stop condition**

> Stop when persisted backend analysis and reuse are accepted. Do not begin browser evaluation in this
> milestone.

## MP-10 - Browser Stockfish Evaluation

**Human can see**

> The currently displayed read-only position receives browser evaluation feedback through the accepted
> browser workflow.

**Human can do**

> A human can start browser evaluation, observe its progress and result, and use the accepted cancellation
> or recovery path.

**Explicitly excluded**

Piece editing, unknown-position persistence, and any assumption that browser results are durable.

**Prerequisite**

Accepted MP-09 and completed fresh MP-10 grilling.

**Human acceptance script**

1. Display an accepted stored position through the read-only viewer.
2. Start browser evaluation and confirm accepted loading and result presentation.
3. Exercise accepted cancellation, resource-limit, and failure behavior.
4. Confirm the board remains read-only and backend persistence behavior is not silently changed.

**Stop condition**

> Stop when browser evaluation of a displayed read-only position is accepted. Do not begin editing in
> this milestone.

## MP-11 - Browser Position Editing

**Human can see**

> The workspace visibly distinguishes an edited position from a stored read-only position and shows its
> accepted validation state.

**Human can do**

> A human can edit a position through the accepted accessible interaction model and reset or correct it
> using the accepted controls.

**Explicitly excluded**

Automatic persistence or analysis of an unknown position and any editing semantics not settled during
MP-11 grilling.

**Prerequisite**

Accepted MP-10 and completed fresh MP-11 grilling.

**Human acceptance script**

1. Enter the accepted editing workflow from a displayed position.
2. Perform representative edits, including the grilled legality and complete-state edge cases.
3. Confirm validation, reset, keyboard, touch, and accessibility behavior.
4. Confirm edits do not silently write an unknown position or alter stored-game data.

**Stop condition**

> Stop when editing semantics and validation are accepted. Do not add unknown-position persistence in
> this milestone.

## MP-12 - Persist and Analyze Unknown Positions

**Human can see**

> A previously unknown position has durable accepted analysis and a visible reuse outcome.

**Human can do**

> A human can explicitly persist and analyze an unknown position through the accepted workflow, then use
> it again under the accepted identity and provenance policy.

**Explicitly excluded**

Unreviewed CRUD, authorization, provenance, duplicate, security, engine, or failure behavior beyond
the MP-12 grilling decisions.

**Prerequisite**

Accepted MP-11 and completed fresh MP-12 grilling.

**Human acceptance script**

1. Create an unknown position through the accepted editing workflow.
2. Explicitly perform the accepted persist-and-analyze action.
3. Confirm validation, provenance, duplicate, failure, and stale-result behavior.
4. Reopen or reuse the position and confirm the accepted result-identity policy.
5. Confirm existing stored games and `/` health behavior remain unchanged.

**Stop condition**

> Stop when unknown-position persistence and reusable analysis are accepted. Do not infer broader product
> CRUD or authorization from this milestone.

## Explicitly Outside This Master Plan

- Implementing any milestone, installing packages, creating focused Plans, compiling work orders,
  dispatching work, validating, reconciling, committing, or pushing.
- Treating this document or the grilling record as implementation authority.
- Replacing or removing the existing `/` health page or weakening its existing states.
- Retaining the MP-01 Foundation Check after MP-05 acceptance.
- A light theme, theme switcher, speculative navigation, fake content, or inactive feature controls.
- A global viewer-specific context panel.
- Custom PGN parsing, custom FEN parsing, a custom chessboard renderer, or a custom router when the
  confirmed package boundaries already provide the required behavior.
- Piece movement before MP-11.
- Persistence of unknown or user-created positions before MP-12.
- A combined backend/browser engine implementation or an automatic browser-result persistence policy.
- Product authentication, authorization, notification, logging, or generic CRUD not required by an
  accepted milestone.
- Assuming historical game counts, fixtures, schemas, packages, engine settings, or API contracts remain
  current without the applicable grilling and repository verification.

## Source Ownership Expected By Future Focused Plans

Future focused Plans must verify and narrow their actual paths rather than inheriting this entire list:

- `frontend/package.json`, `frontend/package-lock.json`, `frontend/.storybook/**`, and the bounded
  temporary foundation-proof files for MP-01.
- `frontend/src/` for application-owned tokens, primitives, shell, routing, viewer, board adapter, and
  feature-local states introduced by MP-02 through MP-05.
- `frontend/vite.config.ts`, `frontend/vitest.config.ts`, frontend test setup, and `tests/e2e/**` only
  where the selected milestone's toolchain proof requires them.
- `backend/app/` for feature routes and service boundaries introduced by accepted data or analysis
  milestones.
- `data/` and capture/extraction tooling for MP-06, only after current ownership and contracts are
  verified.
- `frontend/src/**/*.test.tsx`, `backend/tests/`, and `tests/e2e/` for focused regression and acceptance
  evidence.
- `docs/grilling-docs/static-position-to-analysis-roadmap.md` for detailed decisions and grilling gates,
  not as a substitute for current source inspection.

Conditional implementation paths and verification-only files are not unconditional Touches. Every
selected milestone must preserve unrelated worktree changes.

## Verification Standard For Future Milestones

Every selected milestone requires:

- focused automated coverage for its observable behavior, accessibility semantics, and relevant empty,
  loading, failure, cancel, and boundary states;
- regression coverage for preserved neighboring behavior, especially `/` health status and the board
  safety contract after MP-05;
- representative wide and constrained human review for visual work;
- keyboard and pointer coverage, with touch coverage whenever touch interaction is exposed;
- review of malformed, missing, interrupted, and recovery states where the milestone can encounter them;
- a human acceptance decision before the next milestone starts; and
- explicit confirmation that the milestone's exclusions have not hitchhiked into the change.

For MP-01 through MP-05, the focused proof layers include Storybook, Vitest/React Testing Library,
Storybook accessibility checks, and Playwright/browser checks as applicable. For MP-06 onward, the
applicable grilling must define the representative data and exact operational proof.

The known repository commands include the frontend test, lint, and build scripts in
`frontend/package.json`, backend tests, the end-to-end Playwright suite, and
`.venv\Scripts\python.exe scripts/check_docs.py --check` for documentation validation. A selected
milestone's focused Plan or direct route must verify exact commands and must not add unrelated services
or live-environment dependencies.

## Open Decisions and Grilling Gates

MP-01 through MP-05 have confirmed destination and technology boundaries, but the exact implementation
file ownership and route transport for MP-03 through MP-05 remain the responsibility of assessment and
`to-plan` at selection time.

- **MP-06:** Confirm the current source and replay oracle; schema and ownership; normalization and
  duplicate identity; idempotency, partial failures, reruns; and corpus proof.
- **MP-07:** Settle selection/navigation, frontend/backend boundary, loading and missing states, and
  URL/application-state ownership.
- **MP-08:** Reconfirm the fixture and attribution, then settle control/keyboard behavior, game context,
  and traversal end states.
- **MP-09:** Settle engine packaging and invocation, depth/limits/MultiPV, result fields and identity,
  settings/version invalidation, progress/cancellation/recovery, and persistence schema.
- **MP-10:** Select browser engine technology and settle resource limits, cancellation, evaluation
  presentation, backend relationships, and session-only versus persisted results.
- **MP-11:** Settle legal versus free-form editing, complete FEN-state controls, validation/reset, and
  accessible interaction.
- **MP-12:** Settle provenance and authorization, identity/normalization and duplicates, write and
  analysis triggering, reuse/invalidation, and failure recovery.

These are gates, not questions blocking the broad destination. No MP-06 through MP-12 milestone may
enter focused planning or implementation until its corresponding fresh grilling is complete.

## Provenance

- The primary detailed source is
  `docs/grilling-docs/static-position-to-analysis-roadmap.md`, recorded as confirmed design-review
  evidence on 2026-08-15. It settles the technology and destination boundaries for MP-01 through MP-05
  and preserves directional envelopes for MP-06 through MP-12.
- The source supersedes `single-game-viewer.md`, `pgn-to-fen-extraction.md`, and
  `stockfish-feasibility.md`; historical facts from those documents require current verification before
  operational use.
- Current-state claims were verified from `frontend/src/App.tsx`, the status feature and tests,
  `frontend/package.json`, `frontend/vite.config.ts`, `frontend/vitest.config.ts`,
  `tests/e2e/playwright.config.ts`, `frontend/src/app.css`, `backend/app/main.py`, the health tests,
  and current data paths.
- This existing artifact is the revised master plan at
  `docs/master-plans/static-position-to-analysis.md`. It records destination direction only and does
  not authorize MP-01 or any later implementation.
