# Documentation Router

Start here after reading [the repository instructions](../AGENTS.md).

## Workflow Documents

- [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md) defines focused Plans and nested work orders.
- [templates/order-packet.template.json](templates/order-packet.template.json) is the copy-and-edit source for every
  canonical order compile packet.
- [MASTER_PLAN_TEMPLATE.md](MASTER_PLAN_TEMPLATE.md) defines broad destinations and independently
  selectable slices.
- Active and completed Plans are discovered directly from `plans/active/` and `plans/done/`. Local Plan
  metadata and nested order artifacts are authoritative; there is no central Plan index.

## Technology Stack

Current implemented stack (MP-01 foundation plus the existing backend service):

**Backend**

- FastAPI: HTTP API service
- Pydantic: data validation and models
- uvicorn: ASGI server
- pytest: backend tests
- httpx: HTTP client for tests
- ruff: Python linting
- Python (3.12): runtime

**Frontend runtime**

- React (19.0.0): UI library
- react-router-dom (7.18.2): client-side routing
- @base-ui/react: accessible structural primitives (e.g. drawer)
- chess.js (1.4.0): FEN validation and position inspection
- react-chessboard (5.12.0): chessboard rendering
- react-error-boundary: unexpected render-failure containment
- lucide-react: local semantic icons

**Frontend tooling**

- TypeScript (5.7.3): typed JavaScript
- Vite (6.0.11): build tool and dev server
- Node (>=22 <23): runtime
- CSS Modules + shared global CSS: styling ownership
- Vitest + React Testing Library + jsdom: unit and component tests
- Storybook (10.5.8): mock-up and review components in isolation
- Playwright: end-to-end browser tests
- axe-core (@axe-core/playwright, @chialab/vitest-axe, Storybook addon-a11y): layered accessibility checks
- ESLint + Prettier: linting and formatting

## Adopting Chess Move Trainer

Add canonical references for the adopting project's architecture, product behavior, data, design, and
testing only when those contracts exist. Link them here and configure their validation deliberately;
this skeleton does not prescribe an application layout or technology stack.

<!-- initializer:upstream:start -->
## Optional upstream source

Optional upstream source: [https://github.com/skyrocoster/coordinatorConfig](https://github.com/skyrocoster/coordinatorConfig). Future improvements may be merged manually; this initializer does not synchronize repositories or mutate Git remotes.
<!-- initializer:upstream:end -->
