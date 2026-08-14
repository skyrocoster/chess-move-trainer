---
name: master-plan
description: Create or refine a detailed master plan under docs/master-plans/ for a broad product destination. Use when the user says "master plan", wants to align on a cross-cutting redesign or multi-feature outcome, or needs a large direction split into small human-visible slices. Produces no implementation code or active Plans.
---

# Master plan

Define a broad, concrete product destination and divide it into independently reviewable slices. A
master plan is more detailed than a design principle and broader than an execution Plan. It records
decisions, not implementation status or authority.

## Method

1. Read `docs/README.md`, `docs/MASTER_PLAN_TEMPLATE.md`, related canonical references, and any existing
   master plan for the same destination. Look up repository facts instead of asking the user.
2. Resolve product decisions with the user. Ask one decision at a time, offer three concrete choices,
   mark one `(Recommended)`, and explain the evidence behind the recommendation.
3. Write or refine `docs/master-plans/<slug>.md` using the template. Be detailed enough that later
   routing can either deliver an atomic slice directly or create a focused Plan without rediscovering
   the destination.
4. Use ASCII mockups for UI composition, controls, transformations, states, and interaction sequences
   whenever a picture makes the decision more concrete.
5. Split the destination into small slices. Each slice delivers one specifically scoped feature or
   addition with both a clear **Human can see** result and a clear **Human can do** result.
6. Run the documentation checker after writing the document.

## Boundaries

- Do not implement code, create work orders, or treat the master plan as active queue status.
- Distinguish current repository facts from desired behavior. Present tense describes the destination
  only when the document says so explicitly.
- Name constraints, dependencies, exclusions, responsive behavior, accessibility, failure states, and
  acceptance actions concretely. Terms such as `standard`, `responsive`, and `as appropriate` are not
  decisions.
- Keep slices independently judgeable. Split any slice that changes multiple visible concepts or whose
  acceptance cannot be stated as one coherent user outcome.
- Require human acceptance after every visible slice. Automated checks support that gate but do not
  replace it.
- Do not label slices as direct or Plan-required while authoring the destination. Source shape and
  execution risk can change; `to-plan` judges the route autonomously when a slice is selected.

## Handoff

End by summarizing the destination, unresolved decisions, and the first independently valuable slice.
Implementation starts only when the user selects a slice and `to-plan` verifies its prerequisites and
autonomously routes it to direct quick delivery or a focused Plan.
