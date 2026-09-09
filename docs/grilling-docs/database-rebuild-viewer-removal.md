# Database rebuild: retire Viewer instead of migrating it

> **Confirmed:** 2026-09-09
> **Role:** Directional evidence for assessment and planning; not implementation authorization.

## Decision

Retire the production Viewer completely instead of migrating its game loading, position context, and analysis workflows
to the clean generated API.

- Remove the `/viewer` route, its navigation entry, its workspace, and Viewer-only supporting artifacts.
- Let `/viewer` use the application's ordinary Not Found behavior. Do not add a redirect, compatibility page, or
  retirement message.
- Intentionally retire Viewer-only behavior, including standalone exploratory play with Undo/Reset and its terminal
  position messaging. Do not recreate those behaviors in Repertoire.
- Preserve Repertoire's existing visible behavior. Relocate the code, types, components, styles, fixtures, or test
  support that Repertoire still needs out of Viewer ownership rather than deleting them.
- Perform this as a dedicated removal slice before migrating Repertoire game loading. Do not combine the removal with
  clean game-detail adoption.

## Why

Viewer no longer justifies a separate product surface. Repertoire already provides the useful stored-game entry,
position navigation, board interaction, analysis, and position information that should remain in production. Keeping
Viewer would require three otherwise unnecessary consumer migrations and preserve a second workspace without enough
distinct value.

A separate removal slice keeps its proof simple: Viewer is gone, the old URL is unavailable, and Repertoire still
works. The following database-rebuild slice can then migrate Repertoire game loading without mixing API adoption into
destructive feature cleanup.

## Repository facts informing the decision

- Viewer is currently exposed by `frontend/src/App.tsx` and `frontend/src/features/app-shell/AppShell.tsx`.
- Repertoire currently imports several modules owned under `frontend/src/features/viewer/`, including game loading,
  analysis behavior, board controls, chess types, position context, and shared fixtures. Removing the directory without
  first relocating retained dependencies would break Repertoire.
- Viewer has dedicated component, Storybook, and Playwright coverage. Cross-feature route and shell coverage also
  references it and must be adjusted consistently.
- Existing routing has no redirect convention; unknown routes render the normal Not Found view.
- The current toolchain already provides the required frontend component, Storybook, and browser-test facilities. No
  new dependency or tool is justified by this change.

## Master-plan consequence

Assess an edit to `docs/master-plans/database-rebuild/database-rebuild.md` as part of carrying this direction forward;
do not create a separate plan for planning that edit.

- Replace the next Viewer migration with the dedicated Viewer-removal slice.
- Remove the future Viewer consumer migrations currently identified as `CONSUMER-02`, `CONSUMER-04`, and
  `CONSUMER-07`.
- Resequence the remaining Repertoire consumer slices and simplify retirement prerequisites that currently name both
  Viewer and Repertoire.
- Keep legacy backend routes until their remaining Repertoire consumers migrate in their own slices.

## Boundaries for assessment and planning

- No Repertoire redesign or new interaction.
- No clean API adoption in the Viewer-removal slice.
- No backend route retirement or old-database cleanup.
- No redirect, compatibility layer, replacement Viewer, or preservation of Viewer-only exploratory behavior.
- Preserve unrelated work and completed historical records.

Assessment must identify the exact retained dependencies that need neutral ownership, the Viewer-only artifacts that
can be deleted, the focused proof needed to establish unchanged Repertoire behavior and removed Viewer access, and the
corresponding direct edit to the active database-rebuild master plan.
