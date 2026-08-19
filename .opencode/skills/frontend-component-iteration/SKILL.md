---
name: frontend-component-iteration
description: Use during approved execution for one user-led visual or interaction adjustment to an existing component.
---

# Frontend component iteration

Require an exact component and one approved visual or interaction adjustment. Read only its implementation,
styles, stories, focused tests, and direct dependencies.

1. Identify the concrete cause of the current behavior.
2. Make one smallest requested adjustment while preserving design tokens, accessibility, public contracts, and
   unrelated worktree changes.
3. Run only the proof named in the execute packet.
4. Report the observed change and stop at a genuine visual decision instead of batching speculative polish.

User edits made during review are authoritative. Bound and preserve them before continuing. Keep exploratory
alternatives under `experiments/`; do not create workflow records, broad documentation changes, or a redesign.
