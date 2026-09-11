"""Read-time opening recognition from persisted routes and canonical endpoints."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import CanonicalPosition, canonicalize_board, canonicalize_fen
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .source import OpeningSourceError, _read_one_game

MatchKind = Literal["route", "transposition"]


class OpeningInputError(ValueError):
    """Raised when a FEN or PGN query is not an accepted standard-chess input."""


class OpeningRecognitionError(RuntimeError):
    """Raised when persisted opening data cannot be read or validated safely."""


@dataclass(frozen=True, slots=True)
class RecognizedOpening:
    """One immutable label reached at one encountered ply."""

    ply: int
    eco: str
    name: str
    match: MatchKind

    @property
    def match_kind(self) -> MatchKind:
        """Return the explicit route or transposition match kind."""

        return self.match


@dataclass(frozen=True, slots=True)
class OpeningRecognition:
    """An immutable ordered recognition timeline and its selected current label."""

    recognized: tuple[RecognizedOpening, ...]
    current: RecognizedOpening | None

    @property
    def recognitions(self) -> tuple[RecognizedOpening, ...]:
        """Return the ordered recognition timeline."""

        return self.recognized


@dataclass(frozen=True, slots=True)
class _StoredRoute:
    route_id: int
    eco: str
    name: str
    moves_uci: tuple[str, ...]
    endpoint: CanonicalPosition


def lookup_fen(
    database_path: str | Path, fen: str
) -> OpeningRecognition:
    """Recognize a valid full FEN without writing or exposing database state."""

    position = _parse_fen_input(fen)
    routes = _load_routes(database_path)
    endpoint_map = _endpoint_map(routes)
    direct_routes = endpoint_map.get(position, ())
    if not direct_routes:
        return OpeningRecognition(recognized=(), current=None)

    evidence: dict[tuple[int, str, str], MatchKind] = {}
    for route in direct_routes:
        board = chess.Board()
        for ply, move_uci in enumerate(route.moves_uci, start=1):
            _push_stored_move(board, move_uci, ply)
            reached = canonicalize_board(board)
            for matched_route in endpoint_map.get(reached, ()):
                _record_evidence(
                    evidence,
                    ply,
                    matched_route.eco,
                    matched_route.name,
                    "transposition",
                )
    return _build_recognition(evidence)


def replay_pgn(
    database_path: str | Path, pgn: str
) -> OpeningRecognition:
    """Replay one standard-start PGN and recognize reached opening endpoints."""

    game = _parse_pgn_input(pgn)
    routes = _load_routes(database_path)
    endpoint_map = _endpoint_map(routes)

    board = game.board()
    if board.fen(en_passant="fen") != chess.STARTING_FEN:
        raise OpeningInputError("PGN must use the standard initial position")

    evidence: dict[tuple[int, str, str], MatchKind] = {}
    played_moves: list[str] = []
    for ply, move in enumerate(game.mainline_moves(), start=1):
        if move not in board.legal_moves:
            raise OpeningInputError(f"PGN contains an illegal move at ply {ply}")
        played_moves.append(move.uci())
        board.push(move)
        reached = canonicalize_board(board)
        for route in endpoint_map.get(reached, ()):
            match: MatchKind = (
                "route" if route.moves_uci == tuple(played_moves) else "transposition"
            )
            _record_evidence(evidence, ply, route.eco, route.name, match)

    if not played_moves:
        raise OpeningInputError("PGN contains no moves")
    return _build_recognition(evidence)


def _parse_fen_input(fen: str) -> CanonicalPosition:
    if not isinstance(fen, str):
        raise OpeningInputError("FEN must be a complete six-field string")
    try:
        return canonicalize_fen(fen)
    except ValueError as error:
        raise OpeningInputError(f"invalid FEN: {error}") from error


def _parse_pgn_input(pgn: str) -> chess.pgn.Game:
    if not isinstance(pgn, str) or not pgn.strip():
        raise OpeningInputError("PGN must contain exactly one non-empty game")
    try:
        return _read_one_game(pgn)
    except OpeningSourceError as error:
        raise OpeningInputError(str(error)) from error
    except (TypeError, ValueError, UnicodeError) as error:
        raise OpeningInputError(f"PGN could not be parsed: {error}") from error


def _load_routes(database_path: str | Path) -> tuple[_StoredRoute, ...]:
    try:
        with _open_existing_connection(database_path) as connection:
            _assert_compatible_schema(connection, DEFAULT_LOCK_TIMEOUT_SECONDS)
            with connection.begin():
                route_rows = connection.execute(
                    text(
                        "SELECT r.dor_route_id, r.datasource_opening_id, "
                        "r.derived_position_id, o.do_eco, o.do_name, "
                        "p.dp_position_id, p.dp_placement, p.dp_side_to_move, "
                        "p.dp_castling_rights, p.dp_legal_en_passant "
                        "FROM derived_opening_route AS r "
                        "LEFT JOIN datasource_opening AS o "
                        "ON o.do_opening_id = r.datasource_opening_id "
                        "LEFT JOIN derived_position AS p "
                        "ON p.dp_position_id = r.derived_position_id "
                        "ORDER BY r.dor_route_id"
                    )
                ).all()
                move_rows = connection.execute(
                    text(
                        "SELECT derived_opening_route_id, dorm_ply, dorm_move_uci "
                        "FROM derived_opening_route_move "
                        "ORDER BY derived_opening_route_id, dorm_ply"
                    )
                ).all()
                return _materialize_routes(route_rows, move_rows)
    except SchemaIncompatibleError:
        raise
    except OpeningRecognitionError:
        raise
    except Exception as error:
        raise OpeningRecognitionError("opening catalogue could not be read") from error


def _materialize_routes(
    route_rows: list[object], move_rows: list[object]
) -> tuple[_StoredRoute, ...]:
    moves_by_route: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for row in move_rows:
        try:
            route_id = int(row[0])
            ply = int(row[1])
            move_uci = row[2]
        except (IndexError, TypeError, ValueError) as error:
            raise OpeningRecognitionError("opening route move row is malformed") from error
        if not isinstance(move_uci, str):
            raise OpeningRecognitionError("opening route move row is malformed")
        moves_by_route[route_id].append((ply, move_uci))

    routes: list[_StoredRoute] = []
    known_route_ids: set[int] = set()
    for row in route_rows:
        try:
            route_id = int(row[0])
            opening_id = int(row[1])
            position_id = int(row[2])
            eco = row[3]
            name = row[4]
            endpoint_row_id = row[5]
            endpoint_fields = tuple(row[index] for index in range(6, 10))
        except (IndexError, TypeError, ValueError) as error:
            raise OpeningRecognitionError("opening route row is malformed") from error
        if route_id in known_route_ids:
            raise OpeningRecognitionError("opening route identifiers are duplicated")
        known_route_ids.add(route_id)
        if not isinstance(eco, str) or not isinstance(name, str):
            raise OpeningRecognitionError("opening route label is malformed")
        if opening_id <= 0 or position_id <= 0 or endpoint_row_id is None:
            raise OpeningRecognitionError("opening route references are malformed")
        if endpoint_row_id != position_id or any(
            not isinstance(field, str) for field in endpoint_fields
        ):
            raise OpeningRecognitionError("opening route endpoint is malformed")

        endpoint = _canonical_endpoint(endpoint_fields)
        route_moves = moves_by_route.pop(route_id, [])
        if not route_moves:
            raise OpeningRecognitionError("opening route has no move rows")
        expected_plies = tuple(range(1, len(route_moves) + 1))
        actual_plies = tuple(ply for ply, _move_uci in route_moves)
        if actual_plies != expected_plies:
            raise OpeningRecognitionError("opening route plies are not contiguous")
        moves_uci = tuple(move_uci for _ply, move_uci in route_moves)
        _verify_route_replay(moves_uci, endpoint)
        routes.append(
            _StoredRoute(
                route_id=route_id,
                eco=eco,
                name=name,
                moves_uci=moves_uci,
                endpoint=endpoint,
            )
        )

    if moves_by_route:
        raise OpeningRecognitionError("opening route moves reference an unknown route")
    return tuple(sorted(routes, key=lambda route: (route.eco, route.name, route.moves_uci)))


def _canonical_endpoint(fields: tuple[str, ...]) -> CanonicalPosition:
    try:
        fen = " ".join((*fields, "0", "1"))
        position = canonicalize_fen(fen)
    except (TypeError, ValueError) as error:
        raise OpeningRecognitionError("stored opening endpoint is not canonical") from error
    return position


def _verify_route_replay(
    moves_uci: tuple[str, ...], endpoint: CanonicalPosition
) -> None:
    board = chess.Board()
    for ply, move_uci in enumerate(moves_uci, start=1):
        _push_stored_move(board, move_uci, ply)
    try:
        replayed = canonicalize_board(board)
    except ValueError as error:
        raise OpeningRecognitionError(
            "stored opening route produced an invalid position"
        ) from error
    if replayed != endpoint:
        raise OpeningRecognitionError("stored opening route endpoint does not match replay")


def _push_stored_move(board: chess.Board, move_uci: str, ply: int) -> None:
    try:
        move = chess.Move.from_uci(move_uci)
    except (TypeError, ValueError) as error:
        raise OpeningRecognitionError(f"stored opening move is invalid at ply {ply}") from error
    if move.uci() != move_uci or move not in board.legal_moves:
        raise OpeningRecognitionError(f"stored opening move is illegal at ply {ply}")
    board.push(move)


def _endpoint_map(
    routes: tuple[_StoredRoute, ...],
) -> dict[CanonicalPosition, tuple[_StoredRoute, ...]]:
    grouped: dict[CanonicalPosition, list[_StoredRoute]] = defaultdict(list)
    for route in routes:
        grouped[route.endpoint].append(route)
    return {
        endpoint: tuple(
            sorted(matching, key=lambda route: (route.eco, route.name, route.moves_uci))
        )
        for endpoint, matching in grouped.items()
    }


def _record_evidence(
    evidence: dict[tuple[int, str, str], MatchKind],
    ply: int,
    eco: str,
    name: str,
    match: MatchKind,
) -> None:
    key = (ply, eco, name)
    previous = evidence.get(key)
    if previous == "route" or match == previous:
        return
    evidence[key] = "route" if match == "route" else "transposition"


def _build_recognition(
    evidence: dict[tuple[int, str, str], MatchKind]
) -> OpeningRecognition:
    recognized = tuple(
        RecognizedOpening(ply=ply, eco=eco, name=name, match=match)
        for (ply, eco, name), match in sorted(evidence.items())
    )
    current = _select_current(recognized)
    return OpeningRecognition(recognized=recognized, current=current)


def _select_current(
    recognized: tuple[RecognizedOpening, ...],
) -> RecognizedOpening | None:
    if not recognized:
        return None
    deepest_ply = max(item.ply for item in recognized)
    deepest = tuple(item for item in recognized if item.ply == deepest_ply)
    if any(item.match == "route" for item in deepest):
        deepest = tuple(item for item in deepest if item.match == "route")
    return min(deepest, key=lambda item: (item.eco, item.name))
