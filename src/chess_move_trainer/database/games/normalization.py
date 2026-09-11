"""Pure validation, normalization, and replay of raw Chess.com games."""

from __future__ import annotations

import io
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

import chess
import chess.pgn

from ..positions import CanonicalPosition, canonicalize_board

TrainerColor = Literal["white", "black"]
TrainerOutcome = Literal["win", "loss", "draw"]
_HEADER_LINE = re.compile(r'^\[[A-Za-z0-9_]+ "(?:\\.|[^"\\])*"\]$')
_DRAW_RESULTS = {
    "50move",
    "agreed",
    "insufficient",
    "repetition",
    "stalemate",
    "timevsinsufficient",
}
_LOSS_RESULTS = {"abandoned", "checkmated", "lose", "resigned", "timeout"}
_NON_TERMINATIONS = {"", "normal", "unknown", "unterminated", "win", "loss", "lose"}


class GameNormalizationError(ValueError):
    """Describes why one raw game cannot be normalized."""


@dataclass(frozen=True, slots=True)
class NormalizationWarning:
    game_uuid: str | None
    message: str


@dataclass(frozen=True, slots=True)
class GameOccurrence:
    ply: int
    position: CanonicalPosition
    move_uci: str | None
    halfmove_clock: int
    fullmove_number: int


@dataclass(frozen=True, slots=True)
class NormalizedGame:
    chesscom_game_uuid: UUID
    source_url: str
    original_pgn: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: UUID
    opponent_chesscom_uuid: UUID | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control_source: str | None
    time_class: str | None
    occurrences: tuple[GameOccurrence, ...]


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    game: NormalizedGame | None
    warning: NormalizationWarning | None

    @property
    def accepted(self) -> bool:
        return self.game is not None


class _QuietGameBuilder(chess.pgn.GameBuilder):
    def handle_error(self, error: Exception) -> None:
        self.game.errors.append(error)


def normalize_game(raw_game: object, trainer_uuid: UUID) -> NormalizationResult:
    """Return a fully validated game, or one ordinary warning for a skipped input."""

    raw_uuid = raw_game.get("uuid") if isinstance(raw_game, dict) else None
    warning_uuid = raw_uuid if isinstance(raw_uuid, str) else None
    try:
        game = _normalize_game(raw_game, trainer_uuid)
    except (GameNormalizationError, ValueError, OverflowError) as error:
        return NormalizationResult(
            game=None,
            warning=NormalizationWarning(game_uuid=warning_uuid, message=str(error)),
        )
    return NormalizationResult(game=game, warning=None)


def _normalize_game(raw_game: object, trainer_uuid: UUID) -> NormalizedGame:
    if not isinstance(raw_game, dict):
        raise GameNormalizationError("raw game must be a JSON object")
    game_uuid = _required_uuid(raw_game.get("uuid"), "game UUID")

    if raw_game.get("rules") != "chess":
        raise GameNormalizationError("non-standard game rules are not accepted")

    white = raw_game.get("white")
    black = raw_game.get("black")
    white_participant = white if isinstance(white, dict) else {}
    black_participant = black if isinstance(black, dict) else {}
    white_uuid = _optional_uuid(white_participant.get("uuid"))
    black_uuid = _optional_uuid(black_participant.get("uuid"))
    matching_colors = [
        color
        for color, participant_uuid in (("white", white_uuid), ("black", black_uuid))
        if participant_uuid == trainer_uuid
    ]
    if len(matching_colors) != 1:
        raise GameNormalizationError(
            "exactly one participant must match the configured trainer UUID"
        )
    trainer_color: TrainerColor = matching_colors[0]  # type: ignore[assignment]
    trainer = white_participant if trainer_color == "white" else black_participant
    opponent = black_participant if trainer_color == "white" else white_participant

    source_url = raw_game.get("url")
    if not isinstance(source_url, str) or not source_url:
        raise GameNormalizationError("source URL must be a non-empty string")
    original_pgn = raw_game.get("pgn")
    if not isinstance(original_pgn, str) or not original_pgn:
        raise GameNormalizationError("source PGN must be a non-empty string")

    parsed_game = _parse_pgn(original_pgn)
    board = parsed_game.board()
    if board.fen(en_passant="fen") != chess.STARTING_FEN:
        raise GameNormalizationError("PGN must use the normal starting board")
    occurrences = _replay(parsed_game, board)

    trainer_result = _optional_text(trainer.get("result"))
    opponent_result = _optional_text(opponent.get("result"))
    outcome, termination = _result_metadata(
        trainer_result, opponent_result, parsed_game.headers.get("Termination")
    )

    return NormalizedGame(
        chesscom_game_uuid=game_uuid,
        source_url=source_url,
        original_pgn=original_pgn,
        trainer_color=trainer_color,
        trainer_chesscom_uuid=trainer_uuid,
        opponent_chesscom_uuid=_optional_uuid(opponent.get("uuid")),
        trainer_rating=_optional_integer(trainer.get("rating")),
        opponent_rating=_optional_integer(opponent.get("rating")),
        started_at_utc=_start_timestamp(parsed_game.headers),
        ended_at_utc=_end_timestamp(raw_game.get("end_time"), parsed_game.headers),
        trainer_outcome=outcome,
        termination_reason=termination,
        time_control_source=_optional_text(raw_game.get("time_control")),
        time_class=_optional_text(raw_game.get("time_class")),
        occurrences=occurrences,
    )


def _parse_pgn(source: str) -> chess.pgn.Game:
    header_block = source.split("\n\n", 1)[0]
    if header_block.lstrip().startswith("["):
        for line in header_block.splitlines():
            if line and _HEADER_LINE.fullmatch(line) is None:
                raise GameNormalizationError("PGN contains a malformed header")
    try:
        game = chess.pgn.read_game(io.StringIO(source), Visitor=_QuietGameBuilder)
    except (ValueError, TypeError, UnicodeError) as error:
        raise GameNormalizationError(f"PGN could not be parsed: {error}") from error
    if game is None:
        raise GameNormalizationError("PGN does not contain a game")
    if game.errors:
        raise GameNormalizationError(f"PGN contains an illegal or malformed move: {game.errors[0]}")
    return game


def _replay(game: chess.pgn.Game, board: chess.Board) -> tuple[GameOccurrence, ...]:
    moves = list(game.mainline_moves())
    occurrences: list[GameOccurrence] = []
    for ply, move in enumerate(moves):
        if move not in board.legal_moves:
            raise GameNormalizationError(f"PGN contains an illegal move at ply {ply}")
        occurrences.append(
            GameOccurrence(
                ply=ply,
                position=canonicalize_board(board),
                move_uci=move.uci(),
                halfmove_clock=board.halfmove_clock,
                fullmove_number=board.fullmove_number,
            )
        )
        board.push(move)
    occurrences.append(
        GameOccurrence(
            ply=len(moves),
            position=canonicalize_board(board),
            move_uci=None,
            halfmove_clock=board.halfmove_clock,
            fullmove_number=board.fullmove_number,
        )
    )
    return tuple(occurrences)


def _required_uuid(value: object, field: str) -> UUID:
    parsed = _optional_uuid(value)
    if parsed is None:
        raise GameNormalizationError(f"{field} must be a valid UUID")
    return parsed


def _optional_uuid(value: object) -> UUID | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = UUID(value)
    except ValueError:
        return None
    if str(parsed) != value.lower():
        return None
    return parsed


def _optional_integer(value: object) -> int | None:
    return value if type(value) is int else None


def _optional_text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _start_timestamp(headers: chess.pgn.Headers) -> str | None:
    return _header_timestamp(headers, "UTCDate", "UTCTime") or _header_timestamp(
        headers, "Date", "StartTime"
    )


def _end_timestamp(value: object, headers: chess.pgn.Headers) -> str | None:
    if type(value) in (int, float) and math.isfinite(float(value)):
        return _format_utc(datetime.fromtimestamp(float(value), UTC))
    return _header_timestamp(headers, "EndDate", "EndTime")


def _header_timestamp(
    headers: chess.pgn.Headers, date_name: str, time_name: str
) -> str | None:
    date_value = headers.get(date_name)
    time_value = headers.get(time_name)
    if not date_value or not time_value:
        return None
    try:
        parsed = datetime.strptime(f"{date_value} {time_value}", "%Y.%m.%d %H:%M:%S")
    except ValueError:
        return None
    return _format_utc(parsed.replace(tzinfo=UTC))


def _format_utc(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _result_metadata(
    trainer_result: str | None,
    opponent_result: str | None,
    pgn_termination: str | None,
) -> tuple[TrainerOutcome | None, str | None]:
    trainer_code = trainer_result.casefold() if trainer_result else None
    opponent_code = opponent_result.casefold() if opponent_result else None
    outcome: TrainerOutcome | None = None
    termination: str | None = None

    if trainer_code == "win" or opponent_code in _LOSS_RESULTS:
        outcome = "win"
        termination = _informative_termination(opponent_code)
    elif opponent_code == "win" or trainer_code in _LOSS_RESULTS:
        outcome = "loss"
        termination = _informative_termination(trainer_code)
    elif trainer_code == opponent_code and trainer_code in _DRAW_RESULTS:
        outcome = "draw"
        termination = trainer_code

    if termination is None:
        termination = _informative_termination(pgn_termination)
    return outcome, termination


def _informative_termination(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.casefold() in _NON_TERMINATIONS:
        return None
    return normalized
