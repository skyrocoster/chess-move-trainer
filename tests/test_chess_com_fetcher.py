import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.chess_com import fetch_games


def settings(tmp_path: Path, delay: float = 0) -> fetch_games.Settings:
    return fetch_games.Settings(
        "tester",
        delay,
        "https://example.test/pub",
        tmp_path / "raw",
        tmp_path / "games.db",
        tmp_path / "fetch.log",
    )


def response(status: int, body: dict, etag: str | None = None) -> fetch_games.Response:
    return fetch_games.Response(status, {"ETag": etag} if etag else {}, json.dumps(body).encode())


def game(uuid: str = "g1") -> dict:
    return {
        "uuid": uuid,
        "url": f"https://chess.test/{uuid}",
        "pgn": "[Event test]\n\n1. e4 *",
        "time_control": "600",
        "end_time": 1,
        "rated": True,
        "accuracies": {"white": 91.2, "black": 88.0},
        "tcn": "abc",
        "initial_setup": "",
        "fen": "fen",
        "time_class": "rapid",
        "rules": "chess",
        "eco": "C20",
        "white": {
            "uuid": "w",
            "username": "White",
            "@id": "https://chess.test/white",
            "rating": 1200,
            "result": "win",
        },
        "black": {
            "uuid": "b",
            "username": "Black",
            "@id": "https://chess.test/black",
            "rating": 1100,
            "result": "resigned",
        },
    }


def logger(tmp_path: Path):
    return fetch_games.configure_logging(tmp_path / "fetch.log")


def test_fetches_normalizes_and_writes_raw_data(tmp_path: Path) -> None:
    config = settings(tmp_path)
    archive = {"archives": ["https://example.test/pub/player/tester/games/2024/01"]}
    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(200, {"games": [game()]}, "tag")],
    ):
        assert fetch_games.run(config, logger(tmp_path), sleep=lambda _: None) == 0
    assert (tmp_path / "raw/archives/tester.json").exists()
    assert (tmp_path / "raw/games/2024/01.json").exists()
    with sqlite3.connect(config.database) as db:
        assert db.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 1
        assert db.execute("SELECT username, is_current, etag FROM fetch_state").fetchone() == (
            "tester",
            1,
            "tag",
        )
        assert len(db.execute("PRAGMA foreign_key_list(games)").fetchall()) == 2


def test_historical_month_is_skipped_and_current_uses_etag(tmp_path: Path) -> None:
    config = settings(tmp_path)
    archive = {
        "archives": [
            "https://example.test/pub/player/tester/games/2024/01",
            "https://example.test/pub/player/tester/games/2024/02",
        ]
    }
    calls: list[tuple[str, dict]] = []

    def fake_request(url: str, headers=None):
        calls.append((url, headers or {}))
        return (
            response(200, archive)
            if url.endswith("archives")
            else response(200, {"games": [game()]}, "tag")
        )

    with patch.object(fetch_games, "request", side_effect=fake_request):
        fetch_games.run(config, logger(tmp_path), sleep=lambda _: None)
    with patch.object(
        fetch_games, "request", side_effect=[response(200, archive), response(304, {})]
    ) as mocked:
        fetch_games.run(config, logger(tmp_path), sleep=lambda _: None)
    assert mocked.call_count == 2
    assert calls[1][1] == {}
    assert mocked.call_args_list[1].args[0].endswith("/2024/02")
    assert mocked.call_args_list[1].args[1] == {"If-None-Match": "tag"}


def test_month_filter_fetches_only_requested_archive(tmp_path: Path) -> None:
    config = settings(tmp_path)
    archive = {
        "archives": [
            "https://example.test/pub/player/tester/games/2024/01",
            "https://example.test/pub/player/tester/games/2024/02",
        ]
    }
    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(200, {"games": [game()]})],
    ) as mocked:
        assert (
            fetch_games.run(config, logger(tmp_path), month_filter=(2024, 1), sleep=lambda _: None)
            == 0
        )
    assert mocked.call_count == 2
    assert mocked.call_args_list[1].args[0].endswith("/2024/01")


def test_non_429_month_failure_continues(tmp_path: Path) -> None:
    config = settings(tmp_path)
    archive = {
        "archives": [
            "https://example.test/pub/player/tester/games/2024/01",
            "https://example.test/pub/player/tester/games/2024/02",
        ]
    }
    with patch.object(
        fetch_games,
        "request",
        side_effect=[
            response(200, archive),
            response(500, {}),
            response(200, {"games": [game("g2")]}),
        ],
    ):
        assert fetch_games.run(config, logger(tmp_path), sleep=lambda _: None) == 0
    with sqlite3.connect(config.database) as db:
        assert db.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 1


def test_429_fails_fast(tmp_path: Path) -> None:
    config = settings(tmp_path)
    archive = {
        "archives": [
            "https://example.test/pub/player/tester/games/2024/01",
            "https://example.test/pub/player/tester/games/2024/02",
        ]
    }
    with patch.object(
        fetch_games, "request", side_effect=[response(200, archive), response(429, {})]
    ):
        with pytest.raises(fetch_games.RateLimitError):
            fetch_games.run(config, logger(tmp_path), sleep=lambda _: None)


def test_duplicate_uuid_upserts(tmp_path: Path) -> None:
    config = settings(tmp_path)
    archive = {"archives": ["https://example.test/pub/player/tester/games/2024/01"]}
    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(200, {"games": [game()]})],
    ):
        fetch_games.run(config, logger(tmp_path), sleep=lambda _: None)
    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(200, {"games": [game()]})],
    ):
        fetch_games.run(config, logger(tmp_path), sleep=lambda _: None)
    with sqlite3.connect(config.database) as db:
        assert db.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 1
