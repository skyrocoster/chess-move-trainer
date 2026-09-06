"""Typed configuration for the managed DB-08 rebuilt-neighbour destination."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REBUILT_NEIGHBOUR_KEY = "rebuilt_neighbour"
MANAGED_CANDIDATE_SUFFIX = ".candidate"
_SUPPORTED_KEYS = frozenset({REBUILT_NEIGHBOUR_KEY})


class RebuildConfigurationError(ValueError):
    """Raised when DB-08 configuration cannot define one safe destination."""


@dataclass(frozen=True, slots=True)
class RebuildConfiguration:
    """One configured destination and its package-owned sibling candidate."""

    rebuilt_neighbour: Path

    def __post_init__(self) -> None:
        destination = _normalize_destination(self.rebuilt_neighbour)
        object.__setattr__(self, "rebuilt_neighbour", destination)

        candidate = self.managed_candidate
        if candidate.exists() and candidate.is_dir():
            raise RebuildConfigurationError(
                f"managed candidate path must not be a directory: {candidate}"
            )

    @property
    def managed_candidate(self) -> Path:
        """Return the deterministic temporary sibling owned by DB-08."""

        return self.rebuilt_neighbour.with_name(
            f"{self.rebuilt_neighbour.name}{MANAGED_CANDIDATE_SUFFIX}"
        )

    @property
    def candidate(self) -> Path:
        """Compatibility spelling for the managed candidate path."""

        return self.managed_candidate


def load_rebuild_configuration(path: Path) -> RebuildConfiguration:
    """Load the single-value DB-08 YAML configuration."""

    if not path.is_file():
        raise RebuildConfigurationError(
            f"configuration file does not exist or is not a file: {path}"
        )
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise RebuildConfigurationError(f"could not read configuration YAML: {error}") from error

    if loaded is None:
        values: dict[str, Any] = {}
    elif isinstance(loaded, dict):
        values = loaded
    else:
        raise RebuildConfigurationError("configuration YAML must contain a mapping")

    unexpected = sorted(set(values) - _SUPPORTED_KEYS)
    if unexpected:
        names = ", ".join(str(name) for name in unexpected)
        raise RebuildConfigurationError(
            f"configuration contains unsupported value(s): {names}; "
            f"only {REBUILT_NEIGHBOUR_KEY} is allowed"
        )
    if REBUILT_NEIGHBOUR_KEY not in values:
        raise RebuildConfigurationError(
            f"configuration must define {REBUILT_NEIGHBOUR_KEY}"
        )

    value = values[REBUILT_NEIGHBOUR_KEY]
    if not isinstance(value, str) or not value.strip():
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must be a non-empty path"
        )
    try:
        return RebuildConfiguration(Path(value.strip()).expanduser())
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        if isinstance(error, RebuildConfigurationError):
            raise
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must be a safe file path: {error}"
        ) from error


def _normalize_destination(value: Path) -> Path:
    if not isinstance(value, Path):
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must be a path"
        )
    if "\x00" in str(value):
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must not contain a null character"
        )
    try:
        destination = value.resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must resolve to one file path: {error}"
        ) from error
    if not destination.name:
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must identify a file, not a directory"
        )
    if destination.exists() and destination.is_dir():
        raise RebuildConfigurationError(
            f"{REBUILT_NEIGHBOUR_KEY} must identify a file, not a directory: {destination}"
        )
    candidate = destination.with_name(f"{destination.name}{MANAGED_CANDIDATE_SUFFIX}")
    if os.path.normcase(str(candidate)) == os.path.normcase(str(destination)):
        raise RebuildConfigurationError(
            f"managed candidate path is ambiguous for destination: {destination}"
        )
    return destination
