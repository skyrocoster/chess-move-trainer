# Analysis page

**Started:** 2026-09-21  
**Status:** Implemented and locally verified.  
**Authority:** The user asked for a new analysis page to be implemented directly without a question round. This record captures the assumptions, repository facts, decisions, and verification made during that work; it is not a separate Plan.

## Goal

Add a useful analysis page that presents the analysis data already prepared by the backend, follows the existing frontend architecture and visual conventions, and lets users narrow the data with appropriate filters.

## Initial assumptions

- Existing backend analysis contracts remain authoritative; this work should not invent a second calculation layer in the browser.
- Existing shared page, input, feedback, loading, and data-display components should be reused or extended before introducing new equivalents.
- Filters should reflect real backend-supported dimensions and should make their active scope clear, including empty, loading, error, and reset behavior.
- The page should be reachable through the application's normal navigation and routing conventions.
- Desktop and narrow-screen layouts should both remain usable, with accessible labels and keyboard-operable controls.

## Intended work

1. Find the prepared analysis endpoints and their tests, then record the exact data and filter contract here.
2. Find the nearest existing page, navigation, query, and component patterns and reuse them.
3. Implement the route, navigation entry, analysis presentation, filter behavior, and all normal request states.
4. Add focused component/API tests and verify the relevant behavior locally.

## Decisions and repository facts

### Backend contract

- `GET /api/statistics/overview` is the page's primary source. It already returns game results, rating progression, activity, openings, opponents, recurring positions, analysis coverage, repertoire coverage, training balances, and data-quality counts in one read-only response.
- The backend applies four report cuts consistently: game start date from/to, learner colour, and time class. A required `as_of` date gives repertoire training balances their historical context.
- Invalid filters return `422 invalid_filter`; unavailable storage returns `503 statistics_unavailable`; unexpected failures return a safe `500 unexpected_failure` response.
- The endpoint returns stable zero and empty-list shapes when no games match. The frontend therefore does not need to invent fallback calculations or a second aggregation layer.
- The checked-in generated frontend contract predated the endpoint. It is being refreshed from the served FastAPI OpenAPI document so the page can use the repository's central typed client rather than a one-off fetch call.

### Page direction

- **Thesis:** a chess scorecard, not an engine console. The first view should answer “How am I doing in this slice?” before exposing deeper preparation and coverage details.
- **Palette:** keep the existing Material surface and primary roles; reuse the repository's fixed success, warning, and error accents for wins, draws, and losses. No page-only colour system is added.
- **Type:** keep the repository's system type scale. Large tabular numerals carry the score and rating; headings and labels stay quiet and consistent with the existing shell.
- **Structure:** one global filter card feeds one report. A prominent result record leads into performance breakdowns, while preparation and data-health details sit in clearly named secondary sections.
- **Signature:** a reusable win/draw/loss score track makes the selected slice readable at a glance and also works in the detailed breakdown rows.
- **Restraint:** no decorative chessboard, engine evaluation, or unrelated motion. The data and the active scope remain the focus.

### Filter and request behavior

- The page loads an all-games report immediately using today's UTC date as the training snapshot.
- Filter edits are drafts until “Apply filters” is pressed, preventing a network request for every calendar or dropdown interaction.
- “Reset filters” clears the game cuts and restores today's snapshot in one action.
- The page validates that the start date is not after the end date before requesting data and keeps the last successful report visible while an applied filter refresh is in progress.
- The applied scope is stated in plain language above the results so users can see exactly which dates, colour, and time class they are viewing.

### Implemented page structure

- `/analysis` is lazy-loaded through the existing application router and linked from both desktop and drawer navigation.
- The Performance tab leads with the selected win/draw/loss scorecard, rating context, recent form, monthly results, and backend-provided breakdowns by time class, colour, rating matchup, game length, time control, and termination.
- The Openings tab presents the classified/unclassified scope and the backend's opening result table.
- The Preparation tab presents engine coverage, move-preference coverage, preferred-move adherence, training balances, queue state, recurring positions, and an expandable data-quality summary.
- A shared `OutcomeTrack` now owns the win/draw/loss bar used by both this report and the existing engine analysis panel. This avoids creating a second version of the same visual component.
- Previous report data stays visible while a changed scope loads. Its displayed scope comes from that response, so a failed update never labels old data with new filters.
- Empty reports, initial loading, failed first loads, failed updates, retry actions, narrow screens, forced colours, reduced motion, and horizontally scrollable tables all have explicit behavior.
- Read-only SQLite connections use a bounded 256 MiB memory-map ceiling. This keeps the aggregate report practical when the database is bind-mounted into Docker Desktop on Windows without changing the database or increasing the writable connection policy.

## Verification log

- Refreshed the checked-in OpenAPI contract from FastAPI and regenerated the central frontend client. A semantic audit confirmed that this was additive only: the existing operations and schemas are unchanged, while `GET /api/statistics/overview`, its statistics schemas, generated types, SDK function, and query helper were added.
- Final focused Vitest run passed: **99 tests passed** across the analysis page/API, shared analysis panel and design-system components, router, query keys, generated API surface, central-client adoption guard, and the other reviewed component families.
- Frontend TypeScript project check passed with no errors.
- Targeted Prettier check passed for every changed frontend, generated-client, and grilling-record file.
- Component accessibility checks passed for the visible Performance and Preparation views, and the focused tests exercise tab navigation, deferred filter application, empty data, and unavailable-data recovery.
- Live verification against the managed Docker services succeeded after Docker Desktop became available. `GET /api/statistics/overview` returned `200`; `/analysis` rendered the real 12,710-game report; and the Performance, Openings, and Preparation tabs exposed their labelled regions, tables, and meters.
- The first live report exposed Windows bind-mount performance above two minutes. Enabling SQLite's read-only memory map reduced a fresh container request to **16.7 seconds**. The focused connection/reporting suite passed: **23 tests passed**.
- The only browser-console error was the repository's existing missing `/favicon.ico`; no page, API, React, or Storybook runtime error appeared.
