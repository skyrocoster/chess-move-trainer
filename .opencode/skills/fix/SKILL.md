---
name: fix
description: "Use during PHASE: FIX to apply one exact coordinator-authorized repair after failed Quality validation."
---

# Fix

Require the failed validation evidence, exact paths, intended semantics, failed check, and one deterministic repair.
Reject an open-ended diagnosis or any request to widen scope.

Apply the smallest named repair, rerun only the failed focused check once, audit the changed paths, and stop.

```text
RESULT: REPAIRED | FAILED | BLOCKED
EDITS: <changed paths or none>
CHECK: <exact command and result>
SCOPE: clean | <discrepancy>
ISSUE: none | <remaining failure or blocker>
NEXT: fresh Quality validation | coordinator review
```

A fix never validates itself. Do not run another repair cycle, edit historical records, create workflow
artifacts, commit, or push.
