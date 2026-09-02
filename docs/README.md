# Documentation Router

Start here after reading [the repository instructions](../AGENTS.md).

## Workflow documents

- [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md) is the compact schema for focused implementation Plans.
- [MASTER_PLAN_TEMPLATE.md](MASTER_PLAN_TEMPLATE.md) is the compact schema for broad destinations and
  independently selectable slices.
- Active and completed Plans are discovered directly from `plans/active/` and `plans/done/`. There is no
  central Plan index.
- Grilling records, when needed, live under `grilling-docs/` as freely structured historical synthesis.

Plans are durable implementation context, not transient executor instructions. They describe semantic scope and expected areas;
the case-worker and coordinator keep exact execution boundaries in the active conversation. A transient
`handoff.md` may exist only during context rollover and is removed at closeout.

## Database schema

- [AI-readable SQLite schema](../data/database/schema.txt) is the generated reference for the repository-supported
  tables, keys, relationships, indexes, triggers, and canonical SQL.

## Technology stack

**Backend**

- FastAPI, Pydantic, uvicorn, pytest, httpx, and Ruff
- Python 3.12

**Frontend runtime**

- React, react-router-dom, @base-ui/react, chess.js, react-chessboard, react-error-boundary, and lucide-react

**Frontend tooling**

- TypeScript, Vite, Node `>=24 <25`, CSS Modules, Vitest, React Testing Library, Storybook, Playwright,
  axe-core, ESLint, and Prettier

## Experiments

Early exploration output is noncanonical until explicitly adopted. Basic HTML mock-ups, prototypes, small fixtures,
Python/Node manifests, and ignored generated artifacts belong under [`experiments/`](../experiments/README.md).
After the user selects an HTML direction, rebuild and iterate on it in the existing production Storybook while
keeping it disconnected from the application. Explicit approval of that Storybook candidate is required before
integration assessment. This flow uses the current checkout and does not create Git branches or worktrees.
Unrelated user-owned material under `Scratch/` remains in place.

## Adopting Chess Move Trainer

Add canonical references for the adopting project's architecture, product behavior, data, design, and
testing only when those contracts exist. Link them here and configure their validation deliberately; this
skeleton does not prescribe an application layout or technology stack.
