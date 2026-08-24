# frontend

Vite React TypeScript client for the Chess Move Trainer.

## Entry point

`src/main.tsx` — mounts the React app with `BrowserRouter`.

## Convention

Each feature lives in `src/features/<name>/` and typically contains:

- `Component.tsx` — React component
- `Component.module.css` — CSS Module styles
- `Component.stories.tsx` — Storybook story
- `Component.test.tsx` — Vitest + React Testing Library test

## Features

| Directory | Purpose |
|-----------|---------|
| `src/features/app-shell/` | Layout container, error boundary, 404 view |
| `src/features/board-adapter/` | Chess board wrapper (read-only + interactive modes) |
| `src/features/design-system/` | Shared UI: Button, Disclosure, feedback components, tokens |
| `src/features/status/` | Backend health status page |
| `src/features/viewer/` | Main viewer: board, game loading, analysis panel, eval bar |
| `src/features/foundation/` | Reserved (currently empty) |

## Running

```bash
scripts/dev.py frontend          # starts on port 8444
# or: npm run dev --prefix frontend
```

## Storybook

```bash
npm run storybook --prefix frontend   # port 6006
```

## Key config files

- `vite.config.ts` — Vite bundler config
- `vitest.config.ts` — Vitest test config
- `eslint.config.js` — ESLint config
- `.prettierrc.json` — Prettier config
- `.storybook/` — Storybook config (main.ts, preview.tsx)

## Tests

```bash
npm test --prefix frontend              # Vitest unit/component tests
npm run test-storybook --prefix frontend # Storybook integration tests
```
