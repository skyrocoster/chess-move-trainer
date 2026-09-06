# DB-07 Stockfish Node-Budget Benchmark — Compact Results Report

Experiment: `experiments/prototypes/stockfish-db07-benchmark` (full-run artifacts under `.artifacts/full-run/`).
Report generated: 2026-09-05. This is a descriptive persistence report of already-computed aggregates. It contains
no raw benchmark records.

## 1. Status and Scope

- Full matrix: 2520 jobs (12 profiles x 7 node budgets x 3 rounds x 10 fixed positions; MultiPV 5).
- Successful retained results: **1822 (72.3%)**. Failed: **698 (27.7%)**. Unfinished: 0.
- Dataset state: **INCOMPLETE** (per `.artifacts/full-run/status.txt`: "1822/2520 successful; 698 failed jobs; 0 unfinished").
- All 698 recorded failures are `PermissionError` (`[WinError 5] Access is denied`) around atomic
  manifest/checkpoint persistence or rename. They are **not** Stockfish analysis failures.
- Exactly **four** profiles are incomplete: **t1-h256, t1-h1024, t4-h64, t6-h256**. All other eight profiles are fully
  covered (210/210 each). Failures by incomplete profile: t1-h256 184, t1-h1024 156, t4-h64 152, t6-h256 206 (sum 698).
- An earlier interim summary claiming that all 698 failures belonged to a single profile is **retracted**; the profile
  table below is authoritative and agrees with two independent inventory/coverage passes.
- 6.4M nodes is the **highest-tested reference**, not ground truth.

## 2. Provenance and Safe Extraction Method

- Local source: `.artifacts/full-run/` under this experiment directory.
- `status.txt` supplied the state/counts; `summary.csv` (~140 KB, 1822 successful rows plus header) supplied flattened
  scalar performance columns.
- Convergence and repetition metrics were computed by a **streaming line-by-line pass** over `attempts.jsonl`
  (~3.4 MB, 2520 lines), retaining only scalar and signature aggregates. The raw file was never loaded wholesale or
  emitted into AI context. `summary.json` (~6.8 MB) and `manifest.json` (~82 KB) were not read wholesale either.
- Method note: the raw files are not unusable because of their size alone; the streaming/CSV-aggregate method was
  chosen deliberately so that no bulk artifact content is copied into context. This report reproduces only aggregates.
- No raw positions, principal variations, candidate moves, attempt records, or embedded bulk JSON appear in this report.

## 3. Coverage

### 3.1 By profile (denominator 210 each)

| Profile | Successful | Coverage |
|---|---|---|
| t1-h64   | 210 | 100.0% |
| t1-h256  | 26  | 12.4%  |
| t1-h1024 | 54  | 25.7%  |
| t2-h64   | 210 | 100.0% |
| t2-h256  | 210 | 100.0% |
| t2-h1024 | 210 | 100.0% |
| t4-h64   | 58  | 27.6%  |
| t4-h256  | 210 | 100.0% |
| t4-h1024 | 210 | 100.0% |
| t6-h64   | 210 | 100.0% |
| t6-h256  | 4   | 1.9%   |
| t6-h1024 | 210 | 100.0% |

### 3.2 By node budget (denominator 360 each)

| Budget | Successful | Coverage |
|---|---|---|
| 100k | 259 | 71.9% |
| 200k | 260 | 72.2% |
| 400k | 255 | 70.8% |
| 800k | 264 | 73.3% |
| 1.6M | 256 | 71.1% |
| 3.2M | 263 | 73.1% |
| 6.4M | 265 | 73.6% |

### 3.3 By round (denominator 840 each)

| Round | Successful | Coverage |
|---|---|---|
| R1 | 611 | 72.7% |
| R2 | 611 | 72.7% |
| R3 | 600 | 71.4% |

### 3.4 By position

179–185 successful jobs of 252 each (71.0%–73.4%) across the ten fixed positions.

**Conclusion:** missingness is strongly **profile-driven**, while broadly balanced over node budget, round, and
position. Profile comparisons and matched samples must carry their denominators throughout this report.

## 4. Performance by Node Budget

Wall-clock seconds and medians over successful jobs (n per row). Mixed-profile medians are **descriptive only**; they
are not controlled profile comparisons because profile mix and missingness vary.

| Budget | n | Wall p10 | Wall median | Wall p90 | Median engine NPS | Median depth | Median seldepth | Median hashfull (per mille) |
|---|---|---|---|---|---|---|---|---|
| 100k | 259 | 0.039 | 0.098 | 0.139 | 2,042,775 | 10 | 16 | 1 |
| 200k | 260 | 0.064 | 0.135 | 0.237 | 2,146,502 | 11 | 19 | 3 |
| 400k | 255 | 0.113 | 0.233 | 0.471 | 1,846,092 | 12 | 22 | 7 |
| 800k | 264 | 0.207 | 0.468 | 0.952 | 1,805,217 | 14 | 26 | 15 |
| 1.6M | 256 | 0.392 | 0.818 | 1.899 | 2,093,871 | 15 | 29 | 30 |
| 3.2M | 263 | 0.797 | 1.953 | 3.877 | 1,658,967 | 17 | 33 | 65 |
| 6.4M | 265 | 1.588 | 3.929 | 7.785 | 1,633,941 | 19 | 37 | 134 |

Wall time and depth grow monotonically with budget. Engine NPS is roughly flat to slightly declining at higher budgets,
with non-monotonic wiggle (see Section 10 for why engine NPS and wall-clock-derived rates must not be interchanged).

## 5. Profile Performance and Matched Thread Scaling

### 5.1 Profile medians

Normalized wall seconds per 1M requested nodes; successful n out of 210 each.

| Profile | Successful n/210 | Median engine NPS | Median normalized wall s per 1M nodes |
|---|---|---|---|
| t1-h64   | 210 | 839,430   | 1.2104 |
| t1-h256  | 26  | 852,873   | 1.1998 |
| t1-h1024 | 54  | 791,113   | 1.3942 |
| t2-h64   | 210 | 1,519,624 | 0.6764 |
| t2-h256  | 210 | 1,514,040 | 0.7132 |
| t2-h1024 | 210 | 1,479,674 | 0.8012 |
| t4-h64   | 58  | 3,012,038 | 0.3582 |
| t4-h256  | 210 | 2,963,906 | 0.3883 |
| t4-h1024 | 210 | 3,046,412 | 0.4217 |
| t6-h64   | 210 | 4,597,509 | 0.2457 |
| t6-h256  | 4   | 4,360,072 | 0.3129 |
| t6-h1024 | 210 | 4,022,262 | 0.3642 |

**Warning:** t1-h256 (26), t1-h1024 (54), t4-h64 (58), and t6-h256 (4) are incomplete profiles; their unpaired medians
are drawn from non-representative subsets and are less comparable to the fully covered profiles. t6-h256 has only 4
successful jobs and its row is essentially anecdotal.

### 5.2 Matched thread speedup

Definition: `T_1-thread / T_N-thread` on identical (position, node budget, hash, round) successful pairs.
**Ratio > 1 means faster with more threads.**

| Comparison | Matched pairs n | p10 | Median | p90 |
|---|---|---|---|---|
| t2 vs t1 | 290 | 1.535x | 1.779x | 2.027x |
| t4 vs t1 | 138 | 2.493x | 3.347x | 3.698x |
| t6 vs t1 | 264 | 3.123x | 4.700x | 5.397x |

Scaling is sublinear at six threads (median 4.700x < 6x). Pair sets differ across comparisons because the incomplete
profiles remove different subsets of eligible pairs; the differing n values reflect this.

## 6. Matched Hash Impact

Definition: elapsed ratio `T_candidate_hash / T_64MiB` on identical (position, node budget, threads, round) successful
pairs. **Ratio > 1 means the candidate hash took longer.** Engine-NPS ratio is `NPS_candidate / NPS_64MiB` on the same
pairs.

| Comparison | Matched pairs n | Elapsed ratio p10 | Elapsed ratio median | Elapsed ratio p90 | NPS ratio p10 | NPS ratio median | NPS ratio p90 |
|---|---|---|---|---|---|---|---|
| h256 vs h64   | 298 | 0.90x | 1.04x | 1.28x | 0.832 | 1.000 | 1.148 |
| h1024 vs h64  | 532 | 1.03x | 1.28x | 2.32x | 0.775 | 0.926 | 1.102 |

- The elapsed quantiles above are reciprocal-direction conversions from an original `T_64/T_X` aggregation; the
  direction shown here (candidate over 64) is the one used for interpretation.
- **Correct interpretation:** with elapsed ratio `T_X/T_64`, the h1024 median of 1.28x means h1024 took about **28%
  LONGER** elapsed time than h64 on its matched sample — **not** faster. (An earlier draft that read this ratio as a
  speedup is corrected here.)
- h256 is near parity at the median (1.04x) with a wide range (0.90x–1.28x).
- h1024 is slower at the median and throughout the central 80% of the matched interval (p10 1.03x, p90 2.32x).
- Profile normalized times in Section 5.1 are consistent with this: h1024 rows are generally slower than their h64
  counterparts at equal thread counts.
- No cause (cache behavior, allocation cost, or otherwise) is asserted here; the timing semantics have not been
  source-verified.

Hashfull (Stockfish hashfull, per mille), median / p90 by hash size: h64 61/477; h256 15/129; h1024 3/31.

## 7. Repetition Performance Stability

- Exact configurations (profile x budget x position) with at least 2 successful rounds: **589/840**.
- Complete 3-round configurations: **564/840**.
- Coefficient of variation (CV = sample standard deviation / mean) across available repetitions:
  - Engine NPS CV: median 0.061, p90 0.152.
  - Normalized wall-time CV: median 0.054, p90 0.128.

Repetition scatter is small for typical configurations, with a heavier upper tail.

## 8. Search-Output Convergence vs the 6.4M Highest-Tested Reference

Matched on (position, threads, hash, round). All metrics compare the lower budget against 6.4M.

- **Top-1 first-move agreement:** both runs' single best first move identical.
- **Top-5 intersection:** size of the intersection of the two top-five first-move sets, out of 5.
- **Top-5 Jaccard:** intersection over union of the two top-five first-move sets.
- **Candidate-order agreement:** relative-order comparisons among candidate first moves present in **both** top-five
  sets; reported as numerator/denominator pairs that were consistent (%).

| Lower budget | Matched jobs | Top-1 agreement | Median top-5 intersection /5 | Median Jaccard | Order agreement (%) |
|---|---|---|---|---|---|
| 100k | 249 | 165/249 (66.3%) | 4 | 0.667 | 1264/1647 (76.7%) |
| 200k | 248 | 168/248 (67.7%) | 4 | 0.667 | 1379/1732 (79.6%) |
| 400k | 245 | 161/245 (65.7%) | 4 | 0.667 | 1396/1729 (80.7%) |
| 800k | 248 | 166/248 (66.9%) | 4 | 0.667 | 1545/1863 (82.9%) |
| 1.6M | 246 | 158/246 (64.2%) | 5 | 1.000 | 1676/2027 (82.7%) |
| 3.2M | 245 | 183/245 (74.7%) | 5 | 1.000 | 1807/2091 (86.4%) |

Top-1 progression is **not monotonic** in the lower budget (64.2% at 1.6M vs 74.7% at 3.2M). At the medians, top-five
set overlap reaches 5/5 for the 1.6M and 3.2M comparisons; that is a median over matched comparisons and must **not**
be read as universal or full convergence.

## 9. Adjacent Doubling Convergence

Matched on (position, threads, hash, round); same metric definitions as Section 8, comparing each budget to the next
doubling. Median wall-time ratio is `T_upper / T_lower` (> 1 means the upper budget took longer).

| Transition | Matched jobs | Top-1 agreement | Median top-5 intersection /5 | Median Jaccard | Median depth gain | Median wall-time ratio |
|---|---|---|---|---|---|---|
| 100k→200k | 243 | 182/243 (74.9%) | 4 | 0.667 | +1 | 1.60x |
| 200k→400k | 243 | 174/243 (71.6%) | 4 | 0.667 | +1 | 1.75x |
| 400k→800k | 242 | 174/242 (71.9%) | 4 | 0.667 | +2 | 1.82x |
| 800k→1.6M | 246 | 159/246 (64.6%) | 4 | 0.667 | +2 | 1.91x |
| 1.6M→3.2M | 244 | 163/244 (66.8%) | 5 | 1.000 | +2 | 1.98x |
| 3.2M→6.4M | 245 | 183/245 (74.7%) | 5 | 1.000 | +2 | 2.01x |

Agreement dips mid-ladder (800k→1.6M, 64.6%) and recovers at the top (3.2M→6.4M, 74.7%). Top-five overlap and Jaccard
reach their best values only for the 1.6M→3.2M and 3.2M→6.4M transitions.

## 10. Cross-Round Search Repeatability

Same configuration, different rounds (fresh engine runs).

- 589 exact configurations with at least 2 successful rounds; **1717** round-pair comparisons.
- **Top-1 pairwise agreement:** 1274/1717 (74.2%).
- **Top-1 unanimous among available rounds:** 374/589 (63.5%). Definition: every available successful round of the
  configuration chose the same top-1 first move; for a 2-round group, unanimous means the two rounds agree.
- **Top-five set Jaccard across round pairs:** median 1.000, mean 0.844. As elsewhere, a median Jaccard of 1.0 means
  **at least half** of the matched round-pair comparisons had identical top-five first-move sets — not every
  comparison, and not universal convergence.
- **Rank-1 score absolute difference** across comparable round pairs (all scores centipawn, side-to-move perspective):
  n=1717, median 3.0 cp, mean 4.7 cp, max 40 cp. This is **rank-1 evaluation variation**; when the top move itself
  changed between rounds, this compares the rank-1 scores of (possibly) different moves, not a same-candidate
  variation.

## 11. Cross-Profile Top-Move Consensus

For each node budget there are 30 position/round groups (10 positions x 3 rounds). For each group, profiles vote on the
top first move.

- **Unanimous:** all available successful profiles chose the same first move.
- **Strict majority:** one first move chosen by >50% of the available successful profiles.
- Every group misses at least one profile (four incomplete profiles); "avg available profiles" is the mean number of
  profiles voting per group, out of 12.

| Budget | Unanimous | Strict majority | Avg available profiles /12 |
|---|---|---|---|
| 100k | 14/30 (46.7%) | 27/30 (90.0%) | 8.6 |
| 200k | 11/30 (36.7%) | 30/30 (100.0%) | 8.7 |
| 400k | 11/30 (36.7%) | 27/30 (90.0%) | 8.5 |
| 800k | 12/30 (40.0%) | 28/30 (93.3%) | 8.8 |
| 1.6M | 9/30 (30.0%) | 25/30 (83.3%) | 8.5 |
| 3.2M | 12/30 (40.0%) | 28/30 (93.3%) | 8.8 |
| 6.4M | 12/30 (40.0%) | 28/30 (93.3%) | 8.8 |

Unanimity is modest everywhere (30.0%–46.7%), while a strict-majority move exists in 83.3%–100% of groups. Missing
profiles weaken profile-consensus comparisons, both by shrinking the voter pool and by making the voter mix
position-dependent.

## 12. Sanity / Data Quality

- Successful rows: 1822; all carried five principal-variation lines; all normalized scores were centipawn with
  side-to-move perspective; no mate scores; no malformed successful records found in the streaming pass.
- `engine_nodes / requested_nodes` ratio: min 1.000000, median 1.0006, p90 1.0034, max 1.0115 — a small overshoot only.
- `engine_nps` divided by (`engine_nodes / wall_clock_seconds`): median 1.082, p90 1.974, max 6.185; 462/1822 rows
  exceed 1.3. This is descriptive evidence that **engine-reported NPS and wall-clock-derived rates are not
  interchangeable**; the timing semantics have not been source-verified, so **no causal explanation (startup, warm-up,
  or otherwise) is offered**. Any use of these measures should verify timing boundaries in the source first.

## 13. Interpretation Limits

- This is **descriptive extraction from an incomplete experiment** (1822/2520 successful, state INCOMPLETE).
- **Profile-driven missingness** limits whole-matrix and profile comparisons; matched samples with explicit
  denominators are shown for this reason.
- **Ten fixed positions** do not establish general workload behavior.
- Results describe **individual engine performance only**; no concurrent-worker throughput or capacity result is
  claimed.
- Results apply to **MultiPV 5 and this machine/engine build only**.
- Search agreement here is **stability relative to the tested runs and the 6.4M highest-tested reference**, not chess
  correctness.
- **No Tool node-budget selection** or recommendation is made by this report.
- Any accepted conclusion must later be **independently corroborated by the supported production package/CLI**
  benchmark; this experiment does not replace that step.
