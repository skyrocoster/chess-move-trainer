"""Read-only structural and replacement-readiness verification for DB-08."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from errno import EACCES, EAGAIN, EBUSY, EPERM, ETIMEDOUT
from pathlib import Path
from typing import Any

from sqlalchemy.exc import DatabaseError
from sqlalchemy.engine import Connection

from ..connection import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    _open_connection,
    _validate_lock_timeout,
)
from ..schema import _reference_snapshot, _schema_snapshot
from .configuration import RebuildConfiguration
from .operations import OperationExitCode


class VerificationTarget(str, Enum):
    """Kinds of database artifact accepted by the verifier."""

    NEIGHBOUR = "neighbour"
    CANDIDATE = "candidate"
    SNAPSHOT = "snapshot"


class VerificationStatus(str, Enum):
    """Deterministic structural/readiness result categories."""

    REPLACEMENT_READY = "replacement_ready"
    STRUCTURALLY_VALID_PARTIAL = "structurally_valid_partial"
    INCOMPATIBLE = "incompatible"
    CORRUPT = "corrupt"
    FOREIGN_KEY_INVALID = "foreign_key_invalid"
    MISSING = "missing"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """Facts returned without exposing a database connection or transaction."""

    target: VerificationTarget
    database_path: Path
    status: VerificationStatus
    schema_compatible: bool
    user_version: int | None
    integrity_result: str
    foreign_key_errors: tuple[str, ...]
    opening_count: int
    opening_route_count: int
    opening_move_count: int
    position_count: int
    game_count: int
    game_position_count: int

    @property
    def structurally_valid(self) -> bool:
        """Whether the target passed the structural safety checks."""

        return self.status in {
            VerificationStatus.REPLACEMENT_READY,
            VerificationStatus.STRUCTURALLY_VALID_PARTIAL,
        }

    @property
    def openings_ready(self) -> bool:
        """Whether the opening catalogue has labels, routes, moves, and positions."""

        return (
            self.opening_count > 0
            and self.opening_route_count > 0
            and self.opening_move_count > 0
            and self.position_count > 0
        )

    @property
    def games_ready(self) -> bool:
        """Whether imported games and their stored occurrences are present."""

        return self.game_count > 0 and self.game_position_count > 0

    @property
    def replacement_ready(self) -> bool:
        """Whether the target is structurally valid and has both required data areas."""

        return self.status is VerificationStatus.REPLACEMENT_READY

    @property
    def exit_code(self) -> OperationExitCode:
        """Return the meaningful CLI status for this verification result."""

        if self.status in {
            VerificationStatus.REPLACEMENT_READY,
            VerificationStatus.STRUCTURALLY_VALID_PARTIAL,
        }:
            return OperationExitCode.SUCCEEDED
        if self.status is VerificationStatus.INCOMPATIBLE:
            return OperationExitCode.INCOMPATIBLE
        return OperationExitCode.FAILED

    @property
    def message(self) -> str:
        """Return a stable one-line summary suitable for automation logs."""

        if self.status is VerificationStatus.UNAVAILABLE:
            return (
                f"Unable to verify {self.target.value} target: it is unavailable or "
                "inaccessible; no corruption claim was made."
            )
        return (
            f"Verified {self.target.value} target as {self.status.value}: "
            f"structurally_valid={'yes' if self.structurally_valid else 'no'}, "
            f"replacement_ready={'yes' if self.replacement_ready else 'no'}."
        )

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for JSON CLI output."""

        return {
            "database_path": str(self.database_path),
            "foreign_key_errors": list(self.foreign_key_errors),
            "game_count": self.game_count,
            "game_position_count": self.game_position_count,
            "integrity_result": self.integrity_result,
            "opening_count": self.opening_count,
            "opening_move_count": self.opening_move_count,
            "opening_route_count": self.opening_route_count,
            "position_count": self.position_count,
            "replacement_ready": self.replacement_ready,
            "schema_compatible": self.schema_compatible,
            "status": self.status.value,
            "structurally_valid": self.structurally_valid,
            "target": self.target.value,
            "user_version": self.user_version,
        }


def verify_rebuild_target(
    configuration: RebuildConfiguration,
    target: VerificationTarget | str,
    *,
    snapshot_path: str | Path | None = None,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> VerificationResult:
    """Verify one configuration-managed target or one explicit snapshot."""

    target_kind = _target_kind(target)
    if target_kind is VerificationTarget.NEIGHBOUR:
        if snapshot_path is not None:
            raise ValueError("--snapshot is only valid with --target snapshot")
        path = configuration.rebuilt_neighbour
    elif target_kind is VerificationTarget.CANDIDATE:
        if snapshot_path is not None:
            raise ValueError("--snapshot is only valid with --target snapshot")
        path = configuration.managed_candidate
    else:
        if snapshot_path is None:
            raise ValueError("--snapshot is required with --target snapshot")
        path = Path(snapshot_path).expanduser()

    return verify_database(path, target=target_kind, lock_timeout=lock_timeout)


def verify_database(
    database_path: str | Path,
    *,
    target: VerificationTarget | str = VerificationTarget.NEIGHBOUR,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> VerificationResult:
    """Verify one existing SQLite artifact without opening it for writing."""

    target_kind = _target_kind(target)
    path = _normalize_target_path(database_path)
    timeout_seconds = _validate_lock_timeout(lock_timeout)
    if not path.exists():
        return _missing_result(target_kind, path)

    try:
        with _open_connection(path, "read-only", timeout_seconds) as connection:
            snapshot = _schema_snapshot(connection)
            expected = _reference_snapshot(timeout_seconds)
            schema_compatible = snapshot == expected
            integrity_result = _integrity_result(connection)
            foreign_key_errors = _foreign_key_errors(connection)
            if not schema_compatible:
                return _result(
                    target_kind,
                    path,
                    VerificationStatus.INCOMPATIBLE,
                    schema_compatible=False,
                    user_version=snapshot.user_version,
                    integrity_result=integrity_result,
                    foreign_key_errors=foreign_key_errors,
                )
            if integrity_result != "ok":
                return _result(
                    target_kind,
                    path,
                    VerificationStatus.CORRUPT,
                    schema_compatible=True,
                    user_version=snapshot.user_version,
                    integrity_result=integrity_result,
                    foreign_key_errors=foreign_key_errors,
                )
            if foreign_key_errors:
                return _result(
                    target_kind,
                    path,
                    VerificationStatus.FOREIGN_KEY_INVALID,
                    schema_compatible=True,
                    user_version=snapshot.user_version,
                    integrity_result=integrity_result,
                    foreign_key_errors=foreign_key_errors,
                )

            facts = _read_readiness_facts(connection)
            status = (
                VerificationStatus.REPLACEMENT_READY
                if facts["opening_ready"] and facts["games_ready"]
                else VerificationStatus.STRUCTURALLY_VALID_PARTIAL
            )
            return _result(
                target_kind,
                path,
                status,
                schema_compatible=True,
                user_version=snapshot.user_version,
                integrity_result=integrity_result,
                foreign_key_errors=foreign_key_errors,
                facts=facts,
            )
    except KeyboardInterrupt:
        raise
    except (PermissionError, BlockingIOError, TimeoutError) as error:
        return _unavailable_result(target_kind, path, error)
    except OSError as error:
        if _is_unavailable_os_error(error):
            return _unavailable_result(target_kind, path, error)
        raise
    except DatabaseError as error:
        status = _database_error_status(error)
        if status is VerificationStatus.CORRUPT:
            return _result(
                target_kind,
                path,
                status,
                schema_compatible=False,
                user_version=None,
                integrity_result="unavailable",
                foreign_key_errors=(),
            )
        if status is VerificationStatus.UNAVAILABLE:
            return _unavailable_result(target_kind, path, error)
        raise


def _is_unavailable_os_error(error: OSError) -> bool:
    return error.errno in {EACCES, EAGAIN, EBUSY, EPERM, ETIMEDOUT}


def _database_error_status(error: DatabaseError) -> VerificationStatus | None:
    text = _exception_text(error)
    if any(
        marker in text
        for marker in (
            "file is not a database",
            "database disk image is malformed",
            "database schema is corrupt",
        )
    ):
        return VerificationStatus.CORRUPT
    if any(
        marker in text
        for marker in (
            "database is locked",
            "database table is locked",
            "unable to open database file",
            "permission denied",
            "access is denied",
            "attempt to read a readonly database",
            "attempt to write a readonly database",
            "resource temporarily unavailable",
        )
    ):
        return VerificationStatus.UNAVAILABLE
    return None


def _exception_text(error: BaseException) -> str:
    messages: list[str] = []
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        messages.append(str(current).lower())
        current = current.__cause__ or current.__context__
    return " ".join(messages)


def _unavailable_result(
    target: VerificationTarget,
    path: Path,
    error: BaseException,
) -> VerificationResult:
    del error
    return _result(
        target,
        path,
        VerificationStatus.UNAVAILABLE,
        schema_compatible=False,
        user_version=None,
        integrity_result="unavailable",
        foreign_key_errors=(),
    )


def _target_kind(value: VerificationTarget | str) -> VerificationTarget:
    try:
        return value if isinstance(value, VerificationTarget) else VerificationTarget(value)
    except (TypeError, ValueError) as error:
        allowed = ", ".join(item.value for item in VerificationTarget)
        raise ValueError(f"target must be one of: {allowed}") from error


def _normalize_target_path(value: str | Path) -> Path:
    try:
        return Path(value).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ValueError(f"database target must be a safe file path: {error}") from error


def _integrity_result(connection: Connection) -> str:
    rows = connection.exec_driver_sql("PRAGMA integrity_check").all()
    if len(rows) == 1 and str(rows[0][0]).lower() == "ok":
        return "ok"
    return "; ".join(str(row[0]) for row in rows) or "failed"


def _foreign_key_errors(connection: Connection) -> tuple[str, ...]:
    return tuple(
        ":".join("" if value is None else str(value) for value in row)
        for row in connection.exec_driver_sql("PRAGMA foreign_key_check").all()
    )


def _read_readiness_facts(connection: Connection) -> dict[str, int | bool]:
    counts = {
        "opening_count": _count(connection, "datasource_opening"),
        "opening_route_count": _count(connection, "derived_opening_route"),
        "opening_move_count": _count(connection, "derived_opening_route_move"),
        "position_count": _count(connection, "derived_position"),
        "game_count": _count(connection, "datasource_game"),
        "game_position_count": _count(connection, "derived_game_position"),
    }
    counts["opening_ready"] = (
        counts["opening_count"] > 0
        and counts["opening_route_count"] > 0
        and counts["opening_move_count"] > 0
        and counts["position_count"] > 0
    )
    counts["games_ready"] = (
        counts["game_count"] > 0 and counts["game_position_count"] > 0
    )
    return counts


def _count(connection: Connection, table: str) -> int:
    return int(connection.exec_driver_sql(f"SELECT COUNT(*) FROM {table}").scalar_one())


def _missing_result(target: VerificationTarget, path: Path) -> VerificationResult:
    return _result(
        target,
        path,
        VerificationStatus.MISSING,
        schema_compatible=False,
        user_version=None,
        integrity_result="unavailable",
        foreign_key_errors=(),
    )


def _result(
    target: VerificationTarget,
    path: Path,
    status: VerificationStatus,
    *,
    schema_compatible: bool,
    user_version: int | None,
    integrity_result: str,
    foreign_key_errors: tuple[str, ...],
    facts: dict[str, int | bool] | None = None,
) -> VerificationResult:
    values = facts or {}
    return VerificationResult(
        target=target,
        database_path=path,
        status=status,
        schema_compatible=schema_compatible,
        user_version=user_version,
        integrity_result=integrity_result,
        foreign_key_errors=foreign_key_errors,
        opening_count=int(values.get("opening_count", 0)),
        opening_route_count=int(values.get("opening_route_count", 0)),
        opening_move_count=int(values.get("opening_move_count", 0)),
        position_count=int(values.get("position_count", 0)),
        game_count=int(values.get("game_count", 0)),
        game_position_count=int(values.get("game_position_count", 0)),
    )


__all__ = [
    "VerificationResult",
    "VerificationStatus",
    "VerificationTarget",
    "verify_database",
    "verify_rebuild_target",
]
