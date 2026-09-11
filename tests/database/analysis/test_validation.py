from __future__ import annotations

import pytest

from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
    AnalysisTerminalKind,
    AnalysisValidationError,
    classify_terminal_kind,
    validate_analysis_position,
)
from chess_move_trainer.database.positions import CanonicalPosition, canonicalize_fen

STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = f"{STARTING_PLACEMENT} w KQkq - 0 1"
CHECKMATE_FEN = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"
STALEMATE_FEN = "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"
INSUFFICIENT_MATERIAL_FEN = "8/8/8/8/8/8/2k5/6K1 w - - 0 1"
FEWER_THAN_FIVE_FEN = "7k/8/5Q2/6K1/8/8/8/8 b - - 0 1"


def _position(fen: str) -> CanonicalPosition:
    return canonicalize_fen(fen)


def _line(rank: int, *pv: str) -> AnalysisLine:
    return AnalysisLine(
        rank=rank,
        score_kind=AnalysisScoreKind.CP,
        score_value=rank * 10,
        wdl_wins=400,
        wdl_draws=300,
        wdl_losses=300,
        pv_uci=pv,
        depth=12,
    )


def _result(lines: list[AnalysisLine] | tuple[AnalysisLine, ...] = ()) -> AnalysisResultInput:
    return AnalysisResultInput(
        quality=AnalysisQuality.TOOL,
        configuration_version=1,
        settings={},
        engine_name="normalized-test-input",
        engine_version="1",
        lines=lines,
    )


def _starting_lines() -> list[AnalysisLine]:
    return [
        _line(1, "e2e4", "e7e5"),
        _line(2, "d2d4", "d7d5"),
        _line(3, "g1f3", "g8f6"),
        _line(4, "c2c4", "e7e5"),
        _line(5, "b1c3", "b8c6"),
    ]


@pytest.mark.parametrize(
    ("fen", "terminal_kind"),
    [
        (CHECKMATE_FEN, AnalysisTerminalKind.CHECKMATE),
        (STALEMATE_FEN, AnalysisTerminalKind.STALEMATE),
        (INSUFFICIENT_MATERIAL_FEN, AnalysisTerminalKind.INSUFFICIENT_MATERIAL),
    ],
)
def test_neutral_root_derives_each_approved_terminal_kind(
    fen: str,
    terminal_kind: AnalysisTerminalKind,
) -> None:
    position = _position(fen)

    assert classify_terminal_kind(position) is terminal_kind
    validated = validate_analysis_position(position, _result())
    assert validated.terminal_kind is terminal_kind
    assert validated.lines == ()


@pytest.mark.parametrize("fen", [CHECKMATE_FEN, STALEMATE_FEN, INSUFFICIENT_MATERIAL_FEN])
def test_terminal_positions_reject_candidate_lines(fen: str) -> None:
    with pytest.raises(AnalysisValidationError, match="zero candidate lines"):
        validate_analysis_position(_position(fen), _result([_line(1, "a2a3")]))


def test_neutral_root_does_not_use_halfmove_or_repetition_history_as_terminality() -> None:
    position = _position(f"{STARTING_PLACEMENT} w KQkq - 150 75")

    assert classify_terminal_kind(position) is None


def test_nonterminal_position_requires_five_legal_complete_lines() -> None:
    validated = validate_analysis_position(_position(STARTING_FEN), _result(_starting_lines()))

    assert validated.terminal_kind is None
    assert tuple(line.rank for line in validated.lines) == (1, 2, 3, 4, 5)
    assert tuple(line.pv_uci for line in validated.lines) == (
        ("e2e4", "e7e5"),
        ("d2d4", "d7d5"),
        ("g1f3", "g8f6"),
        ("c2c4", "e7e5"),
        ("b1c3", "b8c6"),
    )


def test_nonterminal_position_with_fewer_than_five_legal_moves_uses_all_roots() -> None:
    lines = [_line(1, "h8h7"), _line(2, "h8g8")]

    validated = validate_analysis_position(_position(FEWER_THAN_FIVE_FEN), _result(lines))

    assert validated.terminal_kind is None
    assert len(validated.lines) == 2


@pytest.mark.parametrize(
    "lines",
    [
        [],
        _starting_lines()[:4],
        [
            _line(1, "e2e4"),
            _line(2, "d2d4"),
            _line(4, "g1f3"),
            _line(5, "c2c4"),
            _line(5, "b1c3"),
        ],
    ],
)
def test_nonterminal_positions_reject_missing_or_noncontiguous_lines(
    lines: list[AnalysisLine],
) -> None:
    with pytest.raises(AnalysisValidationError):
        validate_analysis_position(_position(STARTING_FEN), _result(lines))


def test_candidate_root_moves_must_be_distinct_and_legal() -> None:
    duplicate_root = _starting_lines()
    duplicate_root[-1] = _line(5, "e2e4", "e7e5")
    illegal_root = _starting_lines()
    illegal_root[-1] = _line(5, "e2e5")

    with pytest.raises(AnalysisValidationError, match="root moves must be distinct"):
        validate_analysis_position(_position(STARTING_FEN), _result(duplicate_root))
    with pytest.raises(AnalysisValidationError, match="illegal"):
        validate_analysis_position(_position(STARTING_FEN), _result(illegal_root))


@pytest.mark.parametrize(
    "pv",
    [
        ("e2e9",),
        ("e2e4", "e2e5"),
        ("e2e4", "not-uci"),
    ],
)
def test_malformed_or_later_illegal_pv_moves_are_rejected(pv: tuple[str, ...]) -> None:
    lines = _starting_lines()
    lines[0] = _line(1, *pv)

    with pytest.raises(AnalysisValidationError):
        validate_analysis_position(_position(STARTING_FEN), _result(lines))
