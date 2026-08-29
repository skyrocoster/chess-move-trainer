# Repertoire Position Description - One shared rich description appears below the board controls

> **Status:** Done - Stage 3 accepted by explicit user validation; no independent Quality PASS claimed

- **Read trigger:** Read before executing the approved `/repertoire` position-description relocation.
- **Upstream:** none; based on the approved case packet and bounded assessment

## Outcome

`/viewer` and `/repertoire` use one shared rich position-description component with the existing
`BoardAdapter` disclosure semantics. In `/repertoire`, the disclosure is no longer inside the board
container; it appears in a full-width row below the board and controls and stays synchronized with the
current FEN, orientation, and side to move.

## Scope

- **Included:** Extract the rich `PositionModel`/`VisiblePositionSummary` presentation from the board-adapter
  implementation into `frontend/src/features/board-adapter/PositionDescription.tsx` with its styles in
  `frontend/src/features/board-adapter/PositionDescription.module.css`; keep `BoardAdapter` using that
  component. Integrate the same component into `RepertoireBuilderWorkspace`, update its grid CSS, and update
  only the focused component tests and relevant Storybook checks.
- **Expected areas:**
  `frontend/src/features/board-adapter/{BoardAdapter.tsx,BoardAdapter.module.css,PositionDescription.tsx,PositionDescription.module.css,BoardAdapter.test.tsx,PositionDescription.test.tsx}`;
  `frontend/src/features/repertoire-builder/{RepertoireBuilderWorkspace.tsx,RepertoireBuilderWorkspace.module.css,RepertoireBuilderWorkspace.test.tsx,RepertoireBuilderWorkspace.stories.tsx}`
- **Excluded:** Eval bars; loaded-viewer `GameContext`; recurrence-only `PositionContext`; other repertoire
  text fragments; board/session redesign; API, backend, data, dependency, or public contract changes; unrelated
  worktree changes; commits and pushes.

README maintenance is not planned. If extraction makes an existing component-ownership README stale, stop and
escalate that documentation change rather than editing it as part of this outcome.

## Stages

1. **pending** - Extract and regression-guard the shared rich position-description component.
   - Create `board-adapter/PositionDescription.tsx` as the owner of the existing position model and visible
     summary, moving the minimum private symbols (`PositionModel`, `createPositionModel`, and
     `VisiblePositionSummary`) without changing their generated content or `data-position-*` markers.
   - Move only the summary-specific styles and container-query rules to `PositionDescription.module.css`.
     Preserve the adapter's accessible live description, `aria-describedby` association, hidden reordered body,
     disclosure label, default-collapsed behavior, and forced-colors/reduced-motion behavior.
   - Change `BoardAdapter.tsx` to consume the shared model/component while preserving its `BoardAdapterProps`
     contract and all existing board/unavailable behavior. Do not change `InteractiveBoardAdapter.tsx`.
   - Keep or add focused shared-boundary coverage in `PositionDescription.test.tsx`; run the existing
     `BoardAdapter.test.tsx` suite to prove the viewer/adapter behavior remains unchanged.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/board-adapter/BoardAdapter.test.tsx src/features/board-adapter/PositionDescription.test.tsx --testTimeout=10000 --hookTimeout=10000`
     with Bash tool timeout `120000 ms`.
   - **Breakpoint:** stop and escalate if preserving the existing BoardAdapter semantics requires a new public
     API, changes the rich presentation, or makes the component ownership/documentation ambiguous.

2. **pending** - Integrate the shared component into repertoire and place it in the approved full-width row.
   - Remove the repertoire-local `Disclosure` and `positionSummary`/`fen` presentation from
     `RepertoireBuilderWorkspace.tsx`; keep the interactive board, controls, session workflow, analysis, and
     `sideToMove` behavior unchanged.
   - Derive the shared position model from `session.currentPosition.fen` and `session.orientation`, and render
     `PositionDescription` in a dedicated `positionDescription` grid area after the board/control rows. The
     constrained layout must also place that area below the board and controls, not beside the board.
   - Preserve the shared component's BoardAdapter default-collapsed disclosure behavior. Update only repertoire
     assertions and stories that depended on the old always-open summary or `current-fen` test node; assert the
     shared `data-position-*` presentation and current-position updates instead.
   - Add focused assertions that the description is outside the repertoire board container, appears in the
     full-width row, updates after a move and Flip, and does not alter existing preferred-move, analysis, loading,
     navigation, promotion, or accessibility behavior.
   - Update `RepertoireBuilderWorkspace.module.css` grid areas in both wide and constrained arrangements; do
     not change board/session control styling beyond the new row.
   - **Focused proof:** from `frontend`, run
     `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000`
     with Bash tool timeout `120000 ms`.
   - **Story proof:** from `frontend`, run
     `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000`
     with Bash tool timeout `180000 ms`.
   - **Breakpoint:** stop and escalate if the approved full-width placement requires redesigning the board,
     controls, session panel, or analysis area, or if a current workflow contract must change.

3. **accepted by explicit user validation; no independent Quality PASS** - Closeout was authorized after the
   user confirmed Plan validation and directed closeout without further tests. The latest Luna proof before
   closeout had the complete `scripts/check.py --full` passing, full E2E `73/73` passing, focused affected Axe
   E2E `33/33` passing, no Storybook coverage gaps, and the required Fast Refresh warning resolved. Prior Quality
   validation attempts were cancelled because they launched unbounded background server/dev commands; they are
   not proof.

## Progress and decisions

- **Stage 1:** complete - shared model and rich summary are owned by `frontend/src/features/board-adapter/PositionDescription.tsx`; BoardAdapter regression coverage and focused shared-boundary coverage pass; breakpoint cleared: BoardAdapter behavior preserved.
- **Stage 2:** complete - shared `PositionDescription` is rendered in a dedicated full-width row below the board/control rows and synchronizes from the current FEN and orientation; repertoire workflow and accessibility coverage remain green; breakpoint cleared: approved placement and workflow boundaries preserved.
- **Stage 3:** accepted by explicit user validation - the user confirmed Plan validation and directed closeout
  without further tests. This is not an independent Quality PASS; prior Quality attempts were cancelled because
  they launched unbounded background server/dev commands.

## Proof

- Shared extraction regression: `npm exec vitest run src/features/board-adapter/BoardAdapter.test.tsx src/features/board-adapter/PositionDescription.test.tsx --testTimeout=10000 --hookTimeout=10000` (`frontend`; Bash tool timeout `120000 ms`; passed: 2 files, 12 tests).
- Repertoire regression: `npm exec vitest run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --testTimeout=10000 --hookTimeout=10000` (`frontend`; Bash tool timeout `120000 ms`; passed: 1 file, 14 tests).
- Relevant Storybook interaction checks: `npm run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx --testTimeout=10000 --hookTimeout=10000` (`frontend`; Bash tool timeout `180000 ms`; passed: 1 file, 21 tests).
- Latest Luna validation before closeout: complete `scripts/check.py --full` passed; full E2E `73/73` passed;
  focused affected Axe E2E `33/33` passed; no Storybook coverage gaps; and the required Fast Refresh warning
  was resolved.
- User acceptance: the user confirmed Plan validation and directed closeout without further tests.
- Quality history: prior Quality validation attempts were cancelled because they launched unbounded background
  server/dev commands; they are not proof, and this record makes no claim of independent Quality PASS.

## Escalation boundaries

- Do not substitute `GameContext` or `PositionContext`, add an eval bar, or broaden the text-componentization
  request.
- Do not change the public contracts of `BoardAdapter`, `PositionDescription`, or any API/client to solve an
  implementation inconvenience.
- Stop for any new product, visual, ownership, dependency, data, destructive, acceptance, or documentation
  decision, including a request to change the approved rich disclosure semantics or full-width placement.
- Preserve unrelated user changes and historical records; never commit or push.

## Visible result

> The same rich, collapsible position description appears in `/viewer` and `/repertoire`, with repertoire showing it in a full-width row below the board controls rather than inside the board area.
