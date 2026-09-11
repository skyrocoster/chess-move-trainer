# Database rebuild CONSUMER-06 direction

## Purpose

Settle the date behavior required to migrate Repertoire's existing Preferred Move workflow to the clean timeline API
without introducing the future calendar interface.

This record is directional evidence for `CONSUMER-06`, not implementation authorization by itself.

## Confirmed outcome

Repertoire adopts the generated clean preferred-move GET, PUT, and DELETE operations for the existing selected trainer
transition workflow.

- The preference belongs to the outgoing move after the selected transition's parent FEN.
- Reading the current preference uses a finite UTC window from today, inclusive, until tomorrow, exclusive.
- Saving a selected outgoing UCI uses UTC today as `effective_from` and omits `effective_until`, so it applies from today
  onward.
- Removing the preference also uses UTC today as `effective_from` and omits `effective_until`, so removal applies from
  today onward.
- After a mutation, the workflow refreshes through the clean finite GET and displays the backend-normalized result.
- A clean `move` segment is presented as the saved move, with SAN derived from the parent FEN and outgoing UCI.
- Clean `no_preference` and `unconfigured` values both use the current no-saved-move presentation.
- A legal parent FEN may be configured even when it is absent from imported games; corpus observation is not a save
  prerequisite.

## Reasoning

The current screen answers only "what is my preferred move now?" and provides no date controls. A one-day UTC read
window retrieves exactly the active preference the screen can present, while open-ended mutations preserve the simple
"from now onward" behavior. Fetching an arbitrary future horizon would expose data the interface cannot use.

This policy is intentionally **for now**. Later calendar work may introduce explicit ranges and future schedule
presentation. `CONSUMER-06` must not anticipate that interface.

## Scope boundaries

- The frontend supplies the finite current-day window and mutation start date but does not calculate interval splits,
  merges, overlaps, gaps, or normalization.
- Do not add a calendar, date picker, rolling/far-future read horizon, authored repertoire lines, or caller-side schedule
  arithmetic.
- Do not add compatibility or fallback behavior and do not retire the legacy preferred-move routes; retirement remains
  `RETIRE-05`.
- Do not migrate another consumer or change the accepted clean analysis, position-context, move-response, game-loading,
  navigation, or candidate-move workflows.
- Preserve the existing Preferred Move presentation and interaction except for clean-contract mapping and removal of the
  corpus-only save restriction.

## Planning note

Focused assessment may settle mechanical details such as deriving UTC today/tomorrow consistently for one operation,
generated-client adaptation, typed error mapping, and backend-authoritative refresh without another product decision.
Escalate any need to change the current-day/open-ended policy, expose future periods, distinguish no-preference from
unconfigured in the current UI, change parent-FEN/outgoing-UCI meaning, alter another consumer, or retire a route.
