"""Validation and orchestration for the opening Line Library API."""

from __future__ import annotations

import re

from .api_schemas import LineLibraryResponse
from .errors import OpeningLineLibraryValidationError
from .repository import (
    OpeningLineLibraryQuery,
    OpeningLineLibraryRepository,
    open_read_connection,
)

_ECO_CODE = re.compile(r"^[A-E][0-9]{2}$")


def _eco_value(value: str | None, field: str) -> str | None:
    if value is None or not value.strip():
        return None
    selected = value.strip().upper()
    if _ECO_CODE.fullmatch(selected) is None:
        raise OpeningLineLibraryValidationError(
            "invalid_filter", f"{field} must be an ECO code from A00 through E99"
        )
    return selected


def _validated_query(
    search: str | None,
    eco_from: str | None,
    eco_to: str | None,
    appears_in_my_games: bool,
    sort: str | None,
) -> OpeningLineLibraryQuery:
    selected_search = None if search is None or not search.strip() else search.strip()
    selected_from = _eco_value(eco_from, "eco_from")
    selected_to = _eco_value(eco_to, "eco_to")
    if selected_from is not None and selected_to is not None and selected_from > selected_to:
        raise OpeningLineLibraryValidationError(
            "invalid_filter", "eco_from cannot be greater than eco_to"
        )
    selected_sort = "default" if sort is None or not sort.strip() else sort.strip()
    if selected_sort != "default":
        raise OpeningLineLibraryValidationError(
            "invalid_filter", "sort must be the declared default sort"
        )
    return OpeningLineLibraryQuery(
        search=selected_search,
        eco_from=selected_from,
        eco_to=selected_to,
        appears_in_my_games=appears_in_my_games,
        sort=selected_sort,
    )


def get_opening_line_library(
    search: str | None,
    eco_from: str | None,
    eco_to: str | None,
    appears_in_my_games: bool,
    sort: str | None,
) -> LineLibraryResponse:
    query = _validated_query(search, eco_from, eco_to, appears_in_my_games, sort)
    connection = open_read_connection()
    try:
        return OpeningLineLibraryRepository(connection).fetch(query)
    finally:
        connection.close()
