"""Read-only finite timelines for canonical preferred-move schedules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from ..positions import PositionValidationError, canonicalize_fen
from .ranges import (
    NormalizedPeriod,
    PreferenceState,
    RangeValidationError,
    parse_date_literal,
)
from .repository import (
    PreferredMoveRepository,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
)

TimelinePreferenceKind = Literal["move", "no_preference", "unconfigured"]


@dataclass(frozen=True, slots=True)
class PreferredMoveTimelineRequest:
    """One complete canonical FEN and strict half-open date window."""

    fen: str
    from_date: str
    until: str

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise PreferredMoveValidationError(
                "fen must be a complete legal FEN"
            ) from error

        try:
            start = parse_date_literal(self.from_date, field_name="from")
            end = parse_date_literal(self.until, field_name="until")
        except RangeValidationError as error:
            raise PreferredMoveValidationError(str(error)) from error
        if start >= end:
            raise PreferredMoveValidationError("from must be earlier than until")

        object.__setattr__(self, "fen", _canonical_fen(position))
        object.__setattr__(self, "from_date", start.isoformat())
        object.__setattr__(self, "until", end.isoformat())

    @property
    def from_(self) -> str:
        """Return the strict start date for callers avoiding the reserved word."""

        return self.from_date

    @property
    def until_date(self) -> str:
        """Return the strict end date using the descriptive package spelling."""

        return self.until


@dataclass(frozen=True, slots=True)
class PreferredMoveTimelinePreference:
    """One immutable public tag carried by a timeline segment."""

    kind: TimelinePreferenceKind
    uci: str | None = None

    def __post_init__(self) -> None:
        if self.kind == "move":
            if type(self.uci) is not str or not self.uci:
                raise PreferredMoveValidationError(
                    "a move preference requires a UCI move"
                )
        elif self.kind in ("no_preference", "unconfigured"):
            if self.uci is not None:
                raise PreferredMoveValidationError(
                    "a non-move preference cannot contain a UCI move"
                )
        else:
            raise PreferredMoveValidationError("unknown timeline preference kind")

    @classmethod
    def move(cls, uci: str) -> PreferredMoveTimelinePreference:
        return cls("move", uci)

    @classmethod
    def no_preference(cls) -> PreferredMoveTimelinePreference:
        return cls("no_preference")

    @classmethod
    def unconfigured(cls) -> PreferredMoveTimelinePreference:
        return cls("unconfigured")


@dataclass(frozen=True, slots=True)
class PreferredMoveTimelineSegment:
    """One non-empty half-open segment in an immutable timeline."""

    from_date: str
    until: str
    preference: PreferredMoveTimelinePreference

    def __post_init__(self) -> None:
        try:
            start = parse_date_literal(self.from_date, field_name="segment from")
            end = parse_date_literal(self.until, field_name="segment until")
        except RangeValidationError as error:
            raise PreferredMoveValidationError(str(error)) from error
        if start >= end:
            raise PreferredMoveValidationError(
                "segment from must be earlier than segment until"
            )
        if not isinstance(self.preference, PreferredMoveTimelinePreference):
            raise PreferredMoveValidationError("segment preference is malformed")
        object.__setattr__(self, "from_date", start.isoformat())
        object.__setattr__(self, "until", end.isoformat())

    @property
    def from_(self) -> str:
        """Return the strict segment start date."""

        return self.from_date

    @property
    def until_date(self) -> str:
        """Return the strict segment end date."""

        return self.until


@dataclass(frozen=True, slots=True)
class PreferredMoveTimeline:
    """A complete exact-cover timeline for one finite request window."""

    fen: str
    from_date: str
    until: str
    segments: tuple[PreferredMoveTimelineSegment, ...]

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise PreferredMoveStorageError("timeline FEN is malformed") from error
        try:
            start = parse_date_literal(self.from_date, field_name="from")
            end = parse_date_literal(self.until, field_name="until")
        except RangeValidationError as error:
            raise PreferredMoveStorageError("timeline window is malformed") from error
        if start >= end:
            raise PreferredMoveStorageError("timeline window is malformed")

        segments = tuple(self.segments)
        if not segments or any(
            not isinstance(segment, PreferredMoveTimelineSegment)
            for segment in segments
        ):
            raise PreferredMoveStorageError("timeline segments are malformed")

        cursor = start
        previous_preference: PreferredMoveTimelinePreference | None = None
        for segment in segments:
            segment_start = date.fromisoformat(segment.from_date)
            segment_end = date.fromisoformat(segment.until)
            if segment_start != cursor:
                raise PreferredMoveStorageError(
                    "timeline segments do not exactly cover the requested window"
                )
            if (
                previous_preference is not None
                and previous_preference == segment.preference
            ):
                raise PreferredMoveStorageError(
                    "timeline contains adjacent equal preferences"
                )
            if segment_end > end:
                raise PreferredMoveStorageError(
                    "timeline segments exceed the requested window"
                )
            cursor = segment_end
            previous_preference = segment.preference
        if cursor != end:
            raise PreferredMoveStorageError(
                "timeline segments do not exactly cover the requested window"
            )

        object.__setattr__(self, "fen", _canonical_fen(position))
        object.__setattr__(self, "from_date", start.isoformat())
        object.__setattr__(self, "until", end.isoformat())
        object.__setattr__(self, "segments", segments)

    @property
    def from_(self) -> str:
        """Return the strict timeline start date."""

        return self.from_date

    @property
    def until_date(self) -> str:
        """Return the strict timeline end date."""

        return self.until


class PreferredMoveTimelineRepository:
    """Read one preferred-move timeline from an explicit database path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._repository = PreferredMoveRepository(
            database_path, lock_timeout=lock_timeout
        )

    def read(self, request: PreferredMoveTimelineRequest) -> PreferredMoveTimeline:
        """Return a complete timeline without creating a position or period."""

        if not isinstance(request, PreferredMoveTimelineRequest):
            raise PreferredMoveValidationError(
                "request must be a PreferredMoveTimelineRequest value"
            )
        position = canonicalize_fen(request.fen)
        periods = self._repository.read_periods_for_position(position)
        return _materialize_timeline(request, periods)

    get = read


def read_preferred_moves(
    database_path: str | Path,
    fen: str | PreferredMoveTimelineRequest,
    from_date: str | None = None,
    until: str | None = None,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> PreferredMoveTimeline:
    """Read one finite preferred-move timeline from an explicit database path."""

    if isinstance(fen, PreferredMoveTimelineRequest):
        if from_date is not None or until is not None:
            raise PreferredMoveValidationError(
                "request cannot be combined with from_date or until"
            )
        request = fen
    else:
        if from_date is None or until is None:
            raise PreferredMoveValidationError(
                "fen, from_date, and until are required"
            )
        request = PreferredMoveTimelineRequest(fen, from_date, until)
    return PreferredMoveTimelineRepository(
        database_path, lock_timeout=lock_timeout
    ).read(request)


get_preferred_moves = read_preferred_moves


def _materialize_timeline(
    request: PreferredMoveTimelineRequest,
    periods: tuple[NormalizedPeriod, ...],
) -> PreferredMoveTimeline:
    start = date.fromisoformat(request.from_date)
    end = date.fromisoformat(request.until)
    cursor = start
    segments: list[PreferredMoveTimelineSegment] = []

    for period in periods:
        if period.effective_until is not None and period.effective_until <= start:
            continue
        if period.effective_from >= end:
            break

        clipped_start = max(start, period.effective_from)
        clipped_end = end if period.effective_until is None else min(end, period.effective_until)
        if clipped_end <= clipped_start:
            continue
        if cursor < clipped_start:
            _append_segment(
                segments,
                cursor,
                clipped_start,
                PreferredMoveTimelinePreference.unconfigured(),
            )
        segment_start = max(cursor, clipped_start)
        if segment_start < clipped_end:
            _append_segment(
                segments,
                segment_start,
                clipped_end,
                _timeline_preference(period),
            )
            cursor = clipped_end

    if cursor < end:
        _append_segment(
            segments,
            cursor,
            end,
            PreferredMoveTimelinePreference.unconfigured(),
        )

    return PreferredMoveTimeline(
        fen=request.fen,
        from_date=request.from_date,
        until=request.until,
        segments=tuple(segments),
    )


def _append_segment(
    segments: list[PreferredMoveTimelineSegment],
    start: date,
    end: date,
    preference: PreferredMoveTimelinePreference,
) -> None:
    if start >= end:
        return
    if segments and segments[-1].preference == preference:
        prior = segments[-1]
        segments[-1] = PreferredMoveTimelineSegment(
            from_date=prior.from_date,
            until=end.isoformat(),
            preference=preference,
        )
        return
    segments.append(
        PreferredMoveTimelineSegment(
            from_date=start.isoformat(),
            until=end.isoformat(),
            preference=preference,
        )
    )


def _timeline_preference(
    period: NormalizedPeriod,
) -> PreferredMoveTimelinePreference:
    if period.preference.state is PreferenceState.PREFERRED_MOVE:
        return PreferredMoveTimelinePreference.move(period.preference.move or "")
    return PreferredMoveTimelinePreference.no_preference()


def _canonical_fen(position: object) -> str:
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


# The result spelling is useful to callers that name all package values with
# a request/result pair while retaining the shorter public timeline name.
PreferredMoveTimelineResult = PreferredMoveTimeline


__all__ = [
    "PreferredMoveTimeline",
    "PreferredMoveTimelinePreference",
    "PreferredMoveTimelineRepository",
    "PreferredMoveTimelineRequest",
    "PreferredMoveTimelineResult",
    "PreferredMoveTimelineSegment",
    "TimelinePreferenceKind",
    "get_preferred_moves",
    "read_preferred_moves",
]
