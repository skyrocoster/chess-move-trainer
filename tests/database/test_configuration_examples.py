from __future__ import annotations

from pathlib import Path

import yaml

from chess_move_trainer.database.games.configuration import load_acquire_configuration


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "docs" / "examples"
PLACEHOLDER_USERNAME = "YOUR_CHESS_COM_USERNAME"
PLACEHOLDER_TRAINER_UUID = "00000000-0000-4000-8000-000000000000"


def _load_mapping(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_games_example_documents_setup_and_update_identity_placeholders() -> None:
    path = EXAMPLES / "database-games.example.yaml"
    values = _load_mapping(path)

    assert set(values) == {"username", "trainer_chesscom_uuid"}
    assert values == {
        "username": PLACEHOLDER_USERNAME,
        "trainer_chesscom_uuid": PLACEHOLDER_TRAINER_UUID,
    }

    acquire = load_acquire_configuration(path)
    assert acquire.username == PLACEHOLDER_USERNAME
    assert str(acquire.trainer_chesscom_uuid) == PLACEHOLDER_TRAINER_UUID


def test_no_database_destination_configuration_example_remains() -> None:
    assert not (EXAMPLES / "database-rebuild.example.yaml").exists()
