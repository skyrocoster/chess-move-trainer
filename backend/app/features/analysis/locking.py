"""A single OS-owned lock for one top-level analysis invocation."""

from __future__ import annotations

import os
from pathlib import Path
from types import TracebackType

from .errors import AnalysisLockError


class AnalysisRunLock:
    """Hold a one-byte lock whose lifetime is tied to an open OS file handle."""

    def __init__(self, database: Path, lock_path: Path | None = None) -> None:
        self.database = database.resolve()
        self.path = (lock_path or Path(f"{self.database}.analysis.lock")).resolve()
        self._handle = None
        self._locked = False

    def acquire(self) -> None:
        if self._handle is not None:
            raise AnalysisLockError("analysis lock is already held by this operator")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+b")
        try:
            if not handle.read(1):
                handle.seek(0)
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._handle = handle
            self._locked = True
        except (OSError, ValueError) as error:
            handle.close()
            raise AnalysisLockError(
                f"another analysis operator already owns the lock for {self.database}"
            ) from error

    def release(self) -> None:
        handle = self._handle
        if handle is None:
            return
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()
            self._handle = None
            self._locked = False

    def __enter__(self) -> AnalysisRunLock:
        self.acquire()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.release()
