"""Configuration values and validation for game acquisition and import."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml


ACQUIRE_DEFAULT_TIMEOUT_SECONDS = 30.0
ACQUIRE_DEFAULT_DELAY_SECONDS = 0.25


class GamesConfigurationError(ValueError):
    """Raised when game-tool configuration cannot produce valid command values."""


@dataclass(frozen=True, slots=True)
class AcquireConfiguration:
    """Effective values required by game acquisition."""

    username: str
    trainer_chesscom_uuid: UUID
    request_timeout: float
    request_delay: float


@dataclass(frozen=True, slots=True)
class ImportConfiguration:
    """Effective values required by raw game import."""

    trainer_chesscom_uuid: UUID


def load_acquire_configuration(
    path: Path,
    *,
    username: str | None = None,
    trainer_chesscom_uuid: str | UUID | None = None,
    request_timeout: float | None = None,
    request_delay: float | None = None,
) -> AcquireConfiguration:
    """Load and validate effective acquisition values, preferring explicit overrides."""

    values = _load_yaml_mapping(path)
    effective_username = username if username is not None else values.get("username")
    effective_uuid = (
        trainer_chesscom_uuid
        if trainer_chesscom_uuid is not None
        else values.get("trainer_chesscom_uuid")
    )
    effective_timeout = (
        request_timeout
        if request_timeout is not None
        else values.get("request_timeout", ACQUIRE_DEFAULT_TIMEOUT_SECONDS)
    )
    effective_delay = (
        request_delay
        if request_delay is not None
        else values.get("request_delay", ACQUIRE_DEFAULT_DELAY_SECONDS)
    )

    return AcquireConfiguration(
        username=_required_text(effective_username, "username"),
        trainer_chesscom_uuid=_uuid(effective_uuid),
        request_timeout=_finite_number(effective_timeout, "request_timeout", positive=True),
        request_delay=_finite_number(effective_delay, "request_delay", positive=False),
    )


def load_import_configuration(
    path: Path,
    *,
    trainer_chesscom_uuid: str | UUID | None = None,
) -> ImportConfiguration:
    """Load and validate effective import values, preferring an explicit UUID override."""

    values = _load_yaml_mapping(path)
    effective_uuid = (
        trainer_chesscom_uuid
        if trainer_chesscom_uuid is not None
        else values.get("trainer_chesscom_uuid")
    )
    return ImportConfiguration(trainer_chesscom_uuid=_uuid(effective_uuid))


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise GamesConfigurationError(f"configuration file does not exist or is not a file: {path}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise GamesConfigurationError(f"could not read configuration YAML: {error}") from error
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise GamesConfigurationError("configuration YAML must contain a mapping")
    return loaded


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GamesConfigurationError(f"{field} must be a non-empty string")
    return value.strip()


def _uuid(value: object) -> UUID:
    if isinstance(value, UUID):
        return value
    if not isinstance(value, str):
        raise GamesConfigurationError("trainer_chesscom_uuid must be a valid UUID")
    try:
        return UUID(value)
    except ValueError as error:
        raise GamesConfigurationError("trainer_chesscom_uuid must be a valid UUID") from error


def _finite_number(value: object, field: str, *, positive: bool) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GamesConfigurationError(f"{field} must be a finite number")
    result = float(value)
    valid_bound = result > 0 if positive else result >= 0
    if not math.isfinite(result) or not valid_bound:
        bound = "greater than zero" if positive else "zero or greater"
        raise GamesConfigurationError(f"{field} must be finite and {bound}")
    return result
