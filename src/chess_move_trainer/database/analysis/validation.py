"""Pure input-domain validation for normalized analysis values."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

import chess

from .models import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
    AnalysisTerminalKind,
    AnalysisValidationError,
    ValidatedAnalysisResult,
    _FrozenJsonObject,
)
from ..positions import CanonicalPosition


def _normalize_quality(value: object) -> AnalysisQuality:
    try:
        return AnalysisQuality(value)
    except (TypeError, ValueError) as error:
        raise AnalysisValidationError("quality must be 'browser' or 'tool'") from error


def _normalize_score_kind(value: object) -> AnalysisScoreKind:
    try:
        return AnalysisScoreKind(value)
    except (TypeError, ValueError) as error:
        raise AnalysisValidationError("score kind must be 'cp' or 'mate'") from error


def _require_domain_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise AnalysisValidationError(f"{label} must be an integer")
    return value


def _freeze_json(value: object) -> Any:
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise AnalysisValidationError("settings object keys must be strings")
            frozen[key] = _freeze_json(nested)
        return _FrozenJsonObject(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(nested) for nested in value)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise AnalysisValidationError("settings must contain only JSON-serializable values")


def _normalize_settings(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AnalysisValidationError("settings must be a JSON object/mapping")
    try:
        normalized = _freeze_json(value)
        json.dumps(normalized, allow_nan=False)
    except AnalysisValidationError:
        raise
    except (TypeError, ValueError, OverflowError) as error:
        raise AnalysisValidationError("settings must be a valid JSON object") from error
    if not isinstance(normalized, _FrozenJsonObject):
        raise AnalysisValidationError("settings must be a JSON object/mapping")
    return normalized


def _normalize_pv(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise AnalysisValidationError("PV must be a non-empty ordered move sequence")
    try:
        normalized = tuple(value)  # type: ignore[arg-type]
    except TypeError as error:
        raise AnalysisValidationError("PV must be a non-empty ordered move sequence") from error
    if not normalized:
        raise AnalysisValidationError("PV must be a non-empty ordered move sequence")
    if any(not isinstance(move, str) or not move for move in normalized):
        raise AnalysisValidationError("PV must contain non-empty string move values")
    return normalized


def validate_settings_object(value: object) -> Mapping[str, Any]:
    """Validate and freeze one JSON object without requiring any setting keys."""

    return _normalize_settings(value)


def validate_analysis_line(
    *,
    rank: object,
    score_kind: object,
    score_value: object,
    wdl_wins: object,
    wdl_draws: object,
    wdl_losses: object,
    pv_uci: object,
    depth: object,
) -> AnalysisLine:
    """Construct one normalized line after pure scalar/domain validation."""

    return AnalysisLine(
        rank=rank,  # type: ignore[arg-type]
        score_kind=score_kind,  # type: ignore[arg-type]
        score_value=score_value,  # type: ignore[arg-type]
        wdl_wins=wdl_wins,  # type: ignore[arg-type]
        wdl_draws=wdl_draws,  # type: ignore[arg-type]
        wdl_losses=wdl_losses,  # type: ignore[arg-type]
        pv_uci=pv_uci,  # type: ignore[arg-type]
        depth=depth,  # type: ignore[arg-type]
    )


def validate_analysis_result(
    *,
    quality: object,
    configuration_version: object,
    settings: object,
    engine_name: object,
    engine_version: object,
    lines: object = (),
) -> AnalysisResultInput:
    """Construct one normalized result payload without database or chess checks."""

    return AnalysisResultInput(
        quality=quality,  # type: ignore[arg-type]
        configuration_version=configuration_version,  # type: ignore[arg-type]
        settings=settings,  # type: ignore[arg-type]
        engine_name=engine_name,  # type: ignore[arg-type]
        engine_version=engine_version,  # type: ignore[arg-type]
        lines=lines,  # type: ignore[arg-type]
    )


def _neutral_board(position: CanonicalPosition) -> chess.Board:
    if not isinstance(position, CanonicalPosition):
        raise AnalysisValidationError("position must be a canonical position value")
    try:
        return chess.Board(
            " ".join(
                (
                    position.placement,
                    position.side_to_move,
                    position.castling_rights,
                    position.legal_en_passant,
                    "0",
                    "1",
                )
            )
        )
    except (TypeError, ValueError) as error:
        raise AnalysisValidationError("canonical position could not form a neutral root") from error


def _classify_board(board: chess.Board) -> AnalysisTerminalKind | None:
    if board.is_checkmate():
        return AnalysisTerminalKind.CHECKMATE
    if board.is_stalemate():
        return AnalysisTerminalKind.STALEMATE
    if board.is_insufficient_material():
        return AnalysisTerminalKind.INSUFFICIENT_MATERIAL
    return None


def classify_terminal_kind(position: CanonicalPosition) -> AnalysisTerminalKind | None:
    """Derive the approved terminal kind from a canonical position's neutral root."""

    return _classify_board(_neutral_board(position))


def _validate_line_moves(board: chess.Board, line: AnalysisLine) -> str:
    working = board.copy(stack=False)
    root_uci = ""
    for ply, move_text in enumerate(line.pv_uci, start=1):
        try:
            move = chess.Move.from_uci(move_text)
        except ValueError as error:
            raise AnalysisValidationError(
                f"rank {line.rank} contains malformed UCI at PV ply {ply}"
            ) from error
        if move not in working.legal_moves:
            raise AnalysisValidationError(
                f"rank {line.rank} contains an illegal move at PV ply {ply}"
            )
        if ply == 1:
            root_uci = move.uci()
        working.push(move)
    return root_uci


def validate_analysis_position(
    position: CanonicalPosition,
    result: AnalysisResultInput,
) -> ValidatedAnalysisResult:
    """Validate terminal policy and complete legal candidate lines from a neutral root."""

    if not isinstance(result, AnalysisResultInput):
        raise AnalysisValidationError("result must be an AnalysisResultInput value")
    board = _neutral_board(position)
    terminal_kind = _classify_board(board)
    if terminal_kind is not None:
        if result.lines:
            raise AnalysisValidationError("terminal positions must have zero candidate lines")
        return ValidatedAnalysisResult(terminal_kind=terminal_kind, lines=())

    legal_root_moves = tuple(board.legal_moves)
    expected_line_count = min(5, len(legal_root_moves))
    if len(result.lines) != expected_line_count:
        raise AnalysisValidationError(
            "non-terminal results must contain exactly five lines or one line per legal root move"
        )
    expected_ranks = tuple(range(1, expected_line_count + 1))
    actual_ranks = tuple(line.rank for line in result.lines)
    if actual_ranks != expected_ranks:
        raise AnalysisValidationError("candidate line ranks must be contiguous from 1")

    legal_root_uci = {move.uci() for move in legal_root_moves}
    seen_root_uci: set[str] = set()
    for line in result.lines:
        root_uci = _validate_line_moves(board, line)
        if root_uci not in legal_root_uci:
            raise AnalysisValidationError(
                f"rank {line.rank} does not begin with a legal root move"
            )
        if root_uci in seen_root_uci:
            raise AnalysisValidationError("candidate line root moves must be distinct")
        seen_root_uci.add(root_uci)
    return ValidatedAnalysisResult(terminal_kind=None, lines=result.lines)
