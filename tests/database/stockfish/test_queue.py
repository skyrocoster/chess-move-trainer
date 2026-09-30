from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

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
    BackgroundSeedReason,
    QueueCompletionOutcome,
    QueueQualityError,
    QueueService,
)
from chess_move_trainer.database.stockfish.configuration import profile_for

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
    configuration_version: int | None = None,
    roots: tuple[tuple[str, ...], ...] = OLD_ROOTS,
    engine_version: str = "engine-1",
):
    profile = profile_for(quality)
    if configuration_version is None:
        configuration_version = profile.configuration_version
    if quality is AnalysisQuality.BROWSER and roots == OLD_ROOTS:
        roots = roots[:1]
    return validate_analysis_result(
        quality=quality,
        configuration_version=configuration_version,
        settings=dict(profile.settings),
        engine_name="queue-test-engine",
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

    assert claim.quality is AnalysisQuality.BROWSER
    assert _queue_row(database_path, position_id) == (
        "tool",
        "running",
        "2026-01-01T00:00:02.000000Z",
        claim.claimed_at_utc,
        claim.claim_token,
    )


def test_claim_is_fifo_and_replaces_a_stale_token_with_fresh_uuid(tmp_path: Path) -> None:
    database_path, second_position = _setup(tmp_path)
    first_position = PositionRepository(database_path).resolve_fen(
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    )
    queue = QueueService(database_path)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    # The older request has a higher position ID and is enqueued last.
    queue.enqueue(
        second_position, AnalysisQuality.BROWSER, requested_at=origin + timedelta(seconds=1)
    )
    queue.enqueue(first_position, AnalysisQuality.BROWSER, requested_at=origin)

    first_claim = queue.claim(now=origin + timedelta(seconds=2))
    assert first_claim is not None
    assert first_claim.position_id == first_position

    second_claim = queue.claim(now=origin + timedelta(seconds=3))
    assert second_claim is not None
    assert second_claim.position_id == second_position
    assert queue.release(second_claim)

    stale_reclaim = queue.claim(now=origin + timedelta(seconds=122))
    assert stale_reclaim is not None
    assert stale_reclaim.position_id == first_position
    assert stale_reclaim.claim_token != first_claim.claim_token
    assert UUID(stale_reclaim.claim_token).version == 4
    assert stale_reclaim.claimed_at_utc == "2026-01-01T00:02:02.000000Z"
    assert stale_reclaim.quality is AnalysisQuality.BROWSER


def test_stale_token_cas_is_rejected_for_release_delete_and_complete(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=now)
    old_claim = queue.claim(now=now)
    assert old_claim is not None
    assert queue.release(old_claim)
    current_claim = queue.claim(now=now + timedelta(seconds=2))
    assert current_claim is not None
    assert current_claim.claim_token != old_claim.claim_token

    assert not queue.release(old_claim)
    assert not queue.delete(old_claim)
    stale = queue.complete(old_claim, _result())
    assert stale == QueueCompletionOutcome(applied=False)
    assert _queue_row(database_path, position_id) == (
        "browser",
        "running",
        "2026-01-01T00:00:00.000000Z",
        current_claim.claimed_at_utc,
        current_claim.claim_token,
    )
    assert _stored_analysis(database_path, position_id) is None


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
    # A repeated failure from the old owner must not discard the promoted request.
    assert not queue.fail(promoted_claim)
    assert _queue_row(database_path, position_id) == (
        "tool",
        "queued",
        "2026-01-01T00:00:03.000000Z",
        None,
        None,
    )


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
        2,
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
    assert _stored_analysis(database_path, position_id) == ("browser", 2, "engine-1")


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
        queue.complete(
            claim,
            _result(quality=AnalysisQuality.TOOL, engine_version="engine-2"),
        )

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
        assert connection.execute("SELECT COUNT(*) FROM derived_analysis_result").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM derived_analysis_line").fetchone()[0] == 0
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM derived_analysis_queue WHERE daq_claim_token = ?",
                (claim.claim_token,),
            ).fetchone()[0]
            == 1
        )


def test_background_seed_claims_one_browser_row_atomically_and_only_when_empty(
    tmp_path: Path,
) -> None:
    database_path, position_id = _setup(tmp_path)
    second_position = PositionRepository(database_path).resolve_fen(
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    )
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue = QueueService(database_path, _token_factory=lambda: "background-token")

    claim = queue.seed_and_claim_background(position_id, now=now)

    assert claim is not None
    assert claim.position_id == position_id
    assert claim.quality is AnalysisQuality.BROWSER
    assert claim.claim_token == "background-token"
    assert _queue_row(database_path, position_id) == (
        "browser",
        "running",
        "2026-01-01T00:00:00.000000Z",
        claim.claimed_at_utc,
        "background-token",
    )
    assert queue.seed_and_claim_background(second_position, now=now) is None
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_analysis_queue").fetchone()[0] == 1


def test_background_seed_leaves_existing_requested_work_untouched(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    requested_position = PositionRepository(database_path).resolve_fen(
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    )
    now = datetime(2026, 1, 1, tzinfo=UTC)
    queue = QueueService(database_path)
    queue.enqueue(requested_position, AnalysisQuality.TOOL, requested_at=now)

    assert queue.seed_and_claim_background(position_id, now=now) is None
    claim = queue.claim(now=now)

    assert claim is not None
    assert claim.position_id == requested_position
    assert claim.quality is AnalysisQuality.TOOL


def test_background_capacity_allows_six_claims_and_rejects_a_seventh(tmp_path: Path) -> None:
    database_path = tmp_path / "capacity.db"
    create_schema(database_path)
    positions = PositionRepository(database_path)
    fens = (
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/6P1/8/PPPPPP1P/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/1P6/8/P1PPPPPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/7P/8/PPPPPPP1/RNBQKBNR b KQkq - 0 1",
    )
    position_ids = [positions.resolve_fen(fen) for fen in fens]
    queue = QueueService(database_path)

    claims = [
        queue.seed_and_claim_background(position_id, capacity=6) for position_id in position_ids[:6]
    ]
    outcome = queue.try_seed_and_claim_background(position_ids[6], capacity=6)

    assert all(claim is not None for claim in claims)
    assert outcome.claim is None
    assert outcome.reason is BackgroundSeedReason.AT_CAPACITY
    with sqlite3.connect(database_path) as connection:
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM derived_analysis_queue WHERE daq_state = 'running'"
            ).fetchone()[0]
            == 6
        )


def test_background_seed_skips_duplicate_candidate_and_current_result(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    queue = QueueService(database_path)

    first = queue.seed_and_claim_background(position_id, capacity=6)
    duplicate = queue.try_seed_and_claim_background(position_id, capacity=6)
    assert first is not None
    assert duplicate.reason is BackgroundSeedReason.SKIP_CANDIDATE

    assert queue.complete(first, _result(engine_version="19")).applied
    current = queue.try_seed_and_claim_background(position_id, capacity=6)
    assert current.reason is BackgroundSeedReason.SKIP_CANDIDATE


def test_queued_requested_work_blocks_background_capacity_six(tmp_path: Path) -> None:
    database_path, position_id = _setup(tmp_path)
    requested_position = PositionRepository(database_path).resolve_fen(
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    )
    queue = QueueService(database_path)
    queue.enqueue(requested_position, AnalysisQuality.TOOL)

    outcome = queue.try_seed_and_claim_background(position_id, capacity=6)

    assert outcome.claim is None
    assert outcome.reason is BackgroundSeedReason.BLOCKED_REQUESTED
