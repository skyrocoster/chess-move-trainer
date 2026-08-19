---
name: prototype
description: Use for one isolated Python or TypeScript experiment under experiments to answer a concrete technical question.
---

# Prototype

Require one technical question, hypothesis, and observable success signal. Create the smallest dependency-light
experiment under `experiments/prototypes/<topic>/`; use the experiments workspace rather than application
manifests. Keep small reusable inputs in `experiments/fixtures/` and downloads or generated output in the topic's
ignored `.artifacts/` directory.

Do not import application code or modify product source. Run the experiment and report observation separately
from conclusion.

```text
RESULT: CONFIRMED | DISPROVED | INCONCLUSIVE | BLOCKED
PATHS: <experiment files>
COMMAND: <exact command>
OBSERVED: <output or measurements>
CONCLUSION: <answer limited to the evidence>
LIMITS: none | <remaining uncertainty>
```

Prototype output is noncanonical until explicitly adopted. Do not edit tests, Plans, canonical documentation, or
unrelated `Scratch` content.
