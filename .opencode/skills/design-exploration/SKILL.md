---
name: design-exploration
description: Use when substantial UI or interaction direction is unsettled and exploration should narrow alternatives into a signed-off mock-up and repository-aware design hand-off.
---

# Design exploration

Own design exploration as a flexible narrowing funnel. Keep user decisions and sign-off in the coordinator while
delegating repository facts to `scout` and artifacts to `exploration`. Exploration is optional, noncanonical, and
ends before implementation assessment or Plan writing.

## Decision frontier

Retain only the information needed for the next useful move:

- the latest authoritative artifact and its parent concept;
- the narrower question currently being explored;
- inherited decisions and constraints that remain fixed;
- material unresolved decisions; and
- whether the user has signed off the visual direction and the final design hand-off.

Do not impose a stage checklist, folder convention, numbering scheme, or one-file-per-round rule. Work may enter
midway, skip a catalogue, revisit an earlier question, or stop when the user chooses.

## Route the funnel

1. Retrieve a lightweight factual baseline through one or more bounded `scout` lookups: the current interface,
   genuine user-visible states, retained capabilities, and obvious constraints. Treat implementation as evidence,
   not as the required design.
2. If no useful artifact exists, send `exploration` a bounded `mock-up` brief. For comparison work, send a
   `design-catalogue` brief naming the parent, question, inherited decisions, baseline facts, and minimum sufficient
   fidelity.
3. Present the result as a decision aid. Ask the user to select, reject, combine, refine, or stop. Selection does not
   authorize deletion of alternatives.
4. For another round, branch only the selected concept around a narrower question. Resume the same exploration
   session when its context is still useful; otherwise send a complete frontier packet to a fresh session.
5. Use `grilling` during branching only when an option exposes a material decision that artifacts cannot settle.
   Ask the user for decisions and retrieve repository facts directly.
6. Treat direct user edits to the latest artifact as authoritative. Bound and inspect them before continuing; never
   restore an older interpretation. Report contradictions or consequences instead of silently overruling edits.
7. Obtain explicit visual sign-off when the user considers the selected artifact final. Information completeness is
   helpful but is not a gate.
8. After visual sign-off, retrieve detailed facts about relevant components, models, data flow, contracts, styling,
   accessibility, and focused tests. Then use `grilling` to settle behavior the mock-up cannot express.
9. Send `exploration` a `design-synthesis` brief containing the signed-off artifact, settled decisions, detailed
   repository facts, and unresolved technical facts. Ask the user to confirm the coherent mock-up and design
   document.
10. After final sign-off, end exploration and route the evidence through the existing assessment and planning
    workflow. The design document is not a Plan and does not authorize implementation.

## Fidelity

Use the lowest fidelity that lets the user make the current decision:

- **Static:** self-contained HTML and CSS with representative states shown together.
- **Interactive-light:** self-contained HTML, CSS, and minimal JavaScript for local controls.
- **Behavioral:** React when shared state, transitions, conditional behavior, focus, or realistic interaction is the
  decision under review.
- **Repository-integrated:** only after selection when real component composition or application constraints must be
  evaluated.

Prefer self-contained HTML/CSS/JavaScript for early structural divergence because alternatives are cheap to compare
and discard. Do not require HTML when every option needs substantial interaction, and do not migrate an artifact to
React merely because exploration has advanced. Continue an existing React artifact rather than converting it
backward. Do not import application code during early exploration unless the brief explicitly requires a
repository-integrated evaluation.

## Reopening

Small post-sign-off clarifications may update downstream artifacts directly. A behavioral, contractual, or visual-
direction change reopens exploration and requires renewed selection and sign-off. If the final mock-up and design
document conflict, report the contradiction; do not invent precedence.
