"""Strict, storage-independent normalization of opening source routes."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path

import chess
import chess.pgn

from ..positions import CanonicalPosition, canonicalize_fen


EXPECTED_SOURCE_FILES = ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")
SOURCE_FIELDS = ("eco", "name", "pgn")
_ECO_PATTERN = re.compile(r"[A-E][0-9]{2}\Z")
_UCI_PATTERN = re.compile(r"[a-h][1-8][a-h][1-8][qrbn]?\Z")
_MOVE_NUMBER_PATTERN = re.compile(r"(?:[0-9]+\.(?:\.\.)?|\.\.\.)\Z")
_RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}
_SAN_PATTERN = re.compile(
    r"(?:"
    r"(?:O-O(?:-O)?|0-0(?:-0)?)[+#]{0,2}"
    r"|"
    r"(?:"
    r"[KQRBN][a-h1-8]{0,2}x?[a-h][1-8]"
    r"|"
    r"[a-h](?:x[a-h])?[1-8]"
    r")(?:=[QRBN])?[+#]{0,2}"
    r")(?:[!?]{1,2})?\Z"
)


class OpeningSourceError(ValueError):
    """Raised when the complete five-file opening source cannot be accepted."""


@dataclass(frozen=True, slots=True)
class OpeningRouteSource:
    """One immutable, legally replayed opening route."""

    eco: str
    name: str
    moves_uci: tuple[str, ...]
    endpoint_fen: str

    def __post_init__(self) -> None:
        if type(self.eco) is not str or _ECO_PATTERN.fullmatch(self.eco) is None:
            raise ValueError("eco must be an uppercase ECO code from A00 through E99")
        if type(self.name) is not str:
            raise ValueError("name must be a string")
        if type(self.moves_uci) is not tuple or not self.moves_uci:
            raise ValueError("moves_uci must be a non-empty tuple")
        if any(type(move) is not str or _UCI_PATTERN.fullmatch(move) is None for move in self.moves_uci):
            raise ValueError("moves_uci must contain valid UCI moves")
        if type(self.endpoint_fen) is not str:
            raise ValueError("endpoint_fen must be a complete FEN string")
        try:
            canonicalize_fen(self.endpoint_fen)
        except ValueError as error:
            raise ValueError("endpoint_fen must be a valid chess position") from error

    @property
    def endpoint_position(self) -> CanonicalPosition:
        """Return the immutable four-field identity of the final position."""

        return canonicalize_fen(self.endpoint_fen)

    @property
    def endpoint(self) -> CanonicalPosition:
        """Alias for the immutable final-position identity."""

        return self.endpoint_position

    @property
    def endpoint_key(self) -> tuple[str, str, str, str]:
        """Return the canonical endpoint fields used by storage."""

        position = self.endpoint_position
        return (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
        )


class _ErrorCollectingGameBuilder(chess.pgn.GameBuilder):
    def handle_error(self, error: Exception) -> None:
        self.game.errors.append(error)


def load_opening_sources(source_dir: str | Path) -> tuple[OpeningRouteSource, ...]:
    """Validate, replay, and semantically deduplicate a complete source batch."""

    try:
        root = Path(source_dir)
    except (TypeError, ValueError) as error:
        raise OpeningSourceError("source directory must be a readable directory") from error

    try:
        if not root.is_dir():
            raise OpeningSourceError("source directory must be a readable directory")
        entries = tuple(root.iterdir())
    except OpeningSourceError:
        raise
    except OSError as error:
        raise OpeningSourceError("source directory must be a readable directory") from error

    try:
        source_names = tuple(
            sorted(
                entry.name
                for entry in entries
                if entry.is_file() and entry.suffix.lower() == ".tsv"
            )
        )
    except OSError as error:
        raise OpeningSourceError("source directory contains an unreadable entry") from error
    if source_names != EXPECTED_SOURCE_FILES:
        raise OpeningSourceError(
            f"expected exactly {EXPECTED_SOURCE_FILES}, found {source_names}"
        )

    routes: dict[tuple[str, str, tuple[str, ...]], OpeningRouteSource] = {}
    for source_name in EXPECTED_SOURCE_FILES:
        path = root / source_name
        for row_number, eco, name, pgn in _read_source_rows(path, source_name):
            route = _replay_source_row(source_name, row_number, eco, name, pgn)
            identity = (route.eco, route.name, route.moves_uci)
            routes[identity] = route

    return tuple(routes[key] for key in sorted(routes))


def _read_source_rows(
    path: Path, source_name: str
) -> tuple[tuple[int, str, str, str], ...]:
    rows: list[tuple[int, str, str, str]] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream, delimiter="\t", strict=True)
            try:
                header = next(reader)
            except StopIteration as error:
                raise OpeningSourceError(f"{source_name}: missing header") from error
            if tuple(header) != SOURCE_FIELDS:
                raise OpeningSourceError(
                    f"{source_name}: expected exact fields {SOURCE_FIELDS}, found {tuple(header)}"
                )

            for row in reader:
                row_number = reader.line_num
                if len(row) != len(SOURCE_FIELDS):
                    raise OpeningSourceError(
                        f"{source_name} row {row_number}: expected exactly three fields"
                    )
                eco, name, pgn = row
                if _ECO_PATTERN.fullmatch(eco) is None:
                    raise OpeningSourceError(
                        f"{source_name} row {row_number}: invalid ECO"
                    )
                if not pgn.strip():
                    raise OpeningSourceError(
                        f"{source_name} row {row_number}: move text is empty"
                    )
                rows.append((row_number, eco, name, pgn))
    except OpeningSourceError:
        raise
    except (OSError, UnicodeError, csv.Error) as error:
        raise OpeningSourceError(f"{source_name}: malformed or unreadable TSV") from error
    return tuple(rows)


def _replay_source_row(
    source_name: str, row_number: int, eco: str, name: str, pgn: str
) -> OpeningRouteSource:
    try:
        game = _read_one_game(pgn)
        board = game.board()
        if board.fen(en_passant="fen") != chess.STARTING_FEN:
            raise ValueError("PGN must use the standard initial position")

        moves_uci: list[str] = []
        for ply, move in enumerate(game.mainline_moves(), start=1):
            if move not in board.legal_moves:
                raise ValueError(f"illegal move at ply {ply}")
            moves_uci.append(move.uci())
            board.push(move)
        if not moves_uci:
            raise ValueError("PGN contains no moves")

        return OpeningRouteSource(
            eco=eco,
            name=name,
            moves_uci=tuple(moves_uci),
            endpoint_fen=board.fen(en_passant="fen"),
        )
    except OpeningSourceError:
        raise
    except (TypeError, ValueError, UnicodeError) as error:
        raise OpeningSourceError(
            f"{source_name} row {row_number}: PGN replay failed: {error}"
        ) from error


def _read_one_game(pgn: str) -> chess.pgn.Game:
    _validate_pgn_tokens(pgn)
    stream = io.StringIO(pgn)
    try:
        game = chess.pgn.read_game(stream, Visitor=_ErrorCollectingGameBuilder)
    except (TypeError, ValueError, UnicodeError) as error:
        raise OpeningSourceError(f"PGN could not be parsed: {error}") from error
    if game is None:
        raise OpeningSourceError("PGN does not contain a complete game")
    if game.errors:
        raise OpeningSourceError(f"PGN contains a parse error: {game.errors[0]}")

    try:
        trailing_game = chess.pgn.read_game(stream, Visitor=_ErrorCollectingGameBuilder)
    except (TypeError, ValueError, UnicodeError) as error:
        raise OpeningSourceError(f"PGN contains trailing invalid text: {error}") from error
    if trailing_game is not None:
        raise OpeningSourceError("PGN must contain exactly one game")
    if stream.read().strip():
        raise OpeningSourceError("PGN contains trailing invalid text")
    return game


def _validate_pgn_tokens(pgn: str) -> None:
    """Reject movetext that the permissive PGN reader would silently skip."""

    index = 0
    variation_depth = 0
    result_seen = False
    while index < len(pgn):
        character = pgn[index]
        if character.isspace():
            index += 1
            continue
        if character == "[":
            if result_seen:
                raise OpeningSourceError("PGN contains more than one game")
            index = _consume_header(pgn, index)
            continue
        if character == "{":
            end = pgn.find("}", index + 1)
            if end < 0:
                raise OpeningSourceError("PGN contains an unterminated comment")
            index = end + 1
            continue
        if character == ";":
            newline = pgn.find("\n", index + 1)
            index = len(pgn) if newline < 0 else newline + 1
            continue
        if character == "(":
            if result_seen:
                raise OpeningSourceError("PGN contains trailing invalid text")
            variation_depth += 1
            index += 1
            continue
        if character == ")":
            if variation_depth == 0:
                raise OpeningSourceError("PGN contains an unmatched variation delimiter")
            variation_depth -= 1
            index += 1
            continue

        end = index
        while end < len(pgn) and not pgn[end].isspace() and pgn[end] not in "{}[]();":
            end += 1
        token = pgn[index:end]
        if not token:
            raise OpeningSourceError("PGN contains malformed movetext")
        if token in _RESULTS:
            result_seen = True
        elif result_seen:
            raise OpeningSourceError("PGN contains trailing invalid text")
        elif _MOVE_NUMBER_PATTERN.fullmatch(token) or token.startswith("$") and token[1:].isdigit():
            pass
        elif token in {"!", "?", "!?", "?!", "!!", "??"}:
            pass
        elif _SAN_PATTERN.fullmatch(token) is None:
            raise OpeningSourceError(f"PGN contains invalid movetext token: {token}")
        index = end

    if variation_depth:
        raise OpeningSourceError("PGN contains an unterminated variation")


def _consume_header(pgn: str, start: int) -> int:
    in_quotes = False
    escaped = False
    for index in range(start + 1, len(pgn)):
        character = pgn[index]
        if escaped:
            escaped = False
        elif character == "\\" and in_quotes:
            escaped = True
        elif character == '"':
            in_quotes = not in_quotes
        elif character == "]" and not in_quotes:
            return index + 1
    raise OpeningSourceError("PGN contains an unterminated header")
