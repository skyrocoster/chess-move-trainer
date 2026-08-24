# Caro-Kann history tree (Skyrocoster as Black)

Noncanonical exploration. This directory is **read-only** toward the rest of the repository: it never
writes to the database, application source, tests, plans, or other experiments, and it **never runs
Stockfish** or any engine. The JSON it produces only prepares positions for later engine work.

## Purpose

Answer descriptively: in tracked-corpus games where `Skyrocoster` (matched case-insensitively) played
Black and play began exactly `1. e4 c6`, what actually happened next? The result is a deterministic
move-sequence tree plus a machine-readable JSON file.

## Data scope

- Database: `data/database/chess_games.db` (opened with a read-only SQLite URI, `mode=ro`).
- Corpus/player identity is resolved from metadata (`players` joined to `corpus`), case-insensitively;
  no UUID is embedded in the script.
- Cohort: corpus games with `rules = 'chess'`, the resolved player as Black (and not also White),
  whose plies 1-2 are exactly SAN `e4`, `c6` from the standard initial position.
- Every candidate game is replayed from `chess.Board()` before use. Validation requires adjacent
  same-game ply order from ply 0, canonical SAN, matching stored UCI, rule-aware state fields
  (placement/side/castling/en passant), and halfmove/fullmove clocks; any mismatch aborts the run.
  Each game contributes exactly one path, so duplicate games or prefixes cannot inflate counts.
- Exact move prefixes are preserved: transposing orders stay separate lines even at identical boards.

## Branching and stopping rules

1. Both White and Black moves branch.
2. A node expands children only if it has **>= 20 games** AND at least one single immediate move with a
   local share **strictly above 10%** (exact integer test: `10 * count > games_with_next`).
3. Qualifying edges become child nodes; every immediate move that is not expanded is retained in a
   visible `other moves` aggregate. This includes all moves at a stopped node. The aggregate preserves
   move count, game count, both percentages, and every constituent SAN/UCI/count entry (ordered by
   frequency, then SAN). The JSON `other_moves` field is `null` when there are no unexpanded moves.
4. No fixed depth limit. Branches stop only for machine-readable reasons:
   - `below_min_support_20_games` - position reached by fewer than 20 games (exactly 20 still allows
     expansion). A qualifying edge may create such a small child; the child is represented and stopped.
   - `no_individual_move_above_10pct_local` - at least 20 games but dispersed replies.
   - `no_recorded_next_move` - data exhaustion; nobody at this position has a recorded next move.
5. Games ending at a node stay in that node's outcomes and are counted as "ended or none recorded";
   they are excluded only from the denominator of next-move percentages.
6. Outcomes are whole-game results from Skyrocoster's Black perspective (win / draw / loss /
   unclassified). They describe what happened, not move quality.

## Percentages

- `% at this position` (`local_pct`) = edge count / games with a recorded immediate next move there.
- `% of all root games` (`cumulative_pct`) = edge count / total root-cohort games.
- `raw_win_pct` = wins / classifiable games; `chess_score_pct` = (wins + 0.5*draws) / classifiable
  games. Unclassified results are reported separately, never forced into W/D/L.
- All percentages are rounded to 2 decimals; raw integer counts are authoritative.

## Outputs and run command

Running the script prints a readable indented tree to stdout and writes deterministic JSON into this
directory (default `caro_kann_tree.json`; optional simple override `--output PATH`).

PowerShell from the repository root:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-skyrocoster-tree\caro_kann_tree.py
```

Optional read-only inspection flags: `--database PATH`, `--username NAME`, `--output PATH`.

The core-only analysis reads the authoritative tree JSON without using the database or an engine:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-skyrocoster-tree\caro_kann_core_analysis.py
```

It writes the deterministic structured funnel and stopped-line analysis to
`caro_kann_core_analysis.json` and the readable report to `caro_kann_core_analysis.md`.

The noncanonical historical metrics analysis replays the approved cohort read-only and retains every
position node plus every observed immediate move branch, including tiny and unexpanded branches:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-skyrocoster-tree\caro_kann_historical_metrics.py
```

It writes `caro_kann_historical_metrics.json` and `caro_kann_historical_metrics.md` in this directory.

JSON contains: schema marker (`caro-kann-history-tree/v1`); generated-from metadata without unstable
timestamps; thresholds; percentage definitions; root totals; per-node stable IDs (`n` + first 16 hex
of SHA-256 over the U+001F-joined SAN prefix), full ordered move list in SAN and UCI, six-field FEN,
side to move, counts/outcomes/percentages, `arrived_via` edge stats, `observed_next_moves`,
`children`, grouped `other_moves` details, expansion marker, and stop reason; plus summary stats.

**Engine-ready boundary:** any real node's six-field `fen` can be fed straight to Stockfish later
(`position fen <fen>`). En-passant uses the traditional FEN convention (`python-chess`
`en_passant="fen"`), which engines accept.

## Status

Exploration only - noncanonical until explicitly adopted. Repeated runs on unchanged data produce
byte-identical output (deterministic ordering by frequency then SAN; fixed JSON key order; no
timestamps). No engine process is started anywhere in this experiment.
