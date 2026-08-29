# Position picker and local session - one in-memory legal line from start or a stored prefix

> **Status:** accepted/done - W1 complete; fresh final Quality validation passed and the Plan is archived

- **Read trigger:** Read before each W1 execution stage, before changing the Repertoire Builder session, picker,
  promotion, navigation, orientation, or focused proof surfaces, and at final closeout.
- **Upstream:** [Repertoire Builder master Plan](../../../../master-plans/repertoire-builder/repertoire-builder.md);
  [confirmed Repertoire Builder direction](../../../../grilling-docs/DONE/repertoire-builder-direction.md);
  [accepted R2 scaffold Plan](../../../../plans/done/repertoire-builder/repertoire-builder-scaffold/repertoire-builder-scaffold.md);
  [accepted V1 Viewer Flip/navigation Plan](../../../../plans/done/repertoire-builder/viewer-flip-navigation/viewer-flip-navigation.md);
  [accepted V2 Viewer position-count Plan](../../../../plans/done/repertoire-builder/viewer-position-count/viewer-position-count.md);
  [accepted V3 clickable-analysis-moves Plan](../../../../plans/done/repertoire-builder/viewer-clickable-analysis-moves/viewer-clickable-analysis-moves.md);
  [accepted R1 reusable UTC calendar Plan](../../../../plans/done/repertoire-builder/reusable-utc-calendar/reusable-utc-calendar.md)

## Outcome

Extend the existing `/repertoire` scaffold with a page-owned, in-memory position-picker session. A person can use the
standard starting position or load a stored game UUID and Ply, see the complete stored prefix through the selected Ply,
and continue one legal SAN line with board dragging or the existing displayed legal analysis candidates. Promotion uses
the existing promotion path. Local Previous/Next, position-preserving Flip, staged bottom-side ("my") moves, and
immediate opponent moves work without persistence or a move tree.

The session owns its local continuation only; it does not read or write preferred moves and does not create a new Viewer,
workspace, storage, or API abstraction.

## Scope

- **Included:** A Repertoire Builder session model and pure in-memory history; standard-start initialization; reuse of the
  existing game-loader and `Game`/`GamePosition` types for stored-game loading; complete prefix composition through the
  selected Ply; one legal local SAN line; page-owned board, candidate, promotion, navigation, and orientation wiring;
  bottom-side staging and opponent-turn advancement; focused component/model tests; existing token and responsive
  conventions; the existing Repertoire Builder Storybook story surface; and one bounded feature-specific Storybook
  browser spec only when the focused Storybook proof needs it.
- **Expected areas:** `frontend/src/features/repertoire-builder/**` source, tests, stories, and local CSS except its
  README; existing `frontend/src/features/viewer/GameLoader*`, `gameModel.ts`, and `positionApi.ts` seams for game
  loading; existing `frontend/src/features/board-adapter/BoardAdapter*`, `PromotionPicker*`, and the legal interactive
  board seam; existing `frontend/src/features/viewer/BoardControl*`; existing `frontend/src/features/analysis/AnalysisPanel*`
  only for bounded composition or regression proof; focused existing seam tests where required; and
  `tests/e2e/repertoire-builder-storybook.spec.ts` plus `tests/e2e/playwright.config.ts` only if the approved dedicated
  Storybook browser proof is added to the existing Storybook server selection. This Plan record is included.
- **Excluded:** Preferred-move reads, writes, Add/Save/Edit/Play/Remove behavior, date/calendar mutation, recurrence
  context, persistence of any kind including browser storage, backend/API/database/schema/storage changes, S5 work,
  new game-loading contracts, multiple lines or a move tree, automatic engine or preferred-move selection, invented
  commit/advance behavior, and changes to accepted Viewer behavior. Separate chess Undo or Reset controls are excluded;
  any existing loader-form reset remains a loader concern rather than a chess-session control. New dependencies, new
  Playwright profiles, universal Viewer/session/workspace extraction, unrelated visual redesign, README or historical
  record edits, runtime writes, generated artifacts, commits, pushes, and unrelated worktree changes are excluded.

## Stages

1. **complete - Establish the page-owned session model and start/prefix semantics.** Make both approved starting modes
   produce one deterministic in-memory session without introducing persistence or copying Viewer branch ownership.
   - **Ordered actions:** Re-read this Plan, the master Plan, the confirmed direction, the accepted R2 scaffold, and the
     accepted V1/V2/V3/R1 records. Inspect the current Repertoire Builder scaffold and the named game-loading, chess,
     board, promotion, candidate, and navigation seams before editing. Keep standard start as the default with White at
     the bottom. Reuse the existing game lookup and loader values/types for an optional stored UUID and Ply. For a stored
     game, retain and display the complete game prefix through the selected Ply, then establish the local continuation
     from that position; do not reduce the loaded state to an invented alternate FEN or change the game API contract.
     Model one local history with canonical legal SAN/FEN progression and a current location, keeping prefix context
     distinct from the mutable continuation. Set the initial bottom to the recorded subject color for a stored game and
     White for standard start. Keep all state page-owned and in memory.
   - **Focused proof:** Repertoire Builder model/workspace tests cover standard start, valid stored UUID/Ply loading,
     complete-prefix-through-selected-Ply state, subject-color initial bottom, malformed/unavailable load handling through
     existing conventions, one-line history, current position/FEN, and no persistence or API writes.
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/repertoire-builder`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** Stop and escalate if complete-prefix loading, the existing lookup/result types, standard-start
     initialization, subject-color orientation, or in-memory ownership requires a new API, storage contract, Viewer
     behavior, identity rule, or user-facing failure decision.

2. **complete - Compose legal board/candidate moves, promotion, navigation, and Flip.** Make the local session usable
   without adopting the Viewer branch panel or chess Undo/Reset presentation.
   - **Ordered actions:** Re-read the current Repertoire Builder surface and the accepted V1/V3 seams before editing.
     Render the current session position through the existing board boundary and expose legal board dragging plus the
     existing displayed legal candidate activation path, including Best line, without changing AnalysisPanel or Viewer
     semantics. Use the existing promotion controller/picker and its focus and cancellation behavior for promotion
     moves; do not duplicate promotion rules or embed `InteractiveBoardAdapter`'s temporary-branch panel. Reuse the
     existing Previous/Next/Flip control seam as a leaf while keeping navigation state in the Repertoire page. Previous
     and Next traverse the local in-memory session history. A selected move on a turn where the current bottom color is
     to move is staged as a "my" move and does not silently persist or acquire an unrecorded commit/advance action; a
     move on the opposing turn advances immediately as local context. Flip preserves the current FEN and session
     location, cancels pending staging, and reinterprets which color is "me." After backtracking, choosing a replacement
     truncates only the later local continuation rather than creating a branch or affecting any persisted data (there is
     no persisted data in W1). Preserve accessible labels, focus restoration, constrained layout, and no-overflow local
     conventions.
   - **Focused proof:** Focused Repertoire Builder tests cover legal drag and candidate activation, first-move-only
     candidate behavior, normal and promotion moves, staged bottom-side moves, immediate opponent moves, Previous/Next
     traversal, replacement truncation, Flip FEN preservation and pending-stage cancellation, both initial orientations,
     keyboard/focus behavior, terminal/legal rejection safety, and absence of chess Undo/Reset controls. Include only
     bounded regression tests for reused promotion, candidate, board, or navigation seams when their public behavior is
     exercised by the composition.
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/repertoire-builder src/features/board-adapter/PromotionPicker.test.tsx src/features/analysis/AnalysisPanel.test.tsx src/features/viewer/BoardControl.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** Stop and escalate if legal move or promotion behavior cannot be reused without duplicate chess
     rules, if candidate activation needs a changed engine/API contract, or if navigation, staging, Flip, focus,
     orientation, accessibility, responsive ownership, or the no-Undo/Reset boundary is not derivable from the settled
     direction and existing seams.

3. **complete - Prove the W1 surface through Storybook and bounded browser coverage.** Make the approved start, stored
   prefix, local line, promotion, navigation, orientation, and staging states inspectable without creating a browser
   profile or changing the Viewer.
   - **Ordered actions:** Reconcile the existing Repertoire Builder stories with standard-start, stored-prefix,
     subject-color, local-line, candidate, promotion, staged-my, opponent-immediate, navigation, replacement, Flip,
     constrained, keyboard, and accessibility states using deterministic in-memory fixtures. Build Storybook before its
     interaction suite and use the configured command without an unsupported `--url` argument. The assessed dedicated
     `tests/e2e/repertoire-builder-storybook.spec.ts` is permitted only as a feature-specific browser surface for these
     W1 stories; if added, register it with the existing Storybook test-file selection so it uses the existing bounded
     Storybook server, not a new profile or server contract. Prove wide and constrained fit, board visibility, accessible
     candidate/promotion controls, local navigation, FEN-preserving Flip, cancellation of pending staging, replacement
     truncation, and no horizontal overflow. Bound Storybook readiness to 30 seconds, clean up only the server started
     for proof, and confirm port 6006 is free afterward.
   - **Focused proof:**
     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     If the dedicated feature-specific browser surface is added:

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`

     Each command has a recommended finite `bash` tool timeout of `360000` ms; Storybook startup health has a separate
     maximum of 30 seconds and the server must not remain running after proof.
   - **Breakpoint:** A bounded visual and accessibility review is required at the existing wide and constrained states.
     Stop rather than guessing if the picker needs new hierarchy, exact copy, iconography, selector contracts, focus
     behavior, responsive rules, Storybook configuration, browser profile, dependency, or acceptance scope.

4. **accepted/done - Complete read-only validation and prepare coordinator closeout.** Confirm W1 while preserving all
   unrelated, accepted, and historical material before independent Quality validation.
   - **Ordered actions:** Re-run the focused session/workspace and reused-seam tests, frontend build, Storybook build and
     interactions, the conditional dedicated Storybook browser proof, lint, read-only Prettier, source-size validation,
     and whitespace proof. Run the exact governing repository check without `--fix` or `--full`. A trivial deterministic
     formatting repair is preauthorized only in W1-touched files when a check identifies it; inspect the resulting scope
     and do not use `scripts/check.py --fix` or perform semantic repair. Perform one final Git scope audit against the
     coordinator baseline during execution only. Preserve R2, V1/V2/V3/R1, Viewer behavior, backend/API/storage, all
     historical records, and unrelated worktree material. Report unrelated failures rather than absorbing them.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/repertoire-builder src/features/board-adapter/PromotionPicker.test.tsx src/features/analysis/AnalysisPanel.test.tsx src/features/viewer/BoardControl.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     If the dedicated feature-specific browser surface is added:

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`

     `timeout 120s npm.cmd run lint --prefix frontend`

     `timeout 120s frontend/node_modules/.bin/prettier.cmd --check frontend/src/features/repertoire-builder frontend/src/features/board-adapter/PromotionPicker.tsx frontend/src/features/analysis/AnalysisPanel.tsx frontend/src/features/viewer/BoardControl.tsx tests/e2e/playwright.config.ts` (and `tests/e2e/repertoire-builder-storybook.spec.ts` when the conditional spec is added)

     `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`

     `timeout 30s git diff --check`

     `timeout 600s .venv/Scripts/python.exe scripts/check.py`

     Recommended finite `bash` tool timeouts are respectively `150000`, `150000`, `360000`, `360000`, `360000`,
     `150000`, `150000`, `90000`, `60000`, and `660000` ms. The governing closeout runs without `--fix` or `--full`.
   - **Breakpoint:** Coordinator-owned independent Quality validation, successful bounded Storybook cleanup with port
     6006 confirmation, final acceptance, and a clean scope audit are required before archival. Stop for any unrelated
     failure requiring repair or any scope, product, visual, API, data, dependency, ownership, acceptance, or safety
     expansion.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome or
requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - session model and standard/stored-prefix start semantics; focused Repertoire Builder proof and
  frontend build passed; breakpoint: none.
- **Stage 2:** complete - legal board/candidate moves, promotion, local navigation, staging, opponent advancement, and
  position-preserving Flip; focused interaction, accessibility, and regression proof passed; breakpoint: none.
- **Stage 3:** complete - Storybook states and bounded browser proof; Storybook passed 172 tests and the dedicated
  Storybook browser proof passed 4 tests; required proof ports were clean afterward; breakpoint: none.
- **Stage 4:** accepted/done - read-only closeout passed focused case proof at 60 tests, frontend build, lint, read-only
  Prettier, source-size, whitespace, and the exact full `scripts/check.py` check; fresh independent Quality validation
  passed and the scope audit was clean; breakpoint: none.
- **Settled decisions:** Stored sessions retain the complete prefix through the selected Ply. Standard start begins with
  White at the bottom; stored games begin with the recorded subject color. The bottom color is "me." Flip preserves FEN
  and location, cancels pending staging, and changes which color is "me." Previous/Next are local session navigation;
  replacing a continuation after backtracking truncates later local history. W1 has one in-memory legal SAN line, no
  persistence, no move tree, and no separate chess Undo/Reset UI.
- **No invented behavior:** W1 does not add a commit, save, advance, persistence, preferred-move, or engine-authority
  behavior beyond the recorded staged-my and immediate-opponent semantics. W2 owns the later explicit preferred-move
  workflow.
- **Closeout decisions:** Accept W1 as done. The accepted behavior is standard or complete stored-prefix start, one local
  SAN line, legal board/candidate/promotion moves, staged bottom-side ("my") moves, immediate opponent moves, local
  navigation with replacement truncation, and position-preserving Flip that cancels staging. No persistence, chess
  Undo/Reset controls, or Viewer behavior changes were introduced. The separate README updater changed
  `frontend/README.md` and `frontend/src/features/repertoire-builder/README.md`; this closeout does not edit README,
  product, or test files and does not expand W1 scope.

## Proof

- Focused Vitest/React Testing Library proof covers standard and stored-prefix initialization, complete prefix retention,
  legal SAN/FEN progression, board and candidate activation, promotion, staged bottom-side moves, immediate opponent
  moves, local Previous/Next, replacement truncation, Flip preservation/cancellation, subject-color orientation, focus,
  accessibility, and the absence of chess Undo/Reset controls.
- Existing game-loading, BoardAdapter, PromotionPicker, AnalysisPanel candidate, and BoardControl seams are reused and
  regression-tested only where the Repertoire composition exercises them; Viewer behavior and ownership remain unchanged.
- Storybook stories and interactions cover standard, stored-prefix, promotion, staged/opponent, navigation, Flip,
  constrained, keyboard, accessibility, and no-overflow states. The optional dedicated browser spec is feature-specific,
  uses the existing Storybook server selection, has bounded readiness and cleanup, and is not a new browser profile.
- Frontend build, lint, read-only Prettier, source-size validation, `git diff --check`, and the exact
  `timeout 600s .venv/Scripts/python.exe scripts/check.py` closeout run with finite command and tool timeouts and no
  `--fix` or `--full`.
- Final case proof passed 60 focused tests, frontend build, Storybook build/interactions at 172 tests, the dedicated
  Storybook browser proof at 4 tests, lint, read-only Prettier, source-size validation, `git diff --check`, and the exact
  full `scripts/check.py` closeout; proof ports were clean afterward.
- Fresh independent Quality validation additionally passed 6 responsive browser tests, 23 reused-seam tests, and the
  semantic, persistence, and scope audits. Quality noted the unrelated pre-existing untracked root `NUL`; it was
  preserved, reported, and not deleted.
- Final scope review preserves the accepted A1/V1/V2/V3/R1/R2 records, Viewer behavior, backend/API/storage boundaries,
  historical records, and unrelated worktree material. Any preauthorized formatting repair is deterministic, targeted,
  and semantic-free.

## Acceptance

- Standard start opens with White at the bottom. A stored game UUID and selected Ply load the complete game prefix through
  that Ply and initially place the recorded subject color at the bottom.
- The session remains in memory and exposes one legal SAN line. Board dragging and every existing displayed legal
  candidate, including Best line, use the same legal move path; promotion uses the existing promotion picker and no
  later candidate/PV moves are applied.
- The bottom color is "me." A move selected while the side to move matches the bottom color is staged only; it is not
  silently saved or advanced by an invented W1 action. A move selected on the opposing turn advances immediately as local
  context and is never persisted.
- Previous and Next navigate local session history. Backtracking and selecting a replacement removes only the later
  local continuation and never creates a move tree. Flip preserves the current FEN and session location, cancels pending
  staging, and reinterprets which color is "me."
- No separate chess Undo or Reset UI, persistence, preferred-move mutation, schema/API change, or Viewer/universal
  abstraction is introduced.
- Focused tests, Storybook proof, any approved feature-specific Storybook browser proof, finite repository checks,
  coordinator-owned independent Quality validation, final acceptance, and the scope audit pass.

## Escalation boundaries

- Any unresolved interpretation of prefix completeness, selected Ply, local navigation/history, replacement truncation,
  staging versus advancement, subject-color orientation, Flip cancellation, or bottom-as-"me" semantics.
- Any need for a new product, visual, API, data, dependency, destructive, ownership, accessibility, focus, responsive,
  selector, or acceptance decision; any automatic engine/preferred-move authority; or any invented commit/save/advance
  behavior.
- Any need to alter Viewer behavior, copy Viewer branch/Undo/Reset presentation, extract a universal workspace/session,
  change accepted game-loading or promotion/candidate contracts, add persistence, add a move tree, or modify backend,
  schema, storage, S5, or the preferred-move API.
- Any new browser profile, unsupported Storybook command/configuration, unbounded test/server/cleanup command, occupied
  port 6006 after proof, generated artifact, source/test size violation, runtime write, historical-record edit, commit,
  push, direct baseline collision, or unrelated failure requiring repair or scope absorption.

## Visible result

> **Accepted W1 result:** A person can start at standard chess or a complete stored-game prefix, make one legal local
> SAN line with board/candidate moves and promotion, navigate it locally, flip without changing the position, and see
> bottom-side choices staged while opponent moves advance immediately, with no persistence or chess Undo/Reset controls.
