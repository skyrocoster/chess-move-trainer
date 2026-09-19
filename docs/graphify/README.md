# Graphify catalogue

This catalogue is an advisory map for AI coding agents. Source code, this
`AGENTS.md`, and active Plans remain authoritative when a graph suggestion is
unclear or stale. Graphify runs locally with deterministic AST extraction and
clustering only: it does not use an API, an LLM, semantic inference, or
AI-generated labels.

The six broad layers are refreshed together before `/commit` and cover the
repository, backend, frontend, the complete `src/` core/worker Python package
including schema source, tests, and `.opencode` workflow tooling. Graphify's
code-only mode excludes Markdown and YAML. Ignored runtime data and database
records, including `data/database/chess.db`, are never inputs; the database
layer represents schema source only.

Consult the catalogue when orienting yourself, tracing dependencies, locating
ownership, or working across repository boundaries. A small edit in a known
file does not require opening Graphify.

## Repository layer

`docs/graphify/repository/` — the full Git-visible, deterministically supported
repository corpus.

- [Report](repository/GRAPH_REPORT.md)
- [Interactive graph](repository/graph.html)
- [Graph JSON](repository/graph.json)
- [Analysis JSON](repository/.graphify_analysis.json)
- [Incremental manifest](repository/manifest.json)

## Backend layer

`docs/graphify/backend/` — backend application and colocated backend tests.

- [Report](backend/GRAPH_REPORT.md)
- [Interactive graph](backend/graph.html)
- [Graph JSON](backend/graph.json)
- [Analysis JSON](backend/.graphify_analysis.json)
- [Incremental manifest](backend/manifest.json)

## Frontend layer

`docs/graphify/frontend/` — frontend application, component tests, and
Storybook source.

- [Report](frontend/GRAPH_REPORT.md)
- [Interactive graph](frontend/graph.html)
- [Graph JSON](frontend/graph.json)
- [Analysis JSON](frontend/.graphify_analysis.json)
- [Incremental manifest](frontend/manifest.json)

## Core worker and database schema layer

`docs/graphify/core-data/` — the complete `src/` core/worker Python package,
including Python schema modules and SQL schema or migration source. It never
represents live database records.

- [Report](core-data/GRAPH_REPORT.md)
- [Interactive graph](core-data/graph.html)
- [Graph JSON](core-data/graph.json)
- [Analysis JSON](core-data/.graphify_analysis.json)
- [Incremental manifest](core-data/manifest.json)

## Tests layer

`docs/graphify/tests/` — top-level integration, database, engine, and
end-to-end tests. Backend and frontend tests remain in their domain layers.

- [Report](tests/GRAPH_REPORT.md)
- [Interactive graph](tests/graph.html)
- [Graph JSON](tests/graph.json)
- [Analysis JSON](tests/.graphify_analysis.json)
- [Incremental manifest](tests/manifest.json)

## Agent workflow layer

`docs/graphify/agent-workflow/` — supported code in `.opencode` agent workflow
and tooling. Markdown remains excluded by code-only extraction.

- [Report](agent-workflow/GRAPH_REPORT.md)
- [Interactive graph](agent-workflow/graph.html)
- [Graph JSON](agent-workflow/graph.json)
- [Analysis JSON](agent-workflow/.graphify_analysis.json)
- [Incremental manifest](agent-workflow/manifest.json)
