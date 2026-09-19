# Selected design: Tournament Console

This folder now contains only the selected direction. The other alternatives have been removed because the Tournament Console direction was chosen for implementation.

## Selected direction

**Tournament Console** — a dark, dense, digital surface for competitive club players. The board is the hero; everything else is restrained matte chrome. The signature is the glowing teal move glyph when the correct move is found.

See `01-tournament-console/direction.md` for the full design thesis, palette, type, structure, signature, restraint, accessibility notes, and copy principles.

See `00-frontend-audit/audit.md` for the audit that motivated the redesign.

## What changed after selection

The original mock-up used a monospace typeface to reinforce the console mood. After review, the direction was adapted to use the repository's existing **system-ui** font stack (defined in `frontend/src/styles/cmt-typescale.css`) so the new components fit the current design-system contract without adding a new font.

## Next step

The React/TypeScript implementation of this direction lives in the main frontend source. The mock-up here is kept as the reference artifact.
