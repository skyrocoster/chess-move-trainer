import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import chess

DEFAULT_DATABASE_PATH = Path("data/database/chess_games.db")
DATABASE_PATH_ENV = "CHESS_DATABASE_PATH"
SUBJECT_PLAYER_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"


class PositionNotFoundError(Exception):
    """The requested game occurrence is not in the subject corpus."""


class CorpusUnavailableError(Exception):
    """The corpus cannot be opened or does not have the supported schema."""


class StoredPositionInvalidError(Exception):
    """The corpus occurrence does not satisfy the stored-position contract."""


@dataclass(frozen=True)
class StoredPosition:
    game_uuid: UUID
    ply: int
    fen: str
    subject_color: str


def database_path() -> Path:
    return Path(os.environ.get(DATABASE_PATH_ENV, str(DEFAULT_DATABASE_PATH)))


def open_read_only_connection(path: Path | None = None) -> sqlite3.Connection:
    selected_path = (path or database_path()).expanduser().resolve()
    uri = f"{selected_path.as_uri()}?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as error:
        raise CorpusUnavailableError from error
    connection.row_factory = sqlite3.Row
    return connection


class PositionRepository:
    """Read position occurrences from an already-open read-only connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_position(self, game_uuid: UUID, ply: int) -> StoredPosition:
        self._check_schema()
        try:
            row = self._connection.execute(
                """
                SELECT o.game_uuid, o.ply, o.halfmove_clock, o.fullmove_number,
                       s.placement, s.side_to_move, s.castling, s.en_passant,
                       g.white_player_uuid, g.black_player_uuid,
                       c.subject_player_uuid
                FROM position_occurrence AS o
                JOIN position_state AS s ON s.state_id = o.state_id
                JOIN corpus_game AS cg ON cg.game_uuid = o.game_uuid
                JOIN corpus AS c ON c.corpus_id = cg.corpus_id
                JOIN games AS g ON g.uuid = o.game_uuid
                WHERE o.game_uuid = :game_uuid
                  AND o.ply = :ply
                  AND c.subject_player_uuid = :s
                LIMIT 1
                """,
                {
                    "game_uuid": str(game_uuid),
                    "ply": ply,
                    "s": SUBJECT_PLAYER_UUID,
                },
            ).fetchone()
        except sqlite3.Error as error:
            raise CorpusUnavailableError from error

        if row is None:
            raise PositionNotFoundError

        return self._build_position(row, game_uuid, ply)

    def _check_schema(self) -> None:
        try:
            row = self._connection.execute(
                "SELECT version FROM corpus_schema WHERE id = 1"
            ).fetchone()
        except sqlite3.Error as error:
            raise CorpusUnavailableError from error

        if row is None:
            raise CorpusUnavailableError
        try:
            version = int(row["version"])
        except (KeyError, TypeError, ValueError) as error:
            raise CorpusUnavailableError from error
        if version != 1:
            raise CorpusUnavailableError

    @staticmethod
    def _build_position(row: sqlite3.Row, game_uuid: UUID, ply: int) -> StoredPosition:
        subject_is_white = row["white_player_uuid"] == SUBJECT_PLAYER_UUID
        subject_is_black = row["black_player_uuid"] == SUBJECT_PLAYER_UUID
        if subject_is_white == subject_is_black:
            raise StoredPositionInvalidError
        subject_color = "white" if subject_is_white else "black"

        text_fields = tuple(
            row[field] for field in ("placement", "side_to_move", "castling", "en_passant")
        )
        halfmove_clock = row["halfmove_clock"]
        fullmove_number = row["fullmove_number"]
        if (
            not all(isinstance(value, str) for value in text_fields)
            or isinstance(halfmove_clock, bool)
            or not isinstance(halfmove_clock, int)
            or isinstance(fullmove_number, bool)
            or not isinstance(fullmove_number, int)
            or halfmove_clock < 0
            or fullmove_number < 1
        ):
            raise StoredPositionInvalidError

        fen = " ".join((*text_fields, str(halfmove_clock), str(fullmove_number)))
        if len(fen.split()) != 6:
            raise StoredPositionInvalidError
        try:
            board = chess.Board(fen)
        except (TypeError, ValueError) as error:
            raise StoredPositionInvalidError from error
        if not board.is_valid():
            raise StoredPositionInvalidError

        return StoredPosition(
            game_uuid=game_uuid,
            ply=ply,
            fen=fen,
            subject_color=subject_color,
        )


def fetch_position(game_uuid: UUID, ply: int) -> StoredPosition:
    connection = open_read_only_connection()
    try:
        return PositionRepository(connection).get_position(game_uuid, ply)
    finally:
        connection.close()
