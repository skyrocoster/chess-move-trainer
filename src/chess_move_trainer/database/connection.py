"""Synchronous, explicit-path SQLite connection boundary."""

from __future__ import annotations

import math
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterator, Literal

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.pool import NullPool


DEFAULT_LOCK_TIMEOUT_SECONDS: Final[float] = 5.0
_MAX_SQLITE_TIMEOUT_MS: Final[int] = 2_147_483_647
AccessMode = Literal["read-write", "read-only"]


@dataclass(frozen=True)
class ConnectionProbe:
    """Ordinary data describing the settings verified on an opened database."""

    database_path: Path
    access_mode: AccessMode
    foreign_keys_enabled: bool
    busy_timeout_ms: int
    journal_mode: str


def probe_connection(
    database_path: str | Path,
    *,
    mode: AccessMode = "read-write",
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> ConnectionProbe:
    """Open, verify, and close one explicit database connection.

    The connection itself remains an internal package detail.  Callers receive
    only ordinary probe data so SQLAlchemy objects do not cross this boundary.
    """

    path = _validate_database_path(database_path, mode)
    timeout_seconds = _validate_lock_timeout(lock_timeout)

    with _open_connection(path, mode, timeout_seconds) as connection:
        foreign_keys_enabled = connection.exec_driver_sql(
            "PRAGMA foreign_keys"
        ).scalar_one() == 1
        busy_timeout_ms = int(connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one())
        journal_mode = str(connection.exec_driver_sql("PRAGMA journal_mode").scalar_one())

        if not foreign_keys_enabled:
            raise RuntimeError("SQLite foreign-key enforcement could not be enabled.")

        return ConnectionProbe(
            database_path=path,
            access_mode=mode,
            foreign_keys_enabled=foreign_keys_enabled,
            busy_timeout_ms=busy_timeout_ms,
            journal_mode=journal_mode,
        )


@contextmanager
def _open_connection(
    database_path: Path,
    mode: AccessMode,
    lock_timeout: float,
) -> Iterator[Connection]:
    """Yield one configured SQLAlchemy Core connection for package internals."""

    engine = create_engine(
        "sqlite+pysqlite://",
        creator=lambda: _create_sqlite_connection(database_path, mode, lock_timeout),
        poolclass=NullPool,
    )
    try:
        with engine.connect() as connection:
            if connection.in_transaction():
                raise RuntimeError("Database connection was yielded with an active transaction.")
            yield connection
    finally:
        engine.dispose()


def _create_sqlite_connection(
    database_path: Path,
    mode: AccessMode,
    lock_timeout: float,
) -> sqlite3.Connection:
    if mode == "read-only":
        uri = f"file:{database_path.resolve().as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=lock_timeout)
    else:
        connection = sqlite3.connect(str(database_path), timeout=lock_timeout)

    try:
        _configure_sqlite_connection(connection, lock_timeout)
    except BaseException:
        connection.close()
        raise
    return connection


def _configure_sqlite_connection(connection: sqlite3.Connection, lock_timeout: float) -> None:
    timeout_ms = min(
        _MAX_SQLITE_TIMEOUT_MS,
        max(1, int(lock_timeout * 1000)),
    )
    connection.execute("PRAGMA foreign_keys = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise RuntimeError("SQLite foreign-key enforcement could not be enabled.")
    connection.execute(f"PRAGMA busy_timeout = {timeout_ms}")


def _validate_database_path(database_path: str | Path, mode: AccessMode) -> Path:
    if mode not in ("read-write", "read-only"):
        raise ValueError("mode must be 'read-write' or 'read-only'.")

    path = Path(database_path)
    parent = path.parent
    if not parent.exists():
        raise FileNotFoundError(f"Database parent directory does not exist: {parent}")
    if not parent.is_dir():
        raise NotADirectoryError(f"Database parent path is not a directory: {parent}")
    if path.exists() and not path.is_file():
        raise IsADirectoryError(f"Database target is not a file: {path}")
    if mode == "read-only" and not path.exists():
        raise FileNotFoundError(f"Read-only database target does not exist: {path}")
    return path


def _validate_lock_timeout(lock_timeout: float) -> float:
    if isinstance(lock_timeout, bool):
        raise ValueError("lock_timeout must be finite and greater than zero.")
    try:
        value = float(lock_timeout)
    except (TypeError, ValueError) as error:
        raise ValueError("lock_timeout must be finite and greater than zero.") from error
    if not math.isfinite(value) or value <= 0:
        raise ValueError("lock_timeout must be finite and greater than zero.")
    return value
