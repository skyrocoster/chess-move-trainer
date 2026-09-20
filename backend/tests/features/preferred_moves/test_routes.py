from __future__ import annotations

from backend.app.main import app


def test_plural_route_exists_without_singular_routes() -> None:
    paths = app.openapi()["paths"]
    routes = {(path, method.upper()) for path, item in paths.items() for method in item}

    assert ("/api/preferred-moves", "GET") in routes
    assert ("/api/preferred-move", "GET") not in routes
    assert ("/api/preferred-move", "PUT") not in routes
    assert ("/api/preferred-move", "DELETE") not in routes


def test_routes_use_expected_operation_names() -> None:
    operations = app.openapi()["paths"]["/api/preferred-moves"]
    assert operations["get"]["operationId"] == "getPreferredMoves"
    assert operations["put"]["operationId"] == "putPreferredMoves"
    assert operations["delete"]["operationId"] == "deletePreferredMoves"
