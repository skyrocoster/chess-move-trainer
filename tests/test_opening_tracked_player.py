from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

from scripts.opening_catalog import (
    CLASSIFICATION_INPUT_TABLES,
    TRACKED_PLAYER_SCHEMA_TABLES,
    TRACKED_PLAYER_SCHEMA_VERSION,
    UPSTREAM_PRESERVATION_TABLES,
    OpeningSchemaError,
    TrackedPlayerContractError,
    TrackedPlayerDerivationError,
    TrackedPlayerPublicationError,
    configured_username,
    derive_tracked_player,
    ensure_tracked_player_schema,
    import_recurrence,
    import_tracked_player,
    publish_tracked_player,
    resolve_tracked_player,
    upstream_preservation_signatures,
)
from scripts.opening_catalog.classification_schema import CLASSIFICATION_SCHEMA_TABLES
from scripts.opening_catalog.recurrence_schema import RECURRENCE_SCHEMA_TABLES
from scripts.opening_catalog.schema import RELATIONSHIP_SCHEMA_TABLES, SCHEMA_TABLES
from scripts.opening_catalog.tracked_player_contract import (
    TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS,
    TRACKED_PLAYER_CLASSIFICATION_IDENTITY_FIELDS,
    TRACKED_PLAYER_POSITION_IDENTITY_FIELDS,
    TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS,
    TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS,
)

PLAYER_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
tracked_contract = sys.modules[resolve_tracked_player.__module__]
tracked_persistence = sys.modules[import_tracked_player.__module__]
FORBIDDEN_COLUMNS = {
    "username",
    "player_id",
    "id",
    "rowid",
    "formula",
    "threshold",
    "weight",
    "priority",
    "frontier",
}


def _recurrence_fixture_module() -> ModuleType:
    path = Path(__file__).with_name("test_opening_recurrence.py")
    spec = importlib.util.spec_from_file_location("_s5_recurrence_fixture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("opening recurrence fixture could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _open_stage1_database(path: Path, *, rich: bool = False) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    fixture = _recurrence_fixture_module()
    seed = fixture.seed_stage3_dependencies if rich else fixture.seed_stage2_dependencies
    seed(connection)
    connection.execute(
        "INSERT INTO players (uuid, username, profile_url) VALUES (?, 'Skyrocoster', NULL)",
        (PLAYER_UUID,),
    )
    connection.execute(
        "UPDATE corpus SET subject_player_uuid = ? WHERE subject_player_uuid = 'subject'",
        (PLAYER_UUID,),
    )
    connection.execute(
        "UPDATE games SET white_player_uuid = ? WHERE white_player_uuid = 'subject'",
        (PLAYER_UUID,),
    )
    connection.execute(
        "UPDATE games SET black_player_uuid = ? WHERE black_player_uuid = 'subject'",
        (PLAYER_UUID,),
    )
    connection.execute("DELETE FROM players WHERE uuid = 'subject'")
    connection.commit()
    assert import_recurrence(connection, fixture.CORPUS_ID).status == "success"
    connection.execute(
        "INSERT INTO opening_classification_run VALUES "
        "('classification-fixture', 'manifest-stage1', 7, 1, 1, 1, "
        "'success', 'before', 'before', 'deterministic neutral classification publication')"
    )
    connection.commit()
    return connection


def _primary_key(connection: sqlite3.Connection, table: str) -> tuple[str, ...]:
    columns = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return tuple(row[1] for row in sorted(columns, key=lambda row: row[5]) if row[5])


def _copy_row(
    connection: sqlite3.Connection,
    table: str,
    replacements: dict[str, object],
    where: str,
    parameters: tuple[object, ...],
) -> None:
    columns = [str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")]
    selected = ["?" if column in replacements else f'"{column}"' for column in columns]
    values = tuple(replacements[column] for column in columns if column in replacements)
    connection.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) "
        f"SELECT {', '.join(selected)} FROM {table} WHERE {where}",
        values + parameters,
    )


def _ordered_rows(connection: sqlite3.Connection, table: str) -> tuple[tuple[object, ...], ...]:
    info = connection.execute(f"PRAGMA table_info({table})").fetchall()
    ordering = ", ".join(str(row[1]) for row in sorted(info, key=lambda row: row[5]) if row[5])
    query = f"SELECT * FROM {table} ORDER BY {ordering}"
    return tuple(tuple(row) for row in connection.execute(query))


def _expected_personal_rows(
    connection: sqlite3.Connection,
) -> tuple[tuple[tuple[object, ...], ...], ...]:
    return (
        tuple(
            row[:3]
            for row in _ordered_rows(connection, "opening_classification_game")
            if row[:2] == ("manifest-stage1", 7)
        ),
        *(
            _ordered_rows(connection, table)
            for table in (
                "opening_recurrence_position_projection",
                "opening_recurrence_route_projection",
                "opening_recurrence_branch_projection",
                "opening_recurrence_route_branch_projection",
            )
        ),
    )


def test_stage1_resolves_configured_username_once_and_requires_corpus_agreement(
    tmp_path: Path,
) -> None:
    config = Path("scripts/chess_com/config.yaml")
    assert configured_username(config) == "skyrocoster"
    with _open_stage1_database(tmp_path / "identity.db") as connection:
        identity = resolve_tracked_player(connection, "sKyRoCoStEr")

        assert identity.player_uuid == PLAYER_UUID
        assert identity.corpus_id == 7
        assert identity.manifest_hash == "manifest-stage1"
        assert identity.classification_schema_version == 1
        assert identity.recurrence_schema_version == 1
        assert len(identity.classification_input_signature) == 64
        assert len(identity.recurrence_input_signature) == 64
        assert "username" not in identity.__dataclass_fields__

        connection.execute("UPDATE corpus SET subject_player_uuid = 'opponent' WHERE corpus_id = 7")
        connection.commit()
        with pytest.raises(TrackedPlayerContractError, match="corpus ownership"):
            resolve_tracked_player(connection, "skyrocoster", 7)


def test_stage1_refuses_missing_ambiguous_or_invalid_configuration(tmp_path: Path) -> None:
    with _open_stage1_database(tmp_path / "resolution.db") as connection:
        with pytest.raises(TrackedPlayerContractError, match="found 0"):
            resolve_tracked_player(connection, "missing")
        connection.execute(
            "INSERT INTO players (uuid, username, profile_url) VALUES "
            "('duplicate-player', 'SKYROCOSTER', NULL)"
        )
        connection.commit()
        with pytest.raises(TrackedPlayerContractError, match="found 2"):
            resolve_tracked_player(connection, "skyrocoster")

    invalid_config = tmp_path / "invalid.yaml"
    invalid_config.write_text("subject_uuid: ignored\n", encoding="utf-8")
    with pytest.raises(TrackedPlayerContractError, match="requires one username"):
        configured_username(invalid_config)


def test_stage1_schema_is_additive_uuid_keyed_natural_and_policy_neutral(tmp_path: Path) -> None:
    with _open_stage1_database(tmp_path / "schema.db") as connection:
        before = upstream_preservation_signatures(connection)

        ensure_tracked_player_schema(connection)

        assert upstream_preservation_signatures(connection) == before
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND (name LIKE 'opening_tracked_player%' OR name LIKE 'opening_player_%')"
            )
        }
        assert names == TRACKED_PLAYER_SCHEMA_TABLES
        assert connection.execute(
            "SELECT version FROM opening_tracked_player_schema WHERE id = 1"
        ).fetchone() == (TRACKED_PLAYER_SCHEMA_VERSION,)
        for table in TRACKED_PLAYER_SCHEMA_TABLES:
            sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE name = ?", (table,)
            ).fetchone()[0]
            assert "WITHOUT ROWID" in sql
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            if table != "opening_tracked_player_schema":
                assert not columns & FORBIDDEN_COLUMNS

        assert _primary_key(connection, "opening_player_classification_game") == (
            TRACKED_PLAYER_CLASSIFICATION_IDENTITY_FIELDS
        )
        assert _primary_key(connection, "opening_player_position_projection") == (
            TRACKED_PLAYER_POSITION_IDENTITY_FIELDS
        )
        assert _primary_key(connection, "opening_player_route_projection") == (
            TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS
        )
        assert _primary_key(connection, "opening_player_branch_projection") == (
            TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS
        )
        assert _primary_key(connection, "opening_player_route_branch_projection") == (
            TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS
        )
        player_foreign_keys = connection.execute(
            "PRAGMA foreign_key_list(opening_tracked_player)"
        ).fetchall()
        assert {(row[2], row[3], row[4]) for row in player_foreign_keys} == {
            ("players", "player_uuid", "uuid")
        }
        connection.execute(
            "INSERT INTO opening_tracked_player (player_uuid) VALUES (?)", (PLAYER_UUID,)
        )
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_stage1_schema_refuses_missing_or_incompatible_prerequisites(tmp_path: Path) -> None:
    with sqlite3.connect(tmp_path / "missing.db") as connection:
        with pytest.raises(Exception, match="accepted corpus, S3, and S4 schemas"):
            ensure_tracked_player_schema(connection)
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name LIKE 'opening_tracked_player%'"
            ).fetchall()
            == []
        )

    with _open_stage1_database(tmp_path / "version.db") as connection:
        connection.execute(
            "CREATE TABLE opening_tracked_player_schema "
            "(id INTEGER PRIMARY KEY CHECK (id = 1), version INTEGER NOT NULL) WITHOUT ROWID"
        )
        connection.execute("INSERT INTO opening_tracked_player_schema VALUES (1, 99)")
        connection.commit()
        with pytest.raises(Exception, match="tracked-player schema version 99"):
            ensure_tracked_player_schema(connection)


def test_stage1_tokens_ignore_timestamps_history_and_raw_fact_mutation(tmp_path: Path) -> None:
    with _open_stage1_database(tmp_path / "signatures.db") as connection:
        before = resolve_tracked_player(connection, "skyrocoster", 7)

        connection.execute(
            "UPDATE opening_classification_run SET details = 'after', started_at = 'after'"
        )
        connection.execute(
            "UPDATE opening_recurrence_run SET details = 'after' WHERE corpus_id = 7"
        )
        connection.commit()
        after_history = resolve_tracked_player(connection, "skyrocoster", 7)
        assert after_history.classification_input_signature == before.classification_input_signature
        assert after_history.recurrence_input_signature == before.recurrence_input_signature

        connection.execute(
            "UPDATE opening_classification_game SET source_fingerprint = 'changed' "
            "WHERE manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.execute(
            "UPDATE opening_recurrence_occurrence SET san = 'changed' "
            "WHERE manifest_hash = 'manifest-stage1' AND corpus_id = 7 AND game_uuid = 'game-1' "
            "AND ply = 1"
        )
        connection.commit()
        after_facts = resolve_tracked_player(connection, "skyrocoster", 7)
        assert after_facts == after_history
        connection.execute("UPDATE opening_classification_run SET run_id = 'accepted-s3-change'")
        connection.commit()
        after_s3 = resolve_tracked_player(connection, "skyrocoster", 7)
        assert after_s3.classification_input_signature != after_facts.classification_input_signature


def test_stage1_selects_and_signs_only_current_authoritative_states(tmp_path: Path) -> None:
    with _open_stage1_database(tmp_path / "authoritative.db") as connection:
        before = resolve_tracked_player(connection, "skyrocoster")
        connection.execute("PRAGMA foreign_keys = OFF")
        for table in ("opening_classification_state", "opening_recurrence_state"):
            _copy_row(
                connection,
                table,
                {"accepted_manifest_hash": "manifest-history"},
                "accepted_manifest_hash = ? AND corpus_id = ?",
                ("manifest-stage1", 7),
            )
        connection.commit()

        after_history = resolve_tracked_player(connection, "skyrocoster")
        assert after_history == before

        _copy_row(
            connection,
            "corpus",
            {"corpus_id": 8, "subject_player_uuid": "opponent"},
            "corpus_id = ?",
            (7,),
        )
        for table in ("opening_classification_state", "opening_recurrence_state"):
            _copy_row(
                connection,
                table,
                {"corpus_id": 8},
                "accepted_manifest_hash = ? AND corpus_id = ?",
                ("manifest-stage1", 7),
            )
        connection.commit()

        after_unrelated = resolve_tracked_player(connection, "skyrocoster", 7)
        assert after_unrelated == before

        connection.execute(
            "UPDATE opening_classification_state SET accepted_at = 'selected-change' "
            "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.execute(
            "UPDATE opening_recurrence_state SET accepted_at = 'selected-change' "
            "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.commit()

        after_selected_change = resolve_tracked_player(connection, "skyrocoster", 7)
        assert (
            after_selected_change.classification_input_signature
            == before.classification_input_signature
        )
        assert after_selected_change.recurrence_input_signature == before.recurrence_input_signature


def test_stage1_preservation_signatures_cover_all_upstream_schema_tables() -> None:
    expected = {
        "players",
        "games",
        "corpus_schema",
        "corpus",
        "corpus_game",
        "corpus_run",
        "position_state",
        "position_occurrence",
    }
    expected |= SCHEMA_TABLES | RELATIONSHIP_SCHEMA_TABLES
    expected |= CLASSIFICATION_SCHEMA_TABLES | RECURRENCE_SCHEMA_TABLES
    assert expected <= set(UPSTREAM_PRESERVATION_TABLES)
    assert set(CLASSIFICATION_INPUT_TABLES) < set(UPSTREAM_PRESERVATION_TABLES)


def test_stage1_existing_schema_rejects_malformed_structure_without_mutation(
    tmp_path: Path,
) -> None:
    with _open_stage1_database(tmp_path / "malformed.db") as connection:
        ensure_tracked_player_schema(connection)
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("DROP TABLE opening_player_position_projection")
        connection.execute("CREATE TABLE opening_player_position_projection (player_uuid TEXT)")
        connection.commit()
        connection.execute("PRAGMA foreign_keys = ON")
        before = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'table' "
            "AND name LIKE 'opening_%' ORDER BY name"
        ).fetchall()

        with pytest.raises(OpeningSchemaError, match="incompatible columns"):
            ensure_tracked_player_schema(connection)

        after = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'table' "
            "AND name LIKE 'opening_%' ORDER BY name"
        ).fetchall()
        assert after == before


def test_stage2_derives_and_atomically_publishes_exact_personal_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with _open_stage1_database(tmp_path / "publication.db") as connection:
        before = upstream_preservation_signatures(connection)
        facts = derive_tracked_player(connection, "sKyRoCoStEr", 7)
        neutral_tables = (
            "opening_recurrence_position_projection",
            "opening_recurrence_route_projection",
            "opening_recurrence_branch_projection",
            "opening_recurrence_route_branch_projection",
        )
        classification_games = tuple(
            connection.execute(
                "SELECT manifest_hash, corpus_id, game_uuid FROM opening_classification_game "
                "WHERE manifest_hash = 'manifest-stage1' AND corpus_id = 7 ORDER BY game_uuid"
            )
        )
        expected = (
            classification_games,
            *tuple(_ordered_rows(connection, table) for table in neutral_tables),
        )
        assert facts.counts == tuple(len(rows) for rows in expected)
        ensure_tracked_player_schema(connection)
        signature_scan = tracked_contract._table_signature
        monkeypatch.setattr(
            tracked_contract,
            "_table_signature",
            lambda *args, **kwargs: pytest.fail("full fact signature scan invoked"),
        )
        statements = []
        connection.set_trace_callback(statements.append)
        first = import_tracked_player(connection, "sKyRoCoStEr", 7)

        assert first.status == "success"
        assert any(
            "INSERT INTO opening_player_route_projection SELECT" in sql for sql in statements
        )
        assert all("opening_recurrence_route_event" not in sql for sql in statements)
        assert first.player_uuid == PLAYER_UUID
        assert connection.execute("SELECT player_uuid FROM opening_tracked_player").fetchall() == [
            (PLAYER_UUID,)
        ]
        personal_tables = (
            "opening_player_position_projection",
            "opening_player_route_projection",
            "opening_player_branch_projection",
            "opening_player_route_branch_projection",
        )
        assert _ordered_rows(connection, "opening_player_classification_game") == tuple(
            (PLAYER_UUID, *row) for row in expected[0]
        )
        for table, rows in zip(personal_tables, expected[1:]):
            assert _ordered_rows(connection, table) == tuple((PLAYER_UUID, *row) for row in rows)
        monkeypatch.setattr(tracked_contract, "_table_signature", signature_scan)
        assert upstream_preservation_signatures(connection) == before
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []

        connection.execute(
            "UPDATE opening_classification_state SET accepted_at = 'later' "
            "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.execute(
            "UPDATE opening_recurrence_state SET accepted_at = 'later' "
            "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.commit()
        statements.clear()
        monkeypatch.setattr(
            tracked_contract,
            "_table_signature",
            lambda *args, **kwargs: pytest.fail("full fact signature scan invoked"),
        )
        second = import_tracked_player(connection, "skyrocoster", 7)
        assert second.status == "unchanged"
        assert all("INSERT INTO opening_player" not in sql for sql in statements)
        assert second.run_id == first.run_id
        assert connection.execute("SELECT COUNT(*) FROM opening_tracked_player_run").fetchone() == (
            1,
        )


def test_stage2_independent_builds_have_stable_run_and_output(tmp_path: Path) -> None:
    receipts = []
    identities = []
    outputs = []
    for name in ("first.db", "second.db"):
        with _open_stage1_database(tmp_path / name) as connection:
            connection.execute(
                "UPDATE opening_classification_state SET accepted_at = ? "
                "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7",
                (name,),
            )
            connection.execute(
                "UPDATE opening_recurrence_state SET accepted_at = ? "
                "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7",
                (name,),
            )
            connection.commit()
            facts = derive_tracked_player(connection, "skyrocoster", 7)
            identities.append(facts.identity)
            receipts.append(publish_tracked_player(connection, facts))
            outputs.append(
                tuple(
                    _ordered_rows(connection, table)
                    for table in (
                        "opening_player_classification_game",
                        "opening_player_position_projection",
                        "opening_player_route_projection",
                        "opening_player_branch_projection",
                        "opening_player_route_branch_projection",
                    )
                )
            )
    assert (
        identities[0].classification_input_signature == identities[1].classification_input_signature
    )
    assert identities[0].recurrence_input_signature == identities[1].recurrence_input_signature
    assert receipts[0].run_id == receipts[1].run_id
    assert outputs[0] == outputs[1]


def test_stage2_refuses_changed_input_after_success_and_preserves_prior_state(
    tmp_path: Path,
) -> None:
    personal_tables = (
        "opening_tracked_player",
        "opening_tracked_player_state",
        "opening_tracked_player_run",
        "opening_player_classification_game",
        "opening_player_position_projection",
        "opening_player_route_projection",
        "opening_player_branch_projection",
        "opening_player_route_branch_projection",
    )
    with _open_stage1_database(tmp_path / "changed-after-success.db") as connection:
        first = import_tracked_player(connection, "skyrocoster", 7)
        before = {table: _ordered_rows(connection, table) for table in personal_tables}

        connection.execute(
            "UPDATE opening_recurrence_state SET game_metadata_input_signature = 'accepted-change' "
            "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.execute(
            "UPDATE opening_recurrence_run SET game_metadata_input_signature = 'accepted-change' "
            "WHERE manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.commit()
        upstream_after_input = upstream_preservation_signatures(connection)

        with pytest.raises(TrackedPlayerPublicationError, match="incompatible accepted inputs"):
            import_tracked_player(connection, "skyrocoster", 7)

        assert first.status == "success"
        assert {table: _ordered_rows(connection, table) for table in personal_tables} == before
        assert upstream_preservation_signatures(connection) == upstream_after_input


def test_stage2_refuses_changed_or_incompatible_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with _open_stage1_database(tmp_path / "changed.db") as connection:
        facts = derive_tracked_player(connection, "skyrocoster", 7)
        original = tracked_persistence._resolved_tracked_player

        def change_after_precheck(*args: object, **kwargs: object):
            identity = original(*args, **kwargs)
            connection.execute(
                "UPDATE opening_recurrence_state SET game_metadata_input_signature = 'concurrent'"
            )
            connection.execute(
                "UPDATE opening_recurrence_run SET game_metadata_input_signature = 'concurrent'"
            )
            connection.commit()
            return identity

        monkeypatch.setattr(tracked_persistence, "_resolved_tracked_player", change_after_precheck)
        with pytest.raises(TrackedPlayerPublicationError, match="during publication"):
            publish_tracked_player(connection, facts)
        assert connection.execute(
            "SELECT COUNT(*) FROM opening_tracked_player_state"
        ).fetchone() == (0,)

    with _open_stage1_database(tmp_path / "version.db") as connection:
        connection.execute(
            "UPDATE opening_recurrence_state SET accepted_schema_version = 99 "
            "WHERE accepted_manifest_hash = 'manifest-stage1' AND corpus_id = 7"
        )
        connection.commit()
        with pytest.raises(TrackedPlayerDerivationError, match="versions are incompatible"):
            derive_tracked_player(connection, "skyrocoster", 7)


def test_stage2_storage_failure_rolls_back_complete_publication(tmp_path: Path) -> None:
    with _open_stage1_database(tmp_path / "rollback.db") as connection:
        before = upstream_preservation_signatures(connection)
        facts = derive_tracked_player(connection, "skyrocoster", 7)
        ensure_tracked_player_schema(connection)
        connection.execute(
            "CREATE TRIGGER fail_personal_projection BEFORE INSERT "
            "ON opening_player_position_projection BEGIN SELECT RAISE(ABORT, 'injected'); END"
        )
        connection.commit()

        with pytest.raises(TrackedPlayerPublicationError, match="injected"):
            publish_tracked_player(connection, facts)

        for table in (
            "opening_tracked_player",
            "opening_tracked_player_state",
            "opening_tracked_player_run",
            "opening_player_classification_game",
            "opening_player_position_projection",
            "opening_player_route_projection",
            "opening_player_branch_projection",
            "opening_player_route_branch_projection",
        ):
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone() == (0,)
        assert upstream_preservation_signatures(connection) == before


def test_stage3_rich_personal_projection_matches_fresh_accepted_facts(tmp_path: Path) -> None:
    personal_tables = (
        "opening_player_classification_game",
        "opening_player_position_projection",
        "opening_player_route_projection",
        "opening_player_branch_projection",
        "opening_player_route_branch_projection",
    )
    with _open_stage1_database(tmp_path / "stage3-rich.db", rich=True) as connection:
        before = upstream_preservation_signatures(connection)
        expected = _expected_personal_rows(connection)
        facts = derive_tracked_player(connection, "SkYrOcOsTeR", 7)

        assert facts.counts == (2, 6, 10, 11, 10)
        assert expected[0] == (
            ("manifest-stage1", 7, "game-1"),
            ("manifest-stage1", 7, "game-2"),
        )
        assert connection.execute(
            "SELECT uuid, white_player_uuid, black_player_uuid, end_time, white_rating, "
            "black_rating, white_result, black_result FROM games ORDER BY uuid"
        ).fetchall() == [
            ("game-1", PLAYER_UUID, "opponent", 1700000000, 1800, 1790, "win", "loss"),
            ("game-2", "opponent", PLAYER_UUID, 1700000000, 1795, 1810, "loss", "win"),
        ]

        result = publish_tracked_player(connection, facts)

        assert result.status == "success"
        for table, rows in zip(personal_tables, expected):
            assert _ordered_rows(connection, table) == tuple((PLAYER_UUID, *row) for row in rows)
        assert {row[7] for row in expected[3] if row[6] == "move"} == {"a2a4", "g1h1", "h1a1"}
        assert connection.execute("SELECT player_uuid FROM opening_tracked_player").fetchall() == [
            (PLAYER_UUID,)
        ]
        for table in TRACKED_PLAYER_SCHEMA_TABLES:
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            assert not (columns - {"id"}) & {"username", "player_id", "rowid"}
            assert all(
                "skyrocoster" not in str(value).lower()
                for row in _ordered_rows(connection, table)
                for value in row
            )
        assert upstream_preservation_signatures(connection) == before
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_stage3_failed_republication_preserves_accepted_personal_rows(tmp_path: Path) -> None:
    with _open_stage1_database(tmp_path / "stage3-republication.db", rich=True) as connection:
        facts = derive_tracked_player(connection, "skyrocoster", 7)
        publish_tracked_player(connection, facts)
        before_upstream = upstream_preservation_signatures(connection)
        connection.execute(
            "CREATE TRIGGER fail_republication BEFORE DELETE ON opening_player_classification_game "
            "BEGIN SELECT RAISE(ABORT, 'injected accepted-state failure'); END"
        )
        connection.execute("UPDATE opening_tracked_player_run SET details = 'force-recheck'")
        connection.commit()
        before_personal = {
            table: _ordered_rows(connection, table) for table in TRACKED_PLAYER_SCHEMA_TABLES
        }

        with pytest.raises(TrackedPlayerPublicationError, match="injected accepted-state failure"):
            publish_tracked_player(connection, facts)

        after_personal = {
            table: _ordered_rows(connection, table) for table in TRACKED_PLAYER_SCHEMA_TABLES
        }
        assert after_personal == before_personal
        assert upstream_preservation_signatures(connection) == before_upstream
