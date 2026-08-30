# Chess Move Trainer — Design Intent

A working design document. It records *why* the frontend looks and behaves the way it
does, and the tensions worth resolving before this becomes the basis for frontend/UX
skills. It is intentionally about intent, not a token dump — but every claim is anchored
to the source that proves it so the reasoning can be checked.

> Status: draft for iteration. The product is named a "trainer" but the built UI is
> currently a **study instrument** (position viewer + repertoire builder). The design
> system is being built *ahead* of the drill feature it implies. That gap shapes much of
> what follows.

---

## 1. The governing idea: a workbench, not an arcade

Everything else below is a consequence of one stance:

**This is a tool for thinking about chess, not a game to be played in the UI.**

Evidence of the stance:
- Dark-only runtime theme (`src/app.css:1` imports `dark.css`; no `prefers-color-scheme`,
  no toggle, `src/styles/material/material-theme-provenance.json` sets
  `"runtimeThemeGeneration": false`).
- Flat surfaces, zero gradients anywhere in the source (scout: "no `linear-gradient`…
  all surfaces are flat solid colors").
- Board piece animation explicitly disabled (`InteractiveBoardAdapter.tsx:198,207`:
  `animationDurationInMs: 0`, `showAnimations: false`).
- Feedback is inline and persistent, never a toast that vanishes (Section 6).
- No scoring, no timer, no celebration animation — no "game" feedback loops exist.

Reasoning: a study tool is used in long, focused sessions. Dark reduces eye fatigue;
flat removes visual noise; stillness keeps attention on the position. The product is
competing for the user's *concentration*, not their *dopamine*, so restraint is the brand.

---

## 2. Two visual contracts: the board is neutral, the chrome is branded

The single most important design decision is that the **chessboard and the application
chrome are styled by two different philosophies**, and that split is deliberate.

### 2a. The board keeps its own, timeless identity
- Square colors are the `react-chessboard` defaults — light `#f0d9b5` (cream), dark
  `#b58863` (walnut). The app passes **no** `lightSquareStyle`/`darkSquareStyle`
  (`BoardAdapter.tsx:111-119`, `InteractiveBoardAdapter.tsx:195-209`).
- Piece set is the library default SVG; no `customPieces`, no `pieceTheme`
  (`InteractiveBoardAdapter.tsx:13` imports `defaultPieces` untouched).
- Last-move highlight is a hardcoded translucent yellow `rgba(250,204,21,0.42)` with a
  brown inset ring `rgba(146,94,0,0.42)` (`src/features/board-adapter/lastMove.ts:9-12`).

Reasoning: a chessboard has a **visual contract older than any app**. Wooden tan/brown
squares and standard pieces are instantly legible to every player and carry zero learning
cost. Re-skinning the board in brand indigo would subordinate the object of study to the
chrome. The board is the *subject*; the UI is the *frame*. The frame may be branded; the
subject must stay recognizable.

The hardcoded rgba for the last-move highlight is the one place this philosophy is
inconsistent (Section 8) — it should be a token, but the *intent* (board-local color that
reads as "this square moved") is sound.

### 2b. The chrome is a Material Design 3, indigo-dark identity
- Theme generated from seed `#3F51B5` (Indigo 500), variant `tonal-spot`, scheme `dark`
  (`src/styles/material/material-theme-provenance.json:12`).
- Indigo is a calm, "intellectual" hue — appropriate for a thinking tool, and distinct
  from the red/blue/green urgency of typical game UIs.
- All chrome color flows through `--md-sys-color-*` roles; components never hardcode
  Material values.

Reasoning: MD3 gives a coherent, accessible role system (primary/secondary/tertiary,
surface tiers, outline) for free, so the team spends its creativity on *layout and
feedback* rather than re-deriving a color system. Indigo-dark is the chosen emotional
register: focused, quiet, serious.

---

## 3. Tokens own meaning — and feedback meaning is walled off from theme

There are two token layers, and the boundary between them is a principle, not an accident.

- **`--md-sys-*`** — Material roles for chrome (`dark.css`).
- **`--cmt-*`** — repository-owned design tokens (`src/styles/cmt-tokens.css`): spacing,
  radius, elevation, focus ring, and four **severity** colors (info/success/warning/error).

The severity tokens are **deliberately not aliases** of Material roles. The file states
this inline (`cmt-tokens.css:5-8`): severity mapping must never follow a Material role
change. Concretely, `--cmt-success-accent` (`#8fd49b`) is independent of
`--md-sys-color-tertiary` (`#e6bad7`), even though both are "nice greens/pinks."

Reasoning: **meaning must not drift with theme.** If "success" were just "primary," then
reshading the theme could silently turn a pass into a brand color and a fail into another
brand color, destroying the red/green/amber language users rely on. Severity is a
semantic contract; theme is a cosmetic one. Keeping them separate is why the app can
later flip to light mode (Section 8) without breaking "correct vs wrong."

---

## 4. The team owns every pixel: headless primitives + CSS Modules

The UI is built on **Base UI** headless primitives (`@base-ui/react`) wrapped in custom
components, styled only with **CSS Modules** (`*.module.css`). No MUI, Radix-shadcn,
Chakra, or Ant. No Tailwind utility classes. No global CSS except the reset and tokens.

Evidence: `Button.tsx` wraps `@base-ui/react/button`; `Disclosure` wraps Collapsible;
`CalendarDate` wraps Popover; `EvalBar` wraps Meter; `PreferredMovePanel` wraps
AlertDialog (`src/features/design-system/**`).

Reasoning:
- **Headless** = the library supplies behavior and a11y wiring, the team supplies the
  entire visual language. No imported visual opinions to fight.
- **CSS Modules** = scoped, readable, token-driven plain CSS. The repo explicitly rejects
  utility-class soup in favor of named, semantic classes (`.shell`, `.header`,
  `.workspace`). This makes the design system *legible as code* — a future skill can read
  a component and know the rules.
- The discipline is enforced structurally: every spacing value is one of
  `--cmt-spacing-4/8/12/16/24/32/48` ("no intermediate values",
  `cmt-tokens.css:44-51`), radii are 4/8/12, elevation is e0–e3.

Reasoning in one line: **the design system is the product, not a dependency.** Building
it by hand is slower but means a future frontend/UX skill has a single, coherent, owned
source of truth to learn from.

---

## 5. Typography: invisible on purpose

The only typeface is `system-ui` (`app.css:6`, `cmt-typescale.css:4-8`). No web font,
no `@font-face`, no Roboto, no monospace role. The full 15-role Material typescale is
used, but every role's `-font` is `system-ui`.

Reasoning:
- **Zero load cost, zero FOUT.** A study tool opens fast and stays native to the OS.
- Identity comes from color and layout, not a custom face. The product does not need a
  "designed" typeface to feel intentional.
- Using MD3's *typographic rhythm* (size/weight/line-height roles) without MD3's *font*
  keeps hierarchy disciplined while staying platform-native.

The one exception is glyph-only: `PromotionPicker.module.css:119` uses
`"Noto Sans Symbols 2"` solely to render piece Unicode glyphs (♕♖♗♘) — text, not chrome.

---

## 6. Feedback is positional and persistent, never a toast

There is **no toast/snackbar library**. Feedback lives in document flow at the point of
concern, via three wrappers over one `FeedbackCore` (`src/features/design-system/feedback/`):
`InlineFeedback`, `PanelFeedback`, `PageFeedback`. Live regions are used throughout —
`role="status" aria-live="polite"` for non-blocking state, `role="alert"
aria-live="assertive"` for errors (`GameLoader.tsx`, `AnalysisPanel.tsx`,
`PreferredMovePanel.tsx`).

Reasoning: a learning tool must not let a message disappear before the user has read it.
A transient toast trains the user to *dismiss* feedback; an inline, source-anchored
message trains them to *read* it. Calm and non-interruptive is the point. The four
severities map to lucide icons + the walled-off `--cmt-*` colors (Section 3).

Note the forward-looking gap: these severity tokens and components exist, but the board
does **not yet** color a move correct/incorrect, because the drill feature that would use
them is not built. The design system is ready; the behavior is not.

---

## 7. Motion is functional, sparse, and opt-out

- No animation library; all motion is CSS `transition` at ~120–180ms. Zero `@keyframes`.
- Motion appears only where it *reveals or changes state*: drawer slide, eval-bar fill,
  disclosure chevron, promotion drawer.
- `prefers-reduced-motion: reduce` is honored in eight modules; board transitions are
  force-disabled for it (`InteractiveBoardAdapter.module.css:113-118`, and seven others).
- The board itself does not animate pieces at all (Section 1).

Reasoning: motion should *explain*, never *decorate*. In a study tool, a sliding piece is
a distraction from the resulting position; a filling eval bar *is* information. Restraint
is also an accessibility and performance stance — the app stays calm for sensitive users
and cheap to run.

---

## 8. Open tensions to resolve while iterating

These are the places where the *intent* is clear but the *implementation* has drifted or
is unfinished. They are the most valuable things to decide before writing frontend/UX
skills, because a skill will codify whichever answer you pick.

**The systemic rule that resolves all five.** No visual value — color, duration, radius,
spacing, or shadow — may ever appear as a literal in component code or inline style. Every
value is a named token in `cmt-tokens.css` (or a `--md-sys-*` role), *even if that token is
used exactly once*. Single-use tokens are mandatory, not wasteful: they corner the
designing AI into a conscious choice — reuse an existing token, or mint a new one — instead
of silently hardcoding a hex. A library default is permitted only when we have explicitly
declared a token equal to it, so "we use the default" becomes a recorded decision rather
than an accident. Where the source currently breaks this rule (the `lastMove.ts` rgba, the
undefined motion token), the resolutions below close the gap and turn the fixes into the
seed of a consistent, learnable design language.

1. **Dark-only vs generated light/contrast themes.** Light, medium-contrast, and
   high-contrast MD3 files exist but are never imported (`dark.css` is the only runtime
   theme). Is dark a deliberate product stance (long study sessions) or an MVP shortcut?
   If deliberate, say so — it justifies the whole emotional register. If not, the
   severity tokens (Section 3) are exactly what makes a safe later flip possible.

   **Advised resolution.** Treat dark as a deliberate, documented product stance *and* keep
   the escape hatch real. Because every chrome color already flows through `--md-sys-*` /
   `--cmt-*` tokens, a later flip is already safe — but make it concrete: add a `theme`
   switch (a `data-theme` attribute or a swapped scheme import) and assert in review that
   no component references a raw color literal (the systemic rule above guarantees this).
   If dark-only is declared permanent, state it here so the severity tokens' isolation
   (Section 3) is read as the *reason* a future light mode stays safe, not as unfinished
   work.

2. **Board colors are not tokenized.** The last-move rgba
   (`lastMove.ts:9-12`) and the default square colors are hardcoded, which contradicts the
   token-owns-meaning principle (Section 3). Decide: keep the board explicitly *outside*
   the token system (board is a neutral subject — defensible), or bring it in. A skill
   needs one rule.

   **Advised resolution — the clearest test of the systemic rule.** Replace the inline
   `rgba(...)` in `lastMove.ts:9-12` with two board-local tokens, e.g.
   `--cmt-board-last-move-surface: rgba(250,204,21,0.42)` and
   `--cmt-board-last-move-ring: rgba(146,94,0,0.42)`, declared once in `cmt-tokens.css`.
   Minting them forces the question: is this yellow a one-off, or should it reuse an
   existing accent? (It is board-local and intentionally *not* a severity color, so a new
   token is correct — but the AI had to decide.) Extend the same discipline to the squares:
   declare `--cmt-board-light-square` / `--cmt-board-dark-square` set to the conventional
   `#f0d9b5` / `#b58863` *by decision*, so "the board uses library defaults" is a recorded
   token, not an omission. No `style={{...}}` literals anywhere.

3. **`--cmt-motion-duration-short` is referenced but undefined**
   (`Disclosure.module.css:43`, `MoveHistory.module.css:96-97`). Either define it (likely
   `140ms`) or delete the references. Small, but a skill that cites "the motion token"
   must find it.

   **Advised resolution.** Define a motion-duration scale in `cmt-tokens.css` —
   `--cmt-motion-duration-short` (140ms), plus `--cmt-motion-duration-medium` (180ms) and
   `--cmt-motion-duration-long` — and route every `transition: … <time>` through it. Banish
   raw `ms` from transitions: the eval bar's `180ms`, the drawer's `180ms`, and the
   chevron's currently-undefined token all become token references. This turns the missing
   token from a bug into the seed of a consistent motion language a skill can cite.

4. **No custom board theming despite a bespoke chrome.** The board looks like stock
   `react-chessboard` while everything around it is hand-built. This reads as *intent*
   (neutral subject) but could read as *unfinished*. The doc should state the rule so it
   is not "accidentally" restyled later.

   **Advised resolution.** Codify the exception as a token-backed rule, not a vibe: the
   board is *intentionally* outside brand theming, expressed by the `--cmt-board-*` tokens
   from tension 2 equaling conventional chess colors. A future skill then treats any new
   `--cmt-board-*` token as a conscious, reviewed decision; restyling the board to match
   brand indigo requires explicitly overriding those tokens plus a product sign-off. The
   neutral board is thus a *documented* choice, immune to accidental reskinning.

5. **Drill feedback is designed-for but not built.** Correct/incorrect, hints, and
   scoring colors/animations do not exist on the board yet. The severity system is the
   obvious home for them. When you build the trainer, the intent here says: route move
   outcome through `--cmt-success/error-*`, keep it inline/persistent (Section 6), and do
   **not** add celebratory animation (Section 7).

   **Advised resolution.** When the trainer is built, the systemic rule already points the
   way: move outcomes reuse the existing severity tokens (`--cmt-success-accent`,
   `--cmt-error-accent`) for any chrome/feedback, and any *board-local* treatment (e.g. a
   correct/incorrect square ring) becomes a new `--cmt-board-*` token — never an inline
   style. Do not mint separate "training" colors; if the severity palette suffices (it
   should), the AI reuses it and the decision is recorded. Keep feedback inline/persistent
   (Section 6) and add no celebratory keyframes (Section 7). The severity system was built
   ahead of the drill precisely so this step needs no new color thinking — only token
   discipline.

---

## 9. One-paragraph summary (the "why" in brief)

Chess Move Trainer is a quiet, dark workbench for studying chess, not playing it in the
UI. Its chrome is a deliberately branded Material Design 3 indigo-dark system the team
owns line-by-line through headless Base UI primitives and scoped CSS Modules, while the
chessboard is left as a neutral, timeless wooden object so attention stays on the
position. Meaning is encoded in tokens that are walled off from cosmetic theme changes,
feedback is shown inline and persists instead of popping and vanishing, motion is rare and
explanatory, and the whole surface is built accessible-first — because the user is here to
think, and the design's only job is to get out of the way.

---

*Anchored to source via scouts (color/theming, component/layout, board/viz,
typography/motion/UX). File:line references are for verification, not prescription.*
