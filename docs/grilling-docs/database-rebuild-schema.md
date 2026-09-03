# Database rebuild exact schema catalogue

> Recorded on 3 September 2026; revised the same day after independent review. This document
> is the exact replacement schema catalogue required by direction section 7, item 2 of the
> [database rebuild direction](database-rebuild-direction.md), which remains the binding
> product authority. It names every rebuilt table and field exactly, and settles the
> deliberately conceptual points that the direction record left to "the later actual-name
> and field catalogue" (direction sections 3.1, 3.8, 3.10, 3.11).
>
> **This document is description only.** It is **NOT BUILT** and grants **no implementation
> authorization**: no DDL is executed, no database file is created or changed, and no
> application, API, script, migration, cutover, or tool is built. It does not modify,
> replace, or delete the existing database or any raw source file (direction section 1.3,
> section 8).

---

## 1. Reading guide, conventions, and classification

### 1.1 Binding authority

Every table and field below exists only because the direction record justifies it. Nothing
here reopens a settled direction question, invents a table in the direction's negative
register (direction section 3.12), adds an excluded capability (direction section 5), or
smuggles an excluded field into a surviving table. Where this document makes a choice the
direction delegated to "the later catalogue", the choice is marked **[catalogue decision]**
with a short rationale.

### 1.2 What "1:1" means in this document

No rows migrate from the old database (direction section 1.3), so a 1:1 claim is about
**field meaning, not values**. A new field is a **genuine 1:1 survivor** of an old field
only when all three hold:

1. it carries the **same fact** with the **same meaning**;
2. its stored source values keep the **same representation, unit, and format**; and
3. its derivation is a **direct copy** from the old column's source with no semantic change.

**Nullability and integrity-rule changes alone do not defeat 1:1.** When the rebuilt schema
tightens or relaxes nullability, or adds a CHECK or UNIQUE constraint, the field remains 1:1
when each value that is stored still carries the same source fact in the same representation
(for example `position_state.placement` → `dp_placement`, or `games.time_control` →
`dg_time_control_source`). Those DDL admission rules are recorded separately rather than
mislabelled as a data transformation. What defeats 1:1 is an actual change to the stored
fact: value conversion (epoch seconds to UTC text), re-keying (text position keys or UUID
keys to fresh integer identities), conditional re-selection (white/black columns re-picked
by trainer color), a one-ply shift, re-scoping of the fact's meaning, or a changed stored
representation/domain. A
field that is renamed but satisfies all three conditions is still 1:1 (for example
`position_state.castling` → `dp_castling_rights`). Every field row states its old exact 1:1
name where one exists; transformed lineage is explained separately in section 14, and every
old field is fully accounted for — individually — in section 15.

### 1.3 Table-prefix classification

Every actual table name begins with exactly one of two prefixes:

| Prefix | Meaning |
| --- | --- |
| `datasource_` | Rows whose authoritative facts originate in an **external source** or in **direct user/runtime input**. |
| `derived_` | Rows whose facts are **normalized, computed, engine-produced, or maintenance/operational**. |

Classification of every table, including the borderline cases:

| Table | Prefix | Why |
| --- | --- | --- |
| `datasource_game` | `datasource_` | Authoritative facts come from the external Chess.com monthly archive JSON and the PGN it carries. |
| `datasource_opening` | `datasource_` | Authoritative facts (`eco`, `name`) come verbatim from the external `lichess-org/chess-openings` TSV files. |
| `datasource_preferred_move_period` | `datasource_` | **Borderline, resolved:** each row's authoritative period semantics record direct user decisions — which position, which move (or explicit no preference), and from when. Effective boundaries may be normalized or derived when later edits split or shorten periods, but normalization of boundaries does not change the row's origin: the row exists because the user decided it. So `datasource_` applies even though the referenced position is derived. |
| `derived_position` | `derived_` | Canonical position identity is normalized/computed from game PGNs, route PGNs, and preference input; no external row is copied verbatim. |
| `derived_game_position` | `derived_` | Occurrence rows are normalized by replaying the source PGN. |
| `derived_opening_route` | `derived_` | Routes are computed by replaying source PGNs; the TSV contains no route identity. |
| `derived_opening_route_move` | `derived_` | Route moves are computed by replaying source PGNs. |
| `derived_analysis_result` | `derived_` | Engine-produced output. |
| `derived_analysis_line` | `derived_` | Engine-produced output. |
| `derived_analysis_queue` | `derived_` | **Borderline, resolved:** a queue row is created by a direct runtime request, but its row lifecycle is maintenance/operational coordination — the worker claims it, manages its state, claim marker, and token, and deletes it on completion, so no user-authored fact is retained in it. It is transient operational machinery (direction section 3.10: "only live operational coordination"), therefore `derived_`. |
| (no table) | — | **Borderline, resolved:** the database-wide schema version is stored as SQLite's `PRAGMA user_version`, not as a table, so no table-prefix classification applies (section 2). |

### 1.4 Column naming convention

The convention, applied consistently to every table:

1. **Every non-FK column begins with a declared table shorthand**, a concise unambiguous
   prefix listed in section 1.5.
2. **Every FK column begins with the exact full parent table name**, normally
   `<exact_parent_table_name>_id`, and states its reference unambiguously (for example
   `datasource_game_id INTEGER ... REFERENCES datasource_game(dg_game_id)`).

**PK-versus-FK naming, explained.** A parent table's own surrogate PK column is *not* an FK,
so it carries the **own-table shorthand** (for example `dg_game_id` in `datasource_game`,
`dp_position_id` in `derived_position`, `dor_route_id` in `derived_opening_route`). A child
table's FK to that same parent deliberately uses a **different, longer name** built from the
parent's full table name (for example `datasource_game_id` inside `derived_game_position`).
The two names intentionally differ so that every FK column self-describes which table it
references without consulting any DDL, while every table's own fields stay short and
uniformly prefixed. When a child's **primary key is itself a foreign key** — the case for
`derived_analysis_result` and `derived_analysis_queue`, whose results and requests are keyed
one-per-position, and for `derived_game_position`, `derived_opening_route_move`, and
`datasource_preferred_move_period`, whose composite PKs contain FK columns — the **FK naming
wins** and the PK column uses the parent-full-name form (`derived_position_id`), because the
column's referential role is the more important fact about it. Composite PKs list their
columns explicitly.

### 1.5 Declared table shorthands

| Table | Shorthand |
| --- | --- |
| `datasource_game` | `dg_` |
| `derived_position` | `dp_` |
| `derived_game_position` | `dgp_` |
| `datasource_opening` | `do_` |
| `derived_opening_route` | `dor_` |
| `derived_opening_route_move` | `dorm_` |
| `derived_analysis_result` | `dar_` |
| `derived_analysis_line` | `dal_` |
| `derived_analysis_queue` | `daq_` |
| `datasource_preferred_move_period` | `dpm_` |

### 1.6 Cross-cutting storage conventions [catalogue decision]

- **Timestamps** are `TEXT` in ISO-8601 UTC form `YYYY-MM-DDTHH:MM:SSZ` (the same shape the
  old system generated with `strftime('%Y-%m-%dT%H:%M:%fZ', 'now')`). UK formatting remains
  presentation-only (direction section 2.1).
- **Calendar dates** are `TEXT` in exact canonical ISO form `YYYY-MM-DD`. Because SQLite's
  `date()` function silently normalizes lenient inputs (and yields `NULL` for invalid ones),
  date columns are checked with an exact shape test
  (`GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'`), an explicit
  `date(x) IS NOT NULL` test, and canonical equality (`x = date(x)`). The explicit non-NULL
  test matters because a SQLite CHECK does not reject a NULL expression. Together these
  tests prevent malformed or impossible dates such as `2025-1-1` or `2025-02-30` from
  passing (see `dpm_effective_from`/`dpm_effective_until`).
- **JSON values** are `TEXT` holding valid JSON; columns that must hold a JSON array are
  checked with `json_valid(...)`, `json_type(...) = 'array'`, and, where a non-empty array is
  part of the fact, `json_array_length(...) > 0`.
- **Foreign-key actions.** The settled lifecycles contain no delete flows: games are
  additive by UUID (direction section 3.3), positions are permanently retained (direction
  section 3.2), and catalogue replacement happens inside one transaction. Every FK therefore
  uses `ON DELETE RESTRICT` — SQLite's default `NO ACTION` is not used because `RESTRICT`
  fails immediately and makes accidental cascade loss impossible — with **exactly two
  justified exceptions**, both child sets that have no independent lifecycle and are always
  replaced or removed together with their parent:
  1. `derived_opening_route_move` → `derived_opening_route` uses `ON DELETE CASCADE`; and
  2. `derived_analysis_line` → `derived_analysis_result` uses `ON DELETE CASCADE`
     (direction section 3.9).

  During atomic catalogue replacement the tool deletes **child-first** —
  `derived_opening_route_move` rows before their `derived_opening_route` rows, and route
  rows before `datasource_opening` rows — inside the single publication transaction; the
  CASCADEs cover the child sets, and RESTRICT on the parent-side FKs guarantees nothing is
  removed out of order. No `ON UPDATE` action is specified anywhere; keys are never
  reassigned.
- **Invariants SQLite cannot express declaratively** (cross-row rules) are listed per table
  as *application-enforced invariants*; they are part of the exact meaning of the schema but
  are not CHECK constraints.
- **Indexes are not specified.** Index selection is separate later factual work (direction
  section 7, item 5). Only meaning-bearing `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, and
  `UNIQUE` constraints appear here.

---

## 2. Database-wide schema version: `PRAGMA user_version` [catalogue decision]

**Classification:** maintenance metadata, not a table; therefore no `datasource_`/
`derived_` prefix applies.

**Decision.** The single database-wide schema version (direction section 3.1) is stored in
SQLite's built-in `PRAGMA user_version` as a non-negative integer, value `1` at first
creation and incremented manually whenever the schema changes.

**Rationale.** The direction forbids per-feature `*_schema` tables and a permanent migration
audit ledger (direction section 3.1), and requires only "one database-wide schema version".
`PRAGMA user_version` is a header-level integer that costs no table, no row, and no write
machinery, is read in one statement at connection setup, and satisfies "another
straightforward mechanism" explicitly contemplated by the direction. The old per-feature
`*_schema`, `*_state`, and `*_run` tables have no successor (section 15).

- **Purpose:** database compatibility check for the rebuilt application and maintenance
  processes; never feature data, never history.
- **Source data:** assigned by the schema-creation/maintenance process; no external source.
- **Write/lifecycle:** set on database creation; incremented manually with each schema
  change; schema-changing operations follow the snapshot rules of direction section 2.3.

---

## 3. `datasource_game`

**Classification:** `datasource_` — external Chess.com archive facts.
**Feeder tool (description only, NOT BUILT):** the game importer described in section 13.2.

**Purpose and ownership.** One normalized, trainer-oriented record per accepted standard
Chess.com game (direction section 3.3), including the exact source PGN because copying and
sharing it is a current requirement.

**Source data.** The retained raw monthly archive files
`data/chess-com/raw/games/<YYYY>/<MM>.json`; each game object carries `uuid`, `url`, `pgn`,
`time_control`, `time_class`, `rated`, `rules`, `eco`, `end_time`, `fen`,
`initial_setup`, `tcn`, and `white`/`black` participant objects with `uuid`, `username`,
`rating`, `result`, `@id`. Only standard games (`rules = 'chess'`, normal initial board)
with the configured trainer UUID (`0101b08a-ce8b-11ee-b2fd-e90263e5548c`) are accepted
(direction section 4.1).

**Write and lifecycle.** Additive by Chess.com game UUID; a valid correction replaces one
game's metadata and occurrence set in one transaction; an invalid correction performs no
update or deletion — the prior `datasource_game` and `derived_game_position` rows are left
unchanged (direction section 3.3). No per-game version history.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `dg_game_id` | `INTEGER` | NOT NULL | **PK** | Internal compact integer identity used by occurrence FKs. | Assigned by the importer; never reused. | — `[NEW]` |
| `dg_chesscom_game_uuid` | `TEXT` | NOT NULL | `UNIQUE` | The Chess.com game UUID; unique and searchable so users can keep loading/sharing by external UUID. | Archive game object `uuid`. | `games.uuid` |
| `dg_source_url` | `TEXT` | NOT NULL | — | The game's Chess.com URL, shown by the viewer. | Archive game object `url`. | `games.url` |
| `dg_original_pgn` | `TEXT` | NOT NULL | — | The exact source PGN, byte-preserved, headers/clock annotations/comments intact. | Archive game object `pgn`. | `games.pgn` |
| `dg_trainer_color` | `TEXT` | NOT NULL | `CHECK (dg_trainer_color IN ('white','black'))` | Which color the trainer played; required for core statistics and for deriving the statistics actor. | Determined at intake by comparing archive participant `uuid` values against the configured trainer UUID. | — `[NEW]` |
| `dg_trainer_chesscom_uuid` | `TEXT` | NOT NULL | — | The trainer's archive participant UUID (the selected source identity, direction section 3.3). | Archive participant object `uuid` of the trainer's side. | — (transformed) |
| `dg_opponent_chesscom_uuid` | `TEXT` | NULL | `CHECK (dg_opponent_chesscom_uuid IS NULL OR dg_opponent_chesscom_uuid <> dg_trainer_chesscom_uuid)` | The opponent's archive participant UUID when available; NULL rather than rejecting an otherwise valid game. | Archive participant object `uuid` of the non-trainer side. | — (transformed) |
| `dg_trainer_rating` | `INTEGER` | NULL | — | The trainer's per-game rating snapshot. | Archive participant object `rating` of the trainer's side. | — (transformed) |
| `dg_opponent_rating` | `INTEGER` | NULL | — | The opponent's per-game rating snapshot. | Archive participant object `rating` of the non-trainer side. | — (transformed) |
| `dg_started_at_utc` | `TEXT` | NULL | — | Game start time in UTC when known. | PGN `UTCDate` + `UTCTime` headers inside `dg_original_pgn`, with `Date` + `StartTime` as the supported fallback. | — `[NEW]` |
| `dg_ended_at_utc` | `TEXT` | NULL | — | Game end time in UTC when known; Chess.com's numeric timestamp wins over a disagreeing PGN (direction section 3.3). | Archive game object `end_time` (epoch seconds). | — (transformed) |
| `dg_trainer_outcome` | `TEXT` | NULL | `CHECK (dg_trainer_outcome IN ('win','loss','draw'))` | The trainer's normalized result: win, loss, or draw. | Derived from the archive `result` codes of both participant objects. | — (transformed) |
| `dg_termination_reason` | `TEXT` | NULL | `CHECK (dg_termination_reason IS NULL OR dg_termination_reason NOT IN ('win','loss'))` | How the game ended, taken from the **termination-bearing** archive result code: for a decisive game, the non-`win` participant's code (typically the losing side, for example `resigned`, `checkmated`, `timeout`); for a draw, the common draw code when determinable (for example `agreed`, `repetition`, `insufficient`). An informative PGN `Termination` header is the fallback; otherwise NULL. `win` and `loss` are outcomes, not termination reasons, and are never stored here. | The archive `result` codes of both participant objects, with the PGN `Termination` header as fallback. | — (transformed) |
| `dg_time_control_source` | `TEXT` | NULL | — | The source time-control string (for example `120+1`, `300`), kept verbatim. | Archive game object `time_control`. | `games.time_control` |
| `dg_time_class` | `TEXT` | NULL | — | Chess.com time class (for example `bullet`, `blitz`, `rapid`); kept verbatim, no fixed enumeration is imposed because the archive's value set is the authority. | Archive game object `time_class`. | `games.time_class` |

**Constraints summary.** `PRIMARY KEY (dg_game_id)`; `UNIQUE (dg_chesscom_game_uuid)`;
the four `CHECK` constraints shown (trainer color, opponent UUID distinctness, trainer
outcome domain, termination-reason domain). Foreign keys: none — there is deliberately no
players table (direction section 3.3 keep-out).

**Application-enforced invariants.** Rows exist only for accepted standard games; intake
skip rules (trainer UUID absent, malformed PGN, illegal move, non-standard variant) are
importer behavior, not DDL.

**New fields.** `dg_game_id` and `dg_trainer_color` are genuinely new stored fields;
`dg_started_at_utc` is new as a column (the fact existed only inside the stored PGN
headers). Their lineage is explained in section 14.1.

---

## 4. `derived_position`

**Classification:** `derived_` — normalized canonical identity.
**Feeder tools (description only, NOT BUILT):** the game importer (13.2), the opening
catalogue builder (13.3), the bulk Tool selector while replaying route-only intermediate
positions (13.4), and preferred-move writes (13.6); all create canonical positions.

**Purpose and ownership.** Canonical chess-position identity shared by games, opening
endpoints, analysis, queue work, and preferred moves (direction section 3.2). Identity is
piece placement, side to move, castling rights, and an en-passant square only where a fully
legal en-passant capture exists. Positions are retained permanently once created, even when
nothing currently points at them.

**Source data.** Derived by replaying imported game PGNs (`dg_original_pgn`) and opening
route PGNs from the TSV source, and from the validated position/FEN supplied in a
preference operation for standalone preferred-move positions. FEN en-passant markers are
normalized to `-` when no fully legal capture exists, including pinned-pawn situations.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `dp_position_id` | `INTEGER` | NOT NULL | **PK** | Internal integer identity; stable even when unreferenced. | Freshly assigned on first creation of the identity against the legal-only canonical key. | — `[NEW]` (transformed/re-keyed; see below) |
| `dp_placement` | `TEXT` | NOT NULL | — | Validated canonical FEN board field of the identity. | Computed from the replayed board or the validated supplied position. | `position_state.placement` |
| `dp_side_to_move` | `TEXT` | NOT NULL | `CHECK (dp_side_to_move IN ('w','b'))` | Side to move field of the identity. | Computed from the replayed board or the validated supplied position. | `position_state.side_to_move` |
| `dp_castling_rights` | `TEXT` | NOT NULL | `CHECK (dp_castling_rights IN ('-','K','Q','k','q','KQ','Kk','Kq','Qk','Qq','kq','KQk','KQq','Kkq','Qkq','KQkq'))` | Castling-rights field of the identity in canonical `KQkq` order with no duplicates, `-` when none. | Computed from the replayed board or the validated supplied position. | `position_state.castling` |
| `dp_legal_en_passant` | `TEXT` | NOT NULL | `CHECK (dp_legal_en_passant = '-' OR dp_legal_en_passant GLOB '[a-h][36]')` | En-passant square **only where a fully legal en-passant capture exists**, else `-`. The rank restriction (3 or 6 only) is inherent to the fact: a legal en-passant target can only sit on the rank a double pawn push just crossed. | Computed with legal-only en-passant normalization. | — (transformed) |

**Constraints summary.** `PRIMARY KEY (dp_position_id)`;
`UNIQUE (dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant)` — settled
by direction section 3.2; the side-to-move, castling-order, and en-passant-shape CHECKs
above.

**Application-enforced invariants.** `dp_placement` is a validated canonical FEN board
field: exactly eight rank fields, sixty-four squares, legal piece characters only, exactly
one king per side, and no pawns on the first or eighth rank; its consistency with
`dp_side_to_move`, `dp_castling_rights`, and `dp_legal_en_passant` (castling rights only
where king/rook placement allows them; an en-passant target only where both the pawn that
moved two squares and an adjacent side-to-move pawn make a capture geometrically available)
is validated at creation. `dp_legal_en_passant`
is validated as **fully legal, not merely syntactically shaped**: a value other than `-`
requires that the en-passant capture be fully legal in the position — including that the
capturing pawn is not pinned — which is enforced by the legal-only normalization performed
by every producer (direction section 3.2). SQLite cannot replay chess, so these validity
rules are producer-enforced, not DDL.

**Keep-outs respected.** No halfmove/fullmove counters, no display FEN, no analysis data,
no actor columns, no feature-specific identities (direction section 3.2).

**Transformed fields.** `dp_legal_en_passant` is not a 1:1 survivor of
`position_state.en_passant`: the old system generated FENs with classic
`en_passant="fen"` markers (see `scripts/chess_com/_replay.py:57`), while the new field
carries legal-only normalized values, so identical old and new columns could hold different
values for the same position. `dp_position_id` is not a 1:1 survivor of
`position_state.state_id` either: it is a freshly assigned integer key against a
legal-only canonical identity, so the keying itself changed (re-keyed). See section 14.2.

---

## 5. `derived_game_position`

**Classification:** `derived_` — normalized occurrences.
**Feeder tool (description only, NOT BUILT):** the game importer (13.2).

**Purpose and ownership.** One ordered occurrence of a canonical position inside one
normalized game (direction section 3.4), preserving the separation between one
deduplicated position row and one row per occurrence.

**Source data.** Computed by replaying `dg_original_pgn` for each accepted game. For a game
with N moves there are N+1 occurrence rows; each occurrence stores the move **leaving** it;
the final occurrence's outgoing move is NULL.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `datasource_game_id` | `INTEGER` | NOT NULL | **PK part 1**; FK → `datasource_game(dg_game_id)` `ON DELETE RESTRICT` | The game this occurrence belongs to. | The imported game being replayed. | — (transformed) |
| `dgp_ply` | `INTEGER` | NOT NULL | **PK part 2**; `CHECK (dgp_ply >= 0)` | Zero-based ply of the occurrence within the game; `(datasource_game_id, dgp_ply)` identifies the occurrence. | Position of the occurrence in the replay. | `position_occurrence.ply` |
| `derived_position_id` | `INTEGER` | NOT NULL | FK → `derived_position(dp_position_id)` `ON DELETE RESTRICT` | The canonical position at this occurrence; repeats in one game reuse the same row. | Freshly assigned canonical-position identity computed from the replayed board's four identity fields. | — (transformed; re-keyed from `position_occurrence.state_id`) |
| `dgp_move_uci` | `TEXT` | NULL | `CHECK (dgp_move_uci IS NULL OR dgp_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dgp_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]')` | The move **leaving** this occurrence in UCI; NULL exactly on the final occurrence. The optional trailing letter covers promotions. | Computed from the move played at this occurrence. | — (transformed) |
| `dgp_halfmove_clock` | `INTEGER` | NOT NULL | `CHECK (dgp_halfmove_clock >= 0)` | Halfmove clock at this occurrence; belongs to the occurrence, not to shared identity. | Computed from the replayed board. | `position_occurrence.halfmove_clock` |
| `dgp_fullmove_number` | `INTEGER` | NOT NULL | `CHECK (dgp_fullmove_number >= 1)` | Fullmove number at this occurrence. | Computed from the replayed board. | `position_occurrence.fullmove_number` |

**Constraints summary.** `PRIMARY KEY (datasource_game_id, dgp_ply)` — settles the
direction's "each `(game_id, ply)` occurrence is distinct" with a composite PK and no
surrogate [catalogue decision: the old surrogate `position_occurrence.occurrence_id` is not
recreated; the composite key is the natural identity and the direction's occurrence
semantics need nothing more].

**Application-enforced invariants.** Exactly N+1 rows per N-move game; the initial
occurrence's outgoing move is the game's first move; the final occurrence's outgoing move is
NULL; a display FEN is reconstructed from the four identity fields plus
`dgp_halfmove_clock`/`dgp_fullmove_number`; SAN is derived on demand, never stored. Cross-row
move chaining cannot be expressed as a CHECK and is importer-enforced in one transaction per
game (direction section 3.4).

**Transformed field.** `dgp_move_uci` is not a 1:1 survivor of `position_occurrence.uci`:
the old table stored the move **entering** the occurrence (`scripts/chess_com/_replay.py:117-123`
records `san`/`uci` after pushing the move, with ply 0 NULL), while the new column stores the
move **leaving** it, so the same logical fact sits one ply earlier. See section 14.2.

---

## 6. `datasource_opening`

**Classification:** `datasource_` — external catalogue facts.
**Feeder tool (description only, NOT BUILT):** the opening catalogue builder (13.3).

**Purpose and ownership.** One semantic opening label from the retained
`lichess-org/chess-openings` source (direction section 3.5). The catalogue mirrors the
latest complete validated source set; labels no longer present are not preserved, and the
opening tables are published together as one unit.

**Source data.** The five external TSV files `a.tsv` through `e.tsv`, each row carrying
exactly `eco`, `name`, and `pgn` (direction section 4.4). Identical ECO+name rows from
multiple source routes collapse into one row here.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `do_opening_id` | `INTEGER` | NOT NULL | **PK** | Internal integer identity for route FKs. | Assigned by the catalogue builder at publication. | — `[NEW]` |
| `do_eco` | `TEXT` | NOT NULL | `CHECK (do_eco GLOB '[A-E][0-9][0-9]')`; `UNIQUE (do_eco, do_name)` | The ECO code of the label, kept verbatim. | TSV column `eco`. | `opening_catalog.eco` |
| `do_name` | `TEXT` | NOT NULL | `UNIQUE (do_eco, do_name)` | The opening name, kept verbatim. | TSV column `name`. | `opening_catalog.name` |

**Constraints summary.** `PRIMARY KEY (do_opening_id)`; `UNIQUE (do_eco, do_name)` —
settled by direction section 3.5.

**Keep-outs respected.** No permanent `parent_opening_id`, no classification state, no
recurrence/branch projections, no source history (direction section 3.5).

**New field.** `do_opening_id` is genuinely new: the old catalogue identified label rows by
a composite source-row identity (`manifest_hash`, `source_file`, `source_row_ordinal`) with
no label-level id, and that identity machinery is removed (direction section 2.5).

---

## 7. `derived_opening_route`

**Classification:** `derived_` — computed from the external PGNs.
**Feeder tool (description only, NOT BUILT):** the opening catalogue builder (13.3).

**Purpose and ownership.** One source move sequence that reaches an opening label; one
label may have multiple routes (direction section 3.6). Route relationships are
route-dependent because routes transpose.

**Source data.** Computed by replaying each TSV row's `pgn` column; the route's endpoint is
the canonical position reached by the final move of that PGN.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `dor_route_id` | `INTEGER` | NOT NULL | **PK** | Internal integer identity for the ordered move rows. | Assigned by the catalogue builder at publication. | — `[NEW]` |
| `datasource_opening_id` | `INTEGER` | NOT NULL | FK → `datasource_opening(do_opening_id)` `ON DELETE RESTRICT` | The semantic label this route reaches. | The TSV row's `eco`+`name` label. | — (transformed) |
| `derived_position_id` | `INTEGER` | NOT NULL | FK → `derived_position(dp_position_id)` `ON DELETE RESTRICT` | The route's unique canonical endpoint position. | The position reached by replaying the TSV row's `pgn`. | — (transformed) |

**Constraints summary.** `PRIMARY KEY (dor_route_id)`. There is exactly one route row per
distinct opening-label and move-sequence pair per publication. Duplicate source rows with
the same label and sequence collapse to that one route; no unique constraint beyond the PK
can express this because the sequence is deliberately stored as ordered child rows rather
than as a duplicate opaque parent value.

**Application-enforced invariants.** Exact duplicate move sequences for the same opening
label collapse to one route; route plies in `derived_opening_route_move` are contiguous
from 1 with no gaps; the route replay is legal move by move; and the final replayed position
equals the stored endpoint (`derived_position_id`). **Deliberately not added:** no opaque
move-sequence or hash column (direction section 3.7 rejects it), and no UNIQUE constraint on
`datasource_opening_id`+`derived_position_id`, which would wrongly collapse valid
transpositions — two different sequences may legitimately reach the same endpoint of the
same label as distinct routes (direction section 3.6).

**Keep-outs respected.** No shared-prefix tree, no forced hierarchy, no permanent parent
opening, no intermediate position links, no historical route versions (direction section
3.6).

**Transformed fields.** The old `opening_catalog` endpoint columns
(`endpoint_placement`, `endpoint_side_to_move`, `endpoint_castling`,
`endpoint_en_passant`) carried the endpoint identity denormalized; the new row replaces
them with one `derived_position_id` FK. `endpoint_fen`, `endpoint_halfmove_clock`, and
`endpoint_fullmove_number` have no successor (not part of position identity). The composite
`opening_catalog` row identity (`manifest_hash`, `source_file`, `source_row_ordinal`) and
its source-hash machinery have no successor (direction section 2.5). See section 14.3.

---

## 8. `derived_opening_route_move`

**Classification:** `derived_` — computed from the external PGNs.
**Feeder tool (description only, NOT BUILT):** the opening catalogue builder (13.3).

**Purpose and ownership.** The explicit ordered UCI moves of one route (direction section
3.7); one opaque move-sequence text is deliberately rejected.

**Source data.** Computed by replaying each TSV row's `pgn` column move by move.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `derived_opening_route_id` | `INTEGER` | NOT NULL | **PK part 1**; FK → `derived_opening_route(dor_route_id)` `ON DELETE CASCADE` | The route this move belongs to; moves are replaced together with their route at publication (child-first deletion, section 1.6). | The route being generated. | — (transformed) |
| `dorm_ply` | `INTEGER` | NOT NULL | **PK part 2**; `CHECK (dorm_ply >= 1)` | One-based ply of the move within the route; `(derived_opening_route_id, dorm_ply)` is the settled PK (direction section 3.7). | Position of the move in the replayed PGN. | — (transformed) |
| `dorm_move_uci` | `TEXT` | NOT NULL | `CHECK (dorm_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dorm_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]')` | The move in UCI; short routes are replayed for validation, recognition, and route-versus-transposition comparison. | Computed from the replayed PGN move. | — (transformed) |

**Constraints summary.** `PRIMARY KEY (derived_opening_route_id, dorm_ply)` — settled by
direction section 3.7.

**Application-enforced invariants.** See section 7: plies contiguous from 1, legal replay,
final replayed position equals the stored endpoint, and duplicate sequences per label
collapse to one route.

**Keep-outs respected.** No intermediate `position_id` links, no SAN duplicate, no
membership/hierarchy data (direction section 3.7).

**Transformed fields.** The old `opening_position_membership` rows carried
`manifest_hash`/`source_file`/`source_row_ordinal` context, `san`, `uci_prefix`, and the
four position-identity fields per ply. The new rows keep only route-relative `ply` and UCI;
everything else has no successor (SAN derived on demand; position identities recreated by
replaying the short route; `uci_prefix` was transposition-machinery, removed with
`opening_transposition_link`). See sections 14.3 and 15.

---

## 9. `derived_analysis_result`

**Classification:** `derived_` — engine-produced.
**Feeder tool (description only, NOT BUILT):** the Stockfish worker (13.4), serving both
viewer-triggered and bulk requests (direction section 4.2).

**Purpose and ownership.** The latest complete successful Stockfish result set for one
canonical position (direction section 3.8). Each position retains at most one successful
result plus its child candidate lines; interrupted or failed searches never publish partial
output.

**Canonical terminal policy [catalogue decision].** Shared analysis terminality — the
`dar_terminal_kind` fact on a position-level result — is limited to outcomes determined
**solely by the four-field canonical position**: the no-legal-move outcomes `checkmate` and
`stalemate`, and position-only dead/insufficient-material outcomes
(`insufficient_material`). Repetition and halfmove/fullmove-counter-dependent 50/75-move
outcomes are **excluded** from shared `derived_analysis_result`: they depend on game and
occurrence context that the canonical position deliberately does not carry (direction
section 3.2 keep-out of counters; direction section 3.8 keep-out of occurrence counters in
analysis identity). A game that ends by repetition or the fifty/seventy-five-move rule does
**not** make the shared position terminal. Consistently, analysis reconstructs a **neutral
root** from the four identity fields with halfmove clock `0`, fullmove number `1`, and no
repetition history, so the engine evaluates exactly the facts the canonical position owns.

**Source data.** Stockfish engine output on the position identified by `derived_position_id`
(reconstructed as the neutral root above), produced under the requesting quality level's
fixed node budget and current configuration.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `derived_position_id` | `INTEGER` | NOT NULL | **PK**; FK → `derived_position(dp_position_id)` `ON DELETE RESTRICT` | The analysed position; one row per position because at most one result set exists per position. The FK-as-PK naming follows section 1.4. | The position whose analysis was requested. | — (transformed) |
| `dar_quality` | `TEXT` | NOT NULL | `CHECK (dar_quality IN ('browser','tool'))` | The ordered quality level of this result (`browser` < `tool`); browser fills a missing result and never replaces tool; tool may replace browser. | The requesting quality level. | — `[NEW]` |
| `dar_configuration_version` | `INTEGER` | NOT NULL | `CHECK (dar_configuration_version >= 1)` | The quality level's explicit, manually incremented configuration version; a same-level result is replaced only when this or the engine version changes. | Maintained manually per level. | — `[NEW]` |
| `dar_settings_json` | `TEXT` | NOT NULL | `CHECK (json_valid(dar_settings_json))` | The actual settings used for this result. | The worker's settings record. | `analysis_result.settings_json` |
| `dar_engine_name` | `TEXT` | NOT NULL | — | The engine binary's name. | The worker's engine preflight. | `analysis_result.engine_name` |
| `dar_engine_version` | `TEXT` | NOT NULL | — | The engine's version; changes make a same-level result eligible for replacement. | The worker's engine preflight. | `analysis_result.engine_version` |
| `dar_terminal_kind` | `TEXT` | NULL | `CHECK (dar_terminal_kind IS NULL OR dar_terminal_kind IN ('checkmate','stalemate','insufficient_material'))` | For a terminal position under the canonical terminal policy above, the ending reason; all other positions leave it NULL. | Derived from the neutral-root analysis of the canonical position. | — (transformed; re-scoped) |

**Constraints summary.** `PRIMARY KEY (derived_position_id)` [catalogue decision: the
direction keys the result to `position_id` with at most one result set per position
(direction section 3.8), so the position FK is the PK and no surrogate id is added]; the
quality and terminal-kind CHECKs above.

**Application-enforced invariants.** A terminal position has a result with
`dar_terminal_kind` set and zero candidate lines, distinguishing "analysed and finished"
from "not analysed"; a non-terminal result has 1–5 lines (fewer than five only when the
position has fewer legal moves); replacement publishes only when the complete result and all
lines are ready; the old result stays visible during a same-level replacement. **Publication
re-check:** before publishing, the worker re-reads the stored result for the position so
that Browser never replaces an existing Tool result, and stale or same-level output cannot
replace a newer applicable result; publication writes the complete `derived_analysis_result`
row, all `derived_analysis_line` rows, and the queue transition or conditional deletion in
**one transaction**. The queue-side compare-and-swap on the claim token is specified in
section 11. None of these cross-row facts are CHECK-expressible; they are
worker-published invariants (direction sections 3.8, 4.2).

**New fields.** `dar_quality` and `dar_configuration_version` are genuinely new; together
they replace the old `profile_id`/`settings_fingerprint`/`schema_version` identity
mechanism (the old profile id was an opaque settings string such as
`mp09-balanced-nodes-v2-200000`). See section 14.4.

---

## 10. `derived_analysis_line`

**Classification:** `derived_` — engine-produced.
**Feeder tool (description only, NOT BUILT):** the Stockfish worker (13.4); lines are
published atomically with their parent result and replaced with it, never appended.

**Purpose and ownership.** One ranked candidate line of a complete
`derived_analysis_result` (direction section 3.9). Browser and Tool both request five
lines; fewer only when the position has fewer than five legal moves.

**Source data.** Stockfish multi-line output (`multipv`) for the parent position, including
score, win/draw/loss statistics, displayed depth, and the principal variation.

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `derived_analysis_result_id` | `INTEGER` | NOT NULL | **PK part 1**; FK → `derived_analysis_result(derived_position_id)` `ON DELETE CASCADE` | The complete result this line belongs to; lines have no independent life and are replaced with their result. | The parent analysis run. | — (transformed) |
| `dal_rank` | `INTEGER` | NOT NULL | **PK part 2**; `CHECK (dal_rank BETWEEN 1 AND 5)` | The candidate's rank (1 = best). | Engine `multipv` rank. | `analysis_candidate.rank` |
| `dal_score_kind` | `TEXT` | NOT NULL | `CHECK (dal_score_kind IN ('cp','mate'))` | Whether `dal_score_value` is centipawns or moves-to-mate. | Engine score type. | — (transformed) |
| `dal_score_value` | `INTEGER` | NOT NULL | — | Centipawn-or-mate score **from White's point of view**: positive favors White, negative favors Black. | Engine score, signed per the White-POV convention. | — (transformed) |
| `dal_wdl_wins` | `INTEGER` | NOT NULL | `CHECK (dal_wdl_wins >= 0)`; table CHECK `dal_wdl_wins + dal_wdl_draws + dal_wdl_losses = 1000` | Win-draw-loss statistic: wins (per-mille). | Engine WDL output. | `analysis_candidate.wdl_wins` |
| `dal_wdl_draws` | `INTEGER` | NOT NULL | `CHECK (dal_wdl_draws >= 0)`; table CHECK above | Win-draw-loss statistic: draws (per-mille). | Engine WDL output. | `analysis_candidate.wdl_draws` |
| `dal_wdl_losses` | `INTEGER` | NOT NULL | `CHECK (dal_wdl_losses >= 0)`; table CHECK above | Win-draw-loss statistic: losses (per-mille). | Engine WDL output. | `analysis_candidate.wdl_losses` |
| `dal_pv_uci_json` | `TEXT` | NOT NULL | `CHECK (json_valid(dal_pv_uci_json) AND json_type(dal_pv_uci_json) = 'array' AND json_array_length(dal_pv_uci_json) > 0)` | The complete principal variation as one ordered, **non-empty** JSON list of legal UCI moves; the application reads it whole and may select the next move from it. | Engine principal variation. | `analysis_candidate.pv_uci_json` |
| `dal_depth` | `INTEGER` | NOT NULL | `CHECK (dal_depth >= 0)` | The displayed search depth. | Engine depth output. | `analysis_candidate.depth` |

**Constraints summary.** `PRIMARY KEY (derived_analysis_result_id, dal_rank)` — mirroring
the old `(position_key, rank)` shape with the new key scheme; the score-kind, WDL-domain,
WDL-sum (`= 1000`), non-empty-PV-array, and depth CHECKs above.

**Application-enforced invariants.** For each complete result, ranks are contiguous
1..N with no holes; N is exactly five unless the position has fewer than five legal root
moves; the candidate lines' first (root) moves are distinct from one another and are legal
moves of the canonical root; and every stored principal variation is the complete
engine-returned sequence, legal move by move from the canonical root. These cross-row and
engine-truth facts are not CHECK-expressible; they are publication invariants of the worker.

**Keep-outs respected.** No selective depth, node counts, per-line engine time, one-row-per-
PV-move normalization, or partial lines (direction section 3.9). The old columns `fen`,
`seldepth`, `nodes`, and `engine_time_ms` have no successor (section 15).

**Transformed fields.** `dal_score_kind`/`dal_score_value` are transformed, not 1:1: the
old `cp`/`mate`/`mate_given` domain with its paired per-line representation is replaced by
the two-value domain (`cp`, `mate`) with `dal_score_value` carrying the score directly. The
old `cp` and `mate` values already used **signed White-POV semantics** — the old system
never stored unsigned scores — so the sign convention is preserved unchanged; the
transformation is the replacement of the `mate_given` domain/paired representation, not a
change of sign convention. `derived_analysis_result_id` is transformed because the parent
key changed from text position keys to the integer result key. `analysis_candidate.depth`
remains a genuine 1:1 survivor as `dal_depth`; the rebuilt CHECK (`>= 0`) preserves the old
column's semantics without narrowing its value domain. See section 14.4.

---

## 11. `derived_analysis_queue`

**Classification:** `derived_` — live operational coordination (borderline rationale in
section 1.3).
**Feeder tools (description only, NOT BUILT):** viewer analysis requests insert/promote rows
(13.5); the Stockfish worker claims, completes, releases, or deletes them (13.4).

**Purpose and ownership.** The minimal database work queue coordinating viewer Analyze,
Update, and Retry requests (direction section 3.10). It holds only live state; completed
and failed work leaves no trace.

**Source data.** Viewer runtime requests (position, requested quality, request time) plus
worker-claimed state (claim timestamp and claim token).

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `derived_position_id` | `INTEGER` | NOT NULL | **PK**; FK → `derived_position(dp_position_id)` `ON DELETE RESTRICT` | The position whose analysis is requested; one live request per position. FK-as-PK naming per section 1.4. | The viewer request's position. | — (transformed) |
| `daq_requested_quality` | `TEXT` | NOT NULL | `CHECK (daq_requested_quality IN ('browser','tool'))` | The currently requested quality level, honoring the no-downgrade rules of direction section 4.2. | The highest-quality live viewer request for the position. | — `[NEW]` |
| `daq_state` | `TEXT` | NOT NULL | `CHECK (daq_state IN ('queued','running'))` | Live state only: queued or running. Done rows are deleted; failures are never stored. | Set by the request and the worker's transactional claim. | — (transformed) |
| `daq_requested_at_utc` | `TEXT` | NOT NULL | — | When the (current) request was made; used to honor request ordering. | The viewer request time. | `evaluation_queue.enqueued_at` |
| `daq_claimed_at_utc` | `TEXT` | NULL | Exact state/claim invariant CHECK below | When the current claim was taken; NULL while queued. | The worker at claim time. | — `[NEW]` |
| `daq_claim_token` | `TEXT` | NULL | `UNIQUE`; exact state/claim invariant CHECK below | Fresh unique claim token assigned at each claim; the compare-and-swap key for publication, release, and completion, so a superseded (stale) worker cannot act on a row reclaimed by another worker. | The worker at claim time (freshly generated, unique per claim). | — `[NEW]` |

**Constraints summary.** `PRIMARY KEY (derived_position_id)` [catalogue decision: the
direction's queue contains "position; requested quality; queued or running state; request
time" plus the claim machinery the retry workflow needs, and one live request per position
is the settled shape, so the position FK is the PK, exactly the six columns above, and
nothing more]; `UNIQUE (daq_claim_token)`; and the **exact state/claim invariant**:

```sql
CHECK (
  (daq_state = 'queued'
     AND daq_claimed_at_utc IS NULL AND daq_claim_token IS NULL)
  OR
  (daq_state = 'running'
     AND daq_claimed_at_utc IS NOT NULL AND daq_claim_token IS NOT NULL)
)
```

Queued rows have both claim timestamp and token NULL; running rows have both non-NULL. The
stale-claim threshold is worker behavior, not stored state.

**Application-enforced invariants (queue concurrency algorithm).**

1. **Atomic max-quality UPSERT.** A viewer request for a position with no live row inserts
   one. A request for a position with a live row is an UPSERT that raises
   `daq_requested_quality` to the maximum of the stored and requested quality: a new Tool
   request promotes a queued **or running** Browser request without downgrading any Tool
   request, and without destroying an active claim (state, claim timestamp, and token are
   untouched by a promotion of a running row). A duplicate or lower request never lowers the
   requested quality.
2. **Transactional claim.** A worker claims a row in one conditional transaction: only a
   `queued` row, or a `running` row whose claim has gone stale (its `daq_claimed_at_utc`
   older than the worker's stale threshold), may be claimed. On claim the worker records its
   **worker-local immutable claimed quality** (the `daq_requested_quality` value observed at
   claim time) and assigns a fresh unique `daq_claim_token`, together setting
   `daq_claimed_at_utc`. Stale reclaim **replaces the token**, so the superseded worker's
   token no longer matches and it cannot act.
3. **Compare-and-swap publication.** Publication, release, and completion are
   compare-and-swap operations on the current `daq_claim_token`. If the stored token no
   longer matches the worker's token, the worker's output is **stale: it is discarded, and
   nothing is published, transitioned, or deleted**.
4. **Pre-publication re-check.** Before publishing, the worker re-reads the stored
   `derived_analysis_result` for the position so Browser never replaces an existing Tool
   result and stale or same-level output cannot replace a newer applicable result; the
   complete result, all lines, and the queue transition/deletion are written in **one
   transaction** (section 9).
5. **Promotion while running.** If `daq_requested_quality` was promoted above the worker's
   claimed quality while a Browser run was executing, the Browser output may still publish
   (provided no Tool result exists for the position), but the worker must then **release**
   the row back to `queued` state with the now-higher requested quality — clearing the
   claim timestamp and token — rather than delete it. In every other successful case the
   worker conditionally deletes the row whose token still matches.
6. **Matching-token engine failure.** A matching-token engine failure leaves **no failure
   history** (direction section 3.10): if the row's requested quality was promoted above
   the claimed quality, the worker releases the row back to `queued` so the
   higher-quality work proceeds; otherwise it conditionally deletes the row so the
   position's analysis can be requested again later. A stale (non-matching) token
   discards output and touches nothing, per invariant 3.

**Keep-outs respected.** No completed-job history, failed-job rows, batch history, run
records, audit trail, or shared JSON queue (direction section 3.10). The old columns `fen`,
`position` (FIFO ordinal), `attempts`, `schema_version`, `started_at`, `finished_at`,
`last_error_code`, and `last_error_details` have no successor: an isolated Stockfish error
is printed for that run and skipped, with no database record (direction section 3.10).

---

## 12. `datasource_preferred_move_period`

**Classification:** `datasource_` — direct user input (borderline rationale in section
1.3).
**Feeder tool (description only, NOT BUILT):** the application's preferred-move writes
(13.6).

**Purpose and ownership.** The user-owned preferred-move, explicit no-preference choice, or
absence of configuration for a position across editable half-open UTC calendar-date periods
(direction section 3.11). The rebuilt database starts empty; no current preference rows
migrate.

**Source data.** The user's preferred-move choices in the viewer, plus the validated
position/FEN supplied in the preference operation for any standalone position a preference
introduces.

**Table name** [catalogue decision]: `datasource_preferred_move_period` names the settled
concept directly — user-input facts (datasource) in period form — and satisfies the
direction's "the final table name is not settled" delegation (direction section 3.11).

| Exact name | Type | Null/Default | Key/Constraints | Purpose | Source | Old exact 1:1 field |
| --- | --- | --- | --- | --- | --- | --- |
| `derived_position_id` | `INTEGER` | NOT NULL | **PK part 1**; FK → `derived_position(dp_position_id)` `ON DELETE RESTRICT` | The position the period configures. | The validated position/FEN supplied in the preference operation (created canonically if standalone, direction section 3.11). | — (transformed) |
| `dpm_effective_from` | `TEXT` | NOT NULL | **PK part 2**; `CHECK (dpm_effective_from GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(dpm_effective_from) IS NOT NULL AND dpm_effective_from = date(dpm_effective_from))` | First UTC calendar date the period applies to (**inclusive start** of the half-open range). | The user's chosen start (today for the ordinary viewer action). | — (transformed) |
| `dpm_effective_until` | `TEXT` | NULL | `CHECK (dpm_effective_until IS NULL OR (dpm_effective_until GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(dpm_effective_until) IS NOT NULL AND dpm_effective_until = date(dpm_effective_until) AND dpm_effective_until > dpm_effective_from))` | First UTC calendar date after the period (exclusive); NULL means the period continues indefinitely. A preference displayed as 1–5 January is stored `[2025-01-01, 2025-01-06)`. | Derived when periods are split or ended by later edits. | — `[NEW]` |
| `dpm_move_uci` | `TEXT` | NULL | `CHECK (dpm_move_uci IS NULL OR dpm_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dpm_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]')` | The preferred move when one is preferred; NULL means deliberately no preference for the period. No covering row means unconfigured — no extra state column exists. May be any legal move from the position, not only moves seen in games or routes. | The user's move choice. | — (transformed) |

**Constraints summary.** `PRIMARY KEY (derived_position_id, dpm_effective_from)`
[catalogue decision: the direction's conceptual shape has exactly four fields
(position_id, effective_from, effective_until, move_uci) and "no extra state column";
with the non-overlap invariant below, at most one period per position can start on a given
date, so the position FK plus the start date is the complete identity and no surrogate id is
added]; the canonical-shape-and-valid-date CHECKs above on both date columns.

**Application-enforced invariants.**

- **Period non-overlap.** Periods for one position must not overlap (direction section
  3.11). SQLite has no declarative exclusion constraint, so every overlap check, every
  split/shorten/delete, and the resulting writes occur in **one `BEGIN IMMEDIATE` SQLite
  transaction**, with the overlap condition re-evaluated while holding the writer lock, so
  concurrent local writers cannot interleave. This is never done by a trigger (direction
  section 3.11 keep-out: no no-update/no-delete triggers).
- **Preferred-move legality.** `dpm_move_uci`, when non-NULL, must be a legal move of the
  referenced position. The chosen move is validated from the position (the validated
  position/FEN supplied in the preference operation, or the stored canonical position);
  SQLite cannot replay chess, so this is producer-enforced.
- Historical periods are editable, not append-only.

**Keep-outs respected.** No extra state column, no timestamp-precision semantics, no
append-only history restrictions, no requirement that the move occur in a game or route
(direction section 3.11).

**New field.** `dpm_effective_until` is genuinely new: the old event-sourced storage had no
period end. `dpm_move_uci` is transformed, not 1:1: NULL meant "removal event" in the old
append-only model and means "explicit no-preference period" in the new model. See section
14.5.

---

## 13. Feeding tools and data flow — **NOT BUILT, descriptions only**

> **This entire section is a description of tools that would feed the tables. Nothing here
> is built, and nothing here authorizes building** (direction section 8). It records the
> intended feeding order so the catalogue's source columns have an owner.

### 13.1 Data-flow order (description only)

```text
Chess.com monthly archives (raw files, fetch ledger)
  └─> [Game importer]            -> datasource_game, derived_position, derived_game_position
lichess-org/chess-openings TSVs (raw files)
  └─> [Opening catalogue builder] -> datasource_opening, derived_opening_route,
                                     derived_opening_route_move, derived_position (endpoints)
Viewer requests
  └─> [Viewer analysis requests]  -> derived_analysis_queue (insert or max-quality UPSERT)
  └─> [Preferred-move writes]     -> datasource_preferred_move_period,
                                     derived_position (standalone preference positions)
derived_analysis_queue
  └─> [Stockfish worker]          -> claims/updates/deletes derived_analysis_queue;
                                     publishes derived_analysis_result, derived_analysis_line
Bulk Tool selection (on-demand game query + opening-route replay)
  └─> [Stockfish worker]          -> creates/reuses derived_position for route-only
                                     intermediate positions; writes derived_analysis_result,
                                     derived_analysis_line directly; no queue rows
All readers (viewer, statistics, opening lookup) — read-only; no persisted projections.
```

### 13.2 Game importer (description only)

Reads the raw month files (the fetch ledger; existing months skipped, current month
refetched and merged by game UUID, direction section 2.5). For each archive game: accept
only standard chess from the normal initial board with the configured trainer UUID; replay
and validate the PGN; then in **one transaction per game** write `datasource_game`,
create-or-reuse `derived_position` rows, and write the complete `derived_game_position`
occurrence set. A malformed PGN or illegal move prints a warning for that run and skips the
game; a valid correction replaces one game's metadata and occurrences in one transaction;
**an invalid game correction performs no update or deletion — the prior `datasource_game`
and `derived_game_position` rows remain unchanged.** No fetch-state, run-history, or failure
rows exist.

### 13.3 Opening catalogue builder (description only)

Reads the five TSV files, replays every route PGN, and publishes the complete catalogue —
`datasource_opening`, `derived_opening_route`, `derived_opening_route_move`, and the
`derived_position` endpoint rows — as one unit: one malformed or illegal route rejects the
entire update and leaves the previous working catalogue active (direction section 3.5).
Within the single publication transaction, rows are deleted **child-first**
(`derived_opening_route_move` before `derived_opening_route` before `datasource_opening`;
section 1.6). Routes and endpoints are recomputed; no manifest/hash/state machinery is
retained.

### 13.4 Stockfish worker (description only)

**Viewer live requests** use `derived_analysis_queue` exactly as specified in section 11:
the worker claims a queued or stale-running row transactionally (recording its immutable
worker-local claimed quality and a fresh unique claim token), runs Stockfish **outside** the
database transaction under the claimed quality's fixed node budget, re-checks the stored
result and the claim token before publishing, and then either publishes the complete
`derived_analysis_result` row with all `derived_analysis_line` rows and conditionally
deletes the queue row, or — when the requested quality was promoted above the claimed
quality — releases the row back to queued work instead of deleting it. A matching-token
engine failure releases promoted work or conditionally deletes the row, never storing a
failure record. A stale token discards the output entirely.

**Bulk Tool work is separate from the queue:** it selects its targets on demand (the
direction section 4.2 selection: every unique position reached from imported games or
opening routes for plies 0 through 19 where moves in full moves 1 through 10 are about to be
played). Game targets come from `derived_game_position` and are ordered by descending
occurrence count. Opening-route targets come from legally replaying
`derived_opening_route_move`; each pre-move position through ply 19 is canonicalized and its
`derived_position` row is created or reused as needed. The two sets are unioned by canonical
position identity, with route-only positions assigned frequency zero and processed after
game positions. This is an on-demand selection, **not** a persisted target table and **not**
a queue user. The direction's initial 25-position mixture uses this same direct analysis and
publication path with its separately bounded mix of common and technical positions; that
target list is not persisted. Bulk results are written **directly** to
`derived_analysis_result` and `derived_analysis_line` through the same publication rules:
pre-publication re-check against the stored result (no-downgrade, no stale/same-level
replacement), complete result + all lines in one transaction, no partial output, and no
failure records.

Browser fills a missing result and never replaces Tool; Tool may replace Browser;
same-level replacement happens only when `dar_configuration_version` or
`dar_engine_version` changed; interrupted running work becomes available again via the
stale-claim rule.

### 13.5 Viewer analysis requests (description only)

The viewer inserts a `derived_analysis_queue` row (position, requested quality, request
time) for Analyze/Update/Retry, or performs the atomic max-quality UPSERT of section 11
when a live row already exists, honoring the skip and no-downgrade rules of direction
section 4.2. No API shape is specified here; rebuilt APIs are separate later work
(direction section 7, item 4).

### 13.6 Preferred-move writes (description only)

The application writes `datasource_preferred_move_period` rows: starting a preference today
opens a period with `dpm_effective_until` NULL; choosing another move or "No preferred
move" ends the previous period and opens the new one; dated edits split or shorten
overlapping periods while preserving outside dates; deleting a period leaves those dates
unconfigured. Every overlap check, split/shorten/delete, and the resulting writes happen in
one `BEGIN IMMEDIATE` transaction with the overlap condition rechecked under the writer
lock (section 12). A preference for a position not already canonically stored creates a
valid `derived_position` row **from the validated position/FEN supplied in the preference
operation** — not by replaying the chosen outgoing move; the chosen move is then validated
as legal from that source position. SAN is derived for display, never stored.

### 13.7 Readers (description only)

The game viewer, Position Context (`COUNT(DISTINCT datasource_game_id)` per position and
trainer color), Move Response Distribution (occurrence counts grouped by outgoing
`dgp_move_uci`, actor derived from `dg_trainer_color` and `dp_side_to_move`), opening
lookup (route replay and endpoint matching), and preferred-move reads all query the tables
directly with no materialized summaries (direction sections 3.12, 4.3, 4.4).

---

## 14. Old-database comparison

Old-schema evidence: `data/database/schema.txt` (generated from the repository DDL) and the
source semantics of `scripts/chess_com/_replay.py`. Per section 1.2, "1:1" means same fact,
same value domain, direct-copy derivation — names may differ; values are regenerated, not
migrated; nullability/integrity tightening alone does not defeat 1:1, but conversion,
re-keying, re-selection, shifting, or re-scoping does. Nine old tables are **replaced** by
new tables; the remaining **40 are removed** with no successor. Section 15 enumerates every
old field of every old table individually.

### 14.1 `games` → `datasource_game`

| Old exact field | New exact field | Relationship |
| --- | --- | --- |
| `games.uuid` | `dg_chesscom_game_uuid` | **1:1** (renamed; same fact, same value domain). |
| `games.url` | `dg_source_url` | **1:1** (renamed). |
| `games.pgn` | `dg_original_pgn` | **1:1** (renamed). |
| `games.time_control` | `dg_time_control_source` | **1:1** (renamed; old `NOT NULL`, new nullable — nullability relaxation alone, section 1.2). |
| `games.time_class` | `dg_time_class` | **1:1** (same value domain; nullability unchanged). |
| `games.white_player_uuid` / `games.black_player_uuid` | `dg_trainer_chesscom_uuid` / `dg_opponent_chesscom_uuid` | **Transformed**: the old pair of side-keyed columns is re-selected by trainer color into trainer/opponent columns; which old column feeds which new column depends on the game. The FK to `players` is dropped with that table. |
| `games.white_rating` / `games.black_rating` | `dg_trainer_rating` / `dg_opponent_rating` | **Transformed**: same conditional side-to-perspective re-selection. |
| `games.white_result` / `games.black_result` | `dg_trainer_outcome` + `dg_termination_reason` | **Transformed**: two raw result codes are re-derived into a normalized win/loss/draw outcome plus the termination-bearing code (decisive game: the non-`win` participant's code; draw: the common draw code when determinable; PGN `Termination` header fallback; otherwise NULL); value domain changes. |
| `games.end_time` | `dg_ended_at_utc` | **Transformed**: epoch seconds converted to ISO-8601 UTC text. |
| `games.rated` | — | Removed (explicit keep-out, direction section 3.3). |
| `games.tcn` | — | Removed (keep-out). |
| `games.eco` | — | Removed (Chess.com ECO URL; keep-out). |
| `games.fen`, `games.initial_setup` | — | Removed (final/initial FEN columns; keep-out; the facts remain in raw JSON and the exact PGN). |
| `games.white_accuracy`, `games.black_accuracy` | — | Removed (keep-out). |
| `games.tournament`, `games.match` | — | Removed (keep-out). |
| `games.year`, `games.month` | — | Removed: month provenance lives in the raw month files, which are the fetch ledger; no database column is needed. |
| `games.rules` | — | Removed as a column: standard chess is an intake acceptance rule (`rules = 'chess'` filter, direction section 4.1; the old `corpus_game` CHECK held the same rule), so only accepted games exist and no stored column is needed. |
| — | `dg_game_id` | **[NEW]** internal integer PK (old PK was the UUID text itself). |
| — | `dg_trainer_color` | **[NEW]** stored explicitly; old systems derived it by comparing `white_player_uuid`/`black_player_uuid` with `corpus.subject_player_uuid`. |
| — | `dg_started_at_utc` | **[NEW]** column; the start time existed only inside the PGN headers (`UTCDate` + `UTCTime`, with `Date` + `StartTime` fallback). |

### 14.2 `position_state` → `derived_position`; `position_occurrence` → `derived_game_position`

| Old exact field | New exact field | Relationship |
| --- | --- | --- |
| `position_state.state_id` | `dp_position_id` | **Transformed (re-keyed)**: freshly assigned integer identities against the legal-only canonical four-field key; IDs never migrate, so the keying itself changed. `dp_position_id` is marked `[NEW]` for that reason (section 4). |
| `position_state.placement` | `dp_placement` | **1:1** (old nullable, new NOT NULL plus producer validation — integrity tightening alone, section 1.2). |
| `position_state.side_to_move` | `dp_side_to_move` | **1:1** (same fact; new CHECK is integrity tightening). |
| `position_state.castling` | `dp_castling_rights` | **1:1** (renamed). |
| `position_state.en_passant` | `dp_legal_en_passant` | **Transformed**: old values were classic FEN markers (`en_passant="fen"` generation); new values are legal-only normalized, so the same position can hold different values. |
| `position_occurrence.ply` | `dgp_ply` | **1:1** (same occurrence index domain). |
| `position_occurrence.state_id` | `derived_position_id` | **Transformed (re-keyed)**: the occurrence's canonical-position reference is re-keyed from the old freshly-generated `state_id` keys to the new freshly-assigned `dp_position_id` keys; also renamed per the section 1.4 convention. |
| `position_occurrence.uci` | `dgp_move_uci` | **Transformed**: old stored the move *entering* the occurrence; new stores the move *leaving* it (one-ply shift). |
| `position_occurrence.san` | — | Removed (derived for display, never stored, direction section 3.4). |
| `position_occurrence.halfmove_clock` | `dgp_halfmove_clock` | **1:1**. |
| `position_occurrence.fullmove_number` | `dgp_fullmove_number` | **1:1**. |
| `position_occurrence.game_uuid` | `datasource_game_id` | **Transformed**: text UUID FK re-keyed to the integer game PK. |
| `position_occurrence.occurrence_id` | — | Removed (surrogate replaced by the composite PK `(datasource_game_id, dgp_ply)`). |

### 14.3 `opening_catalog` → `datasource_opening` + `derived_opening_route` + `derived_opening_route_move`

| Old exact field | New exact field | Relationship |
| --- | --- | --- |
| `opening_catalog.eco` | `do_eco` | **1:1** (same value domain; row semantics change from one-row-per-source-row to one-row-per-label). |
| `opening_catalog.name` | `do_name` | **1:1** (same). |
| `opening_catalog.move_sequence` | `derived_opening_route_move` rows (`dorm_move_uci`, ordered by `dorm_ply`) | **Transformed**: one opaque sequence text replaced by explicit ordered child rows (direction section 3.7 rejects the opaque form). |
| `opening_catalog.endpoint_placement` / `.endpoint_side_to_move` / `.endpoint_castling` / `.endpoint_en_passant` | `derived_opening_route.derived_position_id` | **Transformed**: denormalized endpoint identity replaced by one canonical-position FK. |
| `opening_catalog.endpoint_fen` | — | Removed (display FEN reconstructable; not part of identity). |
| `opening_catalog.endpoint_halfmove_clock` / `.endpoint_fullmove_number` | — | Removed (counters are not part of shared identity, direction section 3.2). |
| `opening_catalog.manifest_hash`, `.source_file`, `.source_row_ordinal`, `.source_row_hash` | — | Removed (manifest/hash machinery; direction section 2.5 forbids persistent source hashes and accepted-manifest pointers). |
| `opening_position_membership.ply` | `dorm_ply` | **Transformed**: route-local context replaces the manifest/file/ordinal context. |
| `opening_position_membership.uci` | `dorm_move_uci` | **Transformed** (context change; value domain preserved). |
| `opening_position_membership.placement` / `.side_to_move` / `.castling` / `.en_passant` | — | Removed (intermediate positions are recreated by replaying the short route, direction section 3.7). |
| `opening_position_membership.san` | — | Removed (derived on demand). |
| `opening_position_membership.uci_prefix` | — | Removed (transposition-link machinery; transposition status is computed at request time). |
| `opening_position_membership.manifest_hash`, `.source_file`, `.source_row_ordinal` | — | Removed (composite source-row identity machinery; direction section 2.5). |
| — | `do_opening_id`, `dor_route_id` | **[NEW]** surrogate ids replacing the composite source-row identities. |

### 14.4 `analysis_result` + `analysis_candidate` → `derived_analysis_result` + `derived_analysis_line`

| Old exact field | New exact field | Relationship |
| --- | --- | --- |
| `analysis_result.settings_json` | `dar_settings_json` | **1:1**. |
| `analysis_result.engine_name` | `dar_engine_name` | **1:1**. |
| `analysis_result.engine_version` | `dar_engine_version` | **1:1**. |
| `analysis_result.terminal_kind` | `dar_terminal_kind` | **Transformed (re-scoped)**: the old column recorded whatever terminal kind the producing pipeline set; the shared new fact covers only position-only outcomes (`checkmate`, `stalemate`, `insufficient_material`) determined solely by the canonical position. Repetition and counter-dependent 50/75-move endings are game/occurrence context, not shared terminal facts (section 9). |
| `analysis_result.position_key` | `derived_position_id` | **Transformed**: text position key re-keyed to the integer canonical-position PK; also becomes the child lines' FK basis. |
| `analysis_result.fen` | — | Removed (display FEN reconstructable from position identity plus occurrence counters). |
| `analysis_result.schema_version`, `.settings_fingerprint`, `.profile_id` | `dar_quality` + `dar_configuration_version` | **[NEW]** replacement mechanism: the old opaque profile string (e.g. `mp09-balanced-nodes-v2-200000`) and fingerprint/version markers are replaced by the explicit quality level plus a manually incremented per-level configuration version (direction sections 3.8, 4.2). |
| `analysis_result.engine_binary_sha256` | — | Removed: engine identity is carried by `dar_engine_name`/`dar_engine_version`; a persisted binary hash is unneeded provenance for the local pinned engine. |
| `analysis_result.candidate_count` | — | Removed (derivable from the child rows; storing it duplicates one fact). |
| `analysis_result.completed_at` | — | Removed (completion timestamps kept merely for diagnostics are an explicit keep-out, direction section 3.8). |
| `analysis_result.wall_time_ms` | — | Removed (total wall time is an explicit keep-out). |
| `analysis_candidate.rank` | `dal_rank` | **1:1** (same domain and CHECK). |
| `analysis_candidate.wdl_wins` / `.wdl_draws` / `.wdl_losses` | `dal_wdl_wins` / `dal_wdl_draws` / `dal_wdl_losses` | **1:1** (the rebuilt `= 1000` sum CHECK is integrity tightening of the engine's per-mille convention, section 1.2). |
| `analysis_candidate.pv_uci_json` | `dal_pv_uci_json` | **1:1** (same JSON-array-of-UCI domain; the new non-empty CHECK is integrity tightening). |
| `analysis_candidate.depth` | `dal_depth` | **1:1** (genuine 1:1 semantics; the rebuilt CHECK `>= 0` preserves the old column's value domain). |
| `analysis_candidate.score_kind` | `dal_score_kind` | **Transformed**: the old `cp`/`mate`/`mate_given` domain is replaced by the two-value `cp`/`mate` domain. The old `cp` and `mate` values already used signed White-POV semantics, which are preserved unchanged; only the domain/paired representation is replaced. |
| `analysis_candidate.score_value` | `dal_score_value` | **Transformed**: the `mate_given` paired representation is folded into the two-value signed White-POV score; the sign convention itself is unchanged from the old `cp`/`mate` values. |
| `analysis_candidate.position_key` | `derived_analysis_result_id` | **Transformed**: the child lines' text position key re-keyed to the integer result PK (which is itself the position FK). |
| `analysis_candidate.fen` | — | Removed (parent result's `fen` successor is likewise removed). |
| `analysis_candidate.seldepth` | — | Removed (explicit keep-out, direction section 3.9). |
| `analysis_candidate.nodes` | — | Removed (keep-out). |
| `analysis_candidate.engine_time_ms` | — | Removed (keep-out). |

### 14.5 `evaluation_queue` → `derived_analysis_queue`; `opening_preferred_move_event` → `datasource_preferred_move_period`

| Old exact field | New exact field | Relationship |
| --- | --- | --- |
| `evaluation_queue.enqueued_at` | `daq_requested_at_utc` | **1:1** (renamed; same fact, same TEXT timestamp domain). |
| `evaluation_queue.position_key` | `derived_position_id` | **Transformed**: text key re-keyed to the integer position PK. |
| `evaluation_queue.state` | `daq_state` | **Transformed**: domain narrowed from `queued`/`running`/`done`/`failed` to `queued`/`running`; done rows are deleted and failures are never stored. |
| `evaluation_queue.fen` | — | Removed (the referenced position carries the identity). |
| `evaluation_queue.position` | — | Removed (FIFO ordinal; the minimal queue needs no stored ordering counter). |
| `evaluation_queue.attempts` | — | Removed (no attempt counting; isolated errors are printed and skipped). |
| `evaluation_queue.schema_version` | — | Removed (schema version is database-wide `PRAGMA user_version`). |
| `evaluation_queue.started_at`, `.finished_at` | — | Removed (live state only; `daq_claimed_at_utc` covers the claim). |
| `evaluation_queue.last_error_code`, `.last_error_details` | — | Removed (no failure records, direction section 3.10). |
| — | `daq_requested_quality`, `daq_claimed_at_utc`, `daq_claim_token` | **[NEW]** requested quality and the claim/recovery machinery (timestamp plus unique compare-and-swap token). |
| `opening_preferred_move_event.move_uci` | `dpm_move_uci` | **Transformed**: same UCI value domain when a move is preferred, but NULL changed meaning from "removal event" to "explicit no-preference period". |
| `opening_preferred_move_event.effective_at` | `dpm_effective_from` (+ `dpm_effective_until`) | **Transformed**: instant timestamp replaced by half-open calendar-date periods. |
| `opening_preferred_move_event.player_uuid` | — | Removed (single-user application; storing the actor is redundant, direction section 3.2/3.11 spirit). |
| `opening_preferred_move_event.action` | — | Removed (period state replaces set/remove event verbs). |
| `opening_preferred_move_event.move_san` | — | Removed (SAN derived for display, direction section 3.11). |
| `opening_preferred_move_event.recorded_at` | — | Removed (append-only bookkeeping has no successor). |
| `opening_preferred_move_event.event_id` | — | Removed (surrogate replaced by the composite period PK). |
| `opening_preferred_move_event.placement` / `.side_to_move` / `.castling` / `.en_passant` (composite FK) | `derived_position_id` | **Transformed**: four-column composite position FK replaced by one integer FK. |
| — | `dpm_effective_until` | **[NEW]** half-open period end. |

---

## 15. Old tables and fields removed or replaced — complete accounting

Final section. Every one of the 49 old tables in `data/database/schema.txt` and **every one
of their exact fields** is enumerated below with its disposition. Dispositions:
**1:1** (genuine 1:1 survivor; new exact name given), **transformed** (survives with changed
fact/keying/domain; new exact name given), **removed** (no successor anywhere), **replaced
by new mechanism** (a `[NEW]` field or non-table mechanism takes the fact over), or
**replaced by `PRAGMA user_version`** (non-table schema-version mechanism, section 2).

### 15.1 Replaced tables — every field enumerated

1. `games` → `datasource_game`:
   - `games.uuid` — 1:1 → `dg_chesscom_game_uuid`.
   - `games.url` — 1:1 → `dg_source_url`.
   - `games.pgn` — 1:1 → `dg_original_pgn`.
   - `games.time_control` — 1:1 → `dg_time_control_source`.
   - `games.end_time` — transformed (epoch seconds → ISO-8601 UTC) → `dg_ended_at_utc`.
   - `games.rated` — removed.
   - `games.tcn` — removed.
   - `games.initial_setup` — removed (fact remains in raw JSON and the exact PGN).
   - `games.fen` — removed (same).
   - `games.time_class` — 1:1 → `dg_time_class`.
   - `games.rules` — removed as a column (intake acceptance filter, section 14.1).
   - `games.eco` — removed.
   - `games.white_player_uuid` — transformed (conditional re-selection) → `dg_trainer_chesscom_uuid` or `dg_opponent_chesscom_uuid` by trainer color.
   - `games.black_player_uuid` — transformed (conditional re-selection) → `dg_trainer_chesscom_uuid` or `dg_opponent_chesscom_uuid` by trainer color.
   - `games.white_rating` — transformed (conditional re-selection) → `dg_trainer_rating` or `dg_opponent_rating` by trainer color.
   - `games.black_rating` — transformed (conditional re-selection) → `dg_trainer_rating` or `dg_opponent_rating` by trainer color.
   - `games.white_result` — transformed → `dg_trainer_outcome` and/or `dg_termination_reason`.
   - `games.black_result` — transformed → `dg_trainer_outcome` and/or `dg_termination_reason`.
   - `games.white_accuracy` — removed.
   - `games.black_accuracy` — removed.
   - `games.tournament` — removed.
   - `games.match` — removed.
   - `games.year` — removed (month-file provenance).
   - `games.month` — removed (month-file provenance).
2. `position_state` → `derived_position`:
   - `position_state.state_id` — transformed (re-keyed; IDs freshly assigned) → `dp_position_id` `[NEW]`.
   - `position_state.placement` — 1:1 → `dp_placement`.
   - `position_state.side_to_move` — 1:1 → `dp_side_to_move`.
   - `position_state.castling` — 1:1 → `dp_castling_rights`.
   - `position_state.en_passant` — transformed (legal-only normalization) → `dp_legal_en_passant`.
3. `position_occurrence` → `derived_game_position`:
   - `position_occurrence.occurrence_id` — removed (composite PK replaces the surrogate).
   - `position_occurrence.game_uuid` — transformed (re-keyed) → `datasource_game_id`.
   - `position_occurrence.ply` — 1:1 → `dgp_ply`.
   - `position_occurrence.state_id` — transformed (re-keyed) → `derived_position_id`.
   - `position_occurrence.san` — removed (derived on demand).
   - `position_occurrence.uci` — transformed (one-ply shift) → `dgp_move_uci`.
   - `position_occurrence.halfmove_clock` — 1:1 → `dgp_halfmove_clock`.
   - `position_occurrence.fullmove_number` — 1:1 → `dgp_fullmove_number`.
4. `opening_catalog` → `datasource_opening` + `derived_opening_route` +
   `derived_opening_route_move`:
   - `opening_catalog.manifest_hash` — removed (manifest machinery).
   - `opening_catalog.source_file` — removed (manifest machinery).
   - `opening_catalog.source_row_ordinal` — removed (manifest machinery).
   - `opening_catalog.source_row_hash` — removed (source-hash machinery).
   - `opening_catalog.eco` — 1:1 → `do_eco`.
   - `opening_catalog.name` — 1:1 → `do_name`.
   - `opening_catalog.move_sequence` — transformed → ordered `derived_opening_route_move` rows (`dorm_ply`, `dorm_move_uci`).
   - `opening_catalog.endpoint_fen` — removed (reconstructable display FEN).
   - `opening_catalog.endpoint_placement` — transformed → endpoint `derived_position_id` on `derived_opening_route`.
   - `opening_catalog.endpoint_side_to_move` — transformed → endpoint `derived_position_id` on `derived_opening_route`.
   - `opening_catalog.endpoint_castling` — transformed → endpoint `derived_position_id` on `derived_opening_route`.
   - `opening_catalog.endpoint_en_passant` — transformed → endpoint `derived_position_id` on `derived_opening_route`.
   - `opening_catalog.endpoint_halfmove_clock` — removed (counter not in shared identity).
   - `opening_catalog.endpoint_fullmove_number` — removed (counter not in shared identity).
5. `opening_position_membership` → `derived_opening_route_move`:
   - `opening_position_membership.manifest_hash` — removed (composite source-row identity).
   - `opening_position_membership.source_file` — removed (composite source-row identity).
   - `opening_position_membership.source_row_ordinal` — removed (composite source-row identity).
   - `opening_position_membership.ply` — transformed (route-local context) → `dorm_ply`.
   - `opening_position_membership.placement` — removed (intermediate positions recreated by replay).
   - `opening_position_membership.side_to_move` — removed (same).
   - `opening_position_membership.castling` — removed (same).
   - `opening_position_membership.en_passant` — removed (same).
   - `opening_position_membership.uci` — transformed (context change) → `dorm_move_uci`.
   - `opening_position_membership.san` — removed (derived on demand).
   - `opening_position_membership.uci_prefix` — removed (transposition machinery).
6. `analysis_result` → `derived_analysis_result`:
   - `analysis_result.position_key` — transformed (re-keyed) → `derived_position_id`.
   - `analysis_result.fen` — removed (reconstructable display FEN).
   - `analysis_result.schema_version` — replaced by new mechanism → `dar_quality` + `dar_configuration_version`.
   - `analysis_result.profile_id` — replaced by new mechanism → `dar_quality` (+ `dar_configuration_version`).
   - `analysis_result.settings_json` — 1:1 → `dar_settings_json`.
   - `analysis_result.settings_fingerprint` — replaced by new mechanism → `dar_configuration_version`.
   - `analysis_result.engine_binary_sha256` — removed (engine identity carried by name/version).
   - `analysis_result.engine_name` — 1:1 → `dar_engine_name`.
   - `analysis_result.engine_version` — 1:1 → `dar_engine_version`.
   - `analysis_result.terminal_kind` — transformed (re-scoped to position-only endings) → `dar_terminal_kind`.
   - `analysis_result.candidate_count` — removed (derivable from child rows).
   - `analysis_result.completed_at` — removed (diagnostic keep-out).
   - `analysis_result.wall_time_ms` — removed (keep-out).
7. `analysis_candidate` → `derived_analysis_line`:
   - `analysis_candidate.position_key` — transformed (re-keyed) → `derived_analysis_result_id`.
   - `analysis_candidate.fen` — removed (parent FEN removed likewise).
   - `analysis_candidate.rank` — 1:1 → `dal_rank`.
   - `analysis_candidate.score_kind` — transformed (`mate_given` domain replaced; signed White-POV preserved) → `dal_score_kind`.
   - `analysis_candidate.score_value` — transformed (`mate_given` paired representation folded into the two-value signed score) → `dal_score_value`.
   - `analysis_candidate.wdl_wins` — 1:1 → `dal_wdl_wins`.
   - `analysis_candidate.wdl_draws` — 1:1 → `dal_wdl_draws`.
   - `analysis_candidate.wdl_losses` — 1:1 → `dal_wdl_losses`.
   - `analysis_candidate.pv_uci_json` — 1:1 → `dal_pv_uci_json`.
   - `analysis_candidate.depth` — 1:1 → `dal_depth`.
   - `analysis_candidate.seldepth` — removed (keep-out).
   - `analysis_candidate.nodes` — removed (keep-out).
   - `analysis_candidate.engine_time_ms` — removed (keep-out).
8. `evaluation_queue` → `derived_analysis_queue`:
   - `evaluation_queue.position_key` — transformed (re-keyed) → `derived_position_id`.
   - `evaluation_queue.fen` — removed (position identity carries it).
   - `evaluation_queue.state` — transformed (domain narrowed to `queued`/`running`) → `daq_state`.
   - `evaluation_queue.position` — removed (FIFO ordinal; no stored ordering counter).
   - `evaluation_queue.attempts` — removed (no attempt counting).
   - `evaluation_queue.schema_version` — replaced by `PRAGMA user_version` (non-table).
   - `evaluation_queue.enqueued_at` — 1:1 → `daq_requested_at_utc`.
   - `evaluation_queue.started_at` — replaced by new mechanism → `daq_claimed_at_utc` `[NEW]` (claim moment).
   - `evaluation_queue.finished_at` — removed (completion deletes the row).
   - `evaluation_queue.last_error_code` — removed (no failure records).
   - `evaluation_queue.last_error_details` — removed (no failure records).
9. `opening_preferred_move_event` → `datasource_preferred_move_period`:
   - `opening_preferred_move_event.event_id` — removed (composite period PK replaces the surrogate).
   - `opening_preferred_move_event.player_uuid` — removed (single-user application).
   - `opening_preferred_move_event.placement` — transformed (four-column FK collapsed) → `derived_position_id` (via canonical `derived_position`).
   - `opening_preferred_move_event.side_to_move` — transformed (same collapse) → `derived_position_id`.
   - `opening_preferred_move_event.castling` — transformed (same collapse) → `derived_position_id`.
   - `opening_preferred_move_event.en_passant` — transformed (same collapse) → `derived_position_id`.
   - `opening_preferred_move_event.action` — removed (period state replaces event verbs).
   - `opening_preferred_move_event.move_uci` — transformed (NULL means explicit no-preference) → `dpm_move_uci`.
   - `opening_preferred_move_event.move_san` — removed (SAN derived for display).
   - `opening_preferred_move_event.effective_at` — transformed (instant → half-open dates) → `dpm_effective_from` (+ `dpm_effective_until`).
   - `opening_preferred_move_event.recorded_at` — removed (append-only bookkeeping).

### 15.2 Removed tables — every field enumerated (no successor unless stated)

Per-feature schema tables (the schema-version fact moves to the non-table
`PRAGMA user_version`; every other field has no successor):

10. `analysis_schema`:
    - `analysis_schema.id` — no successor.
    - `analysis_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
    - `analysis_schema.applied_at` — no successor.
11. `corpus_schema`:
    - `corpus_schema.id` — no successor.
    - `corpus_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
    - `corpus_schema.applied_at` — no successor.
12. `evaluation_schema`:
    - `evaluation_schema.id` — no successor.
    - `evaluation_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
    - `evaluation_schema.applied_at` — no successor.
13. `opening_catalog_schema`:
    - `opening_catalog_schema.id` — no successor.
    - `opening_catalog_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
    - `opening_catalog_schema.applied_at` — no successor.
14. `opening_classification_schema`:
    - `opening_classification_schema.id` — no successor.
    - `opening_classification_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
15. `opening_preferred_move_schema`:
    - `opening_preferred_move_schema.id` — no successor.
    - `opening_preferred_move_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
16. `opening_recurrence_schema`:
    - `opening_recurrence_schema.id` — no successor.
    - `opening_recurrence_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).
17. `opening_relationship_schema`:
    - `opening_relationship_schema.id` — no successor.
    - `opening_relationship_schema.version` — replaced by `PRAGMA user_version` (non-table, section 2).

Run/state/manifest families (transient pipeline state is not persisted; every field has no
successor, direction sections 3.12, 5.3):

18. `corpus_run`: `corpus_run.run_id`, `corpus_run.corpus_id`, `corpus_run.status`,
    `corpus_run.started_at`, `corpus_run.finished_at`, `corpus_run.accepted_games`,
    `corpus_run.excluded_games`, `corpus_run.new_games`, `corpus_run.changed_games`,
    `corpus_run.removed_games`, `corpus_run.unchanged_games`,
    `corpus_run.ordered_positions`, `corpus_run.unique_states`,
    `corpus_run.validation`, `corpus_run.details` — each has no successor.
19. `opening_import_run`: `opening_import_run.run_id`,
    `opening_import_run.manifest_hash`, `opening_import_run.schema_version`,
    `opening_import_run.status`, `opening_import_run.started_at`,
    `opening_import_run.finished_at`, `opening_import_run.record_count`,
    `opening_import_run.details` — each has no successor.
20. `opening_catalog_state`: `opening_catalog_state.id`,
    `opening_catalog_state.accepted_manifest_hash`,
    `opening_catalog_state.accepted_schema_version`,
    `opening_catalog_state.accepted_at`,
    `opening_catalog_state.record_count` — each has no successor.
21. `opening_classification_run`: `opening_classification_run.run_id`,
    `opening_classification_run.manifest_hash`,
    `opening_classification_run.corpus_id`,
    `opening_classification_run.schema_version`,
    `opening_classification_run.catalog_schema_version`,
    `opening_classification_run.relationship_schema_version`,
    `opening_classification_run.status`,
    `opening_classification_run.started_at`,
    `opening_classification_run.finished_at`,
    `opening_classification_run.details` — each has no successor.
22. `opening_classification_state`: `opening_classification_state.accepted_manifest_hash`,
    `opening_classification_state.corpus_id`,
    `opening_classification_state.accepted_schema_version`,
    `opening_classification_state.accepted_catalog_schema_version`,
    `opening_classification_state.accepted_relationship_schema_version`,
    `opening_classification_state.accepted_at` — each has no successor.
23. `opening_recurrence_run`: `opening_recurrence_run.run_id`,
    `opening_recurrence_run.manifest_hash`, `opening_recurrence_run.corpus_id`,
    `opening_recurrence_run.schema_version`,
    `opening_recurrence_run.classification_schema_version`,
    `opening_recurrence_run.catalog_schema_version`,
    `opening_recurrence_run.relationship_schema_version`,
    `opening_recurrence_run.corpus_schema_version`,
    `opening_recurrence_run.classification_input_signature`,
    `opening_recurrence_run.corpus_input_signature`,
    `opening_recurrence_run.game_metadata_input_signature`,
    `opening_recurrence_run.status`, `opening_recurrence_run.started_at`,
    `opening_recurrence_run.finished_at`, `opening_recurrence_run.game_count`,
    `opening_recurrence_run.occurrence_count`,
    `opening_recurrence_run.route_event_count`,
    `opening_recurrence_run.branch_event_count`, `opening_recurrence_run.details` —
    each has no successor.
24. `opening_recurrence_state`: `opening_recurrence_state.accepted_manifest_hash`,
    `opening_recurrence_state.corpus_id`,
    `opening_recurrence_state.accepted_schema_version`,
    `opening_recurrence_state.accepted_classification_schema_version`,
    `opening_recurrence_state.accepted_catalog_schema_version`,
    `opening_recurrence_state.accepted_relationship_schema_version`,
    `opening_recurrence_state.accepted_corpus_schema_version`,
    `opening_recurrence_state.classification_input_signature`,
    `opening_recurrence_state.corpus_input_signature`,
    `opening_recurrence_state.game_metadata_input_signature`,
    `opening_recurrence_state.accepted_at`,
    `opening_recurrence_state.game_count`,
    `opening_recurrence_state.occurrence_count`,
    `opening_recurrence_state.route_event_count`,
    `opening_recurrence_state.branch_event_count` — each has no successor.
25. `opening_relationship_run`: `opening_relationship_run.run_id`,
    `opening_relationship_run.manifest_hash`,
    `opening_relationship_run.schema_version`, `opening_relationship_run.status`,
    `opening_relationship_run.record_count`,
    `opening_relationship_run.position_count`,
    `opening_relationship_run.membership_count`,
    `opening_relationship_run.parent_link_count`,
    `opening_relationship_run.transposition_link_count`,
    `opening_relationship_run.details` — each has no successor.
26. `opening_relationship_state`: `opening_relationship_state.accepted_manifest_hash`,
    `opening_relationship_state.accepted_schema_version`,
    `opening_relationship_state.record_count`,
    `opening_relationship_state.position_count`,
    `opening_relationship_state.membership_count`,
    `opening_relationship_state.parent_link_count`,
    `opening_relationship_state.transposition_link_count` — each has no successor.
27. `opening_source_manifest`: `opening_source_manifest.manifest_hash`,
    `opening_source_manifest.source_dataset`, `opening_source_manifest.file_count`,
    `opening_source_manifest.record_count`, `opening_source_manifest.created_at` —
    each has no successor (no manifest machinery, direction section 2.5).
28. `opening_source_file`: `opening_source_file.manifest_hash`,
    `opening_source_file.source_file`, `opening_source_file.source_file_hash`,
    `opening_source_file.record_count` — each has no successor (no persistent source
    hashes, direction section 2.5).

Corpus machinery (single configured trainer replaces the corpus entity; every field has no
successor):

29. `corpus`: `corpus.corpus_id`, `corpus.subject_player_uuid` — each has no successor
    (the configured trainer UUID lives in application configuration, not a table).
30. `corpus_game`: `corpus_game.corpus_id`, `corpus_game.game_uuid`,
    `corpus_game.rules`, `corpus_game.fingerprint` — each has no successor (games are
    retained additively; the standard-chess rule is an intake filter, section 14.1).

Classification, recurrence, and projection machinery (no current reader; every field has no
successor; direction sections 3.12, 5.3, 6):

31. `opening_classification_anchor`: `opening_classification_anchor.manifest_hash`,
    `opening_classification_anchor.corpus_id`,
    `opening_classification_anchor.game_uuid`,
    `opening_classification_anchor.anchor_ply`,
    `opening_classification_anchor.source_file`,
    `opening_classification_anchor.source_row_ordinal`,
    `opening_classification_anchor.anchor_placement`,
    `opening_classification_anchor.anchor_side_to_move`,
    `opening_classification_anchor.anchor_castling`,
    `opening_classification_anchor.anchor_en_passant`,
    `opening_classification_anchor.anchor_san`,
    `opening_classification_anchor.anchor_uci` — each has no successor.
32. `opening_classification_game`: `opening_classification_game.manifest_hash`,
    `opening_classification_game.corpus_id`,
    `opening_classification_game.game_uuid`,
    `opening_classification_game.source_fingerprint` — each has no successor.
33. `opening_classification_route`: `opening_classification_route.manifest_hash`,
    `opening_classification_route.corpus_id`,
    `opening_classification_route.game_uuid`,
    `opening_classification_route.anchor_ply`,
    `opening_classification_route.source_file`,
    `opening_classification_route.source_row_ordinal`,
    `opening_classification_route.route_ply`,
    `opening_classification_route.route_placement`,
    `opening_classification_route.route_side_to_move`,
    `opening_classification_route.route_castling`,
    `opening_classification_route.route_en_passant`,
    `opening_classification_route.route_san`,
    `opening_classification_route.route_uci`,
    `opening_classification_route.route_halfmove_clock`,
    `opening_classification_route.route_fullmove_number` — each has no successor.
34. `opening_recurrence_game`: `opening_recurrence_game.manifest_hash`,
    `opening_recurrence_game.corpus_id`, `opening_recurrence_game.game_uuid`,
    `opening_recurrence_game.source_fingerprint`,
    `opening_recurrence_game.metadata_fingerprint`,
    `opening_recurrence_game.game_sequence`, `opening_recurrence_game.game_color`,
    `opening_recurrence_game.end_time`, `opening_recurrence_game.year`,
    `opening_recurrence_game.month`, `opening_recurrence_game.time_control`,
    `opening_recurrence_game.time_class`, `opening_recurrence_game.white_rating`,
    `opening_recurrence_game.black_rating`, `opening_recurrence_game.white_result`,
    `opening_recurrence_game.black_result` — each has no successor.
35. `opening_recurrence_occurrence`: `opening_recurrence_occurrence.manifest_hash`,
    `opening_recurrence_occurrence.corpus_id`,
    `opening_recurrence_occurrence.game_uuid`, `opening_recurrence_occurrence.ply`,
    `opening_recurrence_occurrence.placement`,
    `opening_recurrence_occurrence.side_to_move`,
    `opening_recurrence_occurrence.castling`,
    `opening_recurrence_occurrence.en_passant`, `opening_recurrence_occurrence.san`,
    `opening_recurrence_occurrence.uci`,
    `opening_recurrence_occurrence.halfmove_clock`,
    `opening_recurrence_occurrence.fullmove_number` — each has no successor (superseded
    functionally by `derived_game_position` + `derived_position`, which are written by the
    importer, not copied from here).
36. `opening_recurrence_route_event`: `opening_recurrence_route_event.manifest_hash`,
    `opening_recurrence_route_event.corpus_id`,
    `opening_recurrence_route_event.game_uuid`,
    `opening_recurrence_route_event.anchor_ply`,
    `opening_recurrence_route_event.source_file`,
    `opening_recurrence_route_event.source_row_ordinal`,
    `opening_recurrence_route_event.route_ply`,
    `opening_recurrence_route_event.placement`,
    `opening_recurrence_route_event.side_to_move`,
    `opening_recurrence_route_event.castling`,
    `opening_recurrence_route_event.en_passant`,
    `opening_recurrence_route_event.san`, `opening_recurrence_route_event.uci`,
    `opening_recurrence_route_event.halfmove_clock`,
    `opening_recurrence_route_event.fullmove_number` — each has no successor.
37. `opening_recurrence_branch_event`: `opening_recurrence_branch_event.manifest_hash`,
    `opening_recurrence_branch_event.corpus_id`,
    `opening_recurrence_branch_event.game_uuid`,
    `opening_recurrence_branch_event.parent_ply`,
    `opening_recurrence_branch_event.parent_placement`,
    `opening_recurrence_branch_event.parent_side_to_move`,
    `opening_recurrence_branch_event.parent_castling`,
    `opening_recurrence_branch_event.parent_en_passant`,
    `opening_recurrence_branch_event.branch_kind`,
    `opening_recurrence_branch_event.child_ply`,
    `opening_recurrence_branch_event.child_placement`,
    `opening_recurrence_branch_event.child_side_to_move`,
    `opening_recurrence_branch_event.child_castling`,
    `opening_recurrence_branch_event.child_en_passant`,
    `opening_recurrence_branch_event.child_san`,
    `opening_recurrence_branch_event.child_uci`,
    `opening_recurrence_branch_event.terminal_outcome` — each has no successor.
38. `opening_recurrence_position_projection`:
    `opening_recurrence_position_projection.manifest_hash`,
    `opening_recurrence_position_projection.corpus_id`,
    `opening_recurrence_position_projection.placement`,
    `opening_recurrence_position_projection.side_to_move`,
    `opening_recurrence_position_projection.castling`,
    `opening_recurrence_position_projection.en_passant`,
    `opening_recurrence_position_projection.color_scope`,
    `opening_recurrence_position_projection.raw_occurrence_count`,
    `opening_recurrence_position_projection.distinct_game_count`,
    `opening_recurrence_position_projection.first_game_sequence`,
    `opening_recurrence_position_projection.first_game_uuid`,
    `opening_recurrence_position_projection.first_ply`,
    `opening_recurrence_position_projection.last_game_sequence`,
    `opening_recurrence_position_projection.last_game_uuid`,
    `opening_recurrence_position_projection.last_ply` — each has no successor
    (statistics are computed on demand, direction section 4.3).
39. `opening_recurrence_route_projection`:
    `opening_recurrence_route_projection.manifest_hash`,
    `opening_recurrence_route_projection.corpus_id`,
    `opening_recurrence_route_projection.anchor_ply`,
    `opening_recurrence_route_projection.source_file`,
    `opening_recurrence_route_projection.source_row_ordinal`,
    `opening_recurrence_route_projection.placement`,
    `opening_recurrence_route_projection.side_to_move`,
    `opening_recurrence_route_projection.castling`,
    `opening_recurrence_route_projection.en_passant`,
    `opening_recurrence_route_projection.color_scope`,
    `opening_recurrence_route_projection.raw_occurrence_count`,
    `opening_recurrence_route_projection.distinct_game_count`,
    `opening_recurrence_route_projection.first_game_sequence`,
    `opening_recurrence_route_projection.first_game_uuid`,
    `opening_recurrence_route_projection.first_route_ply`,
    `opening_recurrence_route_projection.last_game_sequence`,
    `opening_recurrence_route_projection.last_game_uuid`,
    `opening_recurrence_route_projection.last_route_ply` — each has no successor.
40. `opening_recurrence_branch_projection`:
    `opening_recurrence_branch_projection.manifest_hash`,
    `opening_recurrence_branch_projection.corpus_id`,
    `opening_recurrence_branch_projection.parent_placement`,
    `opening_recurrence_branch_projection.parent_side_to_move`,
    `opening_recurrence_branch_projection.parent_castling`,
    `opening_recurrence_branch_projection.parent_en_passant`,
    `opening_recurrence_branch_projection.branch_kind`,
    `opening_recurrence_branch_projection.child_uci`,
    `opening_recurrence_branch_projection.color_scope`,
    `opening_recurrence_branch_projection.raw_event_count`,
    `opening_recurrence_branch_projection.distinct_game_count`,
    `opening_recurrence_branch_projection.first_game_sequence`,
    `opening_recurrence_branch_projection.first_game_uuid`,
    `opening_recurrence_branch_projection.first_parent_ply`,
    `opening_recurrence_branch_projection.last_game_sequence`,
    `opening_recurrence_branch_projection.last_game_uuid`,
    `opening_recurrence_branch_projection.last_parent_ply` — each has no successor.
41. `opening_recurrence_route_branch_projection`:
    `opening_recurrence_route_branch_projection.manifest_hash`,
    `opening_recurrence_route_branch_projection.corpus_id`,
    `opening_recurrence_route_branch_projection.anchor_ply`,
    `opening_recurrence_route_branch_projection.source_file`,
    `opening_recurrence_route_branch_projection.source_row_ordinal`,
    `opening_recurrence_route_branch_projection.parent_placement`,
    `opening_recurrence_route_branch_projection.parent_side_to_move`,
    `opening_recurrence_route_branch_projection.parent_castling`,
    `opening_recurrence_route_branch_projection.parent_en_passant`,
    `opening_recurrence_route_branch_projection.branch_kind`,
    `opening_recurrence_route_branch_projection.child_uci`,
    `opening_recurrence_route_branch_projection.color_scope`,
    `opening_recurrence_route_branch_projection.raw_event_count`,
    `opening_recurrence_route_branch_projection.distinct_game_count`,
    `opening_recurrence_route_branch_projection.first_game_sequence`,
    `opening_recurrence_route_branch_projection.first_game_uuid`,
    `opening_recurrence_route_branch_projection.first_parent_ply`,
    `opening_recurrence_route_branch_projection.last_game_sequence`,
    `opening_recurrence_route_branch_projection.last_game_uuid`,
    `opening_recurrence_route_branch_projection.last_parent_ply` — each has no successor.

Relationship/hierarchy machinery (hierarchy derived at request time, direction section
4.4; every field has no successor):

42. `opening_relationship_position`: `opening_relationship_position.manifest_hash`,
    `opening_relationship_position.placement`,
    `opening_relationship_position.side_to_move`,
    `opening_relationship_position.castling`,
    `opening_relationship_position.en_passant` — each has no successor (superseded
    functionally by `derived_position`, written by rebuilt tools).
43. `opening_parent_link`: `opening_parent_link.manifest_hash`,
    `opening_parent_link.child_source_file`,
    `opening_parent_link.child_source_row_ordinal`,
    `opening_parent_link.child_ply`,
    `opening_parent_link.parent_source_file`,
    `opening_parent_link.parent_source_row_ordinal` — each has no successor.
44. `opening_transposition_link`: `opening_transposition_link.manifest_hash`,
    `opening_transposition_link.placement`,
    `opening_transposition_link.side_to_move`,
    `opening_transposition_link.castling`,
    `opening_transposition_link.en_passant`,
    `opening_transposition_link.source_file_a`,
    `opening_transposition_link.source_row_ordinal_a`,
    `opening_transposition_link.ply_a`,
    `opening_transposition_link.uci_prefix_a`,
    `opening_transposition_link.source_file_b`,
    `opening_transposition_link.source_row_ordinal_b`,
    `opening_transposition_link.ply_b`,
    `opening_transposition_link.uci_prefix_b` — each has no successor (transposition
    status is computed at request time).

Fetch and player machinery (direction sections 2.5, 3.12, 5.1; every field has no
successor):

45. `fetch_state`: `fetch_state.username`, `fetch_state.year`, `fetch_state.month`,
    `fetch_state.etag`, `fetch_state.last_fetched`, `fetch_state.is_current` — each has
    no successor (raw month files are the fetch ledger).
46. `players`: `players.uuid`, `players.username`, `players.profile_url` — each has no
    successor (no normalized players table, direction section 3.3 keep-out).

Append-only preferred-move machinery replaced by editable periods (every field has no
successor):

47. `opening_preferred_move_requirement_event`:
    `opening_preferred_move_requirement_event.event_id`,
    `opening_preferred_move_requirement_event.player_uuid`,
    `opening_preferred_move_requirement_event.placement`,
    `opening_preferred_move_requirement_event.side_to_move`,
    `opening_preferred_move_requirement_event.castling`,
    `opening_preferred_move_requirement_event.en_passant`,
    `opening_preferred_move_requirement_event.action`,
    `opening_preferred_move_requirement_event.effective_at`,
    `opening_preferred_move_requirement_event.recorded_at` — each has no successor.

Append-only analysis history (direction section 3.10 keep-outs; every field has no
successor):

48. `analysis_batch_run`: `analysis_batch_run.run_id`, `analysis_batch_run.status`,
    `analysis_batch_run.selection_json`,
    `analysis_batch_run.settings_fingerprint`, `analysis_batch_run.started_at`,
    `analysis_batch_run.finished_at`,
    `analysis_batch_run.selected_positions`,
    `analysis_batch_run.eligible_positions`,
    `analysis_batch_run.completed_positions`,
    `analysis_batch_run.failed_positions`, `analysis_batch_run.details` — each has no
    successor.
49. `analysis_position_failure`: `analysis_position_failure.failure_id`,
    `analysis_position_failure.run_id`, `analysis_position_failure.fen`,
    `analysis_position_failure.settings_fingerprint`,
    `analysis_position_failure.attempts`, `analysis_position_failure.error_code`,
    `analysis_position_failure.details`, `analysis_position_failure.failed_at` — each
    has no successor.

### 15.3 Accounting statement

- Old tables: 49 total — 9 replaced (15.1), 40 removed (15.2). The count and every table
  name match the `### Table:` inventory in `data/database/schema.txt` exactly.
- Old fields: every field of all 49 old tables is enumerated individually above with its
  disposition — 1:1, transformed, removed, replaced by a `[NEW]` field or mechanism, or
  replaced by the non-table `PRAGMA user_version` — with no abbreviations, ranges, or
  grouped names.
- New tables: none beyond the ten in sections 3–12; nothing from the direction's negative
  register (direction section 3.12) is created.
