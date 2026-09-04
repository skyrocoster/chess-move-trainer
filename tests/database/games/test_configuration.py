from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import pytest

from chess_move_trainer.database.games.configuration import (
    ACQUIRE_DEFAULT_DELAY_SECONDS,
    ACQUIRE_DEFAULT_TIMEOUT_SECONDS,
    GamesConfigurationError,
    load_acquire_configuration,
    load_import_configuration,
)


ROOT = Path(__file__).parents[3]
FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = "11111111-1111-4111-8111-111111111111"


def _write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "games.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, "-m", "chess_move_trainer.database", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        timeout=15,
    )


def test_acquire_uses_yaml_values_and_exact_defaults(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        f"username: synthetic-trainer\ntrainer_chesscom_uuid: {TRAINER_UUID}\n",
    )

    config = load_acquire_configuration(config_path)

    assert config.username == "synthetic-trainer"
    assert config.trainer_chesscom_uuid == UUID(TRAINER_UUID)
    assert config.request_timeout == ACQUIRE_DEFAULT_TIMEOUT_SECONDS == 30.0
    assert config.request_delay == ACQUIRE_DEFAULT_DELAY_SECONDS == 0.25


def test_acquire_cli_values_override_only_matching_yaml_values(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        "\n".join(
            [
                "username: yaml-trainer",
                f"trainer_chesscom_uuid: {TRAINER_UUID}",
                "request_timeout: 9.5",
                "request_delay: 1.5",
            ]
        ),
    )
    override_uuid = "22222222-2222-4222-8222-222222222222"

    config = load_acquire_configuration(
        config_path,
        username="cli-trainer",
        trainer_chesscom_uuid=override_uuid,
        request_timeout=4.0,
        request_delay=0.0,
    )

    assert config.username == "cli-trainer"
    assert config.trainer_chesscom_uuid == UUID(override_uuid)
    assert config.request_timeout == 4.0
    assert config.request_delay == 0.0


def test_import_requires_only_trainer_identity_and_accepts_override(tmp_path: Path) -> None:
    without_username = _write_config(tmp_path, f"trainer_chesscom_uuid: {TRAINER_UUID}\n")
    override_uuid = "33333333-3333-4333-8333-333333333333"

    from_yaml = load_import_configuration(without_username)
    overridden = load_import_configuration(
        without_username, trainer_chesscom_uuid=override_uuid
    )

    assert from_yaml.trainer_chesscom_uuid == UUID(TRAINER_UUID)
    assert overridden.trainer_chesscom_uuid == UUID(override_uuid)


@pytest.mark.parametrize(
    ("yaml_text", "command", "message"),
    [
        (f"trainer_chesscom_uuid: {TRAINER_UUID}\n", "acquire", "username"),
        ("username: synthetic-trainer\n", "acquire", "trainer_chesscom_uuid"),
        ("{}\n", "import", "trainer_chesscom_uuid"),
        ("- not-a-mapping\n", "import", "mapping"),
        ("username: [broken\n", "import", "YAML"),
        ("trainer_chesscom_uuid: not-a-uuid\n", "import", "UUID"),
    ],
)
def test_command_specific_invalid_yaml_is_rejected(
    tmp_path: Path, yaml_text: str, command: str, message: str
) -> None:
    config_path = _write_config(tmp_path, yaml_text)

    with pytest.raises(GamesConfigurationError, match=message):
        if command == "acquire":
            load_acquire_configuration(config_path)
        else:
            load_import_configuration(config_path)


@pytest.mark.parametrize("timeout", [0.0, -1.0, math.nan, math.inf, -math.inf])
def test_acquire_rejects_invalid_effective_timeout(tmp_path: Path, timeout: float) -> None:
    config_path = _write_config(
        tmp_path,
        f"username: synthetic-trainer\ntrainer_chesscom_uuid: {TRAINER_UUID}\n",
    )

    with pytest.raises(GamesConfigurationError, match="request_timeout"):
        load_acquire_configuration(config_path, request_timeout=timeout)


@pytest.mark.parametrize("delay", [-1.0, math.nan, math.inf, -math.inf])
def test_acquire_rejects_invalid_effective_delay(tmp_path: Path, delay: float) -> None:
    config_path = _write_config(
        tmp_path,
        f"username: synthetic-trainer\ntrainer_chesscom_uuid: {TRAINER_UUID}\n",
    )

    with pytest.raises(GamesConfigurationError, match="request_delay"):
        load_acquire_configuration(config_path, request_delay=delay)


def test_config_path_must_name_an_existing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"

    with pytest.raises(GamesConfigurationError, match="configuration file"):
        load_import_configuration(missing)
    with pytest.raises(GamesConfigurationError, match="configuration file"):
        load_import_configuration(tmp_path)


def test_cli_maps_invalid_configuration_to_status_two(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, "trainer_chesscom_uuid: invalid\n")

    result = _run_cli(
        "games",
        "import",
        "--config",
        str(config_path),
        "--raw-root",
        str(tmp_path / "raw"),
        "--database",
        str(tmp_path / "database.db"),
    )

    assert result.returncode == 2
    assert b"trainer_chesscom_uuid" in result.stderr
    assert result.stdout == b""


def test_fixture_inventory_is_synthetic_and_covers_stage_one_categories() -> None:
    expected = {
        "archive-list.json",
        "month-valid.json",
        "month-empty.json",
        "month-unsafe.json",
        "month-duplicate-uuid.json",
        "current-month-local.json",
        "current-month-remote.json",
        "game-trainer-white.json",
        "game-trainer-black.json",
        "game-nullable-metadata.json",
        "game-non-standard.json",
        "game-trainer-absent.json",
        "game-malformed-pgn.json",
        "game-illegal-pgn.json",
        "game-repetition-counters.json",
        "correction-valid.json",
        "correction-invalid.json",
    }

    assert {path.name for path in FIXTURES.glob("*.json")} == expected
    for path in FIXTURES.glob("*.json"):
        content = path.read_text(encoding="utf-8")
        json.loads(content)
        assert "synthetic" in content.lower()
