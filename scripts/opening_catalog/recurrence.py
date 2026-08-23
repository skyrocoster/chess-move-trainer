"""Deterministic S4 recurrence events and projections from accepted rows."""

from __future__ import annotations

import hashlib
import io
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

import chess.pgn

from scripts.chess_com._schema import SCHEMA_VERSION as CORPUS_SCHEMA_VERSION

from .classification_schema import CLASSIFICATION_SCHEMA_VERSION
from .importer import OpeningCatalogError
from .recurrence_contract import (
    GAME_COLORS,
    RecurrenceBranchFact,
    RecurrenceGameFact,
    RecurrenceOccurrenceFact,
    RecurrenceProjections,
    RecurrenceRouteFact,
    project_recurrence,
)
from .recurrence_schema import RECURRENCE_SCHEMA_VERSION
from .schema import RELATIONSHIP_SCHEMA_VERSION
from .schema import SCHEMA_VERSION as CATALOG_SCHEMA_VERSION


class RecurrenceError(OpeningCatalogError):
    """The accepted S1/S2/S3/corpus boundary cannot produce safe S4 facts."""


@dataclass(frozen=True)
class RecurrenceFacts:
    """All authoritative S4 events plus the input provenance used to rebuild them."""

    manifest_hash: str
    corpus_id: int
    schema_version: int
    classification_schema_version: int
    catalog_schema_version: int
    relationship_schema_version: int
    corpus_schema_version: int
    classification_input_signature: str
    corpus_input_signature: str
    game_metadata_input_signature: str
    games: tuple[RecurrenceGameFact, ...]
    occurrences: tuple[RecurrenceOccurrenceFact, ...]
    routes: tuple[RecurrenceRouteFact, ...]
    branches: tuple[RecurrenceBranchFact, ...]

    @property
    def game_count(self) -> int:
        return len(self.games)

    @property
    def occurrence_count(self) -> int:
        return len(self.occurrences)

    @property
    def route_event_count(self) -> int:
        return len(self.routes)

    @property
    def branch_event_count(self) -> int:
        return len(self.branches)

    @property
    def projections(self) -> RecurrenceProjections:
        return project_recurrence(self)


def _query_error(error: sqlite3.Error, message: str) -> RecurrenceError:
    return RecurrenceError(f"{message}: {error}")


def _version(connection: sqlite3.Connection, table: str) -> int:
    try:
        row = connection.execute(f"SELECT version FROM {table} WHERE id = 1").fetchone()
    except sqlite3.Error as error:
        raise _query_error(error, f"required schema table {table!r} is unavailable") from error
    if row is None:
        raise RecurrenceError(f"required schema table {table!r} has no singleton version row")
    return int(row[0])


def _accepted_context(
    connection: sqlite3.Connection, requested_corpus_id: int | None
) -> tuple[str, int, int, int, int, int]:
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        catalog_state = connection.execute(
            "SELECT accepted_manifest_hash, accepted_schema_version, record_count "
            "FROM opening_catalog_state WHERE id = 1"
        ).fetchone()
        relationship_state = connection.execute(
            "SELECT accepted_manifest_hash, accepted_schema_version, record_count "
            "FROM opening_relationship_state"
        ).fetchall()
        classification_state = connection.execute(
            "SELECT accepted_manifest_hash, corpus_id, accepted_schema_version, "
            "accepted_catalog_schema_version, accepted_relationship_schema_version "
            "FROM opening_classification_state"
        ).fetchall()
        corpus_rows = connection.execute(
            "SELECT corpus_id FROM corpus ORDER BY corpus_id"
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted S1/S2/S3/corpus state is unavailable") from error
    if catalog_state is None:
        raise RecurrenceError("an accepted S1 catalog is required")
    manifest_hash = str(catalog_state[0])
    matching_relationships = [row for row in relationship_state if row[0] == manifest_hash]
    if len(matching_relationships) != 1:
        raise RecurrenceError("an accepted S2 relationship state for the S1 manifest is required")
    matching_classification = [row for row in classification_state if row[0] == manifest_hash]
    if requested_corpus_id is None:
        if len(corpus_rows) != 1:
            raise RecurrenceError("one accepted corpus is required when corpus_id is not supplied")
        corpus_id = int(corpus_rows[0][0])
    else:
        corpus_id = int(requested_corpus_id)
    class_rows = [row for row in matching_classification if int(row[1]) == corpus_id]
    if len(class_rows) != 1:
        raise RecurrenceError("an accepted S3 classification state for the corpus is required")
    if not any(int(row[0]) == corpus_id for row in corpus_rows):
        raise RecurrenceError(f"accepted corpus {corpus_id} is missing")
    catalog_version = _version(connection, "opening_catalog_schema")
    relationship_version = _version(connection, "opening_relationship_schema")
    classification_version = _version(connection, "opening_classification_schema")
    corpus_version = _version(connection, "corpus_schema")
    if catalog_version != CATALOG_SCHEMA_VERSION or int(catalog_state[1]) != catalog_version:
        raise RecurrenceError("accepted S1 catalog schema version is incompatible")
    relationship = matching_relationships[0]
    if relationship_version != RELATIONSHIP_SCHEMA_VERSION or int(relationship[1]) != (
        relationship_version
    ):
        raise RecurrenceError("accepted S2 relationship schema version is incompatible")
    classification = class_rows[0]
    if classification_version != CLASSIFICATION_SCHEMA_VERSION or int(classification[2]) != (
        classification_version
    ):
        raise RecurrenceError("accepted S3 classification schema version is incompatible")
    if int(classification[3]) != catalog_version or int(classification[4]) != relationship_version:
        raise RecurrenceError("accepted S3 dependency schema versions are incompatible")
    if corpus_version != CORPUS_SCHEMA_VERSION:
        raise RecurrenceError("accepted corpus schema version is incompatible")
    try:
        catalog_count = connection.execute(
            "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?", (manifest_hash,)
        ).fetchone()[0]
        if int(catalog_count) != int(catalog_state[2]) or int(catalog_count) != int(
            relationship[2]
        ):
            raise RecurrenceError("accepted S1/S2 catalog counts are inconsistent")
    except sqlite3.Error as error:
        raise _query_error(error, "accepted catalog facts are unavailable") from error
    return (
        manifest_hash,
        corpus_id,
        classification_version,
        catalog_version,
        relationship_version,
        corpus_version,
    )


def _digest(rows: Iterable[object]) -> str:
    payload = json.dumps(list(rows), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _input_signatures(
    connection: sqlite3.Connection, manifest_hash: str, corpus_id: int
) -> tuple[str, str, str]:
    try:
        classification_rows = connection.execute(
            "SELECT manifest_hash, corpus_id, game_uuid, source_fingerprint "
            "FROM opening_classification_game WHERE manifest_hash = ? AND corpus_id = ? "
            "ORDER BY game_uuid",
            (manifest_hash, corpus_id),
        ).fetchall()
        classification_rows += connection.execute(
            "SELECT manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
            "source_row_ordinal, anchor_placement, anchor_side_to_move, anchor_castling, "
            "anchor_en_passant, anchor_san, anchor_uci FROM opening_classification_anchor "
            "WHERE manifest_hash = ? AND corpus_id = ? ORDER BY game_uuid, anchor_ply, "
            "source_file, source_row_ordinal",
            (manifest_hash, corpus_id),
        ).fetchall()
        classification_rows += connection.execute(
            "SELECT manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
            "source_row_ordinal, route_ply, route_placement, route_side_to_move, "
            "route_castling, route_en_passant, route_san, route_uci, route_halfmove_clock, "
            "route_fullmove_number FROM opening_classification_route WHERE manifest_hash = ? "
            "AND corpus_id = ? ORDER BY game_uuid, anchor_ply, source_file, source_row_ordinal, "
            "route_ply",
            (manifest_hash, corpus_id),
        ).fetchall()
        corpus_rows = connection.execute(
            "SELECT cg.corpus_id, cg.game_uuid, cg.rules, cg.fingerprint, o.ply, "
            "s.placement, s.side_to_move, s.castling, s.en_passant, o.san, o.uci, "
            "o.halfmove_clock, o.fullmove_number FROM corpus_game AS cg "
            "JOIN position_occurrence AS o ON o.game_uuid = cg.game_uuid "
            "JOIN position_state AS s ON s.state_id = o.state_id "
            "WHERE cg.corpus_id = ? ORDER BY cg.game_uuid, o.ply",
            (corpus_id,),
        ).fetchall()
        metadata_rows = connection.execute(
            "SELECT cg.game_uuid, cg.fingerprint, g.end_time, g.year, g.month, "
            "g.time_control, g.time_class, g.white_rating, g.black_rating, "
            "g.white_result, g.black_result, g.pgn, "
            "CASE WHEN g.white_player_uuid = c.subject_player_uuid THEN 'white' "
            "WHEN g.black_player_uuid = c.subject_player_uuid THEN 'black' ELSE NULL END "
            "FROM corpus AS c JOIN corpus_game AS cg ON cg.corpus_id = c.corpus_id "
            "JOIN games AS g ON g.uuid = cg.game_uuid WHERE c.corpus_id = ? "
            "ORDER BY g.end_time, g.uuid",
            (corpus_id,),
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted S3/corpus/game inputs are unavailable") from error
    return _digest(classification_rows), _digest(corpus_rows), _digest(metadata_rows)


def input_signatures(
    connection: sqlite3.Connection, corpus_id: int | None = None
) -> tuple[str, int, str, str, str, int, int, int, int]:
    """Return accepted identities, schema versions, and provenance signatures."""

    context = _accepted_context(connection, corpus_id)
    (
        manifest_hash,
        accepted_corpus_id,
        class_version,
        catalog_version,
        relationship_version,
        corpus_version,
    ) = context
    classification_signature, corpus_signature, metadata_signature = _input_signatures(
        connection, manifest_hash, accepted_corpus_id
    )
    return (
        manifest_hash,
        accepted_corpus_id,
        classification_signature,
        corpus_signature,
        metadata_signature,
        class_version,
        catalog_version,
        relationship_version,
        corpus_version,
    )


def _terminal_outcome(
    raw_pgn: str | None, white_result: str | None, black_result: str | None
) -> str | None:
    if raw_pgn:
        try:
            game = chess.pgn.read_game(io.StringIO(raw_pgn))
            if game is not None:
                termination = game.headers.get("Termination")
                if termination:
                    return termination.strip().lower().replace(" ", "_")
                board = game.board()
                for move in game.mainline_moves():
                    board.push(move)
                outcome = board.outcome(claim_draw=True)
                if outcome is not None:
                    return outcome.termination.name.lower()
                result = game.headers.get("Result")
                if result and result != "*":
                    return result
        except Exception:
            pass
    if white_result == "draw" or black_result == "draw":
        return "draw"
    if white_result:
        return f"white_{white_result}"
    if black_result:
        return f"black_{black_result}"
    return None


def derive_recurrence(
    connection: sqlite3.Connection, corpus_id: int | None = None
) -> RecurrenceFacts:
    """Derive every global, route, and parent-continuation event from accepted rows."""

    (
        manifest_hash,
        accepted_corpus_id,
        classification_version,
        catalog_version,
        relationship_version,
        corpus_version,
    ) = _accepted_context(connection, corpus_id)
    classification_signature, corpus_signature, metadata_signature = _input_signatures(
        connection, manifest_hash, accepted_corpus_id
    )
    try:
        subject_row = connection.execute(
            "SELECT subject_player_uuid FROM corpus WHERE corpus_id = ?", (accepted_corpus_id,)
        ).fetchone()
        game_rows = connection.execute(
            "SELECT cg.game_uuid, cg.fingerprint, g.end_time, g.year, g.month, "
            "g.time_control, g.time_class, g.white_rating, g.black_rating, "
            "g.white_result, g.black_result, g.white_player_uuid, g.black_player_uuid, g.pgn "
            "FROM corpus_game AS cg JOIN games AS g ON g.uuid = cg.game_uuid "
            "WHERE cg.corpus_id = ? ORDER BY g.end_time, g.uuid",
            (accepted_corpus_id,),
        ).fetchall()
        occurrence_rows = connection.execute(
            "SELECT cg.game_uuid, o.ply, s.placement, s.side_to_move, s.castling, "
            "s.en_passant, o.san, o.uci, o.halfmove_clock, o.fullmove_number "
            "FROM corpus_game AS cg JOIN position_occurrence AS o "
            "ON o.game_uuid = cg.game_uuid JOIN position_state AS s ON s.state_id = o.state_id "
            "WHERE cg.corpus_id = ? ORDER BY cg.game_uuid, o.ply",
            (accepted_corpus_id,),
        ).fetchall()
        route_rows = connection.execute(
            "SELECT game_uuid, anchor_ply, source_file, source_row_ordinal, route_ply, "
            "route_placement, route_side_to_move, route_castling, route_en_passant, route_san, "
            "route_uci, route_halfmove_clock, route_fullmove_number "
            "FROM opening_classification_route WHERE manifest_hash = ? AND corpus_id = ? "
            "ORDER BY game_uuid, anchor_ply, source_file, source_row_ordinal, route_ply",
            (manifest_hash, accepted_corpus_id),
        ).fetchall()
        classification_games = connection.execute(
            "SELECT game_uuid, source_fingerprint FROM opening_classification_game "
            "WHERE manifest_hash = ? AND corpus_id = ? ORDER BY game_uuid",
            (manifest_hash, accepted_corpus_id),
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted recurrence inputs are unavailable") from error
    if subject_row is None:
        raise RecurrenceError(f"accepted corpus {accepted_corpus_id} is missing")
    subject_uuid = subject_row[0]
    if len(classification_games) != len(game_rows) or {row[0] for row in classification_games} != {
        row[0] for row in game_rows
    }:
        raise RecurrenceError("accepted S3 games do not cover the accepted corpus")
    fingerprints = {row[0]: row[1] for row in game_rows}
    if any(fingerprints[row[0]] != row[1] for row in classification_games):
        raise RecurrenceError("accepted S3 game fingerprints differ from the corpus")

    games: list[RecurrenceGameFact] = []
    terminal_by_game: dict[str, str | None] = {}
    game_sequence_by_uuid: dict[str, int] = {}
    game_color_by_uuid: dict[str, str] = {}
    for sequence, row in enumerate(game_rows, start=1):
        white_uuid, black_uuid = row[11], row[12]
        if (white_uuid == subject_uuid) == (black_uuid == subject_uuid):
            raise RecurrenceError(f"accepted game {row[0]!r} has no unique corpus color")
        game_color = "white" if white_uuid == subject_uuid else "black"
        if game_color not in GAME_COLORS:
            raise RecurrenceError(f"unsupported game color {game_color!r}")
        game_sequence_by_uuid[row[0]] = sequence
        game_color_by_uuid[row[0]] = game_color
        terminal_by_game[row[0]] = _terminal_outcome(row[13], row[9], row[10])
        games.append(
            RecurrenceGameFact(
                manifest_hash,
                accepted_corpus_id,
                row[0],
                row[1],
                _metadata_fingerprint(row, game_color),
                sequence,
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                game_color,
            )
        )

    by_game: defaultdict[str, list[RecurrenceOccurrenceFact]] = defaultdict(list)
    for row in occurrence_rows:
        fact = RecurrenceOccurrenceFact(
            manifest_hash,
            accepted_corpus_id,
            row[0],
            int(row[1]),
            tuple(row[2:6]),  # type: ignore[arg-type]
            row[6],
            row[7],
            int(row[8]),
            int(row[9]),
        )
        by_game[fact.game_uuid].append(fact)
    if set(by_game) != set(game_sequence_by_uuid):
        raise RecurrenceError("accepted corpus game occurrence coverage is incomplete")
    for game_uuid, items in by_game.items():
        plies = tuple(item.ply for item in items)
        if not items or plies != tuple(range(plies[0], plies[-1] + 1)) or plies[0] != 0:
            raise RecurrenceError(f"accepted game {game_uuid!r} has incomplete ordered occurrences")
    occurrences = tuple(item for game_uuid in sorted(by_game) for item in by_game[game_uuid])

    routes: list[RecurrenceRouteFact] = []
    occurrence_by_identity = {(item.game_uuid, item.ply): item for item in occurrences}
    for row in route_rows:
        occurrence = occurrence_by_identity.get((row[0], int(row[4])))
        if (
            occurrence is None
            or occurrence.key != tuple(row[5:9])
            or occurrence.san != row[9]
            or occurrence.uci != row[10]
        ):
            raise RecurrenceError("accepted S3 route differs from the corpus occurrence")
        routes.append(
            RecurrenceRouteFact(
                manifest_hash,
                accepted_corpus_id,
                row[0],
                int(row[1]),
                (manifest_hash, row[2], int(row[3])),
                int(row[4]),
                tuple(row[5:9]),  # type: ignore[arg-type]
                row[9],
                row[10],
                int(row[11]),
                int(row[12]),
            )
        )

    branches: list[RecurrenceBranchFact] = []
    for game_uuid in sorted(by_game):
        items = by_game[game_uuid]
        for index, parent in enumerate(items):
            child = items[index + 1] if index + 1 < len(items) else None
            if child is None:
                branches.append(
                    RecurrenceBranchFact(
                        manifest_hash,
                        accepted_corpus_id,
                        game_uuid,
                        parent.ply,
                        parent.key,
                        "terminal",
                        parent.ply,
                        None,
                        None,
                        None,
                        terminal_by_game[game_uuid],
                    )
                )
            else:
                branches.append(
                    RecurrenceBranchFact(
                        manifest_hash,
                        accepted_corpus_id,
                        game_uuid,
                        parent.ply,
                        parent.key,
                        "move",
                        child.ply,
                        child.key,
                        child.san,
                        child.uci,
                        None,
                    )
                )
    return RecurrenceFacts(
        manifest_hash,
        accepted_corpus_id,
        RECURRENCE_SCHEMA_VERSION,
        classification_version,
        catalog_version,
        relationship_version,
        corpus_version,
        classification_signature,
        corpus_signature,
        metadata_signature,
        tuple(games),
        occurrences,
        tuple(routes),
        tuple(branches),
    )


def _metadata_fingerprint(row: tuple[object, ...], game_color: str) -> str:
    return _digest((*row[:11], row[13], game_color))


derive_recurrences = derive_recurrence
build_projections = project_recurrence
derive_projections = project_recurrence
