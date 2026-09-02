# Reusable Tabs - A generic production-ready Tabs component is available in the design system

> **Status:** done - generic Tabs promoted, documented, and visually approved; application adoption remains excluded

- **Read trigger:** Read before promoting the approved tabs Storybook candidate or changing its production component, focused tests, Storybook stories, or design-system documentation.
- **Upstream:** The user-approved Storybook direction and the current executable candidate: `frontend/src/features/design-system/ExclusiveTabsQuietUnderlineDark.tsx`, `ExclusiveTabsQuietUnderlineDark.module.css`, `ExclusiveTabsQuietUnderlineDark.stories.tsx`, and `ExclusiveTabsQuietUnderlineDark.test.tsx`. The candidate is authoritative where it differs from the parent HTML concept. No `DESIGN.md` is required.

## Outcome

Promote the approved isolated tabs direction into the canonical frontend design system as a generic `Tabs` component. Consumers can provide stable tab IDs, labels, and mounted panel content; choose controlled or uncontrolled selection; disable tabs; and use the existing accessible keyboard and overflow interactions without receiving exploratory page/card framing. This promotion deliberately stops before application-screen adoption.

## Scope

- **Included:** Generic `Tabs` and `TabDefinition` API; controlled `selectedId` and uncontrolled `defaultSelectedId`; `onSelectedIdChange`; `ariaLabel` with a generic default; root `<div>` DOM props and `className`; stable tab/tabpanel IDs; disabled-tab skipping and selection safety; mounted-hidden caller content; semantic tab relationships; roving keyboard activation; selection announcement; existing overflow controls, edge fades, focus/selection reveal, wheel conversion, native scrolling, observer behavior, forced-colors, reduced motion, production Storybook stories, focused unit tests, README documentation, and removal of exploratory names/chrome.
- **Expected areas:** `frontend/src/features/design-system/Tabs*`, `frontend/src/features/design-system/README.md`, and the four `frontend/src/features/design-system/ExclusiveTabsQuietUnderlineDark*` candidate files being replaced.
- **Excluded:** Application consumers, routes, APIs, backend work, dependencies, token/theme changes, package or barrel exports, new variants, vertical mode, RTL-specific policy, lazy panels, imperative ref/scroll exposure, historical documentation, broad maintenance, and unrelated cleanup.

## Design fidelity

- **Authority:** The approved current Storybook candidate files are the executable visual and interaction authority. The user-approved promotion request establishes the canonical-production adaptation. The candidate's page/card framing and exploratory names are not production requirements.
- **Excluded artifact content:** `.pageShell` and `.mockSurface` presentation, candidate/exploration naming, fixture-only framing text, and any built-in panel card or interior presentation.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| Candidate `.tabsNavigation`, `.tabList`, and `.tab` rules | Quiet semantic-token underline, single-line rail, readable tab sizing, and visible focus treatment | Rename to `Tabs`; remove page/card shell; keep root placement consumer-owned | Stage 1 token/source review and Stage 3 human Storybook breakpoint |
| Candidate overflow state and `.tabsViewport` fades | Conditional previous/next controls, edge fades, reveal of focused/selected tabs, native horizontal scrolling, touchpad/swipe behavior, and vertical-wheel conversion only while movement is possible | Harden observer lifecycle and DOM measurement without changing the interaction direction | Stage 2 focused unit proof and Stage 3 constrained Storybook breakpoint |
| Candidate tab/tabpanel markup and keyboard handlers | `tablist`/`tab`/`tabpanel` roles, explicit relationships, roving focus, wrapping arrows, Home/End, Enter/Space activation, and polite selection announcement | Replace hard-coded IDs and label with stable string IDs and caller `ariaLabel`; skip disabled tabs | Stage 2 focused unit proof and production Storybook interaction proof |
| Candidate panel rendering | Caller-owned `ReactNode` content; one visible selected panel; inactive panels mounted with `hidden`; no panel interior styling | Keep mounted-hidden behavior fixed; do not add lazy mode or render slots | Stage 2 mounted-content tests and Stage 3 Storybook review |
| Candidate token/accessibility media rules | Semantic color/geometry tokens, forced-colors fallback, reduced-motion behavior, and no literal visual direction change | Remove “Dark” from names while retaining the repository's current dark semantic-token runtime; do not add light-theme switching | Stage 1 CSS/source review and Stage 3 visual breakpoint |

## Stages

1. **done - Production contract and implementation migration**
   - **Ordered actions:**
     1. Replace the exploratory component contract with `Tabs` and `TabDefinition`: `id: string`, `label: string`, `content: ReactNode`, optional `disabled`; `selectedId`, `defaultSelectedId`, `onSelectedIdChange`, `ariaLabel`, and root `className`/DOM props through `Omit<ComponentPropsWithoutRef<"div">, "children">`.
     2. Implement both controlled and uncontrolled selection, a valid enabled fallback when the current selection is absent or disabled, and disabled-tab-aware roving navigation while preserving the approved activation behavior.
     3. Generate stable component-scoped tab/panel IDs from `useId` plus the stable tab ID, keep panels mounted-hidden, and preserve all tab/tabpanel ARIA relationships and the polite announcement.
     4. Remove page/card framing and exploratory naming from the component and CSS; retain the quiet underline, one-line rail, overflow controls/fades, semantic tokens, forced-colors, reduced-motion, and caller-owned panel interiors.
     5. Make measurement safe for SSR/jsdom and missing browser observers: guard browser globals, use an SSR-safe effect, avoid unnecessary observer resubscription, filter mutation observation to relevant layout changes, and disconnect listeners/observers on cleanup.
     6. Logically rename the focused test file to `Tabs.test.tsx` and migrate the existing behavior fixtures sufficiently to exercise the new component name and API.
   - **Focused proof:** Run the focused unit command after the migrated baseline test is runnable. This proof is invalidated by Stage 2's additional behavior/test changes and must then be rerun.
   - **Escalation boundary:** Stop for any change to the approved API envelope, panel mounting policy, visual direction, token ownership, or public ref/imperative behavior.
   - **Breakpoint:** None; no user decision remains before Stage 1.

2. **done - Focused unit coverage for the production contract**
   - **Ordered actions:**
     1. Cover generic string IDs, custom accessible labeling, unique stable relationships, root `className`/DOM prop forwarding, and absence of exploratory shell content.
     2. Cover default selection, controlled selection and callback behavior, uncontrolled changes, invalid/removed selection fallback, disabled activation prevention, disabled navigation skipping, and all approved keyboard activation paths.
     3. Cover mounted caller-owned content with exactly one visible panel, polite announcements, focus/selection reveal, and the tab/tabpanel accessibility tree.
     4. Preserve focused overflow tests for conditional controls, edge fades/state, button scrolling, native scroll updates, vertical wheel conversion and horizontal-wheel pass-through, observer-safe updates, and cleanup.
     5. Preserve CSS assertions for centralized tokens, no panel interior presentation, forced-colors, reduced motion, and focus treatment.
   - **Focused proof:** Rerun the focused unit command below; passing proof remains valid until a later affecting change.
   - **Escalation boundary:** Stop if tests expose an unresolved duplicate-ID runtime policy, a need for lazy panels, or behavior outside the approved horizontal/mounted-hidden contract.
   - **Breakpoint:** None.

3. **done - Production Storybook, documentation, cleanup, and visual sign-off**
   - **Ordered actions:**
     1. Rewrite the story file as `Tabs.stories.tsx` under `Design System/Components/Tabs`, with representative default, controlled/disabled, and overflow interaction coverage using caller-owned content.
     2. Update `frontend/src/features/design-system/README.md` to list `Tabs` as a shared component and describe its generic mounted-panel and overflow behavior.
     3. Remove the four replaced `ExclusiveTabsQuietUnderlineDark*` files after the `Tabs*` replacements are complete; remove all exploratory imports/references and make no barrel or Storybook-config change because existing conventions already discover direct files and the design-system glob.
     4. Run the focused Storybook interaction proof, then perform the one bounded final scope audit against this Plan, preserving unrelated changes.
   - **Focused proof:** Run the focused Storybook command below after the production story/title and cleanup changes. Do not run lint, formatting, builds, source-size, aggregate, maintenance, or repository-hygiene checks.
   - **Escalation boundary:** Stop rather than silently changing direction if the Storybook review requires application integration, a new visual variant, a theme switch, a package entrypoint, or another excluded contract.
   - **Breakpoint:** Required human visual breakpoint after the production Storybook proof. Review `Design System/Components/Tabs` at its normal and constrained/narrow presentation against the fidelity anchors above. User/coordinator sign-off is required before closeout; a visual mismatch that changes direction returns for a decision rather than being absorbed.

## Progress and decisions

- **Decision before Stage 1:** none - the outcome, API envelope, exclusions, and visual authority are approved.
- **Stage 1:** done - production `Tabs` contract and implementation migrated; breakpoint: none.
- **Stage 2:** done - focused unit contract coverage; proof: focused unit command, 19/19 passed; breakpoint: none.
- **Stage 3:** done - production Storybook, README, and exploratory candidate cleanup; proof: focused Storybook command, 4/4 passed; breakpoint: user approved the final visual result.
- **Canonical decisions:** `Tabs` owns navigation, selection, overflow, and ARIA panel hosting; callers provide arbitrary or null mounted `ReactNode` content and own its inner aesthetic. Storybook uses semantic dark surface tokens and retains no exploratory framing or promotional fixture content.

## Proof

- From `G:\ChessMoveTrainer\frontend`, run `timeout 120s npm run test -- --run --project=unit src/features/design-system/Tabs.test.tsx` (command timeout: 120 seconds; recommended bash tool timeout: 150000 ms).
- From `G:\ChessMoveTrainer\frontend`, run `timeout 180s npm run test-storybook -- --run src/features/design-system/Tabs.stories.tsx` (command timeout: 180 seconds; recommended bash tool timeout: 210000 ms).
- These are the only prescribed implementation proofs. Passing behavioral proof is retained until a later stage changes its command, inputs, exercised behavior, configuration, dependencies, or environment.

## Escalation boundaries

- Require a new decision for application-screen adoption, a public package entrypoint or barrel, light-theme runtime switching, lazy/unmounted panels, vertical mode, RTL-specific scrolling policy, imperative ref/scroll API, new variants, dependency or token changes, or a runtime duplicate-ID policy beyond documenting IDs as unique within a `Tabs` instance.
- Do not add routes, APIs, backend behavior, consumers, dependencies, token/theme definitions, commits, pushes, branches, worktrees, stashes, or unrelated cleanup.
- Preserve unrelated working-tree changes and completed historical records. If the bounded final scope audit finds unrelated modifications, leave them untouched and report them rather than absorbing them.

## Visible result

> Storybook shows a reusable `Tabs` component under `Design System/Components/Tabs` with accessible selection, disabled-tab handling, caller-owned panels, and approved responsive overflow behavior.
