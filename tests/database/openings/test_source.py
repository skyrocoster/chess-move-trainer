from __future__ import annotations

import shutil
from dataclasses import FrozenInstanceError
from pathlib import Path

import chess
import pytest

from chess_move_trainer.database.openings.source import (
    OpeningRouteSource,
    OpeningSourceError,
    load_opening_sources,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "catalogue-valid"
EXPECTED_FILES = ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")


def _copy_fixture(tmp_path: Path) -> Path:
    source_dir = tmp_path / "sources"
    shutil.copytree(FIXTURE_DIR, source_dir)
    return source_dir


def _write_batch(source_dir: Path, rows: dict[str, list[str]]) -> None:
    source_dir.mkdir()
    for source_name in EXPECTED_FILES:
        data_rows = rows.get(source_name, [])
        (source_dir / source_name).write_text(
            "eco\tname\tpgn\n" + ("\n".join(data_rows) + "\n" if data_rows else ""),
            encoding="utf-8",
            newline="",
        )


def test_valid_batch_replays_deduplicates_and_preserves_empty_names_and_transpositions(
    tmp_path: Path,
) -> None:
    routes = load_opening_sources(_copy_fixture(tmp_path))

    assert len(routes) == 5
    assert [(route.eco, route.name) for route in routes] == [
        ("A00", "Basic route"),
        ("A00", "Transposing route"),
        ("A00", "Transposing route"),
        ("A01", ""),
        ("B00", "Other route"),
    ]
    assert routes[0].moves_uci == (
        "e2e4",
        "e7e5",
        "g1f3",
        "b8c6",
    )
    assert routes[1].moves_uci != routes[2].moves_uci
    assert routes[1].endpoint_key == routes[2].endpoint_key
    assert routes[0].endpoint_fen.endswith(" 2 3")
    assert isinstance(routes[0].endpoint_position, object)


def test_result_is_immutable_and_does_not_retain_a_board(tmp_path: Path) -> None:
    route = load_opening_sources(_copy_fixture(tmp_path))[0]

    assert isinstance(route, OpeningRouteSource)
    assert not hasattr(route, "board")
    assert isinstance(route.moves_uci, tuple)
    with pytest.raises(FrozenInstanceError):
        route.name = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        route.moves_uci[0] = "a1a2"  # type: ignore[index]


def test_reordered_rows_and_files_produce_the_same_deterministic_result(tmp_path: Path) -> None:
    first = _copy_fixture(tmp_path / "first")
    second = tmp_path / "second" / "sources"
    second.parent.mkdir()
    _write_batch(
        second,
        {
            "a.tsv": ["B00\tOther route\t1. e4 c6", "A00\tTransposing route\t1. e4 e5 2. Nf3 a6 3. Bb5 Nc6"],
            "b.tsv": ["A01\t\t1. d4 d5"],
            "c.tsv": ["A00\tBasic route\t1. e4 e5 2. Nf3 Nc6 *"],
            "d.tsv": ["A00\tTransposing route\t1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"],
            "e.tsv": ["A00\tBasic route\t1. e4 e5 2. Nf3 Nc6"],
        },
    )

    assert load_opening_sources(first) == load_opening_sources(second)


@pytest.mark.parametrize(
    ("description", "mutate"),
    [
        ("missing source", lambda path: (path / "e.tsv").unlink()),
        (
            "additional source",
            lambda path: (path / "f.tsv").write_text(
                "eco\tname\tpgn\nA00\tExtra\t1. e4\n", encoding="utf-8"
            ),
        ),
        (
            "wrong header",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tmoves\nA00\tName\t1. e4\n", encoding="utf-8"
            ),
        ),
        (
            "extra field",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\tName\t1. e4\textra\n", encoding="utf-8"
            ),
        ),
        (
            "malformed TSV",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\t\"unterminated\t1. e4\n", encoding="utf-8"
            ),
        ),
        (
            "invalid ECO",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nZ00\tName\t1. e4\n", encoding="utf-8"
            ),
        ),
        (
            "empty move text",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\tName\t   \n", encoding="utf-8"
            ),
        ),
        (
            "parse error",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\tName\t1. e4 Nonsense\n", encoding="utf-8"
            ),
        ),
        (
            "trailing invalid text",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\tName\t1. e4 e5 1-0 trailing\n", encoding="utf-8"
            ),
        ),
        (
            "illegal replay",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\tName\t1. e5 e4\n", encoding="utf-8"
            ),
        ),
        (
            "incomplete input",
            lambda path: (path / "a.tsv").write_text(
                "eco\tname\tpgn\nA00\tName\t1.\n", encoding="utf-8"
            ),
        ),
        (
            "malformed encoding",
            lambda path: (path / "a.tsv").write_bytes(
                b"eco\tname\tpgn\nA00\tName\t1. e4\xff\n"
            ),
        ),
    ],
)
def test_invalid_batch_raises_source_error_without_returning_partial_result(
    tmp_path: Path, description: str, mutate: object
) -> None:
    source_dir = _copy_fixture(tmp_path)
    mutate(source_dir)  # type: ignore[operator]

    with pytest.raises(OpeningSourceError, match=""):
        load_opening_sources(source_dir)


def test_non_directory_source_is_rejected(tmp_path: Path) -> None:
    source_path = tmp_path / "not-a-directory"
    source_path.write_text("", encoding="utf-8")

    with pytest.raises(OpeningSourceError):
        load_opening_sources(source_path)


def test_standard_start_and_legal_replay_are_required(tmp_path: Path) -> None:
    source_dir = _copy_fixture(tmp_path)
    (source_dir / "a.tsv").write_text(
        'eco\tname\tpgn\nA00\tName\t[SetUp "1"]\n[FEN "8/8/8/8/8/8/4k3/4K3 w - - 0 1"]\n\n1. e4\n',
        encoding="utf-8",
    )

    with pytest.raises(OpeningSourceError):
        load_opening_sources(source_dir)


def test_valid_capture_is_normalized_to_uci(tmp_path: Path) -> None:
    source_dir = tmp_path / "capture"
    _write_batch(
        source_dir,
        {
            name: ["A00\tCapture\t1. e4 d5 2. exd5"]
            if name == "a.tsv"
            else []
            for name in EXPECTED_FILES
        },
    )

    routes = load_opening_sources(source_dir)

    assert routes[0].moves_uci[-1] == "e4d5"
