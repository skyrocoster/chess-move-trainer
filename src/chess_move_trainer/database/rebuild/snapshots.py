"""Verified, package-owned SQLite snapshots for the rebuilt neighbour."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..connection import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    _open_connection,
    _validate_lock_timeout,
)
from .configuration import RebuildConfiguration
from .operations import ExitCode, OperationExitCode, OperationStatus, RebuildOperation
from .verification import VerificationResult, VerificationStatus, VerificationTarget, verify_rebuild_target


SNAPSHOT_MARKER = ".snapshot-"
SNAPSHOT_EXTENSION = ".db"
MAX_RETAINED_SNAPSHOTS = 3


class SnapshotError(RuntimeError):
    """Raised when a verified snapshot cannot be safely published."""


@dataclass(frozen=True, slots=True)
class SnapshotOutcome:
    """Stable result of one standalone snapshot operation."""

    operation: RebuildOperation
    status: OperationStatus
    message: str
    exit_code: ExitCode
    source_path: Path
    snapshot_path: Path | None
    verification: VerificationResult | None
    retained_snapshots: tuple[Path, ...]

    @property
    def completed(self) -> bool:
        """Whether the new snapshot was published and retained safely."""

        return self.status is OperationStatus.SUCCEEDED

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for CLI JSON output."""

        return {
            "exit_code": int(self.exit_code),
            "message": self.message,
            "operation": self.operation.value,
            "retained_snapshots": [str(path) for path in self.retained_snapshots],
            "snapshot_path": None if self.snapshot_path is None else str(self.snapshot_path),
            "source_path": str(self.source_path),
            "status": self.status.value,
            "verification": (
                None if self.verification is None else self.verification.as_dict()
            ),
        }


def create_snapshot(
    configuration: RebuildConfiguration,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> SnapshotOutcome:
    """Back up the configured neighbour, verify it, and retain the newest three."""

    if not isinstance(configuration, RebuildConfiguration):
        raise SnapshotError("configuration must be a RebuildConfiguration")
    try:
        timeout_seconds = _validate_lock_timeout(lock_timeout)
    except ValueError as error:
        raise SnapshotError(str(error)) from error

    source_path = configuration.rebuilt_neighbour
    source_verification = verify_rebuild_target(
        configuration,
        VerificationTarget.NEIGHBOUR,
        lock_timeout=timeout_seconds,
    )
    if not source_verification.structurally_valid:
        return SnapshotOutcome(
            operation=RebuildOperation.SNAPSHOT,
            status=_status_for_verification(source_verification),
            message=(
                "Snapshot was not created because the neighbour failed "
                f"verification: {source_verification.status.value}."
            ),
            exit_code=_exit_code_for_status(_status_for_verification(source_verification)),
            source_path=source_path,
            snapshot_path=None,
            verification=source_verification,
            retained_snapshots=(),
        )

    final_path = _next_snapshot_path(source_path)
    temporary_path = _temporary_path(final_path)
    final_verification: VerificationResult | None = None
    published = False
    try:
        _backup_database(source_path, temporary_path, timeout_seconds)
        temporary_verification = verify_rebuild_target(
            configuration,
            VerificationTarget.SNAPSHOT,
            snapshot_path=temporary_path,
            lock_timeout=timeout_seconds,
        )
        if not temporary_verification.structurally_valid:
            raise SnapshotError(
                f"temporary snapshot failed verification: {temporary_verification.status.value}"
            )

        _fsync_file(temporary_path)
        os.replace(temporary_path, final_path)
        published = True
        final_verification = verify_rebuild_target(
            configuration,
            VerificationTarget.SNAPSHOT,
            snapshot_path=final_path,
            lock_timeout=timeout_seconds,
        )
        if not final_verification.structurally_valid:
            raise SnapshotError(
                f"published snapshot failed verification: {final_verification.status.value}"
            )

        retained = _retain_verified_snapshots(configuration, timeout_seconds)
        return SnapshotOutcome(
            operation=RebuildOperation.SNAPSHOT,
            status=OperationStatus.SUCCEEDED,
            message=(
                f"Snapshot created and verified: {final_path}; "
                f"retained {len(retained)} snapshot(s)."
            ),
            exit_code=OperationExitCode.SUCCEEDED,
            source_path=source_path,
            snapshot_path=final_path,
            verification=final_verification,
            retained_snapshots=retained,
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        if (
            published
            and final_path.exists()
            and (final_verification is None or not final_verification.structurally_valid)
        ):
            _remove_if_present(final_path)
        return SnapshotOutcome(
            operation=RebuildOperation.SNAPSHOT,
            status=OperationStatus.FAILED,
            message=f"Snapshot failed: {error}",
            exit_code=OperationExitCode.FAILED,
            source_path=source_path,
            snapshot_path=final_path if published and final_path.exists() else None,
            verification=final_verification,
            retained_snapshots=(),
        )
    finally:
        _remove_if_present(temporary_path)


def _backup_database(source_path: Path, temporary_path: Path, lock_timeout: float) -> None:
    """Use the driver's backup facility while keeping both handles internal."""

    with _open_connection(source_path, "read-only", lock_timeout) as source:
        with _open_connection(temporary_path, "read-write", lock_timeout) as target:
            source_driver = getattr(source.connection, "driver_connection", source.connection)
            target_driver = getattr(target.connection, "driver_connection", target.connection)
            source_driver.backup(target_driver, pages=1000, sleep=0.05)
            target_driver.commit()


def _retain_verified_snapshots(
    configuration: RebuildConfiguration,
    lock_timeout: float,
) -> tuple[Path, ...]:
    paths = sorted(
        _snapshot_paths(configuration.rebuilt_neighbour),
        key=lambda path: path.name,
        reverse=True,
    )
    verified: list[Path] = []
    unverified: list[Path] = []
    for path in paths:
        result = verify_rebuild_target(
            configuration,
            VerificationTarget.SNAPSHOT,
            snapshot_path=path,
            lock_timeout=lock_timeout,
        )
        if result.structurally_valid:
            verified.append(path)
        else:
            unverified.append(path)

    retained = tuple(verified[:MAX_RETAINED_SNAPSHOTS])
    for path in (*verified[MAX_RETAINED_SNAPSHOTS:], *unverified):
        _remove_required(path)
    return retained


def _snapshot_paths(source_path: Path) -> tuple[Path, ...]:
    pattern = f"{source_path.name}{SNAPSHOT_MARKER}*{SNAPSHOT_EXTENSION}"
    return tuple(path for path in source_path.parent.glob(pattern) if path.is_file())


def _next_snapshot_path(source_path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    base = f"{source_path.name}{SNAPSHOT_MARKER}{stamp}"
    for sequence in range(10_000):
        candidate = source_path.parent / f"{base}-{sequence:03d}{SNAPSHOT_EXTENSION}"
        if not candidate.exists():
            return candidate
    raise SnapshotError("could not allocate a unique snapshot artifact name")


def _temporary_path(final_path: Path) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{final_path.name}.",
        suffix=".tmp",
        dir=final_path.parent,
    )
    os.close(descriptor)
    return Path(name)


def _fsync_file(path: Path) -> None:
    with path.open("r+b") as stream:
        os.fsync(stream.fileno())


def _remove_if_present(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _remove_required(path: Path) -> None:
    try:
        path.unlink()
    except OSError as error:
        raise SnapshotError(f"could not remove retained snapshot: {path}") from error


def _status_for_verification(result: VerificationResult) -> OperationStatus:
    return (
        OperationStatus.INCOMPATIBLE
        if result.status is VerificationStatus.INCOMPATIBLE
        else OperationStatus.FAILED
    )


def _exit_code_for_status(status: OperationStatus) -> ExitCode:
    return (
        OperationExitCode.INCOMPATIBLE
        if status is OperationStatus.INCOMPATIBLE
        else OperationExitCode.FAILED
    )


__all__ = [
    "MAX_RETAINED_SNAPSHOTS",
    "SNAPSHOT_EXTENSION",
    "SNAPSHOT_MARKER",
    "SnapshotError",
    "SnapshotOutcome",
    "create_snapshot",
]
