"""Focused proof for the served API contract."""

from __future__ import annotations

import re

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend.app.main import app

EXPECTED_OPERATION_IDS: dict[str, dict[str, str]] = {
    "/api/health": {"get": "getHealth"},
    "/api/games": {"get": "getGames"},
    "/api/games/{game_uuid}": {"get": "getGame"},
    "/api/openings": {"get": "getOpenings"},
    "/api/openings/{opening_key}": {"get": "getOpeningByKey"},
    "/api/positions/insight": {"get": "getPositionInsight"},
    "/api/analysis": {"get": "getAnalysis"},
    "/api/analysis-requests": {"post": "requestAnalysis"},
    "/api/preferred-moves": {
        "get": "getPreferredMoves",
        "put": "putPreferredMoves",
        "delete": "deletePreferredMoves",
    },
}


def _assert_expected_operation_ids(paths: dict) -> None:
    for path, methods in EXPECTED_OPERATION_IDS.items():
        assert path in paths, f"served schema lost {path}"
        for method, expected_operation_id in methods.items():
            assert paths[path][method]["operationId"] == expected_operation_id


def test_served_schema_remains_full_with_only_clean_operationid_changes() -> None:
    spec = app.openapi()

    current_api_routes = [
        route for route in app.routes if isinstance(route, APIRoute)
    ]
    assert current_api_routes, "expected the real application routes"
    for route in current_api_routes:
        assert route.path in spec["paths"], f"served schema lost {route.path}"

    _assert_expected_operation_ids(spec["paths"])

    # No drift attributable to this stage: every other operation keeps the
    # FastAPI-generated default operation id.
    for route in current_api_routes:
        if route.path in EXPECTED_OPERATION_IDS:
            continue
        path_item = spec["paths"][route.path]
        for method, operation in path_item.items():
            if method not in route.methods or method.lower() == "head":
                continue
            expected_default = re.sub(r"\W", "_", f"{route.name}_{route.path}")
            assert operation["operationId"] == expected_default
            assert operation["operationId"] != "getHealth"


def test_docs_and_served_openapi_remain_available() -> None:
    client = TestClient(app)
    assert client.get("/docs").status_code == 200

    served = client.get("/openapi.json")
    assert served.status_code == 200
    served_spec = served.json()
    assert set(served_spec["paths"]) == set(app.openapi()["paths"])
    assert "/api/health" in served_spec["paths"]
    assert "/api/games" in served_spec["paths"]
    assert "/api/games/{game_uuid}" in served_spec["paths"]
    assert "/api/openings" in served_spec["paths"]
    assert "/api/openings/{opening_key}" in served_spec["paths"]
    assert "/api/openings/line-library" not in served_spec["paths"]
    assert "/api/positions/insight" in served_spec["paths"]
    assert "/api/analysis" in served_spec["paths"]
    assert "/api/analysis-requests" in served_spec["paths"]
    assert "/api/preferred-moves" in served_spec["paths"]
    assert set(served_spec["paths"]["/api/preferred-moves"]) == {"delete", "get", "put"}
    assert not any(path.startswith("/api/evaluation") for path in served_spec["paths"])
    _assert_expected_operation_ids(served_spec["paths"])
    assert served_spec["paths"]["/api/health"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] == {"$ref": "#/components/schemas/HealthResponse"}
