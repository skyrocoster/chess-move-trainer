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

Analysis uses the generated clean `getAnalysis`/`requestAnalysis` operations (see
`features/analysis/analysisApi.ts`): observation follows the selected position, and engine requests
are deliberate Tool-quality requests rather than automatic side effects.

The preferred-move workflow reads the confirmed saved choice, stages the current owner move, saves a
first choice or replacement, lets the saved box play-and-stage its move, and removes the saved choice
(with confirmation) for the fixed owner and source position. The staged move remains local until Save;
the page session itself stays in memory: no move tree, calendar UI, or separate chess Undo/Reset UI.
`Change effective date` remains a visibly disabled action (accessible reason `Date changes are
temporarily unavailable`) that opens no calendar and sends no request.

## Component

| Component                    | Responsibility                                                                                                                                                             |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RepertoireBuilderWorkspace` | Page/state/workflow orchestration — loader, board, callbacks, board notice                                                                                                 |
| `RepertoireSessionPanel`     | Right-side session composition — shared controlled Move History for the combined stored prefix and local SAN line, single live session status, nested `PreferredMovePanel` |
| `positionPickerSession`      | In-memory session model — standard/stored origins, history, move staging                                                                                                   |
| `PreferredMovePanel`         | Nested preferred-move UI — current saved choice, staged move/proposal, position context, deferred date action, Save, and Remove                                            |
| `preferredMoveApi`           | Generated clean client over `getPreferredMoves`/`putPreferredMoves`/`deletePreferredMoves` — GET/PUT/DELETE, failure codes                                                  |
| `preferredMoveState`         | `usePreferredMoveState` read hook — preferred move, loading, error                                                                                                         |
| `preferredMoveWorkflowState` | `usePreferredMoveWorkflow` hook — saved/staged facts, mutations, deferred date capability, play-and-stage, reset                                                           |
| `repertoireWorkflowModel`    | Pure position model — legality, saveability, saved/staged facts, and canonical-UCI relationship                                                                           |

## API contract

Preferred-move data belongs to the fixed owner and persists server-side through the generated clean
plural operations (see `backend/app/features/preferred_move/README.md`); the page session stays in
memory. `preferredMoveApi.ts` wraps `getPreferredMoves` (read), `putPreferredMoves` (Save first
choice/replacement), and `deletePreferredMoves` (Remove) with typed failure codes. The saved
preference is the selected outgoing move for its parent position FEN. Reads use a UTC
`[today, tomorrow)` date window; Save and Remove use today as `effective_from` with no end date and
then refresh through a clean GET. Date editing stays request-free with no PATCH or substitute
mutation.

Saveability derives from legality: legal positions are savable, including novel parent FENs absent
from imported games. Position context (game corpus presence, etc.) is informational and is not a
saveability gate.

## Route

`/repertoire` is lazy-loaded in `src/App.tsx` and linked from the shared AppShell navigation.

## Stories and tests

`RepertoireBuilderWorkspace.stories.tsx`, `RepertoireBuilderWorkspace.test.tsx`,
`RepertoireBuilderWorkspacePreferredMove.stories.tsx`, `PreferredMovePanel.stories.tsx`,
`PreferredMoveWorkflow.stories.tsx`, `positionPickerSession.test.ts`, `preferredMoveApi.test.ts`,
`preferredMoveState.test.ts`, and `repertoireWorkflowModel.test.ts` sit alongside the component. A
feature-specific browser proof, `tests/e2e/repertoire-builder-storybook.spec.ts`, runs against the
existing Storybook server selection in `tests/e2e/playwright.config.ts`.
