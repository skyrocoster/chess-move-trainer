from __future__ import annotations

from pathlib import Path

import pytest

from chess_move_trainer.database.rebuild import RebuildConfiguration
from chess_move_trainer.database.rebuild.proof import (
    Db09PreflightError,
    preflight_db09_paths,
)


def test_db09_paths_exclude_old_database_and_candidate_is_managed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    neighbour = tmp_path / "rebuild" / "db-09-neighbour.db"
    neighbour.parent.mkdir()
    old_database = tmp_path / "old" / "chess_games.db"
    old_database.parent.mkdir()
    games_config = tmp_path / "db-09-games.yaml"
    private_username = "private-trainer-name"
    private_uuid = "33333333-3333-4333-8333-333333333333"
    games_config.write_text(
        f"username: {private_username}\ntrainer_chesscom_uuid: {private_uuid}\n",
        encoding="utf-8",
    )

    result = preflight_db09_paths(
        RebuildConfiguration(neighbour),
        old_database_path=old_database,
        games_configuration_path=games_config,
    )

    assert result.rebuilt_neighbour == neighbour.resolve()
    assert result.managed_candidate == Path(f"{neighbour}.candidate").resolve()
    assert result.managed_candidate != result.rebuilt_neighbour
    assert result.rebuilt_neighbour not in result.protected_old_paths
    assert result.managed_candidate not in result.protected_old_paths
    assert result.private_configuration_valid
    captured = capsys.readouterr()
    assert private_username not in captured.out + captured.err
    assert private_uuid not in captured.out + captured.err

    for suffix in ("-wal", "-shm", ".analysis.lock"):
        with pytest.raises(Db09PreflightError, match="protected old database"):
            preflight_db09_paths(
                RebuildConfiguration(old_database.with_name(old_database.name + suffix)),
                old_database_path=old_database,
            )


def test_db09_paths_reject_an_old_database_sidecar_alias(tmp_path: Path) -> None:
    old_database = tmp_path / "chess_games.db"
    with pytest.raises(Db09PreflightError, match="protected old database"):
        preflight_db09_paths(
            RebuildConfiguration(Path(f"{old_database}-wal")),
            old_database_path=old_database,
        )
