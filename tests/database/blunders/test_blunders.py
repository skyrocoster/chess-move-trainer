from __future__ import annotations

import json
import sqlite3
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.blunders import (
    BlunderPolicy,
    BlunderQuery,
    BlunderRepository,
    BlunderSchemaError,
    BlunderStorageError,
    BlunderValidationError,
    discover_blunders,
)
from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.games.persistence import GameRepository
from chess_move_trainer.database.games.reading import GameReadRepository
from chess_move_trainer.database.stockfish import BROWSER_PROFILE, TOOL_PROFILE

TRAINER_UUID = "11111111-1111-4111-8111-111111111111"
OPPONENT_UUID = "99999999-9999-4999-8999-999999999991"

RANGE_FROM = "2026-01-01T00:00:00Z"
RANGE_TO = "2026-12-31T23:59:59Z"


def _raw_game(
    uuid: str,
    moves: str,
    *,
    trainer_white: bool = True,
    date: str | None = "2026.08.01",
    time: str | None = "12:00:00",
) -> dict[str, object]:
    white_uuid = TRAINER_UUID if trainer_white else OPPONENT_UUID
    black_uuid = OPPONENT_UUID if trainer_white else TRAINER_UUID
    headers = ['[Event "blunder fixture"]']
    if date is not None:
        headers.extend([f'[UTCDate "{date}"]', f'[UTCTime "{time}"]'])
    headers.extend(['[EndDate "2026.08.01"]', '[EndTime "12:30:00"]', '[Result "*"]'])
    return {
        "uuid": uuid,
        "url": f"https://www.chess.com/game/live/{uuid}",
        "rules": "chess",
        "pgn": "\n".join(headers) + f"\n\n{moves} *",
        "white": {"uuid": white_uuid, "rating": 1500, "result": "win"},
        "black": {"uuid": black_uuid, "rating": 1490, "result": "resigned"},
        "time_control": "300+5",
        "time_class": "blitz",
    }


def _seed_game(
    database: Path, raw: dict[str, object]
) -> tuple[int, list[tuple[int, int, str | None]]]:
    normalized = normalize_game(raw, UUID(TRAINER_UUID))
    assert normalized.game is not None, normalized.warning
    game_id = GameRepository(database).persist(normalized.game).game_id
    game = GameReadRepository(database).read(game_id)
    assert game is not None
    occurrences = [
        (occurrence.ply, occurrence.position_id, occurrence.move_uci)
        for occurrence in game.occurrences
    ]
    return game_id, occurrences


def _database(tmp_path: Path, name: str = "blunders.db") -> Path:
    database = tmp_path / name
    create_schema(database)
    return database


def _position_at(occurrences: list[tuple[int, int, str | None]], ply: int) -> int:
    for entry_ply, position_id, _move in occurrences:
        if entry_ply == ply:
            return position_id
    raise AssertionError(f"no occurrence at ply {ply}")


def _add_analysis(
    database: Path,
    position_id: int,
    *,
    quality: str = "browser",
    wins: int | None = None,
    draws: int | None = None,
    losses: int | None = None,
    pv: tuple[str, ...] = ("d2d4",),
    terminal: str | None = None,
) -> None:
    profile = BROWSER_PROFILE if quality == "browser" else TOOL_PROFILE
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_analysis_result
                (derived_position_id, dar_quality, dar_configuration_version,
                 dar_settings_json, dar_engine_name, dar_engine_version,
                 dar_terminal_kind)
            VALUES (?, ?, ?, ?, 'fixture', '1', ?)
            """,
            (
                position_id,
                quality,
                profile.configuration_version,
                json.dumps(dict(profile.settings)),
                terminal,
            ),
        )
        if terminal is None:
            assert wins is not None and draws is not None and losses is not None
            connection.execute(
                """
                INSERT INTO derived_analysis_line
                    (derived_analysis_result_id, dal_rank, dal_score_kind,
                     dal_score_value, dal_wdl_wins, dal_wdl_draws, dal_wdl_losses,
                     dal_pv_uci_json, dal_depth)
                VALUES (?, 1, 'cp', 0, ?, ?, ?, ?, 12)
                """,
                (position_id, wins, draws, losses, f'["{pv[0]}"]'),
            )


def _query(**overrides: object) -> BlunderQuery:
    values: dict[str, object] = {
        "started_at_from": RANGE_FROM,
        "started_at_to": RANGE_TO,
    }
    values.update(overrides)
    return BlunderQuery(**values)  # type: ignore[arg-type]


def test_white_blunder_item_shape_and_scores(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1", "1. e4 e5 2. Nf3 Nc6"),
    )
    before = _position_at(occurrences, 0)
    after = _position_at(occurrences, 1)
    _add_analysis(database, before, wins=800, draws=100, losses=100, pv=("d2d4",))
    _add_analysis(database, after, quality="tool", wins=500, draws=100, losses=400, pv=("e7e5",))

    page = discover_blunders(database, _query(), BlunderPolicy(0.3))

    assert page.total == 1
    assert page.total_pages == 1
    assert page.has_next is False
    assert page.trainer_move_count == 2
    assert page.comparable_move_count == 1
    assert page.skipped_missing_analysis_count == 1
    (item,) = page.items
    assert item.game_uuid == "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1"
    assert item.source_url == "https://www.chess.com/game/live/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1"
    assert item.started_at_utc == "2026-08-01T12:00:00Z"
    assert item.trainer_color == "white"
    assert item.ply == 0
    assert item.fen.endswith("0 1")
    assert len(item.fen.split()) == 6
    assert item.played_move_uci == "e2e4"
    assert item.preferred_move_uci == "d2d4"
    assert item.expected_score_before == 0.85
    assert item.expected_score_after == 0.55
    assert item.expected_score_loss == 0.3
    assert item.before_analysis_quality == "browser"
    assert item.after_analysis_quality == "tool"
    assert {field.name for field in fields(item)} == {
        "game_uuid",
        "source_url",
        "started_at_utc",
        "trainer_color",
        "ply",
        "fen",
        "played_move_uci",
        "preferred_move_uci",
        "expected_score_before",
        "expected_score_after",
        "expected_score_loss",
        "before_analysis_quality",
        "after_analysis_quality",
    }


def test_black_perspective_uses_complement_scores(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game(
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1",
            "1. e4 e5 2. Nf3 Nc6",
            trainer_white=False,
        ),
    )
    before = _position_at(occurrences, 1)
    after = _position_at(occurrences, 2)
    _add_analysis(database, before, wins=200, draws=200, losses=600, pv=("e7e5",))
    _add_analysis(database, after, wins=600, draws=200, losses=200, pv=("g1f3",))

    page = discover_blunders(database, _query(trainer_color="black"), BlunderPolicy(0.3))

    assert page.total == 1
    (item,) = page.items
    assert item.trainer_color == "black"
    assert item.ply == 1
    assert item.played_move_uci == "e7e5"
    assert item.expected_score_before == 0.7
    assert item.expected_score_after == 0.3
    assert item.expected_score_loss == 0.4


def test_exact_threshold_is_included_and_above_is_excluded(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("cccccccc-cccc-4ccc-8ccc-cccccccccccc", "1. e4 e5 2. Nf3 Nc6"),
    )
    _add_analysis(database, _position_at(occurrences, 0), wins=800, draws=100, losses=100)
    _add_analysis(database, _position_at(occurrences, 1), wins=500, draws=100, losses=400)

    assert discover_blunders(database, _query(), BlunderPolicy(0.3)).total == 1
    assert discover_blunders(database, _query(), BlunderPolicy(0.300001)).total == 0


def test_timeframe_filtering_is_inclusive_and_normalized(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _seed_game(
        database,
        _raw_game("dddddddd-dddd-4ddd-8ddd-ddddddddddd1", "1. e4 e5", date="2026.08.01"),
    )
    _seed_game(
        database,
        _raw_game("dddddddd-dddd-4ddd-8ddd-ddddddddddd2", "1. e4 e5", date="2026.08.05"),
    )

    page = discover_blunders(
        database,
        BlunderQuery(
            started_at_from="2026-08-01T14:00:00+02:00",
            started_at_to="2026-08-01T12:00:00Z",
        ),
        BlunderPolicy(0.2),
    )

    assert page.started_at_from == "2026-08-01T12:00:00.000000Z"
    assert page.started_at_to == "2026-08-01T12:00:00.000000Z"
    assert page.in_scope_game_count == 1
    assert page.examined_game_count == 2
    assert page.excluded_game_count == 0


def test_datetime_bounds_are_normalized_to_utc(tmp_path: Path) -> None:
    database = _database(tmp_path)
    query = BlunderQuery(
        started_at_from=datetime(2026, 8, 1, 14, 0, tzinfo=timezone.utc),
        started_at_to=datetime(2026, 8, 2, 14, 0, tzinfo=timezone.utc),
    )
    assert query.started_at_from == "2026-08-01T14:00:00.000000Z"
    assert query.started_at_to == "2026-08-02T14:00:00.000000Z"
    page = BlunderRepository(database).discover(query, BlunderPolicy(0.2))
    assert page.total == 0


@pytest.mark.parametrize(
    "values",
    [
        {"started_at_from": None, "started_at_to": RANGE_TO},
        {"started_at_from": RANGE_FROM, "started_at_to": None},
        {"started_at_from": "not-a-time", "started_at_to": RANGE_TO},
        {"started_at_from": "2026-08-02T00:00:00Z", "started_at_to": RANGE_FROM},
        {"started_at_from": RANGE_TO, "started_at_to": RANGE_FROM},
        {"trainer_color": "green"},
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
    ],
)
def test_query_validation(values: dict[str, object]) -> None:
    merged: dict[str, object] = {
        "started_at_from": RANGE_FROM,
        "started_at_to": RANGE_TO,
    }
    merged.update(values)
    with pytest.raises(BlunderValidationError):
        BlunderQuery(**merged)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "threshold", [0, -0.1, 1.5, float("nan"), float("inf"), "high", None, True]
)
def test_policy_validation(threshold: object) -> None:
    with pytest.raises(BlunderValidationError):
        BlunderPolicy(threshold)  # type: ignore[arg-type]


def test_repository_rejects_wrong_types(tmp_path: Path) -> None:
    database = _database(tmp_path)
    repository = BlunderRepository(database)
    with pytest.raises(BlunderValidationError):
        repository.discover("query", BlunderPolicy(0.2))  # type: ignore[arg-type]
    with pytest.raises(BlunderValidationError):
        repository.discover(_query(), "policy")  # type: ignore[arg-type]


def test_only_trainer_turn_moves_are_counted(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game(
            "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee1",
            "1. e4 e5 2. Nf3 Nc6",
            trainer_white=False,
        ),
    )
    # A huge White-perspective swing fully analyzed on White's own move
    # must be ignored because the trainer plays Black in this game. Only
    # the White pair is analyzed, so neither Black pair is comparable.
    _add_analysis(database, _position_at(occurrences, 0), wins=900, draws=100, losses=0)
    _add_analysis(database, _position_at(occurrences, 1), wins=100, draws=100, losses=800)

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 0
    assert page.trainer_move_count == 2
    assert page.comparable_move_count == 0
    assert page.skipped_missing_analysis_count == 2


def test_missing_analysis_is_skipped_and_counted(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("ffffffff-ffff-4fff-8fff-fffffffffff1", "1. e4 e5 2. Nf3 Nc6"),
    )
    # Before analysis exists but the after-position was never analyzed.
    _add_analysis(database, _position_at(occurrences, 0), wins=800, draws=100, losses=100)

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 0
    assert page.trainer_move_count == 2
    assert page.comparable_move_count == 0
    assert page.skipped_missing_analysis_count == 2


def test_game_without_any_analysis_counts_all_trainer_moves_skipped(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    _seed_game(
        database,
        _raw_game("ffffffff-ffff-4fff-8fff-fffffffffff2", "1. e4 e5"),
    )

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 0
    assert page.trainer_move_count == 1
    assert page.comparable_move_count == 0
    assert page.skipped_missing_analysis_count == 1


def test_terminal_after_positions_use_terminal_scoring(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("11111111-1111-4111-8111-111111111112", "1. e4 e5"),
    )
    _add_analysis(database, _position_at(occurrences, 0), wins=850, draws=100, losses=50)
    _add_analysis(
        database,
        _position_at(occurrences, 1),
        quality="tool",
        terminal="stalemate",
    )

    page = discover_blunders(database, _query(), BlunderPolicy(0.3))

    assert page.total == 1
    (item,) = page.items
    assert item.expected_score_before == 0.9
    assert item.expected_score_after == 0.5
    assert item.expected_score_loss == 0.4
    assert item.after_analysis_quality == "tool"


def test_checkmate_after_follows_side_to_move_loser(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("22222222-2222-4222-8222-222222222222", "1. e4 e5"),
    )
    # After White's opening move Black is to move; checkmate means Black
    # (the side to move) loses, so White's expected score is 1.
    _add_analysis(database, _position_at(occurrences, 0), wins=850, draws=100, losses=50)
    _add_analysis(database, _position_at(occurrences, 1), terminal="checkmate")

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 0
    assert page.comparable_move_count == 1
    assert page.skipped_missing_analysis_count == 0


def test_terminal_before_position_is_skipped(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("33333333-3333-4333-8333-333333333333", "1. e4 e5"),
    )
    _add_analysis(database, _position_at(occurrences, 0), terminal="stalemate")
    _add_analysis(database, _position_at(occurrences, 1), wins=500, draws=200, losses=300)

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 0
    assert page.trainer_move_count == 1
    assert page.comparable_move_count == 0
    assert page.skipped_missing_analysis_count == 1


def _seed_blunder(
    database: Path,
    uuid: str,
    date: str,
    moves: str,
    before_ply: int,
    before_wdl: tuple[int, int, int],
    after_wdl: tuple[int, int, int],
) -> None:
    # Each game uses a distinct opening line so canonical positions (and
    # their shared per-position analysis) never collide across games.
    _game_id, occurrences = _seed_game(database, _raw_game(uuid, moves, date=date))
    # The stored preferred move must be legal in the before position, so
    # reuse the actually played move (always legal there) as the fixture PV.
    played = {ply: move for ply, _position_id, move in occurrences}
    before_pv = played[before_ply]
    assert before_pv is not None
    _add_analysis(
        database,
        _position_at(occurrences, before_ply),
        wins=before_wdl[0],
        draws=before_wdl[1],
        losses=before_wdl[2],
        pv=(before_pv,),
    )
    _add_analysis(
        database,
        _position_at(occurrences, before_ply + 1),
        wins=after_wdl[0],
        draws=after_wdl[1],
        losses=after_wdl[2],
    )


def test_sorting_and_pagination_are_deterministic(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _seed_blunder(
        database,
        "44444444-4444-4444-8444-444444444441",
        "2026.08.01",
        "1. e4 e5 2. Nf3 Nc6",
        2,
        (800, 100, 100),
        (500, 100, 400),
    )
    _seed_blunder(
        database,
        "44444444-4444-4444-8444-444444444442",
        "2026.08.02",
        "1. d4 d5 2. c4 e6",
        2,
        (850, 100, 50),
        (350, 100, 550),
    )
    _seed_blunder(
        database,
        "44444444-4444-4444-8444-444444444443",
        "2026.08.03",
        "1. c4 e5 2. Nc3 Nf6",
        2,
        (800, 200, 0),
        (300, 200, 500),
    )
    policy = BlunderPolicy(0.2)

    first = discover_blunders(database, _query(page_size=2), policy)
    assert first.total == 3
    assert first.total_pages == 2
    assert first.has_next is True
    assert [item.expected_score_loss for item in first.items] == [0.5, 0.5]
    # Tied losses order by later start timestamp first.
    assert [item.game_uuid for item in first.items] == [
        "44444444-4444-4444-8444-444444444443",
        "44444444-4444-4444-8444-444444444442",
    ]

    second = discover_blunders(database, _query(page=2, page_size=2), policy)
    assert second.has_next is False
    assert [item.game_uuid for item in second.items] == ["44444444-4444-4444-8444-444444444441"]


def test_discovery_does_not_mutate_database(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("55555555-5555-4555-8555-555555555555", "1. e4 e5"),
    )
    _add_analysis(database, _position_at(occurrences, 0), wins=800, draws=100, losses=100)
    _add_analysis(database, _position_at(occurrences, 1), wins=500, draws=100, losses=400)
    snapshot = database.read_bytes()

    discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert database.read_bytes() == snapshot


def test_missing_database_reports_storage_error(tmp_path: Path) -> None:
    with pytest.raises(BlunderStorageError):
        discover_blunders(tmp_path / "missing.db", _query(), BlunderPolicy(0.2))


def test_incompatible_database_reports_schema_error(tmp_path: Path) -> None:
    database = tmp_path / "odd.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    with pytest.raises(BlunderSchemaError):
        discover_blunders(database, _query(), BlunderPolicy(0.2))


def test_malformed_timestamps_are_excluded_and_counted(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _seed_game(
        database,
        _raw_game("66666666-6666-4666-8666-666666666661", "1. e4 e5"),
    )
    _seed_game(
        database,
        _raw_game("66666666-6666-4666-8666-666666666662", "1. e4 e5"),
    )
    _seed_game(
        database,
        _raw_game("66666666-6666-4666-8666-666666666663", "1. e4 e5"),
    )
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE datasource_game SET dg_started_at_utc = 'garbage' "
            "WHERE dg_chesscom_game_uuid = '66666666-6666-4666-8666-666666666661'"
        )
        connection.execute(
            "UPDATE datasource_game SET dg_started_at_utc = NULL "
            "WHERE dg_chesscom_game_uuid = '66666666-6666-4666-8666-666666666662'"
        )
        connection.execute(
            "UPDATE datasource_game SET dg_started_at_utc = '2026-08-01T12:00:00' "
            "WHERE dg_chesscom_game_uuid = '66666666-6666-4666-8666-666666666663'"
        )

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 0
    assert page.examined_game_count == 3
    assert page.excluded_game_count == 3
    assert page.in_scope_game_count == 0
    assert page.trainer_move_count == 0


def test_malformed_comparable_row_reports_storage_error(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("77777777-7777-4777-8777-777777777777", "1. e4 e5"),
    )
    before = _position_at(occurrences, 0)
    _add_analysis(database, before, wins=800, draws=100, losses=100)
    _add_analysis(database, _position_at(occurrences, 1), wins=500, draws=100, losses=400)
    with sqlite3.connect(database) as connection:
        # A non-string PV entry keeps the schema JSON CHECK satisfied
        # while breaking the domain preferred-move contract.
        connection.execute(
            "UPDATE derived_analysis_line SET dal_pv_uci_json = '[123]' "
            "WHERE derived_analysis_result_id = ? AND dal_rank = 1",
            (before,),
        )

    with pytest.raises(BlunderStorageError):
        discover_blunders(database, _query(), BlunderPolicy(0.2))


def test_later_ply_fen_preserves_halfmove_and_fullmove(tmp_path: Path) -> None:
    database = _database(tmp_path)
    game_id, occurrences = _seed_game(
        database,
        _raw_game("99999999-9999-4999-8999-999999999993", "1. Nf3 Nc6 2. g3 d5"),
    )
    _add_analysis(
        database,
        _position_at(occurrences, 2),
        wins=800,
        draws=100,
        losses=100,
        pv=("g2g3",),
    )
    _add_analysis(database, _position_at(occurrences, 3), wins=500, draws=100, losses=400)

    page = discover_blunders(database, _query(), BlunderPolicy(0.2))

    assert page.total == 1
    (item,) = page.items
    assert item.ply == 2
    game = GameReadRepository(database).read(game_id)
    assert game is not None
    expected = game.occurrences[2].fen
    assert expected.split()[-2:] != ["0", "1"]
    assert item.fen == expected
    assert len(item.fen.split()) == 6


def test_illegal_preferred_move_reports_storage_error(tmp_path: Path) -> None:
    database = _database(tmp_path)
    _game_id, occurrences = _seed_game(
        database,
        _raw_game("99999999-9999-4999-8999-999999999994", "1. e4 e5"),
    )
    # e2e5 is well-formed UCI but illegal from the start position.
    _add_analysis(
        database,
        _position_at(occurrences, 0),
        wins=800,
        draws=100,
        losses=100,
        pv=("e2e5",),
    )
    _add_analysis(database, _position_at(occurrences, 1), wins=500, draws=100, losses=400)

    with pytest.raises(BlunderStorageError):
        discover_blunders(database, _query(), BlunderPolicy(0.2))


def test_chunked_ids_bounds_in_list_reads() -> None:
    from chess_move_trainer.database.blunders.loaders import _chunked_ids

    ids = set(range(1, 1201))
    chunks = _chunked_ids(ids)

    assert [len(chunk) for chunk in chunks] == [500, 500, 200]
    assert [value for chunk in chunks for value in chunk] == sorted(ids)
    assert _chunked_ids(set()) == []


def test_malformed_consecutive_position_reports_storage_error(tmp_path: Path) -> None:
    database = _database(tmp_path)
    game_id, occurrences = _seed_game(
        database,
        _raw_game("88888888-8888-4888-8888-888888888888", "1. e4 e5 2. Nf3 Nc6"),
    )
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            UPDATE derived_game_position
            SET derived_position_id = ?
            WHERE datasource_game_id = ? AND dgp_ply = 1
            """,
            (_position_at(occurrences, 2), game_id),
        )

    with pytest.raises(BlunderStorageError):
        discover_blunders(database, _query(), BlunderPolicy(0.2))
