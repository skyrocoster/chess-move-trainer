# board-adapter

Chess board adapter frontend feature.

## Scope

Wraps `react-chessboard` with application-specific modes and the promotion-piece picker.

## Components

| Component                 | Mode                                                              |
| ------------------------- | ----------------------------------------------------------------- |
| `BoardAdapter`            | Read-only board display (no user moves)                           |
| `InteractiveBoardAdapter` | Interactive board where the user can make moves                   |
| `PromotionPicker`         | Modal for selecting promotion piece (queen, rook, bishop, knight) |

## Storybook support components

| Component                     | Purpose                                                       |
| ----------------------------- | ------------------------------------------------------------- |
| `StoryHarnessPromotionPicker` | Storybook-only interactive wiring around the promotion picker |

`StoryHarness*` identifies Storybook-only interactive wiring around production-ready components.
`StorySpecimen*` identifies Storybook-only visual/reference surfaces for production-ready
components or tokens. These support components must not be imported by production application
code. Storybook is for production-ready components/tokens; prototypes and pending designs
belong under `experiments/`.

## Pattern

The adapter pattern exists to decouple the rest of the app from `react-chessboard`'s API. Components above this layer interact with `BoardAdapter` or `InteractiveBoardAdapter`, never directly with the underlying library.
