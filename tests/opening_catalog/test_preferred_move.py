from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import chess
import pytest

from scripts.opening_catalog import (
    PREFERRED_MOVE_SCHEMA_TABLES,
    PreferredMoveError,
    compare_games,
    current_state,
    ensure_preferred_move_schema,
    preferred_move_history,
    save_preferred_move_line,
    set_preferred_move,
    set_requirement,
    state_as_known_at,
    state_at,
)

PLAYER = "player-uuid"
OPPONENT = "opponent-uuid"
POSITION = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    "w",
    "KQkq",
    "-",
)
AFTER_E4 = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
    "b",
    "KQkq",
    "-",
)
UNOBSERVED = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPP1PPP/RNBQKBNR",
    "w",
    "KQkq",
    "-",
)
SKYROCASTER = "skyrocoster-stable-uuid"
LINE = "1.e4 c6 2.d4 d5 3.e5 c5"
EFFECTIVE = "2024-09-03T06:00:00Z"


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


def _open_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE players (uuid TEXT PRIMARY KEY, username TEXT NOT NULL, profile_url TEXT);
        CREATE TABLE games (
            uuid TEXT PRIMARY KEY, url TEXT NOT NULL, pgn TEXT NOT NULL,
            time_control TEXT NOT NULL, end_time INTEGER NOT NULL, rated INTEGER,
            tcn TEXT, initial_setup TEXT, fen TEXT, time_class TEXT, rules TEXT, eco TEXT,
            white_player_uuid TEXT NOT NULL, black_player_uuid TEXT NOT NULL,
            white_rating INTEGER, black_rating INTEGER, white_result TEXT, black_result TEXT,
            white_accuracy REAL, black_accuracy REAL, tournament TEXT, match TEXT,
            year INTEGER NOT NULL, month INTEGER NOT NULL,
            FOREIGN KEY (white_player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (black_player_uuid) REFERENCES players(uuid)
        );
        CREATE TABLE position_state (
            state_id INTEGER PRIMARY KEY,
            placement TEXT, side_to_move TEXT, castling TEXT, en_passant TEXT,
            UNIQUE (placement, side_to_move, castling, en_passant)
        );
        CREATE TABLE position_occurrence (
            occurrence_id INTEGER PRIMARY KEY, game_uuid TEXT NOT NULL, ply INTEGER NOT NULL,
            state_id INTEGER NOT NULL, san TEXT, uci TEXT,
            halfmove_clock INTEGER NOT NULL, fullmove_number INTEGER NOT NULL,
            UNIQUE (game_uuid, ply), FOREIGN KEY (game_uuid) REFERENCES games(uuid),
            FOREIGN KEY (state_id) REFERENCES position_state(state_id)
        );
        INSERT INTO players VALUES
            ('player-uuid', 'Player', NULL), ('opponent-uuid', 'Opponent', NULL);
        INSERT INTO games
            (
                uuid, url, pgn, time_control, end_time, white_player_uuid,
                black_player_uuid, year, month
            )
        VALUES
            ('game-before', '', '', '', 1704067199, 'player-uuid', 'opponent-uuid', 2023, 12),
            ('game-after', '', '', '', 1704067201, 'player-uuid', 'opponent-uuid', 2024, 1);
        INSERT INTO position_state VALUES
            (1, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', 'w', 'KQkq', '-'),
            (2, 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR', 'b', 'KQkq', '-'),
            (3, 'rnbqkbnr/pppppppp/8/8/8/8/PPPP1PPP/RNBQKBNR', 'w', 'KQkq', '-');
        INSERT INTO position_occurrence
            (game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number) VALUES
            ('game-before', 0, 1, NULL, NULL, 0, 1),
            ('game-before', 1, 2, 'e4', 'e2e4', 0, 1),
            ('game-after', 0, 1, NULL, NULL, 0, 1),
            ('game-after', 1, 2, 'e4', 'e2e4', 0, 1);
        """
    )
    ensure_preferred_move_schema(connection)
    return connection


def _board_position(board: chess.Board) -> tuple[str, str, str, str]:
    return tuple(board.fen(en_passant="fen").split()[:4])  # type: ignore[return-value]


def _open_line_database(path: Path) -> sqlite3.Connection:
    connection = _open_database(path)
    connection.execute("INSERT INTO players VALUES (?, 'Skyrocoster', NULL)", (SKYROCASTER,))
    connection.execute(
        "INSERT INTO games "
        "(uuid, url, pgn, time_control, end_time, white_player_uuid, black_player_uuid, "
        "year, month) "
        "VALUES ('line-game', '', ?, '', 1704067200, ?, ?, 2024, 1)",
        (LINE, OPPONENT, SKYROCASTER),
    )
    board = chess.Board()
    moves = tuple(LINE.replace("1.", "").replace("2.", "").replace("3.", "").split())
    for ply, san in enumerate((None, *moves), start=0):
        move_uci = move_san = None
        if san is not None:
            move = board.parse_san(san)
            move_uci, move_san = move.uci(), board.san(move)
            board.push(move)
        position = _board_position(board)
        state = connection.execute(
            "SELECT state_id FROM position_state WHERE placement = ? AND side_to_move = ? "
            "AND castling = ? AND en_passant = ?",
            position,
        ).fetchone()
        if state is None:
            state_id = int(
                connection.execute(
                    "INSERT INTO position_state "
                    "(placement, side_to_move, castling, en_passant) VALUES (?, ?, ?, ?)",
                    position,
                ).lastrowid
            )
        else:
            state_id = int(state[0])
        connection.execute(
            "INSERT INTO position_occurrence "
            "(game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number) "
            "VALUES ('line-game', ?, ?, ?, ?, ?, ?)",
            (ply, state_id, move_san, move_uci, board.halfmove_clock, board.fullmove_number),
        )
    connection.commit()
    return connection


def test_schema_has_only_two_append_only_histories(tmp_path: Path) -> None:
    with _open_database(tmp_path / "schema.db") as connection:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND name LIKE 'opening_preferred_move%'"
            )
        }
        assert names == PREFERRED_MOVE_SCHEMA_TABLES
        assert all(
            not any(
                word in str(row[1]).lower() for word in ("projection", "cache", "reason", "source")
            )
            for table in PREFERRED_MOVE_SCHEMA_TABLES
            for row in connection.execute(f"PRAGMA table_info({table})")
        )
        connection.execute(
            "INSERT INTO opening_preferred_move_requirement_event "
            "(player_uuid, placement, side_to_move, castling, en_passant, action, effective_at) "
            "VALUES (?, ?, ?, ?, ?, 'active', '2024-01-01T00:00:00.000000Z')",
            (PLAYER, *POSITION),
        )
        connection.execute(
            "INSERT INTO opening_preferred_move_event "
            "(player_uuid, placement, side_to_move, castling, en_passant, action, "
            "move_uci, move_san, effective_at) VALUES (?, ?, ?, ?, ?, 'set', 'e2e4', 'e4', "
            "'2024-01-01T00:00:00.000000Z')",
            (PLAYER, *POSITION),
        )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE opening_preferred_move_requirement_event SET action = 'active'"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM opening_preferred_move_event")


def test_effective_recorded_and_tied_correction_timelines(tmp_path: Path) -> None:
    with _open_database(tmp_path / "time.db") as connection:
        first = set_requirement(connection, PLAYER, POSITION, True, "2024-01-10T00:00:00Z")
        assert first.changed is True
        corrected = set_requirement(connection, PLAYER, POSITION, False, "2024-01-10T00:00:00Z")
        assert corrected.changed is True
        assert (
            state_at(connection, PLAYER, POSITION, "2024-01-10T00:00:00Z").requirement_active
            is False
        )
        assert (
            state_as_known_at(
                connection,
                PLAYER,
                POSITION,
                first.recorded_at,
                effective_at="2024-01-10T00:00:00Z",
            ).requirement_active
            is True
        )
        assert (
            set_requirement(connection, PLAYER, POSITION, False, "2024-01-10T00:00:00Z").changed
            is False
        )

        future = set_requirement(connection, PLAYER, POSITION, True, "2028-01-01T00:00:00Z")
        assert (
            state_at(connection, PLAYER, POSITION, "2027-12-31T23:59:59Z").requirement_active
            is False
        )
        assert (
            state_at(connection, PLAYER, POSITION, "2028-01-01T00:00:00Z").requirement_active
            is True
        )
        assert future.recorded_at is not None


def test_independent_streams_validate_moves_and_reject_unobserved_positions(
    tmp_path: Path,
) -> None:
    with _open_database(tmp_path / "moves.db") as connection:
        set_requirement(connection, PLAYER, POSITION, True, "2023-12-01T00:00:00Z")
        assert current_state(connection, PLAYER, POSITION, "2023-12-02T00:00:00Z").status == (
            "choice_needed"
        )
        move = set_preferred_move(connection, PLAYER, POSITION, "e2e4", "2024-01-01T00:00:00Z")
        assert (move.move_uci, move.move_san) == ("e2e4", "e4")
        assert (
            current_state(connection, PLAYER, POSITION, "2024-01-02T00:00:00Z").status
            == "satisfied"
        )
        assert (
            set_preferred_move(connection, PLAYER, POSITION, "e2e4", "2024-01-01T00:00:00Z").changed
            is False
        )
        set_requirement(connection, PLAYER, POSITION, False, "2024-01-03T00:00:00Z")
        assert current_state(connection, PLAYER, POSITION, "2024-01-04T00:00:00Z").status == (
            "stored_out_of_scope"
        )
        with pytest.raises(PreferredMoveError, match="illegal"):
            set_preferred_move(connection, PLAYER, POSITION, "e2e5", "2024-01-05T00:00:00Z")
        with pytest.raises(PreferredMoveError, match="game-derived"):
            set_preferred_move(connection, PLAYER, UNOBSERVED, "e2e4", "2024-01-05T00:00:00Z")


def test_move_history_returns_all_move_and_no_move_periods(tmp_path: Path) -> None:
    with _open_database(tmp_path / "history.db") as connection:
        set_preferred_move(connection, PLAYER, POSITION, "e2e4", "2024-01-10T00:00:00Z")
        set_preferred_move(connection, PLAYER, POSITION, "d2d4", "2024-01-20T00:00:00Z")
        set_preferred_move(connection, PLAYER, POSITION, None, "2024-01-30T00:00:00Z")
        periods = preferred_move_history(
            connection,
            PLAYER,
            POSITION,
            "2024-01-01T00:00:00Z",
            "2024-02-01T00:00:00Z",
        )
        assert [(period.start.day, period.end.day, period.move_uci) for period in periods] == [
            (1, 10, None),
            (10, 20, "e2e4"),
            (20, 30, "d2d4"),
            (30, 1, None),
        ]


def test_game_comparison_uses_game_end_time_and_not_judged_state(tmp_path: Path) -> None:
    with _open_database(tmp_path / "games.db") as connection:
        set_preferred_move(connection, PLAYER, POSITION, "e2e4", "2024-01-01T00:00:00Z")
        set_requirement(connection, PLAYER, POSITION, True, "2024-01-01T00:00:00Z")
        comparisons = compare_games(connection, PLAYER, POSITION)
        assert [(item.game_uuid, item.judged, item.matches) for item in comparisons] == [
            ("game-before", False, None),
            ("game-after", True, True),
        ]


def _black_line_positions() -> tuple[tuple[str, str, str, str], ...]:
    board = chess.Board()
    positions = []
    for san in ("e4", "c6", "d4", "d5", "e5", "c5"):
        move = board.parse_san(san)
        board.push(move)
        if board.turn == chess.BLACK:
            positions.append(_board_position(board))
    return tuple(positions)


def _event_counts(connection: sqlite3.Connection) -> tuple[int, int]:
    return tuple(
        int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        for table in (
            "opening_preferred_move_requirement_event",
            "opening_preferred_move_event",
        )
    )


def test_line_replay_saves_exact_black_decisions_and_canonical_snapshots(tmp_path: Path) -> None:
    with _open_line_database(tmp_path / "line.db") as connection:
        result = save_preferred_move_line(connection, SKYROCASTER, "black", LINE, EFFECTIVE)

        assert result.positions == _black_line_positions()
        assert result.changed is True
        assert [item.move_uci for item in result.moves] == ["c7c6", "d7d5", "c6c5"]
        assert [item.move_san for item in result.moves] == ["c6", "d5", "c5"]
        assert all(item.changed for item in result.requirements)
        assert all(item.changed for item in result.moves)
        assert _event_counts(connection) == (3, 3)
        assert connection.execute(
            "SELECT DISTINCT side_to_move FROM opening_preferred_move_requirement_event"
        ).fetchall() == [("b",)]
        assert connection.execute(
            "SELECT DISTINCT side_to_move FROM opening_preferred_move_event"
        ).fetchall() == [("b",)]
        assert (
            connection.execute(
                "SELECT action, effective_at FROM opening_preferred_move_requirement_event "
                "ORDER BY event_id"
            ).fetchall()
            == [("active", "2024-09-03T06:00:00.000000Z")] * 3
        )
        assert connection.execute(
            "SELECT move_uci, move_san, effective_at FROM opening_preferred_move_event "
            "ORDER BY event_id"
        ).fetchall() == [
            ("c7c6", "c6", "2024-09-03T06:00:00.000000Z"),
            ("d7d5", "d5", "2024-09-03T06:00:00.000000Z"),
            ("c6c5", "c5", "2024-09-03T06:00:00.000000Z"),
        ]
        assert all(
            state_at(connection, SKYROCASTER, position, EFFECTIVE).status == "satisfied"
            for position in result.positions
        )


def test_line_replay_unchanged_repeat_is_a_noop(tmp_path: Path) -> None:
    with _open_line_database(tmp_path / "repeat.db") as connection:
        save_preferred_move_line(connection, SKYROCASTER, "black", LINE, EFFECTIVE)
        before = _event_counts(connection)

        result = save_preferred_move_line(connection, SKYROCASTER, "black", LINE, EFFECTIVE)

        assert result.changed is False
        assert not any(item.changed for item in (*result.requirements, *result.moves))
        assert _event_counts(connection) == before == (3, 3)


@pytest.mark.parametrize(
    ("player_uuid", "own_color", "line", "message"),
    (
        ("missing-player", "black", LINE, "existing player UUID"),
        (SKYROCASTER, "purple", LINE, "own_color"),
        (SKYROCASTER, "black", "1.e4 c6 2.d4 d5 3.e5 c5 4.c4 c4", "parser"),
    ),
)
def test_line_replay_rejects_invalid_player_color_or_line_without_events(
    tmp_path: Path,
    player_uuid: str,
    own_color: str,
    line: str,
    message: str,
) -> None:
    with _open_line_database(tmp_path / f"reject-{message}.db") as connection:
        with pytest.raises(PreferredMoveError, match=message):
            save_preferred_move_line(connection, player_uuid, own_color, line, EFFECTIVE)
        assert _event_counts(connection) == (0, 0)


def test_line_replay_rejects_unobserved_position_without_partial_events(tmp_path: Path) -> None:
    with _open_line_database(tmp_path / "unobserved.db") as connection:
        connection.execute(
            "DELETE FROM position_occurrence WHERE game_uuid = 'line-game' AND ply = 3"
        )
        connection.commit()

        with pytest.raises(PreferredMoveError, match="game-derived"):
            save_preferred_move_line(connection, SKYROCASTER, "black", LINE, EFFECTIVE)
        assert _event_counts(connection) == (0, 0)


def test_line_replay_write_failure_rolls_back_all_six_events(tmp_path: Path) -> None:
    with _open_line_database(tmp_path / "rollback.db") as connection:
        connection.isolation_level = None
        placement = _black_line_positions()[0][0].replace("'", "''")
        connection.executescript(
            "CREATE TRIGGER fail_line_replay BEFORE INSERT ON "
            "opening_preferred_move_event "
            f"WHEN NEW.placement = '{placement}' "
            "BEGIN SELECT RAISE(ABORT, 'forced line failure'); END;"
        )
        with pytest.raises(sqlite3.IntegrityError, match="forced line failure"):
            save_preferred_move_line(connection, SKYROCASTER, "black", LINE, EFFECTIVE)
        assert _event_counts(connection) == (0, 0)
