"""Tests for the authoritative test catalogue and its file coverage."""

from __future__ import annotations

import re

from tools.dev.config import FIXTURE_PROFILES
from tools.dev.test.catalog import load_catalog
from tools.dev.test.discovery import (
    _pytest_failure_detail,
    case_id,
    discover,
    discover_test_files,
    group_id,
    slugify,
    validate_catalog_files,
)


def test_every_test_file_has_exactly_one_domain():
    catalog = load_catalog()
    problems = validate_catalog_files(catalog)
    assert problems == []


def test_discovered_files_include_every_runner_family():
    files = discover_test_files()
    assert any(path.startswith("backend/tests/") for path in files)
    assert any(path.startswith("tests/database/") for path in files)
    assert any(path.startswith("frontend/src/") and ".test." in path for path in files)
    assert any(path.startswith("tests/e2e/") for path in files)


def test_domain_metadata_is_complete_and_valid():
    catalog = load_catalog()
    for key, domain in catalog.domains.items():
        assert key
        assert domain.title
        assert domain.owner
        assert domain.purpose
        assert domain.default_fixture in FIXTURE_PROFILES
        for subdomain in domain.subdomains.values():
            if subdomain.default_fixture is not None:
                assert subdomain.default_fixture in FIXTURE_PROFILES


def test_ids_are_stable_logical_names():
    assert slugify("PreferredMovePanel") == "preferred-move-panel"
    assert (
        group_id(
            "frontend",
            "repertoire-builder",
            "frontend/src/features/repertoire-builder/PreferredMovePanel.test.tsx",
        )
        == "frontend.repertoire-builder.preferred-move-panel-test"
    )
    assert (
        case_id(
            "backend",
            "health.client",
            "backend/tests/features/health/test_health.py",
            "test_health_ok",
        )
        == "backend.health.client.test-health::test_health_ok"
    )


def test_case_ids_have_the_documented_layer_prefix():
    catalog = load_catalog()
    for path in discover_test_files():
        metadata = catalog.domain_for_file(path)
        assert metadata is not None
        assert metadata.layer in {"backend", "frontend", "frontend-api", "e2e"}
        assert re.fullmatch(r"[a-z0-9.-]+", metadata.domain_path)


def test_pytest_collection_diagnostic_is_not_a_node_id():
    output = (
        "backend/tests/tooling/test_errors.py::test_error_case\n"
        "E   ImportError: missing dependency\n"
        "ERROR collecting backend/tests/test_more.py\n"
    )
    assert _pytest_failure_detail(output, 2) == "E   ImportError: missing dependency"


def test_failed_discovery_is_not_cached(monkeypatch):
    from tools.dev.test import discovery

    writes = []
    monkeypatch.setattr(discovery, "_load_cache", lambda catalog, root: None)
    monkeypatch.setattr(
        discovery,
        "_discover_pytest",
        lambda catalog, root, result: result.problems.append("pytest collection failed"),
    )
    monkeypatch.setattr(discovery, "_discover_frontend_groups", lambda catalog, root, result: None)
    monkeypatch.setattr(discovery, "_discover_playwright", lambda catalog, root, result: None)
    monkeypatch.setattr(
        discovery, "_write_cache", lambda catalog, root, result: writes.append(result)
    )

    result = discover(load_catalog())

    assert result.problems == ["pytest collection failed"]
    assert writes == []


def test_fingerprint_notices_new_conftest_files(tmp_path):
    from tools.dev.test.discovery import DISCOVERY_EXTRA_INPUT_GLOBS, discovery_fingerprint

    catalog = load_catalog()
    feature = tmp_path / "backend" / "tests" / "features" / "demo"
    feature.mkdir(parents=True)
    (feature / "conftest.py").write_text("x = 1\n", encoding="utf-8")
    assert "backend/tests/**/conftest.py" in DISCOVERY_EXTRA_INPUT_GLOBS

    before = discovery_fingerprint(catalog, tmp_path)
    assert discovery_fingerprint(catalog, tmp_path) == before

    (feature / "conftest.py").write_text("x = 22222\n", encoding="utf-8")
    assert discovery_fingerprint(catalog, tmp_path) != before


def test_real_data_domain_is_the_only_real_db_fixture():
    catalog = load_catalog()
    real = [key for key, domain in catalog.domains.items() if domain.default_fixture == "real-db"]
    assert real == ["real-data"]
