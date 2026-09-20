"""Position insight data readers."""

from __future__ import annotations

from sqlalchemy import text

from .insight_helpers import (
    _read_preference,
    _read_queue_state,
    _read_statistics_count,
    _validate_stored_move,
)
from .insight_models import (
    PositionInsightExperience,
    PositionInsightObservedMove,
    PositionInsightObservedMoveTotals,
    PositionInsightPreference,
    PositionInsightRequest,
    PositionInsightStorageError,
    PositionInsightTerminalTotals,
    _PositionInsightStatistics,
)


def _read_position_data(
    connection: object,
    position_id: int,
    request: PositionInsightRequest,
) -> tuple[
    _PositionInsightStatistics,
    str | None,
    PositionInsightPreference,
]:
    statistics = _read_position_statistics(connection, position_id, request)
    queue_state = _read_queue_state(connection, position_id)
    preference = _read_preference(connection, position_id, request.as_of)
    return statistics, queue_state, preference


def _read_position_statistics(
    connection: object,
    position_id: int | None,
    request: PositionInsightRequest,
) -> _PositionInsightStatistics:
    statistics = connection.execute(
        text(
            """
            WITH corpus_stats AS (
                SELECT
                    COUNT(
                        CASE
                            WHEN g.dg_trainer_color = :trainer_color THEN 1
                        END
                    ) AS total_game_count,
                    COUNT(
                        CASE
                            WHEN g.dg_trainer_color IS NULL
                              OR g.dg_trainer_color NOT IN ('white', 'black')
                            THEN 1
                        END
                    ) AS malformed_game_color_count
                FROM datasource_game AS g
            ),
            position_totals AS (
                SELECT
                    COUNT(*) AS position_occurrence_count,
                    COUNT(
                        DISTINCT CASE
                            WHEN g.dg_trainer_color = :trainer_color
                            THEN o.datasource_game_id
                        END
                    ) AS experience_distinct_game_count,
                    COUNT(
                        CASE WHEN g.dg_trainer_color = :trainer_color THEN 1 END
                    ) AS experience_occurrence_count,
                    COUNT(
                        DISTINCT CASE
                            WHEN g.dg_trainer_color = :trainer_color
                              AND o.dgp_move_uci IS NOT NULL
                            THEN o.datasource_game_id
                        END
                    ) AS outgoing_distinct_game_count,
                    COUNT(
                        CASE
                            WHEN g.dg_trainer_color = :trainer_color
                              AND o.dgp_move_uci IS NOT NULL
                            THEN 1
                        END
                    ) AS outgoing_occurrence_count,
                    COUNT(
                        DISTINCT CASE
                            WHEN g.dg_trainer_color = :trainer_color
                              AND o.dgp_move_uci IS NULL
                            THEN o.datasource_game_id
                        END
                    ) AS terminal_distinct_game_count,
                    COUNT(
                        CASE
                            WHEN g.dg_trainer_color = :trainer_color
                              AND o.dgp_move_uci IS NULL
                            THEN 1
                        END
                    ) AS terminal_occurrence_count
                FROM derived_game_position AS o
                JOIN datasource_game AS g
                  ON g.dg_game_id = o.datasource_game_id
                WHERE o.derived_position_id = :position_id
            )
            SELECT
                c.total_game_count,
                c.malformed_game_color_count,
                t.position_occurrence_count,
                t.experience_distinct_game_count,
                t.experience_occurrence_count,
                t.outgoing_distinct_game_count,
                t.outgoing_occurrence_count,
                t.terminal_distinct_game_count,
                t.terminal_occurrence_count
            FROM corpus_stats AS c
            CROSS JOIN position_totals AS t
            """
        ),
        {"position_id": position_id, "trainer_color": request.trainer_color},
    ).one()
    observed_in_games = bool(_read_statistics_count(statistics[2], "position occurrence count"))
    total_game_count = _read_statistics_count(statistics[0], "total game count")
    malformed_game_color_count = _read_statistics_count(
        statistics[1], "malformed trainer color count"
    )
    if malformed_game_color_count:
        raise PositionInsightStorageError("stored trainer color is malformed")
    experience_distinct_game_count = _read_statistics_count(
        statistics[3], "experience distinct game count"
    )
    experience_occurrence_count = _read_statistics_count(
        statistics[4], "experience occurrence count"
    )
    outgoing_distinct_game_count = _read_statistics_count(
        statistics[5], "outgoing distinct game count"
    )
    outgoing_occurrence_count = _read_statistics_count(statistics[6], "outgoing occurrence count")
    terminal_distinct_game_count = _read_statistics_count(
        statistics[7], "terminal distinct game count"
    )
    terminal_occurrence_count = _read_statistics_count(statistics[8], "terminal occurrence count")
    move_rows = connection.execute(
        text(
            """
            SELECT
                o.dgp_move_uci,
                COUNT(DISTINCT o.datasource_game_id) AS move_distinct_game_count,
                COUNT(*) AS move_occurrence_count
            FROM derived_game_position AS o
            JOIN datasource_game AS g
              ON g.dg_game_id = o.datasource_game_id
            WHERE o.derived_position_id = :position_id
              AND g.dg_trainer_color = :trainer_color
              AND o.dgp_move_uci IS NOT NULL
            GROUP BY o.dgp_move_uci
            """
        ),
        {"position_id": position_id, "trainer_color": request.trainer_color},
    ).all()
    moves: dict[str, tuple[int, int]] = {}
    for row in move_rows:
        try:
            move_uci = row[0]
            move_distinct_game_count = _read_statistics_count(
                row[1], "observed move distinct game count"
            )
            move_occurrence_count = _read_statistics_count(row[2], "observed move occurrence count")
        except IndexError as error:
            raise PositionInsightStorageError("position move statistics are malformed") from error
        _validate_stored_move(move_uci)
        moves[move_uci] = (move_distinct_game_count, move_occurrence_count)

    observed = tuple(
        PositionInsightObservedMove(
            move_uci=move_uci,
            distinct_game_count=move_distinct_game_count,
            occurrence_count=move_occurrence_count,
        )
        for move_uci, (move_distinct_game_count, move_occurrence_count) in sorted(
            moves.items(), key=lambda item: (-item[1][0], item[0])
        )
    )
    return _PositionInsightStatistics(
        observed_in_games=observed_in_games,
        experience=PositionInsightExperience(
            distinct_game_count=experience_distinct_game_count,
            occurrence_count=experience_occurrence_count,
            total_game_count=total_game_count,
        ),
        observed_moves=observed,
        observed_move_totals=PositionInsightObservedMoveTotals(
            distinct_game_count=outgoing_distinct_game_count,
            occurrence_count=outgoing_occurrence_count,
            terminal=PositionInsightTerminalTotals(
                distinct_game_count=terminal_distinct_game_count,
                occurrence_count=terminal_occurrence_count,
            ),
        ),
    )
