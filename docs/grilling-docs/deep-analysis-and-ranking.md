# Deep Stockfish Analysis and Ranking — Historical Grilling Synthesis

**Status:** Settled technical and product-direction synthesis

**Implementation authority:** None

**Relationship:** This is durable historical evidence from the deep Stockfish analysis discussion. It is not a
Plan, master plan, implementation authorization, schema approval, or approval for destructive database work.

## Settled direction

The preferred destination is one unified, durable local Stockfish job and worker system. It should support corpus
analysis, a targeted position, a selected game occurrence, candidate comparison, and root-restricted deep searches
without creating separate analysis subsystems for each use case.

The existing analysis database, schema, and behavior are not fixed constraints. The analysis and evaluation subsystem
may be replaced, and old analysis data does not need to be migrated. Unrelated corpus, game, and trainer data must be
preserved. A backup before a destructive reset is prudent, but reset timing and procedure remain to be decided.

The conceptual model is:

```text
jobs -> targets -> search specifications -> attempts -> immutable versioned results
                                                       -> root candidates -> ordered PV moves
```

An exact six-field FEN is the authoritative engine position. A game occurrence supplies provenance and selection
identity; it is not a substitute for the exact engine position. Four-field position grouping may remain a secondary
convenience, but it must not replace exact FEN identity for analysis evidence.

## Definitions and invariants

### Immutable evidence and compatibility

Search results are immutable and fingerprinted. The fingerprint covers the exact position, root scope, MultiPV,
completed work budget, engine identity and checksum, network and engine options, and relevant execution settings.
Changing a setting produces a new result rather than silently revising an old one. Identical compatible completed work
may be reused.

Recorded execution metadata includes, at minimum, time, reported depth, selective depth, actual nodes,
threads/hash, completion state, and engine metadata. These fields describe what happened; they do not by themselves
define whether one result is a valid deeper checkpoint.

### Search families and depth

Search families distinguish unrestricted best-line searches, candidate-comparison searches, chosen-root analyses, and
later robustness exploration. MultiPV 1, MultiPV N, and root-restricted searches are not interchangeable depth
checkpoints.

“Deeper” means deeper only within the same compatible search family and with a larger completed work budget. Nodes are
the preferred primary measure of work. Reported depth is useful metadata but is not a sufficient ordering rule, and
“deeper” is neither “latest” nor simply “higher reported depth.”

### Stability

Stability is explicit evidence collected across increasing finite checkpoints. It can describe best-root persistence,
evaluation/WDL movement, rank movement, candidate-gap movement, and lower-weight PV churn. Stability is evidence of
search convergence, not certainty about the position or a guarantee of practical success.

### Separate selection concepts

The following terms are intentionally distinct:

- **Latest:** most recently completed according to a defined ordering.
- **Largest compatible budget:** the completed compatible result with the greatest comparable work budget.
- **Preferred:** the result selected by an explicit evidence-selection policy.
- **Stable:** a result or series of checkpoints meeting an explicit stability policy.
- **Pinned:** a result deliberately retained as the chosen reference, regardless of later available work.

The default resolver should choose the largest successfully completed compatible result under an explicit
evidence-selection policy, not blindly choose the latest result.

## Recommended semantics

### Top-X candidate selection

Top-X results need ordered eligibility and fallback rules. A result is eligible only when it is complete and
compatible, has suitable root scope, and contains enough candidates. Moves from incompatible searches must not be
silently mixed into one ranking. Prefer one coherent eligible result; if none is adequate, queue a stronger
compare-N-moves search rather than presenting a synthetic ranking assembled from unrelated evidence.

### Ranking and recommendations

Immutable raw Stockfish evidence should be separate from versioned evidence-selection policies, move-ranking policies,
and user-facing recommendations. This keeps the engine record reproducible while allowing policy changes to be
audited and re-evaluated without rewriting evidence.

A ranking policy may define “strongest” in different ways, including:

- objective engine score or WDL;
- stable-objective standing;
- safe or lower-tail standing;
- practical or robustness standing; or
- a later personalized standing.

When a practical policy recommends a move other than the objective engine leader, the objective engine standing should
always be shown separately. A user-facing recommendation must not imply that a derived practical heuristic is a direct
Stockfish probability.

Stockfish does not directly output “more ways to go right.” Practical robustness is a separately versioned derived
heuristic. Possible future ingredients include objective loss, plausible opponent replies, worst or lower-tail
outcomes, breadth of acceptable continuations, only-move frequency, score gaps, recovery potential, search stability,
and corpus-derived reply frequencies. Engine MultiPV and WDL are not human move probabilities.

### Storage shape

Do not store a reply DAG or tree initially. Store independent versioned searches and PV rows. Reply trees can be
materialized later from exact result IDs and algorithm versions, preserving the provenance of each derived structure.

## Why these distinctions matter

Treating the latest result as the best result can select a recently finished, shallow, incomplete, or otherwise
incompatible search. Treating reported depth as a universal scale can compare different root scopes, MultiPV modes,
budgets, or engine settings as though they were the same experiment. Defining deeper within a compatible search family
and primarily by completed nodes makes the comparison about comparable completed work and preserves important
execution metadata for interpretation.

Likewise, evidence selection and move ranking answer different questions. Evidence selection asks which completed
engine result is valid and appropriate to use. Ranking asks how that result should order candidates. A recommendation
may apply a practical policy on top of objective evidence. Keeping these layers separate prevents a policy preference
from being mistaken for engine output, prevents incompatible searches from being blended, and allows policies to
change without corrupting immutable historical results.

Stability is separate for the same reason: persistence across checkpoints can increase confidence that a search is
converging, but it is not a new engine score, a certainty claim, or permission to ignore incompatible evidence.

## Recommended sequencing

The direction is to approach the destination in this order:

1. Define unified contracts and the schema.
2. Build durable workers, cancellation and restart behavior, and resource governance.
3. Add corpus and targeted-position selection.
4. Add move comparison and chosen-root deep analysis.
5. Add APIs and UI.
6. Consider reply-tree materialization and robustness metrics later.

This ordering establishes one evidence model and durable execution foundation before user-facing ranking features.

## Unresolved decisions

The discussion did not settle implementation or product values for the following items. They must not be inferred from
this record:

- node-budget presets and the definition of a completed checkpoint;
- a maximum MultiPV ceiling;
- worker fairness and job-priority rules;
- result and attempt retention policy;
- ranking weights and thresholds for each ranking policy;
- stability tolerances, checkpoint counts, and convergence rules; and
- reset timing, backup handling, and the exact destructive replacement procedure.

Other contracts, resource limits, cancellation semantics, UI presentation, and policy-version details require explicit
assessment and approval at the relevant implementation boundary. This record does not choose them.

## Risks and tradeoffs

- Replacing analysis storage avoids a forced migration and permits a cleaner unified model, but it risks losing old
  analysis evidence; unrelated data preservation and a prudent backup are therefore explicit safeguards.
- Node-based work comparison is more meaningful than reported depth across compatible searches, but it still requires
  careful compatibility rules and complete execution metadata.
- More MultiPV candidates improve comparison coverage while increasing resource use and potentially changing search
  behavior; a ceiling and budgets remain open decisions.
- Practical robustness can better reflect a user's objective than raw engine score, but it is a derived heuristic that
  can encode arbitrary assumptions and must remain versioned and visibly distinct from objective standing.
- Independent PV rows keep initial storage and provenance tractable, but later tree materialization will require exact
  result identifiers and algorithm-version tracking.
- Durable local workers improve resumability and reuse, while cancellation, restart, fairness, and resource governance
  add operational complexity.

## Exclusions and historical boundary

This synthesis does not implement a worker, API, UI, schema, database reset, migration, reply tree, robustness metric,
ranking policy, or recommendation. It does not authorize tests, dependency changes, Plan work, a master plan, or
destructive database action. It does not set node presets, MultiPV limits, fairness or priority, retention, ranking
weights, stability tolerances, or reset timing.

The destination is master-plan-sized: it describes a broad future direction with selectable slices. Any future
implementation requires explicit approval of the destination and slice envelope before assessment, planning, or
execution. This document remains historical directional evidence only.
