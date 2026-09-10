"""Read-only composition of the public insight for one chess position."""

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


class PositionInsightError(Exception):
    """Base class for bounded position-insight failures."""


class PositionInsightValidationError(PositionInsightError, ValueError):
    """Raised when a position-insight request is invalid."""


class PositionInsightSchemaError(PositionInsightError, RuntimeError):
    """Raised when the selected database is not the exact supported schema."""


class PositionInsightStorageError(PositionInsightError, RuntimeError):
    """Raised when a compatible database cannot provide a valid insight."""


@dataclass(frozen=True, slots=True)
class PositionInsightRequest:
    """The complete position, trainer-color, and date context for one read."""

    fen: str
    trainer_color: TrainerColor
    as_of: str

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise PositionInsightValidationError("fen must be a complete legal FEN") from error
        if self.trainer_color not in ("white", "black"):
            raise PositionInsightValidationError(
                "trainer_color must be 'white' or 'black'"
            )
        if not isinstance(self.as_of, str):
            raise PositionInsightValidationError("as_of must be a literal YYYY-MM-DD date")
        try:
            parsed_date = date.fromisoformat(self.as_of)
        except ValueError as error:
            raise PositionInsightValidationError(
                "as_of must be a literal YYYY-MM-DD date"
            ) from error
        if parsed_date.isoformat() != self.as_of:
            raise PositionInsightValidationError(
                "as_of must be a literal YYYY-MM-DD date"
            )
        object.__setattr__(self, "fen", _canonical_fen(position))


@dataclass(frozen=True, slots=True)
class PositionInsightOpening:
    """The current public opening label reached at this position."""

    key: str
    eco: str
    name: str
    ply: int
    match: Literal["route", "transposition"]


@dataclass(frozen=True, slots=True)
class PositionInsightExperience:
    """Trainer-color-scoped distinct-game and occurrence counts."""

    distinct_game_count: int
    occurrence_count: int
    total_game_count: int


@dataclass(frozen=True, slots=True)
class PositionInsightTerminalTotals:
    """Trainer-color-scoped counts for terminal position occurrences."""

    distinct_game_count: int
    occurrence_count: int


@dataclass(frozen=True, slots=True)
class PositionInsightObservedMoveTotals:
    """Trainer-color-scoped counts for occurrences with outgoing moves."""

    distinct_game_count: int
    occurrence_count: int
    terminal: PositionInsightTerminalTotals


@dataclass(frozen=True, slots=True)
class PositionInsightObservedMove:
    """One stored outgoing move and its trainer-color-scoped counts."""

    move_uci: str
    distinct_game_count: int
    occurrence_count: int


@dataclass(frozen=True, slots=True)
class PositionInsightResult:
    """The public current analysis result without its private position ID."""

    quality: AnalysisQuality
    configuration_version: int
    settings: Mapping[str, Any]
    engine_name: str
    engine_version: str
    terminal_kind: AnalysisTerminalKind | None
    lines: tuple[AnalysisLine, ...]

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "quality", AnalysisQuality(self.quality))
            object.__setattr__(self, "settings", validate_settings_object(self.settings))
            if self.terminal_kind is not None:
                object.__setattr__(
                    self, "terminal_kind", AnalysisTerminalKind(self.terminal_kind)
                )
            normalized_lines = tuple(self.lines)
        except (TypeError, ValueError) as error:
            raise PositionInsightStorageError("analysis result value is malformed") from error
        if type(self.configuration_version) is not int or self.configuration_version < 1:
            raise PositionInsightStorageError("analysis result configuration is malformed")
        if not isinstance(self.engine_name, str) or not self.engine_name:
            raise PositionInsightStorageError("analysis result engine name is malformed")
        if not isinstance(self.engine_version, str) or not self.engine_version:
            raise PositionInsightStorageError("analysis result engine version is malformed")
        if any(not isinstance(line, AnalysisLine) for line in normalized_lines):
            raise PositionInsightStorageError("analysis result lines are malformed")
        if self.terminal_kind is not None and normalized_lines:
            raise PositionInsightStorageError("terminal analysis result has candidate lines")
        if self.terminal_kind is None and not normalized_lines:
            raise PositionInsightStorageError("analysis result has no candidate lines")
        object.__setattr__(self, "lines", normalized_lines)


@dataclass(frozen=True, slots=True)
class PositionInsightAnalysis:
    """Current queue state and, when available, the complete current result."""

    state: AnalysisState
    result: PositionInsightResult | None


@dataclass(frozen=True, slots=True)
class PositionInsightPreference:
    """The preference resolved for the requested date."""

    kind: PreferenceKind
    uci: str | None = None

    def __post_init__(self) -> None:
        if self.kind == "move":
            if not isinstance(self.uci, str) or not self.uci:
                raise PositionInsightStorageError("resolved preference move is malformed")
        elif self.kind in ("no_preference", "unconfigured"):
            if self.uci is not None:
                raise PositionInsightStorageError(
                    "non-move preference must not contain a move"
                )
        else:
            raise PositionInsightStorageError("resolved preference kind is malformed")


@dataclass(frozen=True, slots=True)
class PositionInsight:
    """The complete sparse-capable public insight for one canonical position."""

    fen: str
    trainer_color: TrainerColor
    as_of: str
    observed_in_games: bool
    opening: PositionInsightOpening | None
    experience: PositionInsightExperience
    observed_moves: tuple[PositionInsightObservedMove, ...]
    observed_move_totals: PositionInsightObservedMoveTotals
    analysis: PositionInsightAnalysis
    preference: PositionInsightPreference


class PositionInsightRepository:
    """Compose one insight using only an explicit, compatible database path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def read(self, request: PositionInsightRequest) -> PositionInsight:
        """Read one insight without resolving or creating a derived position."""

        if not isinstance(request, PositionInsightRequest):
            raise PositionInsightValidationError(
                "request must be a PositionInsightRequest value"
            )

        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                position_id = _find_existing_position_id(
                    connection, canonicalize_fen(request.fen)
                )
                if position_id is None:
                    statistics = _read_position_statistics(connection, None, request)
                    return _sparse_insight(request, statistics)
                statistics, queue_state, preference = _read_position_data(
                    connection, position_id, request
                )
        except SchemaIncompatibleError as error:
            raise PositionInsightSchemaError(str(error)) from error
        except PositionInsightError:
            raise
        except Exception as error:
            raise PositionInsightStorageError("position insight could not be read") from error

        opening = _read_opening(self._database_path, request.fen)
        result = _read_analysis_result(self._database_path, position_id)
        state = _analysis_state(queue_state, result)
        return PositionInsight(
            fen=request.fen,
            trainer_color=request.trainer_color,
            as_of=request.as_of,
            opening=opening,
            observed_in_games=statistics.observed_in_games,
            experience=statistics.experience,
            observed_moves=statistics.observed_moves,
            observed_move_totals=statistics.observed_move_totals,
            analysis=PositionInsightAnalysis(state=state, result=result),
            preference=preference,
        )

    get = read


def read_position_insight(
    database_path: str | Path,
    fen: str | PositionInsightRequest,
    trainer_color: TrainerColor | None = None,
    as_of: str | None = None,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> PositionInsight:
    """Read one position insight from an explicit database path."""

    if isinstance(fen, PositionInsightRequest):
        if trainer_color is not None or as_of is not None:
            raise PositionInsightValidationError(
                "request cannot be combined with trainer_color or as_of"
            )
        request = fen
    else:
        if trainer_color is None or as_of is None:
            raise PositionInsightValidationError(
                "fen, trainer_color, and as_of are required"
            )
        request = PositionInsightRequest(fen, trainer_color, as_of)
    return PositionInsightRepository(database_path, lock_timeout=lock_timeout).read(request)


get_position_insight = read_position_insight


def _sparse_insight(
    request: PositionInsightRequest,
    statistics: _PositionInsightStatistics,
) -> PositionInsight:
    return PositionInsight(
        fen=request.fen,
        trainer_color=request.trainer_color,
        as_of=request.as_of,
        opening=None,
        observed_in_games=statistics.observed_in_games,
        experience=statistics.experience,
        observed_moves=statistics.observed_moves,
        observed_move_totals=statistics.observed_move_totals,
        analysis=PositionInsightAnalysis("not_requested", None),
        preference=PositionInsightPreference("unconfigured"),
    )


@dataclass(frozen=True, slots=True)
class _PositionInsightStatistics:
    observed_in_games: bool
    experience: PositionInsightExperience
    observed_moves: tuple[PositionInsightObservedMove, ...]
    observed_move_totals: PositionInsightObservedMoveTotals


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


def _read_statistics_count(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise PositionInsightStorageError(f"{name} is malformed")
    return value


def _read_statistics_flag(value: object) -> bool:
    if type(value) is not int or value not in (0, 1):
        raise PositionInsightStorageError("position observation flag is malformed")
    return bool(value)


def _read_queue_state(connection: object, position_id: int) -> str | None:
    from ..stockfish.queue import QueueStorageError, _read_observed_queue_state

    try:
        return _read_observed_queue_state(connection, position_id)
    except QueueStorageError as error:
        raise PositionInsightStorageError(str(error)) from error


def _read_preference(
    connection: object,
    position_id: int,
    as_of: str,
) -> PositionInsightPreference:
    rows = connection.execute(
        text(
            """
            SELECT dpm_effective_from, dpm_effective_until, dpm_move_uci
            FROM datasource_preferred_move_period
            WHERE derived_position_id = :position_id
            ORDER BY dpm_effective_from
            """
        ),
        {"position_id": position_id},
    ).all()
    periods: list[NormalizedPeriod] = []
    try:
        for row in rows:
            if not isinstance(row[0], str):
                raise ValueError("preference start date")
            if row[1] is not None and not isinstance(row[1], str):
                raise ValueError("preference end date")
            if row[2] is not None:
                _validate_stored_move(row[2])
            preference = (
                Preference.no_preference()
                if row[2] is None
                else Preference.preferred_move(row[2])
            )
            periods.append(period_from_literals(row[0], row[1], preference))
        resolution = resolve_date(normalize_periods(periods), as_of)
    except (IndexError, TypeError, ValueError, RangeValidationError) as error:
        raise PositionInsightStorageError("preferred-move schedule is malformed") from error
    if resolution.state is ResolutionState.PREFERRED_MOVE:
        return PositionInsightPreference("move", resolution.move)
    if resolution.state is ResolutionState.NO_PREFERENCE:
        return PositionInsightPreference("no_preference")
    return PositionInsightPreference("unconfigured")


def _read_opening(database_path: str | Path, fen: str) -> PositionInsightOpening | None:
    try:
        recognition = lookup_fen(database_path, fen)
    except (OpeningInputError, OpeningRecognitionError, SchemaIncompatibleError) as error:
        raise PositionInsightStorageError("opening recognition could not be read") from error
    except PositionInsightError:
        raise
    except Exception as error:
        raise PositionInsightStorageError("opening recognition could not be read") from error
    current = recognition.current
    if current is None:
        return None
    try:
        return PositionInsightOpening(
            key=opening_api_key(current.eco, current.name),
            eco=current.eco,
            name=current.name,
            ply=current.ply,
            match=current.match,
        )
    except ValueError as error:
        raise PositionInsightStorageError("opening recognition is malformed") from error


def _read_analysis_result(
    database_path: str | Path,
    position_id: int,
) -> PositionInsightResult | None:
    try:
        result = AnalysisReadRepository(database_path).read(position_id)
    except (AnalysisReadError, SchemaIncompatibleError) as error:
        raise PositionInsightStorageError("analysis result could not be read") from error
    except PositionInsightError:
        raise
    except Exception as error:
        raise PositionInsightStorageError("analysis result could not be read") from error
    if result is None:
        return None
    return PositionInsightResult(
        quality=result.quality,
        configuration_version=result.configuration_version,
        settings=result.settings,
        engine_name=result.engine_name,
        engine_version=result.engine_version,
        terminal_kind=result.terminal_kind,
        lines=result.lines,
    )


def _analysis_state(
    queue_state: str | None,
    result: PositionInsightResult | None,
) -> AnalysisState:
    if queue_state == "running":
        return "running"
    if queue_state == "queued":
        return "queued"
    if result is not None:
        return "ready"
    return "not_requested"


def _validate_stored_move(value: object) -> None:
    if not isinstance(value, str) or not value:
        raise PositionInsightStorageError("stored UCI move is malformed")
    try:
        move = chess.Move.from_uci(value)
    except (TypeError, ValueError) as error:
        raise PositionInsightStorageError("stored UCI move is malformed") from error
    if move.uci() != value:
        raise PositionInsightStorageError("stored UCI move is not canonical")


def _canonical_fen(position: CanonicalPosition) -> str:
    return " ".join(
        (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
            "0",
            "1",
        )
    )


__all__ = [
    "AnalysisState",
    "PreferenceKind",
    "PositionInsight",
    "PositionInsightAnalysis",
    "PositionInsightError",
    "PositionInsightExperience",
    "PositionInsightOpening",
    "PositionInsightObservedMove",
    "PositionInsightObservedMoveTotals",
    "PositionInsightPreference",
    "PositionInsightRepository",
    "PositionInsightRequest",
    "PositionInsightResult",
    "PositionInsightSchemaError",
    "PositionInsightStorageError",
    "PositionInsightTerminalTotals",
    "PositionInsightValidationError",
    "TrainerColor",
    "get_position_insight",
    "read_position_insight",
]
