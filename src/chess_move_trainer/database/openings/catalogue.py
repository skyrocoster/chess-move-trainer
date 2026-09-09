"""Read-only, explicit-path browsing of the schema-v1 opening catalogue."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import cmp_to_key
from pathlib import Path
from typing import Literal

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .keys import OpeningKeyError, opening_api_key, parse_opening_api_key


OpeningCatalogueSort = Literal[
    "eco_asc",
    "eco_desc",
    "name_asc",
    "name_desc",
    "route_count_asc",
    "route_count_desc",
    "games_reached_asc",
    "games_reached_desc",
    "games_deepest_asc",
    "games_deepest_desc",
]

_SORTS: tuple[OpeningCatalogueSort, ...] = (
    "eco_asc",
    "eco_desc",
    "name_asc",
    "name_desc",
    "route_count_asc",
    "route_count_desc",
    "games_reached_asc",
    "games_reached_desc",
    "games_deepest_asc",
    "games_deepest_desc",
)
_ECO_PATTERN = re.compile(r"[A-E][0-9]{2}\Z")


class OpeningCatalogueError(Exception):
    """Base class for bounded opening-catalogue failures."""


class OpeningCatalogueValidationError(OpeningCatalogueError, ValueError):
    """Raised when an opening-catalogue query is invalid."""


class OpeningCatalogueSchemaError(OpeningCatalogueError, RuntimeError):
    """Raised when the selected database is not exactly schema v1."""


class OpeningCatalogueStorageError(OpeningCatalogueError, RuntimeError):
    """Raised when compatible opening-catalogue data cannot be read safely."""


@dataclass(frozen=True, slots=True)
class OpeningCatalogueQuery:
    """The filters, ordering, and pagination controls for one catalogue read."""

    page: int = 1
    page_size: int = 50
    search: str | None = None
    eco_from: str | None = None
    eco_to: str | None = None
    sort: OpeningCatalogueSort = "eco_asc"

    def __post_init__(self) -> None:
        if type(self.page) is not int or self.page < 1:
            raise OpeningCatalogueValidationError("page must be a positive integer")
        if type(self.page_size) is not int or not 1 <= self.page_size <= 100:
            raise OpeningCatalogueValidationError(
                "page_size must be an integer from 1 through 100"
            )
        if self.search is not None:
            if type(self.search) is not str:
                raise OpeningCatalogueValidationError("search must be text")
            normalized_search = self.search.strip()
            object.__setattr__(
                self,
                "search",
                normalized_search if normalized_search else None,
            )

        normalized_from = _normalize_eco_bound(self.eco_from, "eco_from")
        normalized_to = _normalize_eco_bound(self.eco_to, "eco_to")
        if normalized_from is not None and normalized_to is not None:
            if normalized_from > normalized_to:
                raise OpeningCatalogueValidationError(
                    "eco_from cannot be greater than eco_to"
                )
        object.__setattr__(self, "eco_from", normalized_from)
        object.__setattr__(self, "eco_to", normalized_to)

        if type(self.sort) is not str or self.sort not in _SORTS:
            raise OpeningCatalogueValidationError("sort has an unsupported value")


@dataclass(frozen=True, slots=True)
class OpeningCatalogueEntry:
    """One public ECO/name label and its distinct-game usage counts."""

    key: str
    eco: str
    name: str
    route_count: int
    games_reached: int
    games_deepest: int


@dataclass(frozen=True, slots=True)
class OpeningCataloguePage:
    """One finite, deterministic page of opening labels."""

    items: tuple[OpeningCatalogueEntry, ...]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool


@dataclass(frozen=True, slots=True)
class _OpeningLabel:
    opening_id: int
    key: str
    eco: str
    name: str
    route_count: int


class OpeningCatalogueRepository:
    """Browse normalized openings without exposing a database connection."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = Path(database_path)
        self._lock_timeout = lock_timeout

    def read(self, query: OpeningCatalogueQuery | None = None) -> OpeningCataloguePage:
        """Return the finite page matching every supplied catalogue filter."""

        request = OpeningCatalogueQuery() if query is None else query
        if not isinstance(request, OpeningCatalogueQuery):
            raise OpeningCatalogueValidationError(
                "query must be an OpeningCatalogueQuery"
            )

        entries = self._read_entries()
        filtered = tuple(
            entry for entry in entries if _matches(entry, request)
        )
        ordered = tuple(
            sorted(filtered, key=cmp_to_key(lambda left, right: _compare(left, right, request.sort)))
        )

        total = len(ordered)
        total_pages = math.ceil(total / request.page_size)
        start = (request.page - 1) * request.page_size
        return OpeningCataloguePage(
            items=ordered[start : start + request.page_size],
            page=request.page,
            page_size=request.page_size,
            total=total,
            total_pages=total_pages,
            has_next=request.page < total_pages,
        )

    def read_one(self, opening_key: str) -> OpeningCatalogueEntry | None:
        """Return one exact public-key entry, or ``None`` when it is absent."""

        try:
            parse_opening_api_key(opening_key)
        except OpeningKeyError as error:
            raise OpeningCatalogueValidationError(
                "opening_key must be formatted as ECO:Name"
            ) from error

        return next(
            (entry for entry in self._read_entries() if entry.key == opening_key),
            None,
        )

    def _read_entries(self) -> tuple[OpeningCatalogueEntry, ...]:
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                labels = _load_labels(connection)
                reached, deepest = _load_usage(connection, labels)
        except KeyboardInterrupt:
            raise
        except SchemaIncompatibleError as error:
            raise OpeningCatalogueSchemaError(str(error)) from error
        except OpeningCatalogueError:
            raise
        except Exception as error:
            raise OpeningCatalogueStorageError(
                "opening catalogue could not be read"
            ) from error

        return tuple(
            OpeningCatalogueEntry(
                key=label.key,
                eco=label.eco,
                name=label.name,
                route_count=label.route_count,
                games_reached=len(reached.get(label.key, set())),
                games_deepest=deepest.get(label.key, 0),
            )
            for label in labels
        )

    search = read


OpeningCatalogueReader = OpeningCatalogueRepository


def read_openings(
    database_path: str | Path,
    query: OpeningCatalogueQuery | None = None,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> OpeningCataloguePage:
    """Read one explicit database path without exposing a connection handle."""

    return OpeningCatalogueRepository(database_path, lock_timeout=lock_timeout).read(query)


def read_opening(
    database_path: str | Path,
    opening_key: str,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> OpeningCatalogueEntry | None:
    """Read one exact public opening key from an explicit database path."""

    return OpeningCatalogueRepository(
        database_path, lock_timeout=lock_timeout
    ).read_one(opening_key)


def _load_labels(connection: object) -> tuple[_OpeningLabel, ...]:
    rows = connection.execute(
        text(
            """
            SELECT o.do_opening_id, o.do_eco, o.do_name,
                   COUNT(r.dor_route_id) AS route_count
            FROM datasource_opening AS o
            LEFT JOIN derived_opening_route AS r
              ON r.datasource_opening_id = o.do_opening_id
            GROUP BY o.do_opening_id, o.do_eco, o.do_name
            ORDER BY o.do_opening_id
            """
        )
    ).all()

    labels: list[_OpeningLabel] = []
    by_key: dict[str, tuple[int, str, str]] = {}
    by_id: set[int] = set()
    try:
        for row in rows:
            opening_id = _required_int(row[0], "opening id")
            eco = _required_text(row[1], "opening ECO")
            name = _required_text(row[2], "opening name")
            route_count = _required_int(row[3], "route count")
            if opening_id in by_id or route_count < 0:
                raise ValueError("opening row is malformed")
            key = opening_api_key(eco, name)
            prior = by_key.get(key)
            identity = (opening_id, eco, name)
            if prior is not None and prior != identity:
                raise ValueError("opening API keys collide")
            by_key[key] = identity
            by_id.add(opening_id)
            labels.append(
                _OpeningLabel(
                    opening_id=opening_id,
                    key=key,
                    eco=eco,
                    name=name,
                    route_count=route_count,
                )
            )
    except (IndexError, TypeError, ValueError, OpeningKeyError) as error:
        raise OpeningCatalogueStorageError("opening label row is malformed") from error

    return tuple(labels)


def _load_usage(
    connection: object,
    labels: tuple[_OpeningLabel, ...],
) -> tuple[dict[str, set[int]], dict[str, int]]:
    labels_by_id = {label.opening_id: label for label in labels}
    reached: dict[str, set[int]] = {label.key: set() for label in labels}
    game_opening_max_ply: dict[tuple[int, str], int] = {}

    rows = connection.execute(
        text(
            """
            SELECT g.datasource_game_id, g.dgp_ply,
                   o.do_opening_id, o.do_eco, o.do_name
            FROM derived_game_position AS g
            JOIN derived_opening_route AS r
              ON r.derived_position_id = g.derived_position_id
            JOIN datasource_opening AS o
              ON o.do_opening_id = r.datasource_opening_id
            ORDER BY g.datasource_game_id, g.dgp_ply,
                     o.do_eco, o.do_name
            """
        )
    ).all()

    try:
        for row in rows:
            game_id = _required_int(row[0], "opening game id")
            ply = _required_int(row[1], "opening ply")
            opening_id = _required_int(row[2], "opening id")
            eco = _required_text(row[3], "opening ECO")
            name = _required_text(row[4], "opening name")
            label = labels_by_id.get(opening_id)
            if label is None or label.eco != eco or label.name != name or ply < 0:
                raise ValueError("opening occurrence row is malformed")
            key = opening_api_key(eco, name)
            reached[key].add(game_id)
            prior = game_opening_max_ply.get((game_id, key))
            if prior is None or ply > prior:
                game_opening_max_ply[(game_id, key)] = ply
    except (IndexError, TypeError, ValueError, OpeningKeyError) as error:
        raise OpeningCatalogueStorageError(
            "opening occurrence row is malformed"
        ) from error

    deepest: dict[str, int] = {}
    per_game: dict[int, list[tuple[int, str]]] = {}
    for (game_id, key), ply in game_opening_max_ply.items():
        per_game.setdefault(game_id, []).append((ply, key))
    for matches in per_game.values():
        _ply, key = min(matches, key=lambda match: (-match[0], match[1]))
        deepest[key] = deepest.get(key, 0) + 1
    return reached, deepest


def _matches(entry: OpeningCatalogueEntry, query: OpeningCatalogueQuery) -> bool:
    if query.eco_from is not None and entry.eco < query.eco_from:
        return False
    if query.eco_to is not None and entry.eco > query.eco_to:
        return False
    if query.search is not None:
        needle = query.search.casefold()
        if needle not in entry.eco.casefold() and needle not in entry.name.casefold():
            return False
    return True


def _compare(
    left: OpeningCatalogueEntry,
    right: OpeningCatalogueEntry,
    sort: OpeningCatalogueSort,
) -> int:
    if sort.startswith("eco_"):
        left_value, right_value = left.eco, right.eco
    elif sort.startswith("name_"):
        left_value, right_value = left.name, right.name
    elif sort.startswith("route_count_"):
        left_value, right_value = left.route_count, right.route_count
    elif sort.startswith("games_reached_"):
        left_value, right_value = left.games_reached, right.games_reached
    else:
        left_value, right_value = left.games_deepest, right.games_deepest
    result = (left_value > right_value) - (left_value < right_value)
    if sort.endswith("_desc"):
        result = -result
    if result:
        return result
    return (left.key > right.key) - (left.key < right.key)


def _normalize_eco_bound(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise OpeningCatalogueValidationError(f"{field_name} must be an ECO code")
    normalized = value.strip().upper()
    if _ECO_PATTERN.fullmatch(normalized) is None:
        raise OpeningCatalogueValidationError(f"{field_name} must be an ECO code")
    return normalized


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _required_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{field_name} must be an integer")
    return value


__all__ = [
    "OpeningCatalogueEntry",
    "OpeningCatalogueError",
    "OpeningCataloguePage",
    "OpeningCatalogueQuery",
    "OpeningCatalogueReader",
    "OpeningCatalogueRepository",
    "OpeningCatalogueSchemaError",
    "OpeningCatalogueSort",
    "OpeningCatalogueStorageError",
    "OpeningCatalogueValidationError",
    "read_openings",
]
