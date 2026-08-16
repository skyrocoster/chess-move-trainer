# Plan & Work-Order Template

Repository-dependent work is coordinated through `coordinator`, which owns assessment, route review,
focused Plan writing, bounded order authoring, and approved execution. Retained support agents and skills
provide bounded case-worker, validation, browser, and proof capabilities.

The workflow is driven by retained coordinator skills in `.opencode/skills/`, opencode's native skill directory:

| Skill | Role | Job |
|---|---|---|
| `coordinator-workflow` | coordinator | Assess a repository-dependent request, review its route, and hand off bounded work. |
| `coordinator-order-author` | order author | Compile one approved stage into a canonical work order. |
| `implement-order` | executor | Execute one explicitly approved work order, then stop. |
| `implement-quick` | quick executor | Execute one fully settled atomic change from an approved brief. |
| `deliver-direct` | case-worker | Deliver one approved direct change, verify it, and stop without committing. |
| `coordinator-validator` | validator | Response-only validation for direct and planned-quick proof packets. |
| `validate-order` | validator | Independently validate one canonical order and record its completion evidence. |
| `validate-stage` | validator | Independently validate an accepted Plan stage and record its shipment. |
| `validate-plan` | validator | Verify all stages shipped and perform bounded Plan closeout. |
| `master-plan` | planner | Define a broad destination and independently selectable slices. |
| `write-focused-plan` | planner | Write an approved focused Plan from retained assessment evidence. |

`coordinator` is the sole official primary coordinator. It owns route decisions, scope, proof
sufficiency, and user communication; the case-worker executes only explicitly approved bounded work and
never commits, dispatches, reconciles, or pushes.

The split is also a context-preservation rule: when `to-orders` emits exactly one order, the creating
planner implements that order in the current context, runs its exact proof entries, and preserves its
STATUS/EXECUTOR RESULT. Only stages emitting two or more orders use `dispatch-orders`
and fresh executor contexts.

### Stage execution routing

After settling a Plan stage, choose the smallest safe route:

- **Planned quick stage:** use `quick-executor` when the stage is one atomic change, the exact edit and
  authorized paths are known, no design/architecture/contract/diagnosis work remains, and one focused
  check can judge it. The coordinator writes the ephemeral `implement-quick` brief, dispatches it, and
  records the successful result in the Plan's Status and Shipped table. The executor never edits the
  Plan. The coordinator names this Plan explicitly when invoking `reconcile`, because no work-order
  file exists for the active-index `Next` column to discover. A failed or escalated brief becomes a
  normal `to-orders` stage; do not expand the brief.
- **Work-ordered stage:** use `to-orders` when the executor needs bounded exploration, the stage has
  dependencies, more than one logical change, or normal order evidence and sequencing.
- In a multi-order stage, after each ordered executor returns `DONE`, the coordinator selects `validate-order` and
  sends the exact order packet through the documentation-only validator. On success, it records canonical order
  `DONE` plus executor and independent validator evidence; failure records nothing.
- In a single-order stage, the coordinator does not run `validate-order`. It asks for explicit human acceptance after
  executor `DONE`, then selects `validate-stage` once. That operation independently validates the order and atomically
  records both canonical order `DONE` evidence and the Plan stage's `Status` and `Shipped` row.
- When the final order of a multi-order stage is validated, the coordinator asks for explicit human acceptance of that
  exact stage. After acceptance, `validate-stage` verifies every completed order and updates the Plan's stage
  `Status` and `Shipped` row. Ambiguous or incomplete evidence is rejected without writing.
- After a shipped stage appears to be the final stage, the coordinator selects `validate-plan`. No additional whole-Plan
  human acceptance is required. The skill verifies every stage is shipped, moves the Plan from `plans/active/` to
  `plans/done/`, deletes completed order files, and removes resulting empty folders. Index, manifest, dependency,
  narrative-reference, and broader closeout behavior remain outside this lifecycle.
- **Human stage:** stop and surface the decision when the stage needs a table session, unresolved
  product/design judgment, or High-strength synthesis.

The quick route is a transport optimization, not a second Plan format. The Plan remains the durable
record even though no work-order file is created.

### Master-plan slice routing

Before a focused Plan exists, `to-plan` judges transport without asking the user. It delivers a selected
slice directly only when behavior and ownership are settled, prerequisites have durable acceptance
evidence, implementation is one atomic change, exact authorized paths/facts/check are verified, no
design/architecture/API/data/migration/compatibility/diagnosis decision remains, and no queued or
multi-context coordination state is needed. File count and the presence of a human acceptance gate do
not decide this.

A qualifying slice goes directly through an `implement-quick` brief and mandatory `quick-reconcile`.
Anything unproven gets a focused Plan. An escalated direct brief also becomes a focused Plan carrying
the failed brief's evidence; it is never widened in place.

Every master-plan-backed route writes the master plan's `## Slice delivery receipts` table during
closeout. `quick-reconcile` records route `Direct`; full `reconcile` records route `Plan`. Checks may
write `Implemented; awaiting human acceptance`; only explicit human acceptance writes
`Accepted YYYY-MM-DD`. Only that accepted receipt, or equivalent accepted archived-Plan evidence,
satisfies a dependent slice.

---

## Layer 1 — the Plan (human-readable)

Lives at `docs/plans/active/<feature>/<feature>.md`, named for a concrete outcome. Many Plans may be
active at once; what a Plan waits on is a **dependency**, declared in its `## Touches` section — see
*Lifecycle* below. Short, and free of code — you read it to understand *what* and *why*.

```md
# <Feature> — <one-line outcome>

> **Status:** <what's done, what's next — one line, rewritten each stage>

- **Read trigger:** <when a reader should open this plan>

## What we're building & why
<1–2 short paragraphs.>

## Stages
1. <plain-English intent of stage 1>
2. <plain-English intent of stage 2>
3. <plain-English intent of stage 3>

## Shipped
| Stage | What shipped (≤2 sentences) |
|-------|------------------------------|

## Touches
- `glob/pattern/**`
- **Depends on:** [Other Plan](#)

## Compiler handoff

### Stage <N>
- **Verified edit sites:** `<repo-relative path>` — `<symbol or bounded section>`; <what is already true there>
- **Verified tests:** `<repo-relative path>` — <relevant suite, fixture, or harness fact>
- **Settled contracts:** <exact behavior, ownership boundary, data shape, copy, token, or dependency decision>
- **Constraints:** <invariant or canonical reference the orders must preserve>
- **Open questions:** <what `to-orders` still must resolve, or `none`>
```

**`**Read trigger:**` is required.**
`## Compiler handoff` is a temporary, stage-scoped machine-facing appendix. It preserves verified
answers planning already paid to discover so `to-orders` can target its exploration instead of
rereading the same source. Exact paths, symbols, tests, contracts, and constraints belong here;
unverified assumptions belong under Open questions. `to-orders` consumes the compiled stage's
subsection after its orders pass lint and removes the heading when no handoffs remain. A Plan may
temporarily carry a **`## Planning byproducts`** appendix of verbatim code snippets that fell out of
settling the design (verified regexes, exact expressions, type signatures); `to-orders` moves each
into the relevant order's known facts (marked `verified snippet — use as-is:`) and deletes the
appendix.

Every active Plan **must** declare a `## Touches` section. Each line is a repo-root-relative
backtick-quoted glob matching files the Plan's work orders may modify. When a Plan's `orders/` directory
contains at least one canonical `NN-*.md` work order it is *in-flight*; only in-flight Plans participate in overlap
checks. If two in-flight Plans expand to the same file, the overlap is an error unless one Plan
directly depends on the other via `- **Depends on:** [Label](#)` pointing to the depending Plan's
Markdown file under `docs/plans/active/`.

## Layer 2 — the Work Order (one executor boundary)

Lives only at `docs/plans/active/<feature>/orders/<NN>-<slug>.md`. A Plan stage is a coherent
human-visible shipment; work orders are internal executor boundaries. A one-order Plan is valid when
one executor can safely own the reviewed outcome. No arbitrary path, context, action, or proof caps apply.

**Emit orders with `scripts/new_order.py` from one reviewed JSON compile packet.** Start by copying
[`templates/order-packet.template.json`](templates/order-packet.template.json) to an approved temporary
`docs/plans/active/<feature>/orders/<NN>-<slug>.packet.json` file. Replace every placeholder while preserving all
required keys; do not regenerate the packet from blank output or stdin. `output_path` is mandatory and authoritative.
Run `--packet <temporary-packet-path>`, check the generated order, then delete the temporary packet.
The generator renders only: it does not infer paths, derive anchors, compress actions, synthesize lifecycle
checks, choose wrappers, or rewrite proof commands.

The packet separates identity/dependencies/strength, authorized creates/edits/removes, bounded context,
known facts, ordered structured actions, exact proof entries (`cwd`, `command`, purpose), coordinator and
optional validator acceptance, exclusions, and escalation boundaries. File actions name exact authorized
paths. Explicit non-file actions carry a machine-readable operation and `paths: []`. Context is independent
from authorization and uses `whole_file`, one exact `anchor`, or an anchored line range. New files need no
fabricated context entry. Dependencies are canonical order paths. Root dot-directory paths round-trip.

Generated Markdown is human-readable and embeds the immutable canonical JSON packet. It ends with:

```text
STATUS: PENDING

EXECUTOR RESULT:
- DEVIATIONS: none
- PROOF RESULTS: pending
- DIRTY PATHS: pending
- AUTHORIZATION AUDIT: pending
- ATTEMPTS: 0
- ESCALATION: none
```

The executor fills only these values. Exact proof commands run in packet order from their declared working
directories; `order_check.py` is used only when the packet names it. `scripts/check_orders.py` strictly
validates canonical location, packet/artifact agreement, authorization, actions, context, proof, acceptance,
exclusions, escalation, dependencies, and executor evidence. It does not redesign or resize the order.

Three scripts keep workflow mechanics out of model context: `new_order.py` renders the reviewed packet;
`check_orders.py` validates it; `stage_check.py` performs reconcile checks. `order_check.py` remains an
optional compact proof wrapper. One rule is enforced by the harness rather than by wording:

### On failure — the escalation channel back to the planner

If the executor cannot make an exact proof pass — the harness allows two failed verification runs total,
the initial failure plus at most one repair after it — it writes
`STATUS: FAILED - <reason>`; if the order cannot be executed as written (known fact wrong, named file
missing, or an action contradicts the code) it writes `STATUS: BLOCKED - <reason>`. Either way it fills
the canonical EXECUTOR RESULT with the failed command/output under PROOF RESULTS, dirty paths,
authorization audit, attempts, deviations, and escalation, then leaves partial changes
in the worktree. That evidence is a successful failure outcome; the executor never keeps cycling to
avoid reporting it.

### Failure triage at dispatch

Triage happens **the moment the failure returns**, in `dispatch-orders` — not at reconcile time —
because downstream orders `DEPENDS ON` the failed one and stall until it's reissued and passes. A
`DONE` order needs nothing further; only failures pull the planner back in. Two rules keep failure
knowledge flowing forward so work is never repeated:

- **The planner always tells the executor what already fails.** Whoever compiles an order runs the
  relevant test command first and records any pre-existing failures verbatim in known facts. The
  executor treats those as background noise and exact proof is judged with them still
  present.
- **A reissued order carries what was already tried.** Whoever reissues a FAILED order folds the
  previous failure evidence into the new order's known facts as "already
  attempted, did not work: <approach>".

### Test-run tiers

Each tier runs in the context that can afford its output:

| Tier | Who | What |
|---|---|---|
| Targeted | executor (`implement-order`) | Only the packet's exact proof commands, in order and from their declared working directories. |
| Full | `reconcile`, once per stage | The adopting repository's documented full test, lint, build, and documentation checks. |
| Backstop | CI on push/PR | Everything, always. |

---

## Lifecycle

1. **Active** — the Plan carries a Status line and a plain-English Stages list, and lives under
   `plans/active/`. There may be many at once: a design can be fully settled and written up long
   before there is capacity to build it, and writing it down is how the reasoning survives.

    **Dependencies decide what can start.** A Plan that cannot begin until another ships
   says so with a `**Depends on:**` entry in its `## Touches` section. A Plan is **blocked** while any
   Plan it depends on is still under `plans/active/`, and **ready** once they have all been archived —
     Plan dependencies and folder-local metadata determine readiness. Several Plans can be ready at once
    and nothing ranks them: which ready Plan to pick up is the user's call, made per session rather than
    recorded in a file.
2. **Shipped** — after the required multi-order validations, or directly after execution for a single-order stage, the
     coordinator obtains explicit human stage acceptance. `validate-stage` independently confirms the exact
     Plan/stage/order evidence and atomically records the Plan's **Shipped** row (one ≤2-sentence row per stage); for a
     single-order stage it also records the order `DONE`. A shipped stage does not authorize the next stage. The commit
     history is the record of *how* each thing was built — never duplicate that prose into the Plan.
3. **Complete** — after the coordinator determines that the shipped stage appears final, `validate-plan` independently
     verifies every stage is shipped, moves the Plan to `docs/plans/done/<feature>/`, deletes completed order files, and
     removes resulting empty folders. No additional whole-Plan human gate is required. Index, manifest, dependency,
     narrative-reference, and broader closeout behavior remain outside this validator lifecycle.

## Required model strength (per work order)

State a capability, not a model name. **Light**: bounded/mechanical (rename, stub, narrow test).
**Standard**: ordinary implementation across a small touch set. **High**: broad synthesis, contract
decisions, tricky migration. `to-orders` picks the lowest strength that can safely execute the order
after reading only what it names.

---

## The documentation checker

`scripts/check_docs.py` is aligned with this workflow. For an active Plan it requires only a
`> **Status:**` line, a `**Read trigger:**` header (see Layer 1), and a
`## Touches` section (stages are plain-English list items, not `(next up)` execution blocks). It lints
work orders under `plans/active/<feature>/` by delegating to `scripts/check_orders.py`; enforces the
`## Touches` overlap contract between in-flight Plans; and keeps the workflow-agnostic safety net:
local links/anchors, plan metadata and discovery, plan-redirect lifecycle,
AI-entry precedence, configured test commands, banned legacy references, and the auto-generated
reference inventories. It no longer couples a per-diff code change to a Plan edit, so the executor's
work-order commits pass without touching the Plan; the Plan is updated in batches by `reconcile`.

An earlier plan format (a `(next up)` heading with eight labeled fields) is no longer enforced. The
last plan still written that way may remain until it is naturally retired; it validates fine because
only the Status line is required.
