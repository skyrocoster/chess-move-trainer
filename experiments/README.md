# Experiments

This workspace contains noncanonical exploration output. Nothing here changes application behavior until the
coordinator and user explicitly adopt it.

## Layout

- `mock-ups/<topic>/` contains noncanonical review artifacts: self-contained HTML/CSS/JS pages or isolated
  React mock-ups.
- `prototypes/<topic>/` contains isolated Python or TypeScript experiments.
- `fixtures/` contains small committed inputs used by experiments.
- `**/.artifacts/` contains ignored downloads, generated output, and other disposable runtime data.
- `pyproject.toml` describes the Python workspace. The repository root npm package owns the `frontend` and
  `experiments` workspaces; Node dependencies belong to the experiments workspace, not the application manifest.

The workspace may use the repository's existing ignored `.venv/` and `node_modules/` locations while keeping
generated artifacts ignored. Preserve unrelated user-owned content under `Scratch/`.

## Mock-up fidelity

Mock-ups use the lowest fidelity sufficient for the current review decision. Prefer self-contained HTML/CSS/JS for
static or lightly interactive surfaces; use isolated React under `mock-ups/<topic>/` when shared state, transitions,
conditional behavior, focus, or realistic interaction is material. React dependencies belong to the experiments
workspace, never the application manifest, and React mock-ups stay isolated from application imports unless a brief
explicitly requests a repository-integrated review.

## Node dependencies

Use Node `>=24 <25`, matching the frontend. From the repository root, install all workspace dependencies with:

```text
npm.cmd install
```

For a clean install from the committed root lockfile, use:

```text
npm.cmd ci
```

To add a dependency only to experiments, target that workspace explicitly:

```text
npm.cmd install <package>@<version> --workspace=experiments
```

When both the frontend and experiments need a dependency, target both workspaces in one root command:

```text
npm.cmd install <package>@<version> --workspace=frontend --workspace=experiments
```

Npm does not automatically add a new dependency declaration to every workspace. Keep the root
`package-lock.json` authoritative and do not create child lockfiles.
