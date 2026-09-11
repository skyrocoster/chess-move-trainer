"""Fixed SQL statements used by direct-database proof helpers."""
from __future__ import annotations

_GAME_READ_STATEMENT = """
    SELECT
        g.dg_game_id,
        g.dg_chesscom_game_uuid,
        g.dg_source_url,
        g.dg_original_pgn,
        g.dg_trainer_color,
        g.dg_trainer_chesscom_uuid,
        g.dg_opponent_chesscom_uuid,
        g.dg_trainer_rating,
        g.dg_opponent_rating,
        g.dg_started_at_utc,
        g.dg_ended_at_utc,
        g.dg_trainer_outcome,
        g.dg_termination_reason,
        g.dg_time_control_source,
        g.dg_time_class,
        o.dgp_ply,
        o.derived_position_id,
        o.dgp_move_uci,
        o.dgp_halfmove_clock,
        o.dgp_fullmove_number,
        p.dp_placement,
        p.dp_side_to_move,
        p.dp_castling_rights,
        p.dp_legal_en_passant
    FROM datasource_game AS g
    LEFT JOIN derived_game_position AS o
      ON o.datasource_game_id = g.dg_game_id
    LEFT JOIN derived_position AS p
      ON p.dp_position_id = o.derived_position_id
    WHERE g.dg_game_id = :game_id
    ORDER BY o.dgp_ply
"""
_POSITION_CONTEXT_STATEMENT = """
    SELECT COUNT(DISTINCT o.datasource_game_id)
    FROM derived_game_position AS o
    JOIN datasource_game AS g
      ON g.dg_game_id = o.datasource_game_id
    WHERE o.derived_position_id = :position_id
      AND (
          :trainer_color IS NULL
          OR g.dg_trainer_color = :trainer_color
      )
"""
_MOVE_RESPONSE_STATEMENT = """
    SELECT o.dgp_move_uci, p.dp_side_to_move, g.dg_trainer_color
    FROM derived_game_position AS o
    JOIN datasource_game AS g
      ON g.dg_game_id = o.datasource_game_id
    JOIN derived_position AS p
      ON p.dp_position_id = o.derived_position_id
    WHERE o.derived_position_id = :position_id
      AND (
          :trainer_color IS NULL
          OR g.dg_trainer_color = :trainer_color
      )
    ORDER BY o.datasource_game_id, o.dgp_ply
"""
_OPENING_ROUTE_STATEMENT = """
    SELECT r.dor_route_id, r.datasource_opening_id,
           r.derived_position_id, o.do_eco, o.do_name,
           p.dp_position_id, p.dp_placement, p.dp_side_to_move,
           p.dp_castling_rights, p.dp_legal_en_passant
    FROM derived_opening_route AS r
    LEFT JOIN datasource_opening AS o
      ON o.do_opening_id = r.datasource_opening_id
    LEFT JOIN derived_position AS p
      ON p.dp_position_id = r.derived_position_id
    ORDER BY r.dor_route_id
"""
_OPENING_ROUTE_MOVE_STATEMENT = """
    SELECT derived_opening_route_id, dorm_ply, dorm_move_uci
    FROM derived_opening_route_move
    ORDER BY derived_opening_route_id, dorm_ply
"""
_PREFERRED_POSITION_STATEMENT = """
    SELECT dp_position_id
    FROM derived_position
    WHERE dp_placement = :placement
      AND dp_side_to_move = :side_to_move
      AND dp_castling_rights = :castling_rights
      AND dp_legal_en_passant = :legal_en_passant
"""
_PREFERRED_SCHEDULE_STATEMENT = """
    SELECT dpm_effective_from, dpm_effective_until, dpm_move_uci
    FROM datasource_preferred_move_period
    WHERE derived_position_id = :position_id
    ORDER BY dpm_effective_from
"""
_ANALYSIS_RESULT_STATEMENT = """
    SELECT derived_position_id, dar_quality,
           dar_configuration_version, dar_settings_json,
           dar_engine_name, dar_engine_version, dar_terminal_kind
    FROM derived_analysis_result
    WHERE derived_position_id = :position_id
    ORDER BY CASE dar_quality
        WHEN 'browser' THEN 0 WHEN 'tool' THEN 1 END
"""
_ANALYSIS_LINE_STATEMENT = """
    SELECT dal_rank, dal_score_kind, dal_score_value,
           dal_wdl_wins, dal_wdl_draws, dal_wdl_losses,
           dal_pv_uci_json, dal_depth
    FROM derived_analysis_line
    WHERE derived_analysis_result_id = :position_id
    ORDER BY dal_rank
"""
_BULK_ROUTE_MOVE_STATEMENT = """
    SELECT r.dor_route_id, m.dorm_ply, m.dorm_move_uci
    FROM derived_opening_route AS r
    LEFT JOIN derived_opening_route_move AS m
      ON m.derived_opening_route_id = r.dor_route_id
    ORDER BY r.dor_route_id, m.dorm_ply
"""
_BULK_GAME_PAGE_FIRST_STATEMENT = """
    WITH game_counts AS (
        SELECT derived_position_id AS position_id,
               COUNT(*) AS occurrence_count
        FROM derived_game_position
        WHERE dgp_ply BETWEEN :min_ply AND :max_ply
        GROUP BY derived_position_id
    )
    SELECT gc.position_id, gc.occurrence_count,
           p.dp_placement, p.dp_side_to_move,
           p.dp_castling_rights, p.dp_legal_en_passant
    FROM game_counts AS gc
    JOIN derived_position AS p
      ON p.dp_position_id = gc.position_id
    ORDER BY gc.occurrence_count DESC, gc.position_id ASC
    LIMIT :page_size
"""
_BULK_GAME_PAGE_CURSOR_STATEMENT = """
    WITH game_counts AS (
        SELECT derived_position_id AS position_id,
               COUNT(*) AS occurrence_count
        FROM derived_game_position
        WHERE dgp_ply BETWEEN :min_ply AND :max_ply
        GROUP BY derived_position_id
    )
    SELECT gc.position_id, gc.occurrence_count,
           p.dp_placement, p.dp_side_to_move,
           p.dp_castling_rights, p.dp_legal_en_passant
    FROM game_counts AS gc
    JOIN derived_position AS p
      ON p.dp_position_id = gc.position_id
    WHERE gc.occurrence_count < :last_frequency
       OR (
           gc.occurrence_count = :last_frequency
           AND gc.position_id > :last_position_id
       )
    ORDER BY gc.occurrence_count DESC, gc.position_id ASC
    LIMIT :page_size
"""
_BULK_ELIGIBILITY_STATEMENT = """
    SELECT dar_quality, dar_configuration_version, dar_engine_version
    FROM derived_analysis_result
    WHERE derived_position_id = :position_id
"""

