from __future__ import annotations

import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisObservationRequest,
    AnalysisObservationSchemaError,
    AnalysisObservationState,
    AnalysisObservationStorageError,
    AnalysisObservationValidationError,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisScoreKind,
    read_analysis_observation,
    validate_analysis_result,
)
from chess_move_trainer.database.positions import PositionRepository

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_WITH_COUNTERS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 99 120"
UNSEEN_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 17 8"
UNSEEN_CANONICAL_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
QUEUED_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
ROOTS = (
    ("e2e4", "e7e5"),
    ("d2d4", "d7d5"),
    ("g1f3", "g8f6"),
    ("c2c4", "e7e5"),
    ("b1c3", "b8c6"),
)


def _result():
    return validate_analysis_result(
        quality=AnalysisQuality.TOOL,
        configuration_version=7,
        settings={"Hash": 16, "Threads": 1},
        engine_name="observation-test-engine",
        engine_version="engine-7",
        lines=tuple(
            AnalysisLine(
                rank=rank,
                score_kind=AnalysisScoreKind.CP,
                score_value=rank * 10,
                wdl_wins=400,
                wdl_draws=300,
                wdl_losses=300,
                pv_uci=pv,
                depth=22,
            )
            for rank, pv in enumerate(ROOTS, start=1)
        ),
    )


def _database(tmp_path: Path) -> tuple[Path, int]:
    database = tmp_path / "observation.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    assert AnalysisRepository(database).publish(position_id, _result()).saved
    return database, position_id


def _queue(
    database: Path,
    position_id: int,
    state: str,
    *,
    claim_token: str | None = None,
) -> None:
    with sqlite3.connect(database) as connection:
        if state == "queued" and claim_token is not None:
            connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', ?, '2026-09-09T00:00:00Z', ?, ?)
            """,
            (
                position_id,
                state,
                None if state == "queued" else "2026-09-09T00:01:00Z",
                claim_token,
            ),
        )


def test_existing_and_unseen_fens_are_canonical_sparse_read_only_observations(
    tmp_path: Path,
) -> None:
    database, position_id = _database(tmp_path)
    before = database.read_bytes()

    existing = read_analysis_observation(database, STARTING_WITH_COUNTERS)
    unseen = read_analysis_observation(database, UNSEEN_FEN)

    assert existing.fen == STARTING_FEN
    assert existing.state is AnalysisObservationState.READY
    assert existing.result is not None
    assert not hasattr(existing, "position_id")
    assert not hasattr(existing.result, "position_id")
    assert (
        existing.result.quality,
        existing.result.configuration_version,
        existing.result.settings,
        existing.result.engine_name,
        existing.result.engine_version,
        existing.result.terminal_kind,
    ) == (
        AnalysisQuality.TOOL,
        7,
        {"Hash": 16, "Threads": 1},
        "observation-test-engine",
        "engine-7",
        None,
    )
    assert [
        (
            line.rank,
            line.score_kind,
            line.score_value,
            line.wdl_wins,
            line.wdl_draws,
            line.wdl_losses,
            line.pv_uci,
            line.depth,
        )
        for line in existing.result.lines
    ] == [
        (rank, AnalysisScoreKind.CP, rank * 10, 400, 300, 300, pv, 22)
        for rank, pv in enumerate(ROOTS, start=1)
    ]
    assert unseen == read_analysis_observation(database, UNSEEN_FEN)
    assert unseen.fen == UNSEEN_CANONICAL_FEN
    assert unseen.state is AnalysisObservationState.NOT_REQUESTED
    assert unseen.result is None
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("observation.db-*"))
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM derived_analysis_result WHERE derived_position_id = ?",
                (position_id,),
            ).fetchone()[0]
            == 1
        )


def test_observation_uses_running_queued_ready_not_requested_precedence_and_coexists_with_result(
    tmp_path: Path,
) -> None:
    database, target_position = _database(tmp_path)
    queued_position = PositionRepository(database).resolve_fen(QUEUED_FEN)

    assert read_analysis_observation(database, STARTING_FEN).state == "ready"
    _queue(database, target_position, "queued")
    queued_with_result = read_analysis_observation(database, STARTING_FEN)
    assert queued_with_result.state == "queued"
    assert queued_with_result.result is not None

    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE derived_analysis_queue SET daq_state = 'running', "
            "daq_claimed_at_utc = '2026-09-09T00:01:00Z', daq_claim_token = 'claim'"
        )
    running_with_result = read_analysis_observation(database, STARTING_FEN)
    assert running_with_result.state == "running"
    assert running_with_result.result is not None

    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM derived_analysis_queue")
    assert read_analysis_observation(database, STARTING_FEN).state == "ready"

    _queue(database, queued_position, "queued")
    queued_without_result = read_analysis_observation(database, QUEUED_FEN)
    assert queued_without_result.state == "queued"
    assert queued_without_result.result is None

    assert read_analysis_observation(database, UNSEEN_FEN).state == "not_requested"


@pytest.mark.parametrize(
    "fen",
    [
        "not a FEN",
        STARTING_FEN.rsplit(" ", 2)[0],
        b"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ],
)
def test_invalid_observation_fens_are_rejected_before_storage_access(
    tmp_path: Path, fen: object
) -> None:
    with pytest.raises(AnalysisObservationValidationError):
        AnalysisObservationRequest(fen)  # type: ignore[arg-type]

    with pytest.raises(AnalysisObservationValidationError):
        read_analysis_observation(tmp_path / "missing.db", fen)  # type: ignore[arg-type]


def test_missing_incompatible_malformed_and_invalid_storage_are_typed_failures(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(AnalysisObservationStorageError):
        read_analysis_observation(missing, STARTING_FEN)
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    with pytest.raises(AnalysisObservationSchemaError):
        read_analysis_observation(incompatible, STARTING_FEN)

    malformed = tmp_path / "malformed.db"
    malformed.write_bytes(b"not a SQLite database")
    with pytest.raises(AnalysisObservationStorageError):
        read_analysis_observation(malformed, STARTING_FEN)

    database, position_id = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE derived_analysis_result SET dar_engine_name = '' "
            "WHERE derived_position_id = ?",
            (position_id,),
        )
    with pytest.raises(AnalysisObservationStorageError):
        read_analysis_observation(database, STARTING_FEN)

    queue_database = tmp_path / "malformed-queue.db"
    create_schema(queue_database)
    queue_position = PositionRepository(queue_database).resolve_fen(STARTING_FEN)
    _queue(queue_database, queue_position, "queued", claim_token="unexpected")
    with pytest.raises(AnalysisObservationStorageError):
        read_analysis_observation(queue_database, STARTING_FEN)


def test_observation_values_are_immutable_and_have_no_private_database_handles(
    tmp_path: Path,
) -> None:
    database, _position_id = _database(tmp_path)
    observation = read_analysis_observation(database, STARTING_FEN)

    with pytest.raises(FrozenInstanceError):
        observation.fen = "changed"  # type: ignore[misc]
    assert observation.result is not None
    with pytest.raises(FrozenInstanceError):
        observation.result.configuration_version = 8  # type: ignore[misc]
    with pytest.raises(TypeError, match="immutable"):
        observation.result.settings["Hash"] = 32  # type: ignore[index]
    with pytest.raises(TypeError):
        observation.result.lines[0] = observation.result.lines[0]  # type: ignore[index]
    assert not hasattr(observation, "connection")
    assert not hasattr(observation.result, "raw_connection")


def test_incomplete_current_result_is_rejected_without_fallback(tmp_path: Path) -> None:
    database, position_id = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "DELETE FROM derived_analysis_line WHERE derived_analysis_result_id = ? "
            "AND dal_rank = 5",
            (position_id,),
        )

    with pytest.raises(AnalysisObservationStorageError):
        read_analysis_observation(database, STARTING_FEN)
