# Design exploration as a narrowing funnel

> **Status:** workflow direction settled on 2026-08-31
>
> This is a reusable capability description and a retrospective. It is intended to inform future agents and
> skills, but it does not prescribe agent boundaries and it is not an implementation Plan.

## Purpose

Design exploration exists to help a person make decisions. Its success is not measured by how many artifacts it
produces, how polished every discarded option becomes, or how much implementation work it anticipates. It succeeds
when uncertainty becomes narrower and the person can select a design with confidence.

The work is deliberately freeform. Mock-ups, catalogues, branches, grilling, manual edits, and design documents are
capabilities to use when helpful, not mandatory lifecycle stages. A common journey is:

1. begin with an existing or newly created mock-up;
2. turn the broad design question into a catalogue of substantially different options;
3. select one option and branch it into a narrower catalogue;
4. repeat selection and branching as often as useful, reducing the scope each time;
5. refine the preferred result, including direct human edits;
6. grill unresolved details and repository consequences;
7. after final sign-off, write a detailed, repository-aware design document; and
8. hand the final mock-up and design document to the existing planning system.

That sequence is illustrative rather than compulsory. Work may enter midway, skip a catalogue, return to an earlier
question, combine techniques, or stop whenever the person directing the exploration chooses.

## The funnel

Exploration should normally move from divergence to convergence.

Early rounds ask wide questions: What basic mental model should the interface use? What information matters? Should
the interaction be a card, comparison, timeline, command surface, or something else? These alternatives should be
structurally different. Cosmetic changes alone are rarely useful at this point.

After a person chooses a parent concept, the next branch inherits that decision and asks a smaller question. It may
compare two boxes with three, alternative action arrangements, different state explanations, or different ways to
communicate replacement. A later branch may narrow further into wording, button hierarchy, icon treatment, spacing,
or one unresolved transition.

Every branch should make its lineage understandable, regardless of whether it lives in a new file or an existing
one. It should identify:

- the parent concept;
- the narrower question now being explored; and
- the decisions and constraints inherited unchanged from the parent.

The workflow does not require a particular folder structure, numbering scheme, or one-file-per-round policy. The
important property is conceptual narrowing, not artifact ceremony.

## Catalogues as decision aids

A catalogue presents options together so they can be compared. Each option should receive concise decision support:
its central idea, its meaningful differences, and its important trade-offs. It should not receive the exhaustive
specification reserved for the final selection.

The catalogue may be a pamphlet-like HTML document, a set of static frames, an interactive prototype, or another
form suited to the question. It should contain only as much interaction as the decision requires. Layout questions
may use static examples; state-transition questions may benefit from working controls. Fidelity and validation are
matters of judgment, not prescribed gates.

Rejected alternatives remain user-controlled. They may be disposable, but an agent must preserve them until the
user explicitly removes them or authorizes cleanup. Selecting one option does not itself authorize deletion of the
others.

## Human authority and sign-off

The person directing the work decides when exploration is mature enough to advance. Information completeness is
helpful but is not a gate: constraints can be refined over time.

Direct human edits to a selected mock-up are authoritative, including edits made in another context. The next
capability should inspect the latest artifact, understand what changed, and carry those changes forward rather than
restoring an earlier interpretation. It may report a contradiction or technical consequence, but it must not silently
overrule the edit.

Changes after sign-off are handled according to impact:

- small clarifications may update downstream artifacts directly; and
- behavioral, contractual, or visual-direction changes reopen exploration and require another selection and
  sign-off.

The workflow assumes the user keeps the final mock-up and design document coherent. If an agent nevertheless finds a
contradiction, it reports it rather than inventing precedence or choosing an interpretation.

## Repository grounding at two depths

Repository-aware design benefits from two different levels of investigation.

### Lightweight grounding during exploration

Before or during broad exploration, perform a bounded factual check of the current interface, genuine user-visible
states, important existing capabilities, and obvious technical constraints. This is not intended to make the design
obedient to the current implementation. It prevents alternatives from depending on imaginary states or accidentally
discarding real behavior.

### Detailed grounding after selection

Once the mock-up is final and signed off, inspect the relevant components, models, data flow, contracts, styling
foundations, accessibility behavior, and focused tests in detail. This mapping belongs in the final design document.
Doing it at this point avoids spending implementation-level research on branches likely to be discarded.

## Grilling within the funnel

Grilling may happen at two levels:

- During branching, use focused questions whenever an option exposes a material uncertainty. Ask only decisions;
  retrieve repository facts directly.
- After final visual selection, conduct a repository-grounded grilling pass before writing the detailed design
  document. This catches missing states, ambiguous interactions, retained capabilities, persistence consequences,
  and distinctions that the mock-up alone cannot settle.

Grilling should continue until the person confirms the shared understanding. It should not force completeness for
its own sake: the purpose is to settle decisions that matter now while allowing later refinement.

## The final design document

The detailed design document exists only after the mock-up has been finalized and signed off. Earlier catalogue
notes and rationales are useful exploration evidence but are not substitutes for it.

The document explains the selected design and how it relates to the current repository. Depending on the component,
that can include:

- purpose, mental model, terminology, and non-goals;
- visible anatomy and information hierarchy;
- meaningful states, conditions, transitions, and action visibility;
- interaction, persistence, pending, error, and recovery semantics;
- copy rules and anti-duplication rules;
- visual roles, responsive behavior, tokens, and reusable component boundaries;
- keyboard, focus, semantic, announcement, contrast, and reduced-motion behavior;
- current repository components, models, APIs, ownership boundaries, and tests affected by the design; and
- settled invariants and genuinely unresolved technical facts.

It does not define implementation stages, progress tracking, proof execution, or Plan lifecycle mechanics. After the
design document and final mock-up are ready, they pass to the repository's existing planning system. This exploration
workflow ends at that hand-off.

## Capability boundaries

This direction intentionally avoids deciding how many agents or skills should exist. Future tooling can package the
work in different ways, but the capabilities and hand-offs should remain legible:

- retrieve a lightweight factual baseline;
- create an initial mock-up when one does not already exist;
- generate and explain broad alternatives;
- branch a selected concept around a narrower question;
- incorporate authoritative human edits;
- retrieve detailed repository facts;
- grill unresolved decisions;
- synthesize the finalized design and repository mapping; and
- hand the resulting evidence to the existing planning system.

An agent may perform several capabilities, or one capability may be implemented as a reusable skill. The workflow
does not assume either arrangement.

---

## Case study: preferred-move panel

The preferred-move-panel exercise illustrates the funnel without defining its only valid form.

### Broad catalogue

The work began from an existing `/repertoire` preferred-move panel and produced one pamphlet containing six broad
directions. They differed in hierarchy and mental model rather than merely colour or spacing: a decision card, split
action rail, state timeline, compact command bar, explicit comparison, and stable disclosure treatment. Shared state
examples and short rationales made the alternatives comparable.

### Repeated narrowing

The explicit-comparison concept was selected and branched. From that branch, the decision-stack direction was
selected and narrowed again around whether the design needed three boxes or whether the played/staged move could
also be the proposal. The next selection was **The staged move is the proposal**, a two-box model contrasting the
current saved choice with the temporary staged move.

Each round asked less than the previous one. The process moved from whole-panel mental models, to comparison
structures, to state semantics, and finally to action labels, copy duplication, icon spacing, and button treatment.

### Human refinement

The selected mock-up was refined directly, including adjustments made in a separate context. Those edits became the
new authority. Earlier branches remained exploratory until the user cleaned the folder and retained only the chosen
direction.

### Copy review

A focused review found that the panel repeated the same facts through several labels and explanatory paragraphs:
“no proposal,” “no stage,” “no move staged,” and disabled-Save narration all described one condition; “saved,”
“persisted,” “baseline,” and “current saved choice” described one fact; and the effective date appeared twice. The
selected artifact was simplified to let the boxes and action state communicate more of the behavior themselves.

### Final repository-grounded grilling

The final grilling pass compared the mock-up with the current repository and uncovered questions the visual artifact
could not settle on its own:

- whether the existing **Play saved move** capability was intentionally removed;
- whether explicit Edit mode still existed behind the two-box layout;
- whether old played-match and played-different states remained meaningful;
- whether matching applied to played moves, staged moves, or both;
- whether consequence text was generic, model-owned prose, or component-owned templates;
- how a completely empty saved/staged relationship appeared;
- how the first effective date was chosen;
- what happened when playing the saved choice replaced a temporary proposal;
- whether removing a saved choice also removed staging; and
- whether changing an existing effective date was an independent operation.

The settled direction simplified the panel around relationships rather than named workflow states. Every played move
became staged; clicking the saved-choice box retained the old play capability; explicit Edit mode disappeared;
matching became a saved-versus-staged comparison; Remove retained staging; date change became independent; and fixed
component templates explained the consequence from structured move facts.

This pass also exposed a technical fact: the existing same-move save contract could not safely perform a date-only
change. That did not require reopening the visual direction, but it needed to be recorded for the downstream system.

### Heavy design hand-off

Only after the visual direction and behavior were signed off was
`experiments/mock-ups/preferred-move-panel/DESIGN.md` written beside
`experiments/mock-ups/preferred-move-panel/02-staged-move-is-the-proposal-final-choice.html`. The document mapped the
selected design onto current components, workflow state, API behavior, design tokens, accessibility expectations,
and focused tests without becoming an implementation Plan.

The final mock-up and design document were then ready for hand-off to the existing planning workflow. The case shows
why the funnel is useful: broad creativity happened before expensive specification, while detailed repository work
waited until there was one selected design worth specifying.

## Lessons from the case study

1. **Branch the question, not just the appearance.** Each round should inherit more decisions and explore a smaller
   uncertainty.
2. **A mock-up can imply behavior without settling it.** Final grilling is where implied behavior becomes explicit.
3. **Current implementation states are evidence, not automatically the right product model.** Some should be
   preserved; others can be collapsed after their underlying facts are understood.
4. **Human cleanup and refinement are part of the workflow.** Agents preserve alternatives until told otherwise and
   treat later user edits as authoritative.
5. **Do not write the heavy design document for every branch.** Detailed repository mapping becomes worthwhile only
   after selection.
6. **The hand-off should carry both views of the design.** The mock-up communicates the chosen composition; the
   design document communicates behavior, constraints, and repository meaning.
