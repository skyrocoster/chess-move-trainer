from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli, create_schema
import chess_move_trainer.database.games.persistence as persistence_service
from chess_move_trainer.database.games.persistence import GameRepository, import_raw_games
from chess_move_trainer.database.openings import OpeningCatalogueRepository, load_opening_sources
from chess_move_trainer.database.rebuild import (
    RebuildConfiguration,
    RefreshStage,
    RefreshStageStatus,
    VerificationStatus,
    refresh_database,
)
import chess_move_trainer.database.rebuild.refresh as refresh_service


ROOT = Path(__file__).parents[3]
OPENING_FIXTURES = ROOT / "tests/database/openings/fixtures/catalogue-valid"
GAME_FIXTURES = ROOT / "tests/database/games/fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


def _opening_source(tmp_path: Path) -> Path:
    source = tmp_path / "openings"
    shutil.copytree(OPENING_FIXTURES, source)
    return source


def _raw_root(tmp_path: Path, *fixture_names: str) -> Path:
    root = tmp_path / "raw"
    month = root / "games" / "2026" / "08.json"
    month.parent.mkdir(parents=True)
    games = [
        json.loads((GAME_FIXTURES / fixture_name).read_text(encoding="utf-8"))
        for fixture_name in fixture_names
    ]
    month.write_text(json.dumps({"games": games}), encoding="utf-8")
    return root


def _configuration(tmp_path: Path) -> RebuildConfiguration:
    return RebuildConfiguration(tmp_path / "neighbour.db")


def _counts(database: Path) -> tuple[int, int, int, int]:
    with sqlite3.connect(database) as connection:
        return tuple(
            int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in (
                "datasource_opening",
                "derived_opening_route",
                "datasource_game",
                "derived_game_position",
            )
        )


def _database_snapshot(database: Path) -> dict[str, list[tuple[object, ...]]]:
    with sqlite3.connect(database) as connection:
        return {
            table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table}").fetchall()]
            for table in (
                "datasource_opening",
                "derived_opening_route",
                "derived_opening_route_move",
                "derived_position",
                "datasource_game",
                "derived_game_position",
            )
        }


def _stage(result: object, name: RefreshStage) -> object:
    return next(item for item in result.stages if item.stage is name)


def test_refresh_builds_empty_target_and_skips_unchanged_explicit_sources(
    tmp_path: Path,
) -> None:
    configuration = _configuration(tmp_path)
    source = _opening_source(tmp_path)
    raw_root = _raw_root(tmp_path, "game-trainer-white.json", "game-trainer-black.json")

    first = refresh_database(
        configuration,
        opening_source_dir=source,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )
    before = _database_snapshot(configuration.rebuilt_neighbour)
    second = refresh_database(
        configuration,
        opening_source_dir=source,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert first.completed
    assert second.completed
    assert _stage(second, RefreshStage.OPENINGS).status is RefreshStageStatus.SKIPPED
    assert _stage(second, RefreshStage.GAMES).status is RefreshStageStatus.SKIPPED
    assert second.verification is not None
    assert second.verification.status is VerificationStatus.REPLACEMENT_READY
    assert _database_snapshot(configuration.rebuilt_neighbour) == before


def test_refresh_reuses_one_normalized_game_batch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configuration = _configuration(tmp_path)
    raw_root = _raw_root(tmp_path, "game-trainer-white.json", "game-trainer-black.json")
    original_normalize = persistence_service.normalize_game
    normalized_uuids: list[str] = []

    def count_normalization(raw_game: object, trainer_uuid: UUID) -> object:
        result = original_normalize(raw_game, trainer_uuid)
        if result.game is not None:
            normalized_uuids.append(str(result.game.chesscom_game_uuid))
        return result

    def reject_second_raw_load(*args: object, **kwargs: object) -> object:
        raise AssertionError("refresh must not reread raw months through import_raw_months")

    monkeypatch.setattr(persistence_service, "normalize_game", count_normalization)
    monkeypatch.setattr(persistence_service, "import_raw_months", reject_second_raw_load)

    result = refresh_database(
        configuration,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert _stage(result, RefreshStage.GAMES).status is RefreshStageStatus.SUCCEEDED
    assert len(normalized_uuids) == 2


def test_opening_only_checkpoint_survives_and_later_game_input_completes_it(
    tmp_path: Path,
) -> None:
    configuration = _configuration(tmp_path)
    opening_only = refresh_database(
        configuration,
        opening_source_dir=_opening_source(tmp_path),
    )

    assert not opening_only.completed
    assert _stage(opening_only, RefreshStage.OPENINGS).status is RefreshStageStatus.SUCCEEDED
    assert _stage(opening_only, RefreshStage.GAMES).status is RefreshStageStatus.OMITTED
    assert opening_only.verification is not None
    assert opening_only.verification.openings_ready
    assert not opening_only.verification.replacement_ready

    completed = refresh_database(
        configuration,
        raw_root=_raw_root(tmp_path, "game-trainer-white.json"),
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert completed.completed
    assert _stage(completed, RefreshStage.OPENINGS).status is RefreshStageStatus.SKIPPED
    assert _stage(completed, RefreshStage.GAMES).status is RefreshStageStatus.SUCCEEDED


def test_stage_failure_does_not_block_independent_game_import(tmp_path: Path) -> None:
    configuration = _configuration(tmp_path)
    result = refresh_database(
        configuration,
        opening_source_dir=tmp_path / "missing-openings",
        raw_root=_raw_root(tmp_path, "game-trainer-white.json"),
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert not result.completed
    assert _stage(result, RefreshStage.OPENINGS).status is RefreshStageStatus.UNAVAILABLE
    assert _stage(result, RefreshStage.GAMES).status is RefreshStageStatus.SUCCEEDED
    assert _counts(configuration.rebuilt_neighbour)[2] == 1
    assert result.verification is not None
    assert result.verification.status is VerificationStatus.STRUCTURALLY_VALID_PARTIAL


def test_corrected_game_is_recomputed_on_local_rerun(tmp_path: Path) -> None:
    configuration = _configuration(tmp_path)
    first_root = _raw_root(tmp_path, "correction-valid.json")
    first = refresh_database(
        configuration,
        raw_root=first_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )
    assert not first.completed

    corrected_root = tmp_path / "corrected-raw"
    month = corrected_root / "games" / "2026" / "08.json"
    month.parent.mkdir(parents=True)
    corrected = json.loads((GAME_FIXTURES / "correction-valid.json").read_text(encoding="utf-8"))
    corrected["pgn"] = "[Event \"Synthetic corrected again\"]\n\n1. e4 e5 2. Bc4 Nc6 1-0"
    month.write_text(json.dumps({"games": [corrected]}), encoding="utf-8")

    second = refresh_database(
        configuration,
        raw_root=corrected_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert not second.completed
    assert _stage(second, RefreshStage.GAMES).status is RefreshStageStatus.SUCCEEDED
    with sqlite3.connect(configuration.rebuilt_neighbour) as connection:
        stored = connection.execute(
            "SELECT dg_original_pgn FROM datasource_game"
        ).fetchone()[0]
    assert "corrected again" in stored


def test_changed_game_does_not_rewrite_unchanged_game(tmp_path: Path) -> None:
    database = tmp_path / "per-game-refresh.db"
    create_schema(database)
    first = json.loads((GAME_FIXTURES / "game-trainer-white.json").read_text(encoding="utf-8"))
    neighbor = json.loads((GAME_FIXTURES / "game-trainer-black.json").read_text(encoding="utf-8"))
    assert import_raw_games([first, neighbor], TRAINER_UUID, GameRepository(database)).completed

    changed = dict(first)
    changed["pgn"] = '[Event "Synthetic corrected again"]\n\n1. e4 e5 2. Bc4 Nc6 1-0'
    checkpoints: list[str] = []
    result = import_raw_games(
        [changed, neighbor],
        TRAINER_UUID,
        GameRepository(database, _checkpoint=checkpoints.append),
    )

    assert result.completed
    assert result.imported_count == 2
    assert checkpoints.count("metadata") == 1
    assert _counts(database)[2] == 2


def test_changed_opening_source_republishes_instead_of_skipping(tmp_path: Path) -> None:
    configuration = _configuration(tmp_path)
    source = _opening_source(tmp_path)
    first = refresh_database(configuration, opening_source_dir=source)
    assert _stage(first, RefreshStage.OPENINGS).status is RefreshStageStatus.SUCCEEDED

    for source_file in (source / "a.tsv", source / "b.tsv"):
        source_file.write_text(
            source_file.read_text(encoding="utf-8").replace("Basic route", "Corrected route"),
            encoding="utf-8",
        )
    second = refresh_database(configuration, opening_source_dir=source)

    assert _stage(second, RefreshStage.OPENINGS).status is RefreshStageStatus.SUCCEEDED
    with sqlite3.connect(configuration.rebuilt_neighbour) as connection:
        names = [row[0] for row in connection.execute("SELECT do_name FROM datasource_opening")]
    assert "Corrected route" in names
    assert "Basic route" not in names


def test_refresh_compares_openings_without_per_route_queries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "opening-match.db"
    create_schema(database)
    source = _opening_source(tmp_path)
    routes = load_opening_sources(source)
    OpeningCatalogueRepository(database).replace(routes)
    statements: list[str] = []
    original_open_connection = refresh_service._open_connection

    class TrackingConnection:
        def __init__(self, connection: object) -> None:
            self._connection = connection

        def exec_driver_sql(self, statement: str, *args: object, **kwargs: object) -> object:
            statements.append(statement)
            return self._connection.exec_driver_sql(statement, *args, **kwargs)  # type: ignore[attr-defined]

    @contextmanager
    def tracked_open_connection(*args: object, **kwargs: object):
        with original_open_connection(*args, **kwargs) as connection:
            yield TrackingConnection(connection)

    monkeypatch.setattr(refresh_service, "_open_connection", tracked_open_connection)

    assert refresh_service._opening_source_matches(database, routes, lock_timeout=5.0)
    move_queries = [
        statement
        for statement in statements
        if "FROM derived_opening_route_move" in statement
    ]
    assert len(move_queries) == 1
    assert not any("WHERE derived_opening_route_id = ?" in statement for statement in statements)


def test_refresh_cli_reports_partial_failure_as_json_and_never_acquires(
    tmp_path: Path,
) -> None:
    configuration = _configuration(tmp_path)
    config = tmp_path / "rebuild.yaml"
    config.write_text(f"rebuilt_neighbour: {configuration.rebuilt_neighbour}\n", encoding="utf-8")
    raw_root = _raw_root(tmp_path, "game-trainer-white.json")
    runner = CliRunner()

    result = runner.invoke(
        database_cli.app,
        [
            "rebuild",
            "refresh",
            "--config",
            str(config),
            "--opening-source-dir",
            str(tmp_path / "missing-openings"),
            "--raw-root",
            str(raw_root),
            "--trainer-chesscom-uuid",
            str(TRAINER_UUID),
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["operation"] == "refresh"
    assert payload["status"] == "failed"
    assert payload["stages"][1]["status"] == "unavailable"
    assert payload["stages"][2]["status"] == "succeeded"
    assert "acquire" not in result.stdout.lower()
