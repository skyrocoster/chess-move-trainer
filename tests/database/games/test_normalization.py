from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from chess_move_trainer.database.games.normalization import normalize_game


FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_trainer_white_maps_exact_pgn_and_all_authority_metadata() -> None:
    raw = _fixture("game-trainer-white.json")

    result = normalize_game(raw, TRAINER_UUID)

    assert result.warning is None
    assert result.game is not None
    game = result.game
    assert game.chesscom_game_uuid == UUID("dddddddd-dddd-4ddd-8ddd-ddddddddddd1")
    assert game.source_url == "https://www.chess.com/game/live/synthetic-white"
    assert game.original_pgn == raw["pgn"]
    assert game.trainer_color == "white"
    assert game.trainer_chesscom_uuid == TRAINER_UUID
    assert game.opponent_chesscom_uuid == UUID("99999999-9999-4999-8999-999999999991")
    assert game.trainer_rating == 1500
    assert game.opponent_rating == 1490
    assert game.started_at_utc == "2026-08-01T12:00:00Z"
    assert game.ended_at_utc == "2026-08-01T12:04:00Z"
    assert game.trainer_outcome == "win"
    assert game.termination_reason == "resigned"
    assert game.time_control_source == "300+5"
    assert game.time_class == "blitz"


def test_trainer_black_maps_color_outcome_and_opponent_termination() -> None:
    result = normalize_game(_fixture("game-trainer-black.json"), TRAINER_UUID)

    assert result.game is not None
    assert result.game.trainer_color == "black"
    assert result.game.trainer_outcome == "win"
    assert result.game.termination_reason == "checkmated"


def test_trainer_loss_uses_trainers_termination_bearing_result() -> None:
    raw = _fixture("game-trainer-white.json")
    raw["white"] = {"uuid": str(TRAINER_UUID), "result": "timeout"}
    raw["black"] = {
        "uuid": "99999999-9999-4999-8999-999999999991",
        "result": "win",
    }
    raw["pgn"] = '[Event "Synthetic trainer loss"]\n[Result "0-1"]\n\n1. e4 e5 0-1'

    result = normalize_game(raw, TRAINER_UUID)

    assert result.game is not None
    assert result.game.trainer_outcome == "loss"
    assert result.game.termination_reason == "timeout"


def test_nullable_metadata_remains_nullable_without_rejecting_game() -> None:
    result = normalize_game(_fixture("game-nullable-metadata.json"), TRAINER_UUID)

    assert result.game is not None
    game = result.game
    assert game.opponent_chesscom_uuid is None
    assert game.trainer_rating is None
    assert game.opponent_rating is None
    assert game.started_at_utc is None
    assert game.ended_at_utc is None
    assert game.trainer_outcome is None
    assert game.termination_reason is None
    assert game.time_control_source is None
    assert game.time_class is None


def test_numeric_end_time_wins_and_start_uses_approved_pgn_fallback() -> None:
    raw = _fixture("game-trainer-white.json")
    raw["pgn"] = (
        '[Event "Synthetic timestamp mapping"]\n'
        '[Date "2026.07.30"]\n[StartTime "09:08:07"]\n'
        '[EndDate "1999.01.01"]\n[EndTime "01:02:03"]\n[Result "1-0"]\n\n'
        "1. e4 e5 1-0"
    )

    result = normalize_game(raw, TRAINER_UUID)

    assert result.game is not None
    assert result.game.started_at_utc == "2026-07-30T09:08:07Z"
    assert result.game.ended_at_utc == "2026-08-01T12:04:00Z"


def test_draw_mapping_and_pgn_termination_fallback() -> None:
    draw = normalize_game(_fixture("game-repetition-counters.json"), TRAINER_UUID)
    fallback_raw = _fixture("game-trainer-white.json")
    fallback_raw["white"] = {"uuid": str(TRAINER_UUID), "result": "unknown"}
    fallback_raw["black"] = {
        "uuid": "99999999-9999-4999-8999-999999999991",
        "result": "unknown",
    }
    fallback_raw["pgn"] = (
        '[Event "Synthetic termination fallback"]\n[Termination "adjudication"]\n'
        '[Result "*"]\n\n1. e4 *'
    )
    fallback = normalize_game(fallback_raw, TRAINER_UUID)

    assert draw.game is not None
    assert draw.game.trainer_outcome == "draw"
    assert draw.game.termination_reason == "repetition"
    assert fallback.game is not None
    assert fallback.game.trainer_outcome is None
    assert fallback.game.termination_reason == "adjudication"


@pytest.mark.parametrize(
    ("fixture_name", "reason"),
    [
        ("game-non-standard.json", "non-standard"),
        ("game-trainer-absent.json", "trainer"),
        ("game-malformed-pgn.json", "PGN"),
        ("game-illegal-pgn.json", "PGN"),
    ],
)
def test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(
    fixture_name: str, reason: str
) -> None:
    result = normalize_game(_fixture(fixture_name), TRAINER_UUID)

    assert result.game is None
    assert result.warning is not None
    assert reason.lower() in result.warning.message.lower()


def test_non_unique_trainer_and_non_normal_start_are_skipped() -> None:
    non_unique = _fixture("game-trainer-white.json")
    non_unique["black"] = {"uuid": str(TRAINER_UUID), "result": "win"}
    custom_start = _fixture("game-trainer-white.json")
    custom_start["pgn"] = (
        '[Event "Synthetic custom start"]\n[SetUp "1"]\n'
        '[FEN "8/8/8/8/8/8/4k3/4K3 w - - 0 1"]\n[Result "*"]\n\n*'
    )

    duplicate_result = normalize_game(non_unique, TRAINER_UUID)
    custom_result = normalize_game(custom_start, TRAINER_UUID)

    assert duplicate_result.game is None
    assert duplicate_result.warning is not None
    assert "exactly one" in duplicate_result.warning.message
    assert custom_result.game is None
    assert custom_result.warning is not None
    assert "normal starting" in custom_result.warning.message


@pytest.mark.parametrize(
    "change",
    [
        {"uuid": "not-a-uuid"},
        {"pgn": 7},
        {"url": None},
    ],
)
def test_invalid_required_raw_fields_are_skipped(change: dict[str, object]) -> None:
    raw = _fixture("game-trainer-white.json")
    raw.update(change)

    result = normalize_game(raw, TRAINER_UUID)

    assert result.game is None
    assert result.warning is not None
