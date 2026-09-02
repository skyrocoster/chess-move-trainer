# Experiments

This workspace contains noncanonical exploration output. Nothing here changes application behavior until the
coordinator and user explicitly adopt it.

## Layout

- `mock-ups/<topic>/` contains noncanonical review artifacts: self-contained HTML/CSS/JS pages or isolated
  React mock-ups.
- `prototypes/<topic>/` contains isolated Python or TypeScript experiments.
- `fixtures/` contains small committed inputs used by experiments.
- `**/.artifacts/` contains ignored downloads, generated output, and other disposable runtime data.
- `pyproject.toml` describes the Python workspace. The repository root npm package owns the `frontend`
  and `experiments` workspaces. The experiments workspace currently carries no Node dependencies;
  any future experiment-specific needs are added explicitly, not as standing full-stack access.

The workspace may use the repository's existing ignored `.venv/` and `node_modules/` locations while keeping
generated artifacts ignored. Preserve unrelated user-owned content under `Scratch/`.

## Mock-up fidelity

Mock-ups use the lowest fidelity sufficient for the current review decision. Prefer self-contained HTML/CSS/JS for
static or lightly interactive surfaces; use isolated React under `mock-ups/<topic>/` when shared state, transitions,
conditional behavior, focus, or realistic interaction is material. The experiments workspace carries no standing
Node dependencies, so React mock-up needs are added explicitly per experiment and stay isolated from application
imports unless a brief explicitly requests a repository-integrated review.

## Node dependencies

The experiments workspace currently has no Node dependencies. Node `>=24 <25` still matches the frontend. If a
future experiment needs a dependency, target the experiments workspace explicitly from the repository root:

```text
npm.cmd install <package>@<version> --workspace=experiments
```

Keep the root `package-lock.json` authoritative and do not create child lockfiles.
