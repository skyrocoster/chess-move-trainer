# Quiet underline · application-semantics mock-up

This is a new noncanonical branch of the selected **Quiet underline** concept from
`experiments/mock-ups/exclusive-tabs-catalogue/`. It stays generic: the page has no application imports, network
requests, AnalysisPanel implementation, or MoveResponseDistribution implementation.

## How to view

- Open `index.html` directly in a browser, or serve this folder from the repository root:

  ```text
  py -3 -m http.server 4173 --directory experiments/mock-ups/exclusive-tabs-quiet-underline-dark
  ```

  Then open <http://localhost:4173>.

- Click a tab, or focus the active tab with `Tab` and use `ArrowLeft`/`ArrowRight`, `Home`, or `End`.
- Resize below 620px. The tab list keeps each 48px target intact in a horizontally scrollable rail while the selected
  panel remains a wrapping, bounded section.

## Choices embodied

- **Visual language:** local system-ui stack; dark `surface-container`; `on-surface` titles; `on-surface-variant`
  supporting text; `primary` blue accent; `outline-variant` borders; 8px panel radii.
- **Rhythm:** 16px outer and panel padding with 4px, 8px, 12px, and 16px spacing steps.
- **Quiet underline:** the tab row has no filled control background; the active tab is indicated by a quiet 2px
  primary underline and primary label color.
- **Targets and focus:** every tab has a 48px minimum target; keyboard focus uses a 2px primary outline with a 2px
  offset. The forced-colors media query maps surfaces to `Canvas`, text to `CanvasText`/`GrayText`, borders to
  `ButtonText`, and active/focus treatment to `Highlight`/`HighlightText`.
- **Panel convention:** each generic `tabpanel` is a self-contained `section` with its own header, title, status, and
  status/body placeholder content.
- **Semantics:** one `tablist` owns four `tab` buttons. Tabs use roving `tabindex`, `aria-selected`,
  `aria-controls`, and `tabpanel`/`aria-labelledby`; arrow keys, Home, and End automatically move and activate the
  selected panel. Click and Enter/Space also activate. The panel remains keyboard-addressable with `tabindex="0"`.
- **State model boundary:** this small DOM-local demo behaves like an uncontrolled example. Controlled versus
  uncontrolled API design is intentionally not implemented here.

The only implementation decision being explored is the reusable container's application-facing visual and interaction
semantics; placeholder content is not a product design.
