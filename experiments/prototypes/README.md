# Prototypes

Put isolated Python or TypeScript experiments in a topic folder here. Keep downloads and generated output in
that topic's ignored `.artifacts/` directory.

For TypeScript experiments, run npm commands from the repository root. Use `npm.cmd ci` for a clean install;
use `npm.cmd install <package>@<version> --workspace=experiments` when adding a dependency only to experiments.
If both workspaces need a package, target both explicitly with
`npm.cmd install <package>@<version> --workspace=frontend --workspace=experiments`.
