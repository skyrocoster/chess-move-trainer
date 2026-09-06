"""Typed operation and outcome boundary for the DB-08 orchestration area."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Literal, Protocol

from .configuration import RebuildConfiguration


class RebuildError(Exception):
    """Base error for the package-owned rebuild boundary."""


class RebuildOperationError(RebuildError):
    """Raised when a rebuild operation cannot complete."""


class RebuildUnavailableError(RebuildOperationError):
    """Raised when an operation is reserved for a later DB-08 stage."""


class RebuildOperation(str, Enum):
    """Operations reserved by the DB-08 command group."""

    REFRESH = "refresh"
    CANDIDATE = "candidate"
    VERIFY = "verify"
    SNAPSHOT = "snapshot"
    REPLACE = "replace"
    ROLLBACK = "rollback"


class OperationStatus(str, Enum):
    """Stable status categories shared by operation adapters."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    INCOMPATIBLE = "incompatible"
    INTERRUPTED = "interrupted"
    RESERVED = "reserved"


class OperationExitCode(IntEnum):
    """CLI-compatible result codes for rebuild operation outcomes."""

    SUCCEEDED = 0
    FAILED = 1
    USAGE = 2
    INCOMPATIBLE = 3
    INTERRUPTED = 130


ExitCode = Literal[0, 1, 2, 3, 130]


@dataclass(frozen=True, slots=True)
class OperationOutcome:
    """Typed result crossing from a rebuild service to a CLI adapter."""

    operation: RebuildOperation
    status: OperationStatus
    message: str
    exit_code: ExitCode


class RebuildOperations(Protocol):
    """The inward-facing service shape used by future DB-08 operation stages."""

    def run(
        self,
        operation: RebuildOperation,
        configuration: RebuildConfiguration,
    ) -> OperationOutcome:
        """Run one operation against the package-owned configuration."""


def reserve_operation(
    operation: RebuildOperation,
    configuration: RebuildConfiguration,
) -> OperationOutcome:
    """Return the boundary outcome until a later stage supplies the service."""

    del configuration
    return OperationOutcome(
        operation=operation,
        status=OperationStatus.RESERVED,
        message=f"DB-08 {operation.value} is reserved for a later implementation stage.",
        exit_code=OperationExitCode.FAILED,
    )


__all__ = [
    "ExitCode",
    "OperationExitCode",
    "OperationOutcome",
    "OperationStatus",
    "RebuildError",
    "RebuildOperation",
    "RebuildOperationError",
    "RebuildOperations",
    "RebuildUnavailableError",
    "reserve_operation",
]
