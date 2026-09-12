# Cross-game position training requirements

## Goal

Find the positions the trainer gets wrong across all imported games and calculate whether each position currently requires training. Expose the resulting figures through a thin positions collection API in the existing positions API area. The existing position-insight API remains responsible for the full position details needed by a future Learn interface.

This is no longer an API of separate missed-game occurrences. Game occurrences are evidence used to calculate one requirement for each position and preferred-move pair.

## Game evidence

- Analyze all imported games, not one game at a time.
- Analyze only moves made by each game's stored trainer color.
- Treat every encountered position with an active preferred move as eligible. Do not impose a fixed opening-ply cutoff or require a separate opening classification.
- Resolve the preferred move using the preference period active at the game's start time.
- Group evidence by the unique combination of canonical position and preferred move.
- Every encounter counts independently, including repeated encounters with the same canonical position in one game. A played move matching the active preferred move is one hit; a different played move is one miss. Do not add per-game deduplication or special mixed-result handling for this edge case.
- The game balance must represent a target real-game success rate above 50%. The former `G = game hits - game misses` proposal, which treated a bare majority as sufficient, was rejected.
- The target success rate must be a validated scoring input rather than a constant embedded in the calculation. The initial implementation obtains the application-wide scoring policy from backend configuration, with an 80% default target. Individual games are not otherwise weighted by recency or game identity.
- Use evidence-volume normalization `G = game hits - (target / (1 - target)) * game misses`. At the 80% default this is `G = game hits - 4 * game misses`. This keeps each hit worth one point, puts zero at the selected success rate, and lets a larger game sample provide proportionally stronger evidence.
- Keep the calculation parameterized so a later frontend can supply validated scoring details without replacing the scoring implementation. Frontend-provided scoring details are not part of the initial implementation.
- A position with no configured preference or an explicit `no_preference` contributes no evidence.
- A game without a usable start time cannot be compared with the preference timeline and contributes no evidence.
- Game evidence is calculated live from the current stored preference history. Correcting that history may therefore change old games' contributions.
- Different preferred moves for the same position have separate evidence and training state. If a former preferred move becomes active again, its existing pair is used again.

## Settled training state

- The backend is authoritative. A training-answer request supplies the played move; the backend resolves the preferred move for the request's explicit `as_of` date and decides whether the answer is correct.
- Store training state in the primary chess database through a deliberate schema v2 upgrade.
- Add one aggregate table with one row keyed by canonical position and preferred move.
- Store one signed, potentially fractional training balance `T`, initially zero, together with its latest aggregate update date.
- Before applying an answer, decay the stored aggregate to the request's scoring date. A correct backend-judged answer then replaces it with `effective T + 1`; a wrong answer replaces it with `effective T - 1`.
- Keep the one-unit wrong-answer rule. Do not reset positive strength or apply an additional wrong-answer multiplier; the squared curve already makes the requirement impact of `T - 1` increase with the balance's magnitude.
- Do not store an attempt log, separate training occurrences, or dates for every attempt. The balance and its one aggregate update date are the intended level of persistence.
- The training row does not depend on a preference period. Its preferred move is part of the key; its update date exists only to calculate decay.

## Required scoring behavior

- The game starting point `G` reflects the selected target success rate but does not otherwise weight individual games.
- The weighting belongs to the aggregate training adjustment derived from `T`.
- Let `F(T)` be that weighted adjustment. The exposed requirement is `R = G + F(T)`.
- Training is required exactly when `R < 0`.
- The number of net correct training answers needed to overcome increasingly negative game balances must flatten rather than grow one-for-one or grow exponentially.
- The earlier linear proposal `F(T) = 0.75 * T` does not provide that flattening and is no longer the settled formula.

## Unsettled scoring numbers

The selected default target real-game success rate is 80%, with evidence-volume normalization `G = hits - 4 * misses`: four hits offset one miss, while six hits and five misses produce `G = -14` and still require training.

The selected training adjustment is the squared-credit curve `F(T) = T * abs(T)`. A game balance of `-5` needs three net correct training answers, `-10` needs four, and `-100` needs ten. This curve still flattens the repetition count substantially while avoiding the doubling curve's abrupt jumps and very large excess credit. The doubling candidate `sign(T) * (2^abs(T) - 1)` was rejected.

## Selected time-decay direction

- Use true aggregate decay rather than refreshing all historical training strength after one new answer.
- Apply smooth exponential decay with a configurable half-life to signed training credit while lifetime game evidence remains unchanged. Positive and negative training effects therefore move toward zero with time. The backend-configured default credit half-life is 30 days.
- Derive the effective fractional balance at the scoring date before applying `+1` or `-1`, then persist that updated aggregate and its update date. This avoids resurrecting old strength and does not require an attempt log.
- Decay uses whole calendar days between the aggregate's update date and the request's explicit `as_of` date. Multiple answers on one date have no decay between them; exact timestamps and timezone-dependent decay are excluded.
- True aggregate decay is active in the initial implementation so schema v2 begins with the required fractional balance and aggregate update date. The half-life is configurable with a 30-day default.

## API ownership and shape

- Extend the existing positions API area; do not create a separate missed-occurrence analysis API.
- Keep `GET /api/positions/insight` unchanged as the single-position detail operation. It continues to own opening details, experience, observed moves, engine analysis, and the preferred move for `fen`, `trainer_color`, and `as_of`.
- Add a separate thin collection operation for discovering scored positions. Do not overload the single-position insight response.
- Keep discovery compact but return an explainable backend-calculated scoring breakdown: the position identity required to call the existing insight API, trainer color, preferred move, encounter count, hits, misses, observed success rate, game balance, effective training balance, signed training adjustment, final training requirement, required/not-required state, and minimum additional correct answers needed at the response's `as_of` date. Return the applied scoring policy once in the collection envelope. Do not make the frontend reproduce scoring calculations, and do not duplicate opening, engine, or other full insight details.
- Allow callers to filter the collection by a training-requirement range. This must support fetching required positions below zero as well as positions only just above zero.
- Require at least one training-requirement range boundary. Reject an unfiltered discovery request rather than silently defaulting below zero or returning every eligible position.
- Allow discovery to filter by the repository's stable opening key. Reuse the existing games API distinction between `opening_match=reached` for broader route/transposition association and `opening_match=deepest` for the most specific recognized opening. Opening filtering does not add opening details to the thin result.
- Use an explicit `as_of` date for both discovery and answer submission so the backend and the existing insight endpoint resolve the same active preferred move.
- Reject discovery or answer submission when its `as_of` date is earlier than relevant persisted aggregate training state. The backend must not silently include future training or attempt historical reconstruction without an attempt log.
- Allow discovery to use a future `as_of` date as a non-mutating preview of decay and future training requirements. Reject answer submission when `as_of` is later than the backend's current calendar date so a future-dated mutation cannot advance and lock the aggregate timeline.
- Add a thin answer-submission operation that accepts the played move. The backend judges it, first decays the resolved position and preferred-move pair's aggregate to the scoring date, and then replaces the aggregate `T` value with its one-answer adjustment.
- Exact route names, range-parameter spelling and boundary syntax, validation status codes, and mutation response fields are assessment details unless assessment identifies a user-visible behavior choice. They do not require grilling.

Illustrative, not yet name-approved, discovery flow:

```http
GET /api/positions/training-requirements?as_of=2026-09-12&training_requirement_lt=0
GET /api/positions/training-requirements?as_of=2026-09-12&training_requirement_gt=0&training_requirement_lte=1
```

The caller then requests the selected position's full details from the existing endpoint:

```http
GET /api/positions/insight?fen=...&trainer_color=white&as_of=2026-09-12
```

## Deferred and excluded

- The Learn button and all other frontend work.
- Session size, ordering, randomization, repetition timing, and presentation.
- Training review states beyond the aggregate signed balance.
- An audit or event history of individual training answers.
- Duplicating position-insight fields in the thin discovery response.
- Accepting frontend-provided scoring details in the initial API.

## Remaining user-visible decisions

- Obtain user approval of the revised real-data output prototype before assessment and planning.

Exact API spelling, status codes, persistence representation, numeric precision, pagination, and other mechanical details can proceed to repository assessment after these behaviors are settled.

## Approved real database example and output prototype

The current schema-v1 database at `data/database/chess.db` contains an active, mixed-result pair suitable for assessment and focused tests:

- Canonical FEN: `rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1`
- Trainer color: White
- Preferred move: `b1c3` (`Nc3`), active from 2024-02-29 with no end date
- Opening reference: `B02:Alekhine Defense`
- Eligible encounters as of 2026-09-12: 86, consisting of 28 hits and 58 misses
- At the 80% policy: `G = 28 - 4 * 58 = -204`
- Schema v1 has no training aggregate, so the prototype uses `T = 0`, training adjustment `0`, and `R = -204`
- Fifteen correct answers on the same scoring date would be the minimum to make this pair non-required: `15^2 = 225`, producing `R = 21`

Prototype collection response:

```json
{
  "as_of": "2026-09-12",
  "scoring_policy": {
    "target_success_rate": 0.8,
    "game_hit_weight": 1.0,
    "game_miss_weight": 4.0,
    "training_curve": "squared",
    "training_credit_half_life_days": 30
  },
  "items": [
    {
      "fen": "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
      "trainer_color": "white",
      "preferred_move_uci": "b1c3",
      "encounters": 86,
      "hits": 28,
      "misses": 58,
      "observed_success_rate": 0.325581,
      "game_balance": -204.0,
      "effective_training_balance": 0.0,
      "training_adjustment": 0.0,
      "training_updated_on": null,
      "training_requirement": -204.0,
      "training_required": true,
      "correct_answers_needed": 15
    }
  ]
}
```

## Approval and next step

The user approved the real-data output prototype on 2026-09-12. Repository assessment and Plan writing may proceed. Sol owns assessment and Plan writing; Luna owns later sequential Plan implementation.
