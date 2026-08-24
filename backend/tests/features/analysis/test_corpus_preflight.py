from __future__ import annotations

import builtins
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import chess
import pytest

from backend.app.features.analysis import (
    AnalysisProfile,
    AnalysisRepository,
    ProjectionBasis,
    initialize_analysis_schema,
    run_read_only_preflight,
    select_all_positions,
)
from scripts.stockfish_analysis import analyze_positions

SUBJECT = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
GAME_A = "00000000-0000-0000-0000-00000000000a"
GAME_B = "00000000-0000-0000-0000-00000000000b"


def _profile(checksum: str = "a" * 64) -> AnalysisProfile:
    return AnalysisProfile(
        profile_id="mp09-balanced-nodes-v2-200000",
        engine_binary_sha256=checksum,
        engine_name="Stockfish 18 fake",
        engine_version="18-test",
        node_budget=200_000,
        options={"UCI_ShowWDL": True},
    )


def _database(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE games (uuid TEXT PRIMARY KEY);
        CREATE TABLE corpus (
            corpus_id INTEGER PRIMARY KEY, subject_player_uuid TEXT NOT NULL
        );
        CREATE TABLE corpus_game (corpus_id INTEGER NOT NULL, game_uuid TEXT NOT NULL);
        CREATE TABLE position_state (
            state_id INTEGER PRIMARY KEY,
            placement TEXT, side_to_move TEXT, castling TEXT, en_passant TEXT,
            UNIQUE (placement, side_to_move, castling, en_passant)
        );
        CREATE TABLE position_occurrence (
            occurrence_id INTEGER PRIMARY KEY, game_uuid TEXT, ply INTEGER,
            state_id INTEGER, halfmove_clock INTEGER, fullmove_number INTEGER
        );
        """
    )
    connection.execute("INSERT INTO corpus VALUES (1, ?)", (SUBJECT,))
    state_ids: dict[tuple[str, str, str, str], int] = {}
    occurrence_id = 1
    state_id = 1
    for game_uuid, move in ((GAME_A, "e2e4"), (GAME_B, "d2d4")):
        connection.execute("INSERT INTO games VALUES (?)", (game_uuid,))
        connection.execute("INSERT INTO corpus_game VALUES (1, ?)", (game_uuid,))
        board = chess.Board()
        for ply, uci in enumerate((None, move)):
            if uci:
                board.push_uci(uci)
            fields = board.fen(en_passant="fen").split()
            key = tuple(fields[:4])
            if key not in state_ids:
                state_ids[key] = state_id
                connection.execute(
                    "INSERT INTO position_state VALUES (?, ?, ?, ?, ?)",
                    (state_id, *key),
                )
                state_id += 1
            connection.execute(
                "INSERT INTO position_occurrence VALUES (?, ?, ?, ?, ?, ?)",
                (occurrence_id, game_uuid, ply, state_ids[key], int(fields[4]), int(fields[5])),
            )
            occurrence_id += 1
    connection.commit()
    initialize_analysis_schema(connection)
    connection.close()


def _basis() -> ProjectionBasis:
    return ProjectionBasis(Path("benchmark.json"), 3, 2.0, 10.0)


def test_all_selection_deduplicates_and_tie_breaks_by_exact_fen(tmp_path: Path) -> None:
    database = tmp_path / "corpus.db"
    _database(database)
    connection = sqlite3.connect(database)
    try:
        report = select_all_positions(connection, _profile())
    finally:
        connection.close()

    assert report.game_uuids == (GAME_A, GAME_B)
    assert len(report.positions) == 3
    assert report.positions[0].fen == chess.STARTING_FEN
    assert [position.first_occurrence.ply for position in report.positions] == [0, 1, 1]
    assert [position.fen for position in report.positions[1:]] == sorted(
        position.fen for position in report.positions[1:]
    )
    assert report.missing_positions == 3


def test_preflight_counts_projection_and_hash_memory_without_mutation(tmp_path: Path) -> None:
    database = tmp_path / "preflight.db"
    _database(database)
    profile = _profile()
    connection = sqlite3.connect(database)
    try:
        report = select_all_positions(connection, profile)
        AnalysisRepository(connection).publish(_result(profile, report.positions[0].fen))
        AnalysisRepository(connection).publish(_result(_profile("b" * 64), report.positions[1].fen))
    finally:
        connection.close()

    before = database.read_bytes()
    preflight = run_read_only_preflight(database, profile, workers=5, projection_basis=_basis())

    assert preflight.report.already_done == 1
    assert preflight.report.skipped_positions == 1
    assert preflight.report.stale_positions == 1
    assert preflight.report.missing_positions == 1
    assert preflight.total_hash_memory_mib == 640
    assert preflight.projected_duration_seconds == 1.2
    assert preflight.projected_pending_duration_seconds == 0.8
    assert preflight.projected_disk_bytes == 30
    assert preflight.projected_pending_disk_bytes == 20
    assert database.read_bytes() == before
    assert not Path(f"{database.resolve()}.analysis.lock").exists()


def _result(profile: AnalysisProfile, fen: str):
    from backend.tests.features.analysis.test_operator import _result as make_result

    return make_result(profile, fen)


def _patch_cli(monkeypatch, database: Path, profile: AnalysisProfile) -> None:
    monkeypatch.setattr(
        analyze_positions,
        "_profile",
        lambda _args: (profile, SimpleNamespace(executable=database.parent / "unused.exe")),
    )


@pytest.mark.parametrize("response", ["no", "not the phrase"])
def test_confirmation_refusal_and_invalid_input_are_non_mutating(
    tmp_path: Path, monkeypatch, response: str
) -> None:
    database = tmp_path / "refusal.db"
    _database(database)
    before = database.read_bytes()
    _patch_cli(monkeypatch, database, _profile())
    monkeypatch.setattr(builtins, "input", lambda _prompt: response)
    monkeypatch.setattr(
        analyze_positions,
        "run_all_positions",
        lambda *_args, **_kwargs: pytest.fail("full corpus must not run in confirmation tests"),
    )

    assert (
        analyze_positions.main(
            ["--db", str(database), "--engine", "unused.exe", "--all", "--workers", "5"]
        )
        == 1
    )
    assert database.read_bytes() == before
    assert not Path(f"{database.resolve()}.analysis.lock").exists()


def test_confirmation_eof_and_preflight_only_are_non_mutating(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "eof.db"
    _database(database)
    before = database.read_bytes()
    _patch_cli(monkeypatch, database, _profile())

    def eof(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr(builtins, "input", eof)
    monkeypatch.setattr(
        analyze_positions,
        "run_all_positions",
        lambda *_args, **_kwargs: pytest.fail("full corpus must not run after EOF"),
    )
    assert analyze_positions.main(["--db", str(database), "--engine", "unused.exe", "--all"]) == 1
    assert database.read_bytes() == before

    assert (
        analyze_positions.main(
            [
                "--db",
                str(database),
                "--engine",
                "unused.exe",
                "--all",
                "--preflight-only",
                "--workers",
                "5",
            ]
        )
        == 0
    )
    assert database.read_bytes() == before
    assert not Path(f"{database.resolve()}.analysis.lock").exists()


def test_preflight_failure_is_non_mutating(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "bad.db"
    sqlite3.connect(database).close()
    before = database.read_bytes()
    _patch_cli(monkeypatch, database, _profile())
    monkeypatch.setattr(
        analyze_positions,
        "run_all_positions",
        lambda *_args, **_kwargs: pytest.fail("full corpus must not run after preflight failure"),
    )

    assert (
        analyze_positions.main(
            [
                "--db",
                str(database),
                "--engine",
                "unused.exe",
                "--all",
                "--preflight-only",
            ]
        )
        == 1
    )
    assert database.read_bytes() == before
    assert not Path(f"{database.resolve()}.analysis.lock").exists()
