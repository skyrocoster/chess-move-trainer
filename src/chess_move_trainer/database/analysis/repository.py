"""Atomic publication of one complete current analysis per position."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import CanonicalPosition
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .models import (
    AnalysisError,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisStorageError,
    AnalysisValidationError,
    NotSavedReason,
    PublicationOutcome,
    ValidatedAnalysisResult,
)
from .validation import validate_analysis_position


@dataclass(frozen=True, slots=True)
class _StoredAnalysisResult:
    quality: AnalysisQuality
    configuration_version: int
    engine_version: str


class AnalysisRepository:
    """Publish normalized analysis through an opaque package-owned transaction."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        _checkpoint: Callable[[str], None] | None = None,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._checkpoint = _checkpoint if _checkpoint is not None else lambda _: None

    def publish(
        self,
        dp_position_id: int,
        result: AnalysisResultInput,
    ) -> PublicationOutcome:
        """Validate and atomically publish one complete result for an existing position."""

        _validate_position_id(dp_position_id)
        try:
            with _open_existing_connection(
                self._database_path, self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                position = _load_position(connection, dp_position_id)
                if position is None:
                    connection.rollback()
                    raise AnalysisValidationError(
                        "canonical position does not exist"
                    )
                connection.rollback()

                validated = validate_analysis_position(position, result)

                self._checkpoint("before_lock")
                connection.exec_driver_sql("BEGIN IMMEDIATE")
                transaction = connection.get_transaction()
                if transaction is None:
                    connection.rollback()
                    raise AnalysisStorageError(
                        "SQLite did not establish the immediate analysis transaction"
                    )

                try:
                    self._checkpoint("locked")
                    current = _load_current_result(connection, dp_position_id)
                    reason = _not_saved_reason(result, current)
                    self._checkpoint("rechecked")
                    if reason is not None:
                        transaction.rollback()
                        return PublicationOutcome.not_saved(reason)

                    _replace_result(
                        connection,
                        dp_position_id,
                        result,
                        validated,
                        self._checkpoint,
                    )
                    self._checkpoint("replaced")
                    transaction.commit()
                except BaseException:
                    if connection.in_transaction():
                        transaction.rollback()
                    raise
                return PublicationOutcome.saved_result()
        except KeyboardInterrupt:
            raise
        except AnalysisError:
            raise
        except SchemaIncompatibleError as error:
            raise AnalysisStorageError(
                "database is not a readable compatible schema v1 database"
            ) from error
        except Exception as error:
            raise _translate_storage_error(error) from error


def _validate_position_id(position_id: object) -> None:
    if type(position_id) is not int:
        raise AnalysisValidationError("dp_position_id must be an integer")


def _load_position(connection: object, position_id: int) -> CanonicalPosition | None:
    row = connection.execute(
        text(
            """
            SELECT dp_placement, dp_side_to_move, dp_castling_rights,
                   dp_legal_en_passant
            FROM derived_position
            WHERE dp_position_id = :position_id
            """
        ),
        {"position_id": position_id},
    ).first()
    if row is None:
        return None
    return CanonicalPosition(
        placement=row[0],
        side_to_move=row[1],
        castling_rights=row[2],
        legal_en_passant=row[3],
    )


def _load_current_result(
    connection: object, position_id: int
) -> _StoredAnalysisResult | None:
    row = connection.execute(
        text(
            """
            SELECT dar_quality, dar_configuration_version, dar_engine_version
            FROM derived_analysis_result
            WHERE derived_position_id = :position_id
            """
        ),
        {"position_id": position_id},
    ).first()
    if row is None:
        return None
    try:
        quality = AnalysisQuality(row[0])
    except (TypeError, ValueError) as error:
        raise AnalysisStorageError("stored analysis result has an invalid quality") from error
    if type(row[1]) is not int or row[1] < 1:
        raise AnalysisStorageError(
            "stored analysis result has an invalid configuration version"
        )
    if not isinstance(row[2], str):
        raise AnalysisStorageError(
            "stored analysis result has an invalid engine version"
        )
    return _StoredAnalysisResult(
        quality=quality,
        configuration_version=row[1],
        engine_version=row[2],
    )


def _not_saved_reason(
    result: AnalysisResultInput,
    current: _StoredAnalysisResult | None,
) -> NotSavedReason | None:
    if current is None:
        return None
    if current.quality is AnalysisQuality.TOOL and result.quality is AnalysisQuality.BROWSER:
        return NotSavedReason.LOWER_QUALITY
    if current.quality is result.quality:
        if (
            current.configuration_version == result.configuration_version
            and current.engine_version == result.engine_version
        ):
            return NotSavedReason.DUPLICATE
    return None


def _replace_result(
    connection: object,
    position_id: int,
    result: AnalysisResultInput,
    validated: ValidatedAnalysisResult,
    checkpoint: Callable[[str], None],
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO derived_analysis_result (
                derived_position_id,
                dar_quality,
                dar_configuration_version,
                dar_settings_json,
                dar_engine_name,
                dar_engine_version,
                dar_terminal_kind
            ) VALUES (
                :position_id,
                :quality,
                :configuration_version,
                :settings_json,
                :engine_name,
                :engine_version,
                :terminal_kind
            )
            ON CONFLICT (derived_position_id) DO UPDATE SET
                dar_quality = excluded.dar_quality,
                dar_configuration_version = excluded.dar_configuration_version,
                dar_settings_json = excluded.dar_settings_json,
                dar_engine_name = excluded.dar_engine_name,
                dar_engine_version = excluded.dar_engine_version,
                dar_terminal_kind = excluded.dar_terminal_kind
            """
        ),
        {
            "position_id": position_id,
            "quality": result.quality.value,
            "configuration_version": result.configuration_version,
            "settings_json": _serialize_settings(result),
            "engine_name": result.engine_name,
            "engine_version": result.engine_version,
            "terminal_kind": (
                None
                if validated.terminal_kind is None
                else validated.terminal_kind.value
            ),
        },
    )
    checkpoint("parent_replaced")
    connection.execute(
        text(
            "DELETE FROM derived_analysis_line "
            "WHERE derived_analysis_result_id = :position_id"
        ),
        {"position_id": position_id},
    )
    for line in validated.lines:
        connection.execute(
            text(
                """
                INSERT INTO derived_analysis_line (
                    derived_analysis_result_id,
                    dal_rank,
                    dal_score_kind,
                    dal_score_value,
                    dal_wdl_wins,
                    dal_wdl_draws,
                    dal_wdl_losses,
                    dal_pv_uci_json,
                    dal_depth
                ) VALUES (
                    :position_id,
                    :rank,
                    :score_kind,
                    :score_value,
                    :wdl_wins,
                    :wdl_draws,
                    :wdl_losses,
                    :pv_uci_json,
                    :depth
                )
                """
            ),
            {
                "position_id": position_id,
                "rank": line.rank,
                "score_kind": line.score_kind.value,
                "score_value": line.score_value,
                "wdl_wins": line.wdl_wins,
                "wdl_draws": line.wdl_draws,
                "wdl_losses": line.wdl_losses,
                "pv_uci_json": json.dumps(
                    line.pv_uci,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ),
                "depth": line.depth,
            },
        )


def _serialize_settings(result: AnalysisResultInput) -> str:
    return json.dumps(
        result.settings,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _translate_storage_error(error: Exception) -> AnalysisStorageError:
    candidate: BaseException | None = error
    while candidate is not None:
        if isinstance(candidate, sqlite3.OperationalError) and "locked" in str(
            candidate
        ).lower():
            return AnalysisStorageError(
                "analysis database writer lock was not acquired before timeout"
            )
        candidate = candidate.__cause__ or candidate.__context__
    if isinstance(error, OperationalError) and "locked" in str(error).lower():
        return AnalysisStorageError(
            "analysis database writer lock was not acquired before timeout"
        )
    if isinstance(error, AnalysisStorageError):
        return error
    return AnalysisStorageError("analysis database operation failed")
