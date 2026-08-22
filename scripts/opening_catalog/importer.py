"""Read, replay, and atomically persist the fixed opening source catalog."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import chess
import chess.pgn

from .schema import SCHEMA_VERSION, ensure_schema

SOURCE_DATASET = "lichess-org/chess-openings"
EXPECTED_SOURCE_FILES = ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")
SOURCE_FIELDS = ("eco", "name", "pgn")


class OpeningCatalogError(RuntimeError):
    """Base error for opening catalog reads and publication."""


class OpeningReplayError(OpeningCatalogError):
    """A source record cannot be replayed into a legal endpoint."""

    def __init__(self, message: str, manifest: SourceManifest | None = None) -> None:
        super().__init__(message)
        self.manifest = manifest


class OpeningSourceChangedError(OpeningCatalogError):
    """The source manifest differs from the accepted catalog."""


@dataclass(frozen=True)
class SourceFile:
    name: str
    sha256: str
    record_count: int


@dataclass(frozen=True)
class OpeningRecord:
    source_file: str
    source_row_ordinal: int
    source_row_hash: str
    eco: str
    name: str
    move_sequence: str
    endpoint_fen: str
    endpoint_placement: str
    endpoint_side_to_move: str
    endpoint_castling: str
    endpoint_en_passant: str
    endpoint_halfmove_clock: int
    endpoint_fullmove_number: int

    @property
    def endpoint_key(self) -> tuple[str, str, str, str]:
        return (
            self.endpoint_placement,
            self.endpoint_side_to_move,
            self.endpoint_castling,
            self.endpoint_en_passant,
        )


@dataclass(frozen=True)
class SourceManifest:
    manifest_hash: str
    source_dataset: str
    files: tuple[SourceFile, ...]
    records: tuple[OpeningRecord, ...]

    @property
    def record_count(self) -> int:
        return sum(source_file.record_count for source_file in self.files)


@dataclass(frozen=True)
class ImportResult:
    run_id: str
    manifest_hash: str
    status: str
    record_count: int


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def canonical_row_hash(eco: str, name: str, move_sequence: str) -> str:
    """Hash the source fields without relying on SQLite identifiers."""

    return hashlib.sha256(
        _canonical_json({"eco": eco, "name": name, "pgn": move_sequence})
    ).hexdigest()


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _replay_endpoint(
    source_file: str, source_row_ordinal: int, move_sequence: str
) -> tuple[str, tuple[str, str, str, str], int, int]:
    try:
        game = chess.pgn.read_game(io.StringIO('[Result "*"]\n\n' + move_sequence))
        if game is None:
            raise ValueError("PGN parsed to no game")
        parser_errors = getattr(game, "errors", ())
        if parser_errors:
            raise ValueError(f"PGN parser errors: {parser_errors[0]}")
        board = game.board()
        ply_count = 0
        for move in game.mainline_moves():
            if move not in board.legal_moves:
                raise ValueError(f"illegal move at ply {ply_count + 1}: {move.uci()}")
            board.push(move)
            ply_count += 1
        if ply_count == 0:
            raise ValueError("PGN contains no moves")
        fields = board.fen(en_passant="fen").split()
        if len(fields) != 6:
            raise ValueError(f"endpoint FEN has {len(fields)} fields")
        return (
            " ".join(fields),
            tuple(fields[:4]),  # type: ignore[return-value]
            int(fields[4]),
            int(fields[5]),
        )
    except Exception as error:
        raise OpeningReplayError(
            f"{source_file} row {source_row_ordinal}: replay failed: {error}"
        ) from error


def _manifest_from_files(files: tuple[SourceFile, ...]) -> str:
    payload = {
        "source_dataset": SOURCE_DATASET,
        "files": [
            {"name": source_file.name, "sha256": source_file.sha256} for source_file in files
        ],
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def load_source(source_dir: Path) -> SourceManifest:
    """Read the fixed five-file source and replay every record in memory."""

    source_dir = Path(source_dir)
    actual_files = tuple(sorted(path.name for path in source_dir.glob("*.tsv")))
    if actual_files != EXPECTED_SOURCE_FILES:
        raise OpeningCatalogError(
            f"expected source files {EXPECTED_SOURCE_FILES}, found {actual_files}"
        )

    file_rows: list[tuple[SourceFile, list[dict[str, str]]]] = []
    for source_name in EXPECTED_SOURCE_FILES:
        path = source_dir / source_name
        raw = path.read_bytes()
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if tuple(reader.fieldnames or ()) != SOURCE_FIELDS:
                raise OpeningCatalogError(
                    f"{source_name}: expected fields {SOURCE_FIELDS}, found {reader.fieldnames}"
                )
            rows: list[dict[str, str]] = []
            for row in reader:
                if any(row.get(field) is None for field in SOURCE_FIELDS):
                    raise OpeningCatalogError(f"{source_name}: row has missing source fields")
                rows.append({field: str(row[field]) for field in SOURCE_FIELDS})
        file_rows.append(
            (
                SourceFile(source_name, hashlib.sha256(raw).hexdigest(), len(rows)),
                rows,
            )
        )

    files = tuple(item[0] for item in file_rows)
    manifest = SourceManifest(_manifest_from_files(files), SOURCE_DATASET, files, ())
    records: list[OpeningRecord] = []
    for source_file, rows in file_rows:
        for ordinal, row in enumerate(rows, start=1):
            row_hash = canonical_row_hash(row["eco"], row["name"], row["pgn"])
            try:
                endpoint_fen, endpoint_key, halfmove, fullmove = _replay_endpoint(
                    source_file.name, ordinal, row["pgn"]
                )
            except OpeningReplayError as error:
                raise OpeningReplayError(str(error), manifest) from error
            records.append(
                OpeningRecord(
                    source_file=source_file.name,
                    source_row_ordinal=ordinal,
                    source_row_hash=row_hash,
                    eco=row["eco"],
                    name=row["name"],
                    move_sequence=row["pgn"],
                    endpoint_fen=endpoint_fen,
                    endpoint_placement=endpoint_key[0],
                    endpoint_side_to_move=endpoint_key[1],
                    endpoint_castling=endpoint_key[2],
                    endpoint_en_passant=endpoint_key[3],
                    endpoint_halfmove_clock=halfmove,
                    endpoint_fullmove_number=fullmove,
                )
            )
    return SourceManifest(manifest.manifest_hash, manifest.source_dataset, files, tuple(records))


def _register_manifest(connection: sqlite3.Connection, manifest: SourceManifest) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO opening_source_manifest "
        "(manifest_hash, source_dataset, file_count, record_count, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            manifest.manifest_hash,
            manifest.source_dataset,
            len(manifest.files),
            manifest.record_count,
            _timestamp(),
        ),
    )
    for source_file in manifest.files:
        connection.execute(
            "INSERT OR IGNORE INTO opening_source_file "
            "(manifest_hash, source_file, source_file_hash, record_count) "
            "VALUES (?, ?, ?, ?)",
            (
                manifest.manifest_hash,
                source_file.name,
                source_file.sha256,
                source_file.record_count,
            ),
        )


def _start_run(connection: sqlite3.Connection, manifest: SourceManifest) -> str:
    run_id = uuid.uuid4().hex
    _register_manifest(connection, manifest)
    connection.execute(
        "INSERT INTO opening_import_run "
        "(run_id, manifest_hash, schema_version, status, started_at, record_count) "
        "VALUES (?, ?, ?, 'running', ?, ?)",
        (run_id, manifest.manifest_hash, SCHEMA_VERSION, _timestamp(), manifest.record_count),
    )
    return run_id


def _finish_run(
    connection: sqlite3.Connection,
    run_id: str,
    status: str,
    details: str | None = None,
) -> None:
    connection.execute(
        "UPDATE opening_import_run SET status = ?, finished_at = ?, details = ? WHERE run_id = ?",
        (status, _timestamp(), details, run_id),
    )


def _catalog_row(record: OpeningRecord, manifest_hash: str) -> tuple[object, ...]:
    return (
        manifest_hash,
        record.source_file,
        record.source_row_ordinal,
        record.source_row_hash,
        record.eco,
        record.name,
        record.move_sequence,
        record.endpoint_fen,
        record.endpoint_placement,
        record.endpoint_side_to_move,
        record.endpoint_castling,
        record.endpoint_en_passant,
        record.endpoint_halfmove_clock,
        record.endpoint_fullmove_number,
    )


def _catalog_matches(connection: sqlite3.Connection, manifest: SourceManifest) -> bool:
    actual = connection.execute(
        "SELECT manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name, "
        "move_sequence, endpoint_fen, endpoint_placement, endpoint_side_to_move, "
        "endpoint_castling, endpoint_en_passant, endpoint_halfmove_clock, "
        "endpoint_fullmove_number FROM opening_catalog "
        "WHERE manifest_hash = ? ORDER BY source_file, source_row_ordinal",
        (manifest.manifest_hash,),
    ).fetchall()
    expected = [
        _catalog_row(record, manifest.manifest_hash)
        for record in sorted(
            manifest.records, key=lambda item: (item.source_file, item.source_row_ordinal)
        )
    ]
    return actual == expected


def _accepted_manifest(connection: sqlite3.Connection) -> str | None:
    row = connection.execute(
        "SELECT accepted_manifest_hash FROM opening_catalog_state WHERE id = 1"
    ).fetchone()
    return str(row[0]) if row else None


def _record_failed_run(
    connection: sqlite3.Connection, manifest: SourceManifest, details: str
) -> str:
    with connection:
        run_id = _start_run(connection, manifest)
        _finish_run(connection, run_id, "failed", details)
    return run_id


def import_catalog(connection: sqlite3.Connection, source_dir: Path) -> ImportResult:
    """Atomically publish the first fixed source manifest or safely rerun it."""

    connection.execute("PRAGMA foreign_keys = ON")
    ensure_schema(connection)
    try:
        manifest = load_source(source_dir)
    except OpeningReplayError as error:
        if error.manifest is not None:
            _record_failed_run(connection, error.manifest, str(error))
        raise

    accepted = _accepted_manifest(connection)
    if accepted is not None and accepted != manifest.manifest_hash:
        _record_failed_run(
            connection,
            manifest,
            "source manifest changed; explicit approval is required for a new source version",
        )
        raise OpeningSourceChangedError(
            "source manifest changed; explicit approval is required for a new source version"
        )

    with connection:
        run_id = _start_run(connection, manifest)

    try:
        with connection:
            if accepted is not None:
                if not _catalog_matches(connection, manifest):
                    raise OpeningCatalogError(
                        "accepted opening catalog does not match its source manifest"
                    )
                _finish_run(connection, run_id, "success", "unchanged source manifest")
                return ImportResult(
                    run_id, manifest.manifest_hash, "unchanged", manifest.record_count
                )

            connection.executemany(
                "INSERT INTO opening_catalog ("
                "manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name, "
                "move_sequence, endpoint_fen, endpoint_placement, endpoint_side_to_move, "
                "endpoint_castling, endpoint_en_passant, endpoint_halfmove_clock, "
                "endpoint_fullmove_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [_catalog_row(record, manifest.manifest_hash) for record in manifest.records],
            )
            stored_count = connection.execute(
                "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?",
                (manifest.manifest_hash,),
            ).fetchone()[0]
            if stored_count != manifest.record_count:
                raise OpeningCatalogError(
                    f"catalog record count {stored_count} does not match source "
                    f"count {manifest.record_count}"
                )
            connection.execute(
                "INSERT INTO opening_catalog_state "
                "(id, accepted_manifest_hash, accepted_schema_version, accepted_at, record_count) "
                "VALUES (1, ?, ?, ?, ?)",
                (
                    manifest.manifest_hash,
                    SCHEMA_VERSION,
                    _timestamp(),
                    manifest.record_count,
                ),
            )
            _finish_run(connection, run_id, "success", "initial source publication")
    except Exception as error:
        connection.rollback()
        with connection:
            _finish_run(connection, run_id, "failed", str(error)[:500])
        raise

    return ImportResult(run_id, manifest.manifest_hash, "success", manifest.record_count)
