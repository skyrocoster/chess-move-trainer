"""Exclusive, snapshot-protected replacement of the managed candidate."""

from __future__ import annotations

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
from .snapshots import SnapshotError, SnapshotOutcome, create_snapshot
from .verification import (
    VerificationResult,
    VerificationStatus,
    VerificationTarget,
    verify_rebuild_target,
)


class ReplacementError(RebuildOperationError):
    """Raised when managed replacement inputs cannot be used safely."""


class _ReplacementOS:
    """Module-local filesystem seam so snapshot publication stays independent."""

    replace = staticmethod(replace_destination)


os = _ReplacementOS()


@dataclass(frozen=True, slots=True)
class ReplacementOutcome:
    """Stable result of one exclusive managed-candidate replacement."""

    operation: RebuildOperation
    status: OperationStatus
    message: str
    exit_code: ExitCode
    neighbour_path: Path
    candidate_path: Path
    verification: VerificationResult | None
    snapshot: SnapshotOutcome | None

    @property
    def completed(self) -> bool:
        """Whether the verified candidate was atomically installed."""

        return self.status is OperationStatus.SUCCEEDED

    @property
    def snapshot_path(self) -> Path | None:
        """Return the automatic pre-replacement recovery point, if any."""

        return None if self.snapshot is None else self.snapshot.snapshot_path

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for CLI JSON output."""

        return {
            "candidate_path": str(self.candidate_path),
            "exit_code": int(self.exit_code),
            "message": self.message,
            "neighbour_path": str(self.neighbour_path),
            "operation": self.operation.value,
            "snapshot": None if self.snapshot is None else self.snapshot.as_dict(),
            "snapshot_path": (
                None if self.snapshot_path is None else str(self.snapshot_path)
            ),
            "status": self.status.value,
            "verification": (
                None if self.verification is None else self.verification.as_dict()
            ),
        }


def replace_rebuilt_neighbour(
    configuration: RebuildConfiguration,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> ReplacementOutcome:
    """Replace the configured neighbour from its verified managed sibling.

    Verification is read-only and happens before ownership is requested.  The
    exclusive destination boundary begins before the automatic snapshot and
    remains held through the atomic filesystem swap.
    """

    if not isinstance(configuration, RebuildConfiguration):
        raise ReplacementError("configuration must be a RebuildConfiguration")
    try:
        timeout_seconds = _validate_lock_timeout(lock_timeout)
    except ValueError as error:
        raise ReplacementError(str(error)) from error

    neighbour_path = configuration.rebuilt_neighbour
    candidate_path = configuration.managed_candidate
    candidate_verification = verify_rebuild_target(
        configuration,
        VerificationTarget.CANDIDATE,
        lock_timeout=timeout_seconds,
    )
    if not candidate_verification.replacement_ready:
        status = _status_for_verification(candidate_verification)
        return ReplacementOutcome(
            operation=RebuildOperation.REPLACE,
            status=status,
            message=(
                "Replacement was not started because the managed candidate "
                f"is not replacement-ready: {candidate_verification.status.value}."
            ),
            exit_code=_exit_code_for_status(status),
            neighbour_path=neighbour_path,
            candidate_path=candidate_path,
            verification=candidate_verification,
            snapshot=None,
        )
    if candidate_path.is_symlink():
        return ReplacementOutcome(
            operation=RebuildOperation.REPLACE,
            status=OperationStatus.FAILED,
            message=(
                "Replacement was not started because the managed candidate is "
                "a symbolic link rather than its owned sibling file."
            ),
            exit_code=OperationExitCode.FAILED,
            neighbour_path=neighbour_path,
            candidate_path=candidate_path,
            verification=candidate_verification,
            snapshot=None,
        )

    snapshot: SnapshotOutcome | None = None
    try:
        with exclusive_destination(neighbour_path):
            snapshot = create_snapshot(configuration, lock_timeout=timeout_seconds)
            if not snapshot.completed:
                return ReplacementOutcome(
                    operation=RebuildOperation.REPLACE,
                    status=_status_for_snapshot(snapshot),
                    message=(
                        "Replacement was not performed because the automatic "
                        "verified neighbour snapshot failed: "
                        f"{snapshot.message}"
                    ),
                    exit_code=_exit_code_for_status(_status_for_snapshot(snapshot)),
                    neighbour_path=neighbour_path,
                    candidate_path=candidate_path,
                    verification=candidate_verification,
                    snapshot=snapshot,
                )

            # os.replace is atomic on the same volume.  A failed replace leaves
            # the original neighbour in place; the verified snapshot is retained
            # independently as the recovery point.
            os.replace(candidate_path, neighbour_path)
    except KeyboardInterrupt:
        raise
    except (ExclusiveAccessError, SnapshotError, OSError) as error:
        return ReplacementOutcome(
            operation=RebuildOperation.REPLACE,
            status=OperationStatus.FAILED,
            message=(
                f"Replacement failed: {error}; the configured neighbour was "
                "not replaced."
            ),
            exit_code=OperationExitCode.FAILED,
            neighbour_path=neighbour_path,
            candidate_path=candidate_path,
            verification=candidate_verification,
            snapshot=snapshot,
        )

    return ReplacementOutcome(
        operation=RebuildOperation.REPLACE,
        status=OperationStatus.SUCCEEDED,
        message=(
            f"Replacement completed atomically: {neighbour_path} now contains "
            f"the managed candidate; snapshot retained at {snapshot.snapshot_path}."
        ),
        exit_code=OperationExitCode.SUCCEEDED,
        neighbour_path=neighbour_path,
        candidate_path=candidate_path,
        verification=candidate_verification,
        snapshot=snapshot,
    )


replace_candidate = replace_rebuilt_neighbour


def _status_for_verification(result: VerificationResult) -> OperationStatus:
    return (
        OperationStatus.INCOMPATIBLE
        if result.status is VerificationStatus.INCOMPATIBLE
        else OperationStatus.FAILED
    )


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
    "ExclusiveAccessError",
    "ReplacementError",
    "ReplacementOutcome",
    "replace_candidate",
    "replace_rebuilt_neighbour",
]
