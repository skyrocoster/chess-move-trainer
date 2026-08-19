---
name: validate
description: "Use in a fresh PHASE: VALIDATE session to independently check one observable result without editing."
---

# Validate

Require the observable outcome, exact approved paths, baseline and diff facts, exclusions, acceptance, and exact
checks. Reject implementation narrative or requests to infer approval.

1. Inspect the diff and changed paths against the approved scope.
2. Repeat every supplied focused check and the full suite only when requested.
3. Invoke `browser-validation-invoke` when the packet requires live UI evidence.
4. Compare observable behavior with acceptance and report unrelated failures separately.

Validation is read-only. `PASS` requires green checks, clean scope, and satisfied acceptance. Use `FAIL` for a
behavior, proof, or scope mismatch and `BLOCKED` for missing evidence or infrastructure.

```text
RESULT: PASS | FAIL | BLOCKED
COMMANDS: <exact commands and results>
EVIDENCE: <observable findings>
SCOPE: clean | <discrepancy>
ARTIFACTS: none | <paths>
UNRELATED: none | <separate failure>
NEXT: accept | authorize one exact fix | stop
ISSUE: none | <failure or blocker>
```

Never repair, update Plan state, change acceptance, commit, or push.
