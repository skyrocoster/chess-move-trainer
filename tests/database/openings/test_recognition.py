from __future__ import annotations

import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.openings.persistence import import_opening_catalogue
from chess_move_trainer.database.openings.recognition import (
    OpeningInputError,
    OpeningRecognition,
    OpeningRecognitionError,
    RecognizedOpening,
    lookup_fen,
    replay_pgn,
)
from chess_move_trainer.database.openings.source import load_opening_sources
from chess_move_trainer.database.schema import SchemaIncompatibleError


SOURCE_NAMES = ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")
HEADER = "eco\tname\tpgn\n"


def _publish(tmp_path: Path, rows: list[tuple[str, str, str]]) -> tuple[Path, tuple[object, ...]]:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    row_text = "".join(f"{eco}\t{name}\t{pgn}\n" for eco, name, pgn in rows)
    for source_name in SOURCE_NAMES:
        (source_dir / source_name).write_text(
            HEADER + (row_text if source_name == "a.tsv" else ""),
            encoding="utf-8",
            newline="",
        )

    database_path = tmp_path / "recognition.db"
    create_schema(database_path)
    import_opening_catalogue(source_dir, _repository(database_path))
    return database_path, load_opening_sources(source_dir)


def _repository(database_path: Path) -> object:
    from chess_move_trainer.database.openings.persistence import OpeningCatalogueRepository

    return OpeningCatalogueRepository(database_path)


def _summary(result: OpeningRecognition) -> list[tuple[int, str, str, str]]:
    return [(item.ply, item.eco, item.name, item.match) for item in result.recognized]


def test_pgn_returns_ordered_breadcrumbs_without_future_leakage_and_retains_current_after_departure(
    tmp_path: Path,
) -> None:
    database_path, _routes = _publish(
        tmp_path,
        [
            ("A00", "A", "1. e4"),
            ("A00", "A-1", "1. e4 e5"),
            ("A00", "A-1a", "1. e4 e5 2. Nf3"),
            ("A00", "Future", "1. e4 e5 2. Nf3 Nc6"),
        ],
    )

    before = _database_rows(database_path)
    partial = replay_pgn(database_path, "1. e4 e5")
    departed = replay_pgn(database_path, "1. e4 e5 2. Nf3 h6")

    assert _summary(partial) == [
        (1, "A00", "A", "route"),
        (2, "A00", "A-1", "route"),
    ]
    assert partial.current == partial.recognized[-1]
    assert _summary(departed) == [
        (1, "A00", "A", "route"),
        (2, "A00", "A-1", "route"),
        (3, "A00", "A-1a", "route"),
    ]
    assert departed.current is not None
    assert departed.current.name == "A-1a"
    assert _database_rows(database_path) == before


def test_pgn_distinguishes_exact_route_from_transposition(tmp_path: Path) -> None:
    database_path, _routes = _publish(
        tmp_path,
        [("A00", "Target", "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6")],
    )

    exact = replay_pgn(database_path, "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6")
    transposed = replay_pgn(database_path, "1. e4 e5 2. Nf3 a6 3. Bb5 Nc6")

    assert _summary(exact) == [(6, "A00", "Target", "route")]
    assert _summary(transposed) == [(6, "A00", "Target", "transposition")]


def test_current_prefers_route_then_lexical_name_and_merges_repeated_label_evidence(
    tmp_path: Path,
) -> None:
    route_a = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"
    route_b = "1. e4 e5 2. Nf3 a6 3. Bb5 Nc6"
    database_path, _routes = _publish(
        tmp_path,
        [
            ("A00", "Alpha", route_a),
            ("A00", "Beta", route_a),
            ("A00", "Zeta", route_b),
            ("A00", "Alpha", route_b),
        ],
    )

    result = replay_pgn(database_path, route_a)

    assert _summary(result) == [
        (6, "A00", "Alpha", "route"),
        (6, "A00", "Beta", "route"),
        (6, "A00", "Zeta", "transposition"),
    ]
    assert result.current == RecognizedOpening(6, "A00", "Alpha", "route")


def test_fen_is_clock_insensitive_and_derives_only_reached_broader_labels(
    tmp_path: Path,
) -> None:
    database_path, routes = _publish(
        tmp_path,
        [
            ("A00", "Broad", "1. e4"),
            ("A00", "Deep", "1. e4 e5 2. Nf3"),
            ("A00", "Future", "1. e4 e5 2. Nf3 Nc6"),
        ],
    )
    deep = next(route for route in routes if route.name == "Deep")
    fields = deep.endpoint_fen.split()
    clock_changed = " ".join((*fields[:4], "99", "120"))

    result = lookup_fen(database_path, clock_changed)

    assert _summary(result) == [
        (1, "A00", "Broad", "transposition"),
        (3, "A00", "Deep", "transposition"),
    ]
    assert result.current is not None
    assert result.current.name == "Deep"


def test_fen_direct_match_and_valid_no_match_have_immutable_results(tmp_path: Path) -> None:
    database_path, routes = _publish(tmp_path, [("B00", "Only", "1. e4 c6")])
    endpoint = routes[0].endpoint_fen

    direct = lookup_fen(database_path, endpoint)
    no_match = lookup_fen(
        database_path,
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    )

    assert _summary(direct) == [(2, "B00", "Only", "transposition")]
    assert direct.current == direct.recognized[0]
    assert no_match == OpeningRecognition(recognized=(), current=None)
    with pytest.raises(FrozenInstanceError):
        direct.current = None  # type: ignore[misc]
    with pytest.raises(TypeError):
        direct.recognized[0] = direct.recognized[0]  # type: ignore[index]


@pytest.mark.parametrize(
    "pgn",
    [
        "",
        "1. e5",
        "1. e4 trailing",
        "1. e4 * [Event \"second\"] 1. d4",
        '[SetUp "1"]\n[FEN "8/8/8/8/8/8/4k3/4K3 w - - 0 1"]\n\n1. e4',
    ],
)
def test_invalid_pgn_inputs_raise_opening_input_error(tmp_path: Path, pgn: str) -> None:
    database_path, _routes = _publish(tmp_path, [("A00", "Only", "1. e4")])

    with pytest.raises(OpeningInputError):
        replay_pgn(database_path, pgn)


def test_invalid_fen_raises_opening_input_error(tmp_path: Path) -> None:
    database_path, _routes = _publish(tmp_path, [("A00", "Only", "1. e4")])

    with pytest.raises(OpeningInputError):
        lookup_fen(database_path, "not a FEN")


def test_corrupt_persisted_route_fails_as_operational_error(tmp_path: Path) -> None:
    database_path, routes = _publish(tmp_path, [("A00", "Only", "1. e4 e5")])
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE derived_opening_route_move SET dorm_ply = 3 WHERE dorm_ply = 1"
        )

    with pytest.raises(OpeningRecognitionError):
        lookup_fen(database_path, routes[0].endpoint_fen)


def test_missing_and_incompatible_databases_are_operational_failures_with_schema_distinct(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(OpeningRecognitionError):
        lookup_fen(
            missing,
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        )

    incompatible = tmp_path / "incompatible.db"
    sqlite3.connect(incompatible).close()
    with pytest.raises(SchemaIncompatibleError):
        lookup_fen(
            incompatible,
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        )


def _database_rows(database_path: Path) -> dict[str, list[tuple[object, ...]]]:
    with sqlite3.connect(database_path) as connection:
        return {
            table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table}").fetchall()]
            for table in (
                "datasource_opening",
                "derived_opening_route",
                "derived_opening_route_move",
                "derived_position",
            )
        }
