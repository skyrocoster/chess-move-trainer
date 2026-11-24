"""The ``sg`` developer CLI must stay finite and Docker-free to test."""

from __future__ import annotations

import json
import subprocess

import pytest
from typer.testing import CliRunner

from tools.dev import console, services
from tools.dev.cli.main import app


@pytest.fixture(autouse=True)
def _reset_dry_run():
    yield
    console.set_dry_run(False)


@pytest.fixture(autouse=True)
def _no_docker(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError(f"subprocess must not run in tests: {args}")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)


def test_help_lists_setup_and_dev():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "setup" in result.output
    assert "dev" in result.output


@pytest.mark.parametrize("timeout", [0, -1])
def test_run_rejects_non_positive_timeout(timeout):
    with pytest.raises(ValueError):
        console.run(["docker", "info"], timeout=timeout)
    with pytest.raises(ValueError):
        console.output(["docker", "info"], timeout=timeout)


def _rows(normal: int, six: int) -> str:
    rows = [{"Service": "worker", "State": "running"}] * normal
    rows += [{"Service": "worker-six", "State": "running"}] * six
    return "\n".join(json.dumps(row) for row in rows)


@pytest.mark.parametrize(
    ("normal", "six", "label"),
    [
        (1, 0, "normal"),
        (0, 6, "accelerated-six"),
        (0, 0, "stopped"),
        (1, 2, "invalid/mixed"),
        (0, 3, "invalid/partial"),
        (2, 0, "invalid/partial"),
    ],
)
def test_worker_mode_classification(normal, six, label):
    mode = services.classify_worker_mode(services.parse_ps_rows(_rows(normal, six)))
    assert mode.label == label


def test_parse_ps_rows_accepts_json_array():
    rows = services.parse_ps_rows('[{"Service": "worker", "State": "running"}]')
    assert services.classify_worker_mode(rows).label == "normal"


def test_rows_healthy_requires_running_and_healthy():
    good = [{"Service": n, "State": "running", "Health": "healthy"} for n in
            ("backend", "frontend", "datasette")]
    assert services.rows_healthy(good)
    bad = [dict(good[0], Health="starting"), *good[1:]]
    assert not services.rows_healthy(bad)
    assert not services.rows_healthy(good[:2])


def _invoke(args):
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    return [line for line in result.output.splitlines() if "[dry-run]" in line]


def test_start_dry_run_sequence():
    lines = _invoke(["dev", "start", "--dry-run"])
    text = "\n".join(lines)
    assert "storybook" not in text.lower()
    assert "chess_move_trainer.database update games" in text
    assert text.index("update games") < text.index("update openings")
    assert "--scale worker=1" in lines[-1]
    assert "stop worker-six" in text
    assert "--name chess-move-trainer-db-probe" in text


def test_update_dry_run_sequence():
    lines = _invoke(["dev", "update", "--dry-run"])
    text = "\n".join(lines)
    assert "storybook" not in text.lower()
    assert text.index("stop worker-six") < text.index("update games")
    assert text.index("update openings") < text.index("up --detach --scale worker=1")


def test_setup_db_dry_run_names_database_setup():
    text = "\n".join(_invoke(["dev", "setup-db", "--dry-run"]))
    assert "chess_move_trainer.database setup --database data/database/chess.db" in text
