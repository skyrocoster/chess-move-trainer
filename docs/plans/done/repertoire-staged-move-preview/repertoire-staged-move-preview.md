# Repertoire Staged-Move Preview - A legal bottom-side move appears without committing the local session

> **Status:** done - implementation and independent validation passed; repository closeout reruns were waived by the user

- **Read trigger:** Read before executing the approved `/repertoire` staged-preview behavior change.

## Outcome

When the user selects a legal move for the bottom-side color in `/repertoire`, the board and the shared
`PositionDescription` immediately show the resulting position as a staged preview. The preview remains a visual
projection of the canonical parent position: it does not advance `session.currentPosition`, add to Local SAN history,
or call the preferred-move API. Explicit Add/Save continues to persist the move for the parent position, and Play saved
move remains the operation that commits a move into the local session.

## Scope

- **Included:** Derive the visual position from the existing `session.stagedMove.position` produced by
  `selectPositionPickerMove`; use that derived FEN for the interactive board and the shared `PositionDescription`
  while retaining the parent FEN for `usePreferredMoveWorkflow`, analysis, Local SAN history, mutation requests, and
  canonical session state. Preserve one-move staging, predictable replacement/cancellation, promotion behavior, and
  opponent immediate advancement.
- **Expected areas:**
  `frontend/src/features/repertoire-builder/{RepertoireBuilderWorkspace.tsx,RepertoireBuilderWorkspace.test.tsx,RepertoireBuilderWorkspace.stories.tsx,PreferredMoveWorkflow.stories.tsx,positionPickerSession.test.ts}`;
  `tests/e2e/repertoire-builder-storybook.spec.ts`. Consume the closed
  `frontend/src/features/board-adapter/PositionDescription.tsx` and
  `frontend/src/features/repertoire-builder/RepertoireSessionPanel.tsx` boundaries without inlining or absorbing
  them. `positionPickerSession.ts`, `repertoireWorkflowModel.ts`, and `preferredMoveWorkflowState.ts` should remain
  unchanged unless a focused proof identifies a minimal necessary correction to preserve the approved behavior.
- **Excluded:** Automatic preferred-move persistence or any PUT on staging; durable local-session restoration or
  storage; new API, schema, backend, dependency, or public component-contract work; adding staged moves to SAN
  history before Play saved move; move trees, multi-ply staged chains, Undo/Reset, broader board/session redesign,
  opponent-move changes, preferred-move Add/Save contract changes, visual restyling, speculative README edits,
  unrelated active or historical Plans, unrelated worktree changes, commits, and pushes.

## Stages

1. **complete** - Implement the parent-anchored visual preview from the closed upstream baseline.
   - Confirm that `repertoire-position-description` is completed and closed, then confirm that
     `repertoire-session-panel` is completed and closed. Read the resulting `RepertoireBuilderWorkspace` baseline only
     after those sequential closures; never execute this Plan in parallel with either upstream Plan.
   - Confirm that `PositionPickerMoveRecord.position` already contains the deterministic post-move `GamePosition`
     created by `positionAfterMove` in `positionPickerSession.ts`. Reuse that chess.js-derived FEN; do not add a second
     rules engine or a speculative preview store. Do not mutate `session.currentPosition` for rendering.
   - In `RepertoireBuilderWorkspace`, derive a visual `displayedPosition` as `session.stagedMove?.position` when a
     staged move exists, otherwise `session.currentPosition`. Build the visual position model from
     `displayedPosition.fen` and `session.orientation`, and pass `displayedPosition.fen` to the interactive board's
     `branchSnapshot.currentFen`. Keep `localMoves`, `session.currentPosition.fen`, `session.currentPly`, and
     `sessionSanHistory(session)` parent/session based.
   - Keep `usePreferredMoveWorkflow` and its `workflow.positionModel` keyed to `session.currentPosition.fen`; the
     preferred context, saved-move metadata, and `runMutation` request must continue to use the parent FEN. Keep the
     analysis state and candidate path parent-anchored so a candidate replaces the one staged parent move rather than
     creating a child branch.
   - Preserve the extracted `PositionDescription` and `RepertoireSessionPanel` component boundaries. Do not move
     preview logic into either shared presentation component, and do not create a new public prop merely to render the
     preview.
   - Ensure every staged selection path, including promotion after `usePromotionController`, remains based on the
     canonical parent and `selectPositionPickerMove`. A second interaction must never append to the preview: it may
     replace the staged parent move through the existing one-move selection path, or be rejected by the existing legal
     interaction guard. Stop rather than expanding the model to a move tree if the board package would require a new
     shared/public interaction contract to make this safe.
   - Preserve the existing board/status and session-panel ownership. The canonical `session-origin`/current-ply and
     Local SAN history remain parent-based so the preview is not presented as committed local navigation.
   - Add or adjust the focused session-model assertion only as needed to prove that a staged result already carries the
     post-move FEN while retaining the parent current position; do not add a preview field when the existing move record
     is sufficient.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`
     with Bash tool timeout `120000 ms`.
   - **Breakpoint:** stop and escalate if the closed upstream boundaries cannot be preserved, if preview rendering
     requires changing the preferred-move/public API contract, if parent anchoring cannot be maintained, or if safe
     one-move interaction requires a new board abstraction or product decision.

2. **complete** - Regression-guard preview lifecycle, explicit persistence, and existing repertoire workflows.
   - Update `RepertoireBuilderWorkspace.test.tsx` to prove a legal bottom-side board/candidate move immediately shows
     the resulting FEN and shared `data-position-*` description while `session.currentPosition`, current ply, Local SAN
     history, and parent context remain unchanged.
   - Prove staging does not call `preferredMoveClient.put`; explicit Add and Edit/Save still send the parent FEN and
     staged move UCI. On successful Add/Save, use the narrowest behavior-preserving rule: the existing staged state is
     cleared, the visual preview restores to the parent, and the board does not enter local history. On mutation
     failure, retain the staged preview, draft, and selected date as existing workflow behavior requires.
   - Prove replacing a staged move updates the preview from the parent rather than chaining from the preview. Prove
     Flip, Previous/Next, Reset/load, edit cancellation, and promotion cancellation clear the preview consistently;
     promotion selection shows the promoted resulting position without committing it to history.
   - Prove Play saved move remains the only saved-preferred-move operation that appends the move to local history and
     advances the canonical session. Retain opponent immediate local advancement, navigation/truncation, loading,
     error, date, Remove, accessibility, and no-Undo/Reset coverage.
   - Update only the relevant interaction assertions in `RepertoireBuilderWorkspace.stories.tsx`,
     `PreferredMoveWorkflow.stories.tsx`, and `tests/e2e/repertoire-builder-storybook.spec.ts`. Cover the approved
     preview at wide and constrained widths, the synchronized shared description, no horizontal overflow, no PUT at
     staging, explicit Add/Save parent identity, Flip cancellation, replacement, promotion, and no accidental second
     ply. Preserve the single `RepertoireSessionPanel` boundary and the shared `PositionDescription` ownership from
     the closed upstream baseline.
   - **Focused proof:** from `frontend`, rerun
     `npm exec vitest run src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`
     with Bash tool timeout `120000 ms`.
   - **Story proof:** from `frontend`, run
     `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`
     with Bash tool timeout `180000 ms`; if the Workspace-based selectors in
     `PreferredMoveWorkflow.stories.tsx` change, run the same command targeting that story file with Bash tool timeout
     `180000 ms`.
   - **Bounded browser proof:** with the existing Storybook server available, from the repository root run
     `npm exec playwright test tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`
     with Bash tool timeout `180000 ms`.
   - **Breakpoint:** stop if Add/Save mutates the preview's child FEN, a failed mutation loses pending state, a second
     interaction chains a second ply, opponent behavior changes, or any upstream extracted component, preferred-move
     contract, accessibility behavior, or responsive layout must be redesigned.

3. **complete** - Fresh independent Quality validation of the observable preview behavior.
   - A fresh Quality session validates only the approved repertoire source, focused tests/stories, E2E surface, and the
     closed upstream component boundaries read-only. It must not edit, format, repair, commit, or absorb unrelated
     failures.
   - At wide and constrained widths, exercise a legal bottom-side drag and candidate move and confirm that the board
     and shared position description show the same post-move FEN, while Local SAN history, canonical parent current
     position/current ply, analysis identity, and preferred context remain parent-based.
   - Confirm no preferred-move PUT occurs on staging; explicit Add/Save uses the parent FEN; successful Add/Save
     restores the parent preview without adding history; failed mutation retains preview; Play saved move advances and
     records exactly one local move; opponent moves remain immediate and local-only.
   - Confirm replacement, Flip cancellation, navigation cancellation, promotion selection/cancellation, loading,
     errors, accessibility, no accidental second-ply staging, no horizontal overflow, the unchanged
     `PositionDescription` boundary, and the unchanged `RepertoireSessionPanel` boundary.
   - Re-run the bounded browser proof command from Stage 2 with runner timeout `30000 ms` and Bash tool timeout
     `180000 ms`.
   - **Breakpoint:** return to the coordinator for any visual or accessibility result that calls the approved preview,
     parent anchoring, explicit persistence, one-move interaction, or either closed upstream boundary into question;
     report unrelated baseline failures without repairing them here.

4. **complete (user-waived reruns)** - Run repository closeout and route only necessary ownership documentation.
   - Determine whether the final implementation changes documented component ownership or structure. The expected
     change is consumer logic inside the existing Workspace and requires no README edit; if a real ownership change
     makes `frontend/src/features/repertoire-builder/README.md` stale, route that documentation-only update to
     `readme-updater` after implementation and Quality validation. The case-worker must not edit it speculatively.
   - From the repository root, run `.venv/Scripts/python.exe scripts/check.py` without `--fix` with Bash tool timeout
     `180000 ms`. The closeout runner has no additional supported CLI timeout flag; the Bash timeout remains finite.
   - From `frontend`, run `npm run build` with Bash tool timeout `180000 ms` and `npm run lint` with Bash tool timeout
     `180000 ms` when they are not already covered by the closeout result. Preserve truthful progress and proof; do
     not move this Plan to `docs/plans/done/` except through coordinator closeout.
   - **Breakpoint:** report the exact failing command and stop for any unrelated baseline failure, any failed repair
     loop, any documentation-ownership ambiguity, or any request to commit or push.

## Progress and decisions

- **Stage 1:** complete - both upstream Plans are closed; `displayedPosition` now drives only the board and shared
  description while canonical session/history/workflow identity remains parent-based. Focused Vitest proof passed:
  3 files, 29 tests. Final scope audit clean; breakpoint: preserve both extracted boundaries and parent workflow
  anchoring.
- **Stage 2:** complete - focused Vitest passed 3 files/32 tests; Workspace Storybook passed 21 tests; bounded
  Storybook browser proof passed 6 tests at wide and constrained widths. Existing Storybook server was available, so no
  setup or cleanup was required. Preview lifecycle, parent-anchored persistence, cancellation, promotion, local play,
  opponent behavior, accessibility, and overflow assertions passed; breakpoint: preserve explicit persistence, preview
  lifecycle, and one-move semantics.
- **Stage 3:** complete - fresh independent Quality validation passed. Focused Vitest passed 3 files/32 tests,
  Workspace Storybook passed 21 tests, and bounded Playwright proof passed 6 tests. Wide and constrained browser
  inspection confirmed synchronized preview rendering, parent-anchored session/history, and no horizontal overflow;
  both closed upstream component boundaries remained unchanged.
- **Stage 4:** complete by explicit user waiver - no ownership or structural change made the repertoire-builder README
  stale, so no README update was needed. After the Stage 3 PASS, the user directed that no further retests be run and
  approved closing the Plan using the existing passing proof. Repository `scripts/check.py`, build, and lint reruns were
  therefore not run at closeout; no `--fix` was used.
- **Decision:** this is a separate Plan and must execute only after `repertoire-position-description` is completed and
  closed, followed sequentially by `repertoire-session-panel` being completed and closed; no parallel execution.
- **Decision:** the existing `PositionPickerMoveRecord.position` is the deterministic preview source. Do not add a
  second preview state or rules engine unless the closed baseline proves that source insufficient.
- **Decision:** visual preview and canonical workflow are deliberately split: board/`PositionDescription` use the
  staged child FEN; preferred context, Add/Save request identity, analysis, SAN history, and canonical session remain
  on the parent.
- **Decision:** successful Add/Save clears the staged preview and restores the parent without local advancement;
  Play saved move remains the explicit local-session commit. A mutation failure retains the existing pending draft and
  preview.
- **Decision:** staged replacement is always evaluated from the canonical parent and never appended to the preview;
  move-tree or multi-ply staging is not a fallback.

## Proof

- Focused model and Workspace regression:
  `npm exec vitest run src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`
  (`frontend`; Bash tool timeout `120000 ms`).
- Workspace Storybook interaction proof:
  `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`
  (`frontend`; Bash tool timeout `180000 ms`). If the preferred-workflow story is changed, run the same bounded
  command targeting `src/features/repertoire-builder/PreferredMoveWorkflow.stories.tsx`.
- Bounded browser proof against the existing Storybook server:
  `npm exec playwright test tests/e2e/repertoire-builder-storybook.spec.ts --timeout=30000 --workers=1`
  (repository root; Bash tool timeout `180000 ms`), including wide and constrained preview, persistence, cancellation,
  promotion, overflow, and accessibility checks.
- Fresh independent Quality validation: read-only browser and focused-source review of the approved paths; no repair or
  formatting.
- Repository closeout: not rerun after independent validation, by explicit user direction and closeout approval.
- Build and lint: not rerun after independent validation, by explicit user direction and closeout approval.

## Escalation boundaries

- Do not execute until both upstream Plans are completed, closed, and their final Workspace, shared
  `PositionDescription`, `RepertoireSessionPanel`, test, story, and CSS baselines are available. Never execute this
  Plan in parallel with either upstream Plan.
- Do not inline, absorb, restyle, or change the public contracts of `PositionDescription` or `RepertoireSessionPanel`.
- Do not change `PreferredMovePanel`, `preferredMoveApi`, backend preferred-move routes, API schemas, storage, or
  effective-date semantics to implement a visual preview.
- Stop for any need for automatic persistence, durable session storage, a new API/data/dependency contract, multiple
  staged plies, a move tree, Undo/Reset, changed opponent semantics, or changed Add/Save/Play product semantics.
- Stop if an accessible or safe one-move preview requires a new shared/public board prop or component abstraction; do
  not silently widen the board contract.
- Treat successful Add/Save preview clearing/restoration as the narrow behavior-preserving rule. Escalate if the closed
  baseline requires the preview to remain visible or to advance locally after mutation.
- Preserve unrelated worktree changes, active/historical Plans, and generated artifacts; never commit or push.

## Visible result

> In `/repertoire`, a legal bottom-side move immediately appears on the board and shared position description as a
> staged preview, while history and persistence remain unchanged until the user explicitly saves or plays it.
