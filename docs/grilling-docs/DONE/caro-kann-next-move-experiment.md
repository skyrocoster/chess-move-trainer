# Caro-Kann Next-Move Experiment — Canonical Historical Grilling Synthesis

**Canonical consolidation:** 2026-08-24
**Lead thread recorded:** 2026-08-23
**Status:** Historical and directional evidence from noncanonical read-only experiments and earlier grilling; no implementation authority
**Implementation authority:** None
**Relationship:** This is the canonical record for the Caro-Kann next-move experiment and the four earlier opening-analysis threads that feed it. It is a free-form historical synthesis, not a Plan, product specification, schema, or authorization to implement.

## Reading rules and current status

This document consolidates five former temporary records. The Caro-Kann continuation experiment is deliberately first and remains the lead thread. The historical chain that follows preserves the earlier discovery, classification, database-foundation, and training/repertoire evidence without turning any deferred idea into a new approval.

The current status is not the status of the older design direction alone:

| Record or slice | Current status | Authority and caveat |
| --- | --- | --- |
| MP-06 validated FEN corpus | Accepted and shipped | [Archived MP-06 Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md) |
| S1 source catalog | Accepted and archived | [Archived S1 Plan](../plans/done/s1-source-catalog/s1-source-catalog.md) |
| S2 opening relationships | Accepted and archived | [Archived S2 Plan](../plans/done/s2-opening-relationships/s2-opening-relationships.md) |
| S3 neutral classification | Accepted and archived | [Archived S3 Plan](../plans/done/s3-neutral-classification/s3-neutral-classification.md) |
| S4 authoritative recurrence | Accepted and archived | [Archived S4 Plan](../plans/done/s4-authoritative-recurrence/s4-authoritative-recurrence.md) |
| S5 tracked-player projection | Abandoned and not accepted | [Archived S5 Plan](../plans/done/s5-tracked-player-projection/s5-tracked-player-projection.md) and [S5 retrospective](ABANDONED/s5-tracked-player-projection-retrospective.md) |

The earlier five-slice database direction remains useful historical evidence, but its S5 row must not be read as delivered. S1 through S4 are accepted runtime foundations; the S5 copied/materialized personal projection approach failed during runtime publication, was restored, and was abandoned. Existing S5 implementation and tests remain historical development evidence; this consolidation does not remove them.

Former source-document names are now headings and anchors in this file. Links below point only to current Plans, the current S5 retrospective, the documentation router, or anchors in this canonical file. The deleted former flat grilling paths and the deleted historical master-plan path are not recreated, and completed historical records are not rewritten to repair their old links.

This record does not authorize:

- a database write, migration, backup replacement, or source-data change;
- a preferred move, accepted move, threshold, formula, score, ranking, or adaptive-frontier decision;
- an engine release, budget, population source, dependency, credential flow, or analysis policy;
- a training interface, report interface, notification, route behavior, or other product behavior;
- a claim that the player has trained, remembered, improved, or transferred knowledge; or
- edits to completed Plans, `Scratch/`, the untracked runtime database, product source, commits, or pushes.

## Lead thread: Caro-Kann next-move experiment

### Purpose and deliberately simple foundation

The experiment tests one deliberately basic idea: start from one fixed line from the initial position and prescribe
one exact move for each position in that line. It intentionally avoids graphs, mastery, adaptive behavior,
repertoire complexity, and other broader architecture for now. The aim is to learn what the smallest useful
continuation method reveals before deciding whether a more elaborate model is warranted.

The tracked player is `Skyrocoster`. The experiment analyzes only tracked-corpus games in which Skyrocoster played
Black. This is a read-only historical observation of that corpus, not a claim that the resulting line is a correct or
complete repertoire.

### Selected branch and greedy method

The explicitly selected starting branch is:

> `1. e4 c6 2. d4 d5`

This is used as the Caro-Kann Advance main-line starting point for the experiment. The selection is deliberate rather
than a claim that it was the most common immediate White choice in the filtered corpus. After filtering to
Skyrocoster's opponents in games where Skyrocoster played Black, the immediate plurality after `1...c6` was `Nf3`
with 1,200 games, versus `d4` with 1,146. The experiment nevertheless starts from the chosen `d4` branch.

From that fixed prefix, the method is greedy and local:

1. Match games with the exact full move prefix.
2. At a White turn, choose the most common White opponent move among those exact-prefix games.
3. At the resulting Black turn, inspect Skyrocoster's Black replies.
4. Continue only when the leading Black reply accounts for at least 90% of the available immediate Black replies.
5. Apply no move-number cap. Stop at the first Black divergence below 90% or when the data is exhausted.

The method does not turn a distribution into a prescription merely because one move leads it. The threshold only
determines whether this deliberately simple continuation can proceed to the next position.

### Observed continuation and stopping point

The greedy continuation produced these high-consensus steps:

| Position and selected move | Leading Black reply | Evidence | Decision |
| --- | --- | --- | --- |
| `3.e5` | `c5` | 597/599 = 99.67% | Continue |
| `4.c3` | `Nc6` | 213/218 = 97.71% | Continue |

The next White move was `5.Nf3`. At the exact position after that move, Skyrocoster's Black replies were:

| Black reply | Games |
| --- | ---: |
| `cxd4` | 82 |
| `Bg4` | 45 |
| `Qa5` | 2 |
| `e6` | 1 |

The leading reply was `cxd4` at 82/130 = 63.08%. Because that is below the 90% continuation threshold, the
experiment stops at the position before prescribing Black's move. The accepted stopping line is:

> `1. e4 c6 2. d4 d5 3.e5 c5 4.c3 Nc6 5.Nf3`

This stopping behavior is intentional. The experiment records a divergence frontier rather than silently selecting
the leading reply.

### Evidence at the stopping position

The experiment compares three different kinds of evidence. They answer different questions and must not be treated as
interchangeable.

#### Engine comparison

At the exact Black-to-move position after `5.Nf3`, Stockfish 18 was run with:

- 200,000 nodes;
- MultiPV 5;
- `Threads 1`;
- `Hash 128 MiB`;
- WDL enabled; and
- evaluations reported from Black's perspective.

The top five results were:

| Rank | Move | Evaluation |
| ---: | --- | ---: |
| 1 | `cxd4` | +0.02 |
| 2 | `a6` | -0.54 |
| 3 | `Bg4` | -0.54 |
| 4 | `e6` | -0.63 |
| 5 | `Qc7` | -0.96 |

#### Skyrocoster's whole-game outcomes

These are whole-game results from Skyrocoster's perspective for games in which each reply was played at the
stopping position. They are not proof that the reply caused the later result.

| Reply | Sample | W-D-L | Raw win | Chess score | Sample note |
| --- | ---: | --- | ---: | ---: | --- |
| `cxd4` | n=82 | 50-2-30 | 60.98% | 62.20% | Well-sampled |
| `Bg4` | n=45 | 24-2-19 | 53.33% | 55.56% | Well-sampled |
| `Qa5` | n=2 | 2-0-0 | 100% | 100% | Tiny sample |
| `e6` | n=1 | 0-1-0 | 0% | 50% | Tiny sample |

Engine strength, historical move frequency, and later whole-game outcome are separate evidence channels. Tiny
samples do not establish move quality. `cxd4` is notable because it is engine #1 and the strongest well-sampled
personal outcome, but this experiment deliberately leaves it unprescribed. This record does not decide that
`cxd4`, or any other move, is the move to learn.

### Original continuation frontier

The next discussion should make one decision at a time, starting from the divergent Black position after `5.Nf3`. It
must decide:

1. how a divergent Black position becomes one prescribed move; and
2. how frequency, engine ranking, historical whole-game outcomes, and sample size should be weighed against one
   another.

Only after that decision is explicit should the same simple method continue to the next position. The experiment
should not yet revive graph, mastery, adaptive, or broader repertoire architecture. Those decisions remain deferred
until this small frontier is understood and deliberately adopted, if at all.

### Original experiment location and boundaries

The simple fixed-line experiment lives at:

`experiments/prototypes/caro-kann-next-move/`

Run it from the repository root with:

```text
".venv/Scripts/python.exe" experiments/prototypes/caro-kann-next-move/prototype.py
```

That experiment is noncanonical and read-only. It reads the tracked game data and the Stockfish executable; fresh
engine analysis is not written to the database. It does not change the application, publish a repertoire, or
authorize a database/schema/API/UI/dependency change.

### Later investigation direction and engine-coverage context

Later work sharpened a separate investigation question: look for an exact opening line, in any opening, where
Skyrocoster regularly plays a move that has both poor personal whole-game outcomes and a material immediate worsening
according to Stockfish. Frequency, historical result, and engine quality remain distinct evidence channels. They must
not be combined into an invented score. The numeric meanings of `regularly`, `significantly negative`, and `material
worsening` remain unsettled and are not defined by this record.

The database currently has 3,158 persisted Stockfish 18 analysis roots, which is small relative to the game corpus.
The focused experiment analyses are fresh and intentionally not persisted, so they do not increase that count. This
limitation remains context for later focused engine work, not a reason to infer engine coverage that is not present.

### Later candidate experiment, separate from the Advance position

The following was tested as a later candidate, not as a replacement for the earlier Advance stopping position after
`5.Nf3`:

> `1. e4 c6 2. Nc3 d5 3. exd5 cxd5 4. d4 Nc6 5. Nf3`

Skyrocoster is Black in this line. Among 6,180 qualifying Black games, there were 29 unique exact-prefix games and 29
immediate replies, with no duplicate occurrences. Skyrocoster played only `Bg4`:

| Reply | Sample | W-D-L | Raw win | Chess score |
| --- | ---: | --- | ---: | ---: |
| `Bg4` | n=29 | 15-0-14 | 51.72% | 51.72% |

Fresh Stockfish analysis used Stockfish 18, 200,000 nodes, MultiPV 5, `Threads 1`, `Hash 128 MiB`, WDL enabled,
and the Black perspective. The top five were:

| Rank | Move | Evaluation |
| ---: | --- | ---: |
| 1 | `Bg4` | +0.19 |
| 2 | `a6` | -0.05 |
| 3 | `Nf6` | -0.16 |
| 4 | `Bf5` | -0.18 |
| 5 | `e6` | -0.26 |

Under the chosen two-evidence concept, this line is ruled out as a plainly wrong regular move: `Bg4` is both the
only historical reply and Stockfish's first choice, while the whole-game score is slightly positive. The outcomes are
descriptive and noncausal; they do not show that `Bg4` caused later results.

This later experiment is located at:

`experiments/prototypes/skyrocoster-black-replies-stockfish/`

Run it from the repository root with:

```text
".venv/Scripts/python.exe" experiments/prototypes/skyrocoster-black-replies-stockfish/compare.py
```

The `2.Nc3` candidate remains separately tested and ruled out for that narrow two-evidence question. It must not be
merged with the original Advance divergence or with the later tree and metrics work.

### Later historical-tree track

The following is a later, continuation-oriented corpus-wide historical-tree investigation. It keeps the original
Advance divergence after `5.Nf3` unresolved and does not replace or reclassify the separately tested `2.Nc3` candidate.
It is history only: no engine is used in this track, and the outputs are descriptive rather than canonical.

#### Historical-tree intent and settled rules

The settled root cohort is tracked-corpus games where `Skyrocoster` played Black and the exact start was `1.e4 c6`.
Exact move orders stay separate despite transpositions. The tree branches both White and Black for now.

| Object | Retained information |
| --- | --- |
| Node | Full line, FEN, side, games, W-D-L/unknown, raw win, chess score, next count, and ended count |
| Edge | SAN, UCI, count, local percentage among games with a next move, and cumulative percentage among root games |

Moves expand strictly above 10%. Moves at or below 10% are visibly grouped. Expansion stops below 20 games, with 20
games eligible; there is no depth cap. Ended games remain in outcomes but are excluded from next-move denominators.
The intended result is a readable tree together with engine-ready structured JSON, while retaining the history-only,
no-engine boundary.

#### Finished tree experiment

The completed tree experiment is in:

`experiments/prototypes/caro-kann-skyrocoster-tree/`

Run it from the repository root with:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-skyrocoster-tree\caro_kann_tree.py
```

Its JSON schema is `caro-kann-history-tree/v1`.

| Tree result | Value |
| --- | ---: |
| Root games | 3,358 |
| Root W-D-L/unknown | 1,697-91-1,570-0 |
| Nodes | 229 |
| Expanded nodes | 106 |
| Stopped nodes | 123 |
| Maximum depth | 16 plies |

All stops are currently below support. Among root games with a next move, the root distribution is:

| Root next move | Games | Local/root percentage |
| --- | ---: | ---: |
| `Nf3` | 1,200 | 35.77% |
| `d4` | 1,146 | 34.16% |
| Grouped 23 other move kinds | 1,009 | 30.07% |

Three root games have no next move. Focused invariants and determinism passed. Full production validation was
intentionally deferred.

#### Core-coverage decisions and results

The first lens is the current core. Future intended behavior is described as core, secondary, and long-tail tiers;
their definitions and generation remain a later frontier, not a settled algorithm.

The coverage analysis funnels each ply. Local and root percentages remain distinct. Less-common moves, below-20
attrition, and ended/no-next attrition are explained rather than silently discarded. The top 10 stopped lines are
frequency-only views with outcomes as context; all 123 stopped nodes remain structured.

The core-coverage artifacts are:

- `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_core_analysis.py`
- `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_core_analysis.json`
- `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_core_analysis.md`

Run the analysis from the repository root with:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-skyrocoster-tree\caro_kann_core_analysis.py
```

Its JSON schema is `caro-kann-core-analysis/v1`.

| Ply | Root coverage |
| ---: | ---: |
| 2 | 100% |
| 3 | 69.86% |
| 4 | 69.62% |
| 5 | 62.39% |
| 6 | 62.00% |
| 7 | 53.37% |
| 8 | 50.98% |
| 9 | 38.98% |
| 10 | 28.29% |
| 11 | 20.58% |
| 12 | 6.52% |
| 13 | 4.94% |
| 14 | 2.47% |
| 15 | 2.05% |
| 16 | 0.51% |

The largest stopped exact lines contain only 19 games / 0.57%. This suggests that branch/position coverage may be
more informative than treating deep terminal lines equally. It is an observation, not a product conclusion.
Focused reconciliation and determinism passed; no engine or full suite was run.

#### Poor-results interview contract

The poor-results work starts with broad metrics; usefulness is deferred. It covers all 229 positions and every
immediate move, including tiny and unexpanded samples, while keeping White-opponent branches separate from
Black-Skyrocoster branches.

The slices are combined, bullet, blitz, and rapid; all-time and recent 12 months are separate, with recent counted
from the newest data date and older covering the remainder. Opponent strength is based on White-minus-Black rating:

- `>=100`: stronger;
- `-100<x<100`: similar;
- `<=-100`: weaker;
- unknown: separate.

Each record exposes `n`, W-D-L/unknown, raw win, chess score, a Wilson-style 95% heuristic, below-50, root delta,
parent delta, branch versus aggregate-other-siblings, root reach, loss count/share, signed score-point impact, and
below-baseline shortfall. There is no sample filter.

There are thirteen separate readable top-10 lenses and complete JSON output. Rankings are exploratory only. Nested
records overlap, impacts and loss shares are non-additive, and outcomes are noncausal.

#### Finished historical metrics

The generated historical-metrics artifacts are:

- `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_historical_metrics.py`
- `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_historical_metrics.json`
- `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_historical_metrics.md`

Run them from the repository root with:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-skyrocoster-tree\caro_kann_historical_metrics.py
```

The JSON schema is `caro-kann-historical-metrics/v1`.

The completed output contains 229 nodes and 863 branches: 553 White and 310 Black, including 635 unexpanded entries.
The root score is 51.89%.

| Slice | Count |
| --- | ---: |
| Bullet | 1,346 |
| Blitz | 1,463 |
| Rapid | 544 |
| Other | 5 |
| Recent 12 months | 1,794 |
| Older | 1,564 |
| Stronger opponents | 29 |
| Similar opponents | 3,325 |
| Weaker opponents | 4 |

The newest UTC date is 2026-08-17, so the inclusive recent cutoff is 2025-08-17. The deterministic Wilson-style
95% interval uses effective half-points and is a heuristic, not a calibrated probability statement.

One high-volume signal, without a recommendation, is opponent `3.exd5` after `1.e4 c6 2.Nf3 d5`: n=631, with 13.93
estimated score-points below the root baseline and an interval of 46.93%–52.44%. Its nested `3...cxd5` record has
n=629 and a similar 13.89 shortfall; it cannot be added to the parent record.

One raw Black warning, also without a conclusion, is:

> `1. e4 c6 2.Nf3 d5 3.exd5 cxd5 4.Nc3 d4 5.Ne4 f5`

Here `...f5` has n=8, 0% score, a 0%–19.36% interval, and is -51.89 percentage points from the root. The largest
parent/sibling extremes use n=1–4, illustrating sample noise.

Focused replay, reconciliation, determinism, and read-only proof passed. No engine or full suite was run.

### Final continuation frontier

Everything in the lead experiment remains noncanonical and descriptive. No application adoption, Plan, persistence
policy, training behavior, metric-usefulness decision, broad engine sweep, or production/full testing is approved.
The historical tree, core coverage, and metrics outputs do not prescribe a move or authorize implementation.

The two-track framing remains intact:

- **Track A — Original Advance:** decide the prescribed Black move after the original `5.Nf3` divergence.
- **Track B — Focused search:** investigate other exact lines for a frequent, outcome-negative,
  engine-confirmed mistake only after settling required numeric thresholds and search bounds.

Five distinct resumable items are the continuation frontier:

1. **Original Advance track:** decide its prescribed Black move after the original `5.Nf3`.
2. **Coverage tiers:** decide how to define and generate core, secondary, and long-tail tiers.
3. **Poor-result interpretation:** review which metrics contain signal versus sample noise before ranking or training use.
4. **Focused engine follow-up:** apply focused Stockfish later using retained FEN/SAN/UCI; no broad sweep yet.
5. **Explicit production choice:** choose production adoption and full testing only if explicitly desired.

This record chooses no move, candidate line, threshold, search architecture, persistence policy, implementation route,
or metric-usefulness decision. It remains a grilling record ready for continuation, not a Plan or implementation
authorization.

## Historical chain: exact-position pattern discovery

### Purpose and direction changes

The original discovery request was broad: scout captured chess-game data, compare useful groupings, determine how
repeated FENs could be found, and use prototypes to learn from the data. The discussion first considered game-level
patterns and position reconstruction, then narrowed to exact legal positions and a concrete opening-learning workflow:

1. The user plays the Caro-Kann as Black.
2. The user creates a move graph with one manually preferred move at each of their decision positions.
3. Captured games reveal positions where the user did not play the preferred move.
4. Engine evidence reveals moves that materially worsened the user's position.
5. Frequently reached positions without a preferred move reveal repertoire coverage gaps.
6. Population and engine evidence propose candidates, but neither automatically sets the preferred repertoire move.

The discovery record is evidence for later work, not a product specification or permission to add dependencies,
schemas, downloads, APIs, engines, or UI.

### Repository data and source facts

The bounded discovery found:

- `data/database/chess_games.db` at approximately 44 MB, with 12,369 games, 11,750 players, and 31 monthly fetch-state rows;
- 31 monthly Chess.com JSON files under `data/chess-com/raw/games/`, covering 2024-02 through 2026-08;
- `scripts/chess_com/fetch_games.py` as the fetch and normalization owner;
- `scripts/scout_db_query.py` as a read-only SQLite example;
- no backend application feature consuming this chess data at the time;
- game rows containing PGN, final FEN, player references, ratings, results, time control/class, opening URL, and source metadata, but not separate move-by-move positions;
- 4,612 blitz, 4,217 bullet, 3,422 rapid, and 118 daily games;
- 16 distinct time controls;
- 12,320 distinct final-FEN strings, which are not repeated intermediate-position evidence;
- ECO codes in PGN headers rather than a dedicated equivalent database column; and
- Chess.com accuracy on only 1,528 games.

Potential dimensions such as result, rating, rating gap, color, opponent, time control, date, termination, opening,
and accuracy remain future descriptive context, not a selected product ranking.

The prototype environment used Python 3.12 and an isolated `Scratch/prototypes/.venv/` containing `python-chess`
1.11.2. Neither `python-chess` nor pandas was in the repository's main requirements at discovery time. No Stockfish
was initially installed in the repository, PATH, or common Windows locations before the isolated prototype download.

### Exact-position identity

The first pattern layer is exact legal positions, not structural or situational similarity. `python-chess` owns parsing
and chess-rule semantics. The repetition key is the rule-aware state consisting of:

- piece placement;
- side to move;
- castling rights; and
- legally relevant en-passant state.

Halfmove and fullmove counters are excluded from the grouping key. Full source FEN remains evidence, but is not the
grouping identity. All plies are retained, including ply zero, because common opening positions are the intended
signal; the universal starting position is retained but displayed separately. The analysis concerns repetition across
games, not repetition cycles within one game. Rare within-game opening duplicates may use straightforward occurrence
counts initially.

This four-field identity must not be confused with the exact six-field FEN used by engine analysis. A literal six-field
comparison separates equivalent training states when counters differ, while piece placement alone incorrectly combines
states with different legal decisions.

### Repertoire graph and evidence queues

The conceptual repertoire is keyed by normalized legal position, so different move orders reaching the same position
share one preferred move. The first scope is the Caro-Kann. The graph includes the user's Black decision nodes and
White's connecting branches, but preferred moves are assigned only at the user's Black decisions. Caro-Kann membership
was initially recognized by reaching the canonical position after `1.e4 c6`, rather than by trusting an external label.

The three queues answer different questions:

1. **Repertoire miss:** a preferred move exists for a reached position, but the user played another move.
2. **Harmful move:** the user's move caused a sufficiently negative objective evaluation change under a selected comparison policy.
3. **Coverage gap:** a position occurs frequently enough to deserve a learned response, but no preferred move exists.

The initial direction requires both resulting-position evaluation and evaluation loss against the engine's best candidate
when discussing a harmful move. It does not select the actionable threshold. Manual authority remains with the user;
engine and population evidence cannot silently become preferred moves.

### Opening names, transpositions, and prototype evidence

The selected local name source was the CC0/public-domain `lichess-org/chess-openings` dataset, carrying ECO, English
name, PGN move sequence, and generated UCI/EPD data. `pgn-extract` and Polyglot were researched but not selected for
the local naming role. Lichess Explorer is a population-statistics source, not the local name dataset.

Replay proceeds forward and retains the latest exact opening-name match. An unnamed later position is labelled from
the deepest named ancestor plus moves since that ancestor, for example `B12 Caro-Kann Defense: Advance Variation -
after 3...Bf5`. The prototype downloaded five TSV files with A–E counts 817, 772, 1,250, 614, and 357, for 3,810
records. All replayed successfully; base Caro-Kann, Advance, Exchange, Panov, and Classical positions resolved, while
the post-`3...Bf5` position demonstrated the need for deepest-ancestor naming. Two Panov move orders and a Classical
`3.Nc3`/`3.Nd2` example demonstrated transpositions.

The first useful recurring-position comparison combines continuation frequency and subsequent game result, with
aggregate results first and optional one-factor context for rating gap, time control, color, and period. Descriptive
uncertainty, visible support, and a later small-sample policy are required; formal causal testing was deferred.

### Population evidence

The preferred population direction was realistic Lichess standard play rather than an exclusively elite corpus.
Lichess standard archives are CC0 but very large; broadcast games, TWIC, Chess.com published data, and FIDE lists have
different licensing or reuse limitations. Because bulk archives are impractical for indiscriminate filtering, the
selected acquisition sequence was to query aggregate Opening Explorer statistics first and acquire selected raw games
only when deeper evidence is necessary.

Explorer can filter by position or move sequence, rating bands, speeds, and month range, and returns move frequency,
ratings, outcomes, history, and limited game references. It ranks candidates but cannot select a repertoire move. A
prototype used the authenticated `https://explorer.lichess.org/lichess` endpoint with a narrowly scoped token held in
the Windows user environment. An accidentally exposed setup token was revoked; no credential value belongs in this
record or repository.

The authenticated observation used rating groups `1600,1800,2000,2200`, speeds `blitz,rapid`, and months 2024-01
through 2026-07. Six requests returned HTTP 200. Representative observations were `...c6` after `1.e4` at 9.71%,
`2.d4` after `1.e4 c6` at 50.86%, Advance `3.e5` at 36.09%, `3...Bf5` at 63.19%, and `3...dxe4` after `3.Nc3` at
81.58%. These are point-in-time cohort observations and neither prove causality nor select a move.

### Distinct Stockfish contexts

The historical evidence contains several engine contexts. They are intentionally separate:

| Context | Settings and meaning |
| --- | --- |
| Discovery full-sample intention | Stockfish 18, fixed depth 18, MultiPV 3, Threads 1, Hash 64 MB, White-relative and side-to-move-relative typed scores, PVs and timing. This was an intended branch-diverse sample, not a completed result. |
| Discovery smoke test | One B12 position at depth 1, MultiPV 3, Threads 1, Hash 64, Skill Level 20, Move Overhead 10; process and cleanup proof only, with `...h5`, `...Nc6`, and `...h6`. It has no repertoire significance. |
| Accepted MP-09/MP-10 persisted profile | `mp09-balanced-nodes-v2-200000`: Stockfish 18, 200,000 nodes, MultiPV 5, Threads 1, Hash 128 MiB, engine WDL, exact six-field FEN identity, White-relative typed score semantics. See the [MP-09 Plan](../plans/done/mp09-persisted-backend-stockfish-analysis/mp09-persisted-backend-stockfish-analysis.md) and [MP-10 Plan](../plans/done/mp10-browser-evaluation/mp10-browser-evaluation.md). |
| Fresh Caro-Kann experiment | Stockfish 18, 200,000 nodes, MultiPV 5, Threads 1, Hash 128 MiB, WDL enabled, evaluations reported from Black's perspective. This is fresh, nonpersisted experiment evidence. |

Matching numeric settings do not make these records one analysis run or one evidence namespace. Score perspective,
exact FEN identity, provenance, persistence, and purpose remain explicit. The discovery full prototype was incomplete:
it configured MultiPV incorrectly for the installed binding, called `PovScore.pov()` without a color, and assumed an
unavailable `SimpleEngine.process`. A failed setup also leaked an engine subprocess in one reproduction. The bounded
smoke test corrected those binding faults and proved cleanup. Further prototype commands require external shell
timeouts around downloads, extraction, engine launch, and waits; internal timeouts and `finally` cleanup alone are not
sufficient.

### Discovery decisions and open branches

The discovery decisions were to analyze game- and position-level data in stages; preserve player-centric and
color-aware views; begin with exact positions; let `python-chess` own identity; compare continuations and outcomes;
use descriptive uncertainty; define repertoire misses, harmful moves, and coverage gaps; key the graph by legal
position; use the local CC0 name data; use realistic Lichess play as candidate evidence; query Explorer before bulk
games; keep population and engine evidence separate; record resulting evaluation and loss separately; and use
bounded, timeout-protected Stockfish experiments.

Open branches include preferred-move storage and history, coverage-gap thresholds, regression/forgetting definitions,
non-Caro move-order treatment, statistical display and uncertainty, Explorer cohort and credential policy, engine
profile and stale-result policy, harmful-move thresholds, candidate union rules, batch cancellation and recovery, and
whether production should adopt any experiment. Deferred analysis includes structural similarity, motifs, broad
performance summaries, formal causal claims, and automatic preferred-move selection.

## Historical chain: personal classification and progressive line training

### Conceptual direction

The second historical thread records a confirmed conceptual direction, not a specification or implementation
authority. Exact board position is the primary training identity. Opening labels organize practice but never replace the
exact position. Everything tracked—membership, recurrence, progress, and training moves—attaches to the exact state.

Opening identity and membership are neutral facts, separate from the player's relationship to them. A game receives a
set of memberships rather than one label, each with source type, anchor position, and introduction point. Positions may
belong to multiple collections under a canonical hierarchy and transposition cross-links. The initial direction uses a
fixed standard taxonomy with no user editing, merging, or custom taxonomy. Broad families and nested variations are
retained. Downstream positions may inherit memberships along actual game paths only within a future adaptive frontier;
the exact inheritance arithmetic remains open.

### Adaptive frontier and recurrence

The adaptive opening frontier is derived only from the player's own games. Population data can suggest candidates but
never contributes to what this player is tracked against. The settled signals are:

- absolute support for a position or route;
- conditional branch frequency given that the parent was reached;
- recency, including game sequence so later games weigh more;
- rating proximity; and
- a lower retirement threshold with hysteresis so small sample changes do not churn the frontier.

No exact formula, threshold, weighting scheme, or retirement value is selected. Global recurrence and opening-route
recurrence remain separate. Overall and color-specific counts are retained; color-specific evidence governs relevant
practice, so a state reached often as Black is not silently treated as equally relevant as White.

### Progressive full-line training

Training asks only the player's decision positions while retaining opponent moves as context. It trains full lines,
not isolated moves. The settled rhythm is to reinforce the current line endpoint, extend one decision deeper only after
reliable recall, retain earlier foundation moves, and pause deeper progression when earlier recall weakens. Pausing is
not a reset and never deletes prior progress.

When routes converge on the same exact position, board mastery is shared while route progress is separate. One
player-chosen accepted training move at a shared position creates a shared continuation for all routes through it.
Engine analysis and game history may inform the choice but never select it automatically.

Branch priority is intended eventually to combine personal recurrence, recency, rating relevance, mistake persistence,
typical engine loss, and amount already trained. The purpose is to avoid letting one isolated severe blunder dominate
repeated moderate errors. The factors are directional evidence only; the combination and weights are deferred.

Raw facts and complete attempt history remain durable, while priority is a replaceable calculation. Opening assignment
is permanent in the initial version; later rebuild or reclassification is open but not designed here.

### Explicitly deferred decisions

The thread deliberately leaves open the recurrence/frontier formula, thresholds and hysteresis, priority weighting,
membership/provenance schema, taxonomy editing, assignment rebuilding, line-extension mechanics, and all product,
dependency, or implementation details. It does not alter the earlier exact-position, transposition-aware, manual-
authority, or backend-analysis contracts.

## Historical chain: opening-classification database foundation

### Intended database destination

The database-foundation thread approved a master-plan direction for five sequential, independently Plan-backed slices.
It was database-only: no frontend, API, engines, population evidence, or training surface. The intended destination was
the existing SQLite database and the five fixed TSV files containing all 3,810 opening records. The source catalog was
to preserve ECO, name, move sequence, exact endpoint, and source/import provenance without live Lichess integration.

Exact legal positions remained primary. Opening-owned endpoints were to remain separate from game-derived positions; a
bounded comparison found 3,021 catalog endpoints absent from the existing game-derived `position_state` rows. Those
opening-only endpoints must never be inserted as if they were observed game facts.

The intended slices were:

1. source catalog storage and opening-owned endpoint identity/provenance;
2. opening hierarchy and transposition relationships;
3. neutral game classification and complete downstream route facts;
4. authoritative recurrence facts and deterministic rebuildable aggregates; and
5. tracked-player projection for skyrocoster.

The intended envelope required atomic, idempotent, change-aware, auditable imports with no partial publication; exact
four-field identity; neutral facts independent from player facts; stable UUID identity rather than username, numeric ID,
or SQLite `rowid`; and no formulas or thresholds in the database foundation.

### Actual current slice status

The historical destination must now be read against the accepted Plans:

- **S1 is accepted.** The five fixed source files produced 3,810 catalog records in separate opening-owned tables;
  opening-only endpoints remain outside game-derived position tables.
- **S2 is accepted.** Replay-derived parents, broad/nested memberships, explicit transpositions, and all valid
  memberships are persisted without reducing them to one label.
- **S3 is accepted.** Every exact accepted catalog endpoint reached by an accepted game has source-row provenance,
  game/ply anchor, all matching memberships, and a complete observed suffix route. The accepted runtime evidence records
  12,365 games, 49,608 anchors, and 2,402,576 route facts.
- **S4 is accepted.** Authoritative neutral recurrence and branch facts plus deterministic global and route projections
  were published without formulas, thresholds, frontier, or player decisions. Its accepted runtime evidence records
  639,262 global occurrence events, 2,402,576 route events, 639,262 branch events, and rebuildable projections.
- **S5 is abandoned and not accepted.** Temporary identity, derivation, fixtures, and rollback proof existed, but two
  runtime publication attempts failed or were interrupted. The database was restored to S1–S4 and contains no retained
  S5 tables or personal projection capability. The [S5 retrospective](ABANDONED/s5-tracked-player-projection-retrospective.md)
  records the abandonment and the bounded direction to query existing S1–S4 facts directly rather than retrying the
  copied/materialized projection model.

The status correction is essential: the original five-slice direction is not evidence that all five slices were
accepted. S1–S4 are current accepted foundations; S5 is a closed historical failure, not a pending or delivered
feature.

### Preserved database boundaries

The accepted database work preserves:

- opening-owned catalog and relationship facts separately from accepted game-derived corpus facts;
- exact four-field training/recurrence identity and natural game/ply provenance;
- multiple memberships and transpositions without exclusive-label reduction;
- neutral facts independently from player-specific facts;
- raw authoritative events separately from rebuildable aggregates;
- atomic publication, changed-input refusal, unchanged reruns, rollback, and no partial state; and
- stable player UUID semantics where a player projection is discussed, without usernames as durable identity, numeric
  IDs, or SQLite `rowid`.

The database foundation excludes frontend, APIs, live population integration, preferred moves, training history,
adaptive-frontier formulas, branch-priority scoring, custom taxonomy, taxonomy editing, additional players, destructive
migrations, source changes, dependency changes, Scratch writes, and historical-record edits.

## Historical chain: opening training and repertoire preparation

### Reading rules and observed current facts

The full preparation thread is a design-evidence synthesis. It does not authorize database writes, preferred moves,
thresholds, formulas, engine releases, population sources, credentials, training UI, route behavior, or historical
record edits. When an accepted Plan and the untracked database appear to disagree, the difference is an audit item, not a
reason to rewrite the historical Plan or silently choose the latest number.

At the time of that read-only synthesis, the following values were reported and are not interchangeable denominators:

| Fact | Value | Meaning and caution |
| --- | ---: | --- |
| Fetched game rows | 12,369 | Normalized source rows; not the accepted training corpus |
| Accepted standard games | 12,365 | Standard subject-corpus games; four `oddschess` rows excluded |
| Ordered occurrences | 639,262 | Game-global positions including ply zero; not unique states |
| Unique training states | 510,876 | Deduplicated four-field legal states |
| Opening catalog records | 3,810 | Fixed five-file source with provenance |
| Opening relationship positions | 7,927 | Opening-owned taxonomy relationship keys |
| Opening memberships | 36,925 | Membership-inclusive and not exclusive labels |
| Opening transposition links | 12,077 | Taxonomy relationships, not automatic training equivalence |
| Engine analysis results | 3,158 | Partial exact six-field roots |
| Engine candidate rows | 15,736 | Ranked candidates with variable candidate counts |
| Analysis batch summaries | 2 | Both referred to the same selected game and 83 positions |
| Evaluation queue rows | 1 | Separate evaluation namespace evidence |

The historical MP-09 opening-first preflight projected 515,515 unique six-field FENs, with 515,432 missing at that
time. That was a read-only planning number, not proof that the corpus had been analyzed. The exact four-field corpus
identity and exact six-field engine identity must remain separate.

The preparation thread also recorded an engine provenance audit gap: 3,075 of the 3,158 persisted analysis roots were
outside the exact 83-FEN selection represented by the two durable batch summaries. The available records did not
provide a complete direct result-to-run explanation for those rows. The safe audit categories are: directly tied to a
recorded selected-game batch; directly tied to an evaluation-queue event; carrying engine/profile/settings evidence
without complete run attribution; or failing identity/content validation. These are audit categories, not an
authorization to replace the engine data or infer wrongdoing.

The source covers approximately 31 months, with 4,612 blitz, 4,217 bullet, 3,422 rapid, and 118 daily games. The
database carries time control, time class, date, ratings, colors, results, termination, opening source fields, and
limited accuracy. All current PGNs showed clock markers in the bounded scout, but parser validation is required before
calling those annotations comparable thinking time.

### Identity, ownership, and authority contracts

The four-field training identity is piece placement, side to move, castling rights, and legally relevant en-passant
state. Halfmove and fullmove counters are excluded. The six-field analysis identity includes the counters and is valid
only for that exact FEN and recorded profile; it is not silently reusable for every occurrence of a four-field state.

Opening catalog endpoints and relationship positions are opening-owned. Game-derived states and occurrences are owned
by the accepted corpus. Reports must distinguish global game-derived counts, opening-owned taxonomy counts, route-
specific game-derived counts, and player-specific projections. Multiple valid memberships are preserved.

Neutral facts describe games, routes, memberships, recurrence events, results, ratings, colors, and chronology without
depending on a selected player. Player facts describe how `skyrocoster` relates to those facts. The stable player UUID,
not a username, numeric ID, or `rowid`, is the durable identity boundary.

Manual repertoire authority remains with the user. Engine output, population frequency, opening labels, and historical
play may propose or explain candidates but never select the accepted move automatically. The initial conceptual
direction uses one accepted move per shared exact training position while preserving future history if that move changes.

Raw source, replay, move, route, manual-choice, engine-run, population-snapshot, and attempt facts should remain
durable where they can be audited. Recurrence summaries, branch priority, frontier membership, mastery, queues,
survival curves, and report caches are replaceable calculations with identifiable input and calculation versions.

Progressive training reinforces the current endpoint, extends only after reliable recall, and pauses without deleting
earlier progress. Shared board mastery and route-specific progress remain separate, and route/prompt context remains
important even when exact board identity converges.

### What descriptive analysis can support

The prepared facts can support, subject to the identity and denominator boundaries:

- a corpus and data-quality observatory showing fetched, accepted, excluded, occurrence, state, catalog, engine,
  queue, run, replay, FEN, SAN/UCI, clock, integrity, and provenance categories;
- exact-state recurrence with distinct-game and occurrence support, ply distribution, color, time, rating, date, result,
  taxonomy, and transposition context;
- branch tables with parent, child move, distinct games, occurrences, conditional denominator, cohorts, and support
  warnings, optionally accompanied by an explicitly nonauthoritative entropy-like dispersion summary;
- retrospective comparison of a player's move with a manually accepted move once such a history exists;
- objective move-loss evidence only where exact before/after six-field FENs and comparable engine provenance exist;
- catalog, parent, membership, and taxonomy-transposition inspection;
- historical game-side comparisons by color, time class, rating, opponent, month, termination, result, and source field;
  and
- clock-derived candidates only after parser and source-semantic validation.

Possible staged analytical products were described as: A, read-only corpus observatory; B, exact-state recurrence and
branch report; C, neutral opening classification and route report; D, authoritative events and rebuildable aggregates;
E, tracked-player projection; F, manual repertoire evidence and three queues; G, separate engine and population
candidate reports; H, training-attempt and retention reports; and I, adaptive frontier, priority, and progressive depth.
These are possible slices, not an implementation sequence or authorization.

### Unsupported claims and separate queues

The evidence does not support claiming that a game result proves opening quality, an engine or population move is the
correct personal repertoire move, a population frequency is causal or universal, a six-field engine result is timeless
or reusable for every four-field occurrence, or that the player forgot, mastered, improved, or transferred a line
without attempt events. It does not support calling a route a coverage gap without classification, player projection,
preferred move, support rule, and denominator; calling a move harmful without validated comparable before/after
evidence and a threshold policy; treating later cohorts as proof of improvement; calling a clock annotation exact
thinking time before validation; or attributing the 3,075-result provenance mismatch to wrongdoing or a particular
unauthorized operation.

The queues remain explainable and separate:

- **Repertoire miss:** a user-authorized preferred move exists for the exact state and the player played another move.
- **Harmful move:** a player's move has sufficiently negative objective change under a selected, comparable engine policy.
- **Coverage gap:** a recurring player-relevant state or route lacks a user-authorized preferred move.

A state may belong to more than one queue over time. Queue history must not overwrite why a state became visible. No
priority formula, threshold, hysteresis, or automatic ranking is selected.

### Analytical levels and suggested reports

The historical synthesis kept four analytical levels separate. At the game level, the safe observations are reached
routes, played moves, result, termination, validated clock context, and source replay status; a result does not prove
opening quality. At the route level, the safe observations are entry anchor, downstream path, branch, depth, survival,
and route-specific recurrence; survival does not prove strength or memory. At the position level, the safe observations
are exact state, distinct-game support, occurrence support, incoming routes, outgoing moves, engine coverage, and manual
assignment status; recurrence does not prove importance or a label's identity. At the move-decision level, the safe
observations are the player's move, accepted snapshot, candidate evidence, engine loss where comparable, and future
attempt answer/hint/latency; a non-preferred move is not automatically a blunder.

Suggested report surfaces preserve textual evidence and visible denominators:

- a corpus ledger for fetched, accepted, excluded, occurrence, state, source, and run counts;
- a namespace ledger separating four-field training states, six-field analysis FENs, opening-owned endpoints, and queue rows;
- a provenance ledger separating attributable, queue-attributable, profile-only, and unresolved engine results;
- a source-quality report for replay, malformed FEN, clock-parser, accuracy-subset, duplicate-source, and stale-schema warnings;
- state-detail, branch, opening-graph, coverage, and three-queue tables with support and uncertainty;
- route-survival, breadth/depth, and transposition-convergence reports with route progress separate from shared states; and
- attempt-timeline, retention, transfer, and progress views once append-only training attempts exist.

These are report concepts, not UI requirements. Any visual requires a textual or accessible equivalent and must not hide
denominators, uncertainty, multiple memberships, stale evidence, or unresolved provenance.

### Training attempts, retention, depth, and coverage

Game moves are not training attempts. A future append-only attempt event should preserve attempt identity/time, player,
exact prompted state, route and depth context, accepted-move snapshot, answer, correctness, skipped/timeout state, hint
use, latency, confidence, session/repetition context, line endpoint, calculation version, and failure details. The
accepted-move snapshot prevents a later manual change from rewriting what an earlier attempt meant.

Immediate recall, delayed retention, transfer, mastery, and forgetting each require distinct event definitions. One
correct answer is one successful attempt, not mastery. Missing future attempts are missing evidence, not failures.
Transfer must preserve route, move order, color, context, accepted snapshot, and exposure history because a shared board
does not imply a shared cue.

Breadth, depth, branch mass, survival, and coverage are non-equivalent measures. Reports must name whether they count
families, routes, states, decisions, occurrences, games, or attempts; whether depth means ply, full move, player
decision, route distance, or training endpoint; and which denominator defines branch mass. Survival must distinguish
game ending, branch changes, classification boundaries, missing data, and training pauses. Membership-inclusive counts
must not masquerade as unique-state breadth.

### Transpositions, cohorts, uncertainty, and sensitivity

Taxonomy transpositions describe opening-source relationships. Game-side transpositions preserve each source game,
anchor, ply, incoming prefix, player color, and route even when the four-field state is shared. Reports should offer
global unique-state, route, membership-inclusive, and distinct-game views without adding memberships as exclusive totals.

Useful cohorts include calendar period, time class/control, ratings and rating gap, color, opening route, recency, result
as context, engine profile/date, and future training exposure. Repeated occurrences from one game are not independent
samples. Any uncertainty method, minimum support policy, clustering choice, formal test, or multiple-comparison policy
remains open.

Sensitivity should compare game versus occurrence counts, all history versus recent windows, raw versus recency-weighted
support, rating bands, time classes, low-support handling, membership display modes, depth definitions, harmful-move
thresholds, engine profiles and stale results, and hint-free versus all-attempt outcomes. Sensitivity is not a license
to select the most favorable result.

### Engine and population boundaries

Engine evidence can provide ranked candidates, typed scores and mates, principal variations, resulting-position
evaluation, and evaluation loss relative to a candidate from the exact starting FEN. It cannot supply the user's
preferred move automatically and cannot erase uncertainty from finite budgets, MultiPV ordering, profile changes, stale
results, partial coverage, or provenance gaps.

Population evidence can suggest common responses, expose branches absent from personal games, compare personal choices
with an external reference, and propose candidates for review. It cannot define the player's adaptive frontier, select
a preferred move, establish causality, or generalize to every player. Personal recurrence, population frequency, engine
evidence, and manual authority should be displayed separately rather than collapsed into one score.

### Future storage candidates and second-pass findings

Future design may consider append-only manual preferred-move history, append-only training attempts, neutral game-opening
anchors and route facts, engine and population provenance, raw-source/parser provenance, rebuildable views and caches,
retention/versioning policies, and safe database backup/audit preparation. These are candidates, not selected schemas.

The second pass highlighted that training changes the future sample; shared states do not imply shared cues; accepted
moves can change after attempts; repertoire misses and harmful moves can disagree; counterfactual engine comparisons are
fragile; branch mass can hide a personally important low-mass branch; route survival can be mistaken for abandonment;
membership counts can exaggerate breadth; cumulative history can obscure current behavior; rating proximity is not
neutral; clock data can create false precision; accuracy is a selected subset; fetched, accepted, and analyzed are
different populations; provenance gaps can bias conclusions; population evidence can be mistaken for personal need;
prompts can leak answers; correctness is policy-dependent; opponent plies can inflate depth; taxonomy assignment can
become stale; and rebuilds can change reports without changing raw facts.

Additional future opportunities include confidence calibration, recognition versus recall versus transfer prompts,
route-specific error persistence, move-time context, separate candidate reports, branch novelty, intervention-aware
comparisons, line compression at convergence, and provenance completeness reporting. None is selected here.

### Open decisions retained from the preparation thread

The following remain open and must be settled by later focused grilling or planning rather than implementation:

1. whether one accepted move per state is sufficient, how move history is retained, and whether route-specific preferences are ever needed;
2. coverage-gap support, harmful-move comparison and threshold, queue interaction, priority factors, entry/retirement, and hysteresis;
3. encountered-opening and route semantics, non-Caro move orders, assignment versioning, and multi-membership totals;
4. primary breadth/depth measures and route-survival causes;
5. correctness, hints, timing, confidence, retention, transfer, extension, and pause/recovery policies for training;
6. uncertainty units, interval/resampling/support-tier policy, cohorts, sensitivity, and any formal testing;
7. engine provenance reconciliation, profile, score normalization, mate handling, stale policy, before/after comparability, coverage, and batch recovery;
8. population cohort, source, licensing, credentials, caching, refresh, raw-game acquisition, and display policy; and
9. storage, retention, audit, backup, report, accessibility, and presentation choices.

## Safe canonical conclusion

The lead experiment found a concrete and intentionally unresolved Advance-line frontier after `5.Nf3`, while later
historical-tree, core-coverage, and metrics work supplied descriptive structure without choosing a move. The earlier
chain supplies the identity, ownership, provenance, classification, recurrence, manual-authority, training, and
noncausal-evidence boundaries needed to interpret that experiment safely.

The accepted repository foundation can expose exact state recurrence, route and taxonomy relationships, player-side and
time-control context, and bounded engine or population candidate evidence. It cannot by itself prove a correct personal
move, memory, mastery, improvement, transfer, or causality. The important missing facts remain complete auditable
route context where needed, durable manual preferred-move history, linked engine/population provenance, append-only
training attempts, and versioned rebuildable calculations.

Until those facts and decisions exist, the safe language is “observed,” “candidate,” “under this profile,” “reached,”
“compared,” and “attempted.” It is not “best,” “caused,” “mastered,” “forgotten,” or “trained.” Any later focused Plan
must select one bounded outcome, preserve the four-field/six-field namespace boundary, keep manual authority with the
user, keep engine contexts separate, and escalate rather than deciding an open product, formula, data, engine,
ownership, or acceptance question.

## Canonical evidence references

- [Documentation Router](../README.md)
- [MP-06 Validated FEN Corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md)
- [S1 Source Catalog Plan](../plans/done/s1-source-catalog/s1-source-catalog.md)
- [S2 Opening Relationships Plan](../plans/done/s2-opening-relationships/s2-opening-relationships.md)
- [S3 Neutral Classification Plan](../plans/done/s3-neutral-classification/s3-neutral-classification.md)
- [S4 Authoritative Recurrence Plan](../plans/done/s4-authoritative-recurrence/s4-authoritative-recurrence.md)
- [S5 Tracked-Player Projection Plan](../plans/done/s5-tracked-player-projection/s5-tracked-player-projection.md)
- [S5 Tracked-Player Projection Retrospective](ABANDONED/s5-tracked-player-projection-retrospective.md)
- [MP-09 Persisted Backend Stockfish Analysis Plan](../plans/done/mp09-persisted-backend-stockfish-analysis/mp09-persisted-backend-stockfish-analysis.md)
- [MP-10 Browser Evaluation Plan](../plans/done/mp10-browser-evaluation/mp10-browser-evaluation.md)

The runtime database and tracked `data/database/schema.txt` remain runtime/schema evidence rather than committed
documentation authority. This canonical document preserves the historical records without changing those artifacts.
