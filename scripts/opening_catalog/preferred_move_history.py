"""Direct effective-time history queries for preferred moves."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from .classification_contract import PositionKey
from .preferred_move import (
    MOVE_TABLE,
    REQUIREMENT_TABLE,
    PreferredMoveError,
    _key_values,
    _key_where,
    _normalise_utc,
    _position_key,
    _state_from_events,
    _validate_owner_and_position,
)
from .preferred_move_contract import (
    PreferredMovePeriod,
    PreferredMoveStatePeriod,
    RequirementPeriod,
)
from .preferred_move_schema import ensure_preferred_move_schema


def _event_boundaries(
    connection: sqlite3.Connection,
    table: str,
    player_uuid: str,
    position: PositionKey,
    start_text: str,
    end_text: str,
    recorded_text: str | None,
) -> tuple[datetime, ...]:
    recorded_filter = "" if recorded_text is None else " AND recorded_at <= ?"
    parameters: tuple[object, ...] = (*_key_values(player_uuid, position), start_text, end_text)
    if recorded_text is not None:
        parameters += (recorded_text,)
    rows = connection.execute(
        f"SELECT DISTINCT effective_at FROM {table} WHERE {_key_where()} "
        f"AND effective_at > ? AND effective_at < ?{recorded_filter} ORDER BY effective_at",
        parameters,
    ).fetchall()
    return tuple(_normalise_utc(str(row[0]))[1] for row in rows)


def _period_bounds(
    start: datetime | str, end: datetime | str
) -> tuple[str, str, datetime, datetime]:
    start_text, start_value = _normalise_utc(start)
    end_text, end_value = _normalise_utc(end)
    if end_value <= start_value:
        raise PreferredMoveError("history range end must be after its start")
    return start_text, end_text, start_value, end_value


def requirement_history(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    start: datetime | str,
    end: datetime | str,
    *,
    as_known_at: datetime | str | None = None,
) -> tuple[RequirementPeriod, ...]:
    """Return every active/inactive requirement period in the half-open range."""

    ensure_preferred_move_schema(connection)
    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    start_text, end_text, start_value, end_value = _period_bounds(start, end)
    known_text = None if as_known_at is None else _normalise_utc(as_known_at)[0]
    boundaries = (
        start_value,
        *_event_boundaries(
            connection, REQUIREMENT_TABLE, player_uuid, position, start_text, end_text, known_text
        ),
        end_value,
    )
    periods: list[RequirementPeriod] = []
    for period_start, period_end in zip(boundaries, boundaries[1:]):
        state = _state_from_events(
            connection,
            player_uuid,
            position,
            _normalise_utc(period_start)[0],
            known_text,
        )
        current = RequirementPeriod(period_start, period_end, state.requirement_active)
        if periods and periods[-1].active == current.active:
            periods[-1] = RequirementPeriod(periods[-1].start, period_end, current.active)
        else:
            periods.append(current)
    return tuple(periods)


def preferred_move_history(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    start: datetime | str,
    end: datetime | str,
    *,
    as_known_at: datetime | str | None = None,
) -> tuple[PreferredMovePeriod, ...]:
    """Return every preferred move and no-move period in the half-open range."""

    ensure_preferred_move_schema(connection)
    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    start_text, end_text, start_value, end_value = _period_bounds(start, end)
    known_text = None if as_known_at is None else _normalise_utc(as_known_at)[0]
    boundaries = (
        start_value,
        *_event_boundaries(
            connection, MOVE_TABLE, player_uuid, position, start_text, end_text, known_text
        ),
        end_value,
    )
    periods: list[PreferredMovePeriod] = []
    for period_start, period_end in zip(boundaries, boundaries[1:]):
        state = _state_from_events(
            connection,
            player_uuid,
            position,
            _normalise_utc(period_start)[0],
            known_text,
        )
        current = PreferredMovePeriod(period_start, period_end, state.move_uci, state.move_san)
        if periods and (periods[-1].move_uci, periods[-1].move_san) == (
            current.move_uci,
            current.move_san,
        ):
            periods[-1] = PreferredMovePeriod(
                periods[-1].start, period_end, current.move_uci, current.move_san
            )
        else:
            periods.append(current)
    return tuple(periods)


def state_history(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    start: datetime | str,
    end: datetime | str,
    *,
    as_known_at: datetime | str | None = None,
) -> tuple[PreferredMoveStatePeriod, ...]:
    """Return combined state periods without materializing current state."""

    ensure_preferred_move_schema(connection)
    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    start_text, end_text, start_value, end_value = _period_bounds(start, end)
    known_text = None if as_known_at is None else _normalise_utc(as_known_at)[0]
    boundaries = {start_value, end_value}
    for table in (REQUIREMENT_TABLE, MOVE_TABLE):
        boundaries.update(
            _event_boundaries(
                connection, table, player_uuid, position, start_text, end_text, known_text
            )
        )
    ordered = tuple(sorted(boundaries))
    periods: list[PreferredMoveStatePeriod] = []
    for period_start, period_end in zip(ordered, ordered[1:]):
        state = _state_from_events(
            connection,
            player_uuid,
            position,
            _normalise_utc(period_start)[0],
            known_text,
        )
        current = PreferredMoveStatePeriod(
            period_start,
            period_end,
            state.requirement_active,
            state.move_uci,
            state.move_san,
        )
        if periods and (
            periods[-1].requirement_active,
            periods[-1].move_uci,
            periods[-1].move_san,
        ) == (current.requirement_active, current.move_uci, current.move_san):
            periods[-1] = PreferredMoveStatePeriod(
                periods[-1].start,
                period_end,
                current.requirement_active,
                current.move_uci,
                current.move_san,
            )
        else:
            periods.append(current)
    return tuple(periods)
