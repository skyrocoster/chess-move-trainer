"""Atomic publication of inspected SQLite schema Markdown."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _validate_lock_timeout
from .inspection import inspect_schema, render_schema_markdown


class SchemaPublicationCollisionError(ValueError):
    """Raised when publication would replace the selected database."""


def publish_schema(
    database_path: str | Path,
    output_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> bytes:
    """Inspect a database and atomically publish its deterministic Markdown."""

    database = Path(database_path)
    output = Path(output_path)
    timeout_seconds = _validate_lock_timeout(lock_timeout)
    _validate_output_path(database, output)
    inspection = inspect_schema(database, lock_timeout=timeout_seconds)
    markdown = render_schema_markdown(inspection)
    _atomic_write(output, markdown)
    return markdown


def _validate_output_path(database_path: Path, output_path: Path) -> None:
    parent = output_path.parent
    if not parent.exists():
        raise FileNotFoundError(f"Output parent directory does not exist: {parent}")
    if not parent.is_dir():
        raise NotADirectoryError(f"Output parent path is not a directory: {parent}")
    if output_path.exists() and output_path.is_dir():
        raise IsADirectoryError(f"Output target is not a file: {output_path}")

    try:
        same_resolved_path = database_path.resolve() == output_path.resolve()
    except OSError:
        same_resolved_path = False
    same_file = False
    if database_path.exists() and output_path.exists():
        try:
            same_file = os.path.samefile(database_path, output_path)
        except OSError:
            same_file = False
    if same_resolved_path or same_file:
        raise SchemaPublicationCollisionError("Output path resolves to the selected database path.")


def _atomic_write(output_path: Path, content: bytes) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, output_path)
    except BaseException:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
        raise
