import hashlib
import io
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

from scripts.chess_com import extract_corpus

SUBJECT_UUID = extract_corpus.DEFAULT_SUBJECT


def source_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE players (
            uuid TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            profile_url TEXT
        );
        CREATE TABLE games (
            uuid TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            pgn TEXT NOT NULL,
            time_control TEXT NOT NULL,
            end_time INTEGER NOT NULL,
            rated INTEGER,
            tcn TEXT,
            initial_setup TEXT,
            fen TEXT,
            time_class TEXT,
            rules TEXT,
            eco TEXT,
            white_player_uuid TEXT NOT NULL,
            black_player_uuid TEXT NOT NULL,
            FOREIGN KEY (white_player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (black_player_uuid) REFERENCES players(uuid)
        );
        CREATE TABLE fetch_state (
            username TEXT NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            etag TEXT,
            last_fetched TEXT,
            is_current INTEGER NOT NULL,
            PRIMARY KEY (username, year, month)
        );
        """
    )


def connection(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def corpus_counts(db: sqlite3.Connection) -> tuple[int, int, int]:
    return tuple(
        db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in ("corpus_game", "position_state", "position_occurrence")
    )


FIXTURE_IDS = ("standard", "custom", "shortened", "enpassant")
STANDARD_PGN = """[Event \"fixture\"]
[Result \"*\"]

1. e4 e5 2. Nf3 *
"""
STANDARD_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
CUSTOM_PGN = """[Event \"fixture\"]
[SetUp \"1\"]
[FEN \"4k3/8/8/8/8/8/8/4K2R w - - 3 7\"]
[Result \"*\"]

1. Rh2 *
"""
CUSTOM_FEN = "4k3/8/8/8/8/8/7R/4K3 b - - 4 7"
SHORTENED_PGN = """[Event \"fixture\"]
[Result \"*\"]

1. e4 e5 *
"""
SHORTENED_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6"
ENPASSANT_PGN = """[Event \"fixture\"]
[Result \"*\"]

1. a4 *
"""
ENPASSANT_FEN = "rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1"
UPDATED_PGN = """[Event \"fixture\"]
[Result \"*\"]

1. d4 d5 *
"""
UPDATED_FEN = "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 2"


def fixture_database(path: Path) -> int:
    with connection(path) as db:
        source_schema(db)
        db.executemany(
            "INSERT INTO players (uuid, username, profile_url) VALUES (?, ?, ?)",
            [(SUBJECT_UUID, "skyrocoster", None), ("opponent", "opponent", None)],
        )
        extract_corpus.ensure_corpus_schema(db)
        corpus_id = db.execute(
            "INSERT INTO corpus (subject_player_uuid) VALUES (?)", (SUBJECT_UUID,)
        ).lastrowid
        db.commit()
    assert corpus_id is not None
    return corpus_id


def seed_game(
    db: sqlite3.Connection,
    game_uuid: str,
    pgn: str,
    fen: str,
    initial_setup: str | None = None,
) -> None:
    db.execute(
        "INSERT INTO games "
        "(uuid, url, pgn, time_control, end_time, rated, tcn, initial_setup, fen, "
        "time_class, rules, eco, white_player_uuid, black_player_uuid) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            game_uuid,
            f"https://example.test/{game_uuid}",
            pgn,
            "600",
            0,
            1,
            None,
            initial_setup,
            fen,
            "rapid",
            "chess",
            "A00",
            SUBJECT_UUID,
            "opponent",
        ),
    )


def seed_all_fixtures(db: sqlite3.Connection) -> None:
    seed_game(db, "standard", STANDARD_PGN, STANDARD_FEN)
    seed_game(db, "custom", CUSTOM_PGN, CUSTOM_FEN, "1")
    seed_game(db, "shortened", SHORTENED_PGN, SHORTENED_FEN)
    seed_game(db, "enpassant", ENPASSANT_PGN, ENPASSANT_FEN)
    db.commit()


def persisted_fixture_bytes(db: sqlite3.Connection) -> bytes:
    rows = {
        "corpus_game": db.execute(
            "SELECT corpus_id, game_uuid, rules, fingerprint FROM corpus_game ORDER BY game_uuid"
        ).fetchall(),
        "position_state": db.execute(
            "SELECT state_id, placement, side_to_move, castling, en_passant "
            "FROM position_state ORDER BY state_id"
        ).fetchall(),
        "position_occurrence": db.execute(
            "SELECT game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number "
            "FROM position_occurrence ORDER BY game_uuid, ply"
        ).fetchall(),
    }
    return json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fixture_payload_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_replay_fixture_classes_and_lossless_persistence(tmp_path: Path) -> None:
    db_path = tmp_path / "fixtures.db"
    corpus_id = fixture_database(db_path)

    with connection(db_path) as db:
        seed_all_fixtures(db)
        built: dict[str, list[dict[str, object]]] = {}
        for game_uuid in FIXTURE_IDS:
            occurrences, fingerprint = extract_corpus.replay_game(db, game_uuid)
            built[game_uuid] = occurrences
            assert [item["ply"] for item in occurrences] == list(range(len(occurrences)))
            assert all(len(str(item["fen"]).split()) == 6 for item in occurrences)
            assert occurrences[0]["san"] is None
            assert occurrences[0]["uci"] is None
            assert all(
                item["san"] is not None and item["uci"] is not None for item in occurrences[1:]
            )
            source = db.execute(
                "SELECT pgn, initial_setup, fen, rules FROM games WHERE uuid = ?", (game_uuid,)
            ).fetchone()
            expected_fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "pgn": source[0],
                        "initial_setup": source[1],
                        "fen": source[2],
                        "rules": source[3],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            assert fingerprint == expected_fingerprint

        assert built["standard"][-1]["san"] == "Nf3"
        assert built["standard"][-1]["uci"] == "g1f3"
        assert built["custom"][0]["placement"] == "4k3/8/8/8/8/8/8/4K2R"
        assert built["custom"][-1]["fen"] == CUSTOM_FEN
        assert built["shortened"][-1]["fen"].split()[:4] == SHORTENED_FEN.split()
        assert built["enpassant"][-1]["en_passant"] == "a3"
        assert built["enpassant"][-1]["fen"] == ENPASSANT_FEN

        all_occurrences = [item for game in built.values() for item in game]
        states, linked = extract_corpus.build_states(all_occurrences)
        assert len(linked) == len(all_occurrences)
        assert len(states) < len(linked)
        assert len({state["key"] for state in states}) == len(states)
        assert all(
            item["state_id"]
            == next(state["state_id"] for state in states if state["key"] == item["key"])
            for item in linked
        )

        payload = extract_corpus.persist_fixture(db, corpus_id, FIXTURE_IDS)
        assert payload["states"] == states
        assert corpus_counts(db) == (4, len(states), len(all_occurrences))
        assert db.execute(
            "SELECT san, uci, halfmove_clock, fullmove_number "
            "FROM position_occurrence WHERE game_uuid = 'enpassant' AND ply = 1"
        ).fetchone() == ("a4", "a2a4", 0, 1)


def test_fixture_validation_failure_writes_nothing(tmp_path: Path) -> None:
    db_path = tmp_path / "atomic.db"
    corpus_id = fixture_database(db_path)

    with connection(db_path) as db:
        seed_game(db, "standard", STANDARD_PGN, STANDARD_FEN)
        db.commit()
        extract_corpus.persist_fixture(db, corpus_id, ["standard"])
        before = corpus_counts(db)
        before_membership = db.execute("SELECT COUNT(*) FROM corpus_game").fetchone()[0]

        seed_game(db, "invalid", ENPASSANT_PGN, "8/8/8/8 w - -")
        db.commit()
        with pytest.raises(extract_corpus.ReplayError, match="does not match games.fen"):
            extract_corpus.persist_fixture(db, corpus_id, ["standard", "invalid"])

        assert corpus_counts(db) == before
        assert db.execute("SELECT COUNT(*) FROM corpus_game").fetchone()[0] == before_membership


def test_independent_fixture_builds_are_byte_identical(tmp_path: Path) -> None:
    first_path = tmp_path / "first.db"
    second_path = tmp_path / "second.db"
    first_corpus = fixture_database(first_path)
    second_corpus = fixture_database(second_path)

    with connection(first_path) as first, connection(second_path) as second:
        seed_all_fixtures(first)
        seed_all_fixtures(second)
        first_payload = extract_corpus.build_fixture(first, FIXTURE_IDS)
        second_payload = extract_corpus.build_fixture(second, tuple(reversed(FIXTURE_IDS)))
        assert fixture_payload_bytes(first_payload) == fixture_payload_bytes(second_payload)

        extract_corpus.persist_fixture(first, first_corpus, FIXTURE_IDS)
        extract_corpus.persist_fixture(second, second_corpus, reversed(FIXTURE_IDS))
        assert persisted_fixture_bytes(first) == persisted_fixture_bytes(second)


def test_fresh_database_gets_complete_version_one_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "fresh.db"
    with connection(db_path) as db:
        extract_corpus.ensure_corpus_schema(db)
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND "
                "(name LIKE 'corpus%' OR name LIKE 'position_%')"
            )
        }
        assert tables == {
            "corpus",
            "corpus_game",
            "position_state",
            "position_occurrence",
            "corpus_schema",
            "corpus_run",
        }
        assert db.execute("SELECT version FROM corpus_schema WHERE id=1").fetchone() == (1,)


def test_matching_schema_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "idempotent.db"
    with connection(db_path) as db:
        extract_corpus.ensure_corpus_schema(db)
        extract_corpus.ensure_corpus_schema(db)
        assert db.execute("SELECT COUNT(*) FROM corpus_schema").fetchone() == (1,)


def test_incompatible_schema_is_refused_without_writes(tmp_path: Path) -> None:
    db_path = tmp_path / "incompatible.db"
    with connection(db_path) as db:
        db.execute(
            "CREATE TABLE corpus_schema (id INTEGER PRIMARY KEY CHECK (id = 1), "
            "version INTEGER NOT NULL, applied_at TEXT NOT NULL)"
        )
        db.execute("INSERT INTO corpus_schema VALUES (1, 2, '2026-01-01T00:00:00Z')")
        db.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        db.execute("INSERT INTO sentinel VALUES ('untouched')")
        db.commit()

        with pytest.raises(extract_corpus.CorpusSchemaError, match="version 2"):
            extract_corpus.ensure_corpus_schema(db)

        assert db.execute("SELECT value FROM sentinel").fetchone() == ("untouched",)
        assert (
            db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='corpus'"
            ).fetchone()
            is None
        )
        assert db.execute("SELECT version FROM corpus_schema WHERE id=1").fetchone() == (2,)


def test_init_creates_subject_metadata_and_no_position_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "initialized.db"
    with connection(db_path) as db:
        source_schema(db)
        db.execute("INSERT INTO players VALUES (?, ?, ?)", (SUBJECT_UUID, "skyrocoster", None))
        db.commit()

    extract_corpus.initialize_corpus(db_path, SUBJECT_UUID)
    extract_corpus.initialize_corpus(db_path, SUBJECT_UUID)

    with connection(db_path) as db:
        assert db.execute("SELECT subject_player_uuid FROM corpus").fetchall() == [(SUBJECT_UUID,)]
        assert corpus_counts(db) == (0, 0, 0)
        assert db.execute("SELECT version FROM corpus_schema WHERE id=1").fetchone() == (1,)


def test_init_requires_existing_subject_player_without_writing_position_data(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing-subject.db"
    with connection(db_path) as db:
        source_schema(db)
        db.commit()

    with pytest.raises(sqlite3.IntegrityError):
        extract_corpus.initialize_corpus(db_path, SUBJECT_UUID)

    with connection(db_path) as db:
        assert db.execute("SELECT COUNT(*) FROM corpus").fetchone() == (0,)
        assert corpus_counts(db) == (0, 0, 0)


def test_initial_population_completeness_and_run_history(tmp_path: Path) -> None:
    db_path = tmp_path / "population.db"
    corpus_id = fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        seed_game(db, "oddschess", STANDARD_PGN, STANDARD_FEN)
        db.execute("UPDATE games SET rules = 'oddschess' WHERE uuid = 'oddschess'")
        db.commit()
        output = io.StringIO()
        result = extract_corpus.run_extraction(db, output=output)

        assert result["accepted_games"] == 4
        assert result["excluded_games"] == 1
        assert result["ordered_positions"] == 11
        assert result["unique_states"] == 7
        assert corpus_counts(db) == (4, 7, 11)
        assert db.execute(
            "SELECT COUNT(*) FROM corpus_game WHERE corpus_id = ? AND rules = 'chess'",
            (corpus_id,),
        ).fetchone() == (4,)
        run = db.execute(
            "SELECT status, accepted_games, excluded_games, ordered_positions, unique_states, "
            "validation FROM corpus_run ORDER BY run_id DESC LIMIT 1"
        ).fetchone()
        assert run[:5] == ("success", 4, 1, 11, 7)
        assert "oddschess" in run[5]
        assert "4/4" in output.getvalue()


def test_population_failure_rolls_back_and_records_failed_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "rollback.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        extract_corpus.run_extraction(db, output=io.StringIO())
        before = persisted_fixture_bytes(db)
        original = extract_corpus.replay_game

        def fail_on_standard(connection: sqlite3.Connection, game_uuid: str):
            if game_uuid == "standard":
                raise extract_corpus.ReplayError("forced failure")
            return original(connection, game_uuid)

        monkeypatch.setattr(extract_corpus, "replay_game", fail_on_standard)
        with pytest.raises(extract_corpus.ReplayError, match="forced failure"):
            extract_corpus.run_extraction(db, output=io.StringIO())

        assert persisted_fixture_bytes(db) == before
        assert db.execute(
            "SELECT status, details FROM corpus_run ORDER BY run_id DESC LIMIT 1"
        ).fetchone() == ("failed", "forced failure")


def test_stale_running_row_is_reconciled_before_success(tmp_path: Path) -> None:
    db_path = tmp_path / "stale.db"
    corpus_id = fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        stale_id = extract_corpus.write_run_history(db, corpus_id, "running")
        extract_corpus.run_extraction(db, output=io.StringIO())
        assert db.execute(
            "SELECT status, details FROM corpus_run WHERE run_id = ?", (stale_id,)
        ).fetchone() == ("interrupted", "reconciled before new extraction")


def test_incremental_rerun_leaves_unchanged_rows_and_records_completeness(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "unchanged.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        extract_corpus.run_extraction(db, output=io.StringIO())
        before = persisted_fixture_bytes(db)
        result = extract_corpus.run_extraction(db, output=io.StringIO())

        assert result["new_games"] == 0
        assert result["changed_games"] == 0
        assert result["removed_games"] == 0
        assert result["unchanged_games"] == 4
        assert persisted_fixture_bytes(db) == before
        assert db.execute(
            "SELECT status, unchanged_games, validation FROM corpus_run "
            "ORDER BY run_id DESC LIMIT 1"
        ).fetchone() == ("success", 4, result["validation"])


def test_incremental_new_game_is_added_without_rebuilding_existing_games(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "new.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        extract_corpus.run_extraction(db, output=io.StringIO())
        before = db.execute(
            "SELECT fingerprint FROM corpus_game WHERE game_uuid = 'standard'"
        ).fetchone()
        seed_game(db, "new", STANDARD_PGN, STANDARD_FEN)
        db.commit()

        result = extract_corpus.run_extraction(db, output=io.StringIO())

        assert (result["new_games"], result["changed_games"]) == (1, 0)
        assert result["unchanged_games"] == 4
        assert (
            db.execute(
                "SELECT fingerprint FROM corpus_game WHERE game_uuid = 'standard'"
            ).fetchone()
            == before
        )
        assert db.execute(
            "SELECT COUNT(*) FROM position_occurrence WHERE game_uuid = 'new'"
        ).fetchone() == (4,)


def test_incremental_changed_game_rebuilds_its_global_occurrences(tmp_path: Path) -> None:
    db_path = tmp_path / "changed.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        extract_corpus.run_extraction(db, output=io.StringIO())
        old_fingerprint = db.execute(
            "SELECT fingerprint FROM corpus_game WHERE game_uuid = 'standard'"
        ).fetchone()[0]
        db.execute(
            "UPDATE games SET pgn = ?, fen = ? WHERE uuid = 'standard'",
            (UPDATED_PGN, UPDATED_FEN),
        )
        db.commit()

        result = extract_corpus.run_extraction(db, output=io.StringIO())

        new_fingerprint = db.execute(
            "SELECT fingerprint FROM corpus_game WHERE game_uuid = 'standard'"
        ).fetchone()[0]
        assert result["changed_games"] == 1
        assert result["unchanged_games"] == 3
        assert new_fingerprint != old_fingerprint
        assert db.execute(
            "SELECT san FROM position_occurrence WHERE game_uuid = 'standard' "
            "ORDER BY ply DESC LIMIT 1"
        ).fetchone() == ("d5",)


def test_incremental_removed_and_excluded_games_clean_orphans(tmp_path: Path) -> None:
    db_path = tmp_path / "removed.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        extract_corpus.run_extraction(db, output=io.StringIO())
        db.execute("UPDATE games SET rules = 'oddschess' WHERE uuid = 'standard'")
        db.commit()
        excluded_result = extract_corpus.run_extraction(db, output=io.StringIO())
        assert excluded_result["removed_games"] == 1
        assert db.execute(
            "SELECT COUNT(*) FROM position_occurrence WHERE game_uuid = 'standard'"
        ).fetchone() == (0,)

        db.commit()
        db.execute("PRAGMA foreign_keys = OFF")
        db.execute("DELETE FROM games WHERE uuid = 'custom'")
        db.commit()
        db.execute("PRAGMA foreign_keys = ON")
        removed_result = extract_corpus.run_extraction(db, output=io.StringIO())

        assert removed_result["removed_games"] == 1
        assert db.execute(
            "SELECT COUNT(*) FROM corpus_game WHERE game_uuid IN ('standard', 'custom')"
        ).fetchone() == (0,)
        assert db.execute(
            "SELECT COUNT(*) FROM position_state s LEFT JOIN position_occurrence o "
            "ON o.state_id = s.state_id WHERE o.state_id IS NULL"
        ).fetchone() == (0,)


def test_incremental_removal_preserves_game_global_occurrences_for_other_corpus(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "shared.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_game(db, "standard", STANDARD_PGN, STANDARD_FEN)
        db.execute(
            "INSERT INTO players (uuid, username, profile_url) VALUES (?, ?, ?)",
            ("other-subject", "other", None),
        )
        second_corpus = db.execute(
            "INSERT INTO corpus (subject_player_uuid) VALUES (?)", ("other-subject",)
        ).lastrowid
        fingerprint = extract_corpus.fingerprint_game(db, "standard")
        db.execute(
            "INSERT INTO corpus_game (corpus_id, game_uuid, rules, fingerprint) "
            "VALUES (?, ?, 'chess', ?)",
            (second_corpus, "standard", fingerprint),
        )
        db.commit()
        extract_corpus.run_extraction(db, output=io.StringIO())
        db.execute("UPDATE games SET rules = 'oddschess' WHERE uuid = 'standard'")
        db.commit()

        result = extract_corpus.run_extraction(db, output=io.StringIO())

        assert result["removed_games"] == 1
        assert db.execute(
            "SELECT COUNT(*) FROM corpus_game WHERE corpus_id = ? AND game_uuid = 'standard'",
            (second_corpus,),
        ).fetchone() == (1,)
        assert (
            db.execute(
                "SELECT COUNT(*) FROM position_occurrence WHERE game_uuid = 'standard'"
            ).fetchone()[0]
            > 0
        )


def test_interrupted_incremental_publication_rolls_back_and_records_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "interrupt.db"
    fixture_database(db_path)
    with connection(db_path) as db:
        seed_all_fixtures(db)
        extract_corpus.run_extraction(db, output=io.StringIO())
        before = persisted_fixture_bytes(db)
        seed_game(db, "new", STANDARD_PGN, STANDARD_FEN)
        db.commit()
        original = extract_corpus._persist_game

        def interrupt_on_new(*args: object, **kwargs: object) -> None:
            if args[2] == "new":
                raise KeyboardInterrupt()
            original(*args, **kwargs)

        monkeypatch.setattr(extract_corpus, "_persist_game", interrupt_on_new)
        with pytest.raises(KeyboardInterrupt):
            extract_corpus.run_extraction(db, output=io.StringIO())

        assert persisted_fixture_bytes(db) == before
        assert db.execute(
            "SELECT status, details FROM corpus_run ORDER BY run_id DESC LIMIT 1"
        ).fetchone() == ("interrupted", "KeyboardInterrupt during corpus publication")


def test_busy_database_fails_immediately_with_clear_message(tmp_path: Path) -> None:
    db_path = tmp_path / "busy.db"
    fixture_database(db_path)
    blocker = sqlite3.connect(db_path, timeout=0)
    try:
        blocker.execute("BEGIN EXCLUSIVE")
        with connection(db_path) as db:
            with pytest.raises(
                extract_corpus.CorpusBusyError,
                match=r"database is busy \(concurrent fetch or extraction\); retry later",
            ):
                extract_corpus.run_extraction(db, output=io.StringIO())
    finally:
        blocker.rollback()
        blocker.close()


def test_progress_tty_contains_required_fields() -> None:
    class TTYBuffer(io.StringIO):
        def isatty(self) -> bool:
            return True

    output = TTYBuffer()
    extract_corpus.progress(100, 200, 1234, time.monotonic(), output)
    text = output.getvalue()
    assert "100/200" in text
    assert "50.0%" in text
    assert "positions=1234" in text
    assert "elapsed=" in text
    assert text.startswith("\r")


def test_direct_script_report_uses_public_cli(tmp_path: Path) -> None:
    db_path = tmp_path / "direct-script.db"
    sqlite3.connect(db_path).close()
    script = Path(__file__).resolve().parents[1] / "scripts" / "chess_com" / "extract_corpus.py"

    result = subprocess.run(
        [sys.executable, str(script), "--db", str(db_path), "--report"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "No corpus schema initialized."
