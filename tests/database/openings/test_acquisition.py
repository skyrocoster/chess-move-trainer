from __future__ import annotations

import json
import os
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from chess_move_trainer.database.openings import acquisition as acquisition_module
from chess_move_trainer.database.openings.acquisition import (
    COMMIT_RESOLUTION_URL,
    GITHUB_API_HOST,
    GITHUB_RAW_HOST,
    LICHESS_REPOSITORY,
    LICHESS_REPOSITORY_URL,
    OPENING_SOURCE_FILES,
    RAW_SOURCE_URL_TEMPLATE,
    HttpxOpeningAcquisitionTransport,
    OpeningAcquisitionError,
    OpeningAcquisitionFailure,
    OpeningAcquisitionResult,
    OpeningAcquisitionTransport,
    acquire_openings,
    validate_request_timing,
)
from chess_move_trainer.database.openings.source import load_opening_sources


SHA = "0123456789abcdef0123456789abcdef01234567"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


class FakeTransport:
    def __init__(
        self,
        commit_payload: object,
        file_text: dict[str, str] | None = None,
        failures: dict[str, BaseException] | None = None,
    ) -> None:
        self.commit_payload = commit_payload
        self.file_text = file_text or {}
        self.failures = failures or {}
        self.events: list[tuple[str, str, float]] = []

    def get_json(self, url: str, *, timeout: float) -> object:
        self.events.append(("json", url, timeout))
        failure = self.failures.get(url)
        if failure is not None:
            raise failure
        return self.commit_payload

    def get_text(self, url: str, *, timeout: float) -> str:
        self.events.append(("text", url, timeout))
        failure = self.failures.get(url)
        if failure is not None:
            raise failure
        return self.file_text[url]


def _valid_commit_payload() -> object:
    return json.loads((FIXTURE_DIR / "commit-valid.json").read_text(encoding="utf-8"))


def _file_urls() -> tuple[str, ...]:
    return tuple(
        RAW_SOURCE_URL_TEMPLATE.format(commit=SHA, filename=filename)
        for filename in OPENING_SOURCE_FILES
    )


def _fake_files() -> dict[str, str]:
    return {
        url: (FIXTURE_DIR / "acquisition-valid" / filename).read_text(encoding="utf-8")
        for url, filename in zip(_file_urls(), OPENING_SOURCE_FILES)
    }


def _target_snapshot(source_dir: Path) -> dict[str, bytes]:
    return {
        entry.name: entry.read_bytes()
        for entry in source_dir.iterdir()
        if entry.is_file()
    }


def _parent_snapshot(parent: Path) -> set[Path]:
    return set(parent.iterdir())


def test_fixed_upstream_and_file_contract_are_not_configurable() -> None:
    assert LICHESS_REPOSITORY == "lichess-org/chess-openings"
    assert LICHESS_REPOSITORY_URL == "https://github.com/lichess-org/chess-openings"
    assert GITHUB_API_HOST == "api.github.com"
    assert GITHUB_RAW_HOST == "raw.githubusercontent.com"
    assert OPENING_SOURCE_FILES == ("a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv")
    assert COMMIT_RESOLUTION_URL == (
        "https://api.github.com/repos/lichess-org/chess-openings/commits"
    )
    assert RAW_SOURCE_URL_TEMPLATE == (
        "https://raw.githubusercontent.com/lichess-org/chess-openings/{commit}/{filename}"
    )


def test_transport_protocol_and_production_adapter_expose_only_two_get_shapes() -> None:
    assert set(OpeningAcquisitionTransport.__annotations__) == set()
    assert set(HttpxOpeningAcquisitionTransport.__dict__) >= {"get_json", "get_text"}


def test_result_and_failure_models_are_frozen_and_report_completion() -> None:
    failure = OpeningAcquisitionFailure("resolution", "synthetic failure")
    incomplete = OpeningAcquisitionResult.failure(failure.subject, failure.message)
    complete = OpeningAcquisitionResult(
        resolved_commit="0" * 40,
        published_files=OPENING_SOURCE_FILES,
    )

    assert incomplete.failures == (failure,)
    assert not incomplete.completed
    assert complete.completed
    with pytest.raises(FrozenInstanceError):
        failure.subject = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        complete.resolved_commit = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("timeout", "delay"),
    [(0, 0.25), (-1, 0.25), (float("nan"), 0.25), (30.0, -1), (30.0, float("inf"))],
)
def test_timing_validation_rejects_non_finite_or_out_of_range_values(
    timeout: float, delay: float
) -> None:
    with pytest.raises(ValueError):
        validate_request_timing(timeout, delay)


def test_valid_commit_retrieves_exact_files_in_order_with_finite_timing_and_cleanup(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        (source_dir / filename).write_bytes(f"prior {filename}".encode())
    (source_dir / "keep.txt").write_bytes(b"unrelated")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    transport = FakeTransport(_valid_commit_payload(), _fake_files())
    events: list[tuple[str, object, object]] = []
    observed_staging: list[tuple[Path, dict[str, bytes]]] = []

    def sleeper(delay: float) -> None:
        events.append(("sleep", delay, None))

    def observe(staging_dir: Path) -> None:
        observed_staging.append(
            (
                staging_dir,
                {
                    filename: (staging_dir / filename).read_bytes()
                    for filename in OPENING_SOURCE_FILES
                },
            )
        )

    result = acquire_openings(
        source_dir,
        request_timeout=7.5,
        request_delay=0.125,
        transport=transport,
        sleep=sleeper,
        staging_observer=observe,
    )

    assert result.resolved_commit == SHA
    assert result.completed
    assert result.published_files == OPENING_SOURCE_FILES
    assert result.unchanged_files == ()
    assert [event[:2] for event in transport.events] == [
        ("json", COMMIT_RESOLUTION_URL),
        *[("text", url) for url in _file_urls()],
    ]
    assert [event[2] for event in transport.events] == [7.5] * 6
    assert events == [("sleep", 0.125, None)] * 5
    assert observed_staging == [
        (
            observed_staging[0][0],
            {
                filename: (FIXTURE_DIR / "acquisition-valid" / filename).read_bytes()
                for filename in OPENING_SOURCE_FILES
            },
        )
    ]
    assert _target_snapshot(source_dir) != before_target
    assert _target_snapshot(source_dir) == {
        **{
            filename: (FIXTURE_DIR / "acquisition-valid" / filename).read_bytes()
            for filename in OPENING_SOURCE_FILES
        },
        "keep.txt": b"unrelated",
    }
    assert _parent_snapshot(tmp_path) == before_parent
    assert not observed_staging[0][0].exists()


def test_staged_validation_reuses_source_service_and_rejects_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        (source_dir / filename).write_bytes(f"prior {filename}".encode())
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    files = _fake_files()
    files[_file_urls()[0]] = "eco\tname\tmoves\nA00\tBad\t1. e4\n"
    transport = FakeTransport(_valid_commit_payload(), files)
    validated_paths: list[Path] = []
    real_validator = acquisition_module.load_opening_sources

    def validate(path: Path) -> tuple[object, ...]:
        validated_paths.append(path)
        return real_validator(path)

    monkeypatch.setattr(acquisition_module, "load_opening_sources", validate)
    result = acquisition_module.acquire_openings(source_dir, transport=transport)

    assert result.resolved_commit == SHA
    assert result.failures[0].subject == "validation"
    assert validated_paths and not validated_paths[0].exists()
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


def test_fresh_publish_replaces_all_fixed_files_and_revalidates_output(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    (source_dir / "notes.txt").write_bytes(b"keep me")
    transport = FakeTransport(_valid_commit_payload(), _fake_files())

    result = acquire_openings(source_dir, transport=transport)

    assert result.completed
    assert result.resolved_commit == SHA
    assert result.published_files == OPENING_SOURCE_FILES
    assert result.unchanged_files == ()
    assert load_opening_sources(source_dir)
    assert (source_dir / "notes.txt").read_bytes() == b"keep me"


def test_identical_target_is_a_zero_write_no_op(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        fixture = FIXTURE_DIR / "acquisition-valid" / filename
        (source_dir / filename).write_bytes(fixture.read_bytes())
    (source_dir / "notes.txt").write_bytes(b"keep me")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    replace_calls: list[tuple[Path, Path]] = []

    def replace(source: Path, target: Path) -> None:
        replace_calls.append((source, target))
        raise AssertionError("unchanged content must not be replaced")

    result = acquire_openings(
        source_dir,
        transport=FakeTransport(_valid_commit_payload(), _fake_files()),
        replace=replace,
    )

    assert result.completed
    assert result.published_files == ()
    assert result.unchanged_files == OPENING_SOURCE_FILES
    assert replace_calls == []
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


def test_partly_missing_target_publishes_the_complete_fixed_set(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        if filename != "b.tsv":
            (source_dir / filename).write_bytes(f"old {filename}".encode())
    (source_dir / "notes.txt").write_bytes(b"keep me")

    result = acquire_openings(
        source_dir,
        transport=FakeTransport(_valid_commit_payload(), _fake_files()),
    )

    assert result.completed
    assert result.published_files == OPENING_SOURCE_FILES
    assert result.unchanged_files == ()
    assert load_opening_sources(source_dir)
    assert (source_dir / "notes.txt").read_bytes() == b"keep me"


def test_unexpected_target_tsv_rejects_before_any_swap(tmp_path: Path) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        (source_dir / filename).write_bytes(f"old {filename}".encode())
    (source_dir / "unexpected.tsv").write_bytes(b"synthetic")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    replace_calls: list[tuple[Path, Path]] = []

    def replace(source: Path, target: Path) -> None:
        replace_calls.append((source, target))
        os.replace(source, target)

    result = acquire_openings(
        source_dir,
        transport=FakeTransport(_valid_commit_payload(), _fake_files()),
        replace=replace,
    )

    assert not result.completed
    assert result.failures[0].subject == "target"
    assert "unexpected.tsv" in result.failures[0].message
    assert replace_calls == []
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


@pytest.mark.parametrize("failure_index", range(len(OPENING_SOURCE_FILES)))
def test_each_swap_failure_restores_existing_bytes_and_cleans_temps(
    tmp_path: Path, failure_index: int
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        (source_dir / filename).write_bytes(f"old {filename}".encode())
    (source_dir / "notes.txt").write_bytes(b"keep me")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    failed_filename = OPENING_SOURCE_FILES[failure_index]

    def replace(source: Path, target: Path) -> None:
        if target.name == failed_filename:
            raise OSError(f"synthetic swap failure for {target.name}")
        os.replace(source, target)

    result = acquire_openings(
        source_dir,
        transport=FakeTransport(_valid_commit_payload(), _fake_files()),
        replace=replace,
    )

    assert not result.completed
    assert result.failures[0].subject == failed_filename
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


def test_failed_fresh_publish_removes_new_fixed_files(tmp_path: Path) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    (source_dir / "notes.txt").write_bytes(b"keep me")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)

    def replace(source: Path, target: Path) -> None:
        if target.name == "d.tsv":
            raise OSError("synthetic fresh swap failure")
        os.replace(source, target)

    result = acquire_openings(
        source_dir,
        transport=FakeTransport(_valid_commit_payload(), _fake_files()),
        replace=replace,
    )

    assert not result.completed
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent
    assert all(not (source_dir / filename).exists() for filename in OPENING_SOURCE_FILES)


def test_interruption_restores_prior_set_and_propagates_after_cleanup(tmp_path: Path) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        (source_dir / filename).write_bytes(f"old {filename}".encode())
    (source_dir / "notes.txt").write_bytes(b"keep me")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)

    def replace(source: Path, target: Path) -> None:
        if target.name == "c.tsv":
            raise KeyboardInterrupt
        os.replace(source, target)

    with pytest.raises(KeyboardInterrupt):
        acquire_openings(
            source_dir,
            transport=FakeTransport(_valid_commit_payload(), _fake_files()),
            replace=replace,
        )

    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


def test_rollback_failure_is_reported_as_a_distinct_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    for filename in OPENING_SOURCE_FILES:
        (source_dir / filename).write_bytes(f"old {filename}".encode())

    def replace(source: Path, target: Path) -> None:
        raise OSError("synthetic swap failure")

    def rollback_failure(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise OSError("synthetic rollback failure")

    monkeypatch.setattr(acquisition_module, "_restore_prior_state", rollback_failure)
    result = acquire_openings(
        source_dir,
        transport=FakeTransport(_valid_commit_payload(), _fake_files()),
        replace=replace,
    )

    assert not result.completed
    assert result.failures[0].subject == "rollback"
    assert "synthetic rollback failure" in result.failures[0].message


@pytest.mark.parametrize(
    "fixture_name",
    [
        "commit-empty.json",
        "commit-object.json",
        "commit-missing-sha.json",
        "commit-invalid-sha.json",
    ],
)
def test_malformed_commit_payloads_stop_before_file_requests(
    tmp_path: Path, fixture_name: str
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    (source_dir / "keep.txt").write_bytes(b"unchanged")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    payload = json.loads((FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"))
    transport = FakeTransport(payload, _fake_files())

    result = acquire_openings(source_dir, transport=transport)

    assert result.resolved_commit is None
    assert result.failures[0].subject == "commit resolution"
    assert result.failures[0].message
    assert [event[0] for event in transport.events] == ["json"]
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


@pytest.mark.parametrize(
    "payload",
    [
        ["0123456789abcdef0123456789abcdef01234567"],
        [{"sha": 123}],
        [{"sha": "0123456789abcdef0123456789abcdef0123456"}],
        [{"sha": "0123456789abcdef0123456789abcdef012345678"}],
        [{"sha": "0123456789ABCDEF0123456789abcdef01234567"}],
    ],
)
def test_commit_sha_must_be_exactly_lowercase_forty_hex_characters(
    tmp_path: Path, payload: object
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    transport = FakeTransport(payload, _fake_files())

    result = acquire_openings(source_dir, transport=transport)

    assert result.resolved_commit is None
    assert result.failures[0].subject == "commit resolution"
    assert [event[0] for event in transport.events] == ["json"]


def test_resolution_transport_failure_is_an_ordinary_failure_without_file_request(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    transport = FakeTransport(
        _valid_commit_payload(),
        _fake_files(),
        {COMMIT_RESOLUTION_URL: OpeningAcquisitionError("synthetic HTTP 503")},
    )

    result = acquire_openings(source_dir, transport=transport)

    assert result.resolved_commit is None
    assert result.failures[0].subject == "commit resolution"
    assert "synthetic HTTP 503" in result.failures[0].message
    assert [event[0] for event in transport.events] == ["json"]


def test_retrieval_failure_at_file_four_cleans_staging_and_preserves_target(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    (source_dir / "existing.tsv").write_bytes(b"not a fixed source")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    urls = _file_urls()
    transport = FakeTransport(
        _valid_commit_payload(),
        _fake_files(),
        {urls[3]: OpeningAcquisitionError("synthetic file four failure")},
    )
    observed: list[Path] = []

    result = acquire_openings(
        source_dir,
        transport=transport,
        staging_observer=observed.append,
    )

    assert result.resolved_commit == SHA
    assert result.failures[0].subject == OPENING_SOURCE_FILES[3]
    assert "synthetic file four failure" in result.failures[0].message
    assert [event[0] for event in transport.events] == ["json", "text", "text", "text", "text"]
    assert observed == []
    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent


def test_keyboard_interrupt_cleans_staging_and_propagates_without_target_change(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    (source_dir / "keep.txt").write_bytes(b"unchanged")
    before_target = _target_snapshot(source_dir)
    before_parent = _parent_snapshot(tmp_path)
    urls = _file_urls()
    transport = FakeTransport(
        _valid_commit_payload(),
        _fake_files(),
        {urls[3]: KeyboardInterrupt()},
    )

    with pytest.raises(KeyboardInterrupt):
        acquire_openings(source_dir, transport=transport)

    assert _target_snapshot(source_dir) == before_target
    assert _parent_snapshot(tmp_path) == before_parent
