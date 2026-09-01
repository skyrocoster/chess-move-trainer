# Responsive columns — Idea 03 branch

This is a **noncanonical React + TypeScript + Vite mock-up** branched from
`round-02-divider-design-catalogue/`. It carries forward the selected **Idea 03: Centered pill** divider and
asks one narrower question: how should the bounded Board / Session / Engine workspace recompose as its available
container width changes?

## Responsive question

Can one workspace move cleanly through these container-aware arrangements without changing the selected divider cue?

- **Wide / 3 columns** — Board | centered pill | Session | centered pill | Engine. Both edges are live
  `react-resizable-panels` v4.12.3 separators. The stage edges stay fixed while the inside redistributes.
- **Medium / 2 columns** — Board occupies a full-width row. A separate horizontal `Group` puts Session and Engine
  below it, with one centered-pill divider between them.
- **Narrow / 1 column** — Board, Session, and Engine stack in that order at full width. No vertical separators are
  rendered.

The small mode annotation reports the live stage/container width and the active 3 / 2 / 1 arrangement. The
breakpoints are measured with `ResizeObserver` on the workspace stage rather than derived only from the browser
viewport:

- `>= 1,040px`: wide / 3 columns
- `700px – 1,039px`: medium / 2 columns
- `< 700px`: narrow / 1 column

The panel minimums remain 320px (Board), 280px (Session), and 360px (Engine); the two-panel medium group keeps the
Session and Engine minimums. Reset uses each Group's public `setLayout` API.

## Run

From the repository root:

```text
npm.cmd exec -- vite --config experiments/mock-ups/rearranged-rep/round-03-responsive-columns/vite.config.ts --host 127.0.0.1 --port 5178 --strictPort
```

Open `http://127.0.0.1:5178/`, then stop the server with `Ctrl+C`.

Build the disposable branch with:

```text
npm.cmd exec -- vite build --config experiments/mock-ups/rearranged-rep/round-03-responsive-columns/vite.config.ts
```

Build output is written to `experiments/mock-ups/rearranged-rep/round-03-responsive-columns/.artifacts/dist/`.
