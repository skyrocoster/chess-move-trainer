# Frontend audit: Chess Move Trainer

## What we looked at

- `frontend/src/main.tsx` and `frontend/src/App.tsx` — routing and app shell
- `frontend/src/features/app-shell/AppShell.tsx` and `.module.css` — persistent navigation
- `frontend/src/features/status/StatusView.tsx` and `.module.css` — landing status page
- `frontend/src/features/trainer-practice/TrainerPracticePanel.tsx` — training setup and results
- `frontend/src/features/trainer-practice/TrainerPracticePage.tsx` — page wiring
- `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx` and `.module.css` — main workspace
- `frontend/src/features/repertoire-builder/RepertoireBoardLane.tsx` — board + history + controls
- `frontend/src/styles/cmt-tokens.css` and `frontend/src/styles/cmt-typescale.css` — design tokens

## Current visual direction in one sentence

The app is an **austere dark Material 3 shell** — near-black background `#121318`, lavender primary `#bac3ff`, system-ui typeface, strict 4/8/12/16/24/32/48 spacing, and almost no chess-specific personality layer.

## What works

- **Solid accessibility foundation.** Skip link, visible 2px focus rings, `prefers-reduced-motion` support, forced-colors fallbacks, `aria-current` nav states, and proper ARIA live regions are already in place.
- **Sane information architecture.** Sidebar + main content, mobile drawer, sticky header, responsive breakpoints at 679px.
- **Repertoire workspace has real interaction character.** Last-move highlighting, promotion picker, orientation flip, analysis tabs, move-response distribution, and history navigation give this surface a clear purpose.
- **Token discipline.** Colors, spacing, radii, elevation, and type roles are centralized and consistently applied.

## Where the design is weakest

1. **Status page is a single alert.** `StatusView.tsx` is just a heading plus one `InlineFeedback` banner. It tells the user the backend is healthy, but it does not welcome them, orient them, or give them anywhere to go.
2. **Trainer Practice is an API dump.** Results are rendered as raw `<dl>` key-value pairs (`fen`, `preferred_move_uci`, `encounters`, `effective_training_balance`, etc.) with no board, no move notation cards, no progress signals, and no clear call to action. The most important surface in the product currently looks like a debug panel.
3. **No product identity beyond Material defaults.** The shell, navigation, cards, buttons, and type scale could be dropped into any admin dashboard unchanged. There is no color, texture, or interaction motif that says "chess."
4. **The board feels bolted onto generic chrome.** `react-chessboard` is wrapped in functional but visually neutral lanes. The board does not feel like the hero of the experience.
5. **Navigation labels describe features, not jobs.** "Status," "Repertoire Builder," and "Trainer Practice" are accurate but uninspiring. They do not answer "What am I here to do?"

## Real content and user jobs

The app serves players who want to:

- **Build an opening repertoire** from their own games or imported positions.
- **Train moves** until they can play them confidently in games.
- **Review progress** and decide which lines need attention.

Those jobs are study-shaped: focus, repetition, feedback, and gradual mastery. The current UI treats them more like database administration.

## Biggest opportunities for redesign

| Priority | Surface | Opportunity |
|----------|---------|-------------|
| 1 | Trainer Practice | Turn the raw training-requirements list into a real practice session with a board, move cards, progress, and answer feedback. |
| 2 | Status / Home | Make the landing page useful: show readiness, quick-start actions, and a sense of momentum. |
| 3 | App shell | Give navigation a chess identity through color, iconography, or layout without breaking the accessible structure. |
| 4 | Repertoire workspace | Refine the lane composition so the board feels central and the analysis tabs feel like supporting context. |

## Existing mock-ups to preserve

- `experiments/mock-ups/opening-search-combobox/` — refined dark search selector for openings.
- `experiments/mock-ups/focused-trainer-session/` — warm light "study hall" trainer flow with board, feedback cards, and completion states.

## Notes for the alternative designs that follow

Each alternative below redesigns the same two surfaces so they can be compared directly:

1. **Home / status landing** — what a new or returning player sees first.
2. **Trainer practice session** — the core learning loop.

They deliberately explore different personalities, so we can decide which direction best matches the product's actual audience and job.

---

*Generated during frontend-design exploration. Preserve existing production source and prior mock-ups; these are alternatives, not replacements.*
