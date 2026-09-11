from __future__ import annotations

from fastapi.routing import APIRoute

from backend.app.main import app


def test_plural_route_exists_without_singular_routes() -> None:
    routes = {
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }

    assert ("/api/preferred-moves", "GET") in routes
    assert ("/api/preferred-move", "GET") not in routes
    assert ("/api/preferred-move", "PUT") not in routes
    assert ("/api/preferred-move", "DELETE") not in routes


def test_routes_use_expected_operation_names() -> None:
    get_route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/preferred-moves"
        and "GET" in route.methods
    )
    put_route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/preferred-moves"
        and "PUT" in route.methods
    )
    delete_route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/preferred-moves"
        and "DELETE" in route.methods
    )

    assert get_route.operation_id == "getPreferredMoves"
    assert put_route.operation_id == "putPreferredMoves"
    assert delete_route.operation_id == "deletePreferredMoves"
