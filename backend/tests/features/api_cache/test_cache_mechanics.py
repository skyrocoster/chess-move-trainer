from __future__ import annotations

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from backend.app.caching import (
    ResponseCacheNamespace,
    SingleFlightTimeoutError,
    clear_caches,
    get_or_compute,
)


def _namespace(tmp_path: Path, **overrides: object) -> tuple[ResponseCacheNamespace, Path]:
    database = tmp_path / "mechanics.db"
    database.write_bytes(b"v0")
    options: dict[str, object] = {"ttl_seconds": 60.0, "max_entries": 128}
    options.update(overrides)
    namespace = ResponseCacheNamespace(name="mechanics", **options)  # type: ignore[arg-type]
    return namespace, database


def test_ttl_expiry_forces_recomputation(tmp_path: Path) -> None:
    namespace, database = _namespace(tmp_path, ttl_seconds=0.05)
    calls = 0

    def compute() -> bytes | None:
        nonlocal calls
        calls += 1
        return b'{"ok":true}'

    assert get_or_compute(namespace, ("k",), database, compute) == b'{"ok":true}'
    assert get_or_compute(namespace, ("k",), database, compute) == b'{"ok":true}'
    assert calls == 1
    time.sleep(0.15)
    assert get_or_compute(namespace, ("k",), database, compute) == b'{"ok":true}'
    assert calls == 2


def test_max_entries_evicts_least_recently_used(tmp_path: Path) -> None:
    namespace, database = _namespace(tmp_path, max_entries=2)
    calls: dict[str, int] = {}

    def compute(key: str) -> bytes | None:
        calls[key] = calls.get(key, 0) + 1
        return key.encode("utf-8")

    assert get_or_compute(namespace, ("a",), database, lambda: compute("a")) == b"a"
    assert get_or_compute(namespace, ("b",), database, lambda: compute("b")) == b"b"
    assert get_or_compute(namespace, ("a",), database, lambda: compute("a")) == b"a"
    assert get_or_compute(namespace, ("c",), database, lambda: compute("c")) == b"c"
    assert get_or_compute(namespace, ("a",), database, lambda: compute("a")) == b"a"
    assert get_or_compute(namespace, ("b",), database, lambda: compute("b")) == b"b"
    assert calls == {"a": 1, "b": 2, "c": 1}


def test_concurrent_identical_misses_compute_once(tmp_path: Path) -> None:
    namespace, database = _namespace(tmp_path)
    calls = 0
    started = threading.Barrier(6)

    def compute() -> bytes | None:
        nonlocal calls
        calls += 1
        time.sleep(0.2)
        return b'{"shared":true}'

    def worker() -> bytes | None:
        started.wait(timeout=10)
        return get_or_compute(namespace, ("shared",), database, compute)

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(worker) for _ in range(5)]
        started.wait(timeout=10)
        bodies = [future.result(timeout=30) for future in futures]

    assert calls == 1
    assert bodies == [b'{"shared":true}'] * 5


def test_invalidation_during_inflight_read_prevents_stale_publication(
    tmp_path: Path,
) -> None:
    namespace, database = _namespace(tmp_path)
    calls = 0
    entered = threading.Event()
    release = threading.Event()
    outcomes: list[bytes | None] = []

    def compute() -> bytes | None:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(timeout=10)
        return b'{"stale":false}'

    def leader() -> None:
        outcomes.append(get_or_compute(namespace, ("race",), database, compute))

    thread = threading.Thread(target=leader)
    thread.start()
    assert entered.wait(timeout=10)
    clear_caches()
    release.set()
    thread.join(timeout=10)

    assert outcomes == [b'{"stale":false}']
    assert calls == 1
    # The cleared generation must not have been repopulated behind our back.
    assert get_or_compute(namespace, ("race",), database, compute) == b'{"stale":false}'
    assert calls == 2


def test_failed_leader_wakes_waiters_without_caching(tmp_path: Path) -> None:
    namespace, database = _namespace(tmp_path)
    calls = 0
    started = threading.Barrier(4)

    def boom() -> bytes | None:
        nonlocal calls
        calls += 1
        time.sleep(0.2)
        raise RuntimeError("boom")

    def worker() -> object:
        started.wait(timeout=10)
        try:
            return get_or_compute(namespace, ("fragile",), database, boom)
        except RuntimeError as error:
            return error

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(worker) for _ in range(3)]
        started.wait(timeout=10)
        results = [future.result(timeout=30) for future in futures]

    assert calls == 1
    assert all(isinstance(result, RuntimeError) for result in results)
    assert get_or_compute(namespace, ("fragile",), database, lambda: b"recovered") == b"recovered"
    assert calls == 1


def test_stuck_leader_releases_waiters_and_later_request_becomes_leader(
    tmp_path: Path,
) -> None:
    namespace, database = _namespace(tmp_path)
    calls = 0
    entered = threading.Event()
    release = threading.Event()
    leader_outcomes: list[bytes | None] = []

    def stuck() -> bytes | None:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(timeout=30)
        return b'{"slow":true}'

    def leader() -> None:
        leader_outcomes.append(get_or_compute(namespace, ("stuck",), database, stuck))

    def waiter() -> object:
        assert entered.wait(timeout=10)
        try:
            return get_or_compute(namespace, ("stuck",), database, stuck, wait_timeout_seconds=0.1)
        except SingleFlightTimeoutError as error:
            return error

    leader_thread = threading.Thread(target=leader)
    leader_thread.start()
    assert entered.wait(timeout=10)

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(waiter) for _ in range(3)]
        results = [future.result(timeout=30) for future in futures]

    # Every waiter is released with a typed, finite timeout failure.
    assert all(isinstance(result, SingleFlightTimeoutError) for result in results)
    assert all(isinstance(result, TimeoutError) for result in results)
    # The waiters never computed, nothing was cached, and the stuck entry is gone
    # so a later request can become leader instead of piling onto the stuck one.
    assert calls == 1
    assert namespace.inflight == {}
    assert namespace.cache.get(("stuck",)) is None

    # A later request becomes leader and serves fresh data while the original
    # leader is still stuck. The clear also guarantees the stuck leader's late
    # completion cannot publish over the recovered value.
    clear_caches()
    assert (
        get_or_compute(namespace, ("stuck",), database, lambda: b'{"recovered":true}')
        == b'{"recovered":true}'
    )

    release.set()
    leader_thread.join(timeout=10)
    assert leader_outcomes == [b'{"slow":true}']
    assert get_or_compute(namespace, ("stuck",), database, stuck) == b'{"recovered":true}'
    assert calls == 1


def test_sidecar_presence_and_file_replacement_change_signature(
    tmp_path: Path,
) -> None:
    namespace, database = _namespace(tmp_path)
    calls = 0

    def compute() -> bytes | None:
        nonlocal calls
        calls += 1
        return b'{"sig":true}'

    assert get_or_compute(namespace, ("sig",), database, compute) == b'{"sig":true}'
    assert get_or_compute(namespace, ("sig",), database, compute) == b'{"sig":true}'
    assert calls == 1

    sidecar = Path(str(database) + "-wal")
    sidecar.write_bytes(b"wal-bytes")
    try:
        assert get_or_compute(namespace, ("sig",), database, compute) == b'{"sig":true}'
        assert calls == 2
    finally:
        sidecar.unlink()

    assert get_or_compute(namespace, ("sig",), database, compute) == b'{"sig":true}'
    assert calls == 3

    replacement = tmp_path / "replacement.db"
    replacement.write_bytes(b"v0")
    os.replace(replacement, database)
    assert get_or_compute(namespace, ("sig",), database, compute) == b'{"sig":true}'
    assert calls == 4


def test_missing_database_file_never_gets_created(tmp_path: Path) -> None:
    namespace = ResponseCacheNamespace(name="missing", ttl_seconds=60.0, max_entries=8)
    missing = tmp_path / "never-created.db"

    def compute() -> bytes | None:
        raise FileNotFoundError(missing)

    with pytest.raises(FileNotFoundError):
        get_or_compute(namespace, ("absent",), missing, compute)
    with pytest.raises(FileNotFoundError):
        get_or_compute(namespace, ("absent",), missing, compute)
    assert not missing.exists()
    assert not Path(str(missing) + "-wal").exists()
