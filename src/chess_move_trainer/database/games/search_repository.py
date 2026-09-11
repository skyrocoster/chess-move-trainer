"""Game search repository and loaders."""

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
from .search_errors import GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError
from .search_models import CoverageState, DeepestOpening, GameCoverage, GameSearchPage, GameSearchQuery, GameSearchSort, GameSummary, _GameData
from .search_filters import _compare_games, _coverage_state, _matches
from .search_validation import _normalize_fen, _opening_api_key, _optional_int, _optional_text, _parse_opening_key, _required_int, _required_text, _stored_position


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


