"""Focused proof for the curated clean contract export."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend.app.main import app

REPO_ROOT = Path(__file__).resolve().parents[4]
EXPORT_SCRIPT = REPO_ROOT / "scripts" / "api" / "export_contract.py"

# Finite command-level termination for every exporter invocation in these tests.
EXPORT_TIMEOUT_SECONDS = 60

CLEAN_OPERATIONS = {
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

PRIOR_CLEAN_OPERATION_IDS = {
    "getHealth",
    "getGames",
    "getGame",
    "getOpenings",
    "getOpeningByKey",
    "getPositionInsight",
    "getAnalysis",
    "requestAnalysis",
    "getPreferredMoves",
    "putPreferredMoves",
}


def _run_export(output_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT), str(output_path)],
        cwd=REPO_ROOT,
        timeout=EXPORT_TIMEOUT_SECONDS,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def _exported_operation_ids(spec: dict) -> list[str]:
    return [
        operation.get("operationId")
        for path_item in spec["paths"].values()
        for operation in path_item.values()
        if isinstance(operation, dict)
    ]


def _schema_refs(node: object) -> set[str]:
    refs: set[str] = set()
    if isinstance(node, dict):
        reference = node.get("$ref")
        if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
            refs.add(reference.removeprefix("#/components/schemas/"))
        for value in node.values():
            refs.update(_schema_refs(value))
    elif isinstance(node, list):
        for value in node:
            refs.update(_schema_refs(value))
    return refs


def test_export_contains_only_approved_clean_contract(tmp_path: Path) -> None:
    output = tmp_path / "contract.json"
    _run_export(output)

    spec = json.loads(output.read_text(encoding="utf-8"))

    assert set(spec["paths"]) == set(CLEAN_OPERATIONS)
    expected_operation_ids = {
        operation_id
        for operations in CLEAN_OPERATIONS.values()
        for operation_id in operations.values()
    }
    assert len(spec["paths"]) == 9
    assert len(_exported_operation_ids(spec)) == 11
    assert set(_exported_operation_ids(spec)) == expected_operation_ids
    assert PRIOR_CLEAN_OPERATION_IDS <= set(_exported_operation_ids(spec))
    for path, operations in CLEAN_OPERATIONS.items():
        assert set(spec["paths"][path]) == set(operations)
        for method, operation_id in operations.items():
            assert spec["paths"][path][method]["operationId"] == operation_id
    assert set(spec["paths"]["/api/preferred-moves"]) == {"delete", "get", "put"}
    assert (
        spec["paths"]["/api/preferred-moves"]["delete"]["operationId"]
        == "deletePreferredMoves"
    )

    schemas = spec["components"]["schemas"]
    assert set(schemas) == _schema_refs(spec)

    # Fail-closed guarantee: the only reference resolves inside the contract.
    payload = output.read_text(encoding="utf-8")
    assert payload.count('"$ref"') >= 2
    assert '"$ref": "#/components/schemas/HealthResponse"' in payload
    assert '"$ref": "#/components/schemas/GamesResponse"' in payload
    assert '"$ref": "#/components/schemas/GamesErrorResponse"' in payload
    assert '"$ref": "#/components/schemas/GameDetailResponse"' in payload
    assert '"$ref": "#/components/schemas/OpeningCatalogueResponse"' in payload
    assert '"$ref": "#/components/schemas/OpeningCatalogueErrorResponse"' in payload
    assert '"$ref": "#/components/schemas/OpeningDetailErrorResponse"' in payload
    assert '"$ref": "#/components/schemas/AnalysisRequestBody"' in payload
    assert '"$ref": "#/components/schemas/AnalysisRequestErrorResponse"' in payload
    assert _schema_refs(spec["paths"]["/api/preferred-moves"]["delete"])
    assert _schema_refs(spec["paths"]["/api/preferred-moves"]["put"])
    served_paths = set(app.openapi()["paths"])
    assert set(spec["paths"]).isdisjoint(served_paths - set(CLEAN_OPERATIONS))
    assert not any(path.startswith("/api/evaluation") for path in spec["paths"])
    assert not any(
        path == "/api/preferred-move" or path.startswith("/api/preferred-move/")
        for path in spec["paths"]
    )


def test_export_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _run_export(first)
    _run_export(second)
    assert first.read_bytes() == second.read_bytes()


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
    assert "/api/openings/line-library" in served_spec["paths"]
    assert "/api/positions/insight" in served_spec["paths"]
    assert "/api/analysis" in served_spec["paths"]
    assert "/api/analysis-requests" in served_spec["paths"]
    assert "/api/preferred-moves" in served_spec["paths"]
    assert set(served_spec["paths"]["/api/preferred-moves"]) == {"delete", "get", "put"}
    assert any(path.startswith("/api/evaluation") for path in served_spec["paths"])
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
