from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.app.features.games.router as games_router
from backend.app.caching import GAMES_MAX_ENTRIES, GAMES_TTL_SECONDS

from .conftest import START_FEN, count_reader_calls

GAMES_PATH = "/api/games"


def test_games_namespace_bounds_match_the_plan() -> None:
    assert (GAMES_TTL_SECONDS, GAMES_MAX_ENTRIES) == (60.0, 64)


def test_games_repeat_reads_underlying_reader_once(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, games_router, "search_games")

    first = client.get(GAMES_PATH, params={"page": 1, "page_size": 50})
    second = client.get(GAMES_PATH, params={"page": 1, "page_size": 50})

    assert first.status_code == second.status_code == 200
    assert first.json()["total"] == 3
    assert len(calls) == 1
    assert first.content == second.content


def test_games_equivalent_inputs_share_one_key(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, games_router, "search_games")

    implicit = client.get(GAMES_PATH)
    explicit = client.get(
        GAMES_PATH,
        params={"page_size": 50, "page": 1, "sort": "started_at_desc"},
    )

    assert implicit.status_code == explicit.status_code == 200
    assert len(calls) == 1
    assert explicit.content == implicit.content


def test_games_distinct_filters_use_distinct_keys(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, games_router, "search_games")

    assert client.get(GAMES_PATH, params={"page": 1, "page_size": 2}).status_code == 200
    assert client.get(GAMES_PATH, params={"page": 2, "page_size": 2}).status_code == 200
    assert (
        client.get(GAMES_PATH, params={"page": 1, "page_size": 2, "sort": "length_asc"}).status_code
        == 200
    )
    assert len(calls) == 3


def test_games_error_responses_are_never_cached(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, games_router, "search_games")

    first = client.get(GAMES_PATH, params={"page": 0})
    second = client.get(GAMES_PATH, params={"page": 0})

    assert first.status_code == second.status_code == 422
    assert first.json() == second.json()
    assert calls == []


def test_preferred_move_write_invalidates_cached_games(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, games_router, "search_games")

    assert client.get(GAMES_PATH, params={"page": 1, "page_size": 50}).status_code == 200
    assert len(calls) == 1

    put_response = client.put(
        "/api/preferred-moves",
        json={
            "fen": START_FEN,
            "effective_from": "2026-06-01",
            "effective_until": "2026-07-01",
            "preference": {"kind": "move", "uci": "e2e4"},
        },
    )
    assert put_response.status_code == 200

    repeat = client.get(GAMES_PATH, params={"page": 1, "page_size": 50})
    assert repeat.status_code == 200
    assert len(calls) == 2
