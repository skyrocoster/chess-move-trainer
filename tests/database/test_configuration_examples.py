from __future__ import annotations

from pathlib import Path

import yaml

from chess_move_trainer.database.games.configuration import (
    load_acquire_configuration,
    load_import_configuration,
)
from chess_move_trainer.database.rebuild.configuration import load_rebuild_configuration


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "docs" / "examples"
PLACEHOLDER_USERNAME = "YOUR_CHESS_COM_USERNAME"
PLACEHOLDER_TRAINER_UUID = "00000000-0000-4000-8000-000000000000"
PLACEHOLDER_REBUILT_NEIGHBOUR = "PATH_TO_REBUILT_NEIGHBOUR_DB"


def _load_mapping(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_games_example_is_shared_by_supported_loaders_and_uses_placeholders() -> None:
    path = EXAMPLES / "database-games.example.yaml"
    values = _load_mapping(path)

    assert set(values) == {"username", "trainer_chesscom_uuid"}
    assert values == {
        "username": PLACEHOLDER_USERNAME,
        "trainer_chesscom_uuid": PLACEHOLDER_TRAINER_UUID,
    }

    acquire = load_acquire_configuration(path)
    imported = load_import_configuration(path)
    assert acquire.username == PLACEHOLDER_USERNAME
    assert str(acquire.trainer_chesscom_uuid) == PLACEHOLDER_TRAINER_UUID
    assert str(imported.trainer_chesscom_uuid) == PLACEHOLDER_TRAINER_UUID


def test_rebuild_example_uses_only_loader_supported_placeholder() -> None:
    path = EXAMPLES / "database-rebuild.example.yaml"
    values = _load_mapping(path)

    assert values == {"rebuilt_neighbour": PLACEHOLDER_REBUILT_NEIGHBOUR}
    configuration = load_rebuild_configuration(path)
    assert configuration.rebuilt_neighbour == Path(PLACEHOLDER_REBUILT_NEIGHBOUR).resolve()


def test_example_readme_names_consumers_and_safe_placeholder_policy() -> None:
    readme = (EXAMPLES / "README.md").read_text(encoding="utf-8").lower()

    assert "safe placeholders" in readme
    assert "games acquire" in readme
    assert "games import" in readme
    assert "rebuild" in readme
    assert "real identity must never be committed" in readme
