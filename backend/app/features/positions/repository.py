import os
import re
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


class GameNotFoundError(Exception):
    """The requested game is not an accepted subject-corpus game."""


class CorpusUnavailableError(Exception):
    """The corpus cannot be opened or does not have the supported schema."""


class GameUnavailableError(Exception):
    """The accepted game's stored occurrences do not form a valid complete game."""


@dataclass(frozen=True)
class StoredGamePosition:
    ply: int
    fen: str
    san: str | None


@dataclass(frozen=True)
class StoredGame:
    game_uuid: UUID
    initial_ply: int
    subject_color: str
    source_url: str | None
    positions: tuple[StoredGamePosition, ...]


SAFE_SOURCE_URL = re.compile(r"https://www\.chess\.com/game/(?:live|daily)/[0-9]+")


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

    def get_game(self, game_uuid: UUID, initial_ply: int = 0) -> StoredGame:
        self._check_schema()
        game_row = self._get_accepted_game(game_uuid)
        if game_row is None:
            raise GameNotFoundError
        if game_row["stored_game_uuid"] is None:
            raise GameUnavailableError

        subject_color = self._subject_color(
            game_row["white_player_uuid"], game_row["black_player_uuid"]
        )
        rows = self._get_game_occurrences(game_uuid)
        if not rows:
            raise GameUnavailableError

        positions: list[StoredGamePosition] = []
        board: chess.Board | None = None
        for expected_ply, row in enumerate(rows):
            if row["ply"] != expected_ply:
                raise GameUnavailableError
            fen = self._build_game_fen(row)
            san = row["san"]
            if expected_ply == 0:
                if san is not None:
                    raise GameUnavailableError
                try:
                    board = chess.Board(fen)
                except (TypeError, ValueError) as error:
                    raise GameUnavailableError from error
            else:
                if board is None or not isinstance(san, str) or not san:
                    raise GameUnavailableError
                try:
                    move = board.parse_san(san)
                    if board.san(move) != san:
                        raise GameUnavailableError
                    board.push(move)
                except (TypeError, ValueError) as error:
                    raise GameUnavailableError from error
                if board.fen(en_passant="fen") != fen:
                    raise GameUnavailableError
            positions.append(StoredGamePosition(ply=expected_ply, fen=fen, san=san))

        if initial_ply >= len(positions):
            raise PositionNotFoundError

        return StoredGame(
            game_uuid=game_uuid,
            initial_ply=initial_ply,
            subject_color=subject_color,
            source_url=_safe_source_url(game_row["url"]),
            positions=tuple(positions),
        )

    def _get_accepted_game(self, game_uuid: UUID) -> sqlite3.Row | None:
        try:
            return self._connection.execute(
                """
                SELECT cg.game_uuid, g.uuid AS stored_game_uuid, g.url,
                       g.white_player_uuid, g.black_player_uuid
                FROM corpus AS c
                JOIN corpus_game AS cg ON cg.corpus_id = c.corpus_id
                LEFT JOIN games AS g ON g.uuid = cg.game_uuid
                WHERE c.subject_player_uuid = :s
                  AND cg.game_uuid = :game_uuid
                LIMIT 1
                """,
                {"game_uuid": str(game_uuid), "s": SUBJECT_PLAYER_UUID},
            ).fetchone()
        except sqlite3.Error as error:
            raise CorpusUnavailableError from error

    def _get_game_occurrences(self, game_uuid: UUID) -> list[sqlite3.Row]:
        try:
            return self._connection.execute(
                """
                SELECT o.game_uuid, o.ply, o.state_id, o.san,
                       o.halfmove_clock, o.fullmove_number,
                       s.placement, s.side_to_move, s.castling, s.en_passant
                FROM position_occurrence AS o
                LEFT JOIN position_state AS s ON s.state_id = o.state_id
                WHERE o.game_uuid = :game_uuid
                ORDER BY o.ply, o.occurrence_id
                """,
                {"game_uuid": str(game_uuid)},
            ).fetchall()
        except sqlite3.Error as error:
            raise CorpusUnavailableError from error

    @staticmethod
    def _subject_color(white_player_uuid: object, black_player_uuid: object) -> str:
        subject_is_white = white_player_uuid == SUBJECT_PLAYER_UUID
        subject_is_black = black_player_uuid == SUBJECT_PLAYER_UUID
        if subject_is_white == subject_is_black:
            raise GameUnavailableError
        return "white" if subject_is_white else "black"

    @classmethod
    def _build_game_fen(cls, row: sqlite3.Row) -> str:
        state_id = row["state_id"]
        if isinstance(state_id, bool) or not isinstance(state_id, int):
            raise GameUnavailableError
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
            raise GameUnavailableError

        fen = " ".join((*text_fields, str(halfmove_clock), str(fullmove_number)))
        if len(fen.split()) != 6:
            raise GameUnavailableError
        try:
            board = chess.Board(fen)
        except (TypeError, ValueError) as error:
            raise GameUnavailableError from error
        if not board.is_valid():
            raise GameUnavailableError
        return fen

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


def fetch_game(game_uuid: UUID, initial_ply: int = 0) -> StoredGame:
    connection = open_read_only_connection()
    try:
        return PositionRepository(connection).get_game(game_uuid, initial_ply)
    finally:
        connection.close()


def _safe_source_url(value: object) -> str | None:
    if not isinstance(value, str) or SAFE_SOURCE_URL.fullmatch(value) is None:
        return None
    return value
