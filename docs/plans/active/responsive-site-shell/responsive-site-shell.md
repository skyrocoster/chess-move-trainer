# Responsive Site Shell - reusable shell adopted on the status page

> **Status:** Approved MP-03 Plan. Stage 1 (complete real-component Storybook shell composition) shipped
> and independently validated; Stage 2 supplies the independent layered Storybook proof and the explicit
> pre-adoption review gate; Stage 3 adopts the approved composition on `/` while preserving backend
> health behavior.

- **Read trigger:** Open after accepted MP-02 and before authoring or implementing an MP-03 stage order.

## What we're building & why

MP-03 creates one reusable responsive application shell and proves it in Storybook before production
adoption. The shell owns the text-only Chess Move Trainer identity, real Status navigation at `/`, desktop
top and left regions, the main-content boundary, and the narrow-screen Base UI drawer. Storybook renders the
same production `AppShell`, status view, feedback, and error-boundary components that will be used by `/`;
there is no parallel mock shell.

After the complete Storybook composition is explicitly approved, `/` adopts the shell. The existing health
request remains owned by `StatusPage`, and loading, healthy, and unavailable behavior, messages, abort
handling, and live-region semantics remain intact. MP-03 remains status-only: it does not add `/viewer`, a
router, a board, chess data, analysis, editing, persistence, or speculative navigation.

The [MP-03 master-plan boundary](../../../master-plans/static-position-to-analysis.md), detailed
[grilling record](../../../grilling-docs/static-position-to-analysis-roadmap.md), and selected advisory
[responsive-shell reference](../../../design-guides/mp03-responsive-shell-reference.html) govern this Plan.
The HTML reference is visual guidance only; the shipped MP-02 Material roles, `--cmt-*` tokens, and
`system-ui` typescale are the only visual source of truth.

## Settled decisions

- `AppShell` accepts page content through `children` and owns site-wide structure only. It does not own a
  viewer context panel.
- The persistent identity is text-only **Chess Move Trainer**. The status view heading is **System status**.
- MP-03 has exactly one real destination: **Status** at `/`, implemented as a native `<a href="/">` with
  visible text, Lucide `Activity`, and `aria-current="page"`. No Viewer, disabled future link, fake
  destination, or inactive control appears. MP-05 owns the React Router handoff and replaces this native
  link when it introduces `/viewer`.
- A focus-revealed **Skip to main content** link appears before the repeated header and navigation.
- Wide layout has a sticky `64px` top bar and a persistent, independently scrollable `240px` sidebar below
  it. The main content is fluid, top-aligned, has a `48rem` maximum status width, and uses `24px` wide and
  `16px` constrained layout padding.
- The viewport breakpoint is content-derived and exact: `679px` is constrained and `680px` is desktop.
  Native CSS media queries own this transition. JavaScript resize state and `ResizeObserver` layout state are
  excluded.
- Constrained layout keeps the identity on the left and exposes an icon-only **Open navigation menu**
  control. The left-edge Base UI drawer is a full-height modal surface with width `min(320px, 85vw)`, a
  scrim, inert background, body-scroll locking, a **Navigation** heading, and an icon-only **Close navigation
  menu** control.
- Base UI owns drawer focus containment, initial focus on Close, dismissal, focus restoration to the menu
  trigger, inertness, modal behavior, and keyboard behavior. Required dismissal paths are Close, `Escape`,
  scrim activation, and selecting Status. Swipe-to-close is not required. Application CSS owns only the
  short slide-and-scrim transition and removes it under `prefers-reduced-motion: reduce`.
- `StatusPage` continues to own the health request, abort behavior, and typed loading/success/error state.
  A controlled presentational status view is extracted for the shared production and Storybook surface.
  Loading and success use explicit consumer-owned `role="status"`; unavailable uses `role="alert"`.
  Existing messages and backend error detail are unchanged.
- A selective `react-error-boundary` boundary contains unexpected render failures around shell main content.
  Expected health failures remain typed `StatusPage` state and are never thrown into the boundary. The local
  fallback uses `PageFeedback` with heading **Page unavailable**, message **Something went wrong while
  displaying this page.**, and a local **Try again** button that resets the boundary. No feedback API is
  expanded with actions or recovery props.
- Shell and status presentation use separate CSS Modules. Global CSS is limited to resets and shared theme
  imports; the existing status-card presentation must not remain as a production component style. Shell-local
  structural measurements are CSS custom properties; shared color, typography, spacing, focus, and feedback
  values come directly from the accepted MP-02 token and component contract.
- Lucide supplies only real-use icons. Icon-only controls receive accessible names on the controls, not from
  the SVG. No new package, request-mocking dependency, global state library, custom modal, or custom focus
  mechanics is permitted.

## Stages

1. **SHIPPED - Build the complete real-component shell composition in Storybook:** extract the controlled
   status view, create the feature-owned shell, drawer, and content error boundary, and expose all accepted
   states through Storybook stories and focused component proof without changing production `App.tsx`.
2. **SHIPPED - Prove and review the complete Storybook composition before adoption:** run Storybook interaction
   and axe proof plus browser proof at every required width, then stop for explicit human approval of the
   complete composition. This gate is review only, not implementation work, and no production composition
   change may precede it.
3. **ORDERED - Adopt the approved shell on `/`:** compose the unchanged health page inside `AppShell`, wire
   production token/reset imports and CSS ownership, preserve the temporary Foundation Check as a regression
   surface, and prove the production page at wide, constrained, and breakpoint-edge widths.

## Shipped

| Stage | What shipped (<=2 sentences) |
|-------|------------------------------|
| 1 | Stage 1 shipped the complete real-component Storybook composition: the controlled `StatusView` (System status heading, exact existing loading/healthy/unavailable copy, explicit status/alert roles), the feature-owned `AppShell` (skip link, text-only identity, sticky 64px top bar, 240px sidebar, constrained Base UI drawer with initial Close focus and owned dismissal/restoration, native Status link with `aria-current`), and the `PageContentBoundary` (Page unavailable exact copy plus local Try again reset), proven by focused component/axe tests and a compiling Storybook; production `App.tsx` and `/` remain unchanged pending the Stage 2 pre-adoption gate. |
| 2 | Stage 2 shipped the independent layered Storybook proof and the explicit pre-adoption review gate: build-storybook PASS, test-storybook 20/20, and the real-iframe responsive browser spec 18/18 across 1920x1080, 412x915, 679px, and 680px (desktop/constrained modes, drawer modality and every dismissal/focus path, reduced motion, exact live-region states, unexpected-failure recovery, clean application-owned axe), completed by one deterministic in-scope synchronization repair in the authorized spec. The complete Storybook composition received explicit human pre-adoption approval, so Stage 3 may adopt it on `/`. |

## Touches

- `frontend/src/App.tsx`
- `frontend/src/app.css`
- `frontend/src/features/`
- `frontend/src/features/status/`
- `frontend/src/features/foundation/`
- **Depends on:** [Material Design Foundation](../../done/material-design-foundation/material-design-foundation.md)

The `frontend/src/features/` ownership glob is intentionally narrowed by the compiler handoff below: new
shell files belong under `frontend/src/features/app-shell/`, and status edits are limited to the named
symbols. It does not authorize changes to design-system, chess, viewer, backend, or unrelated feature paths.

### Verification-only paths

These paths provide proof or compatibility regression evidence and are not unconditional implementation
ownership. An order may authorize a path only when the stage proof requires it and names the exact edit:

- `tests/e2e/responsive-shell-storybook.spec.ts` - new Storybook browser proof for Stage 2.
- `tests/e2e/responsive-shell.spec.ts` - new production browser proof for Stage 3.
- `tests/e2e/status.spec.ts` - existing production status regression proof; update only for the accepted
  heading/identity composition if its locator depends on the old heading.
- `frontend/src/features/status/StatusPage.test.tsx` - existing health lifecycle proof; preserve its
  fetch, abort, loading, success, and error assertions.

The temporary Foundation Check paths are implementation-owned only for the exact CSS compatibility migration
named in Stage 3; they are not a general regression target. Do not add product behavior or retire the check;
MP-05 owns retirement.

## Acceptance

Every stage is independently reviewable and requires an explicit human acceptance decision before the next
stage. Automated axe, component, Storybook, and browser checks supplement but do not replace manual
keyboard, focus, responsive, visual, and WCAG 2.2 AA review.

### Stage 1 human gate

Review the complete Storybook composition using the real `AppShell`, controlled status view, MP-02
`InlineFeedback`, and content error boundary. At `1920x1080`, confirm the sticky top bar, visible 240px
sidebar, main boundary, identity, active native Status link, and top-aligned status states. At `412x915`,
confirm the closed constrained shell and open drawer. Exercise menu-trigger focus, initial focus on Close,
focus containment, Close, `Escape`, scrim, Status selection, and focus restoration. Review loading, healthy,
unavailable, reduced-motion, and Page unavailable/Try again states. Confirm no `/viewer`, board, fake link,
future control, request mock dependency, router, or production `App.tsx` change exists.

**Stop:** Do not begin production adoption. The Storybook composition must be complete before Stage 2's
independent proof and the explicit pre-adoption gate.

### Stage 2 human gate

Review the complete Storybook composition and its rendered browser proof at exact targets `1920x1080`,
`412x915`, `679px`, and `680px` (use a stable review height for width-edge checks). Confirm `679px` uses the
drawer mode and `680px` uses the desktop sidebar, with no layout decision made by JavaScript. Confirm axe
results are clean for application-owned content, and manually inspect focus order, keyboard operation,
scrim dismissal, focus restoration, reduced motion, contrast, and comprehension.

**Explicit pre-adoption gate:** a human must approve the complete Storybook composition after this stage.
Record that approval before authorizing any order that modifies production `frontend/src/App.tsx`. If the
composition is not approved, stop and return to the Plan frontier; do not begin a partial production shell.

### Stage 3 final human gate

Open production `/` at `1920x1080`, `412x915`, `679px`, and `680px`. Confirm the accepted wide/constrained
shell, all drawer dismissal and focus paths, reduced-motion behavior, native Status navigation, and absence
of `/viewer`. Exercise backend healthy and unavailable responses and confirm the unchanged health purpose,
messages, abort behavior, and `status`/`alert` semantics. Confirm an unexpected render failure preserves the
shell and exposes the exact Page unavailable message plus local Try again recovery through the Storybook and
component proof. Stop after MP-03 acceptance; do not begin MP-04 or MP-05.

## Exclusions

- `/viewer`, production React Router composition, router-aware navigation, Viewer navigation, fake or disabled
  future destinations, and any MP-05 handoff behavior beyond preserving the native Status link contract.
- Board rendering, `react-chessboard`, `chess.js`, FEN, PGN, board/context/workspace regions, stored data,
  traversal, analysis, Stockfish, editing, persistence, or backend changes.
- New packages, request-mocking dependencies, global state libraries, JS resize state,
  `ResizeObserver`-driven layout switching, custom drawer/focus-trap/modal mechanics, or swipe-to-close as a
  required behavior.
- New feedback severities, feedback actions, recovery props, new feedback APIs, notification infrastructure,
  or throwing expected health failures into the error boundary.
- A parallel Storybook mock, screenshot baselines, visual-regression service, custom icon set, logo, runtime
  font request, light theme, theme switcher, literal page-local colors, inline application CSS, or a second
  shell implementation.
- Product implementation while this Plan is being written, unrelated worktree cleanup, commits, pushes,
  reconciliation, or MP-01 Foundation Check retirement.

## Automated proof contract

Commands are run from the repository root in the documented Windows environment. Storybook commands that
use `test-storybook` require a Storybook server at `http://127.0.0.1:6006`; the existing Playwright
configuration starts backend, frontend, and Storybook servers for browser specs.

### Stage 1 focused proof

```powershell
npm run test --prefix frontend -- --run src/features/status/StatusView.test.tsx src/features/app-shell/AppShell.test.tsx src/features/app-shell/PageContentBoundary.test.tsx
npm run test --prefix frontend -- --run src/features/status/StatusPage.test.tsx
npm run build-storybook --prefix frontend
```

The focused tests must cover the controlled state map and exact copy, explicit live-region semantics, shell
landmarks and native link, skip link, drawer open/close behavior and accessible names, Base UI ownership of
focus/dismissal/restoration, local error fallback and reset, CSS breakpoint declarations, token reuse, and
component-level axe checks. Storybook stories must contain play proofs for the drawer and error recovery.

### Stage 2 layered Storybook proof

```powershell
npm run build-storybook --prefix frontend
npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006
.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\responsive-shell-storybook.spec.ts
```

The Storybook browser spec must visit the real component iframe, set `1920x1080`, `412x915`, `679x915`, and
`680x915` viewports, verify the corresponding shell modes, exercise drawer modality and all required
dismissal/focus paths, inspect loading/healthy/unavailable and unexpected-failure recovery, run
`@axe-core/playwright`, and verify reduced-motion CSS behavior. It must not add a request mock or a parallel
rendering fixture.

### Stage 3 production proof and regression

```powershell
npm run test --prefix frontend -- --run src/features/status/StatusView.test.tsx src/features/status/StatusPage.test.tsx src/features/app-shell/AppShell.test.tsx src/features/app-shell/PageContentBoundary.test.tsx
.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\responsive-shell.spec.ts tests\e2e\status.spec.ts
npm run lint --prefix frontend
npm run build --prefix frontend
.\frontend\node_modules\.bin\prettier.cmd --check frontend
powershell -ExecutionPolicy Bypass -File .\check.ps1
```

Production browser proof must use the live backend for healthy behavior and the existing Playwright route
abort pattern for unavailable behavior. It must verify the four exact review widths, `/` preservation,
native link behavior, drawer modality, focus restoration, rendered CSS, and no `/viewer` or board. The full
check remains the final repository regression gate.

### Documentation-check baseline

Before this Plan was written, `.venv\Scripts\python.exe scripts/check_docs.py --check` had a known baseline
failure caused by unrelated tracked deletions of `docs/design-guides/static-position-to-analysis.md` and
`docs/design-guides/mp02-visual-reference.html`. MP-03 orders must not restore, modify, or claim ownership
of those files. Documentation proof must report that baseline separately from any Plan or order error.

## Compiler handoff

### Stage 1 - complete Storybook composition

- **Route:** `ORDERED`.
- **Dependency:** Accepted MP-02 at `docs/plans/done/material-design-foundation/material-design-foundation.md`.
- **Verified edit sites:**
  - `frontend/src/features/status/StatusPage.tsx` - `StatusPage`, currently owns `ViewState`, the
    `AbortController`, `fetchHealth`, and loading/success/error Promise handling. Preserve the effect,
    abort cleanup, and error-detail conversion; replace only the local render branch with `StatusView`.
  - `frontend/src/features/status/statusApi.ts` - `fetchHealth` is the existing backend health boundary;
    no API or request behavior change is authorized.
  - `frontend/src/App.tsx` - currently renders only `<StatusPage />`; leave it unchanged through Stages 1
    and 2 so production adoption is downstream of the human gate.
  - `frontend/src/features/design-system/feedback/InlineFeedback.tsx` - thin wrapper over
    `FeedbackCore`; it accepts `FeedbackProps` and adds no live-region defaults. StatusView must supply
    explicit `role` values as the consumer.
  - `frontend/src/features/design-system/feedback/PageFeedback.tsx` - thin page wrapper; it has no action
    API. The error fallback composes a local button beside it rather than changing this component.
  - `frontend/src/features/design-system/feedback/feedbackTypes.ts` - accepted severity set is
    information/success/warning/error, with required message, optional heading, and five consumer-owned
    live attributes. Do not add a loading severity or recovery prop.
  - `frontend/src/features/foundation/FoundationCheck.tsx` - current temporary harness uses Base UI
    `Collapsible`, Lucide, and `react-error-boundary`; it is evidence only and is not a shell precedent.
  - `frontend/.storybook/preview.tsx` - current preview loads `app.css` and the generated dark Material
    CSS inside the existing dark decorator. New stories may import the accepted MP-02 token/type CSS using
    the existing story pattern; do not create another visual implementation or change preview behavior in
    this stage unless an order proves the import is required.
- **Proposed new shell ownership:**
  - `frontend/src/features/app-shell/AppShell.tsx` - `AppShell({ children })` owns the skip link, identity,
    desktop header/sidebar, constrained trigger, one shared Status navigation item, Base UI Drawer wiring,
    `<main id="main-content">`, and the `PageContentBoundary` around main content. Keep navigation data
    local and limited to Status at `/`; render the same navigation item in desktop and drawer regions.
  - `frontend/src/features/app-shell/AppShell.module.css` - owns shell structure and measurements,
    desktop/constrained CSS at `max-width: 679px`, drawer/scrim transition, focus-visible treatment, and
    reduced-motion override. Use `--md-sys-*`, `--cmt-*`, and shell-local `64px`/`240px` custom properties;
    do not use literal application colors or inline styles.
  - `frontend/src/features/app-shell/AppShell.stories.tsx` - Storybook composition story using the real
    AppShell, StatusView, InlineFeedback-backed state, and PageContentBoundary. Stories cover wide healthy,
    constrained closed/open, loading, healthy, unavailable, and unexpected failure/Try again states.
  - `frontend/src/features/app-shell/AppShell.test.tsx` - component semantics, landmarks, native link,
    skip link, menu accessible names, Base UI drawer interaction, focus paths, and component axe proof.
  - `frontend/src/features/app-shell/PageContentBoundary.tsx` - thin application-owned wrapper around
    `react-error-boundary` for render failures below main content. Its fallback calls the package reset
    callback from the local Try again button and composes the exact PageFeedback copy.
  - `frontend/src/features/app-shell/PageContentBoundary.module.css` - owns only the fallback/action layout
    and focus treatment; no feedback API or global rule.
  - `frontend/src/features/app-shell/PageContentBoundary.test.tsx` - throws a test-only render failure,
    asserts shell-preserving fallback copy and button, then verifies reset recovery without treating the
    expected StatusPage error as a boundary failure.
  - `frontend/src/features/status/StatusView.tsx` - controlled presentational view accepting the existing
    discriminated state `{ kind: "loading" } | { kind: "success" } | { kind: "error"; message: string }`.
    It renders **System status** and maps loading to information plus `role="status"`, success to success
    plus `role="status"`, and error to error plus `role="alert"`; exact existing messages remain unchanged.
  - `frontend/src/features/status/StatusView.module.css` - owns status presentation only, including the
    `48rem` maximum width and status-local spacing. It consumes accepted typescale, surface, border, focus,
    and spacing tokens.
  - `frontend/src/features/status/StatusView.test.tsx` - renders all three controlled states, asserts exact
    copy and explicit roles, verifies backend error detail, and runs focused axe proof without a network.
- **Verified state flow:** `StatusPage` effect -> `fetchHealth` -> existing discriminated state ->
  `StatusView`; `StatusView` props -> `InlineFeedback` with explicit consumer role; unexpected render below
  shell main -> `react-error-boundary` -> local `PageFeedback` plus Try again -> boundary reset. Expected
  health failure never enters the boundary. Storybook supplies `StatusView` state directly and never mocks
  `fetch`.
- **Verified consumers and defaults:** `frontend/src/App.tsx` is the only production consumer of
  `StatusPage`; `frontend/src/main.tsx` imports `app.css`; no current shell or Drawer consumer exists.
  Existing Base UI usage is `Collapsible` in `FoundationCheck`, so Drawer API usage must be verified against
  the installed `@base-ui/react` 1.7.0 `Drawer` parts and its CSS Modules guidance, not copied from a
  project-local precedent. There is no current error-boundary production consumer or Storybook shell story.
- **Settled contracts:** `@base-ui/react/drawer` owns modal behavior; Lucide `Activity`, `Menu`, and `X`
  are imported individually and hidden SVGs receive names from their controls; `AppShell` exposes only
  `children`; no route context or router is introduced; no JS width state, custom focus trap, custom scrim
  dismissal, or swipe requirement is added.
- **Focused proof:**
  `npm run test --prefix frontend -- --run src/features/status/StatusView.test.tsx src/features/app-shell/AppShell.test.tsx src/features/app-shell/PageContentBoundary.test.tsx`;
  `npm run test --prefix frontend -- --run src/features/status/StatusPage.test.tsx`;
  `npm run build-storybook --prefix frontend`.
- **Human acceptance:** Complete composition is reviewable in Storybook at `1920x1080` and `412x915`, with
  exact edge widths reserved for Stage 2. Confirm all stated states, focus behavior, token use, and absence
  of production adoption.
- **Constraints:** no changes to `App.tsx`, no new packages, no request-mocking dependency, no `/viewer`,
  no production router, no board/chess/data/analysis behavior, no new feedback API, and no changes to
  unrelated design-system or Foundation behavior.
- **Open questions:** none. The exact installed Base UI import/part signatures are a bounded implementation
  lookup, not a product or accessibility decision; the accepted Drawer behavior and CSS ownership above are
  fixed.

### Stage 2 - independent Storybook proof and pre-adoption gate

- **Route:** `ORDERED`.
- **Dependency:** Stage 1 human acceptance and complete Storybook composition; production `App.tsx` remains
  untouched.
- **Verified edit sites:** `tests/e2e/playwright.config.ts` - existing configuration starts backend on 5666,
  frontend on 8444, and Storybook on 6006; preserve the server layout and `reuseExistingServer` behavior.
  No config or package change is needed. The new proof path is
  `tests/e2e/responsive-shell-storybook.spec.ts`, classified as verification-only.
- **Verified Storybook target:** the `AppShell` story must be addressable through its real Storybook iframe
  URL and must render production components, not a fixture copy. The browser proof sets `1920x1080`,
  `412x915`, `679x915`, and `680x915`; the width-edge height is only a stable test height and does not
  alter the product breakpoint contract.
- **Required browser assertions:** desktop sidebar visible at 1920 and 680, constrained menu trigger and
  hidden desktop sidebar at 412 and 679; drawer title/close/name, initial Close focus, focus containment,
  Close/Escape/scrim/Status dismissal, trigger focus restoration, inert/scroll behavior supplied by Base UI;
  reduced-motion transition suppression; loading/healthy/unavailable exact copy and roles; Page unavailable
  exact copy and Try again recovery; and `@axe-core/playwright` results for application-owned content.
- **Focused proof:**
  `npm run build-storybook --prefix frontend`;
  `npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`;
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\responsive-shell-storybook.spec.ts`.
- **Human acceptance:** inspect the rendered Storybook composition at all four exact targets and approve
  the complete shell, status, drawer, focus, motion, and failure composition explicitly. Automated proof is
  supplemental and cannot write this approval.
- **Constraints:** no `frontend/src/App.tsx` edit, no production CSS adoption, no route, no new package, no
  mock dependency, no parallel Storybook component, and no stage-3 work in the same order.
- **Open questions:** none. If the Storybook server or exact iframe story id is unavailable, stop with the
  command/output and return to the compiler; do not weaken the browser proof or bypass the human gate.

### Stage 3 - production adoption on `/`

- **Route:** `ORDERED`.
- **Dependency:** explicit human approval of the complete Stage 2 Storybook composition. A production order
  is invalid without that approval.
- **Verified edit sites:**
  - `frontend/src/App.tsx` - current five-line StatusPage-only composition becomes the single approved
    production composition `<AppShell><StatusPage /></AppShell>`, with no router and no second destination.
  - `frontend/src/app.css` - current global `Inter`/blue status-card stylesheet is the old production page
    presentation. Replace it with reset and shared-theme imports only, including the generated dark Material
    roles and accepted `cmt-tokens.css`/`cmt-typescale.css`; move shell/status presentation to their separate
    CSS Modules and remove the old global status-card declarations.
  - `frontend/src/features/status/StatusPage.tsx` and `StatusView.tsx` - preserve the health effect, abort
    cleanup, request boundary, exact messages, and explicit roles while the view renders inside the shell.
  - `tests/e2e/status.spec.ts` - existing production proof currently locates the old Chess Move Trainer
    heading as the status heading. Update only the locator/assertions needed for the accepted split identity
    and **System status** heading, while retaining live healthy and aborted unavailable checks.
  - `tests/e2e/responsive-shell.spec.ts` - new verification-only production proof using the existing
    Playwright configuration, live health endpoint for success, and existing route-abort pattern for failure.
  - `frontend/src/features/foundation/FoundationCheck.tsx` and
    `frontend/src/features/foundation/FoundationCheck.module.css` - move the current `status-card`
    presentation into a named FoundationCheck CSS Module class and remove the old global card rule; do not
    retire, route, or turn the Foundation Check into product UI.
- **Verified production state flow:** browser `/` -> `AppShell` identity/navigation/drawer -> shell main
  `PageContentBoundary` -> `StatusPage` effect and `fetchHealth` -> `StatusView` -> `InlineFeedback`. A
  backend rejection remains `StatusView` error state with `role="alert"`; a render exception alone reaches
  PageContentBoundary and leaves the shell/navigation available. `/` remains the only route and Status stays
  a native link until MP-05.
- **Consumers/defaults:** `frontend/src/main.tsx` continues to import `app.css` and render `App`; backend
  `backend/app/main.py` and `GET /api/health` are untouched. No router context, location state, global store,
  or request mock is introduced. Existing StatusPage tests remain the health lifecycle regression suite.
- **CSS constraints:** global CSS imports only shared generated dark theme, accepted application tokens and
  typescale, plus resets; app-shell and status modules own structure; shell custom properties own only
  `64px`, `240px`, and related structural measurements; use accepted semantic roles and focus treatment;
  use native media queries at `max-width: 679px`; add reduced-motion override; no inline application CSS.
- **Focused proof:**
  `npm run test --prefix frontend -- --run src/features/status/StatusView.test.tsx src/features/status/StatusPage.test.tsx src/features/app-shell/AppShell.test.tsx src/features/app-shell/PageContentBoundary.test.tsx`;
  `.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\responsive-shell.spec.ts tests\e2e\status.spec.ts`;
  `npm run lint --prefix frontend`;
  `npm run build --prefix frontend`;
  `.\frontend\node_modules\.bin\prettier.cmd --check frontend`;
  `powershell -ExecutionPolicy Bypass -File .\check.ps1`.
- **Human acceptance:** production review at `1920x1080`, `412x915`, `679px`, and `680px`; healthy and
  unavailable backend states; complete drawer keyboard/pointer/focus paths; reduced motion; exact identity,
  heading, link, feedback, and error copy; and explicit confirmation that no `/viewer` or future behavior was
  added.
- **Constraints:** this is the only stage allowed to edit production `App.tsx`; it may not begin without the
  Stage 2 approval. Do not modify backend, package manifests, router behavior, Foundation Check retirement,
  or unrelated worktree files. Stop after MP-03 acceptance before MP-04.
- **Open questions:** none. The documentation-check baseline failure from the unrelated deleted design-guide
  files must be reported verbatim if `check.ps1` or `check_docs.py` includes it; those files are outside this
  Plan and must not be restored.
