---
name: mock-up
description: Use for one standalone noncanonical UI mock-up under experiments when visual options need review.
---

# Mock-up

Create one self-contained HTML file under `experiments/mock-ups/<topic>/`. Use `frontend-design` first when the
brief needs a visual direction. Put requested alternatives in the same file and label the decision each tests.

Use realistic content, responsive layout, semantic HTML, visible keyboard focus, and reduced-motion handling.
Inline CSS and minimal optional JavaScript are allowed; external assets, network requests, and application imports
are not. Verify the file loads without console errors when browser tooling is available.

```text
RESULT: CREATED | BLOCKED
PATH: <exact HTML path>
VERIFICATION: <how it was viewed and observed result>
REVIEW: <decision or alternatives presented>
LIMITS: none | <known limitation>
```

Do not edit product source, tests, Plans, canonical documentation, or unrelated `Scratch` content.
