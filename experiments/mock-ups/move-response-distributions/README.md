# Move response distributions

This is a **noncanonical exploration artifact**. The default route is a standalone React + TypeScript + Recharts Vite
page for selected direction `01C · Grouped tail with disclosure`. It shows only that direction: a classic labeled pie,
five common replies, and a grey `Other` disclosure for four rare replies.
It does not change the canonical frontend, backend, tests, Plans, or product documentation.

The repository-aware synthesis for the signed-off direction is [DESIGN.md](DESIGN.md). It remains noncanonical design
evidence and is not an implementation authorization.

Run from the repository root:

```text
npm.cmd exec -- vite --config experiments/mock-ups/move-response-distributions/vite.config.ts --host 127.0.0.1 --port 5175 --strictPort
```

Open `http://127.0.0.1:5175/`, then stop the server with `Ctrl+C`. The preserved Round 02 catalogue is available at
`http://127.0.0.1:5175/archive/round-02-catalogue/` for lineage and reference only.

Each common sector is clickable. Each represented move has an equivalent text control; `Other` is the text/sector
disclosure control and its four individual move controls appear when opened. The sample is simulated.

Build the document from the repository root with:

```text
npm.cmd exec -- vite build --config experiments/mock-ups/move-response-distributions/vite.config.ts
```

The build writes disposable output to `experiments/mock-ups/move-response-distributions/.artifacts/dist/`.
The page uses the existing workspace copies of React, Recharts, chess.js, and react-chessboard; it adds no
dependencies. The archive preserves the prior full catalogue without making it the default page.
