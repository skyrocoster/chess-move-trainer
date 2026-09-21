"""Internal row loaders for trainer blunder discovery."""

from __future__ import annotations

import json
from collections.abc import Iterable
from uuid import UUID

import chess
from sqlalchemy import text

from ..positions import canonicalize_fen
from ..query_helpers import chunk_sorted_ids
from ..validation import (
    comparable_timestamp,
    require_int,
    require_non_negative_int,
    require_positive_int,
    require_text,
)
from .errors import BlunderError, BlunderStorageError
from .models import BlunderQuery
from .records import _Analysis, _GameScope, _Occurrence

_TERMINAL_KINDS = ("checkmate", "stalemate", "insufficient_material")
_QUALITIES = ("browser", "tool")
_CHUNK_SIZE = 500


def _chunked_ids(values: Iterable[int]) -> list[list[int]]:
    """Return sorted unique identifiers in bounded 500-entry chunks."""

    return chunk_sorted_ids(values, _CHUNK_SIZE)


def _load_scoped_games(
    connection: object, query: BlunderQuery
) -> tuple[dict[int, _GameScope], int, int]:
    try:
        rows = connection.execute(
            text(
                """
                SELECT dg_game_id, dg_chesscom_game_uuid, dg_source_url,
                       dg_trainer_color, dg_started_at_utc
                FROM datasource_game
                ORDER BY dg_game_id
                """
            )
        ).all()
    except BlunderError:
        raise
    except Exception as error:
        raise BlunderStorageError("games could not be read") from error
    games: dict[int, _GameScope] = {}
    examined = 0
    excluded = 0
    try:
        for row in rows:
            game_id = require_int(row[0], "game id")
            if game_id in games:
                raise BlunderStorageError("game identifiers are duplicated")
            examined += 1
            sortable = comparable_timestamp(row[4])
            if sortable is None:
                excluded += 1
                continue
            if not query.started_at_from <= sortable <= query.started_at_to:
                continue
            trainer_color = row[3]
            if trainer_color not in ("white", "black"):
                raise ValueError("stored trainer color is malformed")
            if query.trainer_color is not None and trainer_color != query.trainer_color:
                continue
            game_uuid = require_text(row[1], "game UUID")
            UUID(game_uuid)
            games[game_id] = _GameScope(
                game_uuid=game_uuid,
                source_url=require_text(row[2], "source URL"),
                trainer_color=trainer_color,
                started_at_utc=require_text(row[4], "game start timestamp"),
                started_at_sortable=sortable,
            )
    except BlunderError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise BlunderStorageError("game row is malformed") from error
    return games, examined, excluded


def _load_occurrences(connection: object, game_ids: set[int]) -> dict[int, tuple[_Occurrence, ...]]:
    if not game_ids:
        return {}
    grouped: dict[int, list[_Occurrence]] = {}
    try:
        for chunk in _chunked_ids(game_ids):
            predicate = ", ".join(str(game_id) for game_id in chunk)
            rows = connection.execute(
                text(
                    f"""
                    SELECT o.datasource_game_id, o.dgp_ply, o.derived_position_id,
                           o.dgp_move_uci, p.dp_placement, p.dp_side_to_move,
                           p.dp_castling_rights, p.dp_legal_en_passant,
                           o.dgp_halfmove_clock, o.dgp_fullmove_number
                    FROM derived_game_position AS o
                    JOIN derived_position AS p
                      ON p.dp_position_id = o.derived_position_id
                    WHERE o.datasource_game_id IN ({predicate})
                    ORDER BY o.datasource_game_id, o.dgp_ply
                    """
                )
            ).all()
            for row in rows:
                game_id = require_int(row[0], "occurrence game id")
                if game_id not in game_ids:
                    raise ValueError("occurrence references an unknown game")
                move_uci = row[3]
                if move_uci is not None:
                    _validate_uci(move_uci, "stored outgoing move")
                side_to_move = require_text(row[5], "position side")
                if side_to_move not in ("w", "b"):
                    raise ValueError("stored position side is malformed")
                occurrence = _Occurrence(
                    ply=require_non_negative_int(row[1], "occurrence ply"),
                    position_id=require_positive_int(row[2], "position id"),
                    placement=require_text(row[4], "position placement"),
                    side_to_move=side_to_move,
                    castling_rights=require_text(row[6], "position castling"),
                    legal_en_passant=require_text(row[7], "position en-passant"),
                    move_uci=move_uci,
                    halfmove_clock=require_non_negative_int(row[8], "position halfmove clock"),
                    fullmove_number=require_positive_int(row[9], "position fullmove number"),
                )
                _validate_position(occurrence)
                grouped.setdefault(game_id, []).append(occurrence)
    except BlunderError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise BlunderStorageError("game occurrence row is malformed") from error
    return {game_id: tuple(ordered) for game_id, ordered in grouped.items()}


def _load_analyses(
    connection: object,
    occurrences: dict[int, tuple[_Occurrence, ...]],
    games: dict[int, _GameScope],
) -> dict[int, _Analysis]:
    wanted: set[int] = set()
    for game_id, ordered in occurrences.items():
        scope = games.get(game_id)
        if scope is None:
            continue
        expected_side = "w" if scope.trainer_color == "white" else "b"
        for index in range(len(ordered) - 1):
            before = ordered[index]
            after = ordered[index + 1]
            if after.ply != before.ply + 1:
                continue
            if before.move_uci is None or before.side_to_move != expected_side:
                continue
            wanted.add(before.position_id)
            wanted.add(after.position_id)
    if not wanted:
        return {}
    rank1: dict[int, tuple[int, int, int, str]] = {}
    resolved: dict[int, _Analysis] = {}
    try:
        for chunk in _chunked_ids(wanted):
            predicate = ", ".join(str(position_id) for position_id in chunk)
            parents = connection.execute(
                text(
                    f"""
                    SELECT derived_position_id, dar_quality, dar_terminal_kind
                    FROM derived_analysis_result
                    WHERE derived_position_id IN ({predicate})
                    """
                )
            ).all()
            lines = connection.execute(
                text(
                    f"""
                    SELECT derived_analysis_result_id, dal_wdl_wins,
                           dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json
                    FROM derived_analysis_line
                    WHERE derived_analysis_result_id IN ({predicate})
                      AND dal_rank = 1
                    """
                )
            ).all()
            for row in lines:
                position_id = require_int(row[0], "analysis position id")
                if position_id in rank1:
                    raise BlunderStorageError("analysis rank-1 lines are duplicated")
                wins = require_non_negative_int(row[1], "WDL wins")
                draws = require_non_negative_int(row[2], "WDL draws")
                losses = require_non_negative_int(row[3], "WDL losses")
                if wins + draws + losses != 1000:
                    raise ValueError("stored WDL values must sum to 1000")
                rank1[position_id] = (wins, draws, losses, _preferred_move(row[4]))
            for row in parents:
                position_id = require_int(row[0], "analysis position id")
                if position_id not in wanted:
                    raise ValueError("analysis references an unknown position")
                if position_id in resolved:
                    raise BlunderStorageError("analysis results are duplicated")
                quality = row[1]
                if quality not in _QUALITIES:
                    raise ValueError("stored analysis quality is malformed")
                terminal_kind = row[2]
                if terminal_kind is not None and terminal_kind not in _TERMINAL_KINDS:
                    raise ValueError("stored terminal kind is malformed")
                if terminal_kind is not None and position_id in rank1:
                    raise ValueError("terminal analysis must not have candidate lines")
                line = rank1.get(position_id)
                resolved[position_id] = _Analysis(
                    quality=quality,
                    terminal_kind=terminal_kind,
                    rank1_wins=line[0] if line else None,
                    rank1_draws=line[1] if line else None,
                    rank1_losses=line[2] if line else None,
                    rank1_preferred_move=line[3] if line else None,
                )
    except BlunderError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise BlunderStorageError("analysis row is malformed") from error
    return resolved


def _validate_position(occurrence: _Occurrence) -> None:
    """Reject a stored occurrence whose position is not canonical and legal."""

    position = canonicalize_fen(occurrence.fen)
    if (
        position.placement,
        position.side_to_move,
        position.castling_rights,
        position.legal_en_passant,
    ) != (
        occurrence.placement,
        occurrence.side_to_move,
        occurrence.castling_rights,
        occurrence.legal_en_passant,
    ):
        raise BlunderStorageError("stored game position is not canonical")


def _validate_uci(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} is malformed")
    try:
        move = chess.Move.from_uci(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} is malformed") from error
    if move.uci() != value:
        raise ValueError(f"{field_name} is not canonical")
    return value


def _preferred_move(value: object) -> str:
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError) as error:
        raise ValueError("stored principal variation is malformed") from error
    if not isinstance(parsed, list) or not parsed:
        raise ValueError("stored principal variation is malformed")
    return _validate_uci(parsed[0], "stored preferred move")


__all__ = ["_chunked_ids", "_load_analyses", "_load_occurrences", "_load_scoped_games"]
