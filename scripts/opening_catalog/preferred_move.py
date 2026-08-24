"""Direct append-only preferred-move storage and query access."""

from __future__ import annotations

import io
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Iterable

import chess
import chess.pgn

from .classification_contract import PositionKey
from .preferred_move_contract import (
    GameComparison,
    PreferredMoveLineWrite,
    PreferredMoveState,
    PreferredMoveWrite,
)
from .preferred_move_schema import ensure_preferred_move_schema

REQUIREMENT_TABLE = "opening_preferred_move_requirement_event"
MOVE_TABLE = "opening_preferred_move_event"
POSITION_FIELDS = ("placement", "side_to_move", "castling", "en_passant")
STARTING_POSITION: PositionKey = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    "w",
    "KQkq",
    "-",
)


class PreferredMoveError(ValueError):
    """A preferred-move request cannot satisfy the settled storage contract."""


def _normalise_utc(value: datetime | str) -> tuple[str, datetime]:
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            value = datetime.fromisoformat(text)
        except ValueError as error:
            raise PreferredMoveError("timestamp must be an ISO-8601 UTC datetime") from error
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise PreferredMoveError("timestamp must include a UTC offset")
    utc_value = value.astimezone(UTC)
    return utc_value.isoformat(timespec="microseconds").replace("+00:00", "Z"), utc_value


def _position_key(position: PositionKey) -> PositionKey:
    if len(position) != 4 or not all(isinstance(part, str) and part for part in position):
        raise PreferredMoveError("position must be the exact four non-empty state fields")
    if position[1] not in {"w", "b"}:
        raise PreferredMoveError("position side_to_move must be 'w' or 'b'")
    return position


def _validate_owner_and_position(
    connection: sqlite3.Connection, player_uuid: str, position: PositionKey
) -> chess.Board:
    position = _position_key(position)
    owner = connection.execute("SELECT 1 FROM players WHERE uuid = ?", (player_uuid,)).fetchone()
    if owner is None:
        raise PreferredMoveError("preferred moves require an existing player UUID")
    row = connection.execute(
        "SELECT ps.placement, ps.side_to_move, ps.castling, ps.en_passant "
        "FROM position_state AS ps JOIN position_occurrence AS po ON po.state_id = ps.state_id "
        "WHERE ps.placement = ? AND ps.side_to_move = ? AND ps.castling = ? "
        "AND ps.en_passant = ? LIMIT 1",
        position,
    ).fetchone()
    if row is None:
        raise PreferredMoveError("position is not an existing game-derived position_state")
    fen = " ".join((*position, "0", "1"))
    try:
        return chess.Board(fen)
    except ValueError as error:
        raise PreferredMoveError(
            "position_state does not describe a valid chess position"
        ) from error


def _position_from_board(board: chess.Board) -> PositionKey:
    fields = board.fen(en_passant="fen").split()
    if len(fields) != 6:
        raise PreferredMoveError("replayed position must have an exact six-field FEN")
    return tuple(fields[:4])  # type: ignore[return-value]


def _move_snapshot(board: chess.Board, move_uci: str) -> tuple[str, str]:
    if not isinstance(move_uci, str) or not move_uci:
        raise PreferredMoveError("a preferred move must be canonical legal UCI or None")
    try:
        move = board.parse_uci(move_uci)
    except ValueError as error:
        raise PreferredMoveError("preferred move is illegal for the exact position") from error
    return move.uci(), board.san(move)


def _recorded_now(connection: sqlite3.Connection, table: str) -> str:
    """Return a monotonic database-recorded timestamp in canonical UTC form."""

    now = datetime.now(UTC)
    row = connection.execute(
        f"SELECT recorded_at FROM {table} ORDER BY recorded_at DESC, event_id DESC LIMIT 1"
    ).fetchone()
    if row is not None:
        previous = _normalise_utc(str(row[0]))[1]
        if now <= previous:
            now = previous + timedelta(microseconds=1)
    return now.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _key_where(alias: str = "") -> str:
    prefix = f"{alias}." if alias else ""
    return " AND ".join(f"{prefix}{field} = ?" for field in ("player_uuid", *POSITION_FIELDS))


def _key_values(player_uuid: str, position: PositionKey) -> tuple[object, ...]:
    return (player_uuid, *position)


def _latest_event(
    connection: sqlite3.Connection,
    table: str,
    player_uuid: str,
    position: PositionKey,
    effective_at: str,
    recorded_at: str | None = None,
) -> sqlite3.Row | tuple | None:
    recorded_filter = ""
    parameters: tuple[object, ...] = (*_key_values(player_uuid, position), effective_at)
    if recorded_at is not None:
        recorded_filter = " AND recorded_at <= ?"
        parameters += (recorded_at,)
    return connection.execute(
        f"SELECT * FROM {table} WHERE {_key_where()} AND effective_at <= ?"
        f"{recorded_filter} ORDER BY effective_at DESC, recorded_at DESC, event_id DESC LIMIT 1",
        parameters,
    ).fetchone()


def _latest_effective_at(
    connection: sqlite3.Connection,
    table: str,
    player_uuid: str,
    position: PositionKey,
    effective_at: str,
    recorded_at: str | None = None,
) -> tuple[object, ...] | None:
    row = _latest_event(connection, table, player_uuid, position, effective_at, recorded_at)
    return tuple(row) if row is not None else None


def _set_requirement(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    active: bool,
    effective_at: datetime | str,
) -> PreferredMoveWrite:
    """Append one requirement event without opening or closing a transaction."""

    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    effective_text, effective_value = _normalise_utc(effective_at)
    current = _latest_effective_at(
        connection, REQUIREMENT_TABLE, player_uuid, position, effective_text
    )
    current_active = current is not None and current[6] == "active"
    action = "active" if active else "inactive"
    if current_active == active:
        return PreferredMoveWrite(False, None, action, effective_value, None)
    recorded_text = _recorded_now(connection, REQUIREMENT_TABLE)
    cursor = connection.execute(
        f"INSERT INTO {REQUIREMENT_TABLE} "
        "(player_uuid, placement, side_to_move, castling, en_passant, action, "
        "effective_at, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (*_key_values(player_uuid, position), action, effective_text, recorded_text),
    )
    event_id = int(cursor.lastrowid)
    recorded = _normalise_utc(recorded_text)[1]
    return PreferredMoveWrite(True, event_id, action, effective_value, recorded)


def set_requirement(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    active: bool,
    effective_at: datetime | str,
) -> PreferredMoveWrite:
    """Append a requirement event unless it leaves the effective timeline unchanged."""

    ensure_preferred_move_schema(connection)
    with connection:
        return _set_requirement(connection, player_uuid, position, active, effective_at)


def _set_preferred_move(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    move_uci: str | None,
    effective_at: datetime | str,
) -> PreferredMoveWrite:
    """Append one move event without opening or closing a transaction."""

    board = _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    snapshot = None if move_uci is None else _move_snapshot(board, move_uci)
    effective_text, effective_value = _normalise_utc(effective_at)
    current = _latest_effective_at(connection, MOVE_TABLE, player_uuid, position, effective_text)
    current_move = None if current is None else (current[7], current[8])
    action = "remove" if snapshot is None else "set"
    if current_move == snapshot:
        return PreferredMoveWrite(
            False, None, action, effective_value, None, *(snapshot or (None, None))
        )
    recorded_text = _recorded_now(connection, MOVE_TABLE)
    cursor = connection.execute(
        f"INSERT INTO {MOVE_TABLE} "
        "(player_uuid, placement, side_to_move, castling, en_passant, action, "
        "move_uci, move_san, effective_at, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            *_key_values(player_uuid, position),
            action,
            *(snapshot or (None, None)),
            effective_text,
            recorded_text,
        ),
    )
    event_id = int(cursor.lastrowid)
    recorded = _normalise_utc(recorded_text)[1]
    return PreferredMoveWrite(
        True, event_id, action, effective_value, recorded, *(snapshot or (None, None))
    )


def set_preferred_move(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    move_uci: str | None,
    effective_at: datetime | str,
) -> PreferredMoveWrite:
    """Append a legal move or remove event unless the effective move is unchanged."""

    ensure_preferred_move_schema(connection)
    with connection:
        return _set_preferred_move(connection, player_uuid, position, move_uci, effective_at)


def _replay_line(line: str) -> tuple[tuple[PositionKey, str, chess.Color], ...]:
    if not isinstance(line, str) or not line.strip():
        raise PreferredMoveError("line must contain at least one legal move")
    try:
        game = chess.pgn.read_game(io.StringIO('[Result "*"]\n\n' + line))
    except (TypeError, ValueError) as error:
        raise PreferredMoveError(f"line could not be parsed: {error}") from error
    if game is None:
        raise PreferredMoveError("line could not be parsed")
    parser_errors = getattr(game, "errors", ())
    if parser_errors:
        raise PreferredMoveError(f"line parser error: {parser_errors[0]}")
    board = game.board()
    if _position_from_board(board) != STARTING_POSITION:
        raise PreferredMoveError("line must start from the exact standard starting position")
    decisions: list[tuple[PositionKey, str, chess.Color]] = []
    for ply, move in enumerate(game.mainline_moves(), start=1):
        if move not in board.legal_moves:
            raise PreferredMoveError(f"line contains an illegal move at ply {ply}")
        decisions.append((_position_from_board(board), move.uci(), board.turn))
        board.push(move)
    if not decisions:
        raise PreferredMoveError("line must contain at least one legal move")
    return tuple(decisions)


def save_preferred_move_line(
    connection: sqlite3.Connection,
    player_uuid: str,
    own_color: str,
    line: str,
    effective_at: datetime | str,
) -> PreferredMoveLineWrite:
    """Replay one line and atomically save the player's own-color decisions."""

    ensure_preferred_move_schema(connection)
    colors = {"white": chess.WHITE, "black": chess.BLACK}
    if not isinstance(own_color, str) or own_color not in colors:
        raise PreferredMoveError("own_color must be 'white' or 'black'")
    if not isinstance(player_uuid, str) or not player_uuid.strip():
        raise PreferredMoveError("preferred moves require an existing player UUID")
    owner = connection.execute("SELECT 1 FROM players WHERE uuid = ?", (player_uuid,)).fetchone()
    if owner is None:
        raise PreferredMoveError("preferred moves require an existing player UUID")
    effective_text, _ = _normalise_utc(effective_at)
    decisions = tuple(item for item in _replay_line(line) if item[2] == colors[own_color])
    if not decisions:
        raise PreferredMoveError("line contains no decision for own_color")

    prepared: list[tuple[PositionKey, str]] = []
    for position, move_uci, _ in decisions:
        board = _validate_owner_and_position(connection, player_uuid, position)
        canonical_uci, _ = _move_snapshot(board, move_uci)
        prepared.append((position, canonical_uci))

    connection.execute("SAVEPOINT preferred_move_line")
    try:
        requirements = tuple(
            _set_requirement(connection, player_uuid, position, True, effective_text)
            for position, _ in prepared
        )
        moves = tuple(
            _set_preferred_move(connection, player_uuid, position, move_uci, effective_text)
            for position, move_uci in prepared
        )
    except Exception:
        connection.execute("ROLLBACK TO preferred_move_line")
        connection.execute("RELEASE preferred_move_line")
        raise
    else:
        connection.execute("RELEASE preferred_move_line")
    return PreferredMoveLineWrite(tuple(position for position, _ in prepared), requirements, moves)


def _state_from_events(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    effective_text: str,
    recorded_text: str | None = None,
) -> PreferredMoveState:
    requirement = _latest_event(
        connection, REQUIREMENT_TABLE, player_uuid, position, effective_text, recorded_text
    )
    move = _latest_event(
        connection, MOVE_TABLE, player_uuid, position, effective_text, recorded_text
    )
    return PreferredMoveState(
        player_uuid,
        position,
        requirement is not None and requirement[6] == "active",
        None if move is None else move[7],
        None if move is None else move[8],
    )


def state_at(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    effective_at: datetime | str,
) -> PreferredMoveState:
    """Derive both histories at an effective UTC instant."""

    ensure_preferred_move_schema(connection)
    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    effective_text, _ = _normalise_utc(effective_at)
    return _state_from_events(connection, player_uuid, position, effective_text)


def current_state(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    now: datetime | str | None = None,
) -> PreferredMoveState:
    """Derive present state, leaving future-effective events scheduled."""

    return state_at(connection, player_uuid, position, now or datetime.now(UTC))


def state_as_known_at(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    recorded_at: datetime | str,
    *,
    effective_at: datetime | str | None = None,
) -> PreferredMoveState:
    """Derive state using only events recorded by the requested UTC instant."""

    ensure_preferred_move_schema(connection)
    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    recorded_text, recorded_value = _normalise_utc(recorded_at)
    effective_text, _ = _normalise_utc(effective_at or recorded_value)
    return _state_from_events(connection, player_uuid, position, effective_text, recorded_text)


def compare_games(
    connection: sqlite3.Connection,
    player_uuid: str,
    position: PositionKey,
    game_uuids: Iterable[str] | None = None,
) -> tuple[GameComparison, ...]:
    """Compare observed next moves using each game's ``games.end_time`` state."""

    ensure_preferred_move_schema(connection)
    _validate_owner_and_position(connection, player_uuid, position)
    position = _position_key(position)
    filters = [
        "(g.white_player_uuid = ? OR g.black_player_uuid = ?)",
        "ps.placement = ? AND ps.side_to_move = ? AND ps.castling = ? AND ps.en_passant = ?",
    ]
    parameters: list[object] = [player_uuid, player_uuid, *position]
    selected_games = None if game_uuids is None else tuple(game_uuids)
    if selected_games is not None:
        if not selected_games:
            return ()
        placeholders = ", ".join("?" for _ in selected_games)
        filters.append(f"g.uuid IN ({placeholders})")
        parameters.extend(selected_games)
    rows = connection.execute(
        "SELECT g.uuid, g.end_time, po.ply, next_po.uci "
        "FROM games AS g JOIN position_occurrence AS po ON po.game_uuid = g.uuid "
        "JOIN position_state AS ps ON ps.state_id = po.state_id "
        "LEFT JOIN position_occurrence AS next_po ON next_po.game_uuid = po.game_uuid "
        "AND next_po.ply = po.ply + 1 WHERE " + " AND ".join(filters) + " "
        "ORDER BY g.end_time, g.uuid, po.ply",
        parameters,
    ).fetchall()
    comparisons = []
    for game_uuid, end_time, ply, actual_move in rows:
        if end_time is None:
            continue
        state = state_at(
            connection,
            player_uuid,
            position,
            datetime.fromtimestamp(int(end_time), UTC),
        )
        judged = state.requirement_active and state.move_uci is not None
        actual = None if actual_move is None else str(actual_move).lower()
        comparisons.append(
            GameComparison(
                str(game_uuid),
                int(ply),
                int(end_time),
                state.move_uci,
                actual,
                state.requirement_active,
                judged,
                None if not judged else actual == state.move_uci,
            )
        )
    return tuple(comparisons)


# Names used by callers that describe the same narrow access operations.
record_requirement = set_requirement
record_preferred_move = set_preferred_move
get_current_state = current_state
get_state_at = state_at
get_state_as_known_at = state_as_known_at
compare_games_at_end = compare_games
