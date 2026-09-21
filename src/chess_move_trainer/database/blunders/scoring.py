"""Internal scoring of comparable trainer moves."""

from __future__ import annotations

import chess

from .errors import BlunderStorageError
from .models import BlunderItem, _round_public
from .records import _Analysis, _GameScope, _Occurrence


def _score_pair(
    scope: _GameScope,
    before: _Occurrence,
    after: _Occurrence,
    analyses: dict[int, _Analysis],
) -> tuple[float, tuple[float, str, str, int, BlunderItem]] | None:
    """Score one trainer move, or return None when it is not comparable."""

    before_analysis = analyses.get(before.position_id)
    after_analysis = analyses.get(after.position_id)
    if before_analysis is None or after_analysis is None:
        return None
    if before_analysis.terminal_kind is not None:
        return None
    if (
        before_analysis.rank1_wins is None
        or before_analysis.rank1_draws is None
        or before_analysis.rank1_losses is None
        or before_analysis.rank1_preferred_move is None
    ):
        return None
    _validate_preferred_move(before, before_analysis.rank1_preferred_move)
    white_before = (before_analysis.rank1_wins + 0.5 * before_analysis.rank1_draws) / 1000
    if after_analysis.terminal_kind is not None:
        white_after = _terminal_white_score(after_analysis.terminal_kind, after.side_to_move)
    elif (
        after_analysis.rank1_wins is None
        or after_analysis.rank1_draws is None
        or after_analysis.rank1_losses is None
    ):
        return None
    else:
        white_after = (after_analysis.rank1_wins + 0.5 * after_analysis.rank1_draws) / 1000
    if scope.trainer_color == "white":
        trainer_before, trainer_after = white_before, white_after
    else:
        trainer_before, trainer_after = 1.0 - white_before, 1.0 - white_after
    before_rounded = _round_public(trainer_before)
    after_rounded = _round_public(trainer_after)
    loss = _round_public(before_rounded - after_rounded)
    assert before.move_uci is not None
    assert before_analysis.rank1_preferred_move is not None
    item = BlunderItem(
        game_uuid=scope.game_uuid,
        source_url=scope.source_url,
        started_at_utc=scope.started_at_utc,
        trainer_color=scope.trainer_color,
        ply=before.ply,
        fen=before.fen,
        played_move_uci=before.move_uci,
        preferred_move_uci=before_analysis.rank1_preferred_move,
        expected_score_before=before_rounded,
        expected_score_after=after_rounded,
        expected_score_loss=loss,
        before_analysis_quality=before_analysis.quality,
        after_analysis_quality=after_analysis.quality,
    )
    return loss, (loss, scope.started_at_sortable, scope.game_uuid, before.ply, item)


def _compare_scored(
    left: tuple[float, str, str, int, BlunderItem],
    right: tuple[float, str, str, int, BlunderItem],
) -> int:
    if left[0] != right[0]:
        return -1 if left[0] > right[0] else 1
    if left[1] != right[1]:
        return -1 if left[1] > right[1] else 1
    if left[2] != right[2]:
        return -1 if left[2] < right[2] else 1
    return (left[3] > right[3]) - (left[3] < right[3])


def _terminal_white_score(terminal_kind: str, after_side_to_move: str) -> float:
    """Score a terminal after-position from the White perspective."""

    if after_side_to_move not in ("w", "b"):
        raise BlunderStorageError("terminal position side is malformed")
    if terminal_kind == "checkmate":
        return 0.0 if after_side_to_move == "w" else 1.0
    return 0.5


def _validate_transition(before: _Occurrence, after: _Occurrence) -> None:
    """Prove that the stored outgoing move reaches the consecutive position."""

    assert before.move_uci is not None
    try:
        board = chess.Board(before.fen)
        move = chess.Move.from_uci(before.move_uci)
        if move not in board.legal_moves:
            raise ValueError("stored outgoing move is illegal")
        board.push(move)
        reached = tuple(board.fen(en_passant="legal").split()[:4])
        expected = (
            after.placement,
            after.side_to_move,
            after.castling_rights,
            after.legal_en_passant,
        )
        if reached != expected:
            raise ValueError("stored consecutive position does not follow its move")
    except (TypeError, ValueError) as error:
        raise BlunderStorageError("stored game transition is malformed") from error


def _validate_preferred_move(before: _Occurrence, preferred_move: str) -> None:
    """Prove the stored preferred first move is legal in the before position."""

    try:
        board = chess.Board(before.fen)
        move = chess.Move.from_uci(preferred_move)
        if move.uci() != preferred_move or move not in board.legal_moves:
            raise ValueError("stored preferred move is illegal")
    except (TypeError, ValueError) as error:
        raise BlunderStorageError("stored preferred move is illegal") from error


__all__ = [
    "_compare_scored",
    "_score_pair",
    "_terminal_white_score",
    "_validate_preferred_move",
    "_validate_transition",
]
