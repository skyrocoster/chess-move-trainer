from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisScoreKind,
    AnalysisStorageError,
    PublicationOutcome,
    validate_analysis_result,
)
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import (
    QueueCompletionOutcome,
    QueueQualityError,
    QueueService,
)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
OLD_ROOTS = (
    ("e7e5", "g1f3"),
    ("c7c5", "g1f3"),
    ("e7e6", "d2d4"),
    ("c7c6", "d2d4"),
    ("d7d5", "e4d5"),
)
NEW_ROOTS = (
    ("e7e5", "g1f3"),
    ("c7c5", "d2d4"),
    ("e7e6", "g1f3"),
    ("c7c6", "g1f3"),
    ("d7d6", "g1f3"),
)


def _result(
    *,
    quality: AnalysisQuality = AnalysisQuality.BROWSER,
    configuration_version: int = 1,
    roots: tuple[tuple[str, ...], ...] = OLD_ROOTS,
):
    return validate_analysis_result(
        quality=quality,
        configuration_version=configuration_version,
        settings={"Hash": 16},
        engine_name="queue-test-engine",
        engine_version="engine-1",
        lines=tuple(
            AnalysisLine(
                rank=rank,
                score_kind=AnalysisScoreKind.CP,
                score_value=rank,
                wdl_wins=400,
                wdl_draws=300,
                wdl_losses=300,
                pv_uci=pv,
                depth=12,
            )
            for rank, pv in enumerate(roots, start=1)
        ),
    )


def _setup(tmp_path: Path) -> tuple[Path, int]:
    database_path = tmp_path / "queue.db"
    create_schema(database_path)
    position_id = PositionRepository(database_path).resolve_fen(STARTING_FEN)
    return database_path, position_id


def _queue_row(database_path: Path, position_id: int) -> tuple[object, ...] | None:
    with sqlite3.connect(database_path) as connection:
        return connection.execute(
            """
            SELECT daq_requested_quality, daq_state, daq_requested_at_utc,
                   daq_claimed_at_utc, daq_claim_token
            FROM derived_analysis_queue
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()


def _stored_analysis(database_path: Path, position_id: int) -> tuple[object, ...] | None:
    with sqlite3.connect(database_path) as connection:
        return connection.execute(
            """
            SELECT dar_quality, dar_configuration_version, dar_engine_version
            FROM derived_analysis_result
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()


def test_enqueue_promotes_quality_without_destroying_a_running_claim(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    first = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=first)
    claim = queue.claim(now=first + timedelta(seconds=1))
    assert claim is not None

    queue.enqueue(
        position_id,
        AnalysisQuality.TOOL,
        requested_at=first + timedelta(seconds=2),
    )

    row = _queue_row(database_path, position_id)
    assert row is not None
    assert row[0:2] == ("tool", "running")
    assert row[3:] == (claim.claimed_at_utc, claim.claim_token)


def test_claim_is_fifo_and_replaces_a_stale_token_with_fresh_uuid(tmp_path: Path) -> None:
    database_path, first_position = _setup(tmp_path)
    second_position = PositionRepository(database_path).resolve_fen(
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    )
    queue = QueueService(database_path)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(first_position, AnalysisQuality.BROWSER, requested_at=origin)
    queue.enqueue(
        second_position, AnalysisQuality.BROWSER, requested_at=origin + timedelta(seconds=1)
    )

    first_claim = queue.claim(now=origin + timedelta(seconds=2))
    assert first_claim is not None
    assert first_claim.position_id == first_position

    second_claim = queue.claim(now=origin + timedelta(seconds=3))
    assert second_claim is not None
    assert second_claim.position_id == second_position
    assert queue.release(second_claim)

    stale_reclaim = queue.claim(now=origin + timedelta(minutes=3))
    assert stale_reclaim is not None
    assert stale_reclaim.position_id == first_position
    assert stale_reclaim.claim_token != first_claim.claim_token
    assert stale_reclaim.quality is AnalysisQuality.BROWSER


def test_stale_token_cas_is_rejected_for_release_delete_and_complete(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    old_claim = queue.claim(now=now)
    assert old_claim is not None
    assert queue.release(old_claim)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now + timedelta(seconds=1))
    current_claim = queue.claim(now=now + timedelta(seconds=2))
    assert current_claim is not None

    assert not queue.release(old_claim)
    assert not queue.delete(old_claim)
    stale = queue.complete(old_claim, _result())
    assert stale == QueueCompletionOutcome(applied=False)
    assert _queue_row(database_path, position_id) is not None
    assert _stored_analysis(database_path, position_id) is None
    assert queue.release(current_claim)


def test_matching_failure_deletes_or_releases_promoted_work(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    claim = queue.claim(now=now)
    assert claim is not None
    assert queue.fail(claim)
    assert _queue_row(database_path, position_id) is None

    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now + timedelta(seconds=1))
    promoted_claim = queue.claim(now=now + timedelta(seconds=2))
    assert promoted_claim is not None
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=now + timedelta(seconds=3))
    assert queue.fail(promoted_claim)
    row = _queue_row(database_path, position_id)
    assert row is not None
    assert row[0:2] == ("tool", "queued")
    assert row[3:] == (None, None)


def test_completion_publishes_and_deletes_matching_claim_in_one_lifecycle(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    claim = queue.claim(now=now)
    assert claim is not None

    outcome = queue.complete(claim, _result())

    assert outcome.applied
    assert outcome.deleted
    assert not outcome.released
    assert outcome.publication == PublicationOutcome.saved_result()
    assert _queue_row(database_path, position_id) is None
    assert _stored_analysis(database_path, position_id) == (
        "browser",
        1,
        "engine-1",
    )


def test_browser_completion_after_tool_promotion_publishes_then_releases(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    claim = queue.claim(now=now)
    assert claim is not None
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=now + timedelta(seconds=1))

    outcome = queue.complete(claim, _result())

    assert outcome.applied
    assert outcome.released
    assert not outcome.deleted
    assert outcome.publication == PublicationOutcome.saved_result()
    row = _queue_row(database_path, position_id)
    assert row is not None
    assert row[0:2] == ("tool", "queued")
    assert row[3:] == (None, None)
    assert _stored_analysis(database_path, position_id) == ("browser", 1, "engine-1")


def test_completion_rollback_keeps_queue_and_previous_complete_result(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    initial = AnalysisRepository(database_path)
    assert initial.publish(position_id, _result(quality=AnalysisQuality.TOOL)).saved
    before = _stored_analysis(database_path, position_id)
    queue = QueueService(
        database_path,
        _checkpoint=lambda name: (
            (_ for _ in ()).throw(RuntimeError("injected queue publication failure"))
            if name == "parent_replaced"
            else None
        ),
    )
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=now)
    claim = queue.claim(now=now)
    assert claim is not None

    with pytest.raises(AnalysisStorageError):
        queue.complete(claim, _result(quality=AnalysisQuality.TOOL, configuration_version=2))

    assert _stored_analysis(database_path, position_id) == before
    row = _queue_row(database_path, position_id)
    assert row is not None
    assert row[1] == "running"
    assert row[4] == claim.claim_token


def test_completion_rejects_quality_mismatch_without_mutation(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    claim = queue.claim(now=now)
    assert claim is not None

    with pytest.raises(QueueQualityError):
        queue.complete(claim, _result(quality=AnalysisQuality.TOOL))

    assert _stored_analysis(database_path, position_id) is None
    row = _queue_row(database_path, position_id)
    assert row is not None
    assert row[1] == "running"


def test_failed_publication_does_not_leave_partial_lines(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    claim = queue.claim(now=now)
    assert claim is not None

    with pytest.raises(AnalysisStorageError):
        QueueService(
            database_path,
            _checkpoint=lambda name: (
                (_ for _ in ()).throw(RuntimeError("partial publication failure"))
                if name == "parent_replaced"
                else None
            ),
        ).complete(claim, _result())

    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_result"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_line"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_queue WHERE daq_claim_token = ?",
            (claim.claim_token,),
        ).fetchone()[0] == 1
