"""Transactional creation, compatibility, and explicit schema upgrades."""

from __future__ import annotations

import sqlite3
import tempfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from sqlalchemy.engine import Connection

from .connection import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    _open_connection,
    _open_existing_connection,
    _validate_database_path,
    _validate_lock_timeout,
)

SCHEMA_VERSION = 2
_V1_SCHEMA_VERSION = 1
_SCHEMA_RESOURCE_NAME = "schema_v2.sql"
_V1_SCHEMA_RESOURCE_NAME = "schema_v1.sql"
_UPGRADE_RESOURCE_NAME = "schema_v1_to_v2.sql"


class SchemaIncompatibleError(RuntimeError):
    """Raised when an existing database is not the exact supported schema."""


@dataclass(frozen=True)
class SchemaCreationResult:
    """Ordinary data describing one schema creation request."""

    database_path: Path
    created: bool


@dataclass(frozen=True)
class SchemaUpgradeResult:
    """Ordinary data describing one explicit schema upgrade request."""

    database_path: Path
    upgraded: bool


@dataclass(frozen=True)
class _SchemaSnapshot:
    user_version: int
    objects: tuple[tuple[object, ...], ...]


def create_schema(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> SchemaCreationResult:
    """Create schema v2 or accept an exactly compatible existing database."""

    path = _validate_database_path(database_path, "read-write")
    timeout_seconds = _validate_lock_timeout(lock_timeout)
    existed_before_open = path.exists()
    original_bytes = None
    initializing = False

    try:
        with _open_connection(path, "read-write", timeout_seconds) as connection:
            current = _schema_snapshot(connection)
            connection.rollback()

            if _is_truly_empty(current):
                initializing = True
                if existed_before_open:
                    original_bytes = path.read_bytes()
                with connection.begin():
                    _execute_schema_resource(connection)
                return SchemaCreationResult(database_path=path, created=True)

            expected = _reference_snapshot(timeout_seconds, _SCHEMA_RESOURCE_NAME)
            if current == expected:
                return SchemaCreationResult(database_path=path, created=False)
            raise SchemaIncompatibleError(
                f"Database is not compatible with schema version {SCHEMA_VERSION}: {path}"
            )
    except BaseException:
        if not existed_before_open:
            _remove_new_target(path)
        elif initializing and original_bytes is not None:
            path.write_bytes(original_bytes)
        raise


def _is_truly_empty(snapshot: _SchemaSnapshot) -> bool:
    return snapshot.user_version == 0 and not snapshot.objects


def upgrade_schema(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> SchemaUpgradeResult:
    """Upgrade one existing exact v1 database to v2, or leave exact v2 unchanged."""

    path = _validate_database_path(database_path, "read-write")
    timeout_seconds = _validate_lock_timeout(lock_timeout)

    with _open_existing_connection(path, timeout_seconds) as connection:
        current = _schema_snapshot(connection)
        connection.rollback()
        expected_v1 = _reference_snapshot(timeout_seconds, _V1_SCHEMA_RESOURCE_NAME)
        expected_v2 = _reference_snapshot(timeout_seconds, _SCHEMA_RESOURCE_NAME)

        if current == expected_v2:
            return SchemaUpgradeResult(database_path=path, upgraded=False)
        if current != expected_v1:
            raise SchemaIncompatibleError(
                f"Database is not compatible with schema versions "
                f"{_V1_SCHEMA_VERSION} or {SCHEMA_VERSION}: {path}"
            )

        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            if _schema_snapshot(connection) != expected_v1:
                raise SchemaIncompatibleError(
                    "Database schema changed before the upgrade could begin."
                )
            _execute_schema_resource(connection, _UPGRADE_RESOURCE_NAME)
            if _schema_snapshot(connection) != expected_v2:
                raise SchemaIncompatibleError(
                    f"Schema upgrade did not produce exact schema version {SCHEMA_VERSION}."
                )
            connection.commit()
        except BaseException:
            if connection.in_transaction():
                connection.rollback()
            raise

    return SchemaUpgradeResult(database_path=path, upgraded=True)


def _reference_snapshot(lock_timeout: float, resource_name: str) -> _SchemaSnapshot:
    with tempfile.TemporaryDirectory(prefix="chess-move-trainer-schema-") as directory:
        reference_path = Path(directory) / "reference.db"
        with _open_connection(reference_path, "read-write", lock_timeout) as connection:
            with connection.begin():
                _execute_schema_resource(connection, resource_name)
            snapshot = _schema_snapshot(connection)
            connection.rollback()
        return snapshot


def _schema_snapshot(connection: Connection) -> _SchemaSnapshot:
    user_version = int(connection.exec_driver_sql("PRAGMA user_version").scalar_one())
    objects = tuple(
        tuple(row)
        for row in connection.exec_driver_sql(
            """
            SELECT type, name, tbl_name, sql
            FROM sqlite_master
            WHERE type IN ('table', 'index', 'trigger', 'view')
            ORDER BY type, name
            """
        ).all()
    )
    return _SchemaSnapshot(user_version=user_version, objects=objects)


def _assert_compatible_schema(
    connection: Connection,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> None:
    """Assert exact v2 compatibility without changing the open target."""

    try:
        current = _schema_snapshot(connection)
        connection.rollback()
        expected = _reference_snapshot(lock_timeout, _SCHEMA_RESOURCE_NAME)
        if current != expected:
            raise SchemaIncompatibleError(
                f"Database is not compatible with schema version {SCHEMA_VERSION}."
            )
    finally:
        if connection.in_transaction():
            connection.rollback()


def _execute_schema_resource(
    connection: Connection,
    resource_name: str = _SCHEMA_RESOURCE_NAME,
) -> None:
    resource = resources.files("chess_move_trainer.database").joinpath(resource_name)
    script = resource.read_text(encoding="utf-8")
    pending = ""
    for line in script.splitlines(keepends=True):
        pending += line
        if sqlite3.complete_statement(pending):
            statement = pending.strip()
            if statement:
                _execute_schema_statement(connection, statement)
            pending = ""
    if pending.strip():
        raise RuntimeError(f"Incomplete SQL resource: {resource_name}")


def _execute_schema_statement(connection: Connection, statement: str) -> None:
    connection.exec_driver_sql(statement)


def _remove_new_target(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
