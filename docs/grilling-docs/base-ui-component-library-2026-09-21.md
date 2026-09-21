# Base UI component library completion

**Started:** 2026-09-21  
**Status:** Completed and locally verified.  
**Authority:** The user asked for all Base UI 1.8.0 components not yet represented in the project to receive basic, reusable design-system implementations. The user explicitly requested direct implementation without questions and asked for this running record to keep the work in check. This is a decision and verification log, not a separate Plan.

## Goal

Add reusable project-styled wrappers for the 22 missing Base UI components while preserving existing application behavior and leaving each wrapper flexible enough for later feature-specific composition.

## Scope

- Accordion
- Avatar
- Checkbox Group
- Context Menu
- Dialog
- Fieldset
- Form
- Menu
- Menubar
- Navigation Menu
- Number Field
- OTP Field
- Preview Card
- Scroll Area
- Separator
- Slider
- Switch
- Tabs
- Toast
- Toggle
- Toggle Group
- Tooltip

Base UI utilities such as `CSPProvider`, `DirectionProvider`, `mergeProps`, and `useRender` are not components and remain out of scope.

## Repository facts found before implementation

- `frontend/package.json` pins `@base-ui/react` at 1.8.0.
- Existing design-system components are named exports backed by CSS Modules and centralized `--cmt-*` and `--md-sys-*` tokens.
- Existing wrappers preserve ordinary React props, support controlled and uncontrolled state where Base UI supports both, and allow consumer `className` values.
- The worktree contains unrelated in-progress backend, API, analysis-page, and `OutcomeTrack` work. Those files must not be altered.
- There is no active implementation Plan for this request.
- The existing `Tabs` component is hand-built and already has application consumers and a substantial behavior contract. Its public props, test IDs, overflow behavior, and mounted-panel behavior must remain stable while its interaction primitive moves to Base UI.
- Existing feedback components are persistent page and panel messages; they are explicitly not a toast notification system. Toast therefore needs its own provider and notification API.

## Decisions made without a question round

### Public API approach

- Prefer small project-level APIs for common usage, with React nodes, native element props, controlled state, event callbacks, and consumer class names available where relevant.
- Keep Base UI implementation details behind the project wrappers. Feature code should not need to assemble low-level portals, positioners, backdrops, or focus-management parts for basic use.
- Use data-driven item definitions for repeatable collections such as accordion items, menu items, navigation items, and toggle groups, while allowing arbitrary React content for labels and panels.
- Preserve escape hatches through root props and targeted part-class props rather than exposing raw internal Base UI namespaces as the main application API.

### Styling and accessibility

- Reuse only centralized spacing, radius, elevation, focus, color, typography, and motion tokens.
- Keep keyboard handling, focus management, ARIA relationships, portals, and dismiss behavior in Base UI wherever possible.
- Include visible focus, disabled, reduced-motion, and forced-colors treatment in the shared styles.
- Keep component surfaces neutral and broadly reusable; feature-specific widths, placement, copy, and content remain consumer-owned.

### Compatibility

- Preserve the existing `TabsProps` and `TabDefinition` interfaces and the current DOM test hooks used by its consumers and tests.
- Add new components without changing current call sites. No existing local feedback component will be replaced by Toast.
- Avoid index barrels so imports remain explicit and match the repository's current design-system convention.

### File organization

- Keep broadly used stand-alone components at the design-system root.
- Put advanced form controls under the existing `form-controls/` family.
- Put menu variants under a new `menus/` family so Menu, Context Menu, and Menubar can share one item definition and one styling contract.
- Put popup-based informational components under a new `overlays/` family so Dialog, Preview Card, Toast, and Tooltip share the same surface and transition treatment.
- Use grouped focused test and Storybook files for the new families rather than duplicating setup in 21 nearly identical files. The existing dedicated Tabs tests and stories remain authoritative for Tabs.

## Running work log

- Confirmed the missing-component inventory against the Base UI 1.8.0 documentation and repository imports: 22 components are in scope.
- Reviewed `Button`, `Disclosure`, form-control, and `Tabs` conventions plus the design tokens and catalogue structure.
- Started this record before product-source implementation as requested.
- Inspected the published `@base-ui/react` 1.8.0 type declarations and current component documentation so wrappers use the actual package parts and controlled-state contracts.
- Chose data-driven definitions for repeated items and native/Base UI prop pass-through for one-off controls. This keeps first use simple without preventing later feature-specific content, controlled state, or layout classes.
- Added the root content primitives (`Accordion`, `Avatar`, `ScrollArea`, `Separator`, and `NavigationMenu`) and their shared token-driven styles.
- Added the advanced form family (`CheckboxGroup`, `Fieldset`, `Form`, `NumberField`, `OtpField`, `Slider`, `Switch`, `Toggle`, and `ToggleGroup`). `Field` now forwards its optional `name` to Base UI so `Form` can collect named values.
- Added the menu family (`Menu`, `ContextMenu`, and `Menubar`) with shared item definitions and content rendering.
- Added the overlay family (`Dialog`, `PreviewCard`, `Toast`, and `Tooltip`) with shared popup, transition, forced-colors, and reduced-motion styling.
- Migrated the existing `Tabs` interaction layer to Base UI while preserving its public API, test IDs, mounted panels, keyboard behavior, controlled behavior, and overflow controls. The overflow rail uses a native non-passive wheel listener so vertical wheel input can be converted to horizontal movement without also scrolling the page.
- Added grouped component tests and Storybook stories for each new family, retained the dedicated Tabs coverage, and linked the new stories from the existing reference catalogue pages.
- Performed a read-only API and accessibility audit against the installed Base UI 1.8.0 declarations. The audit found no package API or story-ID mismatches; its concrete runtime and test issues were repaired before final verification.

## Verification log

- Final `powershell -ExecutionPolicy Bypass -File ./dev.ps1 status` reported the backend, frontend, and Storybook services healthy after Docker Desktop became available.
- `npm exec --workspace frontend tsc -- --noEmit -p tsconfig.app.json` passed after the final implementation and story changes.
- Targeted ESLint over the wrappers, tests, stories, and catalogue updates passed with no warnings or errors.
- Targeted Prettier check passed for all implementation, test, story, CSS, and catalogue files in this work.
- Focused Vitest run passed: 5 files and 39 tests covering content primitives, advanced form controls, menu primitives, overlays, and Tabs.
- `npm run --workspace frontend build-storybook -- --output-dir "C:/Users/skyro/AppData/Local/Temp/opencode/storybook-base-ui-components"` completed successfully and bundled all 22 Base UI package entry points.
- The first focused Storybook browser-test run was interrupted by Vite's one-time dependency optimizer reloading the test server after discovering the new Base UI entry points. The final focused run passed: **11 story files and 46 story tests**, including the four new component families and the updated catalogue pages.
- Live Storybook verification confirmed the new stories were indexed after the managed service refreshed. Accordion, form, menu, and dialog examples rendered and operated through their accessible controls; the menu showed each item exactly once after the shared item-content extraction.
