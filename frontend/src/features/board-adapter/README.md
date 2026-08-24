# board-adapter

Chess board adapter frontend feature.

## Scope

Wraps `react-chessboard` with application-specific modes and the promotion-piece picker.

## Components

| Component | Mode |
|-----------|------|
| `BoardAdapter` | Read-only board display (no user moves) |
| `InteractiveBoardAdapter` | Interactive board where the user can make moves |
| `PromotionPicker` | Modal for selecting promotion piece (queen, rook, bishop, knight) |
| `PromotionPickerDemo` | Standalone demo/preview of the promotion picker |

## Pattern

The adapter pattern exists to decouple the rest of the app from `react-chessboard`'s API. Components above this layer interact with `BoardAdapter` or `InteractiveBoardAdapter`, never directly with the underlying library.
