"""Focused Stage 1 proof for the health-only contract export."""

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


def test_export_contains_only_approved_health_contract(tmp_path: Path) -> None:
    output = tmp_path / "contract.json"
    _run_export(output)

    spec = json.loads(output.read_text(encoding="utf-8"))

    assert set(spec["paths"]) == {"/api/health"}
    assert set(spec["paths"]["/api/health"]) == {"get"}
    assert spec["paths"]["/api/health"]["get"]["operationId"] == "getHealth"
    assert set(spec["components"]["schemas"]) == {"HealthResponse"}

    # Fail-closed guarantee: the only reference resolves inside the contract.
    payload = output.read_text(encoding="utf-8")
    assert payload.count('"$ref"') == 1
    assert '"$ref": "#/components/schemas/HealthResponse"' in payload


def test_export_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _run_export(first)
    _run_export(second)
    assert first.read_bytes() == second.read_bytes()


def test_served_schema_remains_full_with_only_health_operationid_change() -> None:
    spec = app.openapi()

    current_api_routes = [
        route for route in app.routes if isinstance(route, APIRoute)
    ]
    assert current_api_routes, "expected the real application routes"
    for route in current_api_routes:
        assert route.path in spec["paths"], f"served schema lost {route.path}"

    health_operation = spec["paths"]["/api/health"]["get"]
    assert health_operation["operationId"] == "getHealth"

    # No drift attributable to this stage: every other operation keeps the
    # FastAPI-generated default operation id.
    for route in current_api_routes:
        if route.path == "/api/health":
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
    assert served_spec["paths"]["/api/health"]["get"]["operationId"] == "getHealth"
    assert served_spec["paths"]["/api/health"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] == {"$ref": "#/components/schemas/HealthResponse"}
