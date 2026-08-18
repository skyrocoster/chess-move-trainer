# MP-06 Validated FEN Corpus — Grilling Record

**Recorded:** 2026-08-18  
**Status:** Confirmed design-review evidence  
**Implementation authority:** None  
**Implementation status:** MP-06 implemented and accepted on 2026-08-18; the
[archived focused Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md) owns the
delivery evidence. This record is historical grilling evidence of the settled contract, not current
implementation state.  

## Purpose

This record settles the product and data decisions needed to plan MP-06 from the
[Static Position to Analysis Workspace master plan](../master-plans/static-position-to-analysis.md).
It does not create a focused Plan, authorize implementation, select final table or symbol names, or
settle the analysis and user-interface contracts owned by later milestones.

## Outcome

MP-06 creates a complete, validated, persisted corpus of positions from the captured games. The corpus
supports later position retrieval and game traversal without adding viewer integration or engine analysis.

## Source, corpus, and perspective

- Tracked Chess.com JSON remains the durable provenance and rebuild source.
- Extraction reads normalized games from `data/database/chess_games.db`.
- A corpus is identified by its subject player's stable UUID. The initial corpus subject is Skyrocoster,
  UUID `0101b08a-ce8b-11ee-b2fd-e90263e5548c`.
- A game belongs to a corpus when `rules=chess` and the subject UUID appears as exactly one player.
- The current accepted corpus contains 12,365 games: 6,185 played as White and 6,180 as Black.
- Four `oddschess` games are excluded. A completed run records the exclusion count and reason.
- Player names, colors, ratings, results, URLs, and PGNs remain owned by the existing game and player
  records. Position rows do not repeat them. The subject's color is derived from each game's white and
  black player UUIDs.
- The database structure may represent another subject-player corpus later, but MP-06 adds no multi-user
  interface or management.

## Ordered position data

For every accepted game, extraction persists ply zero and one ordered position after every half-move. Each
nonzero occurrence records the move that produced it in both SAN, such as `Nf3`, and UCI, such as `g1f3`;
ply zero has no move.

FEN state is retained without loss as independently usable fields:

- piece placement;
- side to move;
- castling rights;
- en-passant target;
- halfmove counter; and
- fullmove number.

A complete six-field FEN can be reconstructed when needed. This separation preserves every counter while
allowing MP-09 to choose a later analysis-identity policy without a corpus migration merely to recover data.

## FEN and replay rules

- Extraction uses standard FEN behavior that preserves the en-passant target after every qualifying
  double pawn move, even when no capture is available.
- The two accepted custom-start chess games replay from their supplied starting FEN.
- A six-field source final FEN must match replay exactly.
- When a source final FEN omits the move counters, replay supplies a complete six-field state and every
  source-provided field must match.
- Invalid input never falls back to the standard starting position.

## Unique position-state index

The unique index groups the first four FEN fields: piece placement, side to move, castling rights, and
en-passant target. Halfmove and fullmove counters remain on each occurrence.

This is a shared position-state index, not a promise that engine analysis is reusable between occurrences.
MP-09 must settle the effect of the fifty-move counter, repetition history, engine identity, settings, and
other reuse constraints. FEN cannot represent prior repetition history, and MP-06 does not pretend otherwise.

## Database and command ownership

- Extraction-owned, versioned corpus tables are added to `data/database/chess_games.db`.
- Position records reference existing games rather than copying game metadata.
- The extraction command initializes its missing tables and schema version, and refuses an incompatible
  schema.
- The fetcher does not own the corpus tables.
- Fetching and extraction remain separate explicit commands during MP-06 testing and acceptance. Later
  automation is deferred.
- Fetching and extraction must not write concurrently. A busy database produces a clear failure rather
  than an extraction against a moving source snapshot.

## Initial extraction and updates

The first run processes every accepted game. Later runs:

- process new games;
- fingerprint PGN, starting position, final FEN, and rules to detect replay-relevant changes;
- rebuild changed games;
- remove occurrences for deleted or newly excluded games;
- remove unique position states with no remaining occurrence;
- leave unchanged corpus rows untouched; and
- record a successful no-change completeness check in run history.

New corpus state is published atomically only after the whole affected run and its completeness checks pass.
A failed or interrupted run rolls back corpus changes so readers retain the previous complete corpus. An
interrupted run is recorded when possible. Partial corpus state is never published.

## Run history and observable progress

A small run-history surface records status, start and finish times, subject corpus, new, changed, removed,
unchanged, accepted, and excluded game counts, ordered-position and unique-state counts, validation results,
and concise failure details.

The command must visibly show that it is still working:

- an interactive terminal continuously updates one line with completed and total games, percentage,
  positions generated, and elapsed time;
- redirected or non-interactive output emits periodic progress lines suitable for logs; and
- progress appears at least every 100 games or 10 seconds, whichever occurs first.

After success, a concise report shows accepted, excluded, new, changed, removed, and processed games,
ordered positions, unique states, and validation results. It does not print every position.

Runtime logs, temporary files, and generated working artifacts must use deliberate nested folder structure;
they must not be scattered through the repository or confused with canonical source data.

## Publication checks

Before publication, extraction proves:

- every accepted game is represented;
- every PGN parses and replays legally;
- custom starting positions are honored;
- every final replay state matches all source-provided FEN fields;
- each game has contiguous plies from zero through its final move;
- SAN and UCI correspond to the replayed move;
- every occurrence references valid game and position-state records;
- unique-state occurrence links and counts are consistent;
- removed or excluded games have no remaining occurrences; and
- the completed corpus belongs to its selected subject player.

## Testing and acceptance evidence

Automated proof uses temporary databases for initial extraction, unchanged reruns, new games, changed games,
removed or excluded games, custom starts, shortened final FENs, en-passant preservation, failures, rollback,
interruption, and integrity and completeness checks. Acceptance also required a complete extraction against
the current captured corpus; that acceptance extraction was completed and human-accepted on 2026-08-18 (see
the [archived Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md)).

The historical full-corpus feasibility replay (pre-implementation) established 12,365 accepted games,
626,897 half-moves, 639,262 ordered occurrences including ply zero, 510,876 unique four-field position
states, and zero parse or legal-replay failures. The implemented and accepted corpus confirmed exactly
these totals: 12,365 accepted games; 639,262 ordered occurrences including ply zero; 510,876 unique
states; four `oddschess` exclusions; and zero replay failures (delivery evidence in the
[archived Plan](../plans/done/mp06-validated-fen-corpus/mp06-validated-fen-corpus.md)).

The approved isolated prototype is available to planning at:

- `Scratch/prototypes/mp06_fen_corpus_prototype.py`
- `Scratch/prototypes/mp06_fen_corpus_sample.json`

It demonstrates replay, complete FEN construction, ordered records, and structural deduplication. It is not
production implementation, and its former four-field “analysis key” terminology must not create an analysis-
reuse promise.

## Planning guidance confirmed by the user

The focused Plan must make the prototype available as evidence and must use properly nested locations for
logs, temporary files, and related artifacts. Its stages must not be over-collapsed. In particular, schema
creation and initialization should be independently reviewable and human-checked before a later stage writes
the complete position corpus. Robust stage boundaries must preserve atomicity and produce meaningful human
acceptance gates rather than merely grouping implementation tasks.

## Explicit exclusions and deferred ownership

MP-06 does not add backend or frontend corpus APIs, viewer selection, traversal, Stockfish analysis, an
analysis-reuse policy, board editing, unknown-position persistence, automatic fetch-to-extraction
orchestration, authentication, authorization, or multi-user management.

Later milestones own the following deliberately deferred decisions:

- MP-07: retrieval API and stored-position selection;
- MP-08: traversal and player-perspective presentation;
- MP-09: repetition-aware analysis identity, halfmove-counter treatment, engine settings, and reuse; and
- later operational work: whether extraction should run automatically after fetching.

## Confirmation

The user confirmed this complete record, including the live progress requirement, on 2026-08-18. The
decision tree had no remaining MP-06 frontier. MP-06 was implemented through the focused Plan in four
human-gated stages, all shipped and accepted on 2026-08-18. This record itself authorizes no
implementation. MP-07 is the next milestone and requires fresh grilling before focused planning; neither
this record nor the master plan settles any MP-07 decision.
