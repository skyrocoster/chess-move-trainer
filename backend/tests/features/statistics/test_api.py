"""Focused API proof for the statistics overview."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.app.features.statistics.router as router_module
from backend.app.caching import clear_caches
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.reporting import (
    StatisticsOverviewQuery,
    read_statistics_overview,
)

TARGET_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
SHARED_OPPONENT = "99999999-9999-4999-8999-999999999991"


def _insert_game(
    connection: sqlite3.Connection,
    game_id: int,
    *,
    color: str,
    opponent_uuid: str | None,
    outcome: str | None,
    started_at: str | None,
    time_class: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid, dg_opponent_chesscom_uuid,
            dg_trainer_rating, dg_opponent_rating, dg_started_at_utc, dg_ended_at_utc,
            dg_trainer_outcome, dg_termination_reason, dg_time_control_source, dg_time_class
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            f"00000000-0000-4000-8000-{game_id:012d}",
            f"https://example.test/statistics-game-{game_id}",
            '[Result "*"]\n\n*',
            color,
            f"11111111-1111-4111-8111-11111111110{game_id}",
            opponent_uuid,
            1500 + game_id * 10,
            1400 + game_id * 10,
            started_at,
            "2026-03-15T12:30:00Z" if started_at is not None else None,
            outcome,
            "checkmate",
            "180+2" if time_class is not None else None,
            time_class,
        ),
    )


def create_statistics_database(path: Path) -> Path:
    create_schema(path)
    position_id = PositionRepository(path).resolve_fen(TARGET_FEN)
    with sqlite3.connect(path) as connection:
        _insert_game(
            connection,
            1,
            color="white",
            opponent_uuid=SHARED_OPPONENT,
            outcome="win",
            started_at="2026-01-05T10:00:00Z",
            time_class="blitz",
        )
        _insert_game(
            connection,
            2,
            color="black",
            opponent_uuid="88888888-8888-4888-8888-888888888882",
            outcome="loss",
            started_at="2026-02-10T10:00:00Z",
            time_class="rapid",
        )
        _insert_game(
            connection,
            3,
            color="white",
            opponent_uuid=SHARED_OPPONENT,
            outcome="draw",
            started_at="2026-03-15T10:00:00Z",
            time_class="blitz",
        )
        for game_id, move_uci in ((1, "e2e4"), (2, "e7e5"), (3, "e2e4")):
            connection.execute(
                """
                INSERT INTO derived_game_position (
                    datasource_game_id, dgp_ply, derived_position_id,
                    dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
                ) VALUES (?, 1, ?, ?, 0, 1)
                """,
                (game_id, position_id, move_uci),
            )
        opening_id = connection.execute(
            """
            INSERT INTO datasource_opening (do_eco, do_name)
            VALUES ('C20', 'King''s Pawn Game')
            RETURNING do_opening_id
            """
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            (opening_id, position_id),
        )
    return path


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    selected = TestClient(app)
    yield selected
    app.dependency_overrides.clear()


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    clear_caches()
    database = create_statistics_database(tmp_path / "statistics.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    yield client, database
    clear_caches()


def _params(**overrides: str) -> dict[str, str]:
    params: dict[str, str] = {"as_of": "2026-04-01"}
    params.update(overrides)
    return params


def test_successful_overview_matches_core_calculations(api_context) -> None:
    client, database = api_context

    response = client.get("/api/statistics/overview", params=_params())

    assert response.status_code == 200
    body = response.json()
    expected = read_statistics_overview(database, StatisticsOverviewQuery(as_of="2026-04-01"))
    assert body["as_of"] == "2026-04-01"
    assert body["filters"] == {
        "started_on_or_after": None,
        "started_on_or_before": None,
        "trainer_color": None,
        "time_class": None,
    }
    assert set(body) == {
        "as_of",
        "filters",
        "games",
        "activity",
        "openings",
        "opponents",
        "positions",
        "analysis",
        "repertoire",
        "data_quality",
    }
    assert body["games"]["record"] == {
        "total_count": 3,
        "known_outcome_count": 3,
        "win_count": 1,
        "loss_count": 1,
        "draw_count": 1,
        "unknown_count": 0,
        "score_rate": expected.games.record.score_rate,
    }
    assert body["games"]["record"]["score_rate"] == 0.5
    assert body["games"]["by_rating_difference"] == [
        {
            "category": "trainer_50_to_199_higher",
            "record": {
                "total_count": 3,
                "known_outcome_count": 3,
                "win_count": 1,
                "loss_count": 1,
                "draw_count": 1,
                "unknown_count": 0,
                "score_rate": 0.5,
            },
        }
    ]
    assert [entry["category"] for entry in body["games"]["by_length_plies"]] == ["0-19"]
    assert body["games"]["by_length_plies"][0]["record"]["total_count"] == 3
    assert body["games"]["duration_seconds"]["count"] == 3
    assert body["games"]["duration_seconds"]["minimum"] == 9000
    assert body["games"]["trainer_rating_progression"] == {
        "dated_rating_count": 3,
        "first_rating": 1510,
        "last_rating": 1530,
        "change": 20,
        "peak_rating": 1530,
        "lowest_rating": 1510,
    }
    assert body["activity"]["dated_game_count"] == 3
    assert body["activity"]["first_game_at_utc"] == "2026-01-05T10:00:00Z"
    assert body["activity"]["last_game_at_utc"] == "2026-03-15T10:00:00Z"
    assert [entry["hour_utc"] for entry in body["activity"]["by_hour_utc"]] == list(range(24))
    assert body["activity"]["by_hour_utc"][10]["record"]["total_count"] == 3
    assert body["activity"]["by_hour_utc"][0]["record"]["total_count"] == 0
    assert body["openings"]["classified_game_count"] == 3
    assert body["openings"]["openings"][0]["key"] == "C20:King's Pawn Game"
    assert body["openings"]["openings"][0]["average_trainer_rating"] == 1520.0
    assert body["openings"]["openings"][0]["average_length_plies"] == 1.0
    assert body["opponents"]["known_opponent_game_count"] == 3
    assert body["opponents"]["repeat_opponent_count"] == 1
    assert body["opponents"]["opponents"][0]["opponent_chesscom_uuid"] == SHARED_OPPONENT
    assert body["opponents"]["opponents"][0]["average_opponent_rating"] == 1420.0
    assert body["opponents"]["opponents"][0]["average_rating_difference"] == 100.0
    assert body["analysis"]["centipawn_line_count"] == 0
    assert body["analysis"]["mate_line_count"] == 0
    assert body["analysis"]["multi_pv_result_count"] == 0
    assert body["repertoire"]["training_balances"]["missing_count"] == 0
    assert body["data_quality"]["invalid_ended_at_count"] == 0
    assert body["data_quality"]["negative_duration_count"] == 0
    assert body["positions"]["occurrence_count"] == 3
    assert body["positions"]["distinct_game_count"] == 3
    assert body["data_quality"]["missing_outcome_count"] == 0
    assert "game_id" not in json.dumps(body)
    assert "position_id" not in json.dumps(body)
    assert "route_id" not in json.dumps(body)


def test_valid_filters_narrow_the_report(api_context) -> None:
    client, _database = api_context

    white = client.get("/api/statistics/overview", params=_params(trainer_color="white"))
    assert white.status_code == 200
    assert white.json()["games"]["record"]["total_count"] == 2
    assert white.json()["filters"]["trainer_color"] == "white"

    rapid = client.get("/api/statistics/overview", params=_params(time_class="rapid"))
    assert rapid.status_code == 200
    assert rapid.json()["games"]["record"]["total_count"] == 1

    ranged = client.get(
        "/api/statistics/overview",
        params=_params(started_on_or_after="2026-02-01", started_on_or_before="2026-02-28"),
    )
    assert ranged.status_code == 200
    assert ranged.json()["games"]["record"]["total_count"] == 1
    assert ranged.json()["filters"] == {
        "started_on_or_after": "2026-02-01",
        "started_on_or_before": "2026-02-28",
        "trainer_color": None,
        "time_class": None,
    }


@pytest.mark.parametrize(
    "params",
    (
        {"as_of": "2026-9-9"},
        {"as_of": "2026-02-30"},
        {"as_of": "2026-04-01", "trainer_color": "purple"},
        {"as_of": "2026-04-01", "time_class": "correspondence"},
        {
            "as_of": "2026-04-01",
            "started_on_or_after": "2026-03-01",
            "started_on_or_before": "2026-01-01",
        },
        {"as_of": "2026-04-01", "started_on_or_after": "not-a-date"},
    ),
)
def test_invalid_filters_give_clear_error(api_context, params: dict[str, str]) -> None:
    client, _database = api_context

    response = client.get("/api/statistics/overview", params=params)

    assert response.status_code == 422
    assert response.json() == {"code": "invalid_filter", "message": "Invalid statistics filter"}


def test_missing_as_of_is_rejected(api_context) -> None:
    client, _database = api_context

    assert client.get("/api/statistics/overview").status_code == 422


def test_empty_database_returns_stable_zero_shapes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    from chess_move_trainer.database import create_schema as _create_schema

    clear_caches()
    try:
        database = tmp_path / "empty-statistics.db"
        _create_schema(database)
        monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))

        response = client.get("/api/statistics/overview", params=_params())

        assert response.status_code == 200
        body = response.json()
        assert body["games"]["record"] == {
            "total_count": 0,
            "known_outcome_count": 0,
            "win_count": 0,
            "loss_count": 0,
            "draw_count": 0,
            "unknown_count": 0,
            "score_rate": None,
        }
        assert body["games"]["trainer_rating"] == {
            "count": 0,
            "minimum": None,
            "maximum": None,
            "average": None,
            "median": None,
        }
        assert body["games"]["by_rating_difference"] == []
        assert body["games"]["by_length_plies"] == []
        assert body["games"]["duration_seconds"] == {
            "count": 0,
            "minimum": None,
            "maximum": None,
            "average": None,
            "median": None,
        }
        assert body["games"]["trainer_rating_progression"] == {
            "dated_rating_count": 0,
            "first_rating": None,
            "last_rating": None,
            "change": None,
            "peak_rating": None,
            "lowest_rating": None,
        }
        assert body["activity"]["first_game_at_utc"] is None
        assert body["activity"]["last_game_at_utc"] is None
        assert body["activity"]["dated_game_count"] == 0
        assert len(body["activity"]["by_weekday_utc"]) == 7
        assert [entry["hour_utc"] for entry in body["activity"]["by_hour_utc"]] == list(range(24))
        assert all(entry["record"]["total_count"] == 0 for entry in body["activity"]["by_hour_utc"])
        assert [window["requested_game_count"] for window in body["activity"]["recent_form"]] == [
            10,
            25,
            50,
        ]
        assert body["activity"]["streaks"]["current_kind"] is None
        assert body["activity"]["streaks"]["current_count"] == 0
        assert body["openings"]["classified_game_count"] == 0
        assert body["openings"]["openings"] == []
        assert body["opponents"]["opponents"] == []
        assert body["positions"]["occurrence_count"] == 0
        assert body["positions"]["average_occurrences_per_observed_position"] is None
        assert [bucket["label"] for bucket in body["positions"]["ply_buckets"]] == [
            "0-19",
            "20-39",
            "40-59",
            "60+",
        ]
        assert body["positions"]["recurring_positions"] == []
        assert body["analysis"]["scoped_position_count"] == 0
        assert body["analysis"]["ready_coverage_rate"] is None
        assert body["analysis"]["centipawn_line_count"] == 0
        assert body["analysis"]["mate_line_count"] == 0
        assert body["analysis"]["multi_pv_result_count"] == 0
        assert body["repertoire"]["trainer_turn_position_count"] == 0
        assert body["repertoire"]["preferred_move_adherence_rate"] is None
        assert body["repertoire"]["training_balances"]["missing_count"] == 0
        assert body["data_quality"]["invalid_ended_at_count"] == 0
        assert body["data_quality"]["negative_duration_count"] == 0
    finally:
        clear_caches()


def test_missing_or_broken_database_gives_unavailable_without_creating_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    clear_caches()
    try:
        missing = tmp_path / "missing-statistics.db"
        monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
        missing_response = client.get("/api/statistics/overview", params=_params())

        assert missing_response.status_code == 503
        assert missing_response.json() == {
            "code": "statistics_unavailable",
            "message": "Statistics unavailable",
        }
        assert not missing.exists()

        incompatible = tmp_path / "incompatible-statistics.db"
        with sqlite3.connect(incompatible) as connection:
            connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
        before = incompatible.read_bytes()
        monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(incompatible))
        incompatible_response = client.get("/api/statistics/overview", params=_params())

        assert incompatible_response.status_code == 503
        assert incompatible_response.json() == {
            "code": "statistics_unavailable",
            "message": "Statistics unavailable",
        }
        assert incompatible.read_bytes() == before
    finally:
        clear_caches()


def test_unexpected_failures_stay_safe_without_leaking_details(
    api_context, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "read_statistics_overview", fail)
    response = client.get("/api/statistics/overview", params=_params())

    assert response.status_code == 500
    assert response.json() == {"code": "unexpected_failure", "message": "Unable to load statistics"}
    assert "database secret" not in response.text


def test_route_uses_expected_operation_name() -> None:
    operation = app.openapi()["paths"]["/api/statistics/overview"]["get"]

    assert operation["operationId"] == "getStatisticsOverview"
    assert "statistics" in operation.get("tags", [])


def test_repeated_requests_read_the_core_once(api_context, monkeypatch: pytest.MonkeyPatch) -> None:
    client, _database = api_context
    clear_caches()
    try:
        original = router_module.read_statistics_overview
        calls: list[tuple[tuple, dict]] = []

        def wrapper(*args: object, **kwargs: object):
            calls.append((args, kwargs))
            return original(*args, **kwargs)

        monkeypatch.setattr(router_module, "read_statistics_overview", wrapper)

        first = client.get("/api/statistics/overview", params=_params())
        second = client.get("/api/statistics/overview", params=_params())

        assert first.status_code == second.status_code == 200
        assert len(calls) == 1
        assert first.content == second.content
    finally:
        clear_caches()
