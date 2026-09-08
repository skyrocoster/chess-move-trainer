from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from chess_move_trainer.database.analysis import (
    AnalysisResultInput,
    validate_analysis_position,
)
from chess_move_trainer.database.analysis.reading import AnalysisReadRepository
from chess_move_trainer.database.openings.source import load_opening_sources
from chess_move_trainer.database.rebuild.proof import (
    DB09_TABLE_NAMES,
    _board_for_moves,
    _find_transposition_pair,
    collect_db09_direct_capabilities,
    collect_db09_proof,
)
from chess_move_trainer.database.positions import canonicalize_board
from chess_move_trainer.database.positions import CanonicalPosition
from chess_move_trainer.database.stockfish import (
    INITIAL_TECHNICAL_POSITIONS,
    TOOL_PROFILE,
)


ROOT = Path(__file__).parents[3]
CANDIDATE = ROOT / "data/chess-com/rebuild/db-09-neighbour.db.candidate"


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


def test_candidate_integrity_and_empty_preferences() -> None:
    proof = collect_db09_proof(CANDIDATE)

    assert proof.database_path == CANDIDATE.resolve()
    assert proof.exact_ten_table_schema
    assert proof.table_names == DB09_TABLE_NAMES
    assert proof.verification.schema_compatible
    assert proof.verification.user_version == 1
    assert proof.verification.integrity_result == "ok"
    assert proof.verification.foreign_key_errors == ()
    assert proof.verification.replacement_ready
    assert proof.verification.openings_ready
    assert proof.verification.games_ready
    assert proof.verification.opening_count > 0
    assert proof.verification.opening_route_count > 0
    assert proof.verification.opening_move_count > 0
    assert proof.verification.position_count > 0
    assert proof.verification.game_count > 0
    assert proof.verification.game_position_count > 0
    assert proof.game_occurrences_valid
    assert proof.opening_routes_valid
    assert proof.preferences_empty
    assert proof.preference_row_count == 0


def test_real_candidate_direct_capabilities() -> None:
    database = Path(
        os.environ.get(
            "DB09_DATABASE",
            str(CANDIDATE),
        )
    )
    opening_source = Path(
        os.environ.get(
            "DB09_OPENING_DIR",
            str(ROOT / "data/chess-com/openings"),
        )
    )

    capabilities = collect_db09_direct_capabilities(database, opening_source)

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


def test_real_candidate_analysis_reads() -> None:
    database = Path(
        os.environ.get(
            "DB09_DATABASE",
            str(CANDIDATE),
        )
    )
    database_uri = f"file:{database.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(database_uri, uri=True) as connection:
        table_names = tuple(
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )
        )
        rows = connection.execute(
            """
            SELECT result.derived_position_id,
                   position.dp_placement,
                   position.dp_side_to_move,
                   position.dp_castling_rights,
                   position.dp_legal_en_passant
            FROM derived_analysis_result AS result
            JOIN derived_position AS position
              ON position.dp_position_id = result.derived_position_id
            ORDER BY result.derived_position_id
            """
        ).fetchall()
        queue_count = connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_queue"
        ).fetchone()[0]
        preference_count = connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0]

    assert table_names == DB09_TABLE_NAMES
    assert len(rows) >= 25
    assert queue_count == 0
    assert preference_count == 0

    reader = AnalysisReadRepository(database)
    terminal_kinds: set[str] = set()
    for position_id, placement, side_to_move, castling_rights, legal_en_passant in rows:
        position = CanonicalPosition(
            placement=placement,
            side_to_move=side_to_move,
            castling_rights=castling_rights,
            legal_en_passant=legal_en_passant,
        )
        result = reader.read(int(position_id))
        assert result is not None
        assert result.quality is TOOL_PROFILE.quality
        assert result.configuration_version == TOOL_PROFILE.configuration_version
        assert result.settings == dict(TOOL_PROFILE.settings)
        assert result.engine_name == "Stockfish"
        assert result.engine_version == "18"
        validated = validate_analysis_position(
            position,
            AnalysisResultInput(
                quality=result.quality,
                configuration_version=result.configuration_version,
                settings=result.settings,
                engine_name=result.engine_name,
                engine_version=result.engine_version,
                lines=result.lines,
            ),
        )
        assert validated.terminal_kind is result.terminal_kind
        if result.terminal_kind is not None:
            terminal_kinds.add(result.terminal_kind.value)

    assert terminal_kinds == {"checkmate", "stalemate"}

    with sqlite3.connect(database_uri, uri=True) as connection:
        for representative in INITIAL_TECHNICAL_POSITIONS:
            canonical = representative.canonical
            row = connection.execute(
                """
                SELECT dp_position_id
                FROM derived_position
                WHERE dp_placement = ?
                  AND dp_side_to_move = ?
                  AND dp_castling_rights = ?
                  AND dp_legal_en_passant = ?
                """,
                (
                    canonical.placement,
                    canonical.side_to_move,
                    canonical.castling_rights,
                    canonical.legal_en_passant,
                ),
            ).fetchone()
            assert row is not None
            result = reader.read(int(row[0]))
            assert result is not None
            assert result.quality is TOOL_PROFILE.quality
            if representative.category in {"checkmate", "stalemate"}:
                assert result.terminal_kind is not None
                assert result.lines == ()
            else:
                assert result.terminal_kind is None
                assert result.lines
