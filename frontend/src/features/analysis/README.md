# analysis

Chess-analysis frontend capability folder.

## Scope

Presentation-only, controlled components for displaying engine analysis. Analysis logic and
data derivation live in the `viewer` feature, not here.

## Components

| Component       | Responsibility                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------- |
| `EvalBar`       | Visual evaluation bar; controlled via `orientation`, `state`, `value`, and `accessibleValue` props |
| `AnalysisPanel` | Controlled panel for engine analysis lines, status, messages, and action buttons                   |

`AnalysisPanel` is a controlled presentation component. Its presentation contracts
(`AnalysisPanelLine` and `AnalysisPanelDisplay`) describe the display state and callback intents
it renders, but it performs no formatting, data derivation, state management, or API calls.
When an `onCandidateMove` callback is provided, every displayed candidate line (including Best)
renders as an accessible pointer/keyboard control; activation signals only that candidate's first
UCI move. Viewer owns those responsibilities.

## Consumers

`viewer` imports `EvalBar` and `AnalysisPanel` and wires in the display values derived by
`viewer/evalBarDisplay.ts` and `viewer/analysisFormatting.ts` respectively. Nothing in this
folder performs evaluation-to-display or analysis-panel derivation, state management, or API
calls.

## Stories and tests

Each component has a `.stories.tsx` and `.test.tsx` file alongside it.
