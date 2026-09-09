"""From-scratch validation and canonicalization of chess positions."""

from __future__ import annotations

import chess

from .._position_identity import CanonicalPosition


class PositionValidationError(ValueError):
    """Raised when an input does not describe an acceptable chess position."""


def canonicalize_fen(fen: str) -> CanonicalPosition:
    """Validate a complete six-field FEN and return its canonical identity."""

    if not isinstance(fen, str):
        raise PositionValidationError("FEN must be a complete six-field string")

    fields = fen.split()
    if len(fields) != 6:
        raise PositionValidationError("FEN must contain exactly six fields")
    _validate_fen_counters(fields[4], fields[5])

    try:
        board = chess.Board(" ".join(fields))
    except (TypeError, ValueError) as error:
        raise PositionValidationError(f"invalid FEN: {error}") from error

    return canonicalize_board(board)


def canonicalize_board(board: chess.Board) -> CanonicalPosition:
    """Validate a board without mutating it and return its legal-only identity."""

    if not isinstance(board, chess.Board):
        raise PositionValidationError("position must be a chess.Board")

    working = board.copy(stack=False)
    _validate_counters(working)

    base = working.copy(stack=False)
    ep_square = base.ep_square
    base.ep_square = None

    if not base.is_valid():
        raise PositionValidationError("board is not a valid chess position")

    if ep_square is not None:
        _validate_en_passant_geometry(working, ep_square)

    try:
        fields = working.fen(en_passant="legal").split()
    except (TypeError, ValueError) as error:
        raise PositionValidationError(f"position could not be canonicalized: {error}") from error

    if len(fields) != 6:
        raise PositionValidationError("canonical board FEN must contain six fields")

    return CanonicalPosition(
        placement=fields[0],
        side_to_move=fields[1],
        castling_rights=fields[2],
        legal_en_passant=fields[3],
    )


def _validate_counters(board: chess.Board) -> None:
    if type(board.halfmove_clock) is not int or board.halfmove_clock < 0:
        raise PositionValidationError("halfmove clock must be a non-negative integer")
    if type(board.fullmove_number) is not int or board.fullmove_number < 1:
        raise PositionValidationError("fullmove number must be a positive integer")


def _validate_fen_counters(halfmove: str, fullmove: str) -> None:
    if not halfmove or any(character not in "0123456789" for character in halfmove):
        raise PositionValidationError("halfmove clock must be a non-negative integer")
    if not fullmove or any(character not in "0123456789" for character in fullmove):
        raise PositionValidationError("fullmove number must be a positive integer")
    if int(fullmove) < 1:
        raise PositionValidationError("fullmove number must be a positive integer")


def _validate_en_passant_geometry(board: chess.Board, ep_square: int) -> None:
    if type(ep_square) is not int or not 0 <= ep_square < 64:
        raise PositionValidationError("en-passant square is outside the board")

    expected_rank = 5 if board.turn == chess.WHITE else 2
    if chess.square_rank(ep_square) != expected_rank:
        raise PositionValidationError("en-passant square has an impossible rank")
    if board.piece_at(ep_square) is not None:
        raise PositionValidationError("en-passant square must be empty")

    moved_square = ep_square - 8 if board.turn == chess.WHITE else ep_square + 8
    source_square = ep_square + 8 if board.turn == chess.WHITE else ep_square - 8
    moved_piece = board.piece_at(moved_square)
    if moved_piece != chess.Piece(chess.PAWN, not board.turn):
        raise PositionValidationError("en-passant target has no matching double-pushed pawn")
    if board.piece_at(source_square) is not None:
        raise PositionValidationError("en-passant source square is occupied")
