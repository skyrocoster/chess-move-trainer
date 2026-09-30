# Part 2 — Statistical analysis and the limits of the chess data

> **Status: implementation in progress — authorized by the user's “Implement” request.**
> Written 2026-09-22. See the implementation checkpoint below for actual completion and proof.

- **Read trigger:** Read before reviewing or implementing Part 2 feature extraction, statistical models, question registration, evidence reports, or finding promotion.
- **Direction:** [Chess learning workflow](../../grilling-docs/chess-learning-workflow-2026-09-21.md), especially Part 2 and the appendix.
- **Required inventory:** [Chess analysis idea catalogue](../../grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md). Its complete inventory remains in scope for disposition; this Plan does not silently replace it with a smaller selection.
- **Prerequisite:** [Completed Part 1](../done/chess-learning-part-1-analysis-infrastructure.md). Its worker can continue collecting coverage while Part 2 is reviewed and later built.
- **Current authorization:** Implement directly, without subagents; update this Plan regularly. Adopt the recommended v1 numerical definitions, retain definition-blocked complex motifs, and do not bypass calibration/promotion gates.

## 1. Purpose and success

Determine how much trustworthy information the stored games can provide about the learner's decisions and responses to opponents. Test broadly, but make it equally possible to conclude that a question is answerable, too uncertain, badly measured, or impossible with today's data.

Examples of useful outcomes:

- A reliable description: “Pawn moves account for X% of eligible learner moves.”
- An adjusted association: “In this defined population, this capture category is associated with an estimated X percentage-point increase in severe-loss risk.”
- A precision limit: “There are enough games to rule out a large difference, but not a small one.”
- A support limit: “This category appears in many moves but only a few independent games.”
- A measurement limit: “The stored candidate lines cannot establish whether this was the only sound legal move.”
- An unavailable question: “The data cannot show whether time pressure caused these errors.”

No numbers in these examples are findings. Success is not a required number of discoveries. A valid run with no promoted associations is an acceptable result. A broken or uncalibrated analysis pipeline is not.

### Three separate deliverables

1. **Supported findings catalogue:** only descriptions and associations meeting their approved gates; every entry identifies its claim type and population.
2. **Complete diagnostic ledger:** every registered question, including failures, inconclusive results, unsupported definitions, and unavailable data. This is a backend review artifact, not a list of possible learner weaknesses.
3. **Data-limit report:** coverage, effective independent support, smallest detectable effects, measurement gaps, sensitivity failures, and what additional observations could resolve each limitation.

The user and an AI may review methods, definitions, code, and evidence. AI must not supply chess explanations, motif labels, causal stories, or conclusions outside the deterministic/statistical outputs.

## 2. Fixed boundaries

- Separate learner moves from opponent moves throughout extraction, denominators, inference, and reporting.
- Pool valid current quick and full rank-one results normally. Do not exclude or down-weight full results, create a separate full-result confirmation population, or require full upgrades for ordinary move-quality findings.
- Keep quality, settings, and engine identity as provenance. Questions needing several candidate lines have their own explicitly restricted population.
- Use deterministic, versioned chess rules. A geometric relationship is not automatically a successful tactic or an explanation of an error.
- Use GEE (generalized estimating equations) for adjusted move-level population-average associations and whole-game bootstrap for uncertainty and stability. Additional dependence checks are specified below.
- No AI-generated labels, lessons, exercises, frontend integration, new public HTTP endpoint, or training-effect claims.
- No automatic engine reruns, full-analysis upgrades, database rebuilds, worker changes, or new data collection under this Plan.
- No live application schema migration by default. Derived research outputs go to separate, versioned local artifacts; product storage can be decided in Part 3.
- Do not alter historical grilling records, completed Plans, or unrelated worktree changes.

## 3. Repository grounding and known constraints

These facts were checked in source while planning; corpus counts have not been refreshed.

| Source | Relevant contract or limit |
|---|---|
| `src/chess_move_trainer/database/schema_v2.sql` | Games store original PGN, colour, IDs, nullable ratings/timestamps/outcomes, termination, and time control. Missing metadata needs an explicit policy. |
| Same schema, `derived_game_position` | Ordered occurrences, outgoing move, halfmove clock, and fullmove number allow before/after pairing and replay. A unique position is not an independent move or game. |
| Same schema, `derived_position` | Canonical identity has placement, side, castling rights, and legal en passant; it omits counters and repetition history. |
| Same schema, analysis tables | One current result per canonical position, White-perspective WDL as documented by the workflow, ranks 1–5, quality/settings/engine provenance. Historical overwritten results are unavailable. |
| `database/stockfish/engine_helpers.py::_fen_for_position` | Engine roots use counters `0 1`; `_classify_terminal` recognizes checkmate, stalemate, and insufficient material. Stored evaluation is not a history-aware evaluation of every occurrence. |
| Same schema, preferred-move periods/training aggregate | Preferences have effective dates; training balances are not individual attempt histories. |
| `pyproject.toml`, `requirements.txt` | Python 3.12 and python-chess are present; NumPy/SciPy/statsmodels are not yet declared. Dependencies would require compatible pinned versions and normal lock/export updates. |
| Completed Part 1 Plan | Quick is 200,000 nodes/SinglePV; full is 6,400,000 nodes/MultiPV 5. Both contribute rank-one outcomes. |

The historical appendix describes reusable blunder-scoring behavior, but `database/blunders/scoring.py` is no longer present at review time. Treat the appendix as a behavioral reference, not an existing module to import or a reason to restore the retired endpoint.

The earlier 12,710-game workload is planning context only. Stage 1 must identify the authoritative database and recount it; do not assume the historical `data/database/chess.db` path is the live Docker volume database.

### Intended ownership, not files created by this draft

- New backend analysis package proposed at `src/chess_move_trainer/statistical_analysis/`, split by snapshot, records, features, registry, models, validation, and reporting responsibilities.
- Focused tests proposed under `tests/statistical_analysis/`.
- Reuse existing database connection/read contracts, canonical position validation, opening recognition, and date-effective preference behavior after inspecting their owners during implementation. Do not duplicate them by default.
- Version-controlled definitions/protocols belong with the analysis package; approved human-readable methodology belongs under `docs/`. Snapshots, fitted results, sample exports, and run logs belong in an explicitly ignored local artifact directory, not Git.
- A finite offline Python command is sufficient. Do not make normal API requests fit models or run bootstraps.

## 4. Snapshot, provenance, and audit contract

### Frozen input

1. Identify the authoritative source, schema version, learner identity, date range, and permitted game variants. Default scope is standard chess; report unsupported variants and malformed games separately.
2. Obtain a transactionally consistent SQLite backup/snapshot through a safe read procedure. Do not copy an open SQLite file without accounting for its journal/WAL, replace the live database, or keep a long read transaction open throughout modelling.
3. Freeze games, occurrences, openings, preference periods, and complete current analysis results together. Compute a content identity; record code revision plus dirty-state identity, dependencies, rule versions, configuration, seeds, and snapshot time.
4. Run every model and report from that immutable snapshot. Worker publications after the snapshot belong to another run, not a partially refreshed report.
5. Persist enough source/provenance evidence to reproduce each result even after live full analysis replaces quick analysis. This is a frozen research snapshot, not a new live engine-history feature.

### Audit before outcome searching

- Count games, learner/opponent moves, unique positions, independent games per category, repeated opponents, opening concentration, date coverage, and time-control classes.
- Verify UUID duplication and detect duplicate game content imported under different IDs; do not silently discard merely similar games.
- Replay moves; check legality, outgoing-move pairing, consecutive ply order, final position, counters, castling, en passant, promotions, and PGN/derived-row agreement.
- Distinguish genuinely unavailable values from invalid values, excluded games, terminal positions, and failed validation. Quarantine invalid records with reason counts; never repair them silently to help a result pass.
- Audit WDL sums/ranges, score perspective, legal PV roots, profile completeness, terminal classification, and before/after analysis provenance.
- Parse time controls without guessing; distinguish increment, non-increment, daily, unknown, and unsupported formats. Duration or UTC hour is not thinking time, time pressure, or the user's local hour.
- Inspect whether PGN clock tags exist only as an availability count, if needed. Their presence does not authorize clock extraction or make clock-based questions supported in v1.
- Audit preference date boundaries and game-time normalization. No matching preference means “not covered,” not “non-adherent.”

Report a denominator waterfall: total → scope-eligible → structurally valid → feature-eligible → outcome-comparable → model-complete. Reconcile every exclusion by reason and by learner/opponent population. Count overlapping missing reasons separately from the mutually exclusive primary exclusion reason.

## 5. Outcome and feature definitions to review

The following are recommended v1 starting points, **not previously approved facts**. Stage 0 must resolve and freeze them before outcome analysis. Definitions can be rejected without blocking review of the rest of this Plan.

### Engine-backed outcomes

- White expected score: `Ew = (wins + 0.5 * draws) / 1000`; Black expected score: `1 - Ew`.
- For the mover, retain signed change `D = E_before - E_after`, plus nonnegative loss `L = max(0, D)`. Positive `D` means deterioration. Preserve negative values as engine inconsistency/improvement diagnostics rather than silently deleting them.
- Example: White `0.65 → 0.40` gives `D = L = 0.25`. The same White scores on a Black move imply Black `0.35 → 0.60`, so `D = -0.25` and `L = 0`.
- Proposed severe-loss threshold: `L >= 0.20`, inclusive, with `0.10` and `0.30` as fixed sensitivity thresholds. The old endpoint's `0.20` is not approval for this choice. Evaluate thresholds before rounding.
- The two-part outcome is `P(L > 0)` and `E[L | L > 0]`, combined into marginal expected loss. Audit WDL quantization and near-zero changes; a fixed small dead-band sensitivity must be registered rather than selected for significance.
- An after-position that is checkmate, stalemate, or insufficient material receives deterministic mover-perspective scoring. A before-position terminal has no eligible outgoing move.
- Do not replace the last position evaluation with the recorded game result: resignation, timeout, draw agreement, and abandonment are separate game-outcome facts.
- Replay can identify repetition/fifty-move claim eligibility and automatic draw conditions. Canonical engine roots cannot recover this history. Flag such occurrences, quantify their contribution, and withhold claims requiring history-aware engine evaluation. Any primary exclusion must be approved and counted; never silently rewrite stored WDL.
- Stockfish expected score is an engine measurement, not a calibrated probability that this learner will win. Calibration against game results is a separate diagnostic, not a reinterpretation of the engine's meaning.

### Proposed deterministic conventions

| Item | Recommended v1 rule or boundary |
|---|---|
| Material values | Pawn 1, knight/bishop 3, rook 5, queen 9; king excluded from material sums. Material balance is not positional advantage. |
| Phase | Opening through ply 20 inclusive; after that, endgame when total non-pawn, non-king material is at most 13, otherwise middlegame. This is an operational label. Register boundary sensitivities, e.g. ply 16/24 and material 10/16. |
| Regions | State exact square sets. Central core `d4/e4/d5/e5`; files a–d queenside, e–h kingside; rank/direction features are colour-relative. |
| Attack/defence | Keep geometric attacks, legal captures, and absolute pins separate. A geometric defender may be pinned. “Attacked and undefended” is a board relation, not proven material loss. |
| Piece identity | Track each original piece through replay, including promotions, rather than equating “same piece type” with “same piece.” |
| Capture denominators | Report both share of all moves and share of captures. Include en passant's actual captured pawn and promotion's moving pawn identity. King-as-captured-piece cells are impossible, not missing observations. |
| Opportunity denominators | “Chosen capture rate” differs from “capture chosen when a legal capture existed.” Register both. Availability is not evidence that the unchosen move was sound. |
| Immediate opponent response | One opponent move paired with the learner's next move; games ending before a response have no response outcome. No outcome imputation. |
| Longer response episodes | Proposed secondary horizon: next three learner moves. Earliest qualifying trigger owns the window; skip overlapping triggers, record censoring, and do not count overlapping windows as independent episodes. |
| Early opponent behaviour | Fixed first ten opponent moves for an early-style summary. Games ending before that landmark are reported separately, not filled with zeros. Prefer continuous shares over arbitrary “high/low” bins. |
| Volatility | Primary per-game median absolute deviation of signed learner-perspective evaluation changes in a fixed eligible segment; report segment length and coverage. Do not compute from a loss-clipped series. |
| Advantage/conversion | Proposed landmark: first observed learner expected score at least 0.80 after the opening. Game result is the conversion outcome; distinguish score rate from outright win rate. |
| Collapse/recovery | Proposed collapse: severe loss followed by another within three learner moves; recovery: return within 0.05 of pre-trigger expected score within five learner moves. These are observed sequences, not mental-state labels; censor unfinished windows. |
| Sound stored alternatives | Proposed WDL distance at most 0.02 from rank one, using consistent mover perspective at the same root. Report count **among stored candidates**, not among all legal moves. |

Every complex feature needs positive examples, counterexamples, boundary cases, exact observation time, and a unit-tested rule. Relative pins, overload, deflection, sacrifices, “initiative,” “good/bad bishop,” and similar terms must either receive precise limited rules or remain definition-blocked. Do not force all errors into motifs. Prefer literal output labels such as “bishop captures an absolutely pinned knight.”

## 6. Versioned question registry and expanded test programme

### Registry contract

Each original catalogue bullet receives a stable question ID and one disposition: registered now, descriptive only, definition-blocked, data-unavailable, or deferred with an explicit reason. None disappear merely because they produce no interesting results.

Before testing, each inferential question records:

- Feature/rule version; learner or opponent population; unit (move, episode, game, period); numerator and denominator.
- Exact exposure timing, outcome, comparator, direction (two-sided by default), null, meaningful-effect threshold, and target population.
- Adjustment set, model/link, clustering/resampling, category pooling, missingness policy, support requirements, and permitted interactions.
- Multiplicity family, all contrasts/cutoffs/windows, uncertainty method, sensitivity tests, promotion gates, seed/budget, and stopping rules.
- Source catalogue mapping, prerequisites, expected limitations, and fixed reporting template.

Do not run every feature against every outcome and every subgroup automatically. Register a bounded contrast list. A broad inventory is useful; an unbounded search through combinations is not.

### Question families

| ID | Family and principal questions | Required limit checks |
|---|---|---|
| Q01 | **Move inventory:** piece mix, square/region/distance/direction, quiet/capture/check, special moves, legal-choice count, recurring-position diversity. | Move-weighted versus game-weighted estimates; colour mirroring; opportunity-conditioned rates; zero/rare cells. |
| Q02 | **Capture matrix:** every legal mover × target pair, including bishop × pawn/knight/bishop/rook/queen; recapture, value relation, defended/pinned targets, check, queen trades. | Structural zeros; en passant/promotion; one capture versus complete exchange; simultaneous matrix intervals. |
| Q03 | **Checks and forcing:** direct/discovered/double checks, one-legal-reply checks, response quality, candidate checks not played, mate delivery/misses. | Legal reply count is not number of sound replies; mate-in-one can be exhaustive, longer missed mates need appropriate evidence. |
| Q04 | **Tactical geometry:** pins, forks, skewers, x-rays, discovered/double attacks, line blocks, loose pieces, king back-rank relations; create/allow/respond where defined. | Geometric feature precision, pinned defenders, false motif positives, outcome-independent definitions; complex search-limited motifs remain separately flagged. |
| Q05 | **Material/exchanges:** material state, bishop pair, queenless positions, imbalance types, simplification ahead/behind, exchange sequences and recovery. | Do not call an immediate material concession unsound; delayed recapture and temporary investment; pre-move versus post-move facts. |
| Q06 | **Pawns:** file/region advances, repeated pawn moves, breaks, doubled/isolated/passed pawns, islands/chains, blocked passers, file opening, shelter changes, promotions. | Structure definitions independent of outcome; promoted-piece identity; overlapping features; rare underpromotions. |
| Q07 | **King/development/activity:** castling rights/timing, king moves, shelter, nearby attacks, first development, repeated pieces, early queen/rook moves, mobility, central control, rook files/ranks, knight squares, bishop pawn-colour relations. | Promoted/replaced pieces; forced king moves; literal labels instead of evaluative names; legal mobility versus geometric control. |
| Q08 | **Sequences:** same-piece moves, return moves, capture/recapture chains, checks, repetitions, volatility, collapse, recovery, conversion. | Non-overlapping episodes, game-end censoring, dependence on window/threshold, different numbers of opportunities, no “tilt” claims. |
| Q09 | **Opening/repertoire:** ECO/route/transposition, first route or preference departure, adherence, response diversity, score at theory exit and later deterioration. | Date-effective preferences; route ambiguity; current repertoire not projected backward; later opening labels not used as pre-move covariates. |
| Q10 | **Engine decisions:** loss distributions, severe loss, missed opponent opportunities, rank-one agreement, stored-candidate presence/spread, sound stored alternatives, cp/mate transitions. | Candidate truncation/selection; signed negative losses; bounded WDL floors/ceilings; no inference that absent-from-top-five means bad. |
| Q11 | **Opponent behaviour:** move/capture/check mix, pawn share, early queen activity, exchanges, castling/development, opening choices, observed error/volatility profiles. | Opponent-only features; distinguish within-game behaviour from history known before a game; no claims about opponents outside this corpus. |
| Q12 | **Opponent pressure/response:** learner response to checks, captures, queen attacks, pawn advances, early departures, material concessions, opponent errors, and open/closed centre rules. | Both game-result and response-quality outcomes, analysed separately; adjust response models using the position before the learner response; overlapping triggers. |
| Q13 | **Context and trends:** colour, phase, ratings, time control, opening, calendar period, recent form, UTC time, termination, and changes in registered features. | Calendar blocks; composition changes; serial dependence; concurrent games; timezone uncertainty; no clock-pressure or causal training claims. |
| Q14 | **Bounded interactions:** mover × capture, mover × phase, capture pair × pin/defence/material, opponent early queen × opening, pawn share × opening, feature × time class, advantage × simplification. | Exact registered contrasts; independent game support in each cell; interaction test rather than “significant here but not there”; no unrestricted three-way search. |

### Additional questions specifically testing the limits

| ID | Additional test | What it establishes or rules out |
|---|---|---|
| L01 | **Coverage frontier:** compare eligible versus analysed occurrences by phase, rarity, date, opening, and frequency of canonical positions. | Whether the background worker's common-position-first order leaves apparent patterns driven by selective coverage. |
| L02 | **Independent-information frontier:** compare move count, game count, distinct opponents, distinct positions, and concentration for every category. | Whether thousands of rows are mostly repeated evidence from a small number of games or positions. |
| L03 | **Detection frontier:** simulate effect sizes and prevalence over observed covariate/cluster structures, without tuning to observed associations. | Minimum detectable effect at 80%/90% power under the full promotion process, not just a nominal p-value. |
| L04 | **Precision/equivalence:** for predeclared primary contrasts, test whether uncertainty fits entirely inside an agreed negligible-effect range. | Distinguishes “no useful difference supported” from “not enough information.” Non-significance alone cannot do this. |
| L05 | **Denominator stress:** all moves versus legal opportunities; move-weighted versus game-weighted; whole game versus fixed phase/landmark. | Whether a conclusion changes because long games or unequal opportunities dominate. |
| L06 | **Measurement stress:** negative signed losses, near-zero WDL changes, saturation near 0/1, cp/mate transitions, history-sensitive occurrences. | Where the engine metric cannot distinguish quality reliably. No invented centipawn value for mate. |
| L07 | **Candidate censoring:** legal-move count versus stored line count, MultiPV availability by context, and candidate-bound statements. | Which questions are only answerable within selected MultiPV positions; no automatic extrapolation to all moves. |
| L08 | **Missingness stress:** remove observations randomly, by phase/rarity, and by simulated latent loss; compute worst-case bounds for bounded outcomes. | Whether conclusions survive plausible selection and what untestable missing-data assumptions remain. |
| L09 | **Influence/replication stress:** remove the most influential game, opponent, opening, and recurring-position groups using a frozen procedure. | Whether a small set of clusters determines the apparent association. |
| L10 | **Definition stress:** fixed alternative phase/material/episode/threshold rules, all reported together. | Whether the finding is robust or an artifact of one plausible definition; never pick the most favourable variant. |
| L11 | **Time/composition stress:** common-context standardized trends, calendar blocks, and summaries at fixed landmarks. | Whether apparent improvement reflects easier opponents, changed time controls/openings, or more favourable starting positions. |
| L12 | **Leakage stress:** intentionally future-contaminated synthetic features and terminal-result substitutions in validation fixtures. | The pipeline detects and rejects information not available at the question's stated observation time. |
| L13 | **Redundancy/composition:** overlapping motifs, correlated features, piece shares summing to one, and sparse interaction cells. | Avoids treating several versions of one pattern as independent discoveries or fitting non-identifiable models. |
| L14 | **Engine expectation versus observed result:** fixed early/phase landmarks with calibration plots and game-level uncertainty. | Describes the gap between engine expected score and this corpus's eventual results; not learner win-probability calibration by assumption. |
| L15 | **Reproducibility/capacity:** same snapshot/seed reproduces outputs; bounded batches estimate runtime, memory, and artifact size. | A failed or timed-out run is incomplete, not an invitation to report only the successful tests. |
| L16 | **Game-ending selection:** distinguish checkmate, resignation, timeout, agreed draw, abandonment, and unknown endings where stored. | Losses and missing response windows can reflect ending mechanisms; duration does not reveal per-move time. |

Questions requiring individual training attempts, intention, learner explanation, an external player baseline, general opponent style, or causal training effects remain data-unavailable. The limit report can recommend new data; it cannot collect it under this Plan.

## 7. Statistical specification

### Model families

| Outcome | Proposed model and understandable output |
|---|---|
| Frequencies/matrices | Exact snapshot proportions, with whole-game bootstrap intervals for generalization beyond those games; simultaneous bands for registered matrix families. Counts on the frozen census itself have no sampling uncertainty. |
| Positive expected-score loss | Binomial GEE for positive loss plus log-link Gamma GEE for positive magnitude; combine standardized predictions and refit both parts per bootstrap draw. Validate skew/bounds and suppress if poorly calibrated. |
| Severe-loss indicator | Binomial/logit GEE clustered by game; standardized risks and risk difference as primary outputs. |
| Win/draw/loss | Nominal multinomial game-level regression, not an ordinal assumption; adjusted outcome probabilities and learner score rate as secondary summary. |
| Volatility | Robust predefined game/segment dispersion; cluster-resampled Brown–Forsythe-style comparisons, not an ordinary independent-observation variance F-test. |
| Response episodes | The appropriate loss/severe-loss model, one record per eligible response/episode, clustered by game. |
| Longitudinal outcomes | Fixed calendar-period effects or a predeclared low-dimensional trend, standardized to common supported contexts; calendar-block bootstrap. |

Default GEE working correlation: independence with robust game-cluster uncertainty; use a fixed exchangeable sensitivity where identifiable. Neither the working correlation nor bootstrap makes crossed opponent/position dependence disappear automatically.

### Adjustment and timing

- Start with colour, learner rating and rating difference, parsed time control, calendar period, pre-move phase, material, and evaluation as appropriate. Avoid including redundant rating terms or the feature itself twice.
- Define an adjustment set per question, not one enormous universal model. Report overlap: predictions for comparisons must stay within contexts represented in both groups.
- For a move at ply 8, use opening information recognizable through ply 8, not the game's deepest later opening label. A final opening label may describe whole games but cannot silently adjust earlier decisions.
- Do not adjust move effects for final game length, result, later material, post-move evaluation, later repertoire updates, or future opponent behaviour.
- Whole-game opponent shares versus game results are retrospective associations, because behaviour and game progress influence each other. Fixed early windows provide a distinct prospective-from-landmark question, conditional on reaching that landmark.
- For learner responses, the position immediately before the learner response is legitimate baseline context. For the total association of an opponent move with later outcomes, that same post-opponent position may be a mediator; do not reuse the response adjustment set blindly.
- Missing engine outcomes are not imputed. Missing covariates have explicit complete-case/unknown-category rules where meaningful, with losses of support reported. Unknown numeric ratings are not assigned invented values.

### Resampling and dependence

- Resample complete games, including all their moves/episodes. Duplicate sampled games receive distinct bootstrap cluster IDs. Refit preprocessing and both model components as registered, not merely resample fitted coefficients.
- Repeated-opponent questions resample opponents with their games or use an approved dependence-robust alternative. Missing opponent identity cannot silently become one shared opponent.
- Recurring positions create crossed dependence across games. Include position concentration and position-group sensitivity; use validated multiway uncertainty if warranted. If game and position/opponent dependence cannot both be handled credibly, withhold the affected generalization.
- Temporal questions use contiguous calendar blocks (proposed four-week primary, two/eight-week sensitivities), retain within-block games, and report the number of blocks. Do not shuffle dates and call that a longitudinal bootstrap.
- Game-weighted sensitivity gives each game's eligible moves total weight one, answering a different stated question from the primary move-weighted analysis.

## 8. Confidence, multiplicity, and stopping rules

### Recommended review proposal

1. Freeze the complete v1 hypothesis family before viewing feature–outcome associations. Retain untestable registered slots conservatively in correction bookkeeping, with no reported fake p-value; do not make the family smaller after failures.
2. Use Benjamini–Hochberg at 5% for the internal discovery ledger, subject to validation of its dependence assumptions; if these fail, choose a valid conservative alternative before corpus inference.
3. Require Holm family-wise correction at 5% across the **complete registered inferential family**, not just discovery winners, for product-facing associations. Holm on this same history is stricter historical evidence, not independent replication.
4. Use multiplicity-aware intervals for promoted contrasts. A conservative simultaneous method is preferable to presenting an ordinary 95% interval as selection-adjusted. Validate tail precision and feasibility before freezing the interval method.
5. Require the interval to lie beyond the approved meaningful-effect boundary in the claimed direction, plus all coverage, support, fit, influence, and sensitivity gates. A p-value alone never promotes.
6. Treat equivalence conclusions as registered inferential claims with their own bounds and multiplicity allocation. “No supported association” is not “no association.”
7. Do not split the historical corpus simply to produce a confirmation set. Later-game confirmation uses definitions frozen now and a future fixed date/sample trigger, with one scheduled look or an approved sequential-testing design.

Descriptive inventory has a separate gate: validated denominator, data scope, and uncertainty if generalized. It need not reject a meaningless null such as “pawn-move share equals zero.” Calling a category unusually bad, best, worst, improving, or linked to results is inference and enters the corrected family.

### Proposed numerical guardrails — review and simulation must ratify

| Gate | Initial proposal |
|---|---|
| Meaningful severe-loss risk difference | 2 percentage points absolute. |
| Meaningful mean expected-score-loss difference | 0.01 expected game points per move. |
| Meaningful game score-rate difference | 0.05 expected game points per game. |
| Other effects | Freeze outcome-specific practical bounds for volatility, multinomial contrasts, interactions, and trends before registering them for promotion; no universal coefficient cutoff. |
| Basic move-contrast support | At least 100 distinct games overall and 50 contributing games in each contrasted exposure group. This is a floor, not proof of power. |
| Rare binary outcomes | At least 30 event-bearing and 30 non-event-bearing games in the fitted population; additional per-cell and parameter-support checks established by simulation. |
| Coverage | At least 90% comparable eligible occurrences in each comparison group and no more than a 5-percentage-point coverage gap. This is necessary, not sufficient against non-random missingness. |
| Bootstrap budget | Start with 2,000 resamples; fixed independent-seed batches can extend to a predeclared 10,000 cap for numerical precision, never to chase significance. Tail precision for simultaneous bounds may require a different validated method or no promotion. |
| Fit success | At least 99% successful bootstrap fits, no unresolved separation/non-identifiability, plausible predictions, and no silent fallback to an easier winning model. |
| Sensitivity | No unexplained direction reversal or dependence on one influential cluster; report variation relative to practical-effect bounds. Exact influence cutoffs must be calibrated and frozen before corpus fitting. |

Numbers are conservative starting proposals, not guarantees. Stage 4 simulations may reveal they are inadequate. Any change must precede real association review and be recorded as a protocol revision. If historical results have already been viewed, label the revised analysis exploratory rather than retroactively preregistered.

### Repeated runs and new questions

- Filling in more analysis on the same historical games is not new independent evidence. Do not rerun until a result crosses a threshold and then stop.
- Freeze the first inference snapshot at an approved coverage/date trigger. Later coverage snapshots are descriptive stability updates unless a repeated-testing policy was approved in advance.
- After review, new combinations or threshold choices enter a new exploratory registry version. They cannot inherit v1's confirmatory status or reset the multiplicity burden by renaming a family.
- Maintain finding status history: historically supported, later confirmed, unstable, superseded, or withdrawn. Never silently replace an old estimate with the most favourable run.

## 9. Validation and stress-test matrix

Use deterministic fixtures and seeded simulations with known truth. Simulations are generated data; they are not evidence about the learner. Save generator parameters and Monte Carlo uncertainty.

| Test | Required behavior |
|---|---|
| Chess fixtures | White/Black symmetry, legal EP, all promotions, castling-right loss, pinned defenders, discovered/double checks, mate/stalemate/insufficient material, terminal exclusions, repeated boards with different histories. |
| Score fixtures | Exact 0.20 inclusion if approved, Black sign, terminal scoring, negative `D`, WDL quantization, cp/mate parity, before/after mixed quick/full, invalid line rejection. |
| Known-null populations | Correlated moves, unequal game lengths, repeated opponents/positions/openings, overlapping features: false positives remain controlled or the method refuses promotion. |
| Known-effect populations | Weak/strong effects across prevalence and cluster counts: estimate bias, interval coverage, power, sign errors, and smallest detectable effects. |
| Confounding/overlap | Construct a raw association that reverses/disappears after context adjustment; detect absent overlap rather than extrapolating a comparison. |
| Sparse/zero-heavy data | All-zero losses, rare severe events, single-category results, tiny cells, extreme skew, separation, collinearity: controlled diagnostic status rather than a spurious precise finding. |
| Missingness | Random, context-dependent, and unobserved-outcome-dependent deletion: distinguish empirical robustness from assumptions the data cannot test. |
| Multiple testing | Full registry under global null and mixed nulls; correlated and interaction families, equivalent duplicate features, failed fits, definition sensitivities, complete promotion pipeline. |
| Time and endings | Trends with/without true improvement, shifting mix, serial dependence, short games, unfinished episodes, concurrent games, outcome leakage. |
| Influence | Inject one huge game, repeated opponent, dominant opening, or common position; the report exposes concentration and promotion fails when appropriate. |
| Reproducibility | Same input/seed produces equivalent output within declared numeric tolerance; changed snapshot or rule changes provenance; partial runs cannot masquerade as complete. |

For the core calibration suite, propose at least 1,000 simulated datasets per agreed scenario. Report binomial Monte Carlo intervals for false-positive and coverage rates; predeclare acceptable tolerance (proposed upper false-positive bound 0.075 for a nominal 0.05 test, lower coverage bound 0.925 for nominal 0.95 intervals). These are validation tolerances, not changed inferential alpha levels. Tighten or expand simulation counts before use if precision is insufficient. Test both individual methods and the complete promotion pipeline; use relevant family-wise/FDR metrics rather than substituting per-test error rates.

No method is accepted merely because statsmodels returns a coefficient. Non-convergence, unsupported covariance estimates, invalid uncertainty, or failed calibration block the affected family. Fixing a model requires rerunning its calibration and invalidated proof.

## 10. Sequential implementation stages after approval

Each stage ends with a reviewable artifact and a stop condition. Do not infer approval for the next unresolved methodological decision from approval to implement infrastructure.

### Stage 0 — Approve and freeze the protocol

- Review Sections 5, 7, and 8; settle severe loss, phase, motifs, windows, meaningful effects, confidence rules, and run budgets.
- Map every original catalogue item and extension to registry IDs and planned dispositions. Freeze the initial allowed interactions and primary/sensitivity distinction.
- **Deliverable:** approved protocol and decision log, initial registry, explicit implementation scope.
- **Stop:** no corpus association analysis until required decisions are settled. Pure counts/availability may inform support planning; do not select questions using observed effects.

### Stage 1 — Snapshot and availability audit

- Implement safe snapshotting, schema/record validation, denominator accounting, and inventory-only outputs.
- Audit history-sensitive canonical positions and missing data; quantify what can be computed without engine analysis, with rank one, and with MultiPV.
- **Proof:** small SQLite fixtures including inconsistent moves, nullable metadata, duplicate source evidence, atomic publication boundaries, and no writes to the source database.
- **Deliverable:** frozen snapshot manifest, availability report, coverage frontier, exclusions, revised feasibility statuses without effect-driven selection.
- **Stop:** resolve unsafe snapshotting, broken replay, or source ambiguity before extraction/inference.

### Stage 2 — Deterministic records and feature definitions

- Build stable move/episode/game records; version rules and store provenance. Begin with inventory/captures/checks/material, then structures, sequences, opening/preference, and opponent features.
- Keep unsupported complex motifs blocked rather than inventing approximations under familiar labels.
- **Proof:** focused chess/outcome fixtures in Section 9; learner/opponent counts and capture matrix totals reconcile; dated preference and observation-time rules hold.
- **Deliverable:** feature dictionary, fixture catalogue, descriptive inventory, coverage per feature, full registry disposition map.
- **Stop:** user reviews disputed feature meanings before they become statistical exposures.

### Stage 3 — Model and reporting infrastructure

- Add pinned compatible numerical dependencies, model families, standardized effects, resampling, multiplicity, gate state machine, and machine-readable reports.
- Implement resumable bounded jobs with immutable configuration and deterministic seeds; reuse cached features but never mix snapshot versions.
- **Proof:** synthetic known effects, nulls, all-zero/rare outcomes, failure statuses, complete family accounting, report/sample traceability, and resume behavior.
- **Deliverable:** executable analysis framework and synthetic-only reports. No learner findings yet.

### Stage 4 — Calibration and data-limit stress tests

- Run the full Section 9 matrix and L02–L15 method-level stresses, benchmark finite representative batches, and calibrate support/influence thresholds.
- Estimate power using audited cluster/covariate structure and stipulated effect sizes, without fitting and cherry-picking historical associations.
- **Deliverable:** method acceptance report, detection frontier, cost estimate, finalized registry/protocol hash, explicit unsupported model families.
- **Stop:** no promotion from methods failing false-positive, interval, numerical, or dependence checks. Budget overruns require scope/budget review, not lower confidence standards.

### Stage 5 — Execute the frozen historical programme

- Run all feasible registered questions in bounded batches: descriptive inventories; learner quality/structure; sequences/openings; opponent outcomes/responses; context/trends/interactions.
- Execute the full predeclared sensitivity set and correction across the full family, even when computation is divided into waves.
- Record every success, failure, blocked question, and reason. Intermediate wave results are provisional and cannot be promoted before family completion.
- **Deliverable:** complete diagnostic ledger, adjusted effects/intervals, coverage and influence reports, sensitivity tables, eligible high-confidence findings, and data-limit report.
- **Stop:** mark interrupted runs incomplete. Do not change definitions after looking at winners within this run.

### Stage 6 — Evidence review and handoff to Part 3

- Generate the user/AI review package described below. Verify each finding back to source records and ensure statements use deterministic templates.
- Review contradictions, null/equivalence outcomes, selection limitations, and the cases where more data would not repair a measurement problem.
- **Deliverable:** accepted evidence package and, if desired, a separately approved schedule for future-game confirmation.
- **Stop:** no trainer integration or lesson generation. If no findings qualify, report that and decide whether to collect more data, revise questions, or stop; do not force a Part 3 learning focus.

### Future verification command contract

No tests are run for this planning-only change. During implementation, each stage must name its actual focused test files before execution. A proposed shape is:

`timeout 120s .venv/Scripts/python.exe -m pytest tests/statistical_analysis/<stage_test_file>.py`

Use a tool timeout of `150000` ms. The placeholder is not an existing runnable test. Simulation/corpus commands must also have an explicit finite command timeout, tool timeout, iteration cap, fit timeout, and checkpoint policy. Approve longer bounded batches based on Stage 4 measurements; never run an unbounded process. Use only focused behavioral proof, not broad lint/build/hygiene suites. If services or a browser become necessary, first follow `docs/DEVELOPMENT_SERVICES.md` and `dev.ps1 status`; no such service action is needed for this draft.

## 11. User and AI evidence review package

Provide a short Markdown index plus machine-readable tables and manifests. Suggested sections:

1. **What was available:** snapshot, denominator waterfall, feature coverage, repeated clusters, unsupported inputs.
2. **What was tested:** complete registry, source-catalogue mapping, exact rules, model assumptions, correction family size, simulations passed/failed.
3. **What is supported:** finding cards grouped by descriptive versus inferential claim, not by how dramatic they sound.
4. **What remains unresolved:** imprecise tests, meaningful-null/equivalence results, failed definitions/models, and impossible questions, clearly separated.
5. **Where the data stops helping:** detection/coverage frontiers, crossed dependence, engine/history/candidate limits, sensitivity failures, and suggested future evidence.
6. **Decisions for Part 3:** evidence suitable for discussion, without inventing a lesson or causal mechanism.

Each finding card includes:

- Stable ID, claim type, exact plain-English statement generated from approved templates, rule and question versions.
- Population/time window, outcome/comparator, eligible/comparable counts, independent games, opponents/positions, and denominator.
- Unadjusted description alongside adjusted marginal effect; simultaneous interval where required; corrected result and meaningful-effect gate.
- Coverage, missingness, overlap, model diagnostics, influential clusters, sensitivity outcomes, limitations, and historical/later-confirmed status.
- Snapshot/code/dependency/engine provenance; analysis command/configuration/seed identity.
- Exact member-record references and deterministic inspection samples: typical qualifying cases, cases inconsistent with the aggregate direction, matched context examples, and definition-boundary cases. Do not display only the worst blunders.
- Game UUID/URL, ply, before/after FEN including occurrence counters, played move, feature facts, WDL/loss, and available candidate evidence. Samples illustrate the definition; they do not prove the association.

The full ledger uses explicit reason codes such as `descriptive_only`, `supported`, `no_supported_difference`, `equivalent_within_bounds`, `underpowered`, `coverage_blocked`, `definition_blocked`, `data_unavailable`, `model_failed`, `unstable`, and `run_incomplete`. Include all applicable gate failures, not only the first one.

## 12. Review agenda and completion checklist

### Recommended order for reviewing this draft

1. Agree that testing limits and reporting non-answers are first-class outcomes, not just finding weaknesses.
2. Approve or revise the scoring, phase, episode, tactical-rule, and meaningful-effect proposals.
3. Review the complete original inventory plus Q01–Q14 and L01–L16. Decide explicit deferrals; do not accidentally drop rare or difficult questions.
4. Agree on descriptive versus inferential output, Holm promotion, equivalence claims, later confirmation, and repeated-run safeguards.
5. Approve artifact location/retention, resource limits, implementation stages, and review stops.

### Part 2 is complete only when

- [ ] Every source-catalogue item has a traceable disposition; all implemented definitions are versioned and tested.
- [ ] Snapshot and feature/model artifacts are reproducible and do not mutate production data.
- [ ] Learner/opponent populations, denominators, timing, missingness, and terminal/history behavior are explicit.
- [ ] Numerical methods and the promotion pipeline pass approved synthetic calibration.
- [ ] Every registered historical question has a result or a recorded reason it could not run; correction accounting is complete.
- [ ] Supported findings pass every approved gate and expose their exact supporting evidence.
- [ ] The diagnostic ledger and data-limit report distinguish lack of evidence, evidence of negligible effects, and unanswerable questions.
- [ ] The user has reviewed the evidence package. No lesson, training flow, frontend integration, or AI chess explanation has been implemented.

## Planning-session record

- Read the governing workflow, full candidate catalogue, completed Part 1 Plan, Graphify signpost, schema source, dependency declarations, and canonical engine-root helper.
- No subagents used. No database inspected, tests run, model fitted, service changed, dependency installed, or product source edited.
- Existing unrelated modification to `tests/database/stockfish/test_worker.py` was present before this Plan and must remain untouched.

## Implementation checkpoint — 2026-09-22

- **Stage 0 in progress:** User authorized implementation. Recommended scoring/phase/windows/support/coverage defaults are the initial protocol; unresolved complex definitions remain blocked, not guessed. Runtime artifacts use the already-ignored `artifacts/statistical-analysis/` directory.
- **Stages 1–6 pending.** One 5-replicate exploratory diagnostic fit is recorded below; it is not a finding. Nothing has been accepted or promoted, and no pilot-sample association fit has been run. Calibration and complete-family checks remain promotion prerequisites.
- **Source facts refreshed:** the live database is in the Docker `chess-database` volume; host `chess-seed.db` is not authoritative. Snapshotting will use SQLite's backup API, not a raw copy of the open database. Existing connection configuration, analysis materialization/validation, canonicalization, and opening recognition contracts are available for reuse.
- **Preserve unrelated changes:** both `tests/database/stockfish/test_mutex.py` and `tests/database/stockfish/test_worker.py` were modified before implementation.
- **Next:** implement frozen protocol/registry and safe snapshot + replay audit with focused fixtures; then record proof before progressing.

### Checkpoint 1 — snapshot and deterministic records

- Implemented `statistical_analysis/{artifacts,protocol,snapshot,readers,extraction,features,scoring,sequences}.py`. Snapshot uses bounded online SQLite backup, schema/foreign-key checks, hashes, and a completion manifest. Extraction is read-only against the snapshot, commits complete games atomically, quarantines inconsistent games, and resumes only under the same snapshot/protocol/extractor identity.
- Reuses production analysis materialization/validation, PGN parsing, canonical position identity, opening-route materialization, and date-effective preference rules. Quick/full rank-one outcomes are pooled; scores use integer 1/2000 units so the severe-loss boundary is exact.
- Features now include piece/capture/check inventory, literal pins/forks/defence, pawn structure, material, king-zone/control counts, tracked piece identity, dated adherence, past-only opening labels, stored-candidate bounds, opponent previous-move context, and observed sequence summaries. This is not a claim that every catalogue feature/model is implemented.
- Pinned numerical dependencies installed locally: NumPy 2.3.3, pandas 2.3.2, SciPy 1.16.2, statsmodels 0.14.5; `uv.lock` and `requirements.txt` regenerated. No service lifecycle action taken.
- **Proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/statistical_analysis/test_snapshot_extraction.py tests/statistical_analysis/test_features.py -q`, tool timeout 150000 ms: **22 passed**. Initial run had two failures (JSON tuple/list normalization and an incorrect knight-attack fixture); corrected and rerun successfully.
- **Stages 0–2 remain in progress:** complete registry, aggregate audit/reporting, live snapshot, and more boundary fixtures still required. Stages 3–6 pending. No historical findings or corpus fits run.
- **Next:** frozen registry/dispositions, streaming audit, model/uncertainty framework, and CLI; keep promotion disabled until actual calibration evidence exists.

### Checkpoint 2 — registry, models, live snapshot (2026-09-22, updated)

- Implemented `registry.py` (118 registered contrasts, 248 catalogue items with stable IDs), `models.py` (GEE marginal contrasts in an isolated worker with per-fit deadlines), `inference.py` (whole-game bootstrap, Holm correction over the complete family, fail-closed gates), `runner.py` (checkpointed resume, historical inference blocked unless `diagnostic=True`), `calibration.py` (seeded simulations), `audit.py` (streaming census, no model fits), `reporting.py` (descriptive-only review package), and `__main__.py` CLI. Fixed `prepare_frame` to carry `opening`, `simulate_frame` to include it, and `fit_contrast` to record `unavailable_column` instead of `KeyError`.
- **Proof:** `.venv/Scripts/python.exe -m pytest tests/statistical_analysis/ -q`, tool timeout 180000 ms: **32 passed**.
- Live snapshot `artifacts/statistical-analysis/part2-20260922-r2`: 12,710 games, 657,654 occurrences, 47,648 stored analysis results; single learner identity confirmed. Registry frozen (118 questions, 248 catalogue items).
- **Hang lesson:** the first full extraction call (570 s budget) blocked the session and was aborted; records.db kept 1,766 committed games but extraction.json still reported 200. Extraction now writes `extraction.progress.json` every 100 games and records processed counts on abort. Extractor identity narrowed to `(snapshot, protocol, records-v1)` with source hash kept as provenance, so progress-only code changes no longer force a restart; record-semantic changes bump `RECORD_VERSION`.
- Fresh run `part2-20260922-r3` (same snapshot/registry copies, new identity): **extraction complete 12,710/12,710 games, 0 excluded**, all in bounded batches.
- **Audit (complete):** learner 322,864 eligible / 83,209 comparable (**25.8%**); opponent 322,080 / 81,653 (**25.3%**). Missing engine analysis dominates exclusions. Measurement limits: 30,055 negative signed losses retained as diagnostics; 7,131 near-zero changes; 27,645 saturated before-WDL; 535 history-sensitive; 177,500 candidate-censored occurrences vs 31,006 MultiPV occurrences. No missing timestamps/ratings/opponent IDs.
- **Calibration null-100:** 100/100 fitted, 3% rejection, 97% coverage; `base_method_checks_pass=false` (correctly fail-closed: only 100 reps, needs ≥1,000) and `promotion_accepted=false`.
- **Diagnostic fit `Q01.piece.pawn.loss` (replicates=5, exploratory):** `support_blocked` / `coverage_blocked` — pawn 41.5% vs non-pawn 19.0% coverage (22 pp gap). Coverage correlates with the feature (common-position-first worker), confirming the L01 concern. Ledger stays `run_incomplete`; nothing promoted.
- **Evidence package:** `REVIEW.md`, `findings.json` (descriptive census only, no associations), `audit.json`, `diagnostics.json`, frozen `registry.json`. Stages 5–6 remain blocked behind coverage (<90% gate) and unaccepted full calibration — this is the honest limit, not a failure to run.

## Bounded representative pilot sample

- **User direction:** provide a representative, small-scale sample for exercising the analysis framework; do not add a new implementation stage. Prepare the code for production use and document, especially, how to start a clean full run after pilot work.
- **Purpose and boundary:** sample complete games from a fully extracted frozen run, preserving each selected game's moves and retaining excluded games for the exclusion-rate picture. Use this for pipeline behavior, coverage, runtime, and report checks. It is not a shortcut around calibration, the complete question family, or promotion gates; pilot summaries are unweighted and non-confirmatory.
- **Sampling design:** fixed seed, game-level stratification by learner colour, time class, game length, and raw rank-one before/after-line availability for learner and opponent moves. For a current frozen snapshot, select games before replay so the pilot does not require a full-corpus extraction. Record stratum counts/inclusion probabilities and source-versus-sample margins. Structural extraction validity is not known until replay; retain sampled failures and count them rather than using extraction status as a preselection stratum. Do not select on game outcomes or model effects.
- **Artifact safety:** create a new, immutable pilot directory; never overwrite or trim the source run. A changed seed/size or interrupted pilot gets a new output directory. The clean full-run reset procedure must use a new run directory and complete source snapshot/extraction; it must not reuse pilot `records.db` or merge diagnostic output from an earlier run.
- **Implementation:** added `statistical_analysis/pilot.py`, `statistical_analysis/snapshot_pilot.py`, `statistical_analysis/full_run.py`, and the `pilot`, `pilot-snapshot`, and `prepare-full` offline commands. The snapshot path chooses games before replay, reducing the need to extract the full corpus just to get a pilot. Every non-empty stratum receives a sample; smaller caps fail before creating output. Pilot audits/reports are explicitly unweighted and non-confirmatory; diagnostic fits carry a permanent pilot-not-promotable gate. `prepare-full` copies only the verified full snapshot, manifest, and registry into a new directory, even if the source extraction was incomplete; old results remain untouched.
- **Pilot artifact:** `artifacts/statistical-analysis/pilot-part2-20260929-r1`, identity `7377049c10054a3545aa420f90a53e7f8a2e89d96b41606b3af36ff6af1475f0`, sampled 1,000 of 12,710 games (50,156 plies), seed `20260922`; no games were excluded. Audit found learner 6,688/25,099 comparable moves (26.6%) and opponent 6,591/25,057 (26.3%). These are unweighted descriptions of this pilot only; no association model was run.
- **Initial offline pilot:** `pilot-part2-20260929-r1` is preserved as a pilot from the older 2026-09-22 snapshot. It had about 26% comparable move coverage and did not reflect the newly requested live snapshot; it is not the current pilot.
- **Fresh live snapshot (2026-09-29):** after user approval, checked managed service status, stopped the normal worker through `dev.ps1`, created a consistent SQLite backup with the SQLite backup API inside the backend container, copied out the standalone backup, and restarted the normal worker through `dev.ps1`. Snapshot `part2-live-20260929-r1` is complete (12,907 games; 240,072 current analysis results; SHA-256 `ba9d01a90ea54b8ef1dacc42350a3579c4a70fbfb76f1e081191e1407a08bf44`). No live data was modified, and the final status check confirmed normal worker mode is running.
- **Full extraction budget finding:** `timeout 110s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis extract --run "artifacts/statistical-analysis/part2-live-20260929-r1" --seconds 100 --max-games 1000` stopped at its 100-second internal budget after 347 games; complete extraction was not published and the resumable partial run was preserved. Snapshot-level sampling now avoids requiring this full 12,907-game replay before a pilot.
- **Current pilot artifact:** `artifacts/statistical-analysis/pilot-live-20260929-r1`, identity `9b34393e5928f71b23042326c0cc278cf280401083dd725dd3ef7225a17b2b56`, sampled 1,000 of 12,907 games (50,467 plies), seed `20260922`, 0 excluded on replay. The full snapshot's raw rank-one pair availability was 54.9% learner / 54.8% opponent. The pilot audit's validated comparable move coverage was 55.6% learner (14,035/25,250) / 55.3% opponent (13,950/25,217), consistent with the user's “about half” estimate. These are descriptive sample outputs only; no pilot association model was run.
- **Proof:** `timeout 120s .venv/Scripts/python.exe -m pytest tests/statistical_analysis/ -q`, tool timeout 150000 ms: **35 passed**. Real commands used finite internal and outer limits: `timeout 120s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis pilot-snapshot --source-run "artifacts/statistical-analysis/part2-live-20260929-r1" --output "artifacts/statistical-analysis/pilot-live-20260929-r1" --max-games 1000 --seed 20260922 --seconds 90`; `timeout 330s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis extract --run "artifacts/statistical-analysis/pilot-live-20260929-r1" --seconds 300 --max-games 1000`; `timeout 75s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis audit --run "artifacts/statistical-analysis/pilot-live-20260929-r1" --seconds 60`; `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.statistical_analysis report --run "artifacts/statistical-analysis/pilot-live-20260929-r1"`. `prepare-full` from a snapshot-only source, interrupted pilot extraction/resume, and pilot non-promotion are covered by focused tests. No association model or simulation run used the new pilot.
- **Reset note:** `prepare-full --source-run "artifacts/statistical-analysis/part2-live-20260929-r1" --output "<new-full-run-directory>" --seconds 90` copies the exact full frozen snapshot/registry into a new directory, even though the source's extraction is incomplete. Then run bounded full `extract`; if extraction stops, resume it in that same directory with the same code/protocol. If preparation stops before ready, preserve it and use another fresh output path. Never delete/reuse the pilot path, copy pilot `records.db`, or carry over a diagnostic ledger. The current pilot's `PILOT.md` documents this; `prepare-full` writes a run-specific `FULL_RUN_RESET.md`.
