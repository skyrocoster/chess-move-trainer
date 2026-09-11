from __future__ import annotations

import copy
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from chess_move_trainer.database import create_schema, lifecycle
from chess_move_trainer.database.games.acquisition import CHESSCOM_API_ORIGIN
from chess_move_trainer.database.games.persistence import GameRepository, import_raw_games

ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "database" / "games" / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")
ARCHIVE_URL = f"{CHESSCOM_API_ORIGIN}/pub/player/update-test/games/archives"


@dataclass
class FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


class Transport:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requests: list[str] = []

    def get_json(self, url: str, *, timeout: float) -> object:
        del timeout
        self.requests.append(url)
        response = self.responses[url]
        if isinstance(response, BaseException):
            raise response
        return response


def _fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _month_url(month: int) -> str:
    return f"{CHESSCOM_API_ORIGIN}/pub/player/update-test/games/2026/{month:02d}"


def _write_config(path: Path) -> None:
    path.write_text(
        "username: update-test\n"
        f"trainer_chesscom_uuid: {TRAINER_UUID}\n"
        "request_delay: 0\n",
        encoding="utf-8",
    )


def _write_month(raw_root: Path, month: int, envelope: object) -> Path:
    path = raw_root / "games" / "2026" / f"{month:02d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope), encoding="utf-8")
    return path


def _count(database: Path, table: str) -> int:
    with sqlite3.connect(database) as connection:
        return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _game_url(database: Path, game_uuid: str) -> str | None:
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT dg_source_url FROM datasource_game WHERE dg_chesscom_game_uuid = ?",
            (game_uuid,),
        ).fetchone()
    return None if row is None else str(row[0])


def test_update_refetches_newest_fills_gaps_persists_independently_and_reports_skips(
    tmp_path: Path,
) -> None:
    database = tmp_path / "database" / "chess.db"
    database.parent.mkdir()
    create_schema(database)
    raw_root = tmp_path / "raw"
    configuration = tmp_path / "games.yaml"
    _write_config(configuration)

    original_white = _fixture("game-trainer-white.json")
    retained_omitted = _fixture("game-trainer-black.json")
    import_raw_games(
        [original_white, retained_omitted],
        TRAINER_UUID,
        GameRepository(database),
    )
    _write_month(raw_root, 7, {"games": [original_white, retained_omitted]})

    corrected_white = copy.deepcopy(original_white)
    corrected_white["url"] = "https://www.chess.com/game/live/update-corrected"
    valid_gap_game = _fixture("game-nullable-metadata.json")
    month_8 = {
        "games": [
            valid_gap_game,
            _fixture("game-malformed-pgn.json"),
            _fixture("game-illegal-pgn.json"),
            _fixture("game-non-standard.json"),
        ]
    }
    month_9 = {"games": "incomplete response"}
    urls = {month: _month_url(month) for month in (7, 8, 9)}
    transport = Transport(
        {
            ARCHIVE_URL: {"archives": [urls[7], urls[8], urls[9]]},
            urls[7]: {"games": [corrected_white]},
            urls[8]: month_8,
            urls[9]: month_9,
        }
    )

    result = lifecycle._update_games(
        _database_path=database,
        _raw_root=raw_root,
        _games_configuration=configuration,
        _game_transport=transport,
        _game_clock=FixedClock(datetime(2026, 9, 15, tzinfo=UTC)),
        _sleep=lambda _: None,
    )

    assert result.exit_code == 1
    assert result.operation is lifecycle.LifecycleOperation.UPDATE_GAMES
    assert transport.requests == [ARCHIVE_URL, urls[7], urls[8], urls[9]]
    assert "dddddddd-dddd-4ddd-8ddd-ddddddddddd6" in result.message
    assert "illegal or malformed move" in result.message
    assert "non-standard game rules" in result.message
    assert "2026-09" in result.message
    assert _game_url(database, original_white["uuid"]) == corrected_white["url"]
    assert _game_url(database, retained_omitted["uuid"]) == retained_omitted["url"]
    assert _game_url(database, valid_gap_game["uuid"]) == valid_gap_game["url"]
    assert _count(database, "datasource_game") == 3
    assert _count(database, "derived_game_position") >= 3
    assert (raw_root / "games" / "2026" / "07.json").is_file()
    assert (raw_root / "games" / "2026" / "08.json").is_file()
    assert not (raw_root / "games" / "2026" / "09.json").exists()
    with sqlite3.connect(database) as connection:
        table_names = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert not any(
        marker in name.casefold()
        for name in table_names
        for marker in ("fetch", "state", "run", "manifest", "recovery")
    )


def test_update_validates_before_replacing_saved_newest_month(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw"
    old = {"synthetic": "prior", "games": []}
    target = _write_month(raw_root, 8, old)
    original = target.read_bytes()
    configuration = tmp_path / "games.yaml"
    _write_config(configuration)
    url = _month_url(8)
    transport = Transport(
        {
            ARCHIVE_URL: {"archives": [url]},
            url: {"games": {"not": "a list"}},
        }
    )

    from chess_move_trainer.database.games.acquisition import acquire_incremental_months
    from chess_move_trainer.database.games.configuration import load_acquire_configuration

    result = acquire_incremental_months(
        load_acquire_configuration(configuration),
        raw_root,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert not result.completed
    assert result.failures[0].month == "2026-08"
    assert target.read_bytes() == original


def test_update_uses_the_saved_month_ledger_and_does_not_fetch_without_one(
    tmp_path: Path,
) -> None:
    database = tmp_path / "database.db"
    create_schema(database)
    raw_root = tmp_path / "raw"
    configuration = tmp_path / "games.yaml"
    _write_config(configuration)
    transport = Transport({ARCHIVE_URL: {"archives": []}})

    result = lifecycle._update_games(
        _database_path=database,
        _raw_root=raw_root,
        _games_configuration=configuration,
        _game_transport=transport,
        _game_clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        _sleep=lambda _: None,
    )

    assert result.exit_code == 1
    assert "no saved monthly game file" in result.message
    assert transport.requests == [ARCHIVE_URL]
