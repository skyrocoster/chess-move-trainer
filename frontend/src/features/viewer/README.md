# viewer

Main chess viewer frontend feature.

## Scope

Displays the chess board, loads and traverses games, and shows engine analysis.

## Components

| Component         | Responsibility                                                             |
| ----------------- | -------------------------------------------------------------------------- |
| `BoardControl`    | Renders the chess board with move navigation                               |
| `GameLoader`      | Loads games from the API, manages loading state                            |
| `GameContext`     | Provides game state (moves, current position, headers) to child components |
| `ViewerWorkspace` | Top-level orchestrator — composes all viewer sub-components                |

`EvalBar` and `AnalysisPanel` are not owned by viewer: they are presentation-only components
imported from the `analysis` feature. Viewer derives all display values — evaluation-to-display
in `evalBarDisplay.ts` and the analysis panel display in `analysisFormatting.ts` — and wires
them into the components along with the callback intents (see `ViewerWorkspace`).

## Data layer

| File                    | Role                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| `positionApi.ts`        | API calls for FEN positions                                                                |
| `analysisApi.ts`        | API calls for Stockfish evaluations                                                        |
| `analysisFormatting.ts` | Derives the analysis panel display and callback intents for the `analysis` `AnalysisPanel` |
| `gameModel.ts`          | Game state model and move traversal logic                                                  |
| `chessPrimitives.ts`    | Low-level chess.js helpers                                                                 |
| `analysisState.ts`      | React state management for analysis data                                                   |
| `evalBarDisplay.ts`     | Derives evaluation-to-display values consumed by the `analysis` `EvalBar`                  |

## Stories and tests

Each component has a `.stories.tsx` and `.test.tsx` file alongside it.
