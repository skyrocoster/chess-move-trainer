"""Pure deterministic inference of preferred-move periods.

The inference boundary accepts observations that have already passed database
eligibility checks.  It deliberately knows nothing about games, persistence,
or command-line operation.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from types import MappingProxyType

from ..positions import CanonicalPosition
from .ranges import NormalizedPeriod, Preference, normalize_periods

QUALIFICATION_WINDOW_DAYS = 90
MINIMUM_MATCHES = 21


@dataclass(frozen=True, slots=True)
class PreferredMoveObservation:
    """One eligible trainer move leaving one canonical position on one date."""

    position: CanonicalPosition
    played_on: date
    move_uci: str

    def __post_init__(self) -> None:
        if not isinstance(self.position, CanonicalPosition):
            raise ValueError("observation position must be canonical")
        if type(self.played_on) is not date:
            raise ValueError("observation played_on must be a calendar date")
        if not isinstance(self.move_uci, str) or not self.move_uci:
            raise ValueError("observation move_uci must be a non-empty string")


@dataclass(frozen=True, slots=True)
class PreferredMoveInferenceSummary:
    """The inferred current schedule for one position with a qualification."""

    position: CanonicalPosition
    periods: tuple[NormalizedPeriod, ...]
    conflicting: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.position, CanonicalPosition):
            raise ValueError("inference summary position must be canonical")
        if type(self.conflicting) is not bool:
            raise ValueError("inference summary conflict flag must be a boolean")
        normalized = normalize_periods(self.periods)
        object.__setattr__(self, "periods", normalized)


@dataclass(frozen=True, slots=True)
class PreferredMoveInferenceResult:
    """All configured position schedules produced by one pure inference run."""

    summaries: tuple[PreferredMoveInferenceSummary, ...]
    conflicting_positions: tuple[CanonicalPosition, ...] = ()

    def __post_init__(self) -> None:
        summaries = tuple(self.summaries)
        if any(
            not isinstance(summary, PreferredMoveInferenceSummary)
            for summary in summaries
        ):
            raise ValueError("inference summaries must contain summary values")
        positions = tuple(summary.position for summary in summaries)
        if len(set(positions)) != len(positions):
            raise ValueError("inference summaries must contain one entry per position")
        if positions != tuple(
            sorted(
                positions,
                key=lambda position: (
                    position.placement,
                    position.side_to_move,
                    position.castling_rights,
                    position.legal_en_passant,
                ),
            )
        ):
            raise ValueError("inference summaries must be in canonical order")
        conflicts = tuple(self.conflicting_positions)
        if any(not isinstance(position, CanonicalPosition) for position in conflicts):
            raise ValueError("conflicting positions must be canonical")
        if len(set(conflicts)) != len(conflicts):
            raise ValueError("conflicting positions must be unique")
        if conflicts != tuple(sorted(conflicts, key=_position_sort_key)):
            raise ValueError("conflicting positions must be in canonical order")
        object.__setattr__(self, "summaries", summaries)
        object.__setattr__(self, "conflicting_positions", conflicts)

    @property
    def schedules(self) -> tuple[PreferredMoveInferenceSummary, ...]:
        """Return the per-position schedules using the storage-facing name."""

        return self.summaries

    @property
    def periods_by_position(
        self,
    ) -> Mapping[CanonicalPosition, tuple[NormalizedPeriod, ...]]:
        """Return a read-only position-to-period view for downstream consumers."""

        return MappingProxyType(
            {summary.position: summary.periods for summary in self.summaries}
        )

@dataclass(frozen=True, slots=True)
class _Qualification:
    """One qualifying rolling window and the signal date it produces."""

    evidence_from: date
    evidence_until: date
    candidate_from: date
    move_uci: str
    matching_occurrences: int
    eligible_occurrences: int


def infer_preferred_moves(
    observations: Iterable[PreferredMoveObservation],
) -> PreferredMoveInferenceResult:
    """Infer normalized preferred-move schedules from eligible observations.

    Every observation is counted independently.  Dates are evaluated in
    calendar order and all arithmetic uses half-open 90-day windows.
    """

    grouped: dict[CanonicalPosition, list[PreferredMoveObservation]] = defaultdict(
        list
    )
    for observation in observations:
        if not isinstance(observation, PreferredMoveObservation):
            raise ValueError("observations must contain PreferredMoveObservation values")
        grouped[observation.position].append(observation)

    summaries: list[PreferredMoveInferenceSummary] = []
    conflicting_positions: list[CanonicalPosition] = []
    for position, position_observations in sorted(
        grouped.items(), key=lambda item: _position_sort_key(item[0])
    ):
        position_result = _infer_position(position_observations)
        if position_result.conflicting:
            conflicting_positions.append(position)
        if position_result.periods:
            summaries.append(
                PreferredMoveInferenceSummary(
                    position=position,
                    periods=position_result.periods,
                    conflicting=position_result.conflicting,
                )
            )
    return PreferredMoveInferenceResult(summaries, tuple(conflicting_positions))


def _infer_position(
    observations: Iterable[PreferredMoveObservation],
) -> _PositionInference:
    ordered = tuple(sorted(observations, key=lambda item: (item.played_on, item.move_uci)))
    qualifications = _qualifications(ordered)
    if not qualifications:
        return _PositionInference((), False)

    by_candidate_date: dict[date, list[_Qualification]] = defaultdict(list)
    for qualification in qualifications:
        by_candidate_date[qualification.candidate_from].append(qualification)

    accepted: list[tuple[date, str]] = []
    active: _Qualification | None = None
    for candidate_date in sorted(by_candidate_date):
        group = _deduplicate_candidate_signals(by_candidate_date[candidate_date])
        if active is None:
            selected = _choose_initial_signal(group, ordered)
            if selected is not None:
                active = selected
                accepted.append((candidate_date, selected.move_uci))
            continue

        incumbent = _latest_signal_for_move(group, active.move_uci) or active
        challengers = [
            signal
            for signal in group
            if signal.move_uci != incumbent.move_uci
            and _compare_evidence(signal, incumbent, ordered) > 0
        ]
        same_move = _latest_signal_for_move(group, incumbent.move_uci)
        if same_move is not None:
            incumbent = same_move
        if not challengers:
            active = incumbent
            continue

        selected = _choose_replacement_signal(challengers, incumbent, ordered)
        if selected is not None:
            accepted.append((candidate_date, selected.move_uci))
            active = selected
        else:
            active = incumbent

    if not accepted:
        return _PositionInference((), _has_conflicting_evidence(qualifications))

    periods = [
        NormalizedPeriod(
            effective_from=start,
            effective_until=(
                accepted[index + 1][0] if index + 1 < len(accepted) else None
            ),
            preference=Preference.preferred_move(move_uci),
        )
        for index, (start, move_uci) in enumerate(accepted)
    ]
    return _PositionInference(
        normalize_periods(periods), _has_conflicting_evidence(qualifications)
    )


@dataclass(frozen=True, slots=True)
class _PositionInference:
    periods: tuple[NormalizedPeriod, ...]
    conflicting: bool


def _qualifications(
    observations: tuple[PreferredMoveObservation, ...],
) -> tuple[_Qualification, ...]:
    distinct_dates = sorted({observation.played_on for observation in observations})
    qualifications: list[_Qualification] = []
    for window_start in distinct_dates:
        window_end = window_start + timedelta(days=QUALIFICATION_WINDOW_DAYS)
        evidence = tuple(
            observation
            for observation in observations
            if window_start <= observation.played_on < window_end
        )
        counts = Counter(observation.move_uci for observation in evidence)
        for move_uci in sorted(counts):
            matching = counts[move_uci]
            total = len(evidence)
            if matching < MINIMUM_MATCHES or matching * 5 < total * 4:
                continue
            candidate_from = min(
                observation.played_on
                for observation in evidence
                if observation.move_uci == move_uci
            )
            qualifications.append(
                _Qualification(
                    evidence_from=window_start,
                    evidence_until=window_end,
                    candidate_from=candidate_from,
                    move_uci=move_uci,
                    matching_occurrences=matching,
                    eligible_occurrences=total,
                )
            )
    return tuple(
        sorted(
            qualifications,
            key=lambda item: (
                item.candidate_from,
                item.evidence_from,
                item.evidence_until,
                item.move_uci,
            ),
        )
    )


def _deduplicate_candidate_signals(
    signals: Iterable[_Qualification],
) -> tuple[_Qualification, ...]:
    earliest: dict[str, _Qualification] = {}
    for signal in sorted(
        signals,
        key=lambda item: (item.evidence_from, item.evidence_until, item.move_uci),
    ):
        earliest.setdefault(signal.move_uci, signal)
    return tuple(earliest.values())


def _latest_signal_for_move(
    signals: Iterable[_Qualification], move_uci: str
) -> _Qualification | None:
    matching = [signal for signal in signals if signal.move_uci == move_uci]
    if not matching:
        return None
    return max(matching, key=lambda item: (item.evidence_from, item.evidence_until))


def _choose_initial_signal(
    signals: tuple[_Qualification, ...],
    observations: tuple[PreferredMoveObservation, ...],
) -> _Qualification | None:
    if len(signals) == 1:
        return signals[0]

    winners = [
        candidate
        for candidate in signals
        if all(
            _compare_evidence(candidate, other, observations) > 0
            for other in signals
            if other.move_uci != candidate.move_uci
        )
    ]
    return winners[0] if len(winners) == 1 else None


def _choose_replacement_signal(
    challengers: list[_Qualification],
    incumbent: _Qualification,
    observations: tuple[PreferredMoveObservation, ...],
) -> _Qualification | None:
    selected = challengers[0]
    for candidate in challengers[1:]:
        if _compare_evidence(candidate, selected, observations) > 0:
            selected = candidate
    if _compare_evidence(selected, incumbent, observations) <= 0:
        return None
    return selected


def _has_conflicting_evidence(
    qualifications: tuple[_Qualification, ...],
) -> bool:
    for index, left in enumerate(qualifications):
        for right in qualifications[index + 1 :]:
            if left.move_uci == right.move_uci:
                continue
            if max(left.evidence_from, right.evidence_from) < min(
                left.evidence_until, right.evidence_until
            ):
                return True
    return False


def _compare_evidence(
    candidate: _Qualification,
    incumbent: _Qualification,
    observations: tuple[PreferredMoveObservation, ...],
) -> int:
    overlap_from = max(candidate.evidence_from, incumbent.evidence_from)
    overlap_until = min(candidate.evidence_until, incumbent.evidence_until)
    if overlap_from >= overlap_until:
        return 1

    candidate_uses = sum(
        observation.move_uci == candidate.move_uci
        and overlap_from <= observation.played_on < overlap_until
        for observation in observations
    )
    incumbent_uses = sum(
        observation.move_uci == incumbent.move_uci
        and overlap_from <= observation.played_on < overlap_until
        for observation in observations
    )
    return (candidate_uses > incumbent_uses) - (candidate_uses < incumbent_uses)


def _position_sort_key(position: CanonicalPosition) -> tuple[str, str, str, str]:
    return (
        position.placement,
        position.side_to_move,
        position.castling_rights,
        position.legal_en_passant,
    )


__all__ = [
    "MINIMUM_MATCHES",
    "QUALIFICATION_WINDOW_DAYS",
    "PreferredMoveInferenceResult",
    "PreferredMoveInferenceSummary",
    "PreferredMoveObservation",
    "infer_preferred_moves",
]
