import sqlite3
from pathlib import Path

from data.database import dump_schema

EXPECTED_TABLES = {
    "players",
    "games",
    "fetch_state",
    "corpus",
    "corpus_game",
    "position_state",
    "position_occurrence",
    "corpus_schema",
    "corpus_run",
    "opening_catalog_schema",
    "opening_source_manifest",
    "opening_source_file",
    "opening_import_run",
    "opening_catalog_state",
    "opening_catalog",
    "opening_relationship_schema",
    "opening_relationship_state",
    "opening_relationship_run",
    "opening_relationship_position",
    "opening_position_membership",
    "opening_parent_link",
    "opening_transposition_link",
    "opening_classification_schema",
    "opening_classification_state",
    "opening_classification_run",
    "opening_classification_game",
    "opening_classification_anchor",
    "opening_classification_route",
    "opening_recurrence_schema",
    "opening_recurrence_state",
    "opening_recurrence_run",
    "opening_recurrence_game",
    "opening_recurrence_occurrence",
    "opening_recurrence_route_event",
    "opening_recurrence_branch_event",
    "opening_recurrence_position_projection",
    "opening_recurrence_route_projection",
    "opening_recurrence_branch_projection",
    "opening_recurrence_route_branch_projection",
    "analysis_schema",
    "analysis_result",
    "analysis_candidate",
    "analysis_batch_run",
    "analysis_position_failure",
    "evaluation_schema",
    "evaluation_queue",
    "opening_preferred_move_schema",
    "opening_preferred_move_requirement_event",
    "opening_preferred_move_event",
}
EXPECTED_INDEXES = {
    "one_current_month",
    "position_occurrence_state_idx",
    "opening_catalog_endpoint_idx",
    "opening_import_run_manifest_idx",
    "opening_position_membership_position_idx",
    "opening_parent_link_parent_idx",
    "opening_transposition_link_position_idx",
    "opening_classification_anchor_position_idx",
    "opening_classification_route_game_idx",
    "opening_recurrence_occurrence_position_idx",
    "opening_recurrence_route_event_position_idx",
    "opening_recurrence_branch_event_parent_idx",
    "evaluation_queue_fifo",
    "opening_preferred_move_requirement_lookup",
    "opening_preferred_move_lookup",
}
EXPECTED_TRIGGERS = {
    "analysis_batch_run_no_update",
    "analysis_batch_run_no_delete",
    "analysis_failure_no_update",
    "analysis_failure_no_delete",
    "opening_preferred_move_requirement_no_update",
    "opening_preferred_move_requirement_no_delete",
    "opening_preferred_move_no_update",
    "opening_preferred_move_no_delete",
}


def test_assembled_schema_contains_every_supported_object() -> None:
    with sqlite3.connect(":memory:") as connection:
        dump_schema.assemble_supported_schema(connection)
        objects = dump_schema.schema_objects(connection)

    assert {item.name for item in objects if item.kind == "table"} == EXPECTED_TABLES
    assert {item.name for item in objects if item.kind == "index"} == EXPECTED_INDEXES
    assert {item.name for item in objects if item.kind == "trigger"} == EXPECTED_TRIGGERS
    assert all(item.sql for item in objects)


def test_render_contains_ai_navigation_and_structural_details() -> None:
    document = dump_schema.render_schema()

    assert "<!-- GENERATED FILE: DO NOT EDIT MANUALLY. -->" in document
    assert "## Source DDL owners" in document
    for source in dump_schema.SCHEMA_SOURCES:
        assert f"- `{source}`" in document
    assert "## Navigation" in document
    for table in EXPECTED_TABLES:
        assert f"### Table: `{table}`" in document
    for index in EXPECTED_INDEXES:
        assert f"### Index: `{index}`" in document
    for trigger in EXPECTED_TRIGGERS:
        assert f"### Trigger: `{trigger}`" in document
    assert "[`analysis_candidate`](#table-analysis_candidate)" in document
    assert "| PK order | Name | Type | Nullable | Default |" in document
    assert "| 1 | `uuid` | `TEXT` | YES |" in document
    assert "| 1 | 0 | `white_player_uuid` | `players` | `uuid` |" in document
    assert "`opening_recurrence_route_branch_projection`" in document
    assert "ON DELETE CASCADE" in document
    assert "CREATE TRIGGER analysis_batch_run_no_update" in document
    assert "CREATE INDEX evaluation_queue_fifo" in document
    assert "WITHOUT ROWID" in document
    assert "INSERT INTO" not in document
    assert "0007925c-5a8d-11f0-9740-f690a301000f" not in document


def test_independent_in_memory_renders_are_byte_identical() -> None:
    assert dump_schema.render_schema() == dump_schema.render_schema()


def test_render_does_not_open_a_runtime_database(monkeypatch) -> None:
    real_connect = dump_schema.sqlite3.connect
    opened: list[str] = []

    def tracked_connect(database, *args, **kwargs):
        opened.append(str(database))
        return real_connect(database, *args, **kwargs)

    monkeypatch.setattr(dump_schema.sqlite3, "connect", tracked_connect)

    dump_schema.render_schema()

    assert opened == [":memory:"]


def test_check_is_read_only_and_write_targets_only_the_selected_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "schema.txt"

    assert dump_schema.schema_is_current(artifact) is False
    assert not artifact.exists()

    dump_schema.write_schema(artifact)

    assert artifact.exists()
    assert dump_schema.schema_is_current(artifact) is True
