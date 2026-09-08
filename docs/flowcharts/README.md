# Database rebuild flowcharts (decision support)

Two visual maps of the confirmed current DB-09 direct lifecycle: one fixed database, exactly
three public data-loading workflows, and a separate Stockfish analysis surface.

- [`database-toolchain.md`](database-toolchain.md) — the complete direct flow: retained game and
  opening sources, `setup`, `update games`, `update openings`, internal composition, the fixed
  database, separate Stockfish analysis, manual rare rebuild, and the DB-09 proof gate.
- [`database-operator-journeys.md`](database-operator-journeys.md) — the same lifecycle as
  operator scenarios: first setup, direct game updates, complete opening refresh, separate
  Stockfish analysis, manual rare rebuild, and the pre-application proof boundary.
- [`database-command-inventory.md`](database-command-inventory.md) — the exact three-workflow
  public data-loading inventory, separate Stockfish surface, absent lifecycle machinery, and
  noncanonical legacy-script boundary.

## Status: decision support only

These diagrams are **not** implementation authorization. They record the current direct-lifecycle
correction from the confirmed simple-lifecycle grilling record and active DB-09 Plan. The
completed DB-08/DB-08A Plans and prior grilling records remain historical and are not rewritten.

Invariants shown deliberately: the fixed destination is exactly `data/database/chess.db`; the
old production database remains untouched; raw sources are retained with only the approved
current-month refetch/merge and no deletion; other files under `data/database/` are outside the
workflow; and application integration/cutover remains behind the DB-09 pre-application gate.

## How to view the diagrams

The diagrams are fenced `mermaid` code blocks inside ordinary Markdown. How they render depends
on where you open them:

- **GitHub (simplest, nothing to install):** open either `.md` file in the repository on GitHub
  and view it rendered. GitHub renders Mermaid flowcharts natively in rendered Markdown views.
- **VS Code:** the built-in Markdown preview may or may not render Mermaid depending on your VS
  Code version and configuration. If you see the diagram as a plain code block, either view the
  file on GitHub or install a Mermaid-capable Markdown preview extension from the VS Code
  marketplace.
- **A plain browser:** double-clicking a local `.md` file shows raw text. A browser by itself
  cannot render Mermaid from a local Markdown file. Use GitHub, a Mermaid-capable editor or
  preview, or the external web-based Mermaid Live Editor (you would paste the diagram text into
  that website; it is a third-party site, not part of this repository).

Precisely stated: **no installation is required to view these diagrams on GitHub.** Viewing them
elsewhere requires a Mermaid-capable preview of some kind; there is no repository-local render
step.

## Where the content comes from

- Current behavioral authority: `docs/grilling-docs/database-rebuild-simple-lifecycle.md`.
- Current implementation boundary: `docs/plans/active/database-rebuild-db-09/database-rebuild-db-09.md`.
- Current master-plan record: `docs/master-plans/database-rebuild/database-rebuild.md`.
- Completed DB-08/DB-08A Plans and prior grilling records remain historical evidence and are not
  changed by this documentation correction.
