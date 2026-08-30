---
name: coordinator-workflow
description: Use for every repository-dependent request; routes decisions, assessment, Plans, execution, Exploration, and optional validation.
---

# Coordinator workflow

The coordinator owns decisions, routing, scope, records, acceptance, and stopping. Keep decision context at the
frontier; delegate repository reads and edits.

## 1. Choose the route

- Answer informational questions directly. Use one bounded `scout` lookup first when the answer depends on
  repository facts.
- Use `grilling` for an explicit interview or material unsettled product, visual, architecture, data, contract,
  or direction decisions.
- Send disposable mock-ups or prototypes to `exploration` with one bounded brief. Their output remains
  noncanonical until explicit adoption.
- For canonical repository work that may change files or create a workflow record, ask once whether Luna or Flash
  should own the case, explain the tradeoff, make one recommendation, and retain the choice. Reserve the
  medium-reasoning Sol case-worker for an explicit user request or particularly hard emergency work; do not offer
  it as a routine option. Launch the selected case-worker with `PHASE: ASSESS`.
- Use `scout` whenever a coordinator decision needs a missing or stale fact. Do not repeat clean case-worker reads.

## 2. Review assessment

Ask the user only when an answer changes the outcome, behavior, contract, dependency, destructive effect, or
acceptance. Handle the case-worker result as follows:

- `DIRECT-CANDIDATE`: resume with `PHASE: EXECUTE DIRECT` and the approved execution packet.
- `PLAN-CANDIDATE`: resume with `PHASE: WRITE PLAN`, the approved Plan path, outcome, scope, stages, proof,
  acceptance, and escalation boundaries.
- `MASTER-PLAN-CANDIDATE`: obtain explicit user approval for the destination and slice envelope, then resume with
  `PHASE: WRITE MASTER PLAN`. Do not implement or choose a slice.
- `QUESTION`, `BLOCKED`, or `NO-PROBLEM`: resolve or report exactly that result; do not force another route.

Before resuming a retained case-worker, call `context_budget`. When assessment returns `PLAN-CANDIDATE`, prefer
resuming that case-worker with `PHASE: WRITE PLAN` while its assessment context is available; this priority applies
through `DECISION-REQUIRED` because writing the Plan externalizes that context. Only start a fresh Plan writer when
the tool reports `ROLLOVER-DEFAULT` or the retained session is unusable. For other results, follow the tool's default
action. At `DECISION-REQUIRED`, resume only if continuity is important and the remaining phase is small; otherwise
start a fresh case-worker with a compact approved packet. When telemetry is unavailable, prefer a fresh case-worker
unless untransferred reasoning makes a short resume safer.

## 3. Execute

Every execute packet must name the outcome, exact paths or bounded Plan area, known facts, ordered actions,
proof commands — each with an explicit finite `bash` tool timeout in milliseconds (missing, zero, or non-finite
timeouts are forbidden because commands can hang) — acceptance, exclusions, support skills if any, and
escalation boundaries. For a Plan, execute one stage at a time with `PHASE: EXECUTE PLAN STAGE`; stages never
run in parallel. The coordinator may split an oversized stage only when the Plan outcome and acceptance remain
unchanged.

Review the returned proof and diff scope. Do not silently expand behavior. User edits at a visual breakpoint are
authoritative: bound them, preserve them, and continue from the resulting state.

Maintain one proof ledger in the active conversation. For every passing command or browser check, retain its
exact command/scenario, working directory, finite timeout, result, covered behavior or check step, and the paths,
configuration, dependencies, and environment it relied on. Passing proof remains valid until a later edit or
environment change could affect what it established. Before requesting any check, compare changes since its pass:
reuse unaffected proof, rerun only invalidated proof, and add only genuinely missing coverage. A broader command
must not be used merely to rerun already-covered tests.

## 4. Accept and record

Accept implementation when finite behavioral tests or browser scenarios establish the Plan or direct-change outcome
and all required human or visual breakpoints pass. Do not use lint, formatting, broad type/build, source-size,
aggregate, or other repository-hygiene checks as implementation proof unless the outcome specifically changes that
tool or constraint. Temporary maintenance violations do not block Plan acceptance; do not append a Quality phase or
complete repository-suite closeout.

When the user separately requests independent validation, launch Quality with `PHASE: VALIDATE`, the observable
outcome, exact approved paths, baseline and diff facts, exclusions, acceptance, the proof ledger, changes since
each proof item, and only the exact missing or invalidated checks. This optional validation is not a Plan stage or
an implementation closeout requirement.

If validation fails, authorize at most one `PHASE: FIX` with the exact failed check, paths, intended semantics,
and deterministic repair. Record the repair as invalidating only proof it could affect. Then run final validation
in a fresh Quality session with unaffected proof retained and only invalidated checks requested. Stop after a
failed repair or a second failed validation.

After behavioral proof and any required human or visual breakpoint pass, update only the active Plan's progress,
decisions, and concise proof. When every stage is accepted, set the Plan to done, remove any transient
`handoff.md`, and move its feature directory from `docs/plans/active/` to `docs/plans/done/`. Complete test/fix
runs belong to a separate maintenance workflow and do not block Plan completion.

Never create legacy lifecycle artifacts, commit, push, rewrite completed records, or disturb unrelated changes.
