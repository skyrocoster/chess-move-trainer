from types import SimpleNamespace

import chess
import pytest

from chess_move_trainer.statistical_analysis.features import ReplayState, move_features, pawn_structure
from chess_move_trainer.statistical_analysis.scoring import outcomes, expected_units
from chess_move_trainer.statistical_analysis.readers import time_control, timestamp


def result(wins, draws=0):
    return SimpleNamespace(lines=[SimpleNamespace(wdl_wins=wins, wdl_draws=draws)])


def test_exact_score_boundary_and_black_sign():
    board = chess.Board()
    after = board.copy()
    after.push_uci("e2e4")
    value = outcomes(board, after, result(650), result(450))
    assert value["loss_units"] == 400 and value["severe"] == 1
    following = after.copy()
    following.push_uci("e7e5")
    value = outcomes(after, following, result(650), result(400))
    assert value["signed_loss_units"] == -500 and value["loss_units"] == 0


@pytest.mark.parametrize("fen,color,expected", [
    ("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1", chess.WHITE, 2000),
    ("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1", chess.BLACK, 0),
    ("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1", chess.WHITE, 1000),
    ("7k/8/6K1/8/8/8/8/8 w - - 0 1", chess.WHITE, 1000),
])
def test_terminal_without_engine(fen, color, expected):
    assert expected_units(chess.Board(fen), color, None)[0] == expected


def test_en_passant_and_piece_identity():
    board, state = chess.Board(), ReplayState()
    for ply, uci in enumerate("e2e4 a7a6 e4e5 d7d5 e5d6".split(), 1):
        move = chess.Move.from_uci(uci)
        record = move_features(board, move, ply, state)
        state.apply(board, move)
        board.push(move)
    assert record["en_passant"] and record["captured_piece"] == "pawn"
    assert record["piece_identity"] == "e2"
    assert "d7" not in state.identities.values()


def test_castling_keeps_rook_identity():
    board, state = chess.Board(), ReplayState()
    for ply, uci in enumerate("e2e4 e7e5 g1f3 b8c6 f1c4 g8f6 e1g1".split(), 1):
        move = chess.Move.from_uci(uci)
        record = move_features(board, move, ply, state)
        state.apply(board, move)
        board.push(move)
    assert record["castling"]
    assert state.identities[chess.F1] == "h1"


@pytest.mark.parametrize("promote", ["q", "r", "b", "n"])
def test_promotions_are_pawn_moves(promote):
    board = chess.Board("7k/P7/8/8/8/8/8/7K w - - 0 1")
    state = ReplayState(identities={s: chess.square_name(s) for s in board.piece_map()})
    record = move_features(board, chess.Move.from_uci("a7a8" + promote), 50, state)
    assert record["piece"] == "pawn" and record["promotion"] != "none"


def test_pawn_structures_and_pinned_defender_are_literal():
    board = chess.Board("4k3/4n3/8/2P5/3P4/8/8/4R2K w - - 0 1")
    assert board.is_pinned(chess.BLACK, chess.E7)
    record = move_features(board, chess.Move.from_uci("c5c6"), 25,
                           ReplayState(identities={s: str(s) for s in board.piece_map()}))
    assert record["destination_attacked_before"]
    assert pawn_structure(board, chess.WHITE)["passed_pawns"] == 2


def test_time_metadata_is_not_guessed():
    assert time_control("600+5") == {"kind": "increment", "base": 600, "increment": 5}
    assert time_control("1/86400")["kind"] == "daily"
    assert time_control("?")["kind"] == "unsupported"
    assert timestamp("2026-09-22T12:00:00") is None
    assert timestamp("2026-09-22T12:00:00+02:00").hour == 10
