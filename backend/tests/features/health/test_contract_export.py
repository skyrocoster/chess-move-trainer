"""Focused proof for the served API contract."""

from __future__ import annotations

import re

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend.app.main import app


def test_served_schema_remains_full_with_only_clean_operationid_changes() -> None:
    spec = app.openapi()

    current_api_routes = [
        route for route in app.routes if isinstance(route, APIRoute)
    ]
    assert current_api_routes, "expected the real application routes"
    for route in current_api_routes:
        assert route.path in spec["paths"], f"served schema lost {route.path}"

    health_operation = spec["paths"]["/api/health"]["get"]
    assert health_operation["operationId"] == "getHealth"
    assert spec["paths"]["/api/games"]["get"]["operationId"] == "getGames"
    assert (
        spec["paths"]["/api/games/{game_uuid}"]["get"]["operationId"]
        == "getGame"
    )
    assert spec["paths"]["/api/openings"]["get"]["operationId"] == "getOpenings"
    assert (
        spec["paths"]["/api/openings/{opening_key}"]["get"]["operationId"]
        == "getOpeningByKey"
    )
    assert (
        spec["paths"]["/api/positions/insight"]["get"]["operationId"]
        == "getPositionInsight"
    )
    assert spec["paths"]["/api/analysis"]["get"]["operationId"] == "getAnalysis"
    assert (
        spec["paths"]["/api/analysis-requests"]["post"]["operationId"]
        == "requestAnalysis"
    )
    assert (
        spec["paths"]["/api/preferred-moves"]["get"]["operationId"]
        == "getPreferredMoves"
    )
    assert (
        spec["paths"]["/api/preferred-moves"]["put"]["operationId"]
        == "putPreferredMoves"
    )
    assert (
        spec["paths"]["/api/preferred-moves"]["delete"]["operationId"]
        == "deletePreferredMoves"
    )

    # No drift attributable to this stage: every other operation keeps the
    # FastAPI-generated default operation id.
    for route in current_api_routes:
        if route.path in {
            "/api/health",
            "/api/games",
            "/api/games/{game_uuid}",
            "/api/openings",
            "/api/openings/{opening_key}",
            "/api/positions/insight",
            "/api/analysis",
            "/api/analysis-requests",
            "/api/preferred-moves",
        }:
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
    assert served_spec["paths"]["/api/health"]["get"]["operationId"] == "getHealth"
    assert served_spec["paths"]["/api/games"]["get"]["operationId"] == "getGames"
    assert (
        served_spec["paths"]["/api/games/{game_uuid}"]["get"]["operationId"]
        == "getGame"
    )
    assert served_spec["paths"]["/api/openings"]["get"]["operationId"] == "getOpenings"
    assert (
        served_spec["paths"]["/api/openings/{opening_key}"]["get"]["operationId"]
        == "getOpeningByKey"
    )
    assert (
        served_spec["paths"]["/api/positions/insight"]["get"]["operationId"]
        == "getPositionInsight"
    )
    assert served_spec["paths"]["/api/analysis"]["get"]["operationId"] == "getAnalysis"
    assert (
        served_spec["paths"]["/api/analysis-requests"]["post"]["operationId"]
        == "requestAnalysis"
    )
    assert (
        served_spec["paths"]["/api/preferred-moves"]["get"]["operationId"]
        == "getPreferredMoves"
    )
    assert (
        served_spec["paths"]["/api/preferred-moves"]["put"]["operationId"]
        == "putPreferredMoves"
    )
    assert (
        served_spec["paths"]["/api/preferred-moves"]["delete"]["operationId"]
        == "deletePreferredMoves"
    )
    assert served_spec["paths"]["/api/health"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] == {"$ref": "#/components/schemas/HealthResponse"}
