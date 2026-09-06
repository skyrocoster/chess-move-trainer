from __future__ import annotations

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database import create_schema
import chess_move_trainer.database.rebuild.cli as rebuild_cli


def test_rebuild_group_and_reserved_operations_have_noninteractive_help() -> None:
    runner = CliRunner()

    group = runner.invoke(database_cli.app, ["rebuild", "--help"])
    assert group.exit_code == 0
    assert "refresh" in group.stdout
    assert "verify" in group.stdout
    assert "snapshot" in group.stdout
    assert "candidate" in group.stdout
    assert "replace" in group.stdout
    assert "rollback" in group.stdout
    assert "recover" not in group.stdout.lower()
    assert group.stderr == ""

    for command in ("refresh", "verify", "snapshot", "candidate", "replace", "rollback"):
        result = runner.invoke(database_cli.app, ["rebuild", command, "--help"])
        assert result.exit_code == 0
        assert "--config" in result.stdout
        assert result.stderr == ""


@pytest.mark.parametrize("command", ["refresh", "verify", "snapshot", "candidate", "replace", "rollback"])
def test_rebuild_commands_require_explicit_configuration(command: str) -> None:
    result = CliRunner().invoke(database_cli.app, ["rebuild", command])

    assert result.exit_code == 2
    assert "--config" in result.stderr
    assert result.stdout == ""


def test_rebuild_invalid_target_is_usage_status_2(tmp_path) -> None:
    neighbour = tmp_path / "neighbour.db"
    create_schema(neighbour)
    config = tmp_path / "rebuild.yaml"
    config.write_text(f"rebuilt_neighbour: {neighbour}\n", encoding="utf-8")

    result = CliRunner().invoke(
        database_cli.app,
        ["rebuild", "verify", "--config", str(config), "--target", "unknown"],
    )

    assert result.exit_code == 2
    assert "target" in result.stderr.lower()
    assert result.stdout == ""


@pytest.mark.parametrize(
    ("command", "service_name"),
    [
        ("refresh", "refresh_database"),
        ("verify", "verify_rebuild_target"),
        ("snapshot", "create_snapshot"),
        ("candidate", "stage_candidate"),
        ("replace", "replace_rebuilt_neighbour"),
        ("rollback", "rollback_rebuilt_neighbour"),
    ],
)
def test_rebuild_interruption_is_status_130_and_stderr_only(
    tmp_path, monkeypatch: pytest.MonkeyPatch, command: str, service_name: str
) -> None:
    neighbour = tmp_path / "neighbour.db"
    create_schema(neighbour)
    config = tmp_path / "rebuild.yaml"
    config.write_text(f"rebuilt_neighbour: {neighbour}\n", encoding="utf-8")

    def interrupt(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise KeyboardInterrupt

    monkeypatch.setattr(rebuild_cli, service_name, interrupt)
    result = CliRunner().invoke(
        database_cli.app,
        ["rebuild", command, "--config", str(config)],
    )

    assert result.exit_code == 130
    assert result.stdout == ""
    assert "Interrupted" in result.stderr
