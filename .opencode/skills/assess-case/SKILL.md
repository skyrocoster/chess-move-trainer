---
name: assess-case
description: Use ONLY in the coordinator's Luna case-worker ASSESS phase to investigate one repository-dependent request and recommend a direct change, focused Plan, or master plan without editing.
---

# Assess one case

Investigate one request in one bounded pass and recommend the smallest route that preserves the
coordination the work actually needs. Assessment gathers evidence and produces a reviewable route
envelope. It does not edit files, write a Plan or master plan, compile orders, implement changes, or
invoke downstream lifecycle work.

## Operating rules

1. Follow `AGENTS.md` and the routing manifest in `docs/README.md`. Read `scratch/` only when the
   handoff names an exact path there.
2. Identify the request as informational/meta, bug, feature, or refactor. Check relevant active Plans
   and `docs/master-plans/` before proposing new durable planning state.
3. Read the owning minimum context, the primary implementation surface, focused tests or styles, and
   structurally equivalent consumers. Use at most two repository-wide precedent searches.
4. For a reported bug, verify the behavior across the bounded class of equivalent rendering or
   computation sites. Use bounded history only when contracts, comments, siblings, and implementation
   disagree. Return `NO-PROBLEM` rather than inventing a defect.
5. Target at most 12 file reads, 4 searches, and roughly 25k input tokens. Read large or generated
   documents in bounded sections. Stop when the route, outcome, scope, proof strategy, and reusable
   implementation evidence are known.
6. Treat workflow scripts as invoke-only. Use their documented command or `--help`; read stdout and
   exit status, but do not open script source unless the request is to change that script's behavior.

Ask only when an answer can change the route or core outcome, control destructive behavior, or settle
an irreversible or external contract. Batch all known blocking questions. Apply repository precedent
and conservative, reversible defaults to presentation and implementation details after the outcome is
clear.

## Choose the route

`DIRECT-CANDIDATE`, `PLAN-CANDIDATE`, and `MASTER-PLAN-CANDIDATE` are peer recommendations. Choose
between them by the shape of the human outcome and its durable coordination need.

- Prefer the least ceremonial route that safely captures the work.
- File count, area count, technical layers, test count, or apparent effort do not select a route.
- The words “plan” and “master plan” in the request do not select a route.
- Missing low-level implementation details do not force a larger route when they can be recovered by
  a bounded lookup during compilation or execution.
- Several implementation stages may still form one focused Plan when they collectively deliver one
  independently acceptable outcome.
- Several independently valuable outcomes indicate a master plan when they belong to one destination
  and benefit from shared direction, boundaries, or sequencing. They do not have to cross ownership
  areas, and every shared decision does not have to block every slice.
- Use `QUESTION` or `BLOCKED` only when evidence is insufficient to select a route safely, not merely
  because implementation details remain unknown.

## `DIRECT-CANDIDATE`

### Choose direct when

- the request has one independently observable outcome;
- the required behavior, exclusions, edit intent, exact authorized paths, and focused proof are
  settled;
- diagnosis and any product, UX, architecture, API, data, migration, compatibility, or external
  contract decisions are already resolved; and
- no durable artifact is needed to preserve decisions or coordinate later work.

One logical change may touch several files. Shared infrastructure or contract work may also be direct
when its behavior and consumers are settled and no durable coordination remains. Escalating during
implementation is safe if a genuine new boundary appears.

Use the smallest proof that catches a plausible regression. Mechanical work needs a diff audit and a
narrow deterministic assertion. Local behavior needs a red/green guard and focused suite. Visible UI
needs focused automated checks plus an independent live script for the relevant states and viewports.

### Return

```text
RESULT: DIRECT-CANDIDATE
TARGET: <surface or behavior>
OUTCOME: <one observable result>
ROUTE BASIS: <why no durable coordination is needed>
STRUCTURAL EVIDENCE: <short path:line facts and equivalent sites checked>
AUTHORIZED PATHS: <exact paths>
CHANGE: <one logical change>
PROOF CONTRACT: <level; regression guard; exact commands; live proof requirement>
CLOSEOUT: MINIMAL | FOCUSED | FULL
ESCALATE IF: <specific boundary that invalidates direct delivery>
ISSUE: none
```

## `PLAN-CANDIDATE`

### Choose a focused Plan when

- the work delivers one coherent, independently acceptable human outcome; and
- durable decisions, ownership, staged delivery, or implementation coordination are useful for that
  outcome.

Do not choose a focused Plan merely because the work spans many files or technical layers. Do not
promote it to a master plan merely because it has several stages: stages can be internal shipments
toward one outcome, while master-plan slices are independently selectable outcomes in their own
right.

The assessment must settle product behavior, observable acceptance, exclusions, ownership, stage
shape, and proof well enough to propose the Plan. It need not perform bounded compiler lookups that do
not affect those decisions. Preserve exact known symbols, state and data flow, precedents, focused test
behavior, consumer defaults, CSS or shell constraints, useful absent-precedent results, exact known
commands, and escalation boundaries. Name genuinely missing implementation facts as compact lookups,
not broad rediscovery. Conditional implementation paths and verification-only files are not
unconditional `Touches`.

Keep one stage when partial delivery would not be a valid human-visible shipment. Put internal
executor sequencing in work orders rather than manufacturing product stages.

### Return

```text
RESULT: PLAN-CANDIDATE
TARGET: <one coherent outcome>
HUMAN OUTCOME: <observable independently acceptable result>
ROUTE BASIS: <durable coordination need; why direct is insufficient and master plan is unnecessary>
PLAN DECISIONS: <settled behavior, contracts, and reversible defaults>
STAGES: <coherent numbered stages labeled ORDERED or QUICK-CANDIDATE>
ACCEPTANCE: <observable script, including relevant empty/error/cancel and accessibility states>
AUTOMATED GATES: <focused commands and live proof>
TOUCHES: <bounded ownership globs>
EXCLUSIONS: <explicit out-of-scope work>
REVIEW FLAGS: <reversible defaults for frontier review, not blocking questions>
COMPILER EVIDENCE: <stage-grouped symbols, flow, precedents, tests, consumers, constraints, commands, and bounded lookups>
ASSESSMENT USE: <reads/searches used; useful absent precedents; budget overruns>
ISSUE: none
```

## `MASTER-PLAN-CANDIDATE`

### Choose a master plan when

- the request describes one broad product destination;
- reaching it contains at least two independently reviewable and independently selectable
  human-visible outcomes or slices; and
- the slices benefit from shared destination-level principles, boundaries, dependencies, or
  sequencing that should survive across later focused Plans.

Crossing product surfaces, capabilities, or owning areas is supporting evidence, not a mandatory
gate. A list of unrelated requests is not one master plan. A large single outcome remains a focused
Plan. Do not require implementation-ready paths, symbols, commands, or stage contracts before making
this recommendation; establish only enough evidence to describe the destination, candidate slices,
shared direction, exclusions, and existing coverage.

Check `docs/master-plans/` before recommending new coverage. If a matching master plan exists, report
its exact path. If the user has selected an existing slice, report its slice ID and recommend normal
`to-plan` routing instead of a duplicate master plan. If the destination exists but needs refinement,
recommend refining that artifact rather than creating another one.

This result is recommendation-only. Stop after returning it. Do not write or refine a master plan,
create a focused Plan, select a slice for the user, compile orders, implement, dispatch, reconcile, or
commit.

### Return

```text
RESULT: MASTER-PLAN-CANDIDATE
TARGET: <broad product destination>
HUMAN DESTINATION: <observable destination-level outcome>
ROUTE BASIS: <why this is multiple slices rather than one focused outcome>
CANDIDATE SLICES: <two or more independently reviewable outcomes>
SHARED DIRECTION: <principles, boundaries, dependencies, or sequencing worth preserving>
EVIDENCE: <short path:line facts across relevant surfaces or capabilities>
EXISTING COVERAGE: <none, matching master-plan path, or exact path and selected slice ID>
EXCLUSIONS: <adjacent work outside the destination>
NEXT ROUTE: <create/refine master plan, or send the selected existing slice through normal to-plan>
ISSUE: none
```

## Non-candidate results

Return one of these only when a candidate route cannot be justified:

- `QUESTION`: one batched question is genuinely required to select the route or core outcome, control
  destructive behavior, or settle an irreversible or external contract.
- `BLOCKED`: cited repository state or missing authorization prevents safe assessment or routing.
- `NO-PROBLEM`: bounded structural evidence disproves the reported gap or finds no requested change.

For these results, return the result label, cited evidence, why no candidate can yet be selected, the
smallest next decision or lookup, and `ISSUE`. Do not turn ordinary implementation uncertainty into a
question or blocker.

## Final checks

Before returning:

- ensure the route rationale distinguishes the chosen candidate from both alternatives;
- include exact paths and evidence where they are known and relevant;
- state scope, exclusions, proof expectations, and issue status;
- preserve useful absent-precedent findings and budget telemetry without narrating discovery; and
- make no edits and invoke no downstream phase.
