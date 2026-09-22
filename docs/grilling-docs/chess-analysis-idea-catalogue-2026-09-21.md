# Chess analysis idea catalogue

**Started:** 2026-09-21  
**Status:** Comprehensive candidate input for Part 2 of the chess-learning workflow.  
**Authority:** This document inventories deterministic analyses the project could attempt. It is not a Plan, an implementation specification, or evidence that any listed relationship exists.

## Purpose

Build a comprehensive, reviewable list of chess questions the backend could test against the user's games. The eventual product-facing findings catalogue should contain only results that pass the agreed sample-size, effect-size, confidence, coverage, and multiple-testing rules.

The ordered route and current stage are recorded in `docs/grilling-docs/chess-learning-workflow-2026-09-21.md`. Part 1 builds analysis coverage; Part 2 tests this catalogue; Part 3 regrills the learning workflow from supported findings.

This is a catalogue of **candidate analyses**, not a catalogue of conclusions.

## Fixed boundaries

- No AI-generated labels, explanations, or causal stories.
- Chess features must come from stored facts or explicit deterministic rules.
- Statistical association is not automatically causation or a chess lesson.
- The learner's moves and opponents' moves remain separate populations.
- Opponent behaviour is tested both against the learner's game results and against the quality of the learner's responses.
- Unsupported observations do not become product findings.
- Every analysis idea and rule definition should be versioned so a later change does not silently alter the meaning of an existing result.

## Availability labels

- **Stored:** already present in the database.
- **Existing:** an aggregate or calculation already exists in repository code.
- **Derivable:** calculable from current stored data with deterministic chess rules.
- **Definition required:** derivable only after the project fixes a precise rule for the chess concept.
- **New data required:** cannot be answered soundly from the current data.

## Current data foundation

### Games — stored

Available from `datasource_game` in `src/chess_move_trainer/database/schema_v2.sql`:

- Chess.com game UUID and source URL.
- Original PGN.
- Learner colour.
- Learner and opponent Chess.com UUIDs.
- Learner and opponent ratings.
- Start and end times.
- Win, loss, or draw from the learner's perspective.
- Termination reason.
- Raw time-control value and time class.

### Position occurrences and moves — stored

Available from `derived_position` and `derived_game_position`:

- Piece placement.
- Side to move.
- Castling rights.
- Legal en-passant square.
- Game and ply order.
- Played move in UCI notation.
- Halfmove and fullmove counters.

These facts are enough to reconstruct the board before each move and deterministically inspect the move with `python-chess`.

### Openings — stored and existing

Available from `datasource_opening`, `derived_opening_route`, and opening recognition:

- ECO code and opening name.
- Known route moves.
- Deepest recognized ply.
- Route or transposition match.
- Current game-level opening performance aggregates.

### Engine analysis — stored and existing

Available from `derived_analysis_result`, `derived_analysis_line`, and the blunder reader:

- Analysis quality and engine configuration.
- Engine name and version.
- Centipawn or mate score.
- Win/draw/loss values.
- Up to five ranked principal variations.
- Analysis depth.
- Terminal-state classification.
- Learner-perspective expected score before and after a move when both positions have analysis.
- Expected-score loss, played move, and rank-one candidate move for comparable trainer moves.

### Repertoire and training — stored and existing

- Preferred move by position and effective date range.
- Position training balance.
- Preferred-move adherence aggregates.
- Position occurrence and move-response distributions split into learner choices and opponent responses.

## Standard outputs that can apply to most candidate features

For each feature or feature combination, the backend could calculate:

### Prevalence

- Count.
- Percentage of eligible moves or games.
- Percentage by colour.
- Percentage by opening or game phase.
- Percentage over time.
- Engine-analysis coverage for the category.

### Move quality

- Expected-score loss distribution.
- Mean, median, variance, and selected quantiles.
- Rate of moves over one or more serious-loss thresholds.
- Difference from the learner's overall baseline.
- Difference from an appropriate within-game, phase, colour, or opening baseline.
- Frequency of sound moves within an agreed distance of the best engine outcome.
- Frequency and size of missed opportunities after an opponent error.

### Game consequences

- Win, draw, loss, and score rate.
- Difference from the learner's baseline result.
- Termination-reason distribution.
- Relationship with game length and later evaluation recovery or collapse.

### Statistical evidence

- Eligible and analysed sample counts.
- Effect size.
- Confidence interval or other uncertainty bound.
- Statistical test result where appropriate.
- Multiple-testing-adjusted promotion result.
- Coverage and missing-data counts.
- Analysis catalogue version and engine configuration.

The exact statistical methods are deliberately not selected in this idea catalogue.

## Candidate learner-move analyses

### 1. Basic move inventory

- Moves by moving piece: pawn, knight, bishop, rook, queen, king. **Derivable**
- Pawn moves as a percentage of all learner moves. **Derivable**
- Moves by origin square, destination square, file, rank, and board region. **Derivable**
- Forward, backward, sideways, and diagonal movement where that description is meaningful for the piece. **Definition required**
- Move distance by piece type. **Derivable**
- Quiet moves versus captures. **Derivable**
- Checks versus non-checks. **Derivable**
- Castling, promotion, and en-passant frequencies. **Derivable**
- Legal-move count available when the learner chose the move. **Derivable**
- Learner move diversity in recurring positions. **Existing/derivable**

Each category can be tested for frequency, expected-score loss, severe-loss rate, variability, result, colour, phase, and trend over time.

### 2. Capture catalogue

- Capture rate overall and by moving piece. **Derivable**
- Capture matrix: moving piece × captured piece. **Derivable**
- Bishop captures of pawns, knights, bishops, rooks, and queens. **Derivable**
- Equivalent capture breakdowns for pawns, knights, rooks, queens, and kings. **Derivable**
- Captures by relative material value: lower-value takes higher-value, equal exchange, higher-value takes lower-value. **Definition required**
- Captures with check. **Derivable**
- Captures that produce checkmate. **Derivable**
- Captures followed immediately by recapture. **Derivable**
- Captures that complete a longer exchange sequence. **Definition required**
- Captures of defended versus undefended pieces. **Derivable after an explicit attack/defence rule**
- Captures onto defended versus undefended destination squares. **Derivable**
- Captures made by a pinned piece. **Derivable**
- Captures of a pinned piece. **Derivable**
- Captures that remove a defender of the king, queen, or another piece. **Definition required**
- Captures that change the material balance in the learner's favour or against it. **Derivable**
- Captures declined when the engine's leading line begins with a capture. **Derivable where analysis coverage permits**
- Queen trades and other major-piece exchanges. **Definition required**
- Frequency and quality of exchanging bishop for knight, knight for bishop, rook for minor piece, queen for material, and exchange sacrifices. **Definition required**

Natural drill-downs include moving piece × captured piece × phase, pin state, check state, defence state, material relationship, opening, colour, and learner result.

### 3. Checks and forcing moves

- Check frequency by moving piece. **Derivable**
- Capture-check, discovered-check, double-check, and promotion-check rates. **Definition required for subtypes**
- Check quality and expected-score-loss distribution. **Derivable after subtype rules**
- Checks that force only one legal reply. **Derivable**
- Checks followed by a loss of initiative or evaluation. **Definition required**
- Missed checking moves when a top engine candidate was a check. **Derivable where principal variation data permits**
- Checkmate delivered or missed. **Derivable where analysis and terminal data permit**
- Frequency and quality of other highly forcing moves, based on the opponent's legal-response count. **Definition required**

### 4. Tactical geometry

The board geometry is available, but every motif needs an explicit rule before testing.

- Absolute pins to the king. **Derivable**
- Relative pins to queens, rooks, or other higher-value pieces. **Definition required**
- Moving a pinned piece. **Derivable/definition required by pin type**
- Creating, maintaining, releasing, or exploiting a pin. **Definition required**
- Forks by piece type and target types. **Definition required**
- Skewers. **Definition required**
- Discovered attacks and discovered checks. **Definition required**
- Double attacks. **Definition required**
- X-ray attacks. **Definition required**
- Removal or deflection of a defender. **Definition required**
- Overloaded defenders. **Definition required**
- Interference and line blocking. **Definition required**
- Trapped or nearly trapped pieces. **Definition required**
- Hanging pieces before and after the move. **Definition required**
- Loose pieces and pieces defended only once. **Definition required**
- Back-rank vulnerability. **Definition required**
- Zwischenzug or intermediate-move opportunities. **Definition required and may require bounded search**
- Sacrifices and temporary material investments. **Definition required and may require multi-ply engine evidence**

For each motif, analysis could distinguish creating the motif, allowing it, exploiting it, missing it, and responding to it.

### 5. Material and exchanges

- Material balance before and after each move. **Derivable**
- Frequency of material gains and losses by piece value. **Derivable after fixing values**
- Expected-score change for equal trades, favourable trades, and unfavourable trades. **Definition required**
- Performance when ahead, equal, or behind in material. **Definition required**
- Quality of simplifying moves while ahead or behind. **Definition required**
- Piece-pair retention and exchange frequency. **Derivable**
- Bishop pair gained, retained, or surrendered. **Definition required**
- Queenless versus queen-present performance. **Derivable**
- Major-piece and minor-piece endgame performance. **Definition required**
- Material imbalance types, such as rook versus two minor pieces. **Definition required**
- Material recovery after an earlier loss. **Derivable where engine and sequence coverage permit**

### 6. Pawn decisions and pawn structure

- Pawn-move frequency overall, by file, and by phase. **Derivable**
- Pawn captures versus non-captures. **Derivable**
- One-square versus two-square advances. **Derivable**
- Central, wing, kingside, and queenside pawn moves. **Definition required**
- Early pawn-move count and repeated movement of the same pawn. **Definition required**
- Pawn pushes while behind or ahead in development. **Definition required**
- Pawn breaks and lever moves. **Definition required**
- Creation or repair of doubled pawns. **Definition required**
- Creation or repair of isolated pawns. **Definition required**
- Creation, movement, blockade, or loss of passed pawns. **Definition required**
- Backward pawns, pawn islands, chains, and phalanxes. **Definition required**
- Connected versus disconnected passed pawns. **Definition required**
- Opening or closing files and diagonals with pawn moves or captures. **Definition required**
- Pawn moves around the learner's castled or uncastled king. **Definition required**
- Premature pawn pushes that cannot move backward, identified only through an explicit rule and outcome evidence. **Definition required**
- Promotion attempts and promotion-piece choices. **Derivable, but likely rare**

### 7. King safety

- Castling rate and kingside versus queenside castling. **Derivable**
- Ply at which the learner castles. **Derivable**
- Retaining, losing, or voluntarily giving up castling rights. **Derivable**
- Remaining uncastled after a defined development point. **Definition required**
- King moves before castling or during the opening. **Derivable with a phase rule**
- Pawn shelter around the king. **Definition required**
- Open and semi-open files near the king. **Definition required**
- Number and value of attackers and defenders near the king. **Definition required**
- Moves that increase or reduce attacks around the king. **Definition required**
- Queen trades when under attack. **Definition required**
- Quality of responses to checks. **Derivable**
- Mate threats allowed, missed, or stopped. **Definition required and engine-dependent**
- Performance with opposite-side castling. **Definition required**

### 8. Development, activity, mobility, and space

- First-development ply for each minor piece. **Definition required**
- Number of developed pieces by selected opening plies. **Definition required**
- Repeated moves by the same piece during development. **Definition required**
- Early queen moves and number of queen moves before a selected ply. **Definition required**
- Early rook moves. **Definition required**
- Blocking one's own undeveloped pieces. **Definition required**
- Legal-move count and change in mobility after a move. **Derivable**
- Mobility by piece type. **Definition required**
- Controlled or occupied central squares. **Definition required**
- Space advantage using an explicit square-control rule. **Definition required**
- Rooks on open or semi-open files. **Definition required**
- Rooks on the seventh or second rank. **Derivable**
- Connected and doubled rooks. **Definition required**
- Knights on rim, central, or outpost squares. **Definition required**
- Good and bad bishops under an explicit pawn-colour rule. **Definition required**
- Queen activity and exposure to attack. **Definition required**
- Piece moves that gain or lose tempo because the piece is immediately attacked. **Definition required**

### 9. Move sequences and habits

- Consecutive moves by the same piece. **Derivable**
- Number of moves made by each piece during selected phases. **Derivable after phase rules**
- Capture–recapture sequences. **Derivable**
- Check sequences. **Derivable**
- Repeated attacks on the same piece. **Definition required**
- Moving a piece and then returning it to its previous square. **Derivable**
- Queen excursions and return moves in the opening. **Definition required**
- Tempo spent responding to opponent threats. **Definition required**
- Repetition of board states and draw claims. **Derivable by replay**
- Evaluation volatility over consecutive learner and opponent plies. **Derivable where engine coverage permits**
- Collapse patterns: one serious error followed quickly by further errors. **Definition required**
- Recovery patterns after an evaluation loss. **Definition required**
- Conversion patterns after obtaining a large advantage. **Definition required**
- Failure to convert or tendency to simplify away an advantage. **Definition required**

### 10. Opening and repertoire relationship

- Opening and variation frequency. **Existing**
- Opening score rate, colour, rating, and game-length breakdown. **Existing/derivable**
- Deepest recognized opening ply. **Existing**
- Route versus transposition frequency and performance. **Existing/derivable**
- First departure from a recognized route. **Derivable after defining route choice**
- First departure from the learner's saved preferred move. **Derivable where preference dates align**
- Preferred-move adherence and quality of deviations. **Existing/derivable**
- Repeated move-order problems. **Definition required**
- Early queen, pawn, bishop, or knight patterns by opening. **Derivable after thresholds**
- Opening positions with high response diversity. **Existing/derivable**
- Openings in which the learner reaches sound positions but later deteriorates. **Derivable where analysis coverage permits**
- Openings in which the learner is already worse at the end of recognized theory. **Derivable where analysis coverage permits**
- Opening recall performance compared with later real-game adherence. **New attempt-history data required for a strong longitudinal comparison**

### 11. Engine-backed move quality

- Expected-score loss for every comparable learner move. **Existing**
- Loss distributions by feature, game, opening, phase, colour, rating difference, and time class. **Derivable**
- Severe-loss count and rate. **Existing/derivable after thresholds**
- Best, worst, median, and most variable move categories. **Derivable**
- Difference between played move and rank-one principal-variation move. **Existing/derivable**
- Whether the played move appears in any stored multi-PV first move. **Derivable**
- Spread between top engine candidates as a measure of decision narrowness. **Derivable after score normalization**
- Sound alternatives: number of candidate moves within an agreed expected-score distance of the best. **Derivable within stored multi-PV limits**
- Forced or nearly forced positions based on legal moves and engine-candidate spread. **Definition required**
- Missed opportunities after the opponent's evaluation-losing move. **Derivable**
- Accuracy of the learner's first response after an opponent mistake. **Derivable**
- Evaluation stability or volatility by move category. **Derivable**
- Moves that change score kind between centipawn and mate. **Derivable**
- Performance by engine-analysis depth or quality. **Stored/derivable**
- Sensitivity to engine version or settings. **Stored for current result, but historical comparisons require retained reruns**

## Candidate opponent-behaviour analyses

Opponent features must be calculated from opponent moves only. They can then be linked separately to final game outcome and to the learner's next or later responses.

### 12. Opponent move style

- Opponent move mix by piece type. **Derivable**
- Opponent pawn-move rate. **Derivable**
- Opponent capture rate and capture matrix. **Derivable**
- Opponent check rate. **Derivable**
- Opponent quiet-move rate. **Derivable**
- Opponent castling rate and timing. **Derivable**
- Opponent early queen activity. **Definition required**
- Opponent repeated-piece movement during development. **Definition required**
- Opponent exchange frequency and queen-trade tendency. **Definition required**
- Opponent move-choice diversity in recurring positions. **Existing/derivable**
- Opponent tactical volatility and engine-measured error rate. **Derivable where analysis coverage permits**
- Opponent opening choices and transpositions. **Existing/derivable**

For each behaviour, test:

- Learner score rate in games containing the behaviour.
- Difference from learner baseline after colour, opening, rating difference, and time class are considered.
- Learner expected-score loss immediately after the behaviour.
- Learner severe-loss rate within a defined response window.
- Openings, phases, and board contexts where the relationship is strongest.

### 13. Opponent pressure and learner response

- Learner responses to checks, captures, threats, and forcing moves. **Derivable/definition required**
- Learner responses to attacks on the queen. **Definition required**
- Learner responses to early queen moves. **Definition required**
- Learner responses to repeated pawn advances. **Definition required**
- Learner responses to kingside or queenside pawn storms. **Definition required**
- Learner responses when the opponent delays castling. **Definition required**
- Learner responses to sacrifices. **Definition required**
- Learner responses after opponent blunders and missed opportunities. **Derivable**
- Learner performance against frequent exchanges versus tension-maintaining play. **Definition required**
- Learner performance against open versus closed centres. **Definition required**
- Learner performance against opposite-side castling attacks. **Definition required**
- Learner performance when the opponent departs from the recognized opening early. **Derivable after departure rule**
- Learner performance against repeat opponents. **Existing/derivable, but opponent sample sizes may be small**

### 14. Opponent profiles at game level

- High versus low pawn-move share. **Definition required**
- High versus low capture share. **Definition required**
- Early queen mover. **Definition required**
- Frequent exchanger. **Definition required**
- Delayed developer or delayed castler. **Definition required**
- High-check or high-forcing-move player. **Definition required**
- High engine-error or high-volatility player. **Definition required**
- Opening specialist within the learner's observed games. **Definition required**

These are deterministic statistical profiles, not personality labels. Thresholds must be explicit, versioned, and based only on observed game facts.

## Game context and segmentation candidates

Every move or opponent-behaviour analysis could be segmented or adjusted by:

- Learner colour. **Stored**
- Opening, ECO, variation, route, or transposition. **Stored/existing**
- Opening versus later play. **Definition required**
- Opening, middlegame, and endgame phase. **Definition required**
- Time class and parsed time control. **Stored; parsing required for base/increment**
- Learner rating, opponent rating, and rating difference. **Stored**
- Game result. **Stored**
- Termination reason. **Stored**
- Game length and duration. **Stored/existing**
- Calendar period, weekday, and UTC hour. **Stored/existing**
- Recent form, streak state, and longitudinal period. **Existing/derivable**
- Material state. **Derivable**
- Evaluation state: better, equal, worse, winning, or losing. **Definition required**
- Position complexity based on legal moves, engine-candidate spread, or volatility. **Definition required**
- Engine configuration, depth, and quality. **Stored**
- Repertoire preference active on the game date. **Stored/derivable**

## Cross-feature and drill-down ideas

The staged analysis can start broadly and split only along predeclared branches. Candidate combinations include:

- Moving piece × capture/non-capture.
- Moving piece × captured piece.
- Moving piece × destination region.
- Moving piece × game phase.
- Capture pair × material state.
- Capture pair × pin state.
- Capture pair × defended/undefended state.
- Capture pair × check state.
- Pawn move type × king side/queen side × castling state.
- Check type × moving piece × opponent response count.
- Tactical motif × learner action: create, allow, exploit, miss, or answer.
- Early queen activity × opening × learner response quality.
- Opponent pawn-move share × opening × learner game result.
- Opponent capture rate × learner severe-loss rate.
- Time class × move feature × expected-score loss.
- Rating difference × move feature × expected-score loss.
- Colour × opening × move feature.
- Evaluation state × exchange choice × later result.
- Advantage size × simplification choice × conversion success.
- Repertoire adherence × engine quality × game result.
- Engine-candidate spread × learner move quality.
- Analysis depth/quality × apparent feature effect.

Every extra dimension reduces samples per cell. The analysis catalogue must bound allowed combinations and include them in the multiple-testing family rather than searching arbitrary combinations until something appears significant.

## Longitudinal learning questions

- Are severe-loss rates declining over time? **Derivable**
- Are losses associated with a promoted pattern declining over time? **Derivable once findings are versioned**
- Is expected-score loss improving for a piece, move type, opening, or phase? **Derivable**
- Does the learner continue making a move pattern after it is identified? **Derivable once identification dates are stored**
- Does real-game performance improve after repertoire practice? **Partly derivable; strong analysis needs attempt history**
- Does real-game response quality improve after pattern practice? **New detailed training-attempt history required**
- Does improvement transfer to different positions sharing the same deterministic feature? **New finding-to-training linkage and attempt history required**
- Do opponent behaviours that previously caused difficulty become less damaging? **Derivable once findings and intervention dates are stored**
- Is improvement durable over weeks or months? **New detailed intervention and attempt history required**

## Data unavailable today

The following questions cannot currently be answered soundly:

- Per-move thinking time or clock pressure; no move clock is stored.
- Time remaining after each move.
- Whether a move was intentional, accidental, guessed, or misunderstood.
- The learner's own explanation of a decision.
- Human coach labels or annotations.
- A population baseline from players outside the games stored in this project.
- An opponent's general style outside games played against the learner.
- Historical changes between multiple engine runs for the same position; only the current stored analysis is authoritative.
- Detailed training attempts, answer history, response time, hints, and retention; the current trainer stores an aggregate balance.
- Reliable causal claims that one feature caused a result.

Potential future inputs, if deliberately approved, include per-move clocks, explicit learner notes, versioned promoted findings, training-attempt history, and an external comparison corpus. None is assumed by this catalogue.

## Reliability and interpretation hazards

- Many moves from one game are related observations, not independent games.
- The same player may appear in multiple games.
- Openings, colour, rating difference, time class, and game phase can confound simple percentages.
- Common features can dominate raw counts while rare features produce unstable effects.
- Categories overlap; one move may be a bishop capture, check, pin release, and opening departure simultaneously.
- Engine coverage is incomplete unless both relevant positions were analysed.
- Centipawn and mate scores need a common outcome treatment; expected-score WDL already supplies one repository-backed option.
- Engine version, settings, depth, and MultiPV coverage affect comparisons.
- Stored principal variations are candidate evidence, not human explanations.
- Correlation with wins or losses does not establish that a move category caused those results.
- Searching many categories and combinations creates false discoveries unless the complete test family is controlled.
- A statistically reliable but tiny effect may not be useful for learning.
- A large effect with very few observations may remain too uncertain for promotion.
- Phase, motif, profile, and threshold definitions must be explicit and versioned.

## Suggested backend analysis families

This grouping is only an organizational aid for a future assessment:

1. **Move inventory** — deterministic feature extraction and descriptive frequencies.
2. **Move quality** — engine-backed outcome distributions by learner feature.
3. **Capture matrix** — mover, target, context, and outcome.
4. **Tactical geometry** — explicitly defined board relationships and actions.
5. **Position structure** — material, pawn, king, development, mobility, and phase features.
6. **Sequence behaviour** — repeated moves, exchanges, volatility, collapse, recovery, and conversion.
7. **Opening and repertoire** — recognition, adherence, departure, and later deterioration.
8. **Opponent behaviour** — opponent move profiles linked separately to game results and learner responses.
9. **Context and trends** — colour, rating, time control, date, form, and longitudinal change.
10. **Confidence and promotion** — test-family control, evidence thresholds, versioning, and the high-confidence findings catalogue.

## Repository evidence consulted

- `src/chess_move_trainer/database/schema_v2.sql`
- `src/chess_move_trainer/database/games/normalization.py`
- `src/chess_move_trainer/database/openings/recognition.py`
- `src/chess_move_trainer/database/reporting/models.py`
- `src/chess_move_trainer/database/reporting/game_aggregates.py`
- `src/chess_move_trainer/database/statistics.py`
- `src/chess_move_trainer/database/blunders/`
- `backend/app/features/trainer_blunders/api_schemas.py`
- `backend/app/features/evaluation/schema.py`
- `requirements.txt`
