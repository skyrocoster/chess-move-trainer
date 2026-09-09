"""Package-owned preferred-move mutation values and operation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from ..positions import CanonicalPosition, PositionValidationError, canonicalize_fen
from .ranges import (
    NormalizedPeriod,
    Preference,
    RangeValidationError,
    parse_date_literal,
    set_preference,
    unset_preference,
)
from .repository import (
    PreferredMoveRepository,
    PreferredMoveValidationError,
    _validate_preference,
)


@dataclass(frozen=True, slots=True)
class PreferredMoveMutationRequest:
    """One complete parent FEN and one configured half-open interval."""

    fen: str
    effective_from: str
    effective_until: str | None = None
    preference: Preference | None = None

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise PreferredMoveValidationError("FEN is invalid") from error

        if not isinstance(self.preference, Preference):
            raise PreferredMoveValidationError("Preference is invalid")

        start = _parse_mutation_date(self.effective_from, "effective_from")
        end = (
            None
            if self.effective_until is None
            else _parse_mutation_date(self.effective_until, "effective_until")
        )
        if end is not None and end <= start:
            raise PreferredMoveValidationError(
                "effective_until must be later than effective_from"
            )

        object.__setattr__(self, "fen", _canonical_fen(position))
        object.__setattr__(self, "effective_from", start.isoformat())
        object.__setattr__(
            self,
            "effective_until",
            None if end is None else end.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class PreferredMoveMutationResult:
    """The applied interval and complete configured schedule after one PUT."""

    fen: str
    effective_from: str
    effective_until: str | None
    preference: Preference
    periods: tuple[NormalizedPeriod, ...]


@dataclass(frozen=True, slots=True)
class PreferredMoveRemovalRequest:
    """One complete parent FEN and one configured half-open interval to remove."""

    fen: str
    effective_from: str
    effective_until: str | None = None

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise PreferredMoveValidationError("FEN is invalid") from error

        start = _parse_mutation_date(self.effective_from, "effective_from")
        end = (
            None
            if self.effective_until is None
            else _parse_mutation_date(self.effective_until, "effective_until")
        )
        if end is not None and end <= start:
            raise PreferredMoveValidationError(
                "effective_until must be later than effective_from"
            )

        object.__setattr__(self, "fen", _canonical_fen(position))
        object.__setattr__(self, "effective_from", start.isoformat())
        object.__setattr__(
            self,
            "effective_until",
            None if end is None else end.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class PreferredMoveRemovalResult:
    """The removed interval and complete configured schedule after DELETE."""

    fen: str
    effective_from: str
    effective_until: str | None
    periods: tuple[NormalizedPeriod, ...]


def put_preferred_move(
    database_path: str | Path,
    request: PreferredMoveMutationRequest,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    _checkpoint: Callable[[str], None] | None = None,
) -> PreferredMoveMutationResult:
    """Atomically apply one ordinary preferred-move mutation value."""

    if not isinstance(request, PreferredMoveMutationRequest):
        raise PreferredMoveValidationError(
            "request must be a PreferredMoveMutationRequest value"
        )

    position = canonicalize_fen(request.fen)
    try:
        _validate_preference(
            position,
            request.preference,
            require_canonical_uci=True,
        )
    except PreferredMoveValidationError as error:
        if str(error) == "move must be valid UCI":
            raise PreferredMoveValidationError("UCI move is invalid") from error
        raise PreferredMoveValidationError(
            "Move is illegal from the parent FEN"
        ) from error

    repository = PreferredMoveRepository(
        database_path,
        lock_timeout=lock_timeout,
        _checkpoint=_checkpoint,
    )
    periods = repository._amend(
        position,
        lambda schedule: set_preference(
            schedule,
            request.effective_from,
            request.effective_until,
            request.preference,
        ),
    )
    return PreferredMoveMutationResult(
        fen=request.fen,
        effective_from=request.effective_from,
        effective_until=request.effective_until,
        preference=request.preference,
        periods=periods,
    )


def delete_preferred_move(
    database_path: str | Path,
    request: PreferredMoveRemovalRequest,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    _checkpoint: Callable[[str], None] | None = None,
) -> PreferredMoveRemovalResult:
    """Atomically remove one ordinary preferred-move interval value."""

    if not isinstance(request, PreferredMoveRemovalRequest):
        raise PreferredMoveValidationError(
            "request must be a PreferredMoveRemovalRequest value"
        )

    position = canonicalize_fen(request.fen)
    repository = PreferredMoveRepository(
        database_path,
        lock_timeout=lock_timeout,
        _checkpoint=_checkpoint,
    )
    periods = repository._amend(
        position,
        lambda schedule: unset_preference(
            schedule,
            request.effective_from,
            request.effective_until,
        ),
    )
    return PreferredMoveRemovalResult(
        fen=request.fen,
        effective_from=request.effective_from,
        effective_until=request.effective_until,
        periods=periods,
    )


def _parse_mutation_date(value: object, field_name: str) -> date:
    try:
        if not isinstance(value, str):
            raise RangeValidationError("date must be a string")
        return parse_date_literal(value, field_name=field_name)
    except (RangeValidationError, TypeError, ValueError) as error:
        raise PreferredMoveValidationError(
            f"{field_name} must be a literal YYYY-MM-DD date"
        ) from error


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
    "PreferredMoveRemovalRequest",
    "PreferredMoveRemovalResult",
    "PreferredMoveMutationRequest",
    "PreferredMoveMutationResult",
    "delete_preferred_move",
    "put_preferred_move",
]
