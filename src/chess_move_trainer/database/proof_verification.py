"""Aggregate verification and direct proof collection."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from sqlalchemy import text

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from .schema import _assert_compatible_schema
from .proof_models import (
    DIRECT_TABLE_NAMES,
    DirectPreflightError,
    DirectProof,
    DirectVerification,
    QueryPlanMeasurement,
)
from .proof_query import _measure_query


def _verify_direct_database(path: Path, *, lock_timeout: float) -> DirectVerification:
    """Read aggregate verification facts from one already-created database."""

    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            user_version = int(
                connection.execute(text("PRAGMA user_version")).scalar_one()
            )
            try:
                _assert_compatible_schema(connection, lock_timeout)
            except Exception:
                return DirectVerification(
                    database_path=path,
                    schema_compatible=False,
                    user_version=user_version,
                    integrity_result="unknown",
                    foreign_key_errors=(),
                    opening_count=0,
                    opening_route_count=0,
                    opening_move_count=0,
                    position_count=0,
                    game_count=0,
                    game_position_count=0,
                )

            integrity_result = str(
                connection.execute(text("PRAGMA integrity_check")).scalar_one()
            )
            foreign_key_errors = tuple(
                " ".join(str(value) for value in row)
                for row in connection.execute(text("PRAGMA foreign_key_check")).all()
            )
            counts = {
                name: int(
                    connection.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar_one()
                )
                for name in DIRECT_TABLE_NAMES
            }
            return DirectVerification(
                database_path=path,
                schema_compatible=True,
                user_version=user_version,
                integrity_result=integrity_result,
                foreign_key_errors=foreign_key_errors,
                opening_count=counts["datasource_opening"],
                opening_route_count=counts["derived_opening_route"],
                opening_move_count=counts["derived_opening_route_move"],
                position_count=counts["derived_position"],
                game_count=counts["datasource_game"],
                game_position_count=counts["derived_game_position"],
            )
    except DirectPreflightError:
        raise
    except Exception as error:
        raise DirectPreflightError("fixed direct database could not be verified") from error


def collect_direct_proof(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    explain_position_id: int | None = None,
) -> DirectProof:
    """Collect aggregate integrity, emptiness, query-plan, and timing facts only."""

    path = Path(database_path).expanduser().resolve(strict=False)
    verification = _verify_direct_database(path, lock_timeout=lock_timeout)
    measurements: list[QueryPlanMeasurement] = []
    try:
        with _open_connection(path, "read-only", lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            table_names = tuple(
                str(row[0])
                for row in connection.execute(
                    text(
                        """
                        SELECT name
                        FROM sqlite_master
                        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                        ORDER BY name
                        """
                    )
                ).all()
            )
            counts = tuple(
                (name, int(connection.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar_one()))
                for name in DIRECT_TABLE_NAMES
            )
            preference_count = dict(counts)["datasource_preferred_move_period"]
            analysis_result_count = dict(counts)["derived_analysis_result"]
            analysis_line_count = dict(counts)["derived_analysis_line"]
            game_occurrence_invariant_violations = int(
                connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM (
                            SELECT g.dg_game_id,
                                   COUNT(o.dgp_ply) AS occurrence_count,
                                   MIN(o.dgp_ply) AS first_ply,
                                   MAX(o.dgp_ply) AS last_ply,
                                   SUM(CASE WHEN o.dgp_move_uci IS NULL THEN 1 ELSE 0 END)
                                       AS final_count,
                                   MAX(
                                       CASE
                                           WHEN o.dgp_move_uci IS NULL THEN o.dgp_ply
                                           ELSE -1
                                       END
                                   ) AS final_ply,
                                   COUNT(
                                       CASE WHEN o.dgp_move_uci IS NOT NULL THEN 1 END
                                   ) AS outgoing_move_count
                            FROM datasource_game AS g
                            LEFT JOIN derived_game_position AS o
                              ON o.datasource_game_id = g.dg_game_id
                            GROUP BY g.dg_game_id
                            HAVING occurrence_count < 1
                                OR first_ply <> 0
                                OR occurrence_count <> last_ply + 1
                                OR final_count <> 1
                                OR final_ply <> last_ply
                                OR outgoing_move_count <> occurrence_count - 1
                        )
                        """
                    )
                ).scalar_one()
            )
            opening_route_invariant_violations = int(
                connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM (
                            SELECT r.dor_route_id,
                                   COUNT(m.dorm_ply) AS move_count,
                                   MIN(m.dorm_ply) AS first_ply,
                                   MAX(m.dorm_ply) AS last_ply,
                                   COUNT(DISTINCT m.dorm_ply) AS distinct_ply_count
                            FROM derived_opening_route AS r
                            LEFT JOIN derived_opening_route_move AS m
                              ON m.derived_opening_route_id = r.dor_route_id
                            GROUP BY r.dor_route_id
                            HAVING move_count < 1
                                OR first_ply <> 1
                                OR last_ply <> move_count
                                OR distinct_ply_count <> move_count
                        )
                        """
                    )
                ).scalar_one()
            )
            if explain_position_id is not None:
                if type(explain_position_id) is not int or explain_position_id < 1:
                    raise DirectPreflightError("explain_position_id must be a positive integer")
                measurements.extend(
                    _measure_query(
                        connection,
                        "position_context",
                        """
                        SELECT COUNT(DISTINCT o.datasource_game_id)
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        WHERE o.derived_position_id = :position_id
                        """,
                        {"position_id": explain_position_id},
                    )
                )
                measurements.extend(
                    _measure_query(
                        connection,
                        "move_response_distribution",
                        """
                        SELECT o.dgp_move_uci, p.dp_side_to_move, g.dg_trainer_color
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        JOIN derived_position AS p
                          ON p.dp_position_id = o.derived_position_id
                        WHERE o.derived_position_id = :position_id
                        """,
                        {"position_id": explain_position_id},
                    )
                )
                measurements.extend(
                    _measure_query(
                        connection,
                        "analysis_read",
                        """
                        SELECT r.derived_position_id, r.dar_quality, l.dal_rank
                        FROM derived_analysis_result AS r
                        LEFT JOIN derived_analysis_line AS l
                          ON l.derived_analysis_result_id = r.derived_position_id
                        WHERE r.derived_position_id = :position_id
                        ORDER BY CASE r.dar_quality
                            WHEN 'browser' THEN 0 WHEN 'tool' THEN 1 END,
                            l.dal_rank
                        """,
                        {"position_id": explain_position_id},
                    )
                )
    except DirectPreflightError:
        raise
    except Exception as error:
        raise DirectPreflightError("aggregate direct proof could not be collected") from error

    return DirectProof(
        database_path=path,
        verification=verification,
        table_names=table_names,
        table_counts=counts,
        preference_row_count=preference_count,
        analysis_result_count=analysis_result_count,
        analysis_line_count=analysis_line_count,
        game_occurrence_invariant_violations=game_occurrence_invariant_violations,
        opening_route_invariant_violations=opening_route_invariant_violations,
        measurements=tuple(measurements),
    )
