# Line Library — Historical Grilling Synthesis

**Recorded:** 2026-08-29  
**Status:** Confirmed directional evidence from product and architecture grilling; no implementation authority  
**Implementation authority:** None  
**Relationship:** This document records the agreed direction for a reusable Line Library picker and its first chess-opening implementation. It is historical evidence, not a Plan, schema, endpoint specification, migration instruction, or authorization to implement.

## Purpose

The Line Library is a reusable rendered picker for browsing and selecting line-oriented material. Its first implementation will browse chess openings, but the reusable component must not encode opening-specific semantics so that future domains, such as preferred-move lines, can use the same interaction model.

The fundamental product model is a **line family**: users browse groups or families that contain one or more concrete lines. The hierarchy may be arbitrarily deep rather than being limited to a fixed group-to-line depth.

The Line Library is a **selector only**. It owns discovery, browsing, filtering controls, hierarchy interaction, selection state, and commit interaction. It does not own board playback, training behavior, repertoire mutation, downstream API actions, or the meaning a consumer assigns to a committed selection.

## Reusable component boundary

The reusable Line Library is a real, fully rendered component rather than only a set of hooks or an API abstraction. It renders the search/filter area, hierarchy, selection controls, loading and error behavior, empty states, and an optional explicit Apply/commit interaction.

The rendering stack is **Headless Tree + Base UI**. Headless Tree supplies hierarchy, focus, and selection mechanics; Base UI supplies generic controls such as search, filters, popovers, and related interaction primitives. The Line Library owns its markup and styling around those primitives.

The shell is configurable. It may render as a self-contained panel by default while allowing the outer shell to be disabled when a consumer embeds it in a page, dialog, drawer, or another container.

Rows use a structured-slot model. The Line Library owns the row skeleton and interactions, while the domain implementation supplies display content such as the primary label, secondary text, badges, metadata, or trailing values. A custom rendering escape hatch may exist for exceptional cases without making domain presentation the generic component's responsibility.

The generic core supports both single-selection and multi-selection modes. It is a controlled core with convenience defaults: the component can manage its own state for ordinary use, while consumers may control relevant state when they need preselection, external reset, URL synchronization, or similar orchestration.

## Authoritative data ownership

The frontend owns **no domain data or domain IDs**. IDs, nodes, relationships, eligibility, and domain meaning come from the database/backend. The frontend must not invent an opening, group, line, ID, or relationship.

The database remains domain-shaped. The normalized Line Library representation is an **API transport contract, not a new database model**. Opening tables and relationships remain opening data; future domains remain free to use storage structures appropriate to those domains.

Each domain backend is responsible for querying and filtering its authoritative data and translating the result into the shared Line Library response contract. The Line Library then renders and interacts with that response.

The backend/database supplies authoritative nodes, IDs, and relationships. A domain-specific frontend implementation may make presentation-only choices over those supplied facts, such as visual arrangement, expansion defaults, metadata display, or use of backend-supported sorting. It may not invent domain identity or relationships.

## Shared normalized API contract

The shared backend Line Library contract uses a **normalized tree** rather than deeply nested node objects. Conceptually, a response has authoritative root IDs plus a collection of nodes keyed or addressable by authoritative ID, with relationships represented by child IDs and reference targets.

This is deliberately a transport shape. It is intended to remain workable if later implementations require lazy children, partial responses, very large trees, references, server-provided counts, or additional metadata without forcing the underlying database into the same representation.

The common node vocabulary explicitly distinguishes:

- **group** — may contain descendants and may itself be selectable;
- **line** — a concrete selectable leaf;
- **reference** — a non-selectable pointer to another authoritative canonical node.

This explicit distinction is preferred over making the frontend infer semantics from metadata or generic capability flags.

Groups and lines may additionally be returned as **disabled** while remaining visible. When they are disabled, the backend supplies the reason. References are inherently non-selectable.

The shared contract also provides a generic vocabulary for filters and sorting while leaving domain semantics with the domain endpoint. The frontend may understand generic filter types and controls, but it does not know what a domain concept such as ECO means unless the backend declares it.

## Hierarchy and transpositions

The opening hierarchy is based on authoritative chess-derived relationships from the backend/database, with the opening implementation free to make presentation choices that do not change those relationships.

Where a line has multiple graph relationships, including transpositions, it has **one canonical selectable location**. Other appearances are represented as non-selectable `reference` nodes that navigate or point to the canonical authoritative node. The same concrete line must not appear as multiple independently selectable copies in different branches.

The hierarchy supports arbitrary depth. Any selectable group represents the concrete eligible lines beneath it in the currently returned tree.

## Selection semantics

Users may select either groups/families or concrete lines.

A group selection always means the group's **currently visible and eligible filtered descendants**, not every hidden member of the canonical family. This keeps one consistent selection model across filtering and direct leaf selection.

The generic Line Library resolves a selected group by traversing the **already filtered tree returned by the API** and collecting its visible eligible descendant line IDs. This traversal is generic tree-selection mechanics and does not make the frontend authoritative for domain data.

For group selection, the committed generic selection description preserves:

- the selected group/family identity;
- the active filter state relevant to that selection; and
- the resolved concrete line IDs represented by that selection.

The generic component reports what was selected. Each domain implementation owns any domain-specific payload or resolution layer needed to turn that generic description into a later downstream operation.

In multi-select mode, groups use tri-state selection:

- unchecked when none of their visible eligible descendants are selected;
- indeterminate when some are selected; and
- checked when all are selected.

Selecting or clearing a group acts on the currently visible eligible descendants.

When filters change, group selections are recomputed against the newly returned eligible set. A concrete leaf selection that is filtered out is removed from selection. Selection is always a subset of the current eligible result.

If an operation imposes a multi-select maximum, that maximum is **backend-declared**. The frontend enforces the returned limit as interaction behavior but is not the source of truth for the constraint.

## Filtering, search, and sorting

Filtering and search for provider-backed domains are performed by the **API/database**, not by client-side domain logic. The Line Library owns generic filter/search interaction state and rendering, then sends the domain-declared filter values to the provider/API.

The shared contract defines reusable filter primitives plus a custom escape hatch. Standard controls may include generic types such as search, select, multiselect, toggle, or range. A domain endpoint declares which filters exist, their labels, backend-owned keys, available options, and any domain metadata needed to render them.

Filter submission timing is configurable. A Line Library use may apply filter changes immediately or require an explicit Apply action. The reusable component supports both rather than baking one network behavior into every domain.

The backend owns the default ordering of returned groups and lines. A domain may additionally declare supported sort modes. The Line Library can render those options and send the selected sort key back without learning the domain meaning of that sort.

## Loading and failure behavior

While a new filter/search request is in flight, the **last successful tree remains visible** so the interface does not unnecessarily collapse or jump. That old result is visibly updating and selection is temporarily disabled because it no longer represents the requested filter state.

If the request fails, the last successful tree remains visible but disabled. The UI surfaces the failure and requires a successful retry or later successful request before selection resumes.

Backend failures use **appropriate HTTP status codes**. Errors must not be represented as successful `200` responses containing an application-level failure flag.

## Lazy loading and scale

The shared contract is designed so lazy loading can be introduced later, but the first opening implementation does **not** require it. Opening v1 returns the entire normalized tree for the current filtered result in one response.

Similarly, the component should be architected so row virtualization can be introduced if real data volume warrants it, but virtualization is **not part of v1**. The decision deliberately avoids adding TanStack Virtual or equivalent complexity before measurement shows it is needed.

The reusable component may support provider-backed and in-memory data sources as an abstraction. The opening implementation is provider/API-backed, and its filtering remains server-side.

## Opening v1 specialization

The first domain implementation is the chess opening library.

Its initial filter scope is intentionally lean:

- text search;
- ECO code/range; and
- "appears in my games".

Additional domain filters such as side, frequency, result, rating, date, or other analytics are deferred. The expectation is that a correct generic filter contract makes future additions incremental rather than architectural changes.

Opening v1 returns the complete filtered normalized hierarchy in one response. The backend owns authoritative opening IDs, hierarchy relationships, filtering, default ordering, any declared sort modes, disabled state/reasons, and applicable selection constraints.

## Explicit non-goals and exclusions

This grilling did **not** authorize or require:

- a generic Line Library database schema or generic node tables;
- frontend-generated domain IDs, groups, lines, relationships, or eligibility rules;
- client-side opening search or filtering over an authoritative full catalog;
- duplicate selectable copies of transposed lines;
- board playback, move navigation, repertoire mutation, training, or downstream API execution inside Line Library;
- lazy-loading implementation in opening v1;
- row virtualization in v1;
- opening filters beyond text search, ECO code/range, and "appears in my games" for v1;
- a particular endpoint name, Python module path, TypeScript file layout, Pydantic model name, database migration, or implementation sequence; or
- implementation work merely because this record now exists.

Those details belong to later planning or implementation work and must not be inferred as settled here.

## Confirmed direction

The confirmed direction is therefore a reusable rendered selector with generic interaction mechanics and a shared normalized backend transport contract, while domain APIs remain authoritative for all domain data and semantics. Openings are the first implementation and should prove the abstraction without forcing opening-specific knowledge into the reusable component.

The component is deliberately designed to accommodate future complexity—deeper hierarchies, references, disabled nodes, backend-declared limits, more filters and sort modes, lazy providers, and eventual virtualization—while keeping the first opening implementation simple enough to return one complete filtered normalized tree.