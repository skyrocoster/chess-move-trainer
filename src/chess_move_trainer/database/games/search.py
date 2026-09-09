"""Read-only, explicit-path search over normalized schema-v1 games."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cmp_to_key
from pathlib import Path
from typing import Literal

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..openings.keys import OpeningKeyError, opening_api_key, parse_opening_api_key
from ..positions import CanonicalPosition, PositionValidationError, canonicalize_fen
from ..schema import SchemaIncompatibleError, _assert_compatible_schema


TrainerColor = Literal["white", "black"]
TrainerOutcome = Literal["win", "loss", "draw"]
OpeningMatch = Literal["reached", "deepest"]
CoverageState = Literal["none", "partial", "complete"]
GameSearchSort = Literal[
    "started_at_desc",
    "started_at_asc",
    "length_desc",
    "length_asc",
    "trainer_rating_desc",
    "trainer_rating_asc",
    "opponent_rating_desc",
    "opponent_rating_asc",
    "opponent_uuid_asc",
    "opponent_uuid_desc",
    "game_uuid_asc",
    "game_uuid_desc",
]

_SORTS: tuple[GameSearchSort, ...] = (
    "started_at_desc",
    "started_at_asc",
    "length_desc",
    "length_asc",
    "trainer_rating_desc",
    "trainer_rating_asc",
    "opponent_rating_desc",
    "opponent_rating_asc",
    "opponent_uuid_asc",
    "opponent_uuid_desc",
    "game_uuid_asc",
    "game_uuid_desc",
)
_TIME_CLASSES = ("bullet", "blitz", "rapid", "daily")
_COVERAGE_STATES = ("none", "partial", "complete")
_RFC3339 = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    r"[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})\Z"
)
class GameSearchError(Exception):
    """Base class for bounded game-search failures."""


class GameSearchValidationError(GameSearchError, ValueError):
    """Raised when a game-search query is invalid."""


class GameSearchSchemaError(GameSearchError, RuntimeError):
    """Raised when the selected database is not exactly schema v1."""


class GameSearchStorageError(GameSearchError, RuntimeError):
    """Raised when a compatible game database cannot be read safely."""


@dataclass(frozen=True, slots=True)
class GameSearchQuery:
    """All approved collection filters and pagination controls."""

    page: int = 1
    page_size: int = 50
    started_at_from: str | datetime | None = None
    started_at_to: str | datetime | None = None
    ended_at_from: str | datetime | None = None
    ended_at_to: str | datetime | None = None
    trainer_color: TrainerColor | None = None
    trainer_outcome: TrainerOutcome | None = None
    termination_reason: str | None = None
    trainer_rating_min: int | None = None
    trainer_rating_max: int | None = None
    opponent_rating_min: int | None = None
    opponent_rating_max: int | None = None
    opponent_chesscom_uuid: str | None = None
    time_class: str | None = None
    time_control: str | None = None
    opening_key: str | None = None
    opening_match: OpeningMatch | None = None
    contains_fen: str | None = None
    move_fen: str | None = None
    move_uci: str | None = None
    min_length_plies: int | None = None
    max_length_plies: int | None = None
    analysis_coverage: CoverageState | None = None
    preferred_coverage: CoverageState | None = None
    sort: GameSearchSort = "started_at_desc"

    def __post_init__(self) -> None:
        _require_positive_int(self.page, "page")
        if type(self.page_size) is not int or not 1 <= self.page_size <= 100:
            raise GameSearchValidationError("page_size must be an integer from 1 through 100")

        for field_name, value, accepted in (
            ("trainer_color", self.trainer_color, ("white", "black")),
            ("trainer_outcome", self.trainer_outcome, ("win", "loss", "draw")),
            ("opening_match", self.opening_match, ("reached", "deepest")),
            ("analysis_coverage", self.analysis_coverage, _COVERAGE_STATES),
            ("preferred_coverage", self.preferred_coverage, _COVERAGE_STATES),
        ):
            if value is not None and value not in accepted:
                raise GameSearchValidationError(f"{field_name} has an unsupported value")
        if self.sort not in _SORTS:
            raise GameSearchValidationError("sort has an unsupported value")

        dates = (
            ("started_at_from", self.started_at_from),
            ("started_at_to", self.started_at_to),
            ("ended_at_from", self.ended_at_from),
            ("ended_at_to", self.ended_at_to),
        )
        normalized_dates = {
            field_name: _normalize_timestamp(value, field_name)
            for field_name, value in dates
        }
        _require_ordered_bounds(
            normalized_dates["started_at_from"],
            normalized_dates["started_at_to"],
            "started_at",
        )
        _require_ordered_bounds(
            normalized_dates["ended_at_from"],
            normalized_dates["ended_at_to"],
            "ended_at",
        )
        for field_name, value in normalized_dates.items():
            object.__setattr__(self, field_name, value)

        if self.termination_reason is not None:
            if type(self.termination_reason) is not str or not self.termination_reason.strip():
                raise GameSearchValidationError("termination_reason must be non-empty")
            object.__setattr__(self, "termination_reason", self.termination_reason.strip().casefold())
        _validate_optional_non_empty_text(self.opponent_chesscom_uuid, "opponent_chesscom_uuid")
        _validate_optional_non_empty_text(self.time_control, "time_control")
        if self.time_class is not None and (
            type(self.time_class) is not str or self.time_class not in _TIME_CLASSES
        ):
            raise GameSearchValidationError("time_class has an unsupported value")

        for field_name in (
            "trainer_rating_min",
            "trainer_rating_max",
            "opponent_rating_min",
            "opponent_rating_max",
        ):
            _require_optional_non_negative_int(getattr(self, field_name), field_name)
        _require_ordered_bounds(
            self.trainer_rating_min, self.trainer_rating_max, "trainer_rating"
        )
        _require_ordered_bounds(
            self.opponent_rating_min, self.opponent_rating_max, "opponent_rating"
        )

        if self.opening_key is None:
            if self.opening_match is not None:
                raise GameSearchValidationError(
                    "opening_match requires opening_key"
                )
        else:
            try:
                _parse_opening_key(self.opening_key)
            except ValueError as error:
                raise GameSearchValidationError(str(error)) from error
            if self.opening_match is None:
                raise GameSearchValidationError(
                    "opening_key requires opening_match"
                )

        contains_position = _normalize_fen(self.contains_fen, "contains_fen")
        move_position = _normalize_fen(self.move_fen, "move_fen")
        if (move_position is None) != (self.move_uci is None):
            raise GameSearchValidationError("move_fen and move_uci must be supplied together")
        if move_position is not None:
            assert self.move_uci is not None
            _validate_legal_move(move_position, self.move_uci)
        object.__setattr__(self, "contains_fen", contains_position)
        object.__setattr__(self, "move_fen", move_position)

        for field_name in ("min_length_plies", "max_length_plies"):
            _require_optional_non_negative_int(getattr(self, field_name), field_name)
        _require_ordered_bounds(
            self.min_length_plies, self.max_length_plies, "length_plies"
        )


@dataclass(frozen=True, slots=True)
class DeepestOpening:
    """The selected deepest opening classification for a game."""

    key: str
    eco: str
    name: str
    ply: int


@dataclass(frozen=True, slots=True)
class GameCoverage:
    """Analysis and preferred-move coverage over distinct game positions."""

    distinct_position_count: int
    analyzed_position_count: int
    preferred_position_count: int
    analysis_coverage: CoverageState
    preferred_coverage: CoverageState


@dataclass(frozen=True, slots=True)
class GameSummary:
    """A public game summary that deliberately contains no SQLite identifiers."""

    game_uuid: str
    source_url: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: str
    opponent_chesscom_uuid: str | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control: str | None
    time_class: str | None
    occurrence_count: int
    length_plies: int
    deepest_opening: DeepestOpening | None
    coverage: GameCoverage


@dataclass(frozen=True, slots=True)
class GameSearchPage:
    """One finite, deterministic page of public game summaries."""

    items: tuple[GameSummary, ...]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool


@dataclass(slots=True)
class _GameData:
    game_uuid: str
    source_url: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: str
    opponent_chesscom_uuid: str | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control: str | None
    time_class: str | None
    occurrences: list[tuple[int, int, str | None, CanonicalPosition]]
    opening_matches: dict[str, tuple[str, str, int]]

    @property
    def occurrence_count(self) -> int:
        return len(self.occurrences)

    @property
    def length_plies(self) -> int:
        return max((item[0] for item in self.occurrences), default=0)


class GameSearchRepository:
    """Search normalized games using one explicit read-only schema-v1 path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = Path(database_path)
        self._lock_timeout = lock_timeout

    def search(self, query: GameSearchQuery | None = None) -> GameSearchPage:
        """Return the finite page matching every supplied query filter."""

        request = GameSearchQuery() if query is None else query
        if not isinstance(request, GameSearchQuery):
            raise GameSearchValidationError("query must be a GameSearchQuery")
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                games = _load_games(connection)
                _load_occurrences(connection, games)
                _load_openings(connection, games)
                analyzed_positions = _load_position_ids(
                    connection,
                    "SELECT derived_position_id FROM derived_analysis_result",
                )
                preferred_positions = _load_position_ids(
                    connection,
                    "SELECT DISTINCT derived_position_id FROM datasource_preferred_move_period",
                )
        except SchemaIncompatibleError as error:
            raise GameSearchSchemaError(str(error)) from error
        except GameSearchError:
            raise
        except Exception as error:
            raise GameSearchStorageError("games could not be read") from error

        summaries = [
            _summarize(game, analyzed_positions, preferred_positions)
            for game in games.values()
        ]
        matched = [
            (game, summary)
            for game, summary in zip(games.values(), summaries, strict=True)
            if _matches(game, summary, request)
        ]
        matched.sort(key=cmp_to_key(lambda left, right: _compare_games(left[1], right[1], request.sort)))

        total = len(matched)
        total_pages = math.ceil(total / request.page_size)
        start = (request.page - 1) * request.page_size
        page_items = tuple(summary for _game, summary in matched[start : start + request.page_size])
        return GameSearchPage(
            items=page_items,
            page=request.page,
            page_size=request.page_size,
            total=total,
            total_pages=total_pages,
            has_next=request.page < total_pages,
        )

    read = search
    query = search


def search_games(
    database_path: str | Path,
    query: GameSearchQuery | None = None,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> GameSearchPage:
    """Search one explicit database path without exposing a connection handle."""

    return GameSearchRepository(database_path, lock_timeout=lock_timeout).search(query)


def _load_games(connection: object) -> dict[int, _GameData]:
    rows = connection.execute(
        text(
            """
            SELECT dg_game_id, dg_chesscom_game_uuid, dg_source_url,
                   dg_trainer_color, dg_trainer_chesscom_uuid,
                   dg_opponent_chesscom_uuid, dg_trainer_rating,
                   dg_opponent_rating, dg_started_at_utc, dg_ended_at_utc,
                   dg_trainer_outcome, dg_termination_reason,
                   dg_time_control_source, dg_time_class
            FROM datasource_game
            ORDER BY dg_game_id
            """
        )
    ).all()
    games: dict[int, _GameData] = {}
    try:
        for row in rows:
            game_id = _required_int(row[0], "game id")
            if game_id in games:
                raise GameSearchStorageError("game identifiers are duplicated")
            trainer_color = row[3]
            if trainer_color not in ("white", "black"):
                raise ValueError("trainer color")
            outcome = row[10]
            if outcome is not None and outcome not in ("win", "loss", "draw"):
                raise ValueError("trainer outcome")
            games[game_id] = _GameData(
                game_uuid=_required_text(row[1], "game UUID"),
                source_url=_required_text(row[2], "source URL"),
                trainer_color=trainer_color,
                trainer_chesscom_uuid=_required_text(row[4], "trainer UUID"),
                opponent_chesscom_uuid=_optional_text(row[5]),
                trainer_rating=_optional_int(row[6]),
                opponent_rating=_optional_int(row[7]),
                started_at_utc=_optional_text(row[8]),
                ended_at_utc=_optional_text(row[9]),
                trainer_outcome=outcome,
                termination_reason=_optional_text(row[11]),
                time_control=_optional_text(row[12]),
                time_class=_optional_text(row[13]),
                occurrences=[],
                opening_matches={},
            )
    except GameSearchError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise GameSearchStorageError("game row is malformed") from error
    return games


def _load_occurrences(connection: object, games: dict[int, _GameData]) -> None:
    rows = connection.execute(
        text(
            """
            SELECT o.datasource_game_id, o.dgp_ply, o.derived_position_id,
                   o.dgp_move_uci, p.dp_placement, p.dp_side_to_move,
                   p.dp_castling_rights, p.dp_legal_en_passant
            FROM derived_game_position AS o
            JOIN derived_position AS p
              ON p.dp_position_id = o.derived_position_id
            ORDER BY o.datasource_game_id, o.dgp_ply
            """
        )
    ).all()
    try:
        for row in rows:
            game_id = _required_int(row[0], "occurrence game id")
            game = games.get(game_id)
            if game is None:
                raise ValueError("occurrence references an unknown game")
            ply = _required_int(row[1], "occurrence ply")
            position_id = _required_int(row[2], "occurrence position id")
            move_uci = _optional_text(row[3])
            position = _stored_position(row[4:8])
            game.occurrences.append((ply, position_id, move_uci, position))
    except GameSearchError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise GameSearchStorageError("game occurrence row is malformed") from error


def _load_openings(connection: object, games: dict[int, _GameData]) -> None:
    rows = connection.execute(
        text(
            """
            SELECT g.datasource_game_id, g.dgp_ply, o.do_eco, o.do_name
            FROM derived_game_position AS g
            JOIN derived_opening_route AS r
              ON r.derived_position_id = g.derived_position_id
            JOIN datasource_opening AS o
              ON o.do_opening_id = r.datasource_opening_id
            ORDER BY g.datasource_game_id, g.dgp_ply, o.do_eco, o.do_name
            """
        )
    ).all()
    try:
        for row in rows:
            game = games.get(_required_int(row[0], "opening game id"))
            if game is None:
                raise ValueError("opening occurrence references an unknown game")
            ply = _required_int(row[1], "opening ply")
            eco = _required_text(row[2], "opening ECO")
            name = _required_text(row[3], "opening name")
            key = _opening_api_key(eco, name)
            prior = game.opening_matches.get(key)
            if prior is None or ply > prior[2]:
                game.opening_matches[key] = (eco, name, ply)
    except GameSearchError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise GameSearchStorageError("opening row is malformed") from error


def _load_position_ids(connection: object, statement: str) -> set[int]:
    try:
        return {_required_int(row[0], "position id") for row in connection.execute(text(statement)).all()}
    except GameSearchError:
        raise
    except (IndexError, TypeError, ValueError) as error:
        raise GameSearchStorageError("coverage row is malformed") from error


def _summarize(
    game: _GameData,
    analyzed_positions: set[int],
    preferred_positions: set[int],
) -> GameSummary:
    distinct_positions = {occurrence[3] for occurrence in game.occurrences}
    distinct_position_ids = {occurrence[1] for occurrence in game.occurrences}
    analyzed_count = len(distinct_position_ids & analyzed_positions)
    preferred_count = len(distinct_position_ids & preferred_positions)
    deepest = None
    if game.opening_matches:
        key, (eco, name, ply) = min(
            game.opening_matches.items(), key=lambda item: (-item[1][2], item[0])
        )
        deepest = DeepestOpening(key=key, eco=eco, name=name, ply=ply)
    return GameSummary(
        game_uuid=game.game_uuid,
        source_url=game.source_url,
        trainer_color=game.trainer_color,
        trainer_chesscom_uuid=game.trainer_chesscom_uuid,
        opponent_chesscom_uuid=game.opponent_chesscom_uuid,
        trainer_rating=game.trainer_rating,
        opponent_rating=game.opponent_rating,
        started_at_utc=game.started_at_utc,
        ended_at_utc=game.ended_at_utc,
        trainer_outcome=game.trainer_outcome,
        termination_reason=game.termination_reason,
        time_control=game.time_control,
        time_class=game.time_class,
        occurrence_count=game.occurrence_count,
        length_plies=game.length_plies,
        deepest_opening=deepest,
        coverage=GameCoverage(
            distinct_position_count=len(distinct_positions),
            analyzed_position_count=analyzed_count,
            preferred_position_count=preferred_count,
            analysis_coverage=_coverage_state(len(distinct_positions), analyzed_count),
            preferred_coverage=_coverage_state(len(distinct_positions), preferred_count),
        ),
    )


def _matches(game: _GameData, summary: GameSummary, query: GameSearchQuery) -> bool:
    if not _in_datetime_bounds(game.started_at_utc, query.started_at_from, query.started_at_to):
        return False
    if not _in_datetime_bounds(game.ended_at_utc, query.ended_at_from, query.ended_at_to):
        return False
    if query.trainer_color is not None and game.trainer_color != query.trainer_color:
        return False
    if query.trainer_outcome is not None and game.trainer_outcome != query.trainer_outcome:
        return False
    if query.termination_reason is not None and (
        game.termination_reason is None
        or game.termination_reason.strip().casefold() != query.termination_reason
    ):
        return False
    if not _in_numeric_bounds(game.trainer_rating, query.trainer_rating_min, query.trainer_rating_max):
        return False
    if not _in_numeric_bounds(game.opponent_rating, query.opponent_rating_min, query.opponent_rating_max):
        return False
    if query.opponent_chesscom_uuid is not None and game.opponent_chesscom_uuid != query.opponent_chesscom_uuid:
        return False
    if query.time_class is not None and game.time_class != query.time_class:
        return False
    if query.time_control is not None and game.time_control != query.time_control:
        return False
    if query.opening_key is not None:
        assert query.opening_match is not None
        if query.opening_match == "reached":
            if query.opening_key not in game.opening_matches:
                return False
        elif summary.deepest_opening is None or summary.deepest_opening.key != query.opening_key:
            return False
    if query.contains_fen is not None:
        expected = canonicalize_fen(query.contains_fen)
        if not any(occurrence[3] == expected for occurrence in game.occurrences):
            return False
    if query.move_fen is not None:
        expected = canonicalize_fen(query.move_fen)
        if not any(
            occurrence[3] == expected and occurrence[2] == query.move_uci
            for occurrence in game.occurrences
        ):
            return False
    if query.min_length_plies is not None and summary.length_plies < query.min_length_plies:
        return False
    if query.max_length_plies is not None and summary.length_plies > query.max_length_plies:
        return False
    if query.analysis_coverage is not None and summary.coverage.analysis_coverage != query.analysis_coverage:
        return False
    if query.preferred_coverage is not None and summary.coverage.preferred_coverage != query.preferred_coverage:
        return False
    return True


def _compare_games(left: GameSummary, right: GameSummary, sort: GameSearchSort) -> int:
    if sort.startswith("started_at_"):
        field = "started_at_utc"
    elif sort.startswith("length_"):
        field = "length_plies"
    elif sort.startswith("trainer_rating_"):
        field = "trainer_rating"
    elif sort.startswith("opponent_rating_"):
        field = "opponent_rating"
    elif sort.startswith("opponent_uuid_"):
        field = "opponent_chesscom_uuid"
    else:
        field = "game_uuid"
    descending = sort.endswith("_desc")
    result = _compare_nullable(getattr(left, field), getattr(right, field), descending)
    if result:
        return result
    if field != "game_uuid":
        return _compare_nullable(left.game_uuid, right.game_uuid, False)
    return 0


def _compare_nullable(left: object, right: object, descending: bool) -> int:
    if left is None:
        return 0 if right is None else 1
    if right is None:
        return -1
    result = (left > right) - (left < right)
    return -result if descending else result


def _coverage_state(distinct_count: int, covered_count: int) -> CoverageState:
    if covered_count == 0:
        return "none"
    if covered_count == distinct_count:
        return "complete"
    return "partial"


def _stored_position(fields: object) -> CanonicalPosition:
    try:
        values = tuple(fields)
        if len(values) != 4 or any(not isinstance(value, str) for value in values):
            raise ValueError("position fields")
        position = canonicalize_fen(" ".join((*values, "0", "1")))
        if position != CanonicalPosition(*values):
            raise ValueError("position is not canonical")
        return position
    except (TypeError, ValueError, PositionValidationError) as error:
        raise GameSearchStorageError("stored position is not canonical") from error


def _normalize_fen(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise GameSearchValidationError(f"{field_name} must be a complete legal FEN")
    try:
        position = canonicalize_fen(value)
    except (PositionValidationError, ValueError) as error:
        raise GameSearchValidationError(f"{field_name} is not a valid FEN") from error
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


def _validate_legal_move(position_fen: str, move_uci: str) -> None:
    if type(move_uci) is not str:
        raise GameSearchValidationError("move_uci must be a legal UCI move")
    try:
        board = chess.Board(position_fen)
        move = chess.Move.from_uci(move_uci)
    except (TypeError, ValueError) as error:
        raise GameSearchValidationError("move_uci must be a legal UCI move") from error
    if move.uci() != move_uci or move not in board.legal_moves:
        raise GameSearchValidationError("move_uci must be legal from move_fen")


def _normalize_timestamp(value: str | datetime | None, field_name: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif type(value) is str and _RFC3339.fullmatch(value):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise GameSearchValidationError(f"{field_name} must be RFC3339 UTC") from error
    else:
        raise GameSearchValidationError(f"{field_name} must be RFC3339 UTC")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise GameSearchValidationError(f"{field_name} must include a UTC offset")
    return parsed.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _in_datetime_bounds(value: str | None, lower: str | None, upper: str | None) -> bool:
    if lower is None and upper is None:
        return True
    if value is None:
        return False
    normalized = _stored_timestamp(value)
    return (lower is None or normalized >= lower) and (upper is None or normalized <= upper)


def _stored_timestamp(value: str) -> str:
    if value.endswith("Z"):
        return value[:-1] + ".000000Z" if "." not in value else value
    return value


def _in_numeric_bounds(value: int | None, lower: int | None, upper: int | None) -> bool:
    if lower is None and upper is None:
        return True
    if value is None:
        return False
    return (lower is None or value >= lower) and (upper is None or value <= upper)


def _require_positive_int(value: object, field_name: str) -> None:
    if type(value) is not int or value < 1:
        raise GameSearchValidationError(f"{field_name} must be a positive integer")


def _require_optional_non_negative_int(value: object, field_name: str) -> None:
    if value is not None and (type(value) is not int or value < 0):
        raise GameSearchValidationError(f"{field_name} must be a non-negative integer")


def _require_ordered_bounds(lower: object, upper: object, field_name: str) -> None:
    if lower is not None and upper is not None and lower > upper:
        raise GameSearchValidationError(f"{field_name} lower bound cannot exceed upper bound")


def _validate_optional_non_empty_text(value: object, field_name: str) -> None:
    if value is not None and (type(value) is not str or not value):
        raise GameSearchValidationError(f"{field_name} must be a non-empty string")


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _opening_api_key(eco: str, name: str) -> str:
    try:
        return opening_api_key(eco, name)
    except OpeningKeyError as error:
        raise ValueError("opening label is malformed") from error


def _parse_opening_key(value: str) -> tuple[str, str]:
    try:
        return parse_opening_api_key(value)
    except OpeningKeyError as error:
        raise ValueError("opening_key must be formatted as ECO:Name") from error


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional text value is malformed")
    return value


def _required_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{field_name} must be an integer")
    return value


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if type(value) is not int:
        raise ValueError("optional integer value is malformed")
    return value


__all__ = [
    "CoverageState",
    "DeepestOpening",
    "GameCoverage",
    "GameSearchError",
    "GameSearchPage",
    "GameSearchQuery",
    "GameSearchRepository",
    "GameSearchSchemaError",
    "GameSearchSort",
    "GameSearchStorageError",
    "GameSearchValidationError",
    "GameSummary",
    "OpeningMatch",
    "search_games",
]
