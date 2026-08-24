# Caro-Kann historical poor-results metrics

**Noncanonical exploratory analysis. No engine was used. No metric is a recommendation, a usefulness decision, or a claim that a move is wrong.**

## Scope and retained population

- Current core only: **229 position nodes** and **863 observed move branches** are retained, including **635 unexpanded move entries** and tiny samples.
- Root cohort: 3358 tracked-corpus games where `Skyrocoster` played Black and the exact opening was `1. e4 c6`.
- Branch actors are distinguished: `553` White-opponent branches and `310` Black-Skyrocoster choices.
- Every node and branch preserves its exact SAN/UCI prefix, replayed six-field FEN, side to move, and engine-ready `position fen` reference. This report does not start an engine.
- Tiny samples are included rather than filtered; uncertainty is visible in every classifiable metric.

## Source and root facts

- Database: `data/database/chess_games.db`; SQLite access was read-only (`mode=ro`). SHA-256: `008cbc735552f15035dec04dd8e22eaa402b6754bd9139aec5dbde30c64fba91`.
- Source tree: `experiments/prototypes/caro-kann-skyrocoster-tree/caro_kann_tree.json`; SHA-256: `e77980dbeb9d5631d3c09d3a945038ca9c1a1f828d26e612c428e1ce345615be`.
- Candidate Black games fully replayed: 6180; root games fully replayed: 3358.
- Root W-D-L/unknown: **1697-91-1570/0**; chess score **51.89%**.
- UTC newest root date: **2026-08-17**. Recency cutoff: **2025-08-17**, inclusive for recent games; earlier dates are older.

### Root time-class summary

| Slice | n | W-D-L / unknown | Raw win | Chess score | 95% heuristic interval |
|---|---:|---:|---:|---:|---:|
| `bullet` | 1346 | 697-28-621/0 | 51.78% | 52.82% | [50.93%, 54.70%] |
| `blitz` | 1463 | 729-49-685/0 | 49.83% | 51.50% | [49.69%, 53.31%] |
| `rapid` | 544 | 269-14-261/0 | 49.45% | 50.74% | [47.77%, 53.70%] |
| `other_or_unknown` | 5 | 2-0-3/0 | 40.00% | 40.00% | [16.82%, 68.73%] |

### Root recency summary

| Slice | n | W-D-L / unknown | Raw win | Chess score | 95% heuristic interval |
|---|---:|---:|---:|---:|---:|
| `recent_12_months` | 1794 | 912-34-848/0 | 50.84% | 51.78% | [50.15%, 53.42%] |
| `older` | 1564 | 785-57-722/0 | 50.19% | 52.01% | [50.26%, 53.76%] |
| `date_unknown` | 0 | 0-0-0/0 | n/a | n/a | n/a |

### Root opponent-strength summary

| Slice | n | W-D-L / unknown | Raw win | Chess score | 95% heuristic interval |
|---|---:|---:|---:|---:|---:|
| `stronger` | 29 | 0-0-29/0 | 0.00% | 0.00% | [0.00%, 6.21%] |
| `similar` | 3325 | 1693-91-1541/0 | 50.92% | 52.29% | [51.08%, 53.48%] |
| `weaker` | 4 | 4-0-0/0 | 100.00% | 100.00% | [67.56%, 100.00%] |
| `unknown` | 0 | 0-0-0/0 | n/a | n/a | n/a |

## Metric definitions and boundaries

- Combined/all-time raw win is `100 * W / (W + D + L)`; chess score is `100 * (W + 0.5 * D) / (W + D + L)`. Unknown outcomes stay outside classifiable denominators.
- The 95% interval is a deterministic **Wilson-style heuristic** on effective half-points: successes `2W + D`, trials `2(W + D + L)`, and `z=1.959963984540054`. It is null when no classifiable outcome exists.
- Root and parent deltas are signed percentage-point differences. Branch sibling comparisons pool all other observed moves at that parent.
- Root reach, root-loss share, and score-point impact are descriptive. Records are nested and overlap, so loss shares and impacts are not additive across the tree.
- Outcomes are descriptive and noncausal. The individual ranking lenses below do not decide whether a move is useful or wrong.
- Strength is based on `white_rating - black_rating`: stronger `>=100`, similar `>-100 and <100`, weaker `<=-100`, unknown if either rating is missing. Time classes are bullet, blitz, rapid, and other/unknown.
- Secondary/long-tail tiers and engine analysis remain future work.

## Top-10 branch views

Each view ranks **all observed move branches with no sample filter**. Null lens metrics are excluded only from that individual view. Ranking uses the exact unrounded metric, then larger relevant slice `n`, complete exact SAN line, move SAN, and move UCI. These are separate tables, not a global recommendation.

### Lowest absolute combined score

Metric: `combined chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 8 | [0.00%, 19.36%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4 f5` | `f5 / f7f5` |
| 2 | 0.00% | 5 | [0.00%, 27.75%] | White opponent | `1. e4 c6 2. a3` | `a3 / a2a3` |
| 3 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 Bg4 4. h3` | `h3 / h2h3` |
| 4 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. c3` | `c3 / c2c3` |
| 5 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Nbd2` | `Nbd2 / b1d2` |
| 6 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. b3` | `b3 / b2b3` |
| 7 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. O-O e6 7. Re1` | `Re1 / f1e1` |
| 8 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 e6` | `e6 / e7e6` |
| 9 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 h6 6. Nxf7 Kxf7 7. Nf3 c5 8. Bd3 Nc6` | `Nc6 / b8c6` |
| 10 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Nxf6+ exf6 6. Be3` | `Be3 / c1e3` |

### Largest negative delta from root

Metric: `delta from root (pp)`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | -51.89 pp | 8 | [0.00%, 19.36%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4 f5` | `f5 / f7f5` |
| 2 | -51.89 pp | 5 | [0.00%, 27.75%] | White opponent | `1. e4 c6 2. a3` | `a3 / a2a3` |
| 3 | -51.89 pp | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 Bg4 4. h3` | `h3 / h2h3` |
| 4 | -51.89 pp | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. c3` | `c3 / c2c3` |
| 5 | -51.89 pp | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Nbd2` | `Nbd2 / b1d2` |
| 6 | -51.89 pp | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. b3` | `b3 / b2b3` |
| 7 | -51.89 pp | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. O-O e6 7. Re1` | `Re1 / f1e1` |
| 8 | -51.89 pp | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 e6` | `e6 / e7e6` |
| 9 | -51.89 pp | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 h6 6. Nxf7 Kxf7 7. Nf3 c5 8. Bd3 Nc6` | `Nc6 / b8c6` |
| 10 | -51.89 pp | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Nxf6+ exf6 6. Be3` | `Be3 / c1e3` |

### Largest negative delta from parent

Metric: `delta from parent (pp)`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | -77.78 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. exd5 cxd5 4. Nc3 Nc6 5. Be3 e5` | `e5 / e7e5` |
| 2 | -71.43 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. Nf3 Bg4 6. Be3 c4` | `c4 / c5c4` |
| 3 | -70.97 pp | 1 | [0.00%, 65.76%] | White opponent | `1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. Nf3 cxd4 6. cxd4 Bg4 7. Be2 e6 8. a3` | `a3 / a2a3` |
| 4 | -68.06 pp | 2 | [0.00%, 48.99%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 Nc6 5. Bb5 a6` | `a6 / a7a6` |
| 5 | -66.67 pp | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 Nc6 5. c3 Bg4 6. Be3` | `Be3 / c1e3` |
| 6 | -66.67 pp | 1 | [0.00%, 65.76%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 c5 4. d4 Nc6 5. Nc3` | `Nc3 / b1c3` |
| 7 | -66.67 pp | 1 | [0.00%, 65.76%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 Nf6 5. d4 Bg4 6. Qe2` | `Qe2 / d1e2` |
| 8 | -66.67 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 cxd4 5. Nxd4 Nc6 6. Be3 Bf5` | `Bf5 / c8f5` |
| 9 | -65.00 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Bb5 c4` | `c4 / c5c4` |
| 10 | -64.42 pp | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. exd5 cxd5 4. Nf3 Nc6 5. c3` | `c3 / c2c3` |

### Largest negative branch-versus-other-siblings gap

Metric: `branch minus other siblings (pp)`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | -100.00 pp | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 h6 6. Nxf7 Kxf7 7. Nf3 c5 8. Bd3 Nc6` | `Nc6 / b8c6` |
| 2 | -100.00 pp | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 c5 4. d4 cxd4 5. Nxd4` | `Nxd4 / f3d4` |
| 3 | -100.00 pp | 2 | [0.00%, 48.99%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 Nc6 5. dxc5 Bg4 6. Nc3 Nxe5` | `Nxe5 / c6e5` |
| 4 | -100.00 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 cxd4 5. Nxd4 Nc6 6. Be3 Bf5` | `Bf5 / c8f5` |
| 5 | -87.50 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. exd5 cxd5 4. Nc3 Nc6 5. Be3 e5` | `e5 / e7e5` |
| 6 | -83.33 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. Nf3 Bg4 6. Be3 c4` | `c4 / c5c4` |
| 7 | -80.00 pp | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 Nc6 5. c3 Bg4 6. Be3` | `Be3 / c1e3` |
| 8 | -75.00 pp | 4 | [7.15%, 59.07%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. e5 c5 4. d4 Nc6 5. c3 Bg4` | `Bg4 / c8g4` |
| 9 | -75.00 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. Be2 c5 5. h3 Bh5` | `Bh5 / g4h5` |
| 10 | -75.00 pp | 1 | [0.00%, 65.76%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 Nf6 5. d4 Bg4 6. Bg5 Bxf3` | `Bxf3 / g4f3` |

### Largest nonnegative high-volume root-baseline shortfall

Metric: `below-baseline shortfall (score-points)`; direction: **descending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 13.93 score-points | 631 | [46.93%, 52.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5` | `exd5 / e4d5` |
| 2 | 13.89 score-points | 629 | [46.92%, 52.44%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5` | `cxd5 / c6d5` |
| 3 | 10.92 score-points | 75 | [30.00%, 45.30%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Bb5+` | `Bb5+ / f1b5` |
| 4 | 10.68 score-points | 221 | [42.45%, 51.72%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3` | `Nc3 / b1c3` |
| 5 | 10.57 score-points | 215 | [42.31%, 51.70%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4` | `dxe4 / d5e4` |
| 6 | 9.73 score-points | 65 | [29.11%, 45.48%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Bb5+ Nc6` | `Nc6 / b8c6` |
| 7 | 8.90 score-points | 206 | [42.80%, 52.40%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4` | `Nxe4 / c3e4` |
| 8 | 8.19 score-points | 195 | [42.78%, 52.65%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6` | `Nf6 / g8f6` |
| 9 | 7.59 score-points | 31 | [17.88%, 39.59%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4` | `d4 / d5d4` |
| 10 | 6.61 score-points | 85 | [36.87%, 51.63%] | White opponent | `1. e4 c6 2. Qf3` | `Qf3 / d1f3` |

### Lowest bullet score

Metric: `bullet chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 5 | [0.00%, 27.75%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bf4` | `Bf4 / c1f4` |
| 2 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Bb5+ Nc6 5. O-O Bg4 6. d4` | `d4 / d2d4` |
| 3 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4` | `Ne4 / c3e4` |
| 4 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. Bxc6+` | `Bxc6+ / b5c6` |
| 5 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. Bxc6+ bxc6` | `bxc6 / b7c6` |
| 6 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. f3` | `f3 / f2f3` |
| 7 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. Nf3 cxd4` | `cxd4 / c5d4` |
| 8 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d6` | `d6 / d7d6` |
| 9 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Nbd2` | `Nbd2 / b1d2` |
| 10 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c4` | `c4 / c2c4` |

### Lowest blitz score

Metric: `blitz chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 6 | [0.00%, 24.25%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4 f5` | `f5 / f7f5` |
| 2 | 0.00% | 6 | [0.00%, 24.25%] | White opponent | `1. e4 c6 2. d4 d5 3. e5 c5 4. Bb5+` | `Bb5+ / f1b5` |
| 3 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Be3` | `Be3 / c1e3` |
| 4 | 0.00% | 4 | [0.00%, 32.44%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. O-O Nf6` | `Nf6 / g8f6` |
| 5 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. a3` | `a3 / a2a3` |
| 6 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 dxe4 4. Ng5` | `Ng5 / f3g5` |
| 7 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Qe2` | `Qe2 / d1e2` |
| 8 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Ng5` | `Ng5 / f3g5` |
| 9 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. Be2 c5 5. O-O` | `O-O / e1g1` |
| 10 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. Be2 c5 5. h3` | `h3 / h2h3` |

### Lowest rapid score

Metric: `rapid chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. dxc5` | `dxc5 / d4c5` |
| 2 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 Bg4 4. h3` | `h3 / h2h3` |
| 3 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. d4` | `d4 / d2d4` |
| 4 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5` | `Ng5 / e4g5` |
| 5 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. g3` | `g3 / g2g3` |
| 6 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. Be2` | `Be2 / f1e2` |
| 7 | 0.00% | 2 | [0.00%, 48.99%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. Be2 Nc6` | `Nc6 / b8c6` |
| 8 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. h3 Bxf3 5. Qxf3 e6 6. d4` | `d4 / d2d4` |
| 9 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Nc3 Bg4 6. Bb5` | `Bb5 / f1b5` |
| 10 | 0.00% | 2 | [0.00%, 48.99%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Nc3 Bg4 6. Bb5 e6` | `e6 / e7e6` |

### Lowest recent-12-month score

Metric: `recent-12-month chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 5 | [0.00%, 27.75%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4` | `Ne4 / c3e4` |
| 2 | 0.00% | 4 | [0.00%, 32.44%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4 f5` | `f5 / f7f5` |
| 3 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. f3` | `f3 / f2f3` |
| 4 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. exd5 cxd5 4. Nf3 Nc6 5. c3` | `c3 / c2c3` |
| 5 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d6` | `d6 / d7d6` |
| 6 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Nbd2` | `Nbd2 / b1d2` |
| 7 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c4` | `c4 / c2c4` |
| 8 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 c5 4. Bb5+` | `Bb5+ / f1b5` |
| 9 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 c5 4. d4 Bg4 5. c3` | `c3 / c2c3` |
| 10 | 0.00% | 2 | [0.00%, 48.99%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Bb5+ Nc6 5. O-O Nf6` | `Nf6 / g8f6` |

### Lowest older score

Metric: `older chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 Bg4 4. h3` | `h3 / h2h3` |
| 2 | 0.00% | 4 | [0.00%, 32.44%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4 f5` | `f5 / f7f5` |
| 3 | 0.00% | 4 | [0.00%, 32.44%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. O-O Nf6` | `Nf6 / g8f6` |
| 4 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. c3` | `c3 / c2c3` |
| 5 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. b3` | `b3 / b2b3` |
| 6 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. a3` | `a3 / a2a3` |
| 7 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 e6` | `e6 / e7e6` |
| 8 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. Bb5 Bf5` | `Bf5 / c8f5` |
| 9 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. Be2 c5 5. O-O` | `O-O / e1g1` |
| 10 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. Nc3` | `Nc3 / b1c3` |

### Lowest stronger-opponent score

Metric: `stronger-opponent chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 11 | [0.00%, 14.87%] | White opponent | `1. e4 c6 2. Nf3` | `Nf3 / g1f3` |
| 2 | 0.00% | 11 | [0.00%, 14.87%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5` | `d5 / d7d5` |
| 3 | 0.00% | 7 | [0.00%, 21.53%] | White opponent | `1. e4 c6 2. Bc4` | `Bc4 / f1c4` |
| 4 | 0.00% | 6 | [0.00%, 24.25%] | White opponent | `1. e4 c6 2. d4` | `d4 / d2d4` |
| 5 | 0.00% | 6 | [0.00%, 24.25%] | Black Skyrocoster | `1. e4 c6 2. d4 d5` | `d5 / d7d5` |
| 6 | 0.00% | 5 | [0.00%, 27.75%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5` | `exd5 / e4d5` |
| 7 | 0.00% | 5 | [0.00%, 27.75%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5` | `cxd5 / c6d5` |
| 8 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4` | `d4 / d2d4` |
| 9 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5` | `e5 / e4e5` |
| 10 | 0.00% | 2 | [0.00%, 48.99%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3` | `Nc3 / b1c3` |

### Lowest similar-opponent score

Metric: `similar-opponent chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 0.00% | 8 | [0.00%, 19.36%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Nc3 d4 5. Ne4 f5` | `f5 / f7f5` |
| 2 | 0.00% | 5 | [0.00%, 27.75%] | White opponent | `1. e4 c6 2. a3` | `a3 / a2a3` |
| 3 | 0.00% | 4 | [0.00%, 32.44%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 Bg4 4. h3` | `h3 / h2h3` |
| 4 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. c3` | `c3 / c2c3` |
| 5 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. e5 Bg4 4. d4 c5 5. c3 Nc6 6. Nbd2` | `Nbd2 / b1d2` |
| 6 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. b3` | `b3 / b2b3` |
| 7 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. O-O e6 7. Re1` | `Re1 / f1e1` |
| 8 | 0.00% | 3 | [0.00%, 39.03%] | Black Skyrocoster | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Ng5 e6` | `e6 / e7e6` |
| 9 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Nxf6+ exf6 6. Be3` | `Be3 / c1e3` |
| 10 | 0.00% | 3 | [0.00%, 39.03%] | White opponent | `1. e4 c6 2. d4 d5 3. Nc3 dxe4 4. f3` | `f3 / f2f3` |

### Lowest weaker-opponent score

Metric: `weaker-opponent chess score %`; direction: **ascending**; sample filter: **none**.

| Rank | Metric | n | 95% heuristic interval | Actor | Complete exact SAN line | Move SAN / UCI |
|---:|---:|---:|---|---|---|---|
| 1 | 100.00% | 2 | [51.01%, 100.00%] | White opponent | `1. e4 c6 2. Nc3` | `Nc3 / b1c3` |
| 2 | 100.00% | 2 | [51.01%, 100.00%] | White opponent | `1. e4 c6 2. Nf3` | `Nf3 / g1f3` |
| 3 | 100.00% | 2 | [51.01%, 100.00%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5` | `d5 / d7d5` |
| 4 | 100.00% | 1 | [34.24%, 100.00%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3` | `Nc3 / b1c3` |
| 5 | 100.00% | 1 | [34.24%, 100.00%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. Nc3 dxe4` | `dxe4 / d5e4` |
| 6 | 100.00% | 1 | [34.24%, 100.00%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 dxe4 4. Nxe4` | `Nxe4 / c3e4` |
| 7 | 100.00% | 1 | [34.24%, 100.00%] | Black Skyrocoster | `1. e4 c6 2. Nf3 d5 3. Nc3 dxe4 4. Nxe4 Nf6` | `Nf6 / g8f6` |
| 8 | 100.00% | 1 | [34.24%, 100.00%] | White opponent | `1. e4 c6 2. Nf3 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Qe2` | `Qe2 / d1e2` |
| 9 | 100.00% | 1 | [34.24%, 100.00%] | White opponent | `1. e4 c6 2. Nf3 d5 3. d4` | `d4 / d2d4` |

## Limitations

This is current-core historical cohort reporting only. It does not establish causality, move quality, usefulness, or a training recommendation. Nested records overlap, the intervals are heuristic, and engine analysis plus secondary/long-tail coverage are intentionally future work.
