"""Windows kernel-owned mutex for database Stockfish work."""

from __future__ import annotations

import ctypes
import hashlib
import math
import os
from pathlib import Path
from typing import Final, Any


WAIT_OBJECT_0: Final[int] = 0x00000000
WAIT_ABANDONED: Final[int] = 0x00000080
WAIT_TIMEOUT: Final[int] = 0x00000102
WAIT_FAILED: Final[int] = 0xFFFFFFFF
ERROR_ALREADY_EXISTS: Final[int] = 183
DEFAULT_ACQUIRE_TIMEOUT_SECONDS: Final[float] = 0.0


class DatabaseMutexError(RuntimeError):
    """Base class for the database-specific mutex boundary."""


class MutexUnavailableError(DatabaseMutexError):
    """Raised when the Windows mutex API is unavailable."""


class MutexBusyError(DatabaseMutexError):
    """A finite wait expired because another process owns the mutex."""


def normalize_database_path(database_path: str | Path) -> str:
    """Return the absolute, normalized path used as mutex identity input."""

    try:
        path = Path(database_path).expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise ValueError("database path could not be normalized") from error
    return os.path.normcase(os.path.normpath(str(path)))


def mutex_name_for_database(database_path: str | Path) -> str:
    """Derive a bounded Windows named-mutex name from one database path."""

    normalized = normalize_database_path(database_path)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"Local\\ChessMoveTrainer.Stockfish.{digest}"


class DatabaseMutex:
    """Acquire and release one database-specific Windows named mutex."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        acquire_timeout: float = DEFAULT_ACQUIRE_TIMEOUT_SECONDS,
    ) -> None:
        self.database_path = Path(database_path)
        self.name = mutex_name_for_database(database_path)
        self.acquire_timeout = _finite_wait(acquire_timeout)
        self._handle: Any | None = None
        self._owned = False
        self._abandoned = False

    @property
    def owned(self) -> bool:
        """Whether this instance currently owns the mutex."""

        return self._owned

    @property
    def acquired_abandoned(self) -> bool:
        """Whether the successful acquisition recovered an abandoned owner."""

        return self._abandoned

    def acquire(self, timeout: float | None = None) -> bool:
        """Try to acquire ownership, returning false for a finite busy wait."""

        if self._owned:
            return True
        if timeout is None:
            timeout = self.acquire_timeout
        wait_seconds = _finite_wait(timeout)
        api = _windows_api()
        handle = api.CreateMutexW(None, False, self.name)
        if not handle:
            raise _windows_error("CreateMutexW")
        wait_ms = max(0, math.ceil(wait_seconds * 1000))
        result = int(api.WaitForSingleObject(handle, wait_ms))
        if result in (WAIT_OBJECT_0, WAIT_ABANDONED):
            self._handle = handle
            self._owned = True
            self._abandoned = result == WAIT_ABANDONED
            return True

        _close_handle(api, handle)
        if result == WAIT_TIMEOUT:
            return False
        if result == WAIT_FAILED:
            raise _windows_error("WaitForSingleObject")
        raise DatabaseMutexError(f"unexpected Windows mutex wait result: {result}")

    def release(self) -> None:
        """Release ownership and close the kernel handle whenever possible."""

        handle = self._handle
        self._handle = None
        was_owned = self._owned
        self._owned = False
        self._abandoned = False
        if handle is None:
            return
        api = _windows_api()
        error: OSError | None = None
        try:
            if was_owned and not api.ReleaseMutex(handle):
                error = _windows_error("ReleaseMutex")
        finally:
            _close_handle(api, handle)
        if error is not None:
            raise error

    def close(self) -> None:
        """Best-effort close, releasing ownership first when necessary."""

        self.release()

    def __enter__(self) -> DatabaseMutex:
        if not self.acquire():
            raise MutexBusyError(f"Stockfish analysis is already running for {self.database_path}")
        return self

    def __exit__(self, *_: object) -> None:
        self.release()

    def __del__(self) -> None:  # pragma: no cover - interpreter cleanup is best effort
        try:
            self.release()
        except BaseException:
            pass


class _WindowsApi:
    def __init__(self) -> None:
        if os.name != "nt":
            raise MutexUnavailableError("database Stockfish mutexes require Windows")
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        except OSError as error:
            raise MutexUnavailableError("Windows kernel32 could not be loaded") from error
        self.CreateMutexW = kernel32.CreateMutexW
        self.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
        self.CreateMutexW.restype = ctypes.c_void_p
        self.WaitForSingleObject = kernel32.WaitForSingleObject
        self.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.WaitForSingleObject.restype = ctypes.c_uint32
        self.ReleaseMutex = kernel32.ReleaseMutex
        self.ReleaseMutex.argtypes = [ctypes.c_void_p]
        self.ReleaseMutex.restype = ctypes.c_bool
        self.CloseHandle = kernel32.CloseHandle
        self.CloseHandle.argtypes = [ctypes.c_void_p]
        self.CloseHandle.restype = ctypes.c_bool


_API: _WindowsApi | None = None


def _windows_api() -> _WindowsApi:
    global _API
    if _API is None:
        _API = _WindowsApi()
    return _API


def _close_handle(api: _WindowsApi, handle: Any) -> None:
    api.CloseHandle(handle)


def _windows_error(operation: str) -> OSError:
    error_code = ctypes.get_last_error()
    return OSError(error_code, f"{operation} failed with Windows error {error_code}")


def _finite_wait(value: float) -> float:
    if isinstance(value, bool):
        raise ValueError("mutex timeout must be finite and non-negative")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError("mutex timeout must be finite and non-negative") from error
    if not math.isfinite(normalized) or normalized < 0:
        raise ValueError("mutex timeout must be finite and non-negative")
    return normalized


__all__ = [
    "DEFAULT_ACQUIRE_TIMEOUT_SECONDS",
    "DatabaseMutex",
    "DatabaseMutexError",
    "MutexBusyError",
    "MutexUnavailableError",
    "mutex_name_for_database",
    "normalize_database_path",
]
