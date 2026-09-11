"""Read-only aggregate proof helpers for the direct-database boundary."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import chess
from sqlalchemy import text

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from .games.reading import GameReadRepository
from .openings.recognition import lookup_fen, replay_pgn
from .openings.source import OpeningRouteSource, load_opening_sources
from .positions import canonicalize_board
from .schema import _assert_compatible_schema
from .statistics import MoveResponseDistributionReader, PositionContextReader

import time
from pathlib import Path
from typing import Any

import chess
from sqlalchemy import text

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from .games.reading import GameReadRepository
from .openings.recognition import lookup_fen, replay_pgn
from .openings.source import load_opening_sources
from .positions import canonicalize_board
from .schema import _assert_compatible_schema
from .statistics import MoveResponseDistributionReader, PositionContextReader
from .proof_models import (
    DirectMeasurementCorpus,
    DirectMeasurements,
    DirectPreflightError,
    QueryPlanMeasurement,
)
from .proof_opening_helpers import _positive_scalar
from .proof_query import _measure_query
from .proof_statements import (
    _ANALYSIS_LINE_STATEMENT,
    _ANALYSIS_RESULT_STATEMENT,
    _BULK_ELIGIBILITY_STATEMENT,
    _BULK_GAME_PAGE_CURSOR_STATEMENT,
    _BULK_GAME_PAGE_FIRST_STATEMENT,
    _BULK_ROUTE_MOVE_STATEMENT,
    _GAME_READ_STATEMENT,
    _MOVE_RESPONSE_STATEMENT,
    _OPENING_ROUTE_MOVE_STATEMENT,
    _OPENING_ROUTE_STATEMENT,
    _POSITION_CONTEXT_STATEMENT,
    _PREFERRED_POSITION_STATEMENT,
    _PREFERRED_SCHEDULE_STATEMENT,
)

_MEASUREMENT_REPETITIONS = 3
_MEASUREMENT_PAGE_SIZE = 100

@dataclass(frozen=True, slots=True)
class _MeasurementInputs:
    game_id: int
    context_position_id: int
    position_identity: tuple[str, str, str, str]
    analysis_position_id: int
    bulk_cursor: tuple[int, int]



def collect_direct_measurements(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    repetitions: int = _MEASUREMENT_REPETITIONS,
) -> DirectMeasurements:
    """Measure the named clean-package SQL reads without retaining row data.

    The statements below intentionally mirror the SQL in the package-owned
    readers and selectors.  Inputs are selected inside the read-only
    connection and are never returned in the evidence value.
    """

    if type(repetitions) is not int or repetitions < 2:
        raise DirectPreflightError("measurement repetitions must be at least two")
    path = Path(database_path).expanduser().resolve(strict=False)
    measurements: list[QueryPlanMeasurement] = []
    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            corpus = _measurement_corpus(connection)
            inputs = _measurement_inputs(connection)

            measurements.extend(
                _measure_query(
                    connection,
                    "GameReadRepository.read",
                    _GAME_READ_STATEMENT,
                    {"game_id": inputs.game_id},
                    repetitions=repetitions,
                )
            )
            for color, label in (
                (None, "all"),
                ("white", "white"),
                ("black", "black"),
            ):
                parameters = {
                    "position_id": inputs.context_position_id,
                    "trainer_color": color,
                }
                measurements.extend(
                    _measure_query(
                        connection,
                        f"PositionContextReader.read/{label}",
                        _POSITION_CONTEXT_STATEMENT,
                        parameters,
                        repetitions=repetitions,
                    )
                )
                measurements.extend(
                    _measure_query(
                        connection,
                        f"MoveResponseDistributionReader.read/{label}",
                        _MOVE_RESPONSE_STATEMENT,
                        parameters,
                        repetitions=repetitions,
                    )
                )

            measurements.extend(
                _measure_query(
                    connection,
                    "openings.recognition/routes",
                    _OPENING_ROUTE_STATEMENT,
                    {},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "openings.recognition/route-moves",
                    _OPENING_ROUTE_MOVE_STATEMENT,
                    {},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "PreferredMoveRepository/find-position",
                    _PREFERRED_POSITION_STATEMENT,
                    {
                        "placement": inputs.position_identity[0],
                        "side_to_move": inputs.position_identity[1],
                        "castling_rights": inputs.position_identity[2],
                        "legal_en_passant": inputs.position_identity[3],
                    },
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "PreferredMoveRepository/load-schedule",
                    _PREFERRED_SCHEDULE_STATEMENT,
                    {"position_id": inputs.context_position_id},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "AnalysisReadRepository/read-result",
                    _ANALYSIS_RESULT_STATEMENT,
                    {"position_id": inputs.analysis_position_id},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "AnalysisReadRepository/read-lines",
                    _ANALYSIS_LINE_STATEMENT,
                    {"position_id": inputs.analysis_position_id},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/load-route-moves",
                    _BULK_ROUTE_MOVE_STATEMENT,
                    {},
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/load-game-page/first",
                    _BULK_GAME_PAGE_FIRST_STATEMENT,
                    _bulk_page_parameters(),
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/load-game-page/cursor",
                    _BULK_GAME_PAGE_CURSOR_STATEMENT,
                    {
                        **_bulk_page_parameters(),
                        "last_frequency": inputs.bulk_cursor[0],
                        "last_position_id": inputs.bulk_cursor[1],
                    },
                    repetitions=repetitions,
                )
            )
            measurements.extend(
                _measure_query(
                    connection,
                    "BulkTargetSelector/check-eligibility",
                    _BULK_ELIGIBILITY_STATEMENT,
                    {"position_id": inputs.analysis_position_id},
                    repetitions=repetitions,
                )
            )
    except DirectPreflightError:
        raise
    except Exception as error:
        raise DirectPreflightError(
            "real direct query-plan measurements could not be collected"
        ) from error

    decision, index_table, index_columns, reason = _measurement_decision(measurements)
    return DirectMeasurements(
        database_path=path,
        corpus=corpus,
        measurements=tuple(measurements),
        index_decision=decision,
        index_table=index_table,
        index_columns=index_columns,
        decision_reason=reason,
    )


def print_direct_measurements(report: DirectMeasurements) -> None:
    """Print only aggregate measurement facts and normalized plan details."""

    corpus = report.corpus
    print(
        "direct measurement corpus: "
        f"databases={corpus.database_count}; games={corpus.game_count}; "
        f"positions={corpus.position_count}; occurrences={corpus.occurrence_count}; "
        f"analysis_results={corpus.analysis_result_count}; "
        f"analysis_lines={corpus.analysis_line_count}"
    )
    for measurement in report.measurements:
        elapsed_ms = tuple(value * 1000 for value in measurement.elapsed_seconds)
        print(
            f"direct measurement: operation={measurement.name}; "
            f"plan={' | '.join(measurement.plan)}; "
            f"result_rows={measurement.result_row_count}; "
            f"repetitions={measurement.repetitions}; "
            f"elapsed_ms_min={min(elapsed_ms):.3f}; "
            f"elapsed_ms_median={_median(elapsed_ms):.3f}; "
            f"elapsed_ms_max={max(elapsed_ms):.3f}"
        )
    index_description = (
        "none"
        if report.index_table is None
        else f"{report.index_table}({','.join(report.index_columns)})"
    )
    print(
        f"direct index decision: decision={report.index_decision}; "
        f"recommended_index={index_description}; reason={report.decision_reason}"
    )


def _measurement_corpus(connection: Any) -> DirectMeasurementCorpus:
    def count(table_name: str) -> int:
        return int(
            connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            .scalar_one()
        )

    return DirectMeasurementCorpus(
        database_count=1,
        game_count=count("datasource_game"),
        position_count=count("derived_position"),
        occurrence_count=count("derived_game_position"),
        analysis_result_count=count("derived_analysis_result"),
        analysis_line_count=count("derived_analysis_line"),
    )


def _measurement_inputs(connection: Any) -> _MeasurementInputs:
    game_id = _positive_scalar(
        connection.execute(
            text(
                """
                SELECT g.dg_game_id
                FROM datasource_game AS g
                JOIN derived_game_position AS o
                  ON o.datasource_game_id = g.dg_game_id
                GROUP BY g.dg_game_id
                ORDER BY g.dg_game_id
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
    )
    context_position_id = _positive_scalar(
        connection.execute(
            text(
                """
                SELECT o.derived_position_id
                FROM derived_game_position AS o
                JOIN datasource_game AS g
                  ON g.dg_game_id = o.datasource_game_id
                GROUP BY o.derived_position_id
                HAVING COUNT(DISTINCT CASE
                           WHEN g.dg_trainer_color = 'white'
                           THEN g.dg_game_id END) > 0
                   AND COUNT(DISTINCT CASE
                           WHEN g.dg_trainer_color = 'black'
                           THEN g.dg_game_id END) > 0
                ORDER BY o.derived_position_id
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
    )
    position_row = connection.execute(
        text(
            """
            SELECT dp_placement, dp_side_to_move,
                   dp_castling_rights, dp_legal_en_passant
            FROM derived_position
            ORDER BY dp_position_id
            LIMIT 1
            """
        )
    ).first()
    if position_row is None or any(not isinstance(value, str) for value in position_row):
        raise DirectPreflightError("fixed direct database lacks a position identity")
    analysis_position_id = _positive_scalar(
        connection.execute(
            text(
                """
                SELECT derived_position_id
                FROM derived_analysis_result
                ORDER BY derived_position_id
                LIMIT 1
                """
            )
        ).scalar_one_or_none()
    )
    first_page = connection.execute(
        text(_BULK_GAME_PAGE_FIRST_STATEMENT),
        _bulk_page_parameters(),
    ).all()
    if not first_page:
        raise DirectPreflightError("fixed direct database lacks a bulk target page")
    try:
        bulk_cursor = (int(first_page[-1][1]), int(first_page[-1][0]))
    except (IndexError, TypeError, ValueError) as error:
        raise DirectPreflightError("real direct bulk target page is malformed") from error
    return _MeasurementInputs(
        game_id=game_id,
        context_position_id=context_position_id,
        position_identity=tuple(str(value) for value in position_row),
        analysis_position_id=analysis_position_id,
        bulk_cursor=bulk_cursor,
    )


def _bulk_page_parameters() -> dict[str, int]:
    return {"min_ply": 0, "max_ply": 19, "page_size": _MEASUREMENT_PAGE_SIZE}


def _measurement_decision(
    measurements: list[QueryPlanMeasurement],
) -> tuple[MeasurementDecision, str | None, tuple[str, ...], str]:
    position_reads = tuple(
        measurement
        for measurement in measurements
        if measurement.name.startswith(
            ("PositionContextReader.read/", "MoveResponseDistributionReader.read/")
        )
    )
    if any(_plan_scans_alias(measurement, "o") for measurement in position_reads):
        return (
            "INDEX-JUSTIFIED",
            "derived_game_position",
            ("derived_position_id", "datasource_game_id", "dgp_ply"),
            "PositionContextReader and MoveResponseDistributionReader each "
            "repeatably scan derived_game_position for one position lookup; "
            "one composite supporting index covers both direct paths. No timing "
            "threshold was used. Catalogue loads and the bounded first-20-ply "
            "bulk aggregate remain structurally appropriate scans.",
        )
    return (
        "NO-INDEX",
        None,
        (),
        "PK, UNIQUE, and existing supporting indexes serve the measured direct "
        "lookups; remaining scans load complete catalogues or bounded aggregates "
        "and are structurally appropriate. No timing threshold was used.",
    )


def _plan_scans_alias(measurement: QueryPlanMeasurement, alias: str) -> bool:
    prefix = f"SCAN {alias.upper()}"
    return any(detail.upper().startswith(prefix) for detail in measurement.plan)


def _median(values: tuple[float, ...]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


