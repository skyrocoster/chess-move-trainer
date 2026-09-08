"""Managed sibling-candidate staging for DB-08."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from uuid import UUID

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _validate_lock_timeout
from .configuration import RebuildConfiguration, RebuildConfigurationError
from .operations import ExitCode, OperationExitCode, OperationStatus, RebuildOperation
from .refresh import RefreshInputError, RefreshOutcome, refresh_database
from .verification import (
    VerificationResult,
    VerificationStatus,
    VerificationTarget,
)


@dataclass(frozen=True, slots=True)
class CandidateOutcome:
    """Stable result of one managed-candidate refresh and verification."""

    operation: RebuildOperation
    status: OperationStatus
    message: str
    exit_code: ExitCode
    candidate_path: Path
    refresh: RefreshOutcome | None
    verification: VerificationResult | None

    @property
    def completed(self) -> bool:
        """Whether the isolated candidate is replacement-ready."""

        return self.status is OperationStatus.SUCCEEDED

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for CLI JSON output."""

        return {
            "candidate_path": str(self.candidate_path),
            "exit_code": int(self.exit_code),
            "message": self.message,
            "operation": self.operation.value,
            "refresh": None if self.refresh is None else self.refresh.as_dict(),
            "status": self.status.value,
            "verification": (
                None if self.verification is None else self.verification.as_dict()
            ),
        }


def stage_candidate(
    configuration: RebuildConfiguration,
    *,
    opening_source_dir: str | Path | None = None,
    raw_root: str | Path | None = None,
    trainer_chesscom_uuid: UUID | str | None = None,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> CandidateOutcome:
    """Refresh and verify only the package-owned sibling candidate path."""

    if not isinstance(configuration, RebuildConfiguration):
        raise RebuildConfigurationError("configuration must be a RebuildConfiguration")
    try:
        timeout_seconds = _validate_lock_timeout(lock_timeout)
    except ValueError as error:
        raise RebuildConfigurationError(str(error)) from error

    candidate_path = configuration.managed_candidate
    refresh: RefreshOutcome | None = None
    verification: VerificationResult | None = None
    try:
        candidate_configuration = RebuildConfiguration(candidate_path)
        if candidate_configuration.rebuilt_neighbour != candidate_path:
            raise RebuildConfigurationError(
                "managed candidate must remain the configured sibling path"
            )
        if candidate_path.exists():
            try:
                if candidate_path.samefile(configuration.rebuilt_neighbour):
                    raise RebuildConfigurationError(
                        "managed candidate must not share the neighbour file"
                    )
            except FileNotFoundError:
                pass
        refresh = refresh_database(
            candidate_configuration,
            opening_source_dir=opening_source_dir,
            raw_root=raw_root,
            trainer_chesscom_uuid=trainer_chesscom_uuid,
            lock_timeout=timeout_seconds,
        )
        if refresh.verification is not None:
            verification = replace(
                refresh.verification,
                target=VerificationTarget.CANDIDATE,
            )
    except KeyboardInterrupt:
        raise
    except RefreshInputError:
        raise
    except Exception as error:
        return CandidateOutcome(
            operation=RebuildOperation.CANDIDATE,
            status=OperationStatus.FAILED,
            message=(
                f"Candidate staging failed: {error}; the configured neighbour "
                "was not modified."
            ),
            exit_code=OperationExitCode.FAILED,
            candidate_path=candidate_path,
            refresh=refresh,
            verification=verification,
        )

    if refresh.completed and verification is not None and verification.replacement_ready:
        return CandidateOutcome(
            operation=RebuildOperation.CANDIDATE,
            status=OperationStatus.SUCCEEDED,
            message=(
                f"Managed candidate staged and verified as replacement-ready: "
                f"{candidate_path}"
            ),
            exit_code=OperationExitCode.SUCCEEDED,
            candidate_path=candidate_path,
            refresh=refresh,
            verification=verification,
        )

    status = (
        OperationStatus.INCOMPATIBLE
        if (
            verification is not None
            and verification.status is VerificationStatus.INCOMPATIBLE
        )
        or refresh.status is OperationStatus.INCOMPATIBLE
        else OperationStatus.FAILED
    )
    exit_code = (
        OperationExitCode.INCOMPATIBLE
        if status is OperationStatus.INCOMPATIBLE
        else OperationExitCode.FAILED
    )
    return CandidateOutcome(
        operation=RebuildOperation.CANDIDATE,
        status=status,
        message=(
            f"Candidate staging incomplete at {candidate_path}; it is not "
            "replacement-ready and the configured neighbour was not modified."
        ),
        exit_code=exit_code,
        candidate_path=candidate_path,
        refresh=refresh,
        verification=verification,
    )


__all__ = ["CandidateOutcome", "stage_candidate"]
