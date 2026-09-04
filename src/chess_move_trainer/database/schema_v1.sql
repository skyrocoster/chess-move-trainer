CREATE TABLE datasource_game (
    dg_game_id INTEGER NOT NULL PRIMARY KEY,
    dg_chesscom_game_uuid TEXT NOT NULL UNIQUE,
    dg_source_url TEXT NOT NULL,
    dg_original_pgn TEXT NOT NULL,
    dg_trainer_color TEXT NOT NULL,
    dg_trainer_chesscom_uuid TEXT NOT NULL,
    dg_opponent_chesscom_uuid TEXT,
    dg_trainer_rating INTEGER,
    dg_opponent_rating INTEGER,
    dg_started_at_utc TEXT,
    dg_ended_at_utc TEXT,
    dg_trainer_outcome TEXT,
    dg_termination_reason TEXT,
    dg_time_control_source TEXT,
    dg_time_class TEXT,
    CHECK (dg_trainer_color IN ('white', 'black')),
    CHECK (dg_opponent_chesscom_uuid IS NULL OR dg_opponent_chesscom_uuid <> dg_trainer_chesscom_uuid),
    CHECK (dg_trainer_outcome IN ('win', 'loss', 'draw')),
    CHECK (dg_termination_reason IS NULL OR dg_termination_reason NOT IN ('win', 'loss'))
);

CREATE TABLE derived_position (
    dp_position_id INTEGER NOT NULL PRIMARY KEY,
    dp_placement TEXT NOT NULL,
    dp_side_to_move TEXT NOT NULL,
    dp_castling_rights TEXT NOT NULL,
    dp_legal_en_passant TEXT NOT NULL,
    CHECK (dp_side_to_move IN ('w', 'b')),
    CHECK (dp_castling_rights IN ('-', 'K', 'Q', 'k', 'q', 'KQ', 'Kk', 'Kq', 'Qk', 'Qq', 'kq', 'KQk', 'KQq', 'Kkq', 'Qkq', 'KQkq')),
    CHECK (dp_legal_en_passant = '-' OR dp_legal_en_passant GLOB '[a-h][36]'),
    UNIQUE (dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant)
);

CREATE TABLE derived_game_position (
    datasource_game_id INTEGER NOT NULL,
    dgp_ply INTEGER NOT NULL,
    derived_position_id INTEGER NOT NULL,
    dgp_move_uci TEXT,
    dgp_halfmove_clock INTEGER NOT NULL,
    dgp_fullmove_number INTEGER NOT NULL,
    PRIMARY KEY (datasource_game_id, dgp_ply),
    FOREIGN KEY (datasource_game_id) REFERENCES datasource_game(dg_game_id) ON DELETE RESTRICT,
    FOREIGN KEY (derived_position_id) REFERENCES derived_position(dp_position_id) ON DELETE RESTRICT,
    CHECK (dgp_ply >= 0),
    CHECK (dgp_move_uci IS NULL OR dgp_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dgp_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]'),
    CHECK (dgp_halfmove_clock >= 0),
    CHECK (dgp_fullmove_number >= 1)
);

CREATE TABLE datasource_opening (
    do_opening_id INTEGER NOT NULL PRIMARY KEY,
    do_eco TEXT NOT NULL,
    do_name TEXT NOT NULL,
    CHECK (do_eco GLOB '[A-E][0-9][0-9]'),
    UNIQUE (do_eco, do_name)
);

CREATE TABLE derived_opening_route (
    dor_route_id INTEGER NOT NULL PRIMARY KEY,
    datasource_opening_id INTEGER NOT NULL,
    derived_position_id INTEGER NOT NULL,
    FOREIGN KEY (datasource_opening_id) REFERENCES datasource_opening(do_opening_id) ON DELETE RESTRICT,
    FOREIGN KEY (derived_position_id) REFERENCES derived_position(dp_position_id) ON DELETE RESTRICT
);

CREATE TABLE derived_opening_route_move (
    derived_opening_route_id INTEGER NOT NULL,
    dorm_ply INTEGER NOT NULL,
    dorm_move_uci TEXT NOT NULL,
    PRIMARY KEY (derived_opening_route_id, dorm_ply),
    FOREIGN KEY (derived_opening_route_id) REFERENCES derived_opening_route(dor_route_id) ON DELETE CASCADE,
    CHECK (dorm_ply >= 1),
    CHECK (dorm_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dorm_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]')
);

CREATE TABLE derived_analysis_result (
    derived_position_id INTEGER NOT NULL PRIMARY KEY,
    dar_quality TEXT NOT NULL,
    dar_configuration_version INTEGER NOT NULL,
    dar_settings_json TEXT NOT NULL,
    dar_engine_name TEXT NOT NULL,
    dar_engine_version TEXT NOT NULL,
    dar_terminal_kind TEXT,
    FOREIGN KEY (derived_position_id) REFERENCES derived_position(dp_position_id) ON DELETE RESTRICT,
    CHECK (dar_quality IN ('browser', 'tool')),
    CHECK (dar_configuration_version >= 1),
    CHECK (json_valid(dar_settings_json)),
    CHECK (dar_terminal_kind IS NULL OR dar_terminal_kind IN ('checkmate', 'stalemate', 'insufficient_material'))
);

CREATE TABLE derived_analysis_line (
    derived_analysis_result_id INTEGER NOT NULL,
    dal_rank INTEGER NOT NULL,
    dal_score_kind TEXT NOT NULL,
    dal_score_value INTEGER NOT NULL,
    dal_wdl_wins INTEGER NOT NULL,
    dal_wdl_draws INTEGER NOT NULL,
    dal_wdl_losses INTEGER NOT NULL,
    dal_pv_uci_json TEXT NOT NULL,
    dal_depth INTEGER NOT NULL,
    PRIMARY KEY (derived_analysis_result_id, dal_rank),
    FOREIGN KEY (derived_analysis_result_id) REFERENCES derived_analysis_result(derived_position_id) ON DELETE CASCADE,
    CHECK (dal_rank BETWEEN 1 AND 5),
    CHECK (dal_score_kind IN ('cp', 'mate')),
    CHECK (dal_wdl_wins >= 0),
    CHECK (dal_wdl_draws >= 0),
    CHECK (dal_wdl_losses >= 0),
    CHECK (dal_wdl_wins + dal_wdl_draws + dal_wdl_losses = 1000),
    CHECK (json_valid(dal_pv_uci_json) AND json_type(dal_pv_uci_json) = 'array' AND json_array_length(dal_pv_uci_json) > 0),
    CHECK (dal_depth >= 0)
);

CREATE TABLE derived_analysis_queue (
    derived_position_id INTEGER NOT NULL PRIMARY KEY,
    daq_requested_quality TEXT NOT NULL,
    daq_state TEXT NOT NULL,
    daq_requested_at_utc TEXT NOT NULL,
    daq_claimed_at_utc TEXT,
    daq_claim_token TEXT UNIQUE,
    FOREIGN KEY (derived_position_id) REFERENCES derived_position(dp_position_id) ON DELETE RESTRICT,
    CHECK (daq_requested_quality IN ('browser', 'tool')),
    CHECK (daq_state IN ('queued', 'running')),
    CHECK (
        (daq_state = 'queued' AND daq_claimed_at_utc IS NULL AND daq_claim_token IS NULL)
        OR
        (daq_state = 'running' AND daq_claimed_at_utc IS NOT NULL AND daq_claim_token IS NOT NULL)
    )
);

CREATE TABLE datasource_preferred_move_period (
    derived_position_id INTEGER NOT NULL,
    dpm_effective_from TEXT NOT NULL,
    dpm_effective_until TEXT,
    dpm_move_uci TEXT,
    PRIMARY KEY (derived_position_id, dpm_effective_from),
    FOREIGN KEY (derived_position_id) REFERENCES derived_position(dp_position_id) ON DELETE RESTRICT,
    CHECK (dpm_effective_from GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(dpm_effective_from) IS NOT NULL AND dpm_effective_from = date(dpm_effective_from)),
    CHECK (dpm_effective_until IS NULL OR (dpm_effective_until GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(dpm_effective_until) IS NOT NULL AND dpm_effective_until = date(dpm_effective_until) AND dpm_effective_until > dpm_effective_from)),
    CHECK (dpm_move_uci IS NULL OR dpm_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dpm_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]')
);

PRAGMA user_version = 1;
