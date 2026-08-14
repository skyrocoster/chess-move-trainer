---
name: write-focused-plan
description: Use ONLY when the coordinator resumes its original Luna case-worker to write an approved focused Plan from retained assessment evidence, including a high-yield compiler handoff.
---

# Write the approved focused Plan

Write the Plan from retained case context and the frontier's corrections. Do not restart broad repository
exploration, implement code, or author work orders.

Require `PROPOSAL APPROVED`, exact `TARGET PATH`, and `FRONTIER CORRECTIONS`. For a real active Plan,
the target must match `docs/plans/active/<feature>/<feature>.md`: the feature directory is required and
the Plan filename must repeat the feature name so future `NN-<slug>.md` work orders can be colocated.
Reject a flat active-Plan target before writing; normalize it to the nested form only when the coordinator
has explicitly authorized that correction. A path under `scratch/` is allowed only when the user explicitly
authorized that simulation path.

1. Apply every frontier correction without reopening settled decisions.
2. Validate the target shape before any write. Create the approved feature directory as needed, and move an
   already-written flat Plan only when that move is explicitly authorized; never silently leave a real Plan
   at `docs/plans/active/<feature>.md`.
3. For a real active Plan, validate every `Touches` entry as a repo-relative glob that currently matches at
   least one existing file or directory. Keep exact paths for future files in the stage compiler handoff;
   never create placeholder production files merely to satisfy the documentation checker.
4. For a real active Plan, use the Layer 1 schema in `docs/PLAN_TEMPLATE.md`: Status, Read trigger, human
   outcome, stages, empty Shipped table, Touches, and stage-grouped compiler handoff. Include UX decisions when
   an interface change requires them; do not invoke a separate interview when conservative defaults were approved.
5. Keep human-facing sections concise. Require explicit observable acceptance and exclusions before writing.
   Preserve paid-for repository answers in the compiler handoff: exact
   owning symbols/state flow, precedents, existing test behaviors, consumers/defaults, relevant CSS/shell
   constraints, useful absent-precedent searches, settled contracts, and true open lookup questions.
6. Touches are ownership globs, not an accidental list that forbids a likely feature-local component. Do not
   authorize unrelated consumer paths merely because they need regression protection. Conditional paths and
   verification-only files are not unconditional Touches; preserve their escalation/verification status.
7. Record frontier-settled stage routing as `ORDERED` or `QUICK-CANDIDATE`, never `ORDERED-CANDIDATE`. Keep
   one coherent stage when partial work would not be a valid human-visible shipment; internal sequencing
   belongs in work orders.
8. For a real active Plan, run `.venv\Scripts\python.exe scripts/check_docs.py --write-generated`, inspect that
   generated changes are regeneration-shaped, then run `.venv\Scripts\python.exe scripts/check_docs.py --check`.
   A user-authorized scratch simulation is outside the docs contract and runs neither command.
9. Never commit.

Return:

```text
RESULT: WRITTEN | BLOCKED | FAILED
ARTIFACT: <path>
CHECKS: <commands/results or scratch exemption>
CONTEXT YIELD: <compiler facts preserved; unnecessary assessment omitted>
REVIEW FLAGS: <anything requiring frontier artifact review, or none>
ISSUE: <none or exact blocker>
```
