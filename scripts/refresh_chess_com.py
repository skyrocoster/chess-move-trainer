"""Run the fetch stage of the repeatable Chess.com refresh command."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Callable, TextIO

import yaml

from scripts.chess_com import extract_corpus, fetch_games
from scripts.chess_com._cli import DEFAULT_SUBJECT
from scripts.chess_com._schema import SCHEMA_VERSION as CORPUS_SCHEMA_VERSION
from scripts.stockfish_analysis.analyze_menu import (
    DEFAULT_DB,
    DEFAULT_ENGINE,
    QUALIFIED_PROFILE,
)
from scripts.opening_catalog import import_classification, import_recurrence
from scripts.opening_catalog.schema import (
    RELATIONSHIP_SCHEMA_TABLES,
    RELATIONSHIP_SCHEMA_VERSION,
    SCHEMA_TABLES,
    SCHEMA_VERSION as CATALOG_SCHEMA_VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = Path(__file__).with_name("chess_com") / "config.yaml"
DEFAULT_WORKERS = 1
DEFAULT_WATCHDOG_SECONDS = 30.0


@dataclass(frozen=True)
class RefreshConfig:
    """All settings owned by one refresh invocation."""

    username: str
    subject_uuid: str
    database: Path
    engine: Path
    profile_id: str
    workers: int
    watchdog_seconds: float
    delay: float
    base_url: str
    raw_root: Path
    log_path: Path

    def fetch_settings(self) -> fetch_games.Settings:
        """Adapt the command contract to the existing fetcher settings."""

        return fetch_games.Settings(
            username=self.username,
            delay=self.delay,
            base_url=self.base_url,
            raw_root=self.raw_root,
            database=self.database,
            log_path=self.log_path,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "username": self.username,
            "subject_uuid": self.subject_uuid,
            "database": str(self.database),
            "engine": str(self.engine),
            "profile_id": self.profile_id,
            "workers": self.workers,
            "watchdog_seconds": self.watchdog_seconds,
            "delay": self.delay,
            "base_url": self.base_url,
            "raw_root": str(self.raw_root),
            "log_path": str(self.log_path),
        }


def _configured_path(values: dict[str, object], key: str, default: Path) -> Path:
    value = values.get(key)
    if value is None:
        return default
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def load_config(
    config_path: Path = DEFAULT_CONFIG,
    *,
    database: Path | None = None,
    engine: Path | None = None,
    profile_id: str | None = None,
    workers: int | None = None,
    watchdog_seconds: float | None = None,
    delay: float | None = None,
) -> RefreshConfig:
    """Load refresh settings while retaining the existing Chess.com defaults."""

    values = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(values, dict):
        raise ValueError("refresh config must be a YAML object")

    fetch = fetch_games.load_settings(config_path, None, delay)
    selected_profile = str(profile_id or values.get("profile_id", QUALIFIED_PROFILE))
    if selected_profile != QUALIFIED_PROFILE:
        raise ValueError(f"only the accepted profile {QUALIFIED_PROFILE} may be configured")

    selected_workers = int(
        workers if workers is not None else values.get("workers", DEFAULT_WORKERS)
    )
    if not 1 <= selected_workers <= 6:
        raise ValueError("workers must be between 1 and 6")
    selected_watchdog = float(
        watchdog_seconds
        if watchdog_seconds is not None
        else values.get("watchdog_seconds", values.get("watchdog", DEFAULT_WATCHDOG_SECONDS))
    )
    if selected_watchdog <= 0:
        raise ValueError("watchdog seconds must be positive")

    return RefreshConfig(
        username=fetch.username,
        subject_uuid=str(values.get("subject_uuid", DEFAULT_SUBJECT)),
        database=database or _configured_path(values, "database", DEFAULT_DB),
        engine=engine or _configured_path(values, "engine", DEFAULT_ENGINE),
        profile_id=selected_profile,
        workers=selected_workers,
        watchdog_seconds=selected_watchdog,
        delay=fetch.delay,
        base_url=fetch.base_url,
        raw_root=_configured_path(values, "raw_root", fetch.raw_root),
        log_path=_configured_path(values, "log_path", fetch.log_path),
    )


@dataclass(frozen=True)
class StageResult:
    """A stable, serializable result for one ordered refresh stage."""

    name: str
    status: str
    exit_code: int = 0
    details: str | None = None
    metrics: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        result = {
            "name": self.name,
            "status": self.status,
            "exit_code": self.exit_code,
            "details": self.details,
        }
        result.update({key: value for key, value in self.metrics.items() if key != "status"})
        return result


StageHook = Callable[[RefreshConfig], StageResult]


@dataclass(frozen=True)
class StageHooks:
    """Optional seams for later stages; Stage 1 supplies none by default."""

    corpus: StageHook | None = None
    s3: StageHook | None = None
    s4: StageHook | None = None
    analysis: StageHook | None = None

    def ordered(self) -> tuple[tuple[str, StageHook], ...]:
        return tuple(
            (name, hook)
            for name, hook in (
                ("corpus", self.corpus),
                ("s3", self.s3),
                ("s4", self.s4),
                ("analysis", self.analysis),
            )
            if hook is not None
        )


@dataclass(frozen=True)
class RefreshReport:
    """The command-level status and the results observed so far."""

    status: str
    stages: tuple[StageResult, ...]
    exit_code: int

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "stages": [stage.as_dict() for stage in self.stages],
        }


def _fetch_stage(config: RefreshConfig, logger, fetcher: Callable) -> StageResult:
    try:
        result = fetcher(config.fetch_settings(), logger)
    except fetch_games.RateLimitError as error:
        return StageResult("fetch", "rate_limited", 2, str(error))
    except Exception as error:
        return StageResult("fetch", "failed", 1, str(error))

    if not isinstance(result, fetch_games.FetchResult):
        raise TypeError("fetcher returned an unsupported result")
    return StageResult(
        "fetch",
        result.status,
        result.exit_code,
        None if result.complete else f"{len(result.failed_months)} month(s) failed",
        result.as_dict(),
    )


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _schema_version(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT version FROM {table} WHERE id = 1").fetchone()
    if row is None:
        raise RuntimeError(f"required schema table {table!r} has no singleton version row")
    return int(row[0])


def _validate_prerequisites(connection: sqlite3.Connection, subject_uuid: str) -> int:
    """Check the accepted S1/S2 and selected corpus boundary without rebuilding it."""

    required = (
        {"players", "games", "corpus_schema", "corpus", "corpus_game", "position_state", "position_occurrence"}
        | SCHEMA_TABLES
        | RELATIONSHIP_SCHEMA_TABLES
    )
    missing = required - _table_names(connection)
    if missing:
        raise RuntimeError(f"required S1/S2/corpus tables are missing: {', '.join(sorted(missing))}")
    if _schema_version(connection, "corpus_schema") != CORPUS_SCHEMA_VERSION:
        raise RuntimeError("accepted corpus schema version is incompatible")
    if _schema_version(connection, "opening_catalog_schema") != CATALOG_SCHEMA_VERSION:
        raise RuntimeError("accepted S1 catalog schema version is incompatible")
    if _schema_version(connection, "opening_relationship_schema") != RELATIONSHIP_SCHEMA_VERSION:
        raise RuntimeError("accepted S2 relationship schema version is incompatible")

    if connection.execute("SELECT 1 FROM players WHERE uuid = ?", (subject_uuid,)).fetchone() is None:
        raise RuntimeError(f"configured subject player {subject_uuid} is missing")
    corpus = connection.execute(
        "SELECT corpus_id FROM corpus WHERE subject_player_uuid = ?", (subject_uuid,)
    ).fetchone()
    if corpus is None:
        raise RuntimeError(f"Corpus metadata is missing for subject {subject_uuid}")
    corpus_id = int(corpus[0])

    catalog_state = connection.execute(
        "SELECT accepted_manifest_hash, accepted_schema_version, record_count "
        "FROM opening_catalog_state WHERE id = 1"
    ).fetchone()
    if catalog_state is None:
        raise RuntimeError("an accepted S1 catalog is required")
    manifest_hash, catalog_version, catalog_count = catalog_state
    if int(catalog_version) != CATALOG_SCHEMA_VERSION:
        raise RuntimeError("accepted S1 catalog schema version is incompatible")
    if connection.execute(
        "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?", (manifest_hash,)
    ).fetchone()[0] != int(catalog_count):
        raise RuntimeError("accepted S1 catalog record counts are inconsistent")

    relationship = connection.execute(
        "SELECT accepted_schema_version, record_count, position_count, membership_count, "
        "parent_link_count, transposition_link_count FROM opening_relationship_state "
        "WHERE accepted_manifest_hash = ?",
        (manifest_hash,),
    ).fetchone()
    if relationship is None:
        raise RuntimeError("an accepted S2 relationship state for the S1 manifest is required")
    if int(relationship[0]) != RELATIONSHIP_SCHEMA_VERSION:
        raise RuntimeError("accepted S2 relationship schema version is incompatible")
    relationship_counts = (
        connection.execute(
            "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?", (manifest_hash,)
        ).fetchone()[0],
        connection.execute(
            "SELECT COUNT(*) FROM opening_relationship_position WHERE manifest_hash = ?",
            (manifest_hash,),
        ).fetchone()[0],
        connection.execute(
            "SELECT COUNT(*) FROM opening_position_membership WHERE manifest_hash = ?",
            (manifest_hash,),
        ).fetchone()[0],
        connection.execute(
            "SELECT COUNT(*) FROM opening_parent_link WHERE manifest_hash = ?", (manifest_hash,)
        ).fetchone()[0],
        connection.execute(
            "SELECT COUNT(*) FROM opening_transposition_link WHERE manifest_hash = ?",
            (manifest_hash,),
        ).fetchone()[0],
    )
    if relationship_counts != tuple(int(value) for value in relationship[1:]):
        raise RuntimeError("accepted S2 relationship counts are inconsistent")
    return corpus_id


def _result_metrics(result: object) -> tuple[str | None, dict[str, object]]:
    if isinstance(result, dict):
        values = dict(result)
    elif is_dataclass(result):
        values = asdict(result)
    else:
        raise TypeError("stage returned an unsupported result")
    status = values.pop("status", None)
    return (str(status) if status is not None else None), values


def _stage_from_result(name: str, result: object, corpus_id: int) -> StageResult:
    result_status, metrics = _result_metrics(result)
    if result_status is None:
        unchanged = all(metrics.get(key, 0) == 0 for key in ("new_games", "changed_games", "removed_games"))
        result_status = "unchanged" if unchanged else "success"
    metrics.setdefault("corpus_id", corpus_id)
    return StageResult(name, result_status, 0, metrics=metrics)


def _default_stage_hooks(
    connection: sqlite3.Connection, corpus_id: int, logger
) -> StageHooks:
    return StageHooks(
        corpus=lambda config: _stage_from_result(
            "corpus",
            extract_corpus.run_extraction(connection, config.subject_uuid, logger=logger),
            corpus_id,
        ),
        s3=lambda _config: _stage_from_result(
            "s3", import_classification(connection, corpus_id), corpus_id
        ),
        s4=lambda _config: _stage_from_result(
            "s4", import_recurrence(connection, corpus_id), corpus_id
        ),
    )


def _run_downstream_stages(
    config: RefreshConfig,
    stages: list[StageResult],
    hooks: StageHooks,
    defaults: StageHooks,
) -> RefreshReport:
    """Run corpus, S3, and S4 in order, retaining each API's own transaction."""

    selected = dict(hooks.ordered())
    for name, default in defaults.ordered():
        hook = selected.get(name, default)
        try:
            stage = hook(config)
        except Exception as error:
            stage = StageResult(name, "failed", 1, str(error))
        if not isinstance(stage, StageResult):
            raise TypeError(f"{name} stage returned an unsupported result")
        stages.append(stage)
        if stage.exit_code != 0:
            return RefreshReport(stage.status, tuple(stages), stage.exit_code)
    return RefreshReport("complete", tuple(stages), 0)


def run(
    config: RefreshConfig,
    *,
    logger=None,
    fetcher: Callable | None = None,
    hooks: StageHooks | None = None,
) -> RefreshReport:
    """Run fetch and stop before downstream stages when it is incomplete.

    Later stages deliberately have no implementation in Stage 1. Keeping the
    return value fetch-only makes that boundary explicit rather than reporting
    work that has not run.
    """

    active_logger = logger or fetch_games.configure_logging(config.log_path)
    fetch_stage = _fetch_stage(config, active_logger, fetcher or fetch_games.run)
    if fetch_stage.status != "complete":
        return RefreshReport(fetch_stage.status, (fetch_stage,), fetch_stage.exit_code)
    stages = [fetch_stage]
    try:
        connection = sqlite3.connect(config.database, timeout=0)
    except Exception as error:
        failed = StageResult("corpus", "failed", 1, str(error))
        return RefreshReport("failed", (fetch_stage, failed), 1)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            corpus_id = _validate_prerequisites(connection, config.subject_uuid)
        except Exception as error:
            failed = StageResult("corpus", "failed", 1, str(error))
            return RefreshReport("failed", (fetch_stage, failed), 1)
        return _run_downstream_stages(
            config,
            stages,
            hooks or StageHooks(),
            _default_stage_hooks(connection, corpus_id, active_logger),
        )
    finally:
        connection.close()


def print_report(report: RefreshReport, output: TextIO = sys.stdout) -> None:
    print(f"refresh status: {report.status}", file=output)
    for stage in report.stages:
        suffix = f": {stage.details}" if stage.details else ""
        print(f"{stage.name}: {stage.status} (exit {stage.exit_code}){suffix}", file=output)
        for key, value in stage.metrics.items():
            if key != "status":
                print(f"  {key}: {value}", file=output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh the configured Chess.com corpus.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--db", type=Path, help="SQLite database path")
    parser.add_argument("--engine", type=Path, help="Stockfish executable path")
    parser.add_argument("--profile-id", help="accepted Stockfish profile ID")
    parser.add_argument("--workers", type=int, help="analysis workers (1-6)")
    parser.add_argument("--watchdog", dest="watchdog_seconds", type=float)
    parser.add_argument("--delay", type=float, help="seconds between archive requests")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(
            args.config,
            database=args.db,
            engine=args.engine,
            profile_id=args.profile_id,
            workers=args.workers,
            watchdog_seconds=args.watchdog_seconds,
            delay=args.delay,
        )
        logger = fetch_games.configure_logging(config.log_path)
        report = run(config, logger=logger)
        print_report(report)
        return report.exit_code
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Refresh configuration failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
