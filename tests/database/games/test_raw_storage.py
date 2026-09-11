from __future__ import annotations

import json
from pathlib import Path

import pytest

from chess_move_trainer.database.games.raw_storage import (
    RawMonthError,
    load_month,
    merge_current_month,
    publish_month,
    validate_month_envelope,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> object:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_exact_structural_gate_accepts_empty_and_other_defective_game_details() -> None:
    assert validate_month_envelope(_fixture("month-empty.json")) == []
    games = validate_month_envelope(_fixture("month-valid.json"))

    assert len(games) == 2
    assert games[0]["pgn"] == "1. e4 e5 *"
    assert validate_month_envelope(
        {
            "synthetic_fixture": "defective details remain raw",
            "games": [
                {
                    "uuid": "12345678-1234-4234-8234-123456789abc",
                    "white": None,
                    "pgn": 17,
                    "rules": "synthetic-unknown",
                }
            ],
        }
    )


@pytest.mark.parametrize(
    "candidate",
    [
        [],
        {"synthetic_fixture": "missing games"},
        {"synthetic_fixture": "wrong games type", "games": {}},
        {"synthetic_fixture": "non-object game", "games": ["game"]},
        {"synthetic_fixture": "missing UUID", "games": [{}]},
        {"synthetic_fixture": "invalid UUID", "games": [{"uuid": "invalid"}]},
        {
            "synthetic_fixture": "duplicate normalized UUID",
            "games": [
                {"uuid": "BBBBBBBB-BBBB-4BBB-8BBB-BBBBBBBBBBBB"},
                {"uuid": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"},
            ],
        },
    ],
)
def test_exact_structural_gate_rejects_only_shape_and_uuid_defects(candidate: object) -> None:
    with pytest.raises(RawMonthError):
        validate_month_envelope(candidate)


def test_current_merge_replaces_adds_and_retains_in_deterministic_order() -> None:
    merged = merge_current_month(
        _fixture("current-month-local.json"), _fixture("current-month-remote.json")
    )

    assert [game["uuid"] for game in merged["games"]] == [
        "cccccccc-cccc-4ccc-8ccc-ccccccccccc1",
        "cccccccc-cccc-4ccc-8ccc-ccccccccccc2",
        "cccccccc-cccc-4ccc-8ccc-ccccccccccc3",
    ]
    assert merged["games"][0]["revision"] == "retain omitted"
    assert merged["games"][1]["revision"] == "corrected replacement"
    assert merged["games"][2]["revision"] == "new game"


def test_valid_empty_remote_current_month_retains_all_local_games() -> None:
    local = _fixture("current-month-local.json")
    merged = merge_current_month(local, _fixture("month-empty.json"))

    assert merged["games"] == local["games"]


def test_publication_is_same_directory_flushed_atomic_and_loadable(tmp_path: Path) -> None:
    target = tmp_path / "games" / "2026" / "08.json"
    observed: dict[str, object] = {}

    def replace(source: Path, destination: Path) -> None:
        observed["source"] = source
        observed["destination"] = destination
        observed["bytes"] = source.read_bytes()
        source.replace(destination)

    publish_month(target, _fixture("month-valid.json"), replace_existing=True, replace=replace)

    assert Path(observed["source"]).parent == target.parent
    assert observed["destination"] == target
    assert observed["bytes"]
    assert load_month(target) == _fixture("month-valid.json")
    assert list(target.parent.glob(f".{target.name}.*.tmp")) == []


@pytest.mark.parametrize("failure", [OSError("replace failed"), KeyboardInterrupt()])
def test_failed_or_interrupted_replacement_preserves_prior_and_cleans_temp(
    tmp_path: Path, failure: BaseException
) -> None:
    target = tmp_path / "games" / "2026" / "08.json"
    target.parent.mkdir(parents=True)
    original = b'{"synthetic_fixture":"prior","games":[]}\n'
    target.write_bytes(original)

    def fail_replace(source: Path, destination: Path) -> None:
        del source, destination
        raise failure

    with pytest.raises(type(failure)):
        publish_month(
            target,
            _fixture("month-valid.json"),
            replace_existing=True,
            replace=fail_replace,
        )

    assert target.read_bytes() == original
    assert list(target.parent.glob(f".{target.name}.*.tmp")) == []


def test_invalid_candidate_never_changes_or_creates_target(tmp_path: Path) -> None:
    existing = tmp_path / "existing.json"
    missing = tmp_path / "missing.json"
    existing.write_text('{"synthetic_fixture":"prior","games":[]}\n', encoding="utf-8")
    original = existing.read_bytes()

    for target in (existing, missing):
        with pytest.raises(RawMonthError):
            publish_month(target, _fixture("month-unsafe.json"), replace_existing=True)

    assert existing.read_bytes() == original
    assert not missing.exists()


def test_historical_publication_never_replaces_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "07.json"
    target.write_text('{"synthetic_fixture":"history","games":[]}\n', encoding="utf-8")
    original = target.read_bytes()

    with pytest.raises(RawMonthError, match="already exists"):
        publish_month(target, _fixture("month-valid.json"), replace_existing=False)

    assert target.read_bytes() == original
