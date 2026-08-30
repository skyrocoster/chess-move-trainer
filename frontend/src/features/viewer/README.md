# viewer

Main chess viewer frontend feature.

## Scope

Displays the chess board, loads and traverses games, and shows engine analysis. Each displayed
analysis candidate (including Best) is an accessible pointer/keyboard control; activating one
applies only the candidate's first UCI move through the existing branch/promotion path (no PV
playback). In the former Game Context location it composes the shared controlled Move History
(retaining safe source attribution and truthful Ply) and the shared Position Reach Frequency
keyed to the current analysis FEN and the loaded subject colour; Flip does not alter that
scope.
Board orientation follows the loaded game's `subject_color` (White at the bottom when no
game is loaded) and can be flipped via the toolbar without changing position, navigation,
or data.

## Components

| Component         | Responsibility                                                                                                          |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `BoardControl`    | Renders the board toolbar: Previous/Next navigation and Flip                                                            |
| `GameLoader`      | Loads games from the API, manages loading state                                                                         |
| `BoardEvalStage`  | Stages the board beside the eval rail; passes orientation to `EvalBar`                                                  |
| `ViewerWorkspace` | Top-level orchestrator — composes all viewer sub-components; owns orientation state (`subject_color` base, Flip toggle) |

`EvalBar`, `AnalysisPanel`, `MoveHistory`, and `PositionReachFrequency` are not owned by
viewer: `EvalBar` and `AnalysisPanel` are presentation-only components imported from the
`analysis` feature; `MoveHistory` and `PositionReachFrequency` are shared feature dependencies
composed in the former Game Context location, with the history retaining source/Ply. Viewer
derives all display values — evaluation-to-display in `evalBarDisplay.ts` and the analysis
panel display in `analysisFormatting.ts` — and wires them into the components along with the
callback intents (see `ViewerWorkspace`).

## Data layer

| File                      | Role                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `positionApi.ts`          | API calls for FEN positions                                                                |
| `positionContextApi.ts`   | Typed API client for position recurrence counts per FEN                                    |
| `analysisApi.ts`          | API calls for Stockfish evaluations                                                        |
| `analysisFormatting.ts`   | Derives the analysis panel display and callback intents for the `analysis` `AnalysisPanel` |
| `gameModel.ts`            | Game state model and move traversal logic                                                  |
| `chessPrimitives.ts`      | Low-level chess.js helpers                                                                 |
| `analysisState.ts`        | React state management for analysis data                                                   |
| `positionContextState.ts` | React state hook for loading position recurrence per FEN                                   |
| `evalBarDisplay.ts`       | Derives evaluation-to-display values consumed by the `analysis` `EvalBar`                  |

## Stories and tests

Each component has a `.stories.tsx` and `.test.tsx` file alongside it.
