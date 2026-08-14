---
name: ux-design
description: Decide interaction behavior for a UI surface before implementation. Use when planning or reshaping a page, dialog, editor, board, or flow; produces UX decisions for a Plan, not code.
---

# UX Design Decisions

This skill works at planning time. It produces decisions for a focused Plan; it does not write
implementation code or assume a framework, visual language, component library, or product domain.

## Read Before Deciding

1. Read the adopting repository's canonical design, accessibility, and interaction references when they
   exist.
2. Inspect the nearest existing surface with the same task shape.
3. Identify the operator, their goal, device constraints, and any interruption or safety constraints.
4. Treat missing canonical guidance as an open decision, not an invitation to invent project-wide rules.

## Decide The Surface

- **Primary task:** State the one task the surface makes easiest.
- **Priority:** Name what must remain visible or reachable when space is constrained.
- **Entry and exit:** Define how the person arrives, cancels, returns, and preserves work.
- **State:** Specify loading, empty, filtered-empty, error, success, and no-selection behavior where they
  apply, including visible copy when it matters.
- **Input:** Define keyboard, pointer, touch, focus, and target-size expectations relevant to the surface.
- **Persistence:** State whether saving is explicit, automatic, deferred, or unavailable, and how failure
  is communicated.
- **Destruction:** Require a confirmation, undo, or other deliberate recovery path when data loss is
  possible.
- **Responsive behavior:** Describe what moves, collapses, sequences, or remains fixed across supported
  viewport conditions.

## Output

Emit this block into the Plan. Fill each applicable line with a concrete decision; omit only behavior
that cannot occur on the surface.

```text
## UX Decisions - <surface name>

Operator:       <person or role>
Primary task:   <one outcome>
Focal element:  <what visually leads and why>
Entry/exit:     <route, cancel/back behavior, and preservation>
Layout:         <wide and constrained behavior>
State:          <loading, empty, error, success, no-selection behavior and copy>
Actions:        <primary, secondary, destructive, and recovery behavior>
Persistence:    <save model and failure feedback>
Input:          <keyboard, pointer, touch, focus, and target expectations>
Accessibility:  <semantic, contrast, announcement, or assistive-technology requirements>
Exclusions:     <adjacent work this decision does not authorize>
```

## Quality Gate

- A person can identify the surface's main task at a glance.
- Each state has a useful next action or an honest explanation.
- The design preserves work across interruption where the product requires it.
- Decisions follow existing project contracts when those contracts exist.
- New project-wide visual or interaction rules are proposed explicitly rather than silently introduced.
