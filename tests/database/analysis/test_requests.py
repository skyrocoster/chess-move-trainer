from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisObservationState,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisRequest,
    AnalysisRequestDisposition,
    AnalysisRequestRepository,
    AnalysisRequestStorageError,
    AnalysisRequestValidationError,
    AnalysisScoreKind,
    request_analysis,
    validate_analysis_result,
)
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import QueueService


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_WITH_COUNTERS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 37 19"
NOVEL_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 17 8"
NOVEL_CANONICAL_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
ROOTS = (
    ("e2e4", "e7e5"),
    ("d2d4", "d7d5"),
    ("g1f3", "g8f6"),
    ("c2c4", "e7e5"),
    ("b1c3", "b8c6"),
)


def _result(
    *,
    quality: AnalysisQuality = AnalysisQuality.BROWSER,
    configuration_version: int = 1,
    engine_version: str = "18",
):
    return validate_analysis_result(
        quality=quality,
        configuration_version=configuration_version,
        settings={"Hash": 1024, "MultiPV": 5, "Nodes": 200000},
        engine_name="Stockfish",
        engine_version=engine_version,
        lines=tuple(
            AnalysisLine(
                rank=rank,
                score_kind=AnalysisScoreKind.CP,
                score_value=rank,
                wdl_wins=400,
                wdl_draws=300,
                wdl_losses=300,
                pv_uci=pv,
                depth=20,
            )
            for rank, pv in enumerate(ROOTS, start=1)
        ),
    )


def _database(tmp_path: Path) -> Path:
    database = tmp_path / "requests.db"
    create_schema(database)
    return database


def _position_with_result(
    database: Path,
    *,
    quality: AnalysisQuality = AnalysisQuality.BROWSER,
    configuration_version: int = 1,
    engine_version: str = "18",
) -> int:
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    assert AnalysisRepository(database).publish(
        position_id,
        _result(
            quality=quality,
            configuration_version=configuration_version,
            engine_version=engine_version,
        ),
    ).saved
    return position_id


def _queue_row(database: Path, position_id: int) -> tuple[object, ...] | None:
    with sqlite3.connect(database) as connection:
        return connection.execute(
            """
            SELECT daq_requested_quality, daq_state, daq_requested_at_utc,
                   daq_claimed_at_utc, daq_claim_token
            FROM derived_analysis_queue
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()


def test_novel_fen_is_canonicalized_and_created_with_one_queue_row(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    outcome = request_analysis(database, NOVEL_FEN)

    assert outcome.disposition is AnalysisRequestDisposition.ENQUEUED
    assert outcome.observation.fen == NOVEL_CANONICAL_FEN
    assert outcome.observation.state is AnalysisObservationState.QUEUED
    assert outcome.observation.result is None
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM derived_analysis_queue").fetchone()[0] == 1


def test_current_result_reuse_is_read_only_and_higher_quality_satisfies_browser(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    position_id = _position_with_result(
        database,
        quality=AnalysisQuality.TOOL,
        configuration_version=99,
        engine_version="old-stockfish",
    )
    before = database.read_bytes()

    outcome = request_analysis(database, STARTING_WITH_COUNTERS)

    assert outcome.disposition is AnalysisRequestDisposition.RESULT_REUSED
    assert outcome.observation.fen == STARTING_FEN
    assert outcome.observation.state is AnalysisObservationState.READY
    assert outcome.observation.result is not None
    assert outcome.observation.result.quality is AnalysisQuality.TOOL
    assert database.read_bytes() == before
    assert _queue_row(database, position_id) is None


def test_stale_equal_quality_result_is_visible_while_refresh_is_queued(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    position_id = _position_with_result(
        database,
        quality=AnalysisQuality.BROWSER,
        configuration_version=99,
        engine_version="old-stockfish",
    )

    outcome = request_analysis(database, STARTING_FEN, AnalysisQuality.BROWSER)

    assert outcome.disposition is AnalysisRequestDisposition.ENQUEUED
    assert outcome.observation.state is AnalysisObservationState.QUEUED
    assert outcome.observation.result is not None
    assert _queue_row(database, position_id) is not None


def test_live_work_is_reused_or_promoted_without_losing_an_active_claim(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    queue = QueueService(database)
    queue.enqueue(position_id, AnalysisQuality.BROWSER)
    claim = queue.claim()
    assert claim is not None

    reused = request_analysis(database, STARTING_FEN, AnalysisQuality.BROWSER)
    promoted = request_analysis(database, STARTING_FEN, AnalysisQuality.TOOL)

    assert reused.disposition is AnalysisRequestDisposition.LIVE_REUSED
    assert reused.observation.state is AnalysisObservationState.RUNNING
    assert promoted.disposition is AnalysisRequestDisposition.PROMOTED
    assert promoted.observation.state is AnalysisObservationState.RUNNING
    row = _queue_row(database, position_id)
    assert row is not None
    assert row[0:2] == ("tool", "running")
    assert row[3:] == (claim.claimed_at_utc, claim.claim_token)

    higher_reuse = request_analysis(database, STARTING_FEN, AnalysisQuality.BROWSER)
    assert higher_reuse.disposition is AnalysisRequestDisposition.LIVE_REUSED
    assert higher_reuse.observation.state is AnalysisObservationState.RUNNING
    assert _queue_row(database, position_id)[3:] == (
        claim.claimed_at_utc,
        claim.claim_token,
    )


def test_position_and_queue_creation_roll_back_together_on_transaction_failure(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    def fail(name: str) -> None:
        if name == "before_commit":
            raise RuntimeError("injected request failure")

    with pytest.raises(AnalysisRequestStorageError):
        AnalysisRequestRepository(database, _checkpoint=fail).request(NOVEL_FEN)

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM derived_analysis_queue").fetchone()[0] == 0


def test_invalid_inputs_are_rejected_before_database_access(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(AnalysisRequestValidationError):
        AnalysisRequest("not a FEN")
    with pytest.raises(AnalysisRequestValidationError):
        AnalysisRequest(STARTING_FEN, "not-a-quality")  # type: ignore[arg-type]
    with pytest.raises(AnalysisRequestValidationError):
        request_analysis(missing, "not a FEN")
    assert not missing.exists()


def test_malformed_queue_or_result_is_a_typed_storage_failure(tmp_path: Path) -> None:
    database = _database(tmp_path)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', 'broken', '2026-09-09T00:00:00Z', NULL, NULL)
            """,
            (position_id,),
        )

    with pytest.raises(AnalysisRequestStorageError):
        request_analysis(database, STARTING_FEN)

    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM derived_analysis_queue")
        connection.execute(
            """
            INSERT INTO derived_analysis_result (
                derived_position_id, dar_quality, dar_configuration_version,
                dar_settings_json, dar_engine_name, dar_engine_version, dar_terminal_kind
            ) VALUES (?, 'browser', 1, '{}', '', '18', NULL)
            """,
            (position_id,),
        )

    with pytest.raises(AnalysisRequestStorageError):
        request_analysis(database, STARTING_FEN)


def test_locked_database_is_a_typed_storage_failure(tmp_path: Path) -> None:
    database = _database(tmp_path)
    locker = sqlite3.connect(database, timeout=0.1)
    locker.execute("BEGIN EXCLUSIVE")
    try:
        with pytest.raises(AnalysisRequestStorageError):
            request_analysis(database, STARTING_FEN, lock_timeout=0.05)
    finally:
        locker.rollback()
        locker.close()


def test_concurrent_mixed_quality_requests_create_one_position_and_queue_row(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    def request(quality: AnalysisQuality):
        return request_analysis(database, NOVEL_FEN, quality)

    with ThreadPoolExecutor(max_workers=6) as executor:
        outcomes = list(
            executor.map(
                request,
                (
                    AnalysisQuality.BROWSER,
                    AnalysisQuality.TOOL,
                    AnalysisQuality.BROWSER,
                    AnalysisQuality.TOOL,
                    AnalysisQuality.BROWSER,
                    AnalysisQuality.TOOL,
                ),
            )
        )

    assert all(outcome.observation.fen == NOVEL_CANONICAL_FEN for outcome in outcomes)
    assert all(
        outcome.observation.state is AnalysisObservationState.QUEUED
        for outcome in outcomes
    )
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM derived_analysis_queue").fetchone()[0] == 1
        assert connection.execute(
            "SELECT daq_requested_quality FROM derived_analysis_queue"
        ).fetchone()[0] == "tool"
