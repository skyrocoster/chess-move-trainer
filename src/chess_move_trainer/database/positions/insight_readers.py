"""Position insight data readers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

import chess
from sqlalchemy import text

from ..analysis.models import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisScoreKind,
    AnalysisTerminalKind,
)
from ..analysis.reading import AnalysisReadError, AnalysisReadRepository
from ..analysis.validation import validate_settings_object
from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..openings.keys import opening_api_key
from ..openings.recognition import (
    OpeningInputError,
    OpeningRecognitionError,
    lookup_fen,
)
from ..preferred_moves.ranges import (
    NormalizedPeriod,
    Preference,
    RangeValidationError,
    ResolutionState,
    normalize_periods,
    period_from_literals,
    resolve_date,
)
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .canonicalization import CanonicalPosition, PositionValidationError, canonicalize_fen
from .repository import _find_existing_position_id


TrainerColor = Literal["white", "black"]
AnalysisState = Literal["not_requested", "queued", "running", "ready"]
PreferenceKind = Literal["move", "no_preference", "unconfigured"]


from .insight_models import AnalysisState, PositionInsight, PositionInsightAnalysis, PositionInsightError, PositionInsightExperience, PositionInsightObservedMove, PositionInsightObservedMoveTotals, PositionInsightOpening, PositionInsightPreference, PositionInsightRequest, PositionInsightResult, PositionInsightSchemaError, PositionInsightStorageError, PositionInsightTerminalTotals, PositionInsightValidationError, PreferenceKind, TrainerColor, _PositionInsightStatistics, _canonical_fen
from .insight_helpers import _read_analysis_result, _read_opening, _read_preference, _read_queue_state, _read_statistics_count, _read_statistics_flag, _validate_stored_move


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
    rows = connection.execute(
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
                    ) AS malformed_game_color_count,
                    CASE
                        WHEN EXISTS (
                            SELECT 1
                            FROM derived_game_position AS observed
                            JOIN datasource_game AS observed_game
                              ON observed_game.dg_game_id = observed.datasource_game_id
                            WHERE observed.derived_position_id = :position_id
                        ) THEN 1
                        ELSE 0
                    END AS observed_in_games
                FROM datasource_game AS g
            ),
            position_rows AS (
                SELECT
                    1 AS row_marker,
                    o.datasource_game_id AS game_id,
                    o.dgp_ply AS ply,
                    o.dgp_move_uci AS move_uci,
                    g.dg_trainer_color AS trainer_color
                FROM derived_game_position AS o
                JOIN datasource_game AS g
                  ON g.dg_game_id = o.datasource_game_id
                WHERE o.derived_position_id = :position_id
            ),
            position_totals AS (
                SELECT
                    COUNT(
                        DISTINCT CASE
                            WHEN trainer_color = :trainer_color THEN game_id
                        END
                    ) AS experience_distinct_game_count,
                    COUNT(
                        CASE
                            WHEN trainer_color = :trainer_color THEN 1
                        END
                    ) AS experience_occurrence_count,
                    COUNT(
                        DISTINCT CASE
                            WHEN trainer_color = :trainer_color
                              AND move_uci IS NOT NULL
                            THEN game_id
                        END
                    ) AS outgoing_distinct_game_count,
                    COUNT(
                        CASE
                            WHEN trainer_color = :trainer_color
                              AND move_uci IS NOT NULL
                            THEN 1
                        END
                    ) AS outgoing_occurrence_count,
                    COUNT(
                        DISTINCT CASE
                            WHEN trainer_color = :trainer_color
                              AND move_uci IS NULL
                            THEN game_id
                        END
                    ) AS terminal_distinct_game_count,
                    COUNT(
                        CASE
                            WHEN trainer_color = :trainer_color
                              AND move_uci IS NULL
                            THEN 1
                        END
                    ) AS terminal_occurrence_count
                FROM position_rows
            ),
            move_totals AS (
                SELECT
                    move_uci,
                    COUNT(DISTINCT game_id) AS move_distinct_game_count,
                    COUNT(*) AS move_occurrence_count
                FROM position_rows
                WHERE trainer_color = :trainer_color
                  AND move_uci IS NOT NULL
                GROUP BY move_uci
            )
            SELECT
                c.observed_in_games,
                c.total_game_count,
                c.malformed_game_color_count,
                t.experience_distinct_game_count,
                t.experience_occurrence_count,
                t.outgoing_distinct_game_count,
                t.outgoing_occurrence_count,
                t.terminal_distinct_game_count,
                t.terminal_occurrence_count,
                r.row_marker,
                r.game_id,
                r.ply,
                r.move_uci,
                r.trainer_color,
                m.move_distinct_game_count,
                m.move_occurrence_count
            FROM corpus_stats AS c
            CROSS JOIN position_totals AS t
            LEFT JOIN position_rows AS r ON 1 = 1
            LEFT JOIN move_totals AS m
              ON m.move_uci = r.move_uci
             AND r.trainer_color = :trainer_color
            ORDER BY r.game_id, r.ply
            """
        ),
        {"position_id": position_id, "trainer_color": request.trainer_color},
    ).all()

    if not rows:
        raise PositionInsightStorageError("position statistics are malformed")

    first = rows[0]
    observed_in_games = _read_statistics_flag(first[0])
    total_game_count = _read_statistics_count(first[1], "total game count")
    malformed_game_color_count = _read_statistics_count(
        first[2], "malformed trainer color count"
    )
    if malformed_game_color_count:
        raise PositionInsightStorageError("stored trainer color is malformed")
    experience_distinct_game_count = _read_statistics_count(
        first[3], "experience distinct game count"
    )
    experience_occurrence_count = _read_statistics_count(
        first[4], "experience occurrence count"
    )
    outgoing_distinct_game_count = _read_statistics_count(
        first[5], "outgoing distinct game count"
    )
    outgoing_occurrence_count = _read_statistics_count(
        first[6], "outgoing occurrence count"
    )
    terminal_distinct_game_count = _read_statistics_count(
        first[7], "terminal distinct game count"
    )
    terminal_occurrence_count = _read_statistics_count(
        first[8], "terminal occurrence count"
    )
    moves: dict[str, tuple[int, int]] = {}
    for row in rows:
        if row[0] != (1 if observed_in_games else 0):
            raise PositionInsightStorageError("position observation statistics are malformed")
        if any(row[index] != first[index] for index in range(1, 9)):
            raise PositionInsightStorageError("position statistics are inconsistent")
        if row[9] is None:
            if any(row[index] is not None for index in range(10, 16)):
                raise PositionInsightStorageError("position row statistics are malformed")
            continue
        game_id = row[10]
        move_uci = row[12]
        color = row[13]
        if type(game_id) is not int or game_id < 1:
            raise PositionInsightStorageError("stored game identifier is malformed")
        if color not in ("white", "black"):
            raise PositionInsightStorageError("stored trainer color is malformed")
        if move_uci is not None:
            _validate_stored_move(move_uci)
        if color != request.trainer_color:
            continue
        if move_uci is not None:
            move_distinct_game_count = _read_statistics_count(
                row[14], "observed move distinct game count"
            )
            move_occurrence_count = _read_statistics_count(
                row[15], "observed move occurrence count"
            )
            existing = moves.setdefault(
                move_uci, (move_distinct_game_count, move_occurrence_count)
            )
            if existing != (move_distinct_game_count, move_occurrence_count):
                raise PositionInsightStorageError("observed move statistics are inconsistent")

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


