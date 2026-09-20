"""Clock and SQLite lock helpers for training-answer submission."""

from __future__ import annotations

import sqlite3
from datetime import UTC, date, datetime
from typing import Callable

from .training_requirements_models import TrainingRequirementStorageError

UtcCalendarDateClock = Callable[[], date | datetime]


def _utc_today() -> date:
    return datetime.now(UTC).date()


def _clock_date(clock: UtcCalendarDateClock) -> date:
    try:
        value = clock()
    except Exception as error:
        raise TrainingRequirementStorageError(
            "UTC calendar-date clock could not be read"
        ) from error
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise TrainingRequirementStorageError(
                "UTC calendar-date clock must return an aware datetime"
            )
        return value.astimezone(UTC).date()
    if isinstance(value, date):
        return value
    raise TrainingRequirementStorageError("UTC calendar-date clock must return a date")


def _is_lock_failure(error: BaseException) -> bool:
    pending: list[BaseException] = [error]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        marker = id(current)
        if marker in seen:
            continue
        seen.add(marker)
        if isinstance(current, sqlite3.OperationalError):
            message = str(current).lower()
            if "locked" in message or "busy" in message:
                return True
        for attribute in ("orig", "__cause__", "__context__"):
            nested = getattr(current, attribute, None)
            if isinstance(nested, BaseException):
                pending.append(nested)
    return False
