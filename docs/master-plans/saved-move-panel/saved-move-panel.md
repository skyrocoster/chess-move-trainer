# Saved Move Panel

> **Status:** direction settled

## Destination
Make `/repertoire` and `/viewer` a shared, state-driven move-navigation workspace: people can navigate one linear history, inspect truthful current-position reach evidence, and manage preferred moves in repertoire without losing the accepted board, evaluation, source/ply, storage, session, or training behavior.

## Settled direction
- Upstream direction is [the confirmed saved-move panel redesign](../../grilling-docs/saved-move-panel-redesign.md); the mock-up is directional evidence only.
- Use the existing Material/CMT design system, typography, spacing, radii, focus treatment, reduced-motion behavior, forced-colour support, and primitives. Preserve the existing board and evaluation components.
- Move History is a real reusable component on both routes. It uses the existing linear history, supports active SAN selection, board synchronization, automatic scrolling, accessible focus, and previous/next/start/end navigation without variation trees.
- In `/viewer`, Move History replaces Game Context in place and retains essential source and ply information. Existing viewer branch behavior remains linear and must not become variation authoring.
- Position Reach Frequency measures `the user's games as the repertoire colour that reached this position / all of the user's games as that colour`. Its denominator is independent of display-board flip, and it updates after user moves, opponent moves, and every history transition.
- Preferred-move reads expose the persisted effective date additively and truthfully; `as_of` behavior, fixed ownership, append-only storage, and existing mutations remain intact. The repertoire panel displays, changes, and reloads that effective date.
- Repertoire uses state-driven panel presentation for no saved move, saved move, matching played move, and unsaved played move. Existing go-to/play, edit, remove, and date capabilities remain explicit; the mock-up's **Not now** action is not adopted.
- Slices are independently reviewable and follow the listed order. The existing completed Repertoire Builder foundation is accepted; the active Line Library Plan remains independent.

## Selectable slices
| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| **H1 — Shared Linear Move History Foundation** | Storybook shows a reusable CMT-styled linear history where a person can select SAN moves, use keyboard previous/next/start/end navigation, see the active move, and keep it in view. | Existing CMT design system and accepted viewer/repertoire linear position models | Route wiring, backend/API work, panel UX, effective dates, frequency, and changes to board/evaluation behavior |
| **D1 — Persisted Effective-Date Read Contract** | A preferred-move read returns the persisted effective date applied to the saved state, and the typed client retains it after reload. | Accepted preferred-move API and append-only storage | Panel redesign, changed `as_of` semantics, new persistence, schema changes, and recorded-date presentation |
| **F1 — Position Reach Frequency Contract and Component** | A reusable frequency component visibly presents the reached count, colour-correct all-games denominator, percentage/bar state, and unavailable states for the current position. | Accepted recurrence projections and position-context boundary | Route integration, move-frequency or engine statistics, new materialized data, migrations, and a denominator that follows board flip |
| **V1 — Viewer History and Context Replacement** | `/viewer` uses Move History in the existing Game Context location; selecting or navigating history changes the board, preserves source/ply, keeps the active move visible, and updates reach frequency. | H1 and F1 | Repertoire workflow, preferred-move mutations, duplicate context panels, and variation authoring |
| **R1 — Repertoire Linear History Integration** | `/repertoire` uses Move History to navigate its stored prefix and local SAN line while preserving current-position synchronization, opponent immediacy, and linear truncation/replacement. | H1 | State-driven saved-move presentation, effective-date UI, new persistence, and variation trees |
| **R2 — Repertoire State-Driven Panel** | `/repertoire` presents the four settled saved-move states with last-played focus, truthful effective date display/change, and Position Reach Frequency while the shared history remains synchronized. | D1, F1, and R1 | Mock Local Session strip, **Not now**, variations, multiple preferred moves, automatic persistence, board/evaluation redesign, and training changes |

## Slice results
- **H1:** Reusable controlled linear Move History with click and keyboard navigation, active-row synchronization, and automatic scrolling.
- **D1:** Additive preferred-move read semantics that expose the persisted effective date.
- **F1:** Reusable, colour-correct Position Reach Frequency for the current position.
- **V1:** In-place Viewer history replacement with retained source and ply.
- **R1:** Shared linear history navigation for the Repertoire Builder session.
- **R2:** Complete state-driven repertoire panel with truthful dates and current-position frequency.

## Exclusions
- The mock-up's board, evaluation treatment, inline palette, Local Session strip, and **Not now** action.
- Variation trees, branch management, multiple preferred moves, new training behavior, or changes to accepted linear session semantics.
- New database tables, migrations, recurrence rebuilds, materialized personal projections, caches, new identities, runtime data ownership, or speculative APIs. Existing read contracts may receive only the approved additive truthful fields; any broader API or data decision requires escalation.
- Changes to the accepted board, evaluation, fixed preferred-move ownership, append-only storage, source/ply context, or existing mutation authority.
- New dependencies, unrelated route redesign, authentication or authorization, and active Line Library selector or future preferred-move-line work.
- Historical-record rewrites, completed-plan edits, README work unrelated to this destination, `Scratch/` changes, commits, pushes, and unrelated worktree changes.
