# Saved move panel redesign

> **Status:** direction settled on 2026-08-29

## Intent

Adopt the state-driven side-panel UX from
`experiments/mock-ups/saved-moves/saved-move.html` for `/repertoire`, while preserving the application's accepted
board, evaluation, navigation, storage, and session design. Reusable information panels introduced by this work
must be real shared components and must also work fully in `/viewer` where applicable.

The mock-up is directional evidence for the surrounding panels, not a source implementation. Its board,
evaluation treatment, palette, and Local Session strip are not adopted.

## Settled experience

### Repertoire state panel

- The side panel changes meaningfully with the current workflow state rather than exposing one static form.
- On the user's turn with no saved move, it explains that no preferred move is saved and invites the user to play
  a move before saving it.
- On the user's turn with a saved move, it presents that move and the existing go-to/play, edit, remove, and date
  capabilities in the adapted design.
- After the user plays a move, the board advances normally. The panel remains focused on that last move long
  enough to show either:
  - confirmation that it matched the preferred move; or
  - that it is not saved, with an action to save it as the preferred move.
- The mock-up's **Not now** action is omitted.
- Existing chess-session semantics remain linear. Playing a different move from an earlier position may replace
  or truncate the later local continuation; this work does not introduce variation trees.

### Effective date

- A saved preferred move displays its persisted effective date, including a friendly `Today` presentation when
  applicable.
- The date remains changeable through the adapted panel.
- The preferred-move read contract must expose the stored effective date so the display remains truthful after a
  reload. The existing append-only preferred-move storage direction is preserved.

### Position reach frequency

- The frequency bar measures how often the user reaches the **current position**; it does not measure how often a
  particular preferred move was played.
- Its population is colour-correct:

  `the user's games as the repertoire colour that reached this position / all of the user's games as that colour`

- It updates after the user's move, after an opponent move, and whenever history navigation changes the current
  position. It remains useful even at positions where the user cannot save a preferred move.
- Position Reach Frequency is an independently reusable component. The repertoire state panel may wrap it now,
  but it must not be coupled to that panel so it can be reused elsewhere later.

### Shared move history

- Move History is a true shared component used by both `/repertoire` and `/viewer`.
- Selecting a SAN move jumps the board to that position.
- The active move is visually clear, remains synchronized with existing Previous/Next navigation, and is kept in
  view by automatic scrolling.
- Keyboard navigation follows established chess-product conventions without displacing accepted application
  controls: previous/next navigation and start/end navigation must be available, with accessible focus behavior.
- The component uses the existing linear history. Variation authoring and branch management are excluded.

### Viewer replacement

- In `/viewer`, Move History replaces Game Context **in place** rather than adding a competing sidebar card.
- Essential accepted context, including source and ply information, remains available in the replacement
  presentation.

## Live-product research considered

Research was checked on 2026-08-29 against Lichess Analysis/Study behavior and source, Chess.com Analysis/Game
Review and official support material, and Chessable keyboard documentation.

The products consistently support clickable or tappable move navigation, a clear active move, keyboard stepping,
and board synchronization. Lichess additionally keeps the active row visible automatically. Lichess and
Chess.com preserve alternate continuations as variations, but that pattern is deliberately not adopted here
because it would change Chess Move Trainer's linear session model and materially expand this redesign.

Position statistics in established products update with the viewed position. That supports updating the reusable
reach-frequency component on every board/history transition rather than attaching it only to a saved move.

## Existing system boundaries

- Use the application's existing Material/CMT design tokens, typography, spacing, radii, focus treatment,
  reduced-motion behavior, forced-colour support, and design-system primitives. Do not copy the mock-up's inline
  colour system.
- Preserve the existing board and evaluation components and their behavior.
- Preserve accepted preferred-move authority, append-only event storage, repertoire navigation, and local-session
  rules except for the explicitly settled presentation and read-contract additions above.
- Replace existing presentation in place where the new components supersede it; do not leave duplicate Game
  Context or plain-text history panels.
- The active line-library Plan remains independent. This direction must not take ownership of its selector or
  future preferred-move-line contract.
- No new dependency, variation model, training behavior, or unrelated route redesign is authorized.

## Planning handoff

This direction is broad enough for a master plan with independently reviewable, sequential slices. The first
child Plan should establish the reusable foundations and contracts needed by later repertoire and viewer
integration without attempting the entire destination in one implementation Plan.
