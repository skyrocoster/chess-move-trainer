"""Profile budgets and catalogue registration rules stay pinned."""

from __future__ import annotations

from tools.dev.config import CATALOG_PATH, REPOSITORY_ROOT
from tools.dev.test import profiles
from tools.dev.test.catalog import load_catalog


def test_catalogue_and_readme_exist_and_readme_states_the_registration_rule():
    assert CATALOG_PATH.is_file()
    readme = (REPOSITORY_ROOT / "tests" / "catalog" / "README.md").read_text(encoding="utf-8")
    assert "Register it in the same change" in readme


def test_catalogue_title_and_version():
    catalog = load_catalog()
    assert catalog.meta["title"] == "Chess Move Trainer test catalogue"
    assert catalog.meta["version"] == 1


def test_profile_budgets_are_finite_and_pinned():
    assert profiles.PROFILE_BUDGETS == {
        "quick": 600.0,
        "smoke": 120.0,
        "full": 3600.0,
        "e2e": 900.0,
        "real-data": 900.0,
    }
    for profile in profiles.PROFILES.values():
        assert profile.budget_seconds > 0


def test_only_the_real_data_profile_allows_real_data():
    allowed = [name for name, profile in profiles.PROFILES.items() if profile.allow_real_data]
    assert allowed == ["real-data"]
