from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
PACKAGE_PATH = ROOT / "src" / "chess_move_trainer" / "database"


def _python_sources() -> list[Path]:
    return sorted(PACKAGE_PATH.glob("*.py"))


def test_database_package_has_no_legacy_or_production_import_direction() -> None:
    forbidden_prefixes = ("backend", "scripts", "legacy")
    imported_modules: list[str] = []

    for source_path in _python_sources():
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported_modules
        for prefix in forbidden_prefixes
    )
    assert all("schema.txt" not in path.read_text(encoding="utf-8") for path in _python_sources())


def test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin() -> None:
    sql_resource = (PACKAGE_PATH / "schema_v1.sql").read_text(encoding="utf-8").upper()
    python_text = "\n".join(path.read_text(encoding="utf-8") for path in _python_sources())
    cli_text = "\n".join(
        (PACKAGE_PATH / name).read_text(encoding="utf-8")
        for name in ("__main__.py", "cli.py")
        if (PACKAGE_PATH / name).exists()
    )

    assert sql_resource.count("CREATE TABLE") == 10
    assert "PRAGMA USER_VERSION = 1" in sql_resource
    assert "CREATE TABLE" not in python_text.upper()
    assert "PRAGMA USER_VERSION =" not in python_text.upper()
    assert "SQLITE3" not in cli_text.upper()
    assert "SQLALCHEMY" not in cli_text.upper()
    assert "SUBPROCESS" not in cli_text.upper()
    assert "CREATE TABLE" not in cli_text.upper()


def test_package_contains_no_runtime_wrapper_or_copied_legacy_generator() -> None:
    package_text = "\n".join(path.read_text(encoding="utf-8") for path in _python_sources())

    assert "runpy" not in package_text
    assert "subprocess" not in package_text
    assert "legacy" not in package_text.lower()
    assert "backend" not in package_text.lower()
