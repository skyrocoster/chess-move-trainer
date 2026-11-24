"""Contract tests for ``sg screenshot``. No browser is started."""

from __future__ import annotations

import re

import pytest
from typer.testing import CliRunner

from tools.dev.cli.main import app
from tools.dev.config import REPOSITORY_ROOT
from tools.dev.screenshots.catalog import (
    ACTION_KINDS,
    DEFAULT_BASE_URL,
    EXPECTED_HTTP_ERRORS,
    ROUTE_EXEMPTIONS,
    TARGETS,
    VIEWPORT_GROUPS,
    VIEWPORTS,
    Action,
    CatalogTarget,
    Locator,
    parse_viewport,
    parse_viewports,
    resolve_targets,
)

runner = CliRunner()
_APP = REPOSITORY_ROOT / "frontend" / "src" / "App.tsx"


def test_root_help_lists_the_screenshot_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "screenshot" in result.output


def test_list_prints_every_target():
    result = runner.invoke(app, ["screenshot", "--list"])
    assert result.exit_code == 0
    for name in TARGETS:
        assert name in result.output


def test_default_base_url_is_the_frontend_port():
    assert DEFAULT_BASE_URL == "http://127.0.0.1:8444"


def test_targets_have_unique_names_routes_and_valid_actions():
    assert len({target.name for target in TARGETS.values()}) == len(TARGETS)
    assert len({(t.path, t.actions) for t in TARGETS.values()}) == len(TARGETS)
    assert TARGETS["home"].path == "/"
    for name, target in TARGETS.items():
        assert name == target.name
        assert target.path.startswith("/")
        assert all(action.kind in ACTION_KINDS for action in target.actions)


def test_expected_http_errors_are_narrow_rules():
    for rule in EXPECTED_HTTP_ERRORS:
        assert rule.reason
        assert rule.status >= 400


def test_viewport_groups_only_name_known_viewports():
    assert set(VIEWPORT_GROUPS["review"]) <= set(VIEWPORTS)
    assert [v.name for v in parse_viewports("review")] == list(VIEWPORT_GROUPS["review"])
    assert parse_viewport("1280x800").width == 1280
    with pytest.raises(ValueError):
        parse_viewport("100x100")
    with pytest.raises(ValueError):
        parse_viewport("nonsense")


@pytest.mark.parametrize(
    "name", ["Save", "Create game", "delete line", "Remove", "Submit", "Confirm", "Apply"]
)
def test_commit_word_guard_rejects_committing_clicks(name):
    with pytest.raises(ValueError, match="commit"):
        Action("click", Locator(role="button", name=name))


def test_commit_word_guard_allows_view_changes_and_other_kinds():
    Action("click", Locator(role="button", name="Show details"))
    Action("wait_for", Locator(role="button", name="Save"))


def test_schema_validation():
    with pytest.raises(ValueError):
        Locator()
    with pytest.raises(ValueError):
        Locator(role="button", css=".x")
    with pytest.raises(ValueError):
        Locator(name="x", css=".x")
    with pytest.raises(ValueError):
        Action("press")
    with pytest.raises(ValueError):
        Action("hover", Locator(css=".x"))
    with pytest.raises(ValueError):
        CatalogTarget("Bad Name", "/")
    with pytest.raises(ValueError):
        CatalogTarget("ok", "no-slash")
    with pytest.raises(ValueError):
        CatalogTarget("ok", "/x/{id}")


def test_resolve_targets_handles_names_routes_and_all():
    home = resolve_targets(None)[0]
    assert home.url == "http://127.0.0.1:8444/"
    assert resolve_targets("/trainer")[0].url.endswith("/trainer")
    assert len(resolve_targets(None, all_targets=True)) == len(TARGETS)
    with pytest.raises(ValueError):
        resolve_targets("home", all_targets=True)
    with pytest.raises(ValueError):
        resolve_targets("not-a-target")


def parse_app_routes(source: str) -> list[str]:
    """Route paths from ``<Route path="...">`` elements in App.tsx, in file order."""
    return list(dict.fromkeys(re.findall(r'<Route\s+path="([^"]+)"', source)))


def _shape(path: str) -> str:
    return re.sub(r":\w+|\{id\}", "{id}", path.split("?")[0])


def route_drift(routes, target_paths: dict[str, str], exemptions: dict[str, str]) -> list[str]:
    """Return a problem for each route, target or exemption that no longer agree."""
    problems: list[str] = []
    route_shapes = {_shape(route) for route in routes}
    target_shapes = {_shape(path) for name, path in target_paths.items() if name != "not-found"}
    exempt_shapes = {_shape(route) for route in exemptions}
    for route in sorted(routes):
        if _shape(route) not in target_shapes | exempt_shapes:
            problems.append(f"Route {route} has no screenshot target or exemption.")
    for name, path in sorted(target_paths.items()):
        if name != "not-found" and _shape(path) not in route_shapes:
            problems.append(f"Target {name!r} ({path}) matches no route in App.tsx.")
    for route in sorted(exemptions):
        if route not in routes:
            problems.append(f"ROUTE_EXEMPTIONS lists {route}, which is not in App.tsx.")
    return problems


def _paths() -> dict[str, str]:
    return {name: target.path for name, target in TARGETS.items()}


def test_every_route_has_a_target_or_an_exemption_and_nothing_is_stale():
    routes = parse_app_routes(_APP.read_text(encoding="utf-8"))
    assert len(routes) >= 4, f"parsed only {len(routes)} routes; the parser needs updating"
    assert {"/", "/repertoire", "/trainer", "/analysis"} <= set(routes)
    assert route_drift(routes, _paths(), ROUTE_EXEMPTIONS) == []


def test_not_found_target_hits_no_real_route():
    routes = parse_app_routes(_APP.read_text(encoding="utf-8"))
    assert TARGETS["not-found"].path not in routes


_ROUTES = ["/", "/a", "/b", "*"]


@pytest.mark.parametrize(
    ("routes", "targets", "exemptions", "expected"),
    [
        (_ROUTES + ["/new"], {"h": "/", "a": "/a", "b": "/b"}, {"*": "x"}, "Route /new has no"),
        (_ROUTES, {"h": "/", "a": "/a", "b": "/b", "gone": "/gone"}, {"*": "x"}, "Target 'gone'"),
        (_ROUTES, {"h": "/", "a": "/a", "b": "/b"}, {"*": "x", "/ghost": "y"}, "lists /ghost"),
        (_ROUTES, {"h": "/", "a": "/a"}, {"*": "x"}, "Route /b has no"),
    ],
)
def test_route_drift_guard_fires(routes, targets, exemptions, expected):
    problems = route_drift(routes, targets, exemptions)
    assert any(expected in problem for problem in problems), problems


def test_driver_ships_as_package_data():
    pyproject = (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"tools.dev.screenshots" = ["driver.mjs"]' in pyproject
    assert (REPOSITORY_ROOT / "src/tools/dev/screenshots/driver.mjs").is_file()
