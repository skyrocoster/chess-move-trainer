"""Consistent online SQLite backup, never a raw copy of a live database."""

from __future__ import annotations

import importlib.metadata
import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from chess_move_trainer.database.connection import _create_sqlite_connection, _open_connection
from chess_move_trainer.database.schema import _assert_compatible_schema

from .artifacts import Budget, digest, file_digest, read_json, write_json
from .protocol import DEFAULT_PROTOCOL


def code_provenance():
    root = Path(__file__).resolve().parents[3]
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=root, capture_output=True,
                                  check=True, timeout=10).stdout.decode().strip()
        except (OSError, subprocess.SubprocessError):
            return "unavailable"
    sources = {str(p.relative_to(root)): file_digest(p)
               for p in sorted((root / "src/chess_move_trainer").rglob("*.py"))}
    versions = {}
    for name in ("chess", "numpy", "scipy", "statsmodels", "pandas", "SQLAlchemy"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {"revision": git("rev-parse", "HEAD"), "dirty_diff_sha256": digest(git("diff", "HEAD")),
            "source_sha256": digest(sources), "dependencies": versions}


def create_snapshot(source: Path, directory: Path, *, seconds: float = 120,
                    source_label: str | None = None):
    budget = Budget(seconds)
    source = source.resolve(strict=True)
    directory = directory.resolve()
    if directory.exists():
        raise FileExistsError("snapshot directory must be new; existing snapshots are immutable")
    with _open_connection(source, "read-only", 5.0) as connection:
        _assert_compatible_schema(connection, 5.0)
    directory.mkdir(parents=True)
    partial = directory / "snapshot.db.partial"
    try:
        origin = _create_sqlite_connection(source, "read-only", 5.0)
        destination = sqlite3.connect(partial, timeout=5)
        try:
            # Pin a short-lived WAL read snapshot so worker commits cannot keep
            # restarting the incremental backup. Released immediately after copying.
            origin.execute("BEGIN")
            origin.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()
            origin.backup(destination, pages=256, sleep=0.01,
                          progress=lambda *args: budget.check())
            origin.rollback()
            # A standalone rollback-journal snapshot does not need mutable WAL sidecars.
            destination.execute("PRAGMA journal_mode=DELETE")
            destination.set_progress_handler(lambda: int(_expired(budget)), 10000)
            if destination.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                raise ValueError("snapshot failed SQLite quick_check")
            if destination.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise ValueError("snapshot has broken foreign keys")
        finally:
            origin.close()
            destination.close()
        target = directory / "snapshot.db"
        os.replace(partial, target)
        manifest = {
            "status": "complete", "source": source_label or str(source),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "snapshot_sha256": file_digest(target, budget), "schema_version": 2,
            "protocol": DEFAULT_PROTOCOL.to_dict(), "protocol_sha256": DEFAULT_PROTOCOL.identity,
            "code": code_provenance(),
        }
        write_json(directory / "manifest.json", manifest)
        return manifest
    except BaseException:
        write_json(directory / "failure.json", {"status": "run_incomplete"})
        raise


def _expired(budget):
    try:
        budget.check()
    except TimeoutError:
        return True
    return False


def verify_snapshot(directory: Path, budget: Budget):
    manifest = read_json(directory / "manifest.json")
    if manifest.get("status") != "complete":
        raise ValueError("snapshot is incomplete")
    if manifest.get("protocol_sha256") != DEFAULT_PROTOCOL.identity:
        raise ValueError("snapshot protocol does not match this implementation")
    if file_digest(directory / "snapshot.db", budget) != manifest["snapshot_sha256"]:
        raise ValueError("snapshot contents changed")
    return manifest
