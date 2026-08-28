---
name: coordinator-workflow
description: Use for every repository-dependent request; routes decisions, assessment, Plans, execution, Exploration, and Quality.
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

Before resuming a retained case-worker, call `context_budget`. Follow its default action. When it reports
`DECISION-REQUIRED`, resume only if continuity is important and the remaining phase is small; otherwise start a
fresh case-worker with a compact approved packet. When telemetry is unavailable, prefer a fresh case-worker unless
untransferred reasoning makes a short resume safer.

## 3. Execute

Every execute packet must name the outcome, exact paths or bounded Plan area, known facts, ordered actions,
proof commands — each with an explicit finite `bash` tool timeout in milliseconds (missing, zero, or non-finite
timeouts are forbidden because commands can hang) — acceptance, exclusions, support skills if any, and
escalation boundaries. For a Plan, execute one stage at a time with `PHASE: EXECUTE PLAN STAGE`; stages never
run in parallel. The coordinator may split an oversized stage only when the Plan outcome and acceptance remain
unchanged.

Review the returned proof and diff scope. Do not silently expand behavior. User edits at a visual breakpoint are
authoritative: bound them, preserve them, and continue from the resulting state.

## 4. Validate and record

Use a fresh `quality` validation for observable product behavior, UI/browser work, data or schema changes,
cross-layer/shared contracts, destructive effects, or whenever the Plan or proof requires independence. Focused
case-worker proof may close low-risk documentation or workflow-only changes.

Launch Quality with `PHASE: VALIDATE`, the observable outcome, exact approved paths, baseline and diff facts,
exclusions, acceptance, and exact checks. Include a bounded browser scenario only when live evidence is required.

If validation fails, authorize at most one `PHASE: FIX` with the exact failed check, paths, intended semantics,
and deterministic repair. Then run final validation in a fresh Quality session. Stop after a failed repair or a
second failed validation.

After proof and any required human or visual breakpoint pass, update only the active Plan's progress, decisions,
and concise proof. When every stage is accepted, set the Plan to done, remove any transient `handoff.md`, and move
its feature directory from `docs/plans/active/` to `docs/plans/done/`.

Never create legacy lifecycle artifacts, commit, push, rewrite completed records, or disturb unrelated changes.
