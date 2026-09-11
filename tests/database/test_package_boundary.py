from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_common_package_and_database_namespace_are_importable() -> None:
    package = importlib.import_module("chess_move_trainer")
    database = importlib.import_module("chess_move_trainer.database")
    lifecycle = importlib.import_module("chess_move_trainer.database.lifecycle")
    positions = importlib.import_module("chess_move_trainer.database.positions")
    analysis = importlib.import_module("chess_move_trainer.database.analysis")
    games = importlib.import_module("chess_move_trainer.database.games")
    openings = importlib.import_module("chess_move_trainer.database.openings")
    proof = importlib.import_module("chess_move_trainer.database.proof")

    assert package.__name__ == "chess_move_trainer"
    assert database.__name__ == "chess_move_trainer.database"
    assert lifecycle.__name__ == "chess_move_trainer.database.lifecycle"
    assert lifecycle.DEFAULT_DATABASE_PATH.as_posix() == "data/database/chess.db"
    assert tuple(operation.value for operation in lifecycle.LifecycleOperation) == (
        "setup",
        "update games",
        "update openings",
    )
    for name in ("setup_database", "update_games", "update_openings"):
        assert hasattr(lifecycle, name)
    assert positions.__name__ == "chess_move_trainer.database.positions"
    assert analysis.__name__ == "chess_move_trainer.database.analysis"
    assert games.__name__ == "chess_move_trainer.database.games"
    assert openings.__name__ == "chess_move_trainer.database.openings"
    assert proof.__name__ == "chess_move_trainer.database.proof"
    for name in (
        "PositionInsight",
        "PositionInsightAnalysis",
        "PositionInsightExperience",
        "PositionInsightOpening",
        "PositionInsightObservedMove",
        "PositionInsightObservedMoveTotals",
        "PositionInsightPreference",
        "PositionInsightRepository",
        "PositionInsightRequest",
        "PositionInsightResult",
        "PositionInsightError",
        "PositionInsightSchemaError",
        "PositionInsightStorageError",
        "PositionInsightTerminalTotals",
        "PositionInsightValidationError",
        "read_position_insight",
        "get_position_insight",
    ):
        assert hasattr(positions, name)
    for name in (
        "AnalysisObservation",
        "AnalysisObservationError",
        "AnalysisObservationRepository",
        "AnalysisObservationRequest",
        "AnalysisObservationResult",
        "AnalysisObservationSchemaError",
        "AnalysisObservationState",
        "AnalysisObservationStorageError",
        "AnalysisObservationValidationError",
        "AnalysisRequest",
        "AnalysisRequestDisposition",
        "AnalysisRequestError",
        "AnalysisRequestRepository",
        "AnalysisRequestResult",
        "AnalysisRequestSchemaError",
        "AnalysisRequestStorageError",
        "AnalysisRequestValidationError",
        "get_analysis_observation",
        "read_analysis_observation",
        "request_analysis",
    ):
        assert hasattr(analysis, name)
    assert not any(
        name in analysis.__all__ for name in ("FastAPI", "BaseModel", "backend")
    )
    assert not any(
        name in positions.__all__ for name in ("FastAPI", "BaseModel", "backend")
    )
    for name in (
        "OpeningRouteSource",
        "load_opening_sources",
        "OpeningInputError",
        "RecognizedOpening",
        "OpeningRecognition",
        "lookup_fen",
        "replay_pgn",
        "opening_api_key",
        "parse_opening_api_key",
        "OpeningCatalogueEntry",
        "OpeningCatalogueError",
        "OpeningCataloguePage",
        "OpeningCatalogueQuery",
        "OpeningCatalogueReader",
        "OpeningCatalogueSchemaError",
        "OpeningCatalogueStorageError",
        "OpeningCatalogueValidationError",
        "read_opening",
        "read_openings",
    ):
        assert hasattr(openings, name)
    for name in (
        "CoverageState",
        "GameSearchQuery",
        "GameSearchPage",
        "GameSummary",
        "GameCoverage",
        "GameDetail",
        "GameDetailOccurrence",
        "GameSearchRepository",
        "GameSearchValidationError",
        "GameSearchSchemaError",
        "GameSearchStorageError",
        "GameSearchSort",
        "read_game",
        "search_games",
    ):
        assert hasattr(games, name)
    for name in (
        "DEFAULT_DATABASE_PATH",
        "DirectProof",
        "collect_direct_proof",
    ):
        assert hasattr(proof, name)
    for name in (
        "OpeningAcquisitionError",
        "OpeningAcquisitionResult",
        "acquire_openings",
        "import_opening_catalogue",
        "RebuildConfiguration",
        "RebuildOperation",
        "verify_database",
        "create_snapshot",
        "replace_rebuilt_neighbour",
        "rollback_rebuilt_neighbour",
    ):
        assert not hasattr(openings, name)
        assert not hasattr(proof, name)
    assert Path(package.__file__).parts[-3:-1] == ("src", "chess_move_trainer")


def test_preferred_moves_package_public_namespace_is_importable() -> None:
    preferred_moves = importlib.import_module(
        "chess_move_trainer.database.preferred_moves"
    )

    assert preferred_moves.__name__ == "chess_move_trainer.database.preferred_moves"
    for name in (
        "Preference",
        "NormalizedPeriod",
        "DateResolution",
        "PreferenceState",
        "ResolutionState",
        "PreferredMoveRepository",
        "PreferredMoveValidationError",
        "PreferredMoveSchemaError",
        "PreferredMoveStorageError",
        "PreferredMoveLockError",
        "PreferredMoveTimeline",
        "PreferredMoveTimelinePreference",
        "PreferredMoveTimelineRepository",
        "PreferredMoveTimelineRequest",
        "PreferredMoveTimelineResult",
        "PreferredMoveTimelineSegment",
        "get_preferred_moves",
        "read_preferred_moves",
    ):
        assert hasattr(preferred_moves, name)


def test_packaging_preserves_backend_and_declares_database_sql_resources() -> None:
    with (ROOT / "pyproject.toml").open("rb") as pyproject_file:
        config = tomllib.load(pyproject_file)

    package_find = config["tool"]["setuptools"]["packages"]["find"]
    package_data = config["tool"]["setuptools"]["package-data"]

    assert "backend*" in package_find["include"]
    assert "chess_move_trainer*" in package_find["include"]
    assert package_data["chess_move_trainer.database"] == ["*.sql"]
