# Static Position to Analysis — Advisory Design Guide

**Recorded:** 2026-08-16  
**Status:** Accepted advisory guidance for MP-02 planning  
**Implementation authority:** None  
**Canonical status:** Non-canonical

## Purpose and ownership

This guide preserves the visual and reusable-feedback decisions accepted while grilling MP-02 of the
[Static Position to Analysis Workspace master plan](../master-plans/static-position-to-analysis.md).
It exists to help the future MP-02 focused Plan and may provide continuity if the user deliberately
chooses to consult it during later milestones.

This guide is not a source contract, focused Plan, work order, or implementation authorization. It does
not override the master plan, a focused Plan, an official Material Theme Builder export, or implemented
source. Only the future MP-02 focused Plan is currently required to link to it. The user will decide
whether later work should reuse, revise, or retire this guidance; there is no automatic maintenance rule.

The accepted static [MP-02 visual reference](mp02-visual-reference.html) illustrates these decisions. Its
palette values are conceptual, not an official Theme Builder export or production tokens.

## MP-02 outcome

MP-02 establishes the reusable visual and feedback language for Chess Move Trainer. Its human-reviewable
surface is Storybook. It does not restyle or adopt the new system on production `/`, add the site shell or
production routing, or begin board, chess-data, interaction, analysis, or persistence behavior.

## Visual thesis

The selected direction is **Tournament analysis desk**: a restrained, precise, reading-first dark
workspace. It should feel suitable for careful chess study without imitating a chessboard, score sheet,
or engine console.

The design deliberately avoids a signature structural motif in MP-02. In particular, it does not create
a score-sheet rail, evaluation strip, notation register, fake analytical content, or other component
without a real consumer. Distinctiveness comes from the accepted palette, disciplined typography,
balanced density, restrained shapes, border-first depth, and coherent feedback treatment.

## Color system and provenance

- Use a fixed dark Material Design 3 scheme.
- Use source seed `#3F51B5`.
- Use the **Tonal Spot** variant at **standard contrast**.
- Preserve the official Material Theme Builder export unchanged when MP-02 produces it.
- Record the seed, variant, contrast level, and generation settings separately so the export can be
  reproduced.
- Keep application-owned semantic token CSS separate from generated output.
- Preserve Material naming for exported/system roles with `--md-sys-*` variables.
- Namespace Chess Move Trainer extensions with `--cmt-*`.
- Do not generate the fixed theme at runtime.
- Do not add a light theme, theme switcher, external font request, or runtime theme control.

The official export does not prove accessibility by itself. Every rendered foreground/background pair,
focus treatment, feedback pair, and relevant state must be checked against the WCAG 2.2 Level AA
acceptance target. “High contrast” means reliably legible hierarchy, not maximum contrast on every
surface.

### Feedback color ownership

Information, success, warning, and error each receive dedicated semantic token pairs rather than being
direct aliases of primary, secondary, tertiary, and error roles. Each severity needs:

- an accent/color role;
- an on-color role where the implementation uses a filled accent;
- a container role; and
- an on-container role.

These pairs must be individually contrast-verified. Text and iconography must preserve meaning without
depending on color alone.

## Typography

- Define the complete Material 3 role set: display, headline, title, body, and label at all standard
  sizes.
- Use the native `system-ui` stack.
- Centralize family, size, line height, weight, and letter spacing as semantic typescale variables.
- Do not download Google Fonts or add a font asset merely to obtain Roboto.
- Do not add a monospace notation/data role in MP-02. A later milestone with a real notation or analysis
  consumer may grill that decision.

## Density, spacing, shape, and depth

### Density and spacing

Use a balanced default density: comfortable reading surfaces with moderately compact labels and
metadata. The spacing scale is:

`4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`

Do not introduce intermediate spacing tokens without a demonstrated consumer and a deliberate contract
change.

### Shape

Use the restrained radius hierarchy `4px`, `8px`, and `12px`. The system should feel precise and
document-like rather than pill-heavy or broadly rounded.

### Surface hierarchy and elevation

Use tonal surfaces and fine borders as the normal depth hierarchy. Reserve subtle elevation for major or
genuinely floating emphasis. Avoid turning every region into a generic floating card.

### Keyboard focus

The shared focus contract is a `2px` indigo-primary ring with `2px` of surface-colored separation. It
must remain visible across every supported dark surface and at the accepted review sizes.

## Reusable feedback contract

### Semantic variants

The supported variants are:

- information;
- success;
- warning; and
- error.

Loading is consumer state, not a feedback severity.

### Content and icon contract

Every feedback presentation accepts a required message and an optional heading. MP-02 does not add
action controls, recovery workflows, or arbitrary child composition.

Each severity has a fixed Lucide icon:

| Severity | Icon |
|---|---|
| Information | `Info` |
| Success | `CircleCheck` |
| Warning | `TriangleAlert` |
| Error | `CircleX` |

There is no custom-icon API in MP-02. The icon is decorative to assistive technology because the heading
and message carry the meaning.

### Presentation structure

One shared semantic core supports three explicit wrappers:

- `InlineFeedback`;
- `PanelFeedback`; and
- `PageFeedback`.

The wrappers make layout intent discoverable while keeping severity, icon, content, and accessibility
treatment consistent.

### Announcement ownership

Severity does not automatically select `status` or `alert` behavior. The consumer knows whether content
is static, newly inserted, or updated and therefore explicitly owns live-region semantics. This prevents
static panel and page content from being announced merely because it renders.

## Storybook review contract

MP-02's review surface contains:

1. a token overview;
2. a complete typescale specimen;
3. a feedback matrix covering four severities across inline, panel, and page presentations; and
4. one restrained combined composition that proves coherence without pretending to be production UI.

Every implementation stage in the future MP-02 focused Plan must be **story-first and story-complete**:

1. Start by expressing the stage's intended visual outcome as a Storybook story.
2. Implement until that story is working and reviewable.
3. End the stage with the story still providing its tangible human-review surface.

Token groundwork may begin with a specimen story that becomes valid as its tokens are implemented.

## Acceptance and proof direction

Human visual review targets:

- desktop at `1920 × 1080` CSS pixels; and
- Pixel 8a portrait at `412 × 915` CSS pixels.

MP-02 does not introduce committed screenshot baselines or an external visual-regression service. Proof
combines focused component and interaction tests, automated accessibility checks, responsive Storybook
review, contrast verification, keyboard-focus review, and explicit human visual acceptance. Automated
axe results supplement but do not replace human WCAG review.

## Explicit MP-02 exclusions

MP-02 does not:

- restyle production `/` or adopt the new primitives there;
- create the site shell, navigation, production routing, or `/viewer`;
- create a board adapter, chessboard, chess notation, move behavior, stored-data behavior, or position
  workflow;
- add action controls, recovery workflows, notifications, logging, or persistence;
- add engine behavior, evaluation copy, evaluation visuals, or analysis controls;
- add a light theme or theme switcher;
- add a global state library;
- promote the temporary MP-01 Foundation Check into reusable product UI;
- introduce a monospace role or speculative structural signature; or
- treat the advisory HTML reference's conceptual colors as official or production-ready.

The temporary Foundation Check remains development-only until MP-05 removes it after real stories and
consumers replace its compatibility proofs.

## Decision history

Three visual directions were compared in a temporary HTML/CSS prototype: Tournament analysis desk,
Chessboard geometry, and Engine workstation. Tournament analysis desk was selected. The rejected
directions and comparison scaffolding were removed before the reference was accepted. The accepted
reference was then checked against this decision record and retained only the selected, MP-02-bounded
specimens.

The advisory reference contains no JavaScript, external requests, motion, gradients, interactive
controls, shell, board, chess behavior, engine behavior, or data workflow. Its conceptual colors must be
replaced or validated against the official export before implementation.
