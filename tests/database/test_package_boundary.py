from __future__ import annotations

import importlib
import tomllib
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_common_package_and_database_namespace_are_importable() -> None:
    package = importlib.import_module("chess_move_trainer")
    database = importlib.import_module("chess_move_trainer.database")
    positions = importlib.import_module("chess_move_trainer.database.positions")
    games = importlib.import_module("chess_move_trainer.database.games")

    assert package.__name__ == "chess_move_trainer"
    assert database.__name__ == "chess_move_trainer.database"
    assert positions.__name__ == "chess_move_trainer.database.positions"
    assert games.__name__ == "chess_move_trainer.database.games"
    assert Path(package.__file__).parts[-3:-1] == ("src", "chess_move_trainer")


def test_packaging_preserves_backend_and_declares_database_sql_resources() -> None:
    with (ROOT / "pyproject.toml").open("rb") as pyproject_file:
        config = tomllib.load(pyproject_file)

    package_find = config["tool"]["setuptools"]["packages"]["find"]
    package_data = config["tool"]["setuptools"]["package-data"]

    assert "backend*" in package_find["include"]
    assert "chess_move_trainer*" in package_find["include"]
    assert package_data["chess_move_trainer.database"] == ["*.sql"]


def test_permanent_tool_setup_is_an_editable_no_dependency_install() -> None:
    setup_script = (ROOT / "setup-tools.ps1").read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in setup_script
    assert "--editable" in setup_script
    assert "--no-deps" in setup_script
    assert "setup.ps1" not in setup_script
    assert "database" not in setup_script.lower()
