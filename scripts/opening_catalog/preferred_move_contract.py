"""Small value contracts for the direct preferred-move access layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .classification_contract import PositionKey


@dataclass(frozen=True)
class PreferredMoveState:
    """The independently derived requirement and preferred-move state."""

    player_uuid: str
    position: PositionKey
    requirement_active: bool
    move_uci: str | None
    move_san: str | None

    @property
    def status(self) -> str:
        if self.requirement_active and self.move_uci is not None:
            return "satisfied"
        if self.requirement_active:
            return "choice_needed"
        if self.move_uci is not None:
            return "stored_out_of_scope"
        return "not_required"


@dataclass(frozen=True)
class PreferredMoveWrite:
    """The result of an append attempt, including no-op writes."""

    changed: bool
    event_id: int | None
    action: str
    effective_at: datetime
    recorded_at: datetime | None
    move_uci: str | None = None
    move_san: str | None = None


@dataclass(frozen=True)
class PreferredMoveLineWrite:
    """The two-history writes produced by one validated line replay."""

    positions: tuple[PositionKey, ...]
    requirements: tuple[PreferredMoveWrite, ...]
    moves: tuple[PreferredMoveWrite, ...]

    @property
    def changed(self) -> bool:
        return any(item.changed for item in (*self.requirements, *self.moves))


@dataclass(frozen=True)
class RequirementPeriod:
    """One effective-time interval of requirement state."""

    start: datetime
    end: datetime
    active: bool


@dataclass(frozen=True)
class PreferredMovePeriod:
    """One effective-time interval, including an explicit no-move period."""

    start: datetime
    end: datetime
    move_uci: str | None
    move_san: str | None


@dataclass(frozen=True)
class PreferredMoveStatePeriod:
    """One effective-time interval of the combined directly derived state."""

    start: datetime
    end: datetime
    requirement_active: bool
    move_uci: str | None
    move_san: str | None

    @property
    def status(self) -> str:
        if self.requirement_active and self.move_uci is not None:
            return "satisfied"
        if self.requirement_active:
            return "choice_needed"
        if self.move_uci is not None:
            return "stored_out_of_scope"
        return "not_required"


@dataclass(frozen=True)
class GameComparison:
    """Comparison of one observed position occurrence at its game's end time."""

    game_uuid: str
    occurrence_ply: int
    end_time: int
    preferred_move_uci: str | None
    actual_move_uci: str | None
    requirement_active: bool
    judged: bool
    matches: bool | None

    @property
    def is_judged(self) -> bool:
        return self.judged
