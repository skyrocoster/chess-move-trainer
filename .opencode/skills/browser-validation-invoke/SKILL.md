---
name: browser-validation-invoke
description: Use from Quality validation to capture isolated browser evidence for one exact approved UI scenario.
---

# Browser validation invocation

This supporting skill captures evidence; the parent `validate` skill decides the overall Quality result. Do not
edit repository files or reuse a browser profile from implementation.

Require the startup command when needed, target URL, exact user steps, expected observations, setup and cleanup,
and artifact location. Reject an open-ended request to explore the UI.

Run only the supplied scenario with the configured Playwright tools. Capture relevant assertions, console errors,
failed network requests, and requested screenshots. Clean up started services and temporary data.

```text
RESULT: PASS | PRODUCT-FAIL | INFRA-FAIL
SCENARIO: <steps performed>
EVIDENCE: <observations and assertions>
CONSOLE/NETWORK: clean | <failures>
ARTIFACTS: none | <paths>
ISSUE: none | <product or infrastructure failure>
```
