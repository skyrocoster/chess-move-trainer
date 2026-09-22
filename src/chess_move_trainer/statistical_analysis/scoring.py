"""Exact WDL arithmetic; signed discrepancies are retained, never discarded."""

import chess

from .protocol import DEFAULT_PROTOCOL as P


def expected_units(board, color, result):
    if board.is_checkmate():
        return (0 if board.turn == color else 2000), "checkmate"
    if board.is_stalemate():
        return 1000, "stalemate"
    if board.is_insufficient_material():
        return 1000, "insufficient_material"
    if result is None:
        return None, "missing_analysis"
    if not result.lines:
        raise ValueError("nonterminal position requires a rank-one line")
    line = result.lines[0]
    white = 2 * line.wdl_wins + line.wdl_draws
    return (white if color else 2000 - white), "engine"


def outcomes(board, after, before_result, after_result):
    before, before_kind = expected_units(board, board.turn, before_result)
    following, after_kind = expected_units(after, board.turn, after_result)
    signed = before - following if before is not None and following is not None else None
    loss = max(0, signed) if signed is not None else None
    return {
        "expected_before_units": before, "expected_after_units": following,
        "before_score_source": before_kind, "after_score_source": after_kind,
        "signed_loss_units": signed, "loss_units": loss,
        "loss": loss / 2000 if loss is not None else None,
        "severe": int(loss >= P.severe_loss_units) if loss is not None else None,
        "severe_010": int(loss >= 200) if loss is not None else None,
        "severe_030": int(loss >= 600) if loss is not None else None,
    }


def engine_features(board, move, result):
    if result is None or not result.lines:
        return {"rank_one_agreement": None, "stored_candidates": 0,
                "played_in_stored_candidates": None, "sound_stored_candidates": None,
                "stored_candidate_spread": None}
    scores = [(2 * line.wdl_wins + line.wdl_draws) for line in result.lines]
    if not board.turn:
        scores = [2000 - s for s in scores]
    return {
        "rank_one_agreement": move.uci() == result.lines[0].pv_uci[0],
        "stored_candidates": len(scores),
        "played_in_stored_candidates": any(move.uci() == line.pv_uci[0] for line in result.lines),
        "sound_stored_candidates": sum(score >= scores[0] - P.sound_distance_units for score in scores),
        "stored_candidate_spread": (max(scores) - min(scores)) / 2000,
    }
