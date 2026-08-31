---
name: mock-up
description: Use for one standalone noncanonical HTML or React UI mock-up under experiments when a visual direction needs review.
---

# Mock-up

Create one isolated review artifact under `experiments/mock-ups/<topic>/`. Use `frontend-design` first when the
brief needs a visual direction. For comparative alternatives or a branch from a selected concept, use
`design-catalogue` instead. When continuing an artifact, inspect the latest version first and preserve authoritative
user edits.

Use the lowest fidelity that answers the review question. Prefer one self-contained HTML/CSS file with minimal
optional JavaScript for a static or lightly interactive surface. Use React in the experiments workspace when shared
state, transitions, conditional behavior, focus, or realistic interaction is material. Continue an existing React
artifact instead of converting it backward, and do not migrate to React merely because exploration has advanced.

Use realistic content, responsive layout, semantic elements, visible keyboard focus, and reduced-motion handling.
Keep early exploration isolated from application imports and network requests. A repository-integrated mock-up may
use real components only when the brief explicitly requests it after selection. Verify the artifact loads without
console errors when browser tooling is available; give React artifacts an exact finite viewing command.

```text
RESULT: CREATED | UPDATED | BLOCKED
PATHS: <exact artifact paths>
FIDELITY: STATIC | INTERACTIVE-LIGHT | REACT | REPOSITORY-INTEGRATED
VERIFICATION: <how it was viewed and observed result>
REVIEW: <direction or decision presented>
LIMITS: none | <known limitation>
```

Do not edit product source, tests, Plans, canonical documentation, or unrelated `Scratch` content.
