# Master Plan Template

A master plan defines a broad, cross-cutting product destination in enough detail that later execution
does not reopen settled product decisions. It is a working design document, not an execution Plan,
queue entry, or implementation authority.

Master plans live at `docs/master-plans/<slug>.md`. For exactly one selected slice, the coordinator
chooses direct quick delivery or a focused Plan under `docs/plans/active/`, preserving explicit
dependencies and human acceptance.

## Authoring Standard

- Be detailed. Record the destination, rationale, interaction rules, important states, boundaries, and
  acceptance evidence rather than only naming themes or epics.
- State whether present-tense prose describes current behavior or the desired destination. Never let a
  desired behavior read as already shipped.
- Use ASCII mockups whenever UI layout, hierarchy, transitions, responsive transformations, layered
  surfaces, or tool states are easier to judge visually than in prose.
- Label important controls and regions in mockups. Show wide and constrained compositions when they
  differ. Add state or step mockups when the interaction changes over time.
- Split work by human-observable value, not by technical layer. Each slice must have one coherent
  **Human can see** outcome and one coherent **Human can do** outcome.
- Make slices small enough to implement and judge independently. If a slice changes several visual
  concepts, requires multiple acceptance stories, or can only be understood as “finish the redesign,”
  split it again.
- State exclusions aggressively so adjacent cleanup, refactors, and later slices cannot hitchhike.
- Use exact nouns, actions, viewport conditions, and states. `Standard`, `responsive`, `intuitive`,
  `clean up`, and `as appropriate` are placeholders, not decisions.

## Document Template

Replace every prompt. Remove sections that truly do not apply rather than leaving empty headings.

````md
# <Destination Name> - Master Plan

> **Status:** <Decision state only, such as “Draft for guided review” or “Destination agreed.” State
> explicitly that this document authorizes no implementation.>

## What This Document Is

<Define the destination and why it needs a master plan rather than one focused Plan. Explain that
implementation status lives only in docs/plans/active/. State how present-tense destination language
must be read.>

## Why This Change Exists

<Describe the human problem, where the current experience breaks down, and why the destination matters.
Use repository evidence for current behavior and clearly label assumptions.>

## Product Outcome

> <One concise statement of the broad human outcome.>

### Success Means

- **Human can see:** <What becomes visibly clear across the completed destination.>
- **Human can do:** <What task or workflow becomes possible or materially better.>
- **The product preserves:** <Important existing capability or invariant.>

## Governing Principles

- <Decision rule later slices must follow.>
- <Accessibility, input, safety, audience, or interruption rule.>
- <Principle that resolves likely tradeoffs.>

## Current State

<Only verified current facts. Name the relevant surfaces and behavior without turning this into a source
inventory. Include a compact current-state mockup when useful.>

```text
+---------------- current ----------------+
| <label visible regions and controls>     |
+------------------------------------------+
```

## Destination

<Describe the complete desired composition and behavior. Organize large destinations into named product
concepts. For each concept, settle hierarchy, interaction, state, responsive transformation,
accessibility, feedback, and failure behavior as applicable.>

### <Destination Concept>

<Concrete decisions and rationale.>

```text
Wide:
+------------------------------------------------+
| <labelled destination composition>             |
+------------------------------------------------+

Constrained:
+---------------------------+
| <labelled transformation> |
+---------------------------+
```

### Interaction And State Rules

- **Entry:** <How the human enters or starts the workflow.>
- **Primary action:** <What advances the task and where it remains reachable.>
- **Selection/focus:** <What selection means and how focus behaves.>
- **Empty:** <What is visible and actionable with no data or selection.>
- **Loading:** <What region waits and what remains usable.>
- **Failure:** <Where the failure appears and how recovery works.>
- **Success/save:** <How completion or durability is communicated.>
- **Escape/cancel/back:** <Exact precedence and state preservation.>
- **Wide/constrained:** <What docks, overlays, moves, collapses, or becomes sequential.>
- **Keyboard/touch:** <Equivalent paths and target/focus requirements.>

### Interaction Sequence

```text
Step 1: <starting state>
  [control] -> <immediate visible response>

Step 2: <changed state>
  <human action> -> <result, save, navigation, or error>
```

## Cross-Cutting Constraints

- <Architecture, data, API, audience, accessibility, or ownership boundary.>
- <Existing behavior that must not regress.>
- <Canonical reference that remains authoritative until a slice ships.>

## Small Visible Slices

Each row is a destination slice, not active implementation status. A focused Plan may split a row
further but must not silently combine rows. Dependencies mean “accepted by a human,” not merely merged
or green in CI.

| Slice | Requires accepted | Human can see | Human can do | Explicit boundary | Human gate |
|---|---|---|---|---|---|
| <MP-01> | - | <One visible result> | <One operable capability> | <Nearby work excluded> | <Shortest decisive acceptance path> |
| <MP-02> | <MP-01> | <One visible result> | <One operable capability> | <Nearby work excluded> | <Shortest decisive acceptance path> |

## Slice Delivery Receipts

This table is written only by `quick-reconcile` or `reconcile`. It is route-independent delivery and
acceptance evidence, not an implementation queue. Omit rows for slices that have not reached a
reconcile path.

| Slice | Route | State | Evidence |
|---|---|---|---|
| <MP-01> | Direct or Plan | Implemented; awaiting human acceptance or Accepted YYYY-MM-DD | <Focused check and short outcome, or linked Plan> |

### <MP-01> - <Human-Visible Feature Name>

**Human can see**

> <One sentence a non-developer can verify by looking at the named surface.>

**Human can do**

> <One sentence naming an action and observable result.>

**Before**

```text
+-----------------------------+
| <current composition/state> |
+-----------------------------+
```

**After**

```text
+---------------------------------+
| <slice composition/state only>  |
+---------------------------------+
```

**Included**

- <Exact visible behavior delivered by this slice.>
- <Exact interaction, responsive, accessibility, or state behavior delivered here.>

**Explicitly excluded**

- <Named adjacent slice, refactor, or behavior that must not hitchhike.>
- <Technical redesign not required for the human outcome.>

**Prerequisite**

<Accepted slice IDs or none. Explain the behavioral dependency. The focused Plan must encode any
implementation dependency using the repository Plan format.>

**Human acceptance script**

1. Open <named surface> with <required data/state> at <wide or constrained condition>.
2. Confirm <specific visible result>.
3. Perform <specific action> and confirm <specific result>.
4. Repeat the applicable input path when keyboard, pointer, or touch behavior is relevant.
6. Confirm <named preserved behavior or neighboring surface> is unchanged.

**Automated gate**

- <Focused behavior and accessibility regressions.>
- <Required repository checks.>

**Stop condition**

> Stop when <human can see result>, <human can do result>, automated checks pass, and the human marks
> <MP-01> accepted. Do not begin <named adjacent slices>.

## Explicitly Outside This Master Plan

- <Tempting adjacent product change.>
- <Architecture, data, visual-system, or workflow redesign not required by this destination.>
- <Future idea deliberately left undecided.>

## Source Ownership Expected By Future Focused Plans

<Name likely owning areas and bounded source families only to route later exploration. State that every
focused Plan must verify and narrow these paths and does not inherit this whole list.>

## Verification Standard For Future Slices

<State focused automated expectations and the human review conditions: representative data, wide and
constrained layouts, keyboard-plus-mouse, touch, accessibility, and preserved neighboring behavior as
applicable. Human judgment remains the final gate for visible work.>

## Open Decisions

- <Unsettled decision, owner, and what evidence would settle it, or “None.”>

## Provenance

<Prior plans, accepted mockups, user decisions, research, or superseded documents folded into this
destination. Distinguish directional evidence from binding decisions.>
````

## Slice Quality Gate

Before keeping a slice, answer yes to every question:

1. Can a non-developer describe one new thing they will see?
2. Can they perform one named action and observe its result?
3. Can the slice ship without an adjacent slice also being implemented?
4. Do the before/after mockups or descriptions show only this slice's change?
5. Are empty, loading, failure, responsive, keyboard, and touch behavior settled where relevant?
6. Does the acceptance script test behavior rather than CSS classes or implementation structure?
7. Does the stop condition forbid starting the next visible change?

If any answer is no, refine the decision or split the slice before creating a focused Plan.

Slice quality does not decide execution transport. When a slice is selected, `to-plan` judges from
current repository evidence whether direct delivery is safe or durable Plan state is necessary.
