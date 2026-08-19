# Experiments

This workspace contains noncanonical exploration output. Nothing here changes application behavior until the
coordinator and user explicitly adopt it.

## Layout

- `mock-ups/<topic>/` contains standalone HTML/CSS review pages.
- `prototypes/<topic>/` contains isolated Python or TypeScript experiments.
- `fixtures/` contains small committed inputs used by experiments.
- `**/.artifacts/` contains ignored downloads, generated output, and other disposable runtime data.
- `pyproject.toml` and `package.json` describe the Python and Node workspace. Dependencies belong to the
  experiments workspace, not the application manifests.

The workspace may use the repository's existing ignored `.venv/` and `node_modules/` locations while keeping
generated artifacts ignored. Preserve unrelated user-owned content under `Scratch/`.
