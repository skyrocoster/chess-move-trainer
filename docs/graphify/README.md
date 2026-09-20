# Graphify catalogue

Advisory, deterministic code maps for repository orientation and dependency
tracing. Source code and [`AGENTS.md`](../../AGENTS.md) remain authoritative.

Each layer contains a report, interactive graph, JSON graph, analysis, and
manifest:

- [Repository](repository/GRAPH_REPORT.md)
- [Backend](backend/GRAPH_REPORT.md)
- [Frontend](frontend/GRAPH_REPORT.md)
- [Core worker and schema source](core-data/GRAPH_REPORT.md)
- [Tests](tests/GRAPH_REPORT.md)
- [OpenCode workflow](agent-workflow/GRAPH_REPORT.md)

Refresh all layers from the repository root with
`.venv/Scripts/python.exe src/tools/graphify_catalogue.py`.
