# Chess learning workflow

**Started:** 2026-09-21  
**Status:** Direction aligned into three ordered parts; Part 1 is next.  
**Authority:** This is a running record of the user's product-direction decisions. It is historical evidence, not a Plan or implementation authorization.

## Purpose

The broad objective is to help the user stop repeating costly mistakes in real games. The immediate work is not to invent the final training experience. It is to build sufficient analysis coverage, run rigorous backend analysis, and then use the supported findings to decide the learning workflow.

The separate candidate inventory at `docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md` is the comprehensive input to Part 2. It records possible deterministic analyses, not proven findings.

## Agreed three-part route

1. **Analysis infrastructure** — make quick analysis useful in the frontend and continuously fill missing analysis in the background.
2. **Statistical models and analysis** — create the deterministic feature and statistical models, run the defined questions, and produce high-confidence findings.
3. **Finalise and regrill** — review the findings and make the remaining decisions about the learning workflow, training, presentation, and integration.

The parts are ordered. Once Part 1 is accepted, its worker can keep collecting coverage while Part 2 is designed and built. Part 3 must be informed by actual supported findings rather than guesses about which chess patterns matter.

## Direction that applies throughout

- Do not use AI now or in the future for chess explanations, pattern labels, or generated causal stories.
- Stockfish evaluations and principal variations are move-quality evidence, not human explanations.
- Extract chess features from stored facts and explicit deterministic rules.
- Discover patterns across the move and game population before deciding what should become a lesson.
- Keep learner and opponent moves as separate populations.
- Treat statistical associations as associations, not automatic causal explanations.
- Publish only findings that pass the agreed confidence rules. Failed and underpowered tests may remain backend diagnostics but are not product findings.

# Part 1 — Analysis infrastructure

## Outcome

Establish an affordable, continuously growing analysis corpus while also improving the existing frontend analysis path:

- `browser` becomes the quick analysis tier: lower node budget and SinglePV.
- `tool` remains the full tier: higher node budget and MultiPV.
- The frontend can request quick analysis and explicitly upgrade a position to full analysis.
- While the Docker worker is running, it uses otherwise idle time to analyse missing positions at quick quality.
- Full results replace quick results for the same position and are included normally in later rank-one statistical analysis.

## Existing repository foundation

- The database already permits exactly the two quality values `browser` and `tool` and stores one current result per canonical position.
- Existing publication rules allow tool to replace browser, prevent browser from replacing tool, and replace the result, settings, engine provenance, and candidate lines atomically.
- Queue promotion already upgrades browser work to tool and prevents downgrade.
- A tool result already satisfies a browser request.
- The production frontend currently requests only tool analysis. Browser is otherwise effectively unused outside API defaults and fixtures.
- The Docker worker already polls every five seconds, drains the durable `derived_analysis_queue`, processes one Stockfish search at a time, and recovers interrupted claims.
- Frontend analysis requests already use that queue.
- The worker currently does not discover work. It becomes idle when the queue is empty.
- The manual bulk command is not the desired mechanism: it bypasses the queue, produces tool results directly, and selects opening-focused targets rather than the complete game corpus.

## Quick and full analysis contract

### Quick tier

- Persisted quality remains `browser` even though its product role is now “quick analysis.”
- Use the existing 200,000-node budget.
- Change it from MultiPV 5 to SinglePV.
- Provide the rank-one score, WDL, depth, principal variation, engine provenance, and settings needed by the frontend and statistical analysis.

### Full tier

- Persisted quality remains `tool`.
- Retain the existing 6,400,000-node budget and MultiPV 5 behavior.
- Continue to provide deeper analysis and alternative candidate lines.
- Replace the quick result when the user requests an upgrade.

### Shared statistical use

- Rank-one quick and full results have the same relevant data shape.
- Later move-quality analysis uses whichever current result is stored for the position.
- Do not exclude, down-weight, separate, or require a special confirmation sample for full results.
- Analysis quality remains provenance metadata, not a reason to remove a result.
- Questions that inherently need several candidate lines can use only results that contain those lines; ordinary rank-one WDL analysis includes both tiers together.

## Required profile and validation change

- MultiPV is currently configured globally at five lines for both qualities.
- Current validation requires five candidate lines, or one per legal move if fewer than five are legal, regardless of quality.
- Part 1 therefore needs profile-specific MultiPV settings and quality-aware validation, completeness checks, readers, and focused contract tests.
- Reusing the existing `browser` enum value does not itself require a schema migration.

## Continuous background worker behavior

- Always claim already-requested queue work first.
- When no requested work exists, discover one missing or stale quick-analysis target, or a deliberately tiny bounded batch, and enqueue it through the existing durable queue.
- Recheck requested work between background targets so a frontend request waits for at most the current quick search rather than a large background backlog.
- Do not enqueue the whole corpus at once. The current queue is FIFO and has no source-priority field.
- Select from all eligible game positions, not only the current bulk command's first twenty plies and opening routes.
- Use a deterministic target order. Positions occurring in the most games are a useful first order because early analysis then covers the largest number of move occurrences.
- Full results satisfy the quick requirement and must never be downgraded.
- Background work creates quick results only. Full upgrades remain explicit requests.
- Continue until no quick target remains, then return to quiet polling.
- Reuse the existing engine process, database mutex, queue claims, quality promotion, crash recovery, and shutdown behavior rather than creating another Stockfish execution path.

## Current workload

A read-only count of `data/database/chess.db` found:

- 12,710 games.
- 644,944 played-move occurrences.
- 530,732 unique canonical positions.
- 322,864 learner-move occurrences.
- Only 32 unique positions currently have stored engine analysis.
- Existing results use the same settings but are split between Stockfish 18 and Stockfish 19.
- Making every learner move before/after comparable touches 519,155 unique positions.
- Of those, 2,403 are deterministic checkmate, stalemate, or insufficient-material terminals that need no engine search.
- A clean quick-analysis sweep therefore needs approximately 516,752 Stockfish searches.
- Covering learner and opponent move quality together raises that only modestly to approximately 522,149 searches.
- No analysis jobs were queued or running when these counts were taken.

At 200,000 nodes per quick search, the learner-analysis sweep is about 103.35 billion nodes rather than 3.31 trillion nodes at the full budget. Illustrative uninterrupted runtime is approximately 28.7 hours at one million nodes/second, 14.4 hours at two million, 5.7 hours at five million, or 2.9 hours at ten million, before orchestration overhead.

## Part 1 operational boundaries

- The current Docker service has no automatic restart policy. Background completion continues only while the explicitly started worker remains up.
- Do not flood the FIFO queue with background work.
- Coordinate database rebuild or replacement with the running worker so an active database is not swapped underneath a claim.
- Part 1 does not implement the statistical feature catalogue, statistical promotion rules, learning exercises, or final workflow.

## Part 1 completion point

Part 1 is complete when focused behavioral proof establishes that:

- quick requests produce valid SinglePV results;
- full requests still produce MultiPV results and replace quick results;
- the frontend can request quick analysis and request an upgrade;
- the worker processes requested work before continuously selected background work;
- background work eventually progresses through eligible unanalysed positions without creating a large queue backlog;
- stopping and restarting preserves or safely recovers work.

# Part 2 — Statistical models and analysis

## Outcome

Create the backend feature and statistical models, execute the versioned candidate questions against the analysed corpus, and produce a catalogue containing only high-confidence supported findings.

This is proper backend inference, not frontend grouping and not manual inspection of raw percentages.

## Analysis scope

The full candidate inventory is maintained in `docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md`. Major families include:

- move frequencies and moving-piece distributions;
- capture and moving-piece × captured-piece matrices;
- checks, forcing moves, and special moves;
- deterministic tactical geometry;
- material, exchange, pawn-structure, king-safety, development, mobility, and space features;
- move sequences, volatility, collapse, recovery, and conversion;
- openings, transpositions, route departures, and repertoire adherence;
- engine-backed expected-score loss, severe-loss rate, missed opportunities, and sound alternatives;
- opponent move styles and behaviors linked separately to learner game results and learner response quality;
- context, interactions, and longitudinal change.

Initial outputs include statements such as “pawn moves are X% of my moves,” capture breakdowns such as bishop × captured-piece rates, and statistically tested relationships between those features and move quality or game outcome.

## Learner and opponent populations

- The learner's moves are the primary move-quality dataset.
- Opponent moves remain separate rather than being merged into learner percentages.
- Opponent analysis asks which recurring opponent behaviors are associated with poor learner outcomes.
- Assess opponent behavior at both levels: final game result and the engine-backed quality of the learner's response.
- Candidate examples include high pawn-move share, early queen activity, frequent exchanges, checks, and opening departures.

## Accepted statistical backbone

Use generalized estimating equations and whole-game cluster bootstrap:

- Use deterministic, versioned move-feature records as model inputs.
- Keep descriptive move percentages move-weighted when the question is “what percentage of my moves.”
- Treat the game as the normal independent cluster for move-level inference so moves from one game do not create false certainty.
- Use a game-weighted sensitivity where appropriate so one long game does not dominate.
- Use opponent clustering for repeated-opponent questions, position sensitivity for recurring positions, and calendar-block resampling for longitudinal questions.
- Report adjusted probabilities, risk differences, expected-score differences, or other understandable marginal effects rather than relying on raw model coefficients.

GEE supplies adjusted population-average associations while allowing moves in one game to be correlated. The whole-game bootstrap resamples complete games, refits the analysis, and checks whether the effect and interval survive actual game-to-game variation.

## Proposed model by outcome

- **Feature frequencies and capture matrices:** descriptive proportions with whole-game cluster-bootstrap intervals and simultaneous bands where needed.
- **Expected-score loss:** a two-part model separating the probability of positive loss from the size of loss when positive.
- **Severe-loss occurrence:** binomial marginal regression with game clustering; report risk difference as the primary effect.
- **Win/draw/loss:** game-level nominal multinomial regression, with learner score rate as a secondary summary.
- **Volatility:** a predefined robust dispersion measure with Brown–Forsythe/Levene-style testing and whole-game bootstrap rather than an ordinary variance F-test.
- **Immediate response to opponent behavior:** non-overlapping response episodes, adjusted for the position before the response and clustered by game.
- **Longitudinal change:** game- or fixed-period marginal models with calendar-block bootstrap.

## Proposed adjustment and coverage policy

- Predeclare a small adjustment set including learner colour, rating difference, time class/control, opening, deterministic phase, calendar period, and relevant pre-move material or evaluation state.
- Do not adjust for facts occurring after the move being studied.
- Do not impute missing engine analysis by default.
- Report eligible, comparable, and missing counts and coverage rates by feature and comparison group.
- Include both quick and full rank-one results as the same outcome shape.
- Suppress promotion when a model fails, the independent game sample is inadequate, one game/opponent/opening/position dominates, or coverage is materially inadequate.

## Confidence and multiplicity policy to finalise in Part 2

- Freeze each catalogue version's feature definitions, eligible population, outcome, adjustment set, engine rules, drill-downs, null, direction, test family, correction method, and minimum-effect rule before running it.
- The researched proposal is Benjamini–Hochberg false-discovery-rate control across the complete predeclared backend discovery family.
- A stronger product-facing gate may use Holm or Westfall–Young family-wise confirmation, later-game confirmation, or a deliberately approved combination.
- Require adequate independent game counts, effect-size and interval rules, model stability, bootstrap stability, coverage, and resistance to influential clusters. A p-value alone is insufficient.
- Use the complete frozen historical snapshot rather than wasting a personal dataset on a simple history split. Freeze any finding definition before testing it against later games.
- Failed and underpowered tests remain diagnostics only.

The exact stronger correction, minimum meaningful effects, confirmation rule, severe-loss threshold, phase definition, opponent-behavior windows, volatility measure, and tactical rules remain Part 2 decisions.

## Dependencies and validation

- Current Python dependencies do not include a statistical modelling library.
- The researched conventional stack is NumPy/SciPy plus statsmodels.
- Bayesian modelling is not the initial recommendation because it adds prior sensitivity, heavier dependencies, and more complex calibration.
- Validation should use deterministic simulations covering nested moves, unequal game lengths, repeated opponents/openings/positions, confounding, zero-heavy losses, rare events, missing coverage, multiple testing, and longitudinal drift.
- Required checks include false-positive control, interval coverage, pseudoreplication resistance, rare-category suppression, missingness behavior, model convergence, and bootstrap stability.

The research basis includes Liang and Zeger on GEE, Cameron and Miller on cluster-robust inference, Benjamini and Hochberg on false-discovery control, Brown–Cai–DasGupta on binomial intervals, NIST guidance for robust dispersion testing, Rubin on missing-data mechanisms, and Davison and Hinkley on bootstrap methods.

## Part 2 output and stopping point

Part 2 produces:

- a versioned deterministic feature catalogue;
- the fitted and validated statistical model families;
- complete backend diagnostics for all defined questions;
- a product-facing catalogue containing only findings that pass the approved high-confidence gate;
- exact supporting samples, effects, intervals, coverage, and model provenance for every finding.

Part 2 stops at evidence. It does not silently turn a statistical association into a training lesson or integrate findings into the trainer.

# Part 3 — Finalise and regrill the learning workflow

## Trigger

Begin Part 3 only after Part 2 has produced real supported findings. The next grilling round should use those findings as its evidence rather than trying to predict the user's weaknesses in advance.

## Regrilling agenda

- Decide which supported findings are meaningful learning focuses rather than merely statistically reliable descriptions.
- Decide how to show the deterministic evidence without claiming an AI-generated or engine-generated explanation.
- Inspect representative positions supporting each finding.
- Decide what chess lesson, if any, follows from the pattern.
- Decide how to construct varied exercises that test a reusable decision pattern rather than memorisation of one exact non-opening position.
- Decide what counts as a sound answer when several moves avoid the error.
- Decide how to measure improvement across later games and related positions.
- Decide how opening recall and pattern-based learning belong in one day-to-day workflow.
- Decide how the analysis, repertoire, trainer, and progress views connect.

## Earlier learning hypotheses to revisit

- Opening recall remains an obvious, directly measurable learning method because opening positions recur.
- For a mistake-repair exercise, any sound move within a reasonable evaluation range may be more useful than requiring the engine's exact best move.
- Repeating an exact non-opening position is not enough because the position is unlikely to recur.
- A reusable lesson may concern a broader decision pattern, such as exchanging a bishop for a pinned knight at the wrong time.
- Individual positions should support an aggregate pattern, not serve as the starting point for an invented explanation.

These are directional hypotheses for Part 3, not authorization to build the final learning experience before the evidence exists.

## Explicit exclusions

- Do not treat one corrected move as proof that a weakness is fixed.
- Do not build non-opening learning around exact-position memorisation.
- Do not require the exact engine-best move when another approved sound move solves the problem.
- Do not use AI-generated explanations or pattern labels.
- Do not force each blunder into a predefined tactical-motif label before analysing the game population.
- Do not expose unsupported or underpowered statistical observations as possible weaknesses.
- Do not implement the final learning workflow before the Part 3 grilling decisions are confirmed.

# Appendix (2026-09-22) — Retired single-blunder lookup: what was built and what to keep

Part 1 is now complete (see `docs/plans/done/chess-learning-part-1-analysis-infrastructure.md`).
The worker fills quick (`browser`, 200,000 nodes, SinglePV) coverage in the background while full
(`tool`, 6,400,000 nodes, MultiPV 5) stays an explicit upgrade. Rank-one quick and full results are
pooled together for move-quality work. The older single-blunder lookup described below still runs,
but it is superseded by the Part 2 population analysis and can be removed so it is not in the way.
The full build record stays in `docs/grilling-docs/blunder-training-backend-2026-09-21.md`.

## What existed

- Domain reader: `src/chess_move_trainer/database/blunders/` (`__init__.py`, `models.py`,
  `repository.py`, `scoring.py`, `loaders.py`, `records.py`, `errors.py`).
- HTTP layer: `backend/app/features/trainer_blunders/` (`__init__.py`, `router.py`,
  `api_schemas.py`), served as `GET /api/trainer/blunders` with operation id `getTrainerBlunders`.
- Wiring: `get_blunder_policy()` in `backend/app/dependencies.py`,
  `trainer_blunders_key()` in `backend/app/caching.py`, router registration in
  `backend/app/main.py`.
- Tests: `tests/database/blunders/test_blunders.py` plus
  `backend/tests/features/trainer_blunders/` (`conftest.py`, `test_api.py`).
  Contract checks naming this endpoint also live in
  `backend/tests/features/health/test_contract_export.py` and
  `frontend/src/api/generatedSurface.test.ts`.
- Generated surface only: `frontend/src/api/generated/` (`openapi.json`, `sdk.gen.ts`,
  `types.gen.ts`, `index.ts`, `@tanstack/react-query.gen.ts`) plus the re-export in
  `frontend/src/api/client.ts`. No feature under `frontend/src/features/` calls it.
- It wrote nothing: no table, no migration, no JSON store. It read `datasource_game`,
  `derived_game_position`, `derived_position`, `derived_analysis_result`, and
  `derived_analysis_line`.

## Definition that worked

- A blunder was one trainer move losing at least `0.20` expected game points.
- Expected score came from Stockfish win/draw/loss values: `win + 0.5 * draw`, viewed from the
  trainer's colour. Stored WDL values are per-mille White-perspective numbers that sum to 1000.
- Example: a White move at 0.65 expected score followed by 0.40 is a 0.25 loss and counts;
  an exact 0.20 loss also counts. Using WDL this way handled centipawn and mate scores with one
  rule instead of inventing a centipawn value for mate.
- The `0.20` default lived only in `backend/app/dependencies.py`
  (`CHESS_BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS`, default `0.20`). The domain `BlunderPolicy`
  itself had no hard-coded default. An invalid configured threshold made only this endpoint
  return controlled `503 trainer_blunders_unavailable`.

## How it derived the answer

- It paired consecutive positions in one game (`derived_game_position` ordered by ply) and kept
  only moves where the side to move matched the stored trainer colour.
- Both the before and after positions needed a completed rank-one analysis. A before-position
  terminal needed no search and was not comparable. An after-position terminal was scored
  directly: checkmate is 0 or 1 by side to move, stalemate and insufficient material are 0.5.
- It never guessed missing analysis. Every in-scope trainer move was either comparable or counted
  in `skipped_missing_analysis_count`.
- It checked stored data with `python-chess`: the outgoing move had to be legal and reach the
  next stored position, the preferred move (first move of the before-position principal variation)
  had to be legal, positions had to be canonical, and WDL had to sum to 1000.
- Request rules: mandatory inclusive RFC3339 `started_at_from` / `started_at_to` (normalized the
  same way as game search), optional `trainer_color`, `page` from 1, `page_size` 1 through 100.
- Result order was deterministic: largest loss first, then later game start, then game UUID, then ply.
- Response fields reused the training-requirements names `fen`, `trainer_color`, and
  `preferred_move_uci` so a client could show the board exercise without SQLite identifiers. Score
  floats were rounded to six places. Each item also carried game UUID, source URL, start time, ply,
  played move, before/after scores and loss, and before/after analysis quality (`browser`/`tool`).
- Coverage counts were explicit: examined, excluded (bad timestamp), in-scope games, trainer moves,
  comparable moves, and skipped-for-missing-analysis moves.
- Errors: bad timeframe/filter gave `422 invalid_filter`; bad storage or schema gave controlled
  `503`; anything unexpected gave `500`.

## What the tests proved

Focused verification passed 54 tests across the domain and API suites. They covered White and
Black score perspective, exact-threshold inclusion, timestamp normalization and inclusive bounds,
trainer-turn filtering, later-ply FEN handling, legal preferred moves, missing-analysis coverage,
terminal scoring, deterministic ordering and pagination, large-ID reads, read-only behavior,
missing/incompatible storage, strict API output, policy configuration, caching, controlled errors,
and OpenAPI registration. Part 1 Stage 2 also kept `tests/database/blunders/test_blunders.py`
passing to prove rank-one pooling across current `browser` and `tool` results.

## Why removal is safe

- Read-only: deleting it changes no stored games, positions, analysis results, or queue rows.
- No schema or worker dependency: the Stockfish queue, worker, profiles, publication rules, and
  background discovery do not import it.
- No product caller: no code under `frontend/src/features/` uses it; only the generated SDK,
  the `client.ts` re-export, and the two contract-surface tests name it.
- Removal must include the wiring and contract updates, not just the domain folder: the router and
  schemas, `get_blunder_policy`, `trainer_blunders_key`, `main.py` registration, both test suites,
  the two contract-surface test expectations, and regeneration of `frontend/src/api/generated/`.
  The catalogue mentions at `docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md:75,507-508`
  become historical references once removed.

## What Part 2 can reuse

- The WDL-to-expected-score conversion (`(wins + 0.5 * draws) / 1000`, trainer perspective) and
  the terminal after-position scoring above. These are the same before/after comparison Part 2
  needs for expected-score loss and severe-loss questions.
- The consecutive before/after pairing over `derived_game_position` plus the legality/canonical
  checks as a pattern for building versioned move-feature records.
- The coverage-counting pattern: eligible, comparable, missing, plus excluded games counted
  separately, instead of silently dropping incomplete data.
- The lesson about what not to keep: a single-move list sorted by loss is a starting-point
  inspector, not a finding. Part 2 must still run the population models (game-clustered inference,
  multiplicity control, coverage and stability gates) and Part 3 must still decide what, if
  anything, becomes a lesson. Do not carry the `0.20` threshold forward as an approved severe-loss
  definition; Part 2 sets that threshold explicitly.
