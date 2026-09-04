from __future__ import annotations

from dataclasses import FrozenInstanceError

import chess
import pytest

from chess_move_trainer.database.positions import (
    CanonicalPosition,
    PositionValidationError,
    canonicalize_board,
    canonicalize_fen,
)


STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = f"{STARTING_PLACEMENT} w KQkq - 0 1"


def test_board_input_returns_immutable_ordinary_canonical_data_without_mutation() -> None:
    board = chess.Board(STARTING_FEN)
    before = board.fen(en_passant="fen")

    position = canonicalize_board(board)

    assert isinstance(position, CanonicalPosition)
    assert position.placement == STARTING_PLACEMENT
    assert position.side_to_move == "w"
    assert position.castling_rights == "KQkq"
    assert position.legal_en_passant == "-"
    assert board.fen(en_passant="fen") == before
    with pytest.raises(FrozenInstanceError):
        position.placement = "8"  # type: ignore[misc]


def test_complete_fen_and_board_inputs_produce_the_same_identity() -> None:
    fen = f"{STARTING_PLACEMENT} w KQkq - 17 42"

    from_fen = canonicalize_fen(fen)
    from_board = canonicalize_board(chess.Board(fen))

    assert from_fen == from_board
    assert from_fen == CanonicalPosition(STARTING_PLACEMENT, "w", "KQkq", "-")


def test_castling_rights_are_returned_in_canonical_order() -> None:
    position = canonicalize_board(chess.Board(STARTING_FEN))

    assert position.castling_rights == "KQkq"


@pytest.mark.parametrize(
    "fen",
    [
        STARTING_PLACEMENT + " w KQkq -",
        STARTING_PLACEMENT + " w KQkq - 0",
        STARTING_PLACEMENT + " w KQkq - -1 1",
        STARTING_PLACEMENT + " w KQkq - 0 0",
        STARTING_PLACEMENT + " x KQkq - 0 1",
    ],
)
def test_complete_fen_requires_valid_side_and_counters(fen: str) -> None:
    with pytest.raises(PositionValidationError):
        canonicalize_fen(fen)


def test_board_counters_are_validated_but_excluded_from_identity() -> None:
    first = chess.Board(STARTING_FEN)
    second = chess.Board(f"{STARTING_PLACEMENT} w KQkq - 99 120")
    first.halfmove_clock = 12
    first.fullmove_number = 34

    assert canonicalize_board(first) == canonicalize_board(second)

    first.halfmove_clock = -1
    with pytest.raises(PositionValidationError):
        canonicalize_board(first)


@pytest.mark.parametrize(
    "fen",
    [
        "8/8/8/8/8/8/8/4K3 w - - 0 1",
        "4k3/8/8/8/8/8/8/P3K3 w - - 0 1",
        "4k3/8/8/8/8/8/8/4K3 w K - 0 1",
    ],
)
def test_invalid_positions_are_rejected_before_storage(fen: str) -> None:
    with pytest.raises(PositionValidationError):
        canonicalize_fen(fen)


def test_raw_four_field_storage_input_is_not_accepted() -> None:
    with pytest.raises(PositionValidationError):
        canonicalize_fen(STARTING_PLACEMENT + " w KQkq")
