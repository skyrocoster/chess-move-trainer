"""Shared target types, SQL predicates, and row helpers for Stockfish targets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import chess
from sqlalchemy import text

from ..connection import _open_existing_connection
from ..positions import CanonicalPosition, canonicalize_board, canonicalize_fen
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .configuration import STOCKFISH_VERSION, profile_for

TARGET_MIN_PLY = 0
TARGET_MAX_PLY = 19
DEFAULT_TARGET_PAGE_SIZE = 100
INITIAL_COMMON_TARGET_COUNT = 20


class TargetSelectionError(RuntimeError):
    """Raised when the live database cannot provide valid bulk targets."""


class TargetInputError(TargetSelectionError, ValueError):
    """Raised when target paging or limit input is invalid."""


@dataclass(frozen=True, slots=True)
class BulkTarget:
    """One eligible canonical position and its imported-game frequency."""

    position_id: int
    frequency: int
    position: CanonicalPosition

    def __post_init__(self) -> None:
        if type(self.position_id) is not int or self.position_id < 1:
            raise TargetSelectionError("bulk target position_id must be a positive integer")
        if type(self.frequency) is not int or self.frequency < 0:
            raise TargetSelectionError("bulk target frequency must be non-negative")
        if not isinstance(self.position, CanonicalPosition):
            raise TargetSelectionError("bulk target must contain a canonical position")

    @property
    def canonical(self) -> CanonicalPosition:
        """Return the canonical position consumed by the engine."""

        return self.position


@dataclass(frozen=True, slots=True)
class InitialTechnicalPosition:
    """One stable technical representative in the initial-analysis preset."""

    category: str
    fen: str

    @property
    def canonical(self) -> CanonicalPosition:
        """Return the canonical identity represented by the fixed FEN."""

        return canonicalize_fen(self.fen)


INITIAL_TECHNICAL_POSITIONS = (
    InitialTechnicalPosition(
        "checkmate",
        "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1",
    ),
    InitialTechnicalPosition(
        "stalemate",
        "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1",
    ),
    InitialTechnicalPosition(
        "legal en passant",
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3",
    ),
    InitialTechnicalPosition(
        "promotion",
        "4k3/P7/8/8/8/8/8/4K3 w - - 0 1",
    ),
    InitialTechnicalPosition(
        "castling",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
    ),
)
INITIAL_TECHNICAL_CATEGORIES = tuple(
    representative.category for representative in INITIAL_TECHNICAL_POSITIONS
)


@dataclass(frozen=True, slots=True)
class _RouteMove:
    route_id: int
    ply: int
    move_uci: str


def _background_result_parameters() -> dict[str, int | str]:
    """Return the authoritative browser-result eligibility parameters."""

    profile = profile_for("browser")
    return {
        "browser_quality": "browser",
        "configuration_version": profile.configuration_version,
        "engine_version": STOCKFISH_VERSION,
        "multipv": profile.multipv,
        "nodes": profile.nodes,
        "show_wdl": 1,
        "settings_key_count": len(profile.settings),
    }


def _background_result_eligibility_sql(result_alias: str = "r") -> str:
    """Return the shared predicate for missing or stale browser results."""

    return f"""
        (
            {result_alias}.derived_position_id IS NULL
            OR (
                {result_alias}.dar_quality = :browser_quality
                AND {result_alias}.dar_terminal_kind IS NULL
                AND (
                    {result_alias}.dar_configuration_version <> :configuration_version
                    OR {result_alias}.dar_engine_version <> :engine_version
                    OR json_type({result_alias}.dar_settings_json, '$.MultiPV') IS NOT 'integer'
                    OR json_extract({result_alias}.dar_settings_json, '$.MultiPV') <> :multipv
                    OR json_type({result_alias}.dar_settings_json, '$.Nodes') IS NOT 'integer'
                    OR json_extract({result_alias}.dar_settings_json, '$.Nodes') <> :nodes
                    OR json_type({result_alias}.dar_settings_json, '$.Threads') IS NOT 'integer'
                    OR json_type({result_alias}.dar_settings_json, '$.Hash') IS NOT 'integer'
                    OR json_type({result_alias}.dar_settings_json, '$.UCI_ShowWDL') IS NOT 'true'
                    OR json_extract({result_alias}.dar_settings_json, '$.UCI_ShowWDL') <> :show_wdl
                    OR (
                        SELECT COUNT(*)
                        FROM json_each({result_alias}.dar_settings_json)
                    ) <> :settings_key_count
                )
            )
        )
    """


def _load_route_moves(
    database_path: str | Path,
    lock_timeout: float,
) -> tuple[tuple[int, tuple[_RouteMove, ...]], ...]:
    try:
        with _open_existing_connection(database_path, lock_timeout) as connection:
            _assert_compatible_schema(connection, lock_timeout)
            rows = connection.execute(
                text(
                    """
                    SELECT r.dor_route_id, m.dorm_ply, m.dorm_move_uci
                    FROM derived_opening_route AS r
                    LEFT JOIN derived_opening_route_move AS m
                      ON m.derived_opening_route_id = r.dor_route_id
                    ORDER BY r.dor_route_id, m.dorm_ply
                    """
                )
            ).all()
    except SchemaIncompatibleError:
        raise
    except Exception as error:
        raise TargetSelectionError("opening routes could not be read") from error

    grouped: dict[int, list[_RouteMove]] = {}
    for row in rows:
        route_id = int(row[0])
        grouped.setdefault(route_id, [])
        if row[1] is not None and row[2] is not None:
            grouped[route_id].append(
                _RouteMove(route_id=route_id, ply=int(row[1]), move_uci=str(row[2]))
            )
    return tuple((route_id, tuple(grouped[route_id])) for route_id in sorted(grouped))


def _record_route_position(
    board: chess.Board,
    position_work: object,
    route_positions: dict[int, CanonicalPosition],
) -> None:
    canonical = canonicalize_board(board)
    position_id = position_work.resolve_board(board)
    route_positions[position_id] = canonical


def _target_from_row(row: object) -> BulkTarget:
    try:
        return BulkTarget(
            position_id=int(row[0]),
            frequency=int(row[1]),
            position=CanonicalPosition(
                placement=str(row[2]),
                side_to_move=str(row[3]),
                castling_rights=str(row[4]),
                legal_en_passant=str(row[5]),
            ),
        )
    except (IndexError, TypeError, ValueError) as error:
        raise TargetSelectionError("imported-game target row is malformed") from error


def _validate_limit(limit: int | None) -> None:
    if limit is not None and (type(limit) is not int or limit <= 0):
        raise TargetInputError("limit must be a positive integer when supplied")
