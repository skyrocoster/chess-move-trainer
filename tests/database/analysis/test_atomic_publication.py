from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisScoreKind,
    AnalysisStorageError,
    AnalysisValidationError,
    NotSavedReason,
    PublicationOutcome,
    validate_analysis_result,
)
from chess_move_trainer.database.positions import PositionRepository

STARTING_FEN = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
)
OLD_ROOTS = (
    ("e2e4", "e7e5"),
    ("d2d4", "d7d5"),
    ("g1f3", "g8f6"),
    ("c2c4", "e7e5"),
    ("b1c3", "b8c6"),
)
NEW_ROOTS = (
    ("a2a3", "a7a6"),
    ("a2a4", "a7a5"),
    ("b2b3", "b7b6"),
    ("b2b4", "b7b5"),
    ("g2g3", "g7g6"),
)


def _line(rank: int, pv: tuple[str, ...]) -> AnalysisLine:
    return AnalysisLine(
        rank=rank,
        score_kind=AnalysisScoreKind.CP,
        score_value=rank,
        wdl_wins=400,
        wdl_draws=300,
        wdl_losses=300,
        pv_uci=pv,
        depth=12,
    )


def _lines(roots: tuple[tuple[str, ...], ...] = OLD_ROOTS) -> tuple[AnalysisLine, ...]:
    return tuple(_line(rank, pv) for rank, pv in enumerate(roots, start=1))


def _result(
    *,
    quality: AnalysisQuality = AnalysisQuality.TOOL,
    configuration_version: int = 1,
    engine_version: str = "engine-1",
    lines: tuple[AnalysisLine, ...] | None = None,
):
    return validate_analysis_result(
        quality=quality,
        configuration_version=configuration_version,
        settings={"Hash": 16},
        engine_name="atomic-test-engine",
        engine_version=engine_version,
        lines=_lines() if lines is None else lines,
    )


def _repository(tmp_path: Path) -> tuple[Path, AnalysisRepository, int]:
    database_path = tmp_path / "analysis.db"
    create_schema(database_path)
    position_id = PositionRepository(database_path).resolve_fen(STARTING_FEN)
    return database_path, AnalysisRepository(database_path), position_id


def _snapshot(
    database_path: Path, position_id: int
) -> tuple[tuple[object, ...] | None, list[tuple[object, ...]]]:
    with sqlite3.connect(database_path) as connection:
        parent = connection.execute(
            """
            SELECT derived_position_id, dar_quality, dar_configuration_version,
                   dar_settings_json, dar_engine_name, dar_engine_version,
                   dar_terminal_kind
            FROM derived_analysis_result
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()
        lines = connection.execute(
            """
            SELECT derived_analysis_result_id, dal_rank, dal_score_kind,
                   dal_score_value, dal_wdl_wins, dal_wdl_draws,
                   dal_wdl_losses, dal_pv_uci_json, dal_depth
            FROM derived_analysis_line
            WHERE derived_analysis_result_id = ?
            ORDER BY dal_rank
            """,
            (position_id,),
        ).fetchall()
    return parent, lines


def test_replacement_failure_after_parent_write_restores_exact_old_result_and_lines(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved
    before = _snapshot(database_path, position_id)

    def checkpoint(name: str) -> None:
        if name == "parent_replaced":
            raise RuntimeError("injected replacement failure")

    failing = AnalysisRepository(database_path, _checkpoint=checkpoint)
    with pytest.raises(AnalysisStorageError):
        failing.publish(
            position_id,
            _result(configuration_version=2, lines=_lines(NEW_ROOTS)),
        )

    assert _snapshot(database_path, position_id) == before


def test_first_publication_failure_leaves_no_parent_or_child_rows(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)

    def checkpoint(name: str) -> None:
        if name == "parent_replaced":
            raise RuntimeError("injected first-publication failure")

    failing = AnalysisRepository(database_path, _checkpoint=checkpoint)
    with pytest.raises(AnalysisStorageError):
        failing.publish(position_id, _result())

    parent, lines = _snapshot(database_path, position_id)
    assert parent is None
    assert lines == []


def test_transaction_recheck_lower_quality_interleaving_is_deterministic(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(
        position_id, _result(quality=AnalysisQuality.BROWSER)
    ).saved
    ready = threading.Event()
    release = threading.Event()

    def checkpoint(name: str) -> None:
        if name == "before_lock":
            ready.set()
            if not release.wait(5.0):
                raise RuntimeError("timed out waiting to release candidate")

    candidate = AnalysisRepository(database_path, _checkpoint=checkpoint)
    outcomes: list[PublicationOutcome] = []
    errors: list[BaseException] = []

    def publish_candidate() -> None:
        try:
            outcomes.append(
                candidate.publish(
                    position_id,
                    _result(
                        quality=AnalysisQuality.BROWSER,
                        lines=_lines(NEW_ROOTS),
                    ),
                )
            )
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=publish_candidate, daemon=True)
    worker.start()
    try:
        assert ready.wait(5.0)
        assert repository.publish(position_id, _result(lines=_lines(NEW_ROOTS))).saved
    finally:
        release.set()
    worker.join(timeout=5.0)

    assert not worker.is_alive()
    assert errors == []
    assert outcomes == [PublicationOutcome.not_saved(NotSavedReason.LOWER_QUALITY)]
    parent, lines = _snapshot(database_path, position_id)
    assert parent is not None
    assert parent[1:3] == ("tool", 1)
    assert [json.loads(row[7]) for row in lines] == [list(pv) for pv in NEW_ROOTS]


def test_transaction_recheck_rejects_duplicate_published_while_candidate_waits(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    ready = threading.Event()
    release = threading.Event()

    def checkpoint(name: str) -> None:
        if name == "before_lock":
            ready.set()
            if not release.wait(5.0):
                raise RuntimeError("timed out waiting to release candidate")

    candidate = AnalysisRepository(database_path, _checkpoint=checkpoint)
    outcomes: list[PublicationOutcome] = []
    errors: list[BaseException] = []

    def publish_candidate() -> None:
        try:
            outcomes.append(
                candidate.publish(
                    position_id,
                    _result(lines=_lines(NEW_ROOTS)),
                )
            )
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=publish_candidate, daemon=True)
    worker.start()
    try:
        assert ready.wait(5.0)
        assert repository.publish(position_id, _result()).saved
    finally:
        release.set()
    worker.join(timeout=5.0)

    assert not worker.is_alive()
    assert errors == []
    assert outcomes == [PublicationOutcome.not_saved(NotSavedReason.DUPLICATE)]
    parent, lines = _snapshot(database_path, position_id)
    assert parent is not None
    assert parent[2] == 1
    assert [json.loads(row[7]) for row in lines] == [list(pv) for pv in OLD_ROOTS]


def test_successful_refresh_replaces_the_complete_old_line_set_exactly(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved

    assert repository.publish(
        position_id,
        _result(configuration_version=2, engine_version="engine-2", lines=_lines(NEW_ROOTS)),
    ) == PublicationOutcome.saved_result()

    parent, lines = _snapshot(database_path, position_id)
    assert parent == (
        position_id,
        "tool",
        2,
        '{"Hash":16}',
        "atomic-test-engine",
        "engine-2",
        None,
    )
    assert [
        (row[1], row[2], row[3], row[4], row[5], row[6], json.loads(row[7]), row[8])
        for row in lines
    ] == [
        (rank, "cp", rank, 400, 300, 300, list(pv), 12)
        for rank, pv in enumerate(NEW_ROOTS, start=1)
    ]


def test_invalid_submission_fails_before_publication_and_preserves_complete_data(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved
    before = _snapshot(database_path, position_id)
    checkpoints: list[str] = []
    invalid_lines = list(_lines())
    invalid_lines[0] = _line(1, ("e2e5",))
    validating = AnalysisRepository(
        database_path, _checkpoint=lambda name: checkpoints.append(name)
    )

    with pytest.raises(AnalysisValidationError):
        validating.publish(
            position_id,
            _result(configuration_version=2, lines=tuple(invalid_lines)),
        )

    assert checkpoints == []
    assert _snapshot(database_path, position_id) == before


def test_failure_checkpoint_is_private_and_does_not_add_public_or_persisted_state(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert not hasattr(repository, "checkpoint")
    assert not hasattr(repository, "connection")
    assert not hasattr(repository, "raw_connection")

    def checkpoint(name: str) -> None:
        if name == "parent_replaced":
            raise RuntimeError("injected private-seam failure")

    with pytest.raises(AnalysisStorageError):
        AnalysisRepository(database_path, _checkpoint=checkpoint).publish(
            position_id, _result()
        )

    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_result"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_line"
        ).fetchone()[0] == 0
