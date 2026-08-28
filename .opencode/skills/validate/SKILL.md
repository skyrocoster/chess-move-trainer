---
name: validate
description: "Use in a fresh PHASE: VALIDATE session to independently check one observable result without editing."
---

# Validate

Require the observable outcome, exact approved paths, baseline and diff facts, exclusions, acceptance, and exact
checks. If a required field is missing, return `BLOCKED` without searching for it. Reject implementation narrative
or requests to infer approval.

1. In one Git inspection, compare changed path names and only the relevant changed hunks with the approved scope.
   Do not inspect adjacent files, unrelated changes, or recheck Git state later.
2. Run each supplied focused check once via the `bash` tool with an explicit finite timeout in milliseconds
   (missing, zero, or non-finite timeouts are forbidden because commands can hang), in order, and the full suite
   only when explicitly requested. Stop on the first definitive required failure unless another supplied check is
   necessary to classify it.
3. Invoke `browser-validation-invoke` only when an exact browser scenario is supplied.
4. Compare the resulting evidence only with explicit acceptance, report unrelated failures separately, and return.

Validation is read-only. `PASS` requires green checks, clean scope, and satisfied acceptance. Use `FAIL` for a
behavior, proof, or scope mismatch and `BLOCKED` for missing evidence or infrastructure.

Do not add checks, review architecture or implementation quality, search for hidden requirements, diagnose beyond
what is needed to classify the result, or repeat a command to gain confidence.

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
