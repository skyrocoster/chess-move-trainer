---
name: assess-case
description: "Use during PHASE: ASSESS to investigate one repository request and select the smallest safe route without editing."
---

# Assess one case

Investigate one bounded request and select the smallest safe route. Never edit, write a workflow record, or start
downstream work.

1. Read `docs/README.md`, the relevant active Plan or destination record when one exists, the owning source,
   focused tests, and only the nearest consumer or precedent needed to establish the change shape.
2. Separate observed facts from desired behavior. Treat grilling records and master plans as optional evidence,
   not mandatory steps.
3. Define the observable outcome, included and excluded behavior, expected paths, implementation-critical facts,
   proof, acceptance, useful support skills, and exact escalation boundary.

Choose:

- `DIRECT-CANDIDATE` for one settled outcome with exact paths, focused proof, and no durable coordination need.
- `PLAN-CANDIDATE` for one coherent outcome needing durable context, multiple sequential stages, or breakpoints.
- `MASTER-PLAN-CANDIDATE` for a broad destination with at least two independently selectable outcomes.
- `QUESTION`, `BLOCKED`, or `NO-PROBLEM` only when the evidence supports that result.

Return:

```text
RESULT: DIRECT-CANDIDATE | PLAN-CANDIDATE | MASTER-PLAN-CANDIDATE | QUESTION | BLOCKED | NO-PROBLEM
TARGET: <surface or destination>
OUTCOME: <observable result>
ROUTE BASIS: <why this is the smallest safe route>
EVIDENCE: <concise path:line or symbol facts>
SCOPE: <included behavior; expected paths; explicit exclusions>
CHANGE SHAPE: <one logical change, sequential stages, or selectable slices>
KNOWN FACTS: <facts execution must preserve>
SUPPORT SKILLS: none | <explicit skill names and purpose>
PROOF: <regression guard, exact focused commands, full/live proof when required>
ACCEPTANCE: <observable pass condition and any real breakpoint>
ESCALATE IF: <specific decision or scope boundary>
ISSUE: none | <question or blocker>
```

Stop after the result.
