# Graph Report - .opencode  (2026-09-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 9 nodes · 8 edges · 3 communities (1 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- This report represents the complete pre-commit working tree, including local changes.
- See `manifest.json` for per-file content hashes.
- Refresh all layers with `timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py` (or invoke `/commit`, which runs it first).
## Community Hubs (Navigation)
- Community 0
- Community 1

## God Nodes (most connected - your core abstractions)
1. `globFiles()` - 3 edges
2. `execute()` - 2 edges
3. `resolveRg()` - 2 edges
4. `CACHE_RESUME_WINDOWS_MS` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (3 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.83
Nodes (3): execute(), globFiles(), resolveRg()

## Knowledge Gaps
- **1 isolated node(s):** `CACHE_RESUME_WINDOWS_MS`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 4 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `CACHE_RESUME_WINDOWS_MS` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
