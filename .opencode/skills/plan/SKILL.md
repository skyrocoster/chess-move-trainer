---
name: plan
description: "Use during PHASE: WRITE PLAN to create or refine one approved focused implementation Plan without coding."
---

# Plan

Require an approved target under `docs/plans/active/<feature>/<feature>.md`, outcome, scope, stage shape, proof,
acceptance, and escalation boundaries. Reuse retained assessment facts; read only `docs/PLAN_TEMPLATE.md`, the
router, and an existing matching Plan when present. Never implement.

Write the compact template exactly enough to preserve:

- one semantic, human-visible outcome and visible-result line;
- upstream evidence, expected areas, and explicit exclusions;
- sequential AI-focused stages with ordered actions, focused proof, and real breakpoints;
- non-overlapping proof where practical, with reruns only after a stage changes something that could affect the
  earlier result;
- concise progress and decisions; and
- escalation boundaries for any decision not already settled.

Expected areas describe ownership; they are not exact executor authorization. Do not add parallel stages,
transient execution logs, speculative work, or legacy records. Preserve truthful completed progress when refining
an existing Plan. If outcome, scope, dependency, proof, or acceptance is unresolved, do not guess.

Do not prescribe the same command for implementation, Quality, and closeout. State that passing proof is retained
until an affecting change; Quality audits and fills evidence gaps; closeout uses `scripts/check.py` selectors only
for required steps not already covered by valid proof.

Run the coordinator-supplied documentation check when present, with an explicit finite `bash` tool timeout in
milliseconds (missing, zero, or non-finite timeouts are forbidden because commands can hang); otherwise inspect
the final document against the template and report that no automated Plan checker exists.

```text
RESULT: WRITTEN | UNDER-CAPTURED | BLOCKED
PATH: <approved Plan path or none>
CHECKS: <command and result, or manual template review>
ISSUE: none | <missing decision or blocker>
```
