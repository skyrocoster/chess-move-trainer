"""SQL readers for position, analysis, and repertoire reporting scopes."""

from __future__ import annotations

from statistics import median

from sqlalchemy import text

from .models import (
    AnalysisStatistics,
    NumericSummary,
    PlyBucket,
    PositionStatistics,
    RecurringPosition,
    RepertoireStatistics,
    StatisticsOverviewStorageError,
    TrainingBalanceStatistics,
)

_BUCKETS = (
    ("0-19", 0, 19),
    ("20-39", 20, 39),
    ("40-59", 40, 59),
    ("60+", 60, None),
)


def read_position_statistics(
    connection: object, where_sql: str, params: dict[str, object]
) -> PositionStatistics:
    aggregate = connection.execute(
        text(
            f"""
            WITH selected_occurrences AS (
                SELECT
                    gp.datasource_game_id,
                    gp.dgp_ply,
                    gp.derived_position_id,
                    gp.dgp_move_uci,
                    p.dp_side_to_move,
                    g.dg_trainer_color
                FROM derived_game_position AS gp
                JOIN datasource_game AS g ON g.dg_game_id = gp.datasource_game_id
                JOIN derived_position AS p ON p.dp_position_id = gp.derived_position_id
                WHERE {where_sql}
            ),
            per_position AS (
                SELECT derived_position_id, COUNT(*) AS occurrence_count
                FROM selected_occurrences
                GROUP BY derived_position_id
            )
            SELECT
                (SELECT COUNT(*) FROM derived_position),
                COUNT(DISTINCT so.derived_position_id),
                COUNT(DISTINCT so.datasource_game_id),
                COUNT(*),
                COUNT(CASE WHEN so.dgp_move_uci IS NOT NULL THEN 1 END),
                COUNT(CASE WHEN so.dgp_move_uci IS NULL THEN 1 END),
                COUNT(
                    CASE WHEN
                        (so.dp_side_to_move = 'w' AND so.dg_trainer_color = 'white')
                        OR (so.dp_side_to_move = 'b' AND so.dg_trainer_color = 'black')
                    THEN 1 END
                ),
                COUNT(
                    CASE WHEN NOT (
                        (so.dp_side_to_move = 'w' AND so.dg_trainer_color = 'white')
                        OR (so.dp_side_to_move = 'b' AND so.dg_trainer_color = 'black')
                    ) THEN 1 END
                ),
                COUNT(DISTINCT so.dgp_move_uci),
                (SELECT COUNT(*) FROM per_position WHERE occurrence_count > 1)
            FROM selected_occurrences AS so
            """
        ),
        params,
    ).one()
    values = tuple(_count(aggregate[index], "position aggregate") for index in range(10))
    observed_position_count = values[1]

    bucket_rows = connection.execute(
        text(
            f"""
            SELECT
                CASE
                    WHEN gp.dgp_ply < 20 THEN '0-19'
                    WHEN gp.dgp_ply < 40 THEN '20-39'
                    WHEN gp.dgp_ply < 60 THEN '40-59'
                    ELSE '60+'
                END AS bucket,
                COUNT(*),
                COUNT(DISTINCT gp.datasource_game_id),
                COUNT(DISTINCT gp.derived_position_id)
            FROM derived_game_position AS gp
            JOIN datasource_game AS g ON g.dg_game_id = gp.datasource_game_id
            WHERE {where_sql}
            GROUP BY bucket
            """
        ),
        params,
    ).all()
    bucket_values: dict[str, tuple[int, int, int]] = {}
    for row in bucket_rows:
        label = _text(row[0], "ply bucket")
        bucket_values[label] = (
            _count(row[1], "ply bucket occurrence count"),
            _count(row[2], "ply bucket game count"),
            _count(row[3], "ply bucket position count"),
        )

    recurring_rows = connection.execute(
        text(
            f"""
            SELECT
                p.dp_placement,
                p.dp_side_to_move,
                p.dp_castling_rights,
                p.dp_legal_en_passant,
                COUNT(DISTINCT gp.datasource_game_id),
                COUNT(*),
                COUNT(CASE WHEN gp.dgp_move_uci IS NOT NULL THEN 1 END),
                COUNT(CASE WHEN gp.dgp_move_uci IS NULL THEN 1 END)
            FROM derived_game_position AS gp
            JOIN datasource_game AS g ON g.dg_game_id = gp.datasource_game_id
            JOIN derived_position AS p ON p.dp_position_id = gp.derived_position_id
            WHERE {where_sql}
            GROUP BY gp.derived_position_id
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC, COUNT(DISTINCT gp.datasource_game_id) DESC,
                     gp.derived_position_id
            LIMIT 20
            """
        ),
        params,
    ).all()
    recurring = tuple(
        RecurringPosition(
            fen=" ".join(
                (
                    _text(row[0], "position placement"),
                    _text(row[1], "position side"),
                    _text(row[2], "position castling"),
                    _text(row[3], "position en passant"),
                    "0",
                    "1",
                )
            ),
            distinct_game_count=_count(row[4], "recurring position game count"),
            occurrence_count=_count(row[5], "recurring position occurrence count"),
            outgoing_occurrence_count=_count(row[6], "recurring position outgoing count"),
            terminal_occurrence_count=_count(row[7], "recurring position terminal count"),
        )
        for row in recurring_rows
    )
    return PositionStatistics(
        database_position_count=values[0],
        observed_position_count=observed_position_count,
        distinct_game_count=values[2],
        occurrence_count=values[3],
        outgoing_occurrence_count=values[4],
        terminal_occurrence_count=values[5],
        trainer_turn_occurrence_count=values[6],
        opponent_turn_occurrence_count=values[7],
        distinct_outgoing_move_count=values[8],
        repeated_position_count=values[9],
        average_occurrences_per_observed_position=(
            None if not observed_position_count else _rounded(values[3] / observed_position_count)
        ),
        ply_buckets=tuple(
            PlyBucket(
                label=label,
                minimum_ply=minimum,
                maximum_ply=maximum,
                occurrence_count=bucket_values.get(label, (0, 0, 0))[0],
                distinct_game_count=bucket_values.get(label, (0, 0, 0))[1],
                distinct_position_count=bucket_values.get(label, (0, 0, 0))[2],
            )
            for label, minimum, maximum in _BUCKETS
        ),
        recurring_positions=recurring,
    )


def read_analysis_statistics(
    connection: object, where_sql: str, params: dict[str, object]
) -> AnalysisStatistics:
    row = connection.execute(
        text(
            f"""
            WITH scoped_positions AS (
                SELECT DISTINCT gp.derived_position_id
                FROM derived_game_position AS gp
                JOIN datasource_game AS g ON g.dg_game_id = gp.datasource_game_id
                WHERE {where_sql}
            ),
            line_totals AS (
                SELECT
                    derived_analysis_result_id,
                    COUNT(*) AS line_count,
                    SUM(dal_depth) AS depth_total,
                    COUNT(CASE WHEN dal_score_kind = 'cp' THEN 1 END) AS cp_line_count,
                    COUNT(CASE WHEN dal_score_kind = 'mate' THEN 1 END) AS mate_line_count
                FROM derived_analysis_line
                GROUP BY derived_analysis_result_id
            )
            SELECT
                COUNT(*),
                COUNT(ar.derived_position_id),
                COUNT(CASE WHEN ar.dar_quality = 'browser' THEN 1 END),
                COUNT(CASE WHEN ar.dar_quality = 'tool' THEN 1 END),
                COUNT(CASE WHEN ar.dar_terminal_kind IS NOT NULL THEN 1 END),
                COUNT(CASE WHEN aq.daq_state = 'queued' THEN 1 END),
                COUNT(CASE WHEN aq.daq_state = 'running' THEN 1 END),
                COUNT(
                    CASE WHEN ar.derived_position_id IS NULL
                              AND aq.derived_position_id IS NULL THEN 1 END
                ),
                COALESCE(SUM(lt.line_count), 0),
                COALESCE(SUM(lt.cp_line_count), 0),
                COALESCE(SUM(lt.mate_line_count), 0),
                COUNT(CASE WHEN lt.line_count > 1 THEN 1 END),
                COALESCE(SUM(lt.depth_total), 0)
            FROM scoped_positions AS sp
            LEFT JOIN derived_analysis_result AS ar
              ON ar.derived_position_id = sp.derived_position_id
            LEFT JOIN derived_analysis_queue AS aq
              ON aq.derived_position_id = sp.derived_position_id
            LEFT JOIN line_totals AS lt
              ON lt.derived_analysis_result_id = sp.derived_position_id
            """
        ),
        params,
    ).one()
    values = tuple(_count(row[index], "analysis aggregate") for index in range(13))
    return AnalysisStatistics(
        scoped_position_count=values[0],
        ready_position_count=values[1],
        browser_quality_count=values[2],
        tool_quality_count=values[3],
        terminal_result_count=values[4],
        queued_position_count=values[5],
        running_position_count=values[6],
        not_requested_position_count=values[7],
        line_count=values[8],
        centipawn_line_count=values[9],
        mate_line_count=values[10],
        multi_pv_result_count=values[11],
        average_depth=None if not values[8] else _rounded(values[12] / values[8]),
        ready_coverage_rate=None if not values[0] else _rounded(values[1] / values[0]),
    )


def read_repertoire_statistics(
    connection: object,
    where_sql: str,
    params: dict[str, object],
    as_of: str,
) -> RepertoireStatistics:
    repertoire_params = {**params, "as_of": as_of}
    rows = connection.execute(
        text(
            f"""
            WITH trainer_occurrences AS (
                SELECT
                    gp.derived_position_id,
                    gp.dgp_move_uci
                FROM derived_game_position AS gp
                JOIN datasource_game AS g ON g.dg_game_id = gp.datasource_game_id
                JOIN derived_position AS p ON p.dp_position_id = gp.derived_position_id
                WHERE {where_sql}
                  AND (
                      (p.dp_side_to_move = 'w' AND g.dg_trainer_color = 'white')
                      OR (p.dp_side_to_move = 'b' AND g.dg_trainer_color = 'black')
                  )
            ),
            scoped_positions AS (
                SELECT DISTINCT derived_position_id FROM trainer_occurrences
            ),
            active_preferences AS (
                SELECT
                    derived_position_id,
                    dpm_move_uci,
                    COUNT(*) OVER (PARTITION BY derived_position_id) AS active_period_count
                FROM datasource_preferred_move_period
                WHERE dpm_effective_from <= :as_of
                  AND (dpm_effective_until IS NULL OR :as_of < dpm_effective_until)
            )
            SELECT
                sp.derived_position_id,
                ap.derived_position_id,
                ap.dpm_move_uci,
                ap.active_period_count,
                COUNT(CASE WHEN t.dgp_move_uci IS NOT NULL THEN 1 END),
                COUNT(
                    CASE WHEN t.dgp_move_uci IS NOT NULL
                              AND t.dgp_move_uci = ap.dpm_move_uci THEN 1 END
                ),
                ta.dpta_training_balance,
                ta.dpta_updated_on
            FROM scoped_positions AS sp
            LEFT JOIN trainer_occurrences AS t
              ON t.derived_position_id = sp.derived_position_id
            LEFT JOIN active_preferences AS ap
              ON ap.derived_position_id = sp.derived_position_id
            LEFT JOIN derived_position_training_aggregate AS ta
              ON ta.derived_position_id = sp.derived_position_id
             AND ta.dpta_preferred_move_uci = ap.dpm_move_uci
            GROUP BY
                sp.derived_position_id,
                ap.derived_position_id,
                ap.dpm_move_uci,
                ap.active_period_count,
                ta.dpta_training_balance,
                ta.dpta_updated_on
            ORDER BY sp.derived_position_id
            """
        ),
        repertoire_params,
    ).all()
    seen: set[int] = set()
    move_preferences = no_preferences = unconfigured = observed_preferences = 0
    opportunities = played = 0
    balances: list[float] = []
    updated_count = 0
    for row in rows:
        position_id = _positive_int(row[0], "repertoire position id")
        if position_id in seen:
            raise StatisticsOverviewStorageError("preferred-move schedules overlap")
        seen.add(position_id)
        configured_id = row[1]
        move = row[2]
        if configured_id is not None and _count(row[3], "active preference count") != 1:
            raise StatisticsOverviewStorageError("preferred-move schedules overlap")
        opportunity_count = _count(row[4], "preferred-move opportunity count")
        played_count = _count(row[5], "preferred-move played count")
        if configured_id is None:
            unconfigured += 1
        elif move is None:
            no_preferences += 1
        else:
            if not isinstance(move, str) or not move:
                raise StatisticsOverviewStorageError("preferred move is malformed")
            move_preferences += 1
            opportunities += opportunity_count
            played += played_count
            observed_preferences += int(played_count > 0)
            if row[6] is not None:
                if type(row[6]) not in (int, float):
                    raise StatisticsOverviewStorageError("training balance is malformed")
                balances.append(float(row[6]))
                updated_count += int(row[7] is not None)
    trainer_positions = len(seen)
    return RepertoireStatistics(
        trainer_turn_position_count=trainer_positions,
        move_preference_position_count=move_preferences,
        no_preference_position_count=no_preferences,
        unconfigured_position_count=unconfigured,
        preference_coverage_rate=(
            None if not trainer_positions else _rounded(move_preferences / trainer_positions)
        ),
        preference_observed_position_count=observed_preferences,
        preferred_move_opportunity_count=opportunities,
        preferred_move_played_count=played,
        preferred_move_adherence_rate=(
            None if not opportunities else _rounded(played / opportunities)
        ),
        training_balances=TrainingBalanceStatistics(
            count=len(balances),
            negative_count=sum(value < 0 for value in balances),
            zero_count=sum(value == 0 for value in balances),
            positive_count=sum(value > 0 for value in balances),
            updated_count=updated_count,
            missing_count=move_preferences - len(balances),
            summary=_numeric_summary(balances),
        ),
    )


def _numeric_summary(values: list[float]) -> NumericSummary:
    if not values:
        return NumericSummary(0, None, None, None, None)
    return NumericSummary(
        count=len(values),
        minimum=_number(min(values)),
        maximum=_number(max(values)),
        average=_rounded(sum(values) / len(values)),
        median=_number(float(median(values))),
    )


def _count(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return value


def _positive_int(value: object, name: str) -> int:
    result = _count(value, name)
    if result < 1:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return result


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise StatisticsOverviewStorageError(f"{name} is malformed")
    return value


def _rounded(value: float) -> float:
    return round(value, 6)


def _number(value: float) -> int | float:
    return int(value) if value.is_integer() else _rounded(value)


__all__ = [
    "read_analysis_statistics",
    "read_position_statistics",
    "read_repertoire_statistics",
]
