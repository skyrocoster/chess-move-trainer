# Divider design catalogue — round 02 branch

This is a **noncanonical React + TypeScript + Vite catalogue** derived from the accepted interaction in
`round-02-adjacent-dividers/`. It keeps the same bounded three-panel mechanics and compares only the visual and
interaction affordance of the two internal dividers.

## Catalogue question

Which divider treatment makes the shared edge easiest to discover without turning it into a fourth working panel?

The six treatments are:

- **Whisper hairline** — quiet 1px seam; cleanest, but easiest to miss at rest.
- **Recessed rail** — visible inset gutter; structural and clear, but more engineered.
- **Centered pill** — compact rounded handle; familiar drag cue with a lighter full-height presence.
- **Dot grip** — three-dot tactile cue; friendly and compact, but potentially confused with a menu grip.
- **Edge tabs** — paired notches at the card edges; strong ownership of the shared boundary, with more visual noise.
- **State beacon** — near-invisible at rest, blue on hover/focus and amber while active; strongest feedback, weakest idle discovery.

The selected treatment is applied to both live `react-resizable-panels` v4.12.3 separators in the workspace preview.
The Group remains horizontal with Board, Session, and Engine in order; minimums are 320 px, 280 px, and 360 px.
Reset uses the Group's public `setLayout` API. The narrow stacked fallback renders no vertical separators.

## Run

From the repository root:

```text
npm.cmd exec -- vite --config experiments/mock-ups/rearranged-rep/round-02-divider-design-catalogue/vite.config.ts --host 127.0.0.1 --port 5178 --strictPort
```

Open `http://127.0.0.1:5178/`, then stop the server with `Ctrl+C`.

Build the disposable catalogue with:

```text
npm.cmd exec -- vite build --config experiments/mock-ups/rearranged-rep/round-02-divider-design-catalogue/vite.config.ts
```

Build output is written to `experiments/mock-ups/rearranged-rep/round-02-divider-design-catalogue/.artifacts/dist/`.
