"""Shared query-plan measurement helper."""
from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text

from .proof_models import DirectPreflightError, QueryPlanMeasurement


def _measure_query(
    connection: Any,
    name: str,
    statement: str,
    parameters: dict[str, object],
    *,
    repetitions: int = 1,
) -> tuple[QueryPlanMeasurement, ...]:
    if type(repetitions) is not int or repetitions < 1:
        raise DirectPreflightError("measurement repetitions must be positive")
    plan_rows = connection.execute(
        text(f"EXPLAIN QUERY PLAN {statement}"), parameters
    ).all()
    elapsed_seconds: list[float] = []
    result_row_count: int | None = None
    for _ in range(repetitions):
        started = time.perf_counter()
        rows = connection.execute(text(statement), parameters).all()
        elapsed_seconds.append(time.perf_counter() - started)
        if result_row_count is None:
            result_row_count = len(rows)
        elif len(rows) != result_row_count:
            raise DirectPreflightError(
                f"measurement result count changed for {name}"
            )
    return (
        QueryPlanMeasurement(
            name=name,
            plan=tuple(" ".join(str(row[-1]).split()) for row in plan_rows),
            elapsed_seconds=tuple(elapsed_seconds),
            result_row_count=0 if result_row_count is None else result_row_count,
        ),
    )
