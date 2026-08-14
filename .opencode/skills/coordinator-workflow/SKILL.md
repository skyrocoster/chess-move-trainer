---
name: coordinator-workflow
description: Use ONLY as the coordinator's single-entry workflow for coordinator-owned grilling, DeepSeek factual scouting, resumable Luna cases, direct-route approval, and focused Plan review.
---

# Coordinator workflow

Keep frontier context for decisions. Do not spend it on routine repository retrieval.

## Entry and grilling

Answer a purely informational/meta request directly only when no repository investigation is needed. For vague
repository-dependent requests or any user request to discuss, grill, interview, explore, or reach shared
understanding before acting, invoke `grilling` and follow its design-tree protocol before assessment. For a vague
repository-dependent request, invoke the `scout-case` agent with one bounded lookup before asking
the first question; use the user's message and the minimum routing documents to identify the concrete setup and
likely decision boundary without diagnosing or proposing a solution. Then ask exactly one dependency-ready frontier
decision per turn, provide explicit options and one clearly labeled recommendation, and wait for the user's answer
before recomputing the frontier. A recommendation is not the user's answer: never select an option for them. Preserve
confirmed answers, decisions, reasons, uncertainty, and the stopping rationale.

For repository facts needed by the decision tree, invoke a fresh `scout-case` agent with one bounded
factual question, known context, lookup limits, and stop conditions. Treat the running
lookup as an unsettled prerequisite: do not ask its downstream question until the lookup returns. The scout returns facts only; it may not diagnose, advise, infer intent, propose a route or
implementation, ask the user questions, edit, or invoke assessment.

The initial scout is not a one-time gate. Whenever a later frontier question needs repository evidence that is
missing, stale, contradictory, or too broad to support a grounded recommendation, invoke a fresh
`scout-case` agent with another bounded lookup. Scout only the prerequisite fact needed for that next
question, incorporate the result into the decision tree, and repeat as often as required without switching to
assessment or asking the user for retrievable repository facts.

Do not assess, route, write, or implement while the grilling tree has an open frontier or pending fact lookup. When
the frontier is empty, present the shared-understanding summary and obtain the user's explicit confirmation required
by `grilling`. Only that confirmation ends the grilling phase and permits assessment.

When outcome and evidence are sufficient, explicitly hand the clarified request and accumulated facts to
`assess-case`. Assessment may recommend `MASTER-PLAN-CANDIDATE` using its operational gate. This workflow may
authorize the retained case-worker to write that master plan after the user approves the compact destination
envelope; implementation and downstream slice routing remain separate.

Small conversations need no document. At least four confirmed decisions, or an explicit user request, requires
presenting a complete verbose record for confirmation before writing. Obtain or confirm an explicit safe target path
then; never invent a persistent location. Preserve the original request, every question and answer, every confirmed
decision and its reason, repository evidence, unresolved items, and stop rationale. This is neither a Plan nor
implementation authorization.

Qualifying coordinator grilling records are stored under `docs/grilling-docs/` using a conservative descriptive
filename. The fixed directory removes the need to ask for a destination, but does not remove the requirement to
present the complete record for user review and receive explicit confirmation before writing it. These records are
historical design-review evidence only: they do not create or update Plans, master plans, implementation routes, or
product behavior.

For other requests, spawn `coordinator-caseworker` with this handoff:

```text
PHASE: ASSESS
USER REQUEST: <verbatim request>
SIMULATION PATH: <explicit scratch path, or none>
Invoke `assess-case`. Do not edit.
```

Retain the returned task/session ID. All later case-worker work for this case resumes that same ID.

## Review the assessment

The case-worker returns `DIRECT-CANDIDATE`, `PLAN-CANDIDATE`, `MASTER-PLAN-CANDIDATE`, `QUESTION`,
`NO-PROBLEM`, or `BLOCKED`.

- Do not reread repository files to verify clean cited evidence.
- Ask only when the answer changes the route/core outcome, safety/destructive behavior, or an
  irreversible/external contract. Batch all known blocking questions once.
- For reversible Plan details, choose conservative defaults: repository precedent; lossless over lossy;
  accessible/readable over dense; temporary over persisted; smallest coherent scope.
- For `MASTER-PLAN-CANDIDATE`, confirm the compact destination envelope and obtain explicit user approval before
  writing. An already-covered slice is not a new master-plan candidate: report its exact path and slice ID and stop
  for normal `to-plan` routing rather than authoring or executing it here.

## Master-plan candidate

Review the compact envelope for one coherent broad destination, independently valuable slices, settled shared
direction, explicit exclusions, repository evidence, and no unresolved product decision. Master plans record
direction only and authorize no implementation.

After explicit user approval, resume the same task ID:

```text
PHASE: WRITE MASTER PLAN
PROPOSAL APPROVED: yes
TARGET PATH: docs/master-plans/<slug>.md
DESTINATION: <approved broad human outcome>
SLICES: <approved independently reviewable slices>
SHARED DIRECTION: <approved decisions and constraints>
EXCLUSIONS: <approved boundaries>
KNOWN FACTS: <approved cited repository evidence>
Invoke `master-plan`. Do not implement.
```

Read the written master plan exactly once. Make only minor in-scope corrections directly; material faults return to
the same case-worker. Run the documentation checker and present the reviewed path, destination, slices, unresolved
decisions, and first independently valuable slice. Stop without selecting, planning, or implementing a slice.

Before approving a Plan candidate, require explicit observable acceptance and exclusions. Frontier-settled
stages are recorded as `ORDERED` or `QUICK-CANDIDATE`, never `ORDERED-CANDIDATE`. A dirty generated index
pointing to a missing Plan is a repository-state contradiction to report, not automatically a product
blocker; continue from cited source/ownership evidence and let the frontier decide whether writing is safe.

## Direct candidate

Review the compact envelope for one atomic change, settled behavior, exact paths, structural evidence, one
focused proof contract, safe escalation, and no contract/design/data/migration decision. Reject an under-routed
candidate without exploring source yourself.

When approved, resume the same task ID:

```text
PHASE: EXECUTE DIRECT
ROUTE APPROVED: yes
GOAL: <approved outcome>
AUTHORIZED PATHS: <exact paths>
KNOWN FACTS: <approved cited facts>
CHANGE: <one logical change>
IN-SCOPE REPAIRS: <deterministic checker-reported repairs allowed within authorized paths, preserving intent and not expanding behavior, ownership, contracts, or production scope>
PROOF CONTRACT: <level, regression guard, focused commands, live requirement>
CLOSEOUT: <MINIMAL | FOCUSED | FULL>
ESCALATE IF: <exact boundaries>
Invoke `deliver-direct`.
```

Review an `ESCALATED` result against the original paths and intent before starting a new ASSESS round. If the
repair is already authorized and deterministic, resume the same case-worker with clarification and the remaining
verification attempt. Start a narrow ASSESS only when new facts, decisions, or scope are genuinely required.

After `FIXED-PENDING-VALIDATION`, a fresh `coordinator-validator` may receive only the observable proof packet
and diff/baseline facts, never implementation narrative. It runs the inert validator phase machine only when a
future handoff names the exact phase and approvals. Validation cannot repair product implementation. REVALIDATE
and later phases require retained-session handoffs plus explicit coordinator gates; closeout and COMMIT are never
implied by passing validation, and this route does not execute current lifecycle operations.

No direct route auto-commits. Present the implementation proof and an observable human-acceptance checklist.

## Ordered implementation

The frontier may resume the retained case-worker for exactly one explicitly approved canonical work order. This is
distinct from direct delivery and order authoring; it does not dispatch, validate, reconcile, or perform lifecycle
closeout.

```text
PHASE: EXECUTE ORDER
ROUTE APPROVED: yes
ORDER PATH: docs/plans/active/<feature>/orders/<NN>-<slug>.md
ESCALATE IF: <exact boundaries>
Invoke `implement-order`.
```

The case-worker uses the order's packet as its immutable envelope, touches only packet-authorized paths, runs only
exact packet proof commands in order, permits one deterministic in-scope repair, and returns `DONE`, `FAILED`,
`BLOCKED`, or `ESCALATED` with proof, scope, guard, attempt, and deviation telemetry. It must stop without executing
the example browser-validation order unless that exact order is separately approved and handed off.

## Plan candidate

The ASSESS call should already contain a complete Plan proposal and compiler evidence. Review it for:

- one human-visible outcome;
- route size and coherent stages;
- conservative, non-lossy defaults;
- explicit exclusions;
- empty/error/cancel and relevant accessibility states;
- regression and live-proof quality;
- no deferred product, UX, architecture, data, or contract decisions; and
- compiler handoff that preserves paid-for symbols, state flow, tests, consumers, constraints, and absent
  precedents without discovery logs.

Require exact owning symbols/state flow and exact commands already known; unknowns are compact bounded
lookups, not broad rediscovery. Conditional implementation paths and verification-only files are not
unconditional `Touches` or authorization. If partial implementation is not a valid human-visible shipment,
keep one coherent stage and put internal sequencing in work orders.

State all minor corrections in one message. If correction needs new repository evidence or materially changes
the outcome, resume ASSESS narrowly instead of silently redesigning it. Otherwise resume the same task ID:

```text
PHASE: WRITE PLAN
PROPOSAL APPROVED: yes
TARGET PATH: <docs/plans/active/<feature>/<feature>.md or user-authorized scratch path>
FRONTIER CORRECTIONS: <all corrections, or none>
Invoke `write-focused-plan`.
```

Read the written Plan exactly once. Make minor in-scope corrections directly when needed. A material fault goes
back to the same case-worker. Present the reviewed Plan to the user. Order authoring for a named `ORDERED` stage may
use the bounded Luna protocol below; ordered execution remains outside this workflow. One
explicitly selected planned quick stage may use the route below.

## Planned quick stage

This is distinct from a direct free-form fix. The Plan is durable context, and stage review must determine that
the selected stage is now one atomic edit with exact paths, verified facts, no remaining decisions, and one
focused proof contract. Decide this before creating any work order.

When every quick criterion is proven, spawn a fresh `coordinator-quick-executor` with only:

```text
Invoke `implement-quick`.
GOAL: <one outcome>
AUTHORIZED PATHS: <exact paths and bounds>
KNOWN FACTS: <verified answers>
CHANGE: <one atomic logical edit>
PROOF CONTRACT: <red/green guard, exact focused commands, live requirement and script>
ESCALATE IF: <exact boundaries>
```

Do not include the Plan or discovery narrative. On `DONE`, run the same independent validator rule used for a
visible direct change, then report evidence. Plan recording, closeout, reconciliation, and commit remain outside
this workflow. On `ESCALATED`, do not widen the brief; the stage becomes ordered and this flow
stops. Direct free-form fixes never use this fresh executor; they resume their original case-worker task ID.

## Context discipline

Normal Plan handling uses two case-worker calls: `ASSESS + PLAN-DRAFT`, then resumed `WRITE PLAN`. Only a truly
blocking batched question adds a call. Do not request separate route, draft, audit, and write passes.

Before every retained `coordinator-caseworker` resume, invoke `context_budget` with its task/session ID. The
tool measures the latest completed assistant request's active context as input plus cache-read tokens; never replace
that runtime value with an estimate or cumulative billed tokens.

- Below 100k: resume normally.
- From 100k through 119,999: note the warning and prefer a compact handoff when the next phase is separable.
- From 120k through 199,999: record an explicit `RESUME`, `ROLLOVER`, or `STOP` decision before continuing.
- At 200k or above: `ROLLOVER` is the hard default. Resume only when critical authorization or unresolved reasoning
  cannot be transferred safely and the next operation is short; state the exceptional rationale.
- If telemetry is unavailable: do not guess. Prefer `ROLLOVER`; use `STOP` if a safe continuation packet cannot be
  produced.

Record the gate as:

```text
CONTEXT DECISION: RESUME | ROLLOVER | STOP
ACTIVE TOKENS: <runtime value or unavailable>
NEXT PHASE: <phase>
RATIONALE: <why continuity or freshness is safer>
```

Choose `ROLLOVER` when starting a distinct phase, when a Plan/order/approved envelope fully carries the next action,
after compaction, or when substantial reads, edits, or proof output remain. A rollover launches a fresh
`coordinator-caseworker`; never resume the old task ID. Supply only the approved outcome, current route and
phase, decisions and exclusions, exact authorized paths, cited verified facts, remaining action, proof contract,
escalation boundaries, and prior results that affect the next phase. Do not transfer the transcript or discovery
narrative. Choose `STOP` when that packet cannot preserve required authorization or unresolved decisions safely.

## Order-authoring review

For one explicitly named `ORDERED` Plan stage, the frontier chooses a Luna context mode and invokes the shared
`coordinator-order-author` skill:

- **Warm:** resume the retained `coordinator-caseworker` session with `PHASE: AUTHOR ORDERS` so paid-for Plan and
  repository context can be reused.
- **Fresh:** launch a new `coordinator-caseworker` session with only `PHASE: AUTHOR ORDERS` and the complete
  frontier-reviewed compile packet. Do not include the retained transcript or discovery narrative.

The skill and protocol are identical in both modes; the host session alone determines whether context is warm or
fresh. Stronger-model order-author agents, model-specific compiler skills, strong defaults, and warm-Luna-versus-
strong-model comparisons are deferred and are not active routes.

The handoff contains the exact Plan path, named stage, frontier-reviewed compile envelope, canonical nested output
paths, invoke-only order tool, and checker command, then explicitly says `Invoke coordinator-order-author`. In `PROPOSE`, the Luna
case-worker reads the Plan exactly once and returns the skill's fixed compact proposal with `ZERO | ONE | MULTIPLE |
UNDER-CAPTURED`, exact boundaries, dependencies, strength, paths, context sufficiency, acceptance/proof coverage,
lookup classifications, expected tool interaction, telemetry, and issue. `ZERO` is already complete,
invalid/not implementable, or quick. `ONE` is valid when one executor boundary is sufficient, but must explain why
durable Plan state was warranted and quick execution is inappropriate. `MULTIPLE` requires genuine executor
boundaries and settled sequencing; never split artificially. `UNDER-CAPTURED` returns to Plan repair.

The frontier owns envelope/proposal/telemetry review and may issue one correction. Then there is one approved `WRITE`
and one deterministic generator/checker repair. No phase performs production discovery, execution, dispatch,
validation, reconcile, commit, or Plan-status work. Outcomes are `PROPOSAL PASS / MATERIALIZATION DEFERRED` and
`PROPOSAL+WRITE PASS`. `WRITE` supplies one lossless canonical JSON packet per approved order and uses
`new_order.py --packet`; it never uses repeated authoring flags or lets the generator infer the reviewed envelope.
Preserve proposal-to-write continuity and the invoke-only tool rules in the shared skill.
This ordered implementation route is bounded to the retained case-worker and one approved order;
production dispatch and later lifecycle parts remain outside this workflow.
