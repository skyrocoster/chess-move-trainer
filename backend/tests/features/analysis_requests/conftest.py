from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from backend.tests.features.analysis_observation.conftest import (
    _complete_analysis_result,
    create_insight_database,
)


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    database = create_insight_database(tmp_path / "analysis-requests.db")
    _complete_analysis_result(database)
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    return client, database


__all__ = ["api_context", "client"]
