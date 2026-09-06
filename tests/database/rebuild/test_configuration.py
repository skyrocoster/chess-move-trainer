from __future__ import annotations

from pathlib import Path

import pytest

from chess_move_trainer.database.rebuild import (
    MANAGED_CANDIDATE_SUFFIX,
    REBUILT_NEIGHBOUR_KEY,
    RebuildConfiguration,
    RebuildConfigurationError,
    load_rebuild_configuration,
)


def _write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "rebuild.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_configuration_owns_one_destination_and_derives_a_sibling_candidate(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "rebuilt.db"
    configuration = load_rebuild_configuration(
        _write_config(tmp_path, f"{REBUILT_NEIGHBOUR_KEY}: {destination}\n")
    )

    assert configuration.rebuilt_neighbour == destination.resolve()
    assert configuration.managed_candidate == Path(
        f"{destination}{MANAGED_CANDIDATE_SUFFIX}"
    ).resolve()
    assert configuration.managed_candidate.parent == configuration.rebuilt_neighbour.parent
    assert configuration.managed_candidate != configuration.rebuilt_neighbour
    assert configuration.candidate == configuration.managed_candidate


@pytest.mark.parametrize(
    "yaml_text",
    [
        "{}\n",
        "rebuilt_neighbour: ''\n",
        "rebuilt_neighbour: .\n",
        "rebuilt_neighbour: rebuilt.db\ncandidate: another.db\n",
        "rebuilt_neighbour: rebuilt.db\nactive: another.db\n",
        "- rebuilt.db\n",
    ],
)
def test_configuration_rejects_missing_ambiguous_or_unsafe_values(
    tmp_path: Path,
    yaml_text: str,
) -> None:
    with pytest.raises(RebuildConfigurationError):
        load_rebuild_configuration(_write_config(tmp_path, yaml_text))


def test_configuration_rejects_existing_directory_destination(tmp_path: Path) -> None:
    directory = tmp_path / "directory"
    directory.mkdir()

    with pytest.raises(RebuildConfigurationError, match="directory"):
        RebuildConfiguration(directory)


def test_configuration_path_must_name_an_existing_file(tmp_path: Path) -> None:
    with pytest.raises(RebuildConfigurationError, match="configuration file"):
        load_rebuild_configuration(tmp_path / "missing.yaml")
