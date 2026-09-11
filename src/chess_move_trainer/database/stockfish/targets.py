"""On-demand, authority-defined Stockfish bulk target selection."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import CanonicalPosition, canonicalize_board, canonicalize_fen
from ..positions.repository import position_transaction
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .configuration import CONFIGURATION_VERSION, STOCKFISH_VERSION

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


class BulkTargetSelector:
    """Read stable bounded pages and never persist a target list."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        page_size: int = DEFAULT_TARGET_PAGE_SIZE,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        if type(page_size) is not int or page_size <= 0:
            raise TargetInputError("page_size must be a positive integer")
        self._database_path = database_path
        self._page_size = page_size
        self._lock_timeout = lock_timeout

    def iter_targets(
        self,
        *,
        limit: int | None = None,
        include_ineligible: bool = False,
    ) -> Iterator[BulkTarget]:
        """Yield game targets followed by route-only targets in stable order."""

        _validate_limit(limit)
        route_positions = self._replay_route_positions()
        game_position_ids: set[int] = set()
        yielded = 0
        cursor: tuple[int, int] | None = None

        while True:
            page = self._load_game_page(cursor)
            if not page:
                break
            for target in page:
                game_position_ids.add(target.position_id)
                if not include_ineligible and not self._is_eligible(target.position_id):
                    continue
                yield target
                yielded += 1
                if limit is not None and yielded >= limit:
                    return
            last = page[-1]
            cursor = (last.frequency, last.position_id)

        route_only = sorted(
            (
                BulkTarget(position_id=position_id, frequency=0, position=position)
                for position_id, position in route_positions.items()
                if position_id not in game_position_ids
            ),
            key=lambda target: target.position_id,
        )
        for start in range(0, len(route_only), self._page_size):
            page = route_only[start : start + self._page_size]
            for target in page:
                if not include_ineligible and not self._is_eligible(target.position_id):
                    continue
                yield target
                yielded += 1
                if limit is not None and yielded >= limit:
                    return

    def _load_game_page(
        self,
        cursor: tuple[int, int] | None,
    ) -> tuple[BulkTarget, ...]:
        try:
            with _open_existing_connection(self._database_path, self._lock_timeout) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                if cursor is None:
                    statement = text(
                        """
                        WITH game_counts AS (
                            SELECT derived_position_id AS position_id,
                                   COUNT(*) AS occurrence_count
                            FROM derived_game_position
                            WHERE dgp_ply BETWEEN :min_ply AND :max_ply
                            GROUP BY derived_position_id
                        )
                        SELECT gc.position_id, gc.occurrence_count,
                               p.dp_placement, p.dp_side_to_move,
                               p.dp_castling_rights, p.dp_legal_en_passant
                        FROM game_counts AS gc
                        JOIN derived_position AS p
                          ON p.dp_position_id = gc.position_id
                        ORDER BY gc.occurrence_count DESC, gc.position_id ASC
                        LIMIT :page_size
                        """
                    )
                    parameters = {
                        "min_ply": TARGET_MIN_PLY,
                        "max_ply": TARGET_MAX_PLY,
                        "page_size": self._page_size,
                    }
                else:
                    statement = text(
                        """
                        WITH game_counts AS (
                            SELECT derived_position_id AS position_id,
                                   COUNT(*) AS occurrence_count
                            FROM derived_game_position
                            WHERE dgp_ply BETWEEN :min_ply AND :max_ply
                            GROUP BY derived_position_id
                        )
                        SELECT gc.position_id, gc.occurrence_count,
                               p.dp_placement, p.dp_side_to_move,
                               p.dp_castling_rights, p.dp_legal_en_passant
                        FROM game_counts AS gc
                        JOIN derived_position AS p
                          ON p.dp_position_id = gc.position_id
                        WHERE gc.occurrence_count < :last_frequency
                           OR (
                               gc.occurrence_count = :last_frequency
                               AND gc.position_id > :last_position_id
                           )
                        ORDER BY gc.occurrence_count DESC, gc.position_id ASC
                        LIMIT :page_size
                        """
                    )
                    parameters = {
                        "min_ply": TARGET_MIN_PLY,
                        "max_ply": TARGET_MAX_PLY,
                        "last_frequency": cursor[0],
                        "last_position_id": cursor[1],
                        "page_size": self._page_size,
                    }
                rows = connection.execute(statement, parameters).all()
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise TargetSelectionError("imported-game targets could not be read") from error
        return tuple(_target_from_row(row) for row in rows)

    def _is_eligible(self, position_id: int) -> bool:
        try:
            with _open_existing_connection(self._database_path, self._lock_timeout) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                row = connection.execute(
                    text(
                        """
                        SELECT dar_quality, dar_configuration_version, dar_engine_version
                        FROM derived_analysis_result
                        WHERE derived_position_id = :position_id
                        """
                    ),
                    {"position_id": position_id},
                ).first()
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise TargetSelectionError("analysis eligibility could not be read") from error
        if row is None or row[0] == "browser":
            return True
        if row[0] != "tool":
            raise TargetSelectionError("stored analysis has an invalid quality")
        return row[1] != CONFIGURATION_VERSION or row[2] != STOCKFISH_VERSION

    def _replay_route_positions(self) -> dict[int, CanonicalPosition]:
        routes = _load_route_moves(self._database_path, self._lock_timeout)
        route_positions: dict[int, CanonicalPosition] = {}
        try:
            with position_transaction(
                self._database_path,
                lock_timeout=self._lock_timeout,
            ) as position_work:
                for route_id, moves in routes:
                    if not moves:
                        raise TargetSelectionError(
                            f"opening route {route_id} has no legal moves"
                        )
                    board = chess.Board()
                    _record_route_position(board, position_work, route_positions)
                    for route_move in moves:
                        try:
                            move = chess.Move.from_uci(route_move.move_uci)
                        except ValueError as error:
                            raise TargetSelectionError(
                                f"opening route {route_id} has malformed UCI"
                                f" at ply {route_move.ply}"
                            ) from error
                        if move not in board.legal_moves:
                            raise TargetSelectionError(
                                f"opening route {route_id} has an illegal move"
                                f" at ply {route_move.ply}"
                            )
                        board.push(move)
                        if route_move.ply <= TARGET_MAX_PLY:
                            _record_route_position(board, position_work, route_positions)
        except SchemaIncompatibleError:
            raise
        except TargetSelectionError:
            raise
        except Exception as error:
            raise TargetSelectionError("opening routes could not be replayed") from error
        return route_positions


class InitialAnalysisTargetSelector:
    """Select the fixed 20-common plus five-technical initial mixture."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        page_size: int = DEFAULT_TARGET_PAGE_SIZE,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._common_selector = BulkTargetSelector(
            database_path,
            page_size=page_size,
            lock_timeout=lock_timeout,
        )
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def iter_targets(self, *, limit: int | None = None) -> Iterator[BulkTarget]:
        """Yield the stable initial set, skipping already-current analyses."""

        _validate_limit(limit)
        technical = self._technical_targets()
        technical_positions = {target.position for target in technical}
        common: list[BulkTarget] = []
        for target in self._common_selector.iter_targets(include_ineligible=True):
            if target.position in technical_positions:
                continue
            common.append(target)
            if len(common) == INITIAL_COMMON_TARGET_COUNT:
                break

        if len(common) != INITIAL_COMMON_TARGET_COUNT:
            raise TargetSelectionError(
                "initial analysis requires at least 20 common positions"
            )

        yielded = 0
        for target in (*common, *technical):
            if not self._common_selector._is_eligible(target.position_id):
                continue
            yield target
            yielded += 1
            if limit is not None and yielded >= limit:
                return

    def _technical_targets(self) -> tuple[BulkTarget, ...]:
        try:
            with position_transaction(
                self._database_path,
                lock_timeout=self._lock_timeout,
            ) as position_work:
                return tuple(
                    BulkTarget(
                        position_id=position_work.resolve_fen(representative.fen),
                        frequency=0,
                        position=representative.canonical,
                    )
                    for representative in INITIAL_TECHNICAL_POSITIONS
                )
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise TargetSelectionError(
                "initial technical positions could not be prepared"
            ) from error


TargetSelector = BulkTargetSelector


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


__all__ = [
    "BulkTarget",
    "BulkTargetSelector",
    "DEFAULT_TARGET_PAGE_SIZE",
    "INITIAL_COMMON_TARGET_COUNT",
    "INITIAL_TECHNICAL_CATEGORIES",
    "INITIAL_TECHNICAL_POSITIONS",
    "InitialAnalysisTargetSelector",
    "InitialTechnicalPosition",
    "TARGET_MAX_PLY",
    "TARGET_MIN_PLY",
    "TargetInputError",
    "TargetSelectionError",
    "TargetSelector",
]
