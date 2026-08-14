---
name: deliver-direct
description: Use ONLY when the coordinator resumes its original Luna case-worker with an approved direct change and proof contract; implements, verifies, checks scope, and stops without committing.
---

# Deliver an approved direct change

This phase runs in the same case-worker session that assessed the change. Reuse retained repository context;
do not restart exploration.

Require explicit `ROUTE APPROVED`, `GOAL`, exact `AUTHORIZED PATHS`, `KNOWN FACTS`, one `CHANGE`, a `PROOF
CONTRACT`, `CLOSEOUT`, and `ESCALATE IF`. Missing fields block execution.

1. Confirm current facts still match the approved envelope using only already-known sites or a tiny freshness
   check. Do not broaden assessment.
2. For a bug, establish the approved red regression evidence before production editing when cheap and
   deterministic. Do not create a brittle source-text assertion merely to manufacture red.
3. Make the smallest approved change, only in authorized paths. Add the behavior-local regression guard when
   the proof requires it.
4. Run every triggered focused check from the proof, using only commands the adopting repository documents.
   A visible UI change requires live evidence only when the proof contract says so; it does not automatically
   require a full suite.
5. Audit `git diff` against authorized paths, one logical change, and assessed intent. Preserve unrelated dirty
   worktree state.
6. If a required check identifies a deterministic documentation or metadata defect inside an already authorized
   path, use at most the existing remaining verification attempt to make the smallest repair when it preserves
   approved intent and does not expand behavior, ownership, external contracts, or production scope. Re-run the
   check; escalate for an unauthorized path, semantic widening, ambiguity, or exhausted attempts.
7. Run `.venv\Scripts\python.exe scripts/check_docs.py --check` for every closeout. FOCUSED may update the
   authorized documentation-managed surface before checking. FULL is exceptional for direct delivery and runs
   `.venv\Scripts\python.exe scripts/stage_check.py` plus canonical docs. If closeout needs unapproved paths,
   escalate instead of widening.
8. Never commit. Stop after two failed verification runs total. Never weaken proof.

Return:

```text
RESULT: FIXED-PENDING-VALIDATION | VERIFIED | ESCALATED | FAILED
EDITS: <authorized changed paths>
REGRESSION: <red/green evidence, or why red was inappropriate>
CHECKS: <commands and results>
SCOPE AUDIT: clean | <exact discrepancy>
LIVE CHECK: required | not required
ACCEPTANCE SCRIPT: <observable states/viewports/unchanged behavior, or none>
CLOSEOUT: <tier and docs-check result>
ISSUE: <none or exact blocker>
```

Use `FIXED-PENDING-VALIDATION` when independent live proof remains. Use `VERIFIED` only when the approved proof
did not require it and every other check passed.
