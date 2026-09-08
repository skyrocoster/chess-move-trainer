from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy.engine import Connection

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.openings.persistence import (
    CataloguePublication,
    OpeningCatalogueRepository,
    OpeningPersistenceError,
    import_opening_catalogue,
)
from chess_move_trainer.database.openings.source import OpeningSourceError, load_opening_sources
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.schema import SchemaIncompatibleError


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "catalogue-valid"
SOURCE_NAMES = ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")


def _source_dir(tmp_path: Path) -> Path:
    source_dir = tmp_path / "sources"
    shutil.copytree(FIXTURE_DIR, source_dir)
    return source_dir


def _write_source_dir(tmp_path: Path, pgn: str, *, eco: str = "A00", name: str = "Replacement") -> Path:
    source_dir = tmp_path / "replacement"
    source_dir.mkdir()
    for source_name in SOURCE_NAMES:
        row = f"{eco}\t{name}\t{pgn}\n" if source_name == "a.tsv" else ""
        (source_dir / source_name).write_text(
            "eco\tname\tpgn\n" + row, encoding="utf-8", newline=""
        )
    return source_dir


def _rows(database_path: Path, table: str) -> list[tuple[object, ...]]:
    with sqlite3.connect(database_path) as connection:
        return [tuple(row) for row in connection.execute(f"SELECT * FROM {table}").fetchall()]


def _catalogue_snapshot(database_path: Path) -> dict[str, list[tuple[object, ...]]]:
    return {
        table: _rows(database_path, table)
        for table in (
            "datasource_opening",
            "derived_opening_route",
            "derived_opening_route_move",
            "derived_position",
        )
    }


def test_first_publication_writes_labels_routes_and_contiguous_children(tmp_path: Path) -> None:
    database_path = tmp_path / "catalogue.db"
    create_schema(database_path)
    routes = load_opening_sources(_source_dir(tmp_path))

    publication = OpeningCatalogueRepository(database_path).replace(routes)

    assert publication == CataloguePublication(opening_count=4, route_count=5, move_count=20)
    assert publication.label_count == 4
    assert len(_rows(database_path, "datasource_opening")) == 4
    assert len(_rows(database_path, "derived_opening_route")) == 5
    with sqlite3.connect(database_path) as connection:
        route_rows = connection.execute(
            "SELECT derived_opening_route_id, dorm_ply, dorm_move_uci "
            "FROM derived_opening_route_move ORDER BY derived_opening_route_id, dorm_ply"
        ).fetchall()
    current_route = None
    expected_ply = 1
    for route_id, ply, _move_uci in route_rows:
        if route_id != current_route:
            current_route = route_id
            expected_ply = 1
        assert ply == expected_ply
        expected_ply += 1


def test_routes_sharing_labels_and_endpoints_remain_distinct(tmp_path: Path) -> None:
    database_path = tmp_path / "shared.db"
    create_schema(database_path)
    routes = load_opening_sources(_source_dir(tmp_path))

    OpeningCatalogueRepository(database_path).replace(routes)

    with sqlite3.connect(database_path) as connection:
        transposing_label_id = connection.execute(
            "SELECT do_opening_id FROM datasource_opening "
            "WHERE do_eco = 'A00' AND do_name = 'Transposing route'"
        ).fetchone()[0]
        transposing_routes = connection.execute(
            "SELECT dor_route_id, derived_position_id FROM derived_opening_route "
            "WHERE datasource_opening_id = ? ORDER BY dor_route_id",
            (transposing_label_id,),
        ).fetchall()
        assert len(transposing_routes) == 2
        assert transposing_routes[0][1] == transposing_routes[1][1]


def test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "reuse.db"
    create_schema(database_path)
    routes = load_opening_sources(_source_dir(tmp_path))
    reused_id = PositionRepository(database_path).resolve_fen(routes[0].endpoint_fen)
    unrelated_id = PositionRepository(database_path).resolve_fen(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
    )

    OpeningCatalogueRepository(database_path).replace(routes)
    replacement = load_opening_sources(
        _write_source_dir(tmp_path, "1. c4 e5", eco="C00")
    )
    OpeningCatalogueRepository(database_path).replace(replacement)

    position_ids = {row[0] for row in _rows(database_path, "derived_position")}
    assert reused_id in position_ids
    assert unrelated_id in position_ids
    assert len(_rows(database_path, "datasource_opening")) == 1
    assert len(_rows(database_path, "derived_opening_route")) == 1


def test_deletion_checkpoint_order_is_child_first(tmp_path: Path) -> None:
    database_path = tmp_path / "deletion-order.db"
    create_schema(database_path)
    routes = load_opening_sources(_source_dir(tmp_path))
    events: list[str] = []

    OpeningCatalogueRepository(database_path, _checkpoint=events.append).replace(routes)

    assert [event for event in events if event.startswith("deleted_")] == [
        "deleted_route_moves",
        "deleted_routes",
        "deleted_openings",
    ]


def test_malformed_input_is_rejected_before_repository_mutation(tmp_path: Path) -> None:
    database_path = tmp_path / "pretransaction.db"
    create_schema(database_path)
    source_dir = _source_dir(tmp_path)
    (source_dir / "a.tsv").write_text(
        "eco\tname\tpgn\nA00\tBad\t1. e4 Nonsense\n", encoding="utf-8"
    )
    before = _catalogue_snapshot(database_path)

    class UnexpectedRepository:
        def replace(self, routes: object) -> None:
            raise AssertionError("replace must not be called for malformed input")

    with pytest.raises(OpeningSourceError):
        import_opening_catalogue(source_dir, UnexpectedRepository())  # type: ignore[arg-type]
    assert _catalogue_snapshot(database_path) == before


def test_storage_failure_rolls_back_catalogue_and_new_endpoints(tmp_path: Path) -> None:
    database_path = tmp_path / "storage-failure.db"
    create_schema(database_path)
    original = load_opening_sources(_source_dir(tmp_path))
    OpeningCatalogueRepository(database_path).replace(original)
    before = _catalogue_snapshot(database_path)
    replacement = load_opening_sources(_write_source_dir(tmp_path, "1. c4 e5"))

    def fail_after_route(event: str) -> None:
        if event == "route":
            raise RuntimeError("synthetic storage failure")

    with pytest.raises(OpeningPersistenceError):
        OpeningCatalogueRepository(database_path, _checkpoint=fail_after_route).replace(replacement)

    assert _catalogue_snapshot(database_path) == before


def test_keyboard_interrupt_rolls_back_catalogue_and_new_endpoints(tmp_path: Path) -> None:
    database_path = tmp_path / "interrupt.db"
    create_schema(database_path)
    original = load_opening_sources(_source_dir(tmp_path))
    OpeningCatalogueRepository(database_path).replace(original)
    before = _catalogue_snapshot(database_path)
    replacement = load_opening_sources(_write_source_dir(tmp_path, "1. c4 e5"))

    def interrupt_after_route(event: str) -> None:
        if event == "route":
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        OpeningCatalogueRepository(
            database_path, _checkpoint=interrupt_after_route
        ).replace(replacement)

    assert _catalogue_snapshot(database_path) == before


def test_schema_incompatibility_remains_distinguishable(tmp_path: Path) -> None:
    database_path = tmp_path / "incompatible.db"
    sqlite3.connect(database_path).close()

    with pytest.raises(SchemaIncompatibleError):
        OpeningCatalogueRepository(database_path).replace(())


def test_replace_uses_returned_ids_and_batches_route_moves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_path = tmp_path / "returned-ids.db"
    create_schema(database_path)
    routes = load_opening_sources(_source_dir(tmp_path))
    calls: list[tuple[str, object]] = []
    original_execute = Connection.execute

    def record_execute(
        connection: Connection,
        statement: object,
        parameters: object = None,
        *,
        execution_options: object = None,
    ) -> object:
        calls.append((str(statement), parameters))
        if parameters is None:
            return original_execute(
                connection,
                statement,
                execution_options=execution_options,
            )
        return original_execute(
            connection,
            statement,
            parameters,
            execution_options=execution_options,
        )

    monkeypatch.setattr(Connection, "execute", record_execute)
    publication = OpeningCatalogueRepository(database_path).replace(routes)

    assert publication.move_count == 20
    label_inserts = [
        (statement, parameters)
        for statement, parameters in calls
        if "INSERT INTO datasource_opening" in statement
    ]
    route_inserts = [
        (statement, parameters)
        for statement, parameters in calls
        if "INSERT INTO derived_opening_route " in statement
    ]
    route_move_inserts = [
        (statement, parameters)
        for statement, parameters in calls
        if "INSERT INTO derived_opening_route_move" in statement
    ]

    assert len(label_inserts) == 4
    assert all("RETURNING do_opening_id" in statement for statement, _ in label_inserts)
    assert len(route_inserts) == 5
    assert all("RETURNING dor_route_id" in statement for statement, _ in route_inserts)
    assert len(route_move_inserts) == 1
    move_parameters = route_move_inserts[0][1]
    assert isinstance(move_parameters, list)
    assert len(move_parameters) == 20
    route_plies = [
        (int(parameters["route_id"]), int(parameters["ply"]))
        for parameters in move_parameters
    ]
    assert route_plies == sorted(route_plies)
    assert not any(
        "SELECT do_opening_id FROM datasource_opening" in statement
        or "SELECT dor_route_id FROM derived_opening_route" in statement
        for statement, _ in calls
    )
