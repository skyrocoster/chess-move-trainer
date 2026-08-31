---
name: design-catalogue
description: Use in noncanonical UI exploration to compare broad alternatives or branch a selected concept around one narrower design question.
---

# Design catalogue

Create a comparative decision aid under `experiments/mock-ups/<topic>/`. Require a parent concept or starting
surface, one question, inherited decisions and constraints, lightweight repository facts, and the minimum fidelity
needed to decide. When continuing existing work, inspect the latest artifact first and preserve authoritative user
edits.

## Shape the alternatives

- For broad exploration, make options structurally different in mental model, hierarchy, information, or
  interaction. Cosmetic variations alone are insufficient unless appearance is the explicit question.
- For a branch, inherit the selected parent unchanged except for the narrower question. Make lineage legible in the
  artifact regardless of filenames or folder structure.
- Give every option concise decision support: central idea, meaningful differences, and important trade-offs. Do not
  write the exhaustive specification reserved for the final choice.
- Use realistic content and genuine user-visible states. Preserve important existing capabilities unless their
  removal is explicitly being explored.
- Include only enough interaction to evaluate the question. Keep rejected alternatives until the user explicitly
  authorizes cleanup.

## Choose fidelity

Default early catalogues to one self-contained HTML/CSS page, with minimal JavaScript when useful. Use React in the
experiments workspace when shared state, transitions, conditional actions, keyboard or focus behavior, responsive
interaction, or realistic component composition is material to the decision. Continue the artifact's existing
technology when changing it would add work without improving the decision.

React output must remain isolated under `experiments/mock-ups/<topic>/`, use the experiments workspace and its
dependencies, and provide an exact finite command for viewing it. Do not import application code unless the brief
explicitly requests a repository-integrated comparison after selection. Do not add dependencies when the existing
workspace can answer the question.

Use responsive layout, semantic elements, visible keyboard focus, and reduced-motion handling at either fidelity.
When browser tooling is available, verify the comparison surface loads without console errors and exercise only the
interaction required by the decision.

```text
RESULT: CREATED | UPDATED | BLOCKED
PATHS: <exact catalogue paths>
LINEAGE: <parent; current question; inherited decisions>
OPTIONS: <central idea and trade-off for each option>
FIDELITY: STATIC | INTERACTIVE-LIGHT | REACT | REPOSITORY-INTEGRATED
VERIFICATION: <finite command or browser scenario and observed result>
NEXT DECISION: <one selection or unresolved question for the user>
LIMITS: none | <known limitation>
```

Do not choose the winner, delete alternatives, edit product source or tests, or turn catalogue notes into an
implementation Plan.
