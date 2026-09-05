from __future__ import annotations

import importlib

from chess_move_trainer.database.preferred_moves import (
    DateResolution,
    NormalizedPeriod,
    Preference,
    PreferenceState,
    PreferredMoveError,
    PreferredMoveLockError,
    PreferredMoveRepository,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
    RangeValidationError,
    ResolutionState,
    normalize_periods,
    parse_date_literal,
    period_from_literals,
    resolve_date,
    set_preference,
    unset_preference,
)


def test_preferred_moves_public_api_exports_ordinary_contracts() -> None:
    package = importlib.import_module("chess_move_trainer.database.preferred_moves")

    assert package.__all__ == [
        "DateResolution",
        "NormalizedPeriod",
        "Preference",
        "PreferenceState",
        "PreferredMoveError",
        "PreferredMoveLockError",
        "PreferredMoveRepository",
        "PreferredMoveSchemaError",
        "PreferredMoveStorageError",
        "PreferredMoveValidationError",
        "RangeValidationError",
        "ResolutionState",
        "normalize_periods",
        "parse_date_literal",
        "period_from_literals",
        "resolve_date",
        "set_preference",
        "unset_preference",
    ]
    assert PreferenceState.PREFERRED_MOVE.value == "preferred_move"
    assert ResolutionState.UNCONFIGURED.value == "unconfigured"
    assert issubclass(PreferredMoveLockError, PreferredMoveStorageError)
    assert issubclass(PreferredMoveValidationError, PreferredMoveError)
    assert issubclass(PreferredMoveSchemaError, PreferredMoveError)
    assert issubclass(RangeValidationError, ValueError)


def test_preferred_moves_public_api_does_not_promote_handles_or_internals() -> None:
    package = importlib.import_module("chess_move_trainer.database.preferred_moves")
    forbidden_exports = {
        "sqlite3",
        "sqlalchemy",
        "Connection",
        "connection",
        "raw_connection",
        "_PositionUnitOfWork",
        "_open_existing_connection",
        "_assert_compatible_schema",
        "_find_position_id",
        "_load_schedule",
        "_replace_schedule",
        "_canonicalize_four_field_fen",
    }

    assert not forbidden_exports.intersection(package.__all__)
    assert all(not name.startswith("_") for name in package.__all__)
    for name in forbidden_exports:
        assert not hasattr(package, name)
    assert not hasattr(PreferredMoveRepository, "connection")
    assert not hasattr(PreferredMoveRepository, "raw_connection")


def test_preferred_moves_public_exports_are_usable_without_handles() -> None:
    move = Preference.preferred_move("e2e4")
    period = period_from_literals("2026-01-01", "2026-02-01", move)

    assert parse_date_literal("2026-01-01").isoformat() == "2026-01-01"
    assert normalize_periods([period]) == (period,)
    assert set_preference([], "2026-01-01", "2026-02-01", move) == (
        period_from_literals("2026-01-01", "2026-02-01", move),
    )
    assert unset_preference([period], "2027-01-01", "2027-02-01") == (period,)
    assert resolve_date([], "2026-01-01") == DateResolution(
        ResolutionState.UNCONFIGURED
    )
