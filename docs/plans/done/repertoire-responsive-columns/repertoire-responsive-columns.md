# `/repertoire` responsive columns - Board, Session, and Engine reflow inside fixed bounds

> **Status:** done - Stages 1, 2, 3, and 4 are complete and coordinator-accepted

- **Read trigger:** Read before beginning this `/repertoire` implementation, before each sequential stage, and whenever context is handed off during the work.
- **Upstream:** The user-approved, signed-off composition in `experiments/mock-ups/rearranged-rep/round-03-responsive-columns/`; `DESIGN.md` is the repository-aware authority for behavior, ownership, contracts, and exclusions, while `src/App.tsx` and `src/styles.css` provide the visual composition and responsive fidelity anchors. The updated `DESIGN.md` records the settled component and named-container corrections.

## Outcome

The `/repertoire` workspace uses the real board, session facts, and engine analysis in a responsive three-lane composition. At wide stage widths the three lanes resize internally with two centered-pill separators; at medium widths the board owns a full row above a resizable Session/Engine row; at narrow widths the lanes stack without separators. The existing in-memory workflows, API contracts, accessibility semantics, and dual analysis meanings remain unchanged.

## Scope

- **Included:**
  - A feature-local `RepertoireResponsiveStage` taking `{ board, session, engine }: ReactNode` and owning stage measurement, mode selection, resizable groups, clamped defaults, minimums, reset, and private separator/layout helpers.
  - A standalone `RepertoireBoardLane` composing `BoardEvalStage`, `BoardControl`, and exactly one controlled `MoveHistory`.
  - A session-facts-only `RepertoireSessionPanel` retaining its name and story boundary while removing history props and rendering.
  - Local Session and Engine semantic wrappers, with `PositionDescription` in Session and the real `AnalysisPanel` in Engine.
  - Explicit named CSS container ownership, the wider bounded workspace, the `react-resizable-panels` workspace dependency move, and focused behavioral, Storybook, Playwright, and human visual proof.
- **Expected areas:** `frontend/src/features/repertoire-builder/RepertoireResponsiveStage*`, `RepertoireBoardLane*`, `RepertoireBuilderWorkspace*`, `RepertoireSessionPanel*`, `repertoireBuilderStoryRender.tsx`, `repertoireBuilderStoryAssertions.ts`, `repertoireBuilderStoryHelpers.ts`, `RepertoireBuilderWorkspace.test.tsx`, `RepertoireBuilderWorkspaceWorkflow.test.tsx`, affected repertoire stories, `frontend/src/features/viewer/BoardEvalStage*`, `frontend/src/features/board-adapter/PositionDescription.module.css` and its focused test/story, `package.json`, `frontend/package.json`, `package-lock.json`, and `tests/e2e/repertoire-builder-storybook.spec.ts`.
- **Excluded:** `frontend/src/App.tsx` route changes, AppShell redesign, Viewer layout redesign, backend/API/database/domain changes, persisted layouts or new preferences, new workflow/FEN/history/analysis state, mock-up content or review chrome in production, generic lane abstractions, custom splitter behavior, broad lint/format/type/build/aggregate/maintenance checks, and unrelated worktree or user-owned experiment changes. `DESIGN.md` is upstream evidence for this Plan and is not rewritten by implementation.

## Design fidelity

- **Authority:** `DESIGN.md` governs repository meaning, real-state mapping, accessibility, contracts, exclusions, and the settled component/container boundaries. The signed mock-up directory governs the visual composition, centered-pill treatment, and responsive hierarchy. Its fake content and review-sheet chrome are excluded.
- **Excluded artifact content:** fake board, corpus, and engine values; mock headings and explanatory copy; mode annotations and measured-width readouts; lineage/review cards; noncanonical stamps; and custom mock controls.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| `DESIGN.md` A3; mock `App.tsx:301-324` | Stage-width modes: `>=1040px` wide, `700-1039px` medium, `<700px` narrow; exact lane order and separator presence | Use a `ResizeObserver` owned by `RepertoireResponsiveStage` and data attributes/classes for DOM mode selection | Stage harness and browser checks exercise 699/700 and 1039/1040 stage boundaries; human review confirms the resulting compositions |
| `DESIGN.md` A3/A6; mock `App.tsx:78-92,210-253` | Board/Session/Engine minimums of 320/280/360px, valid clamped defaults, fixed outer stage edges, ephemeral layout, and reset | Translate pixel defaults and library layout calls to the installed `react-resizable-panels` API; do not add persistence | Focused splitter checks verify minimums, internal redistribution, fixed stage bounds, and reset restoration |
| `DESIGN.md` A5/A6; mock `styles.css:92-100` | Library separator hit targets, accessible names, keyboard/focus feedback, and a small centered pill that strengthens on interaction | Use CMT/Material tokens and omit the mock's `Idea 03` label; keep decoration `aria-hidden` | Playwright checks named separators, keyboard resizing, focus-visible behavior, coarse/fine target affordance, and no separators in narrow mode |
| `DESIGN.md` A4/A7; workspace state at `RepertoireBuilderWorkspace.tsx:88-186,246-349` | One workflow owner, one controlled history, one status live region, displayed-position evaluation on Board, parent-position analysis in Engine, and all move/promotion/Flip/reset semantics | Pass fully configured board content into `RepertoireBoardLane` and lane nodes into the stage; retain existing IDs and ARIA contracts where they do not duplicate content | Workspace/workflow tests and stories cover loading, history, promotion, staging, saved-move mutation states, status, and dual analysis |
| `DESIGN.md` A6/A9; AppShell `AppShell.module.css:6-7,119-124` | Named query ownership and a bounded workspace widened toward 1540px without document overflow or AppShell changes | Remove the obsolete anonymous repertoire container; name the stage and existing internally responsive owners; use semantic lane wrappers without making them CSS containers | Focused CSS/component checks find no anonymous repertoire query owner; browser and visual checks confirm the wider stage stays inside AppShell |

## Stages

1. **done - Container and dependency foundation**
   - Move the exact `react-resizable-panels` `4.12.3` production declaration from root `package.json` to `frontend/package.json`, update lockfile workspace metadata, and retain one resolved version.
   - Establish `repertoire-workspace-stage` on the future stage owner. Remove the obsolete `.repertoire` anonymous container and old grid query. Add the `position-description` owner and named queries, and scope `board-eval-stage` through a host that preserves the shared Viewer `grid-area: board` placement.
   - Keep `BoardEvalStage` behavior and props unchanged; any host wrapper is a containment/placement correction only. Retain existing `board-control`, `preferred-move-panel`, and `analysis-panel` names. Do not add containers to lanes, MoveHistory, PositionReachFrequency, or InteractiveBoardAdapter.
    - Retained proof from the repository root (Bash tool timeout: `120000` ms): `timeout 90s npm ls react-resizable-panels --workspace frontend --depth=0` — passed; frontend resolves `react-resizable-panels` `4.12.3`.
    - Retained proof from the repository root (Bash tool timeout: `120000` ms): `timeout 90s npm --workspace frontend run test -- --run src/features/viewer/BoardEvalStage.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/board-adapter/PositionDescription.test.tsx` — passed, 3 files / 24 tests.
    - Coordinator acceptance: the scope audit found the intended seven files only, limited lockfile churn, preserved Viewer grid placement, and no Stage 2/3 behavior. The current narrow layout remains an explicitly marked temporary Stage-1 scaffold pending Stage 3 replacement. Unrelated worktree changes and untracked experiments remain preserved.
   - **Breakpoint/escalation:** Stop if workspace dependency placement requires an additional experiment ownership decision, or if preserving Viewer grid placement requires a Viewer behavior/layout change rather than the approved technical host correction.

2. **done - Lane boundary extraction and workspace recomposition**
   - Add `RepertoireBoardLane` with explicit board/evaluation/orientation, BoardControl, and controlled MoveHistory inputs. Keep history data derived from `positionPickerHistory(session)` and keep staged owner previews out of history.
   - Narrow `RepertoireSessionPanelProps` to its session-facts inputs (`PreferredMovePanelProps`, optional position context, and `sessionStatus`); remove history props and rendering rather than adding slots or a compatibility mega-prop facade. Preserve its root test identity and one `InlineFeedback` status region.
   - Recompose `RepertoireBuilderWorkspace` so heading, loader, and origin remain above the stage; Board owns history; Session contains the session panel plus PositionDescription; Engine contains the real AnalysisPanel. Keep all existing state, callbacks, request clients, `viewKey`, and parent/displayed analysis meanings in the workspace.
   - Replace raw DOM-parent and raw CSS-grid assertions in `RepertoireBuilderWorkspace.test.tsx` and story helpers with semantic lane/component assertions. Update `RepertoireSessionPanel.stories.tsx` and add focused stories only for the new standalone boundaries; do not preserve assertions that require obsolete ancestry.
    - Retained proof from the repository root (Bash tool timeout: `150000` ms): `timeout 120s npm --workspace frontend run test -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx` — passed, 2 files / 39 tests, 11.92s.
    - Coordinator acceptance: exactly one controlled `MoveHistory` now belongs to `RepertoireBoardLane`; `RepertoireSessionPanel` is session-facts-only with one live status and `PreferredMovePanel`; `PositionDescription` is in Session and `AnalysisPanel` is in Engine; dual analysis, state, and callback ownership is retained.
    - No Stage 3 behavior exists yet; the temporary layout scaffold remains pending Stage 3. Existing stale `session-move-history` selectors in `tests/e2e/repertoire-builder-storybook.spec.ts` are an expected Stage-4 integration update, not a Stage-2 acceptance blocker.
    - Preferred-move files and E2E modifications already existed as unrelated user work before Stage 2 and remain preserved; they are not attributed to this stage.
    - **Breakpoint/escalation:** Stop if any consumer outside the approved repertoire files requires the removed history component API, or if composition would require a second history, status region, workflow hook, or API request.

3. **done - Responsive stage implementation and focused stage harness**
   - Implement `RepertoireResponsiveStage` with the real library `Group`, `Panel`, and `Separator` components. Use distinct wide and medium groups, fixed `inline-size: 100%`, `min-inline-size: 0`, and no storage/persistence.
   - Implement the settled modes and defaults: wide Board/Session/Engine with two separators; medium full-width Board row plus Session/Engine group; narrow Board → Session → Engine stack with no separator. Clamp defaults against available panel space and enforce 320/280/360px minimums where panels are resizable.
   - Keep `PillSeparator`, measurement, mode calculation, default-layout calculation, and reset control private to the stage. Give separators the approved accessible names and make the library hit target larger than the visual pill. Do not copy mock labels or readouts.
    - Use the named stage query for any medium Board-lane internal arrangement; lane wrappers remain semantic structural elements, not additional CSS query containers.
    - Add a focused stage test/harness that can hold the stage at exactly 699, 700, 1039, and 1040px and assert mode, separator count, lane order, minimums, and reset. Bash tool timeout: `120000` ms; command-level timeout: `timeout 90s npm --workspace frontend run test -- --run src/features/repertoire-builder/RepertoireResponsiveStage.test.tsx src/features/repertoire-builder/RepertoireBoardLane.test.tsx`.
    - Retained proof from the repository root (Bash tool timeout: `120000` ms): `timeout 90s npm --workspace frontend run test -- --run src/features/repertoire-builder/RepertoireResponsiveStage.test.tsx src/features/repertoire-builder/RepertoireBoardLane.test.tsx` — passed, 2 files/8 tests.
    - Retained proof from the repository root (Bash tool timeout: `150000` ms): `timeout 120s npm --workspace frontend run test -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx` — passed, 2 files/39 tests; this refreshed Stage-2 proof invalidated by integration.
    - Stage 1 proof remains retained.
    - Coordinator acceptance: the audit accepted exact boundaries, named separators, minimum sizes/default/reset, fixed stage bounds, the medium Board full row, narrow mode without separators, the `96.25rem` workspace bound, and no persistence or custom resizing.
    - Visual, Storybook, and E2E acceptance remain Stage 4; no visual acceptance is claimed yet.
   - **Breakpoint/escalation:** A passing DOM test does not authorize visual acceptance. Stop for coordinator/user review if the real library cannot provide keyboard/coarse-pointer resizing, or if the stage edges move during internal resizing; do not implement a custom splitter or viewport-only fallback.

4. **done - Focused integration, story, E2E, and visual acceptance**
   - Add a representative medium workspace story/viewport alongside the existing wide and constrained stories. Update repertoire story renderers, assertions, and helpers to scope history to Board, status/preferred content to Session, and position description to Session without first-match or obsolete-parent assumptions.
   - Extend focused Storybook and Playwright coverage for wide, medium, and narrow real states; empty/loading/error/unsavable/preferred mutation states; history and disclosure semantics; dual analysis; no overflow; axe; forced-colors/reduced-motion; separator names/focus/keyboard behavior; minimums; fixed bounds; reset; and the absence of separators below 700px. Keep checks container-width based rather than inferring layout from viewport alone.
   - Bash tool timeout: `150000` ms; command-level timeout: `timeout 120s npm --workspace frontend run test-storybook -- --run src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx src/features/repertoire-builder/RepertoireBuilderWorkspacePreferredMove.stories.tsx src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx src/features/repertoire-builder/RepertoireResponsiveStage.stories.tsx src/features/repertoire-builder/RepertoireBoardLane.stories.tsx`.
    - Bash tool timeout: `210000` ms; command-level timeout: `timeout 180s npm exec playwright -- test tests/e2e/repertoire-builder-storybook.spec.ts`.
    - At the required human visual breakpoint, inspect the actual `/repertoire` route at one wide, one medium, and one narrow stage, immediately around 699/700 and 1039/1040, including drag/reset, forced-colors, reduced-motion, AppShell bounds, and overflow. Behavioral/DOM checks alone cannot prove this fidelity.
    - Retained proof from the repository root (Bash tool timeout: `150000` ms): the focused Storybook command above passed, 5 files / 40 tests, 15.47s.
    - Retained proof from the repository root (Bash tool timeout: `210000` ms): the focused Playwright command above passed, 14/14, 49.5s. The initial connection-refused attempt was a bounded Storybook startup issue, not a behavioral failure.
    - Coordinator visual acceptance: actual-route evidence covered wide 1249px, medium 849px, narrow 549px, exact 699/700 and 1039/1040 boundaries, drag/reset, focus and keyboard resizing, forced-colors, reduced-motion, AppShell bounds, no overflow, and narrow separator removal. The signed hierarchy, medium full-width Board row, wider bounded composition, centered-pill treatment, and overflow behavior matched with no visual decision breakpoint.
    - **Breakpoint/escalation:** none; coordinator accepted the behavioral, browser, and visual result. No new edits were made during final Stage-4 execution; inherited Plan changes and the user's `frontend/vitest.config.ts` test-run fix remain preserved.

Every stage is sequential. A passing proof item remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependency, or environment; later stages rerun only missing or invalidated proof. Stages 1, 2, 3, and 4 are complete and coordinator-accepted.

## Progress and decisions

- **Stage 1:** done - proof: frontend dependency resolution passed; focused shared component proof passed (3 files / 24 tests); scope audit accepted; breakpoint: none.
- **Stage 2:** done - proof: focused workspace and workflow regression tests passed (2 files / 39 tests, 11.92s); scope and ownership accepted; breakpoint: none.
- **Stage 3:** done - proof: exact-boundary stage harness and splitter behavior tests passed (2 files / 8 tests); workspace/workflow proof refreshed after integration (2 files / 39 tests); scope audit accepted; breakpoint: none, with visual acceptance deferred to Stage 4.
- **Stage 4:** done - proof: focused Storybook passed (5 files / 40 tests, 15.47s); focused Playwright passed (14/14, 49.5s); actual-route wide, medium, narrow, boundary, interaction, accessibility-mode, AppShell-bound, overflow, and separator evidence was visually inspected and accepted; breakpoint: none.

## Proof

- Use only the finite, directly scoped commands listed in the stages, with the stated Bash tool and command-level timeouts.
- The focused proof must demonstrate the responsive composition, named separator controls, keyboard/focus behavior, panel minimums, fixed outer bounds, reset, no narrow separators, real workflow retention, no duplicate content/live regions, no document overflow, and the retained accessibility semantics.
- Do not use lint, formatting, broad type/build, source-size, aggregate, `scripts/check.py`, complete-suite, or Quality validation as Plan completion proof.

## Escalation boundaries

- A new product, visual, API, data, dependency, destructive, ownership, or acceptance decision not settled in `DESIGN.md` or this Plan.
- Any need to change AppShell, redesign Viewer, alter backend/API/domain behavior, persist layouts, add workflow state, or introduce generic lane abstractions.
- Any discovered external consumer of the removed `RepertoireSessionPanel` history props.
- Any inability of `react-resizable-panels` 4.12.3 to satisfy the settled separator, keyboard, pointer-target, minimum, reset, or fixed-edge requirements.
- Any visual breakpoint rejection of the signed wide/medium/narrow hierarchy or wider bounded workspace.

## Visible result

> `/repertoire` visibly reflows the real Board, Session, and Engine into the signed wide, medium, and narrow arrangements, with usable centered-pill resizing and reset while all existing trainer workflows still behave the same.
