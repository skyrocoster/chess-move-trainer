from __future__ import annotations

import importlib

from chess_move_trainer.database.analysis import (
    AnalysisError,
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
    AnalysisStorageError,
    AnalysisValidationError,
    NotSavedReason,
    PublicationOutcome,
    validate_analysis_line,
    validate_analysis_result,
    validate_settings_object,
)


def test_analysis_public_namespace_exports_only_ordinary_contracts() -> None:
    package = importlib.import_module("chess_move_trainer.database.analysis")

    assert package.__name__ == "chess_move_trainer.database.analysis"
    assert package.__all__ == [
        "AnalysisError",
        "AnalysisLine",
        "AnalysisQuality",
    "AnalysisResultInput",
    "AnalysisRepository",
        "AnalysisScoreKind",
        "AnalysisStorageError",
        "AnalysisTerminalKind",
        "AnalysisValidationError",
        "NotSavedReason",
        "PublicationOutcome",
        "ValidatedAnalysisResult",
        "classify_terminal_kind",
        "validate_analysis_line",
        "validate_analysis_position",
        "validate_analysis_result",
        "validate_settings_object",
    ]
    assert AnalysisQuality.BROWSER.value == "browser"
    assert AnalysisQuality.TOOL.value == "tool"
    assert AnalysisScoreKind.CP.value == "cp"
    assert AnalysisScoreKind.MATE.value == "mate"
    assert NotSavedReason.DUPLICATE.value == "duplicate"
    assert NotSavedReason.STALE_OR_OUTDATED.value == "stale_or_outdated"
    assert NotSavedReason.LOWER_QUALITY.value == "lower_quality"
    assert issubclass(AnalysisValidationError, AnalysisError)
    assert issubclass(AnalysisStorageError, AnalysisError)
    assert all(not name.startswith("_") for name in package.__all__)


def test_analysis_public_namespace_does_not_expose_database_handles() -> None:
    package = importlib.import_module("chess_move_trainer.database.analysis")

    for name in (
        "sqlite3",
        "sqlalchemy",
        "Connection",
        "connection",
        "raw_connection",
        "_open_existing_connection",
    ):
        assert not hasattr(package, name)

    assert not hasattr(AnalysisLine, "connection")
    assert not hasattr(AnalysisResultInput, "raw_connection")
