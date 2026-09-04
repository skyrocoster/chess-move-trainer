from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from chess_move_trainer.database.games.acquisition import (
    CHESSCOM_API_ORIGIN,
    acquire_months,
)
from chess_move_trainer.database.games.configuration import AcquireConfiguration


FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@dataclass
class FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


class SyntheticTransport:
    def __init__(self, responses: dict[str, object]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, float]] = []

    def get_json(self, url: str, *, timeout: float) -> Any:
        self.requests.append((url, timeout))
        response = self.responses[url]
        if isinstance(response, BaseException):
            raise response
        return response


def _config(*, timeout: float = 30.0, delay: float = 0.25) -> AcquireConfiguration:
    return AcquireConfiguration(
        username="synthetic-trainer",
        trainer_chesscom_uuid=UUID("11111111-1111-4111-8111-111111111111"),
        request_timeout=timeout,
        request_delay=delay,
    )


def _archive_url() -> str:
    return f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/archives"


def test_fixed_endpoint_timing_archive_selection_and_transient_archive_use(tmp_path: Path) -> None:
    july_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/07"
    august_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/08"
    transport = SyntheticTransport(
        {
            _archive_url(): _fixture("archive-list.json"),
            july_url: _fixture("month-valid.json"),
            august_url: _fixture("month-empty.json"),
        }
    )
    delays: list[float] = []

    result = acquire_months(
        _config(timeout=8.5, delay=0.75),
        tmp_path,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 20, tzinfo=UTC)),
        sleep=delays.append,
    )

    assert result.completed
    assert result.published_months == ("2026-07", "2026-08")
    assert transport.requests == [
        (_archive_url(), 8.5),
        (july_url, 8.5),
        (august_url, 8.5),
    ]
    assert delays == [0.75, 0.75]
    assert (tmp_path / "games" / "2026" / "07.json").exists()
    assert (tmp_path / "games" / "2026" / "08.json").exists()
    assert not (tmp_path / "archives").exists()


def test_existing_history_is_skipped_and_missing_history_is_created_once(tmp_path: Path) -> None:
    july_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/07"
    august_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/08"
    july_path = tmp_path / "games" / "2026" / "07.json"
    july_path.parent.mkdir(parents=True)
    july_path.write_text(json.dumps(_fixture("month-empty.json")), encoding="utf-8")
    original_history = july_path.read_bytes()
    transport = SyntheticTransport(
        {
            _archive_url(): _fixture("archive-list.json"),
            august_url: _fixture("month-valid.json"),
        }
    )

    result = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 1, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert result.skipped_months == ("2026-07",)
    assert july_path.read_bytes() == original_history
    assert [request[0] for request in transport.requests] == [_archive_url(), august_url]

    september_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/09"
    archive = {"synthetic_fixture": "history once", "archives": [august_url, september_url]}
    second_transport = SyntheticTransport(
        {
            _archive_url(): archive,
            august_url: AssertionError("existing history must not be requested"),
            september_url: _fixture("month-empty.json"),
        }
    )
    second = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=second_transport,
        clock=FixedClock(datetime(2026, 9, 1, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert second.completed
    assert second.skipped_months == ("2026-08",)
    assert second.published_months == ("2026-09",)
    assert [request[0] for request in second_transport.requests] == [
        _archive_url(),
        september_url,
    ]


def test_unlisted_current_month_is_not_constructed_or_replaced_by_latest_history(
    tmp_path: Path,
) -> None:
    july_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/07"
    archive = {"synthetic_fixture": "current unlisted", "archives": [july_url]}
    transport = SyntheticTransport(
        {_archive_url(): archive, july_url: _fixture("month-valid.json")}
    )

    result = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert result.published_months == ("2026-07",)
    assert [request[0] for request in transport.requests] == [_archive_url(), july_url]
    assert not (tmp_path / "games" / "2026" / "08.json").exists()


def test_current_month_merges_corrections_new_games_and_omissions(tmp_path: Path) -> None:
    august_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/08"
    current_path = tmp_path / "games" / "2026" / "08.json"
    current_path.parent.mkdir(parents=True)
    current_path.write_text(
        json.dumps(_fixture("current-month-local.json")), encoding="utf-8"
    )
    transport = SyntheticTransport(
        {
            _archive_url(): {"synthetic_fixture": "current only", "archives": [august_url]},
            august_url: _fixture("current-month-remote.json"),
        }
    )

    result = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )
    saved = json.loads(current_path.read_text(encoding="utf-8"))

    assert result.completed
    assert [game["revision"] for game in saved["games"]] == [
        "retain omitted",
        "corrected replacement",
        "new game",
    ]


def test_valid_empty_current_response_retains_local_games(tmp_path: Path) -> None:
    august_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/08"
    current_path = tmp_path / "games" / "2026" / "08.json"
    current_path.parent.mkdir(parents=True)
    local = _fixture("current-month-local.json")
    current_path.write_text(json.dumps(local), encoding="utf-8")
    transport = SyntheticTransport(
        {
            _archive_url(): {"synthetic_fixture": "current only", "archives": [august_url]},
            august_url: _fixture("month-empty.json"),
        }
    )

    result = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert result.completed
    assert json.loads(current_path.read_text(encoding="utf-8"))["games"] == local["games"]


def test_unsafe_response_preserves_current_and_other_defects_are_published(
    tmp_path: Path,
) -> None:
    august_url = f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/08"
    current_path = tmp_path / "games" / "2026" / "08.json"
    current_path.parent.mkdir(parents=True)
    current_path.write_text(json.dumps(_fixture("month-valid.json")), encoding="utf-8")
    original = current_path.read_bytes()
    archive = {"synthetic_fixture": "current only", "archives": [august_url]}
    unsafe_transport = SyntheticTransport(
        {_archive_url(): archive, august_url: _fixture("month-duplicate-uuid.json")}
    )

    unsafe = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=unsafe_transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert not unsafe.completed
    assert current_path.read_bytes() == original

    defective = {
        "synthetic_fixture": "details accepted raw",
        "games": [
            {"uuid": "77777777-7777-4777-8777-777777777777", "pgn": None, "white": 4}
        ],
    }
    acceptable_transport = SyntheticTransport(
        {_archive_url(): archive, august_url: defective}
    )
    acceptable = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=acceptable_transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert acceptable.completed
    assert json.loads(current_path.read_text(encoding="utf-8"))["games"][-1] == defective["games"][0]


def test_month_failure_continues_and_returns_incomplete_result(tmp_path: Path) -> None:
    urls = [
        f"{CHESSCOM_API_ORIGIN}/pub/player/synthetic-trainer/games/2026/{month:02d}"
        for month in (6, 7, 8)
    ]
    archive = {"synthetic_fixture": "continuation", "archives": urls}
    transport = SyntheticTransport(
        {
            _archive_url(): archive,
            urls[0]: RuntimeError("synthetic rate limit"),
            urls[1]: _fixture("month-valid.json"),
            urls[2]: _fixture("month-empty.json"),
        }
    )

    result = acquire_months(
        _config(delay=0.0),
        tmp_path,
        transport=transport,
        clock=FixedClock(datetime(2026, 8, 15, tzinfo=UTC)),
        sleep=lambda _: None,
    )

    assert not result.completed
    assert result.published_months == ("2026-07", "2026-08")
    assert result.failures[0].month == "2026-06"
    assert "rate limit" in result.failures[0].message
    assert not (tmp_path / "games" / "2026" / "06.json").exists()
    assert (tmp_path / "games" / "2026" / "07.json").exists()
    assert (tmp_path / "games" / "2026" / "08.json").exists()
