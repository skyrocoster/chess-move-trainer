from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from backend.app.features.openings.catalogue_api_schemas import (
    OpeningCatalogueResponse,
)
from chess_move_trainer.database import create_schema

from .conftest import create_openings_database


CLIENT = TestClient(app)

_POSITIONS = {
    1: (
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "w",
        "KQkq",
        "-",
    ),
    2: (
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
        "b",
        "KQkq",
        "-",
    ),
    3: (
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR",
        "w",
        "KQkq",
        "-",
    ),
}


def _create_rebuilt_database(database: Path) -> Path:
    create_schema(database)
    with sqlite3.connect(database) as connection:
        for position_id, fields in _POSITIONS.items():
            connection.execute(
                """
                INSERT INTO derived_position
                    (dp_position_id, dp_placement, dp_side_to_move,
                     dp_castling_rights, dp_legal_en_passant)
                VALUES (?, ?, ?, ?, ?)
                """,
                (position_id, *fields),
            )
        for game_id in range(1, 4):
            connection.execute(
                """
                INSERT INTO datasource_game
                    (dg_game_id, dg_chesscom_game_uuid, dg_source_url,
                     dg_original_pgn, dg_trainer_color,
                     dg_trainer_chesscom_uuid)
                VALUES (?, ?, ?, ?, 'white', ?)
                """,
                (
                    game_id,
                    f"00000000-0000-4000-8000-{game_id:012d}",
                    f"https://example.test/{game_id}",
                    "[Result \"*\"]\n\n*",
                    "11111111-1111-4111-8111-111111111111",
                ),
            )
        connection.executemany(
            "INSERT INTO datasource_opening (do_opening_id, do_eco, do_name) VALUES (?, ?, ?)",
            (
                (1, "A00", "Alpha"),
                (2, "B10", "Beta:Study"),
                (3, "C20", "Empty"),
                (4, "D30", "Delta"),
            ),
        )
        connection.executemany(
            """
            INSERT INTO derived_opening_route
                (dor_route_id, datasource_opening_id, derived_position_id)
            VALUES (?, ?, ?)
            """,
            (
                (1, 1, 1),
                (2, 2, 1),
                (3, 2, 2),
                (4, 4, 3),
            ),
        )
        connection.executemany(
            """
            INSERT INTO derived_game_position
                (datasource_game_id, dgp_ply, derived_position_id,
                 dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number)
            VALUES (?, ?, ?, NULL, 0, 1)
            """,
            (
                (1, 1, 1),
                (1, 2, 2),
                (2, 3, 1),
                (3, 1, 3),
            ),
        )
    return database


def _use_database(monkeypatch: pytest.MonkeyPatch, database: Path) -> None:
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))


def _create_encoded_key_database(database: Path) -> Path:
    _create_rebuilt_database(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE datasource_opening SET do_name = ? WHERE do_opening_id = 3",
            ("King's + Réti Opening",),
        )
    return database


def _keys(response) -> list[str]:
    assert response.status_code == 200
    return [item["key"] for item in response.json()["items"]]


def test_clean_openings_returns_exact_flat_response_and_public_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = _create_rebuilt_database(tmp_path / "rebuilt.db")
    _use_database(monkeypatch, database)

    response = CLIENT.get("/api/openings", params={"future_filter": "ignored"})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "key": "A00:Alpha",
                "eco": "A00",
                "name": "Alpha",
                "route_count": 1,
                "games_reached": 2,
                "games_deepest": 1,
            },
            {
                "key": "B10:Beta:Study",
                "eco": "B10",
                "name": "Beta:Study",
                "route_count": 2,
                "games_reached": 2,
                "games_deepest": 1,
            },
            {
                "key": "C20:Empty",
                "eco": "C20",
                "name": "Empty",
                "route_count": 0,
                "games_reached": 0,
                "games_deepest": 0,
            },
            {
                "key": "D30:Delta",
                "eco": "D30",
                "name": "Delta",
                "route_count": 1,
                "games_reached": 1,
                "games_deepest": 1,
            },
        ],
        "page": 1,
        "page_size": 50,
        "total": 4,
        "total_pages": 1,
        "has_next": False,
    }
    assert not {"game_id", "position_id", "opening_id", "route_id"} & set(
        json.dumps(response.json()).split('"')
    )


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ({"search": " beta "}, ["B10:Beta:Study"]),
        ({"search": "20", "eco_from": " b00 ", "eco_to": " d30"}, ["C20:Empty"]),
        ({"sort": "eco_desc"}, ["D30:Delta", "C20:Empty", "B10:Beta:Study", "A00:Alpha"]),
        ({"sort": "route_count_asc"}, ["C20:Empty", "A00:Alpha", "D30:Delta", "B10:Beta:Study"]),
        ({"sort": "games_deepest_desc"}, ["A00:Alpha", "B10:Beta:Study", "D30:Delta", "C20:Empty"]),
        ({"page_size": 2, "page": 2}, ["C20:Empty", "D30:Delta"]),
        ({"page": 3, "page_size": 2}, []),
        ({"search": "not-present"}, []),
    ],
)
def test_clean_openings_maps_filters_sorts_and_pages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    query: dict[str, object],
    expected: list[str],
) -> None:
    _use_database(monkeypatch, _create_rebuilt_database(tmp_path / "rebuilt.db"))

    response = CLIENT.get("/api/openings", params=query)

    assert _keys(response) == expected
    if not expected and query.get("search") == "not-present":
        assert response.json()["total_pages"] == 0


@pytest.mark.parametrize(
    "query",
    [
        {"page": "0"},
        {"page_size": "101"},
        {"eco_from": "Z99"},
        {"eco_from": "C20", "eco_to": "B10"},
        {"sort": "unknown"},
    ],
)
def test_known_invalid_opening_filters_use_typed_422_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    query: dict[str, str],
) -> None:
    _use_database(monkeypatch, _create_rebuilt_database(tmp_path / "rebuilt.db"))

    response = CLIENT.get("/api/openings", params=query)

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_filter",
        "message": "Invalid opening filter",
    }


def test_clean_openings_uses_default_chess_db_and_stays_read_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    default_database = tmp_path / "data" / "database" / "chess.db"
    default_database.parent.mkdir(parents=True)
    _create_rebuilt_database(default_database)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(REBUILT_DATABASE_PATH_ENV, raising=False)
    before = default_database.read_bytes()

    response = CLIENT.get("/api/openings")
    detail_response = CLIENT.get("/api/openings/A00%3AAlpha")

    assert response.status_code == 200
    assert detail_response.status_code == 200
    assert default_database.read_bytes() == before
    assert not list(default_database.parent.glob("chess.db-*"))
    assert not default_database.with_name("chess.db-wal").exists()
    assert not default_database.with_name("chess.db-shm").exists()
    assert not default_database.with_name("chess.db-journal").exists()


@pytest.mark.parametrize(
    ("opening_key", "expected"),
    [
        (
            "B10:Beta:Study",
            {
                "key": "B10:Beta:Study",
                "eco": "B10",
                "name": "Beta:Study",
                "route_count": 2,
                "games_reached": 2,
                "games_deepest": 1,
            },
        ),
        (
            "C20:King's + Réti Opening",
            {
                "key": "C20:King's + Réti Opening",
                "eco": "C20",
                "name": "King's + Réti Opening",
                "route_count": 0,
                "games_reached": 0,
                "games_deepest": 0,
            },
        ),
    ],
)
def test_clean_opening_detail_returns_exact_flat_response_for_encoded_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    opening_key: str,
    expected: dict[str, object],
) -> None:
    database = (
        _create_encoded_key_database(tmp_path / "rebuilt.db")
        if "King's" in opening_key
        else _create_rebuilt_database(tmp_path / "rebuilt.db")
    )
    _use_database(monkeypatch, database)

    response = CLIENT.get(
        f"/api/openings/{quote(opening_key, safe='')}",
        params={"future_query": "ignored"},
    )

    assert response.status_code == 200
    assert response.json() == expected
    assert not {"game_id", "position_id", "opening_id", "route_id"} & set(
        json.dumps(response.json()).split('"')
    )


@pytest.mark.parametrize("opening_key", ["not-a-key", "A0:Alpha", "A00:"])
def test_clean_opening_detail_rejects_malformed_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    opening_key: str,
) -> None:
    _use_database(monkeypatch, _create_rebuilt_database(tmp_path / "rebuilt.db"))

    response = CLIENT.get(f"/api/openings/{quote(opening_key, safe='')}")

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_opening_key",
        "message": "Invalid opening key",
    }


def test_clean_opening_detail_returns_typed_404_for_absent_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _use_database(monkeypatch, _create_rebuilt_database(tmp_path / "rebuilt.db"))

    response = CLIENT.get("/api/openings/A00%3ANot%20in%20the%20catalogue")

    assert response.status_code == 404
    assert response.json() == {
        "code": "opening_not_found",
        "message": "Opening not found",
    }


def test_clean_openings_ignore_the_legacy_database_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rebuilt = _create_rebuilt_database(tmp_path / "rebuilt.db")
    legacy = tmp_path / "legacy.db"
    create_openings_database(legacy)
    _use_database(monkeypatch, rebuilt)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(legacy))

    clean_response = CLIENT.get("/api/openings")

    assert clean_response.status_code == 200
    assert _keys(clean_response) == [
        "A00:Alpha",
        "B10:Beta:Study",
        "C20:Empty",
        "D30:Delta",
    ]


def test_clean_openings_missing_or_incompatible_data_is_typed_503(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "missing.db"
    _use_database(monkeypatch, missing)
    missing_response = CLIENT.get("/api/openings")
    assert missing_response.status_code == 503
    assert missing_response.json() == {
        "code": "openings_unavailable",
        "message": "Openings unavailable",
    }
    assert not missing.exists()

    missing_detail_response = CLIENT.get("/api/openings/A00%3AAlpha")
    assert missing_detail_response.status_code == 503
    assert missing_detail_response.json() == {
        "code": "openings_unavailable",
        "message": "Openings unavailable",
    }

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE not_schema_v1 (value TEXT)")
    before = incompatible.read_bytes()
    _use_database(monkeypatch, incompatible)

    response = CLIENT.get("/api/openings")

    assert response.status_code == 503
    assert response.json() == {
        "code": "openings_unavailable",
        "message": "Openings unavailable",
    }
    assert incompatible.read_bytes() == before

    detail_response = CLIENT.get("/api/openings/A00%3AAlpha")
    assert detail_response.status_code == 503
    assert detail_response.json() == {
        "code": "openings_unavailable",
        "message": "Openings unavailable",
    }


def test_clean_openings_unexpected_failures_are_safe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import importlib

    router_module = importlib.import_module("backend.app.features.openings.router")

    _use_database(monkeypatch, _create_rebuilt_database(tmp_path / "rebuilt.db"))

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("private failure details")

    monkeypatch.setattr(router_module, "read_openings", fail)

    response = CLIENT.get("/api/openings")

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to load openings",
    }

    monkeypatch.setattr(router_module, "read_opening", fail)
    detail_response = CLIENT.get("/api/openings/A00%3AAlpha")
    assert detail_response.status_code == 500
    assert detail_response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to load opening",
    }


def test_openings_routes_and_games_routes_remain_registered_and_models_are_strict() -> None:
    routes = {
        (route.path, route.operation_id)
        for route in app.routes
        if isinstance(route, APIRoute)
    }

    assert ("/api/openings", "getOpenings") in routes
    assert ("/api/openings/{opening_key}", "getOpeningByKey") in routes
    opening_routes = [
        route.path
        for route in app.routes
        if isinstance(route, APIRoute) and route.path.startswith("/api/openings")
    ]
    assert "/api/openings/line-library" not in opening_routes
    assert ("/api/games", "getGames") in routes
    assert ("/api/games/{game_uuid}", "getGame") in routes
    with pytest.raises(ValidationError):
        OpeningCatalogueResponse(
            items=[],
            page=1,
            page_size=50,
            total=0,
            total_pages=0,
            has_next=False,
            private_id=1,
        )
