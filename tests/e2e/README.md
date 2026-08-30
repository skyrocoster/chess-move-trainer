# e2e

Playwright end-to-end browser tests.

## Config

`playwright.config.ts` — sets base URL to `http://localhost:8444` and auto-starts three web servers:

| Server | Port | Purpose |
|--------|------|---------|
| Backend (uvicorn) | 5666 | API health check at `/api/health` |
| Frontend (Vite) | 8444 | Dev server for browser tests |
| Storybook | 6006 | Component isolation for Storybook-based tests |

## Running

```bash
npx playwright test --config tests/e2e/playwright.config.ts
```

Tests require both the backend and frontend to be available. If they are already running, Playwright reuses them.

## Spec coverage

Specs cover the status page, viewer (live, branch, storybook), responsive shell, board adapter, design-system accessibility, and the opening line-library Storybook surface (synthetic in-memory fixtures).
