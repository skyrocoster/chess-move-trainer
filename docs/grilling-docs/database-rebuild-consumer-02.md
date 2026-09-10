# Database rebuild CONSUMER-02: fully armed Repertoire game sessions

> **Confirmed:** 2026-09-09
> **Role:** Directional evidence for assessment and planning; not implementation authorization.
> **Authority:** This records the decisions reached with the user for the expanded `CONSUMER-02` slice. It
> supersedes the earlier staged-move-preview interaction where the decisions conflict, while leaving completed
> historical records unchanged.

## Decision

Migrate Repertoire game loading to the generated clean `getGame()` operation and use the complete returned game to
create a fully armed Repertoire session. This is intentionally broader than a transport-only migration: the same Plan
must replace Repertoire's split preview/current-position model with one immediate-advance session model because full
game navigation, imported moves, local alternatives, and Preferred Move selection all meet at that boundary.

The visible result is one understandable workspace:

- loading a game immediately makes its complete main line available in Move History;
- the board can move backward and forward through that game;
- all position-dependent panels follow the selected position rather than eagerly loading every game position;
- playing the recorded continuation advances along the imported game;
- playing a different move creates one simple temporary alternative without destroying the imported game; and
- every played move advances the session immediately, while the selected transition retains enough parent-and-move
  information for an explicit Preferred Move action.

## Loaded-game behavior

- Loading a known game remains optional. Repertoire still opens in its existing fresh standard-start local session with
  no imported game selected, and Reset returns to that state. Complete-game navigation and imported-main-line behavior
  activate only after a successful UUID load.
- Use the generated `getGame()` client exported through `frontend/src/api/client.ts`. Do not call the legacy
  `/api/games/{game_uuid}/positions` route, add a fallback, or recreate the legacy HTTP contract behind an adapter.
- Remove the optional Ply input. A loaded game always starts at its first occurrence (Ply 0); there is no load-time
  `position_not_found` outcome.
- Retain the complete ordered game in the session rather than slicing and discarding everything after a selected Ply.
- Preserve the useful current identity and presentation behavior: the game UUID, its actual initial FEN, trainer-color
  orientation, existing loading/reset/error accessibility, and the current SAN-style Move History presentation.
- Populate Move History with the complete imported game as soon as loading succeeds. Previous, Next, Home, End, and
  direct history selection navigate the imported main line, with the initial position selected after load.
- Derive the existing SAN presentation from the clean occurrence FENs and outgoing UCI moves. The API remains the sole
  source of game data; no legacy game request or PGN-shaped fallback is allowed.
- Do not add displays for the clean response's extra metadata merely because it is available. In particular, no new
  PGN, rating, result, time-control, player-identity, or source-link interface belongs to this slice.

## Selected-position behavior

Loading the complete game arms the workspace; it does not eagerly load every panel for every occurrence.

- The selected game or branch position is the one current position for the board, current Ply, side to move, Position
  Context, Analysis, evaluation display, Move Response Distribution, and Preferred Move workflow.
- Navigate first, then let the existing position-dependent workflows request data for that selected FEN. Preserve their
  finite cancellation/stale-response protections.
- Do not prefetch supporting data for every game position or introduce a cache merely to make navigation speculative.
- This slice does not migrate Position Context, Move Response Distribution, Analysis, or Preferred Move HTTP calls to
  their clean generated operations. Those remain the later consumer slices named by the master plan.

## Main line and one temporary branch

The imported game is an immutable main line for the lifetime of the loaded session.

- If a board move matches the imported game's recorded next UCI move, advance along the imported main line.
- If it differs, retain the imported game and create one temporary branch from that game position.
- While branching, Move History remains linear: show the imported prefix through the branch point followed by the
  temporary branch. Do not render a tree or show multiple alternatives.
- Moves played after the first divergence extend the one active branch. Navigating backward and replacing its tail may
  retain the existing single-line behavior; do not create a branch collection.
- Provide one clear **Return to game** action while a branch is active. It discards the complete temporary branch and
  returns to the branch point on the intact imported main line.
- A later alternative does not automatically rejoin the imported game merely because it reaches the same FEN. Rejoin,
  branch persistence, branch switching, and authored repertoire trees are excluded.
- Loading another game or using the existing Reset behavior replaces the current session as it does today; no branch
  persistence or discard-confirmation workflow is required.

## Corrected move and Preferred Move model

Remove the hidden staged board-move lifecycle. Every legal board move immediately advances to its resulting position
and enters the active Move History path. The board and panels must not remain split between a displayed child and a
canonical parent.

Preferred Move semantics still require the parent position. Preserve that information explicitly as the selected
transition rather than by holding the whole workspace one move behind:

```text
parent FEN + selected outgoing UCI move
```

- When the selected transition was made by the trainer's color, its move is an available candidate for the parent
  position's Preferred Move action.
- The same rule applies whether the trainer move came from the imported game, matched the main line when played on the
  board, or belongs to the temporary branch.
- Navigating to an imported trainer move therefore allows the user to save that move as preferred for the position it
  came from.
- Selection never saves automatically. Existing explicit save/replace/remove actions and their date behavior remain in
  control.
- Opponent-side transitions are not Preferred Move candidates. At Ply 0 there is no incoming transition.
- The interface must make the parent-and-move meaning understandable; it must not imply that a preference belongs to
  the resulting child position.

This decision deliberately supersedes the accepted staged-preview behavior that left the board, evaluation rail, and
move-response display on a child position while Move History, current Ply, side to move, Position Context, and the main
Analysis panel remained on the parent. Completed Plans recording that earlier decision remain historical and must not
be rewritten.

## Repository facts informing the decision

- The clean `GET /api/games/{game_uuid}` operation is already generated as `getGame()`. It returns complete metadata,
  original PGN, trainer color, and ordered occurrences containing Ply, FEN, and outgoing `move_uci`.
- `frontend/src/api/client.ts` already configures and re-exports the generated client with the application's API base
  URL.
- The legacy backend also returned the complete game. Current frontend `createStoredGameSession` truncates it with
  `positions.slice(0, selectedPly + 1)`, so the loss of the later game is a frontend session decision rather than a
  backend limitation.
- Current navigation primitives and Move History already support previous, next, home, end, and arbitrary history
  selection, but only across the truncated stored prefix plus one local continuation.
- Current Repertoire board moves made by the trainer's color enter a special `stagedMove` preview. That preview changes
  some displayed child-FEN surfaces while retaining the parent for history, context, side-to-move, and primary analysis.
  Preferred Move save currently depends on this staged flag even though the parent position and move can be represented
  as an ordinary selected transition.
- The clean game response has sufficient ordered FEN/UCI information to validate and build the complete navigable game
  and its SAN presentation without calling the legacy route.

## Planning and ordering requirements

Treat this as one expanded `CONSUMER-02` Plan because the generated response mapping, complete game timeline, navigation,
branch behavior, immediate move advancement, and Preferred Move transition semantics all change the same Repertoire
session model. Do not produce two competing session rewrites.

The Plan must order the work so lower-level invariants exist before workspace integration. At minimum, assessment must
decide an AI-executable sequence covering:

1. the complete clean game-detail mapping and deterministic SAN/main-line representation;
2. a session model that retains an immutable imported main line, selected position, selected transition, and at most one
   temporary branch;
3. immediate move advancement, main-line matching, linear branch replacement, Return to game, and complete navigation;
4. Preferred Move derivation from the selected trainer transition without the staged-preview dependency;
5. generated-client loading integration, Ply removal, cancellation/error handling, and workspace presentation; and
6. focused component/browser proof of the complete user journey and explicit checks that later consumer APIs did not
   migrate and the legacy backend route was not retired.

The assessment may refine stage boundaries to avoid invalid intermediate states, but it must not weaken or reorder the
semantic dependencies above merely to mirror current file layout.

## Client-state and test tooling

- Call the generated `getGame()` operation directly through `frontend/src/api/client.ts` for this explicit
  submit/cancel/reset workflow. Do not add a second TanStack Query cache around the loaded Repertoire session.
- The existing TanStack Query dependency and providers remain available for consumers such as Status that benefit from
  query lifecycle behavior. Do not add Query devtools, persistence, another TanStack package, or a new server-state
  abstraction for this slice.
- Use the repository's existing Vitest, React Testing Library, user-event, accessibility, Storybook interaction, and
  Playwright facilities. Do not add MSW, a hook-testing package, or another testing dependency.
- Replace the stale blanket assertion in `frontend/src/api/noAdoption.test.ts`, which still forbids every production
  import of `api/client` despite accepted Status adoption, with an explicit approved-consumer guard. It must allow the
  accepted Status usage and this Repertoire `getGame()` usage while continuing to detect premature adoption of later
  clean operations or direct imports from the generated directory.

## Boundaries

- No fallback, compatibility shim, legacy game-detail call, or second game-loading path.
- No retirement of `/api/games/{game_uuid}/positions`; that remains `RETIRE-01` after all required consumer work.
- No migration of position insight, move response, analysis, or preferred-move HTTP operations.
- No eager all-position requests, speculative cache, autoplay, engine-selected moves, or automatic preference writes.
- No new TanStack Query or testing dependency.
- No game tree, branch collection, branch persistence, authored repertoire-line store, calendar redesign, or new
  backend/database behavior.
- No Viewer restoration or migration, old-database work, broad maintenance run, commit, push, branch, worktree, or
  unrelated cleanup.
- Preserve unrelated worktree changes and completed historical records.

## Master-plan consequence

The active database-rebuild master plan currently describes `CONSUMER-02` only as generated clean game-detail adoption
with preserved Repertoire behavior. Planning must carry this confirmed expansion into the active slice description,
envelope, risks, and visible result without changing the ordering or contracts of later consumer and retirement slices.
