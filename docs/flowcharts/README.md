# Database rebuild flowcharts (decision support)

Two visual maps of the clean database toolchain built by DB-01 through DB-08A, with the implemented
DB-08 rebuild operations, the `openings acquire` source step, and the DB-09 handoff shown as
decision-support context.

- [`database-toolchain.md`](database-toolchain.md) — the complete flow: Chess.com acquisition,
  raw month ledger, game import, opening publication, preferred moves, Stockfish
  benchmark/bulk/queue/worker, the neighbor database's ten tables, `rebuild refresh`,
  `rebuild verify`, `rebuild snapshot`, `rebuild candidate`, `rebuild replace`,
  `rebuild rollback`, and the DB-09 proof gate.
- [`database-operator-journeys.md`](database-operator-journeys.md) — the same toolchain seen as
  operator scenarios: refresh and verify, later managed-candidate staging, optional acquisition,
  direct serial initial analysis versus the API-03 queue, interruption and ordinary rerun,
  snapshot plus replacement, rollback, and DB-09 proof.
- [`database-command-inventory.md`](database-command-inventory.md) — the durable DB-09 package
  command inventory and the noncanonical/forbidden legacy `scripts/` boundary.

## Status: decision support only

These diagrams are **not** settled product authority and **not** implementation authorization.
They summarize the retained DB-08 assessment and the implemented command surface. The binding
authorities remain the master plan's DB-08 envelope and the two grilling documents named there.

Invariants shown deliberately: the old database (`data/database/chess_games.db`) is never
modified, snapshotted, replaced, or deleted by DB-08, and application cutover (CUT-01) lies
outside DB-08.

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

- Master plan DB-08 envelope: `docs/master-plans/database-rebuild/database-rebuild.md`
  (slice "DB-08 — Rebuild, snapshot, and replacement operations").
- Clean-toolchain records: `docs/plans/done/database-rebuild-db-01/` through
  `docs/plans/done/database-rebuild-db-07/` (each focused Plan owns its accepted CLI commands,
  package boundaries, and proof).
- Conceptual evidence touchpoints named by the DB-08 envelope (legacy scripts, backend path
  helpers) appear only as clearly marked legacy/future context, never as implementation targets.
