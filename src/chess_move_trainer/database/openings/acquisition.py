"""Acquire and safely publish the fixed Lichess opening source.

The source repository, hosts, and five file names are deliberately fixed.  This
module resolves one default-branch commit, retrieves and strictly validates all
five files, then performs the approved staged per-file publication with
rollback.  It does not use a database.  On Windows, an abrupt crash during the
swaps can expose a temporary mixed revision, which an idempotent rerun repairs;
no whole-directory atomicity or concurrent-reader invisibility is promised.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

import httpx

from .source import OpeningSourceError, load_opening_sources


LICHESS_REPOSITORY = "lichess-org/chess-openings"
LICHESS_REPOSITORY_URL = f"https://github.com/{LICHESS_REPOSITORY}"
GITHUB_API_HOST = "api.github.com"
GITHUB_RAW_HOST = "raw.githubusercontent.com"
OPENING_SOURCE_FILES = ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")
COMMIT_RESOLUTION_URL = (
    f"https://{GITHUB_API_HOST}/repos/{LICHESS_REPOSITORY}/commits"
)
RAW_SOURCE_URL_TEMPLATE = (
    f"https://{GITHUB_RAW_HOST}/{LICHESS_REPOSITORY}/{{commit}}/{{filename}}"
)
DEFAULT_REQUEST_TIMEOUT = 30.0
DEFAULT_REQUEST_DELAY = 0.25
_COMMIT_SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")


class OpeningAcquisitionError(RuntimeError):
    """Raised for an operational opening-source acquisition error."""


@dataclass(frozen=True, slots=True)
class OpeningAcquisitionFailure:
    """One subject and message explaining an incomplete acquisition."""

    subject: str
    message: str


@dataclass(frozen=True, slots=True)
class OpeningAcquisitionResult:
    """Immutable report for one opening-source acquisition attempt."""

    resolved_commit: str | None = None
    published_files: tuple[str, ...] = ()
    unchanged_files: tuple[str, ...] = ()
    failures: tuple[OpeningAcquisitionFailure, ...] = ()

    @property
    def completed(self) -> bool:
        """Whether a commit was resolved and no failure was recorded."""

        return self.resolved_commit is not None and not self.failures

    @classmethod
    def failure(
        cls,
        subject: str,
        message: str,
        *,
        resolved_commit: str | None = None,
    ) -> OpeningAcquisitionResult:
        """Build a failure result without implying any publication."""

        return cls(
            resolved_commit=resolved_commit,
            failures=(OpeningAcquisitionFailure(subject, message),),
        )


@dataclass(frozen=True, slots=True)
class _PriorFileState:
    """In-memory presence and bytes for one fixed target file."""

    filename: str
    existed: bool
    content: bytes | None


class OpeningAcquisitionTransport(Protocol):
    """Minimal transport required by commit resolution and file retrieval."""

    def get_json(self, url: str, *, timeout: float) -> object:
        """Return one decoded JSON response."""

    def get_text(self, url: str, *, timeout: float) -> str:
        """Return one text response."""


class HttpxOpeningAcquisitionTransport:
    """Production transport using finite-timeout ``httpx`` requests."""

    def get_json(self, url: str, *, timeout: float) -> object:
        _validate_request_timeout(timeout)
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def get_text(self, url: str, *, timeout: float) -> str:
        _validate_request_timeout(timeout)
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text


def validate_request_timing(request_timeout: float, request_delay: float) -> None:
    """Reject non-finite or out-of-range acquisition timing values."""

    _validate_request_timeout(request_timeout)
    if isinstance(request_delay, bool) or not math.isfinite(float(request_delay)):
        raise ValueError("request-delay must be finite and nonnegative")
    if float(request_delay) < 0:
        raise ValueError("request-delay must be finite and nonnegative")


def acquire_openings(
    source_dir: str | Path,
    *,
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
    request_delay: float = DEFAULT_REQUEST_DELAY,
    transport: OpeningAcquisitionTransport | None = None,
    sleep: Callable[[float], None] | None = None,
    staging_observer: Callable[[Path], None] | None = None,
    replace: Callable[[Path, Path], None] | None = None,
) -> OpeningAcquisitionResult:
    """Resolve, validate, and safely publish one fixed five-file source batch.

    The observer is an offline proof hook called after all five files have been
    written to staging and before validation.  It is not used by the CLI.

    Windows cannot replace an existing nonempty directory atomically as one
    operation.  This implementation therefore swaps the five files one at a
    time with rollback; an abrupt crash during that window can expose a mixed
    revision, which an idempotent rerun repairs.  It does not promise
    concurrent-reader invisibility.
    """

    validate_request_timing(request_timeout, request_delay)
    try:
        target_dir = Path(source_dir)
    except (TypeError, ValueError) as error:
        raise OpeningAcquisitionError("source directory must be a path") from error
    acquisition_transport = (
        HttpxOpeningAcquisitionTransport() if transport is None else transport
    )
    sleep_fn = time.sleep if sleep is None else sleep

    try:
        commit_payload = acquisition_transport.get_json(
            COMMIT_RESOLUTION_URL,
            timeout=request_timeout,
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return OpeningAcquisitionResult.failure(
            "commit resolution",
            f"request failed: {error}",
        )

    resolved_commit = _extract_resolved_commit(commit_payload)
    if resolved_commit is None:
        return OpeningAcquisitionResult.failure(
            "commit resolution",
            "response must be a nonempty list with a lowercase forty-hex-digit sha",
        )

    staging_dir: Path | None = None
    try:
        staging_dir = Path(
            tempfile.mkdtemp(
                prefix=f".{target_dir.name or 'openings'}-staging-",
                dir=str(target_dir.parent),
            )
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return OpeningAcquisitionResult.failure(
            "staging",
            f"could not create staging directory: {error}",
            resolved_commit=resolved_commit,
        )

    try:
        for filename in OPENING_SOURCE_FILES:
            file_url = RAW_SOURCE_URL_TEMPLATE.format(
                commit=resolved_commit,
                filename=filename,
            )
            try:
                sleep_fn(request_delay)
                text = acquisition_transport.get_text(
                    file_url,
                    timeout=request_timeout,
                )
            except KeyboardInterrupt:
                raise
            except Exception as error:
                return OpeningAcquisitionResult.failure(
                    filename,
                    f"retrieval failed: {error}",
                    resolved_commit=resolved_commit,
                )
            if type(text) is not str:
                return OpeningAcquisitionResult.failure(
                    filename,
                    "retrieval returned non-text content",
                    resolved_commit=resolved_commit,
                )
            try:
                (staging_dir / filename).write_text(
                    text,
                    encoding="utf-8",
                    newline="",
                )
            except KeyboardInterrupt:
                raise
            except Exception as error:
                return OpeningAcquisitionResult.failure(
                    filename,
                    f"staging failed: {error}",
                    resolved_commit=resolved_commit,
                )

        if staging_observer is not None:
            staging_observer(staging_dir)

        try:
            load_opening_sources(staging_dir)
        except KeyboardInterrupt:
            raise
        except Exception as error:
            return OpeningAcquisitionResult.failure(
                "validation",
                f"staged source rejected: {error}",
                resolved_commit=resolved_commit,
            )

        try:
            if target_dir.exists() and not target_dir.is_dir():
                return OpeningAcquisitionResult.failure(
                    "target",
                    "source directory path is not a directory",
                    resolved_commit=resolved_commit,
                )
            unexpected = _unexpected_target_tsvs(target_dir)
        except OSError as error:
            return OpeningAcquisitionResult.failure(
                "target",
                f"could not inspect source directory: {error}",
                resolved_commit=resolved_commit,
            )
        if unexpected:
            return OpeningAcquisitionResult.failure(
                "target",
                f"unexpected TSV file(s): {', '.join(unexpected)}",
                resolved_commit=resolved_commit,
            )

        try:
            prior_state = _capture_prior_state(target_dir)
        except (OSError, OpeningAcquisitionError) as error:
            return OpeningAcquisitionResult.failure(
                "target",
                f"could not capture prior source state: {error}",
                resolved_commit=resolved_commit,
            )

        target_was_absent = not target_dir.exists()
        if target_was_absent:
            try:
                target_dir.mkdir()
            except OSError as error:
                return OpeningAcquisitionResult.failure(
                    "publication",
                    f"could not create source directory: {error}",
                    resolved_commit=resolved_commit,
                )

        try:
            if _staged_content_matches_target(staging_dir, target_dir):
                return OpeningAcquisitionResult(
                    resolved_commit=resolved_commit,
                    unchanged_files=OPENING_SOURCE_FILES,
                )
        except OSError as error:
            if target_was_absent:
                _remove_created_target_directory(target_dir)
            return OpeningAcquisitionResult.failure(
                "target",
                f"could not compare source content: {error}",
                resolved_commit=resolved_commit,
            )

        replace_operation = _atomic_replace if replace is None else replace
        current_filename: str | None = None
        try:
            for current_filename in OPENING_SOURCE_FILES:
                _replace_staged_file(
                    staging_dir / current_filename,
                    target_dir / current_filename,
                    replace_operation,
                )
        except KeyboardInterrupt:
            try:
                _restore_prior_state(target_dir, prior_state)
                if target_was_absent:
                    _remove_created_target_directory(target_dir)
            except Exception as rollback_error:
                raise OpeningAcquisitionError(
                    f"rollback failed after interruption: {rollback_error}"
                ) from rollback_error
            raise
        except Exception as error:
            try:
                _restore_prior_state(target_dir, prior_state)
                if target_was_absent:
                    _remove_created_target_directory(target_dir)
            except Exception as rollback_error:
                return OpeningAcquisitionResult.failure(
                    "rollback",
                    f"rollback failed after publication error: {rollback_error}",
                    resolved_commit=resolved_commit,
                )
            return OpeningAcquisitionResult.failure(
                current_filename or "publication",
                f"publication failed: {error}",
                resolved_commit=resolved_commit,
            )

        return OpeningAcquisitionResult(
            resolved_commit=resolved_commit,
            published_files=OPENING_SOURCE_FILES,
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return OpeningAcquisitionResult.failure(
            "staging",
            f"staging failed: {error}",
            resolved_commit=resolved_commit,
        )
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)


def _extract_resolved_commit(payload: object) -> str | None:
    if not isinstance(payload, list) or not payload:
        return None
    first = payload[0]
    if not isinstance(first, dict):
        return None
    sha = first.get("sha")
    if type(sha) is not str or _COMMIT_SHA_PATTERN.fullmatch(sha) is None:
        return None
    return sha


def _unexpected_target_tsvs(target_dir: Path) -> tuple[str, ...]:
    if not target_dir.exists():
        return ()
    return tuple(
        sorted(
            entry.name
            for entry in target_dir.iterdir()
            if entry.is_file()
            and entry.suffix.lower() == ".tsv"
            and entry.name not in OPENING_SOURCE_FILES
        )
    )


def _capture_prior_state(target_dir: Path) -> tuple[_PriorFileState, ...]:
    state: list[_PriorFileState] = []
    for filename in OPENING_SOURCE_FILES:
        path = target_dir / filename
        if not path.exists():
            state.append(_PriorFileState(filename, False, None))
            continue
        if not path.is_file():
            raise OpeningAcquisitionError(f"fixed target is not a file: {filename}")
        state.append(_PriorFileState(filename, True, path.read_bytes()))
    return tuple(state)


def _staged_content_matches_target(staging_dir: Path, target_dir: Path) -> bool:
    return all(
        (target_dir / filename).is_file()
        and (target_dir / filename).read_bytes()
        == (staging_dir / filename).read_bytes()
        for filename in OPENING_SOURCE_FILES
    )


def _replace_staged_file(
    staged_file: Path,
    target_file: Path,
    replace_operation: Callable[[Path, Path], None],
) -> None:
    _atomic_replace_content(
        target_file,
        staged_file.read_bytes(),
        replace_operation=replace_operation,
    )


def _atomic_replace_content(
    target_file: Path,
    content: bytes,
    *,
    replace_operation: Callable[[Path, Path], None],
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target_file.parent,
        prefix=f".{target_file.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as temporary_file:
            descriptor = -1
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        replace_operation(temporary, target_file)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise


def _atomic_replace(source_file: Path, target_file: Path) -> None:
    os.replace(source_file, target_file)


def _restore_prior_state(
    target_dir: Path,
    prior_state: tuple[_PriorFileState, ...],
) -> None:
    for state in prior_state:
        target_file = target_dir / state.filename
        if state.existed:
            assert state.content is not None
            _atomic_replace_content(
                target_file,
                state.content,
                replace_operation=os.replace,
            )
        elif target_file.exists():
            if not target_file.is_file():
                raise OpeningAcquisitionError(
                    f"cannot remove newly-created fixed target: {state.filename}"
                )
            target_file.unlink()


def _remove_created_target_directory(target_dir: Path) -> None:
    if target_dir.exists():
        target_dir.rmdir()


def _validate_request_timeout(value: float) -> None:
    if isinstance(value, bool) or not math.isfinite(float(value)) or float(value) <= 0:
        raise ValueError("request-timeout must be finite and greater than zero")
