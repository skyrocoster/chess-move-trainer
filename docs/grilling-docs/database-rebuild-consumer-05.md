# Database rebuild CONSUMER-05 direction

## Purpose

Settle the Repertoire analysis behavior for `CONSUMER-05` before assessing and planning its migration from the
legacy evaluation endpoints to the generated clean analysis client.

This record is directional evidence. It is not implementation authorization by itself.

## Confirmed outcome

Repertoire analysis follows the currently selected/displayed position and adopts the clean analysis lifecycle through
the generated `getAnalysis()` and `requestAnalysis()` operations.

- Selecting or navigating to a position observes its existing analysis automatically.
- Observation alone never starts engine work.
- When analysis has not been requested, the user can deliberately choose **Analyze position**.
- Every Repertoire analysis request asks for `tool` quality. Browser-quality analysis is not part of this workflow, so
  no browser-to-tool upgrade control or wording is required.
- Queued and running work is polled and presented as progress for the selected position.
- If an existing result accompanies active work, it remains visible until the completed result replaces it.
- A ready result is presented without an Update or Retry-analysis action.
- The legacy **Update analysis** and **Retry analysis** actions are removed because the clean API requests a desired
  result and safely reuses sufficient work; it does not expose action-shaped update/retry semantics or persisted
  failure state.
- **Retry observation** remains available for a connection or loading failure.
- Existing candidate-line interaction, including playing a candidate move and following the resulting selected
  position, remains unchanged.

## Reasoning

Tool-quality analysis was chosen because it completes within seconds in the intended environment, so a lower-quality
interactive tier is unnecessary. Starting analysis remains deliberate because moving through a game should not queue
engine work for positions the user only visits briefly.

Controls should correspond to real clean-API behavior. Removing action-shaped Update and Retry controls avoids
promising forced recalculation or queue-failure semantics that the clean contract intentionally does not provide.

## Scope boundaries

- This is the one selected/current-position Repertoire analysis workflow already named by the database-rebuild master
  plan; it does not restore a parent-versus-displayed-position split.
- Use only the generated clean analysis GET and POST operations for this workflow. Do not add a compatibility adapter
  or fallback.
- Do not migrate preferred-move behavior or any other remaining consumer.
- Do not retire the legacy evaluation routes in this slice; that remains `RETIRE-04`.
- Do not add arbitrary engine settings, automatic bulk analysis, browser-quality controls, analysis history, persisted
  failures, or queue internals.
- Preserve the existing position navigation and candidate-line experience except for the confirmed lifecycle changes
  above.

## Planning note

Focused assessment may settle implementation details such as generated-client adaptation, bounded polling mechanics,
and exact error mapping without another product decision, provided the confirmed behavior and boundaries remain
unchanged. Escalate any need to change the analysis trigger, requested quality, user-visible lifecycle, generated
contract, another consumer, or route-retirement scope.
