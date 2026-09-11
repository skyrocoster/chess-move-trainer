from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest

from chess_move_trainer.database import create_schema, lifecycle
from chess_move_trainer.database.games.persistence import GameRepository, import_raw_games
from chess_move_trainer.database.openings.acquisition import (
    COMMIT_RESOLUTION_URL,
    OPENING_SOURCE_FILES,
    RAW_SOURCE_URL_TEMPLATE,
    OpeningAcquisitionError,
)
from chess_move_trainer.database.openings.persistence import (
    OpeningCatalogueRepository,
    import_opening_catalogue,
)
from chess_move_trainer.database.openings.source import load_opening_sources

ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "database"
OPENING_FIXTURES = FIXTURES / "openings" / "fixtures"
GAME_FIXTURES = FIXTURES / "games" / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")
SHA = "0123456789abcdef0123456789abcdef01234567"


class OpeningTransport:
    def __init__(
        self,
        files: dict[str, str],
        failures: dict[str, BaseException] | None = None,
    ) -> None:
        self.files = files
        self.failures = failures or {}
        self.events: list[tuple[str, str, float]] = []

    def get_json(self, url: str, *, timeout: float) -> object:
        self.events.append(("json", url, timeout))
        failure = self.failures.get(url)
        if failure is not None:
            raise failure
        assert url == COMMIT_RESOLUTION_URL
        return [{"sha": SHA}]

    def get_text(self, url: str, *, timeout: float) -> str:
        self.events.append(("text", url, timeout))
        failure = self.failures.get(url)
        if failure is not None:
            raise failure
        return self.files[url]


def _latest_files() -> dict[str, str]:
    return {
        RAW_SOURCE_URL_TEMPLATE.format(commit=SHA, filename=filename): (
            OPENING_FIXTURES / "acquisition-valid" / filename
        ).read_text(encoding="utf-8")
        for filename in OPENING_SOURCE_FILES
    }


def _copy_sources(tmp_path: Path) -> Path:
    source_dir = tmp_path / "openings"
    shutil.copytree(OPENING_FIXTURES / "catalogue-valid", source_dir)
    return source_dir


def _fixture_game(name: str) -> dict[str, object]:
    return json.loads((GAME_FIXTURES / name).read_text(encoding="utf-8"))


def _source_snapshot(source_dir: Path) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in source_dir.iterdir()
        if path.is_file()
    }


def _catalogue_snapshot(database: Path) -> dict[str, list[tuple[object, ...]]]:
    with sqlite3.connect(database) as connection:
        return {
            table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table}")]
            for table in (
                "datasource_opening",
                "derived_opening_route",
                "derived_opening_route_move",
                "derived_position",
            )
        }


def _game_snapshot(database: Path) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    with sqlite3.connect(database) as connection:
        return (
            [tuple(row) for row in connection.execute("SELECT * FROM datasource_game")],
            [
                tuple(row)
                for row in connection.execute(
                    "SELECT * FROM derived_game_position ORDER BY datasource_game_id, dgp_ply"
                )
            ],
        )


def test_update_openings_publishes_complete_latest_catalogue_and_leaves_games_untouched(
    tmp_path: Path,
) -> None:
    database = tmp_path / "chess.db"
    source_dir = _copy_sources(tmp_path)
    create_schema(database)
    import_opening_catalogue(source_dir, OpeningCatalogueRepository(database))
    import_raw_games(
        [_fixture_game("game-trainer-white.json")],
        TRAINER_UUID,
        GameRepository(database),
    )
    before_games = _game_snapshot(database)
    (source_dir / "notes.txt").write_bytes(b"keep unrelated source note")
    transport = OpeningTransport(_latest_files())
    delays: list[float] = []

    result = lifecycle._update_openings(
        _database_path=database,
        _opening_source_dir=source_dir,
        _opening_transport=transport,
        _sleep=delays.append,
    )

    assert result.exit_code == 0
    assert result.operation is lifecycle.LifecycleOperation.UPDATE_OPENINGS
    assert "5 opening label(s)" in result.message
    assert "5 route(s)" in result.message
    assert transport.events == [
        ("json", COMMIT_RESOLUTION_URL, 30.0),
        *[
            ("text", RAW_SOURCE_URL_TEMPLATE.format(commit=SHA, filename=filename), 30.0)
            for filename in OPENING_SOURCE_FILES
        ],
    ]
    assert delays == [0.25] * 5
    assert _source_snapshot(source_dir) == {
        **{
            filename: (OPENING_FIXTURES / "acquisition-valid" / filename).read_bytes()
            for filename in OPENING_SOURCE_FILES
        },
        "notes.txt": b"keep unrelated source note",
    }
    assert _game_snapshot(database) == before_games

    routes = load_opening_sources(source_dir)
    assert len(routes) == 5
    with sqlite3.connect(database) as connection:
        labels = connection.execute(
            "SELECT do_eco, do_name FROM datasource_opening ORDER BY do_eco, do_name"
        ).fetchall()
        route_endpoints = connection.execute(
            """
            SELECT p.dp_placement, p.dp_side_to_move,
                   p.dp_castling_rights, p.dp_legal_en_passant
            FROM derived_opening_route AS r
            JOIN derived_position AS p ON p.dp_position_id = r.derived_position_id
            ORDER BY r.dor_route_id
            """
        ).fetchall()
    assert len(labels) == 5
    assert len(route_endpoints) == 5
    assert set(route_endpoints) == {route.endpoint_key for route in routes}
    assert not any(path.name.startswith(".openings-staging-") for path in tmp_path.iterdir())
    assert not any(
        marker in path.name.casefold()
        for path in source_dir.iterdir()
        for marker in ("commit", "revision", "manifest", "history")
    )


@pytest.mark.parametrize("failure_kind", ["invalid", "incomplete"])
def test_update_openings_preserves_source_and_catalogue_before_publication(
    tmp_path: Path,
    failure_kind: str,
) -> None:
    database = tmp_path / "chess.db"
    source_dir = _copy_sources(tmp_path)
    create_schema(database)
    import_opening_catalogue(source_dir, OpeningCatalogueRepository(database))
    before_source = _source_snapshot(source_dir)
    before_catalogue = _catalogue_snapshot(database)
    files = _latest_files()
    failures: dict[str, BaseException] = {}
    if failure_kind == "invalid":
        invalid_url = RAW_SOURCE_URL_TEMPLATE.format(commit=SHA, filename="a.tsv")
        files[invalid_url] = (
            OPENING_FIXTURES / "acquisition-invalid-pgn" / "a.tsv"
        ).read_text(encoding="utf-8")
    else:
        failed_url = RAW_SOURCE_URL_TEMPLATE.format(commit=SHA, filename="d.tsv")
        failures[failed_url] = OpeningAcquisitionError("synthetic incomplete response")
    transport = OpeningTransport(files, failures)

    result = lifecycle._update_openings(
        _database_path=database,
        _opening_source_dir=source_dir,
        _opening_transport=transport,
        _sleep=lambda _: None,
    )

    assert result.exit_code == 1
    assert "Update openings failed" in result.message
    assert _source_snapshot(source_dir) == before_source
    assert _catalogue_snapshot(database) == before_catalogue
    assert not any(path.name.startswith(".openings-staging-") for path in tmp_path.iterdir())
