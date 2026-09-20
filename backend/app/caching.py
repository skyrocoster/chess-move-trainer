"""Process-local cache for safe repeated backend reads.

Bounded ``cachetools.TTLCache`` namespaces sit behind one lock with per-key
single-flight: concurrent identical misses invoke the underlying reader once.
Only immutable serialized payloads from successful (``200``) reads are stored;
validation, stale, missing, and failure responses are never cached. A
database-file signature (main file plus ``-wal``/``-shm``/journal sidecars) is
checked before serving a hit and before publishing a miss; any change advances
the cache generation, clears every namespace, and forces recomputation.
Successful writes clear the whole cache explicitly. No ``Cache-Control`` or
other browser caching headers are emitted.

Single-flight waits are bounded: a waiter whose leader does not finish within
``SINGLE_FLIGHT_TIMEOUT_SECONDS`` discards the registered in-flight entry (so
a later request can become leader) and raises ``SingleFlightTimeoutError``.
Timeout failures are never cached.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from cachetools import TTLCache
from fastapi.responses import Response

from chess_move_trainer.database.games import GameSearchQuery
from chess_move_trainer.database.openings import OpeningCatalogueQuery
from chess_move_trainer.database.positions import (
    TrainingRequirementPolicy,
    TrainingRequirementQuery,
)

TRAINING_TTL_SECONDS = 60.0
TRAINING_MAX_ENTRIES = 128
OPENINGS_TTL_SECONDS = 900.0
OPENINGS_MAX_ENTRIES = 128
GAMES_TTL_SECONDS = 60.0
GAMES_MAX_ENTRIES = 64
READ_TTL_SECONDS = 300.0
READ_MAX_ENTRIES = 512
SINGLE_FLIGHT_TIMEOUT_SECONDS = 30.0

_SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")


class SingleFlightTimeoutError(TimeoutError):
    """A single-flight leader did not finish within the bounded wait."""


class _Inflight:
    """Single-flight state for one cache key being computed."""

    __slots__ = ("condition", "done", "error", "generation")

    def __init__(self, generation: int) -> None:
        self.condition = threading.Condition()
        self.done = False
        self.error: BaseException | None = None
        self.generation = generation


@dataclass
class ResponseCacheNamespace:
    """One bounded TTL namespace with its own single-flight table."""

    name: str
    ttl_seconds: float
    max_entries: int
    cache: TTLCache = field(init=False)
    inflight: dict[Hashable, _Inflight] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.cache = TTLCache(maxsize=self.max_entries, ttl=self.ttl_seconds)
        _REGISTRY.append(self)


_REGISTRY: list[ResponseCacheNamespace] = []

training_namespace = ResponseCacheNamespace(
    name="training", ttl_seconds=TRAINING_TTL_SECONDS, max_entries=TRAINING_MAX_ENTRIES
)
openings_namespace = ResponseCacheNamespace(
    name="openings", ttl_seconds=OPENINGS_TTL_SECONDS, max_entries=OPENINGS_MAX_ENTRIES
)
games_namespace = ResponseCacheNamespace(
    name="games", ttl_seconds=GAMES_TTL_SECONDS, max_entries=GAMES_MAX_ENTRIES
)
read_namespace = ResponseCacheNamespace(
    name="read", ttl_seconds=READ_TTL_SECONDS, max_entries=READ_MAX_ENTRIES
)

_lock = threading.RLock()
_generation = 0
_last_signatures: dict[str, tuple] = {}


def _current_signature(resolved: str) -> tuple:
    """Fingerprint the database main file and SQLite sidecars without creating anything."""

    base = Path(resolved)
    entries: list[tuple | None] = []
    for candidate in (base, *(Path(str(base) + suffix) for suffix in _SIDECAR_SUFFIXES)):
        try:
            stat = candidate.stat()
        except OSError:
            entries.append(None)
        else:
            entries.append(
                (
                    stat.st_size,
                    stat.st_mtime_ns,
                    getattr(stat, "st_dev", None),
                    getattr(stat, "st_ino", None),
                )
            )
    return (resolved, tuple(entries))


def openings_catalogue_version(database_path: Path | str) -> str:
    """Return a bounded opaque version for the database and SQLite sidecars."""

    resolved = str(Path(database_path).resolve())
    signature = _current_signature(resolved)
    material = json.dumps(signature, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _refresh_signature_locked(resolved: str) -> bool:
    """Record the current signature; on change for a known path, clear all and return True."""

    global _generation
    signature = _current_signature(resolved)
    previous = _last_signatures.get(resolved)
    _last_signatures[resolved] = signature
    if previous is None or previous == signature:
        return False
    _generation += 1
    for namespace in _REGISTRY:
        namespace.cache.clear()
    return True


def clear_caches() -> None:
    """Drop every cached payload and advance the generation.

    This is the sanctioned seam for write invalidation, tests, and benchmarks.
    In-flight computations that started before the clear never publish stale data.
    """

    global _generation
    with _lock:
        _generation += 1
        for namespace in _REGISTRY:
            namespace.cache.clear()


def serialize_response_body(body: object) -> bytes:
    """Serialize one response model exactly like Starlette's JSONResponse."""

    payload = body.model_dump(mode="json", by_alias=True) if hasattr(body, "model_dump") else body
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
    ).encode("utf-8")


def training_requirements_key(
    database_path: Path | str,
    query: TrainingRequirementQuery,
    policy: TrainingRequirementPolicy,
) -> tuple:
    """Canonical key from the validated query, resolved database, and policy."""

    return (
        "training-requirements",
        str(Path(database_path).resolve()),
        query.as_of,
        query.training_requirement_gt,
        query.training_requirement_gte,
        query.training_requirement_lt,
        query.training_requirement_lte,
        query.trainer_color,
        query.opening_key,
        query.opening_match,
        query.page,
        query.page_size,
        policy.target_success_rate,
        policy.credit_half_life_days,
    )


def openings_key(database_path: Path | str, query: OpeningCatalogueQuery) -> tuple:
    """Canonical key from the validated catalogue query and resolved database."""

    return (
        "openings",
        str(Path(database_path).resolve()),
        query.page,
        query.page_size,
        query.search,
        query.eco_from,
        query.eco_to,
        query.sort,
    )


def opening_detail_key(database_path: Path | str, opening_key: str) -> tuple:
    """Canonical key for one opening detail read."""

    return ("opening", str(Path(database_path).resolve()), opening_key)


def games_key(database_path: Path | str, query: GameSearchQuery) -> tuple:
    """Canonical key from the validated games query and resolved database."""

    return (
        "games",
        str(Path(database_path).resolve()),
        query.page,
        query.page_size,
        query.started_at_from,
        query.started_at_to,
        query.ended_at_from,
        query.ended_at_to,
        query.trainer_color,
        query.trainer_outcome,
        query.termination_reason,
        query.trainer_rating_min,
        query.trainer_rating_max,
        query.opponent_rating_min,
        query.opponent_rating_max,
        query.opponent_chesscom_uuid,
        query.time_class,
        query.time_control,
        query.opening_key,
        query.opening_match,
        query.contains_fen,
        query.move_fen,
        query.move_uci,
        query.min_length_plies,
        query.max_length_plies,
        query.analysis_coverage,
        query.preferred_coverage,
        query.sort,
    )


def game_detail_key(database_path: Path | str, game_uuid: str) -> tuple:
    """Canonical key for one immutable game-detail read."""

    return ("game-detail", str(Path(database_path).resolve()), game_uuid)


def analysis_key(database_path: Path | str, fen: str) -> tuple:
    """Canonical key for one validated analysis observation."""

    return ("analysis", str(Path(database_path).resolve()), fen)


def position_insight_key(
    database_path: Path | str,
    fen: str,
    trainer_color: str,
    as_of: str,
) -> tuple:
    """Canonical key for one validated position insight."""

    return (
        "position-insight",
        str(Path(database_path).resolve()),
        fen,
        trainer_color,
        as_of,
    )


def preferred_moves_key(
    database_path: Path | str,
    fen: str,
    from_date: str,
    until: str,
) -> tuple:
    """Canonical key for one validated preferred-move timeline."""

    return (
        "preferred-moves",
        str(Path(database_path).resolve()),
        fen,
        from_date,
        until,
    )


def _discard_inflight(
    namespace: ResponseCacheNamespace, key: Hashable, inflight: _Inflight
) -> None:
    """Remove ``inflight`` only while it is still the registered entry for ``key``.

    A timed-out waiter can orphan a still-running leader, after which a new
    in-flight entry may be registered for the same key. The identity check
    keeps every removal from deleting another caller's entry. Call with
    ``_lock`` held.
    """

    if namespace.inflight.get(key) is inflight:
        del namespace.inflight[key]


def get_or_compute(
    namespace: ResponseCacheNamespace,
    key: Hashable,
    database_path: Path | str,
    compute: Callable[[], bytes | None],
    wait_timeout_seconds: float = SINGLE_FLIGHT_TIMEOUT_SECONDS,
) -> bytes | None:
    """Return the cached payload or compute it once per key.

    ``compute`` runs outside the global lock and returns the serialized
    ``200`` payload, or ``None`` for a successful but uncacheable read (such
    as a ``404``). Exceptions propagate to every waiter and are never stored.
    A payload is published only when the generation captured at lookup time
    still matches and the database signature is unchanged after computing.

    Waiters bound their wait to ``wait_timeout_seconds``. A waiter whose
    leader never finishes discards the registered in-flight entry — so a
    later request can become leader instead of piling onto the stuck one —
    and raises ``SingleFlightTimeoutError``. Timeout failures are never
    cached. A slow leader that eventually completes still returns (and may
    publish) its own result under the usual generation and signature checks.
    """

    resolved = str(Path(database_path).resolve())
    while True:
        with _lock:
            _refresh_signature_locked(resolved)
            generation = _generation
            payload = namespace.cache.get(key)
            if payload is not None:
                return payload
            inflight = namespace.inflight.get(key)
            if inflight is None:
                inflight = _Inflight(generation)
                namespace.inflight[key] = inflight
                leader = True
            else:
                leader = False
        if leader:
            break
        deadline = time.monotonic() + wait_timeout_seconds
        timed_out = False
        with inflight.condition:
            while not inflight.done:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                inflight.condition.wait(remaining)
        if timed_out:
            with _lock:
                _discard_inflight(namespace, key, inflight)
            raise SingleFlightTimeoutError(
                f"single-flight leader for namespace {namespace.name!r} did not "
                f"finish within {wait_timeout_seconds:.1f}s"
            )
        with _lock:
            if inflight.error is not None:
                raise inflight.error
            if inflight.generation != _generation:
                continue
            payload = namespace.cache.get(key)
            if payload is not None:
                return payload
        # The leader finished without publishing (a concurrent invalidation or
        # signature change won); retry as a fresh lookup.
    try:
        payload = compute()
    except BaseException as error:
        with _lock:
            with inflight.condition:
                inflight.error = error
                inflight.done = True
                inflight.condition.notify_all()
            _discard_inflight(namespace, key, inflight)
        raise
    with _lock:
        if (
            payload is not None
            and inflight.generation == _generation
            and not _refresh_signature_locked(resolved)
        ):
            namespace.cache[key] = payload
        with inflight.condition:
            inflight.done = True
            inflight.condition.notify_all()
        _discard_inflight(namespace, key, inflight)
    return payload


def json_response(payload: bytes, headers: Mapping[str, str] | None = None) -> Response:
    """Wrap one cached or freshly computed payload in a fresh response."""

    return Response(content=payload, media_type="application/json", headers=headers)


__all__ = [
    "GAMES_MAX_ENTRIES",
    "GAMES_TTL_SECONDS",
    "OPENINGS_MAX_ENTRIES",
    "OPENINGS_TTL_SECONDS",
    "READ_MAX_ENTRIES",
    "READ_TTL_SECONDS",
    "SINGLE_FLIGHT_TIMEOUT_SECONDS",
    "TRAINING_MAX_ENTRIES",
    "TRAINING_TTL_SECONDS",
    "SingleFlightTimeoutError",
    "analysis_key",
    "clear_caches",
    "game_detail_key",
    "games_key",
    "games_namespace",
    "get_or_compute",
    "json_response",
    "opening_detail_key",
    "openings_catalogue_version",
    "openings_key",
    "openings_namespace",
    "position_insight_key",
    "preferred_moves_key",
    "read_namespace",
    "serialize_response_body",
    "training_namespace",
    "training_requirements_key",
]
