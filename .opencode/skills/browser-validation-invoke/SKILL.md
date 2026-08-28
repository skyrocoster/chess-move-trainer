---
name: browser-validation-invoke
description: Use from Quality validation to capture isolated browser evidence for one exact approved UI scenario.
---

# Browser validation invocation

This supporting skill captures evidence; the parent `validate` skill decides the overall Quality result. Do not
edit repository files or reuse a browser profile from implementation.

Require the startup command when needed, target URL, exact user steps, expected observations, setup and cleanup,
and artifact location. If required information is missing, return `INFRA-FAIL` without searching for it. Reject an
open-ended request to explore the UI.

Run the supplied scenario once with the configured Playwright tools, and run any required startup command via the
`bash` tool with an explicit finite timeout in milliseconds (missing, zero, or non-finite timeouts are forbidden
because commands can hang). Capture only the requested assertions and artifacts, plus scenario-breaking console
or network failures observed during those steps. Do not explore other pages, states, responsive sizes, or edge
cases. Clean up anything started by the scenario and return immediately.

```text
RESULT: PASS | PRODUCT-FAIL | INFRA-FAIL
SCENARIO: <steps performed>
EVIDENCE: <observations and assertions>
CONSOLE/NETWORK: clean | <failures>
ARTIFACTS: none | <paths>
ISSUE: none | <product or infrastructure failure>
```
