from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[2]
PACKAGE_PATH = ROOT / "src" / "chess_move_trainer" / "database"


def _python_sources() -> list[Path]:
    return sorted(PACKAGE_PATH.rglob("*.py"))


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
    assert "SQLALCHEMY" not in cli_text.upper()
    assert "SQLITE3" not in cli_text.upper()
    assert "CHESS.PGN" not in cli_text.upper()
    assert "CANONICALIZE" not in cli_text.upper()
    assert "SELECT " not in cli_text.upper()
    assert "INSERT " not in cli_text.upper()


def test_package_contains_no_runtime_wrapper_or_copied_legacy_generator() -> None:
    package_text = "\n".join(path.read_text(encoding="utf-8") for path in _python_sources())
    non_engine_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in _python_sources()
        if path.relative_to(PACKAGE_PATH).parts[:1] != ("stockfish",)
    )

    assert "runpy" not in package_text
    assert "subprocess" not in non_engine_text
    assert "legacy" not in package_text.lower()
    assert "backend" not in package_text.lower()


def test_rebuild_boundary_has_only_aggregate_proof_modules() -> None:
    rebuild_path = PACKAGE_PATH / "rebuild"
    assert sorted(path.name for path in rebuild_path.glob("*.py")) == [
        "__init__.py",
        "proof.py",
    ]

    for source_path in sorted(rebuild_path.rglob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        assert not any(
            module == prefix or module.startswith(f"{prefix}.")
            for module in imported_modules
            for prefix in ("backend", "frontend", "scripts", "legacy")
        )

    proof_text = "\n".join(
        path.read_text(encoding="utf-8") for path in rebuild_path.rglob("*.py")
    )
    assert "data/database/chess.db" in proof_text
    assert "subprocess" not in proof_text.lower()
    assert "sqlite3" not in proof_text.lower()


def test_rebuild_has_no_file_lifecycle_commands_or_persistent_run_state() -> None:
    rebuild_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PACKAGE_PATH / "rebuild").rglob("*.py"))
    )
    for forbidden in (
        "recover",
        "manifest",
        "audit_log",
        "run_history",
        "failure_row",
        "managed_candidate",
        "rebuilt_neighbour",
        "snapshot",
        "rollback",
        "replacement",
        "replacement_ready",
    ):
        assert forbidden not in rebuild_text.lower()


def test_position_service_does_not_promote_raw_handles_or_schema_creation() -> None:
    positions_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PACKAGE_PATH / "positions").rglob("*.py"))
    )

    assert "create_schema" not in positions_text
    assert "sqlite3.Connection" not in positions_text
    assert "sqlalchemy.engine.Connection" not in positions_text
    assert "raw_connection" not in positions_text


def test_games_responsibilities_preserve_network_and_database_separation() -> None:
    games_path = PACKAGE_PATH / "games"
    acquisition_text = (games_path / "acquisition.py").read_text(encoding="utf-8").lower()
    import_side_text = "\n".join(
        (games_path / name).read_text(encoding="utf-8").lower()
        for name in ("normalization.py", "persistence.py")
    )

    assert "sqlite3" not in acquisition_text
    assert "sqlalchemy" not in acquisition_text
    assert "httpx" not in import_side_text

    acquisition_tree = ast.parse((games_path / "acquisition.py").read_text(encoding="utf-8"))
    acquisition_imports = [
        node.module
        for node in ast.walk(acquisition_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    ]
    assert not any("connection" in module or "position" in module for module in acquisition_imports)


def test_openings_have_no_legacy_application_or_games_dependency() -> None:
    openings_path = PACKAGE_PATH / "openings"
    imported_modules: list[str] = []
    for source_path in sorted(openings_path.rglob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

    assert not any(
        module == "games"
        or module.endswith(".games")
        or module.startswith(("backend", "legacy", "scripts"))
        for module in imported_modules
    )


def test_opening_acquisition_owns_transport_without_storage_or_process_direction() -> None:
    acquisition_path = PACKAGE_PATH / "openings" / "acquisition.py"
    tree = ast.parse(acquisition_path.read_text(encoding="utf-8"))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)

    assert "httpx" in imported_modules
    assert not any(
        module == forbidden
        or module.startswith(f"{forbidden}.")
        for module in imported_modules
        for forbidden in ("backend", "games", "scripts", "legacy", "sqlite3", "subprocess")
    )
    acquisition_text = acquisition_path.read_text(encoding="utf-8").lower()
    assert "sqlite" not in acquisition_text
    assert "subprocess" not in acquisition_text


def test_lower_level_database_packages_do_not_depend_on_openings() -> None:
    for package_name in ("positions", "games"):
        package_path = PACKAGE_PATH / package_name
        for source_path in sorted(package_path.rglob("*.py")):
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
            imports = [
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            ]
            assert not any(
                module == "openings" or module.endswith(".openings")
                for module in imports
            )


def test_preferred_moves_dependencies_are_owned_and_one_way() -> None:
    preferred_path = PACKAGE_PATH / "preferred_moves"
    forbidden_modules = (
        "backend",
        "frontend",
        "games",
        "openings",
        "scripts",
        "legacy",
    )
    allowed_database_modules = {
        "connection",
        "schema",
        "positions",
        "positions.repository",
    }

    for source_path in sorted(preferred_path.rglob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module is not None:
                    modules = [node.module]
                elif node.level == 2 and node.module is not None:
                    modules = [f"database.{node.module}"]
                elif node.level == 2:
                    modules = ["database"]
                elif node.level == 1 and node.module is not None:
                    modules = [f"preferred_moves.{node.module}"]
                elif node.level == 1:
                    modules = ["preferred_moves"]
                else:
                    modules = []
            else:
                continue

            for module in modules:
                assert not (
                    module in forbidden_modules
                    or module.startswith(
                        tuple(f"{prefix}." for prefix in forbidden_modules)
                    )
                    or module.startswith(
                        tuple(f"chess_move_trainer.{prefix}" for prefix in forbidden_modules)
                    )
                )
                if module.startswith("database."):
                    assert module.removeprefix("database.") in allowed_database_modules


def test_database_and_position_lower_layers_do_not_import_preferred_moves() -> None:
    lower_level_paths = [
        PACKAGE_PATH / "connection.py",
        PACKAGE_PATH / "schema.py",
        PACKAGE_PATH / "positions" / "__init__.py",
        PACKAGE_PATH / "positions" / "canonicalization.py",
        PACKAGE_PATH / "positions" / "repository.py",
    ]

    for source_path in lower_level_paths:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported_modules.append(node.module or "")
        assert not any(
            module == "preferred_moves"
            or module.endswith(".preferred_moves")
            or module.startswith(".preferred_moves")
            for module in imported_modules
        )


def test_preferred_moves_feature_and_cli_have_no_excluded_or_business_logic_imports() -> None:
    preferred_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PACKAGE_PATH / "preferred_moves").rglob("*.py"))
    )
    cli_text = "\n".join(
        (PACKAGE_PATH / name).read_text(encoding="utf-8")
        for name in ("__main__.py", "cli.py")
    )

    for forbidden in (
        "backend",
        "frontend",
        "games",
        "openings",
        "scripts",
        "legacy",
        "runpy",
        "subprocess",
    ):
        assert forbidden not in preferred_text.lower()
    for forbidden in (
        "sqlalchemy",
        "sqlite3",
        "subprocess",
        "chess.pgn",
        "create table",
        "pragma user_version",
        "canonicalize",
        "select ",
        "insert ",
    ):
        assert forbidden not in cli_text.lower()

    cli_tree = ast.parse(cli_text)
    cli_imports = []
    for node in ast.walk(cli_tree):
        if isinstance(node, ast.Import):
            cli_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            cli_imports.append(node.module)
    assert not any(
        module == "chess" or module.startswith("chess.") for module in cli_imports
    )
