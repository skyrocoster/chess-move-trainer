# Caro-Kann core coverage analysis

This is deterministic, noncanonical exploratory analysis of the authoritative `caro_kann_tree.json`.
It summarizes the current **core** tier only; it does not claim to cover the whole repertoire.

## Scope and interpretation

The first post-root split keeps 2,346 games, or 69.86% of all 3,358 root games. That is the roughly 70% current core at the first post-root split, not total repertoire coverage.

`% at this position` is a local percentage on one exact branch edge: edge games divided by the parent position's games with a recorded next move. `% of all root games` divides by the full 3,358-game root cohort. Funnel rows intentionally do not invent an aggregate local percentage for a whole ply.

The funnel counts disjoint real source nodes at each represented ply. Continuing games are qualifying expanded child nodes. The remainder is assigned once: expanded grouped `other_moves` are less-common moves; expanded games without a next move and stopped no-next nodes are ended/no-next; a stopped node's full games go into its named stop bucket.

## Coverage funnel

| Ply | Represented | Root coverage | Continuing | less-common moves | ended/no-next | below-20 stop | Reconciles |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 3,358 | 100.00% | 2,346 | 1,009 | 3 | 0 | yes |
| 3 | 2,346 | 69.86% | 2,338 | 8 | 0 | 0 | yes |
| 4 | 2,338 | 69.62% | 2,095 | 241 | 2 | 0 | yes |
| 5 | 2,095 | 62.39% | 2,082 | 12 | 1 | 0 | yes |
| 6 | 2,082 | 62.00% | 1,792 | 252 | 2 | 36 | yes |
| 7 | 1,792 | 53.37% | 1,712 | 72 | 0 | 8 | yes |
| 8 | 1,712 | 50.98% | 1,309 | 347 | 2 | 54 | yes |
| 9 | 1,309 | 38.98% | 950 | 33 | 0 | 326 | yes |
| 10 | 950 | 28.29% | 691 | 140 | 0 | 119 | yes |
| 11 | 691 | 20.58% | 219 | 5 | 0 | 467 | yes |
| 12 | 219 | 6.52% | 166 | 25 | 0 | 28 | yes |
| 13 | 166 | 4.94% | 83 | 4 | 0 | 79 | yes |
| 14 | 83 | 2.47% | 69 | 14 | 0 | 0 | yes |
| 15 | 69 | 2.05% | 17 | 4 | 0 | 48 | yes |
| 16 | 17 | 0.51% | 0 | 0 | 0 | 17 | yes |

The below-20 rule is applied when a qualifying child is reached: that child appears in the next ply's represented coverage, then its full games are counted as below-20 stop attrition. All 123 stopped exact lines remain in the JSON output.

## Top 10 stopped exact lines

These lines are ranked only by games descending, then complete-line order. W-D-L, raw win, and chess score are historical context only; they do not imply causation or affect rank.

| Rank | Games | Root coverage | W-D-L / unknown | Raw win | Chess score | Stop reason | Complete line |
| ---: | ---: | ---: | :--- | ---: | ---: | :--- | :--- |
| 1 | 19 | 0.57% | 8-0-11 / 0 | 42.11% | 42.11% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. Bb5+ Nc6 5. O-O Bg4 |
| 2 | 19 | 0.57% | 6-1-12 / 0 | 31.58% | 34.21% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Bb5 Bg4 6. O-O e6 |
| 3 | 19 | 0.57% | 11-0-8 / 0 | 57.89% | 57.89% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nc6 5. Nc3 Bg4 6. h3 |
| 4 | 19 | 0.57% | 9-1-9 / 0 | 47.37% | 50.00% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. exd5 cxd5 4. d4 Nf6 5. Bb5+ |
| 5 | 19 | 0.57% | 10-0-9 / 0 | 52.63% | 52.63% | `below_min_support_20_games` | 1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. Nf3 Bg4 6. Be2 |
| 6 | 19 | 0.57% | 9-0-10 / 0 | 47.37% | 47.37% | `below_min_support_20_games` | 1. e4 c6 2. d4 d5 3. e5 c5 4. dxc5 Nc6 5. Bb5 |
| 7 | 19 | 0.57% | 12-0-7 / 0 | 63.16% | 63.16% | `below_min_support_20_games` | 1. e4 c6 2. d4 d5 3. exd5 cxd5 4. Nc3 Nc6 5. Nf3 Bg4 6. Be2 |
| 8 | 18 | 0.54% | 7-1-10 / 0 | 38.89% | 41.67% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. Nc3 Bg4 |
| 9 | 18 | 0.54% | 11-1-6 / 0 | 61.11% | 63.89% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. Nc3 d4 |
| 10 | 18 | 0.54% | 9-0-9 / 0 | 50.00% | 50.00% | `below_min_support_20_games` | 1. e4 c6 2. Nf3 d5 3. Nc3 dxe4 4. Nxe4 Nf6 5. Nxf6+ exf6 6. Bc4 |

The JSON contains all 123 stopped exact lines, with complete SAN/UCI prefixes, node IDs, six-field FENs, side to move, arrival context, counts, root percentages, outcomes, and stop reasons.

## Output and limits

- Source: `caro_kann_tree.json` (`caro-kann-history-tree/v1`); root denominator: 3,358 games.
- Tier marker: `core`. Future core/secondary/long-tail tier intent is recorded, but only core is implemented here.
- No database was read and no engine was run. Positions are references for possible later engine work only.
- The structured output contains branch-local percentages only on exact branch/edge records; funnel percentages are root-cohort coverage.
