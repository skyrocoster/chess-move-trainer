"""Synchronous Chess.com archive discovery and raw-month acquisition."""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote, unquote, urlsplit

import httpx

from .configuration import AcquireConfiguration
from .raw_storage import load_month, merge_current_month, publish_month


CHESSCOM_API_ORIGIN = "https://api.chess.com"
_MONTH_PATH = re.compile(r"^/pub/player/([^/]+)/games/(\d{4})/(\d{2})$")


class AcquisitionError(RuntimeError):
    """Raised when archive discovery cannot safely identify listed months."""


class AcquisitionClock(Protocol):
    """Injectable UTC clock used to select the current archive month."""

    def now(self) -> datetime: ...


class JsonTransport(Protocol):
    """Injectable synchronous JSON transport for deterministic acquisition."""

    def get_json(self, url: str, *, timeout: float) -> Any: ...


@dataclass(frozen=True, slots=True)
class ArchiveMonth:
    year: int
    month: int
    url: str

    @property
    def label(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"


@dataclass(frozen=True, slots=True)
class AcquisitionFailure:
    month: str | None
    message: str


@dataclass(frozen=True, slots=True)
class AcquisitionResult:
    published_months: tuple[str, ...]
    skipped_months: tuple[str, ...]
    failures: tuple[AcquisitionFailure, ...]

    @property
    def completed(self) -> bool:
        return not self.failures


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class HttpxJsonTransport:
    """Production synchronous transport fixed to URLs selected by this package."""

    def get_json(self, url: str, *, timeout: float) -> Any:
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()


def acquire_months(
    configuration: AcquireConfiguration,
    raw_root: Path,
    *,
    transport: JsonTransport | None = None,
    clock: AcquisitionClock | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> AcquisitionResult:
    """Discover listed months and safely acquire every eligible raw month."""

    effective_transport = transport if transport is not None else HttpxJsonTransport()
    effective_clock = clock if clock is not None else SystemClock()
    archive_url = _archive_url(configuration.username)
    try:
        archive_response = effective_transport.get_json(
            archive_url, timeout=configuration.request_timeout
        )
        listed_months = _discover_months(archive_response, configuration.username)
        current = _current_month(effective_clock)
    except Exception as error:
        return AcquisitionResult(
            published_months=(),
            skipped_months=(),
            failures=(AcquisitionFailure(month=None, message=str(error)),),
        )

    published: list[str] = []
    skipped: list[str] = []
    failures: list[AcquisitionFailure] = []
    for archive_month in listed_months:
        month_key = (archive_month.year, archive_month.month)
        if month_key > current:
            continue
        target = raw_root / "games" / f"{archive_month.year:04d}" / f"{archive_month.month:02d}.json"
        is_current = month_key == current
        if not is_current and target.exists():
            skipped.append(archive_month.label)
            continue
        try:
            if configuration.request_delay:
                sleep(configuration.request_delay)
            remote = effective_transport.get_json(
                archive_month.url, timeout=configuration.request_timeout
            )
            if is_current and target.exists():
                candidate = merge_current_month(load_month(target), remote)
            else:
                candidate = remote
            publish_month(target, candidate, replace_existing=is_current)
        except Exception as error:
            failures.append(
                AcquisitionFailure(month=archive_month.label, message=str(error))
            )
            continue
        published.append(archive_month.label)

    return AcquisitionResult(
        published_months=tuple(published),
        skipped_months=tuple(skipped),
        failures=tuple(failures),
    )


def _archive_url(username: str) -> str:
    return f"{CHESSCOM_API_ORIGIN}/pub/player/{quote(username, safe='')}/games/archives"


def _discover_months(response: object, username: str) -> tuple[ArchiveMonth, ...]:
    if not isinstance(response, dict) or not isinstance(response.get("archives"), list):
        raise AcquisitionError("archive response must be an object with an archives list")

    months: dict[tuple[int, int], ArchiveMonth] = {}
    for value in response["archives"]:
        if not isinstance(value, str):
            raise AcquisitionError("every archive entry must be a fixed Chess.com month URL")
        parsed = urlsplit(value)
        match = _MONTH_PATH.fullmatch(parsed.path)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "api.chess.com"
            or parsed.query
            or parsed.fragment
            or match is None
            or unquote(match.group(1)).casefold() != username.casefold()
        ):
            raise AcquisitionError("every archive entry must be a fixed Chess.com month URL")
        year = int(match.group(2))
        month = int(match.group(3))
        if not 1 <= month <= 12:
            raise AcquisitionError("archive entry contains an invalid calendar month")
        key = (year, month)
        prior = months.get(key)
        if prior is not None and prior.url != value:
            raise AcquisitionError("archive response contains conflicting URLs for one month")
        months[key] = ArchiveMonth(year=year, month=month, url=value)
    return tuple(months[key] for key in sorted(months))


def _current_month(clock: AcquisitionClock) -> tuple[int, int]:
    now = clock.now()
    if now.tzinfo is None or now.utcoffset() is None:
        raise AcquisitionError("acquisition clock must return a timezone-aware datetime")
    utc_now = now.astimezone(UTC)
    return utc_now.year, utc_now.month
