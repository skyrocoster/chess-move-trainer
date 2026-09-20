from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.reporting import (
    StatisticsOverviewQuery,
    StatisticsOverviewStorageError,
    StatisticsOverviewValidationError,
    read_statistics_overview,
)

WHITE_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
BLACK_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"
SECOND_BLACK_FEN = "rnbqkbnr/pp1ppppp/8/2p5/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 2"
OPPONENT_A = "99999999-9999-4999-8999-999999999991"
OPPONENT_B = "99999999-9999-4999-8999-999999999992"


def _insert_game(
    connection: sqlite3.Connection,
    game_id: int,
    color: str,
    outcome: str | None,
    started_at: str | None,
    opponent: str | None,
    trainer_rating: int | None,
    opponent_rating: int | None,
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
            f"https://example.test/report-{game_id}",
            '[Result "*"]\n\n*',
            color,
            "11111111-1111-4111-8111-111111111111",
            opponent,
            trainer_rating,
            opponent_rating,
            started_at,
            None if started_at is None else started_at,
            outcome,
            None if outcome is None else "checkmate",
            None if time_class is None else "180+2",
            time_class,
        ),
    )


def _insert_occurrence(
    connection: sqlite3.Connection,
    game_id: int,
    ply: int,
    position_id: int,
    move: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, ?, ?, ?, 0, 1)
        """,
        (game_id, ply, position_id, move),
    )


def _create_report_database(path: Path) -> Path:
    create_schema(path)
    white_position = PositionRepository(path).resolve_fen(WHITE_FEN)
    black_position = PositionRepository(path).resolve_fen(BLACK_FEN)
    second_black_position = PositionRepository(path).resolve_fen(SECOND_BLACK_FEN)
    with sqlite3.connect(path) as connection:
        _insert_game(
            connection,
            1,
            "white",
            "win",
            "2026-01-05T10:00:00Z",
            OPPONENT_A,
            1500,
            1450,
            "blitz",
        )
        _insert_game(
            connection,
            2,
            "white",
            "draw",
            "2026-01-06T10:00:00Z",
            OPPONENT_A,
            1520,
            1520,
            "rapid",
        )
        _insert_game(
            connection,
            3,
            "black",
            "loss",
            "2026-02-01T10:00:00Z",
            OPPONENT_B,
            1490,
            1550,
            "blitz",
        )
        _insert_game(connection, 4, "white", None, None, None, None, None, None)

        _insert_occurrence(connection, 1, 5, white_position, "e2e4")
        _insert_occurrence(connection, 1, 20, black_position, "e7e5")
        _insert_occurrence(connection, 1, 30, white_position, None)
        _insert_occurrence(connection, 2, 5, white_position, "d2d4")
        _insert_occurrence(connection, 3, 65, second_black_position, "c7c5")

        c20 = connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) "
            "VALUES ('C20', 'King''s Pawn Game') RETURNING do_opening_id"
        ).fetchone()[0]
        b20 = connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) "
            "VALUES ('B20', 'Sicilian Defense') RETURNING do_opening_id"
        ).fetchone()[0]
        connection.executemany(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            ((c20, white_position), (c20, black_position), (b20, second_black_position)),
        )

        connection.executemany(
            """
            INSERT INTO derived_analysis_result (
                derived_position_id, dar_quality, dar_configuration_version,
                dar_settings_json, dar_engine_name, dar_engine_version, dar_terminal_kind
            ) VALUES (?, ?, 1, '{}', 'Stockfish', '19', ?)
            """,
            ((white_position, "tool", None), (black_position, "browser", "stalemate")),
        )
        connection.execute(
            """
            INSERT INTO derived_analysis_line (
                derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value,
                dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth
            ) VALUES (?, 1, 'cp', 25, 400, 350, 250, '["e2e4"]', 20)
            """,
            (white_position,),
        )
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state, daq_requested_at_utc
            ) VALUES (?, 'tool', 'queued', '2026-03-01T00:00:00Z')
            """,
            (second_black_position,),
        )

        connection.executemany(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci
            ) VALUES (?, '2026-01-01', NULL, ?)
            """,
            ((white_position, "e2e4"), (second_black_position, "c7c5")),
        )
        connection.executemany(
            """
            INSERT INTO derived_position_training_aggregate (
                derived_position_id, dpta_preferred_move_uci,
                dpta_training_balance, dpta_updated_on
            ) VALUES (?, ?, ?, ?)
            """,
            (
                (white_position, "e2e4", -0.25, "2026-03-01"),
                (second_black_position, "c7c5", 0.5, None),
            ),
        )
    return path


def test_complete_overview_aggregates_every_owned_data_family(tmp_path: Path) -> None:
    database = _create_report_database(tmp_path / "complete-report.db")

    report = read_statistics_overview(database, StatisticsOverviewQuery(as_of="2026-04-01"))

    assert report.games.record.total_count == 4
    assert report.games.record.known_outcome_count == 3
    assert report.games.record.score_rate == 0.5
    assert report.games.trainer_rating.count == 3
    assert report.games.trainer_rating.median == 1500
    assert report.games.rating_difference.minimum == -60
    assert report.games.rating_difference.maximum == 50
    assert report.games.length_plies.maximum == 65
    assert report.games.duration_seconds.count == 3
    assert report.games.duration_seconds.average == 0
    assert report.games.trainer_rating_progression.first_rating == 1500
    assert report.games.trainer_rating_progression.last_rating == 1490
    assert report.games.trainer_rating_progression.change == -10
    assert report.games.trainer_rating_progression.peak_rating == 1520
    assert [item.category for item in report.games.by_time_class] == ["blitz", "rapid", "unknown"]
    assert {item.category for item in report.games.by_rating_difference} == {
        "trainer_50_to_199_higher",
        "within_49",
        "opponent_50_to_199_higher",
        "unknown",
    }
    assert {item.category for item in report.games.by_length_plies} == {"0-19", "20-39", "60+"}

    assert report.activity.first_game_at_utc == "2026-01-05T10:00:00Z"
    assert report.activity.last_game_at_utc == "2026-02-01T10:00:00Z"
    assert [period.period for period in report.activity.by_month] == ["2026-01", "2026-02"]
    assert report.activity.streaks.current_kind == "loss"
    assert report.activity.streaks.longest_unbeaten_count == 2
    assert report.activity.streaks.longest_winless_count == 2
    assert len(report.activity.by_hour_utc) == 24
    assert report.activity.by_hour_utc[10].record.total_count == 3

    assert report.openings.classified_game_count == 3
    assert report.openings.unclassified_game_count == 1
    assert report.openings.distinct_opening_count == 2
    assert report.openings.openings[0].key == "C20:King's Pawn Game"
    assert report.openings.openings[0].record.total_count == 2
    assert report.openings.openings[0].average_trainer_rating == 1510
    assert report.openings.openings[0].average_length_plies == 17.5
    assert report.opponents.known_opponent_game_count == 3
    assert report.opponents.unknown_opponent_game_count == 1
    assert report.opponents.repeat_opponent_count == 1
    assert report.opponents.opponents[0].average_opponent_rating == 1485
    assert report.opponents.opponents[0].average_rating_difference == 25

    assert report.positions.database_position_count == 3
    assert report.positions.observed_position_count == 3
    assert report.positions.occurrence_count == 5
    assert report.positions.outgoing_occurrence_count == 4
    assert report.positions.terminal_occurrence_count == 1
    assert report.positions.trainer_turn_occurrence_count == 4
    assert report.positions.opponent_turn_occurrence_count == 1
    assert report.positions.distinct_outgoing_move_count == 4
    assert report.positions.repeated_position_count == 1
    assert report.positions.average_occurrences_per_observed_position == 1.666667
    assert [bucket.occurrence_count for bucket in report.positions.ply_buckets] == [2, 2, 0, 1]
    assert len(report.positions.recurring_positions) == 1
    assert report.positions.recurring_positions[0].fen == " ".join(
        (*WHITE_FEN.split()[:4], "0", "1")
    )

    assert report.analysis.scoped_position_count == 3
    assert report.analysis.ready_position_count == 2
    assert report.analysis.browser_quality_count == 1
    assert report.analysis.tool_quality_count == 1
    assert report.analysis.terminal_result_count == 1
    assert report.analysis.queued_position_count == 1
    assert report.analysis.not_requested_position_count == 0
    assert report.analysis.line_count == 1
    assert report.analysis.centipawn_line_count == 1
    assert report.analysis.mate_line_count == 0
    assert report.analysis.multi_pv_result_count == 0
    assert report.analysis.average_depth == 20
    assert report.analysis.ready_coverage_rate == 0.666667

    assert report.repertoire.trainer_turn_position_count == 2
    assert report.repertoire.move_preference_position_count == 2
    assert report.repertoire.no_preference_position_count == 0
    assert report.repertoire.unconfigured_position_count == 0
    assert report.repertoire.preference_coverage_rate == 1.0
    assert report.repertoire.preference_observed_position_count == 2
    assert report.repertoire.preferred_move_opportunity_count == 3
    assert report.repertoire.preferred_move_played_count == 2
    assert report.repertoire.preferred_move_adherence_rate == 0.666667
    assert report.repertoire.training_balances.negative_count == 1
    assert report.repertoire.training_balances.positive_count == 1
    assert report.repertoire.training_balances.updated_count == 1
    assert report.repertoire.training_balances.missing_count == 0
    assert report.repertoire.training_balances.summary.average == 0.125

    assert report.data_quality.missing_outcome_count == 1
    assert report.data_quality.missing_started_at_count == 1
    assert report.data_quality.invalid_started_at_count == 0
    assert report.data_quality.invalid_ended_at_count == 0
    assert report.data_quality.negative_duration_count == 0
    assert report.data_quality.missing_opponent_count == 1


def test_filters_scope_games_positions_analysis_and_repertoire_together(tmp_path: Path) -> None:
    database = _create_report_database(tmp_path / "filtered-report.db")

    white = read_statistics_overview(
        database,
        StatisticsOverviewQuery(as_of="2026-04-01", trainer_color="white"),
    )
    january = read_statistics_overview(
        database,
        StatisticsOverviewQuery(
            as_of="2026-04-01",
            started_on_or_after="2026-01-01",
            started_on_or_before="2026-01-31",
        ),
    )
    before_preferences = read_statistics_overview(
        database,
        StatisticsOverviewQuery(as_of="2025-12-31", time_class="blitz"),
    )

    assert white.games.record.total_count == 3
    assert white.positions.occurrence_count == 4
    assert white.positions.observed_position_count == 2
    assert white.analysis.scoped_position_count == 2
    assert white.repertoire.trainer_turn_position_count == 1
    assert white.repertoire.preferred_move_opportunity_count == 2

    assert january.games.record.total_count == 2
    assert january.positions.occurrence_count == 4
    assert january.openings.classified_game_count == 2
    assert january.opponents.distinct_known_opponent_count == 1

    assert before_preferences.games.record.total_count == 2
    assert before_preferences.repertoire.trainer_turn_position_count == 2
    assert before_preferences.repertoire.move_preference_position_count == 0
    assert before_preferences.repertoire.unconfigured_position_count == 2
    assert before_preferences.repertoire.preferred_move_adherence_rate is None


def test_bad_timestamps_are_reported_and_negative_durations_are_excluded(tmp_path: Path) -> None:
    database = _create_report_database(tmp_path / "timestamp-quality.db")
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            UPDATE datasource_game
            SET dg_started_at_utc = 'not-a-timestamp',
                dg_ended_at_utc = 'also-not-a-timestamp'
            WHERE dg_game_id = 4
            """
        )
        connection.execute(
            """
            UPDATE datasource_game
            SET dg_ended_at_utc = '2026-01-31T10:00:00Z'
            WHERE dg_game_id = 3
            """
        )

    report = read_statistics_overview(database, StatisticsOverviewQuery(as_of="2026-04-01"))

    assert report.data_quality.invalid_started_at_count == 1
    assert report.data_quality.invalid_ended_at_count == 1
    assert report.data_quality.negative_duration_count == 1
    assert report.games.duration_seconds.count == 2


def test_overlapping_active_preference_periods_are_rejected(tmp_path: Path) -> None:
    database = _create_report_database(tmp_path / "overlapping-preferences.db")
    white_position = PositionRepository(database).resolve_fen(WHITE_FEN)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci
            ) VALUES (?, '2026-02-01', NULL, 'e2e4')
            """,
            (white_position,),
        )

    with pytest.raises(StatisticsOverviewStorageError, match="schedules overlap"):
        read_statistics_overview(database, StatisticsOverviewQuery(as_of="2026-04-01"))


@pytest.mark.parametrize(
    "values",
    (
        {"as_of": "2026-9-1"},
        {"as_of": "2026-02-30"},
        {"as_of": "2026-04-01", "trainer_color": "green"},
        {"as_of": "2026-04-01", "time_class": "classical"},
        {
            "as_of": "2026-04-01",
            "started_on_or_after": "2026-02-01",
            "started_on_or_before": "2026-01-01",
        },
    ),
)
def test_query_rejects_ambiguous_or_invalid_filters(values: dict[str, str]) -> None:
    with pytest.raises(StatisticsOverviewValidationError):
        StatisticsOverviewQuery(**values)
