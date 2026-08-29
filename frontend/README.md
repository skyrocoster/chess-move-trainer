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

| Directory                          | Purpose                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------- |
| `src/features/app-shell/`          | Layout container, error boundary, 404 view                                   |
| `src/features/board-adapter/`      | Chess board wrapper (read-only + interactive modes)                          |
| `src/features/design-system/`      | Shared UI: Button, Disclosure, feedback components, tokens                   |
| `src/features/repertoire-builder/` | Repertoire Builder: position-picker session with preferred-move workflow      |
| `src/features/status/`             | Backend health status page                                                   |
| `src/features/viewer/`             | Main viewer: board, game loading, analysis panel, eval bar, position context |
| `src/features/foundation/`         | Reserved (currently empty)                                                   |

## Running

Requires Node `>=24 <25` (pinned in `package.json` `engines`).

```bash
scripts/dev.py frontend          # starts on port 8444
# or: npm run dev --prefix frontend
```

## Storybook

```bash
npm run storybook --prefix frontend   # port 6006
```

The dev server on port 6006 is still required by the Playwright E2E Storybook specs in `tests/e2e/`;
the Vitest Storybook tests (see below) do not need it.

## Key config files

- `vite.config.ts` — Vite bundler config
- `vitest.config.ts` — Vitest test config
- `eslint.config.js` — ESLint config
- `.prettierrc.json` — Prettier config
- `.storybook/` — Storybook config (main.ts, preview.tsx)

## Tests

```bash
npm test --prefix frontend                           # all Vitest projects: `unit` (jsdom) + `storybook` (browser)
npm.cmd run test-storybook --prefix frontend -- --run  # Storybook tests only, in headless Chromium via Vitest browser mode; no separate Storybook server required
```

Unit tests are the isolated `unit` Vitest project. Storybook tests run through
`@storybook/addon-vitest` (Vitest 4 browser mode) and need no running Storybook server.
