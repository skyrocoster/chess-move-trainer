# Opening Position Pattern Discovery - Grilling Record

**Recorded:** 2026-08-18  
**Status:** Confirmed discovery and prototype evidence; the position-corpus and occurrence-model branches
are settled by MP-06, while the repertoire, population, and engine branches remain open for MP-07 and
later grilling  
**Implementation authority:** None  
**Relationship:** Detailed input for later repertoire, position-corpus, and engine-analysis grilling; the
position-corpus branch fed MP-06 (see the [MP-06 grilling record](../grilling-docs/mp06-validated-fen-corpus.md)
and the archived [Validated FEN corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md)),
and the remaining branches feed MP-07 and later milestones

## Purpose

This record preserves the discovery discussion about finding patterns in captured chess games, with the
conversation ultimately narrowing to repeated opening positions and a Caro-Kann repertoire workflow. It records
the decisions, reasons, source research, prototype locations, observed results, failures, and open branches needed
before focused planning.

This is not a product specification or authorization to add dependencies, schemas, downloads, APIs, engine
packaging, or UI. The prototypes are disposable evidence under `Scratch/prototypes/`. Any production use still
requires the applicable milestone grilling and route assessment.

## Original request and direction change

The initial request was broad discovery: scout the existing chess game data; consider useful groupings and
comparisons; determine how repeated FENs could be found; and then use Python prototypes to learn from the data.
Installing additional Python libraries through a direct order was acceptable.

The first proposed analysis sequence was game-level patterns followed by position-level reconstruction. The user
selected both, staged, and selected a combined player-centric and color-aware perspective. A broad game-level
profile was briefly considered, but the user then clarified that the immediate discussion should concern the
theory of finding patterns in positions rather than general game summaries.

The position discussion narrowed again from arbitrary similarity to exact legal positions, then to a concrete
opening-learning workflow:

1. The user plays the Caro-Kann as Black.
2. The user creates a move graph with one manually preferred move at each of their decision positions.
3. Captured games reveal positions where the user did not play the preferred move.
4. Engine evidence reveals moves that materially worsened the user's position.
5. Frequently reached positions without a preferred move reveal repertoire coverage gaps.
6. Population evidence from realistic online games and engine evidence propose candidates, but neither source
   automatically sets the preferred repertoire move.

## Repository data scouted

### Primary captured-game data

- `data/database/chess_games.db` is the current normalized SQLite store. It was approximately 44 MB and contained
  12,369 games, 11,750 players, and 31 monthly fetch-state rows when scouted.
- `data/chess-com/raw/games/` contains 31 monthly Chess.com JSON files covering 2024-02 through 2026-08, plus the
  archives response under `data/chess-com/raw/archives/`.
- `scripts/chess_com/fetch_games.py` owns fetching and normalization.
- `scripts/scout_db_query.py` demonstrates read-only SQLite access.
- No backend application feature currently consumes this chess data.

The database `games` rows include UUID, URL, PGN, time control, end time, rated flag, TCN, initial setup, final FEN,
time class, rules, opening URL, player references, ratings, results, Chess.com accuracy values where available,
tournament/match references, year, and month. Move-by-move positions are not stored separately; they must be
replayed from PGN.

### Scale and useful dimensions

- Date coverage: 31 months, 2024-02 through 2026-08.
- Time classes: 4,612 blitz, 4,217 bullet, 3,422 rapid, and 118 daily games.
- Time controls: 16 distinct values, led by `180+2`, `600`, `120+1`, `60+1`, and `300`.
- Every game had a non-empty final FEN and PGN headers including `CurrentPosition` and `Termination`.
- There were 12,320 distinct stored final-FEN strings among 12,369 games. This is not a useful estimate of
  repeated intermediate positions because only each game's final FEN is stored.
- Opening values in the database are Chess.com opening URLs; ECO codes remain in PGN headers rather than a
  dedicated database column.
- Chess.com accuracy was present for only 1,528 games.
- Tournament and match columns had no populated rows.

Potential game-level comparisons identified during scouting included result, rating and rating gap, color,
opponent, time control/class, month/date, termination, opening, and accuracy. These remain valid future discovery
dimensions but were deliberately deprioritized in this conversation.

### Current dependency facts

- The repository targets Python 3.12.
- Neither `python-chess` nor pandas is in `requirements.txt` or the main `.venv`.
- The prototypes use an isolated environment at `Scratch/prototypes/.venv/`, containing `python-chess` 1.11.2.
- No Stockfish or other UCI engine was installed in the repository, PATH, or checked common Windows locations
  before the Stockfish prototype downloaded its isolated official binary.

## Exact-position identity

### Settled decisions

- Exact positions, not initially structural or situational similarity, are the first pattern layer.
- `python-chess` should own parsing and chess-rule semantics.
- Repeated-position identity is rule-aware state excluding halfmove and fullmove counters.
- The identity includes piece placement, side to move, castling rights, and legally relevant en-passant state.
- Analysis concerns repetition across different games, not repetition cycles within one game.
- Within-game duplicate occurrences are rare in openings and can be ignored for the initial frequency analysis;
  straightforward occurrence counts are acceptable.
- Every ply is retained, including ply zero, because common opening positions are the intended signal.
- The universal starting position is retained but displayed separately from ranked opening positions.

The conversation initially considered storing both full-FEN and normalized identities. The user instead selected
the library-derived rule-aware identity as the operative repetition key. Full source FEN remains useful evidence,
but it is not the grouping key.

### Why position identity matters

A literal six-field FEN comparison separates otherwise equivalent positions because its move counters differ.
Conversely, grouping by piece placement alone incorrectly combines states with different sides to move, castling
rights, or legal en-passant moves. A normalized four-field EPD-style key produced from a legal `python-chess`
board provides the intended identity for opening transpositions and repertoire decisions.

## Repertoire graph model

### Settled graph decisions

- The underlying repertoire is keyed by normalized legal position, not by move-order path.
- Different move orders that reach the same position share one preferred move.
- The conceptual structure is therefore a directed position graph, even if a future interface displays familiar
  move trees.
- The first repertoire scope is the Caro-Kann.
- The graph includes the user's Black decision nodes and White's moves as connecting branches.
- Preferred moves are assigned only at the user's Black decision nodes.
- A game belongs to the Caro-Kann graph when its replay reaches the canonical position after `1.e4 c6`, rather
  than because an external opening label says Caro-Kann.

### Action queues

The clarified workflow produces three distinct queues:

1. **Repertoire miss:** a preferred move exists for a reached position, but the user played another move.
2. **Harmful move:** the user's played move caused a sufficiently negative objective evaluation change.
3. **Coverage gap:** no preferred move exists for a position that occurs frequently enough to deserve a learned
   response.

The earlier idea of detecting generic forgetting was refined into this explicit workflow. Regression, inconsistent
recall, and repeated misses may still become useful labels later, but the repertoire comparison above is the more
direct source of truth.

## Opening names and transpositions

### Source decision

The selected opening-name source is
[`lichess-org/chess-openings`](https://github.com/lichess-org/chess-openings). It is a CC0/public-domain dataset
with ECO code, English name, and PGN move sequence. Its generated distribution can also carry UCI and EPD values.
The source is maintained for transposition-aware classification and recommends finding the deepest named position
encountered in a line.

Alternatives researched but not selected were:

- `pgn-extract`'s approximately 2,014-entry `eco.pgn`, which is sequence-oriented and carries GPL/distribution
  considerations;
- `python-chess` Polyglot support, which maps positions to weighted moves but contains no names or ECO codes; and
- the Lichess Opening Explorer API, which is useful for population statistics but is not the local name dataset.

### Programmatic naming decision

Game replay proceeds forward. At each ply, the program checks whether the normalized position has an exact Lichess
opening-name match and retains the most recent match. An unnamed later position is labeled with the deepest named
ancestor plus the moves since that ancestor, for example:

`B12 Caro-Kann Defense: Advance Variation - after 3...Bf5`

This preserves standard terminology without pretending every decision position has its own canonical name.

## Prototype 1: opening-name EPD lookup

### Location and purpose

- Script: `Scratch/prototypes/proto-chess-openings-epd-lookup-2026-08-18.py`
- Cached data: `Scratch/prototypes/proto-chess-openings-epd-lookup-2026-08-18.data/`
- Environment: `Scratch/prototypes/.venv/`

This disposable prototype exists to prove that the CC0 Lichess opening data can be downloaded, replayed with
`python-chess`, indexed by normalized position, used to name Caro-Kann positions, and remain stable across
transpositions. It does not read the user's game database.

### Observed evidence

- Five raw TSV files were downloaded with schema `eco | name | pgn`.
- Row counts were A: 817, B: 772, C: 1,250, D: 614, and E: 357, for 3,810 total rows.
- All 3,810 rows replayed successfully.
- The prototype produced 3,810 distinct EPD keys and observed no duplicate position keys in the current source.
- Base Caro-Kann, `2.d4 d5`, Advance `3.e5`, Exchange, Panov, and Classical test positions resolved.
- The position after Advance `3...Bf5` had no exact name, demonstrating the need for deepest-ancestor naming.
- Two different Panov move orders produced the same EPD and the same B14 opening result.
- A Classical position reached with `3.Nc3` matched a source line written with `3.Nd2`, providing another concrete
  transposition example.

Representative command:

```bash
Scratch/prototypes/.venv/Scripts/python.exe Scratch/prototypes/proto-chess-openings-epd-lookup-2026-08-18.py
```

## Comparing continuations at repeated positions

### Settled analytical output

For every recurring exact position, the first useful comparison combines:

- continuation move frequency;
- subsequent game result;
- aggregate result first; and
- optional one-factor comparisons for rating gap, time control, color, and period.

The analysis should be descriptive with uncertainty rather than formal causal hypothesis testing. Sample sizes and
confidence intervals should be visible. The exact treatment of small samples was left undecided because tree and
graph presentation has not yet been designed. Options discussed were hiding low-support moves, showing everything
with warnings, or assigning anecdotal/emerging/established support tiers.

## Evidence for candidate moves

### Manual authority

The user manually owns every preferred repertoire move. Neither engine-best moves nor population popularity may
automatically become repertoire choices.

Candidate generation uses layered evidence:

1. Find moves commonly chosen from the position by a relevant population.
2. Add objectively strong engine alternatives that popularity alone may omit.
3. Display frequency, population outcomes, engine evaluation, and evaluation loss as separate evidence.
4. Require the user to explicitly select the preferred move.

A single weighted score was rejected as the initial model because it would hide trade-offs and embed arbitrary
weights. Population outcomes are observational and confounded; engine scores represent objective search under
specific settings, not personal repertoire suitability.

### Harmful-move definition

Both of these values are needed:

- resulting position evaluation after the user's move; and
- evaluation loss compared with the engine's best candidate from the position before the move.

This distinction matters because a move can leave the player worse without causing the disadvantage, or lose
substantial value while the resulting position remains favorable. The threshold that makes a move actionable is
not yet settled.

## Freely reusable population data

### Sources researched

The following current source terms were checked:

- **Lichess standard rated games:** more than eight billion games, monthly `.pgn.zst` archives, CC0, ratings and
  title tags included. This is unrestricted but extremely large and mostly non-master play.
- **Lichess broadcast games:** approximately 1.18 million over-the-board games since 2020, commonly with titles,
  FIDE IDs, ratings, and engine evaluations, licensed CC BY-SA 4.0.
- **TWIC:** useful master games but explicitly personal-use only and all rights reserved.
- **Chess.com Published-Data API:** publicly accessible, but no verified open data-reuse license.
- **FIDE rating lists:** publicly downloadable but no verified open license and no game moves.

The user preferred the Lichess standard population because it better represents realistic, less-prepared opponents
playing each other than an exclusively elite master corpus.

### Bulk archive limitation

Lichess does not provide a global API that returns raw games filtered by rating, opening, speed, or date. Standard
game downloads are monthly archives; a recent month was roughly 29 GB compressed. Lichess documents streaming or
partial decompression, but filtering remains client-side and a partial download only yields a file prefix.

The selected acquisition sequence is therefore:

1. Query aggregate Opening Explorer statistics first.
2. Acquire selected raw games later only when deeper evidence is necessary.

## Lichess Opening Explorer

### API role

The Explorer can filter aggregate Lichess game statistics by position or move sequence, rating bands, speeds, and
month range. It returns move frequency, average rating, White/draw/Black counts, optional monthly history, and a
small number of game references. It does not return the underlying filtered game corpus.

Explorer data ranks candidate moves but cannot set preferred moves. Its evidence should be combined with engine
analysis and shown separately.

### Authentication discovery and credential handling

The current endpoint is `https://explorer.lichess.org/lichess`. Anonymous calls returned HTTP 401; the legacy
`explorer.lichess.ovh` host is no longer the usable endpoint. A narrowly scoped Lichess token was selected for the
prototype.

One token was accidentally pasted into a shell command during setup. It was treated as exposed and revoked. A
replacement was stored in the Windows user environment as `LICHESS_TOKEN`; its value is not recorded here or in
the repository. Because the running tool process predated the environment change, the authenticated run read the
Windows User environment value directly into process memory without printing, logging, or persisting it.

## Prototype 2: Lichess Opening Explorer

### Location and purpose

- Script: `Scratch/prototypes/proto-lichess-opening-explorer-2026-08-18.py`

This standard-library-only prototype exists to verify the live Explorer endpoint, authentication, schema, filters,
rate behavior, and Caro-Kann continuation statistics before any application integration. It supports configurable
rating bands, speeds, date range, number of moves, optional history, and explicit FENs. It does not fetch raw games
or read the user's game database.

### Authenticated run

The successful run used rating groups `1600,1800,2000,2200`, speeds `blitz,rapid`, and months 2024-01 through
2026-07. Six authenticated requests returned HTTP 200 in approximately 0.07-0.17 seconds each. No 429/503 or
rate-limit/retry headers were observed.

The live response matched the documented schema: position-level White/draw/Black totals and opening identity;
move-level SAN, UCI, average rating, outcomes, optional game reference, and optional opening identity.

### Representative observations

- After `1.e4`, `...c6` occurred in 9.71% of approximately 487.4 million filtered games.
- After `1.e4 c6`, `2.d4` occurred in 50.86% of approximately 47.3 million games.
- After `1.e4 c6 2.d4 d5`, White chose `3.e5` 36.09%, `3.exd5` 30.97%, and `3.Nc3` 21.47%.
- After Advance `3.e5`, Black chose `3...Bf5` 63.19%, `3...c5` 29.29%, and `3...e6` 4.21%.
- After `3.Nc3`, Black chose `3...dxe4` 81.58% of approximately 5.8 million games.

These values are point-in-time observations under coarse rating groups. They neither prove causality nor select a
repertoire move.

Representative safe PowerShell invocation, where the token is retrieved at runtime and never appears in command
text, is:

```powershell
powershell -NoProfile -Command "$t=[Environment]::GetEnvironmentVariable('LICHESS_TOKEN','User'); if($t){ $env:LICHESS_TOKEN=$t; python Scratch\prototypes\proto-lichess-opening-explorer-2026-08-18.py --ratings 1600,1800,2000,2200 --speeds blitz,rapid --since 2024-01 --until 2026-07 --moves 12 --top-moves 8 } else { Write-Output 'RETRIEVAL FAILED (sanitized)' }"
```

## Stockfish research and decisions

### Distribution facts

- Stockfish 18, tag `sf_18`, is the selected stable prototype release.
- The official Windows x86-64 AVX2 archive is `stockfish-windows-x86-64-avx2.zip`.
- Published and verified SHA-256:
  `6f6c272ebd6ea594377715235c8a7326f75940ef4f4f856f45106028fe6ae900`.
- AVX2 is the official recommended variant for most Intel 2013+ and AMD 2015+ systems.
- The archive includes the executable, GPLv3 license, source, and documentation. There is no separate NNUE file;
  the network is embedded.
- No detached signature or Authenticode signature was available; integrity relies on the official GitHub release
  and its published SHA-256.

### Settled prototype settings

- Use a reproducible, branch-diverse sample before expanding to every named Caro-Kann position.
- Use fixed depth rather than fixed nodes or wall time.
- Initial intended full analysis depth: 18.
- MultiPV: 3.
- Threads: 1.
- Hash: 64 MB.
- Record both White-relative and side-to-move-relative scores.
- Preserve mate scores structurally instead of flattening them into arbitrary centipawn values.
- Record PVs, first moves, achieved depth, nodes, engine time, and wall time.
- Do not assign preferred repertoire moves from engine output.

## Prototype 3: full Stockfish Caro-Kann sample

### Location and intended purpose

- Script: `Scratch/prototypes/proto-stockfish-caro-kann-2026-08-18.py`
- Data and engine directory: `Scratch/prototypes/proto-stockfish-caro-kann-2026-08-18.data/`

This disposable prototype was intended to download and verify the official Stockfish archive, select one named
Caro-Kann position per ECO code B10-B19 from the Lichess dataset, analyze the ten-position sample at depth 18 with
MultiPV 3, and write structured JSON evidence.

### Current status: incomplete and unsafe to run as written

The initial runs appeared to hang and their subagents were cancelled. The full script currently has three verified
`python-chess` 1.11.2 compatibility faults:

1. It attempts to configure `MultiPV` directly even though `python-chess` manages that option and requires
   `multipv=` on `analyse()`.
2. It calls `PovScore.pov()` without the now-required color argument.
3. It assumes `SimpleEngine.process` exists; process status is available through the transport instead.

A failed setup leaked an engine subprocess through a non-daemon asyncio loop in one reproduction. The full script
has not been repaired and no complete depth-18 sample result exists. Its module-level intended behavior is useful
design evidence, but its execution result must not be represented as successful.

## Prototype 4: bounded Stockfish smoke test

### Location and reason for existence

- Script: `Scratch/prototypes/proto-stockfish-smoke-2026-08-18.py`

This second engine script isolates one B12 Caro-Kann position at depth 1. It exists specifically to reproduce and
correct the engine-binding faults without letting a shell or subagent wait indefinitely. It reuses the already
downloaded and checksum-verified Stockfish archive, makes no new download, writes no result file, and guarantees
engine cleanup in `finally` handling.

Every potentially blocking engine shell command for this smoke test was required to use an external 30-second Git
Bash timeout in addition to a 20-second internal analysis timeout:

```bash
timeout --signal=KILL 30s Scratch/prototypes/.venv/Scripts/python.exe Scratch/prototypes/proto-stockfish-smoke-2026-08-18.py
```

### Smoke-test evidence

- Wrapper exit: 0; it did not hit timeout exit 124/137.
- Engine: Stockfish 18 from the verified AVX2 archive.
- Position: B12 Caro-Kann Defense: Advance Variation, Van der Wiel Attack after
  `1.e4 c6 2.d4 d5 3.e5 Bf5 4.Nc3 e6 5.g4 Bg6 6.Nge2 c5 7.h4`.
- Settings: depth 1, MultiPV 3, Threads 1, Hash 64, Skill Level 20, Move Overhead 10.
- Resulting first moves were `...h5`, `...Nc6`, and `...h6`; these shallow results are only process proof and have
  no repertoire significance.
- Analysis wall time was approximately 0.03 seconds.
- `engine.quit()` succeeded, subprocess exit code was 0, and `engine.close()` confirmed termination.

The smoke script correctly passes `multipv=3`, calls `score.pov(board.turn)`, obtains process status through the
engine transport, and cleans up after setup or analysis failures.

## Required timeout policy for further engine prototypes

The shell hang is now a first-class safety finding. No further full Stockfish prototype should be run without an
explicit external timeout around every command capable of downloading, extracting, launching, or waiting on the
engine. Internal Python timeouts and `finally` cleanup remain necessary but are not sufficient.

The proposed next staged proof, not yet approved or executed, was:

1. Repair the three known faults in the full prototype.
2. Run one depth-18 position with a 60-second external shell timeout.
3. Only after that passes and runtime is observed, run the branch-diverse sample with a 300-second external shell
   timeout.

The user requested this grilling record before selecting that next execution option.

## Decision log

The question-by-question outcomes were:

1. Analyze both game-level and position-level data, staged.
2. Preserve both player-centric and color-aware perspectives.
3. Defer the broad game-profile prototype after the focus shifted to positional theory.
4. Start with exact positions rather than structural or situational similarity.
5. Let `python-chess` own legal identity, excluding move counters.
6. Detect repetition across games, not within-game cycles.
7. Retain all opening plies; treat common openings as signal.
8. Keep ply zero but present it separately.
9. Ignore the rare within-game occurrence-count distortion for opening analysis.
10. Compare continuations and outcomes together.
11. Show aggregate evidence first, then one-factor contextual comparisons.
12. Use descriptive uncertainty rather than formal hypothesis testing.
13. Defer the display and support-tier policy.
14. Define the end goal as repertoire misses, harmful moves, and coverage gaps.
15. Key the repertoire by legal position so transpositions share decisions.
16. Represent White replies as graph branches and assign preferences at the user's Black nodes.
17. Identify Caro-Kann membership by reaching `1.e4 c6`.
18. Select the local CC0 Lichess opening-name dataset.
19. Label unnamed nodes with their deepest named ancestor plus continuation.
20. Replay forward and retain the latest exact name match.
21. Use realistic Lichess play as the preferred population evidence.
22. Query Explorer aggregates before acquiring raw bulk games.
23. Use a narrow environment-only OAuth token for Explorer access.
24. Rank move candidates using population evidence but require explicit user selection.
25. Combine population and engine candidates while displaying evidence separately.
26. Record both resulting evaluation and loss versus engine-best.
27. Prototype Stockfish over a branch-diverse Caro sample before expanding.
28. Use fixed depth 18 and MultiPV 3 for the intended sample.
29. Store White-relative and side-to-move-relative scores.
30. After hangs, require exact external shell timeouts and prove one depth-1 position before expansion.

## Open decision tree

### Position corpus and occurrence model

These questions are settled by MP-06, implemented and accepted on 2026-08-18: the extraction-owned
version-1 schema and ownership; game-global `position_occurrence` rows per game and ply with SAN/UCI and
counters plus a deduplicated first-four-field `position_state` unique index; atomic, idempotent reruns
with fingerprint change detection, rollback, and publication/completeness proof; and provenance retained
via the game reference plus ply and move fields. Delivery evidence is in the archived
[Validated FEN corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md); the
settled contract is in the [MP-06 grilling record](../grilling-docs/mp06-validated-fen-corpus.md). The
branches below remain open for MP-07 and later grilling.

### Repertoire behavior

- Preferred-move storage schema, provenance, mutation workflow, and history.
- Whether one preferred move is always sufficient or alternatives/transpositions need explicit policy.
- Frequency threshold for creating a coverage-gap task.
- Definition and time window for regression, inconsistency, or forgetting labels.
- Treatment of positions where the graph is reached from non-Caro move orders.

### Statistical presentation

- Tree, graph, table, or combined presentation.
- Small-sample policy and confidence-interval method.
- Support tiers, if any.
- Context filters and whether comparisons remain one-factor-at-a-time.
- Outcome normalization from the user's perspective and handling of rating/time-control confounding.

### Population evidence

- Production OAuth flow and secret ownership; the prototype's Windows user environment is not a production secret
  contract.
- Explorer request caching, refresh cadence, fair-use rate policy, and stale data behavior.
- Exact rating bands, speeds, and historical window for repertoire decisions.
- When aggregate evidence warrants selective raw-game acquisition.
- Whether and how CC0 bulk archive streaming should be added later.

### Engine evidence

- Repair and bounded depth-18 proof for the full prototype.
- Production Stockfish download/packaging, GPL compliance, version identity, and executable compatibility.
- Final depth, MultiPV, Threads, Hash, and analysis limits.
- Engine-result identity and invalidation when engine/version/settings change.
- Score normalization, WDL use, mate handling, and evaluation-loss calculation.
- Thresholds for harmful moves and whether they vary by opening phase or evaluation range.
- Candidate union/deduplication between Explorer moves and engine PVs.
- Batch progress, cancellation, timeout, recovery, persistence, and rerun behavior.

### Explicitly deferred analysis

- Structural position similarity, pawn structures, motifs, and situational/tactical pattern detection.
- General performance, opponent, and repertoire summaries outside the exact-position workflow.
- Formal causal claims from observational game outcomes.
- Automatically selecting or changing preferred repertoire moves.

## Completion rationale

This discovery established a coherent theory and evidence chain: replay captured PGNs into normalized legal
positions; key a transposition-aware Caro-Kann graph by those positions; attach deepest-ancestor opening names;
compare the user's moves with explicit repertoire choices; use Explorer aggregates to identify realistic
population candidates; use Stockfish to add objective candidates and quantify move loss; and leave final repertoire
authority with the user.

The local opening-name and authenticated Explorer prototypes succeeded. The bounded Stockfish smoke test succeeded
and exposed precise fixes and timeout requirements. The full depth-18 Stockfish prototype remains incomplete. This
record therefore closes the current discussion without claiming that production data modeling, UI, engine
analysis, or repertoire mutation is settled or authorized.
