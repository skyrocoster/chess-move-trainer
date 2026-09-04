"""Atomic publication of normalized opening routes into the v1 catalogue tables."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import CanonicalPosition, canonicalize_board
from ..positions.repository import _PositionUnitOfWork
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .source import OpeningRouteSource, load_opening_sources


class OpeningPersistenceError(RuntimeError):
    """Raised when a compatible database cannot publish the opening catalogue."""


@dataclass(frozen=True, slots=True)
class CataloguePublication:
    """Immutable counts describing one successfully committed catalogue replacement."""

    opening_count: int
    route_count: int
    move_count: int

    @property
    def label_count(self) -> int:
        """Return the number of distinct ECO/name labels published."""

        return self.opening_count


class OpeningCatalogueRepository:
    """Publish normalized routes without exposing a database connection."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        _checkpoint: Callable[[str], None] | None = None,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._checkpoint = _checkpoint if _checkpoint is not None else lambda _: None

    def replace(self, routes: Iterable[OpeningRouteSource]) -> CataloguePublication:
        """Atomically replace all opening rows with the supplied semantic routes."""

        normalized_routes = _prepare_routes(routes)
        labels = tuple(sorted({(route.eco, route.name) for route in normalized_routes}))
        move_count = sum(len(route.moves_uci) for route in normalized_routes)

        try:
            with _open_existing_connection(self._database_path, self._lock_timeout) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                with connection.begin():
                    position_work = _PositionUnitOfWork(connection)
                    endpoint_ids = self._resolve_endpoints(
                        connection, position_work, normalized_routes
                    )
                    self._checkpoint("endpoints")

                    connection.execute(text("DELETE FROM derived_opening_route_move"))
                    self._checkpoint("deleted_route_moves")
                    connection.execute(text("DELETE FROM derived_opening_route"))
                    self._checkpoint("deleted_routes")
                    connection.execute(text("DELETE FROM datasource_opening"))
                    self._checkpoint("deleted_openings")

                    label_ids = self._insert_labels(connection, labels)
                    route_ids = self._insert_routes(
                        connection, normalized_routes, label_ids, endpoint_ids
                    )
                    self._insert_route_moves(connection, normalized_routes, route_ids)
                    self._verify_publication(
                        connection, normalized_routes, route_ids, endpoint_ids
                    )
                    self._checkpoint("verified")
        except KeyboardInterrupt:
            raise
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise OpeningPersistenceError(
                "opening catalogue could not be published"
            ) from error

        return CataloguePublication(
            opening_count=len(labels),
            route_count=len(normalized_routes),
            move_count=move_count,
        )

    def _resolve_endpoints(
        self,
        connection: object,
        position_work: _PositionUnitOfWork,
        routes: tuple[OpeningRouteSource, ...],
    ) -> dict[tuple[str, str, str, str], int]:
        del connection
        endpoint_ids: dict[tuple[str, str, str, str], int] = {}
        for route in routes:
            if route.endpoint_key in endpoint_ids:
                continue
            try:
                board = chess.Board(route.endpoint_fen)
            except (TypeError, ValueError) as error:
                raise OpeningPersistenceError("route endpoint could not be reconstructed") from error
            endpoint_ids[route.endpoint_key] = position_work.resolve_board(board)
            self._checkpoint("endpoint")
        return endpoint_ids

    def _insert_labels(
        self, connection: object, labels: tuple[tuple[str, str], ...]
    ) -> dict[tuple[str, str], int]:
        label_ids: dict[tuple[str, str], int] = {}
        for eco, name in labels:
            connection.execute(
                text(
                    "INSERT INTO datasource_opening (do_eco, do_name) "
                    "VALUES (:eco, :name)"
                ),
                {"eco": eco, "name": name},
            )
            row = connection.execute(
                text(
                    "SELECT do_opening_id FROM datasource_opening "
                    "WHERE do_eco = :eco AND do_name = :name"
                ),
                {"eco": eco, "name": name},
            ).first()
            if row is None:
                raise OpeningPersistenceError("published opening label was not returned")
            label_ids[(eco, name)] = int(row[0])
            self._checkpoint("label")
        return label_ids

    def _insert_routes(
        self,
        connection: object,
        routes: tuple[OpeningRouteSource, ...],
        label_ids: dict[tuple[str, str], int],
        endpoint_ids: dict[tuple[str, str, str, str], int],
    ) -> dict[tuple[str, str, tuple[str, ...]], int]:
        route_ids: dict[tuple[str, str, tuple[str, ...]], int] = {}
        for route in routes:
            connection.execute(
                text(
                    "INSERT INTO derived_opening_route "
                    "(datasource_opening_id, derived_position_id) "
                    "VALUES (:opening_id, :position_id)"
                ),
                {
                    "opening_id": label_ids[(route.eco, route.name)],
                    "position_id": endpoint_ids[route.endpoint_key],
                },
            )
            row = connection.execute(
                text(
                    "SELECT dor_route_id FROM derived_opening_route "
                    "WHERE datasource_opening_id = :opening_id "
                    "AND derived_position_id = :position_id "
                    "ORDER BY dor_route_id DESC LIMIT 1"
                ),
                {
                    "opening_id": label_ids[(route.eco, route.name)],
                    "position_id": endpoint_ids[route.endpoint_key],
                },
            ).first()
            if row is None:
                raise OpeningPersistenceError("published opening route was not returned")
            route_ids[(route.eco, route.name, route.moves_uci)] = int(row[0])
            self._checkpoint("route")
        return route_ids

    def _insert_route_moves(
        self,
        connection: object,
        routes: tuple[OpeningRouteSource, ...],
        route_ids: dict[tuple[str, str, tuple[str, ...]], int],
    ) -> None:
        for route in routes:
            route_id = route_ids[(route.eco, route.name, route.moves_uci)]
            for ply, move_uci in enumerate(route.moves_uci, start=1):
                connection.execute(
                    text(
                        "INSERT INTO derived_opening_route_move "
                        "(derived_opening_route_id, dorm_ply, dorm_move_uci) "
                        "VALUES (:route_id, :ply, :move_uci)"
                    ),
                    {"route_id": route_id, "ply": ply, "move_uci": move_uci},
                )
                self._checkpoint("route_move")

    def _verify_publication(
        self,
        connection: object,
        routes: tuple[OpeningRouteSource, ...],
        route_ids: dict[tuple[str, str, tuple[str, ...]], int],
        endpoint_ids: dict[tuple[str, str, str, str], int],
    ) -> None:
        for route in routes:
            route_id = route_ids[(route.eco, route.name, route.moves_uci)]
            rows = connection.execute(
                text(
                    "SELECT dorm_ply, dorm_move_uci "
                    "FROM derived_opening_route_move "
                    "WHERE derived_opening_route_id = :route_id ORDER BY dorm_ply"
                ),
                {"route_id": route_id},
            ).all()
            expected_rows = tuple(
                (ply, move_uci) for ply, move_uci in enumerate(route.moves_uci, start=1)
            )
            if tuple((int(row[0]), str(row[1])) for row in rows) != expected_rows:
                raise OpeningPersistenceError("route move plies are not contiguous")

            board = chess.Board()
            for ply, move_uci in enumerate(route.moves_uci, start=1):
                try:
                    move = chess.Move.from_uci(move_uci)
                except ValueError as error:
                    raise OpeningPersistenceError(
                        f"route contains invalid UCI at ply {ply}"
                    ) from error
                if move not in board.legal_moves:
                    raise OpeningPersistenceError(f"route contains an illegal move at ply {ply}")
                board.push(move)
            replayed = canonicalize_board(board)
            endpoint_id = endpoint_ids[route.endpoint_key]
            endpoint_row = connection.execute(
                text(
                    "SELECT dp_placement, dp_side_to_move, dp_castling_rights, "
                    "dp_legal_en_passant FROM derived_position "
                    "WHERE dp_position_id = :position_id"
                ),
                {"position_id": endpoint_id},
            ).first()
            if endpoint_row is None:
                raise OpeningPersistenceError("route endpoint was not stored")
            stored = CanonicalPosition(
                placement=str(endpoint_row[0]),
                side_to_move=str(endpoint_row[1]),
                castling_rights=str(endpoint_row[2]),
                legal_en_passant=str(endpoint_row[3]),
            )
            if replayed != stored or stored != route.endpoint_position:
                raise OpeningPersistenceError("route endpoint does not match replay")


def import_opening_catalogue(
    source_dir: str | Path, repository: OpeningCatalogueRepository
) -> CataloguePublication:
    """Normalize all source files before asking the repository to mutate storage."""

    routes = load_opening_sources(source_dir)
    return repository.replace(routes)


def _prepare_routes(routes: Iterable[OpeningRouteSource]) -> tuple[OpeningRouteSource, ...]:
    try:
        prepared = tuple(routes)
    except TypeError as error:
        raise OpeningPersistenceError("routes must be an iterable of normalized routes") from error
    if any(not isinstance(route, OpeningRouteSource) for route in prepared):
        raise OpeningPersistenceError("routes must contain only normalized opening routes")

    ordered = tuple(sorted(prepared, key=lambda route: (route.eco, route.name, route.moves_uci)))
    identities = [(route.eco, route.name, route.moves_uci) for route in ordered]
    if len(set(identities)) != len(identities):
        raise OpeningPersistenceError("routes contain a duplicate semantic identity")
    return ordered
