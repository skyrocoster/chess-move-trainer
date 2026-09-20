"""Stored scalar validation for training-requirement row loaders."""

from __future__ import annotations

from .training_requirements_models import TrainingRequirementStorageError


def _text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TrainingRequirementStorageError(f"{name} is malformed")
    return value


def _positive_int(value: object, name: str) -> int:
    if type(value) is not int or value < 1:
        raise TrainingRequirementStorageError(f"{name} is malformed")
    return value


def _non_negative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise TrainingRequirementStorageError(f"{name} is malformed")
    return value
