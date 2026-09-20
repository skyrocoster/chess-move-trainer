"""Repository for one complete, read-only statistics overview."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .game_aggregates import (
    _GameRow,
    activity_statistics,
    data_quality_statistics,
    game_statistics,
    opening_statistics,
    opponent_statistics,
)
from .models import (
    StatisticsOverview,
    StatisticsOverviewError,
    StatisticsOverviewQuery,
    StatisticsOverviewSchemaError,
    StatisticsOverviewStorageError,
    StatisticsOverviewValidationError,
)
from .scope_readers import (
    read_analysis_statistics,
    read_position_statistics,
    read_repertoire_statistics,
)


class StatisticsOverviewRepository:
    """Compose aggregate reports from an explicit compatible database path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def read(self, query: StatisticsOverviewQuery) -> StatisticsOverview:
        if not isinstance(query, StatisticsOverviewQuery):
            raise StatisticsOverviewValidationError("query must be a StatisticsOverviewQuery value")
        where_sql, params = _game_filter(query)
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                games = _read_games(connection, where_sql, params)
                deepest = _read_deepest_openings(connection, where_sql, params, games)
                positions = read_position_statistics(connection, where_sql, params)
                analysis = read_analysis_statistics(connection, where_sql, params)
                repertoire = read_repertoire_statistics(connection, where_sql, params, query.as_of)
        except SchemaIncompatibleError as error:
            raise StatisticsOverviewSchemaError(str(error)) from error
        except StatisticsOverviewError:
            raise
        except Exception as error:
            raise StatisticsOverviewStorageError("statistics overview could not be read") from error
        return StatisticsOverview(
            query=query,
            games=game_statistics(games),
            activity=activity_statistics(games),
            openings=opening_statistics(games, deepest),
            opponents=opponent_statistics(games),
            positions=positions,
            analysis=analysis,
            repertoire=repertoire,
            data_quality=data_quality_statistics(games),
        )

    get = read


def read_statistics_overview(
    database_path: str | Path,
    query: StatisticsOverviewQuery,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> StatisticsOverview:
    """Read one complete statistics overview from an explicit database path."""

    return StatisticsOverviewRepository(database_path, lock_timeout=lock_timeout).read(query)


def _game_filter(query: StatisticsOverviewQuery) -> tuple[str, dict[str, object]]:
    clauses = ["1 = 1"]
    params: dict[str, object] = {}
    if query.started_on_or_after is not None:
        clauses.append("date(g.dg_started_at_utc) >= :started_on_or_after")
        params["started_on_or_after"] = query.started_on_or_after
    if query.started_on_or_before is not None:
        clauses.append("date(g.dg_started_at_utc) <= :started_on_or_before")
        params["started_on_or_before"] = query.started_on_or_before
    if query.trainer_color is not None:
        clauses.append("g.dg_trainer_color = :trainer_color")
        params["trainer_color"] = query.trainer_color
    if query.time_class is not None:
        clauses.append("g.dg_time_class = :time_class")
        params["time_class"] = query.time_class
    return " AND ".join(clauses), params


def _read_games(
    connection: object, where_sql: str, params: dict[str, object]
) -> tuple[_GameRow, ...]:
    rows = connection.execute(
        text(
            f"""
            SELECT
                g.dg_game_id,
                g.dg_trainer_color,
                g.dg_opponent_chesscom_uuid,
                g.dg_trainer_rating,
                g.dg_opponent_rating,
                g.dg_started_at_utc,
                g.dg_ended_at_utc,
                g.dg_trainer_outcome,
                g.dg_termination_reason,
                g.dg_time_control_source,
                g.dg_time_class,
                COALESCE(MAX(gp.dgp_ply), 0)
            FROM datasource_game AS g
            LEFT JOIN derived_game_position AS gp
              ON gp.datasource_game_id = g.dg_game_id
            WHERE {where_sql}
            GROUP BY g.dg_game_id
            ORDER BY g.dg_game_id
            """
        ),
        params,
    ).all()
    return tuple(_game_row(row) for row in rows)


def _read_deepest_openings(
    connection: object,
    where_sql: str,
    params: dict[str, object],
    games: tuple[_GameRow, ...],
) -> dict[int, tuple[str, str, int]]:
    rows = connection.execute(
        text(
            f"""
            WITH selected_games AS (
                SELECT g.dg_game_id
                FROM datasource_game AS g
                WHERE {where_sql}
            ),
            opening_hits AS (
                SELECT
                    gp.datasource_game_id,
                    o.do_eco,
                    o.do_name,
                    MAX(gp.dgp_ply) AS deepest_ply
                FROM derived_game_position AS gp
                JOIN selected_games AS sg ON sg.dg_game_id = gp.datasource_game_id
                JOIN derived_opening_route AS r
                  ON r.derived_position_id = gp.derived_position_id
                JOIN datasource_opening AS o
                  ON o.do_opening_id = r.datasource_opening_id
                GROUP BY gp.datasource_game_id, o.do_eco, o.do_name
            ),
            ranked AS (
                SELECT
                    datasource_game_id,
                    do_eco,
                    do_name,
                    deepest_ply,
                    ROW_NUMBER() OVER (
                        PARTITION BY datasource_game_id
                        ORDER BY deepest_ply DESC, do_eco || ':' || do_name
                    ) AS opening_rank
                FROM opening_hits
            )
            SELECT datasource_game_id, do_eco, do_name, deepest_ply
            FROM ranked
            WHERE opening_rank = 1
            ORDER BY datasource_game_id
            """
        ),
        params,
    ).all()
    selected_ids = {game.game_id for game in games}
    result: dict[int, tuple[str, str, int]] = {}
    for row in rows:
        game_id = _positive_int(row[0], "opening game id")
        if game_id not in selected_ids or game_id in result:
            raise StatisticsOverviewStorageError("opening classification is malformed")
        eco = _required_text(row[1], "opening ECO")
        name = _required_text(row[2], "opening name")
        ply = _nonnegative_int(row[3], "opening ply")
        result[game_id] = (eco, name, ply)
    return result


def _game_row(row: object) -> _GameRow:
    try:
        game_id = _positive_int(row[0], "game id")
        trainer_color = _required_text(row[1], "trainer color")
        opponent_uuid = _optional_text(row[2], "opponent UUID")
        trainer_rating = _optional_int(row[3], "trainer rating")
        opponent_rating = _optional_int(row[4], "opponent rating")
        started_at = _optional_text(row[5], "started timestamp")
        ended_at = _optional_text(row[6], "ended timestamp")
        outcome = _optional_text(row[7], "trainer outcome")
        termination_reason = _optional_text(row[8], "termination reason")
        time_control = _optional_text(row[9], "time control")
        time_class = _optional_text(row[10], "time class")
        length_plies = _nonnegative_int(row[11], "game length")
    except IndexError as error:
        raise StatisticsOverviewStorageError("game statistics row is malformed") from error
    if trainer_color not in ("white", "black"):
        raise StatisticsOverviewStorageError("trainer color is malformed")
    if outcome not in (None, "win", "loss", "draw"):
        raise StatisticsOverviewStorageError("trainer outcome is malformed")
    return _GameRow(
        game_id=game_id,
        trainer_color=trainer_color,
        opponent_uuid=opponent_uuid,
        trainer_rating=trainer_rating,
        opponent_rating=opponent_rating,
        started_at_utc=started_at,
        ended_at_utc=ended_at,
        outcome=outcome,
        termination_reason=termination_reason,
        time_control=time_control,
        time_class=time_class,
        length_plies=length_plies,
    )


def _positive_int(value: object, name: str) -> int:
    result = _nonnegative_int(value, name)
    if result < 1:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return result


def _nonnegative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return value


def _optional_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    if type(value) is not int:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return value


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return value


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, name)


__all__ = ["StatisticsOverviewRepository", "read_statistics_overview"]
