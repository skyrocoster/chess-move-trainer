"""Deterministic, strictly read-only selection of the frozen MP-09 fixtures."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

import chess

from .errors import AnalysisValidationError
from .models import canonical_fen

FIXTURE_ORDER_VERSION = "mp09-exact-fen-sha256-v1"
BANDS = ((0, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 24))


@dataclass(frozen=True)
class BenchmarkFixture:
    band: str
    fen: str
    minimum_ply: int
    source_game_uuid: str
    source_occurrence_id: int
    order_sha256: str

    def as_dict(self) -> dict[str, str | int]:
        return asdict(self)


def _connect_read_only(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise AnalysisValidationError(f"corpus database does not exist: {path}")
    return sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro&immutable=1", uri=True)


def _database_guard(path: Path) -> tuple[int, int, bool, bool]:
    stat_result = path.stat()
    return (
        stat_result.st_mtime_ns,
        stat_result.st_size,
        Path(f"{path}-wal").exists(),
        Path(f"{path}-shm").exists(),
    )


def _exact_fen_count(connection: sqlite3.Connection) -> int:
    rows = connection.execute(
        """
        SELECT ps.placement, ps.side_to_move, ps.castling, ps.en_passant,
               po.halfmove_clock, po.fullmove_number
        FROM position_occurrence po
        JOIN position_state ps ON ps.state_id = po.state_id
        JOIN corpus_game cg ON cg.game_uuid = po.game_uuid
        """
    )
    return len({tuple(row) for row in rows})


def _minimum_occurrences(connection: sqlite3.Connection) -> list[tuple[object, ...]]:
    return connection.execute(
        """
        WITH accepted AS (
            SELECT ps.placement, ps.side_to_move, ps.castling, ps.en_passant,
                   po.halfmove_clock, po.fullmove_number, po.ply, po.game_uuid,
                   po.occurrence_id
            FROM position_occurrence po
            JOIN position_state ps ON ps.state_id = po.state_id
            JOIN corpus_game cg ON cg.game_uuid = po.game_uuid
            WHERE po.ply BETWEEN 0 AND 24
        ), ranked AS (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY placement, side_to_move, castling, en_passant,
                             halfmove_clock, fullmove_number
                ORDER BY ply, game_uuid, occurrence_id
            ) AS occurrence_rank
            FROM accepted
        )
        SELECT placement, side_to_move, castling, en_passant, halfmove_clock,
               fullmove_number, ply, game_uuid, occurrence_id
        FROM ranked
        WHERE occurrence_rank = 1 AND ply BETWEEN 0 AND 24
        """
    ).fetchall()


def select_benchmark_fixtures(path: Path) -> tuple[list[BenchmarkFixture], int]:
    """Select four hash-ordered unique placements from each frozen ply band."""

    before = _database_guard(path)
    connection = _connect_read_only(path)
    try:
        if connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE 'analysis_%'"
        ).fetchone() != (0,):
            raise AnalysisValidationError("live corpus unexpectedly contains analysis tables")
        exact_fen_count = _exact_fen_count(connection)
        rows = _minimum_occurrences(connection)
    finally:
        connection.close()
    if _database_guard(path) != before:
        raise AnalysisValidationError("read-only fixture selection changed corpus database state")

    candidates: dict[tuple[int, int], list[tuple[str, str, int, str, int]]] = {
        band: [] for band in BANDS
    }
    for row in rows:
        placement, side, castling, en_passant, halfmove, fullmove, ply, game, occurrence = row
        fen = canonical_fen(f"{placement} {side} {castling} {en_passant} {halfmove} {fullmove}")
        board = chess.Board(fen)
        if board.outcome(claim_draw=True) is not None or board.legal_moves.count() < 5:
            continue
        band = next((value for value in BANDS if value[0] <= int(ply) <= value[1]), None)
        if band is None:
            continue
        order = hashlib.sha256(f"{FIXTURE_ORDER_VERSION}\n{fen}".encode("ascii")).hexdigest()
        candidates[band].append((order, fen, int(ply), str(game), int(occurrence)))

    selected: list[BenchmarkFixture] = []
    placements: set[str] = set()
    for band in BANDS:
        band_name = f"{band[0]}-{band[1]}"
        for order, fen, ply, game, occurrence in sorted(candidates[band]):
            placement = fen.split(" ", 1)[0]
            if placement in placements:
                continue
            placements.add(placement)
            selected.append(BenchmarkFixture(band_name, fen, ply, game, occurrence, order))
            if sum(fixture.band == band_name for fixture in selected) == 4:
                break
        if sum(fixture.band == band_name for fixture in selected) != 4:
            raise AnalysisValidationError(f"fixture band {band_name} cannot supply four positions")
    if {fixture.fen.split()[1] for fixture in selected} != {"w", "b"}:
        raise AnalysisValidationError("frozen fixtures must contain both sides to move")
    return selected, exact_fen_count
