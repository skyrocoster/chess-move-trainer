# Move Response Distributions — Historical Grilling Synthesis

**Status:** Settled visual and product-direction synthesis

**Implementation authority:** None

**Relationship:** This historical record links the [signed-off focused 01C mock-up](../../experiments/mock-ups/move-response-distributions/)
and its [repository-aware design hand-off](../../experiments/mock-ups/move-response-distributions/DESIGN.md).
This record and `DESIGN.md` are historical, noncanonical evidence. Neither is an implementation Plan or an
implementation authorization.

## Settled decisions

1. **First integration target:** Repertoire Builder only. Viewer is excluded initially, although reusable composition
   is desirable.
2. **Corpus scope:** Use games matching the selected repertoire color.
3. **Metric:** Count distinct games per reply, not raw occurrences. A recurring parent can let one game contribute to
   more than one child branch. Preserve that accurate caveat; do not invent global de-duplication across child
   branches.
4. **Presentation:** Show the top five replies individually. Group all remaining replies in **Other**, and omit
   **Other** when there is no tail.
5. **Opening-family names:** Include them only when classification is reliable; there is no placeholder requirement.
6. **Reply selection:** Selecting a reply advances through the existing Repertoire Builder move flow. **Other** is
   disclosure-only and is not a move.
7. **API shape:** Use a dedicated response-distribution endpoint. Its exact endpoint name and implementation details
   remain downstream assessment/planning matters.
8. **Responsibility split:** Follow the existing “Seen this position X times” / `PositionReachFrequency` pattern:
   the backend owns normalized position and move data; the frontend owns loading, presentation, grouping, and
   interaction.
9. **States:** Provide explicit loading, no-games, and unavailable states.
10. **Visual sign-off:** The focused 01C mock-up is visually approved.

## Historical boundary

This synthesis records the settled direction for hand-off to the existing assessment and planning workflow. It does
not select an endpoint name, chart dependency, exact insertion point, normalization source, or other implementation
detail. It does not authorize product changes, API or schema work, dependency installation, test changes, or Plan
execution.
