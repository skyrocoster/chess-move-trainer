# Astra's Reflections

Started: 2026-09-19.

## Purpose and reading guide

This is an evolving, evidence-based review to help you decide where Chess Move Trainer should go next. At your request, I ask myself one question at a time, investigate it using only Scout subagents, and save the answer before starting the next question. No application code is being implemented.

These are my reflections, **not your decisions, an approved Plan, or permission to implement anything**. Recommendations are deliberately separate from repository facts. Source inspection does not prove that a feature works in a running application. No runtime tests have been run for this document.

Entries will include an answer, supporting file references, possible direction, tradeoffs, and remaining uncertainty. Earlier entries may be qualified by later evidence rather than silently treated as final conclusions.

## Progress

- Completed reflections: 3.
- Current question: **Can a new user get enough suitable data into the application to benefit from that training model?**

## Reflections

### 1. What useful training journey can a person actually complete with the features already present?

**Answer:** The application lets someone inspect a known game, explore moves, and save a preferred move. It also lets them find positions that need training. Source inspection does **not** show a complete browser-based practice session where the person answers those positions and records the results.

The distinction matters: `/repertoire` is an interactive study and editing workspace; `/trainer` currently displays training requirements. Calling both of these “practice” would hide the gap between preparing material and testing recall.

**Evidence:**
- `frontend/src/App.tsx` wires `/`, `/repertoire`, and `/trainer` into the real application.
- `frontend/src/features/game/GameLoader.tsx` loads a game by UUID. `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx` supports legal moves, history, branches, analysis, and preferred-move interaction.
- `frontend/src/features/repertoire-builder/preferredMoveWorkflowState.ts` implements saving, removing, and playing a preferred move, including re-reading the preference after a write. Persistence lives in `backend/app/features/preferred_moves/router.py`.
- `frontend/src/features/trainer-practice/TrainerPracticePage.tsx` and `TrainerPracticePanel.tsx` select an opening, colour, and date and display positions, preferred moves, balances, and answer requirements. There is no interactive answering board on that page.
- `backend/app/features/position_training_requirements/router.py` already exposes an answer-submission endpoint. The Scout found no live frontend caller for it.

**My reflection:** The strongest candidate for the next product direction is completing one small practice loop using the existing training data, not adding another way to inspect it. For example: select an opening, receive one position, make a move without seeing the answer, receive feedback, and have that attempt recorded.

**Tradeoff:** That prioritises usefulness over a wider set of editing and analysis options. It also depends on whether the existing answer rules are suitable for a real session; that is the next question, not an assumption.

**Other friction:** A person must already know a game UUID to load it. The training listing does not link directly to its position in the repertoire workspace. Those are separate access problems, even if the answer loop is completed.

**Uncertainty:** This is a source-level account, not a browser check. Storybook candidates and experiments were not counted as shipped behaviour. The Scout reported no active Plan files at the time of inspection.

### 2. How much of a real answer-and-feedback training loop already exists behind the interface?

**Answer:** Substantially more than the current trainer screen exposes. The backend accepts a position, learner colour, date, and played move. It checks legality, compares the answer with the saved preferred move, updates training credit, and returns the new requirement. A browser practice loop would not need to invent these core operations.

**Evidence:**
- `backend/app/features/position_training_requirements/router.py`, `submit_position_training_answer`, exposes `POST /api/positions/training-requirements/answers` and clears cached requirement results after success.
- `src/chess_move_trainer/database/positions/training_answers.py` validates the FEN, side to move, UCI move, and legality. Correctness is `request.played_move_uci == preferred_move_uci`; an engine does not judge the answer.
- That module persists an aggregate balance for the position/preferred-move pair. A correct answer adds credit; a wrong legal answer subtracts credit. It returns correctness and a freshly calculated requirement, including `correct_answers_needed`.
- Writes use a transaction and a bounded database-lock wait. Future dates and dates older than the stored update are rejected. Same-day submissions remain valid.
- `tests/database/positions/test_training_answers.py` covers credit changes, decay, invalid/stale/future input, rollback, and lock timeout. `tests/database/positions/test_training_requirements_concurrency.py` checks that two concurrent submissions both count. These tests were inspected, not executed.

**My reflection:** This product is currently designed to test **recall of your repertoire**, not to judge every objectively good chess move. That is a coherent purpose. The interface should say “That is not your saved move” rather than implying that every different legal move is bad chess.

**Important constraint:** There is no duplicate-request protection in this contract. If a request succeeds but the response is lost, sending it again can count the attempt twice. Serialising database writes prevents a different problem; it does not make retries safe. A real answering interface needs a deliberate policy for uncertain submissions, and stronger retry guarantees would require a backend change.

**History constraint:** The persisted record is an aggregate, not a list of individual attempts. It can support “how much practice is needed now,” but not an honest reconstruction of “which answers did I give last Tuesday?” without additional storage.

**Possible direction:** Reuse this backend for a small recall session, while explicitly deciding answer visibility, uncertain-submit handling, and when to advance or finish. Avoid expanding into engine-judged exercises unless that is a separate chosen product goal.

**Uncertainty and correction:** This bounded inspection did not investigate preferred-move creation. Entry 1 already established a user-facing save path; the preference table should not be interpreted as evidence that only a background process can choose the answer. The educational meaning of the scoring formula still needs inspection.

### 3. What does the training score actually encourage someone to practise?

**Answer:** Repairing departures from a preferred repertoire in actual games, with practice credit that fades over time. This is not currently a general-purpose system for learning arbitrary new positions before you encounter them in games.

**Evidence:**
- `backend/app/dependencies.py` supplies a target success rate of 0.8 and a practice-credit half-life of 30 days.
- `src/chess_move_trainer/database/positions/training_requirements_models.py` turns that target into a game-miss weight of 4, versus 1 for a hit.
- `src/chess_move_trainer/database/positions/training_requirements_scoring.py` calculates game balance as `hits - 4 × misses`, then adds `T × abs(T)`, where `T` is the effective practice balance. A negative total means training is required.
- `src/chess_move_trainer/database/positions/training_answers.py` adds or subtracts 1 from the effective balance for each answer. After time decay the balance can be fractional; it is not necessarily an integer.
- `src/chess_move_trainer/database/positions/training_requirements_repository.py` and the answer implementation limit eligible game evidence by position, trainer colour, usable game date, and applicable preferred-move periods. Answer submission rejects positions without eligible game encounters.

**Concrete example:** With two game hits and one miss, game balance is `2 - 4 = -2`. Starting with no practice credit, one correct answer gives an adjustment of 1, leaving the total at -1. A second gives an adjustment of 4, bringing it to +2. That position no longer requires training under this rule. With no new game evidence, after 30 days the adjustment falls from 4 to 2, and after further decay the position will need training again.

**My reflection:** There is a clear product identity here: “Use my games to find repertoire moves I need to remember.” That is more specific than “learn chess openings,” and it could be a strength if the user understands it.

**Caution about repeated answers:** Larger positive balances produce disproportionately larger credit because the adjustment is squared. Repeating an already-revealed answer immediately can therefore reduce the requirement quickly. The storage tracks net balance, not streaks or spaced recall; it cannot establish that repetition represents durable learning. A future session should deliberately choose whether and when to repeat a position.

**Tradeoff to decide:**
- Keep the game-driven model as the central promise: fewer concepts, strongly connected to actual mistakes.
- Add a separate “learn new repertoire” mode: useful before playing games, but it needs eligibility and progress rules beyond the existing game-driven requirement.

**Preference changes matter:** Game encounters are interpreted using the preference that applied on their date, and only evidence compatible with the currently selected preferred move contributes. Practice credit is stored per position/move pair. Switching to a never-trained move has no previous credit; switching back may find an existing aggregate. Changing a preference is therefore more than changing a label on a flashcard.

**Uncertainty:** The formula is implemented policy, not evidence of educational effectiveness. High encounter frequency alone does not imply a high need to train: the balance of hits and misses matters. This inspection did not establish the best queue order or validate the defaults with users.
