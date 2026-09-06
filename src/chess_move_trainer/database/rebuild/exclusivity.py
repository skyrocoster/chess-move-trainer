"""Transient destination ownership for destructive DB-08 operations."""

from __future__ import annotations

import ctypes
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ..stockfish.mutex import (
    DatabaseMutex,
    DatabaseMutexError,
    MutexBusyError,
    MutexUnavailableError,
)


class ExclusiveAccessError(RuntimeError):
    """Raised when a managed destination cannot be owned safely."""


_GENERIC_READ = 0x80000000
_GENERIC_WRITE = 0x40000000
_FILE_SHARE_READ = 0x00000001
_FILE_SHARE_DELETE = 0x00000004
_OPEN_EXISTING = 3
_FILE_ATTRIBUTE_NORMAL = 0x00000080
_ERROR_ACCESS_DENIED = 5
_ERROR_SHARING_VIOLATION = 32
_ERROR_LOCK_VIOLATION = 33
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class _WindowsFileApi:
    """Small ctypes boundary for the handle that protects one destination."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise OSError("destination file guards require Windows")
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        except OSError as error:
            raise OSError("Windows kernel32 could not be loaded") from error

        self.CreateFileW = kernel32.CreateFileW
        self.CreateFileW.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        self.CreateFileW.restype = ctypes.c_void_p
        self.CloseHandle = kernel32.CloseHandle
        self.CloseHandle.argtypes = [ctypes.c_void_p]
        self.CloseHandle.restype = ctypes.c_bool
        self.ReplaceFileW = kernel32.ReplaceFileW
        self.ReplaceFileW.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_wchar_p,
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.ReplaceFileW.restype = ctypes.c_bool


_FILE_API: _WindowsFileApi | None = None


def _windows_file_api() -> _WindowsFileApi:
    global _FILE_API
    if _FILE_API is None:
        _FILE_API = _WindowsFileApi()
    return _FILE_API


class _DestinationFileGuard:
    """A held Windows share-mode guard for the current destination file."""

    def __init__(self, api: _WindowsFileApi, handle: Any, path: Path) -> None:
        self._api = api
        self._handle = handle
        self._path = path

    @classmethod
    def acquire(cls, path: Path) -> _DestinationFileGuard:
        try:
            api = _windows_file_api()
            handle = api.CreateFileW(
                str(path),
                _GENERIC_READ | _GENERIC_WRITE,
                _FILE_SHARE_READ | _FILE_SHARE_DELETE,
                None,
                _OPEN_EXISTING,
                _FILE_ATTRIBUTE_NORMAL,
                None,
            )
        except OSError as error:
            raise ExclusiveAccessError(
                f"exclusive access to the configured neighbour could not be "
                f"demonstrated on this system: {error}"
            ) from error

        if handle in (None, 0, _INVALID_HANDLE_VALUE):
            error_code = ctypes.get_last_error()
            if error_code in {
                _ERROR_ACCESS_DENIED,
                _ERROR_SHARING_VIOLATION,
                _ERROR_LOCK_VIOLATION,
            }:
                reason = "another process has the neighbour open"
            else:
                reason = f"Windows error {error_code}"
            raise ExclusiveAccessError(
                f"exclusive access to the configured neighbour is unavailable; "
                f"{reason}: {path}"
            )
        return cls(api, handle, path)

    def release(self) -> None:
        handle = self._handle
        self._handle = None
        if handle is None:
            return
        if not self._api.CloseHandle(handle):
            error_code = ctypes.get_last_error()
            raise ExclusiveAccessError(
                f"exclusive access to the configured neighbour could not be "
                f"released cleanly (Windows error {error_code}): {self._path}"
            )


def replace_destination(source: Path, target: Path) -> None:
    """Atomically install ``source`` while the destination guard is held."""

    if os.name != "nt":
        os.replace(source, target)
        return
    try:
        api = _windows_file_api()
    except OSError as error:
        raise OSError(f"Windows atomic replacement is unavailable: {error}") from error
    if not api.ReplaceFileW(str(target), str(source), None, 0, None, None):
        error_code = ctypes.get_last_error()
        raise OSError(
            error_code,
            f"ReplaceFileW failed with Windows error {error_code}: "
            f"{source} -> {target}",
        )


@contextmanager
def exclusive_destination(database_path: Path) -> Iterator[None]:
    """Hold cooperative and file-system exclusivity for one destructive action.

    The named mutex serializes DB-08 operations that cooperate with this
    package.  The held file handle is the actual destination guard: it asks for
    read/write access, shares reads and deletes for the operation's
    read-only verification and atomic replacement, and does not share writes.
    Consequently an ordinary SQLite read/write opener cannot coexist: its
    requested write access conflicts with this handle's missing write-share
    flag, both when this handle is acquired and while it is held.  Neither
    guard is a persistent file or a database record, and a busy owner is never
    interrupted.
    """

    mutex = DatabaseMutex(database_path, acquire_timeout=0)
    file_guard: _DestinationFileGuard | None = None
    try:
        if not mutex.acquire(timeout=0):
            raise MutexBusyError(str(database_path))
    except MutexBusyError as error:
        raise ExclusiveAccessError(
            f"exclusive access to the configured neighbour is unavailable; "
            f"another process owns it: {database_path}"
        ) from error
    except MutexUnavailableError as error:
        raise ExclusiveAccessError(
            f"exclusive access to the configured neighbour could not be "
            f"demonstrated on this system: {error}"
        ) from error
    except DatabaseMutexError as error:
        raise ExclusiveAccessError(
            f"exclusive access to the configured neighbour failed: {error}"
        ) from error

    try:
        file_guard = _DestinationFileGuard.acquire(database_path)
        yield
    finally:
        try:
            if file_guard is not None:
                file_guard.release()
        finally:
            mutex.release()


__all__ = ["ExclusiveAccessError", "exclusive_destination", "replace_destination"]
