# Safe Read-Only Board Adapter - one accepted Storybook composition

> **Status:** MP-04 Plan approved for one ordered Storybook-only stage; implementation and automated proof
> must complete before explicit human acceptance, and MP-05 remains blocked until that acceptance.

- **Read trigger:** Open after accepted MP-03 and before authoring or implementing the MP-04 stage order.

## What we're building & why

MP-04 creates one reusable, application-owned adapter that safely displays a chess position through
`react-chessboard`. The adapter is implemented once and reviewed through Storybook; Storybook is the real
component surface, not a mock or parallel implementation. The stage establishes the strict FEN validation
boundary, read-only board behavior, bounded fluid sizing, orientation and coordinate options, complete
generated position description, and contained unavailable state needed by the later viewer.

The stage is deliberately Storybook-only. Focused component, Storybook, browser, and accessibility proof
must pass before review. Human acceptance then ships the stage and is a hard prerequisite for MP-05
production integration. Review corrections keep this same stage open: the adapter and stories are revised,
all proof is rerun, and the complete surface is presented again. MP-04 does not change `/`, create `/viewer`,
or retire the temporary MP-01 Foundation Check.

The detailed [MP-04 grilling record](../../../grilling-docs/static-position-to-analysis-roadmap.md),
[MP-04 master-plan boundary](../../../master-plans/static-position-to-analysis.md), and persistent
[expanded-description advisory reference](../../../design-guides/mp04-board-adapter-reference.html) govern
this Plan. The HTML reference is explicitly non-canonical and visual guidance only; the shipped MP-02
feedback and semantic-token contracts remain the implementation sources of truth.

## Settled decisions

- The adapter's complete public contract is `fen`, optional `orientation`, optional `showCoordinates`, and
  required non-empty `label`. It exposes no sizing prop, description replacement, package options, package
  state, movement handlers, or speculative future properties.
- `orientation` defaults to White and `showCoordinates` defaults to visible. The board is static and
  non-focusable, with White displayed at the bottom by default.
- `chess.js` `validateFen` defines MP-04 validity. FEN is strict and untrimmed: surrounding whitespace is
  rejected rather than normalized, and no custom historical-legality layer is added.
- Invalid or unsupported input never silently becomes the standard starting position. Invalid input and an
  unexpected `react-chessboard` render failure produce the same compact, width-bounded **Position unavailable**
  presentation using the shipped shared feedback primitives. There is no retry control, callback, or
  user-facing package diagnostic; changed safe input is the recovery path.
- `react-chessboard` is isolated behind the adapter and remains read-only. Its default board and piece
  appearance is retained unless focused accessibility review proves that a minimum centralized semantic-token
  correction is required.
- The board is a described static graphic. The required `label` supplies its concise contextual accessible
  name; the adapter generates a separate description associated through `aria-describedby`.
- One generated position model supplies both the permanently available assistive description and a separate
  visible native **Position description** disclosure. The disclosure is collapsed by default and expanded in
  its dedicated story; collapsing it never removes the assistive description.
- The generated description includes orientation, side to move, every occupied square in stable FEN order
  from `a8` through `h1` using natural piece names, fully expanded castling rights, an explicit en-passant
  target or no-target statement, halfmove clock, and fullmove number.
- The adapter uses container-driven `width: 100%` sizing capped at `40rem`/`640px`; it must remain a bounded
  square at the fixed `320px`, `480px`, and `640px` review checkpoints without horizontal overflow.
- The single `Board Adapter` Storybook group has seven directly addressable stories: default valid starting
  position; a verified realistic deterministic rich non-starting FEN; Black orientation; hidden coordinates;
  constrained-width sizing; invalid FEN with **Position unavailable**; and expanded position description.
- The selected advisory reference records only the accepted expanded-description treatment. The roadmap's
  conditional removal of the superseded three-option scratch comparison is preserved as a record constraint;
  this Plan does not inspect or authorize `scratch/` access without separate exact-path authorization.

## Stages

1. **SHIPPED - Complete the Storybook-only board adapter stage:** implement the real adapter, seven direct
   stories, focused component proof, Storybook interaction and accessibility proof, and the Storybook browser
   proof at the required sizing checkpoints; then stop for explicit human acceptance. Requested corrections
   remain inside this one stage and require complete re-proof before another review.

## Shipped

| Stage | What shipped (<=2 sentences) |
|-------|------------------------------|
| 1 | Storybook-only board adapter stage shipped: strict read-only BoardAdapter with seven direct stories, focused/Storybook/browser/axe proof, and repository regression all passing, with explicit human acceptance recorded. |

## Touches

- `frontend/src/features/`
- `frontend/.storybook/main.ts`
- **Depends on:** [Responsive Site Shell](../../done/responsive-site-shell/responsive-site-shell.md)

The broad feature glob is narrowed by the compiler handoff to the new board-adapter ownership below. The
`.storybook/main.ts` touch is narrowed to a single `stories`-array glob insertion registering the new
board-adapter story group; it does not authorize changes to the existing shell, status, foundation,
design-system, backend, viewer, other Storybook configuration, or unrelated feature paths.

### Verification-only paths

The new Storybook browser proof will live under the existing `tests/e2e/` directory and is not unconditional
implementation ownership. An order may authorize the exact new spec only when the stage proof requires it.

The existing advisory HTML is review-only and is not an implementation touch. Any token correction is
conditional and must name the exact centralized semantic-token file only after an accepted accessibility
failure proves it necessary.

## Acceptance

Automated component, Storybook, browser, and accessibility checks supplement but do not replace manual visual,
keyboard, responsive, assistive-technology, contrast, and WCAG 2.2 AA review. Review must follow successful
automated proof. If changes are requested, the stage remains open and all proof and this acceptance sequence
repeat.

### Stage 1 human gate

1. Confirm the focused component and Storybook browser proof passed before beginning visual acceptance;
   automated proof supplements rather than replaces this review.
2. Open the valid starting-position and rich non-starting-position stories and confirm strict FEN rendering,
   static behavior, package-default appearance, White-default orientation, and visible-default coordinates.
3. Inspect the Black-orientation and hidden-coordinate stories, confirming that the textual inventory remains
   in stable `a8` through `h1` order.
4. Review the board in fixed `320px`, `480px`, and `640px` containers and confirm it remains a bounded square
   without horizontal overflow.
5. Inspect the required contextual label and the complete description: orientation, side to move, naturally
   named occupied squares, expanded castling rights, explicit en-passant state, halfmove clock, and fullmove
   number.
6. Confirm the assistive description remains available while the visual disclosure is collapsed, then inspect
   the dedicated expanded-description story and its keyboard behavior.
7. Exercise invalid FEN and unexpected render failure and confirm the same compact **Position unavailable**
   state, no misleading board, no retry control, no package diagnostic, and survival of the surrounding story
   surface.
8. Verify coordinate and piece/square contrast and review the complete composition under Windows High
   Contrast/`forced-colors`; if a default fails, confirm only the minimum centralized token correction was made.
9. Confirm the visual board, pieces, and squares add no keyboard stops or interactive semantics and that no
   movement handlers, analysis arrows, inactive future props, sizing/description customization, or color
   controls are exposed.
10. Explicitly accept the complete Storybook surface. If changes are requested, keep this single stage open,
    rerun all proof after revision, and repeat the human review before MP-05 begins.

**Stop condition:** stop when the adapter's safety and accessibility contract is accepted. Do not create
`/viewer`, integrate the adapter into production, connect stored data, or begin MP-05 from this Plan.

## Exclusions

- `/viewer`, production integration, production `App.tsx`, React Router composition, router-aware navigation,
  shell changes, viewer workspace/context regions, stored data, traversal, PGN parsing, movement, dragging,
  highlighting, arrows, Stockfish, persistence, and backend work.
- Custom historical-legality rules, silent normalization, trimming, fallback to the starting position,
  exposed `react-chessboard` options or state, description customization, sizing props, inactive callbacks,
  speculative handlers, and TODO-driven public contracts.
- User-adjustable square colors, color wheels, presets, piece-theme selection, broader palette design, light
  theme, theme switching, and any token changes not proven necessary by the accepted accessibility contract.
- Pixel-snapshot tests, visual-regression services, new packages, request-mocking dependencies, global state
  libraries, custom board interaction, custom error/retry workflows, and new feedback APIs.
- Editing the persistent advisory HTML, treating it as implementation authority, exploring or updating the
  user-owned `scratch/` path without separate exact-path authorization, unrelated worktree cleanup, MP-01
  Foundation Check retirement, commits, pushes, reconciliation, or adjacent milestone work.

## Automated proof contract

Commands run from the repository root in the documented Windows environment. Storybook interaction tests use
the existing Storybook tooling and require the Storybook server at `http://127.0.0.1:6006`; the existing
Playwright configuration supplies the repository's documented browser-server setup.

### Stage 1 focused proof

```powershell
npm run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx
npm run build-storybook --prefix frontend
npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006
.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\board-adapter-storybook.spec.ts
```

The component and Storybook proof must cover strict valid/invalid FEN behavior, the rich fixture's complete
state, default and Black orientation, coordinate visibility, bounded sizing, generated description parity,
collapsed and expanded disclosure behavior, non-interactivity, invalid and unexpected-failure containment,
shared unavailable feedback, and focused axe checks. The browser proof must use the real Storybook iframe,
exercise the seven direct stories, check `320px`, `480px`, and `640px` containers, verify keyboard disclosure
behavior and no board interaction, run `@axe-core/playwright`, and include a `forced-colors` review context.
Pixel snapshots are not permitted.

### Stage 1 repository regression

```powershell
npm run lint --prefix frontend
npm run build --prefix frontend
.\frontend\node_modules\.bin\prettier.cmd --check frontend
.\.venv\Scripts\python.exe scripts\check.py
```

These checks must not be used to widen the implementation scope. Existing unrelated baseline failures must be
reported rather than repaired outside the authorized board-adapter paths.

## Compiler handoff

### Stage 1 - complete Storybook-only board adapter

- **Route:** `ORDERED`.
- **Dependency:** Accepted MP-03 at `docs/plans/done/responsive-site-shell/responsive-site-shell.md`; MP-05
  production integration is invalid until this stage receives explicit human acceptance.
- **Verified edit sites:**
  - `frontend/src/features/board-adapter/BoardAdapter.tsx` - proposed new application-owned adapter. It
    must own strict `chess.js` validation, position inspection, generated description, read-only
    `react-chessboard` translation, bounded sizing, orientation/coordinate defaults, disclosure state, and the
    contained unavailable result. Consumers must not import the package directly.
  - `frontend/src/features/board-adapter/BoardAdapter.module.css` - proposed new local presentation for the
    bounded board, description/disclosure, unavailable state, focus treatment, and forced-colors behavior;
    use existing semantic roles and no inline application CSS.
  - `frontend/src/features/board-adapter/BoardAdapter.stories.tsx` - proposed new single `Board Adapter`
    Storybook group with exactly seven direct stories. Stories must render the real adapter, not a fixture copy
    or parallel mock.
  - `frontend/src/features/board-adapter/BoardAdapter.test.tsx` - proposed focused component proof for the
    contract, generated state description, disclosure, non-interactivity, invalid input, unexpected package
    failure containment, bounded sizing, and component-level axe behavior.
  - `tests/e2e/board-adapter-storybook.spec.ts` - proposed verification-only browser proof against the real
    Storybook iframe, including exact container checkpoints, direct stories, forced-colors coverage, and
    `@axe-core/playwright` results.
  - `frontend/src/features/foundation/FoundationCheck.tsx:1-63` - current temporary compatibility harness is
    the only existing direct `react-chessboard` consumer. It uses `chess.js` validation and read-only package
    options for proof only; it must remain unchanged and must not become the adapter.
  - `frontend/src/features/foundation/FoundationCheck.test.tsx:16-34` - current axe proof excludes the
    package-generated `[aria-roledescription="draggable"]` wrappers. MP-04 must establish its own application
    accessibility boundary and must not copy this temporary harness as product behavior.
  - `frontend/src/features/design-system/feedback/PanelFeedback.tsx:5-9` - shipped thin wrapper over the
    accepted feedback core. Reuse the existing feedback contract for the bounded unavailable presentation;
    do not add retry, action, severity, or package-diagnostic props.
  - `frontend/.storybook/preview.tsx` - existing Storybook preview loads the shared application CSS and
    generated dark Material theme. Reuse that surface and the accepted MP-02 `--md-sys-*`/`--cmt-*` contracts;
    do not create a second visual implementation.
  - `frontend/.storybook/main.ts` - proposed single `stories`-array glob insertion to register the new
    `board-adapter` story group alongside the existing foundation, design-system, and app-shell globs. No other
    Storybook configuration (`test-runner.ts`, `preview.tsx`, `package.json` scripts) is touched.
- **Verified state flow:** adapter props -> strict `validateFen` result -> one inspected chess position model
  -> board options plus generated assistive/visible description. Invalid validation returns the shared
  unavailable presentation without rendering a fallback board. An unexpected package render failure is
  contained at the adapter boundary and returns the same unavailable presentation. The visible disclosure owns
  only its local open/closed state; its collapsed state never removes the assistive description.
- **Verified consumers and defaults:** no production board or viewer consumer exists. `FoundationCheck` is
  temporary compatibility evidence and remains outside this feature. MP-05 will later provide the first
  production consumer. The pinned dependencies are already present in `frontend/package.json`; no package
  installation or version change is authorized.
- **Settled contracts:** public props are limited to `fen`, `orientation`, `showCoordinates`, and non-empty
  `label`; White and visible coordinates are defaults; `validateFen` defines strict validity; `react-chessboard`
  is read-only and isolated; descriptions are generated internally; invalid and unexpected failures share the
  compact **Position unavailable** state; and no retry, package diagnostics, sizing prop, description override,
  movement, arrows, highlighting, or color controls are exposed.
- **Accessibility constraints:** the visual board is a non-focusable described graphic with no piece, square,
  drag, button, or keyboard semantics. The required contextual label is separate from the complete generated
  `aria-describedby` description. Occupied squares use stable `a8` through `h1` order independent of visual
  orientation. The visible native disclosure is collapsed by default and has a dedicated expanded story.
- **CSS and appearance constraints:** retain package-default board and piece appearance; use CSS Modules for
  application-owned structure; consume shipped Material semantic roles and typescale; do not add page-local
  literal colors or inline application styles. A minimum centralized semantic-token correction is conditional
  on a focused accepted accessibility failure and must be named by the compiler before authorization.
- **Focused proof:**
  `npm run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx`;
  `npm run build-storybook --prefix frontend`;
  `npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`;
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\board-adapter-storybook.spec.ts`.
- **Repository regression proof:** `npm run lint --prefix frontend`; `npm run build --prefix frontend`;
  `.\frontend\node_modules\.bin\prettier.cmd --check frontend`; and
  `.\.venv\Scripts\python.exe scripts\check.py`.
- **Human acceptance:** after all automated proof passes, execute all ten Stage 1 acceptance steps at the
  starting, rich, Black, hidden-coordinate, invalid, and expanded stories; inspect `320px`, `480px`, and
  `640px` containers; inspect keyboard, assistive, contrast, and forced-colors behavior; and explicitly accept
  the complete Storybook surface. Corrections keep the same stage open and require complete re-proof.
- **Bounded lookups:** verify the installed `react-chessboard` 5.12.0 type/DOM behavior and the wrapper
  attributes needed to contain package-generated draggable semantics; validate the exact deterministic rich FEN
  fixture with the pinned `validateFen` and position model; and select a Storybook-compatible failure exercise
  that does not add a public test prop or eighth story. These lookups may refine implementation mechanics but
  may not change the settled public contract or stage boundary.
- **Open questions:** none at the product or acceptance boundary. The three bounded implementation lookups
  above remain for order compilation.
