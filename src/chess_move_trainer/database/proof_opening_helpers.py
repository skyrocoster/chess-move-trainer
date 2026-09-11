"""Pure opening helpers for direct-database proof inputs."""
from __future__ import annotations

import chess

from .openings.source import OpeningRouteSource
from .positions import canonicalize_board
from .proof_models import DirectPreflightError


def _positive_scalar(value: object) -> int:
    if type(value) is not int or value < 1:
        raise DirectPreflightError("fixed direct database lacks a usable proof input")
    return value


def _pgn_for_moves(moves_uci: tuple[str, ...]) -> str:
    board = chess.Board()
    tokens: list[str] = []
    for move_uci in moves_uci:
        try:
            move = chess.Move.from_uci(move_uci)
        except (TypeError, ValueError) as error:
            raise DirectPreflightError("opening source move could not be replayed") from error
        if move not in board.legal_moves:
            raise DirectPreflightError("opening source move is not legal")
        if board.turn is chess.WHITE:
            tokens.append(f"{board.fullmove_number}.")
        elif not tokens:
            tokens.append(f"{board.fullmove_number}...")
        tokens.append(board.san(move))
        board.push(move)
    if not tokens:
        raise DirectPreflightError("opening source route has no moves")
    return " ".join(tokens)


def _opening_label(item: object) -> tuple[str, str]:
    return (str(item.eco), str(item.name))


def _find_transposition_pair(
    routes: tuple[OpeningRouteSource, ...],
) -> tuple[OpeningRouteSource, tuple[str, ...]]:
    source_identities = {
        (route.eco, route.name, route.moves_uci) for route in routes
    }
    ordered = sorted(routes, key=lambda route: (len(route.moves_uci), route.eco, route.name))
    for route in ordered:
        for transposed_moves in _bounded_move_reorders(route.moves_uci):
            if (route.eco, route.name, transposed_moves) in source_identities:
                continue
            try:
                board = _board_for_moves(transposed_moves)
            except DirectPreflightError:
                continue
            if canonicalize_board(board) == route.endpoint_position:
                return route, transposed_moves
    raise DirectPreflightError("pinned opening source has no bounded transposition pair")


def _bounded_move_reorders(moves_uci: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    """Return bounded deterministic reorders of one pinned source route."""

    candidates: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()
    for start in range(len(moves_uci)):
        for destination in range(len(moves_uci)):
            if start == destination:
                continue
            reordered = list(moves_uci)
            moved = reordered.pop(start)
            reordered.insert(destination, moved)
            candidate = tuple(reordered)
            if candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)
    for first in range(len(moves_uci)):
        for second in range(first + 1, len(moves_uci)):
            if first % 2 != second % 2:
                continue
            reordered = list(moves_uci)
            reordered[first], reordered[second] = reordered[second], reordered[first]
            candidate = tuple(reordered)
            if candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)
    return tuple(candidates)


def _board_for_moves(moves_uci: tuple[str, ...]) -> chess.Board:
    board = chess.Board()
    for move_uci in moves_uci:
        try:
            move = chess.Move.from_uci(move_uci)
        except (TypeError, ValueError) as error:
            raise DirectPreflightError("opening source move could not be replayed") from error
        if move not in board.legal_moves:
            raise DirectPreflightError("opening source move is not legal")
        board.push(move)
    return board


def _find_nested_routes(
    routes: tuple[OpeningRouteSource, ...],
) -> tuple[OpeningRouteSource, OpeningRouteSource]:
    ordered = sorted(routes, key=lambda route: (len(route.moves_uci), route.eco, route.name))
    for deep in ordered:
        for prefix in ordered:
            if len(prefix.moves_uci) >= len(deep.moves_uci):
                continue
            if deep.moves_uci[: len(prefix.moves_uci)] != prefix.moves_uci:
                continue
            if _opening_label(prefix) == _opening_label(deep):
                continue
            return prefix, deep
    raise DirectPreflightError("pinned opening source has no bounded nested route pair")


