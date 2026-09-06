from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.rebuild import (
    RebuildConfiguration,
    VerificationStatus,
    VerificationTarget,
    stage_candidate,
    verify_rebuild_target,
)
from chess_move_trainer.database.games.persistence import GameRepository
import chess_move_trainer.database.rebuild.refresh as refresh_service


ROOT = Path(__file__).parents[3]
OPENING_FIXTURES = ROOT / "tests/database/openings/fixtures/catalogue-valid"
GAME_FIXTURES = ROOT / "tests/database/games/fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


def _opening_source(tmp_path: Path) -> Path:
    source = tmp_path / "openings"
    shutil.copytree(OPENING_FIXTURES, source)
    return source


def _raw_root(tmp_path: Path, fixture_name: str) -> Path:
    root = tmp_path / "raw"
    month = root / "games" / "2026" / "08.json"
    month.parent.mkdir(parents=True)
    game = json.loads((GAME_FIXTURES / fixture_name).read_text(encoding="utf-8"))
    month.write_text(json.dumps({"games": [game]}), encoding="utf-8")
    return root


def _neighbour(tmp_path: Path) -> Path:
    neighbour = tmp_path / "neighbour.db"
    create_schema(neighbour)
    return neighbour


def test_candidate_staging_uses_only_managed_sibling_and_preserves_neighbour(
    tmp_path: Path,
) -> None:
    neighbour = _neighbour(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()
    opening_source = _opening_source(tmp_path)
    raw_root = _raw_root(tmp_path, "game-trainer-white.json")

    outcome = stage_candidate(
        configuration,
        opening_source_dir=opening_source,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert outcome.completed
    assert outcome.candidate_path == configuration.managed_candidate
    assert outcome.candidate_path.exists()
    assert outcome.candidate_path.parent == neighbour.parent
    assert outcome.candidate_path != neighbour
    assert outcome.verification is not None
    assert outcome.verification.target is VerificationTarget.CANDIDATE
    assert outcome.verification.status is VerificationStatus.REPLACEMENT_READY
    assert neighbour.read_bytes() == before
    assert not (tmp_path / "arbitrary-candidate.db").exists()
    assert verify_rebuild_target(
        configuration, VerificationTarget.NEIGHBOUR
    ).replacement_ready is False


def test_incomplete_candidate_is_kept_partial_and_neighbour_bytes_are_untouched(
    tmp_path: Path,
) -> None:
    neighbour = _neighbour(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()

    outcome = stage_candidate(
        configuration,
        opening_source_dir=tmp_path / "missing-openings",
        raw_root=_raw_root(tmp_path, "game-trainer-white.json"),
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert not outcome.completed
    assert outcome.candidate_path == configuration.managed_candidate
    assert outcome.candidate_path.exists()
    assert outcome.verification is not None
    assert not outcome.verification.replacement_ready
    assert neighbour.read_bytes() == before
    assert verify_rebuild_target(
        configuration, VerificationTarget.CANDIDATE
    ).status is VerificationStatus.STRUCTURALLY_VALID_PARTIAL


def test_candidate_cli_reports_isolated_success_as_json(tmp_path: Path) -> None:
    neighbour = _neighbour(tmp_path)
    config = tmp_path / "rebuild.yaml"
    config.write_text(f"rebuilt_neighbour: {neighbour}\n", encoding="utf-8")
    opening_source = _opening_source(tmp_path)
    raw_root = _raw_root(tmp_path, "game-trainer-white.json")

    result = CliRunner().invoke(
        database_cli.app,
        [
            "rebuild",
            "candidate",
            "--config",
            str(config),
            "--opening-source-dir",
            str(opening_source),
            "--raw-root",
            str(raw_root),
            "--trainer-chesscom-uuid",
            str(TRAINER_UUID),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["operation"] == "candidate"
    assert payload["status"] == "succeeded"
    assert payload["verification"]["target"] == "candidate"
    assert result.stderr == ""


def test_interrupted_candidate_refresh_leaves_partial_candidate_for_normal_rerun(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    neighbour = _neighbour(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()
    opening_source = _opening_source(tmp_path)
    raw_root = _raw_root(tmp_path, "game-trainer-white.json")

    def interrupt(_: str) -> None:
        raise KeyboardInterrupt

    original_repository = refresh_service.GameRepository

    class InterruptingGameRepository(GameRepository):
        def __init__(self, *args: object, **kwargs: object) -> None:
            kwargs["_checkpoint"] = interrupt
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(refresh_service, "GameRepository", InterruptingGameRepository)
    with pytest.raises(KeyboardInterrupt):
        stage_candidate(
            configuration,
            opening_source_dir=opening_source,
            raw_root=raw_root,
            trainer_chesscom_uuid=TRAINER_UUID,
        )

    assert configuration.managed_candidate.exists()
    assert neighbour.read_bytes() == before
    partial = verify_rebuild_target(configuration, VerificationTarget.CANDIDATE)
    assert partial.status is VerificationStatus.STRUCTURALLY_VALID_PARTIAL
    assert partial.openings_ready
    assert not partial.games_ready

    monkeypatch.setattr(refresh_service, "GameRepository", original_repository)
    recovered = stage_candidate(
        configuration,
        opening_source_dir=opening_source,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert recovered.completed
    assert recovered.verification is not None
    assert recovered.verification.replacement_ready
    assert neighbour.read_bytes() == before


def test_exception_during_candidate_refresh_is_partial_and_next_rerun_recovers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    neighbour = _neighbour(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()
    opening_source = _opening_source(tmp_path)
    raw_root = _raw_root(tmp_path, "game-trainer-white.json")
    original_repository = refresh_service.GameRepository

    def fail(_: str) -> None:
        raise RuntimeError("synthetic candidate crash")

    class FailingGameRepository(GameRepository):
        def __init__(self, *args: object, **kwargs: object) -> None:
            kwargs["_checkpoint"] = fail
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(refresh_service, "GameRepository", FailingGameRepository)
    failed = stage_candidate(
        configuration,
        opening_source_dir=opening_source,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert not failed.completed
    assert failed.refresh is not None
    assert failed.verification is not None
    assert failed.verification.status is VerificationStatus.STRUCTURALLY_VALID_PARTIAL
    assert neighbour.read_bytes() == before

    monkeypatch.setattr(refresh_service, "GameRepository", original_repository)
    recovered = stage_candidate(
        configuration,
        opening_source_dir=opening_source,
        raw_root=raw_root,
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert recovered.completed
    assert recovered.verification is not None
    assert recovered.verification.replacement_ready
    assert neighbour.read_bytes() == before


def test_empty_managed_candidate_is_reconstructed_by_normal_staging_rerun(
    tmp_path: Path,
) -> None:
    neighbour = _neighbour(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    configuration.managed_candidate.write_bytes(b"")
    before = neighbour.read_bytes()

    outcome = stage_candidate(
        configuration,
        opening_source_dir=_opening_source(tmp_path),
        raw_root=_raw_root(tmp_path, "game-trainer-white.json"),
        trainer_chesscom_uuid=TRAINER_UUID,
    )

    assert outcome.completed
    assert outcome.verification is not None
    assert outcome.verification.replacement_ready
    assert neighbour.read_bytes() == before
