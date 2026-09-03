"""Fetch Chess.com monthly archives into raw JSON and normalized SQLite."""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "https://api.chess.com/pub"


class RateLimitError(RuntimeError):
    """The API rejected a request because of rate limiting."""


@dataclass(frozen=True)
class Settings:
    username: str
    delay: float
    base_url: str
    raw_root: Path
    database: Path
    log_path: Path


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes


@dataclass(frozen=True)
class MonthFailure:
    """A monthly archive that could not be fetched or persisted."""

    year: int
    month: int
    error: str

    def as_dict(self) -> dict[str, object]:
        return {"year": self.year, "month": self.month, "error": self.error}


@dataclass(frozen=True)
class FetchResult:
    """The observable outcome of processing the selected archive months."""

    status: str
    requested_months: int
    fetched_months: int
    unchanged_months: int
    skipped_months: int
    failed_months: tuple[MonthFailure, ...] = ()

    @property
    def complete(self) -> bool:
        return self.status == "complete"

    @property
    def exit_code(self) -> int:
        return 0 if self.complete else 1

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "requested_months": self.requested_months,
            "fetched_months": self.fetched_months,
            "unchanged_months": self.unchanged_months,
            "skipped_months": self.skipped_months,
            "failed_months": [failure.as_dict() for failure in self.failed_months],
        }


def load_settings(config_path: Path, username: str | None, delay: float | None) -> Settings:
    values = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    name = username or values.get("username", "skyrocoster")
    wait = float(delay if delay is not None else values.get("delay", 1.0))
    base = str(values.get("base_url", DEFAULT_BASE_URL)).rstrip("/")
    return Settings(
        name,
        wait,
        base,
        ROOT / "data/chess-com/raw",
        ROOT / "data/database/chess_games.db",
        ROOT / "data/chess-com/logs/fetch.log",
    )


def configure_logging(path: Path) -> logging.Logger:
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("chess_com_fetcher")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


def request(url: str, headers: dict[str, str] | None = None) -> Response:
    try:
        with urlopen(Request(url, headers=headers or {}, method="GET"), timeout=60) as result:
            return Response(result.status, dict(result.headers.items()), result.read())
    except HTTPError as error:
        return Response(error.code, dict(error.headers.items()), error.read())
    except URLError as error:
        raise RuntimeError(f"request failed: {error.reason}") from error


def parse_json(response: Response) -> dict:
    if response.status == 304:
        return {}
    try:
        value = json.loads(response.body)
    except json.JSONDecodeError as error:
        raise ValueError("response was not valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("response JSON must be an object")
    return value


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS players (
            uuid TEXT PRIMARY KEY, username TEXT NOT NULL, profile_url TEXT,
            UNIQUE (username, uuid)
        );
        CREATE TABLE IF NOT EXISTS games (
            uuid TEXT PRIMARY KEY, url TEXT NOT NULL, pgn TEXT NOT NULL,
            time_control TEXT NOT NULL, end_time INTEGER NOT NULL, rated INTEGER,
            tcn TEXT, initial_setup TEXT, fen TEXT, time_class TEXT, rules TEXT, eco TEXT,
            white_player_uuid TEXT NOT NULL, black_player_uuid TEXT NOT NULL,
            white_rating INTEGER, black_rating INTEGER, white_result TEXT, black_result TEXT,
            white_accuracy REAL, black_accuracy REAL, tournament TEXT, match TEXT,
            year INTEGER NOT NULL, month INTEGER NOT NULL,
            FOREIGN KEY (white_player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (black_player_uuid) REFERENCES players(uuid),
            UNIQUE (year, month, uuid)
        );
        CREATE TABLE IF NOT EXISTS fetch_state (
            username TEXT NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL,
            etag TEXT, last_fetched TEXT, is_current INTEGER NOT NULL,
            PRIMARY KEY (username, year, month)
        );
        CREATE UNIQUE INDEX IF NOT EXISTS one_current_month
            ON fetch_state (username) WHERE is_current = 1;
        """
    )
    connection.commit()


def month_from_url(url: str) -> tuple[int, int]:
    parts = url.rstrip("/").split("/")
    return int(parts[-2]), int(parts[-1])


def save_json(root: Path, relative: str, value: dict) -> None:
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def upsert_month(connection: sqlite3.Connection, games: list[dict], year: int, month: int) -> None:
    for game in games:
        players = [game.get("white", {}), game.get("black", {})]
        for player in players:
            connection.execute(
                "INSERT INTO players VALUES (?, ?, ?) "
                "ON CONFLICT(uuid) DO UPDATE SET username=excluded.username, "
                "profile_url=excluded.profile_url",
                (player["uuid"], player["username"], player.get("@id")),
            )
        connection.execute(
            """INSERT INTO games VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(uuid) DO UPDATE SET url=excluded.url, pgn=excluded.pgn,
            end_time=excluded.end_time,
            white_rating=excluded.white_rating, black_rating=excluded.black_rating,
            white_result=excluded.white_result, black_result=excluded.black_result,
            white_accuracy=excluded.white_accuracy, black_accuracy=excluded.black_accuracy""",
            (
                game["uuid"],
                game["url"],
                game["pgn"],
                game["time_control"],
                game["end_time"],
                int(game["rated"]) if "rated" in game else None,
                game.get("tcn"),
                game.get("initial_setup"),
                game.get("fen"),
                game.get("time_class"),
                game.get("rules"),
                game.get("eco"),
                game["white"]["uuid"],
                game["black"]["uuid"],
                game["white"].get("rating"),
                game["black"].get("rating"),
                game["white"].get("result"),
                game["black"].get("result"),
                game.get("accuracies", {}).get("white"),
                game.get("accuracies", {}).get("black"),
                game.get("tournament"),
                game.get("match"),
                year,
                month,
            ),
        )


def mark_state(
    connection: sqlite3.Connection,
    settings: Settings,
    year: int,
    month: int,
    etag: str | None,
    current: bool,
) -> None:
    now = datetime.now(UTC).isoformat()
    connection.execute("UPDATE fetch_state SET is_current=0 WHERE username=?", (settings.username,))
    connection.execute(
        """INSERT INTO fetch_state VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(username, year, month) DO UPDATE SET etag=excluded.etag,
        last_fetched=excluded.last_fetched, is_current=excluded.is_current""",
        (settings.username, year, month, etag, now, int(current)),
    )


def run(
    settings: Settings,
    logger: logging.Logger,
    month_filter: tuple[int, int] | None = None,
    sleep=time.sleep,
) -> FetchResult:
    settings.database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database)
    create_schema(connection)
    archive_url = f"{settings.base_url}/player/{settings.username}/games/archives"
    try:
        archive_response = request(archive_url)
        if archive_response.status == 429:
            raise RateLimitError("archive list request returned HTTP 429")
        if archive_response.status != 200:
            raise RuntimeError(f"archive list request returned HTTP {archive_response.status}")
        archive_data = parse_json(archive_response)
        save_json(settings.raw_root, f"archives/{settings.username}.json", archive_data)
        archives = archive_data.get("archives", [])
        if month_filter:
            archives = [url for url in archives if month_from_url(url) == month_filter]
            if not archives:
                logger.error("Month %04d/%02d not found in archives", *month_filter)
                return FetchResult(
                    "incomplete",
                    0,
                    0,
                    0,
                    0,
                    (MonthFailure(*month_filter, "month was not present in the archive list"),),
                )
        current_url = archives[-1] if archives else None
        connection.execute(
            "UPDATE fetch_state SET is_current=0 WHERE username=?", (settings.username,)
        )
        fetched_months = 0
        unchanged_months = 0
        skipped_months = 0
        failed_months: list[MonthFailure] = []
        for index, url in enumerate(archives):
            year, month = month_from_url(url)
            current = url == current_url
            state = connection.execute(
                "SELECT etag, is_current FROM fetch_state WHERE username=? AND year=? AND month=?",
                (settings.username, year, month),
            ).fetchone()
            if state and not current and state[1] == 0:
                logger.info("Skipping fetched historical month %04d/%02d", year, month)
                skipped_months += 1
                continue
            if index or settings.delay:
                sleep(settings.delay)
            headers = {"If-None-Match": state[0]} if state and state[0] else {}
            try:
                response = request(url, headers)
                if response.status == 429:
                    raise RateLimitError(f"month {year:04d}/{month:02d} returned HTTP 429")
                if response.status == 304:
                    mark_state(connection, settings, year, month, state[0], current)
                    connection.commit()
                    logger.info("Month %04d/%02d unchanged", year, month)
                    unchanged_months += 1
                    continue
                if response.status != 200:
                    raise RuntimeError(f"month returned HTTP {response.status}")
                data = parse_json(response)
                save_json(settings.raw_root, f"games/{year:04d}/{month:02d}.json", data)
                with connection:
                    upsert_month(connection, data.get("games", []), year, month)
                    mark_state(
                        connection, settings, year, month, response.headers.get("ETag"), current
                    )
                fetched_months += 1
                logger.info("Fetched month %04d/%02d", year, month)
            except RateLimitError:
                raise
            except Exception as error:  # Month failures must not block later months.
                logger.error("Skipping month %04d/%02d: %s", year, month, error)
                failed_months.append(MonthFailure(year, month, str(error)))
        result = FetchResult(
            "incomplete" if failed_months else "complete",
            len(archives),
            fetched_months,
            unchanged_months,
            skipped_months,
            tuple(failed_months),
        )
        if result.complete:
            logger.info("Fetch complete for %s", settings.username)
        else:
            logger.error(
                "Fetch incomplete for %s: %d month(s) failed",
                settings.username,
                len(failed_months),
            )
        return result
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch Chess.com monthly games.")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.yaml"))
    parser.add_argument("--username")
    parser.add_argument("--delay", type=float)
    parser.add_argument("--month", help="Fetch only a single month in YYYY/MM format")
    args = parser.parse_args(argv)
    settings = load_settings(args.config, args.username, args.delay)
    logger = configure_logging(settings.log_path)
    month_filter = None
    if args.month:
        try:
            year, month = args.month.split("/")
            month_filter = (int(year), int(month))
        except ValueError:
            logger.error("--month must be in YYYY/MM format")
            return 1
    try:
        result = run(settings, logger, month_filter)
        return result.exit_code
    except RateLimitError as error:
        logger.error("Rate limited; stopping: %s", error)
        return 2
    except Exception as error:
        logger.error("Fetch failed: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
