# Repertoire fully armed game sessions - Loaded games navigate and play as one immediate session

> **Status:** done - all five stages accepted; focused unit and browser proof passed

- **Read trigger:** Before assessing or implementing the expanded `CONSUMER-02` Repertoire migration.
- **Upstream:** [expanded CONSUMER-02 grilling record](../../../grilling-docs/database-rebuild-consumer-02.md) and the [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md).

## Outcome

Repertoire can optionally load a known game through the generated clean `getGame()` operation and turn the complete
response into one fully armed session. The loaded main line is navigable from Ply 0, every legal move advances the
session immediately, and one simple temporary alternative can be explored without losing the imported game. The
selected transition retains its parent FEN and outgoing UCI so explicit Preferred Move actions still apply to the
position the move came from.

## Scope

- **Included:** A neutral clean game-detail/main-line mapper; replacement of the legacy Repertoire game-loading
  transport; complete imported-game session state; Previous/Next/Home/End/direct history navigation; immediate
  main-line matching and one linear temporary branch with Return to game; selected-transition Preferred Move
  derivation; direct generated-client loading with cancellation, reset, loading, and error behavior; removal of the
  optional Ply input and obsolete load-time `position_not_found`; selected-position panel requests; focused component
  and browser proof; the explicit client-adoption guard; and the already-completed bounded active master-plan
  correction.
- **Expected areas:** `frontend/src/api/{client.ts,noAdoption.test.ts}`, `frontend/src/features/game/`,
  `frontend/src/features/repertoire-builder/`, `tests/e2e/repertoire-builder-storybook.spec.ts`, and
  `docs/master-plans/database-rebuild/database-rebuild.md`.
- **Excluded:** Backend/API contract changes; migration of Position Context, Move Response Distribution, Analysis, or
  Preferred Move HTTP operations; retirement of `/api/games/{game_uuid}/positions`; fallback or compatibility layers;
  eager panel requests, speculative caching, autoplay, automatic preference writes, game trees, branch collections or
  persistence, authored repertoire lines, Viewer work, database work, broad maintenance, unrelated cleanup, and any
  commit, push, branch, worktree, or stash.

## Stages

1. **done** - Establish the neutral clean game-detail boundary without changing production wiring. Ordered actions:
   map generated `GameDetailResponse.occurrences` (`ply`, `fen`, `move_uci`) into a neutral feature/session main-line
   model; derive the existing SAN-style presentation deterministically from FEN/UCI; retain UUID, actual initial FEN,
   trainer orientation, and every ordered occurrence; and keep clean extra metadata, PGN, source-link, and player data
   out of the UI. Do not synthesize the legacy `{ initial_ply, subject_color, positions }` transport envelope or expose
   a replacement `GameLookupResult` compatibility shape. Preserve any still-needed legacy Position Context ownership
   colocated in `frontend/src/features/game/positionApi.ts`. Focused proof: from `G:\ChessMoveTrainer\frontend`,
   command-level timeout 120s and Bash tool timeout 150000ms,
   `timeout 120s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/game/gameModel.test.ts`
   covers complete occurrence mapping, Ply 0, SAN, actual initial FEN, orientation, and metadata exclusion. Breakpoint:
   escalate if the clean response lacks deterministic FEN/UCI data or would require changing the accepted API contract.
2. **done** - Prove the destination session boundary as a pure model before production cutover. Ordered actions:
   establish a neutral, unmounted boundary model and its invariants for an optional fresh standard-start session and a
   successful imported session with the complete immutable main line selected at Ply 0; represent the selected current
   position and selected transition `{ parentFEN, outgoingUCI }`; represent at most one temporary linear branch; define
   navigation over the active line, branch replacement from earlier history, Return to game, Reset, and replacement by a
   new load; and keep the current staged production model and handlers untouched until the atomic cutover stage. This
   pure boundary is not a second mounted production session model or a compatibility layer. Focused proof: from
   `G:\ChessMoveTrainer\frontend`, command-level timeout 120s and Bash tool timeout 150000ms,
   `timeout 120s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/positionPickerSessionBoundary.test.ts`
   covers fresh/reset state, complete imported history with Next enabled, all navigation bounds, immutable main line,
   one branch, branch-tail replacement, no rejoin, Return to game, selected transition, and Ply 0. Breakpoint:
   escalate any requirement for a branch tree, branch switching, persistence, rejoin, or a second mounted production
   session model.
3. **done** - Perform one atomic Repertoire production cutover after the destination invariants pass. Ordered
   actions: use `getGame({ path: { game_uuid }, signal })` through `frontend/src/api/client.ts`; replace `fetchGame`,
   `GameLookup`, `GameLookupResult`, and the legacy game-detail transport in the Repertoire load path with the neutral
   mapper and destination session input; remove the Game Loader Ply field, `initialPly`, and load-time
   `position_not_found`; deliberately map clean `game_not_found`, `games_unavailable`, validation, and unexpected
   failures into the existing accessible user-level loading/error behavior where equivalent; preserve optional loading,
   fresh standard-start behavior, and Reset; and do not use `useQuery`, a second cache, or a second game-loading path.
   In this same atomic cutover, replace the staged parent/child lifecycle and every direct `stagedMove`/`commitStagedMove`
   consumer with the destination session: imported continuation matches by clean outgoing UCI; divergence preserves the
   immutable main line and makes active history imported prefix plus one branch; replay from earlier branch history may
   replace its tail; no automatic rejoin; Return to game discards the entire branch and selects its branch point; and a
   new load or Reset discards the session without confirmation or persistence. Immediate advancement works in fresh and
   loaded sessions. The board, Move History, current Ply, side to move, Position Context, primary Analysis, evaluation
   display, Move Response Distribution, and Preferred Move state all use one selected current position; supporting data
   requests only that selected FEN with existing cancellation/stale protection; no all-occurrence prefetch or session
   cache is added. Preferred candidates derive from the selected parent FEN/outgoing UCI for imported trainer
   transitions, manually played matching trainer transitions, and trainer branch transitions; opponent transitions and
   Ply 0 are excluded; explicit save/replace/remove and date semantics remain, with no autosave. Keep `positionApi.ts`
   ownership needed by legacy Position Context; do not silently migrate or delete that later consumer. In the same
   atomic cutover, replace the blanket `frontend/src/api/noAdoption.test.ts` assertion with the explicit approved-
   consumer guard: allow only accepted Status and Repertoire `getGame()` imports through `api/client`, prohibit direct
   generated-directory imports, and prohibit premature later-operation production adoption. Focused proof:
   from `G:\ChessMoveTrainer\frontend`, command-level timeout 240s and Bash tool timeout 270000ms,
   `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/game/GameLoader.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBoardLane.test.tsx src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/preferredMoveState.test.ts src/features/repertoire-builder/PreferredMovePanel.test.tsx src/api/noAdoption.test.ts`
   covers fresh/reset, optional load, complete loaded history at Ply 0 with Next enabled, clean success/error mapping,
   immediate fresh/loaded moves, UCI matching, divergence, replacement, Return to game, new-load/reset discard, one
   selected position, lazy selected-FEN requests, stale cancellation, all three trainer-transition origins,
   opponent/Ply 0 exclusions, explicit persistence/date behavior, and no automatic save. Breakpoint: escalate if atomic
   cutover reveals another production consumer, requires a fallback/compatibility layer, changes the accepted error or
   API contract, or requires retiring a legacy route.
4. **done** - Add the Storybook fixture and immediately prove the complete browser journey without changing the
   settled visual direction. Ordered actions: update only the existing Repertoire fixtures and accessibility assertions
   needed for complete imported navigation, recorded continuation, divergence, Return to game, immediate moves, and
   parent-labelled Preferred Move actions in `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`
   and `frontend/src/features/repertoire-builder/repertoireBuilderStoryHelpers.ts`; preserve existing SAN appearance,
   responsive composition, keyboard behavior, loading/error accessibility, and absence of clean PGN/source/extra-
   metadata UI; and use only existing Vitest, React Testing Library, user-event, accessibility, and Playwright
   facilities, with no MSW or hook-testing dependency. No Storybook play functions are planned to change, so no
   Storybook Vitest project run is required. Focused proof: from `G:\ChessMoveTrainer`, command-level timeout 240s and
   Bash tool timeout 270000ms, run the exact updated scenario with the config that starts its bounded Storybook server:
   `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "proves imported game session navigation, immediate branching, return, and preferred parent" --timeout=30000`. Breakpoint: pause for coordinator review only if the existing presentation cannot express Return to game without a new visual direction.
5. **done** - Close the documentation envelope without further product work. Ordered actions: verify the completed
   `CONSUMER-02` master-plan correction and expanded grilling reference remain aligned with this Plan; preserve later slice
   ordering, CLEAN analysis semantics, and route-retirement timing; and do not treat documentation verification as a
   second implementation stage. Focused proof: manual line-by-line review of the grilling record, this Plan, and the
   changed master-plan passages against the coverage map and dependency order. Breakpoint: escalate any contradiction in
   approved behavior, ownership, acceptance, or later-slice contracts.

Stages are sequential and must each leave production and its focused tests coherent. A passing proof remains valid until
a later stage changes its command, inputs, exercised behavior, configuration, dependencies, or environment; later stages
rerun only invalidated proof. Stage 1 and Stage 2 are pure boundaries/fixtures only; they must not create a second mounted
production session model. Stage 3 is the atomic production cutover for the old staged lifecycle, its direct consumers,
and the adoption guard. Stage 4 owns each Storybook fixture change and its immediate browser proof.

## Progress and decisions

- **Assessment:** done - repository map, clean-client facts, session seams, proof seams, and exclusions are retained in
  the upstream grilling record.
- **Planning correction:** done - the master-plan `CONSUMER-02` row, consumer envelope, risk, and visible-result
  description were expanded, and the grilling record is now a governing reference; Stage 5 verifies rather than edits
  them.
- **Stage 1:** done - neutral clean mapping retains UUID, actual Ply 0 FEN, trainer orientation, and every ordered
  occurrence; deterministic SAN derives from parent FEN/outgoing UCI; focused proof passed 3 tests; breakpoint: none.
- **Stage 2:** done - pure unmounted boundary covers fresh/imported state, complete immutable main line, bounded
  navigation, selected transitions, one temporary branch, branch-tail replacement, Return to game, Reset, and load
  replacement; proof: 10 focused tests passed; breakpoint: no second mounted production model.
- **Stage 3:** done - Repertoire uses clean `getGame()` and one destination session for immediate fresh/loaded moves,
  full imported navigation, one temporary branch/Return to game, selected-position requests, parent-transition Preferred
  Move actions, and the explicit adoption guard; proof: 68 focused tests passed across 9 files; breakpoint: none.
- **Stage 4:** done - clean imported-game Storybook fixtures and the focused journey cover Ply 0, full history,
  immediate recorded continuation, branch divergence/replacement, Return to game, and parent-labelled Preferred Move
  action; proof: the exact focused Playwright scenario passed; breakpoint: no visual direction change.
- **Stage 5:** done - manual line-by-line review confirmed the grilling record, Plan, and master-plan correction align;
  later-slice ordering, CLEAN analysis semantics, adoption limits, and route-retirement timing remain intact.

### Grilling coverage map

| Grilling family | Plan coverage |
|---|---|
| Optional loading, fresh standard start, Reset, and load replacement | Stages 2-3; Stage 3 focused proof |
| Clean mapping, complete history, SAN, identity, presentation, and error handling | Stages 1 and 3; Stage 4 journey |
| One selected current position and lazy selected-FEN workflows | Stage 3; Stage 4 browser proof |
| Immutable main line, UCI matching, one branch, replacement, Return, no rejoin/persistence | Stages 2-3; Stage 3 unit proof and Stage 4 browser proof |
| Immediate moves and selected parent/outgoing-UCI Preferred Move model | Stage 3; Stage 4 journey |
| Tooling, direct client adoption, no cache/dependencies, and explicit guard | Stage 3 |
| Boundaries, later consumers, route retirement, and master-plan correction | Scope exclusions, escalation boundaries, and Progress; Stage 5 verification |

## Proof

- **Neutral mapping:** workdir `G:\ChessMoveTrainer\frontend`; command-level timeout 120s; Bash tool timeout
  150000ms; `timeout 120s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/game/gameModel.test.ts`.
- **Pure session boundary:** workdir `G:\ChessMoveTrainer\frontend`; command-level timeout 120s; Bash tool timeout
  150000ms; `timeout 120s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/repertoire-builder/positionPickerSessionBoundary.test.ts`.
- **Atomic load/session/move cutover:** workdir `G:\ChessMoveTrainer\frontend`; command-level timeout 240s; Bash tool
  timeout 270000ms; `timeout 240s npm exec vitest -- --project unit --run --testTimeout=20000 src/features/game/GameLoader.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx src/features/repertoire-builder/RepertoireBoardLane.test.tsx src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/preferredMoveState.test.ts src/features/repertoire-builder/PreferredMovePanel.test.tsx src/api/noAdoption.test.ts`.
- **Focused browser journey and changed Storybook fixture:** workdir `G:\ChessMoveTrainer`; command-level timeout 240s;
  Bash tool timeout 270000ms;
  `timeout 240s npm exec playwright test -- --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "proves imported game session navigation, immediate branching, return, and preferred parent" --timeout=30000`. The config starts the bounded Storybook server; no separately pre-running server is required.
- **Documentation closeout:** workdir `G:\ChessMoveTrainer`; manual line-by-line review of the grilling record, this
  Plan, and the changed master-plan passages; no command or Bash tool invocation.
- CLEAN-02 backend/generated proof is retained. No lint, formatting, broad type/build, source-size, aggregate,
  hygiene, backend, full-suite, whole-Storybook, or legacy-route-retirement check belongs to this Plan.

## Escalation boundaries

- Any new product behavior beyond the confirmed optional complete-session, immediate-move, and one-branch semantics.
- Any visual redesign, new dependency, API/schema/route change, backend change, legacy-route retirement, or migration of
  a later consumer.
- Any need for a mounted compatibility session, game tree, branch persistence or switching, rejoin behavior, automatic
  preference writes, eager panel loading, cache, fallback, or direct generated-directory imports.
- Any newly discovered production consumer, ownership conflict, destructive effect, changed acceptance, or error behavior
  that cannot preserve the existing accessible user-level meaning.

## Visible result

> A user can leave Repertoire fresh, load a game at Ply 0, navigate its full SAN history, play the recorded line or one
> temporary alternative immediately, return to the imported game, and explicitly save a selected trainer move for its
> parent position.
