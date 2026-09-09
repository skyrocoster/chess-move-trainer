from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.openings.catalogue import (
    OpeningCatalogueQuery,
    OpeningCatalogueRepository,
    OpeningCatalogueSchemaError,
    OpeningCatalogueStorageError,
    OpeningCatalogueValidationError,
    read_opening,
)
from chess_move_trainer.database.openings.keys import opening_api_key


_POSITIONS = {
    1: (
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "w",
        "KQkq",
        "-",
    ),
    2: (
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
        "b",
        "KQkq",
        "-",
    ),
    3: (
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR",
        "w",
        "KQkq",
        "-",
    ),
}


def _make_database(tmp_path: Path) -> Path:
    database = tmp_path / "catalogue.db"
    create_schema(database)
    with sqlite3.connect(database) as connection:
        for position_id, fields in _POSITIONS.items():
            connection.execute(
                """
                INSERT INTO derived_position
                    (dp_position_id, dp_placement, dp_side_to_move,
                     dp_castling_rights, dp_legal_en_passant)
                VALUES (?, ?, ?, ?, ?)
                """,
                (position_id, *fields),
            )
        for game_id in range(1, 4):
            connection.execute(
                """
                INSERT INTO datasource_game
                    (dg_game_id, dg_chesscom_game_uuid, dg_source_url,
                     dg_original_pgn, dg_trainer_color,
                     dg_trainer_chesscom_uuid)
                VALUES (?, ?, ?, ?, 'white', ?)
                """,
                (
                    game_id,
                    f"00000000-0000-4000-8000-{game_id:012d}",
                    f"https://example.test/{game_id}",
                    "[Result \"*\"]\n\n*",
                    "11111111-1111-4111-8111-111111111111",
                ),
            )
        labels = (
            (1, "A00", "Alpha"),
            (2, "B10", "Beta:Study"),
            (3, "C20", "Gamma"),
            (4, "D30", "Empty"),
            (5, "E99", "Echo"),
        )
        connection.executemany(
            "INSERT INTO datasource_opening (do_opening_id, do_eco, do_name) VALUES (?, ?, ?)",
            labels,
        )
        routes = (
            (1, 1, 1),
            (2, 1, 1),
            (3, 2, 1),
            (4, 2, 2),
            (5, 3, 3),
        )
        connection.executemany(
            """
            INSERT INTO derived_opening_route
                (dor_route_id, datasource_opening_id, derived_position_id)
            VALUES (?, ?, ?)
            """,
            routes,
        )
        occurrences = (
            (1, 2, 1),
            (1, 3, 1),
            (1, 5, 2),
            (2, 5, 1),
            (2, 4, 3),
            (3, 1, 2),
            (3, 4, 2),
        )
        connection.executemany(
            """
            INSERT INTO derived_game_position
                (datasource_game_id, dgp_ply, derived_position_id,
                 dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number)
            VALUES (?, ?, ?, NULL, 0, 1)
            """,
            occurrences,
        )
    return database


def _keys(page: object) -> list[str]:
    return [item.key for item in page.items]  # type: ignore[attr-defined]


def test_catalogue_counts_distinct_usage_and_selects_deterministic_deepest(
    tmp_path: Path,
) -> None:
    database = _make_database(tmp_path)

    page = OpeningCatalogueRepository(database).read()

    assert _keys(page) == [
        "A00:Alpha",
        "B10:Beta:Study",
        "C20:Gamma",
        "D30:Empty",
        "E99:Echo",
    ]
    assert page.total == 5
    assert page.total_pages == 1
    assert not page.has_next
    assert page.items[0].route_count == 2
    assert page.items[0].games_reached == 2
    assert page.items[0].games_deepest == 1
    assert page.items[1].route_count == 2
    assert page.items[1].games_reached == 3
    assert page.items[1].games_deepest == 2
    assert page.items[2].route_count == 1
    assert page.items[2].games_reached == 1
    assert page.items[2].games_deepest == 0
    assert page.items[3].route_count == 0
    assert page.items[3].games_reached == 0
    assert page.items[3].games_deepest == 0
    assert page.items[1].key == opening_api_key("B10", "Beta:Study")


def test_read_opening_matches_catalogue_entry_for_colon_and_unicode_key(
    tmp_path: Path,
) -> None:
    database = _make_database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE datasource_opening SET do_name = ? WHERE do_opening_id = 5",
            ("Réti:Étude Opening",),
        )

    page = OpeningCatalogueRepository(database).read()
    detail = read_opening(database, "E99:Réti:Étude Opening")

    expected = next(item for item in page.items if item.key == "E99:Réti:Étude Opening")
    assert detail == expected
    assert detail is not None
    assert detail.route_count == 0
    assert detail.games_reached == 0
    assert detail.games_deepest == 0


def test_read_opening_returns_none_for_valid_absent_key(tmp_path: Path) -> None:
    database = _make_database(tmp_path)

    assert read_opening(database, "A00:Not in the catalogue") is None


@pytest.mark.parametrize("opening_key", ["not-a-key", "A0:Alpha", "A00:"])
def test_read_opening_rejects_malformed_key(
    tmp_path: Path, opening_key: str
) -> None:
    database = _make_database(tmp_path)

    with pytest.raises(OpeningCatalogueValidationError):
        read_opening(database, opening_key)


@pytest.mark.parametrize(
    ("sort", "expected"),
    [
        ("eco_asc", ["A00:Alpha", "B10:Beta:Study", "C20:Gamma", "D30:Empty", "E99:Echo"]),
        ("eco_desc", ["E99:Echo", "D30:Empty", "C20:Gamma", "B10:Beta:Study", "A00:Alpha"]),
        ("name_asc", ["A00:Alpha", "B10:Beta:Study", "E99:Echo", "D30:Empty", "C20:Gamma"]),
        ("name_desc", ["C20:Gamma", "D30:Empty", "E99:Echo", "B10:Beta:Study", "A00:Alpha"]),
        ("route_count_asc", ["D30:Empty", "E99:Echo", "C20:Gamma", "A00:Alpha", "B10:Beta:Study"]),
        ("route_count_desc", ["A00:Alpha", "B10:Beta:Study", "C20:Gamma", "D30:Empty", "E99:Echo"]),
        ("games_reached_asc", ["D30:Empty", "E99:Echo", "C20:Gamma", "A00:Alpha", "B10:Beta:Study"]),
        ("games_reached_desc", ["B10:Beta:Study", "A00:Alpha", "C20:Gamma", "D30:Empty", "E99:Echo"]),
        ("games_deepest_asc", ["C20:Gamma", "D30:Empty", "E99:Echo", "A00:Alpha", "B10:Beta:Study"]),
        ("games_deepest_desc", ["B10:Beta:Study", "A00:Alpha", "C20:Gamma", "D30:Empty", "E99:Echo"]),
    ],
)
def test_catalogue_supports_all_approved_sorts(
    tmp_path: Path, sort: str, expected: list[str]
) -> None:
    page = OpeningCatalogueRepository(_make_database(tmp_path)).read(
        OpeningCatalogueQuery(sort=sort)  # type: ignore[arg-type]
    )

    assert _keys(page) == expected


def test_catalogue_search_and_eco_bounds_are_trimmed_and_combine_with_and(
    tmp_path: Path,
) -> None:
    repository = OpeningCatalogueRepository(_make_database(tmp_path))

    assert _keys(repository.search(OpeningCatalogueQuery(search="  beta  "))) == [
        "B10:Beta:Study"
    ]
    assert _keys(
        repository.read(OpeningCatalogueQuery(search="a", eco_from=" b00 ", eco_to=" d99"))
    ) == ["B10:Beta:Study", "C20:Gamma"]
    assert repository.read(OpeningCatalogueQuery(search="   ")).total == 5


def test_catalogue_paginates_empty_and_beyond_end_pages(tmp_path: Path) -> None:
    repository = OpeningCatalogueRepository(_make_database(tmp_path))

    first = repository.read(OpeningCatalogueQuery(page_size=2, page=1))
    second = repository.read(OpeningCatalogueQuery(page_size=2, page=2))
    beyond = repository.read(OpeningCatalogueQuery(page_size=2, page=4))
    empty = repository.read(OpeningCatalogueQuery(search="not-present"))

    assert _keys(first) == ["A00:Alpha", "B10:Beta:Study"]
    assert first.total_pages == 3 and first.has_next
    assert _keys(second) == ["C20:Gamma", "D30:Empty"]
    assert _keys(beyond) == [] and beyond.total == 5 and not beyond.has_next
    assert empty.items == ()
    assert empty.total == 0 and empty.total_pages == 0 and not empty.has_next


@pytest.mark.parametrize(
    "kwargs",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"search": 4},
        {"eco_from": "A0"},
        {"eco_to": "F00"},
        {"eco_from": "C20", "eco_to": "B99"},
        {"sort": "unknown"},
    ],
)
def test_catalogue_rejects_invalid_filters(kwargs: dict[str, object]) -> None:
    with pytest.raises(OpeningCatalogueValidationError):
        OpeningCatalogueQuery(**kwargs)


def test_catalogue_is_deterministic_read_only_and_uses_explicit_path(tmp_path: Path) -> None:
    database = _make_database(tmp_path)
    before = database.read_bytes()
    repository = OpeningCatalogueRepository(database)

    first = repository.read(OpeningCatalogueQuery(page_size=3, sort="name_desc"))
    second = repository.read(OpeningCatalogueQuery(page_size=3, sort="name_desc"))
    detail = read_opening(database, "B10:Beta:Study")

    assert first == second
    assert detail is not None
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("catalogue.db-*"))


def test_catalogue_rejects_missing_incompatible_and_malformed_data(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(OpeningCatalogueStorageError):
        OpeningCatalogueRepository(missing).read()
    with pytest.raises(OpeningCatalogueStorageError):
        read_opening(missing, "A00:Alpha")

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE not_schema_v1 (value TEXT)")
    before = incompatible.read_bytes()
    with pytest.raises(OpeningCatalogueSchemaError):
        OpeningCatalogueRepository(incompatible).read()
    with pytest.raises(OpeningCatalogueSchemaError):
        read_opening(incompatible, "A00:Alpha")
    assert incompatible.read_bytes() == before

    malformed_directory = tmp_path / "malformed"
    malformed_directory.mkdir()
    malformed = _make_database(malformed_directory)
    with sqlite3.connect(malformed) as connection:
        connection.execute(
            "UPDATE datasource_opening SET do_name = '' WHERE do_opening_id = 1"
        )
    with pytest.raises(OpeningCatalogueStorageError):
        OpeningCatalogueRepository(malformed).read()
