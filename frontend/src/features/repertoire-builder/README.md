# repertoire-builder

Repertoire Builder frontend page with an in-memory position-picker session, a cohesive right-side session
panel, and a preferred-move workflow.

## Scope

Serves the `/repertoire` route: a responsive workspace with the Repertoire Builder heading, a chess
board, and a page-owned local session. The session starts from the standard starting position
(White at the bottom) or from a stored game UUID and Ply, retaining the complete stored prefix
through the selected Ply and initially placing the recorded subject color at the bottom. It
supports one legal local SAN line via board dragging and the displayed legal analysis candidates
(including Best line), promotion through the existing picker, local Previous/Next with truncation
of the later continuation on replacement, position-preserving Flip that cancels pending staging,
staged bottom-side ("my") moves, immediate opponent moves, and one visible staged/status sentence shown
through the single live session-status message.

The preferred-move workflow reads, adds, saves (replaces), plays locally, and removes (with
confirmation) the fixed owner's one move per game-derived position, using an optional UTC effective
date and typed errors; mutations are explicit only. The page session itself stays in memory: no
move tree or separate chess Undo/Reset UI.

## Component

| Component                    | Responsibility                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `RepertoireBuilderWorkspace` | Page/state/workflow orchestration — loader, board, callbacks, board notice                                  |
| `RepertoireSessionPanel`     | Right-side session composition — Local SAN history, single live session status, nested `PreferredMovePanel` |
| `positionPickerSession`      | In-memory session model — standard/stored origins, history, move staging                                    |
| `PreferredMovePanel`         | Nested preferred-move UI — private behavior/presentation; context/saveability, date, add/save/play/remove   |
| `preferredMoveApi`           | Typed `/api/preferred-move` client — GET/PUT/DELETE, failure codes                                          |
| `preferredMoveState`         | `usePreferredMoveState` read hook — preferred move, loading, error                                          |
| `preferredMoveWorkflowState` | `usePreferredMoveWorkflow` hook — draft, date, mutations, play, reset                                       |
| `repertoireWorkflowModel`    | Pure position model — saveability, saved move, draft state                                                  |

## API contract

Preferred-move data belongs to the fixed owner and persists server-side via `/api/preferred-move`
(see `backend/app/features/preferred_move/README.md`); the page session stays in memory.
`preferredMoveApi.ts` provides typed `GET` (read), `PUT` (add/replace), and `DELETE` (remove)
clients with an optional UTC `effective_at`, explicit-only mutations, and typed failure codes.
Saveability derives from position context: positions absent from the catalog are unsavable, while
positions with zero personal games remain savable.

## Route

`/repertoire` is lazy-loaded in `src/App.tsx` and linked from the shared AppShell navigation.

## Stories and tests

`RepertoireBuilderWorkspace.stories.tsx`, `RepertoireBuilderWorkspace.test.tsx`,
`PreferredMoveWorkflow.stories.tsx`, `positionPickerSession.test.ts`, `preferredMoveApi.test.ts`,
`preferredMoveState.test.ts`, and `repertoireWorkflowModel.test.ts` sit alongside the component. A
feature-specific browser proof, `tests/e2e/repertoire-builder-storybook.spec.ts`, runs against the
existing Storybook server selection in `tests/e2e/playwright.config.ts`.
