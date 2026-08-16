---
name: validate-stage
description: Independently validate an accepted Plan stage, including its sole order when applicable, and record it.
---

# Validate and ship one Plan stage

Use this skill only when the coordinator explicitly selects `validate-stage` after an exact Plan stage has received
explicit human acceptance. The coordinator may infer that an order appears final from canonical Plan narrative,
order names, numbering, and dependencies, but this skill is the independent guard. It must reject ambiguous or
incomplete stage evidence rather than writing lifecycle state.

For a stage containing exactly one order, this is the only validation operation: validate the executor result, record
the order `DONE` with executor and validator evidence, and ship the stage in one combined operation. Do not require or
run `validate-order` first. For a stage containing multiple orders, retain the existing stage-shipment operation after
each order has separately passed `validate-order`.

## Scope and permissions

The validator is the existing `coordinator-validator` agent. Its file scope remains `docs/` only. The approved
manifest must name exactly one active Plan, the accepted stage's canonical order paths, and the triggering order path;
the skill may read those paths and write the named Plan path plus the sole order path only for a single-order stage.
Never add a machine-readable stage-to-order mapping
or final-order marker. Never read or edit product source, tests, configuration, `.opencode/`, `artifacts/`, unrelated
Plans, unrelated orders, indexes, manifests, dependency records, or narrative-reference artifacts.

The skill cannot repair implementation, rewrite order evidence, infer human acceptance, authorize another stage,
validate the whole Plan, commit, or push.

## Required handoff

The coordinator handoff must contain all of the following before the skill reads the Plan:

```text
validator: coordinator-validator
skill: validate-stage
coordinator_approved: true
approved_paths: [one active Plan path and every unique order path in the stage]
plan_path: <exact active Plan path>
stage: <exact stage number and canonical name>
trigger_order_path: <exact order path>
stage_order_paths: <complete canonical order set supplied from Plan context; trigger_order_path is one member>
human_stage_acceptance: <explicit acceptance for this exact Plan and stage>
executor_result: <immutable EXECUTOR RESULT and proof output; required for a single-order stage>
order_validation_evidence: <immutable successful validate-order evidence for every order; required for a multi-order stage>
baseline_and_diff: <immutable facts for the stage scope>
checks: <exact independent checks and required browser result, or none>
exclusions: <stage exclusions and lifecycle boundaries>
```

Reject missing or non-explicit acceptance, missing order paths, duplicate or drifting paths, implementation narrative,
or an incomplete evidence packet. Acceptance for a different stage, a prior unrecorded validation, or a coordinator
inference without human approval is not authorization.

## Execution contract

1. Read the named Plan and every named stage order only. Use the Plan's canonical narrative, stage numbering, order
   names, and dependencies to verify the supplied stage boundary; do not invent schema or discover a mapping.
2. Confirm the stage identity and stage cardinality. For a single-order stage, independently validate that order's
   executor result, proof, authorization audit, dirty-path facts, attempts, deviations, escalation, scope, and
   exclusions exactly as `validate-order` would; the order need not already be `DONE`. For a multi-order stage,
   confirm every order has canonical `STATUS: DONE` and successful executor and independent validator evidence.
   Confirm the triggering order and supplied baseline/diff facts agree with the stage scope.
3. Confirm explicit human acceptance identifies this exact Plan and stage. Repeat every exact independent check
   supplied by the coordinator, invoking `browser-validation-invoke` first when required.
4. If stage membership, numbering, dependencies, order completion, proof, scope, exclusions, or acceptance is
   ambiguous or incomplete, return evidence only. Do not edit the Plan or any order.
5. After every check passes, perform one combined lifecycle operation. For a single-order stage, set the sole order's
   canonical status to `DONE`, record its executor and validator evidence in the existing evidence structure, and
   update the named Plan's stage status and `Shipped` record. For a multi-order stage, update only the Plan stage
   status and `Shipped` record. Do not change other stages, order packets, indexes, manifests, dependencies, or
   narrative references.
6. Stop after this stage operation. A shipped stage is not permission to select the next stage or close the Plan.

The write is atomic at the documentation-operation boundary: all order, stage, and acceptance checks must pass before
any lifecycle update begins. If every required write cannot be completed, report the write failure and do not claim
order completion or shipment.

## Return

```text
RESULT: PASS | FAIL | BLOCKED
SKILL: validate-stage
PLAN: <exact active Plan path>
STAGE: <number and canonical name>
SHIPMENT WRITE: stage Status and Shipped updated | none
ORDER STATUS WRITE: DONE with executor and validator evidence | already validated | none
COMMANDS: <exact independent commands and results>
EVIDENCE: <stage identity, order completeness, acceptance, proof, scope, and exclusion findings>
SCOPE: clean | <exact discrepancy>
APPROVALS: coordinator approved and explicit human stage acceptance | <missing or invalid approval>
NEXT: <coordinator final-stage inspection, next-stage report, or stop>
ISSUE: <none or exact blocker>
```
