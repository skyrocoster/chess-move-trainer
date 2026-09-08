"""Read the complete current analysis result and candidate lines."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .models import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisScoreKind,
    AnalysisTerminalKind,
)


class AnalysisReadError(RuntimeError):
    """Raised when a current analysis result is incomplete or malformed."""


@dataclass(frozen=True, slots=True)
class AnalysisReadResult:
    """One current result with all of its ordered candidate lines."""

    position_id: int
    quality: AnalysisQuality
    configuration_version: int
    settings: dict[str, object]
    engine_name: str
    engine_version: str
    terminal_kind: AnalysisTerminalKind | None
    lines: tuple[AnalysisLine, ...]

    @property
    def result(self) -> AnalysisReadResult:
        """Return the current result value for callers using a result/read shape."""

        return self

    @property
    def quality_order(self) -> int:
        """Return the settled Browser < Tool ordering."""

        return 0 if self.quality is AnalysisQuality.BROWSER else 1


class AnalysisReadRepository:
    """Read one complete current result through a package-owned read path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def read(self, position_id: int) -> AnalysisReadResult | None:
        """Return the current complete result for a canonical position."""

        if type(position_id) is not int or position_id < 1:
            raise AnalysisReadError("position_id must be a positive integer")
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                parent = connection.execute(
                    text(
                        """
                        SELECT derived_position_id, dar_quality,
                               dar_configuration_version, dar_settings_json,
                               dar_engine_name, dar_engine_version, dar_terminal_kind
                        FROM derived_analysis_result
                        WHERE derived_position_id = :position_id
                        ORDER BY CASE dar_quality WHEN 'browser' THEN 0 WHEN 'tool' THEN 1 END
                        """
                    ),
                    {"position_id": position_id},
                ).first()
                if parent is None:
                    return None
                line_rows = connection.execute(
                    text(
                        """
                        SELECT dal_rank, dal_score_kind, dal_score_value,
                               dal_wdl_wins, dal_wdl_draws, dal_wdl_losses,
                               dal_pv_uci_json, dal_depth
                        FROM derived_analysis_line
                        WHERE derived_analysis_result_id = :position_id
                        ORDER BY dal_rank
                        """
                    ),
                    {"position_id": position_id},
                ).all()
        except SchemaIncompatibleError:
            raise
        except AnalysisReadError:
            raise
        except Exception as error:
            raise AnalysisReadError("analysis result could not be read") from error

        return _materialize_result(parent, line_rows)

    read_current = read
    get = read


def _materialize_result(parent: object, line_rows: list[object]) -> AnalysisReadResult:
    try:
        position_id = int(parent[0])
        quality = AnalysisQuality(parent[1])
        configuration_version = int(parent[2])
        settings_value = json.loads(parent[3])
        if not isinstance(settings_value, dict):
            raise ValueError("analysis settings must be a JSON object")
        engine_name = _required_text(parent[4], "engine name")
        engine_version = _required_text(parent[5], "engine version")
        terminal_kind = (
            None if parent[6] is None else AnalysisTerminalKind(parent[6])
        )
        lines = tuple(_line_from_row(row) for row in line_rows)
    except (IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise AnalysisReadError("analysis result row is malformed") from error

    ranks = tuple(line.rank for line in lines)
    if ranks != tuple(range(1, len(lines) + 1)):
        raise AnalysisReadError("analysis lines are not complete and contiguous")
    if terminal_kind is not None and lines:
        raise AnalysisReadError("terminal analysis must not have candidate lines")
    if terminal_kind is None and not lines:
        raise AnalysisReadError("non-terminal analysis must have candidate lines")
    return AnalysisReadResult(
        position_id=position_id,
        quality=quality,
        configuration_version=configuration_version,
        settings=dict(settings_value),
        engine_name=engine_name,
        engine_version=engine_version,
        terminal_kind=terminal_kind,
        lines=lines,
    )


def _line_from_row(row: object) -> AnalysisLine:
    try:
        pv = json.loads(row[6])
        if not isinstance(pv, list):
            raise ValueError("principal variation must be a JSON array")
        return AnalysisLine(
            rank=int(row[0]),
            score_kind=AnalysisScoreKind(row[1]),
            score_value=int(row[2]),
            wdl_wins=int(row[3]),
            wdl_draws=int(row[4]),
            wdl_losses=int(row[5]),
            pv_uci=tuple(pv),
            depth=int(row[7]),
        )
    except (IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise AnalysisReadError("analysis line row is malformed") from error


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


__all__ = ["AnalysisReadError", "AnalysisReadRepository", "AnalysisReadResult"]
