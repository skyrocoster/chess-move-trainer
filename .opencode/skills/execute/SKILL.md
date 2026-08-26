---
name: execute
description: Use during an execute phase to implement one approved direct change or one Plan stage and prove it.
---

# Execute

Require a coordinator packet containing the phase, outcome, exact paths or bounded Plan area, known facts,
ordered actions, proof commands, acceptance, exclusions, support skills if any, and escalation boundaries. Return
`BLOCKED` before editing when any required field is missing or contradictory.

1. Inspect only the approved paths and trust the packet's dirty-state baseline. Preserve unrelated changes.
2. For a bug, capture a meaningful red regression when it is cheap and deterministic; never manufacture a brittle
   source-text failure.
3. Make the smallest approved change. Do not refactor, polish, or repair adjacent behavior.
4. Run every focused proof command. Use full-suite or browser proof only when the packet requires it.
5. Perform one final changed-path and semantic scope audit against the packet. Do not repeatedly run `git status`
   or `git diff`. On a failed check, make at most one deterministic, in-scope repair and rerun that check once;
   never weaken proof.
6. Stop without updating Plan progress. The coordinator records accepted results.

Escalate before crossing a path boundary or making a new product, visual, API, data, dependency, destructive,
ownership, or acceptance decision.

```text
RESULT: DONE | BLOCKED | ESCALATED | FAILED
EDITS: <changed paths or none>
REGRESSION: <red/green evidence or why red was not useful>
PROOF: <exact commands and results>
SCOPE AUDIT: clean | <discrepancy>
ACCEPTANCE: <observable result or remaining breakpoint>
RESIDUAL RISK: none | <specific risk>
ISSUE: none | <blocker>
```

Never create workflow artifacts, commit, or push.
