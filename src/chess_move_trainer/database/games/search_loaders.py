"""Row loaders used by the game search repository."""

from __future__ import annotations

from sqlalchemy import text

from .search_errors import GameSearchError, GameSearchStorageError
from .search_models import _GameData
from .search_validation import _optional_int, _optional_text, _required_int, _required_text


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
