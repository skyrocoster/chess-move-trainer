"""Read-only cross-game evidence and scored-position discovery."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..openings.keys import opening_api_key
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .training_requirements_models import (
    TrainerColor,
    TrainingRequirementError,
    TrainingRequirementItem,
    TrainingRequirementPage,
    TrainingRequirementPolicy,
    TrainingRequirementQuery,
    TrainingRequirementSchemaError,
    TrainingRequirementStaleError,
    TrainingRequirementStorageError,
    TrainingRequirementValidationError,
    parse_calendar_date,
    validate_uci,
)
from .training_requirements_scoring import (
    score_training_pair,
    training_adjustment,
)
from .training_requirements_storage import _non_negative_int, _positive_int, _text


@dataclass(frozen=True, slots=True)
class _PreferencePeriod:
    effective_from: date
    effective_until: date | None
    move_uci: str | None


@dataclass(slots=True)
class _EvidenceGroup:
    position_id: int
    trainer_color: TrainerColor
    preferred_move_uci: str
    hits: int = 0
    misses: int = 0
    game_ids: set[int] = field(default_factory=set)


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


class TrainingRequirementRepository:
    """Discover scored position/preferred-move pairs without writing storage."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def discover(
        self,
        query: TrainingRequirementQuery | None = None,
        policy: TrainingRequirementPolicy | None = None,
        **query_values: object,
    ) -> TrainingRequirementPage:
        """Return one deterministic page of globally scored current pairs."""

        if query is None:
            query = TrainingRequirementQuery(**query_values)
        elif query_values:
            raise TrainingRequirementValidationError(
                "query values cannot be combined with a TrainingRequirementQuery"
            )
        if not isinstance(query, TrainingRequirementQuery):
            raise TrainingRequirementValidationError(
                "query must be a TrainingRequirementQuery value"
            )
        if not isinstance(policy, TrainingRequirementPolicy):
            raise TrainingRequirementValidationError("policy must be a TrainingRequirementPolicy")

        try:
            with _open_connection(
                self._database_path,
                "read-only",
                self._lock_timeout,
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                return self._discover_connection(connection, query, policy)
        except SchemaIncompatibleError as error:
            raise TrainingRequirementSchemaError(str(error)) from error
        except TrainingRequirementError:
            raise
        except Exception as error:
            raise TrainingRequirementStorageError(
                "training requirements could not be read"
            ) from error

    def _discover_connection(
        self,
        connection: object,
        query: TrainingRequirementQuery,
        policy: TrainingRequirementPolicy,
    ) -> TrainingRequirementPage:
        preferences = _load_preferences(connection)
        positions: dict[int, _PositionRecord] = {}
        groups: dict[tuple[int, str], _EvidenceGroup] = {}
        for row in _load_occurrences(connection):
            (
                position_id,
                move_uci,
                game_id,
                trainer_color,
                started_at_utc,
                position,
            ) = row
            if position.side_to_move not in ("w", "b"):
                raise TrainingRequirementStorageError("stored position side is malformed")
            expected_color = "white" if position.side_to_move == "w" else "black"
            if trainer_color not in ("white", "black"):
                raise TrainingRequirementStorageError("stored trainer color is malformed")
            if trainer_color != expected_color or move_uci is None:
                continue
            game_date = _usable_game_date(started_at_utc)
            if game_date is None:
                continue
            preferred_move = _active_preference(preferences.get(position_id, ()), game_date)
            if preferred_move is None:
                continue
            validate_uci(move_uci, "stored outgoing move")
            validate_uci(preferred_move, "stored preferred move")
            positions[position_id] = position
            key = (position_id, preferred_move)
            group = groups.get(key)
            if group is None:
                group = _EvidenceGroup(position_id, trainer_color, preferred_move)
                groups[key] = group
            if move_uci == preferred_move:
                group.hits += 1
            else:
                group.misses += 1
            group.game_ids.add(game_id)

        opening_matches = (
            _load_opening_matches(connection) if query.opening_key is not None else {}
        )
        aggregates = _load_training_aggregates(connection)
        as_of = parse_calendar_date(query.as_of, "as_of")
        current_groups = _current_scoped_groups(
            groups,
            preferences,
            as_of,
            query.trainer_color,
            query.opening_key,
            query.opening_match,
            opening_matches,
        )

        scored: list[TrainingRequirementItem] = []
        for group in current_groups:
            aggregate = aggregates.get((group.position_id, group.preferred_move_uci))
            if aggregate is None:
                aggregate = _TrainingAggregate(0.0, None)
            if aggregate.updated_on is not None:
                updated_on = parse_calendar_date(aggregate.updated_on, "training_updated_on")
                if updated_on > as_of:
                    raise TrainingRequirementStaleError(
                        "training state is newer than the requested as_of date"
                    )

            game_value, effective_value, result, required, answers = score_training_pair(
                group.hits,
                group.misses,
                aggregate.balance,
                aggregate.updated_on,
                as_of,
                policy,
            )
            encounters = group.hits + group.misses
            scored.append(
                TrainingRequirementItem(
                    fen=positions[group.position_id].fen,
                    trainer_color=group.trainer_color,
                    preferred_move_uci=group.preferred_move_uci,
                    encounters=encounters,
                    hits=group.hits,
                    misses=group.misses,
                    observed_success_rate=group.hits / encounters,
                    game_balance=game_value,
                    effective_training_balance=effective_value,
                    training_adjustment=training_adjustment(effective_value),
                    training_updated_on=aggregate.updated_on,
                    training_requirement=result,
                    training_required=required,
                    correct_answers_needed=answers,
                )
            )

        scored.sort(key=_item_sort_key)
        filtered = [
            item for item in scored if query.requirement_range.contains(item.training_requirement)
        ]
        start = (query.page - 1) * query.page_size
        return TrainingRequirementPage(
            as_of=query.as_of,
            scoring_policy=policy,
            items=tuple(filtered[start : start + query.page_size]),
            page=query.page,
            page_size=query.page_size,
            total=len(filtered),
        )


def discover_training_requirements(
    database_path: str | Path,
    query: TrainingRequirementQuery | None = None,
    policy: TrainingRequirementPolicy | None = None,
    **query_values: object,
) -> TrainingRequirementPage:
    """Discover scored requirements from one explicit existing database."""

    return TrainingRequirementRepository(database_path).discover(
        query,
        policy,
        **query_values,
    )


read_training_requirements = discover_training_requirements
get_training_requirements = discover_training_requirements


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


def _current_scoped_groups(
    groups: dict[tuple[int, str], _EvidenceGroup],
    preferences: dict[int, tuple[_PreferencePeriod, ...]],
    as_of: date,
    trainer_color: TrainerColor | None,
    opening_key: str | None,
    opening_match: str | None,
    opening_matches: dict[int, dict[str, int]],
) -> list[_EvidenceGroup]:
    selected: list[_EvidenceGroup] = []
    current_by_position: dict[int, _EvidenceGroup] = {}
    for position_id in {position_id for position_id, _move in groups}:
        current_move = _active_preference(preferences.get(position_id, ()), as_of)
        if current_move is None:
            continue
        group = groups.get((position_id, current_move))
        if group is None:
            continue
        current_by_position[position_id] = group

    for group in current_by_position.values():
        if trainer_color is not None and group.trainer_color != trainer_color:
            continue
        if opening_key is not None and not _group_matches_opening(
            group,
            opening_key,
            opening_match,
            opening_matches,
        ):
            continue
        selected.append(group)
    return selected


def _group_matches_opening(
    group: _EvidenceGroup,
    opening_key: str,
    opening_match: str | None,
    opening_matches: dict[int, dict[str, int]],
) -> bool:
    matching_game_ids = {
        game_id for game_id in group.game_ids if opening_key in opening_matches.get(game_id, {})
    }
    if opening_match == "reached":
        return bool(matching_game_ids)
    if opening_match == "deepest":
        for game_id in matching_game_ids:
            matches = opening_matches[game_id]
            deepest_key = min(matches, key=lambda key: (-matches[key], key))
            if deepest_key == opening_key:
                return True
    return False


def _active_preference(periods: tuple[_PreferencePeriod, ...], on_date: date) -> str | None:
    active = [
        period
        for period in periods
        if period.effective_from <= on_date
        and (period.effective_until is None or on_date < period.effective_until)
    ]
    if not active:
        return None
    active.sort(key=lambda period: period.effective_from, reverse=True)
    return active[0].move_uci


def _usable_game_date(value: object) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.date()
    return parsed.astimezone(UTC).date()


def _item_sort_key(item: TrainingRequirementItem) -> tuple[str, str, str, str, str, str]:
    placement, side, castling, en_passant, _halfmove, _fullmove = item.fen.split()
    return (
        placement,
        side,
        castling,
        en_passant,
        item.trainer_color,
        item.preferred_move_uci,
    )
