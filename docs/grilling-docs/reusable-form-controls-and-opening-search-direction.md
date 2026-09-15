# Reusable form controls and opening-search direction

Date: 2026-09-14

Status: Complete and confirmed on 2026-09-15.

## Goal

Turn the visual language of `experiments/mock-ups/opening-search-combobox/index.html` into reusable form-control primitives before adding opening-specific presentation and behavior. The opening picker must be a composition of those primitives, not the source of a one-off component library.

## Current-state facts considered

- The frontend already pins `@base-ui/react` at version 1.7.0.
- `frontend/src/features/design-system/Button.tsx` already wraps the Base UI Button and should remain the standard button foundation.
- There is no shared Field/FormField component and no current use of Base UI Field.
- Current production field patterns are inconsistent:
  - `frontend/src/features/game/GameLoader.tsx` uses a wrapping label and a local inline validation alert.
  - `frontend/src/features/trainer-practice/TrainerPracticePanel.tsx` uses separate labels with raw inputs and selects, plus mostly form-level errors.
  - `frontend/src/features/design-system/line-library/LineLibraryFilters.tsx` uses Base UI Input, Select, and Checkbox with local field markup and styling.
- Eight controls are suitable for a later shared-Field migration: four in Trainer Practice, one in Game Loader, and three in Line Library Filters.
- The tri-state checkbox in `LineLibraryTree.tsx` is part of a composite tree widget and is not a normal form field migration candidate.
- `LineLibrary` overlaps with opening browsing but is not currently rendered by a production route. It is not an existing production opening-picker replacement target.
- The current opening-catalogue response mixes stable reference fields (`key`, ECO, and name) with counts derived from the active game database (`route_count`, `games_reached`, and `games_deepest`).
- The frontend currently has no persistent browser-data cache. Opening queries use only in-memory TanStack Query caching, while the backend invalidates its process-local cache when the database files change.
- The current opening API already provides stable key, ECO, name, and `route_count`. `route_count` is the number of stored move-sequence routes published under that ECO/name label; it is the existing value closest to the mock-up's “N lines.”
- No production opening or route field currently records White/Black repertoire ownership.
- Opening routes store UCI moves, but no opening API currently exposes their move sequences or a SAN preview. Producing the mock-up's preview therefore requires a new catalogue field or endpoint and server-side move replay/conversion.
- These availability facts do not authorize a new chain, repertoire-line, or preferred-move model. The mock-up's opening metadata remains presentation direction until later integration assessment.

## Approved primitive direction

### Shared field foundation

1. Introduce a shared Field composition backed by Base UI Field.
2. Field owns the consistent presentation and association of:
   - label;
   - description or help text;
   - required and disabled state;
   - invalid state; and
   - validation error text.
3. Controls remain independent from Field so the same Field can wrap TextInput, Select, Combobox, Autocomplete, RadioGroup, and other suitable controls.
4. After the Field design is approved in Storybook, migrate all eight suitable existing controls together rather than creating a fourth field pattern or waiting for incidental feature work.
5. Do not force the Line Library tree-selection checkbox into Field.
6. Field has a presentation-only validation contract: it displays externally supplied invalid state and error text but does not run validation or decide when errors become visible.
7. Each form or feature retains responsibility for validation timing, such as while typing, after blur, or after submission. This keeps Field reusable without introducing a form-state framework.

### TextInput

1. The search-field appearance in the HTML mock-up becomes the default TextInput visual design.
2. TextInput supports optional leading and trailing content slots.
3. The primitive owns the field frame, spacing, focus, disabled, read-only, and invalid presentation.
4. Consumers supply feature-specific content. In the opening picker, this includes the search icon, selected ECO badge, and clear action.
5. The control is fluid across viewports. It fills the available container by default, uses an accessible minimum height rather than a rigid fixed height, and allows the parent layout to apply a maximum width when needed.
6. Do not introduce desktop/mobile component variants or arbitrary fixed density sizes without a demonstrated need.
7. The initial TextInput treatment covers single-line text-like values: text, search, email, URL, telephone, and password.
8. Number and date inputs require separate Storybook decisions because of their specialized browser controls and interaction. Multiline text is a separate control rather than a TextInput mode.

### Select, Combobox, and Autocomplete

1. Select and Combobox remain separate accessible components rather than one universal Dropdown component.
2. Autocomplete is also separate from Combobox:
   - Combobox restricts the committed value to a listed option.
   - Autocomplete accepts free-form text and optionally suggests completions.
3. The point of use chooses the appropriate component. Do not add an `allowCustomValue` flag that changes the meaning and type of a Combobox value.
4. Select, Combobox, and Autocomplete share one dropdown visual language: popup surface, list spacing, option states, selection treatment, empty presentation, elevation, and responsive foundations.
5. Base UI owns accessible interaction behavior, including focus management, keyboard navigation, selection state, ARIA relationships, popup positioning, Escape handling, and outside-press handling.
6. Shared popup, list, positioning, and behavioral foundations remain private implementation details of Select, Combobox, and Autocomplete rather than public pieces that features assemble directly.
7. The rich-option content anatomy is the shared public composition surface. This lets features provide domain content without taking ownership of dropdown behavior.
8. Exact TypeScript symbol names and prop shapes belong to technical assessment as long as they preserve this boundary and do not expose unnecessary Base UI internals.
9. Dropdown controls provide generic loading and empty defaults, such as “Loading…” and “No options found.”
10. Consumers may replace those defaults with context-specific wording or richer non-interactive content. The opening picker should use this extension point for query-specific feedback.
11. The default responsive treatment remains an anchored popup rather than changing into a mobile sheet.
12. The popup is at least as wide as its control, may use a consumer-requested wider preferred size for rich content, and remains constrained within viewport gutters.
13. Base UI may shift or flip the popup to avoid collisions. The list uses the available bounded height and scrolls internally when needed.
14. Representative desktop and narrow Storybook sizes must demonstrate width, collision, maximum-height, and scrolling behavior before approval.

### Dropdown options

1. Provide a standard rich-option anatomy with slots for:
   - leading content;
   - primary text;
   - secondary text;
   - trailing content; and
   - selection indicator.
2. Include a custom-content escape hatch for cases that the standard slots cannot express.
3. The primitive provides flexible layout foundations but does not decide which feature information disappears, truncates, or wraps at narrow widths.
4. Each consumer owns the responsive priority of its domain content.
5. The custom-content escape hatch replaces only the option's visual body. It does not replace the semantic option container, selected and disabled treatment, or selection indicator.
6. Every custom option supplies a required plain-text label for its accessible name and default filtering text, even when that text is presented through custom visuals.

### RadioGroup

1. Use Base UI RadioGroup and Radio semantics, not ToggleGroup, for explicit one-of-many choices.
2. The segmented design shown by Both / White / Black becomes the default RadioGroup appearance.
3. Provide an explicit stacked-list appearance for long or explanatory choices.
4. Preserve a required selection. The active choice must not be toggleable into an empty state.
5. The control remains fluid rather than being sized for one viewport.
6. The consumer explicitly chooses segmented or stacked appearance according to its content rather than the component switching automatically at a viewport breakpoint.
7. Use segmented appearance for a small set of short labels. Use stacked rows when options have long labels, supporting descriptions, or cannot remain clear in a compact row.

### Existing-control migration compatibility

1. Migrating the eight suitable controls is behavior-preserving. It may change shared structure and styling but must preserve externally controlled values, labels, validation timing, disabled behavior, and existing empty-value meanings.
2. The native date input may receive the shared Field composition but is not converted into TextInput or deprived of its browser date picker before a separate date-control decision.
3. The Line Library binary checkbox may receive shared Field presentation while retaining its existing Base UI checkbox behavior and clickable label. The composite tri-state tree checkbox remains excluded.
4. Existing empty strings that mean “all” or no filter remain valid values. The migration must not silently create a second meaning for absence.
5. A later explicitly approved control replacement may change presentation while preserving meaning; feature behavior is not modernized incidentally during the shared-control migration.

### Buttons and non-behavioral pieces

1. Reuse the existing design-system Button for primary and ordinary button actions.
2. Combobox may use Base UI's dedicated clear behavior while matching the shared button and field styling.
3. Do not invent Base UI wrappers where there is no useful behavior to wrap. Badges, panel surfaces, move previews, and inline information bars remain semantic React components styled with production tokens.

## Opening-specific additions to the primitives

The opening picker will be composed only after the generic primitive direction is represented in the production Storybook. Its opening-specific pieces are additions through the approved primitive APIs:

- The search icon uses TextInput's leading slot.
- The selected ECO badge and clear action use trailing input content.
- Opening results use the shared dropdown-option slots:
  - ECO badge in the leading slot;
  - opening name as primary text;
  - move-sequence preview as secondary text;
  - repertoire side and line count as trailing content;
  - selected check through the selection-indicator slot.
- `EcoBadge` owns ECO presentation and any approved A-E family colour mapping.
- `RepertoireSideBadge` owns the White/Black glyph, label, accessible name, and its feature-controlled narrow-layout treatment.
- `MoveSequencePreview` owns SAN move-number formatting and truncation.
- `OpeningOptionRow` composes those domain pieces into the generic option slots.
- `OpeningSearchCombobox` owns opening filtering, selected-opening identity, opening query integration, and any synthetic "All openings" choice.
- `OpeningStartBar` is a domain composition using the existing design-system Button; it is not a generic toolbar primitive.
- Opening-specific match counts, empty copy, loading copy, and start feedback are supplied through the generic Combobox status/empty extension points or adjacent domain presentation.
- Repertoire side and Learner colour remain separate concepts and must not share state. In the desired future presentation, repertoire side filters which opening rows are browsed while Learner colour filters training positions by the learner's side to move.
- The initial application integration does not assume openings are colour-specific and does not add repertoire side to the training-requirements API. Repertoire-side presentation remains fixture-backed Storybook direction until its production data is deliberately revisited after user testing.
- When both controls eventually have production backing, their respective Both/all choices mean no filter on their own axis. Neither control synchronizes with or silently resets the other.
- “All openings” is an explicit selectable choice rather than an unlabeled cleared state. After commitment, the field displays “All openings.”
- In the initial application integration, “All openings” omits the opening key and retrieves across all openings while still applying Learner colour and as-of date. A future repertoire-side request contract may refine that behavior only after a separate decision.
- Opening search uses a complete, versioned catalogue snapshot persisted in the browser. Filtering after the snapshot is available is local rather than issuing a request for each keystroke.
- The persisted snapshot may include mutable aggregate fields, but the frontend must compare a backend-provided database or catalogue version and replace the snapshot when the active database changes. It may show the previous snapshot immediately while that check runs.
- A missing or stale snapshot triggers retrieval of a complete replacement. The exact browser storage mechanism and version-contract shape belong to technical assessment.
- Committed opening identity is held by the stable opening key rather than by the current result object, so filtering or replacing the snapshot does not itself change the selection.
- ECO, move preview, repertoire-side summary, and line count remain desired future opening-row presentation. Fixture data may represent them during Storybook design work.
- This grilling does not choose or imply a production source or persistence model for those fields. Their availability and semantics are assessed only after Storybook approval; any material product or data decision discovered then returns to the user.
- `EcoBadge` uses one consistent colour for each A-E ECO family. The visible ECO code remains the primary identification; colour is a secondary scanning cue and never the sole carrier of meaning.
- Clearing the opening field returns it to an uncommitted state rather than selecting “All openings.” It empties the query, hides the selected ECO badge, and leaves the primary action unavailable until the user explicitly selects a specific opening or “All openings.”
- Clearing the opening field preserves repertoire side, Learner colour, and as-of date. Escape closes the popup without clearing or changing those values.
- Focusing a committed selection selects its displayed opening name without changing the committed value. Typing replaces that text, clears the committed opening, hides its ECO badge, and starts a new query.
- The primary application action remains retrieval rather than claiming to begin a playable session. Its label becomes “Find training positions,” and successful retrieval continues to display the existing results in place.
- Application integration must wire the approved form state into the real training-requirements API request and retain its loading, empty, date-validation, stale-data, and error handling. This is not a fixture-only form after integration.
- That initial request uses the currently supported contract: a specific stable opening key when selected, no opening key for “All openings,” optional Learner colour, and the as-of date, while retaining the endpoint's existing opening-match and training-requirement filters.
- Repertoire side is not added to that request in this iteration. This is a deliberate provisional boundary for user testing, not a claim that production openings are colour-specific.
- Storybook remains application-isolated and may use controlled fixture handlers. Real API wiring begins only after explicit Storybook approval, in accordance with the workflow boundary below.
- At narrow widths, opening rows preserve ECO, opening name, and selection indication. Move preview truncates, line count hides first, and a repertoire-side label may collapse to its accessible glyph.
- The exact narrow breakpoint and truncation behavior require visual demonstration in Storybook rather than being assumed from the desktop mock-up.

## Intended production migration area

After Storybook approval, the principal opening-search integration target is `frontend/src/features/trainer-practice/TrainerPracticePanel.tsx`:

- replace its separate catalogue search field, search button, and raw Opening select with the approved opening-search composition;
- render its bounded Learner colour choice with the shared RadioGroup design while preserving All colours, White, and Black meanings;
- use the existing design-system Button for the “Find training positions” action; and
- preserve the production as-of date capability unless a later explicit decision changes it.

Supporting state and server integration remain in `TrainerPracticePage.tsx` and `trainerPracticeApi.ts`. Focused tests live in `TrainerPracticePanel.test.tsx`, `GameLoader.test.tsx`, `LineLibrary.test.tsx`, `App.test.tsx`, and `tests/e2e/trainer-practice.spec.ts`; the exact proof set belongs to later assessment rather than this record.

## Decision closeout

### Generic primitives

No unresolved product or behavior direction remains for the generic primitives. Exact TypeScript APIs, visual measurements, and responsive demonstrations belong to technical assessment and Storybook iteration within the boundaries above.

### Opening composition

No unresolved product or behavior direction remains for the opening composition at this stage. Production sources for fixture-backed future presentation fields remain deliberately deferred until after Storybook approval and user testing.

## Workflow boundary

This record is durable directional evidence, not a Plan or implementation authorization. The next visual step is to rebuild the generic primitives as application-isolated candidates in the existing production Storybook. Application integration and migration require explicit approval of those Storybook candidates first. Opening-specific integration is assessed only after that approval.
