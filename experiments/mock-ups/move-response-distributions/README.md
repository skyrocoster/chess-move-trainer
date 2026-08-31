# Move response distributions

This is a **noncanonical exploration artifact**. It is a standalone React + TypeScript + Recharts Vite
document for comparing five ways to present Black's responses after `1.e4`. It does not change the
canonical frontend, backend, tests, Plans, or product documentation.

Run from the repository root:

```text
npm.cmd exec -- vite --config experiments/mock-ups/move-response-distributions/vite.config.ts --host 127.0.0.1 --port 5175 --strictPort
```

Open `http://127.0.0.1:5175/`, then stop the server with `Ctrl+C`.

Build the document from the repository root with:

```text
npm.cmd exec -- vite build --config experiments/mock-ups/move-response-distributions/vite.config.ts
```

The build writes disposable output to `experiments/mock-ups/move-response-distributions/.artifacts/dist/`.
The page uses the existing workspace copies of React, Recharts, chess.js, and react-chessboard; it adds no
dependencies.
