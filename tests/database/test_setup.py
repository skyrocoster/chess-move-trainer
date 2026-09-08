from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from chess_move_trainer.database import lifecycle
from chess_move_trainer.database.games.acquisition import CHESSCOM_API_ORIGIN
from chess_move_trainer.database.openings.acquisition import (
    COMMIT_RESOLUTION_URL,
    OPENING_SOURCE_FILES,
    RAW_SOURCE_URL_TEMPLATE,
)


ROOT = Path(__file__).parents[2]
GAME_FIXTURES = ROOT / "tests" / "database" / "games" / "fixtures"
OPENING_FIXTURES = ROOT / "tests" / "database" / "openings" / "fixtures" / "catalogue-valid"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")
SHA = "0123456789abcdef0123456789abcdef01234567"
MONTH_URL = f"{CHESSCOM_API_ORIGIN}/pub/player/setup-test/games/2026/01"
ARCHIVE_URL = f"{CHESSCOM_API_ORIGIN}/pub/player/setup-test/games/archives"


@dataclass
class FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


class GameTransport:
    def __init__(self, games: list[dict[str, Any]]) -> None:
        self.games = games
        self.requests: list[str] = []

    def get_json(self, url: str, *, timeout: float) -> object:
        del timeout
        self.requests.append(url)
        if url == ARCHIVE_URL:
            return {"archives": [MONTH_URL]}
        if url == MONTH_URL:
            return {"games": self.games}
        raise AssertionError(f"unexpected game URL: {url}")


class OpeningTransport:
    def __init__(self) -> None:
        self.requests: list[str] = []

    def get_json(self, url: str, *, timeout: float) -> object:
        del timeout
        self.requests.append(url)
        assert url == COMMIT_RESOLUTION_URL
        return [{"sha": SHA}]

    def get_text(self, url: str, *, timeout: float) -> str:
        del timeout
        self.requests.append(url)
        filename = url.rsplit("/", 1)[-1]
        return (OPENING_FIXTURES / filename).read_text(encoding="utf-8")


def _game_fixture(name: str) -> dict[str, Any]:
    return json.loads((GAME_FIXTURES / name).read_text(encoding="utf-8"))


def _write_configuration(path: Path) -> None:
    path.write_text(
        "username: setup-test\n"
        f"trainer_chesscom_uuid: {TRAINER_UUID}\n",
        encoding="utf-8",
    )


def _setup(
    tmp_path: Path,
    *,
    game_transport: GameTransport | None = None,
    opening_transport: OpeningTransport | None = None,
) -> lifecycle.LifecycleResult:
    database_path = tmp_path / "database" / "chess.db"
    database_path.parent.mkdir(exist_ok=True)
    configuration = tmp_path / "games.yaml"
    _write_configuration(configuration)
    return lifecycle._setup_database(
        _database_path=database_path,
        _raw_root=tmp_path / "raw",
        _opening_source_dir=tmp_path / "openings",
        _games_configuration=configuration,
        _game_transport=game_transport,
        _game_clock=FixedClock(datetime(2026, 1, 15, tzinfo=UTC)),
        _opening_transport=opening_transport,
        _sleep=lambda _: None,
    )


def _snapshot_files(root: Path) -> dict[Path, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def _counts(database: Path) -> dict[str, int]:
    tables = (
        "datasource_game",
        "datasource_opening",
        "derived_game_position",
        "derived_opening_route",
        "derived_opening_route_move",
        "derived_position",
    )
    with sqlite3.connect(database) as connection:
        return {
            table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in tables
        }


def test_setup_absent_path_composes_complete_sources_and_reports_quick_checks(
    tmp_path: Path,
) -> None:
    game_transport = GameTransport(
        [_game_fixture("game-trainer-white.json"), _game_fixture("game-trainer-black.json")]
    )
    opening_transport = OpeningTransport()

    result = _setup(
        tmp_path,
        game_transport=game_transport,
        opening_transport=opening_transport,
    )
    database = tmp_path / "database" / "chess.db"

    assert result.exit_code == 0
    assert result.database_path == database
    assert result.message == (
        "Setup completed: imported 2 game(s), skipped 0; published 4 opening label(s), "
        "5 route(s), and 20 route move(s)."
    )
    assert database.is_file()
    assert game_transport.requests == [ARCHIVE_URL, MONTH_URL]
    assert opening_transport.requests == [
        COMMIT_RESOLUTION_URL,
        *[
            RAW_SOURCE_URL_TEMPLATE.format(commit=SHA, filename=filename)
            for filename in OPENING_SOURCE_FILES
        ],
    ]
    assert tuple(
        sorted(path.name for path in (tmp_path / "openings").iterdir())
    ) == OPENING_SOURCE_FILES
    assert (tmp_path / "raw" / "games" / "2026" / "01.json").is_file()


def test_setup_creates_normalized_and_owned_derived_rows(tmp_path: Path) -> None:
    _setup(
        tmp_path,
        game_transport=GameTransport(
            [_game_fixture("game-trainer-white.json"), _game_fixture("game-trainer-black.json")]
        ),
        opening_transport=OpeningTransport(),
    )

    counts = _counts(tmp_path / "database" / "chess.db")

    assert counts["datasource_game"] == 2
    assert counts["derived_game_position"] == 10
    assert counts["derived_position"] >= 9
    assert counts["datasource_opening"] == 4
    assert counts["derived_opening_route"] == 5
    assert counts["derived_opening_route_move"] == 20
    database = tmp_path / "database" / "chess.db"
    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 2
    assert not database.with_name("chess.db-wal").exists()
    assert not database.with_name("chess.db-shm").exists()


def test_setup_refuses_preexisting_database_before_any_side_effect(tmp_path: Path) -> None:
    database_root = tmp_path / "database"
    database_root.mkdir()
    database = database_root / "chess.db"
    database.write_bytes(b"pre-existing database bytes")
    (database_root / "other.db").write_bytes(b"unrelated bytes")
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    (raw_root / "sentinel.txt").write_bytes(b"raw source")
    opening_root = tmp_path / "openings"
    opening_root.mkdir()
    (opening_root / "sentinel.txt").write_bytes(b"opening source")
    before_database = database.read_bytes()
    before_tree = _snapshot_files(tmp_path)

    result = lifecycle._setup_database(
        _database_path=database,
        _raw_root=raw_root,
        _opening_source_dir=opening_root,
        _games_configuration=tmp_path / "missing.yaml",
        _game_transport=pytest.fail,
        _opening_transport=pytest.fail,
        _sleep=lambda _: None,
    )

    assert result.exit_code == 1
    assert "already exists" in result.message
    assert database.read_bytes() == before_database
    assert _snapshot_files(tmp_path) == before_tree


def test_setup_failure_after_creation_removes_only_new_database(tmp_path: Path, monkeypatch) -> None:
    database_root = tmp_path / "database"
    database_root.mkdir()
    unrelated = database_root / "other.db"
    unrelated.write_bytes(b"unrelated database")
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    raw_source = raw_root / "source.json"
    raw_source.write_bytes(b"raw source")
    opening_root = tmp_path / "openings"
    opening_root.mkdir()
    opening_source = opening_root / "source.tsv"
    opening_source.write_bytes(b"opening source")
    configuration = tmp_path / "games.yaml"
    _write_configuration(configuration)
    before_other = unrelated.read_bytes()
    before_raw = raw_source.read_bytes()
    before_opening = opening_source.read_bytes()

    def fail_after_schema(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise RuntimeError("synthetic setup failure after schema creation")

    monkeypatch.setattr(lifecycle, "acquire_months", fail_after_schema)
    result = lifecycle._setup_database(
        _database_path=database_root / "chess.db",
        _raw_root=raw_root,
        _opening_source_dir=opening_root,
        _games_configuration=configuration,
        _sleep=lambda _: None,
    )

    assert result.exit_code == 1
    assert "synthetic setup failure" in result.message
    assert not (database_root / "chess.db").exists()
    assert unrelated.read_bytes() == before_other
    assert raw_source.read_bytes() == before_raw
    assert opening_source.read_bytes() == before_opening
    assert tuple(path.name for path in database_root.iterdir()) == ("other.db",)


def test_setup_cleans_exact_stale_and_failed_database_sidecars_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_root = tmp_path / "database"
    database_root.mkdir()
    database = database_root / "chess.db"
    for suffix in ("-journal", "-wal", "-shm"):
        database.with_name(database.name + suffix).write_bytes(b"stale sidecar")
    unrelated = database_root / "chess.db.backup"
    unrelated.write_bytes(b"unrelated database")
    similarly_named = database_root / "chess.db-journal.extra"
    similarly_named.write_bytes(b"unrelated sibling")
    configuration = tmp_path / "games.yaml"
    _write_configuration(configuration)
    real_create_schema = lifecycle.create_schema

    def create_schema_after_preflight(*args: object, **kwargs: object) -> object:
        assert not any(
            database.with_name(database.name + suffix).exists()
            for suffix in ("-journal", "-wal", "-shm")
        )
        return real_create_schema(*args, **kwargs)

    def fail_bulk_import(*args: object, **kwargs: object) -> object:
        del args
        assert kwargs["bulk"] is True
        for suffix in ("-journal", "-wal", "-shm"):
            database.with_name(database.name + suffix).write_bytes(b"new sidecar")
        raise RuntimeError("synthetic bulk import failure")

    monkeypatch.setattr(lifecycle, "create_schema", create_schema_after_preflight)
    monkeypatch.setattr(lifecycle, "import_raw_months", fail_bulk_import)
    result = lifecycle._setup_database(
        _database_path=database,
        _raw_root=tmp_path / "raw",
        _opening_source_dir=tmp_path / "openings",
        _games_configuration=configuration,
        _game_transport=GameTransport([_game_fixture("game-trainer-white.json")]),
        _game_clock=FixedClock(datetime(2026, 1, 15, tzinfo=UTC)),
        _sleep=lambda _: None,
    )

    assert result.exit_code == 1
    assert "synthetic bulk import failure" in result.message
    assert not database.exists()
    assert not any(database.with_name(database.name + suffix).exists() for suffix in ("-journal", "-wal", "-shm"))
    assert unrelated.read_bytes() == b"unrelated database"
    assert similarly_named.read_bytes() == b"unrelated sibling"


def test_setup_uses_direct_internal_services_without_stockfish_or_legacy_delegation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    events: list[str] = []
    real_game_acquire = lifecycle.acquire_months
    real_game_import = lifecycle.import_raw_months
    real_opening_acquire = lifecycle.acquire_openings
    real_opening_import = lifecycle.import_opening_catalogue

    def game_acquire(*args: object, **kwargs: object) -> object:
        events.append("game acquisition")
        return real_game_acquire(*args, **kwargs)

    def game_import(*args: object, **kwargs: object) -> object:
        events.append("game import")
        assert kwargs["bulk"] is True
        return real_game_import(*args, **kwargs)

    def opening_acquire(*args: object, **kwargs: object) -> object:
        events.append("opening acquisition")
        return real_opening_acquire(*args, **kwargs)

    def opening_import(*args: object, **kwargs: object) -> object:
        events.append("opening import")
        return real_opening_import(*args, **kwargs)

    monkeypatch.setattr(lifecycle, "acquire_months", game_acquire)
    monkeypatch.setattr(lifecycle, "import_raw_months", game_import)
    monkeypatch.setattr(lifecycle, "acquire_openings", opening_acquire)
    monkeypatch.setattr(lifecycle, "import_opening_catalogue", opening_import)

    result = _setup(
        tmp_path,
        game_transport=GameTransport(
            [_game_fixture("game-trainer-white.json"), _game_fixture("game-trainer-black.json")]
        ),
        opening_transport=OpeningTransport(),
    )

    source = (ROOT / "src" / "chess_move_trainer" / "database" / "lifecycle.py").read_text(
        encoding="utf-8"
    ).lower()
    assert result.exit_code == 0
    assert events == [
        "game acquisition",
        "game import",
        "opening acquisition",
        "opening import",
    ]
    assert "stockfish" not in source
    assert "subprocess" not in source
    assert "database.cli" not in source
