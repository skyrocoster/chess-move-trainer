from __future__ import annotations

import chess
import pytest

from chess_move_trainer.database.positions import PositionValidationError, canonicalize_fen

LEGAL_EN_PASSANT_FEN = (
    "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
)
NO_CAPTURER_FEN = (
    "rnbqkbnr/ppp1pppp/8/3p4/8/P7/1PPPPPPP/RNBQKBNR w KQkq d6 0 2"
)
PINNED_CAPTURER_FEN = (
    "4r1k1/ppp2ppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQ d6 0 3"
)


@pytest.mark.parametrize(
    ("fen", "expected_en_passant"),
    [
        (LEGAL_EN_PASSANT_FEN, "d6"),
        (NO_CAPTURER_FEN, "-"),
        (PINNED_CAPTURER_FEN, "-"),
    ],
)
def test_legal_only_en_passant_normalization(fen: str, expected_en_passant: str) -> None:
    position = canonicalize_fen(fen)

    assert position.legal_en_passant == expected_en_passant


def test_impossible_en_passant_geometry_is_rejected_instead_of_repaired() -> None:
    impossible = "rnbqkbnr/ppp1pppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq d6 0 1"

    with pytest.raises(PositionValidationError):
        canonicalize_fen(impossible)


@pytest.mark.parametrize(
    "fen",
    [
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq i6 0 3",
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d5 0 3",
    ],
)
def test_malformed_en_passant_target_is_rejected(fen: str) -> None:
    with pytest.raises(PositionValidationError):
        canonicalize_fen(fen)


def test_board_input_does_not_mutate_classic_en_passant_state() -> None:
    board = chess.Board(PINNED_CAPTURER_FEN)
    before = (
        board.fen(en_passant="fen"),
        board.turn,
        board.castling_rights,
        board.ep_square,
        board.halfmove_clock,
        board.fullmove_number,
        len(board.move_stack),
    )

    canonicalize_fen(PINNED_CAPTURER_FEN)
    after = (
        board.fen(en_passant="fen"),
        board.turn,
        board.castling_rights,
        board.ep_square,
        board.halfmove_clock,
        board.fullmove_number,
        len(board.move_stack),
    )

    assert after == before
