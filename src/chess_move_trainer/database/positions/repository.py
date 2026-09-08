"""Permanent canonical-position storage behind an opaque transaction boundary."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TypeAlias

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .canonicalization import CanonicalPosition, canonicalize_board, canonicalize_fen


class PositionStorageError(RuntimeError):
    """Raised when a compatible position database cannot be used safely."""


PositionIdentity: TypeAlias = tuple[str, str, str, str]


class PositionRepository:
    """Resolve canonical positions using package-owned connections and transactions."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    @contextmanager
    def transaction(self) -> Iterator[_PositionUnitOfWork]:
        """Yield an opaque all-or-nothing unit of work for one existing v1 database."""

        with _open_existing_connection(self._database_path, self._lock_timeout) as connection:
            try:
                _assert_compatible_schema(connection, self._lock_timeout)
            except (FileNotFoundError, SchemaIncompatibleError, ValueError):
                raise
            except Exception as error:
                raise PositionStorageError(
                    "database is not a readable compatible schema v1 database"
                ) from error

            with connection.begin():
                yield _PositionUnitOfWork(connection)

    def resolve_board(self, board: object) -> int:
        """Canonicalize and persist one board in an owned transaction."""

        with self.transaction() as unit_of_work:
            return unit_of_work.resolve_board(board)

    def resolve_fen(self, fen: str) -> int:
        """Canonicalize and persist one complete FEN in an owned transaction."""

        with self.transaction() as unit_of_work:
            return unit_of_work.resolve_fen(fen)


@contextmanager
def position_transaction(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> Iterator[_PositionUnitOfWork]:
    """Open one opaque package-owned transaction for grouped position work."""

    with PositionRepository(database_path, lock_timeout=lock_timeout).transaction() as unit_of_work:
        yield unit_of_work


class _PositionUnitOfWork:
    """Opaque position operations bound to one package-owned transaction."""

    def __init__(
        self,
        connection: object,
        *,
        position_cache: dict[PositionIdentity, int] | None = None,
    ) -> None:
        self._connection = connection
        self._position_cache = position_cache if position_cache is not None else {}
        self._new_position_cache: dict[PositionIdentity, int] = {}

    def resolve_board(self, board: object) -> int:
        return self._resolve(canonicalize_board(board))

    def resolve_fen(self, fen: str) -> int:
        return self._resolve(canonicalize_fen(fen))

    def _resolve(self, position: CanonicalPosition) -> int:
        identity = _position_identity(position)
        cached = self._position_cache.get(identity)
        if cached is not None:
            return cached
        tentative = self._new_position_cache.get(identity)
        if tentative is not None:
            return tentative

        parameters = {
            "placement": position.placement,
            "side_to_move": position.side_to_move,
            "castling_rights": position.castling_rights,
            "legal_en_passant": position.legal_en_passant,
        }
        try:
            row = self._connection.execute(
                text(
                    """
                    INSERT INTO derived_position (
                        dp_placement,
                        dp_side_to_move,
                        dp_castling_rights,
                        dp_legal_en_passant
                    ) VALUES (
                        :placement,
                        :side_to_move,
                        :castling_rights,
                        :legal_en_passant
                    )
                    ON CONFLICT (
                        dp_placement,
                        dp_side_to_move,
                        dp_castling_rights,
                        dp_legal_en_passant
                    ) DO NOTHING
                    RETURNING dp_position_id
                    """
                ),
                parameters,
            ).first()
            inserted = row is not None
            if row is None:
                row = self._connection.execute(
                    text(
                        """
                        SELECT dp_position_id
                        FROM derived_position
                        WHERE dp_placement = :placement
                          AND dp_side_to_move = :side_to_move
                          AND dp_castling_rights = :castling_rights
                          AND dp_legal_en_passant = :legal_en_passant
                        LIMIT 1
                        """
                    ),
                    parameters,
                ).first()
        except Exception as error:
            raise PositionStorageError("canonical position could not be stored") from error

        if row is None:
            raise PositionStorageError("canonical position was not returned after storage")
        position_id = int(row[0])
        if inserted:
            self._new_position_cache[identity] = position_id
        else:
            self._position_cache[identity] = position_id
        return position_id

    @property
    def _new_positions(self) -> dict[PositionIdentity, int]:
        """Return IDs that may be promoted after the owning transaction commits."""

        return self._new_position_cache


def _position_identity(position: CanonicalPosition) -> PositionIdentity:
    return (
        position.placement,
        position.side_to_move,
        position.castling_rights,
        position.legal_en_passant,
    )
