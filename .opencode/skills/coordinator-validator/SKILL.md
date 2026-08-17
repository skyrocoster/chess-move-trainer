---
name: coordinator-validator
description: Response-only independent validation for direct and planned-quick proof packets.
---

# Direct and planned-quick validation

This compatibility skill preserves the existing response-only validator route for direct changes and planned-quick
stages. It is not the lifecycle operation for canonical ordered Plan work. The coordinator must select
`validate-order`, `validate-stage`, or `validate-plan` for that hierarchy.

## Scope and permissions

The validator's file scope is `docs/` only, enforced by the agent's `permission` block: `read`, `edit`
(`edit`/`write`/`patch`), `glob`, `grep`, and `list` allow only `docs/` — a catch-all `"*": deny` comes first and
the narrow `"docs"` / `"docs/*"` allow rules come last. Every path outside `docs/` is denied: source code, tests,
configuration, `.opencode/`, `artifacts/`, and any other location.

- The validator receives only an observable proof packet and baseline/diff facts, never implementation narrative.
- Validation is read-only. It never edits product implementation, tests, configuration, or lifecycle documentation.
- Bash is retained only for the exact supplied checks, the full local check suite, and read-only inspection. The check
  script may regenerate derived configuration as an expected side effect.
- Do not diagnose or repair a product failure. Return evidence and stop.

## Required handoff

The coordinator handoff must identify the route as `direct` or `planned-quick` and provide:

- the observable outcome and acceptance expectations;
- immutable proof output, baseline and diff facts, and any machine-readable browser result;
- the exact checks to repeat, including any required browser-validation invocation; and
- the exclusions and scope audit needed to judge the proof.

Reject implementation narrative, missing evidence, path drift, unexpected changes, failed checks, or any request to
edit a lifecycle artifact. A direct or planned-quick result never authorizes order, stage, or Plan closeout.

## Execution

1. Confirm the supplied proof packet and changed-path facts without exploring outside the handoff.
2. Repeat every supplied independent check from fresh context. Run
   `.venv\Scripts\python.exe scripts\check.py` when required by the packet and include its output.
3. Check the observable acceptance, exclusions, and scope facts. Do not infer a missing product or human decision.
4. Return evidence only. Do not record `DONE`, shipment, Plan status, or archival state.

## Return

```text
RESULT: PASS | FAIL | BLOCKED
ROUTE: direct | planned-quick
COMMANDS: <exact commands and results>
EVIDENCE: <observable proof and independent findings>
SCOPE: clean | <exact discrepancy>
ARTIFACTS: <browser or other machine-readable artifacts, or none>
NEXT: <coordinator action, or stop>
ISSUE: <none or exact blocker>
```
