# design-system

Shared UI components and design tokens.

## Scope

Material Design-based component library used across the frontend.

## Components

| Component      | Purpose                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| `Button`       | Styled button with variants                                                                          |
| `CalendarDate` | Controlled UTC date picker (Base UI Popover + react-day-picker); null allowed, future dates disabled |
| `Disclosure`   | Expandable/collapsible content section                                                               |
| `feedback/`    | Feedback display components: `Inline`, `Panel`, `Page`, `Core`                                       |
| `line-library/`  | Tree-based opening line picker: `LineLibrary`, `LineLibraryFilters`, `LineLibraryTree`               |

## Storybook support components

| File                               | Purpose                                                |
| ---------------------------------- | ------------------------------------------------------ |
| `StorySpecimenTokenOverview`       | Displays all design tokens                             |
| `StorySpecimenTypescale`           | Displays the type scale                                |
| `StorySpecimenFoundation`          | Displays foundation styles                             |
| `StorySpecimenAccessibilityReview` | Automated accessibility checks against components      |
| `StorySpecimenCombinedComposition` | Composed specimen showing multiple components together |

`StorySpecimen*` identifies Storybook-only visual/reference surfaces for production-ready
components or tokens. `StoryHarness*` identifies Storybook-only interactive wiring around
production-ready components. These support components must not be imported by production
application code. Storybook is for production-ready components/tokens; prototypes and pending
designs belong under `experiments/`.

## Tokens

CSS custom properties defined in `frontend/src/styles/`:

- `cmt-tokens.css` — color, spacing, and sizing tokens
- `cmt-typescale.css` — typography scale

## Theme

Material Design theme export and provenance metadata live in `frontend/src/styles/material/`.
