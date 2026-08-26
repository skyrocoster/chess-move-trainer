# design-system

Shared UI components and design tokens.

## Scope

Material Design-based component library used across the frontend.

## Components

| Component    | Purpose                                                        |
| ------------ | -------------------------------------------------------------- |
| `Button`     | Styled button with variants                                    |
| `Disclosure` | Expandable/collapsible content section                         |
| `feedback/`  | Feedback display components: `Inline`, `Panel`, `Page`, `Core` |

## Visual specimens

| File                  | Purpose                                                |
| --------------------- | ------------------------------------------------------ |
| `TokenOverview`       | Displays all design tokens                             |
| `TypescaleSpecimen`   | Displays the type scale                                |
| `FoundationSpecimen`  | Displays foundation styles                             |
| `AccessibilityReview` | Automated accessibility checks against components      |
| `CombinedComposition` | Composed specimen showing multiple components together |

## Tokens

CSS custom properties defined in `frontend/src/styles/`:

- `cmt-tokens.css` — color, spacing, and sizing tokens
- `cmt-typescale.css` — typography scale

## Theme

Material Design theme export and provenance metadata live in `frontend/src/styles/material/`.
