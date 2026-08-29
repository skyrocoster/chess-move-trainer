---
name: validate
description: "Use in a fresh PHASE: VALIDATE session to independently check one observable result without editing."
---

# Validate

Require the observable outcome, exact approved paths, baseline and diff facts, exclusions, acceptance, retained
proof with its covered behavior and inputs, changes since each proof item, and exact missing or invalidated checks.
If a required field is missing, return `BLOCKED` without searching for it. Reject implementation narrative or
requests to infer approval.

1. In one Git inspection, compare changed path names and only the relevant changed hunks with the approved scope.
   Do not inspect adjacent files, unrelated changes, or recheck Git state later.
2. Independently classify each retained passing proof as valid or invalidated. It remains valid when no later
   change could affect its command, selected tests, exercised product paths or behavior, configuration,
   dependencies, fixtures, generated inputs, or required environment. Fresh-session independence does not by
   itself invalidate proof.
3. Run each supplied missing or invalidated focused check once via the `bash` tool with an explicit finite timeout
   in milliseconds (missing, zero, or non-finite timeouts are forbidden because commands can hang), in order. Do
   not run a full or broader suite when its only purpose is to repeat retained proof. Stop on the first definitive
   required failure unless another supplied check is necessary to classify it.
4. Invoke `browser-validation-invoke` only when an exact missing or invalidated browser scenario is supplied.
5. Compare retained and new evidence only with explicit acceptance, report unrelated failures separately, and return.

Validation is read-only. `PASS` requires valid green proof for every required check, clean scope, and satisfied
acceptance; that proof may be retained or newly run. Use `FAIL` for a behavior, proof, or scope mismatch and
`BLOCKED` for missing evidence or infrastructure.

Do not add checks, review architecture or implementation quality, search for hidden requirements, diagnose beyond
what is needed to classify the result, or repeat a command to gain confidence.

```text
RESULT: PASS | FAIL | BLOCKED
RETAINED: <still-valid passing proof, or none>
COMMANDS: <exact newly run commands and results, or none>
INVALIDATED: <proof rejected and affecting change, or none>
EVIDENCE: <observable findings>
SCOPE: clean | <discrepancy>
ARTIFACTS: none | <paths>
UNRELATED: none | <separate failure>
NEXT: accept | authorize one exact fix | stop
ISSUE: none | <failure or blocker>
```

Never repair, update Plan state, change acceptance, commit, or push.
