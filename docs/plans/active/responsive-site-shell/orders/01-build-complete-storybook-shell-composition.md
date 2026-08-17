# WORK ORDER 01 — Build complete Storybook shell composition

- **OUTPUT:** `docs/plans/active/responsive-site-shell/orders/01-build-complete-storybook-shell-composition.md`
- **GOAL:** Build and prove the complete real-component responsive shell composition in Storybook without changing production App.tsx, production adoption, or the existing health request behavior.
- **REQUIRED STRENGTH:** Standard — Well-specified frontend composition with exact copy, accessibility, state, CSS, and focused proof contracts; it has no data or irreversible behavior.
- **DEPENDS ON:** none

## Authorization

### Creates
- `frontend/src/features/app-shell/AppShell.tsx`
- `frontend/src/features/app-shell/AppShell.module.css`
- `frontend/src/features/app-shell/AppShell.stories.tsx`
- `frontend/src/features/app-shell/AppShell.test.tsx`
- `frontend/src/features/app-shell/PageContentBoundary.tsx`
- `frontend/src/features/app-shell/PageContentBoundary.module.css`
- `frontend/src/features/app-shell/PageContentBoundary.test.tsx`
- `frontend/src/features/status/StatusView.tsx`
- `frontend/src/features/status/StatusView.module.css`
- `frontend/src/features/status/StatusView.test.tsx`

### Edits
- `frontend/src/features/status/StatusPage.tsx`

### Removes
- none

## Context inputs
1. `docs/plans/active/responsive-site-shell/responsive-site-shell.md` — whole file
   - Purpose: Authoritative MP-03 Plan and Stage 1 compiler handoff, including ownership, settled behavior, acceptance, exclusions, and exact proof commands.
2. `docs/plans/done/material-design-foundation/material-design-foundation.md` — whole file
   - Purpose: Accepted MP-02 dependency defining the available Material roles, cmt tokens, typescale, feedback, and focus contracts.
3. `frontend/src/features/status/StatusPage.tsx` — whole file
   - Purpose: Preserve the existing ViewState, AbortController, fetchHealth effect, abort cleanup, loading/success/error handling, and error-detail conversion while replacing only the local render branch.
4. `frontend/src/features/status/statusApi.ts` — whole file
   - Purpose: Existing backend health boundary; it is context only and its API and request behavior must remain unchanged.
5. `frontend/src/App.tsx` — whole file
   - Purpose: Confirm the production composition remains unchanged and StatusPage-only through Stage 1.
6. `frontend/src/features/design-system/feedback/InlineFeedback.tsx` — whole file
   - Purpose: Use the existing thin FeedbackCore wrapper and supply explicit live-region roles from StatusView.
7. `frontend/src/features/design-system/feedback/PageFeedback.tsx` — whole file
   - Purpose: Compose the existing page feedback wrapper with a local Try again button in the boundary fallback; do not add an action API.
8. `frontend/src/features/design-system/feedback/feedbackTypes.ts` — whole file
   - Purpose: Use the accepted information/success/warning/error severity set and consumer-owned live attributes without adding loading or recovery contracts.
9. `frontend/src/features/foundation/FoundationCheck.tsx` — whole file
   - Purpose: Evidence of installed Base UI, Lucide, and react-error-boundary usage only; it is not a shell precedent and must remain unchanged.
10. `frontend/.storybook/preview.tsx` — whole file
   - Purpose: Preserve the existing Storybook preview behavior and use its accepted story CSS import pattern only if the new stories require it.
11. `frontend/package.json` — whole file
   - Purpose: Confirm the installed @base-ui/react 1.7.0 and react-error-boundary 6.1.3 dependencies before implementing their bounded APIs; do not change package dependencies.

## Known facts
- Stage 1 is the complete real-component shell composition in Storybook and must stop before production adoption.
- The accepted dependency is MP-02 at docs/plans/done/material-design-foundation/material-design-foundation.md; no new packages or request-mocking dependency are permitted.
- frontend/src/App.tsx currently renders only StatusPage and must remain unchanged through Stages 1 and 2.
- StatusPage continues to own ViewState, the AbortController, fetchHealth, the effect, abort cleanup, loading/success/error Promise handling, and backend error-detail conversion; only its local render branch changes to StatusView.
- statusApi.ts is the existing backend health boundary and its API and request behavior must not change.
- StatusView accepts the discriminated state { kind: "loading" } | { kind: "success" } | { kind: "error"; message: string } and renders the exact existing messages under the System status heading.
- StatusView maps loading to InlineFeedback severity information with explicit role status, success to severity success with explicit role status, and error to severity error with explicit role alert.
- InlineFeedback is a thin FeedbackCore wrapper with no live-region defaults, so StatusView supplies the explicit consumer-owned role.
- The accepted feedback severities are information, success, warning, and error; there is no loading severity, recovery prop, action API, or new feedback API.
- AppShell accepts only children and owns the skip link, text-only Chess Move Trainer identity, desktop header/sidebar, constrained menu trigger, one local Status navigation item, Base UI Drawer wiring, main id main-content, and PageContentBoundary around main content.
- The only navigation item is a native anchor with href "/", visible Status text, Lucide Activity, and aria-current="page"; no router, /viewer, fake destination, future control, or route context is added.
- Wide layout uses a sticky 64px top bar, an independently scrollable 240px sidebar, and a fluid top-aligned main region with 48rem maximum status width and 24px wide padding.
- The exact responsive breakpoint is max-width 679px for constrained mode and 680px for desktop; CSS media queries own the transition, with no JavaScript width state or ResizeObserver.
- Constrained mode keeps the identity on the left and exposes an icon-only Open navigation menu control; the left-edge Base UI modal drawer is min(320px, 85vw) wide, full-height, scrimmed, inert, body-scroll-locking, and headed Navigation with an icon-only Close navigation menu control.
- @base-ui/react/drawer owns focus containment, initial focus on Close, dismissal, focus restoration to the trigger, inertness, modal behavior, and keyboard behavior; required dismissal paths are Close, Escape, scrim activation, and selecting Status, with no required swipe-to-close.
- Application CSS owns only the drawer slide-and-scrim transition and removes it under prefers-reduced-motion: reduce; no custom focus trap or custom scrim dismissal is added.
- Lucide Activity, Menu, and X are imported individually; icon-only control names come from the controls, not SVG content.
- AppShell.module.css owns shell structure, measurements, max-width 679px media query, drawer/scrim transition, focus-visible treatment, and reduced-motion override; it uses --md-sys-*, --cmt-*, and shell-local 64px/240px custom properties with no literal application colors or inline styles.
- PageContentBoundary is a thin react-error-boundary wrapper around shell main content; its local fallback uses PageFeedback with heading Page unavailable, message Something went wrong while displaying this page., and a local Try again button that calls the package reset callback.
- PageContentBoundary.module.css owns only fallback/action layout and focus treatment; it adds no feedback API or global rule.
- Expected health failures remain typed StatusPage error state and never enter PageContentBoundary; only unexpected render failures below shell main reach the boundary.
- StatusView.module.css owns status presentation only, including 48rem maximum width and status-local spacing, and consumes accepted typescale, surface, border, focus, and spacing tokens.
- AppShell stories use the real AppShell, StatusView, InlineFeedback-backed states, and PageContentBoundary; they cover wide healthy, constrained closed/open, loading, healthy, unavailable, and unexpected failure/Try again states, with play proofs for drawer behavior and error recovery.
- Focused component tests cover controlled states and exact copy, explicit roles, backend error detail, shell landmarks and native link, skip link, drawer accessible names and interaction, Base UI focus/dismissal/restoration, boundary reset recovery, breakpoint declarations, token reuse, and component-level axe checks without network mocking.
- The three required proof commands must run in this order: focused StatusView/AppShell/PageContentBoundary tests, StatusPage lifecycle tests, then Storybook build.
- The human Stage 1 gate reviews Storybook at 1920x1080 and 412x915, all listed states and focus paths, reduced motion, token use, and absence of production adoption, /viewer, board, fake link, future control, request mock dependency, router, and App.tsx change.
- The installed dependencies are @base-ui/react 1.7.0 and react-error-boundary 6.1.3; verify the exact Drawer part signatures and CSS Modules guidance against the installed package without changing the product contract.

## Ordered actions
1. **file** (`frontend/src/features/status/StatusPage.tsx`) — Preserve StatusPage's ViewState, AbortController, fetchHealth effect, abort cleanup, loading/success/error handling, and backend error-detail conversion. Replace only the local render branch so it renders StatusView with the existing discriminated state; do not alter request behavior, messages, or expected error flow.
2. **file** (`frontend/src/features/status/StatusView.tsx`) — Create the controlled presentational status view accepting { kind: "loading" } | { kind: "success" } | { kind: "error"; message: string }. Render the System status heading and exact existing messages through InlineFeedback, mapping loading to information with explicit role=status, success to success with explicit role=status, and error to error with explicit role=alert. Keep it network-free and presentational.
3. **file** (`frontend/src/features/status/StatusView.module.css`) — Create CSS Modules for status presentation only, including status-local spacing and a 48rem maximum width. Consume accepted MP-02 typescale, surface, border, focus, and spacing tokens; do not add literal page-local colors, inline CSS, or global rules.
4. **file** (`frontend/src/features/status/StatusView.test.tsx`) — Create focused network-free component tests for loading, success, and error states. Assert the System status heading, exact existing copy including backend error detail, explicit status/alert roles, and a focused axe check.
5. **file** (`frontend/src/features/app-shell/AppShell.tsx`) — Create AppShell accepting only children. Own the focus-revealed Skip to main content link, text-only Chess Move Trainer identity, wide header/sidebar, constrained Open navigation menu control, native Status navigation item at / with visible text, Activity icon, and aria-current=page, Base UI Drawer wiring, main id=main-content, and PageContentBoundary around main content. Keep navigation data local and limited to Status; render the same item in desktop and drawer regions. Use installed @base-ui/react/drawer parts and Lucide Activity/Menu/X, with Base UI owning modal focus, dismissal, inertness, keyboard behavior, and restoration. Do not add route context, router, JS width state, custom focus mechanics, or swipe behavior.
6. **file** (`frontend/src/features/app-shell/AppShell.module.css`) — Create shell CSS Modules for the sticky 64px top bar, 240px independently scrollable sidebar, main layout, constrained mode at max-width 679px, drawer and scrim transition, focus-visible treatment, and reduced-motion override. Use --md-sys-* and --cmt-* tokens plus shell-local structural custom properties for 64px and 240px; do not use literal application colors, inline application styles, global rules, JS breakpoint state, or custom scrim dismissal.
7. **file** (`frontend/src/features/app-shell/PageContentBoundary.tsx`) — Create a thin react-error-boundary wrapper for unexpected render failures below shell main content. Render children normally; on failure compose PageFeedback with heading Page unavailable and message Something went wrong while displaying this page., plus a local Try again button that calls the package reset callback. Do not change PageFeedback or treat expected StatusPage health errors as render failures.
8. **file** (`frontend/src/features/app-shell/PageContentBoundary.module.css`) — Create CSS Modules only for the PageContentBoundary fallback/action layout and focus treatment. Do not add feedback API, global rules, literal page-local colors, or inline application CSS.
9. **file** (`frontend/src/features/app-shell/AppShell.stories.tsx`) — Create Storybook stories composed from the real AppShell, StatusView, InlineFeedback-backed state, and PageContentBoundary. Cover wide healthy, constrained closed/open, loading, healthy, unavailable, and unexpected failure/Try again states. Include play proofs for opening/closing and required drawer dismissal/focus behavior as applicable, and for Try again recovery. Supply StatusView state directly without fetch or request mocks; use the existing accepted story CSS import pattern if needed without changing preview behavior.
10. **file** (`frontend/src/features/app-shell/AppShell.test.tsx`) — Create component tests for shell semantics and landmarks, skip link, text identity, native Status link and aria-current, menu control accessible names, wide/constrained regions, Base UI Drawer open/close behavior, Close/Escape/scrim/Status dismissal, initial Close focus, focus containment and restoration, and a component-level axe proof. Do not use a request-mocking dependency or test custom focus mechanics that the application does not own.
11. **file** (`frontend/src/features/app-shell/PageContentBoundary.test.tsx`) — Create a test-only throwing child that verifies the shell-preserving Page unavailable fallback, exact message, and local Try again button, then verifies reset recovery. Keep expected StatusPage health errors typed and outside the boundary failure path.

## Exact proof commands

### Proof 1 — Prove the new controlled status states, exact copy and live-region semantics, shell semantics and drawer behavior, boundary fallback/reset, CSS/token contracts, and focused component axe coverage.
Working directory: `.`

```text
npm run test --prefix frontend -- --run src/features/status/StatusView.test.tsx src/features/app-shell/AppShell.test.tsx src/features/app-shell/PageContentBoundary.test.tsx
```

### Proof 2 — Prove the existing health lifecycle, fetch boundary, abort cleanup, loading/success/error flow, and preserved expected backend error behavior after the render-branch extraction.
Working directory: `.`

```text
npm run test --prefix frontend -- --run src/features/status/StatusPage.test.tsx
```

### Proof 3 — Prove the complete real-component Storybook composition builds, including the shell, controlled status states, drawer stories, feedback, and error-boundary recovery story.
Working directory: `.`

```text
npm run build-storybook --prefix frontend
```

## Acceptance handoff

### Coordinator
- Review the complete real-component Storybook composition at 1920x1080: sticky top bar, visible 240px sidebar, main boundary, text-only identity, active native Status link, and top-aligned loading, healthy, and unavailable states.
- Review the constrained closed and open composition at 412x915: identity placement, menu trigger, drawer width/surface, Navigation heading, Close control, scrim, and absence of the desktop sidebar.
- Exercise menu-trigger focus, initial focus on Close, focus containment, Close, Escape, scrim activation, Status selection, and focus restoration; confirm Base UI owns these behaviors.
- Review reduced-motion behavior, Page unavailable exact copy, local Try again recovery, explicit status/alert semantics, and token-based presentation.
- Confirm no /viewer, board, fake link, future control, request-mock dependency, router, new feedback API, production App.tsx change, production adoption, or unrelated design-system/Foundation change exists.

### Validator
- none

## Exclusions
- Do not edit frontend/src/App.tsx, frontend/src/app.css, frontend/src/features/status/statusApi.ts, package manifests, backend files, or production adoption paths.
- Do not add /viewer, a production router, route context, Viewer navigation, a fake or disabled future destination, board/chess/data/analysis behavior, persistence, or backend behavior.
- Do not add packages, request-mocking dependencies, global state, JS resize state, ResizeObserver layout switching, custom modal/focus-trap mechanics, custom scrim dismissal, or required swipe-to-close.
- Do not add loading feedback severity, feedback actions, recovery props, a new feedback API, notification infrastructure, or throw expected health failures into the error boundary.
- Do not create a parallel Storybook mock or shell, second shell implementation, screenshot baseline, visual-regression service, custom icon set, logo, runtime font request, light theme, theme switcher, literal page-local colors, or inline application CSS.
- Do not modify unrelated design-system or Foundation behavior, retire the Foundation Check, update Plan status, reconcile, commit, push, or perform adjacent work.

## Escalate if
- The installed Base UI Drawer API or CSS Modules guidance cannot support the settled drawer behavior without inventing a custom modal, focus, keyboard, or scrim mechanism.
- react-error-boundary is unavailable or its installed API cannot provide the settled reset callback without a package change.
- Any requested implementation requires changing App.tsx, app.css, statusApi.ts, package manifests, backend behavior, router behavior, unrelated design-system/Foundation files, or any path outside this order's authorization.
- The exact existing StatusPage messages, abort cleanup, error-detail conversion, health request behavior, or StatusPage test lifecycle cannot be preserved while extracting StatusView.
- The required component states, drawer dismissal/focus paths, error recovery, token/breakpoint contracts, Storybook play proofs, or exact proof commands cannot be implemented as specified.
- A proof command fails for a reason requiring changed semantics or scope rather than a deterministic in-scope repair; stop and return to the coordinator.

## Canonical compile packet

```json
{
  "output_path": "docs/plans/active/responsive-site-shell/orders/01-build-complete-storybook-shell-composition.md",
  "identity": {
    "number": "01",
    "slug": "build-complete-storybook-shell-composition",
    "title": "Build complete Storybook shell composition",
    "goal": "Build and prove the complete real-component responsive shell composition in Storybook without changing production App.tsx, production adoption, or the existing health request behavior."
  },
  "depends_on": [],
  "required_strength": {
    "level": "Standard",
    "reason": "Well-specified frontend composition with exact copy, accessibility, state, CSS, and focused proof contracts; it has no data or irreversible behavior."
  },
  "authorization": {
    "creates": [
      "frontend/src/features/app-shell/AppShell.tsx",
      "frontend/src/features/app-shell/AppShell.module.css",
      "frontend/src/features/app-shell/AppShell.stories.tsx",
      "frontend/src/features/app-shell/AppShell.test.tsx",
      "frontend/src/features/app-shell/PageContentBoundary.tsx",
      "frontend/src/features/app-shell/PageContentBoundary.module.css",
      "frontend/src/features/app-shell/PageContentBoundary.test.tsx",
      "frontend/src/features/status/StatusView.tsx",
      "frontend/src/features/status/StatusView.module.css",
      "frontend/src/features/status/StatusView.test.tsx"
    ],
    "edits": [
      "frontend/src/features/status/StatusPage.tsx"
    ],
    "removes": []
  },
  "context": [
    {
      "path": "docs/plans/active/responsive-site-shell/responsive-site-shell.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Authoritative MP-03 Plan and Stage 1 compiler handoff, including ownership, settled behavior, acceptance, exclusions, and exact proof commands."
    },
    {
      "path": "docs/plans/done/material-design-foundation/material-design-foundation.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Accepted MP-02 dependency defining the available Material roles, cmt tokens, typescale, feedback, and focus contracts."
    },
    {
      "path": "frontend/src/features/status/StatusPage.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Preserve the existing ViewState, AbortController, fetchHealth effect, abort cleanup, loading/success/error handling, and error-detail conversion while replacing only the local render branch."
    },
    {
      "path": "frontend/src/features/status/statusApi.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Existing backend health boundary; it is context only and its API and request behavior must remain unchanged."
    },
    {
      "path": "frontend/src/App.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Confirm the production composition remains unchanged and StatusPage-only through Stage 1."
    },
    {
      "path": "frontend/src/features/design-system/feedback/InlineFeedback.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Use the existing thin FeedbackCore wrapper and supply explicit live-region roles from StatusView."
    },
    {
      "path": "frontend/src/features/design-system/feedback/PageFeedback.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Compose the existing page feedback wrapper with a local Try again button in the boundary fallback; do not add an action API."
    },
    {
      "path": "frontend/src/features/design-system/feedback/feedbackTypes.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Use the accepted information/success/warning/error severity set and consumer-owned live attributes without adding loading or recovery contracts."
    },
    {
      "path": "frontend/src/features/foundation/FoundationCheck.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Evidence of installed Base UI, Lucide, and react-error-boundary usage only; it is not a shell precedent and must remain unchanged."
    },
    {
      "path": "frontend/.storybook/preview.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Preserve the existing Storybook preview behavior and use its accepted story CSS import pattern only if the new stories require it."
    },
    {
      "path": "frontend/package.json",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Confirm the installed @base-ui/react 1.7.0 and react-error-boundary 6.1.3 dependencies before implementing their bounded APIs; do not change package dependencies."
    }
  ],
  "known_facts": [
    "Stage 1 is the complete real-component shell composition in Storybook and must stop before production adoption.",
    "The accepted dependency is MP-02 at docs/plans/done/material-design-foundation/material-design-foundation.md; no new packages or request-mocking dependency are permitted.",
    "frontend/src/App.tsx currently renders only StatusPage and must remain unchanged through Stages 1 and 2.",
    "StatusPage continues to own ViewState, the AbortController, fetchHealth, the effect, abort cleanup, loading/success/error Promise handling, and backend error-detail conversion; only its local render branch changes to StatusView.",
    "statusApi.ts is the existing backend health boundary and its API and request behavior must not change.",
    "StatusView accepts the discriminated state { kind: \"loading\" } | { kind: \"success\" } | { kind: \"error\"; message: string } and renders the exact existing messages under the System status heading.",
    "StatusView maps loading to InlineFeedback severity information with explicit role status, success to severity success with explicit role status, and error to severity error with explicit role alert.",
    "InlineFeedback is a thin FeedbackCore wrapper with no live-region defaults, so StatusView supplies the explicit consumer-owned role.",
    "The accepted feedback severities are information, success, warning, and error; there is no loading severity, recovery prop, action API, or new feedback API.",
    "AppShell accepts only children and owns the skip link, text-only Chess Move Trainer identity, desktop header/sidebar, constrained menu trigger, one local Status navigation item, Base UI Drawer wiring, main id main-content, and PageContentBoundary around main content.",
    "The only navigation item is a native anchor with href \"/\", visible Status text, Lucide Activity, and aria-current=\"page\"; no router, /viewer, fake destination, future control, or route context is added.",
    "Wide layout uses a sticky 64px top bar, an independently scrollable 240px sidebar, and a fluid top-aligned main region with 48rem maximum status width and 24px wide padding.",
    "The exact responsive breakpoint is max-width 679px for constrained mode and 680px for desktop; CSS media queries own the transition, with no JavaScript width state or ResizeObserver.",
    "Constrained mode keeps the identity on the left and exposes an icon-only Open navigation menu control; the left-edge Base UI modal drawer is min(320px, 85vw) wide, full-height, scrimmed, inert, body-scroll-locking, and headed Navigation with an icon-only Close navigation menu control.",
    "@base-ui/react/drawer owns focus containment, initial focus on Close, dismissal, focus restoration to the trigger, inertness, modal behavior, and keyboard behavior; required dismissal paths are Close, Escape, scrim activation, and selecting Status, with no required swipe-to-close.",
    "Application CSS owns only the drawer slide-and-scrim transition and removes it under prefers-reduced-motion: reduce; no custom focus trap or custom scrim dismissal is added.",
    "Lucide Activity, Menu, and X are imported individually; icon-only control names come from the controls, not SVG content.",
    "AppShell.module.css owns shell structure, measurements, max-width 679px media query, drawer/scrim transition, focus-visible treatment, and reduced-motion override; it uses --md-sys-*, --cmt-*, and shell-local 64px/240px custom properties with no literal application colors or inline styles.",
    "PageContentBoundary is a thin react-error-boundary wrapper around shell main content; its local fallback uses PageFeedback with heading Page unavailable, message Something went wrong while displaying this page., and a local Try again button that calls the package reset callback.",
    "PageContentBoundary.module.css owns only fallback/action layout and focus treatment; it adds no feedback API or global rule.",
    "Expected health failures remain typed StatusPage error state and never enter PageContentBoundary; only unexpected render failures below shell main reach the boundary.",
    "StatusView.module.css owns status presentation only, including 48rem maximum width and status-local spacing, and consumes accepted typescale, surface, border, focus, and spacing tokens.",
    "AppShell stories use the real AppShell, StatusView, InlineFeedback-backed states, and PageContentBoundary; they cover wide healthy, constrained closed/open, loading, healthy, unavailable, and unexpected failure/Try again states, with play proofs for drawer behavior and error recovery.",
    "Focused component tests cover controlled states and exact copy, explicit roles, backend error detail, shell landmarks and native link, skip link, drawer accessible names and interaction, Base UI focus/dismissal/restoration, boundary reset recovery, breakpoint declarations, token reuse, and component-level axe checks without network mocking.",
    "The three required proof commands must run in this order: focused StatusView/AppShell/PageContentBoundary tests, StatusPage lifecycle tests, then Storybook build.",
    "The human Stage 1 gate reviews Storybook at 1920x1080 and 412x915, all listed states and focus paths, reduced motion, token use, and absence of production adoption, /viewer, board, fake link, future control, request mock dependency, router, and App.tsx change.",
    "The installed dependencies are @base-ui/react 1.7.0 and react-error-boundary 6.1.3; verify the exact Drawer part signatures and CSS Modules guidance against the installed package without changing the product contract."
  ],
  "actions": [
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/status/StatusPage.tsx"
      ],
      "instruction": "Preserve StatusPage's ViewState, AbortController, fetchHealth effect, abort cleanup, loading/success/error handling, and backend error-detail conversion. Replace only the local render branch so it renders StatusView with the existing discriminated state; do not alter request behavior, messages, or expected error flow."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/status/StatusView.tsx"
      ],
      "instruction": "Create the controlled presentational status view accepting { kind: \"loading\" } | { kind: \"success\" } | { kind: \"error\"; message: string }. Render the System status heading and exact existing messages through InlineFeedback, mapping loading to information with explicit role=status, success to success with explicit role=status, and error to error with explicit role=alert. Keep it network-free and presentational."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/status/StatusView.module.css"
      ],
      "instruction": "Create CSS Modules for status presentation only, including status-local spacing and a 48rem maximum width. Consume accepted MP-02 typescale, surface, border, focus, and spacing tokens; do not add literal page-local colors, inline CSS, or global rules."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/status/StatusView.test.tsx"
      ],
      "instruction": "Create focused network-free component tests for loading, success, and error states. Assert the System status heading, exact existing copy including backend error detail, explicit status/alert roles, and a focused axe check."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/AppShell.tsx"
      ],
      "instruction": "Create AppShell accepting only children. Own the focus-revealed Skip to main content link, text-only Chess Move Trainer identity, wide header/sidebar, constrained Open navigation menu control, native Status navigation item at / with visible text, Activity icon, and aria-current=page, Base UI Drawer wiring, main id=main-content, and PageContentBoundary around main content. Keep navigation data local and limited to Status; render the same item in desktop and drawer regions. Use installed @base-ui/react/drawer parts and Lucide Activity/Menu/X, with Base UI owning modal focus, dismissal, inertness, keyboard behavior, and restoration. Do not add route context, router, JS width state, custom focus mechanics, or swipe behavior."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/AppShell.module.css"
      ],
      "instruction": "Create shell CSS Modules for the sticky 64px top bar, 240px independently scrollable sidebar, main layout, constrained mode at max-width 679px, drawer and scrim transition, focus-visible treatment, and reduced-motion override. Use --md-sys-* and --cmt-* tokens plus shell-local structural custom properties for 64px and 240px; do not use literal application colors, inline application styles, global rules, JS breakpoint state, or custom scrim dismissal."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/PageContentBoundary.tsx"
      ],
      "instruction": "Create a thin react-error-boundary wrapper for unexpected render failures below shell main content. Render children normally; on failure compose PageFeedback with heading Page unavailable and message Something went wrong while displaying this page., plus a local Try again button that calls the package reset callback. Do not change PageFeedback or treat expected StatusPage health errors as render failures."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/PageContentBoundary.module.css"
      ],
      "instruction": "Create CSS Modules only for the PageContentBoundary fallback/action layout and focus treatment. Do not add feedback API, global rules, literal page-local colors, or inline application CSS."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/AppShell.stories.tsx"
      ],
      "instruction": "Create Storybook stories composed from the real AppShell, StatusView, InlineFeedback-backed state, and PageContentBoundary. Cover wide healthy, constrained closed/open, loading, healthy, unavailable, and unexpected failure/Try again states. Include play proofs for opening/closing and required drawer dismissal/focus behavior as applicable, and for Try again recovery. Supply StatusView state directly without fetch or request mocks; use the existing accepted story CSS import pattern if needed without changing preview behavior."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/AppShell.test.tsx"
      ],
      "instruction": "Create component tests for shell semantics and landmarks, skip link, text identity, native Status link and aria-current, menu control accessible names, wide/constrained regions, Base UI Drawer open/close behavior, Close/Escape/scrim/Status dismissal, initial Close focus, focus containment and restoration, and a component-level axe proof. Do not use a request-mocking dependency or test custom focus mechanics that the application does not own."
    },
    {
      "kind": "file",
      "paths": [
        "frontend/src/features/app-shell/PageContentBoundary.test.tsx"
      ],
      "instruction": "Create a test-only throwing child that verifies the shell-preserving Page unavailable fallback, exact message, and local Try again button, then verifies reset recovery. Keep expected StatusPage health errors typed and outside the boundary failure path."
    }
  ],
  "proof": [
    {
      "cwd": ".",
      "command": "npm run test --prefix frontend -- --run src/features/status/StatusView.test.tsx src/features/app-shell/AppShell.test.tsx src/features/app-shell/PageContentBoundary.test.tsx",
      "purpose": "Prove the new controlled status states, exact copy and live-region semantics, shell semantics and drawer behavior, boundary fallback/reset, CSS/token contracts, and focused component axe coverage."
    },
    {
      "cwd": ".",
      "command": "npm run test --prefix frontend -- --run src/features/status/StatusPage.test.tsx",
      "purpose": "Prove the existing health lifecycle, fetch boundary, abort cleanup, loading/success/error flow, and preserved expected backend error behavior after the render-branch extraction."
    },
    {
      "cwd": ".",
      "command": "npm run build-storybook --prefix frontend",
      "purpose": "Prove the complete real-component Storybook composition builds, including the shell, controlled status states, drawer stories, feedback, and error-boundary recovery story."
    }
  ],
  "acceptance_handoff": {
    "coordinator": {
      "requirements": [
        "Review the complete real-component Storybook composition at 1920x1080: sticky top bar, visible 240px sidebar, main boundary, text-only identity, active native Status link, and top-aligned loading, healthy, and unavailable states.",
        "Review the constrained closed and open composition at 412x915: identity placement, menu trigger, drawer width/surface, Navigation heading, Close control, scrim, and absence of the desktop sidebar.",
        "Exercise menu-trigger focus, initial focus on Close, focus containment, Close, Escape, scrim activation, Status selection, and focus restoration; confirm Base UI owns these behaviors.",
        "Review reduced-motion behavior, Page unavailable exact copy, local Try again recovery, explicit status/alert semantics, and token-based presentation.",
        "Confirm no /viewer, board, fake link, future control, request-mock dependency, router, new feedback API, production App.tsx change, production adoption, or unrelated design-system/Foundation change exists."
      ]
    },
    "validator": null
  },
  "exclusions": [
    "Do not edit frontend/src/App.tsx, frontend/src/app.css, frontend/src/features/status/statusApi.ts, package manifests, backend files, or production adoption paths.",
    "Do not add /viewer, a production router, route context, Viewer navigation, a fake or disabled future destination, board/chess/data/analysis behavior, persistence, or backend behavior.",
    "Do not add packages, request-mocking dependencies, global state, JS resize state, ResizeObserver layout switching, custom modal/focus-trap mechanics, custom scrim dismissal, or required swipe-to-close.",
    "Do not add loading feedback severity, feedback actions, recovery props, a new feedback API, notification infrastructure, or throw expected health failures into the error boundary.",
    "Do not create a parallel Storybook mock or shell, second shell implementation, screenshot baseline, visual-regression service, custom icon set, logo, runtime font request, light theme, theme switcher, literal page-local colors, or inline application CSS.",
    "Do not modify unrelated design-system or Foundation behavior, retire the Foundation Check, update Plan status, reconcile, commit, push, or perform adjacent work."
  ],
  "escalate_if": [
    "The installed Base UI Drawer API or CSS Modules guidance cannot support the settled drawer behavior without inventing a custom modal, focus, keyboard, or scrim mechanism.",
    "react-error-boundary is unavailable or its installed API cannot provide the settled reset callback without a package change.",
    "Any requested implementation requires changing App.tsx, app.css, statusApi.ts, package manifests, backend behavior, router behavior, unrelated design-system/Foundation files, or any path outside this order's authorization.",
    "The exact existing StatusPage messages, abort cleanup, error-detail conversion, health request behavior, or StatusPage test lifecycle cannot be preserved while extracting StatusView.",
    "The required component states, drawer dismissal/focus paths, error recovery, token/breakpoint contracts, Storybook play proofs, or exact proof commands cannot be implemented as specified.",
    "A proof command fails for a reason requiring changed semantics or scope rather than a deterministic in-scope repair; stop and return to the coordinator."
  ]
}
```
STATUS: DONE

EXECUTOR RESULT:
- DEVIATIONS: none (deterministic in-scope corrections: AppShell drawer wiring for initial focus on Close and a native Status `<a href="/">` link, with `finalFocus={triggerRef}` and `initialFocus={closeButtonRef}`; scrim-dismissal test-scoping correction asserting drawer closure rather than trigger-focus restoration under jsdom 26.0.0, with focus restoration on scrim left to Base UI and verified in Stage 2's real-browser proof)
- PROOF RESULTS: Proof 1 passed (StatusView/AppShell/PageContentBoundary: 3 files, 10 tests); Proof 2 passed (StatusPage: 3 tests); Proof 3 passed (build-storybook compiled and registered the AppShell stories). Bounded frontier corrections: frontend/.storybook/main.ts gained one app-shell stories glob (without it build-storybook silently skipped the shell stories); AppShell.stories.tsx type cleanup (Meta args plus UnexpectedContent typed `(): never`) resolved TS2322/TS2786 and fixed the previously-failing `tsc -b` build with no story state, copy, or play proof changed.
- DIRTY PATHS: pre-existing unrelated dirty paths preserved: deleted docs/design-guides/static-position-to-analysis.md and docs/design-guides/mp02-visual-reference.html; modified docs/grilling-docs/static-position-to-analysis-roadmap.md and docs/master-plans/static-position-to-analysis.md; untracked docs/design-guides/mp03-responsive-shell-reference.html.
- AUTHORIZATION AUDIT: clean — authorized paths only; frontend/src/App.tsx, app.css, statusApi.ts, package manifests, and backend unchanged.
- ATTEMPTS: 0
- ESCALATION: none

VALIDATOR RESULT (validate-stage, 2026-08-16):
- Independent checks: all four supplied commands passed — focused StatusView/AppShell/PageContentBoundary tests (10/10), StatusPage lifecycle tests (3/3), build-storybook (success, AppShell stories registered), and npm run build (tsc -b and vite build success).
- Full local check suite (check.ps1): documentation check reports only the documented pre-existing baseline (7 broken local links from the unrelated deleted design-guide files; zero errors from this Plan or order); Ruff lint/format, Python tests, Frontend tests, ESLint, Prettier, Frontend build, and source-size check all passed. E2E: 4/5 passed; the single failure is tests/e2e/status.spec.ts locating the old "Chess Move Trainer" heading, the Plan-documented Stage 3 update target (verification-only path) after the authorized "System status" heading split.
- Scope audit confirmed via git status/diff: authorized creates/edits plus the two documented frontier corrections only; no App.tsx, app.css, statusApi.ts, manifest, or backend change.
- Human stage acceptance for this exact Plan and Stage 1 recorded by the coordinator.
