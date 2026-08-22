import sqlite3
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

import backend.app.features.positions.router as positions_router_module
from backend.app.features.positions.repository import (
    PositionRepository,
    open_read_only_connection,
)
from backend.app.main import app

SUBJECT_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
OPPONENT_UUID = "02020202-ce8b-11ee-b2fd-e90263e5548c"
WHITE_GAME_UUID = "11111111-1111-4111-8111-111111111111"
BLACK_GAME_UUID = "22222222-2222-4222-8222-222222222222"
INITIAL_STATE = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    "w",
    "KQkq",
    "-",
    0,
    1,
)
AFTER_E4_STATE = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
    "b",
    "KQkq",
    "e3",
    0,
    1,
)
AFTER_E4_C6_STATE = (
    "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR",
    "w",
    "KQkq",
    "-",
    0,
    2,
)


def create_schema(db: sqlite3.Connection, version: int = 1) -> None:
    db.executescript(
        """
        CREATE TABLE corpus_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        );
        CREATE TABLE corpus (
            corpus_id INTEGER PRIMARY KEY,
            subject_player_uuid TEXT NOT NULL
        );
        CREATE TABLE corpus_game (
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            rules TEXT NOT NULL,
            fingerprint TEXT NOT NULL
        );
        CREATE TABLE games (
            uuid TEXT PRIMARY KEY,
            url TEXT,
            white_player_uuid TEXT NOT NULL,
            black_player_uuid TEXT NOT NULL
        );
        CREATE TABLE position_state (
            state_id INTEGER PRIMARY KEY,
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL,
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL
        );
        CREATE TABLE position_occurrence (
            occurrence_id INTEGER PRIMARY KEY,
            game_uuid TEXT NOT NULL,
            ply INTEGER NOT NULL,
            state_id INTEGER NOT NULL,
            san TEXT NULL,
            halfmove_clock INTEGER NOT NULL,
            fullmove_number INTEGER NOT NULL
        );
        """
    )
    db.execute("INSERT INTO corpus_schema (id, version) VALUES (1, ?)", (version,))
    db.execute(
        "INSERT INTO corpus (corpus_id, subject_player_uuid) VALUES (1, ?)",
        (SUBJECT_UUID,),
    )
    db.execute(
        "INSERT INTO position_state "
        "(state_id, placement, side_to_move, castling, en_passant) "
        "VALUES (?, ?, ?, ?, ?)",
        (1, *INITIAL_STATE[:4]),
    )
    db.execute(
        "INSERT INTO position_state "
        "(state_id, placement, side_to_move, castling, en_passant) "
        "VALUES (?, ?, ?, ?, ?)",
        (2, *AFTER_E4_STATE[:4]),
    )
    db.execute(
        "INSERT INTO position_state "
        "(state_id, placement, side_to_move, castling, en_passant) "
        "VALUES (?, ?, ?, ?, ?)",
        (3, *AFTER_E4_C6_STATE[:4]),
    )


def seed_game(
    db: sqlite3.Connection,
    game_uuid: str,
    white_player_uuid: str,
    black_player_uuid: str,
    source_url: str | None = "https://www.chess.com/game/live/123456789",
) -> None:
    db.execute(
        "INSERT INTO games (uuid, url, white_player_uuid, black_player_uuid) VALUES (?, ?, ?, ?)",
        (game_uuid, source_url, white_player_uuid, black_player_uuid),
    )
    db.execute(
        "INSERT INTO corpus_game (corpus_id, game_uuid, rules, fingerprint) "
        "VALUES (1, ?, 'chess', 'fixture')",
        (game_uuid,),
    )
    db.execute(
        "INSERT INTO position_occurrence "
        "(game_uuid, ply, state_id, san, halfmove_clock, fullmove_number) "
        "VALUES (?, 0, 1, NULL, ?, ?)",
        (game_uuid, INITIAL_STATE[4], INITIAL_STATE[5]),
    )
    db.executemany(
        "INSERT INTO position_occurrence "
        "(game_uuid, ply, state_id, san, halfmove_clock, fullmove_number) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            (game_uuid, 1, 2, "e4", AFTER_E4_STATE[4], AFTER_E4_STATE[5]),
            (game_uuid, 2, 3, "c6", AFTER_E4_C6_STATE[4], AFTER_E4_C6_STATE[5]),
        ),
    )


def fixture_database(
    path: Path,
    *,
    version: int = 1,
    invalid_placement: str | None = None,
    source_url: str | None = "https://www.chess.com/game/live/123456789",
) -> Path:
    with sqlite3.connect(path) as db:
        create_schema(db, version)
        seed_game(db, WHITE_GAME_UUID, SUBJECT_UUID, OPPONENT_UUID, source_url)
        seed_game(db, BLACK_GAME_UUID, OPPONENT_UUID, SUBJECT_UUID, source_url)
        if invalid_placement is not None:
            db.execute(
                "UPDATE position_state SET placement = ? WHERE state_id = 1",
                (invalid_placement,),
            )
    return path


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    ("game_uuid", "subject_color"),
    ((WHITE_GAME_UUID, "white"), (BLACK_GAME_UUID, "black")),
)
def test_position_success_returns_exact_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
    game_uuid: str,
    subject_color: str,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{game_uuid}/positions/0")

    assert response.status_code == 200
    assert response.json() == {
        "game_uuid": game_uuid,
        "ply": 0,
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "subject_color": subject_color,
    }


def test_repository_reads_from_a_read_only_connection(
    tmp_path: Path,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    connection = open_read_only_connection(db_path)
    try:
        result = PositionRepository(connection).get_position(UUID(WHITE_GAME_UUID), 0)
    finally:
        connection.close()

    assert result.fen.endswith(" w KQkq - 0 1")
    assert result.subject_color == "white"


def test_malformed_uuid_and_negative_ply_use_fastapi_validation(
    client: TestClient,
) -> None:
    malformed = client.get("/api/games/not-a-uuid/positions/0")
    negative = client.get(f"/api/games/{WHITE_GAME_UUID}/positions/-1")

    assert malformed.status_code == 422
    assert negative.status_code == 422
    assert "code" not in malformed.json()
    assert "code" not in negative.json()


def test_missing_occurrence_returns_typed_not_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(fixture_database(tmp_path / "corpus.db")))

    response = client.get("/api/games/33333333-3333-4333-8333-333333333333/positions/0")

    assert response.status_code == 404
    assert response.json() == {
        "code": "position_not_found",
        "message": "Position not found",
    }


def test_missing_corpus_is_request_local_and_does_not_affect_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    missing_path = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(missing_path))

    position_response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions/0")
    health_response = client.get("/api/health")

    assert position_response.status_code == 503
    assert position_response.json() == {
        "code": "corpus_unavailable",
        "message": "Corpus unavailable",
    }
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
    assert not missing_path.exists()


def test_default_database_path_is_read_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    monkeypatch.delenv("CHESS_DATABASE_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions/0")

    assert response.status_code == 503
    assert not (tmp_path / "data" / "database" / "chess_games.db").exists()


def test_unsupported_corpus_schema_returns_503(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "unsupported.db", version=2)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions/0")

    assert response.status_code == 503
    assert response.json()["code"] == "corpus_unavailable"
    assert "version" not in response.text


def test_invalid_stored_position_returns_safe_500(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "invalid.db", invalid_placement="not-a-board")
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions/0")

    assert response.status_code == 500
    assert response.json() == {
        "code": "stored_position_invalid",
        "message": "Stored position unavailable",
    }
    assert "not-a-board" not in response.text


def test_unexpected_failure_returns_safe_typed_error(
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    def fail_unexpectedly() -> None:
        raise RuntimeError("database secret")

    monkeypatch.setattr(positions_router_module, "fetch_position", fail_unexpectedly)

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions/0")

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to load position",
    }
    assert "database secret" not in response.text


def test_position_request_does_not_modify_corpus_or_widen_cors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    before = db_path.read_bytes()
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(
        f"/api/games/{WHITE_GAME_UUID}/positions/0",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    assert db_path.read_bytes() == before
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("query", ("", "?ply=0"))
def test_whole_game_success_returns_exact_ordered_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
    query: str,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions{query}")

    assert response.status_code == 200
    assert response.json() == {
        "game_uuid": WHITE_GAME_UUID,
        "initial_ply": 0,
        "subject_color": "white",
        "source_url": "https://www.chess.com/game/live/123456789",
        "positions": [
            {
                "ply": 0,
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "san": None,
            },
            {
                "ply": 1,
                "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
                "san": "e4",
            },
            {
                "ply": 2,
                "fen": "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
                "san": "c6",
            },
        ],
    }


def test_whole_game_success_supports_black_and_initial_pointer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{BLACK_GAME_UUID}/positions?ply=1")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"game_uuid", "initial_ply", "subject_color", "source_url", "positions"}
    assert body["initial_ply"] == 1
    assert body["subject_color"] == "black"
    assert set(body["positions"][0]) == {"ply", "fen", "san"}
    assert [position["ply"] for position in body["positions"]] == [0, 1, 2]


def test_whole_game_out_of_range_and_missing_game_are_typed_not_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(fixture_database(tmp_path / "corpus.db")))

    out_of_range = client.get(f"/api/games/{WHITE_GAME_UUID}/positions?ply=3")
    missing_game = client.get("/api/games/33333333-3333-4333-8333-333333333333/positions")

    assert out_of_range.status_code == 404
    assert out_of_range.json() == {"code": "position_not_found", "message": "Position not found"}
    assert missing_game.status_code == 404
    assert missing_game.json() == {"code": "game_not_found", "message": "Game not found"}


def test_whole_game_negative_query_ply_uses_fastapi_validation(
    client: TestClient,
) -> None:
    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions?ply=-1")

    assert response.status_code == 422
    assert "code" not in response.json()


@pytest.mark.parametrize(
    ("mutation", "parameters"),
    (
        ("DELETE FROM position_occurrence WHERE game_uuid = ? AND ply = 1", (WHITE_GAME_UUID,)),
        (
            "UPDATE position_occurrence SET state_id = 99 WHERE game_uuid = ? AND ply = 1",
            (WHITE_GAME_UUID,),
        ),
        (
            "UPDATE position_state SET placement = 'not-a-board' WHERE state_id = 2",
            (),
        ),
        (
            "UPDATE position_occurrence SET san = 'not-a-move' WHERE game_uuid = ? AND ply = 1",
            (WHITE_GAME_UUID,),
        ),
        (
            "UPDATE games SET black_player_uuid = ? WHERE uuid = ?",
            (SUBJECT_UUID, WHITE_GAME_UUID),
        ),
    ),
)
def test_whole_game_rejects_incomplete_or_invalid_stored_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
    mutation: str,
    parameters: tuple[str, ...],
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    with sqlite3.connect(db_path) as db:
        db.execute(mutation, parameters)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions")

    assert response.status_code == 500
    assert response.json() == {"code": "game_unavailable", "message": "Game unavailable"}
    assert "not-a-board" not in response.text
    assert "not-a-move" not in response.text


def test_whole_game_rejects_duplicate_occurrences(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    with sqlite3.connect(db_path) as db:
        db.execute(
            "INSERT INTO position_occurrence "
            "(game_uuid, ply, state_id, san, halfmove_clock, fullmove_number) "
            "VALUES (?, 1, 2, 'e4', 0, 1)",
            (WHITE_GAME_UUID,),
        )
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions")

    assert response.status_code == 500
    assert response.json()["code"] == "game_unavailable"


@pytest.mark.parametrize(
    ("source_url", "expected"),
    (
        ("https://www.chess.com/game/live/123456789", "https://www.chess.com/game/live/123456789"),
        (
            "https://www.chess.com/game/daily/987654321",
            "https://www.chess.com/game/daily/987654321",
        ),
        ("http://www.chess.com/game/live/123456789", None),
        ("https://chess.com/game/live/123456789", None),
        ("https://www.chess.com/game/live/123456789?unsafe=1", None),
        (None, None),
    ),
)
def test_whole_game_source_attribution_is_safe_or_null(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
    source_url: str | None,
    expected: str | None,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db", source_url=source_url)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions")

    assert response.status_code == 200
    assert response.json()["source_url"] == expected


def test_whole_game_missing_corpus_is_safe_and_health_is_isolated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    missing_path = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(missing_path))

    game_response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions")
    health_response = client.get("/api/health")

    assert game_response.status_code == 503
    assert game_response.json() == {
        "code": "corpus_unavailable",
        "message": "Corpus unavailable",
    }
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
    assert not missing_path.exists()


def test_whole_game_unsupported_schema_is_typed_without_details(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "unsupported.db", version=2)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions")

    assert response.status_code == 503
    assert response.json() == {
        "code": "corpus_unavailable",
        "message": "Corpus unavailable",
    }
    assert "version" not in response.text


def test_whole_game_request_is_read_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    db_path = fixture_database(tmp_path / "corpus.db")
    before = db_path.read_bytes()
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(db_path))

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions?ply=1")

    assert response.status_code == 200
    assert db_path.read_bytes() == before


def test_whole_game_unexpected_failure_is_safe_and_typed(
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    def fail_unexpectedly() -> None:
        raise RuntimeError("database secret")

    monkeypatch.setattr(positions_router_module, "fetch_game", fail_unexpectedly)

    response = client.get(f"/api/games/{WHITE_GAME_UUID}/positions")

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to load game",
    }
    assert "database secret" not in response.text
