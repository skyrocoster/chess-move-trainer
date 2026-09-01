# Flexible repertoire columns — first design branch

This is a **noncanonical React + TypeScript + Vite design catalogue** beneath the preserved parent artifact
[`../initial.html`](../initial.html). It explores one question only: how can all three inherited principal columns
flex at useful desktop widths without leaving a lane that is merely decorative or unusable?

The page uses local fake repertoire, board, reach-frequency, staged-move, and engine-line data. It has no backend calls
and imports no production components. The three options are deliberately retained together:

- **01 · Fluid proportion** — relative weights solve a continuous three-way split, then stack all three lanes below
  their combined readable floor.
- **02 · Preferred envelopes** — pixel targets protect dense content, with spare room shared and the engine receiving
  the final stretch; its narrow fallback keeps Board + Session together before a full-width Engine tray.
- **03 · Priority dock** — bounded priority weights keep Board + Engine on the primary narrow scan path and dock
  Session below when three lanes cannot fit.

## Run

From the repository root:

```text
npm.cmd exec -- vite --config experiments/mock-ups/rearranged-rep/round-01-flexible-columns/vite.config.ts --host 127.0.0.1 --port 5176 --strictPort
```

Open `http://127.0.0.1:5176/`, then stop the server with `Ctrl+C`.

Build the disposable artifact with:

```text
npm.cmd exec -- vite build --config experiments/mock-ups/rearranged-rep/round-01-flexible-columns/vite.config.ts
```

Build output is written to `experiments/mock-ups/rearranged-rep/round-01-flexible-columns/.artifacts/dist/`.

## Interaction notes

Switch models with the three catalogue cards. Each model keeps its own allocation state, so switching does not erase a
previously explored setting. Drag or keyboard-adjust **all three** allocation sliders, use **Reset this model** or
**Reset all**, and resize the browser to observe each model's intentional narrow fallback. The annotation below the
workbench calls out the sizing rule, safeguards, and fallback for the active model.
