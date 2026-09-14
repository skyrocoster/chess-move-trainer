from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import importlib

import backend.app.features.openings.router as openings_router

# NOTE: see test_training_cache.py — the package __init__ shadows `.router`.
training_router = importlib.import_module(
    "backend.app.features.position_training_requirements.router"
)

from .conftest import (
    OPENINGS_PARAMS,
    START_FEN,
    TRAINING_PARAMS,
    UNSEEN_FEN,
    count_reader_calls,
)

OPENINGS_PATH = "/api/openings"
TRAINING_PATH = "/api/positions/training-requirements"


def test_openings_repeat_reads_underlying_reader_once(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, openings_router, "read_openings")

    first = client.get(OPENINGS_PATH, params=OPENINGS_PARAMS)
    second = client.get(OPENINGS_PATH, params={**OPENINGS_PARAMS, "page_size": 50})

    assert first.status_code == second.status_code == 200
    assert len(calls) == 1
    assert first.content == second.content


def test_opening_detail_repeat_and_missing_key_behavior(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, openings_router, "read_opening")

    detail = client.get(f"{OPENINGS_PATH}/{quote('A00:Cache Opening', safe='')}")
    assert detail.status_code == 200
    repeat = client.get(f"{OPENINGS_PATH}/{quote('A00:Cache Opening', safe='')}")
    assert repeat.status_code == 200
    assert len(calls) == 1
    assert repeat.content == detail.content

    missing = client.get(f"{OPENINGS_PATH}/{quote('E99:No Such Opening', safe='')}")
    assert missing.status_code == 404
    missing_again = client.get(f"{OPENINGS_PATH}/{quote('E99:No Such Opening', safe='')}")
    assert missing_again.status_code == 404
    # A missing key must never populate the cache: the reader runs again.
    assert len(calls) == 3


def test_put_and_delete_preferred_moves_invalidate_cached_reads(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    openings_calls = count_reader_calls(monkeypatch, openings_router, "read_openings")
    training_calls = count_reader_calls(
        monkeypatch, training_router, "discover_training_requirements"
    )

    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert len(openings_calls) == 1
    assert len(training_calls) == 1

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

    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert len(openings_calls) == 2
    assert len(training_calls) == 2

    delete_response = client.request(
        "DELETE",
        "/api/preferred-moves",
        json={"fen": UNSEEN_FEN, "effective_from": "2026-06-01"},
    )
    assert delete_response.status_code == 200

    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert len(openings_calls) == 3
    assert len(training_calls) == 3


def test_failed_writes_do_not_invalidate_cached_reads(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, openings_router, "read_openings")

    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert len(calls) == 1

    rejected = client.put(
        "/api/preferred-moves",
        json={
            "fen": "not a fen",
            "effective_from": "2026-06-01",
            "preference": {"kind": "move", "uci": "e2e4"},
        },
    )
    assert rejected.status_code == 422

    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert len(calls) == 1
