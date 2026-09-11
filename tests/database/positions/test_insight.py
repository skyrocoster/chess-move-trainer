from __future__ import annotations

import json
import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import (
    PositionInsightRepository,
    PositionInsightRequest,
    PositionInsightSchemaError,
    PositionInsightStorageError,
    PositionInsightValidationError,
    PositionRepository,
    read_position_insight,
)
from chess_move_trainer.database.preferred_moves import (
    PreferredMoveRemovalRequest,
    delete_preferred_move,
)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TARGET_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
TARGET_WITH_COUNTERS = " ".join((*TARGET_FEN.split()[:4], "99", "120"))
TARGET_CANONICAL_FEN = " ".join((*TARGET_FEN.split()[:4], "0", "1"))
UNSEEN_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 17 8"
UNSEEN_CANONICAL_FEN = UNSEEN_FEN.rsplit(" ", 2)[0] + " 0 1"


def _position_id(database: Path, fen: str) -> int:
    return PositionRepository(database).resolve_fen(fen)


def _game(connection: sqlite3.Connection, game_id: int, color: str) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            f"game-{game_id}",
            f"https://example.test/game-{game_id}",
            "[Result \"*\"]\n\n*",
            color,
            f"trainer-{game_id}",
        ),
    )


def _occurrence(
    connection: sqlite3.Connection,
    game_id: int,
    ply: int,
    position_id: int,
    move_uci: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, ?, ?, ?, 0, 1)
        """,
        (game_id, ply, position_id, move_uci),
    )


def _install_opening(connection: sqlite3.Connection, position_id: int) -> None:
    opening = connection.execute(
        """
        INSERT INTO datasource_opening (do_eco, do_name)
        VALUES ('C20', 'King''s Pawn Game')
        RETURNING do_opening_id
        """
    ).fetchone()[0]
    route = connection.execute(
        """
        INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
        VALUES (?, ?)
        RETURNING dor_route_id
        """,
        (opening, position_id),
    ).fetchone()[0]
    connection.executemany(
        """
        INSERT INTO derived_opening_route_move
            (derived_opening_route_id, dorm_ply, dorm_move_uci)
        VALUES (?, ?, ?)
        """,
        ((route, 1, "e2e4"), (route, 2, "e7e5")),
    )


def _install_analysis(connection: sqlite3.Connection, position_id: int) -> None:
    connection.execute(
        """
        INSERT INTO derived_analysis_result (
            derived_position_id, dar_quality, dar_configuration_version,
            dar_settings_json, dar_engine_name, dar_engine_version, dar_terminal_kind
        ) VALUES (?, 'tool', 7, ?, 'Stockfish', '18', NULL)
        """,
        (position_id, json.dumps({"Hash": 16})),
    )
    connection.execute(
        """
        INSERT INTO derived_analysis_line (
            derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value,
            dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth
        ) VALUES (?, 1, 'cp', 34, 450, 300, 250, '["a2a3"]', 22)
        """,
        (position_id,),
    )


def _install_preference(connection: sqlite3.Connection, position_id: int) -> None:
    connection.executemany(
        """
        INSERT INTO datasource_preferred_move_period (
            derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci
        ) VALUES (?, ?, ?, ?)
        """,
        (
            (position_id, "2026-01-01", "2026-02-01", "a2a3"),
            (position_id, "2026-02-01", "2026-03-01", None),
            (position_id, "2026-03-01", None, "b2b3"),
        ),
    )


def _database(tmp_path: Path) -> tuple[Path, int]:
    database = tmp_path / "insight.db"
    create_schema(database)
    position_id = _position_id(database, TARGET_FEN)
    with sqlite3.connect(database) as connection:
        _game(connection, 1, "white")
        _game(connection, 2, "white")
        _game(connection, 3, "black")
        _game(connection, 4, "black")
        _game(connection, 5, "white")
        _occurrence(connection, 1, 2, position_id, "a2a3")
        _occurrence(connection, 1, 4, position_id, "a2a3")
        _occurrence(connection, 2, 2, position_id, "b2b3")
        _occurrence(connection, 3, 2, position_id, "a2a3")
        _occurrence(connection, 4, 2, position_id, None)
        _install_opening(connection, position_id)
        _install_analysis(connection, position_id)
        _install_preference(connection, position_id)
    return database, position_id


def test_existing_position_composes_canonical_opening_counts_analysis_and_preference(
    tmp_path: Path,
) -> None:
    database, _position_id = _database(tmp_path)

    insight = read_position_insight(
        database,
        TARGET_WITH_COUNTERS,
        "white",
        "2026-01-15",
    )

    assert insight.fen == TARGET_CANONICAL_FEN
    assert insight.trainer_color == "white"
    assert insight.as_of == "2026-01-15"
    assert insight.opening is not None
    assert (
        insight.opening.key,
        insight.opening.eco,
        insight.opening.name,
        insight.opening.ply,
        insight.opening.match,
    ) == ("C20:King's Pawn Game", "C20", "King's Pawn Game", 2, "transposition")
    assert insight.experience.distinct_game_count == 2
    assert insight.experience.occurrence_count == 3
    assert insight.experience.total_game_count == 3
    assert insight.observed_in_games is True
    assert insight.observed_move_totals.distinct_game_count == 2
    assert insight.observed_move_totals.occurrence_count == 3
    assert insight.observed_move_totals.terminal.distinct_game_count == 0
    assert insight.observed_move_totals.terminal.occurrence_count == 0
    assert [
        (move.move_uci, move.distinct_game_count, move.occurrence_count)
        for move in insight.observed_moves
    ] == [("a2a3", 1, 2), ("b2b3", 1, 1)]
    assert insight.analysis.state == "ready"
    assert insight.analysis.result is not None
    assert insight.analysis.result.quality.value == "tool"
    assert insight.analysis.result.configuration_version == 7
    assert insight.analysis.result.settings == {"Hash": 16}
    assert insight.analysis.result.lines[0].pv_uci == ("a2a3",)
    assert insight.preference.kind == "move"
    assert insight.preference.uci == "a2a3"

    black = read_position_insight(database, TARGET_FEN, "black", "2026-01-15")
    assert black.experience.distinct_game_count == 2
    assert black.experience.occurrence_count == 2
    assert black.experience.total_game_count == 2
    assert black.observed_in_games is True
    assert black.observed_move_totals.distinct_game_count == 1
    assert black.observed_move_totals.occurrence_count == 1
    assert black.observed_move_totals.terminal.distinct_game_count == 1
    assert black.observed_move_totals.terminal.occurrence_count == 1
    assert [move.move_uci for move in black.observed_moves] == ["a2a3"]


def test_observation_is_true_for_other_color_only_and_selected_counts_stay_zero(
    tmp_path: Path,
) -> None:
    database, _target_position_id = _database(tmp_path)
    position_id = _position_id(database, STARTING_FEN)
    with sqlite3.connect(database) as connection:
        _occurrence(connection, 3, 6, position_id, "e2e4")

    insight = read_position_insight(database, STARTING_FEN, "white", "2026-09-09")

    assert insight.observed_in_games is True
    assert insight.experience.distinct_game_count == 0
    assert insight.experience.occurrence_count == 0
    assert insight.experience.total_game_count == 3
    assert insight.observed_move_totals.distinct_game_count == 0
    assert insight.observed_move_totals.occurrence_count == 0
    assert insight.observed_move_totals.terminal.distinct_game_count == 0
    assert insight.observed_move_totals.terminal.occurrence_count == 0
    assert insight.observed_moves == ()


@pytest.mark.parametrize(
    ("as_of", "kind", "uci"),
    [
        ("2026-02-15", "no_preference", None),
        ("2026-03-01", "move", "b2b3"),
        ("2025-12-31", "unconfigured", None),
    ],
)
def test_preference_is_resolved_by_the_package_for_the_requested_date(
    tmp_path: Path,
    as_of: str,
    kind: str,
    uci: str | None,
) -> None:
    database, _position_id = _database(tmp_path)

    preference = read_position_insight(database, TARGET_FEN, "white", as_of).preference

    assert preference.kind == kind
    assert preference.uci == uci


def test_delete_is_immediately_visible_as_unconfigured_in_position_insight(
    tmp_path: Path,
) -> None:
    database, _position_id = _database(tmp_path)

    delete_preferred_move(
        database,
        PreferredMoveRemovalRequest(TARGET_FEN, "2026-01-01", "2026-02-01"),
    )

    insight = read_position_insight(
        database, TARGET_FEN, "white", "2026-01-15"
    )
    assert insight.preference.kind == "unconfigured"
    assert insight.preference.uci is None


def test_unseen_legal_position_is_sparse_and_has_no_opening_or_preference(
    tmp_path: Path,
) -> None:
    database, _position_id = _database(tmp_path)
    before = database.read_bytes()

    insight = read_position_insight(database, UNSEEN_FEN, "black", "2026-09-09")

    assert insight.fen == UNSEEN_CANONICAL_FEN
    assert insight.opening is None
    assert insight.observed_in_games is False
    assert insight.experience.distinct_game_count == 0
    assert insight.experience.occurrence_count == 0
    assert insight.experience.total_game_count == 2
    assert insight.observed_moves == ()
    assert insight.observed_move_totals.distinct_game_count == 0
    assert insight.observed_move_totals.occurrence_count == 0
    assert insight.observed_move_totals.terminal.distinct_game_count == 0
    assert insight.observed_move_totals.terminal.occurrence_count == 0
    assert insight.analysis.state == "not_requested"
    assert insight.analysis.result is None
    assert insight.preference.kind == "unconfigured"
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("insight.db-*"))
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1


def test_internal_unobserved_position_is_sparse_without_writes(tmp_path: Path) -> None:
    database, _target_position_id = _database(tmp_path)
    position_id = _position_id(database, UNSEEN_FEN)
    before = database.read_bytes()

    insight = read_position_insight(database, UNSEEN_FEN, "black", "2026-09-09")

    assert position_id > 0
    assert insight.observed_in_games is False
    assert insight.experience.distinct_game_count == 0
    assert insight.experience.occurrence_count == 0
    assert insight.experience.total_game_count == 2
    assert insight.observed_moves == ()
    assert insight.observed_move_totals.distinct_game_count == 0
    assert insight.observed_move_totals.occurrence_count == 0
    assert insight.observed_move_totals.terminal.distinct_game_count == 0
    assert insight.observed_move_totals.terminal.occurrence_count == 0
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("insight.db-*"))


def test_analysis_queue_precedence_keeps_a_current_result_visible(tmp_path: Path) -> None:
    database, position_id = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', 'queued', '2026-09-09T00:00:00Z', NULL, NULL)
            """,
            (position_id,),
        )

    queued = read_position_insight(database, TARGET_FEN, "white", "2026-09-09")
    assert queued.analysis.state == "queued"
    assert queued.analysis.result is not None

    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM derived_analysis_queue")
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', 'running', '2026-09-09T00:00:00Z',
                      '2026-09-09T00:01:00Z', 'claim-token')
            """,
            (position_id,),
        )

    running = read_position_insight(database, TARGET_FEN, "white", "2026-09-09")
    assert running.analysis.state == "running"
    assert running.analysis.result is not None


def test_queue_without_result_reports_queued_and_no_result(tmp_path: Path) -> None:
    database, _target_position_id = _database(tmp_path)
    second_position = _position_id(database, STARTING_FEN)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', 'queued', '2026-09-09T00:00:00Z', NULL, NULL)
            """,
            (second_position,),
        )

    insight = read_position_insight(database, STARTING_FEN, "white", "2026-09-09")

    assert insight.analysis.state == "queued"
    assert insight.analysis.result is None


@pytest.mark.parametrize(
    ("fen", "color", "as_of"),
    [
        ("not a FEN", "white", "2026-09-09"),
        (STARTING_FEN, "purple", "2026-09-09"),
        (STARTING_FEN, "white", "2026-9-9"),
        (STARTING_FEN, "white", "2026-02-30"),
    ],
)
def test_invalid_position_insight_inputs_are_rejected_before_storage_access(
    tmp_path: Path,
    fen: str,
    color: str,
    as_of: str,
) -> None:
    with pytest.raises(PositionInsightValidationError):
        PositionInsightRequest(fen, color, as_of)  # type: ignore[arg-type]

    with pytest.raises(PositionInsightValidationError):
        read_position_insight(tmp_path / "missing.db", fen, color, as_of)  # type: ignore[arg-type]


def test_missing_incompatible_and_malformed_storage_are_typed_failures(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(PositionInsightStorageError):
        read_position_insight(missing, STARTING_FEN, "white", "2026-09-09")
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    with pytest.raises(PositionInsightSchemaError):
        read_position_insight(incompatible, STARTING_FEN, "white", "2026-09-09")

    malformed = tmp_path / "malformed.db"
    malformed.write_bytes(b"not a SQLite database")
    with pytest.raises(PositionInsightStorageError):
        read_position_insight(malformed, STARTING_FEN, "white", "2026-09-09")

    database, position_id = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE derived_analysis_result SET dar_engine_name = '' WHERE derived_position_id = ?",
            (position_id,),
        )
    with pytest.raises(PositionInsightStorageError):
        read_position_insight(database, TARGET_FEN, "white", "2026-09-09")


def test_reads_are_immutable_and_do_not_create_rows_or_sidecars(tmp_path: Path) -> None:
    database, _position_id = _database(tmp_path)
    before = database.read_bytes()

    insight = PositionInsightRepository(database).read(
        PositionInsightRequest(TARGET_WITH_COUNTERS, "white", "2026-09-09")
    )

    with pytest.raises(FrozenInstanceError):
        insight.fen = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        insight.observed_moves[0] = insight.observed_moves[0]  # type: ignore[index]
    assert insight.analysis.result is not None
    with pytest.raises(TypeError):
        insight.analysis.result.settings["Hash"] = 32  # type: ignore[index]
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("insight.db-*"))
