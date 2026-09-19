# Alternative 01: Tournament Console

## Brief

A design direction for competitive club players who treat opening study as match preparation. The surface is dense, fast, and unapologetically digital — like a chess engine interface crossed with a sports dashboard.

## Direction

### Thesis

**"The board is a battlefield; the chrome gets out of the way."**

Everything outside the board is dark and restrained so the position, the evaluation, and the required move read as illuminated information on a console.

### Palette

A near-black field with saturated signal accents. Colors are named by role, not by Material role.

| Token | Value | Role |
|-------|-------|------|
| `--field` | `#0b0c10` | Background behind everything |
| `--panel` | `#111318` | Cards, sidebar, header |
| `--panel-raised` | `#181b22` | Hover/selected surfaces |
| `--ink` | `#e8e9ed` | Primary text |
| `--ink-soft` | `#9ba0ad` | Secondary text |
| `--ink-faint` | `#5c6270` | Tertiary text, dividers |
| `--move` | `#4ef1d4` | Correct / saved move, success |
| `--move-dim` | `#0f3d36` | Success container |
| `--danger` | `#ff5c7f` | Illegal, error, miss |
| `--danger-dim` | `#3d101a` | Error container |
| `--hint` | `#ffd76f` | Warning, retry, review |
| `--hint-dim` | `#3d3316` | Warning container |
| `--accent` | `#8bb6ff` | Links, focus, active nav |
| `--accent-dim` | `#142845` | Primary container |
| `--grid` | `#22262e` | Borders, hairlines |

### Type

The repository's existing **system-ui** stack (defined in `frontend/src/styles/cmt-typescale.css`) is kept unchanged. The console mood is achieved through spacing, color, and weight rather than a monospace face.

| Role | Size | Weight | Use |
|------|------|--------|-----|
| Display | `clamp(2rem, 5vw, 3.5rem)` | 700 | Hero headlines |
| Headline | `1.5rem` | 600 | Page titles |
| Title | `1rem` | 600 | Card titles, move readouts |
| Body | `0.875rem` | 400 | Explanations, labels |
| Caption | `0.75rem` | 500 | Metadata, coordinates |
| Micro | `0.6875rem` | 600 | Tags, badges |

### Structure

- **App shell:** full-width top bar with a compact logo mark, global status dot, and icon-only nav on desktop that expands to text on hover/focus. Mobile keeps a bottom-sheet drawer.
- **Home:** large status readout, a "Start training" primary action, and a compact stat strip (streak, due positions, win rate).
- **Trainer setup:** inline form in a single panel, no sidebar clutter.
- **Trainer session:** board centered in a wide stage, right rail for move cards and session progress, bottom rail for engine/evaluation context.

### Signature

**Glowing move glyphs.** When the user finds the correct move, the move notation and the destination square share a single teal glow (`box-shadow: 0 0 18px var(--move)`). This is the only decorative glow in the UI; everything else stays matte.

### Restraint

- No gradients.
- No rounded corners larger than 8px.
- No illustrations or photos.
- Animations are limited to 120ms fades and a single glow pulse.

## Critique against the brief

- **Audience fit:** Strong for tournament players who already use engines and databases. Might feel cold to casual learners.
- **Single job:** Trainer practice is clearly the hero; repertoire builder becomes secondary.
- **Could it be reused for another product?** The dark-console look is generic. What makes it specific is the move-glow signature, the chess-first layout, and the high-signal color system. Remove those and it is just another dashboard.

## Accessibility notes

- High-contrast text ratios are preserved (light ink on `#111318` exceeds WCAG AA).
- Focus rings use `--accent` at 2px with 2px separation.
- `prefers-reduced-motion` disables glow pulse and fade transitions.
- Forced-colors mode keeps borders via `CanvasText` and drops glow entirely.

## Interface-copy principles

- Buttons say what they do: "Start training session", "Reveal answer", "Retry this position."
- Errors name the problem and the next step: "That move is illegal — pick a legal move."
- Labels use active verbs: "Find the move", "Continue to next position."
