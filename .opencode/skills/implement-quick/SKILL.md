---
name: implement-quick
description: Use ONLY in the coordinator's quick executor for one fully settled planned quick stage with exact paths, facts, change, proof, and escalation boundaries.
---

# Implement one quick brief

Execute one complete brief and stop. Do not read the Plan or explore outside its authorization.

## Required brief

```text
GOAL: <one outcome>
AUTHORIZED PATHS: <exact files and bounded sections when needed>
KNOWN FACTS: <verified answers, not lookup instructions>
CHANGE: <one atomic logical edit>
PROOF CONTRACT: <regression guard; exact focused commands; live requirement>
ESCALATE IF: <scope/fact/contract boundaries>
```

Block before reading source if any field is missing, a path is a broad conditional glob, the change contains
multiple independently useful outcomes, or the proof delegates a decision to you.

## Execute

1. Read the brief once. Trust `KNOWN FACTS`; do not re-assess the route or search for alternatives.
2. Read only `AUTHORIZED PATHS`, bounded to named symbols/sections when supplied.
3. Establish approved red evidence before the production fix when cheap and deterministic. Do not add brittle
   implementation-detail checks solely to manufacture red.
4. Make the smallest `CHANGE`. Do not refactor, rename, polish, or repair nearby behavior.
5. Run every exact focused command in `PROOF CONTRACT`. Apply triggered lint/typecheck only when already named
   in the contract; the brief author owns check selection.
6. Audit the changed paths and logical scope. Preserve unrelated dirty worktree state.
7. Stop after the first green proof. If proof fails, make at most one distinct in-scope repair and rerun once.
   Two failed verification runs total means `FAILED`; never weaken proof.
8. Do not run closeout, documentation regeneration, full suites, browser validation, or commits unless the
   brief explicitly includes a focused command. The coordinator owns post-implementation routing.

Escalate without improvising when a known fact is wrong, another path is needed, scope grows, a design/
architecture/API/data/migration/compatibility/diagnosis/contract decision appears, or live proof reveals a
different failure boundary. Leave truthful partial work in place.

Return exactly:

```text
RESULT: DONE | ESCALATED | FAILED | BLOCKED
EDITS: <changed paths, or none>
REGRESSION: <red/green evidence, or why red was inappropriate>
CHECKS: <commands and results>
SCOPE AUDIT: clean | <exact discrepancy>
LIVE CHECK: required | not required
ACCEPTANCE SCRIPT: <brief's observable script, or none>
ATTEMPTS: <verification runs and repair count>
ISSUE: <none or exact blocker>
```
