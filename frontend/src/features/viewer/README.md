# viewer

Main chess viewer frontend feature.

## Scope

Displays the chess board, loads and traverses games, and shows engine analysis.

## Components

| Component | Responsibility |
|-----------|---------------|
| `BoardControl` | Renders the chess board with move navigation |
| `GameLoader` | Loads games from the API, manages loading state |
| `GameContext` | Provides game state (moves, current position, headers) to child components |
| `AnalysisPanel` | Displays engine analysis lines and scores |
| `EvalBar` | Visual evaluation bar alongside the board |
| `ViewerWorkspace` | Top-level orchestrator — composes all viewer sub-components |

## Data layer

| File | Role |
|------|------|
| `positionApi.ts` | API calls for FEN positions |
| `analysisApi.ts` | API calls for Stockfish evaluations |
| `analysisFormatting.ts` | Formats analysis data for display |
| `gameModel.ts` | Game state model and move traversal logic |
| `chessPrimitives.ts` | Low-level chess.js helpers |
| `analysisState.ts` | React state management for analysis data |

## Stories and tests

Each component has a `.stories.tsx` and `.test.tsx` file alongside it.
