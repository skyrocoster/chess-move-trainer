---
name: validate-order
description: Independently validate one completed canonical order and record its DONE evidence.
---

# Validate one canonical order

Use this skill only when the coordinator explicitly selects `validate-order` for one canonical ordered Plan order in
a stage containing multiple orders. A single-order stage uses `validate-stage` once instead.
The executor's `DONE` result is implementation evidence, not lifecycle completion. This skill independently checks
that result and, only after every check passes, records the canonical order as `DONE` with executor and validator
evidence.

## Scope and permissions

The validator is the existing `coordinator-validator` agent. Its file scope remains `docs/` only: read and write only
the exact approved order path under `docs/plans/active/<feature>/orders/`. Never read or edit product source, tests,
configuration, `.opencode/`, `artifacts/`, Plans, other orders, or any path outside the supplied manifest.

The skill is documentation-only. It cannot repair implementation, amend proof, broaden the order scope, infer human
acceptance, mark a stage shipped, close a Plan, commit, or push.

## Required handoff

The coordinator handoff must contain all of the following before the skill reads the order:

```text
validator: coordinator-validator
skill: validate-order
coordinator_approved: true
approved_paths: [one exact canonical order path under docs/]
order_path: <the same exact path>
executor_result: <immutable EXECUTOR RESULT and proof output>
baseline_and_diff: <immutable facts sufficient for scope comparison>
checks: <exact independent checks and required browser result, or none>
exclusions: <order exclusions and lifecycle boundaries>
```

Reject missing or duplicated order paths, non-canonical paths, implementation narrative, mutable evidence, path drift,
or missing executor proof. The handoff must not ask this skill to inspect a Plan or infer stage membership.

## Execution contract

1. Read the named order once and compare its canonical packet, authorization, acceptance, exclusions, and expected
   proof with the immutable handoff. Do not re-derive the packet or discover another order.
2. Confirm the executor result is for this exact order and that its proof, authorization audit, dirty-path facts,
   attempts, deviations, and escalation are complete and successful.
3. Repeat every exact independent check supplied by the coordinator. Invoke `browser-validation-invoke` first when
   the packet requires browser evidence. Run the repository's full check suite when the handoff requires it and
   include the machine-readable result.
4. Compare changed paths with the order authorization and reject unexpected paths, missing proof, failed proof,
   exclusion violations, or any ambiguity. Previous unrecorded validation is not durable evidence.
5. On failure, return evidence only. Do not edit the order or any other file.
6. On success, perform one write-after-pass update to the named order: set its canonical status to `DONE` and record
   both the executor evidence and the independent validator evidence in the existing order evidence structure. Do
   not make a partial lifecycle update or alter the packet, implementation instructions, or unrelated prose.
7. Stop after this operation. Do not validate a stage or Plan and do not authorize the next order. If the supplied
   Plan context establishes that this is a single-order stage, reject the handoff and require the combined
   `validate-stage` route instead.

The write is atomic at the documentation-operation boundary: all validation must pass before the single canonical
order update begins. If the approved order cannot be written completely, report the write failure and do not claim
success.

## Return

```text
RESULT: PASS | FAIL | BLOCKED
SKILL: validate-order
ORDER: <exact canonical order path>
STATUS WRITE: DONE with executor and validator evidence | none
COMMANDS: <exact independent commands and results>
EVIDENCE: <identity, proof, authorization, diff, and exclusion findings>
SCOPE: clean | <exact discrepancy>
APPROVALS: coordinator approved | <missing or invalid approval>
NEXT: <coordinator stage-context inspection, or stop>
ISSUE: <none or exact blocker>
```
