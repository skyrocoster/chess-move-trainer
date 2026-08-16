# Material Design Foundation — reusable visual and feedback language

> **Status:** MP-02 stages 1-9 (provenance and semantic theme tokens; complete Material 3 typescale; spacing, shape, depth, and focus foundations; feedback semantic core and variants; inline feedback; panel feedback; page feedback; combined composition; responsive and accessibility review fixture) shipped and independently validated.

- **Read trigger:** Open when implementing or reviewing MP-02 after accepted MP-01 and before authoring a stage work order.

## What we're building & why

MP-02 establishes the reusable visual and feedback language for Chess Move Trainer. Storybook is the
human-reviewable surface: it will show the accepted dark Material roles, complete system-ui typescale,
foundational geometry/depth/focus specimens, reusable feedback presentations, and one restrained
composition.

The [MP-02 master-plan slice](../../../master-plans/static-position-to-analysis.md) owns the milestone
boundary and dependency direction. The [consolidated grilling record](../../../grilling-docs/static-position-to-analysis-roadmap.md)
owns the detailed accepted decisions. This Plan becomes implementation authority when approved. The
[advisory design guide](../../../design-guides/static-position-to-analysis.md) and its
[visual reference](../../../design-guides/mp02-visual-reference.html) are linked supporting context only;
they are non-canonical, and the visual reference's conceptual colors must not be treated as production
tokens. MP-01's accepted receipt remains at
[verified-technology-foundation](../../done/verified-technology-foundation/verified-technology-foundation.md).

Production `/` remains visually and structurally unchanged throughout MP-02. The temporary MP-01
Foundation Check remains development-only until MP-05.

## Settled decisions

- Use a fixed dark Material 3 scheme with seed `#3F51B5`, Tonal Spot, and standard contrast.
- Obtain the official Web Material Theme Builder CSS export at
  `https://material-foundation.github.io/material-theme-builder/` (verified builder version `2.1.5`),
  using the official Export CSS action. The export is a ZIP containing these exact members:
  `css/light.css`, `css/light-mc.css`, `css/light-hc.css`, `css/dark.css`, `css/dark-mc.css`, and
  `css/dark-hc.css`.
- Preserve the downloaded ZIP and a byte-preserving extraction unchanged under the paths named in the
  compiler handoff. Only `css/dark.css` is imported into Storybook; light and contrast variants remain
  preserved evidence and are not runtime inputs.
- Record provenance in the fixed schema below. The raw export and extracted members are generated
  artifacts; provenance metadata, application tokens, components, stories, and tests are repository-owned.
  No runtime theme generation is used.
- Preserve Material system naming with `--md-sys-*` and namespace application extensions with `--cmt-*`.
- Define the complete 15-role Material 3 system-ui typescale. Do not add external fonts or a monospace role.
- Use balanced density, spacing `4/8/12/16/24/32/48px`, radii `4/8/12px` with `8px` default, tonal
  surfaces and fine borders first, restrained elevation, and a `2px` indigo-primary focus ring with
  `2px` surface separation.
- Define dedicated information, success, warning, and error feedback token sets: accent, on-accent,
  container, and on-container. Do not alias severities directly to primary, secondary, tertiary, or error.
- Use fixed Lucide icons `Info`, `CircleCheck`, `TriangleAlert`, and `CircleX`. Feedback accepts a required
  message and optional heading only: no actions, recovery workflow, arbitrary children, or custom icon API.
- Use one shared semantic core with explicit `InlineFeedback`, `PanelFeedback`, and `PageFeedback` wrappers.
  Consumers explicitly own `role`, `aria-live`, and related live-region semantics; severity never selects
  announcement behavior. Loading is consumer state, not a feedback severity.
- Every implementation stage starts with its intended Storybook story and ends with that story working and
  reviewable. Each stage is independently visible and ordered.
- Review at `1920×1080` and Pixel 8a portrait `412×915`. Do not add screenshot baselines.

### Theme Builder provenance schema

`frontend/src/styles/material/material-theme-provenance.json` must contain this settled schema. Hash values
are populated from the obtained artifact, not invented:

```json
{
  "schemaVersion": 1,
  "generator": {
    "name": "Material Theme Builder",
    "version": "2.1.5",
    "sourceUrl": "https://material-foundation.github.io/material-theme-builder/",
    "repositoryUrl": "https://github.com/material-foundation/material-theme-builder",
    "exportFormat": "web-css-zip",
    "exportAction": "Export CSS"
  },
  "theme": {
    "seed": "#3F51B5",
    "variant": "tonal-spot",
    "contrast": "standard",
    "scheme": "dark"
  },
  "application": {
    "typeface": "system-ui"
  },
  "artifact": {
    "archive": "material-theme-builder-css-export.zip",
    "runtimeMember": "css/dark.css",
    "archiveSha256": "<computed lowercase SHA-256>",
    "runtimeMemberSha256": "<computed lowercase SHA-256>",
    "members": [
      "css/light.css",
      "css/light-mc.css",
      "css/light-hc.css",
      "css/dark.css",
      "css/dark-mc.css",
      "css/dark-hc.css"
    ]
  },
  "ownership": {
    "rawExport": "generated-unmodified",
    "extractedMembers": "generated-byte-preserving",
    "provenanceMetadata": "repository-owned",
    "applicationTokens": "repository-owned",
    "runtimeThemeGeneration": false
  }
}
```

## Stages

1. **SHIPPED — Provenance and semantic theme tokens:** Storybook shows the fixed dark export, provenance,
   namespaces, system roles, and application token ownership.
2. **SHIPPED — Complete Material 3 typescale:** Storybook shows all 15 system-ui typescale roles.
3. **SHIPPED — Spacing, shape, depth, and focus foundations:** Storybook shows the exact density, spacing,
   radius, surface, border, elevation, and focus specimens.
4. **SHIPPED — Feedback semantic core and variants:** Storybook shows all four severity mappings through one
   shared semantic core with fixed icons and dedicated token sets.
5. **SHIPPED — Inline feedback:** Storybook shows the four inline presentations.
6. **SHIPPED — Panel feedback:** Storybook shows the four panel presentations.
7. **SHIPPED — Page feedback:** Storybook shows the four page presentations.
8. **SHIPPED — Combined composition:** Storybook shows one restrained composition using the accepted system.
9. **SHIPPED — Responsive and accessibility review fixture:** Storybook adds a distinct review surface for
   constrained layout, long content, focus, and consumer-owned live semantics.

## Shipped

| Stage | What shipped (≤2 sentences) |
|-------|------------------------------|
| 1 | `DesignSystem/TokenOverview` shows the fixed dark scheme, seed/settings, hash-verified `@material/material-color-utilities` 0.4.0 provenance, `--md-sys-*` roles, and 16 dedicated `--cmt-*` feedback tokens through a `.dark` Storybook preview wrapper. Production `/` remains unchanged and only extracted `css/dark.css` is imported at runtime. |
| 2 | `DesignSystem/CompleteTypescale` shows all 15 Material 3 system-ui typescale roles (display/headline/title/body/label × large/medium/small) through the centralized `--md-sys-typescale-*` variables in `cmt-typescale.css`, with no external fonts or monospace role and production `/` unchanged. |
| 3 | `DesignSystem/Foundations` shows the exact spacing 4/8/12/16/24/32/48 with no intermediate values, radii 4/8/12 with 8px default, tonal surfaces and fine borders, reserved e0-e3 elevation, and the 2px `--md-sys-color-primary` focus ring with 2px separation through centralized `--cmt-*` foundation tokens in `cmt-tokens.css`. Production `/` remains unchanged. |
| 4 | `Feedback/SemanticVariants` shows information/success/warning/error through one shared `FeedbackCore` with fixed decorative Lucide icons and dedicated `--cmt-*` feedback tokens on a dark story backdrop; required message and optional heading, consumer-supplied live-region attributes forwarded without defaults, no actions/children/custom icon, and production `/` unchanged. |
| 5 | `Feedback/InlineMatrix` shows all four inline presentations through the thin `InlineFeedback` wrapper reusing the shipped `FeedbackCore` and fixed decorative Lucide icons with dedicated `--cmt-*` accent tokens in a compact transparent/border-first treatment; required message and optional heading, consumer-supplied live-region attributes forwarded without defaults, and production `/` unchanged. |
| 6 | `Feedback/PanelMatrix` shows all four filled panel presentations through the thin `PanelFeedback` wrapper reusing the shipped `FeedbackCore` and fixed decorative Lucide icons with dedicated `--cmt-*` container/on-container tokens owning the filled surface and severity accent as a visual cue only; required message and optional heading, no new props, no default role/aria-live, and production `/` unchanged. |
| 7 | `Feedback/PageMatrix` shows all four page-level presentations through the thin `PageFeedback` wrapper reusing the shipped `FeedbackCore` and fixed decorative Lucide icons; the page treatment uses the accepted tonal surface with the severity accent as a visual cue only, no alert/status assignment, no new props, no default role/aria-live, consumer-supplied live-region attributes forwarded as-is, and production `/` unchanged. |
| 8 | `Composition/TournamentAnalysisDesk` shows one restrained surface combining the accepted typescale heading region, tonal surfaces with fine borders, one reserved elevation level, and exactly one `PanelFeedback`-backed feedback presentation through the shipped `FeedbackCore`. It reuses only centralized `--md-sys-typescale-*` and `--cmt-*` tokens without duplicate definitions, is Storybook-only with production `/` unchanged, and contains no board, shell, score rail, evaluation strip, actions, or speculative copy. |
| 9 | `Acceptance/ResponsiveAccessibilityReview` is a distinct review fixture (not a duplicate of the combined composition) placing inline, panel, and page presentations plus FoundationSpecimen-style focus specimens in a constrained review container, showing long-message wrapping, no-heading content, and explicit consumer-owned `role`/`aria-live` forwarded without wrapper defaults; verified at 1920×1080 and 412×915 portrait via the verification-only Playwright spec (axe, wrapping, focus), with production `/` unchanged. |

## Touches

- `frontend/.storybook/main.ts`
- `frontend/.storybook/preview.tsx`
- `frontend/src/**` — implementation ownership is limited to the exact material, token, and design-system
  paths in the compiler handoff; production and Foundation paths listed under exclusions are regression-only.
- **Depends on:** [Verified Technology Foundation](../../done/verified-technology-foundation/verified-technology-foundation.md)

## Verification-only paths

The following path is not unconditional Plan ownership. A stage order may add it only when its browser proof
is required and the order explicitly authorizes it:

- `tests/e2e/design-system-accessibility.spec.ts`

Existing status tests and the existing Foundation accessibility spec remain regression evidence and are not
implementation targets.

## Acceptance

At every stage, the executor first adds the named Storybook story and its focused expectation, observes the
expected red proof where applicable, implements only the stage's owning symbols, and finishes with the same
story and focused proof green. A reviewer then accepts that stage's **User can see** result before the next
ordered stage begins.

Final acceptance requires:

1. Review all nine Storybook stages at `1920×1080`.
2. Review the responsive acceptance fixture at `412×915` portrait.
3. Confirm all four severities across inline, panel, and page presentations.
4. Confirm required message, optional heading, fixed decorative icons, no actions, and no custom icon API.
5. Confirm no feedback wrapper supplies default `role` or `aria-live`; explicit consumer semantics remain
   visible in the acceptance fixture.
6. Verify rendered foreground/background pairs and focus treatment against WCAG 2.2 AA manually in addition
   to automated axe results.
7. Confirm no loading, cancellation, recovery, empty-message, shell, route, board, chess, data, engine,
   persistence, light-theme, or theme-switcher behavior appears. Loading/cancellation are not MP-02 feedback
   states and are intentionally absent.
8. Confirm production `/` remains visually and structurally unchanged and the Foundation Check remains
   temporary.

## Exclusions

- Any production `/` restyling, shell, routing, board, chess, data, engine, persistence, or product adoption.
- Light theme, theme switcher, runtime theme generation, external fonts, and monospace typescale.
- Score-sheet rails, evaluation strips, fake analysis, speculative structural motifs, fake content, and
  inactive future controls.
- Feedback actions, recovery workflows, notifications, logging, persistence, arbitrary children, and custom
  icons.
- Automatic live-region behavior selected from severity.
- Foundation Check promotion or removal; MP-05 owns its retirement.
- Screenshot baselines or an external visual-regression service.
- Changes to unrelated worktree files or to existing production/status/Foundation regression tests.

## Automated gates

Stage-focused commands are run from the repository root in PowerShell/Windows layout:

```powershell
npm run test --prefix frontend -- --run src/features/design-system/themeProvenance.test.ts
npm run test --prefix frontend -- --run src/features/design-system/TypescaleSpecimen.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/FoundationSpecimen.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/feedback/FeedbackCore.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/feedback/InlineFeedback.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/feedback/PanelFeedback.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/feedback/PageFeedback.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/CombinedComposition.test.tsx
npm run test --prefix frontend -- --run src/features/design-system/AccessibilityReview.test.tsx
```

Storybook and browser proof use the verified existing scripts and server layout:

```powershell
npm run build-storybook --prefix frontend
npm run storybook --prefix frontend
npm run test-storybook --prefix frontend -- --url http://127.0.0.1:6006
.\node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts tests\e2e\design-system-accessibility.spec.ts
```

The Playwright configuration already starts the backend, frontend, and Storybook servers. The standalone
Storybook test-runner command requires the Storybook command to be running first.

Verified quality and final regression commands are:

```powershell
npm run lint --prefix frontend
npm run build --prefix frontend
.\frontend\node_modules\.bin\prettier.cmd --check frontend
.\.venv\Scripts\python.exe scripts\check_docs.py --check
powershell -ExecutionPolicy Bypass -File .\check.ps1
```

## Compiler handoff

### Stage 1 — provenance and semantic theme tokens

- **Dependency:** Accepted MP-01 at `docs/plans/done/verified-technology-foundation/verified-technology-foundation.md`.
- **User can see:** `DesignSystem/TokenOverview` shows the fixed dark scheme, seed/settings, raw-export
  provenance, `--md-sys-*` roles, `--cmt-*` application tokens, and dedicated feedback-token ownership.
- **Story-first path:** `frontend/src/features/design-system/TokenOverview.stories.tsx` must be created before
  implementation. The component owner is `frontend/src/features/design-system/TokenOverview.tsx`; its focused
  test is `TokenOverview.test.tsx` and the artifact contract test is `themeProvenance.test.ts`.
- **Exact token paths:**
  `frontend/src/styles/material/material-theme-builder-css-export.zip`;
  `frontend/src/styles/material/material-theme-builder-css-export/css/{light.css,light-mc.css,light-hc.css,dark.css,dark-mc.css,dark-hc.css}`;
  `frontend/src/styles/material/material-theme-provenance.json`;
  `frontend/src/styles/cmt-tokens.css`.
- **Obtaining flow:** Use the official deployed builder, set seed `#3F51B5`, Tonal Spot, standard contrast,
  and dark scheme, choose the official CSS export, download the ZIP, preserve it unchanged, extract the six
  named members byte-for-byte, compute the two SHA-256 values, and populate the fixed metadata schema.
  Never recreate the export from the advisory HTML or handwrite generated color values.
- **Generated/owned boundary:** Raw ZIP and extracted CSS are generated-unmodified; provenance metadata,
  `cmt-tokens.css`, components, stories, and tests are repository-owned. Storybook imports only extracted
  `css/dark.css` inside a `.dark` preview wrapper. Production entrypoints do not import these files.
- **State flow:** Static CSS and metadata → Storybook preview/theme wrapper → token overview and future
  design-system components. No runtime generator, theme switch, or React theme state exists.
- **Focused proof:** `themeProvenance.test.ts` validates the schema, exact six archive members, hashes, `.dark`
  selector, `--md-sys-color-*` output, and dark-only runtime import. Run the Stage 1 Vitest command, then
  `npm run build-storybook --prefix frontend`.
- **Human gate:** Confirm provenance is honest, raw output is unmodified, and no conceptual reference color
  has become official output.
- **Stop condition:** Stop with token overview and fixed dark token source reviewable; do not begin typescale
  or feedback components in the same stage.
- **Exclusions:** No production import, light theme behavior, runtime generation, shell, board, or feedback UI.
- **Open questions:** none.

### Stage 2 — complete Material 3 typescale

- **Dependency:** Stage 1 accepted.
- **User can see:** `DesignSystem/CompleteTypescale` shows display large/medium/small, headline large/medium/small,
  title large/medium/small, body large/medium/small, and label large/medium/small.
- **Story-first path:** `frontend/src/features/design-system/TypescaleSpecimen.stories.tsx` first; owner
  `TypescaleSpecimen.tsx`, CSS Module within the same feature path, and `TypescaleSpecimen.test.tsx`.
- **State flow:** Centralized `--md-sys-typescale-*` semantic variables → specimen roles; no local ad hoc
  font declarations, fetched fonts, or component state.
- **Settled values:** system-ui stack; complete family, size, line-height, weight, and letter-spacing roles;
  no monospace role.
- **Focused proof:** Stage 2 Vitest command must enumerate all 15 roles and assert the system-ui contract;
  Storybook build remains green.
- **Human gate:** Confirm all roles are visible and hierarchy remains legible at both review sizes.
- **Stop condition:** Stop with the complete typescale story working; do not add geometry or feedback.
- **Exclusions:** No notation role, external font request, shell, route, or production styling.
- **Open questions:** none.

### Stage 3 — spacing, shape, depth, and focus foundations

- **Dependency:** Stage 2 accepted.
- **User can see:** `DesignSystem/Foundations` shows balanced density, spacing `4/8/12/16/24/32/48`, radii
  `4/8/12`, tonal surfaces, fine borders, reserved elevation, and the focus ring.
- **Story-first path:** `FoundationSpecimen.stories.tsx` first; owner `FoundationSpecimen.tsx`, bounded CSS
  Module, and `FoundationSpecimen.test.tsx`.
- **State flow:** `cmt-tokens.css` values → static specimen classes; a real focusable specimen is focused by
  the Storybook play function only to prove the focus treatment.
- **Settled depth:** `e0` none; subtle `e1/e2/e3` shadows only for major/floating emphasis. Borders and tonal
  surfaces carry normal structure.
- **Focused proof:** Stage 3 Vitest command plus Storybook play interaction; verify no intermediate spacing
  tokens and no focus regression.
- **Human gate:** Confirm exact scale values, restrained shape, border-first depth, and focus visibility.
- **Stop condition:** Stop with foundational specimens independently reviewable.
- **Exclusions:** No feedback semantics, product controls, shell, or route adoption.
- **Open questions:** none.

### Stage 4 — feedback semantic core and variants

- **Dependency:** Stage 3 accepted.
- **User can see:** `Feedback/SemanticVariants` shows information, success, warning, and error mappings.
- **Story-first path:** `frontend/src/features/design-system/feedback/SemanticVariants.stories.tsx` first;
  owners are `feedbackTypes.ts`, `FeedbackCore.tsx`, bounded feedback styles, and `FeedbackCore.test.tsx`.
- **Exact symbols:** `FeedbackSeverity = "information" | "success" | "warning" | "error"`; `FeedbackProps`
  contains `severity`, required `message`, optional `heading`, and explicit consumer-supplied live-region
  attributes. `FEEDBACK_VARIANTS` maps each severity to one fixed Lucide icon and dedicated token names.
- **State flow:** Consumer props → static variant map → decorative icon plus shared heading/message structure;
  there is no internal state, effect, action, child composition, loading severity, or automatic `role`/`aria-live`.
- **Focused proof:** Stage 4 Vitest command asserts all four variants, fixed icon mapping, required/optional
  content, dedicated token usage, and absence of actions/custom icon/children.
- **Human gate:** Confirm the semantic core is shared and the four severities are individually legible.
- **Stop condition:** Stop with the core and variant matrix reviewable; do not implement presentation wrappers
  in this stage.
- **Exclusions:** No notifications, recovery, live-region defaults, or product consumer.
- **Open questions:** none.

### Stage 5 — inline feedback

- **Dependency:** Stage 4 accepted.
- **User can see:** `Feedback/InlineMatrix` shows all four inline presentations.
- **Story-first path:** `InlineFeedback.stories.tsx` first; owner `InlineFeedback.tsx`, its CSS Module, and
  `InlineFeedback.test.tsx` under `frontend/src/features/design-system/feedback/`.
- **State flow:** `FeedbackProps` → `InlineFeedback` → `FeedbackCore`; transparent/border-first presentation
  consumes accent tokens and does not change semantic attributes.
- **Focused proof:** Stage 5 Vitest command asserts all severities, optional heading, required message, fixed
  icon, no actions, and no default live-region semantics.
- **Human gate:** Confirm inline treatment is compact, readable, and distinct from panel/page treatment.
- **Stop condition:** Stop with the inline matrix story complete and reviewable.
- **Exclusions:** No panel/page layout, shell, or consumer-owned workflow.
- **Open questions:** none.

### Stage 6 — panel feedback

- **Dependency:** Stage 5 accepted.
- **User can see:** `Feedback/PanelMatrix` shows all four filled panel presentations.
- **Story-first path:** `PanelFeedback.stories.tsx` first; owner `PanelFeedback.tsx`, its CSS Module, and
  `PanelFeedback.test.tsx`.
- **State flow:** Same `FeedbackProps` → `PanelFeedback` → `FeedbackCore`; container/on-container tokens own
  the filled surface and severity accent remains a visual cue only.
- **Focused proof:** Stage 6 Vitest command asserts semantic sharing, all four containers, content contract,
  and no automatic announcement role.
- **Human gate:** Confirm panel hierarchy and contrast are distinct from inline feedback.
- **Stop condition:** Stop with the panel matrix story complete and reviewable.
- **Exclusions:** No page-level structure, actions, or consumer state machine.
- **Open questions:** none.

### Stage 7 — page feedback

- **Dependency:** Stage 6 accepted.
- **User can see:** `Feedback/PageMatrix` shows all four page-level presentations.
- **Story-first path:** `PageFeedback.stories.tsx` first; owner `PageFeedback.tsx`, its CSS Module, and
  `PageFeedback.test.tsx`.
- **State flow:** Same `FeedbackProps` → `PageFeedback` → `FeedbackCore`; page treatment uses the accepted
  surface and severity accent without assigning `alert` or `status`.
- **Focused proof:** Stage 7 Vitest command asserts all page variants, content semantics, fixed icons, and
  consumer-owned live behavior.
- **Human gate:** Confirm page presentation is structurally distinct, responsive, and not a notification system.
- **Stop condition:** Stop with page feedback independently reviewable.
- **Exclusions:** No shell, routing, notification delivery, recovery, or production adoption.
- **Open questions:** none.

### Stage 8 — combined composition

- **Dependency:** Stage 7 accepted.
- **User can see:** `Composition/TournamentAnalysisDesk` combines accepted typescale, geometry, surfaces,
  borders, one reserved elevation level, and one feedback presentation.
- **Story-first path:** `CombinedComposition.stories.tsx` first; owner `CombinedComposition.tsx`, bounded CSS
  Module, and `CombinedComposition.test.tsx`.
- **State flow:** Existing token and feedback components compose without duplicate token definitions, fake data,
  or product routing.
- **Focused proof:** Stage 8 Vitest command asserts composition landmarks and absence of board, shell, score rail,
  evaluation strip, actions, and speculative copy.
- **Human gate:** Confirm coherence without mistaking the composition for production UI.
- **Stop condition:** Stop with the accepted combined composition reviewable; do not treat it as final responsive
  or accessibility acceptance.
- **Exclusions:** No production consumer, shell, board, route, or fake analytical content.
- **Open questions:** none.

### Stage 9 — responsive and accessibility review fixture

- **Dependency:** Stage 8 accepted.
- **User can see:** `Acceptance/ResponsiveAccessibilityReview` is a distinct Storybook fixture, not a duplicate
  of the combined composition. It places all presentation levels in a constrained review container and shows
  long-message wrapping, no-heading content, explicit consumer-owned live semantics, and focus specimens.
- **Story-first path:** `AccessibilityReview.stories.tsx` first; owner `AccessibilityReview.tsx`, bounded CSS
  Module, and `AccessibilityReview.test.tsx`.
- **State flow:** Review fixture → existing token/feedback components; explicit wrapper attributes demonstrate
  consumer-owned `role`/`aria-live`. The fixture is Storybook-only and is not exported as product UI.
- **Focused proof:** Stage 9 Vitest command; Storybook test-runner against `http://127.0.0.1:6006`; and the
  conditional verification-only `tests/e2e/design-system-accessibility.spec.ts` using the existing Playwright
  configuration. Browser proof checks both `1920×1080` and `412×915`, axe, wrapping, focus, and contrast-relevant
  rendered states.
- **Human gate:** Confirm responsive layout, keyboard focus, contrast, long content, omitted heading, and live
  semantics at both target sizes. Automated axe is supplemental, not the human WCAG decision.
- **Stop condition:** Stop when the complete MP-02 Storybook review surface is accepted. Do not begin MP-03.
- **Exclusions:** No screenshot baselines, production adoption, shell, routing, board, or new reusable product API.
- **Open questions:** none.
