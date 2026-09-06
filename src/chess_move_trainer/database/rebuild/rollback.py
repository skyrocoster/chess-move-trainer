"""Exclusive rollback from retained, verified DB-08 snapshots."""

from __future__ import annotations

import os as _os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _validate_lock_timeout
from .configuration import RebuildConfiguration
from .exclusivity import (
    ExclusiveAccessError,
    exclusive_destination,
    replace_destination,
)
from .operations import (
    ExitCode,
    OperationExitCode,
    OperationStatus,
    RebuildOperation,
    RebuildOperationError,
)
from .replacement import _status_for_verification
from .snapshots import (
    SnapshotError,
    SnapshotOutcome,
    _snapshot_paths,
    create_snapshot,
)
from .verification import (
    VerificationResult,
    VerificationTarget,
    verify_rebuild_target,
)


class RollbackInputError(ValueError):
    """Raised when rollback names a source outside retained snapshots."""


class RollbackError(RebuildOperationError):
    """Raised when rollback inputs cannot be used safely."""


class _RollbackOS:
    """Module-local filesystem seam isolated from snapshot publication."""

    close = staticmethod(_os.close)
    fsync = staticmethod(_os.fsync)
    replace = staticmethod(replace_destination)


os = _RollbackOS()


@dataclass(frozen=True, slots=True)
class RollbackOutcome:
    """Stable result of one exclusive managed-neighbour rollback."""

    operation: RebuildOperation
    status: OperationStatus
    message: str
    exit_code: ExitCode
    neighbour_path: Path
    selected_snapshot: Path | None
    verification: VerificationResult | None
    snapshot: SnapshotOutcome | None

    @property
    def completed(self) -> bool:
        """Whether the selected snapshot was atomically restored."""

        return self.status is OperationStatus.SUCCEEDED

    @property
    def snapshot_path(self) -> Path | None:
        """Return the automatic pre-rollback recovery point, if any."""

        return None if self.snapshot is None else self.snapshot.snapshot_path

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for CLI JSON output."""

        return {
            "exit_code": int(self.exit_code),
            "message": self.message,
            "neighbour_path": str(self.neighbour_path),
            "operation": self.operation.value,
            "selected_snapshot": (
                None if self.selected_snapshot is None else str(self.selected_snapshot)
            ),
            "snapshot": None if self.snapshot is None else self.snapshot.as_dict(),
            "snapshot_path": (
                None if self.snapshot_path is None else str(self.snapshot_path)
            ),
            "status": self.status.value,
            "verification": (
                None if self.verification is None else self.verification.as_dict()
            ),
        }


def rollback_rebuilt_neighbour(
    configuration: RebuildConfiguration,
    *,
    snapshot_path: str | Path | None = None,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> RollbackOutcome:
    """Restore the newest or explicitly selected retained managed snapshot."""

    if not isinstance(configuration, RebuildConfiguration):
        raise RollbackError("configuration must be a RebuildConfiguration")
    try:
        timeout_seconds = _validate_lock_timeout(lock_timeout)
    except ValueError as error:
        raise RollbackError(str(error)) from error

    neighbour_path = configuration.rebuilt_neighbour
    retained = _verified_retained_snapshots(configuration, timeout_seconds)
    selected = _select_snapshot(retained, snapshot_path)
    if selected is None:
        return RollbackOutcome(
            operation=RebuildOperation.ROLLBACK,
            status=OperationStatus.FAILED,
            message=(
                "Rollback was not performed because no retained verified "
                "snapshot is available for the configured neighbour."
            ),
            exit_code=OperationExitCode.FAILED,
            neighbour_path=neighbour_path,
            selected_snapshot=None,
            verification=None,
            snapshot=None,
        )

    selected_verification: VerificationResult | None = None
    snapshot: SnapshotOutcome | None = None
    temporary_path: Path | None = None
    try:
        with exclusive_destination(neighbour_path):
            # Reverify after ownership is established.  This closes the gap
            # between source selection and the destructive portion of rollback.
            selected_verification = verify_rebuild_target(
                configuration,
                VerificationTarget.SNAPSHOT,
                snapshot_path=selected,
                lock_timeout=timeout_seconds,
            )
            if not selected_verification.structurally_valid:
                status = _status_for_verification(selected_verification)
                return RollbackOutcome(
                    operation=RebuildOperation.ROLLBACK,
                    status=status,
                    message=(
                        "Rollback was not performed because the selected retained "
                        f"snapshot failed re-verification: {selected_verification.status.value}."
                    ),
                    exit_code=_exit_code_for_status(status),
                    neighbour_path=neighbour_path,
                    selected_snapshot=selected,
                    verification=selected_verification,
                    snapshot=None,
                )

            # Preserve the selected source before retention can remove an older
            # snapshot when the fresh current-neighbour snapshot is published.
            temporary_path = _copy_to_temporary(selected, neighbour_path.parent)
            temporary_verification = verify_rebuild_target(
                configuration,
                VerificationTarget.SNAPSHOT,
                snapshot_path=temporary_path,
                lock_timeout=timeout_seconds,
            )
            if not temporary_verification.structurally_valid:
                raise RollbackError(
                    "temporary rollback source failed verification: "
                    f"{temporary_verification.status.value}"
                )

            snapshot = create_snapshot(configuration, lock_timeout=timeout_seconds)
            if not snapshot.completed:
                status = _status_for_snapshot(snapshot)
                return RollbackOutcome(
                    operation=RebuildOperation.ROLLBACK,
                    status=status,
                    message=(
                        "Rollback was not performed because the current neighbour "
                        "could not be preserved in a verified snapshot: "
                        f"{snapshot.message}"
                    ),
                    exit_code=_exit_code_for_status(status),
                    neighbour_path=neighbour_path,
                    selected_snapshot=selected,
                    verification=selected_verification,
                    snapshot=snapshot,
                )

            # The temporary source is beside the configured neighbour, so this
            # same-volume replace is atomic and cannot expose a partial database.
            _atomic_replace(temporary_path, neighbour_path)
            temporary_path = None
    except KeyboardInterrupt:
        raise
    except (ExclusiveAccessError, OSError, RollbackError, SnapshotError) as error:
        return RollbackOutcome(
            operation=RebuildOperation.ROLLBACK,
            status=OperationStatus.FAILED,
            message=(
                f"Rollback failed: {error}; the configured neighbour was not "
                "overwritten."
            ),
            exit_code=OperationExitCode.FAILED,
            neighbour_path=neighbour_path,
            selected_snapshot=selected,
            verification=selected_verification,
            snapshot=snapshot,
        )
    finally:
        if temporary_path is not None:
            _remove_if_present(temporary_path)

    return RollbackOutcome(
        operation=RebuildOperation.ROLLBACK,
        status=OperationStatus.SUCCEEDED,
        message=(
            f"Rollback completed atomically: restored {selected} to "
            f"{neighbour_path}; snapshot retained at {snapshot.snapshot_path}."
        ),
        exit_code=OperationExitCode.SUCCEEDED,
        neighbour_path=neighbour_path,
        selected_snapshot=selected,
        verification=selected_verification,
        snapshot=snapshot,
    )


rollback_neighbour = rollback_rebuilt_neighbour


def _verified_retained_snapshots(
    configuration: RebuildConfiguration,
    lock_timeout: float,
) -> tuple[Path, ...]:
    """Return only the newest three managed snapshot artifacts that verify."""

    verified: list[Path] = []
    paths = sorted(
        _snapshot_paths(configuration.rebuilt_neighbour),
        key=lambda path: path.name,
        reverse=True,
    )
    for path in paths:
        if path.is_symlink():
            continue
        result = verify_rebuild_target(
            configuration,
            VerificationTarget.SNAPSHOT,
            snapshot_path=path,
            lock_timeout=lock_timeout,
        )
        if result.structurally_valid:
            verified.append(path)
    return tuple(verified[:3])


def _select_snapshot(
    retained: tuple[Path, ...], requested: str | Path | None
) -> Path | None:
    if requested is None:
        return retained[0] if retained else None
    try:
        selected = Path(requested).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise RollbackInputError(f"snapshot path is not safe: {error}") from error
    if selected not in retained:
        raise RollbackInputError(
            "snapshot must be one of the three newest retained verified "
            "snapshots managed beside the configured neighbour"
        )
    return selected


def _copy_to_temporary(source: Path, directory: Path) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=".rollback-source-",
        suffix=".tmp",
        dir=directory,
    )
    os.close(descriptor)
    temporary = Path(name)
    try:
        shutil.copyfile(source, temporary)
        with temporary.open("r+b") as stream:
            os.fsync(stream.fileno())
    except BaseException:
        _remove_if_present(temporary)
        raise
    return temporary


def _remove_if_present(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _atomic_replace(source: Path, target: Path) -> None:
    """Replace one same-volume artifact without exposing a partial file."""

    os.replace(source, target)


def _status_for_snapshot(result: SnapshotOutcome) -> OperationStatus:
    if result.verification is not None:
        return _status_for_verification(result.verification)
    return OperationStatus.FAILED


def _exit_code_for_status(status: OperationStatus) -> ExitCode:
    return (
        OperationExitCode.INCOMPATIBLE
        if status is OperationStatus.INCOMPATIBLE
        else OperationExitCode.FAILED
    )


__all__ = [
    "RollbackError",
    "RollbackInputError",
    "RollbackOutcome",
    "rollback_neighbour",
    "rollback_rebuilt_neighbour",
]
