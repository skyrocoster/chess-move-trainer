"""Position insight models."""

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


@dataclass(frozen=True, slots=True)
class _PositionInsightStatistics:
    observed_in_games: bool
    experience: PositionInsightExperience
    observed_moves: tuple[PositionInsightObservedMove, ...]
    observed_move_totals: PositionInsightObservedMoveTotals


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
