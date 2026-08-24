"""Read-only accepted-game selection and exact-FEN eligibility inspection."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from uuid import UUID

import chess

from .errors import AnalysisValidationError
from .models import AnalysisProfile, ResultEligibility, canonical_fen
from .repository import AnalysisRepository
from .schema import require_analysis_schema

SUBJECT_PLAYER_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
QUALIFIED_NODE_BUDGET = 200_000


class GameSelectionError(RuntimeError):
    """An explicit game is not an accepted, complete stored game."""


@dataclass(frozen=True)
class SelectedOccurrence:
    game_uuid: str
    ply: int
    fen: str


@dataclass(frozen=True)
class SelectedPosition:
    fen: str
    occurrences: tuple[SelectedOccurrence, ...]

    @property
    def first_occurrence(self) -> SelectedOccurrence:
        return min(self.occurrences, key=lambda item: (item.ply, item.game_uuid))


@dataclass(frozen=True)
class SelectionReport:
    game_uuids: tuple[str, ...]
    positions: tuple[SelectedPosition, ...]
    already_done: int
    skipped_positions: int
    stale_positions: int
    missing_positions: int
    processable_fens: frozenset[str]

    @property
    def positions_to_process(self) -> tuple[SelectedPosition, ...]:
        return tuple(
            position for position in self.positions if position.fen in self.processable_fens
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "games": list(self.game_uuids),
            "selected_positions": len(self.positions),
            "already_done": self.already_done,
            "skipped_positions": self.skipped_positions,
            "stale_positions": self.stale_positions,
            "missing_positions": self.missing_positions,
        }


def _validated_uuid(value: str) -> str:
    try:
        return str(UUID(str(value)))
    except (AttributeError, ValueError, TypeError) as error:
        raise GameSelectionError(f"invalid game UUID: {value!r}") from error


def _accepted_game(connection: sqlite3.Connection, game_uuid: str) -> bool:
    try:
        row = connection.execute(
            """
            SELECT 1
            FROM corpus AS c
            JOIN corpus_game AS cg ON cg.corpus_id = c.corpus_id
            JOIN games AS g ON g.uuid = cg.game_uuid
            WHERE c.subject_player_uuid = ? AND cg.game_uuid = ?
            LIMIT 1
            """,
            (SUBJECT_PLAYER_UUID, game_uuid),
        ).fetchone()
    except sqlite3.Error as error:
        raise GameSelectionError(
            "corpus schema is unavailable for selected-game analysis"
        ) from error
    return row is not None


def _game_occurrences(
    connection: sqlite3.Connection, game_uuid: str
) -> tuple[SelectedOccurrence, ...]:
    try:
        rows = connection.execute(
            """
            SELECT o.ply, s.placement, s.side_to_move, s.castling, s.en_passant,
                   o.halfmove_clock, o.fullmove_number
            FROM position_occurrence AS o
            JOIN position_state AS s ON s.state_id = o.state_id
            WHERE o.game_uuid = ?
            ORDER BY o.ply, o.occurrence_id
            """,
            (game_uuid,),
        ).fetchall()
    except sqlite3.Error as error:
        raise GameSelectionError("stored game positions are unavailable") from error
    if not rows:
        raise GameSelectionError(f"accepted game {game_uuid} has no stored positions")

    occurrences: list[SelectedOccurrence] = []
    for expected_ply, row in enumerate(rows):
        ply = row[0]
        if isinstance(ply, bool) or not isinstance(ply, int) or ply != expected_ply:
            raise GameSelectionError(f"accepted game {game_uuid} has incomplete ply ordering")
        fields = row[1:5]
        halfmove, fullmove = row[5:7]
        if (
            not all(isinstance(value, str) for value in fields)
            or isinstance(halfmove, bool)
            or not isinstance(halfmove, int)
            or isinstance(fullmove, bool)
            or not isinstance(fullmove, int)
            or halfmove < 0
            or fullmove < 1
        ):
            raise GameSelectionError(f"accepted game {game_uuid} has invalid stored FEN fields")
        try:
            fen = canonical_fen(" ".join((*fields, str(halfmove), str(fullmove))))
            if not chess.Board(fen).is_valid():
                raise AnalysisValidationError("invalid board")
        except (AnalysisValidationError, ValueError, TypeError) as error:
            raise GameSelectionError(
                f"accepted game {game_uuid} has an invalid stored FEN"
            ) from error
        occurrences.append(SelectedOccurrence(game_uuid, ply, fen))
    return tuple(occurrences)


def select_positions(
    connection: sqlite3.Connection,
    game_uuids: list[str] | tuple[str, ...],
    profile: AnalysisProfile,
) -> SelectionReport:
    """Build one exact-FEN queue from every ply of explicit accepted games."""

    require_analysis_schema(connection)
    if profile.node_budget != QUALIFIED_NODE_BUDGET:
        raise AnalysisValidationError(
            f"selected-game analysis requires {QUALIFIED_NODE_BUDGET} nodes"
        )
    normalized = tuple(sorted({_validated_uuid(value) for value in game_uuids}))
    if not normalized:
        raise GameSelectionError("at least one accepted game UUID is required")

    for game_uuid in normalized:
        if not _accepted_game(connection, game_uuid):
            raise GameSelectionError(f"game is not an accepted subject-corpus game: {game_uuid}")
    return _select_positions(connection, normalized, profile)


def select_all_positions(
    connection: sqlite3.Connection, profile: AnalysisProfile
) -> SelectionReport:
    """Build the opening-first exact-FEN queue for the complete accepted subject corpus."""

    require_analysis_schema(connection)
    if profile.node_budget != QUALIFIED_NODE_BUDGET:
        raise AnalysisValidationError(
            f"corpus-wide analysis requires {QUALIFIED_NODE_BUDGET} nodes"
        )
    try:
        rows = connection.execute(
            """
            SELECT DISTINCT cg.game_uuid
            FROM corpus AS c
            JOIN corpus_game AS cg ON cg.corpus_id = c.corpus_id
            WHERE c.subject_player_uuid = ?
            ORDER BY cg.game_uuid
            """,
            (SUBJECT_PLAYER_UUID,),
        ).fetchall()
    except sqlite3.Error as error:
        raise GameSelectionError(
            "subject corpus is unavailable for corpus-wide analysis"
        ) from error
    normalized = tuple(sorted({_validated_uuid(str(row[0])) for row in rows}))
    if not normalized:
        raise GameSelectionError("subject corpus has no accepted games")
    return _select_positions(connection, normalized, profile)


def _select_positions(
    connection: sqlite3.Connection,
    normalized: tuple[str, ...],
    profile: AnalysisProfile,
) -> SelectionReport:
    by_fen: dict[str, list[SelectedOccurrence]] = {}
    for game_uuid in normalized:
        for occurrence in _game_occurrences(connection, game_uuid):
            by_fen.setdefault(occurrence.fen, []).append(occurrence)

    positions = tuple(
        SelectedPosition(
            fen,
            tuple(sorted(occurrences, key=lambda item: (item.ply, item.game_uuid))),
        )
        for fen, occurrences in sorted(
            by_fen.items(),
            key=lambda item: (min(entry.ply for entry in item[1]), item[0]),
        )
    )
    repository = AnalysisRepository(connection)
    states = repository.eligibilities(tuple(position.fen for position in positions), profile)
    already_done = sum(state is ResultEligibility.ELIGIBLE for state in states.values())
    stale = sum(state is ResultEligibility.STALE for state in states.values())
    missing = sum(state is ResultEligibility.MISSING for state in states.values())
    processable = frozenset(
        fen for fen, state in states.items() if state is not ResultEligibility.ELIGIBLE
    )
    return SelectionReport(
        normalized,
        positions,
        already_done=already_done,
        skipped_positions=already_done,
        stale_positions=stale,
        missing_positions=missing,
        processable_fens=processable,
    )


def work_positions(
    connection: sqlite3.Connection,
    report: SelectionReport,
    profile: AnalysisProfile,
) -> tuple[SelectedPosition, ...]:
    """Recheck current eligibility immediately before dispatching work."""

    repository = AnalysisRepository(connection)
    states = repository.eligibilities(tuple(position.fen for position in report.positions), profile)
    return tuple(
        position
        for position in report.positions
        if states[position.fen] is not ResultEligibility.ELIGIBLE
    )
