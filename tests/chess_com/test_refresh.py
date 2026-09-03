import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import refresh_chess_com as refresh
from scripts.chess_com import fetch_games
from tests.opening_catalog.test_recurrence import open_database, seed_stage2_dependencies


def response(status: int, body: dict, etag: str | None = None) -> fetch_games.Response:
    headers = {"ETag": etag} if etag else {}
    return fetch_games.Response(status, headers, json.dumps(body).encode())


def game(uuid: str = "g1") -> dict:
    return {
        "uuid": uuid,
        "url": f"https://chess.test/{uuid}",
        "pgn": "[Event test]\n\n1. e4 *",
        "time_control": "600",
        "end_time": 1,
        "rated": True,
        "white": {"uuid": "w", "username": "White", "rating": 1200, "result": "win"},
        "black": {
            "uuid": "b",
            "username": "Black",
            "rating": 1100,
            "result": "resigned",
        },
    }


def config(tmp_path: Path) -> refresh.RefreshConfig:
    return refresh.RefreshConfig(
        username="tester",
        subject_uuid="subject",
        database=tmp_path / "games.db",
        engine=tmp_path / "stockfish.exe",
        profile_id=refresh.QUALIFIED_PROFILE,
        workers=1,
        watchdog_seconds=30.0,
        delay=0,
        base_url="https://example.test/pub",
        raw_root=tmp_path / "raw",
        log_path=tmp_path / "fetch.log",
    )


def test_fetch_rerun_inserts_uuid_once_and_is_unchanged(tmp_path: Path) -> None:
    settings = config(tmp_path)
    archive = {"archives": ["https://example.test/pub/player/tester/games/2024/01"]}

    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(200, {"games": [game()]}, "tag")],
    ):
        first = fetch_games.run(
            settings.fetch_settings(),
            fetch_games.configure_logging(settings.log_path),
            sleep=lambda _seconds: None,
        )

    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(304, {})],
    ):
        second = fetch_games.run(
            settings.fetch_settings(),
            fetch_games.configure_logging(settings.log_path),
            sleep=lambda _seconds: None,
        )

    assert first.status == "complete"
    assert first.fetched_months == 1
    assert second.status == "complete"
    assert second.unchanged_months == 1
    with sqlite3.connect(settings.database) as database:
        assert database.execute("SELECT COUNT(*) FROM games WHERE uuid = 'g1'").fetchone()[0] == 1


def test_incomplete_fetch_reports_non_429_month_failure(tmp_path: Path) -> None:
    settings = config(tmp_path)
    archive = {
        "archives": [
            "https://example.test/pub/player/tester/games/2024/01",
            "https://example.test/pub/player/tester/games/2024/02",
        ]
    }
    with patch.object(
        fetch_games,
        "request",
        side_effect=[
            response(200, archive),
            response(500, {}),
            response(200, {"games": [game("g2")]}),
        ],
    ):
        report = refresh.run(settings, logger=fetch_games.configure_logging(settings.log_path))

    assert report.status == "incomplete"
    assert report.exit_code != 0
    assert report.stages[0].metrics["failed_months"] == [
        {"year": 2024, "month": 1, "error": "month returned HTTP 500"}
    ]


def test_fetch_rate_limit_is_fail_fast_and_nonzero(tmp_path: Path) -> None:
    settings = config(tmp_path)
    archive = {
        "archives": [
            "https://example.test/pub/player/tester/games/2024/01",
            "https://example.test/pub/player/tester/games/2024/02",
        ]
    }
    with patch.object(
        fetch_games,
        "request",
        side_effect=[response(200, archive), response(429, {}), response(200, {})],
    ) as requests:
        report = refresh.run(settings, logger=fetch_games.configure_logging(settings.log_path))

    assert report.status == "rate_limited"
    assert report.exit_code != 0
    assert requests.call_count == 2


def test_incomplete_fetch_stops_all_downstream_stages(tmp_path: Path) -> None:
    settings = config(tmp_path)
    calls = Mock()
    failed = fetch_games.FetchResult(
        "incomplete",
        requested_months=1,
        fetched_months=0,
        unchanged_months=0,
        skipped_months=0,
        failed_months=(fetch_games.MonthFailure(2024, 1, "month returned HTTP 500"),),
    )
    hooks = refresh.StageHooks(
        corpus=lambda _config: calls("corpus"),
        s3=lambda _config: calls("s3"),
        s4=lambda _config: calls("s4"),
        analysis=lambda _config: calls("analysis"),
    )

    report = refresh.run(settings, fetcher=lambda _settings, _logger: failed, hooks=hooks)

    assert report.status == "incomplete"
    assert report.exit_code != 0
    calls.assert_not_called()


def test_report_shape_is_serializable(tmp_path: Path) -> None:
    settings = config(tmp_path)
    complete = fetch_games.FetchResult("complete", 0, 0, 0, 0)
    stage = refresh.StageResult("fetch", "complete", metrics=complete.as_dict())
    report = refresh.RefreshReport("complete", (stage,), 0)

    assert report.as_dict() == {
        "status": "complete",
        "exit_code": 0,
        "stages": [
            {
                "name": "fetch",
                "status": "complete",
                "exit_code": 0,
                "details": None,
                "requested_months": 0,
                "fetched_months": 0,
                "unchanged_months": 0,
                "skipped_months": 0,
                "failed_months": [],
            }
        ],
    }


def test_refresh_publishes_accepted_and_excludes_invalid_games_then_reruns_noop(
    tmp_path: Path,
) -> None:
    settings = config(tmp_path)
    with open_database(settings.database) as database:
        seed_stage2_dependencies(database)
        database.execute("UPDATE opening_relationship_state SET position_count = 1")
        database.execute(
            "UPDATE games SET pgn = ?, rules = 'chess' WHERE uuid = 'game-1'",
            ('[Result "*"]\n\n1. a4 *',),
        )
        database.execute(
            "UPDATE games SET pgn = ?, rules = 'oddschess' WHERE uuid = 'game-2'",
            ('[Result "*"]\n\n1. a4 *',),
        )
        database.execute(
            "INSERT INTO games "
            "(uuid, url, pgn, time_control, end_time, rated, tcn, initial_setup, fen, "
            "time_class, rules, eco, white_player_uuid, black_player_uuid, white_rating, "
            "black_rating, white_result, black_result, year, month) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "game-3",
                "url-3",
                '[Result "*"]\n\n1. a4 *',
                "600",
                1700000002,
                1,
                None,
                None,
                None,
                "rapid",
                "chess",
                "A00",
                "subject",
                "opponent",
                1800,
                1790,
                "win",
                "loss",
                2024,
                1,
            ),
        )
        database.commit()

    complete = fetch_games.FetchResult("complete", 0, 0, 0, 0)
    first = refresh.run(settings, fetcher=lambda _settings, _logger: complete)

    assert [stage.name for stage in first.stages] == ["fetch", "corpus", "s3", "s4"]
    assert [stage.status for stage in first.stages] == ["complete", "success", "success", "success"]
    assert first.stages[1].metrics["new_games"] == 1
    assert first.stages[1].metrics["removed_games"] == 1
    assert first.stages[2].metrics["game_count"] == 2
    assert first.stages[3].metrics["game_count"] == 2
    with open_database(settings.database) as database:
        assert database.execute(
            "SELECT game_uuid FROM corpus_game WHERE corpus_id = 7 ORDER BY game_uuid"
        ).fetchall() == [("game-1",), ("game-3",)]
        assert database.execute(
            "SELECT game_uuid FROM opening_classification_game ORDER BY game_uuid"
        ).fetchall() == [("game-1",), ("game-3",)]
        assert database.execute(
            "SELECT game_uuid FROM opening_recurrence_game ORDER BY game_uuid"
        ).fetchall() == [("game-1",), ("game-3",)]
        assert database.execute(
            "SELECT accepted_manifest_hash, corpus_id, game_count "
            "FROM opening_recurrence_state"
        ).fetchone() == ("manifest-stage1", 7, 2)

    second = refresh.run(settings, fetcher=lambda _settings, _logger: complete)

    assert second.status == "complete"
    assert [stage.status for stage in second.stages] == [
        "complete",
        "unchanged",
        "unchanged",
        "unchanged",
    ]


def test_refresh_stops_after_corpus_failure(tmp_path: Path) -> None:
    settings = config(tmp_path)
    calls = Mock()
    complete = fetch_games.FetchResult("complete", 0, 0, 0, 0)
    hooks = refresh.StageHooks(
        corpus=lambda _config: refresh.StageResult("corpus", "failed", 1, "forced corpus failure"),
        s3=lambda _config: calls("s3"),
        s4=lambda _config: calls("s4"),
    )
    with patch.object(refresh, "_validate_prerequisites", return_value=7):
        report = refresh.run(
            settings,
            fetcher=lambda _settings, _logger: complete,
            hooks=hooks,
        )

    assert report.status == "failed"
    assert [stage.name for stage in report.stages] == ["fetch", "corpus"]
    assert report.exit_code != 0
    calls.assert_not_called()
