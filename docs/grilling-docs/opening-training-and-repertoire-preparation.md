# Opening Training and Repertoire Preparation — Full Grilling Synthesis

**Recorded:** 2026-08-22
**Status:** Full design-evidence synthesis; confirmed direction and open analytical choices
**Implementation authority:** None
**Relationship:** Builds on the exact-position, opening-catalog, transposition, recurrence, progressive-training,
and backend-analysis evidence recorded in the existing grilling documents and completed Plans. It supersedes no
historical record and does not amend any completed Plan.

## Purpose

This document describes possible ways to use the currently prepared chess corpus, opening catalog, opening
relationships, and partial engine data to study openings, prepare a repertoire, and eventually train it. It is a
durable record of evidence, safe interpretations, analytical opportunities, preparation needs, and unresolved
decisions. It is deliberately written so that a later focused Plan can use it without treating it as implementation
authority.

The central distinction is:

> The prepared data can describe what was reached, what was played, what recurred, what branches were popular in
> the observed population, and what an engine reported under a particular analysis identity. It cannot, by itself,
> prove that a move is the right personal repertoire move, that a player has memorised a line, or that training
> caused a later result.

The initial subject is the tracked player `skyrocoster`, especially Caro-Kann positions reached as Black. The
analytical model remains useful for other openings later, but expanding the subject, opening scope, or product
surface is an open decision rather than an implication of this record.

## 1. Reading rules and authority boundaries

This is design evidence, not a product specification, database schema, API contract, implementation Plan, or work
order. It does not authorize:

- a database write, migration, backup replacement, or source-data change;
- a preferred move, accepted move, threshold, formula, score, ranking, or adaptive-frontier decision;
- an engine release, budget, population source, dependency, credential flow, or analysis policy;
- a training interface, report interface, notification, route behavior, or other product behavior;
- a claim that the player has trained, remembered, improved, or transferred knowledge; or
- edits to existing historical grilling records, completed Plans, `Scratch/`, or the valuable untracked runtime DB.

The existing records remain the authorities for their settled boundaries. In particular:

- [Opening Position Pattern Discovery](opening-position-pattern-discovery.md) establishes exact legal position
  identity, the transposition-aware repertoire graph, the three initial queues, manual preferred-move authority,
  observational uncertainty, and the separate population and engine evidence channels.
- [Opening Classification Database Foundation](opening-classification-database-foundation.md) establishes the
  opening-owned catalog and relationship preparation route, the separation of neutral and player facts, and the
  sequential S1-S5 envelope.
- [Personal Opening Classification and Progressive Line Training](opening-classification-and-progressive-training.md)
  establishes the conceptual direction for player-only frontiers, global versus route recurrence, full-line
  practice, shared position mastery, route-specific progress, pause-not-delete progression, and replaceable
  priority calculations.
- The completed [S1 Source Catalog Plan](../plans/done/s1-source-catalog/s1-source-catalog.md), [S2 Opening
  Relationships Plan](../plans/done/s2-opening-relationships/s2-opening-relationships.md), [MP-06 Validated FEN
  Corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md), [MP-09 Persisted Backend
  Stockfish Analysis Plan](../plans/done/mp09-persisted-backend-stockfish-analysis/mp09-persisted-backend-stockfish-analysis.md),
  and [MP-10 Browser Evaluation Plan](../plans/done/mp10-browser-evaluation/mp10-browser-evaluation.md) provide
  delivery evidence and current-state caveats.

When a historical Plan and the current untracked database appear to disagree, the difference is an audit item. It
must not be silently resolved by changing the historical record or by assuming that the latest-looking number is the
intended product truth.

## 2. Observed current facts

### 2.1 Corpus, catalog, and relationship counts

The following values are current read-only observations or accepted delivery facts. They are not interchangeable
denominators.

| Fact | Current value | Meaning and caution |
|---|---:|---|
| Fetched game rows | 12,369 | Rows in the normalized `games` source table. This is not the accepted training corpus. |
| Accepted standard games | 12,365 | Accepted subject-corpus games with standard chess rules and the subject appearing once. Four `oddschess` rows are excluded. |
| Ordered occurrences | 639,262 | Game-global position occurrences, including ply zero and one row per stored ply. Occurrence counts are not unique-position counts. |
| Unique training states | 510,876 | Deduplicated four-field legal states: placement, side to move, castling rights, and legal en-passant state. Move counters are excluded. |
| Opening catalog records | 3,810 | The fixed five-file opening source, with source row and import provenance. |
| Opening relationship positions | 7,927 | Replay-derived opening-owned relationship position keys. These are not all game-derived states. |
| Opening memberships | 36,925 | Post-move catalog memberships, including valid multiple memberships. They must not be summed as exclusive opening labels. |
| Opening transposition links | 12,077 | Explicit source-line transposition events. They describe taxonomy relationships, not automatic training equivalence of every context. |
| Engine analysis results | 3,158 | Current exact six-field FEN result roots under the stored analysis namespace. This is partial coverage. |
| Engine candidate rows | 15,736 | Ranked candidate rows associated with those results; roots can have fewer than five candidates, including terminal roots. |
| Recorded analysis batch summaries | 2 | Both durable summaries refer to the same selected game and 83 positions: the first completed 83, and the second reused all 83. |
| Evaluation queue rows | 1 | Current evaluation-queue evidence, separate from the corpus and training namespaces. |

The accepted four-field corpus identity is the training and recurrence grouping identity. A six-field FEN can be
reconstructed from an occurrence by adding its halfmove and fullmove counters, but that does not make the six-field
engine identity interchangeable with the four-field training identity. The historical MP-09 opening-first preflight
projected 515,515 unique six-field FENs, with 515,432 missing at that time. That projection was a read-only planning
number, not proof that the full set was analyzed.

The opening endpoint separation is essential. S1 found 3,021 opening endpoints that were not already present in the
game-derived `position_state` table. Those endpoints remain opening-owned facts. They must not be inserted into
game-derived occurrence tables merely to make joins convenient.

### 2.2 Game dimensions and source limitations

The source covers approximately 31 months, from 2024-02 through 2026-08, with the observed time-class counts:

- 4,612 blitz games;
- 4,217 bullet games;
- 3,422 rapid games; and
- 118 daily games.

The games table carries time control, time class, date, ratings, colors, results, termination, opening URL, and
other source fields. Chess.com accuracy is present for only 1,528 games, so accuracy cannot stand in for a complete
player-performance measure. The `games.eco`-like opening value is a Chess.com URL; ECO codes are available in PGN
headers rather than as a dedicated equivalent code field. The opening URL, PGN ECO tag, local Lichess taxonomy, and
replayed legal route are related evidence sources, not automatically identical labels.

All 12,369 current PGNs contain a clock annotation marker in the raw text during the bounded scout. That supports a
possible think-time analysis, but it does not yet prove that every annotation is well-formed, comparable across time
controls, correctly interpreted around increments, or safe to call thinking time. A robust parser validation pass is
required before treating clock-derived values as facts.

### 2.3 Engine provenance audit gap

The current read-only comparison found 3,075 of the 3,158 `analysis_result` FENs outside the exact 83-FEN selection
represented by the two durable analysis batch summaries. The current result schema and records do not provide a
complete, direct result-to-run explanation for those rows. This is a documentary and data-quality audit gap.

It is not evidence of wrongdoing or proof of an unauthorized run. The historical MP-09 record states that a full
corpus execution was not authorized or accepted, while the MP-10 historical Plan contains a note that a corpus fill
was running. Both statements must be preserved as historical tension until a bounded provenance audit reconciles
them. The synthesis may report the 3,075 mismatch, but must not attribute it to a person, operation, or failed
control without evidence.

The audit should distinguish at least:

1. a result root that is directly tied to a recorded selected-game batch;
2. a result root that is directly tied to a recorded evaluation-queue event;
3. a result root that has engine/profile/settings evidence but no complete run attribution; and
4. a result root whose identity or content fails validation.

Those categories are audit outputs, not a replacement engine or provenance schema.

### 2.4 What is not present

The current prepared data has no preferred-move assignment history and no training-attempt event table. It therefore
cannot currently prove:

- a repertoire miss against a user-authorized move;
- a training answer being correct or incorrect;
- immediate recall, delayed retention, transfer, mastery, or forgetting;
- route progress caused by practice; or
- a trained success rate at any line depth.

The current S3 neutral game classification, S4 event and aggregate projections, and S5 tracked-player projections
are also unbuilt. S1 and S2 provide the opening catalog and taxonomy relationships, but they do not yet prove every
named opening route encountered by every accepted game.

The tracked `schema.txt` is stale and is not a current schema authority. It must not be edited as part of this
synthesis. Current schema claims should be tied to accepted Plans or a fresh read-only runtime inspection.

## 3. Settled identity, ownership, and authority rules

### 3.1 Four-field training identity

The exact legal state used for training and recurrence is the four-field identity:

1. piece placement;
2. side to move;
3. castling rights; and
4. legally relevant en-passant state.

Halfmove and fullmove counters are deliberately excluded from this identity. This lets different games and legal
move orders converge on one board state for repertoire and recurrence purposes while preserving each occurrence's
position in its source game.

This identity is not piece placement alone. Combining states with different side to move, castling rights, or legal
en-passant rights would combine materially different decisions.

### 3.2 Six-field analysis identity

Engine analysis uses the exact six-field FEN, including halfmove and fullmove counters. The analysis identity is
therefore deliberately separate from the four-field training identity. A current engine result can be useful
evidence for an occurrence with that exact six-field FEN, but it must not be silently promoted to a reusable result
for every occurrence of the four-field state.

The separation prevents two opposite errors:

- treating equivalent training states as different merely because counters differ; and
- treating exact-FEN engine evidence as universally reusable when its stored identity and settings do not support it.

### 3.3 Opening ownership and taxonomy membership

Opening catalog endpoints and relationship positions are opening-owned. Game-derived position states and occurrences
are owned by the accepted corpus. Opening-only positions must never masquerade as game observations.

A game and a position may have multiple valid opening memberships. Broad families, nested variations, and
transposition links should be preserved rather than collapsed into one preferred label. A route report must show
whether a count is:

- a global game-derived count;
- an opening-owned taxonomy count;
- a route-specific game-derived count; or
- a player-specific projection.

### 3.4 Neutral facts and player facts

Neutral facts describe the game, route, opening membership, recurrence event, result, rating, color, and chronology
without depending on a selected player. Player facts describe how `skyrocoster` relates to those neutral facts,
including color, reached route, personal recurrence, preferred move, misses, attempts, and progress.

The player projection must reference the existing stable player UUID. A username may be resolved at an import or setup
boundary, but it must not be the durable identity of a fact. No numeric player ID or SQLite `rowid` is a product
identity.

### 3.5 Manual repertoire authority

The user manually owns the accepted or preferred repertoire move at a user decision position. Engine output,
population frequency, opening labels, and historical play may propose or explain candidates, but none of them selects
the accepted move automatically.

The settled initial direction is one accepted move per shared exact training position. Whether future alternatives,
conditional preferences, or move versions are needed remains open. Any accepted-move history should preserve the
previous value rather than erase it.

### 3.6 Raw facts and replaceable calculations

Raw source, replay, move, route, manual-choice, engine-run, population-snapshot, and training-attempt facts should
remain durable wherever they can be reconstructed or audited. Recurrence summaries, branch priority, frontier
membership, mastery, queues, survival curves, and report caches are calculations that may be replaced when a formula
or interpretation changes.

Changing a calculation must not destroy the events that made the old calculation possible. When a calculation is
recomputed, its input versions, calculation version, and run outcome should be identifiable, but the exact storage
mechanism is open.

### 3.7 Pause-not-delete and shared mastery

Progressive line training reinforces the current line endpoint, extends only after reliable recall, and pauses deeper
progression when earlier recall weakens. A pause is not a reset and never deletes prior progress.

When routes converge on one exact four-field state, board mastery is shared while route progress remains separate.
One accepted move at that shared state creates a shared continuation for all routes through it. The route context,
prompt context, and route depth must still be preserved when measuring training, because the same board can be reached
through different histories.

## 4. What can be analyzed now

The following opportunities are possible with the prepared data, subject to the identity and denominator boundaries
above. “Possible now” means that the raw or already accepted facts are sufficient for a descriptive analysis. It does
not mean that a production report, UI, API, schema, or automatic queue is authorized.

### 4.1 Corpus and data-quality observatory

A first report can show:

- fetched rows versus accepted standard-corpus rows;
- the four excluded `oddschess` rows and their exclusion reason;
- accepted-game ownership and color balance;
- occurrence completeness by game and ply;
- unique four-field state counts and repeated-state counts;
- catalog, relationship, and transposition counts;
- engine-result, candidate, queue, batch, and failure counts;
- source, schema, manifest, profile, and run versions;
- PGN replay, FEN, SAN/UCI, and clock-parser validation results; and
- integrity, foreign-key, backup, lock, and sidecar observations when a future audit is authorized.

This observatory is valuable because it tells later analysts whether a missing result means “not observed,” “not
accepted,” “not classified,” “not analyzed,” “not attributable,” or “failed validation.” It must never turn a missing
fact into a zero.

### 4.2 Exact-state recurrence

For every four-field state that occurs in accepted games, a descriptive analysis can examine:

- number of distinct accepted games reaching it;
- raw occurrence count, with game count shown separately;
- earliest, latest, and distribution of reached plies;
- color and player-side context;
- time class, time control, rating, rating gap, date, and result context;
- the next move or terminal outcome from the state;
- whether the state is in a named or multiple taxonomy relationship; and
- whether multiple move orders converge on it.

The count of occurrences and the count of games are different evidence. A single game with a repeated state can add
more occurrences, while a state reached by many games has broader game support. Both may be useful, but neither
should be hidden inside one “frequency” number.

### 4.3 Branch mass and continuation dispersion

At a recurring state, continuation analysis can show the observed mass of each next move and the denominator from
which that mass was calculated. The most useful first view is:

- parent state;
- side to move and relevant player color;
- child move;
- raw count of games and occurrences;
- conditional share among parent-reaching observations;
- result and context slices; and
- uncertainty or support warnings.

An entropy-like measure can summarize whether a state has one concentrated continuation or many dispersed branches.
Its base, treatment of low counts, denominator, and use in ranking are not selected here. It must remain a descriptive
companion to the branch table, not a hidden replacement for the table.

High branch mass does not mean “correct.” High dispersion does not mean “unlearnable.” A concentrated population
branch may be a practical response, while a low-mass branch may be critical to this player's actual games.

### 4.4 Retrospective move consistency

Once a manual preferred move exists, a replay can compare the player's move at each relevant decision occurrence with
the move that was accepted at that state. This supports retrospective labels such as:

- preferred move played;
- repertoire miss;
- move not comparable because the preferred assignment was absent or changed;
- move outside the approved route; and
- repeated miss at the same state.

This is a comparison of recorded play to a user-authorized reference. It is not a proof that the preferred move is
objectively best or that a non-preferred move was a chess mistake.

At present, no preferred-move history exists, so this analysis is a future opportunity rather than a current result.

### 4.5 Objective move-loss evidence

Where the exact six-field FEN before a player's move and the exact six-field resulting FEN have comparable, valid engine
evidence, an analysis can preserve two distinct values:

1. the resulting position's evaluation; and
2. the loss relative to the engine's best candidate from the starting position.

The distinction matters. A move can enter a position that is already unfavorable without causing all of that
disadvantage. Conversely, a move can lose value while the resulting position remains favorable. The current engine
coverage, profile identity, MultiPV behavior, and provenance gap make this a partial, setting-specific observation.

No harmful-move threshold is selected. A future report should show the raw values, score kind, engine profile,
candidate context, and coverage status before any action label is considered.

### 4.6 Opening and taxonomy relationships

The current S1/S2 data can support inspection of:

- catalog records and their exact opening-owned endpoints;
- deepest earlier named parents;
- broad and nested memberships;
- named-source transpositions; and
- positions shared by several catalog records.

It cannot yet be described as a complete neutral classification of every accepted game because S3 is unbuilt. A
future replay-derived classification can attach every encountered named opening to its anchor and downstream route,
but it must retain all memberships and provenance rather than choosing one label.

### 4.7 Historical game-side analysis

The game source can support descriptive comparisons by player color, time class, time control, rating, opponent,
month, termination, result, opening source field, and the limited accuracy subset. A Caro-Kann route may be
recognized by replaying the canonical `1.e4 c6` entry condition rather than trusting a URL, but a durable route
classification is still a future preparation slice.

Historical game-side analysis is useful for locating where the player actually arrived. It is not a causal study of
why a game was won or lost.

### 4.8 Clock-derived thinking-time candidates

After parser validation, clock annotations could support derived measures such as remaining clock, elapsed clock,
increment-adjusted consumption, move-time bands, time trouble, and decision-time differences by branch. These values
must remain derived from raw PGN plus a parser version, with explicit handling for:

- missing or malformed annotations;
- increments and time controls;
- clock precision and rounding;
- move annotations not matching every ply;
- clock reset or source-specific semantics; and
- comparison across bullet, blitz, rapid, and daily games.

Until those checks pass, the safe statement is only that clock markers appear in the raw PGNs.

## 5. Safe interpretations and unsupported claims

### 5.1 Statements that are safe when denominators are shown

The data can safely support statements such as:

- “This four-field legal state was reached by N accepted games and M stored occurrences.”
- “Among games reaching this state in this selected period or time class, these continuations were observed.”
- “This branch has higher or lower observed conditional mass than another branch in the same defined cohort.”
- “These taxonomy records reach the same opening-owned state through different source prefixes.”
- “The player played this move in K of the comparable occurrences after a manual preferred move was recorded.”
- “Under this exact six-field FEN and this recorded engine profile, the engine reported this candidate and this
  evaluation loss.”
- “This population source reported this move frequency for this rating, speed, date, and position filter.”
- “These training attempts produced these answers under these prompt, hint, timing, and route contexts.”

Each statement needs its population, cohort, identity, date, denominator, and uncertainty. “Observed” is the default
verb. “Suggests” may be appropriate when the evidence is consistent and caveats remain visible. “Proves” is rarely
appropriate for this observational corpus.

### 5.2 Statements that are not supported

The current or proposed analytical data cannot safely support these claims without new evidence and an explicit
decision:

- a game result proves opening quality;
- a move is the correct personal repertoire move because an engine or population chose it;
- a population frequency is causal, representative of all players, or appropriate for this player without a defined
  cohort;
- the single-player corpus generalizes to the chess population;
- an engine result under one six-field FEN and one profile is timeless or applies to every four-field occurrence;
- a player forgot, mastered, improved, or transferred a line when no attempt event records that behavior;
- a route is a coverage gap without a defined route classification, preferred move, support rule, and denominator;
- a move was harmful without a validated before/after comparison and an explicit threshold policy;
- a player improved because a later cohort has a different result or evaluation distribution;
- a clock annotation is exact thinking time before parser and source-semantic validation; or
- the 3,075 engine-result provenance mismatch demonstrates wrongdoing or a particular unauthorized run.

## 6. Target selection and the three queues

### 6.1 What a target is

A target is a position, route, branch, or line endpoint that may deserve further human attention. It is not
automatically a training assignment and not necessarily a problem. A target report should expose the evidence that
made it visible:

- personal recurrence and distinct-game support;
- opening-route recurrence and conditional branch mass;
- player's color and decision ownership;
- recency and rating proximity as separate context;
- retrospective preferred-move consistency, when available;
- engine-loss evidence, when comparable and attributable;
- amount of training already attempted, when events exist; and
- uncertainty, missingness, and provenance status.

The settled direction is to keep these dimensions visible rather than hiding them inside one weighted score. The
formula, weights, entry and retirement thresholds, and hysteresis values remain open.

### 6.2 Repertoire-miss queue

**Definition:** A preferred move exists for the exact four-field decision state, the state was reached in the
player's relevant game context, and the player played another move.

**Evidence needed:** the accepted-move snapshot and its validity interval, the exact state, the game and ply, player
color, played move, route context, and any comparable engine or population evidence shown separately.

**Useful analyses:** miss count by state, distinct games with a miss, first/recent miss, repeated-miss pattern,
branch mass after the miss, time-control and rating context, and whether the same state was answered correctly in
later attempts.

**Limit:** A repertoire miss is a mismatch with the user's chosen reference. It is not automatically a harmful move,
a memory failure, or an opening-quality judgment.

### 6.3 Harmful-move queue

**Definition:** A player's move has evidence of a sufficiently negative objective change under a selected engine
comparison policy.

**Evidence needed:** exact six-field starting identity, exact resulting identity, same or explicitly comparable
engine profile, engine-best candidate set, resulting evaluation, evaluation loss, score kind, mate handling, and
provenance.

**Useful analyses:** distribution of losses, repeated moderate losses versus isolated severe losses, position-evaluation
bands, time-control context, branch mass, and disagreement between engine and user-preferred move.

**Limit:** No threshold is selected. Resulting evaluation and evaluation loss must remain separate. A harmful-move
label must never be inferred solely from game result, opening label, population frequency, or one shallow engine line.

### 6.4 Coverage-gap queue

**Definition:** A recurring player-relevant state or route has no user-authorized preferred move and may deserve a
response in the repertoire.

**Evidence needed:** neutral classification and route facts, player projection, four-field recurrence, conditional
branch mass, player color, recency/rating context, and an explicit support policy.

**Useful analyses:** high-mass states without an accepted move, branches that repeatedly appear after a named anchor,
transposition-converged states, and routes whose depth exceeds current accepted repertoire coverage.

**Limit:** It is not a gap merely because a state is frequent globally, occurs in the population, or has an engine
candidate. The player-only frontier rule remains: population evidence may propose candidates, but only the player's
games define what is tracked as this player's opening frontier.

### 6.5 Queue interaction without automatic ranking

One state can be in more than one queue. For example, a preferred move can exist, the player can miss it, and the move
can also have engine-loss evidence. A state can be a coverage gap before a preferred move is selected and later become a
repertoire-miss state. Queue history should preserve those transitions rather than overwrite the earlier reason.

An isolated engine outlier should not automatically outrank repeated moderate misses. Conversely, a high recurrence
state should not hide a rare but severe branch. A future priority calculation may combine these factors, but its
inputs and output must remain inspectable and replaceable.

## 7. Success and failure at four analytical levels

The word “success” has different meanings at different levels. Historical games, repertoire decisions, and training
attempts must not be collapsed into one score.

| Level | What can be observed | Possible future success/failure language | What must not be claimed |
|---|---|---|---|
| Game | Reached route, played moves, result, termination, clock/context if validated, and whether source replay passed | “The game reached this route,” “the source was complete,” or “the player played the accepted move at these decision points” | The result proves the opening was good or bad, or that the player learned from the game |
| Route | Entry anchor, downstream path, branch taken, depth reached, route survival, and route-specific recurrence once classification exists | “This route was observed through depth D,” “this branch retained X of the games reaching its parent,” or “the player has attempted this route to this training depth” | Route survival proves a best line, or game attrition proves repertoire failure |
| Position | Exact four-field state, distinct-game support, occurrence count, incoming routes, outgoing moves, engine coverage, and manual assignment status | “This state recurs,” “this state has no accepted move,” “this state is shared by routes,” or “this state has these attempt outcomes” | Recurrence proves importance, a label proves identity, or lack of an attempt proves lack of knowledge |
| Move decision | Player move, accepted move snapshot, candidate evidence, engine loss where available, answer/hint/latency in future attempts | “The move matched the accepted snapshot,” “the move was an observed miss,” “the attempt was answered without a hint,” or “the response transferred across this route” | A non-preferred move is automatically a blunder, or one correct answer proves mastery |

### 7.1 Game-level success and failure

Game result, termination, rating, and time control are source facts or contextual observations. They can be used to
describe what happened after an opening route, but they cannot define opening success without a separate, explicit
objective. A win may follow a poor opening, and a loss may follow a sound opening.

Source success has a different meaning: a game replayed legally, matched its final-position evidence, and was included
in the accepted corpus. Source failure means parse, replay, identity, completeness, or acceptance failure. Those are
data-pipeline labels, not chess-performance labels.

### 7.2 Route-level success and failure

Route analysis can measure entry, continuation, branch survival, and depth. “Survival” should mean only that a route
continued to the defined next observation, not that the position was objectively good or remembered. A route can end
because the game ended, the player chose another branch, the taxonomy stopped naming, or the route definition ended.
Those causes need separate labels.

Future training route progress can record how far each route has been practiced. It must remain separate from the
shared board-state mastery of converged positions.

### 7.3 Position-level success and failure

A position is successfully observed when it is present and valid in the corpus. It is successfully classified when its
route and membership provenance are complete. It is successfully prepared for training when a manual accepted move
and any required prompt context are present. These are different preparation states.

A position-level training result can only be assessed from attempt events. Correctness may be defined against the
accepted move snapshot for that attempt, while a richer future analysis may preserve alternate legal or candidate
moves as separate evidence. No such policy is selected here.

### 7.4 Move-decision success and failure

A retrospective decision can be compared with an accepted move. A future prompted decision can record an answer,
hints, time, confidence, and context. The two should not be conflated: playing a move in a real game and answering a
prompt are different events with different exposure and pressure.

## 8. Memorisation, retention, and transfer

### 8.1 Why no training claim is possible now

The current DB has no attempt events. Game moves are not training attempts. A correct historical move can reflect
calculation, preparation, coincidence, or an unrecorded prompt, and a wrong move can reflect time pressure or a
deliberate choice. Therefore no current report may claim memorisation, forgetting, mastery, retention, or transfer.

### 8.2 Future attempt facts to preserve

Future preparation should consider append-only attempt events containing, at minimum as conceptual fields:

- attempt identity and event time;
- tracked player identity;
- exact four-field prompted training state;
- route, opening membership, anchor, and route-depth context at prompt time;
- the accepted/preferred move snapshot visible to that attempt;
- answer move in a stable legal representation and the submitted notation if useful;
- correctness classification, skipped/timeout status, and hint usage;
- response latency and any relevant timing phase;
- self-reported confidence before or after answering, if collected;
- session and repetition context;
- line endpoint or curriculum context;
- calculation/version identity used to derive any summary; and
- failure details when the attempt could not be evaluated.

This is a candidate event contract, not a schema decision. The accepted-move snapshot is important because a later
manual change must not rewrite what an earlier attempt was judged against.

### 8.3 Immediate recall

Immediate recall can compare the answer with the accepted move under a fixed prompt context. Reports should separate:

- first exposure from repeated exposure;
- no-hint answers from hinted answers;
- answer correctness from answer latency;
- confidence from objective correctness; and
- current line-endpoint questions from earlier foundation questions.

One correct answer is evidence of one successful attempt, not mastery.

### 8.4 Delayed retention and forgetting

Retention requires attempts separated by a meaningful delay. A future report could show correctness, latency, hints,
and confidence by delay band, session, route, position, and line depth. A forgetting or regression label requires a
defined time window and comparison rule; neither is selected here.

The report must account for censoring: a player who stops attempting a line provides no evidence that the line was
retained or forgotten. Missing attempts are missing evidence, not failures.

### 8.5 Transfer

Transfer can be studied at several boundaries:

- the same four-field state reached through a different move order;
- the same accepted move asked in a different opening route;
- an earlier position asked after a deeper line was practiced;
- a route branch not used during training; or
- a real-game decision after prior prompted practice.

The prompt route, move order, color, context, accepted-move snapshot, and exposure history must be preserved. A
correct answer at a transposed board may indicate shared board knowledge, route-specific cueing, or both. The analysis
must not assume that transfer is automatic merely because the four-field state is shared.

### 8.6 Mastery and pause-not-delete progression

Mastery should be treated as a replaceable summary over attempts, not a permanent raw fact. Route progress should
record the deepest reliably practiced decision point per route without deleting earlier progress when deeper work is
paused. The exact reliability definition, number of attempts, delay, hint policy, and recovery rule remain open.

## 9. Breadth, line depth, branch mass, entropy, survival, and coverage

### 9.1 Breadth

Breadth can mean several non-equivalent things:

- number of opening families or nested memberships represented;
- number of named routes entered by accepted games;
- number of distinct four-field positions reached;
- number of player decision positions with an accepted move;
- number of branches with sufficient observed support; or
- number of routes with training attempts.

A breadth report must name which one it uses. A large taxonomy catalog is not large personal repertoire breadth, and a
large number of states is not large memorised breadth.

### 9.2 Line depth

“Depth” can be measured as:

- half-move or ply depth from an anchor;
- full-move number;
- number of the player's decision points;
- number of decisions successfully practiced; or
- route-specific distance after a named opening anchor.

The progressive-training direction is decision-centric: opponent moves remain context and the player is asked at the
player's decision positions. Analytical reports should therefore expose both move context and decision depth rather
than silently substituting full-move depth for training depth.

The same exact position can be shallow on one route and deep on another. It can also be reached at different plies by
transposition. Depth is therefore route-relative even when board identity is shared.

### 9.3 Branch mass

Branch mass describes how much observed support a child branch has among the observations that reached its parent. It
can be shown globally, by player color, by opening route, by time class, by period, or by player-specific cohort.

The denominator must be visible. Candidate denominators include distinct games, occurrences, decision events, or
training attempts. These answer different questions and cannot be silently mixed.

### 9.4 Entropy-like branch dispersion

An entropy-like summary can describe whether a parent has concentrated or dispersed continuations. It is useful for
finding stable main branches, ambiguous decision points, and branches where simple frequency hides meaningful spread.

The exact formula, logarithm base, smoothing, minimum support, and interpretation are open. It must not be used as a
hidden quality score or as an automatic priority decision. Showing the underlying branch counts alongside any
summary is mandatory for a trustworthy interpretation.

### 9.5 Survival

Route survival can show the proportion of observations continuing from one route depth to the next. It should separate
at least:

- game ending;
- player choosing another legal branch;
- opponent choosing another branch;
- route classification ending;
- corpus omission or replay failure; and
- a training curriculum pausing deeper progression.

These are not one kind of attrition. A route's observed survival is not evidence that it is objectively stronger or
that a player knows it better.

### 9.6 Coverage

Coverage can compare observed player decision states or route branches with states that have a manual accepted move,
engine evidence, population candidates, or training attempts. Each numerator and denominator must be named.

Possible views include:

- observed player decision positions with versus without an accepted move;
- route depth reached versus route depth practiced;
- high-mass branches with versus without a preferred move;
- accepted moves with versus without engine/population evidence; and
- attempted positions with recent retention evidence.

Coverage is preparation coverage, not proof of chess quality or memory.

## 10. Transpositions, route context, and shared versus route mastery

### 10.1 Taxonomy transpositions

S2 preserves catalog transpositions where different source prefixes reach the same exact opening-owned position.
Reports can show the source lines, shared state, named memberships, and deepest earlier parents. A taxonomy
transposition is evidence about the opening source, not necessarily evidence that the user's games reached both paths.

### 10.2 Game-side transpositions

After neutral game classification is prepared, replay can show different game move orders reaching the same four-field
state. The report should retain each source game, route anchor, ply, incoming prefix, and player color. The state may be
shared for training while the route history remains useful context.

### 10.3 Avoiding double counting

Multiple memberships and transpositions create several legitimate views of one state. Reports should offer:

- global unique-state counts;
- opening-route counts;
- membership-inclusive counts with an explicit multi-membership note; and
- distinct-game counts.

They should not add every membership as if memberships were mutually exclusive. A “total opening positions” number is
meaningless unless its counting rule is stated.

### 10.4 Shared board mastery and route progress

The settled training direction gives one shared mastery fact to a converged exact four-field state and separate route
progress to each route. This avoids making the same board look like unrelated knowledge solely because it was reached
through different move orders.

It also creates an important analytical interaction: a player may recall the move when the route cue is familiar but
not when the same state is reached through a transposition. Attempt context must therefore be preserved even though
the board identity is shared.

## 11. Cohorts, nonstationarity, uncertainty, and sensitivity

### 11.1 Cohort dimensions

Useful descriptive cohorts include:

- calendar period or game sequence;
- time class and exact time control;
- player rating, opponent rating, and rating gap;
- player color and side to move;
- opening family, named variation, anchor, and route;
- recency relative to the current corpus end;
- result and termination as context only;
- engine profile and analysis date; and
- training exposure, delay, hint, confidence, and route context once attempts exist.

The single-player corpus is observational and strongly subject to year, time-class, rating, and preparation drift.
Recent bullet games cannot be casually pooled with older rapid games and treated as one stationary population.

### 11.2 Unit of analysis

Repeated occurrences from one game are not independent samples. A report should state whether its unit is:

- an accepted game;
- a distinct game reaching a state;
- a position occurrence;
- a move-decision event;
- a route event; or
- a training attempt.

When uncertainty is calculated, dependence by game and repeated attempts by session should be considered. The choice
of clustering or resampling method remains open.

### 11.3 Uncertainty presentation

Every rate, share, or comparison should show support and an uncertainty treatment appropriate to its unit. Candidate
approaches include conservative interval estimates for proportions, resampling at the game rather than occurrence
level, or support tiers such as anecdotal, emerging, and established. No interval method or support-tier policy is
selected here.

Small samples should be visible rather than silently hidden. A table may show all branches with warnings, hide only
below a human-approved display floor, or use support tiers. That is a presentation decision for later grilling.

### 11.4 Sensitivity analysis

Results should be checked against plausible alternative choices, including:

- game count versus occurrence count;
- all history versus recent windows;
- raw versus recency-weighted support;
- rating-proximity bands;
- bullet/blitz/rapid separation;
- inclusion or exclusion of low-support branches;
- one membership versus membership-inclusive display, without changing raw facts;
- alternative route-depth definitions;
- alternative harmful-move thresholds;
- engine profile and stale-result handling; and
- hint-free versus all-attempt training outcomes.

The output should identify which conclusions remain stable and which change under reasonable choices. Sensitivity is
not a license to pick the result that looks best; the candidate choices and their rationale must remain visible.

### 11.5 Multiple comparisons and causal limits

Thousands of states and branches create many opportunities for accidental patterns. The initial direction is
descriptive, not formal causal hypothesis testing. If later work introduces formal tests, it must separately decide
the comparison family, correction policy, pre-registration or exploratory label, and causal assumptions.

Even a stable association does not establish that an opening move caused a result. A training intervention changes
which positions are practiced and which future games are played, creating feedback that must be recorded rather than
ignored.

## 12. Engine and population evidence boundaries

### 12.1 Engine evidence

Engine evidence is a candidate and explanation channel. It can provide:

- ranked candidate moves under recorded settings;
- typed scores and mate information;
- principal variations and first moves;
- evaluation of the resulting exact six-field position; and
- evaluation loss relative to the engine's candidate from the exact starting FEN.

It cannot provide the user's preferred move automatically. It also cannot erase uncertainty arising from finite
search budgets, MultiPV ordering, profile changes, stale results, partial coverage, or provenance gaps.

The accepted MP-09 evidence established a fixed qualified profile for its own analysis namespace, but this synthesis
does not choose a future harmful-move policy, engine coverage plan, or replacement profile. Any engine comparison
must identify engine version, binary identity, settings, score representation, result date, and exact six-field FEN.

### 12.2 Population evidence

Lichess Explorer-style aggregates can report move frequency and outcome context for a defined position, rating group,
speed, and date window. The selected population direction is realistic online play rather than an exclusively elite
corpus, but the exact cohort and acquisition policy remain open.

Population evidence can:

- suggest common responses;
- expose branches the personal corpus has not seen;
- compare observed personal choices with an external reference; and
- help identify candidate lines for manual review.

It cannot define the player's adaptive frontier, select a preferred move, establish causality, or generalize to every
player. Aggregate Explorer data is not a substitute for a filtered raw-game corpus. Licensing, credentials, caching,
refresh, and raw-game acquisition are future decisions.

### 12.3 Keeping the evidence channels separate

A useful candidate report should show personal recurrence, population frequency, engine candidate/evaluation, and
manual accepted move in separate columns or panels. A single combined score is explicitly not selected because it
hides trade-offs and embeds arbitrary weights.

The final authority remains the user. The population and engine channels inform a decision; they never make it.

## 13. Future storage and preparation candidates

The following are future durable-fact candidates, not selected schemas. They are listed so later Plans can evaluate
ownership, identity, provenance, retention, and rebuild behavior before implementation.

### 13.1 Manual preferred-move assignment history

Consider an append-only history for each manual assignment containing:

- player UUID;
- exact four-field state;
- accepted move representation;
- assignment time and source context;
- optional human rationale or note;
- validity or supersession relationship;
- taxonomy/route context used when assigning it; and
- a durable assignment version referenced by later attempts.

The history should allow a later calculation to answer “which accepted move was authoritative when this game or
training attempt occurred?” without rewriting old evidence.

### 13.2 Training-attempt events

Use the candidate event facts in Section 8.2. The event should be immutable enough to preserve prompt context,
accepted-move snapshot, answer, hints, latency, confidence, timing, session, and route context. Current mastery,
priority, retention curves, and frontier status should be derived from those events.

### 13.3 Neutral game-opening anchors and route facts

Future S3 preparation should preserve every exact named opening reached by an accepted game, its source membership,
anchor position, anchor ply, game provenance, and downstream route facts. It should support multiple memberships and
transpositions without letting a player-specific projection alter neutral truth.

### 13.4 Analysis and population provenance

Engine results need exact six-field identity, profile/settings identity, engine binary/version evidence, result time,
run identity, failure state, and replacement/staleness history. Population snapshots should identify source, request
filters, rating bands, speeds, date range, retrieval time, response version if available, and licensing/credential
boundary without storing secrets.

The current 3,075-row mismatch demonstrates why result content alone is not sufficient provenance.

### 13.5 Raw source and parser provenance

Raw PGNs, source game identity, fetch manifest, corpus fingerprint, replay/parser version, opening manifest, taxonomy
version, and clock-parser version should remain identifiable. Derived clock values, route labels, and normalized reports
should point back to the raw source and the calculation run that produced them.

### 13.6 Rebuildable views and caches

Keep these as rebuildable views or caches rather than irreplaceable facts:

- recurrence and branch counts;
- branch mass and entropy-like summaries;
- route survival and depth curves;
- global and route-specific coverage;
- repertoire-miss, harmful-move, and coverage-gap queues;
- adaptive-frontier membership;
- priority scores;
- current mastery and retention summaries;
- route progress and line-endpoint summaries; and
- report or visual caches.

If a cache is retained for speed, its source fact versions, calculation version, and invalidation state should be
visible. Cache retention must not make an old formula appear to be a raw fact.

### 13.7 Retention and versioning choices

Later work must decide how long to retain:

- original source rows and raw PGN;
- excluded and failed source records;
- old taxonomy manifests;
- old manual preferred moves;
- engine results made stale by profile changes;
- population snapshots;
- training attempts and failed attempts; and
- derived report runs.

The safe default for design discussion is to retain raw facts and mark calculations stale rather than deleting
history. A later retention policy may define privacy, storage, and cleanup exceptions, but it must not silently erase
the evidence needed to interpret historical training results.

### 13.8 Backup and audit preparation

`data/database/chess_games.db` is valuable, prepared, untracked runtime data. It must remain uncommitted and must be
read or copied only under an explicitly safe, read-only or authorized bounded workflow. Before any future authorized
write, preparation should consider an independently verified backup, integrity and foreign-key checks, a lock and
active-writer check, file hash/size/mtime capture, and pre/post table signatures. This is preparation guidance, not
permission to write the DB now.

## 14. Possible staged analytical products

These are possible analytical slices, not an implementation sequence or authorization. Each would need its own
assessment, and any durable data or product behavior would need fresh decisions.

### Stage A — Read-only corpus observatory

Show fetched versus accepted denominators, corpus completeness, state/occurrence counts, opening-owned versus
game-derived boundaries, engine coverage, provenance categories, and source-quality warnings. This stage can be
entirely descriptive and is the safest immediate analytical product.

### Stage B — Exact-state recurrence and branch report

Show recurring four-field states, continuation branches, conditional mass, entropy-like dispersion, context cohorts,
uncertainty, and route-independent transposition evidence. It should not claim player repertoire gaps until manual
assignments and neutral route facts exist.

### Stage C — Neutral opening classification and route report

Build on S1 and S2 with S3 neutral game classification: every named opening encountered, anchor, provenance, multiple
memberships, and downstream route. This enables route survival, route recurrence, and taxonomy-aware reports without
yet choosing player priority or training behavior.

### Stage D — Authoritative events and rebuildable aggregates

Build on S3 with S4 event facts and deterministic projections for global and route recurrence, parent/child branches,
color, chronology, result, and rating context. No frontier, priority, formula, or threshold is implied.

### Stage E — Tracked-player projection

Build on S3/S4 with S5 projection through the stable player UUID. This makes player color, personal recurrence, and
observed routes inspectable while neutral facts remain independent. It does not yet establish a training outcome.

### Stage F — Manual repertoire evidence and three queues

After a preferred-move history is deliberately designed, compare historical player moves with accepted snapshots and
derive repertoire-miss and coverage-gap evidence. Harmful-move evidence may be attached where engine identity and
coverage are sufficient. Queue labels remain explainable and non-destructive.

### Stage G — Separate engine and population candidate reports

Show engine and population alternatives alongside personal recurrence and manual authority. This stage should first
repair or classify analysis provenance and should preserve profile/date/cohort caveats. It must not auto-select a move.

### Stage H — Training event and retention reports

After attempt events exist, show immediate recall, delayed retention, hints, latency, confidence, transfer, and route
progress. This is the first stage where trained-recall language could be considered, and even then only with explicit
event definitions and uncertainty.

### Stage I — Adaptive frontier, priority, and progressive depth

Only after raw events and projections are trustworthy could a later design evaluate frontier hysteresis, priority
factors, mastery summaries, route depth, and pause-not-delete curriculum behavior. These calculations should remain
replaceable and should not alter the underlying event record.

## 15. Suggested reports and visual outputs

These are report concepts, not UI requirements. A later design may select tables, static documents, charts, or an
application surface according to its own accessibility and interaction review.

### 15.1 Evidence and audit reports

- **Corpus ledger:** fetched, accepted, excluded, occurrence, state, source, and run counts with denominators.
- **Namespace ledger:** four-field training states, six-field analysis FENs, opening-owned endpoints, and queue rows
  shown separately.
- **Provenance ledger:** result roots grouped by directly attributable, queue-attributable, profile-only, and
  unresolved audit status.
- **Source-quality report:** replay failures, malformed FENs, clock-parser validation, accuracy coverage, duplicate
  source identity, and stale schema warnings.

### 15.2 Repertoire and branch reports

- **State detail table:** state identity, player side, game support, occurrence support, incoming routes, outgoing
  branches, current accepted-move status, engine coverage, and uncertainty.
- **Branch table:** parent, child move, distinct games, occurrences, conditional mass, cohorts, and support tier.
- **Opening graph:** named anchors, nested memberships, transposition links, and routes, with multi-membership counts
  made explicit.
- **Coverage matrix:** observed player decision positions by route depth and accepted-move status.
- **Three-queue report:** repertoire misses, harmful-move evidence, and coverage gaps with separate evidence columns.

### 15.3 Depth and convergence reports

- **Route survival curve:** route continuation by decision depth, with game ending and branch-change causes separated.
- **Breadth/depth table:** number of observed routes, states, accepted decisions, and attempted decisions by depth
  definition.
- **Transposition convergence map:** different prefixes meeting at shared states, with route-specific progress shown
  separately from shared board state.

### 15.4 Training reports

- **Attempt timeline:** answer, hint, latency, confidence, accepted-move version, and route context.
- **Retention view:** correctness and delay bands with censoring and support visible.
- **Transfer matrix:** same state across move orders/routes, with prompt context and exposure history.
- **Progress view:** current line endpoint, earlier foundation checks, paused depth, and route-specific progress, never
  deleting prior progress.

Any visual should retain a textual table or accessible equivalent. A chart that hides denominators or uncertainty is
not sufficient evidence.

## 16. Second pass — what the first pass misses

This section is deliberately a second scouting pass after the main analytical outline. It surfaces interactions and
edge cases that are easy to miss when recurrence, engine evidence, and training are considered separately.

### 16.1 Training changes the future sample

Once the player trains a branch, future attempts and future games are no longer an untouched observation of the old
state. A later improvement may reflect training, changed time control, changed opponent, changed opening choice, or
natural variation. Training sessions and manual interventions must therefore be recorded as events if before/after
comparisons are ever considered.

### 16.2 Shared state does not mean shared cue

The four-field state can be identical while the move-order prefix, opening name, opponent response, and line depth
differ. Shared board mastery and route progress are intentionally separate, but transfer analysis must also preserve
the cue that led to the board. Otherwise a route-specific memory effect will look like a board-knowledge effect.

### 16.3 The accepted move can change after the attempt

A later manual change can make an old answer appear wrong if the system compares it with the current move. Attempt and
game comparisons therefore require the accepted-move snapshot and its validity, not only the current preferred move.

### 16.4 A harmful move and a repertoire miss can disagree

The player may choose a non-preferred move that is objectively comparable to the preferred move, or may play the
preferred move despite a large engine loss under a later profile. The queues answer different questions and should
remain separate. A single “mistake” label loses that distinction.

### 16.5 Counterfactual engine comparisons are fragile

The before-move engine result and after-move engine result may differ because of profile, version, node budget, mate
handling, WDL, or stale replacement rather than because the move changed the position. A future comparison needs
matched provenance and should report unresolved comparison status rather than fabricate a loss.

### 16.6 Branch mass can hide the branch worth learning

A main branch may have high population mass but be easy for the player, while a low-mass branch may recur in the
player's own games and repeatedly cause misses. Global frequency, personal recurrence, conditional branch mass, and
mistake persistence must be visible together.

### 16.7 Survival can be confused with abandonment

A route ending can mean game termination, a legal move into an unnamed continuation, a taxonomy boundary, a player
choice, an opponent choice, or missing data. Route survival needs event causes before it can guide coverage.

### 16.8 Membership-inclusive counts can exaggerate breadth

A position under a broad family and two nested variations may be counted three times in a taxonomy report while being
one four-field training state and one game occurrence. Every visual and summary needs an explicit counting mode.

### 16.9 Cumulative corpus counts obscure current behavior

The accepted corpus spans strong time-control and period differences. A large historical recurrence can be irrelevant
to the current repertoire if it belongs to an old phase. Recent windows and full-history views should be compared, not
silently substituted.

### 16.10 Rating proximity is not a neutral adjustment

Rating proximity can make a route more personally relevant, but it is correlated with date, time class, opponent
selection, and perhaps preparation. It should remain an explicit cohort or sensitivity dimension until a weighting
policy is chosen.

### 16.11 Clock data can create false precision

An annotated clock value can be precise as text but not comparable as thinking time. Increment handling, server delay,
source formatting, and missing move annotations can all create false confidence. Raw clock text, parser status, and
derived value should be distinguishable.

### 16.12 Accuracy is a selected subset, not a ground truth

Chess.com accuracy is present for only 1,528 games and its calculation context is not a complete training outcome.
Using it as a validation target could select games with different source characteristics and should be treated as a
subset analysis.

### 16.13 Fetched, accepted, and analyzed are three different populations

Fetched games include four excluded rows. Accepted occurrences include only standard subject games. Engine results
cover exact six-field roots, not all four-field states or all occurrences. A report that joins these without showing
the denominators can make partial coverage appear complete.

### 16.14 Provenance gaps can bias conclusions

If the 3,075 result mismatch is not resolved, engine-covered states may not be a random or known sample. Any analysis
using them should show an “attributable versus unresolved” split and avoid interpreting coverage as a deliberate
opening-selection policy.

### 16.15 Population evidence can be misread as personal need

A common population move may be absent from this player's games because the player never reached that route. The
player-only frontier rule prevents population data from expanding the tracked frontier silently. Population evidence
can still be shown as an external candidate channel.

### 16.16 Training prompts can leak the answer

Showing engine lines, opening names, SAN, arrows, or a familiar route immediately before an attempt can change its
meaning. Prompt exposure, hints, prior screen state, and repeated same-session attempts must be recorded if retention
is ever measured.

### 16.17 Correctness can be policy-dependent

An answer may be legal and objectively strong but differ from the one accepted by the user. Conversely, an answer may
match the accepted move in SAN while representing a different context if the identity or move parser is wrong. The
accepted-move snapshot, legal move identity, and comparison policy must be visible.

### 16.18 Depth can be inflated by opponent moves

A line with many plies may contain few player decisions. Training depth should preserve both ply depth and decision
depth, and route depth should not be inferred from full-move numbers alone.

### 16.19 Stale assignments and permanent opening classification interact

The initial direction treats opening assignment as permanent, while future taxonomy updates or reclassification remain
open. If taxonomy records change later, reports need the assignment version that created them rather than silently
relabeling historical routes.

### 16.20 Rebuilds can change the report without changing the facts

Changing recency weights, support thresholds, engine eligibility, or mastery formulas may change queues and frontier
views while leaving raw events unchanged. That is expected only if calculations are versioned and old results remain
auditable.

### 16.21 Additional opportunities surfaced by the second pass

Later grilling may consider:

- calibration of confidence against actual attempt correctness;
- separate “recognition,” “recall,” and “transfer” prompts;
- route-specific versus state-specific error persistence;
- player move-time and confidence as context for harmful-move evidence;
- counterfactual candidate reports that keep engine, population, and manual evidence separate;
- branch novelty and frontier expansion from the player's own new games;
- intervention-aware before/after summaries with explicit non-causal language;
- line compression where many routes converge on one shared continuation; and
- a provenance completeness score that never pretends unresolved records are absent.

These are opportunities, not selected features or formulas.

## 17. Open decisions

The following decisions remain intentionally open. The alternatives and evaluation criteria are recorded so later
grilling can choose deliberately rather than allowing implementation to choose by accident.

### 17.1 Repertoire authority

- Is exactly one accepted move per state sufficient for the initial workflow, or are alternatives and context-specific
  moves required?
- What history and reason should be retained when a user changes the accepted move?
- Should an accepted move be valid globally across all routes, or can a later product introduce route-specific
  preferences without violating shared-position authority?

Evaluate against transposition simplicity, user control, historical auditability, training comparison stability, and
the risk of hiding legitimate alternatives.

### 17.2 Queue definitions and priority

- What support rule makes a recurring state a coverage gap?
- What objective comparison and threshold make a move harmful?
- How should a repertoire miss, harmful move, and coverage gap coexist?
- Should priority use recurrence, recency, rating relevance, mistake persistence, engine loss, and amount trained as
  separate sortable evidence or as a replaceable combined calculation?
- What entry, retirement, and hysteresis policies prevent frontier churn?

Evaluate against explainability, sensitivity, false positives, rare-branch protection, and manual override.

### 17.3 Route and classification semantics

- What exactly counts as an encountered opening and a downstream route in S3?
- How should non-Caro move orders be treated in the player's projection?
- Should opening assignment remain permanent indefinitely or receive a future versioned rebuild path?
- How should multiple taxonomy memberships appear in route totals without double counting?

Evaluate against replay provenance, transposition fidelity, stable historical reports, and denominator clarity.

### 17.4 Breadth, depth, and survival

- Which depth measures are primary: plies, full moves, player decisions, route distance, or training endpoints?
- Should breadth be reported by states, routes, memberships, accepted decisions, or attempted decisions?
- How should route survival distinguish game termination, branch changes, classification boundaries, and missing data?

Evaluate against human interpretability, transposition handling, and whether the measure answers a repertoire or a
training question.

### 17.5 Training measurement

- What is a correct answer: exact accepted move, legal equivalent, accepted alternative, or a future policy?
- Which hints, timing, confidence, and prompt contexts define immediate recall?
- What delay and comparison rule define retention or regression?
- What evidence is sufficient for transfer across move orders and routes?
- How is line extension allowed after reliable recall, and how is paused progress resumed?

Evaluate against event completeness, cue leakage, user authority, route/state separation, and censoring.

### 17.6 Statistics and uncertainty

- Which unit receives uncertainty: game, distinct game-state pair, occurrence, decision, route, or attempt?
- Which interval, resampling, clustering, or support-tier method is appropriate?
- What minimum support policy should be shown, hidden, or warned?
- Which cohort and sensitivity views are required before a comparison is considered stable?
- When would formal hypothesis testing be justified, if ever?

Evaluate against dependence, nonstationarity, multiple comparisons, readability, and false certainty.

### 17.7 Engine evidence

- How should the 3,075-row provenance mismatch be reconciled and classified?
- Which analysis profile, settings, score normalization, mate treatment, and stale-result policy apply to future
  harmful-move comparisons?
- What exact before/after evidence is required for a comparable evaluation loss?
- When is engine coverage sufficient for a report, and how should unresolved coverage be displayed?

Evaluate against reproducibility, runtime cost, profile identity, provenance completeness, and manual authority.

### 17.8 Population evidence

- Which rating bands, speeds, date ranges, and population source are relevant?
- When do aggregate statistics justify selective raw-game acquisition?
- How should source licensing, credentials, caching, refresh, and stale population snapshots be handled?
- How should population evidence be displayed without expanding the player-only frontier?

Evaluate against relevance, licensing, cost, reproducibility, domain shift, and separation from personal facts.

### 17.9 Storage, retention, and audit

- Which raw facts are immutable, and which derived facts may be rebuilt or cached?
- How are manual moves, attempts, engine runs, population snapshots, taxonomy versions, and calculation versions
  identified over time?
- How long are stale engine results and old accepted-move versions retained?
- What backup, integrity, lock, and recovery evidence is required before a runtime write?
- How is the valuable untracked DB protected without implying that it belongs in source control?

Evaluate against recoverability, storage cost, privacy, auditability, and preservation of historical meaning.

### 17.10 Reports and presentation

- Which reports are tables, graphs, static documents, or a future product surface?
- How are denominators, uncertainty, multiple memberships, stale evidence, and unresolved provenance made prominent?
- What textual and accessible equivalent accompanies each visual?

Evaluate against decision usefulness, accessibility, cognitive load, and the risk that a visual compresses away a
caveat.

## 18. Safe conclusion

The prepared corpus is already capable of supporting a valuable observational opening laboratory. It can expose exact
state recurrence, branch mass and dispersion, move-order convergence, taxonomy relationships, player-side and
time-control context, and carefully bounded engine or population candidate evidence. The accepted S1/S2 foundation
also provides the ownership and provenance discipline needed to build neutral route facts without corrupting the
game-derived corpus.

The most important missing facts are not another score or a more persuasive label. They are:

1. complete neutral game-route classification;
2. durable manual preferred-move history;
3. auditable engine and population provenance;
4. append-only training attempts with accepted-move snapshots and prompt context; and
5. versioned, rebuildable calculations for recurrence, frontier, priority, mastery, retention, and line depth.

Until those facts exist, the safe product language is “observed,” “candidate,” “under this profile,” “reached,”
“compared,” and “attempted.” It is not “best,” “caused,” “mastered,” “forgotten,” or “trained.” Any later focused Plan
must select only one bounded outcome from this evidence, preserve the four-field/six-field namespace boundary, keep
manual authority with the user, and escalate rather than deciding an open product, formula, data, engine, or
acceptance question.

## Evidence references

- [Documentation Router](../README.md)
- [Static Position to Analysis Roadmap](static-position-to-analysis-roadmap.md)
- [Opening Position Pattern Discovery](opening-position-pattern-discovery.md)
- [Opening Classification Database Foundation](opening-classification-database-foundation.md)
- [Personal Opening Classification and Progressive Line Training](opening-classification-and-progressive-training.md)
- [MP-10 Browser Evaluation](mp10-browser-evaluation.md)
- [Opening Classification Database Preparation master plan](../master-plans/opening-classification-database-preparation.md)
- [S1 Source Catalog Plan](../plans/done/s1-source-catalog/s1-source-catalog.md)
- [S2 Opening Relationships Plan](../plans/done/s2-opening-relationships/s2-opening-relationships.md)
- [MP-06 Validated FEN Corpus Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md)
- [MP-09 Persisted Backend Stockfish Analysis Plan](../plans/done/mp09-persisted-backend-stockfish-analysis/mp09-persisted-backend-stockfish-analysis.md)
- [MP-10 Browser Evaluation Plan](../plans/done/mp10-browser-evaluation/mp10-browser-evaluation.md)

The current runtime database and the tracked `data/database/schema.txt` are deliberately not treated as committed
documentation authority. The runtime DB was inspected read-only for the current counts in Section 2 and remains
valuable untracked data to preserve.
