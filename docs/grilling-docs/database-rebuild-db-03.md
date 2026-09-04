# Database rebuild DB-03 grilling handoff

> **Status:** coordinator-approved handoff
> **Confirmation:** The user confirmed this shared understanding on 2026-09-04.
> **Authorization:** This handoff settles DB-03 direction for focused planning. It does not authorize implementation.

## Authority and outcome

This handoff is bounded by the settled direction and DB-03 envelope in
`docs/master-plans/database-rebuild/database-rebuild.md`, together with only the DB-03 authority ranges named there
from `database-rebuild-direction.md` and `database-rebuild-schema.md`. It does not reopen those decisions.

DB-03 will provide a clean, package-owned two-stage toolchain. Acquisition maintains retained Chess.com raw month
files. Import independently rebuilds accepted standard trainer games into `datasource_game`,
`derived_game_position`, and the shared `derived_position` catalogue.

## Confirmed acquisition decisions

- “Current month” means the UTC calendar month. It is refetched only when Chess.com lists that month in its archive
  response. If it is not listed, acquisition does not construct or request its URL and does not refetch the newest
  historical month.
- A fetched month is safe to publish or merge only when the response is a JSON object containing a `games` list and
  every entry has a valid, unique Chess.com game UUID. An empty list is valid. Other defective game details may remain
  in raw source and be skipped later by normalization. A structurally unsafe or UUID-ambiguous response leaves the
  prior usable file intact.
- Existing historical month files are immutable and skipped. A historical month listed by Chess.com but missing
  locally is fetched once, validated, atomically created, and thereafter treated as immutable.
- The current-month file is merged additively by Chess.com game UUID: new games are added, corrected games replace
  their earlier raw representation, and games omitted from the latest response remain.
- If an eligible month request fails, acquisition continues with the other eligible months. The failed file remains
  unchanged or absent, successfully published files remain, and the command returns a nonzero incomplete result.
- No raw source is deleted.

## Confirmed configuration and CLI boundary

The cohesive importable package is owned under `chess_move_trainer.database.games`, with separate responsibilities
for configuration, HTTP acquisition, raw-month storage, normalization, and game/occurrence persistence. Acquisition
does not open SQLite. Normalization does not access the network. Shared position writes compose with the existing
package-owned canonical-position service rather than duplicating it or exposing database handles publicly.

The existing Typer application at `python -m chess_move_trainer.database` gains these supported thin commands:

- `games acquire --config PATH --raw-root PATH`, with explicit `--username` and
  `--trainer-chesscom-uuid` overrides and explicit transport settings where applicable. It performs only archive
  discovery and raw-file work.
- `games import --config PATH --raw-root PATH --database PATH`, with an explicit
  `--trainer-chesscom-uuid` override. It performs only raw-to-SQLite normalization.

The package-owned YAML format keeps `username` and `trainer_chesscom_uuid` separate. It does not derive one from the
other or fetch a player profile. Commands are noninteractive, accept explicit paths, have useful `--help`, and are
safe for automation. Exit status `0` means the operation completed, including any reported per-game skips; `1` means
the operation was incomplete or failed operationally; `2` is Typer's invalid invocation/configuration status; and
`130` means user interruption with the active atomic unit rolled back or left unpublished. No special rate-limit exit
or persisted failure/run state is introduced.

Synchronous `httpx`, which is already pinned, is the acquisition transport default. Normalized UTC timestamps use
canonical `YYYY-MM-DDTHH:MM:SSZ` text. These are implementation defaults, not new dependencies or broader features.

## Settled normalization behavior

- Import accepts standard chess games from the normal initial position when exactly one archive participant UUID
  matches the configured trainer UUID. Non-standard, trainer-absent, malformed, or illegal games remain raw and do
  not create normalized rows; warnings and skips are not persisted.
- `datasource_game` retains the exact source PGN and trainer-oriented metadata. Chess.com's numeric end time takes
  precedence over a disagreeing PGN time, and authority-defined unknown metadata remains nullable.
- A game with N moves produces exactly N+1 zero-based occurrences. Each occurrence stores the UCI move leaving that
  position; the final occurrence stores NULL. Repeated positions reuse the permanent canonical position identity.
- Each fully valid game commits independently. A later invalid game or interruption does not roll back earlier valid
  games.
- A valid accepted correction atomically replaces that game's metadata and complete occurrence set only after full
  validation. A malformed or illegal correction leaves the prior normalized game and occurrences intact.
- No special behavior or focused proof will be invented for the speculative case where a structurally valid correction
  changes a previously accepted game into a non-standard or trainer-absent game. If real source data or implementation
  proof reveals that case, it is escalated for a decision.

## Focused planning and proof obligations

The focused Plan should proceed sequentially through package/configuration and CLI boundaries, archive traversal and
atomic raw publication, normalization and replay, correction/transaction behavior, and focused package/CLI proof.
Synthetic fixtures must cover the approved archive and month behavior without exposing personal game content.

Focused proof must establish:

- archive requests, existing-history skips, one-time missing-history creation, and listed-current-month selection;
- new/corrected/omitted UUID merge behavior and prior-file preservation for unsafe responses;
- continuation plus nonzero completion when one eligible month request fails;
- trainer as White and Black, nullable metadata, non-standard and trainer-absent skips, malformed and illegal games;
- exact N+1 outgoing-move occurrences, final NULL, canonical position reuse, and normal-start enforcement;
- independent valid-game commits, atomic valid correction replacement, and invalid-correction preservation;
- Typer help, explicit inputs, noninteractive invocation, meaningful exits, and source/package boundaries.

Only finite focused package or CLI tests that directly prove these behaviors belong to DB-03 implementation proof.
Lint, formatting, broad type/build, source-size, aggregate, and repository-maintenance checks do not.

## Exclusions and escalation

DB-03 adds no table or persisted player, corpus, fingerprint, fetch-state, ETag, run, history, failure, or manifest
machinery. It does not migrate old rows, rewrite existing historical files, delete raw data, adapt legacy code, or
change APIs, production backend/application modules, frontend code, openings, analysis, cutover, or retirement.
Legacy tools remain read-only conceptual evidence and may not be imported, wrapped, copied, patched, or delegated to.

Escalate rather than silently expand if real input exposes the deferred eligibility-changing correction, archive
participant identity is unavailable, safe behavior appears to require extra schema/history or historical-file
rewrites, package composition would expose raw database handles, or any required behavior changes a settled contract,
dependency, destructive effect, or acceptance boundary.
