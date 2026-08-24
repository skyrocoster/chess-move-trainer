"""Build and inspect the repository-supported SQLite schema document."""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from backend.app.features.analysis.schema import initialize_analysis_schema
from backend.app.features.evaluation.schema import initialize_evaluation_schema
from scripts.chess_com._schema import ensure_corpus_schema
from scripts.chess_com.fetch_games import create_schema
from scripts.opening_catalog.classification_schema import ensure_classification_schema
from scripts.opening_catalog.preferred_move_schema import ensure_preferred_move_schema
from scripts.opening_catalog.recurrence_schema import ensure_recurrence_schema
from scripts.opening_catalog.schema import ensure_relationship_schema, ensure_schema

OUT_PATH = Path(__file__).parent / "schema.txt"
SCHEMA_SOURCES = (
    "scripts/chess_com/fetch_games.py:create_schema",
    "scripts/chess_com/_schema.py:ensure_corpus_schema",
    "scripts/opening_catalog/schema.py:ensure_schema",
    "scripts/opening_catalog/schema.py:ensure_relationship_schema",
    "scripts/opening_catalog/classification_schema.py:ensure_classification_schema",
    "scripts/opening_catalog/preferred_move_schema.py:ensure_preferred_move_schema",
    "scripts/opening_catalog/recurrence_schema.py:ensure_recurrence_schema",
    "backend/app/features/analysis/schema.py:initialize_analysis_schema",
    "backend/app/features/evaluation/schema.py:initialize_evaluation_schema",
)
OBJECT_TYPE_ORDER = {"table": 0, "index": 1, "trigger": 2, "view": 3}


@dataclass(frozen=True)
class SchemaObject:
    """One explicitly declared object from the assembled schema."""

    kind: str
    name: str
    table: str | None
    sql: str


def assemble_supported_schema(connection: sqlite3.Connection) -> None:
    """Assemble every supported schema namespace in dependency order."""

    create_schema(connection)
    ensure_corpus_schema(connection)
    ensure_schema(connection)
    ensure_relationship_schema(connection)
    ensure_classification_schema(connection)
    ensure_recurrence_schema(connection)
    ensure_preferred_move_schema(connection)
    initialize_analysis_schema(connection)
    initialize_evaluation_schema(connection)


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _canonical_sql(sql: str) -> str:
    """Normalize stored SQLite SQL without depending on source indentation."""

    return " ".join(sql.split())


def schema_objects(connection: sqlite3.Connection) -> list[SchemaObject]:
    """Return explicitly declared schema objects in stable order."""

    rows = connection.execute(
        """
        SELECT type, name, tbl_name, sql
        FROM sqlite_master
        WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL
        ORDER BY type, name
        """
    ).fetchall()
    return [
        SchemaObject(
            kind=str(row[0]),
            name=str(row[1]),
            table=str(row[2]) if row[2] is not None else None,
            sql=_canonical_sql(str(row[3])),
        )
        for row in sorted(rows, key=lambda row: (OBJECT_TYPE_ORDER[str(row[0])], str(row[1])))
    ]


def _pragma_rows(connection: sqlite3.Connection, pragma: str, name: str) -> list[tuple]:
    identifier = _quote_identifier(name)
    return connection.execute(f"PRAGMA {pragma}({identifier})").fetchall()


def _anchor(name: str) -> str:
    return "".join(char if char.isalnum() or char in "_-" else "-" for char in name.lower())


def _cell(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _render_navigation(objects: Iterable[SchemaObject]) -> list[str]:
    grouped = {
        kind: [item for item in objects if item.kind == kind]
        for kind in ("table", "index", "trigger", "view")
    }
    lines = ["## Navigation", ""]
    for kind in ("table", "index", "trigger", "view"):
        if not grouped[kind]:
            continue
        title = f"{kind.title()}s"
        lines.append(f"### {title}")
        for item in grouped[kind]:
            lines.append(f"- [`{item.name}`](#{kind}-{_anchor(item.name)})")
        lines.append("")
    return lines


def _render_table(connection: sqlite3.Connection, item: SchemaObject) -> list[str]:
    columns = _pragma_rows(connection, "table_info", item.name)
    foreign_keys = _pragma_rows(connection, "foreign_key_list", item.name)
    lines = [
        f"### Table: `{item.name}`",
        f'<a id="table-{_anchor(item.name)}"></a>',
        "",
        "#### Columns",
        "",
        "| PK order | Name | Type | Nullable | Default |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for cid, name, declared_type, not_null, default, primary_key in columns:
        del cid
        lines.append(
            f"| {_cell(primary_key)} | `{_cell(name)}` | `{_cell(declared_type)}` | "
            f"{'NO' if not_null else 'YES'} | `{_cell(default)}` |"
        )

    lines.extend(["", "#### Foreign keys", ""])
    if foreign_keys:
        lines.extend(
            [
                "| ID | Order | From | To table | To column | On update | On delete | Match |",
                "| ---: | ---: | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for foreign_key in foreign_keys:
            key_id, order, target, source_column, target_column, on_update, on_delete, match = (
                foreign_key
            )
            lines.append(
                f"| {_cell(key_id)} | {_cell(order)} | `{_cell(source_column)}` | "
                f"`{_cell(target)}` | `{_cell(target_column)}` | {_cell(on_update)} | "
                f"{_cell(on_delete)} | {_cell(match)} |"
            )
    else:
        lines.append("None declared.")

    lines.extend(["", "#### Canonical SQL", "", "```sql", item.sql, "```", ""])
    return lines


def _index_details(connection: sqlite3.Connection, item: SchemaObject) -> tuple[object, ...]:
    if item.table is None:
        return ("", "", "", "")
    for row in _pragma_rows(connection, "index_list", item.table):
        if row[1] == item.name:
            _, _, unique, origin, partial = row
            columns = [
                row[2] if row[2] is not None else f"<expression {row[1]}>"
                for row in _pragma_rows(connection, "index_info", item.name)
            ]
            return (item.table, "yes" if unique else "no", ", ".join(columns), partial, origin)
    return (item.table, "", "", "", "")


def _render_index(connection: sqlite3.Connection, item: SchemaObject) -> list[str]:
    table, unique, columns, partial, origin = _index_details(connection, item)
    return [
        f"### Index: `{item.name}`",
        f'<a id="index-{_anchor(item.name)}"></a>',
        "",
        f"- **Table:** `{table}`",
        f"- **Unique:** {unique}",
        f"- **Columns:** {', '.join(f'`{column.strip()}`' for column in str(columns).split(','))}",
        f"- **Partial:** {'yes' if partial else 'no'}",
        f"- **Origin:** `{origin}`",
        "",
        "#### Canonical SQL",
        "",
        "```sql",
        item.sql,
        "```",
        "",
    ]


def _render_trigger(item: SchemaObject) -> list[str]:
    return [
        f"### Trigger: `{item.name}`",
        f'<a id="trigger-{_anchor(item.name)}"></a>',
        "",
        f"- **Table:** `{item.table}`",
        "",
        "#### Canonical SQL",
        "",
        "```sql",
        item.sql,
        "```",
        "",
    ]


def render_schema(connection: sqlite3.Connection | None = None) -> str:
    """Render the supported schema, using only an in-memory database by default."""

    if connection is None:
        with sqlite3.connect(":memory:") as temporary_connection:
            assemble_supported_schema(temporary_connection)
            return render_schema(temporary_connection)

    objects = schema_objects(connection)
    lines = [
        "<!-- GENERATED FILE: DO NOT EDIT MANUALLY. -->",
        "# AI-readable SQLite schema",
        "",
        "> This document is generated from the repository-supported DDL in memory.",
        "> It contains schema structure only; it does not read or describe runtime database data.",
        "> Generator: `data/database/dump_schema.py`.",
        "",
        "## Source DDL owners",
        "",
    ]
    lines.extend(f"- `{source}`" for source in SCHEMA_SOURCES)
    lines.extend(["", *_render_navigation(objects), "## Schema objects", ""])

    for item in objects:
        if item.kind == "table":
            lines.extend(_render_table(connection, item))
        elif item.kind == "index":
            lines.extend(_render_index(connection, item))
        elif item.kind == "trigger":
            lines.extend(_render_trigger(item))
        else:
            lines.extend(
                [
                    f"### {item.kind.title()}: `{item.name}`",
                    f'<a id="{item.kind}-{_anchor(item.name)}"></a>',
                    "",
                    "#### Canonical SQL",
                    "",
                    "```sql",
                    item.sql,
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def write_schema(path: Path = OUT_PATH) -> None:
    """Explicitly write one rendered document to the selected artifact path."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_schema(), encoding="utf-8")


def schema_is_current(path: Path = OUT_PATH) -> bool:
    """Return whether the selected artifact exactly matches a fresh render."""

    try:
        return path.read_text(encoding="utf-8") == render_schema()
    except FileNotFoundError:
        return False


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true", help="explicitly write the schema artifact")
    modes.add_argument("--check", action="store_true", help="check the artifact without writing")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.write:
        write_schema()
        print(f"Wrote schema to {OUT_PATH}")
        return 0

    if schema_is_current():
        print(f"Schema is current: {OUT_PATH}")
        return 0

    print(
        f"Schema is missing or stale: {OUT_PATH}. "
        "Run the explicit write operation to regenerate it.",
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
