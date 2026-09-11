from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from chess_move_trainer.database.games.configuration import load_acquire_configuration
from chess_move_trainer.database.games.persistence import load_normalized_months
from chess_move_trainer.database.games.raw_storage import load_month
from chess_move_trainer.database.openings.source import load_opening_sources
from chess_move_trainer.database.positions import canonicalize_board
from chess_move_trainer.database.proof import (
    _board_for_moves,
    _find_transposition_pair,
    collect_direct_capabilities,
)

ROOT = Path(__file__).parents[3]
DIRECT_DATABASE = ROOT / "data/database/chess.db"


def _database() -> Path:
    return Path(os.environ.get("DIRECT_DATABASE", str(DIRECT_DATABASE)))


def test_pinned_source_has_a_bounded_same_side_transposition_pair() -> None:
    routes = load_opening_sources(ROOT / "data/chess-com/openings")

    route, alternate = _find_transposition_pair(routes)

    differing_plies = [
        ply for ply, (source, candidate) in enumerate(zip(route.moves_uci, alternate))
        if source != candidate
    ]
    assert alternate != route.moves_uci
    assert sorted(alternate) == sorted(route.moves_uci)
    assert len(differing_plies) == 2
    assert differing_plies[0] % 2 == differing_plies[1] % 2
    assert canonicalize_board(_board_for_moves(alternate)) == route.endpoint_position


def test_real_direct_database_capabilities() -> None:
    database = _database()
    opening_source = Path(
        os.environ.get(
            "DIRECT_OPENING_DIR",
            str(ROOT / "data/chess-com/openings"),
        )
    )

    capabilities = collect_direct_capabilities(database, opening_source)

    assert capabilities.real_game_metadata_complete
    assert capabilities.real_game_occurrence_count > 1
    assert capabilities.real_game_final_occurrence_present
    assert capabilities.context_all_game_count >= capabilities.context_white_game_count > 0
    assert capabilities.context_all_game_count >= capabilities.context_black_game_count > 0
    assert capabilities.actor_occurrence_count > 0
    assert capabilities.actor_played_occurrence_count > 0
    assert capabilities.actor_final_occurrence_count < capabilities.actor_occurrence_count
    assert capabilities.actor_outgoing_move_kind_count > 0
    assert capabilities.actor_my_choice_count > 0
    assert capabilities.actor_opponent_response_count > 0
    assert capabilities.final_position_final_occurrence_count > 0
    assert capabilities.opening_ordered_recognition_count > 0
    assert capabilities.opening_current_after_departure
    assert capabilities.opening_route_match_proven
    assert capabilities.opening_transposition_match_proven
    assert capabilities.opening_fen_clock_insensitive
    assert capabilities.opening_future_variation_excluded


def test_real_direct_database_matches_the_retained_source_ledger() -> None:
    database = _database()
    raw_root = Path(
        os.environ.get(
            "DIRECT_RAW_ROOT",
            str(ROOT / "data/chess-com/raw"),
        )
    )
    configuration = load_acquire_configuration(
        Path(
            os.environ.get(
                "DIRECT_GAMES_CONFIGURATION",
                str(ROOT / "data/chess-com/direct-games.yaml"),
            )
        )
    )

    normalized = load_normalized_months(
        raw_root,
        configuration.trainer_chesscom_uuid,
    )
    accepted = tuple(item.game for item in normalized if item.game is not None)
    rejected_count = sum(item.game is None for item in normalized)
    source_record_count = len(normalized)
    accepted_by_id: dict[str, str] = {}
    duplicate_normalized_count = 0
    for game in accepted:
        game_uuid = str(game.chesscom_game_uuid)
        if game_uuid in accepted_by_id:
            duplicate_normalized_count += 1
            continue
        accepted_by_id[game_uuid] = game.source_url

    month_paths = sorted(
        (raw_root / "games").glob("[0-9][0-9][0-9][0-9]/[0-9][0-9].json")
    )
    source_months_by_id: dict[str, set[str]] = {}
    for month_path in month_paths:
        month = f"{month_path.parent.name}-{month_path.stem}"
        for raw_game in load_month(month_path)["games"]:
            raw_uuid = raw_game.get("uuid")
            if isinstance(raw_uuid, str) and raw_uuid in accepted_by_id:
                source_months_by_id.setdefault(raw_uuid, set()).add(month)

    duplicate_source_id_count = sum(
        len(months) - 1 for months in source_months_by_id.values() if len(months) > 1
    )
    missing_month_mapping_count = sum(
        game_uuid not in source_months_by_id for game_uuid in accepted_by_id
    )
    source_month_to_ids = {
        month: {
            game_uuid
            for game_uuid, months in source_months_by_id.items()
            if month in months
        }
        for month in {month for months in source_months_by_id.values() for month in months}
    }

    with sqlite3.connect(database) as connection:
        database_rows = connection.execute(
            "SELECT dg_chesscom_game_uuid, dg_source_url FROM datasource_game"
        ).fetchall()
    database_by_id: dict[str, str] = {}
    duplicate_database_count = 0
    for game_uuid, source_url in database_rows:
        normalized_uuid = str(game_uuid)
        if normalized_uuid in database_by_id:
            duplicate_database_count += 1
            continue
        database_by_id[normalized_uuid] = str(source_url)

    assert source_record_count == len(accepted) + rejected_count
    assert rejected_count >= 0
    assert duplicate_normalized_count == 0
    assert duplicate_source_id_count == 0
    assert duplicate_database_count == 0
    assert missing_month_mapping_count == 0
    _assert_same_key_set(accepted_by_id, database_by_id, "source/database game IDs")
    _assert_same_mapping(accepted_by_id, database_by_id, "source/database URLs")

    database_month_to_ids = {
        month: {
            game_uuid
            for game_uuid in database_by_id
            if month in source_months_by_id.get(game_uuid, set())
        }
        for month in source_month_to_ids
    }
    _assert_same_mapping(
        source_month_to_ids,
        database_month_to_ids,
        "source/database month mapping",
    )
    print(
        "source ledger: "
        f"records={source_record_count} accepted={len(accepted)} "
        f"rejected={rejected_count} months={len(source_month_to_ids)} "
        f"database_games={len(database_rows)}"
    )


def _assert_same_key_set(left: dict[str, object], right: dict[str, object], label: str) -> None:
    if set(left) != set(right):
        overlap_count = len(set(left) & set(right))
        raise AssertionError(
            f"{label} mismatch: left_count={len(left)} right_count={len(right)} "
            f"overlap_count={overlap_count}"
        )


def _assert_same_mapping(
    left: dict[str, object], right: dict[str, object], label: str
) -> None:
    if set(left) != set(right):
        _assert_same_key_set(left, right, label)
    mismatch_count = sum(left[key] != right[key] for key in left)
    if mismatch_count:
        raise AssertionError(f"{label} mismatch: mismatch_count={mismatch_count}")
