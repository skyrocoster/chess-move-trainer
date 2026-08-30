from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.features.openings.contract import encode_catalog_node_id

from .conftest import MANIFEST, create_openings_database


def _catalog_id(source_file: str, row: int) -> str:
    from backend.app.features.openings.contract import CatalogIdentity

    return encode_catalog_node_id(CatalogIdentity(MANIFEST, source_file, row))


def _body_for(response) -> dict:
    assert response.status_code == 200
    return response.json()


def test_line_library_returns_complete_normalized_hierarchy_and_declarations(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _database = api_context

    body = _body_for(client.get("/api/openings/line-library"))

    root_id = _catalog_id("a.tsv", 1)
    family_id = _catalog_id("a.tsv", 2)
    leaf_id = _catalog_id("a.tsv", 3)
    other_id = _catalog_id("b.tsv", 1)
    not_mine_id = _catalog_id("c.tsv", 1)
    assert set(body) == {
        "roots",
        "nodes",
        "filters",
        "filter_apply_mode",
        "sorts",
        "selection_limit",
    }
    assert body["nodes"][root_id]["kind"] == "group"
    assert body["nodes"][family_id]["kind"] == "group"
    assert body["nodes"][leaf_id]["kind"] == "line"
    assert body["nodes"][other_id]["kind"] == "line"
    assert body["nodes"][not_mine_id]["kind"] == "line"
    assert family_id in body["nodes"][root_id]["child_ids"]
    assert leaf_id in body["nodes"][family_id]["child_ids"]
    assert body["filter_apply_mode"] == "immediate"
    assert [item["key"] for item in body["filters"]] == [
        "search",
        "eco",
        "appears_in_my_games",
    ]
    assert body["filters"][1]["type"] == "range"
    assert body["filters"][2]["metadata"] == {"scope": "fixed accepted corpus"}
    assert body["sorts"] == [
        {"key": "default", "label": "Default", "default": True, "direction": "asc"}
    ]
    assert body["selection_limit"] is None


def test_line_library_uses_arbitrary_depth_and_deterministic_transposition_references(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _database = api_context

    first = _body_for(client.get("/api/openings/line-library"))
    second = _body_for(client.get("/api/openings/line-library"))

    assert first == second
    references = [node for node in first["nodes"].values() if node["kind"] == "reference"]
    assert len(references) == 2
    assert all(node["selectable"] is False for node in references)
    assert {node["target_id"] for node in references} == {
        _catalog_id("a.tsv", 3),
        _catalog_id("b.tsv", 1),
    }
    assert all(node["child_ids"] == [] for node in references)
    assert all(node["target_id"] in first["nodes"] for node in references)


def test_search_filter_returns_matching_lines_and_required_ancestors(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _database = api_context

    body = _body_for(client.get("/api/openings/line-library", params={"search": "leaf"}))

    assert _catalog_id("a.tsv", 3) in body["nodes"]
    assert _catalog_id("a.tsv", 2) in body["nodes"]
    assert _catalog_id("a.tsv", 1) in body["nodes"]
    assert _catalog_id("b.tsv", 1) not in body["nodes"]
    assert _catalog_id("c.tsv", 1) not in body["nodes"]


def test_eco_range_filter_is_applied_by_the_provider(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _database = api_context

    body = _body_for(
        client.get(
            "/api/openings/line-library",
            params={"eco_from": "A01", "eco_to": "A02"},
        )
    )

    assert _catalog_id("a.tsv", 2) in body["nodes"]
    assert _catalog_id("a.tsv", 3) in body["nodes"]
    assert _catalog_id("a.tsv", 1) in body["nodes"]
    assert _catalog_id("b.tsv", 1) not in body["nodes"]
    assert _catalog_id("c.tsv", 1) not in body["nodes"]


def test_appears_in_my_games_uses_only_the_fixed_accepted_corpus(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _database = api_context

    body = _body_for(
        client.get(
            "/api/openings/line-library",
            params={"appears_in_my_games": "true"},
        )
    )

    assert _catalog_id("a.tsv", 3) in body["nodes"]
    assert _catalog_id("b.tsv", 1) in body["nodes"]
    assert _catalog_id("a.tsv", 1) in body["nodes"]
    assert _catalog_id("a.tsv", 2) in body["nodes"]
    assert _catalog_id("c.tsv", 1) not in body["nodes"]


def test_invalid_filter_and_unknown_sort_return_typed_422_errors(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _database = api_context

    invalid_eco = client.get("/api/openings/line-library", params={"eco_from": "Z99"})
    invalid_sort = client.get("/api/openings/line-library", params={"sort": "frequency"})

    assert invalid_eco.status_code == 422
    assert invalid_eco.json() == {
        "code": "invalid_filter",
        "message": "eco_from must be an ECO code from A00 through E99",
    }
    assert invalid_sort.status_code == 422
    assert invalid_sort.json() == {
        "code": "invalid_filter",
        "message": "sort must be the declared default sort",
    }


def test_incompatible_database_returns_typed_503_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database = tmp_path / "incompatible.db"
    create_openings_database(database, recurrence_schema_version=2)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from backend.app.main import app

    response = TestClient(app).get("/api/openings/line-library")

    assert response.status_code == 503
    assert response.json() == {
        "code": "line_library_unavailable",
        "message": "Opening Line Library unavailable",
    }


def test_missing_database_returns_typed_503_without_creating_it(
    tmp_path: Path,
    monkeypatch,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(missing))
    from backend.app.main import app

    response = TestClient(app).get("/api/openings/line-library")

    assert response.status_code == 503
    assert response.json() == {
        "code": "line_library_unavailable",
        "message": "Opening Line Library unavailable",
    }
    assert not missing.exists()


def test_api_is_read_only_and_creates_no_sqlite_sidecars(
    api_context: tuple[TestClient, Path],
) -> None:
    client, database = api_context
    before_digest = hashlib.sha256(database.read_bytes()).digest()
    with sqlite3.connect(database) as db:
        before_tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()

    response = client.get("/api/openings/line-library")

    assert response.status_code == 200
    assert hashlib.sha256(database.read_bytes()).digest() == before_digest
    with sqlite3.connect(database) as db:
        after_tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    assert after_tables == before_tables
    assert not database.with_name(database.name + "-wal").exists()
    assert not database.with_name(database.name + "-shm").exists()
    assert not database.with_name(database.name + "-journal").exists()
