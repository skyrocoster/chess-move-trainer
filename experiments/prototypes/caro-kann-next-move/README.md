# Caro-Kann next-move experiment

This small, noncanonical experiment follows common moves in the tracked chess corpus. It uses games where
`Skyrocoster` played Black and starts from the chosen line:

`1. e4 c6 2. d4 d5`

At each step it chooses White's most common opponent move, then Skyrocoster's most common Black reply. A
Black reply is continued only when it has at least 90% of replies with an immediate move. There is no
move-number cap; the first reply below 90% stops the experiment.

The current stopping line is:

`1. e4 c6 2. d4 d5 3. e5 c5 4. c3 Nc6 5. Nf3`

Black's replies there were:

- `cxd4`: 82
- `Bg4`: 45
- `Qa5`: 2
- `e6`: 1

The leading reply was `cxd4` at 82/130 (63.08%), so it was recorded as a divergence and not continued.

At that stopping position the experiment also compares the top five Stockfish 18 Black moves with every
Black move Skyrocoster actually played. Stockfish uses 200,000 nodes, MultiPV 5, one thread, 128 MiB hash,
and WDL enabled; scores and WDL are shown from Black's perspective. Personal results show the full range
with no sample cutoff: games, W-D-L, raw win percentage, and chess score percentage. These are whole-game
outcomes, not proof that a move caused a result. Replies from one or two games are marked as tiny samples.

Run from the repository root:

```text
.venv\Scripts\python.exe experiments\prototypes\caro-kann-next-move\prototype.py
```

The experiment reads `data/database/chess_games.db` and
`data/stockfish/stockfish-windows-x86-64-avx2.exe` in read-only mode. It does not write engine results, change
the application or database, and remains noncanonical.
