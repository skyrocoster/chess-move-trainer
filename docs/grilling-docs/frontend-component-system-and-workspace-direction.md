# Frontend component system and adjustable workspace direction

Date: 2026-09-15

Status: Complete and confirmed by the user on 2026-09-15.

## Purpose and authority

This record captures the intended direction for the frontend component system, its Storybook catalogue, panel-like surfaces, and the adjustable three-region workspace.

It replaces the chronological grilling record that produced these decisions. It is organized around the resulting concepts rather than the order in which questions were asked.

This is durable directional evidence. It is not a Plan, an implementation or migration authorization, a dependency decision, or proof that the intended system already exists.

## Outcome sought

The frontend should make the consistent and accessible choice the easiest choice for both people and AI agents.

The user wants:

- visual consistency across related interfaces;
- established accessibility behavior instead of repeatedly hand-building common interactions;
- predictable change propagation, so changing a shared decision changes its intended consumers;
- one visible set of approved building blocks rather than multiple competing local interpretations;
- enough flexibility to design something genuinely new when existing components do not fit; and
- a lightweight workflow that guides AI without adding broad checks, mandatory cleanup programmes, or duplicate governance processes.

All product work is performed with AI assistance. The repository therefore needs explicit component purposes, boundaries, and approval states. Source code alone is not sufficient because an AI can otherwise treat whichever nearby implementation it finds as the current design direction.

## Starting repository context

- A common card recipe—outline border, rounded corners, a surface-container background, and sometimes elevation—is repeated across feature-owned CSS modules rather than owned by one shared foundation.
- The word “Panel” currently describes several different things: visual containment, interactive widgets, resizable layout regions, feedback presentations, and plain logical sections.
- `@base-ui/react` 1.7.0 is installed and already supplies behavior for disclosures, drawers, dialogs, popovers, toolbars, form controls, and meters.
- Some interaction remains hand-built, most notably Tabs and a disclosure-like control.
- Specialist behavior already uses specialist foundations, including `react-resizable-panels`, Headless Tree, Recharts, React DayPicker, and FullCalendar.

These facts explain the need for consolidation but do not approve any current implementation as the final shared design.

## Core design principles

### Group by purpose and behavior

Components belong to the same family when they perform the same job and have the same semantic and interaction responsibilities.

- Similar appearance alone does not make two components the same family.
- Legitimate visual differences within one family use meaningful named options.
- Different jobs remain separate even when they share visual treatment.
- Existing pixel differences, local convenience, and historical drift do not automatically become supported variants.
- Features select approved named options instead of locally redefining shared borders, spacing, radius, backgrounds, or elevation.

A modal dialog and an information card may both look like bordered rectangles, but they do not belong to one behavioral component. Two information cards with different approved emphasis may belong to one family.

### Reuse is a design decision

Design must explicitly choose whether a need should:

- reuse an approved component as-is;
- compose approved components;
- extend an existing family with a meaningful named option; or
- introduce a new candidate because the established options do not fit.

AI agents must inspect the approved catalogue before creating a local alternative. They must not invent a new version merely because it is easier in the immediate file.

When no approved component fits, the normal design workflow applies. A new candidate needs a short explanation of the missing job, why the approved options do not fit, and a visible candidate for user review. No additional component-system bureaucracy is required.

### Prefer established foundations without forcing them

The preferred order is:

1. reuse the approved repository component that already owns the job;
2. use Base UI when it provides the relevant interaction pattern;
3. use an established specialist library for specialist behavior;
4. use native semantic HTML where the browser already supplies the correct foundation; and
5. use a new dependency or custom interaction only when the established options do not fit.

Base UI or another pre-built foundation is preferred because it reduces repeated interaction and accessibility decisions. It is not an absolute requirement. Adopting Base UI is not, by itself, a reason to accept a worse design or lose behavior the user values.

### Accessibility has shared and feature-owned parts

WCAG 2.2 Level AA is the baseline.

An established primitive can supply mechanics such as keyboard navigation, focus management, state relationships, selection, and dismissal. It cannot guarantee meaningful feature wording, heading structure, labels, reading order, state announcements, or correct composition.

Shared components should require necessary accessibility context through their APIs where practical. For example, an icon-only action should require a meaningful accessible name. Generic fallback labels such as “Action” are not acceptable substitutes.

Approved components retain:

- production-backed Storybook examples for their real presentation and important states; and
- focused checks for the keyboard, focus, state, and component-contract guarantees they own.

Feature work may rely on those established guarantees. It still verifies the labels, headings, announcements, reading and focus order, and surrounding composition introduced by the feature. It should not repeatedly re-prove the same primitive behavior in every consumer.

## Separation of responsibilities

The intended frontend system separates four concerns:

| Concern | Owns | Does not own |
| --- | --- | --- |
| Behavior family | Semantics, keyboard and focus behavior, state contract | Unrelated feature content |
| Visual foundation | Shared border, background, corners, elevation, and spacing choices | Widget behavior or feature meaning |
| Feature composition | Domain content, data, wording, and arrangement of approved pieces | Reinventing shared foundations |
| Workspace layout | Region geometry, resizing, responsive structure, scrolling, and saved widths | Child component appearance or domain meaning |

This separation allows an interactive family to reuse a shared visual treatment without combining unrelated behavior into one universal `Panel`.

## Component-family direction

### Surface

The frontend should have one approved visual foundation for ordinary non-interactive panel or card containment.

Surface owns:

- background;
- border treatment;
- corner treatment;
- elevation;
- meaningful named spacing or containment options; and
- embedded or uncontained presentation when a real composition needs it.

Surface does not:

- impose one universal header, body, and footer structure;
- become clickable through an `onClick` option;
- own resizing;
- own feedback announcements; or
- replace the correct native element or interactive primitive.

“Non-interactive” describes the Surface's behavior, not a fixed physical size. A Surface remains fluid and adapts to its parent workspace region.

Likely current evidence for this family includes the outer treatments used by `AnalysisPanel`, `MoveResponseDistribution`, `PositionReachFrequency`, `PreferredMovePanel`, `LineLibrary`, `MoveHistory`, `PositionDescription`, and other card-like compositions. These examples are evidence for later classification, not automatic approval or a migration list.

### Interactive components using Surface appearance

Card-like interactive components may compose the Surface visual foundation while retaining their own behavior foundation.

Examples of the intended separation are:

- Tabs behavior supplied by a Tabs primitive, with approved contained or embedded visual presentation;
- Disclosure behavior supplied by Base UI Collapsible, with optional Surface containment; and
- Toolbar behavior supplied by Base UI Toolbar, with its own appropriate presentation.

Changing the shared border treatment may affect all approved contained presentations. It must not silently alter tab selection, disclosure expansion, keyboard behavior, or feature meaning.

### Feedback

Warning, error, success, and status messages form a separate semantic family.

Feedback owns:

- severity presentation;
- the contract for status or alert announcement behavior;
- any required accessible context; and
- approved panel, page, or inline presentations.

A feature should not create feedback by applying an error colour to a generic Surface and remembering the semantics itself. Feedback may share lower-level tokens or recipes with Surface, but it remains a separate public family.

Current evidence includes `FeedbackCore`, `PanelFeedback`, `PageFeedback`, `InlineFeedback`, and feature-owned error or status bands that may later be classified against that family.

### Whole-item actions

A whole clickable card-like item belongs to a separate action family, such as an ActionTile concept.

It should use proper button or link semantics and own focus, keyboard activation, disabled state, and accessible naming. It may share the approved Surface appearance, but a non-interactive Surface does not become interactive merely by receiving a click handler.

Current preferred-move choice boxes are relevant evidence for later classification. They are not automatically approved as the final shared action family.

### Behavior-specific and specialist families

The following remain separate because their behavior is materially different:

- Tabs;
- Disclosure and other collapsible patterns;
- dialogs, alert dialogs, drawers, and popovers;
- form controls and toolbars;
- feedback and live status;
- meters and progress displays;
- trees, charts, calendars, and chess-specific visualizations; and
- resizable workspace layout.

Base UI already provides suitable foundations for many of these. Existing specialist libraries remain appropriate where Base UI does not own the problem, including `react-resizable-panels`, Headless Tree, Recharts, React DayPicker, and FullCalendar.

## Storybook catalogue as the visible system

### Role of the catalogue

Storybook is the visible catalogue and demonstration environment. It answers both:

- what currently exists; and
- after explicit review, which foundations are approved and how they should be selected.

It does not duplicate component implementations. The component source remains the implementation, its colocated story remains the live example, and a structured catalogue record carries the design decision.

Ideally, Storybook displays the same structured record that AI agents read. The repository should not maintain one set of rules for Storybook and another for AI.

### Required catalogue information

Each entry uses a consistent small set of fields:

- status;
- purpose;
- when to use;
- when not to use;
- underlying native, Base UI, repository, or specialist foundation;
- approved named options; and
- accessibility responsibility.

Optional notes may explain unusual details but do not replace those fields.

### Status and approval

The catalogue distinguishes at least:

- approved reusable foundation;
- candidate requiring design review;
- feature-specific composition;
- **Needs replacement**;
- experimental or in-development work; and
- fixture-only material.

Reusable foundations and complete feature compositions remain visibly separate. Feature compositions demonstrate how approved pieces work together without making the whole feature a general-purpose component.

Catalogue presence does not imply approval. Storybook's existing **Production** grouping means that the application currently uses or demonstrates something; it does not mean that item is approved for general reuse.

Only explicit user approval after reviewing a production-backed Storybook candidate makes a foundation canonical. AI may gather evidence and recommend a status, and tests may prove behavior, but neither makes the design decision.

### Story ownership

The real story for a component lives beside that component. Catalogue pages link to it.

When catalogue work discovers that a component has no story, the story should be added beside the production component rather than becoming a second implementation owned by a catalogue page.

Prototypes, in-development components, and fixtures remain visible in clearly separated sections. Hiding them would not stop AI from finding them elsewhere; explicit non-approved status is safer than leaving their meaning to inference.

### Current catalogue evidence

The completed first-pass catalogue currently contains an overview and seven family pages under `Reference/Catalogue`.

- Existing Production and Reference stories remain the live examples; catalogue pages generally link to them.
- All story links inspected during this grilling resolved.
- Most family pages provide prose and links rather than duplicate examples.
- The Form Controls catalogue additionally owns eight new stories for production controls that previously lacked stories. They are useful evidence, but future deliberate refinement should place component stories beside their components.
- Current guidance is primarily free-form prose.
- The catalogue does not yet provide consistent per-entry status, foundation, use boundary, accessibility responsibility, or **Needs replacement** fields.

The catalogue is therefore a valid first-pass inventory and navigation layer, but it is not yet the final canonical decision source.

## Change propagation, replacement, and scope

### What propagates

Changes to centrally owned visual decisions—such as the standard border, radius, background, elevation, or a named option—should propagate to every consumer of that approved foundation.

Changes to semantics, interaction, keyboard behavior, data meaning, or product outcomes require explicit review. A central styling change must not become a way to alter feature behavior silently.

Consumers must not copy or pin shared styles merely to avoid deliberate system updates.

### Replacing a foundation

When an approved shared component is rebuilt on a different foundation, the design workflow determines which existing qualities are preserved and which tradeoffs the user accepts.

For example, a Base UI-backed Tabs candidate is not accepted merely because it uses Base UI. It must preserve the approved appearance and behavior the user values, or the user must knowingly accept the difference.

Once replacement work is deliberately taken up and the replacement is approved:

- all consumers in the affected component family move to the accepted foundation;
- the accepted implementation occupies the canonical export; and
- the competing production implementation is removed.

Temporary alternatives may coexist in Storybook during design comparison. They do not remain as permanent competing production choices.

The existing grilling, Storybook iteration, explicit approval, planning, and proof workflow already records accepted qualities and tradeoffs. The catalogue does not add another acceptance record or parallel process.

### Needs replacement and incidental work

**Needs replacement** records that an existing component is not the intended long-term foundation and must not be selected for new work.

It does not:

- authorize production edits;
- force migration to become the next task;
- create a mandatory cleanup programme; or
- expand unrelated work.

When approved catalogue guidance conflicts with older local code, new work follows the approved component and flags the older mismatch lightly. Merely touching the old feature is not permission to migrate it. The normal approved task or Plan scope decides when replacement is included.

This is compatible with whole-family replacement: timing is user-directed, but an accepted migration converges on one implementation rather than preserving permanent duplicates.

### Advisory conformance checking

A future catalogue-conformance check may flag likely bypasses of approved components, provided it is quick, focused, and advisory.

It must not become a broad quality gate, trigger repeated checks, block unrelated work, or remove the justified-exception path through the usual design workflow.

This advisory check is separate from the focused behavioral evidence retained by an approved component.

## Adjustable three-region workspace

### Concept

The application should use an adjustable work surface rather than rigidly sized panels.

The settled model is:

- major workspace regions are user-resizable;
- components inside those regions remain fluid;
- individual Surfaces do not own resizing; and
- resizing is a shared layout responsibility.

### Ownership

The adjustable layout becomes a shared page-level WorkspaceLayout composed inside AppShell.

AppShell continues to own the application-wide header, navigation, mobile navigation drawer, skip link, and main content boundary. It does not gain a three-column mode.

WorkspaceLayout owns:

- three-region geometry;
- resizing and separators;
- usable minimum widths;
- responsive mode changes;
- declared reading and collapsed stacking order;
- reset behavior;
- per-workspace saved widths; and
- region-level scrolling.

This keeps status, trainer, not-found, and other ordinary pages free from workspace state they do not need.

### Geometry rather than meaning

WorkspaceLayout is purpose-built for exactly three wide-screen regions. It is not a generic arbitrary-pane engine.

The regions are generic left, middle, and right slots. The shared layout does not assign universal meanings such as Board, Session, Engine, primary work, or supporting analysis. Each workspace composition chooses its content.

Because geometry does not reveal content priority, each workspace explicitly declares the order used for reading, keyboard navigation, and collapsed presentation. The shared mechanism keeps visible order and assistive-technology order aligned.

### Wide, medium, and narrow behavior

- Wide mode provides three user-resizable regions within approved usable minimums.
- Medium mode uses one shared reduced arrangement when three usable regions no longer fit.
- Narrow mode uses one declared vertical stack and one normal page scrollbar.
- Exact breakpoints, medium composition, and each workspace's narrow order remain later visual design decisions.
- The layout must not preserve unusably narrow columns or introduce routine horizontal page scrolling.

Workspace regions may be resized but do not manually hide, restore, dock, or reorder for now. Those capabilities require a demonstrated need and the normal design workflow.

### Alignment and child presentation

The workspace standard owns:

- outer column alignment;
- common top alignment;
- gutters;
- width rules; and
- standard gaps.

Each column keeps an independent vertical content stack for now. Internal panel bottoms do not need to align across columns, and shared horizontal tracks are deliberately deferred.

WorkspaceLayout does not automatically wrap children in Surface. A child may be a board, Surface, Tabs, toolbar, or another approved component. The workspace aligns those children without forcing different jobs to look like one card.

### Scrolling and persistence

At wide sizes, WorkspaceLayout occupies the available application work area and each region scrolls independently when its content is longer than the available height. Child panels do not each invent additional nested scrolling merely because they are inside the workspace.

At narrow sizes, the ordered stack returns to one normal page scroll.

User-adjusted widths are remembered separately for each workspace. A reset action restores that workspace's approved defaults. The persistence mechanism and treatment of revised defaults remain technical assessment questions.

### Current workspace evidence

The present repertoire implementation uses `react-resizable-panels` with board, session, and engine regions.

- Wide mode uses one horizontal group with three regions.
- Board content independently stacks the board, controls, and move history.
- Session content independently stacks the repertoire session content and position description.
- Engine content renders the analysis tabs.
- Board and session currently share a 16px gap value, but there is no cross-column row system.
- Equal outer height comes from stretching the regions; internal edges align only by coincidence.
- Medium mode currently has a hard-coded full-width board row above session and engine.
- Widths are not currently persisted.
- The current stage is feature-local even though its slots are content-agnostic.

These facts support later design and assessment. They do not make the current implementation the required final architecture.

## Potential changes implied by this direction

The following are plausible changes if separate future work is approved. They are not a sequence, implementation instruction, or migration authorization.

### Catalogue refinement

- Add one consistent structured decision record for each catalogue entry.
- Display that record in Storybook and make the same source readable by AI agents.
- Review current entries for approved, candidate, feature composition, **Needs replacement**, experimental, and fixture-only status.
- Move catalogue-owned component stories beside their production components when that refinement is deliberately undertaken.
- Consider a lightweight advisory signal for bypassing approved foundations.

### Shared component foundations

- Explore and approve a shared Surface foundation rather than preserving repeated feature-owned card recipes.
- Classify existing panel-like components against Surface, Feedback, whole-item action, behavior-specific, feature-composition, or no-surface roles.
- Consolidate duplicated feedback presentations behind the approved Feedback family where later review supports it.
- Explore a proper whole-item action family for repeated choice-box patterns.
- Review hand-built Tabs against a Base UI-backed candidate while preserving or consciously changing the qualities the user values.
- Continue using Base UI-backed Disclosure, overlays, form controls, toolbars, and meters where those foundations remain appropriate.

### Workspace foundation

- Explore the three-region WorkspaceLayout as a production-backed design candidate.
- Settle the visual form of wide, medium, and narrow modes.
- Settle minimum widths, separators, keyboard behavior, available-height handling, and per-workspace persistence.
- Assess extraction from the current repertoire-local stage only after the shared candidate is approved.

These changes must use the existing design and planning workflow. A catalogue classification or this directional record does not itself authorize them.

## Explicitly rejected approaches

The confirmed direction rejects:

- one universal `Panel` that combines non-interactive containment, actions, feedback, overlays, and resizing;
- forcing every surface through Base UI when there is no relevant widget behavior;
- treating every current styling difference as an official option;
- allowing feature-owned CSS to override shared visual foundations casually;
- treating every Production story or catalogue entry as approved for reuse;
- duplicating component implementations or maintained stories inside catalogue pages;
- keeping accepted old and new foundations as permanent competing choices;
- opportunistic migration merely because an AI is already editing a nearby file;
- mandatory cleanup scheduling created by **Needs replacement** status;
- broad, repeated, or blocking catalogue-conformance checks;
- putting the adjustable workspace into AppShell;
- making WorkspaceLayout a generic arbitrary-pane engine;
- forcing every workspace child into Surface;
- cross-column shared row tracks at this stage; and
- manual hide, dock, or reorder behavior at this stage.

## Deliberately deferred

This direction does not decide:

- exact TypeScript APIs, symbol names, file locations, or implementation mechanisms;
- final catalogue status for each existing component;
- exact Surface options, measurements, or visual design;
- whether Base UI can preserve every valued detail of current hand-built interactions;
- exact workspace breakpoints, medium arrangement, per-workspace narrow order, minimum widths, persistence mechanism, or available-height calculation;
- migration targets, order, timing, or proof commands;
- dependency additions or removals; or
- application integration.

Those questions belong to later design exploration and technical assessment after explicit user direction.

## Communication requirement

The user is relying on the workflow for specialist guidance rather than claiming expertise in frontend component architecture, Storybook, accessibility engineering, or design-system governance.

Future work must:

- explain normal practice in plain language;
- distinguish product decisions from technical mechanisms;
- recommend a reasonable default rather than presenting unexplained choices;
- identify where the user's initial framing should be reconsidered; and
- avoid treating requests for guidance as implementation authorization.

## Closeout

The user confirmed the underlying direction on 2026-09-15. This synthesis supersedes the chronological grilling record and is the durable evidence for future discussion.
