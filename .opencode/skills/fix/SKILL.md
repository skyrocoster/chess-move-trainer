---
name: fix
description: "Use during PHASE: FIX to apply one exact coordinator-authorized repair after failed Quality validation."
---

# Fix

Require the failed validation evidence, exact paths, intended semantics, failed check, and one deterministic repair.
If a required field is missing, return `BLOCKED` without investigating. Reject an open-ended diagnosis or any
request to widen scope.

Apply the named deterministic repair without exploring alternatives. Rerun only the failed focused check once via
the `bash` tool with an explicit finite timeout in milliseconds (missing, zero, or non-finite timeouts are
forbidden because commands can hang), confirm once that only the authorized paths changed, and return
immediately. Do not inspect Git state before the repair or recheck it afterward. If the repair or check fails,
report that result without further diagnosis or another edit.

```text
RESULT: REPAIRED | FAILED | BLOCKED
EDITS: <changed paths or none>
CHECK: <exact command and result>
SCOPE: clean | <discrepancy>
ISSUE: none | <remaining failure or blocker>
NEXT: fresh Quality validation | coordinator review
```

A fix never validates itself. Do not run another repair cycle, edit historical records, create workflow
artifacts, run additional checks, commit, or push.
