---
name: implement-order
description: Use ONLY in the coordinator's case-worker for one explicitly approved canonical work order.
---

# Implement one ordered boundary

Execute exactly one already-approved canonical work order, then stop. This bounded route is not dispatch, validation,
reconciliation, or lifecycle closeout.

## Required handoff

Require `ROUTE APPROVED: yes`, one exact `ORDER PATH` matching
`docs/plans/active/<feature>/orders/<NN>-<slug>.md`, and `ESCALATE IF` before reading anything. Reject missing,
non-canonical, or multiple order paths; never discover or select an order.

## Execution contract

1. Read the named order once. Trust its embedded canonical JSON compile packet; do not re-derive facts, authorization,
   actions, proof, acceptance, exclusions, or escalation boundaries.
2. Read only packet `context` paths and do not reflexively reread edited sources.
3. Perform ordered packet actions and touch only `authorization.creates`, `authorization.edits`, and
   `authorization.removes`. Never add paths, actions, adapters, or semantics.
4. Run each exact packet proof command in declared order. Do not execute coordinator or validator acceptance.
5. On proof failure, make at most one deterministic in-scope repair, then rerun that proof once. Escalate rather than
   diagnosing broadly, weakening proof, or widening scope.
6. Audit dirty paths and authorization; preserve unrelated worktree changes.
7. Record truthful proof, scope, attempts, deviations, and escalation details. Do not rewrite the
   order, packet, Plan, status, or lifecycle artifacts.
8. Stop after this one order. Never dispatch another order, independently validate, reconcile, close out a Plan/order
   lifecycle, commit, or push.

## Return

```text
RESULT: DONE | FAILED | BLOCKED | ESCALATED
ORDER: <exact path>
EDITS: <changed paths, or none>
PROOF: <exact commands and results>
SCOPE AUDIT: clean | <exact discrepancy>
TELEMETRY: <attempts, guard events, deviations, and relevant proof facts>
ISSUE: <none or exact blocker>
```

`DONE` requires packet proofs and authorization audit to pass. Use `FAILED` for an exhausted proof attempt, `BLOCKED`
for unusable authorization/order input, and `ESCALATED` for packet, contract, permission, or scope conflicts.
