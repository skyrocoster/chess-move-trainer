# Skyrocoster Black replies versus Stockfish

This is a standalone, noncanonical comparison for one exact line:

`1. e4 c6 2. Nc3 d5 3. exd5 cxd5 4. d4 Nc6 5. Nf3`

It resolves `Skyrocoster` case-insensitively through the tracked corpus, keeps only games in which that
player was Black, and replays each PGN from the standard initial position with `python-chess`. A game is
matched only when the complete SAN prefix is adjacent in that same game and reaches the target FEN. Replies
are counted once per matched game; position-only transpositions and duplicate occurrences are not used.

The CLI prints every personal Black reply with whole-game W-D-L from Black's perspective, raw win percentage,
chess score, and a tiny-sample flag. It then performs a fresh Stockfish 18 exact-position search with 200,000
nodes, MultiPV 5, Threads 1, Hash 128 MiB, and WDL enabled. Engine scores and WDL are normalized from Black's
perspective. No engine result is written to the database, cache, or an output file.

Run from the repository root:

```text
.venv\Scripts\python.exe experiments\prototypes\skyrocoster-black-replies-stockfish\compare.py
```

Optional `--database`, `--engine`, and `--username` arguments are available for read-only inspection. The
experiment is noncanonical and does not edit application source or existing experiments.
