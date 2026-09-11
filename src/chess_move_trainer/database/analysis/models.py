"""Immutable normalized analysis values and bounded outcome categories."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AnalysisError(Exception):
    """Base class for bounded analysis-package failures."""


class AnalysisValidationError(AnalysisError, ValueError):
    """Raised when normalized analysis input is outside the catalogue domain."""


class AnalysisStorageError(AnalysisError, RuntimeError):
    """Reserved category for an unexpected analysis storage failure."""


class AnalysisQuality(str, Enum):
    """The two approved analysis quality levels."""

    BROWSER = "browser"
    TOOL = "tool"


class AnalysisScoreKind(str, Enum):
    """The two approved score representations."""

    CP = "cp"
    MATE = "mate"


class AnalysisTerminalKind(str, Enum):
    """Terminal outcomes derived from a canonical neutral root."""

    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"


class NotSavedReason(str, Enum):
    """Expected reasons a later publication operation may decline a result."""

    DUPLICATE = "duplicate"
    STALE_OR_OUTDATED = "stale_or_outdated"
    LOWER_QUALITY = "lower_quality"


class _FrozenJsonObject(dict[str, Any]):
    """A JSON-compatible dict whose ordinary mutation operations are disabled."""

    __slots__ = ()

    def __init__(self, values: Mapping[str, Any]) -> None:
        dict.__init__(self, values)

    @staticmethod
    def _immutable(*_: object, **__: object) -> None:
        raise TypeError("settings are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable


@dataclass(frozen=True, slots=True)
class AnalysisLine:
    """One normalized candidate line before terminal or chess-legality checks."""

    rank: int
    score_kind: AnalysisScoreKind
    score_value: int
    wdl_wins: int
    wdl_draws: int
    wdl_losses: int
    pv_uci: tuple[str, ...]
    depth: int

    def __post_init__(self) -> None:
        from .validation import (
            _normalize_pv,
            _normalize_score_kind,
            _require_domain_int,
        )

        if type(self.rank) is not int or not 1 <= self.rank <= 5:
            raise AnalysisValidationError("rank must be an integer from 1 through 5")
        object.__setattr__(self, "score_kind", _normalize_score_kind(self.score_kind))
        _require_domain_int(self.score_value, "score value")
        for name, value in (
            ("WDL wins", self.wdl_wins),
            ("WDL draws", self.wdl_draws),
            ("WDL losses", self.wdl_losses),
        ):
            if type(value) is not int or value < 0:
                raise AnalysisValidationError(f"{name} must be a non-negative integer")
        if self.wdl_wins + self.wdl_draws + self.wdl_losses != 1000:
            raise AnalysisValidationError("WDL values must sum to 1000")
        object.__setattr__(self, "pv_uci", _normalize_pv(self.pv_uci))
        if type(self.depth) is not int or self.depth < 0:
            raise AnalysisValidationError("depth must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class AnalysisResultInput:
    """A complete engine-independent result payload without position or terminal authority."""

    quality: AnalysisQuality
    configuration_version: int
    settings: Mapping[str, Any]
    engine_name: str
    engine_version: str
    lines: tuple[AnalysisLine, ...] = ()

    def __post_init__(self) -> None:
        from .validation import _normalize_quality, _normalize_settings

        object.__setattr__(self, "quality", _normalize_quality(self.quality))
        if type(self.configuration_version) is not int or self.configuration_version < 1:
            raise AnalysisValidationError(
                "configuration version must be an integer greater than or equal to 1"
            )
        object.__setattr__(self, "settings", _normalize_settings(self.settings))
        if not isinstance(self.engine_name, str):
            raise AnalysisValidationError("engine name must be a string")
        if not isinstance(self.engine_version, str):
            raise AnalysisValidationError("engine version must be a string")
        if isinstance(self.lines, (str, bytes)):
            raise AnalysisValidationError(
                "lines must be an ordered collection of AnalysisLine values"
            )
        try:
            normalized_lines = tuple(self.lines)
        except TypeError as error:
            raise AnalysisValidationError(
                "lines must be an ordered collection of AnalysisLine values"
            ) from error
        if any(not isinstance(line, AnalysisLine) for line in normalized_lines):
            raise AnalysisValidationError("lines must contain only AnalysisLine values")
        object.__setattr__(self, "lines", normalized_lines)


@dataclass(frozen=True, slots=True)
class ValidatedAnalysisResult:
    """A result whose terminal kind and candidate lines passed position validation."""

    terminal_kind: AnalysisTerminalKind | None
    lines: tuple[AnalysisLine, ...]

    def __post_init__(self) -> None:
        if self.terminal_kind is not None:
            try:
                normalized_terminal_kind = AnalysisTerminalKind(self.terminal_kind)
            except ValueError as error:
                raise AnalysisValidationError("terminal kind is not supported") from error
            object.__setattr__(self, "terminal_kind", normalized_terminal_kind)
        normalized_lines = tuple(self.lines)
        if any(not isinstance(line, AnalysisLine) for line in normalized_lines):
            raise AnalysisValidationError("validated lines must contain only AnalysisLine values")
        if self.terminal_kind is not None and normalized_lines:
            raise AnalysisValidationError("terminal validated results cannot contain lines")
        object.__setattr__(self, "lines", normalized_lines)


@dataclass(frozen=True, slots=True)
class PublicationOutcome:
    """Saved or expected not-saved result for the future publication service."""

    saved: bool
    reason: NotSavedReason | None = None

    def __post_init__(self) -> None:
        if type(self.saved) is not bool:
            raise AnalysisValidationError("publication outcome saved flag must be a boolean")
        if self.saved:
            if self.reason is not None:
                raise AnalysisValidationError("a saved outcome cannot have a not-saved reason")
            return
        if self.reason is None:
            raise AnalysisValidationError("a not-saved outcome requires a reason")
        try:
            normalized_reason = NotSavedReason(self.reason)
        except ValueError as error:
            raise AnalysisValidationError(
                "publication outcome has an unknown not-saved reason"
            ) from error
        object.__setattr__(self, "reason", normalized_reason)

    @classmethod
    def saved_result(cls) -> PublicationOutcome:
        """Build the successful publication outcome."""

        return cls(saved=True)

    @classmethod
    def not_saved(cls, reason: NotSavedReason | str) -> PublicationOutcome:
        """Build an expected not-saved outcome with its explicit reason."""

        return cls(saved=False, reason=reason)
