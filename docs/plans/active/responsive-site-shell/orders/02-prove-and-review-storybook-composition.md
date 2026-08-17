# WORK ORDER 02 — Prove and review Storybook composition

- **OUTPUT:** `docs/plans/active/responsive-site-shell/orders/02-prove-and-review-storybook-composition.md`
- **GOAL:** Prove the complete real-component Storybook composition at every required width and stop for the explicit pre-adoption human gate without changing the production composition.
- **REQUIRED STRENGTH:** High — The order coordinates the verified real-iframe readiness and axe-scope correction with deterministic focus, scrim, and recovery interaction proof across four required viewports and the pre-adoption review gate.
- **DEPENDS ON:** `docs/plans/active/responsive-site-shell/orders/01-build-complete-storybook-shell-composition.md`

## Authorization

### Creates
- none

### Edits
- `tests/e2e/responsive-shell-storybook.spec.ts`

### Removes
- none

## Context inputs
1. `docs/plans/active/responsive-site-shell/responsive-site-shell.md` — whole file
   - Purpose: The approved MP-03 Plan records the Stage 2 boundary, acceptance gate, proof contract, exclusions, and escalation conditions.
2. `tests/e2e/playwright.config.ts` — whole file
   - Purpose: Preserve the existing backend, frontend, and Storybook server layout, base URL, headless mode, and reuseExistingServer behavior while running the browser proof.
3. `tests/e2e/responsive-shell-storybook.spec.ts` — whole file
   - Purpose: The authorized Storybook browser proof whose verified root correction and remaining deterministic focus, scrim, and recovery interactions require the bounded repair.
4. `frontend/.storybook/test-runner.ts` — whole file
   - Purpose: Retained valid Storybook test-runner setup for viewport configuration; it is attempted work and is not authorized for editing.
5. `frontend/src/features/app-shell/AppShell.stories.tsx` — whole file
   - Purpose: Retained real-component Storybook stories and passing interaction repairs; they are context only and are not authorized for editing.
6. `frontend/src/features/app-shell/AppShell.tsx` — whole file
   - Purpose: Read-only context for the real shell controls, CSS breakpoint, Base UI drawer, accessible names, and portaled drawer behavior.
7. `frontend/src/features/app-shell/PageContentBoundary.tsx` — whole file
   - Purpose: Read-only context for the real error-boundary fallback and reset composition covered by the retained Storybook recovery interaction.
8. `frontend/.storybook/main.ts` — whole file
   - Purpose: Read-only Storybook configuration context; preserve the existing Storybook 10 and addon configuration.
9. `frontend/.storybook/preview.tsx` — whole file
   - Purpose: Read-only Storybook preview and decorator context; preserve the existing preview behavior.

## Known facts
- Stage 1 human acceptance is recorded and the complete real-component Storybook composition is shipped; production frontend/src/App.tsx remains untouched.
- The Storybook title is App Shell/AppShell and the relevant CSF ids are app-shell-appshell--wide-healthy, app-shell-appshell--constrained-closed, app-shell-appshell--constrained-open, app-shell-appshell--loading, app-shell-appshell--healthy, app-shell-appshell--unavailable, and app-shell-appshell--unexpected-failure-try-again.
- The exact review viewports are 1920x1080, 412x915, 679x915, and 680x915; the native CSS breakpoint is max-width: 679px, so 679px is constrained and 680px is desktop.
- The existing Playwright configuration starts backend port 5666, frontend port 8444, and Storybook port 6006 with reuseExistingServer true, baseURL http://localhost:8444, and headless execution; preserve this configuration.
- Storybook 10, @storybook/addon-a11y, storybook/test imports, @storybook/test-runner, and @axe-core/playwright are already installed and must be retained; no addon or package is needed.
- The existing frontend/.storybook/test-runner.ts provides the retained viewport setup and must not be edited by this order.
- The existing AppShell.stories.tsx uses within for in-canvas content and the owner document body for portaled drawer content; the UnexpectedFailureTryAgain play interaction passes and the story file must not be edited by this order.
- The real Storybook iframe mount root is #storybook-root; the readiness wait and application-owned axe include scope already use that confirmed selector and must remain aligned.
- The browser proof must use the real Storybook iframe and production components, not a mock, fixture, parallel component, or request mock.
- Required browser proof covers desktop sidebar at 1920 and 680, constrained trigger and hidden desktop sidebar at 412 and 679, drawer title/close/name, initial Close focus, focus containment, Close/Escape/scrim/Status dismissal, trigger focus restoration, Base UI inertness and scroll behavior, reduced-motion suppression, loading/healthy/unavailable exact copy with role=status or role=alert, Page unavailable exact copy with Try again recovery, and clean application-owned axe checks.
- The current focused proof has build-storybook passing, test-storybook passing 20/20, and the responsive Storybook browser spec passing 15/18; the three failures are focus containment after rapid key presses, scrim targeting at x=4 inside the open drawer, and Try again button detachment during the retained Storybook play interaction.
- Bounded replays showed that polling focus containment after each key, targeting an exposed right-side scrim point, and synchronizing an immediate real Try again button action each passed 10/10; preserve real UI interaction and do not use DOM event dispatch or an actionability bypass.
- Stage 2 is verification-only: do not edit frontend/src/App.tsx, adopt production CSS, begin Stage 3, add a route, add a dependency, or change production behavior.

## Ordered actions
1. **file** (`tests/e2e/responsive-shell-storybook.spec.ts`) — Edit only this Storybook browser spec. Preserve the confirmed #storybook-root readiness wait and the matching #storybook-root axe include scope. Preserve the real iframe URLs and story ids, all four viewport cases, desktop and constrained assertions, drawer modality and every focus/dismissal/inertness/scroll assertion, reduced-motion behavior, exact loading/healthy/unavailable roles and copy, unexpected-failure recovery, and clean application-owned axe checks. In the focus-containment loop, synchronize after each Tab or Shift+Tab until the real active element is inside the dialog, then retain the assertion that it is inside; do not weaken or remove the assertion. For scrim dismissal, activate a visible exposed point on the right-side scrim outside the open 321px drawer at the 412px viewport, retaining dialog-hidden and trigger-focus assertions; use a real Playwright UI interaction. For unexpected-failure recovery, synchronize a real Playwright click on the visible Try again button against the retained Storybook play interaction and possible button detachment, while retaining the exact fallback and recovered-copy assertions; do not use DOM event dispatch, an actionability bypass, mocks, fixtures, or changes to the story. Do not add packages, addons, production edits, or any other path.

## Exact proof commands

### Proof 1 — Build the complete Storybook composition and verify the retained Storybook 10 stories and test-runner-compatible source compile.
Working directory: `.`

```text
npm run build-storybook --prefix frontend
```

### Proof 2 — Run the Storybook interaction proof, including the retained drawer and unexpected-failure recovery interactions, without introducing another testing addon.
Working directory: `.`

```text
npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006
```

### Proof 3 — Run the required real-iframe responsive browser proof, modal and focus checks, exact state assertions, reduced-motion checks, and axe checks.
Working directory: `.`

```text
.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\responsive-shell-storybook.spec.ts
```

## Acceptance handoff

### Coordinator
- After all three declared focused proof commands pass, review the complete Storybook composition at 1920x1080, 412x915, 679px, and 680px using a stable height for width-edge review.
- Confirm that 679px uses the drawer mode and 680px uses the desktop sidebar, with the transition owned by native CSS and no JavaScript layout decision.
- Confirm clean application-owned axe results and manually inspect focus order, keyboard operation, initial and restored focus, focus containment, Close/Escape/scrim/Status dismissal, inertness, scroll behavior, reduced motion, contrast, and comprehension.
- Confirm that no addon, package, mock, fixture, production App.tsx or CSS adoption, Stage 3 work, DOM-dispatched interaction, actionability bypass, or weakened assertion was introduced.
- Record explicit human pre-adoption approval of the complete Storybook composition before authorizing any order that modifies frontend/src/App.tsx; if approval is not granted, stop and return to the Plan frontier.

### Validator
- none

## Exclusions
- Do not edit frontend/src/App.tsx or any production CSS.
- Do not perform production adoption, add a route, or begin Stage 3 work.
- Do not edit frontend/.storybook/test-runner.ts, frontend/src/features/app-shell/AppShell.stories.tsx, AppShell.tsx, PageContentBoundary.tsx, frontend/.storybook/main.ts, or frontend/.storybook/preview.tsx.
- Do not add a package, addon, viewport-addon dependency, request-mocking dependency, mock, fixture, or parallel Storybook component.
- Do not add JavaScript resize state, ResizeObserver layout state, custom drawer or focus mechanics, or a react-error-boundary upgrade.
- Do not change the breakpoint contract, weaken required browser assertions, replace real UI interaction with DOM event dispatch or an actionability bypass, run the full suite, or bypass the explicit human pre-adoption gate.

## Escalate if
- The confirmed #storybook-root mount root, Storybook server, or an exact required iframe story id is unavailable.
- The retained Storybook play interaction cannot be synchronized with a real Try again UI click within this spec without DOM-dispatched interaction, an actionability bypass, or a story/configuration change.
- Any declared focused proof command cannot run for the changed scope or required semantics.
- The remaining repair requires a new path, changed semantics, a dependency or addon, a mock or fixture, weakened assertions, production adoption, or wider authorization.

## Canonical compile packet

```json
{
  "output_path": "docs/plans/active/responsive-site-shell/orders/02-prove-and-review-storybook-composition.md",
  "identity": {
    "number": "02",
    "slug": "prove-and-review-storybook-composition",
    "title": "Prove and review Storybook composition",
    "goal": "Prove the complete real-component Storybook composition at every required width and stop for the explicit pre-adoption human gate without changing the production composition."
  },
  "depends_on": [
    "docs/plans/active/responsive-site-shell/orders/01-build-complete-storybook-shell-composition.md"
  ],
  "required_strength": {
    "level": "High",
    "reason": "The order coordinates the verified real-iframe readiness and axe-scope correction with deterministic focus, scrim, and recovery interaction proof across four required viewports and the pre-adoption review gate."
  },
  "authorization": {
    "creates": [],
    "edits": [
      "tests/e2e/responsive-shell-storybook.spec.ts"
    ],
    "removes": []
  },
  "context": [
    {
      "path": "docs/plans/active/responsive-site-shell/responsive-site-shell.md",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "The approved MP-03 Plan records the Stage 2 boundary, acceptance gate, proof contract, exclusions, and escalation conditions."
    },
    {
      "path": "tests/e2e/playwright.config.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Preserve the existing backend, frontend, and Storybook server layout, base URL, headless mode, and reuseExistingServer behavior while running the browser proof."
    },
    {
      "path": "tests/e2e/responsive-shell-storybook.spec.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "The authorized Storybook browser proof whose verified root correction and remaining deterministic focus, scrim, and recovery interactions require the bounded repair."
    },
    {
      "path": "frontend/.storybook/test-runner.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Retained valid Storybook test-runner setup for viewport configuration; it is attempted work and is not authorized for editing."
    },
    {
      "path": "frontend/src/features/app-shell/AppShell.stories.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Retained real-component Storybook stories and passing interaction repairs; they are context only and are not authorized for editing."
    },
    {
      "path": "frontend/src/features/app-shell/AppShell.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Read-only context for the real shell controls, CSS breakpoint, Base UI drawer, accessible names, and portaled drawer behavior."
    },
    {
      "path": "frontend/src/features/app-shell/PageContentBoundary.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Read-only context for the real error-boundary fallback and reset composition covered by the retained Storybook recovery interaction."
    },
    {
      "path": "frontend/.storybook/main.ts",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Read-only Storybook configuration context; preserve the existing Storybook 10 and addon configuration."
    },
    {
      "path": "frontend/.storybook/preview.tsx",
      "scope": {
        "kind": "whole_file"
      },
      "purpose": "Read-only Storybook preview and decorator context; preserve the existing preview behavior."
    }
  ],
  "known_facts": [
    "Stage 1 human acceptance is recorded and the complete real-component Storybook composition is shipped; production frontend/src/App.tsx remains untouched.",
    "The Storybook title is App Shell/AppShell and the relevant CSF ids are app-shell-appshell--wide-healthy, app-shell-appshell--constrained-closed, app-shell-appshell--constrained-open, app-shell-appshell--loading, app-shell-appshell--healthy, app-shell-appshell--unavailable, and app-shell-appshell--unexpected-failure-try-again.",
    "The exact review viewports are 1920x1080, 412x915, 679x915, and 680x915; the native CSS breakpoint is max-width: 679px, so 679px is constrained and 680px is desktop.",
    "The existing Playwright configuration starts backend port 5666, frontend port 8444, and Storybook port 6006 with reuseExistingServer true, baseURL http://localhost:8444, and headless execution; preserve this configuration.",
    "Storybook 10, @storybook/addon-a11y, storybook/test imports, @storybook/test-runner, and @axe-core/playwright are already installed and must be retained; no addon or package is needed.",
    "The existing frontend/.storybook/test-runner.ts provides the retained viewport setup and must not be edited by this order.",
    "The existing AppShell.stories.tsx uses within for in-canvas content and the owner document body for portaled drawer content; the UnexpectedFailureTryAgain play interaction passes and the story file must not be edited by this order.",
    "The real Storybook iframe mount root is #storybook-root; the readiness wait and application-owned axe include scope already use that confirmed selector and must remain aligned.",
    "The browser proof must use the real Storybook iframe and production components, not a mock, fixture, parallel component, or request mock.",
    "Required browser proof covers desktop sidebar at 1920 and 680, constrained trigger and hidden desktop sidebar at 412 and 679, drawer title/close/name, initial Close focus, focus containment, Close/Escape/scrim/Status dismissal, trigger focus restoration, Base UI inertness and scroll behavior, reduced-motion suppression, loading/healthy/unavailable exact copy with role=status or role=alert, Page unavailable exact copy with Try again recovery, and clean application-owned axe checks.",
    "The current focused proof has build-storybook passing, test-storybook passing 20/20, and the responsive Storybook browser spec passing 15/18; the three failures are focus containment after rapid key presses, scrim targeting at x=4 inside the open drawer, and Try again button detachment during the retained Storybook play interaction.",
    "Bounded replays showed that polling focus containment after each key, targeting an exposed right-side scrim point, and synchronizing an immediate real Try again button action each passed 10/10; preserve real UI interaction and do not use DOM event dispatch or an actionability bypass.",
    "Stage 2 is verification-only: do not edit frontend/src/App.tsx, adopt production CSS, begin Stage 3, add a route, add a dependency, or change production behavior."
  ],
  "actions": [
    {
      "kind": "file",
      "paths": [
        "tests/e2e/responsive-shell-storybook.spec.ts"
      ],
      "instruction": "Edit only this Storybook browser spec. Preserve the confirmed #storybook-root readiness wait and the matching #storybook-root axe include scope. Preserve the real iframe URLs and story ids, all four viewport cases, desktop and constrained assertions, drawer modality and every focus/dismissal/inertness/scroll assertion, reduced-motion behavior, exact loading/healthy/unavailable roles and copy, unexpected-failure recovery, and clean application-owned axe checks. In the focus-containment loop, synchronize after each Tab or Shift+Tab until the real active element is inside the dialog, then retain the assertion that it is inside; do not weaken or remove the assertion. For scrim dismissal, activate a visible exposed point on the right-side scrim outside the open 321px drawer at the 412px viewport, retaining dialog-hidden and trigger-focus assertions; use a real Playwright UI interaction. For unexpected-failure recovery, synchronize a real Playwright click on the visible Try again button against the retained Storybook play interaction and possible button detachment, while retaining the exact fallback and recovered-copy assertions; do not use DOM event dispatch, an actionability bypass, mocks, fixtures, or changes to the story. Do not add packages, addons, production edits, or any other path."
    }
  ],
  "proof": [
    {
      "cwd": ".",
      "command": "npm run build-storybook --prefix frontend",
      "purpose": "Build the complete Storybook composition and verify the retained Storybook 10 stories and test-runner-compatible source compile."
    },
    {
      "cwd": ".",
      "command": "npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006",
      "purpose": "Run the Storybook interaction proof, including the retained drawer and unexpected-failure recovery interactions, without introducing another testing addon."
    },
    {
      "cwd": ".",
      "command": ".\\node_modules\\.bin\\playwright.cmd test --config tests\\e2e\\playwright.config.ts tests\\e2e\\responsive-shell-storybook.spec.ts",
      "purpose": "Run the required real-iframe responsive browser proof, modal and focus checks, exact state assertions, reduced-motion checks, and axe checks."
    }
  ],
  "acceptance_handoff": {
    "coordinator": {
      "requirements": [
        "After all three declared focused proof commands pass, review the complete Storybook composition at 1920x1080, 412x915, 679px, and 680px using a stable height for width-edge review.",
        "Confirm that 679px uses the drawer mode and 680px uses the desktop sidebar, with the transition owned by native CSS and no JavaScript layout decision.",
        "Confirm clean application-owned axe results and manually inspect focus order, keyboard operation, initial and restored focus, focus containment, Close/Escape/scrim/Status dismissal, inertness, scroll behavior, reduced motion, contrast, and comprehension.",
        "Confirm that no addon, package, mock, fixture, production App.tsx or CSS adoption, Stage 3 work, DOM-dispatched interaction, actionability bypass, or weakened assertion was introduced.",
        "Record explicit human pre-adoption approval of the complete Storybook composition before authorizing any order that modifies frontend/src/App.tsx; if approval is not granted, stop and return to the Plan frontier."
      ]
    },
    "validator": null
  },
  "exclusions": [
    "Do not edit frontend/src/App.tsx or any production CSS.",
    "Do not perform production adoption, add a route, or begin Stage 3 work.",
    "Do not edit frontend/.storybook/test-runner.ts, frontend/src/features/app-shell/AppShell.stories.tsx, AppShell.tsx, PageContentBoundary.tsx, frontend/.storybook/main.ts, or frontend/.storybook/preview.tsx.",
    "Do not add a package, addon, viewport-addon dependency, request-mocking dependency, mock, fixture, or parallel Storybook component.",
    "Do not add JavaScript resize state, ResizeObserver layout state, custom drawer or focus mechanics, or a react-error-boundary upgrade.",
    "Do not change the breakpoint contract, weaken required browser assertions, replace real UI interaction with DOM event dispatch or an actionability bypass, run the full suite, or bypass the explicit human pre-adoption gate."
  ],
  "escalate_if": [
    "The confirmed #storybook-root mount root, Storybook server, or an exact required iframe story id is unavailable.",
    "The retained Storybook play interaction cannot be synchronized with a real Try again UI click within this spec without DOM-dispatched interaction, an actionability bypass, or a story/configuration change.",
    "Any declared focused proof command cannot run for the changed scope or required semantics.",
    "The remaining repair requires a new path, changed semantics, a dependency or addon, a mock or fixture, weakened assertions, production adoption, or wider authorization."
  ]
}
```
STATUS: DONE

EXECUTOR RESULT:
- DEVIATIONS: none
- PROOF RESULTS: `npm run build-storybook --prefix frontend` PASS ("Storybook build completed successfully", nonfatal Windows libuv teardown assertion); `npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006` PASS (Test Suites: 11 passed, 11 total; Tests: 20 passed, 20 total); Playwright browser spec final PASS "18 passed (19.7s)" after one deterministic in-scope repair (initial run 17 passed / 1 failed).
- DIRTY PATHS: preserved only; deleted docs/design-guides/static-position-to-analysis.md and docs/design-guides/mp02-visual-reference.html; modified docs/grilling-docs/static-position-to-analysis-roadmap.md and docs/master-plans/static-position-to-analysis.md; untracked docs/design-guides/mp03-responsive-shell-reference.html.
- AUTHORIZATION AUDIT: clean; only tests/e2e/responsive-shell-storybook.spec.ts edited; frontend/src/App.tsx, production CSS, AppShell.stories.tsx, AppShell.tsx, PageContentBoundary.tsx, frontend/.storybook/main.ts, frontend/.storybook/preview.tsx, and frontend/.storybook/test-runner.ts unchanged; no package, addon, mock, fixture, or parallel component added.
- ATTEMPTS: 1 deterministic in-scope repair (removed the pre-race retry visibility wait so the real Try again click synchronizes against the retained Storybook play interaction, retaining the recovered-copy assertion).
- ESCALATION: none

VALIDATOR RESULT:
- DEVIATIONS: none
- PROOF RESULTS: independent rerun PASS — `npm run build-storybook --prefix frontend` "Storybook build completed successfully"; `npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006` "Test Suites: 11 passed, 11 total" / "Tests: 20 passed, 20 total"; `./node_modules/.bin/playwright test --config tests/e2e/playwright.config.ts tests/e2e/responsive-shell-storybook.spec.ts` "18 passed (20.9s)".
- DIRTY PATHS: preserved and consistent with baseline via `git status`; no unexpected path.
- AUTHORIZATION AUDIT: clean; the repair and final spec state remain within the order's single authorized path and required synchronization semantics; no production, config, story, package, mock, or weakened-assertion change.
- ATTEMPTS: 0
- ESCALATION: none
