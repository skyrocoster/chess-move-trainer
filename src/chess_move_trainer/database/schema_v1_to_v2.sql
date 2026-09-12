CREATE TABLE derived_position_training_aggregate (
    derived_position_id INTEGER NOT NULL,
    dpta_preferred_move_uci TEXT NOT NULL,
    dpta_training_balance REAL NOT NULL,
    dpta_updated_on TEXT,
    PRIMARY KEY (derived_position_id, dpta_preferred_move_uci),
    FOREIGN KEY (derived_position_id) REFERENCES derived_position(dp_position_id) ON DELETE RESTRICT,
    CHECK (dpta_preferred_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dpta_preferred_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]'),
    CHECK (
        typeof(dpta_training_balance) = 'real'
        AND dpta_training_balance = dpta_training_balance
        AND dpta_training_balance BETWEEN -1.7976931348623157e+308 AND 1.7976931348623157e+308
    ),
    CHECK (
        dpta_updated_on IS NULL OR (
            typeof(dpta_updated_on) = 'text'
            AND dpta_updated_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
            AND date(dpta_updated_on) IS NOT NULL
            AND dpta_updated_on = date(dpta_updated_on)
        )
    )
);

PRAGMA user_version = 2;
