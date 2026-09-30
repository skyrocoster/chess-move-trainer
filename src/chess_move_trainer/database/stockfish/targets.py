"""On-demand, authority-defined Stockfish bulk target selection."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import CanonicalPosition
from ..positions.repository import position_transaction
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .configuration import STOCKFISH_VERSION, profile_for, quality_settings_match
from .target_support import (
    DEFAULT_TARGET_PAGE_SIZE,
    INITIAL_COMMON_TARGET_COUNT,
    INITIAL_TECHNICAL_CATEGORIES,
    INITIAL_TECHNICAL_POSITIONS,
    TARGET_MAX_PLY,
    TARGET_MIN_PLY,
    BulkTarget,
    InitialTechnicalPosition,
    TargetInputError,
    TargetSelectionError,
    _background_result_eligibility_sql,
    _background_result_parameters,
    _load_route_moves,
    _record_route_position,
    _target_from_row,
    _validate_limit,
)


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
                         SELECT dar_quality, dar_configuration_version,
                                dar_engine_version, dar_settings_json
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
        profile = profile_for(row[0])
        try:
            settings = json.loads(row[3])
        except (IndexError, TypeError, ValueError, json.JSONDecodeError):
            return True
        return (
            row[1] != profile.configuration_version
            or row[2] != STOCKFISH_VERSION
            or not quality_settings_match(settings, profile)
        )

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
                        raise TargetSelectionError(f"opening route {route_id} has no legal moves")
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


class BackgroundTargetSelector:
    """Select bounded, all-game-position browser targets in stable order."""

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

    def iter_targets(self, *, limit: int | None = None) -> Iterator[BulkTarget]:
        """Yield eligible all-ply game positions without retaining a target list."""

        _validate_limit(limit)
        yielded = 0
        cursor: tuple[int, int] | None = None
        while True:
            page = self._load_game_page(cursor)
            if not page:
                return
            for target in page:
                yield target
                yielded += 1
                if limit is not None and yielded >= limit:
                    return
            last = page[-1]
            cursor = (last.frequency, last.position_id)

    def _load_game_page(
        self,
        cursor: tuple[int, int] | None,
    ) -> tuple[BulkTarget, ...]:
        parameters = _background_result_parameters()
        parameters["page_size"] = self._page_size
        cursor_clause = ""
        if cursor is not None:
            parameters.update(
                {
                    "last_frequency": cursor[0],
                    "last_position_id": cursor[1],
                }
            )
            cursor_clause = """
              AND (
                    gc.game_count < :last_frequency
                    OR (
                        gc.game_count = :last_frequency
                        AND gc.position_id > :last_position_id
                    )
                  )
            """
        try:
            with _open_existing_connection(self._database_path, self._lock_timeout) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                rows = connection.execute(
                    text(
                        f"""
                        WITH game_counts AS (
                            SELECT derived_position_id AS position_id,
                                   COUNT(DISTINCT datasource_game_id) AS game_count
                            FROM derived_game_position
                            GROUP BY derived_position_id
                        )
                        SELECT gc.position_id, gc.game_count,
                               p.dp_placement, p.dp_side_to_move,
                               p.dp_castling_rights, p.dp_legal_en_passant
                        FROM game_counts AS gc
                        JOIN derived_position AS p
                          ON p.dp_position_id = gc.position_id
                        LEFT JOIN derived_analysis_result AS r
                          ON r.derived_position_id = gc.position_id
                        LEFT JOIN derived_analysis_queue AS q
                          ON q.derived_position_id = gc.position_id
                         WHERE q.derived_position_id IS NULL
                           AND {_background_result_eligibility_sql()}
                        {cursor_clause}
                        ORDER BY gc.game_count DESC, gc.position_id ASC
                        LIMIT :page_size
                        """
                    ),
                    parameters,
                ).all()
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise TargetSelectionError("background game targets could not be read") from error
        return tuple(_target_from_row(row) for row in rows)


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
            raise TargetSelectionError("initial analysis requires at least 20 common positions")

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


__all__ = [
    "BackgroundTargetSelector",
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
