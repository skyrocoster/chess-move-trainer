---
name: validate-plan
description: Verify every Plan stage is shipped and perform bounded whole-Plan closeout.
---

# Validate and close one Plan

Use this skill only when the coordinator explicitly selects `validate-plan` after the coordinator has determined that
the just-shipped stage appears to be the final stage. No additional whole-Plan human acceptance is required: every
stage was separately accepted before `validate-stage` recorded shipment. This skill independently verifies that fact
and performs only the confirmed bounded closeout.

## Scope and permissions

The validator is the existing `coordinator-validator` agent. Its file scope remains `docs/` only. The approved
manifest must name the active Plan, its exact destination under `docs/plans/done/`, and every completed canonical order
file that may be deleted. The skill may write only those approved Plan/order paths and remove only folders made empty by
those deletions. Never read or edit product source, tests, configuration, `.opencode/`, `artifacts/`, indexes,
manifests, dependency records, narrative-reference artifacts, or unrelated Plans and orders.

The skill cannot add a final-stage marker or stage mapping, repair implementation, rewrite a shipment record, run a
separate reconciliation system, commit, or push.

## Required handoff

The coordinator handoff must contain all of the following before the skill reads the Plan:

```text
validator: coordinator-validator
skill: validate-plan
coordinator_approved: true
approved_paths: [active Plan path, destination Plan path, and every completed order path]
active_plan_path: <exact docs/plans/active/... Plan path>
done_plan_path: <exact docs/plans/done/... Plan path>
final_stage: <stage identified by Plan narrative>
completed_order_paths: <complete canonical order list to remove after closeout>
stage_shipment_evidence: <immutable successful validate-stage evidence for every stage>
checks: <exact independent checks, or none>
exclusions: <Plan closeout exclusions>
```

Reject missing or non-canonical active/done paths, a destination that is not the matching active-to-done move, missing
stage evidence, implementation narrative, mutable evidence, path drift, or any request for broader closeout work.

## Execution contract

1. Read the active Plan and every supplied completed order path only. Verify the Plan identity, all stages in its
   canonical narrative, and a successful shipment record for every stage. Do not infer completion from one final order,
   executor success, or unrecorded validation.
2. Verify the supplied final-stage context is consistent with the Plan's narrative and that every completed order to be
   removed is canonical, belongs to this Plan, and is already complete. Reject incomplete or ambiguous stage evidence
   without writing.
3. Repeat every exact independent check supplied by the coordinator and include its result. Do not add an index,
   manifest, dependency, narrative-reference, or broader closeout check outside the approved packet.
4. After every verification passes, move the Plan from its exact active path to the exact matching done path, delete
   only the completed order files in the manifest, and remove only folders that became empty as a direct result. Do not
   edit the Plan contents during the move or alter unrelated documentation.
5. Treat the move and cleanup as one bounded write-after-pass operation. If any precondition fails, return without
   writing. If an approved filesystem operation fails, stop and report the exact partial-operation risk; never improvise
   recovery or touch an unapproved path.
6. Stop after Plan closeout. Do not update indexes, manifests, dependency records, narrative references, or commit.

## Return

```text
RESULT: PASS | FAIL | BLOCKED
SKILL: validate-plan
PLAN: <active path -> done path>
CLOSEOUT WRITE: Plan moved, completed orders deleted, empty folders removed | none
COMMANDS: <exact independent commands and results>
EVIDENCE: <all-stage shipment, final-stage, order-identity, and exclusion findings>
SCOPE: clean | <exact discrepancy>
APPROVALS: coordinator approved; no additional whole-Plan acceptance required | <invalid approval>
NEXT: <report closed Plan, or stop>
ISSUE: <none or exact blocker>
```
