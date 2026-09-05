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


def _line(rank: int, pv: tuple[str, ...], *, score_value: int | None = None) -> AnalysisLine:
    return AnalysisLine(
        rank=rank,
        score_kind=AnalysisScoreKind.CP,
        score_value=rank if score_value is None else score_value,
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
    settings: dict[str, object] | None = None,
    engine_name: str = "normalized-test-engine",
    engine_version: str = "engine-1",
    lines: tuple[AnalysisLine, ...] | None = None,
):
    return validate_analysis_result(
        quality=quality,
        configuration_version=configuration_version,
        settings={"Threads": 1, "Hash": 16} if settings is None else settings,
        engine_name=engine_name,
        engine_version=engine_version,
        lines=_lines() if lines is None else lines,
    )


def _repository(tmp_path: Path) -> tuple[Path, AnalysisRepository, int]:
    database_path = tmp_path / "analysis.db"
    create_schema(database_path)
    position_id = PositionRepository(database_path).resolve_fen(STARTING_FEN)
    return database_path, AnalysisRepository(database_path), position_id


def _stored_result(database_path: Path, position_id: int) -> tuple[tuple[object, ...] | None, list[tuple[object, ...]]]:
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


def test_publication_requires_an_existing_position_and_never_creates_one(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "existing-only.db"
    create_schema(database_path)
    repository = AnalysisRepository(database_path)

    with pytest.raises(AnalysisValidationError, match="does not exist"):
        repository.publish(42, _result())

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0
        assert (
            connection.execute("SELECT COUNT(*) FROM derived_analysis_result").fetchone()[0]
            == 0
        )


def test_first_publication_persists_exact_parent_and_complete_lines(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    result = _result()

    assert repository.publish(position_id, result) == PublicationOutcome.saved_result()

    parent, lines = _stored_result(database_path, position_id)
    assert parent == (
        position_id,
        "tool",
        1,
        '{"Hash":16,"Threads":1}',
        "normalized-test-engine",
        "engine-1",
        None,
    )
    assert [
        (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            json.loads(row[7]),
            row[8],
        )
        for row in lines
    ] == [
        (position_id, rank, "cp", rank, 400, 300, 300, list(pv), 12)
        for rank, pv in enumerate(OLD_ROOTS, start=1)
    ]


def test_one_current_result_is_replaced_by_a_new_same_quality_version(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)

    assert repository.publish(position_id, _result()) .saved
    assert repository.publish(
        position_id,
        _result(configuration_version=2, lines=_lines(NEW_ROOTS)),
    ).saved

    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_result WHERE derived_position_id = ?",
            (position_id,),
        ).fetchone()[0] == 1


def test_tool_replaces_browser_but_browser_cannot_downgrade_it(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)

    assert repository.publish(
        position_id, _result(quality=AnalysisQuality.BROWSER)
    ).saved
    assert repository.publish(position_id, _result(quality=AnalysisQuality.TOOL)).saved
    outcome = repository.publish(
        position_id,
        _result(
            quality=AnalysisQuality.BROWSER,
            configuration_version=9,
            engine_version="engine-9",
            lines=_lines(NEW_ROOTS),
        ),
    )

    assert outcome == PublicationOutcome.not_saved(NotSavedReason.LOWER_QUALITY)
    parent, lines = _stored_result(database_path, position_id)
    assert parent is not None
    assert parent[1:3] == ("tool", 1)
    assert [row[7] for row in lines] == [json.dumps(pv, separators=(",", ":")) for pv in OLD_ROOTS]


def test_identical_same_quality_configuration_and_engine_is_not_saved(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved
    before = _stored_result(database_path, position_id)

    outcome = repository.publish(
        position_id,
        _result(lines=_lines(NEW_ROOTS)),
    )

    assert outcome == PublicationOutcome.not_saved(NotSavedReason.DUPLICATE)
    assert _stored_result(database_path, position_id) == before


def test_same_quality_configuration_version_change_refreshes_result(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved

    assert repository.publish(
        position_id,
        _result(configuration_version=2, lines=_lines(NEW_ROOTS)),
    ) == PublicationOutcome.saved_result()

    parent, _ = _stored_result(database_path, position_id)
    assert parent is not None
    assert parent[2:4] == (2, '{"Hash":16,"Threads":1}')


def test_same_quality_engine_version_change_refreshes_result(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved

    assert repository.publish(
        position_id,
        _result(engine_version="engine-2", lines=_lines(NEW_ROOTS)),
    ) == PublicationOutcome.saved_result()

    parent, _ = _stored_result(database_path, position_id)
    assert parent is not None
    assert parent[5] == "engine-2"


def test_replacement_removes_every_old_line_and_commits_only_new_lines(
    tmp_path: Path,
) -> None:
    database_path, repository, position_id = _repository(tmp_path)
    assert repository.publish(position_id, _result()).saved

    replacement = _result(configuration_version=2, lines=_lines(NEW_ROOTS))
    assert repository.publish(position_id, replacement).saved

    _, lines = _stored_result(database_path, position_id)
    assert [json.loads(row[7]) for row in lines] == [list(pv) for pv in NEW_ROOTS]
    assert len(lines) == len(NEW_ROOTS)


def test_old_committed_result_remains_visible_until_replacement_commits(
    tmp_path: Path,
) -> None:
    database_path, _, position_id = _repository(tmp_path)
    original = AnalysisRepository(database_path)
    assert original.publish(position_id, _result()).saved

    replaced = threading.Event()
    release = threading.Event()
    errors: list[BaseException] = []

    def checkpoint(name: str) -> None:
        if name == "replaced":
            replaced.set()
            if not release.wait(5.0):
                raise RuntimeError("timed out waiting to release replacement")

    replacement_repository = AnalysisRepository(database_path, _checkpoint=checkpoint)

    def publish() -> None:
        try:
            replacement_repository.publish(
                position_id,
                _result(configuration_version=2, lines=_lines(NEW_ROOTS)),
            )
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=publish, daemon=True)
    worker.start()
    try:
        assert replaced.wait(5.0), "replacement did not reach its pre-commit checkpoint"
        parent, lines = _stored_result(database_path, position_id)
        assert parent is not None
        assert parent[2] == 1
        assert [json.loads(row[7]) for row in lines] == [list(pv) for pv in OLD_ROOTS]
    finally:
        release.set()
    worker.join(timeout=5.0)

    assert not worker.is_alive()
    assert errors == []
    parent, _ = _stored_result(database_path, position_id)
    assert parent is not None
    assert parent[2] == 2
