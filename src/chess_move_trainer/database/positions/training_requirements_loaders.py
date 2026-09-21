"""Database row loaders for training-requirement discovery."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from sqlalchemy import text

from ..openings.keys import opening_api_key
from .training_requirements_models import (
    TrainingRequirementStorageError,
    parse_calendar_date,
    validate_uci,
)
from .training_requirements_storage import _non_negative_int, _positive_int, _text


@dataclass(frozen=True, slots=True)
class _PreferencePeriod:
    effective_from: date
    effective_until: date | None
    move_uci: str | None


@dataclass(frozen=True, slots=True)
class _PositionRecord:
    placement: str
    side_to_move: str
    castling_rights: str
    legal_en_passant: str

    @property
    def fen(self) -> str:
        return " ".join(
            (
                self.placement,
                self.side_to_move,
                self.castling_rights,
                self.legal_en_passant,
                "0",
                "1",
            )
        )


@dataclass(frozen=True, slots=True)
class _TrainingAggregate:
    balance: float
    updated_on: str | None


def _load_occurrences(
    connection: object,
    *,
    position_id: int | None = None,
) -> Iterable[tuple[object, ...]]:
    if position_id is None:
        statement = text(
            """
            SELECT
                o.derived_position_id,
                o.dgp_move_uci,
                o.datasource_game_id,
                g.dg_trainer_color,
                g.dg_started_at_utc,
                p.dp_placement,
                p.dp_side_to_move,
                p.dp_castling_rights,
                p.dp_legal_en_passant
            FROM (
                SELECT DISTINCT derived_position_id
                FROM datasource_preferred_move_period
            ) AS preferred_position
            CROSS JOIN derived_game_position AS o
              ON o.derived_position_id = preferred_position.derived_position_id
            JOIN datasource_game AS g
              ON g.dg_game_id = o.datasource_game_id
            JOIN derived_position AS p
              ON p.dp_position_id = o.derived_position_id
            """
        )
        parameters = None
    else:
        statement = text(
            """
            SELECT
                o.derived_position_id,
                o.dgp_move_uci,
                o.datasource_game_id,
                g.dg_trainer_color,
                g.dg_started_at_utc,
                p.dp_placement,
                p.dp_side_to_move,
                p.dp_castling_rights,
                p.dp_legal_en_passant
            FROM derived_game_position AS o
            JOIN datasource_game AS g
              ON g.dg_game_id = o.datasource_game_id
            JOIN derived_position AS p
              ON p.dp_position_id = o.derived_position_id
            WHERE o.derived_position_id = :position_id
            """
        )
        parameters = {"position_id": position_id}

    rows = connection.execute(statement, parameters).all()
    normalized: list[tuple[object, ...]] = []
    positions: dict[int, _PositionRecord] = {}
    for row in rows:
        occurrence_position_id = _positive_int(row[0], "stored position identifier")
        game_id = _positive_int(row[2], "stored game identifier")
        position = positions.get(occurrence_position_id)
        if position is None:
            position = _PositionRecord(
                _text(row[5], "stored position placement"),
                _text(row[6], "stored position side"),
                _text(row[7], "stored castling rights"),
                _text(row[8], "stored en-passant square"),
            )
            positions[occurrence_position_id] = position
        normalized.append(
            (
                occurrence_position_id,
                row[1],
                game_id,
                row[3],
                row[4],
                position,
            )
        )
    return normalized


def _load_preferences(connection: object) -> dict[int, tuple[_PreferencePeriod, ...]]:
    rows = connection.execute(
        text(
            """
            SELECT derived_position_id, dpm_effective_from,
                   dpm_effective_until, dpm_move_uci
            FROM datasource_preferred_move_period
            ORDER BY derived_position_id, dpm_effective_from
            """
        )
    ).all()
    periods: defaultdict[int, list[_PreferencePeriod]] = defaultdict(list)
    for row in rows:
        position_id = _positive_int(row[0], "stored preference position identifier")
        effective_from = parse_calendar_date(row[1], "stored preference start date")
        effective_until = (
            None if row[2] is None else parse_calendar_date(row[2], "stored preference end date")
        )
        if effective_until is not None and effective_until <= effective_from:
            raise TrainingRequirementStorageError("stored preference period is malformed")
        move_uci = None if row[3] is None else validate_uci(row[3], "stored preferred move")
        periods[position_id].append(_PreferencePeriod(effective_from, effective_until, move_uci))
    return {position_id: tuple(values) for position_id, values in periods.items()}


def _load_opening_matches(connection: object) -> dict[int, dict[str, int]]:
    rows = connection.execute(
        text(
            """
            SELECT g.datasource_game_id, g.dgp_ply, o.do_eco, o.do_name
            FROM derived_game_position AS g
            JOIN derived_opening_route AS r
              ON r.derived_position_id = g.derived_position_id
            JOIN datasource_opening AS o
              ON o.do_opening_id = r.datasource_opening_id
            ORDER BY g.datasource_game_id, g.dgp_ply, o.do_eco, o.do_name
            """
        )
    ).all()
    matches: defaultdict[int, dict[str, int]] = defaultdict(dict)
    for row in rows:
        game_id = _positive_int(row[0], "stored opening game identifier")
        ply = _non_negative_int(row[1], "stored opening ply")
        eco = _text(row[2], "stored opening ECO")
        name = _text(row[3], "stored opening name")
        key = opening_api_key(eco, name)
        previous = matches[game_id].get(key)
        if previous is None or ply > previous:
            matches[game_id][key] = ply
    return dict(matches)


def _load_training_aggregates(
    connection: object,
) -> dict[tuple[int, str], _TrainingAggregate]:
    rows = connection.execute(
        text(
            """
            SELECT derived_position_id, dpta_preferred_move_uci,
                   dpta_training_balance, dpta_updated_on
            FROM derived_position_training_aggregate
            """
        )
    ).all()
    aggregates: dict[tuple[int, str], _TrainingAggregate] = {}
    for row in rows:
        position_id = _positive_int(row[0], "stored aggregate position identifier")
        move_uci = validate_uci(row[1], "stored aggregate preferred move")
        try:
            balance = float(row[2])
        except (TypeError, ValueError, OverflowError) as error:
            raise TrainingRequirementStorageError(
                "stored aggregate training balance is malformed"
            ) from error
        if not math.isfinite(balance):
            raise TrainingRequirementStorageError("stored aggregate training balance is not finite")
        updated_on = row[3]
        if updated_on is not None:
            updated_on = parse_calendar_date(updated_on, "stored aggregate update date").isoformat()
        aggregates[(position_id, move_uci)] = _TrainingAggregate(balance, updated_on)
    return aggregates
