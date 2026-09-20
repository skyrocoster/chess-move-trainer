# Training page completion

**Started:** 2026-09-20  
**Status:** Implemented and locally verified.  
**Authority:** The user asked for the remainder of the training page to be implemented directly, without a question round. This record explains the product decisions made during that work; it is not a separate Plan.

## Goal

Turn `/trainer` from a retrieval/debug listing into a usable recall loop: choose training material, solve one board position at a time, receive backend-judged feedback, and finish with a short session summary.

## Repository facts found before implementation

- `TrainerPracticePage.tsx` already retrieves every training-required position for the selected opening, learner colour, and date.
- `TrainerPracticePanel.tsx` currently exposes raw response metadata, FEN values, and preferred moves. Showing `preferred_move_uci` before an attempt gives away the answer.
- `POST /api/positions/training-requirements/answers` already validates a legal move, compares it with the saved preferred move, updates training credit, and returns the updated requirement.
- `InteractiveBoardAdapter` and `InteractiveBoardHarness` already provide the legal-move board, promotion picker, answer highlights, orientation, and locked feedback states needed by the trainer. The training page should reuse them rather than build another board.
- The answer endpoint stores an aggregate balance rather than an attempt history and has no request idempotency key. A lost response therefore must not trigger an automatic mutation retry.

## Decisions recorded during implementation

### Session shape

- A successful search with positions starts a focused session immediately; there is no second setup screen that repeats the filters the user just chose.
- The backend response order is retained. No randomization or new scheduling rule is introduced.
- One retrieved position is shown at a time, with visible progress and the board oriented to the learner's colour.
- The saved move stays hidden until the answer has been judged or the user explicitly reveals it.

### Answer behavior

- Illegal board input is rejected locally and does not call the answer endpoint.
- The first legal move is submitted once and locks the board while the backend judges it.
- Correct and incorrect results both show the played move and the saved move. Copy says “saved move,” not “best move,” because the backend judges repertoire recall rather than objective chess quality.
- “Show saved move” is a review action. It does not write a correct or incorrect answer and it advances only when the user chooses to continue.
- A failed or uncertain answer submission is never retried automatically. The screen explains that it could not confirm the answer and lets the user continue, avoiding an accidental double count.

### Session completion

- The session summary reports positions completed, correct first answers, saved moves reviewed, and unconfirmed submissions. It does not claim mastery or retention.
- Training-requirement queries are invalidated after confirmed answers so a later search reflects the updated backend score.
- The existing filters remain available above the session. Running a new search replaces the current session with the new result set.

## Verification log

- The generated answer operation is now exposed through `frontend/src/api/client.ts` and wrapped by `submitTrainingAnswer` with typed stale, missing, and uncertain failure states.
- `TrainerSession.tsx` now owns the one-position-at-a-time session, reuses the existing interactive board, promotion behavior, shared UCI parsing, design-system feedback and buttons, and Base UI progress behavior, submits only legal moves, reveals feedback, advances the queue, and presents the final summary.
- `TrainerPracticePanel.tsx` now starts that session instead of printing raw API fields. The existing opening, colour, date, loading, empty, stale, and retry states remain in place.
- The shared board harness gained only the optional orientation, hidden-branch-panel, and rejected-move-notice controls needed for this reuse. Existing callers keep their previous defaults.
- The focused Vitest run passed: **73 tests passed** across the trainer page/API, interactive board adapter, and shared game move mapping.
- The frontend application TypeScript check passed with no errors.
- The targeted Prettier check passed for every changed TypeScript, CSS, end-to-end test, and documentation file.
- Per the user's explicit instruction, no development service was started. Browser and Playwright runtime checks were therefore not run in this session; the Playwright expectations were updated to the new session UI for the next existing-service run.
