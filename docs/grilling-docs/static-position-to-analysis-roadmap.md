# Static Position to Analysis Roadmap — Consolidated Grilling Record

**Recorded:** 2026-08-15  
**Status:** Confirmed design-review evidence  
**Implementation authority:** None  
**Supersedes:** `single-game-viewer.md`, `pgn-to-fen-extraction.md`, and `stockfish-feasibility.md`

## Purpose and document relationship

This record consolidates the product discussion about where Chess Move Trainer implementation should begin and how later capabilities should be ordered. It preserves the detailed decisions and reasoning that would be too granular for a master plan.

The intended documentation relationship is:

1. This grilling record owns the detailed product decisions, rationale, boundaries, and unanswered-decision tree.
2. A future lightweight master plan may reference this record rather than reproduce it.
3. The master plan will own milestone direction and dependencies, but it will not settle the later milestones recorded here as requiring fresh grilling.
4. Focused Plans may be created only after the applicable milestone has completed its required grilling.

The accepted MP-02 visual and feedback decisions now live in the advisory
[Static Position to Analysis design guide](../design-guides/static-position-to-analysis.md), with an accepted
[static visual reference](../design-guides/mp02-visual-reference.html). Those artifacts are non-canonical and
authorize no implementation. The future MP-02 focused Plan must link to them; later milestones use or update them
only when the user deliberately chooses to do so.

The lightweight master plan now exists at [`docs/master-plans/static-position-to-analysis.md`](../master-plans/static-position-to-analysis.md). This record remains the detailed decision authority; the master plan owns milestone direction, strict dependencies, and human gates without replacing this rationale.

## Original intent

The implementation should begin with slices that reveal something tangible. At the end of each slice, it should be possible to state plainly what has been created, rather than describe only internal infrastructure.

The initial idea of beginning with a complete stored FEN corpus was revised. The first need is time and space for visual design before chess behavior is added. Implementation will therefore begin with a reusable application foundation that can safely display exactly one static chess position.

The governing progression is **static structure first, then stored data, then traversal, then analysis, then mutation**. Functionality should not be filled in merely to make an interface look complete. At the same time, shared foundations and deliberate extension boundaries should be established early so known later uses do not force structural redesign.

## Tangible milestone tree

```text
MP-01 — verified technology foundation
└── MP-02 — Material design tokens and reusable UI primitives
    └── MP-03 — responsive site shell
        └── MP-04 — safe read-only board adapter
            └── MP-05 — integrated static viewer at /viewer
                └── MP-06 — complete validated FEN corpus stored for captured games
                    └── MP-07 — any stored FEN can be pulled into the read-only viewer
                        └── MP-08 — stored FENs can be walked in order to form a game
                            └── MP-09 — backend Stockfish analysis is stored and reused
                                └── MP-10 — Stockfish evaluates a read-only position in-browser
                                    └── MP-11 — a position can be edited in the browser
                                        └── MP-12 — an unknown FEN can be persisted and analyzed
```

This tree expresses strict dependency and direction. MP-01 through MP-05 collectively replace the original broad “Slice 1” envelope. Their shared product and technology direction is settled in this record. MP-01 is implemented and accepted; MP-02 through MP-05 still require route assessment and an appropriately bounded Plan or direct brief before implementation. MP-06 onward remains deliberately ungrilled.

## Grilling gate

- **MP-01:** implemented and accepted on 2026-08-15; its completion is recorded in the archived focused Plan and the master-plan receipt.
- **MP-02 through MP-05:** their destination boundaries are settled by this record and remain eligible for route assessment and focused planning one milestone at a time.
- **MP-06 onward:** each requires its own fresh grilling before focused planning or implementation.
- The milestone names below are destination envelopes only. They do not settle schemas, APIs, workflows, storage policy, engine settings, interaction behavior, or acceptance details.
- No later milestone may infer authorization from the older records that this document supersedes.

## Foundation roadmap revision

The amount of selected technology and reusable structure made the original static-viewer foundation too broad to remain one independently reviewable milestone. The master-plan direction must therefore replace the old MP-01 with five whole-numbered milestones and renumber every later milestone.

### MP-01 — verified technology foundation

**Tangible claim:**

> We created and verified the application’s component-development technology foundation.

MP-01 installs and configures the complete selected production and development stack. It proves compatibility through a temporary Storybook **Foundation Check** rather than through package-manifest changes alone.

The Foundation Check exercises, at minimum:

- shared global CSS loading;
- CSS Modules;
- a Lucide icon;
- a Base UI structural primitive;
- React Router context;
- chess.js validation of a known valid and invalid FEN;
- react-chessboard rendering of a safe static position; and
- react-error-boundary containment of a deliberately exercised render failure.

The proof is a development-only compatibility harness. It is not the production board adapter, final token system, shell, route, viewer, or shared error architecture. It must avoid publishing speculative application APIs.

MP-01 also configures the selected Storybook and accessibility-test integrations sufficiently to prove that their toolchains build and execute. Exact dependency pins follow the confirmed technology section below.

MP-01 must not:

- change the existing `/` page or its styling;
- create `/viewer`;
- introduce production route composition;
- establish the final Material palette or typescale;
- create the production site shell;
- create the production board adapter;
- claim the compatibility harness as reusable product UI; or
- begin any later foundation milestone.

The temporary Foundation Check remains only until real stories and consumers prove all integrations. MP-05 acceptance must remove it rather than retain a duplicate diagnostics page that can drift from production components.

#### Implementation status and current evidence

MP-01 was implemented and accepted on 2026-08-15. The archived focused Plan at
`docs/plans/done/verified-technology-foundation/verified-technology-foundation.md:3,49-65`
records all 13 ordered stages shipped and the acceptance state. The current repository evidence is:

- `frontend/package.json:9-54` contains the selected exact runtime, Storybook, and layered accessibility
  proof tooling and scripts;
- `frontend/src/features/foundation/FoundationCheck.tsx:1-135` exercises the selected integration
  boundaries;
- `frontend/src/features/foundation/FoundationCheck.test.tsx:16-35` provides component-level axe proof,
  while `FoundationCheck.stories.tsx:17-59` provides Storybook states and interactions;
- `frontend/.storybook/main.ts:3-10` and `preview.tsx:1-4` configure the Storybook surface;
- `tests/e2e/foundation-accessibility.spec.ts:8-34` and `tests/e2e/playwright.config.ts:7-25` provide
  the browser axe proof and its Storybook server; and
- `frontend/src/App.tsx:1-4` remains `StatusPage`-only, with no production router or `/viewer`.

The full local check passed during the assessment. MP-02 is the next implementation frontier. The
temporary Foundation Check remains in place because MP-05 has not yet replaced its compatibility proofs.

### MP-02 — Material tokens and reusable UI primitives

**Tangible claim:**

> We created the reusable visual and feedback language for the application.

MP-02 owns the official Material Theme Builder export, recorded source seed/settings, semantic dark color variables, system-font typescale variables, common spacing/shape/elevation/focus decisions needed by real consumers, and the reusable inline, panel, and page-level feedback presentations. Storybook provides the human-reviewable surface for these primitives.

MP-02 does not apply a site shell, create a board adapter, or change production routing.

#### Accepted MP-02 design decisions

The detailed accepted decisions are preserved in the advisory
[design guide](../design-guides/static-position-to-analysis.md) rather than duplicated throughout this roadmap
record. In summary:

- the visual thesis is **Tournament analysis desk**;
- the fixed dark Material 3 scheme uses seed `#3F51B5`, Tonal Spot, and standard contrast, with the official
  Theme Builder export preserved separately from application-owned semantic tokens;
- the complete Material 3 `system-ui` typescale, balanced density, spacing `4/8/12/16/24/32/48px`, restrained
  `4/8/12px` radii, border-first depth, selective elevation, and a separated `2px` indigo focus ring form the
  visual foundation;
- reusable information, success, warning, and error feedback uses dedicated contrast-verified token pairs, fixed
  Lucide icons, required messages, optional headings, explicit inline/panel/page wrappers, and consumer-owned
  live-region semantics; and
- each future MP-02 implementation stage must start from a Storybook story and end with that story working and
  reviewable at the accepted `1920×1080` desktop and `412×915` Pixel 8a portrait targets.

MP-02 does not restyle production `/`, create actions or recovery workflows, add a monospace role, add a
structural signature motif, or introduce any shell, routing, board, chess-data, engine, persistence, light-theme,
or theme-switching behavior. The accepted HTML reference remains advisory and its conceptual colors are not an
official export or production tokens.

### MP-03 — responsive site shell

**Tangible claim:**

> We created a reusable responsive application shell shared by real pages.

MP-03 owns the text identity, real-destination navigation, desktop top/left regions, narrow-screen Base UI drawer behavior, main-content boundary, responsive shell media queries, and adoption by the existing `/` status page. It must preserve the status behavior while changing its structural presentation.

MP-03 does not create a viewer route, board, or viewer-owned contextual panel.

### MP-04 — safe read-only board adapter

**Tangible claim:**

> We created a reusable component that safely displays a chess position.

MP-04 owns the chess.js validation boundary, react-chessboard isolation, standard-FEN application contract, read-only configuration, orientation and coordinate options, bounded fluid sizing, accessible description, shared unavailable-state integration, and Storybook proof for valid and invalid positions.

MP-04 does not create `/viewer`, traverse positions, move pieces, parse PGN, access stored data, or run Stockfish.

### MP-05 — integrated static viewer

**Tangible claim:**

> We created a page that safely displays one position inside the reusable application workspace.

MP-05 owns production React Router composition, durable `/viewer`, the viewer workspace and viewer-owned desktop context region, constrained-layout omission of empty context, integration of the MP-04 adapter with the standard starting position, and preservation of `/`.

MP-05 removes the temporary MP-01 Foundation Check after real shell, primitive, board, error, router, and viewer stories or consumers replace every compatibility proof. It does not connect stored data or add chess interaction.

### Renumbering map

```text
old MP-01 -> new MP-01 through MP-05
old MP-02 -> new MP-06
old MP-03 -> new MP-07
old MP-04 -> new MP-08
old MP-05 -> new MP-09
old MP-06 -> new MP-10
old MP-07 -> new MP-11
old MP-08 -> new MP-12
```

## Original static-foundation destination shared by MP-01 through MP-05

### Tangible claim

> We created a reusable, responsive application foundation that safely displays one static chess position.

### Product boundary

Slice 1 creates the structural and visual foundation for the application. It displays the standard chess starting position and proves that the board can be embedded safely in a reusable viewer workspace.

Slice 1 does **not**:

- parse or replay PGN;
- read positions from the database;
- step forward or backward through moves;
- allow a user to pick up or move a piece;
- highlight squares or draw analysis arrows;
- run Stockfish in either environment;
- persist a position or analysis;
- present speculative controls as if their functions exist; or
- populate empty regions with fake product content.

The absence of those functions is intentional. The purpose is to scaffold the static structure first and add the parts that move in later, separately grilled slices.

## Slice 1 — page and routing decisions

1. The static position page will have a durable dedicated route such as `/viewer`.
2. A standard client-side router will be introduced rather than implementing custom pathname switching.
3. React Router is the selected routing foundation.
4. The existing root page at `/` will retain its current backend-status purpose.
5. Both `/` and `/viewer` will use the shared site shell, proving that the shell is site-wide rather than viewer-specific.
6. The root status behavior will not be folded into the viewer or removed merely to create the new route.

### Reasoning

A dedicated viewer route preserves existing behavior and gives design work a stable product destination. Introducing the normal routing foundation now avoids custom navigation and nested-layout infrastructure once additional pages appear.

## Slice 1 — site-wide shell

### Ownership boundary

The shell owns site-wide structure:

- top navigation region;
- left navigation region;
- main-content region; and
- responsive mobile navigation behavior.

The shell does **not** own a global right context panel. Context belongs to the page or feature that understands it. For the viewer, the right context panel is inside the viewer workspace within `<main>`.

This distinction is deliberate: future pages should not inherit a chess-viewer-specific panel merely because they use the site shell.

### Identity and navigation

- The shell uses the text-only identity **Chess Move Trainer**.
- No logo or decorative brand asset is required in this slice.
- Navigation contains only real destinations.
- The Viewer destination may be shown because it exists.
- Speculative destinations must not appear as disabled controls or placeholder navigation.

### Responsive behavior

- Desktop uses a top bar and visible left sidebar.
- On narrow screens, the left navigation becomes a menu drawer.
- Opening, closing, and keyboard-dismissing the drawer are real structural behaviors and must work in Slice 1.
- Rendering an inactive drawer control would not constitute a safe responsive foundation.

## Slice 1 — reusable layout foundation

The first slice should establish a broader reusable layout system rather than only page-local markup. The goal is to avoid rebuilding the same structural concepts when subsequent pages and features arrive.

Candidate shared primitives include:

- site shell;
- navigation regions;
- main-content container;
- workspace layout;
- primary workspace region;
- contextual panel region;
- board container; and
- shared feedback presentations.

Exact component names and file ownership remain implementation-planning details, but the ownership boundaries above are settled.

### Viewer workspace

- The viewer workspace lives inside the shell's main-content region.
- It owns both the primary board area and its contextual panel.
- On desktop, the intentionally empty context panel remains visible so the real composition can be evaluated and designed.
- Empty means intentionally unpopulated; it must not be filled with fake functions or explanatory filler.
- On narrow screens, contextual content stacks below the primary content.
- When the context region is empty at that narrow layout, the empty region is omitted rather than consuming vertical space.

## Slice 1 — visual system

The broad direction below is retained as historical foundation context. The accepted MP-02-specific values,
component boundaries, proof targets, and exclusions are owned by the advisory
[design guide](../design-guides/static-position-to-analysis.md). Where this older broad-slice language is less
specific, the accepted MP-02 record governs MP-02 planning without changing later milestone boundaries.

### Direction

- The baseline aesthetic is a dark, high-contrast application and analysis workspace.
- Material Design 3 is the published color-system specification.
- The implementation must use Material semantic color roles rather than scattering literal colors through components.
- WCAG 2.2 Level AA is the accessibility target.

### Theme scope

- Slice 1 implements the dark theme only.
- Semantic tokens must be structured so another theme can be added later.
- A light theme and theme switcher are not Slice 1 requirements.
- Theme readiness must not be confused with implementing non-working theme controls.

### CSS ownership

- Inline CSS is not used.
- Shared theme values and colors live in centralized global token/theme files.
- Components own their structural and local presentation through CSS Modules.
- Shell, workspace, board, and error styles should not accumulate in one undifferentiated global component stylesheet.

The aim is to centralize design decisions while retaining clear component ownership.

## Slice 1 — reusable board contract

### Displayed position

- The page displays the standard starting position.
- It is static and read-only.
- White is displayed at the bottom.
- Rank and file coordinates are visible.

### Reusable configuration

- Board orientation is configurable even though this page uses White.
- Coordinate visibility is configurable even though this page shows coordinates.
- The board is a fluid square that uses available space up to a configurable maximum.
- It must not grow without bound on large screens or force horizontal scrolling on narrow screens.

### Safety behavior

- Invalid or unsupported position input must not silently become the standard starting position.
- A plausible fallback board could misrepresent the requested chess state and is therefore unsafe.
- Invalid input produces a contained, accessible **Position unavailable** state.
- A malformed position must not break the surrounding shell or workspace.

### Accessibility representation

Assistive technology receives more than an unlabeled visual grid. The reusable board contract includes:

- an accessible board label;
- the board orientation; and
- a concise textual description of the displayed position.

The board is not treated as decorative because the position is the page's primary information.

### Future extension boundary

Known later uses may include movement, highlighting, and analysis arrows, but none is implemented or exposed as an inactive API in Slice 1.

The selected approach is:

- establish a documented board adapter boundary;
- define clear extension points;
- expose only props and behaviors that work in Slice 1; and
- avoid speculative handlers, inactive properties, and TODO-driven public contracts.

This balances reuse with the static-first rule. Later capabilities should extend or adapt the board deliberately after their own grilling, not appear as unfinished controls now.

## Slice 1 — shared feedback foundation

Feedback presentation is shared from the beginning so feature-local status and error designs do not fracture
later. The accepted MP-02 contract is detailed in the advisory
[design guide](../design-guides/static-position-to-analysis.md).

MP-02 establishes:

- a shared semantic feedback core for information, success, warning, and error;
- reusable `InlineFeedback` presentation;
- reusable `PanelFeedback` presentation; and
- reusable `PageFeedback` presentation.

These presentations share semantic structure, accessibility treatment, fixed severity icons, and Material-theme
styling. Consumers explicitly own live-region behavior. The later position-unavailable state uses this foundation
without expanding MP-02 into board behavior.

Slice 1 does not invent application logging, notification delivery, backend recovery, or persistence workflows merely to complete an imagined error platform. Those require real consumers and separate decisions.

## Reuse philosophy

The normal rule of waiting for multiple consumers before abstracting was deliberately rejected for the layout foundation. Previous redesign costs justify establishing known shared structures early.

That decision does not authorize unlimited speculative abstraction. The agreed boundary is:

- build reusable primitives for already-known recurring structures;
- keep APIs limited to behavior that actually works;
- document extension boundaries for credible later capabilities;
- do not create fake functions, inactive controls, or speculative public props; and
- allow later grilling to decide behavior without reopening the site-wide structural foundation unnecessarily.

No design can guarantee that change will never be required. The concrete goal is to avoid foreseeable structural redesign for the known roadmap.

## MP-01 through MP-05 — confirmed technology foundation

These choices were grilled after the original broad static-foundation boundary was settled. They are part of the detailed MP-01 through MP-05 design authority. MP-01 has installed and compatibility-checked the complete stack; MP-02 through MP-05 remain pending implementation selection and introduce its real product consumers. The selections use established packages where those packages fit the existing React application and the agreed styling, accessibility, and ownership boundaries.

Versions below are the researched stable versions on 2026-08-15. The repository convention is to pin exact dependency versions. Focused planning must verify the package metadata and lockfile operation immediately before installation, but it must not silently substitute a different technology.

### Selection principles

1. Prefer maintained off-the-shelf behavior over custom implementations.
2. Keep third-party packages behind application-owned boundaries where replacement is credible.
3. Do not adopt a large framework when its design system or styling model conflicts with settled product decisions.
4. A package's future capabilities do not authorize those capabilities in Slice 1.
5. Application-owned visual decisions remain centralized through Material semantic tokens and CSS Modules.
6. Expected product failures remain ordinary typed states; unexpected render failures use an error boundary.
7. Automated accessibility tools supplement keyboard, responsive, assistive-technology, and human review. They do not prove complete WCAG conformance.

### React and build baseline

The existing pinned baseline remains in place for Slice 1:

- React `19.0.0`;
- React DOM `19.0.0`;
- TypeScript `5.7.3`;
- Vite `6.0.11`; and
- Node `>=22 <23`.

Slice 1 must not become a general React, Vite, or Node upgrade. A selected dependency must work with this baseline unless a later assessment demonstrates that a change is unavoidable and returns that decision to the frontier.

### Routing — React Router DOM 7

**Selected:** `react-router-dom` `7.18.2`, with its matching React Router dependency.

Reasons:

- It supports React 19.0.0 and Node 22.
- It provides the established client-side routing foundation required for `/` and `/viewer`.
- Current React Router 8.3.0 requires React 19.2.7 or later and Node 22.22 or later; its framework tooling also moves to Vite 7.
- Upgrading the application toolchain solely to use Router 8 would widen Slice 1 without providing a meaningful benefit for its two simple routes.
- Custom pathname and History API handling was rejected because it would duplicate established routing behavior and create a later migration.

The accepted risk is a bounded future Router 8 migration. Application routes should use conventional React Router composition and avoid unnecessary router-specific abstractions so that migration remains localized.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/react-router/latest`
- `https://registry.npmjs.org/react-router-dom/latest`
- `https://raw.githubusercontent.com/remix-run/react-router/main/CHANGELOG.md`

### Board rendering — react-chessboard behind an adapter

**Selected:** `react-chessboard` `5.12.0`.

Relevant package evidence:

- MIT license;
- explicit React and React DOM `^19.0.0` peer support;
- Node `>=20.11.0` support;
- active release and repository activity in August 2026;
- responsive and mobile board rendering;
- documented custom pieces, dimensions, styling, event handling, and later extension capabilities; and
- built-in future surfaces for arrows and square/piece customization.

The application will consume the package normally. It will not copy, vendor, fork, or rewrite selected source files. Although the MIT license permits modification with attribution, doing so would transfer chessboard maintenance to this repository and undermine the off-the-shelf goal.

The package is isolated behind an application-owned board adapter. Consumers depend on that adapter rather than importing `react-chessboard` directly. The adapter owns:

- accepted FEN input;
- safe validation before rendering;
- read-only configuration;
- board orientation;
- coordinate visibility;
- bounded responsive sizing;
- accessible label and textual position description;
- the contained position-unavailable result; and
- the narrow translation from application semantic tokens to supported package options.

The adapter preserves the option to replace the package later without changing every page that displays a board. Standard FEN remains the application-facing position representation; package-specific state must not escape the adapter.

`react-chessboard` internally uses React style objects and ships hard-coded default square colors that can be overridden. This is a confirmed, narrow exception to the prohibition on inline application CSS. Application components must not adopt that pattern. Theme values passed through the adapter must originate from the centralized theme contract rather than introduce page-local literals.

The package's movement, highlighting, arrows, drag-and-drop, and event features are not Slice 1 behavior. The adapter exposes only working read-only properties. It must not publish inactive callbacks or speculative options merely because the dependency supports them.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/react-chessboard/latest`
- `https://github.com/Clariity/react-chessboard`
- `https://raw.githubusercontent.com/Clariity/react-chessboard/main/README.md`
- `https://raw.githubusercontent.com/Clariity/react-chessboard/main/src/defaults.ts`
- `https://raw.githubusercontent.com/Clariity/react-chessboard/main/src/types.ts`

`@lichess-org/chessground` was considered and rejected for Slice 1. Its active package is framework-agnostic rather than a React component, its official documentation contains no accessibility claim, and its GPL-3.0-or-later license imposes broader redistribution obligations. The obsolete unscoped `chessground` npm package is deprecated and must not be installed accidentally.

### Position validation and inspection — chess.js

**Selected:** `chess.js` `1.4.0`.

Relevant package evidence:

- BSD-2-Clause license;
- zero runtime dependencies;
- bundled TypeScript declarations;
- ESM and CommonJS builds;
- explicit `validateFen(fen)` result handling;
- constructors and loading APIs that reject invalid FEN unless validation is deliberately skipped; and
- headless position inspection without a UI dependency.

Slice 1 uses `chess.js` only to validate FEN and obtain the position information required by the board adapter and accessible description. It must not enable movement, game replay, PGN parsing, legal-move interaction, or chess-state mutation in this slice.

A custom FEN parser was rejected because `chess.js` already owns the established syntax and position validation behavior. Passing unvalidated FEN directly to the board was rejected because the application must distinguish invalid input from the valid standard starting position.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/chess.js/latest`
- `https://github.com/jhlywa/chess.js`
- `https://jhlywa.github.io/chess.js/`

### Accessible structural primitives — Base UI

**Selected:** `@base-ui/react` `1.7.0`, used selectively behind application-owned components.

Relevant package evidence:

- MIT license;
- explicit React `^17 || ^18 || ^19` peer support;
- active monthly stable releases through August 2026;
- no bundled CSS and explicit CSS Modules support;
- WAI-ARIA Authoring Practices alignment;
- an official claim of compliance with WCAG 2.2 success criteria related to component behavior;
- documented testing across browsers, devices, platforms, and screen readers; and
- a true Drawer primitive with focus management, dismissal, swipe behavior, data-state attributes, and a documented mobile-navigation composition.

Base UI supplies behavior, not product appearance. Application-owned shell and navigation components wrap the selected primitives and style them using Material semantic tokens and CSS Modules. Base UI must not become an alternative design system or an invitation to add unused primitives.

The initial real consumer is the narrow-screen navigation drawer. Its opening, focus containment, dismissal, focus restoration, and keyboard behavior should use the established primitive rather than custom focus-management code. React Aria Components and Radix Primitives were considered; both are credible accessible libraries but require composing a drawer from lower-level modal or dialog parts. Base UI directly supplies the needed structure.

Like comparable headless libraries, Base UI may use narrowly scoped functional inline styles for overlay positioning, gestures, or scroll locking. Those package internals are third-party behavior exceptions. Application appearance remains class- and token-owned.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/@base-ui/react/latest`
- `https://base-ui.com/react/components/drawer`
- `https://base-ui.com/react/overview/accessibility`
- `https://base-ui.com/react/overview/quick-start`
- `https://base-ui.com/react/overview/releases`

### Icons — Lucide React

**Selected:** `lucide-react` `1.31.0`.

Relevant package evidence:

- ISC license, with inherited Feather icons under MIT;
- React `^19.0.0` peer support;
- active maintenance and trusted-publisher provenance;
- individually importable, tree-shakable SVG components;
- `currentColor` as the default color behavior; and
- documented accessibility behavior: decorative icons are hidden from assistive technology by default, while meaningful labels belong on their controls.

Only icons with a real Slice 1 use are imported. Menu and navigation icons inherit semantic theme colors through CSS. Icon-only controls must receive an accessible name on the control, not rely on the SVG to provide one.

Runtime Google Material Symbols were rejected because they would create external font requests and loading behavior. Self-hosted Material Symbols were also rejected for this small icon set because they would require font or asset subsetting and an additional asset pipeline. Lucide adds no runtime network request.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/lucide-react/latest`
- `https://lucide.dev/guide/packages/lucide-react`
- `https://lucide.dev/guide/react/advanced/accessibility`
- `https://lucide.dev/guide/react/basics/color`

### Material 3 implementation — specification and exported tokens

No Material component framework is selected.

MUI Material was rejected because its official documentation states that it implements Material Design 2; Material Design 3 remains a tracked open direction. Its normal `sx` and Emotion styling model also conflicts with the settled CSS Modules and no-inline-application-style ownership.

Material Web Components was rejected because, although it implements Material 3 CSS custom properties, the project officially remains in maintenance mode pending new maintainers and has no official React wrapper.

Slice 1 instead uses:

- the published Material Design 3 specification;
- a fixed dark scheme exported through the official Material Theme Builder;
- committed semantic CSS custom properties using Material role naming;
- a recorded source seed and generation settings so the palette can be reproduced; and
- component-owned CSS Modules that consume semantic variables.

The application does not generate its fixed theme at runtime. Google's `@material/material-color-utilities` was researched and remains an established Apache-2.0 algorithm library, but its documented `applyTheme` path mutates CSS custom properties on an element at runtime and it does not document static CSS-file generation. Runtime generation would add machinery and style mutation that the fixed first theme does not require.

The token source must preserve semantic pairings such as surface/on-surface and container/on-container. Exported values must still be checked against the Slice 1 WCAG 2.2 AA acceptance contract; use of an official generator is not by itself proof of every rendered contrast combination.

Official evidence retrieved during grilling:

- `https://github.com/material-foundation/material-theme-builder`
- `https://github.com/material-foundation/material-color-utilities`
- `https://registry.npmjs.org/@material/material-color-utilities/0.4.0`
- `https://material-web.dev/theming/color/`

### Typography — system font stack

Material 3 typography tokens use a native `system-ui` stack. No font is loaded from Google at runtime, and no font asset is added merely to obtain Roboto.

Official Material theming guidance identifies Roboto as the default only when the typeface is not changed and explicitly demonstrates overriding the plain typeface with `system-ui`. Material typescale roles remain centralized even though the underlying font follows the operating system.

The theme must define the required font family, size, line height, weight, and letter-spacing roles. Components consume semantic typescale variables instead of reproducing ad hoc text declarations.

Official evidence retrieved during grilling:

- `https://material-web.dev/theming/typography/`

### Responsive CSS — viewport and container queries

Responsive behavior uses native CSS rather than JavaScript resize state:

- viewport media queries control site-shell transitions such as desktop sidebar versus narrow-screen drawer; and
- CSS container queries control reusable workspace, primary-region, contextual-panel, and board-container reflow based on the space their parent provides.

This division prevents reusable components from assuming that viewport width equals their available width. `ResizeObserver`-driven React state is not used for ordinary layout switching.

### State ownership — React state and context

Slice 1 uses React component state and context only. Zustand, Redux Toolkit, and other application-state libraries are excluded.

The real state in this slice is local or structural: current route, drawer open/closed state, one immutable position input, and contained feedback state. No confirmed cross-feature ownership or synchronized server cache exists to justify a global store. A later milestone may select a state technology only after its grilling identifies a real ownership requirement.

### Unexpected rendering failures — react-error-boundary

**Selected:** `react-error-boundary` `6.1.3`.

Relevant package evidence:

- MIT license;
- explicit React `^18 || ^19` support;
- zero runtime dependencies;
- active maintenance through August 2026;
- fallback component/render support;
- reset callbacks and reset keys; and
- reporting hooks with React component-stack information.

The package is used selectively around major page or workspace regions so an unexpected rendering failure does not unnecessarily destroy the complete shell. Fallbacks use the shared typed presentation system and Material styles.

Expected errors are not thrown into an error boundary. Invalid FEN, unavailable position data, and other anticipated product outcomes remain explicit typed UI state. Error boundaries cover failures during rendering below them; they do not automatically catch event-handler errors, arbitrary asynchronous errors, server-side rendering errors, or failures in the boundary itself.

Using the package avoids maintaining a custom class-based boundary, which React still requires when implementing `getDerivedStateFromError` and `componentDidCatch` directly.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/react-error-boundary/latest`
- `https://github.com/bvaughn/react-error-boundary`
- `https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary`

### Component workshop — Storybook

**Selected:** Storybook `10.5.8` with `@storybook/react-vite` and only the addons required by the accepted Slice 1 workflow.

Relevant package evidence:

- MIT license;
- React 19, Vite 6, TypeScript 5.7, Node 22, and Vitest 3 compatibility;
- active maintenance through August 2026;
- CSS Modules and shared global CSS support through its Vite builder;
- responsive viewport tooling;
- play-function interaction tests;
- axe-backed accessibility support; and
- static Storybook build output.

Storybook is a real Slice 1 design surface because the slice intentionally establishes reusable visual foundations before later product functionality. Stories should cover meaningful states and compositions such as:

- shell at wide and constrained widths;
- navigation drawer open and closed;
- workspace with desktop empty context and constrained omission;
- board orientation and coordinate configurations actually supported by the adapter;
- valid starting position;
- position unavailable;
- inline, panel, and page-level error presentations; and
- relevant focus and interaction states.

Storybook must reuse the same committed Material tokens and CSS Modules as the application. It is not a second implementation of the components. Storybook stories do not replace application component tests or browser acceptance.

Ladle was considered and rejected. It is smaller and Vite-native, but its official tooling has no third-party addon system, weaker viewport support, and less recent release activity. Storybook better matches the explicit need for responsive design, state review, accessibility checks, and reusable-component development.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/storybook/latest`
- `https://registry.npmjs.org/@storybook/react-vite/latest`
- `https://storybook.js.org/docs/get-started/frameworks/react-vite`
- `https://storybook.js.org/docs/essentials/viewport`
- `https://storybook.js.org/docs/writing-tests/accessibility-testing`
- `https://storybook.js.org/docs/configure/styling-and-css`

### Accessibility automation

The established accessibility layers are:

- `@chialab/vitest-axe` `0.19.1` for fast component-level axe checks in the existing Vitest and React Testing Library environment;
- Storybook's maintained axe accessibility integration for isolated visual states; and
- `@axe-core/playwright` `4.13.0` for axe checks against the fully rendered application in a real browser.

The older `vitest-axe` package was rejected because its only release was in 2022 and it retains a stale axe-core dependency. The selected Chialab integration supports Vitest 3 and current axe-core peers.

Browser checks are required for rendered color contrast and layout-dependent behavior that JSDOM cannot prove. Component checks remain useful for rapid semantic regression feedback. Duplicate checks should be purposeful: shared primitives are checked close to their component, while page compositions and rendered CSS are checked in Storybook or Playwright at the appropriate acceptance layer.

Axe-core documents rules for WCAG 2.0, 2.1, and 2.2 but estimates that automated analysis finds only a portion of accessibility defects. Some WCAG 2.2 rules are disabled by default, and incomplete results require manual review. Focus order, keyboard usability, responsive drawer behavior, meaningful board description, and human comprehension remain explicit manual or interaction-test gates.

Official evidence retrieved during grilling:

- `https://registry.npmjs.org/@chialab/vitest-axe/latest`
- `https://registry.npmjs.org/@axe-core/playwright/latest`
- `https://github.com/dequelabs/axe-core`
- `https://dequeuniversity.com/rules/axe/4.13/`

### Confirmed technology exclusions

Slice 1 does not use:

- MUI Material;
- Material Web Components;
- a vendored or forked chessboard;
- the deprecated unscoped `chessground` package;
- a custom chessboard renderer;
- a custom FEN parser;
- a custom router;
- custom drawer, focus-trap, or modal-dismissal mechanics;
- Google Fonts or Material Symbols runtime requests;
- runtime Material theme generation;
- a global application-state library;
- JavaScript-driven responsive layout state where CSS can own layout;
- an inactive public API for future board capabilities; or
- axe results as a substitute for human accessibility acceptance.

### Technology decision rationale

The selected stack establishes behavior at the smallest appropriate boundary:

```text
React Router DOM -> route composition
Base UI -> accessible structural behavior
application shell/workspace components -> product ownership and Material presentation
chess.js -> FEN validation and position inspection
application board adapter -> safe, accessible, replaceable board contract
react-chessboard -> established visual board rendering
react-error-boundary -> unexpected render-failure containment
Lucide React -> small, local, semantic-color icons
Storybook -> isolated reusable-component design and review
Vitest/axe + Storybook/axe + Playwright/axe -> layered automated accessibility evidence
```

This structure uses established packages without allowing package APIs, style systems, or future capabilities to become the product contract accidentally.

## Later milestone envelopes

The following sections preserve direction only. Every unanswered branch remains open until that milestone's grilling.

### MP-06 — validated FEN corpus

#### Tangible claim

> We created a complete, validated list of chess positions for the captured games and stored it properly.

Relevant decisions preserved from the superseded PGN-to-FEN discussion:

- retain per-game ordered position sequences;
- also retain a derived deduplicated unique-position index;
- include ply zero;
- use `python-chess` rather than a custom PGN parser;
- build positions through a separate idempotent step after game fetching;
- backfill the existing captured games on the first run;
- preserve board state, side to move, castling rights, and en-passant state when normalizing uniqueness;
- normalize halfmove and fullmove counters for the unique-position identity;
- verify replay against the PGN `CurrentPosition` value when that source contract remains available; and
- keep replayable per-game FENs lossless even when the unique index uses normalization.

These preserved decisions are inputs to MP-06 grilling, not implementation authority. MP-06 grilling must confirm them against current repository state and settle all schema, ownership, failure, rerun, and proof behavior.

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

The earlier selected fixture was a real standard-position game between Skyrocoster and wasabi30, ending after 44 plies with `22...Bd3#`, sourced from Chess.com. Whether that fixture and the earlier minimal-control design remain appropriate must be reconfirmed during MP-08 grilling.

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

```text
MP-06: validated FEN corpus
├── confirm current source and replay oracle
├── confirm schema and ownership
├── settle normalization and duplicate identity
├── settle idempotency, failures, and partial runs
└── settle observable proof and corpus completeness

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
7. **Document ownership:** this one record replaces the three narrower grilling documents. The future master plan will reference this detailed record rather than absorb its contents.

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

The MP-01 through MP-05 foundation design frontier is settled. MP-01 is implemented and accepted;
MP-02 is the next implementation frontier, and MP-02 through MP-05 remain pending route selection while
their destinations, sequence, exclusions, technology stack, temporary compatibility-proof lifecycle, page
structure, shell ownership, responsive behavior, visual-system basis, styling ownership, board safety
contract, accessibility target, shared-error foundation, and reuse boundaries remain settled.

The later milestone frontier is intentionally not opened here. Each later milestone carries an explicit grilling prerequisite and an unanswered-decision branch. This preserves a coherent master-plan direction without pretending that later product behavior has already been designed.

The user explicitly confirmed this consolidated understanding and authorized recording it in detail while atomically deleting the three superseded grilling records.
