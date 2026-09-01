# Adjacent divider split view — focused branch

This is a **noncanonical React + TypeScript + Vite mock-up** continuing the preserved parent concept and rejected
Round 01. It answers one focused question: can a user move the actual shared edge between each adjacent column rather
than manipulate an abstract allocation?

The wide layout has exactly two vertical divider bars supplied by `react-resizable-panels` v4.12.3:

- The **Board / Session** bar starts by changing those adjacent panel sizes. The library may use other available room
  when a minimum is reached.
- The **Session / Engine** bar starts by changing those adjacent panel sizes. Board stays unchanged unless a minimum
  requires the library to redistribute available room.

The library owns pointer dragging and keyboard controls: `←` / `→` move the active boundary by its built-in step, and
`Home` / `End` jump to the active boundary limits. Board, Session, and Engine have readable minimums of 320 px, 280
px, and 360 px respectively. **Reset split** calls the Group's public `setLayout` API to return to the initial split.

When the stage cannot fit those minimums, the bars are not rendered. An obvious stacked fallback appears instead, with
Board → Session → Engine in full-width reading order. This branch uses only local fake repertoire, board, and engine
data; it has no backend calls and imports no production code. The parent `initial.html` and
`round-01-flexible-columns/` remain unchanged.

## Run

From the repository root:

```text
npm.cmd exec -- vite --config experiments/mock-ups/rearranged-rep/round-02-adjacent-dividers/vite.config.ts --host 127.0.0.1 --port 5177 --strictPort
```

Open `http://127.0.0.1:5177/`, then stop the server with `Ctrl+C`.

Build the disposable artifact with:

```text
npm.cmd exec -- vite build --config experiments/mock-ups/rearranged-rep/round-02-adjacent-dividers/vite.config.ts
```

Build output is written to `experiments/mock-ups/rearranged-rep/round-02-adjacent-dividers/.artifacts/dist/`.
