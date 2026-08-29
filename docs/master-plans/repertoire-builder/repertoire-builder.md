# Repertoire Builder — Viewer-first manual repertoire workspace

> **Status:** direction settled

> This Master Plan records an approved destination and selectable implementation slices. It does not authorize
> implementation. Every slice requires its own focused Plan and an explicit coordinator execution route. Slices are
> sequential; no slices run in parallel.

## Destination

Add a Viewer-style `/repertoire` workspace where Skyrocoster can build one manual preferred-move line from the standard
start or an existing game prefix, inspect neutral recurrence context, and explicitly save, replace, play, or remove
legal preferred moves without changing the accepted corpus or storage boundaries.

## Settled direction

- API-first is limited to the narrow neutral position-context endpoint; the preferred-move API is already complete and
  is an accepted foundation, not a new slice.
- Viewer-affecting capabilities are split and proven in Viewer first: Flip/navigation, position-count context, and
  clickable analysis moves. Repertoire Builder reuses those proven boundaries.
- Only the settled non-Viewer reusable UTC calendar component is created before the page scaffold.
- The Repertoire Builder scaffold remains thin: route, navigation, Viewer-style layout, and standard starting board;
  it must not create temporary workflow contracts or placeholder persistence.
- Position-picker and local-session mechanics precede the complete preferred-move persistence workflow.
- The default position is standard start with White at the bottom. An alternate game UUID plus ply shows the complete
  prefix through that ply and initially places Skyrocoster's actual recorded game color at the bottom.
- Bottom color means “me.” Opponent moves are local context and never persist; only bottom-color-to-move decisions can
  become preferred moves. There is one local SAN line, Previous/Next local navigation, no move tree, and no separate
  Undo/Reset controls.
- Flip keeps the position, cancels a pending unsaved response, and reinterprets “me.” Backtracking and choosing a new
  move discards only the later local continuation; persisted preferences remain.
- Existing preferred moves are read-only until explicit Edit, Play saved move, or confirmed Remove. Add/Edit stages one
  legal move for explicit Add/Save on “my” turns; opponent moves advance immediately without persistence.
- The neutral context endpoint uses accepted S4/direct recurrence facts. `color_scope` is Skyrocoster's stable game
  color, not side to move; recurrence uses distinct games and includes overall corpus existence.
- A zero count in the requested personal-color scope with overall corpus existence remains savable. No overall corpus
  existence means navigable but unsavable under the existing preferred-move boundary.
- One reusable UTC calendar-date component uses approved `react-day-picker` within Base UI Popover/design tokens. It has
  no editable time, treats blank as now, maps selected dates to `00:00 UTC`, disallows future dates, applies to
  add/replace/remove, and clears after successful mutation.
- The full existing AnalysisPanel controls remain. Every displayed legal candidate, including the rank-1 Best line,
  is clickable and behaves like a legal board drag; candidate behavior is implemented in Viewer first.
- Preserve fixed stable UUID ownership, one preferred move, exact four-field identity, full-FEN HTTP boundaries,
  legal UCI/SAN, existing corpus positions, append-only history, no schema change, and no S5 revival.

## Selectable slices

| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| **A1 — Neutral position-context API** | A neutral FEN request returns overall corpus eligibility and distinct-game White/Black recurrence for the stable subject. | Accepted S4 facts; accepted preferred-move API remains a separate foundation. | Preferred-move changes, schema/S5 work, side-to-move counts, mutations, and speculative APIs. |
| **V1 — Viewer Flip/navigation** | Viewer’s shared toolbar provides Flip without changing the current position; loaded-game orientation still starts at Skyrocoster’s recorded color. | A1 complete; focused V1 Plan accepted and complete. | Repertoire “me” semantics, preferred moves, and persistence. |
| **V2 — Viewer position-count integration** | Viewer shows the shared neutral recurrence statistic as White/Black or Never seen. | A1, V1 accepted/complete for sequence. | Personal projections, preferred state, and S4 changes. |
| **V3 — Viewer clickable analysis moves** | Viewer makes every displayed legal candidate, including Best line, activate the same legal move/promotion path as board drag. | A1, V1, and V2 accepted/complete; dependency satisfied. | Repertoire staging, Add/Save, persistence, and engine API changes. |
| **R1 — Reusable UTC calendar component** | A token-styled Base UI Popover date component supports the approved UTC-only date behavior. | A1–V3 for sequence; approved `react-day-picker` dependency. | Viewer integration, editable time, mutation-specific workflow, and extra dependencies. |
| **R2 — Repertoire Builder scaffold** | `/repertoire`, navigation, heading, Viewer-style workspace, and standard starting board with White bottom are available. | A1–V3, R1. | Temporary workflow contracts, fake save controls, alternate loading, and persistence. |
| **W1 — Position picker and local session mechanics** | Standard or game-prefix starts support one local SAN line, drag/candidate moves, local Previous/Next, Flip, staged “my” moves, and immediate opponent moves. | A1–V3, R1, R2; existing game-loader and promotion seams. | Preferred reads/writes, date mutation, line/tree storage, and S5. |
| **W2 — Complete preferred-move workflow** | The page supports read-only saved moves, Edit, Play saved move, confirmed Remove, explicit Add/Save, context/saveability messaging, and UTC-dated existing-API mutations. | A1–V3, R1, R2, W1, and the completed preferred-move API; all dependencies are accepted/done. | New preferred endpoints/fields, unobserved-position insertion, multiple moves, automatic selection, and schema changes. |

## Slice planning boundaries

Each item below is a boundary for its future focused Plan, not an implementation queue.

- **A1:** Expected areas are a bounded backend position-context feature, router registration, and isolated API tests.
  Read accepted S4 projections directly or through accepted recurrence access; do not edit recurrence scripts or schema.
  Prove valid/invalid FEN, White/Black game-color counts, overall existence, and safe unavailable-schema behavior.
  Escalate any new denominator, identity, schema, ownership, or API policy.
- **V1:** Expected areas are `BoardControl`, `ViewerWorkspace`, their focused stories/tests, and Viewer browser proof.
  Preserve page-owned navigation, branch, focus, accessibility, and layout ownership. Escalate any need for a
  universal navigation or workspace abstraction.
- **V2:** Expected areas are the shared position-context client/component and Viewer/GameContext composition with
  focused stories/tests/browser proof. Use recurrence color scope rather than side to move. Escalate any need for S5,
  personal projections, or changed Viewer ownership.
- **V3:** Expected areas are the controlled AnalysisPanel display/callback seam, analysis formatting, Viewer move
  wiring, and focused Viewer/Storybook/browser proof. Preserve legal drag, promotion, and focus behavior. The accepted
  product scope includes the rank-1 Best line and all displayed legal candidates. Escalate any backend engine contract,
  duplicate move implementation, or unresolved accessible affordance.
- **R1:** Expected areas are one reusable UTC calendar component, its stories/tests, and the frontend manifests. Use
  only the approved dependency and established Popover/tokens. Escalate any time-editing, timezone, token, or
  dependency expansion.
- **R2:** Expected areas are the App route, shared navigation entry, and a page-specific repertoire shell/stories/tests.
  Reuse existing leaf components without extracting a universal workspace framework. Escalate if the thin scaffold needs
  temporary state, placeholder persistence, or a visual/product decision.
- **W1:** Expected areas are the Repertoire page session model, picker surface, existing game-loading types, promotion
  behavior, and focused workflow proof. Do not copy Viewer chess semantics or the Viewer branch panel/Undo/Reset
  presentation; escalate if a bounded reuse/extraction cannot preserve them.
- **W2:** Expected areas are the Repertoire workflow, preferred-move frontend client, shared context/date components,
  and focused API-mocked/browser proof against the accepted preferred-move contract. Preserve append-only mutations,
  explicit user authority, unsavable absent positions, and successful-mutation date clearing. Escalate any contract,
  schema, ownership, automatic-selection, or multiple-move request.

## Slice results

- **A1:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/neutral-position-context-api/neutral-position-context-api.md)
- **V1:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/viewer-flip-navigation/viewer-flip-navigation.md)
- **V2:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/viewer-position-count/viewer-position-count.md)
- **V3:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/viewer-clickable-analysis-moves/viewer-clickable-analysis-moves.md)
- **R1:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/reusable-utc-calendar/reusable-utc-calendar.md)
- **R2:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/repertoire-builder-scaffold/repertoire-builder-scaffold.md)
- **W1:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/position-picker-local-session/position-picker-local-session.md)
- **W2:** [Accepted focused Plan — complete](../../plans/done/repertoire-builder/complete-preferred-move-workflow/complete-preferred-move-workflow.md)

## Exclusions

- Reviving, repairing, or publishing the abandoned S5 tracked-player projection.
- Any schema change, migration, recurrence rebuild, materialized personal projection, cache, line table, or move tree.
- Username identity, player selection, authentication, authorization, or changed ownership.
- Speculative APIs, speculative session storage, multiple preferred moves, automatic engine/population selection, or
  any silent persistence.
- Changes to accepted S4 facts, the existing corpus, or the completed preferred-move API and append-only storage.
- Separate Undo/Reset controls, broad repertoire architecture, universal Viewer/session/workspace frameworks, or
  unrelated visual redesign.
- Dependencies other than the approved `react-day-picker` dependency.
- READMEs, completed Plans, historical rewrites, runtime database writes, commits, pushes, and unrelated worktree
  changes.
